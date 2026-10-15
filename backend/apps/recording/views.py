# -*- coding: utf-8 -*-
"""录制接口（P0-②）

九个端点（前端 `api/index.js` 一一对应）：
    POST   /recording/session/                        创建会话
    GET    /recording/session/                        会话列表（履历页）
    GET    /recording/session/<id>/                   会话详情（含 IR）
    POST   /recording/session/<id>/events/            事件增量推送（multipart 优先）
    POST   /recording/session/<id>/finish/            结束并归一化 → IR
    POST   /recording/session/<id>/discard/           丢弃会话
    POST   /recording/session/<id>/ai_enhance/        AI 增强（P2）
    POST   /recording/parse/                          录制文件直传解析（P0-④ 主入口）
    POST   /recording/import/                         IR → 落库成用例步骤

★ 两条必须记住的平台约束（踩过）：
  1) `DATA_UPLOAD_MAX_MEMORY_SIZE`（默认 2.5MB）**只作用于 JSON body**，
     超限时 Django 在框架层直接返 400，视图根本进不去 —— 所以凡是可能大的数据
     （录制事件流、导出的录制文件）一律走 **multipart**（`request.FILES`）。
  2) `utils/base.py::CustomRender` 会**无条件**把返回的 dict 包进 `result`
     （含 `results` 键的除外）⇒ 视图只返裸 payload，前端统一读
     `(resp.data || {}).result || resp.data || {}`。
"""
import json
import logging
import re
import time
import traceback
import uuid

from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.projects.models import Project
from apps.recording import ai_enhance
from apps.recording.importer import (
    ELEMENT_BY_CHOICES,
    MODE_CHOICES,
    RecordingImportError,
    import_ir,
)
from apps.recording.models import RecordingSession
from apps.recording.serializers import (
    RecordingSessionListSerializer,
    RecordingSessionSerializer,
)
from apps.tests.models import Case
from core.recorder import normalizer as NZ
from core.recorder import sources as SRC
from utils.base import BasePageNumberPagination

logger = logging.getLogger('recording')

# 单个会话允许累积的事件上限 —— 防止扩展/脚本失控把一个会话撑成几十万条，
# 后面归一化与详情接口都会被拖死。
MAX_EVENTS_PER_SESSION = 20000
# raw_payload 里保留原文的上限（字符数）。超过就只留规范事件流 + 截断标记。
MAX_RAW_PAYLOAD_CHARS = 5_000_000

_ALLOWED_EXT = ('.json', '.har', '.txt', '.js', '.ts', '.py', '.mjs')


# ---------------------------------------------------------------------------
# 内部工具
# ---------------------------------------------------------------------------
def _user_id(request):
    return getattr(request.user, 'id', None)


def _try_parse_ndjson(text):
    """把 NDJSON（每行一个 JSON 对象）解析成 list；不是 NDJSON 就返回 None。

    ★ 为什么必须支持（v0.20.3 修复的真缺陷）
      扩展早期版本用 **NDJSON** 上传事件批（`file=events.ndjson`，
      Content-Type: application/x-ndjson）。而 `_read_upload` 只做
      `json.loads(text)` —— 多行 NDJSON 会抛
      `Extra data: line 2 column 1 (char N)`，视图把这句话原样当 400 detail 返回，
      扩展侧只能显示「最近错误：Extra data: ...」。
      实测：录制事件**一条都传不上来**，用户看到的却是"项目识别成功 + 录制报错"。
      在这里兼容 NDJSON，可以让**已经装了旧插件的用户不必重新安装**。

    ★ 判定必须严格：**每一行**都要能解析成对象/数组才算 NDJSON。
      Playwright 脚本、普通文本里夹一行 JSON 的都不会被误判成事件流。
    """
    lines = [ln.strip() for ln in str(text or '').splitlines()]
    lines = [ln for ln in lines if ln]
    if len(lines) < 2:
        # 单行的情况 json.loads 已经处理过了，这里不再重复
        return None
    out = []
    for ln in lines:
        if ln[0] not in '{[':
            return None
        try:
            obj = json.loads(ln)
        except ValueError:
            return None
        if not isinstance(obj, (dict, list)):
            return None
        out.append(obj)
    return out


def _read_upload(request):
    """从 multipart / JSON 里取出「一份录制数据」。

    返回 (data, file_name)：
      · 上传文件 → 按 UTF-8 解码后尝试 JSON 解析（含 NDJSON），失败则当脚本文本
      · `events` / `payload` 文本字段 → 同样处理
      · JSON body（仅适合小包）→ 原样返回
    """
    f = request.FILES.get('file') or request.FILES.get('recording')
    if f is not None:
        raw = f.read()
        name = getattr(f, 'name', '') or ''
        text = raw.decode('utf-8-sig', 'replace')
        try:
            return json.loads(text), name
        except ValueError:
            nd = _try_parse_ndjson(text)
            if nd is not None:
                return nd, name
            return text, name

    for key in ('payload', 'events', 'content'):
        v = request.data.get(key)
        if v is None or v == '':
            continue
        if isinstance(v, (dict, list)):
            return v, ''
        text = str(v)
        try:
            return json.loads(text), ''
        except ValueError:
            nd = _try_parse_ndjson(text)
            if nd is not None:
                return nd, ''
            return text, ''

    # 纯 JSON body（Django 的 2.5MB 限制在这里生效，大包会被框架层挡掉）
    body = request.data
    if isinstance(body, (list, dict)):
        if isinstance(body, dict) and not (body.get('steps') or body.get('actions')
                                           or body.get('events')):
            return None, ''
        return body, ''
    return None, ''


def _source_from_request(request, file_name=''):
    src = (request.data.get('source') or '').strip().lower()
    if src in ('', 'auto', 'none'):
        src = None
    if not src and file_name:
        low = file_name.lower()
        if low.endswith(('.js', '.ts', '.mjs', '.py')):
            src = SRC.SOURCE_PLAYWRIGHT_SCRIPT
    return src


# ---------------------------------------------------------------------------
# ★ 两套字母表的桥接（这不是可有可无的装饰，是必需的）
#   SRC.SOURCE_*           = **解析器**来源：devtools_recorder / playwright_script
#                            / native / raw_events —— 描述「数据长什么样」
#   RecordingSession.Source = **会话**来源：manual_upload / extension /
#                            devtools_plugin / cdp / playwright_script
#                            —— 描述「用户从哪个入口拿到它」
#   直接把前者写进 session.source 的后果：
#     · `get_source_display()` 返回英文原值（choices 里没有 ⇒ 无 display）
#     · 前端按 `source=devtools_plugin` 筛选，一条都查不到
#   所以入库前必须过这张表；反之取出来喂给解析器时也要能反向认出来
#   （reverse 侧由 core/recorder/sources.py::normalize_source 的别名表兜住）。
# ---------------------------------------------------------------------------
_SESSION_SOURCE_BY_REC = {
    SRC.SOURCE_DEVTOOLS: RecordingSession.Source.DEVTOOLS_PLUGIN,
    SRC.SOURCE_PLAYWRIGHT_SCRIPT: RecordingSession.Source.PLAYWRIGHT_SCRIPT,
    SRC.SOURCE_NATIVE: RecordingSession.Source.EXTENSION,
    SRC.SOURCE_RAW: RecordingSession.Source.MANUAL_UPLOAD,
}


def _session_source_from(rec_source, fallback=None):
    """解析器来源 → 会话来源（认不出来就落到手动上传）。"""
    return _SESSION_SOURCE_BY_REC.get(rec_source) or fallback \
        or RecordingSession.Source.MANUAL_UPLOAD


def _normalize(data, source=None):
    """调用归一化引擎。异常统一转成可读 400 —— 这是用户最容易撞到的一层。"""
    try:
        events, meta = SRC.normalize_source(data, source)
    except ValueError as e:
        raise RecordingImportError(str(e))
    except Exception as e:
        logger.warning('[REC] 归一化失败: %s', traceback.format_exc())
        raise RecordingImportError('录制数据解析失败：%s' % e)
    if not events:
        raise RecordingImportError(
            '没能从这份数据里解析出任何操作。请确认导出的是'
            '「Chrome DevTools Recorder 的 JSON」或「Playwright codegen 生成的脚本」。')
    try:
        ir = NZ.build_ir(events, meta)
    except Exception as e:
        logger.warning('[REC] IR 构建失败: %s', traceback.format_exc())
        raise RecordingImportError('操作序列归一化失败：%s' % e)
    return events, meta, ir


# ---------------------------------------------------------------------------
# ★★ 原始录制数据的脱敏（P0 级，实测发现的真缺陷）
#
# 背景：`raw_payload` 的设计意图是「留证据，出问题可回溯」。但录制数据里
#       必然含用户在登录框里敲的**明文账号密码**。原样入库的后果：
#         · 明文凭据永久留在数据库（备份、快照、导出全会带走）
#         · 任何一个能读会话的用户都能看到（平台是多租户/多项目的）
#         · 用户完全无感 —— 他以为「只是导入了录制」
#       实测：`SELECT ... FROM tb_recording_session WHERE raw_payload LIKE '%<密码>%'`
#       命中 1 条，即已真实发生。
#
# 修法：入库前做脱敏，而不是放弃存原文。
#       证据的价值在「动作序列 / 选择器 / 顺序 / 元素线索」，**值本身不参与定位**，
#       抹掉值几乎不损失排查能力；反之抹掉整份原文会真的让问题无法复现。
#       脱敏后在 raw_payload 上打 `redacted: true` + 计数，取证时一眼能看出
#       「这里被有意抹过」，不会被误当成「录制本来就没有值」。
# ---------------------------------------------------------------------------
REDACTED = '***REDACTED***'

# ① 键名命中即脱敏（无论值是什么）
_SENSITIVE_KEY_RE = re.compile(
    r'(pass(word|wd)?|pwd|secret|token|authorization|cookie|session|'
    r'api[_-]?key|access[_-]?key|private[_-]?key|credential)', re.I)

# ② 元素线索命中即把同一层的 value 脱敏（与 core/recorder/normalizer 的
#    敏感判定思路一致：线索在看得到名字的地方）
_SENSITIVE_HINT_RE = re.compile(
    r'(密码|口令|password|passwd|pwd|secret|token|密钥|凭据|credential)', re.I)

# ③ 参与「线索文本」的键（和 normalizer._field_haystack 保持同一批）
_HINT_KEYS = ('target', 'name', 'id', 'placeholder', 'aria_label', 'aria-label',
              'title', 'data-testid', 'autocomplete', 'key', 'label', 'text')

# 字符串字面量（供脚本文本逐行脱敏用）
_STR_LITERAL_RE = re.compile(r"""(['"`])(?:\\.|(?!\1).)*\1""")


def _hint_text(obj):
    """把一个 dict 里能说明「这个元素是什么」的文本拼起来。"""
    parts = []
    for k in _HINT_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and v:
            parts.append(v)
    sel = obj.get('selectors')
    if sel:
        try:
            parts.append(json.dumps(sel, ensure_ascii=False))
        except (TypeError, ValueError):
            parts.append(str(sel))
    return ' '.join(parts)


def _redact_obj(data, depth=0):
    """递归脱敏。返回 (脱敏后的数据, 抹掉的值的个数)。"""
    if depth > 15:
        return data, 0
    if isinstance(data, dict):
        hit = bool(_SENSITIVE_HINT_RE.search(_hint_text(data)))
        n = 0
        out = {}
        for k, v in data.items():
            if _SENSITIVE_KEY_RE.search(str(k)):
                if isinstance(v, (dict, list)):
                    # 整个容器都可能是凭据结构，只留形状不留内容
                    out[k] = {'_redacted': True}
                else:
                    out[k] = REDACTED
                n += 1
                continue
            if k == 'value' and hit and not isinstance(v, (dict, list)):
                out[k] = REDACTED
                n += 1
                continue
            nv, sub = _redact_obj(v, depth + 1)
            out[k] = nv
            n += sub
        return out, n
    if isinstance(data, list):
        n = 0
        out = []
        for x in data:
            nx, sub = _redact_obj(x, depth + 1)
            out.append(nx)
            n += sub
        return out, n
    return data, 0


def _redact_text(text):
    """脚本文本（Playwright codegen）：逐行脱敏。

    ★ 为什么逐行而不是整段丢弃：一份录制的 script 可能几百行，
      只有一行是 `.fill('#password', '...')`。整段丢会让「原件不可回溯」，
      逐行替换能把损失压到最小。
    """
    lines = text.split('\n')
    n = 0
    for i, line in enumerate(lines):
        if not _SENSITIVE_HINT_RE.search(line):
            continue
        new, cnt = _STR_LITERAL_RE.subn("'%s'" % REDACTED, line)
        if cnt == 0:
            # 线索在，但其实没有字符串字面量可替 —— 保守起见整行抹掉
            lines[i] = '// [已脱敏：该行疑似包含凭据] ' + line[:40]
            n += 1
        else:
            lines[i] = new
            n += cnt
    return '\n'.join(lines), n


def _redact(payload):
    """统一入口：返回 (脱敏后的 payload, 抹掉的个数)。"""
    if isinstance(payload, str):
        return _redact_text(payload)
    try:
        return _redact_obj(payload)
    except Exception:  # 结构太怪就整体不存，宁可少证据也不留明文
        logger.warning('[REC] raw_payload 脱敏失败，改为不存原文: %s',
                       traceback.format_exc())
        return None, -1


def _store_payload(session, source, payload, extra=None):
    """把原始数据与来源写进 `raw_payload`（**证据**：出问题时可回溯）。

    ★ 先脱敏再入库：见上方 `_redact` 的说明 —— 原文里必然含明文凭据，
      原样入库是 P0 级安全问题（实测已发生）。
    超长时降级为「只留规范事件流」—— 原文是证据，但证据不能把数据库压垮。
    """
    payload, redacted_n = _redact(payload)
    if isinstance(payload, dict) and payload.get('redacted') is True and redacted_n == -1:
        redacted_n = 0

    raw = {'source': source, 'payload': payload}
    if redacted_n:
        raw['redacted'] = True
        raw['redacted_count'] = redacted_n
        raw['redacted_note'] = (
            '录制原文中识别为凭据的字段已抹为 %s（保留动作序列与选择器，仅去掉值）。'
            '值不参与元素定位，故不影响问题复现。' % REDACTED)
    if extra:
        raw.update(extra)
    try:
        size = len(json.dumps(raw, ensure_ascii=False))
    except (TypeError, ValueError):
        size = 0
    if size > MAX_RAW_PAYLOAD_CHARS:
        raw = {
            'source': source,
            'payload': None,
            'truncated': True,
            'truncated_size': size,
            'note': '原始数据超过 %d 字符，未存入数据库（未落入会话的事件流仍可用）'
                    % MAX_RAW_PAYLOAD_CHARS,
            'redacted': bool(redacted_n),
        }
        if extra:
            raw.update(extra)
    session.raw_payload = raw
    return raw


# ---------------------------------------------------------------------------
# 1) 创建会话
# ---------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recording_session_create(request):
    """创建录制会话。

    请求（JSON 或 form）:
      project_id 必填；name / source / case_id / start_url 可选
    返回:
      {session_id, name, token, status, status_display, source, source_display}
    """
    project_id = request.data.get('project_id')
    if not project_id:
        return Response(data={'detail': '缺少参数 project_id'}, status=400)
    project_obj = Project.objects.filter(id=project_id, is_delete=False).first()
    if project_obj is None:
        return Response(data={'detail': '项目 %s 不存在或已删除' % project_id}, status=400)

    case_obj = None
    case_id = request.data.get('case_id')
    if case_id:
        case_obj = Case.objects.filter(id=case_id, is_delete=False).first()
        if case_obj is None:
            return Response(data={'detail': '用例 %s 不存在或已删除' % case_id}, status=400)
        if case_obj.type != Case.FunctionCaseType.WEB_UI:
            return Response(data={'detail': '录制只能挂到「Web自动化」用例，当前是「%s」'
                                          % case_obj.get_type_display()}, status=400)

    source = (request.data.get('source') or RecordingSession.Source.MANUAL_UPLOAD).strip()
    if source not in [c[0] for c in RecordingSession.Source.choices]:
        return Response(data={'detail': '不支持的录制来源「%s」' % source}, status=400)

    name = (request.data.get('name') or '').strip() or ('录制_%s' % time.strftime('%m%d_%H%M%S'))
    session = RecordingSession.objects.create(
        name=name[:128],
        project_id=project_obj.id,
        case=case_obj,
        status=RecordingSession.Status.RECORDING,
        source=source,
        start_url=(request.data.get('start_url') or '').strip()[:512],
        raw_payload={'source': source, 'payload': {'events': []}},
        ir_payload={},
        stats={},
        ai_meta={},
        # 扩展侧上传凭据：会话级、可随时作废，避免扩展持有用户长期令牌
        token=uuid.uuid4().hex,
        create_by_id=_user_id(request), update_by_id=_user_id(request),
    )
    return Response(data={
        'session_id': session.id,
        'name': session.name,
        'token': session.token,
        'status': session.status,
        'status_display': session.get_status_display(),
        'source': session.source,
        'source_display': session.get_source_display(),
    }, status=200)


# ---------------------------------------------------------------------------
# 2) 会话列表
# ---------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recording_session_list(request):
    """会话列表（履历页）。

    查询参数: project_id / status / case_id / source / keyword(名称模糊) / page / size
    ★ 分页参数是 `size`（不是 page_size），越界会被分页器吞成 {count:0, results:[]}。
    """
    qs = RecordingSession.objects.filter(is_delete=False).select_related(
        'project', 'case').order_by('-create_time', '-id')
    project_id = request.query_params.get('project_id')
    if project_id:
        qs = qs.filter(project_id=project_id)
    case_id = request.query_params.get('case_id')
    if case_id:
        qs = qs.filter(case_id=case_id)
    status_v = request.query_params.get('status')
    if status_v not in (None, ''):
        qs = qs.filter(status=status_v)
    source_v = request.query_params.get('source')
    if source_v:
        qs = qs.filter(source=source_v)
    kw = (request.query_params.get('keyword') or '').strip()
    if kw:
        qs = qs.filter(Q(name__icontains=kw) | Q(start_url__icontains=kw))

    paginator = BasePageNumberPagination()
    page = paginator.paginate_queryset(qs, request)
    ser = RecordingSessionListSerializer(page, many=True)
    return paginator.get_paginated_response(ser.data)


# ---------------------------------------------------------------------------
# 3) 会话详情
# ---------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recording_session_detail(request, session_id):
    session = RecordingSession.objects.filter(id=session_id, is_delete=False).first()
    if session is None:
        return Response(data={'detail': '录制会话 %s 不存在或已删除' % session_id}, status=404)
    ser = RecordingSessionSerializer(session)
    payload = dict(ser.data)
    payload['summary'] = NZ.summarize(session.ir_payload or {})
    return Response(data=payload, status=200)


# ---------------------------------------------------------------------------
# 4) 事件增量推送
# ---------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def recording_session_events(request, session_id):
    """把一批录制事件追加到会话。

    ★ 为什么优先 multipart：`DATA_UPLOAD_MAX_MEMORY_SIZE`（2.5MB）只卡 JSON body，
      事件包一旦超限，Django 在框架层就返 400 了，视图拿不到任何信息，
      用户只看到「请求失败」。multipart 不受该限制。

    请求:
      file | events | payload  —— 三选一
      append  —— 默认 true；false 表示整批覆盖（调试重录用）
      source  —— 可选，首包建议显式给，后续可省
    """
    session = RecordingSession.objects.filter(id=session_id, is_delete=False).first()
    if session is None:
        return Response(data={'detail': '录制会话 %s 不存在或已删除' % session_id}, status=404)
    if session.status == RecordingSession.Status.DISCARDED:
        return Response(data={'detail': '该会话已丢弃，不能再写入事件'}, status=400)

    data, file_name = _read_upload(request)
    if data is None:
        return Response(data={'detail': '没有收到事件数据（请用 file 或 events 字段提交）'},
                        status=400)

    source = _source_from_request(request, file_name) or (session.raw_payload or {}).get('source')
    try:
        events, meta = SRC.normalize_source(data, source)
    except ValueError as e:
        return Response(data={'detail': str(e)}, status=400)
    except Exception as e:
        logger.warning('[REC] 事件包解析失败: %s', traceback.format_exc())
        return Response(data={'detail': '事件包解析失败：%s' % e}, status=400)

    # ==================== P4 幂等闸门（断网补传不重复） ====================
    # ★ 为什么必须做：`append=true`（默认）是**追加**语义，客户端重试一批事件就会
    #   重复写入一次。实施计划 §07 里写的「端点已是幂等设计」是**错的**，这里补上。
    #
    #   幂等键 = (session_id, seq)：丢弃 `seq <= last_seq` 的条目，再推进 last_seq。
    #
    # ★★ 为什么幂等键必须看**原始入参**、不能看归一化后的事件（实测踩到的坑）：
    #     core/recorder/sources.py::normalize_source 会给**没有 seq 的事件自动补 seq**
    #     （按序号 1,2,3…）。若据此去重，那么旧客户端 / 手工导入 / 其它解析器的批次
    #     会被整体判定成「重放」而**被丢光** —— 一次静默的数据丢失，而且离线检查
    #     看源码根本发现不了（只有真跑一次才会暴露）。
    #   ⇒ 判据：`原始入参`里**每条**事件都带 seq 才启用去重；否则走旧行为。
    def _raw_event_list(d):
        if isinstance(d, dict):
            for _k in ('events', 'steps', 'actions'):
                _v = d.get(_k)
                if isinstance(_v, list):
                    return _v
        elif isinstance(d, list):
            return d
        return []

    _raws = _raw_event_list(data)
    _has_seq = bool(_raws) and all(
        isinstance(_x, dict) and _x.get('seq') is not None for _x in _raws)

    append = str(request.data.get('append', 'true')).lower() not in ('false', '0', 'no')
    _last = int(session.last_seq or 0)
    _skipped = 0
    if append and _has_seq:
        _kept = []
        _max = _last
        for _e in events:
            _s = _e.get('seq') if isinstance(_e, dict) else None
            if _s is None:
                _kept.append(_e)
                continue
            try:
                _s = int(_s)
            except (TypeError, ValueError):
                _kept.append(_e)
                continue
            if _s <= _last:
                _skipped += 1
                continue
            _kept.append(_e)
            if _s > _max:
                _max = _s
        events = _kept
        if _max != _last:
            session.last_seq = _max
    elif append:
        # 旧客户端（事件不带 seq）：**完全不去重、不动 last_seq**，
        # 行为与改造前逐字一致 —— 新旧客户端可以混用同一套接口。
        pass
    else:
        # 整批覆盖（调试重录）：不去重，并把 last_seq 重置为本批最大值
        # （本批无 seq 语义时归 0，与"没有幂等基线"等价）
        _seqs = []
        if _has_seq:
            for _e in events:
                _s = _e.get('seq') if isinstance(_e, dict) else None
                if _s is None:
                    continue
                try:
                    _seqs.append(int(_s))
                except (TypeError, ValueError):
                    pass
        session.last_seq = max(_seqs) if _seqs else 0

    raw = dict(session.raw_payload or {})
    old = (raw.get('payload') or {})
    old_events = old.get('events') if isinstance(old, dict) else None
    if append and isinstance(old_events, list):
        merged = list(old_events) + list(events)
    else:
        merged = list(events)

    if len(merged) > MAX_EVENTS_PER_SESSION:
        return Response(data={
            'detail': '本会话事件数将达到 %d 条，超过上限 %d。请结束当前会话后新建一个，'
                      '或调大 MAX_EVENTS_PER_SESSION。' % (len(merged), MAX_EVENTS_PER_SESSION)
        }, status=400)

    # ★ raw_payload['source'] 一律写**解析器侧**值（meta['source']）：
    #   finish() 会把它原样喂回 SRC.normalize_source()，两侧混写会让
    #   「取出来再解析」这条路径依赖别名表的容错 —— 别名表是兜底，不该是主路径。
    _store_payload(session, meta.get('source') or SRC.SOURCE_NATIVE,
                   {'events': merged, 'meta': meta},
                   extra={'file_name': file_name} if file_name else None)
    if session.status == RecordingSession.Status.FINISHED:
        session.status = RecordingSession.Status.RECORDING
    session.save(update_fields=['raw_payload', 'status', 'update_time', 'last_seq'])
    return Response(data={
        'session_id': session.id,
        'received': len(events),
        # ★ skipped>0 就是「这一批是重放的」最直接证据 —— 客户端据此停止重发
        'skipped': _skipped,
        'last_seq': int(session.last_seq or 0),
        'total': len(merged),
        'source': meta.get('source') or SRC.SOURCE_NATIVE,
    }, status=200)


# ---------------------------------------------------------------------------
# 5) 结束并归一化
# ---------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recording_session_finish(request, session_id):
    """结束录制 → 跑归一化 → 落 `ir_payload`。

    请求: options(可选) —— 透传给 core/recorder/normalizer.DEFAULT_OPTIONS 的覆盖项
    返回: {session_id, summary, ir}
    """
    session = RecordingSession.objects.filter(id=session_id, is_delete=False).first()
    if session is None:
        return Response(data={'detail': '录制会话 %s 不存在或已删除' % session_id}, status=404)

    raw = session.raw_payload or {}
    payload = raw.get('payload')
    source = raw.get('source')
    if not payload:
        return Response(data={'detail': '该会话没有可用的录制数据（raw_payload 为空或已截断）'},
                        status=400)

    # ★ 零事件必须**报错**，不能静默生成一个空 IR（v0.20.3 修复）
    #   原行为：扩展传不上事件时（见 _try_parse_ndjson 的说明），
    #   raw_payload.payload 仍是建会话时写的 {'events': []} —— 它是 truthy，
    #   于是一路走到 build_ir([]) 返回一个 0 步的 IR + HTTP 200。
    #   用户看到「已生成 IR：步骤 0 条」，会以为"生成失败但没提示"，
    #   而真正的错误（上传 400）早就被 popup 当成"最近错误"一闪而过了。
    #   语义上「一个事件都没收到」不是成功，必须显式说出来。
    if isinstance(payload, dict) and not (
            payload.get('events') or payload.get('actions') or payload.get('steps')
            or payload.get('kind') or payload.get('type')):
        return Response(data={
            'detail': '该会话还没有收到任何录制事件，无法生成步骤。'
                      '①请在页面上正常操作几下（点击/输入）后再点「结束并生成」；'
                      '②若插件面板显示「最近错误」，说明事件上传失败，请把该错误反馈给开发。',
        }, status=400)

    options = request.data.get('options') or {}
    if not isinstance(options, dict):
        return Response(data={'detail': 'options 必须是对象'}, status=400)

    # ★★★ 2026-10-15 修：用**库存形状**决定解析器，而不是用 `raw_payload['source']` 的声明值。
    #
    #   为什么：`raw_payload['payload']` 存的一律是**归一化之后**的形状
    #   （`{'events': [...], 'meta': {...}}`，见 recording_session_events 的
    #   `_store_payload(session, meta['source'], {'events': merged, 'meta': meta})`），
    #   而 `raw_payload['source']` 记的是**原始上传数据**的来源（它同时要给
    #   `/events/` 的增量批次做来源回退，所以不能改成别的值）。
    #   两者对不上：拿「原始数据的来源」去解析「已归一化的数据」，只有
    #   native / raw_events 能过 ——
    #     · devtools_recorder ⇒ 抛「DevTools Recorder 数据缺少 steps 数组」
    #     · playwright_script ⇒ 抛「Playwright 脚本必须是文本」
    #   于是 finish 直接 400，而这句话与真实原因（"库存形状 ≠ 声明来源"）
    #   毫无关联 —— 与「两套字母表」那一族缺陷同形，排查成本极高。
    #   实测复现：/events/ 显式声明 source=devtools_recorder 后 finish 必 400。
    #
    #   现在按形状分派：是归一化形状 ⇒ 用 native 解析器；否则（parse 直存的
    #   原始文件）沿用声明的来源。已交付的扩展路径行为**逐字不变**（它本来就发 native）。
    effective_source = source
    if (isinstance(payload, dict)
            and isinstance(payload.get('events'), list)
            and isinstance(payload.get('meta'), dict)):
        effective_source = SRC.SOURCE_NATIVE

    try:
        events, meta = SRC.normalize_source(payload, effective_source)
        ir = NZ.build_ir(events, meta, options or None)
    except Exception as e:
        logger.warning('[REC] 归一化失败: %s', traceback.format_exc())
        return Response(data={'detail': '归一化失败：%s' % e}, status=400)

    session.ir_payload = ir
    session.stats = ir.get('stats') or {}
    session.status = RecordingSession.Status.FINISHED
    meta_ir = ir.get('meta') or {}
    if not session.start_url and meta_ir.get('start_url'):
        session.start_url = str(meta_ir['start_url'])[:512]
    session.save(update_fields=['ir_payload', 'stats', 'status', 'start_url', 'update_time'])
    return Response(data={
        'session_id': session.id,
        'status': session.status,
        'status_display': session.get_status_display(),
        'summary': NZ.summarize(ir),
        'ir': ir,
    }, status=200)


# ---------------------------------------------------------------------------
# 6) 丢弃会话
# ---------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recording_session_discard(request, session_id):
    session = RecordingSession.objects.filter(id=session_id, is_delete=False).first()
    if session is None:
        return Response(data={'detail': '录制会话 %s 不存在或已删除' % session_id}, status=404)
    session.status = RecordingSession.Status.DISCARDED
    session.update_by_id = _user_id(request)
    session.save(update_fields=['status', 'update_by_id', 'update_time'])
    return Response(data={'session_id': session.id, 'status': session.status,
                          'status_display': session.get_status_display()}, status=200)


# ---------------------------------------------------------------------------
# 7) AI 增强（P2）—— A1 定位器优化 / A2 断言补全 / A3 用例命名
# ---------------------------------------------------------------------------
AI_SCOPES = ai_enhance.SCOPES


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recording_session_ai_enhance(request, session_id):
    """对 IR 做 AI 增强（P2）：A1 定位器优化 / A2 断言补全 / A3 用例命名。

    请求:
      scopes        ['locator'|'assertion'|'naming']  要跑哪几件事（**必填、不默认**）
      ai_config_id  int                               可选，指定项目下的 AI 配置
    返回（**永不 4xx**）:
      {session_id, scopes, rule:{added, assertions, report},
       locator:[...], assertion:[...], naming:[...],
       dropped:[...], ai_meta:{used_calls, limit, calls}, ai_error}

    ★ 三条设计决策（改动前先读 `ai_enhance.py` 模块 docstring）
      1) **永远 200**：AI 不可用 / 超时 / 输出被截断，统统降级成
         「规则产物 + `ai_error`」。录制 IR 本身已是有效产物，
         AI 失败绝不能让用户以为录制坏了 —— 这是平台上 HAR 归因踩过的坑
         （返 5xx 会让前端把「AI 没跑成」显示成「功能不可用」）。
      2) **只建议不落库**：本视图**不写** `session.ir_payload`（唯一的例外是
         `ai_meta` 记账）。所有建议原样回给审阅台，由人勾选后走 `patch/`。
         这样「AI 建议未采纳 ⇒ 元素库零改动」是**结构上成立**的，而不是靠自觉。
      3) **scopes 必填**：三个 scope 都不自动跑（设计方案 §05 明确要求），
         缺参数属于调用方契约错误，这里返 400 是合理的 —— 它不是「AI 失败」。
    """
    session = RecordingSession.objects.filter(id=session_id, is_delete=False).first()
    if session is None:
        return Response(data={'detail': '录制会话 %s 不存在或已删除' % session_id}, status=404)

    body = request.data if isinstance(request.data, dict) else {}
    scopes = body.get('scopes')
    if isinstance(scopes, str):
        scopes = [x.strip() for x in scopes.split(',') if x.strip()]
    if not isinstance(scopes, list) or not scopes:
        return Response(data={
            'detail': '缺少参数 scopes。可选：%s —— 三个 AI 动作都不自动触发，'
                      '必须显式指定要跑哪几个。' % '、'.join(AI_SCOPES),
        }, status=400)
    bad = [s for s in scopes if s not in AI_SCOPES]
    if bad:
        return Response(data={'detail': '不支持的 scope：%s（可选：%s）'
                                      % ('、'.join(map(str, bad)), '、'.join(AI_SCOPES))},
                        status=400)

    ir = session.ir_payload
    if not isinstance(ir, dict) or not isinstance(ir.get('actions'), list):
        return Response(data={'detail': '该会话还没有 IR。请先解析录制文件'
                                        '（POST /recording/parse/）。'}, status=400)

    ai_config_id = body.get('ai_config_id')
    try:
        ai_config_id = int(ai_config_id) if ai_config_id not in (None, '') else None
    except (TypeError, ValueError):
        return Response(data={'detail': 'ai_config_id 必须是整数'}, status=400)

    try:
        payload = ai_enhance.enhance(session, session.project_id, scopes, ai_config_id)
    except Exception as e:                      # noqa: BLE001
        # 兜底：连编排本身都炸了，也必须是「有内容的 200 + ai_error」，
        # 而不是 500 —— 否则前端会渲染成「平台挂了」。
        logger.exception('[REC-AI] 编排异常 session=%s', session_id)
        payload = {
            'session_id': session.id,
            'scopes': scopes,
            'rule': {'added': [], 'assertions': [], 'report': {}},
            'locator': [], 'assertion': [], 'naming': [], 'dropped': [],
            'ai_meta': {'used_calls': None, 'limit': ai_enhance.MAX_AI_CALLS_PER_SESSION,
                        'calls': []},
            'ai_error': 'AI 增强执行异常：%s' % e,
        }
    return Response(data=payload)


# ---------------------------------------------------------------------------
# 7b) 审阅台编辑（P1）—— **只改 IR，不落库**
# ---------------------------------------------------------------------------
def _norm_patch_locator(loc):
    """把审阅台传来的定位器收敛成合法形状。

    ★ `by` 必须收敛到 8 个合法值：底座 `_build_locator` 只认它们，
      不在表里的会被当成裸 CSS 用（历史上 `aria`/`pierce` 就是这样坏掉的）。
    """
    loc = loc if isinstance(loc, dict) else {}
    by = str(loc.get('by') or '').strip().lower()
    if by not in ELEMENT_BY_CHOICES:
        by = 'css'
    value = str(loc.get('value') or '')
    opts = loc.get('opts')
    return {'by': by, 'value': value, 'opts': opts if isinstance(opts, dict) else {}}


def _same_locator_pair(cand, by, value):
    if not isinstance(cand, dict):
        return False
    return (str(cand.get('by') or '').strip().lower() == by
            and str(cand.get('value') or '') == value)


def _assertion_key(spec):
    """断言的内容指纹，用于「删除断言」时定位目标。

    ★ 为什么是三元组而不是数组下标：见 `drop_assertions` 分支的说明。
    ★ `expect` 统一 str()：录制侧可能给数字 1，审阅台回传字符串 '1'，
      不归一化就会被判成「没匹配到」而静默删不掉。
    """
    spec = spec if isinstance(spec, dict) else {}
    exp = spec.get('expect')
    return (
        str(spec.get('method') or ''),
        str(spec.get('extract_keyword') or ''),
        '' if exp is None else str(exp),
    )


def _recount_ir(ir):
    """按 `enabled` 重算统计块（审阅台改完之后必须重算，否则列表页数字骗人）。

    ★ 元素去重口径必须与**解析期**和**落库期**三方一致，否则审阅台会出现
      「我只改了一个定位器，元素数怎么自己变了」这种不可解释的现象：

        · 解析期（normalizer）：`elements_unique = len(refs)`，refs 以
          `element.element_ref` 为键；
        · 落库期（importer._ElementResolver）：等级 1 用 `element_ref`，
          等级 2 退化用 `(name, by, value)`；
        · 本函数（审阅台重算）：**必须**同口径。

      曾经的实现读的是 `el.get('ref')` —— 而 IR 里的键名是 **`element_ref`**，
      于是这个分支永远取不到值，一路退化到 `'by:value'` 拼串。而
      `_element_ref()` 的指纹是 **`by|value|opts`** 三重，`opts` 不能丢：
      role 类候选的 value 只是角色名（textbox/button），真正的区分度全在
      `opts.name`（无障碍名）上。丢掉 opts 就会把页面上所有文本框算成同一个
      元素 —— 数字对不上，且「改一下定位器元素数就跳」。
    """
    acts = [a for a in (ir.get('actions') or []) if isinstance(a, dict)]
    kept = [a for a in acts if a.get('enabled', True) is not False]
    refs = set()
    for a in kept:
        el = a.get('element') or {}
        # 键名是 element_ref（不是 ref）—— 见 normalizer._make_action()
        r = el.get('element_ref')
        if not r:
            locs = el.get('locators') or []
            if locs and isinstance(locs[0], dict):
                # 退化口径对齐 importer._ElementResolver 的第二级缓存 key，
                # 这样面板上的数字就等于「落库实际会新建的元素数」
                l0 = locs[0]
                r = '%s|%s|%s' % (el.get('name') or '', l0.get('by'), l0.get('value'))
        if r:
            refs.add(r)
    stats = ir.setdefault('stats', {})
    stats['kept_actions'] = len(kept)
    stats['manual_off'] = len(acts) - len(kept)
    stats['elements_unique'] = len(refs)
    stats['assertions'] = sum(len(a.get('assertions') or []) for a in kept)
    stats['needs_review'] = [a.get('seq') for a in kept if a.get('needs_review')]
    return stats


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def recording_session_patch(request, session_id):
    """审阅台编辑：**只改 `ir_payload`，不落库**。

    ★ 为什么「编辑不落库、落库是一次原子动作」（设计决策，别改）
      录制天然是脏的：混着 hover、内部跳转、误点。用户要反复试
      「勾掉这几条 / 换个定位器 / 把值提成变量」。如果每试一次就写一遍
      `tb_step`，用例里会堆满半成品步骤，且**无法撤销** —— 用户就再也不敢改了。
      所以：编辑只动 IR（绝对覆盖式，天然幂等、可反复），
      `/recording/import/` 才是唯一真正写库的动作。

    请求（全部可选，只给要改的）:
      keep_seqs    [int]  要保留的动作 seq；给了就以它为准，其余置 enabled=False
      enable_seqs  [int]  显式启用的 seq（与 keep_seqs 二选一，或叠加）
      order        [int]  新顺序；未列出的按原相对顺序排在后面
      actions      {"<seq>": {...}}  按 seq 覆盖：
                     enabled  bool                       启停
                     desc     str                        步骤描述（限 100 字符）
                     locator  {by,value,opts}            改主定位器（自动提到候选链首位并标记 pinned）
                     value    {arg,kind,var_name,value}  改参数值/变量
                              arg 缺省 'value'（fill / select_option 的值就在这个键上）
      assertions   [{seq, method, expect, extract_keyword, extract_args, rule}]
                                                        人工新增断言（**追加**语义）
      drop_assertions  [{seq, method, expect, extract_keyword}]
                                                        按内容指纹删除断言
                                                        （**删除**语义，与上一项分开）
      name         str                                    会话名（限 128）
    返回:
      {session_id, status, status_display, summary, ir, changed, patch_notes}
    """
    session = RecordingSession.objects.filter(id=session_id, is_delete=False).first()
    if session is None:
        return Response(data={'detail': '录制会话 %s 不存在或已删除' % session_id}, status=404)

    ir = session.ir_payload
    if not isinstance(ir, dict) or not isinstance(ir.get('actions'), list):
        return Response(data={'detail': '该会话还没有可编辑的 IR。请先解析录制文件'
                                        '（POST /recording/parse/）。'}, status=400)

    body = request.data
    acts = [a for a in ir['actions'] if isinstance(a, dict)]
    changed = []
    notes = []

    # ---- 1) 启停 ----
    keep = body.get('keep_seqs')
    if isinstance(keep, str):
        keep = [x for x in keep.replace(' ', '').split(',') if x]
    if isinstance(keep, (list, tuple)):
        keep_set = set()
        for x in keep:
            try:
                keep_set.add(int(x))
            except (TypeError, ValueError):
                pass
        for a in acts:
            a['enabled'] = a.get('seq') in keep_set
        changed.append('keep_seqs=%d 条保留' % len(keep_set))

    enable = body.get('enable_seqs')
    if isinstance(enable, str):
        enable = [x for x in enable.replace(' ', '').split(',') if x]
    if isinstance(enable, (list, tuple)):
        for x in enable:
            try:
                sx = int(x)
            except (TypeError, ValueError):
                continue
            for a in acts:
                if a.get('seq') == sx:
                    a['enabled'] = True
                    changed.append('启用 seq=%s' % sx)

    # ---- 2) 顺序（稳定排序：未列出的保持原相对顺序排在后面）----
    order = body.get('order')
    if isinstance(order, str):
        order = [x for x in order.replace(' ', '').split(',') if x]
    if isinstance(order, (list, tuple)) and order:
        idx = {}
        for i, x in enumerate(order):
            try:
                idx[int(x)] = i
            except (TypeError, ValueError):
                continue
        if idx:
            base = len(idx)
            acts.sort(key=lambda a: idx.get(
                a.get('seq'),
                base + (a.get('seq') if isinstance(a.get('seq'), int) else 0)))
            changed.append('order=%d 条' % len(idx))

    # ---- 3) 按 seq 覆盖字段 ----
    edits = body.get('actions')
    if isinstance(edits, str):
        try:
            edits = json.loads(edits)
        except ValueError:
            return Response(data={'detail': 'actions 不是合法的 JSON'}, status=400)
    if isinstance(edits, dict):
        by_seq = {a.get('seq'): a for a in acts}
        for k, patch in edits.items():
            try:
                seq = int(k)
            except (TypeError, ValueError):
                continue
            act = by_seq.get(seq)
            if act is None:
                notes.append({'level': 'warn', 'message': '动作 seq=%s 不存在，已忽略' % k})
                continue
            if not isinstance(patch, dict):
                continue

            if 'enabled' in patch:
                act['enabled'] = bool(patch['enabled'])
                changed.append('seq=%s enabled=%s' % (seq, act['enabled']))

            if 'desc' in patch:
                act['desc'] = str(patch['desc'] or '')[:100]
                changed.append('seq=%s desc' % seq)

            if 'locator' in patch:
                loc = _norm_patch_locator(patch.get('locator'))
                if loc['value']:
                    el = act.setdefault('element', {})
                    locs = [c for c in (el.get('locators') or []) if isinstance(c, dict)]
                    # 被选中的候选提到首位并标记 pinned —— pinned 的意义是
                    # 「人工确认过的定位器」，将来 P3 回退链不再用打分自动改写它。
                    head = dict(loc)
                    head['source'] = 'manual'
                    head['pinned'] = True
                    head['score'] = max([c.get('score') or 0 for c in locs] + [0.99])
                    rest = [c for c in locs if not _same_locator_pair(c, loc['by'], loc['value'])]
                    el['locators'] = [head] + rest
                    # 置信度同步拉满：人工选定即视为可信，审阅台的琥珀色标记随之消失
                    act['confidence'] = 1.0
                    act['needs_review'] = False
                    # ★ 刻意**不**重算 element_ref（设计决策，别当成漏改）：
                    #   element_ref 是「同一元素在本次录制里的身份」，由解析期
                    #   `by|value|opts` 指纹定下。审阅台改的只是「用哪个定位器找它」，
                    #   元素身份没变。保持 ref 不变带来两个好处：
                    #     1) 同一元素的另一处出现（未改）仍与之合并成一条元素记录，
                    #        不会因为改了一处就裂成两条；
                    #     2) 旧定位器会被 importer._merge_alternatives 收进备选链，
                    #        等于白拿一个回退候选（P3 自愈正好用它）。
                    #   若将来改成重算，`_recount_ir` 与解析期的元素数会对不上，
                    #   用户会看到「只改了一处，元素数 +1」。
                    changed.append('seq=%s locator=%s:%s' % (seq, loc['by'], loc['value'][:40]))
                else:
                    notes.append({'level': 'warn',
                                  'message': 'seq=%s 的 locator 缺少 value，已忽略' % seq})

            if 'value' in patch:
                v = patch.get('value')
                arg = 'value'
                if isinstance(v, dict):
                    arg = str(v.get('arg') or 'value')
                    kind = str(v.get('kind') or 'literal')
                    if kind not in ('literal', 'variable'):
                        kind = 'literal'
                    if kind == 'variable':
                        nv = {'kind': 'variable',
                              'var_name': str(v.get('var_name') or '')[:60]}
                        # 敏感字段保持「不落原文」：前端把 value 传空即维持脱敏
                        if v.get('value') not in (None, ''):
                            nv['value'] = v.get('value')
                    else:
                        nv = {'kind': 'literal', 'value': v.get('value')}
                else:
                    kind = 'literal'
                    nv = {'kind': 'literal', 'value': v}
                args = act.get('args')
                if not isinstance(args, dict):
                    args = {}
                args[arg] = nv
                act['args'] = args
                changed.append('seq=%s %s=%s' % (seq, arg, kind))

    # ---- 4) 人工新增断言 ----
    adds = body.get('assertions')
    if isinstance(adds, str):
        try:
            adds = json.loads(adds)
        except ValueError:
            return Response(data={'detail': 'assertions 不是合法的 JSON'}, status=400)
    if isinstance(adds, list):
        by_seq2 = {a.get('seq'): a for a in acts}
        for spec in adds:
            if not isinstance(spec, dict):
                continue
            try:
                seq = int(spec.get('seq'))
            except (TypeError, ValueError):
                notes.append({'level': 'warn', 'message': '新增断言缺少合法 seq，已忽略'})
                continue
            act = by_seq2.get(seq)
            if act is None:
                notes.append({'level': 'warn',
                              'message': '新增断言指向不存在的 seq=%s，已忽略' % seq})
                continue
            item = {
                'method': str(spec.get('method') or 'check_equal'),
                'expect': spec.get('expect'),
                'extract_keyword': str(spec.get('extract_keyword') or ''),
                'extract_args': spec.get('extract_args') if isinstance(spec.get('extract_args'), dict) else {},
                'rule': 'manual',
                # ★ 人工加的断言 auto 恒为 True：用户已经明确说「这里要断言」，
                #   再把它归到 deferred（待补）等于无视用户的输入。
                'auto': True,
                'brittle': False,
                'manual': True,
            }
            act.setdefault('assertions', []).append(item)
            changed.append('seq=%s 新增断言 %s' % (seq, item['method']))

    # ---- 4.5) 删除断言 ----
    # ★ 为什么需要这个（不是在小题大做）：
    #   录制会自动推导出一批断言，其中相当一部分是**脆弱**的 —— 最典型的是
    #   「元素文本内容」（页面文案一改就红）、以及派生自 hover/内部跳转的伪断言。
    #   审阅台如果只能「新增」不能「删除」，用户面对这些噪音只有两个选择：
    #   要么全留着（用例一改版就批量假失败，很快没人再看报告），
    #   要么关掉整个「自动断言」开关（连真正有价值的 URL 断言一起丢掉）。
    #   两者都是坏结局，所以删除必须是一等能力。
    #
    # ★ 为什么按「内容」匹配而不是按数组下标匹配：
    #   下标依赖「客户端与服务端断言列表逐项一致」这个隐含假设，
    #   一旦有别的入口（如扩展实时推送、AI 补全）动过这个动作的断言，
    #   下标就会错位、删错行，而且**删错了不报错**。内容匹配最差也只是
    #   「删掉了另一条内容完全相同的断言」—— 语义上等价，无害。
    drops = body.get('drop_assertions')
    if isinstance(drops, str):
        try:
            drops = json.loads(drops)
        except ValueError:
            return Response(data={'detail': 'drop_assertions 不是合法的 JSON'}, status=400)
    if isinstance(drops, list):
        by_seq3 = {a.get('seq'): a for a in acts}
        for spec in drops:
            if not isinstance(spec, dict):
                continue
            try:
                seq = int(spec.get('seq'))
            except (TypeError, ValueError):
                notes.append({'level': 'warn', 'message': '删除断言缺少合法 seq，已忽略'})
                continue
            act = by_seq3.get(seq)
            if act is None:
                notes.append({'level': 'warn',
                              'message': '删除断言指向不存在的 seq=%s，已忽略' % seq})
                continue
            cur = [x for x in (act.get('assertions') or []) if isinstance(x, dict)]
            tgt = _assertion_key(spec)
            hit = -1
            for i, x in enumerate(cur):
                if _assertion_key(x) == tgt:
                    hit = i
                    break
            if hit < 0:
                notes.append({'level': 'warn',
                              'message': 'seq=%s 上没有匹配到要删除的断言（可能已被删）' % seq})
                continue
            cur.pop(hit)
            act['assertions'] = cur
            changed.append('seq=%s 删除断言 %s' % (seq, tgt[0]))

    # ---- 5) 会话名 ----
    if body.get('name'):
        session.name = str(body['name']).strip()[:128]
        changed.append('name')

    # ---- 6) 重算统计 + 落盘 ----
    ir['actions'] = acts
    _recount_ir(ir)
    session.ir_payload = ir
    session.stats = ir.get('stats') or {}
    if session.status != RecordingSession.Status.DISCARDED:
        session.status = RecordingSession.Status.REVIEWING
    session.update_by_id = _user_id(request)
    session.save(update_fields=['ir_payload', 'stats', 'status', 'name',
                               'update_by_id', 'update_time'])

    return Response(data={
        'session_id': session.id,
        'name': session.name,
        'status': session.status,
        'status_display': session.get_status_display(),
        'summary': NZ.summarize(ir),
        'ir': ir,
        'changed': changed,
        'patch_notes': notes,
    }, status=200)


# ---------------------------------------------------------------------------
# 8) 录制文件直传解析（P0-④ 主入口）
# ---------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def recording_parse(request):
    """上传一份录制文件 / 粘贴一段录制数据 → 建会话并归一化成 IR。

    ★ 与 `/recording/session/<id>/finish/` 的区别：
      这个端点面对的是「已经录完的一整份文件」（DevTools Recorder 导出 JSON、
      Playwright codegen 脚本），一次到位；finish 面对的是
      「实时流式推事件」的扩展。两者最终都落到同一张表、同一个 IR 结构。

    请求（multipart 优先）:
      file        录制文件（.json / .js / .py …）
      payload     文本形式的数据（与 file 二选一）
      project_id  必填
      name        可选，会话名
      source      可选，强制指定来源
      case_id     可选，目标用例（预绑定）
    返回:
      {session_id, source, summary, ir}
    """
    project_id = request.data.get('project_id')
    if not project_id:
        return Response(data={'detail': '缺少参数 project_id'}, status=400)
    project_obj = Project.objects.filter(id=project_id, is_delete=False).first()
    if project_obj is None:
        return Response(data={'detail': '项目 %s 不存在或已删除' % project_id}, status=400)

    data, file_name = _read_upload(request)
    if data is None:
        return Response(data={'detail': '没有收到录制数据。请选择录制文件（.json / .js），'
                                        '或把内容粘贴到数据框里。'}, status=400)
    if file_name and not file_name.lower().endswith(_ALLOWED_EXT):
        # 只提示不拦截：有些环境导出成 .har / .txt，按内容识别更可靠
        logger.info('[REC] 非常规扩展名的录制文件: %s', file_name)

    source = _source_from_request(request, file_name)
    try:
        events, meta, ir = _normalize(data, source)
    except RecordingImportError as e:
        return Response(data={'detail': str(e)}, status=400)

    case_obj = None
    case_id = request.data.get('case_id')
    if case_id:
        case_obj = Case.objects.filter(id=case_id, is_delete=False).first()
        if case_obj is not None and case_obj.type != Case.FunctionCaseType.WEB_UI:
            case_obj = None

    name = (request.data.get('name') or '').strip()
    if not name:
        base = (meta.get('title') or file_name or '录制').strip()
        name = '%s_%s' % (base[:100], time.strftime('%m%d_%H%M'))
    session = RecordingSession.objects.create(
        name=name[:128],
        project_id=project_obj.id,
        case=case_obj,
        status=RecordingSession.Status.FINISHED,
        # ★ 必须过桥接表：meta['source'] 是解析器侧值（devtools_recorder…），
        #   而 session.source 的 choices 是会话侧值（devtools_plugin…）。
        #   直接写前者 → get_source_display() 失效 + 前端按来源筛选查不到。
        source=_session_source_from(meta.get('source')),
        start_url=str(ir.get('meta', {}).get('start_url') or '')[:512],
        ir_payload=ir,
        stats=ir.get('stats') or {},
        ai_meta={},
        token=uuid.uuid4().hex,
        create_by_id=_user_id(request), update_by_id=_user_id(request),
    )
    _store_payload(session, meta.get('source'), data,
                   extra={'file_name': file_name, 'events_count': len(events)})
    session.save(update_fields=['raw_payload'])

    return Response(data={
        'session_id': session.id,
        'name': session.name,
        'source': session.source,
        'start_url': session.start_url,
        'summary': NZ.summarize(ir),
        'ir': ir,
    }, status=200)


# ---------------------------------------------------------------------------
# 9) IR → 落库
# ---------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recording_import(request):
    """把 IR 落库成用例步骤。

    请求:
      project_id          必填
      session_id          可选 —— 给了就优先用它存好的 IR，并回写 imported_case_id
      ir                  可选 —— 给了就以它为准（审阅台改过之后的版本）
      mode                new_case（默认）/ append_steps
      case_id / case_name / module_id / plant_id / import_assertions
    返回: importer.import_ir 的结果（含跳过明细与待人工补的断言）
    """
    project_id = request.data.get('project_id')
    if not project_id:
        return Response(data={'detail': '缺少参数 project_id'}, status=400)
    project_obj = Project.objects.filter(id=project_id, is_delete=False).first()
    if project_obj is None:
        return Response(data={'detail': '项目 %s 不存在或已删除' % project_id}, status=400)

    mode = (request.data.get('mode') or 'new_case').strip()
    if mode not in MODE_CHOICES:
        return Response(data={'detail': '不支持的模式「%s」，可选：%s'
                                      % (mode, '、'.join(MODE_CHOICES))}, status=400)

    session = None
    session_id = request.data.get('session_id')
    if session_id:
        session = RecordingSession.objects.filter(id=session_id, is_delete=False).first()
        if session is None:
            return Response(data={'detail': '录制会话 %s 不存在或已删除' % session_id}, status=400)

    ir = request.data.get('ir')
    if isinstance(ir, str):
        try:
            ir = json.loads(ir)
        except ValueError:
            return Response(data={'detail': 'ir 不是合法的 JSON'}, status=400)
    if not isinstance(ir, dict):
        ir = (session.ir_payload if session is not None else None) or None
    if not isinstance(ir, dict) or not ir.get('actions'):
        return Response(data={'detail': '没有可落库的 IR。请先上传录制文件解析，'
                                        '或把审阅后的 IR 一并提交。'}, status=400)

    if mode == 'append_steps' and not request.data.get('case_id'):
        return Response(data={'detail': '追加模式必须提供 case_id'}, status=400)

    import_assertions = request.data.get('import_assertions', True)
    if isinstance(import_assertions, str):
        import_assertions = import_assertions.lower() not in ('false', '0', 'no', '')

    try:
        result = import_ir(
            ir=ir,
            project_id=project_obj.id,
            user_id=_user_id(request),
            case_id=request.data.get('case_id'),
            module_id=request.data.get('module_id'),
            plant_id=request.data.get('plant_id'),
            mode=mode,
            case_name=request.data.get('case_name'),
            import_assertions=bool(import_assertions),
            session=session,
        )
    except RecordingImportError as e:
        return Response(data={'detail': str(e)}, status=400)
    except Exception as e:
        logger.error('[REC] 落库失败: %s', traceback.format_exc())
        return Response(data={'detail': '落库失败：%s' % e}, status=500)

    return Response(data=result, status=200)
