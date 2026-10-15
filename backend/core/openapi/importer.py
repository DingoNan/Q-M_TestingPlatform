# -*- coding: utf-8 -*-
"""Swagger 2.0 / OpenAPI 3.x 解析（P2 接口资产自动发现，2026-10-15 甘肃 242 实测后新增）。

★ 为什么要有这个模块：
  甘肃 242 那 32 个接口是我开着浏览器抓 XHR、再一条条手工录进去的，成本极高且容易漏。
  绝大多数后端服务都能直接暴露 /v2/api-docs（Swagger 2.0）或 /v3/api-docs（OpenAPI 3.x），
  解析它就能一次性把接口资产建全。平台此前只有 HAR 导入（要有真实流量），
  这里补上「无流量、只看契约」的路径。

★ 设计约束：
  1) **纯函数、不依赖 Django**：本模块只做解析，落库交给视图，便于离线单测；
  2) 解析不出来就如实报错，绝不猜、绝不静默丢弃 —— 静默丢接口比报错更危险；
  3) 示例值从 schema 递归生成（无 example 时按类型给零值），保证落库后可直接调试。

★ 两个版本的关键差异（踩过才知道）：
  - Swagger 2.0：basePath + parameters（in=body/query/path），body 只有一个；
  - OpenAPI 3.x：servers[].url + requestBody.content['application/json'].schema；
  两者 tag 语义一致，故统一映射到「服务模块」。
"""
import re

# 只认这些 HTTP 方法，避免把 paths 下的扩展字段（如 x-xxx）当成方法
_HTTP_METHODS = ('get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace')

# URL 里的路径参数占位符：Swagger 用 {id}，平台落库后执行期需要能替换，故原样保留
_PATH_PARAM = re.compile(r'\{([^}/]+)\}')

# 模块名长度受 ServiceModule.name(max_length=20) 限制
_MAX_MODULE_NAME = 20


def _zero_value(schema, depth=0):
    """按 JSON Schema 递归生成示例值。depth 防自引用死循环。"""
    if depth > 6 or not isinstance(schema, dict):
        return None
    # 显式 example 优先（最贴近真实）
    if 'example' in schema:
        return schema['example']
    stype = schema.get('type')
    if isinstance(stype, list):
        stype = stype[0] if stype else None
    if stype == 'array':
        item = schema.get('items') or {}
        one = _zero_value(item, depth + 1)
        return [one] if one is not None else []
    if stype == 'object' or 'properties' in schema:
        props = schema.get('properties') or {}
        out = {}
        for k, v in props.items():
            out[k] = _zero_value(v, depth + 1)
        return out
    if stype in ('integer', 'number'):
        return 0
    if stype == 'boolean':
        return True
    if stype == 'string':
        fmt = schema.get('format') or ''
        if 'date-time' in fmt:
            return '2026-01-01T00:00:00'
        if 'date' in fmt:
            return '2026-01-01'
        return ''
    # 没写 type 但有 properties 的情况上面已覆盖；其余统一返回空对象占位
    return {}


def _schema_to_json(schema):
    """把 schema 转成可直接落库的 json 字段（object / 其它都包一层安全处理）。"""
    val = _zero_value(schema)
    return val if val is not None else {}


def _params_from_swagger2(operation, path_item):
    """Swagger 2.0：parameters 里 in=query 的转查询参数；in=body 的转 json body。"""
    params, body = [], None
    merged = list(operation.get('parameters') or []) + list(path_item.get('parameters') or [])
    for p in merged:
        if not isinstance(p, dict):
            continue
        where = p.get('in')
        if where in ('query', 'path', 'header'):
            params.append({
                'key': p.get('name'),
                'value': _zero_value(p.get('schema') or {'type': p.get('type') or 'string'}),
                'desc': p.get('description') or '',
                'required': bool(p.get('required')),
                'in': where,
            })
        elif where == 'body':
            body = _schema_to_json(p.get('schema') or {})
    return params, body


def _params_from_openapi3(operation, path_item):
    """OpenAPI 3.x：parameters 转查询参数；requestBody.content 转 json body。"""
    params, body = [], None
    for p in (operation.get('parameters') or []) + (path_item.get('parameters') or []):
        if not isinstance(p, dict):
            continue
        where = p.get('in')
        if where in ('query', 'path', 'header', 'cookie'):
            schema = (p.get('schema') or {})
            params.append({
                'key': p.get('name'),
                'value': _zero_value(schema),
                'desc': p.get('description') or '',
                'required': bool(p.get('required')),
                'in': where,
            })

    req_body = operation.get('requestBody') or {}
    content = req_body.get('content') or {}
    # 优先取 JSON，其次表单，其余按第一个能解析的媒体类型
    media = None
    for key in ('application/json', 'application/*+json', 'application/x-www-form-urlencoded',
                'multipart/form-data'):
        if key in content:
            media = content[key]
            break
    if media is None and content:
        media = list(content.values())[0]
    if isinstance(media, dict):
        if 'example' in media:
            body = media['example']
        else:
            body = _schema_to_json(media.get('schema') or {})
    return params, body


def _response_example(operation, is_v3):
    """取成功响应（2xx）的示例体。"""
    responses = operation.get('responses') or {}
    if not isinstance(responses, dict):
        return {}
    # 按优先级挑一个 2xx
    chosen = None
    for code in ('200', '201', '202', '204'):
        if code in responses:
            chosen = responses[code]
            break
    if chosen is None:
        for code, val in responses.items():
            if str(code).startswith('2'):
                chosen = val
                break
    if chosen is None:
        return {}
    if not isinstance(chosen, dict):
        return {}
    if is_v3:
        content = chosen.get('content') or {}
        media = None
        for key in ('application/json', 'application/*+json'):
            if key in content:
                media = content[key]
                break
        if media is None and content:
            media = list(content.values())[0]
        if isinstance(media, dict):
            if 'example' in media:
                return media['example']
            return _schema_to_json(media.get('schema') or {})
        return {}
    # Swagger 2.0：responses.200.schema
    if 'schema' in chosen:
        return _schema_to_json(chosen['schema'] or {})
    if 'examples' in chosen:
        ex = chosen['examples'] or {}
        first = list(ex.values())[0] if ex else None
        return first if first is not None else {}
    return {}


def _clean_module_name(tag, fallback):
    """模块名清洗：去掉首尾空白，超长截断（ServiceModule.name 最长 20）。"""
    name = (str(tag or '')).strip() or fallback
    if len(name) > _MAX_MODULE_NAME:
        name = name[:_MAX_MODULE_NAME]
    return name


def parse_openapi(doc, default_tag='默认模块'):
    """把 Swagger 2.0 / OpenAPI 3.x 文档解析成扁平接口列表。

    入参 doc：已解析好的 dict（调用方负责 JSON/YAML 解析）。
    返回：
      {
        'ok': bool, 'error': str,
        'version': '2.0' | '3.x',
        'info': {'title','version','base_path'},
        'items': [ {tag, name, url, method, params, json, headers, response, summary} ],
        'tags': [str],
        'stats': {'paths': n, 'operations': n}
      }
    """
    if not isinstance(doc, dict):
        return {'ok': False, 'error': '文档根节点必须是对象', 'items': []}

    is_v3 = 'openapi' in doc
    version = str(doc.get('openapi') or doc.get('swagger') or ('3.0' if is_v3 else '2.0'))

    paths = doc.get('paths')
    if not isinstance(paths, dict) or not paths:
        return {'ok': False, 'error': '文档中 paths 为空或格式不正确', 'items': []}

    # Swagger 2.0 用 host + basePath；OpenAPI 3.x 用 servers[].url 的路径部分
    base_path = ''
    if not is_v3:
        base_path = (doc.get('basePath') or '').strip()
    else:
        servers = doc.get('servers') or []
        for s in servers:
            url = (s or {}).get('url') or ''
            m = re.match(r'^https?://[^/]+(.*)$', url)
            if m:
                base_path = m.group(1).rstrip('/')
                break
            if url.startswith('/'):
                base_path = url.rstrip('/')
                break
    if base_path and not base_path.startswith('/'):
        base_path = '/' + base_path

    info = {
        'title': ((doc.get('info') or {}).get('title') or '').strip(),
        'version': ((doc.get('info') or {}).get('version') or '').strip(),
        'base_path': base_path,
    }

    items, tags_seen = [], []
    for raw_path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method in _HTTP_METHODS:
            operation = path_item.get(method)
            if not isinstance(operation, dict):
                continue
            tag_list = operation.get('tags') or []
            tag = _clean_module_name(tag_list[0] if tag_list else '', default_tag)
            if tag not in tags_seen:
                tags_seen.append(tag)

            name = (operation.get('summary') or operation.get('operationId')
                    or ('%s %s' % (method.upper(), raw_path))).strip()
            # Api.name 最长 50
            if len(name) > 50:
                name = name[:50]

            if is_v3:
                params, body = _params_from_openapi3(operation, path_item)
            else:
                params, body = _params_from_swagger2(operation, path_item)

            items.append({
                'tag': tag,
                'name': name,
                'url': (base_path + raw_path) if base_path else raw_path,
                'method': method.upper(),
                'params': params,
                'json': body if body is not None else {},
                'headers': [{'key': 'Content-Type', 'value': 'application/json',
                             'desc': 'Swagger 导入默认请求头', 'required': True}],
                'response': _response_example(operation, is_v3),
                'summary': (operation.get('description') or '').strip()[:500],
            })

    if not items:
        return {'ok': False, 'error': 'paths 中没有解析到任何接口操作', 'items': []}

    return {
        'ok': True, 'error': '', 'version': version, 'info': info,
        'items': items, 'tags': tags_seen,
        'stats': {'paths': len(paths), 'operations': len(items)},
    }


def load_openapi_text(text):
    """把文本解析成 dict，兼容 JSON 与 YAML（YAML 需要 pyyaml）。不抛异常。"""
    if not text or not str(text).strip():
        return None, '内容为空'
    text = str(text).strip()
    if text.startswith('{'):
        import json
        try:
            return json.loads(text), ''
        except Exception as e:
            return None, 'JSON 解析失败：%s: %s' % (type(e).__name__, e)
    try:
        import yaml
        return yaml.safe_load(text), ''
    except ImportError:
        return None, '内容不是 JSON，且当前环境缺少 pyyaml，无法解析 YAML 格式的 OpenAPI'
    except Exception as e:
        return None, 'YAML 解析失败：%s: %s' % (type(e).__name__, e)
