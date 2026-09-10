"""
AI生成接口自动化用例 - 落库逻辑

核心职责:
1. 从Api表深拷贝参数树，重新生成id(避免与接口文档冲突)
2. 把LLM生成的override贴到参数树对应字段
3. 数据驱动模式: 把override字段值替换为 ${caseData.<字段名>}，case.data存所有场景值
4. 独立用例模式: override直接贴值，case.data=default_case_data()
5. 落库 Step + Case + CaseSteps
6. 断言act引用 ${stepResponse.<case_step_id>.<act_field>}，落库后回填

关键设计:
- LLM出场景和值，接口文档出结构
- 不生成setup/teardown脚本
- 断言使用check.py的方法(method字段)，act引用FuncAndParams格式
"""
import uuid
import logging
from typing import List, Dict, Any, Tuple, Optional

from django.db import transaction

from apps.interfaces.models import Api
from apps.tests.models import Case, CaseSteps, Step
from apps.envs.models import Module, Plant
from apps.projects.models import Project
from apps.tests.models import default_case_data
from core.com.enum_obj import StepType
from apps.ai_service.api_case_schemas import GeneratedApiCase, ParamOverride

logger = logging.getLogger('ai_service')


def _ensure_unique_case_name(name: str) -> str:
    """确保用例名称不与已有Case冲突

    Case.name 有 unique 约束，AI 生成的名字可能重复。
    策略: 如果名字已存在，追加短UUID后缀。
    """
    name = name[:50]
    if not Case.objects.filter(name=name).exists():
        return name
    # 截断留空间给后缀
    suffix = f'_{uuid.uuid4().hex[:6]}'
    base = name[:50 - len(suffix)]
    new_name = f'{base}{suffix}'
    # 极小概率仍冲突，再追加
    while Case.objects.filter(name=new_name).exists():
        suffix = f'_{uuid.uuid4().hex[:6]}'
        new_name = f'{base}{suffix}'
    return new_name


# ===== 参数树工具 =====
def _regenerate_tree_ids(tree: Any) -> Any:
    """深拷贝参数树并重新生成所有id

    Api表里的参数树id是接口文档的id，直接拷贝到Step会和接口文档冲突。
    CaseStepCreate的mergeParamLists也做了类似处理，但这里是空用例直接拷贝，更简单。

    输入参数树结构(每个节点):
        {
            "id": "xxx",
            "parentId": "yyy",
            "name": "...",
            "value": "...",
            "type": "string",
            "children": [...]  # 嵌套节点
        }
    """
    if not tree:
        return []
    if not isinstance(tree, list):
        return tree

    # 先建立老id → 新id映射，再二次遍历修复parentId
    id_mapping: Dict[str, str] = {}

    def _collect_ids(nodes: list):
        for node in nodes:
            if not isinstance(node, dict):
                continue
            old_id = node.get('id')
            if old_id:
                id_mapping[old_id] = uuid.uuid4().hex
            children = node.get('children') or node.get('child') or []
            if children:
                _collect_ids(children)

    _collect_ids(tree)

    def _rebuild(nodes: list, parent_new_id=None) -> list:
        new_nodes = []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            old_id = node.get('id', '')
            new_node = {k: v for k, v in node.items() if k not in ('id', 'parentId')}
            new_node['id'] = id_mapping.get(old_id, uuid.uuid4().hex)
            new_node['parentId'] = parent_new_id

            children = node.get('children') or node.get('child')
            if children:
                new_node['children'] = _rebuild(children, new_node['id'])
            new_nodes.append(new_node)
        return new_nodes

    return _rebuild(tree)


def _flat_list_to_tree(flat_list: list) -> list:
    """将扁平列表(通过parentId关联)转为树结构(根节点带children)

    Api.json存储为扁平数组(所有节点在同一层，通过parentId关联父子关系)，
    但执行引擎的list_to_dict需要树结构(根节点带children嵌套)。
    此函数做转换，浅拷贝节点避免影响原扁平列表(api_json仍用扁平格式)。
    """
    if not flat_list or not isinstance(flat_list, list):
        return []

    # 浅拷贝每个节点，避免给原列表节点添加children
    nodes = [dict(n) if isinstance(n, dict) else n for n in flat_list]

    # 建立 id → node 映射
    node_map: Dict[str, dict] = {}
    for node in nodes:
        if isinstance(node, dict):
            nid = node.get('id', '')
            if nid:
                node_map[nid] = node

    # 按parentId构建树: 根节点提到顶层，子节点挂到父节点children
    root_nodes = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        parent_id = node.get('parentId')
        # 根节点: parentId 为 null/空/None
        if not parent_id or parent_id == '' or parent_id == 'null':
            root_nodes.append(node)
        elif parent_id in node_map:
            parent = node_map[parent_id]
            parent.setdefault('children', []).append(node)
        else:
            # 父节点不存在(可能被remove删除)，作为根节点
            root_nodes.append(node)

    return root_nodes


def _ensure_nested_children(nodes: list) -> list:
    """把扁平(parentId)参数树转换为嵌套(children)结构；已嵌套的原样返回

    用于响应参数树: Api.response 里的 response_data 是扁平结构(父引用parentId)，
    Api.response_tree 里的是嵌套结构(已有children)。统一成嵌套后再提取字段路径。
    """
    if not isinstance(nodes, list) or not nodes:
        return []
    # 已存在children/child嵌套关系 → 视为已嵌套
    if any(isinstance(n, dict) and (n.get('children') or n.get('child')) for n in nodes):
        return [n for n in nodes if isinstance(n, dict)]

    id_to_node: Dict[str, dict] = {
        n['id']: n for n in nodes if isinstance(n, dict) and n.get('id')
    }
    roots = []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        pid = n.get('parentId')
        if pid and pid in id_to_node:
            id_to_node[pid].setdefault('children', []).append(n)
        else:
            roots.append(n)
    return roots


def unwrap_response_data(tree: Any) -> List[list]:
    """从响应树包装结构中取出所有 response_data 参数树(已转为嵌套children结构)

    Api.response / Api.response_tree 按HTTP状态码分组存储，结构为:
        [{"response_data": [<参数树节点>], "response_status": 200}, ...]
    其中 response_data 内节点的 name 路径才是真实响应体字段(如 msg / result.token_access)，
    response_status 是HTTP状态码(对应内置 apiStatusCode，不是响应体字段)。
    旧数据可能直接是裸参数树列表(根节点带name)，也兼容。

    Returns:
        [参数树节点list, ...] —— 每个状态码条目一个，节点为嵌套children结构
    """
    trees: List[list] = []
    if not tree or not isinstance(tree, list):
        return trees
    for entry in tree:
        if not isinstance(entry, dict):
            continue
        if 'response_data' in entry:
            data = entry.get('response_data') or []
            if isinstance(data, list) and data:
                trees.append(_ensure_nested_children(data))
        elif entry.get('name'):
            # 旧格式: 裸参数树节点
            trees.append(_ensure_nested_children([entry]))
    return trees


def _param_tree_paths(nodes: list, path_prefix: str = '', depth: int = 0) -> List[str]:
    """提取嵌套参数树的 name 点号路径列表(包含对象节点自身路径，便于对象非空断言)

    如 [{'name':'result','children':[{'name':'token_access'}]}]
    → ['result', 'result.token_access']
    """
    paths: List[str] = []
    if not isinstance(nodes, list) or depth > 6:
        return paths
    for node in nodes:
        if not isinstance(node, dict):
            continue
        name = node.get('name')
        if not name:
            continue
        current_path = f"{path_prefix}.{name}" if path_prefix else str(name)
        paths.append(current_path)
        children = node.get('children') or node.get('child') or []
        if children:
            paths.extend(_param_tree_paths(children, current_path, depth + 1))
    return paths


def extract_response_field_paths(api) -> List[str]:
    """提取接口真实响应体字段路径(去重，保序)

    优先取 response_tree(嵌套结构)，回退 response(扁平结构)。
    返回如 ['code', 'msg', 'result', 'result.token_access']，
    对应运行时 ${stepResponse.<id>.apiResponseBody.<path>} 的 <path> 部分。
    """
    paths: List[str] = []
    for tree in (getattr(api, 'response_tree', None), getattr(api, 'response', None)):
        for nodes in unwrap_response_data(tree):
            for p in _param_tree_paths(nodes):
                if p not in paths:
                    paths.append(p)
        if paths:
            break
    return paths


def _find_node_by_path(tree: list, target_path: str) -> Tuple[Optional[dict], Optional[list]]:
    """按点号路径查找参数树节点

    path如 "address.city" → 找根级address节点 → 找其children里的city节点
    返回 (node, parent_list) 便于修改
    """
    if not tree or not target_path:
        return None, None

    parts = target_path.split('.')
    current_list = tree
    current_node = None

    for i, part in enumerate(parts):
        found = None
        for node in current_list:
            if not isinstance(node, dict):
                continue
            if node.get('name') == part:
                found = node
                break
        if not found:
            return None, None
        current_node = found
        if i < len(parts) - 1:
            current_list = current_node.get('children') or current_node.get('child') or []
            if not isinstance(current_list, list):
                return None, None

    return current_node, current_list


def _apply_override_to_tree(tree: list, overrides: List[Dict[str, Any]]):
    """把override贴到参数树对应字段

    override dict结构(GeneratedApiCase.model_dump后的格式):
        {"path": "userId", "value": "123", "type": "number", "is_null": False, "remove": False}

    规则:
    - remove=True: 从parent_list里删除该节点(missing_required场景)
    - is_null=True 或 value=None: 节点value设为None，type设为null
    - type字段存在: 同步更新节点的type(string/boolean/array/object/number/null)
    - 其他: 节点value设为override的value
    """
    if not tree or not overrides:
        return

    for ov in overrides:
        path = ov.get('path')
        if not path:
            continue
        node, parent_list = _find_node_by_path(tree, path)
        if not node:
            logger.warning(f"[AI-SAVER] override路径未找到: {path}")
            continue

        if ov.get('remove'):
            # 从父列表移除
            if parent_list and node in parent_list:
                parent_list.remove(node)
            continue

        if ov.get('is_null'):
            node['value'] = None
            node['type'] = 'null'
        else:
            node['value'] = ov.get('value')
            # 同步更新节点type(仅当override显式指定type时)
            ov_type = ov.get('type')
            if ov_type:
                node['type'] = ov_type


def _replace_tree_value_with_case_data_ref(tree: list, target_path: str, field_name: str):
    """把参数树指定路径的value替换为 ${caseData.<field_name>} 引用

    用于数据驱动模式: Step参数树对应字段的值改成引用，
    执行时由 set_case_data_params 注入实际值。
    """
    if not tree:
        return
    node, _ = _find_node_by_path(tree, target_path)
    if node:
        node['value'] = f"${{caseData.{field_name}}}"


def _collect_override_paths(cases: List[dict]) -> List[str]:
    """收集多条用例override路径的并集

    用于数据驱动模式: Step参数树里所有被override的字段都要改成${caseData.xxx}引用
    """
    paths = set()
    for c in cases:
        for key in ('header_overrides', 'param_overrides', 'body_overrides'):
            for ov in c.get(key, []):
                if not ov.get('remove'):
                    paths.add(ov.get('path'))
    return sorted(paths)


def _case_data_field_name(path: str) -> str:
    """参数路径转caseData字段名

    "address.city" → "address_city" (点号转下划线)
    """
    return path.replace('.', '_')


def _build_case_data_value(cases: List[dict], override_paths: List[str]) -> List[dict]:
    """构建case.data['value']列表

    每条用例对应value里一个dict，key是caseData字段名，value是override的值
    缺失的path用文档示例值(这里用None，实际执行时Step参数树是${caseData.xxx}引用，
    缺失字段会解析失败，因此要保证每条都有全部path的值)

    特殊字段 _name_: 用例名，用于执行日志显示
    """
    value_list = []
    for c in cases:
        entry = {'_name_': c.get('name', '')}

        # 构建path → override值映射
        override_map: Dict[str, Any] = {}
        for key in ('header_overrides', 'param_overrides', 'body_overrides'):
            for ov in c.get(key, []):
                path = ov.get('path')
                if not path or ov.get('remove'):
                    continue
                if ov.get('is_null'):
                    override_map[path] = None
                else:
                    override_map[path] = ov.get('value')

        # 填充所有override_paths
        for path in override_paths:
            field = _case_data_field_name(path)
            entry[field] = override_map.get(path)

        value_list.append(entry)
    return value_list


# ===== 落库主逻辑 =====
def save_generated_api_cases(api_id: int, generated_cases: List[dict],
                             user_id: int, project_id: int,
                             module_id: int, tag_ids: List[int] = None) -> List[dict]:
    """把AI生成的用例落库

    Args:
        api_id: 接口文档ID
        generated_cases: GeneratedApiCase.model_dump() 列表
        user_id: 创建人
        project_id: 项目ID
        module_id: 用例模块ID(决定Step.plant)
        tag_ids: 标签ID列表

    Returns:
        [{'id': case_id, 'name': case_name, 'mode': 'single|data_driven'}, ...]
    """
    logger.info(
        f"[AI-SAVER] 开始落库: api_id={api_id}, cases={len(generated_cases)}, "
        f"module_id={module_id}"
    )
    saved = []
    tag_ids = tag_ids or []

    # 按 data_driven_group 聚合
    groups = _group_by_data_driven(generated_cases)

    for group_key, group_cases in groups.items():
        try:
            if group_key and len(group_cases) > 1 and all(
                c.get('param_structure_same') for c in group_cases
            ):
                # 数据驱动模式
                case_info = _create_data_driven_case(
                    api_id, group_cases, user_id, project_id, module_id, tag_ids
                )
                case_info['mode'] = 'data_driven'
            else:
                # 独立用例模式
                case_info = _create_single_case(
                    api_id, group_cases[0], user_id, project_id, module_id, tag_ids
                )
                case_info['mode'] = 'single'
            saved.append(case_info)
        except Exception as e:
            logger.error(f"[AI-SAVER] 落库失败 group={group_key}: {e}")
            raise

    logger.info(f"[AI-SAVER] 落库完成，共 {len(saved)} 个用例")
    return saved


def _group_by_data_driven(cases: List[dict]) -> Dict[str, List[dict]]:
    """按data_driven_group聚合

    - 有group且param_structure_same=true的归到同一组
    - 无group或param_structure_same=false的各自独立一组(用唯一key)
    """
    groups: Dict[str, List[dict]] = {}
    for i, c in enumerate(cases):
        group = c.get('data_driven_group')
        if not group or not c.get('param_structure_same'):
            group = f"_single_{i}"  # 独立用例唯一key
        groups.setdefault(group, []).append(c)
    return groups


def _create_single_case(api_id: int, case_dict: dict,
                        user_id: int, project_id: int,
                        module_id: int, tag_ids: List[int]) -> dict:
    """创建独立用例(1 Case + 1 Step + 1 CaseSteps)

    override直接贴值到Step参数树，case.data=default_case_data()
    """
    api = Api.objects.get(id=api_id)
    module = Module.objects.get(id=module_id)

    with transaction.atomic():
        # 1. 深拷贝参数树，重新生成id
        new_headers = _regenerate_tree_ids(api.headers)
        new_params = _regenerate_tree_ids(api.params)
        new_json = _regenerate_tree_ids(api.json) if api.body_type == Api.BodyType.Json else []
        new_data = _regenerate_tree_ids(api.data) if api.body_type == Api.BodyType.Data else []
        new_response_tree = _regenerate_tree_ids(api.response_tree)

        # 2. 应用override
        _apply_override_to_tree(new_headers, case_dict.get('header_overrides', []))
        _apply_override_to_tree(new_params, case_dict.get('param_overrides', []))
        if api.body_type == Api.BodyType.Json:
            _apply_override_to_tree(new_json, case_dict.get('body_overrides', []))
        else:
            _apply_override_to_tree(new_data, case_dict.get('body_overrides', []))

        # 3. 新建Step
        step = _build_step(
            api, module, project_id, user_id,
            case_dict.get('desc') or case_dict.get('name', ''),
            new_headers, new_params, new_json, new_data, new_response_tree,
            case_dict.get('assertions', [])
        )
        step.save()

        # 4. 新建Case
        case = _build_case(
            _ensure_unique_case_name(case_dict.get('name', f'AI生成用例_{api.name}')),
            project_id, module_id, user_id, default_case_data()
        )
        case.save()
        if tag_ids:
            case.tag.set(tag_ids)

        # 5. 关联CaseSteps并回填断言act引用
        _create_case_steps_and_fill_check(case, step, case_dict.get('assertions', []))

    logger.info(f"[AI-SAVER] 独立用例落库: case_id={case.id}, name={case.name}")
    return {'id': case.id, 'name': case.name}


def _create_data_driven_case(api_id: int, group_cases: List[dict],
                             user_id: int, project_id: int,
                             module_id: int, tag_ids: List[int]) -> dict:
    """创建数据驱动用例(1 Case + 1 Step + 1 CaseSteps)

    Step参数树对应字段值改成 ${caseData.xxx}引用，case.data存所有场景值
    """
    api = Api.objects.get(id=api_id)
    module = Module.objects.get(id=module_id)
    template = group_cases[0]  # 用第一条作为Step模板

    with transaction.atomic():
        # 1. 深拷贝参数树
        new_headers = _regenerate_tree_ids(api.headers)
        new_params = _regenerate_tree_ids(api.params)
        new_json = _regenerate_tree_ids(api.json) if api.body_type == Api.BodyType.Json else []
        new_data = _regenerate_tree_ids(api.data) if api.body_type == Api.BodyType.Data else []
        new_response_tree = _regenerate_tree_ids(api.response_tree)

        # 2. 收集所有被override的路径并集
        override_paths = _collect_override_paths(group_cases)

        # 2.5 应用template的override(设置节点type，value会在下一步被替换为引用)
        _apply_override_to_tree(new_headers, template.get('header_overrides', []))
        _apply_override_to_tree(new_params, template.get('param_overrides', []))
        if api.body_type == Api.BodyType.Json:
            _apply_override_to_tree(new_json, template.get('body_overrides', []))
        else:
            _apply_override_to_tree(new_data, template.get('body_overrides', []))

        # 3. 把参数树里这些路径的值替换为 ${caseData.<field>}引用
        for path in override_paths:
            field = _case_data_field_name(path)
            _replace_tree_value_with_case_data_ref(new_headers, path, field)
            _replace_tree_value_with_case_data_ref(new_params, path, field)
            _replace_tree_value_with_case_data_ref(new_json, path, field)
            _replace_tree_value_with_case_data_ref(new_data, path, field)

        # 4. 构造case.data
        case_data = {
            'name': [_case_data_field_name(p) for p in override_paths],
            'value': _build_case_data_value(group_cases, override_paths),
        }

        # 5. 新建Step(用template的desc和assertions)
        step = _build_step(
            api, module, project_id, user_id,
            template.get('desc') or template.get('name', ''),
            new_headers, new_params, new_json, new_data, new_response_tree,
            template.get('assertions', [])
        )
        step.save()

        # 6. 新建Case(用第一条的name作为Case名)
        case = _build_case(
            _ensure_unique_case_name(template.get('name', f'AI数据驱动用例_{api.name}')),
            project_id, module_id, user_id, case_data
        )
        case.save()
        if tag_ids:
            case.tag.set(tag_ids)

        # 7. 关联CaseSteps并回填断言act引用
        _create_case_steps_and_fill_check(case, step, template.get('assertions', []))

    logger.info(
        f"[AI-SAVER] 数据驱动用例落库: case_id={case.id}, name={case.name}, "
        f"data_rows={len(case_data['value'])}"
    )
    return {'id': case.id, 'name': case.name}


def _build_step(api: Api, module: Module, project_id: int, user_id: int,
                desc: str, headers: list, params: list, json_body: list,
                data_body: list, response_tree: list,
                assertions: list) -> Step:
    """构建Step对象(不保存)

    断言的act引用在 _create_case_steps_and_fill_check 里回填
    """
    return Step(
        desc=desc[:100] if desc else api.name,
        project_id=project_id,
        database_name=None,
        step_active_tab='body',
        is_check=False,
        type=StepType.Request,
        com_step_type=StepType.Request,
        timeout=7,
        allow_redirects=True,
        verify=False,
        keyword=str(api.id),  # 绑定接口文档ID
        plant=module.plant,
        api_service=api.service,
        api_method=api.method,
        api_uri=api.url,
        api_headers=headers,
        common_headers=False,
        api_json_type=api.api_json_type,
        json_body_deal=None,
        api_json=json_body,
        body_type=api.body_type,
        api_json_tree=_flat_list_to_tree(json_body),
        api_data=data_body,
        data_body_deal=None,
        api_response=[],
        api_response_tree=response_tree,
        api_response_type=api.api_response_type,
        response_body_deal=None,
        api_params=params,
        check_params=[],  # 占位，回填时填入
        run_params=[],
        loop=[],
        until=[],
        setup='',
        script='',
        teardown='',
        func_params=[],
        create_by_id=user_id,
        update_by_id=user_id,
    )


def _build_case(name: str, project_id: int, module_id: int,
                user_id: int, data: dict) -> Case:
    """构建Case对象(不保存)"""
    return Case(
        name=name[:50],
        type=Case.FunctionCaseType.API,
        project_id=project_id,
        module_id=module_id,
        params=[],
        data=data,
        recent_test_result=Case.CaseResult.NoRUN,
        create_by_id=user_id,
        update_by_id=user_id,
    )


def _create_case_steps_and_fill_check(case: Case, step: Step, assertions: list):
    """创建CaseSteps关联，并回填Step的check_params act引用

    断言act引用格式: ${stepResponse.<case_step_id>.<act_field>}
    case_step_id在CaseSteps创建后才能拿到，因此要两步走

    check_params结构(与check.py的loop_assert_by_check_list匹配):
        {
            "method": "check_number_equal",      # check.py中的函数名
            "exp_value": 200,                    # 预期值
            "act_value": "${stepResponse.xxx.apiStatusCode}",  # 实际值引用
            "andOr": ""                          # 条件逻辑(暂不用)
        }
    """
    case_step = CaseSteps.objects.create(
        case=case,
        step=step,
        step_index=0,
        step_params=[],
        parent_id=None,
        is_run=True,
        fail_is_continue=CaseSteps.IsContinue.Stop,
    )

    # 构建check_params
    check_params = []
    for a in assertions:
        a_dict = a if isinstance(a, dict) else a.model_dump() if hasattr(a, 'model_dump') else {}
        method = a_dict.get('method', 'check_number_equal')
        act_field = a_dict.get('act_field', 'apiStatusCode')
        raw_exp = a_dict.get('exp_value')
        if raw_exp is None:
            exp_value = ''
        elif isinstance(raw_exp, str):
            exp_value = raw_exp
        else:
            exp_value = str(raw_exp)
        check_params.append({
            'method': method,
            'exp_value': exp_value,
            'act_value': f'${{stepResponse.{case_step.id}.{act_field}}}',
            'andOr': '',
        })

    Step.objects.filter(id=step.id).update(check_params=check_params)
