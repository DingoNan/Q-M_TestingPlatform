# -*- coding: utf-8 -*-
"""IR → 落库（P0-②）

职责边界（改动前务必先读）
--------------------------------------------------------------------------
· 本模块是录制链路**唯一**的写库入口：元素 / 步骤 / 断言 / 用例变量都在这里落库。
· `core/recorder/` 只做「事件流 → IR」，不碰任何 ORM；本模块只吃 IR，不解析事件流。
  这条边界必须守住 —— 它是「归一化引擎能离线跑完整单测」的前提，也是整套方案里
  唯一能 100% 自动化验证的部分（见 core/recorder/tests/test_normalizer.py）。
· 与 `apps/ai_service/scenario_case_saver.py::_build_web_step` 的关系：
    那边是「LLM 给关键字 + 元素名」，这边是「IR 给关键字 + 定位器候选」。
    两者共用同一套落库契约，所以这里**复用契约**而不是另起一套。

落库契约（改这里之前先确认执行底座没变）
--------------------------------------------------------------------------
1) `Step.func_params` 是**扁平列表** `[{name,value,type,children,parentId}]`；
   `EleObject` 型参数的 value 是**元素 id 的字符串**，运行期由
   `core/com/common.py::func_list_to_dict` 换成 `ElementSerializers(...).data`。
   ⇒ 元素必须先落库拿到 id，才能建步骤。
2) `Step.check_params` 是 `[{id,method,exp_value,act_value,andOr}]`；
   `act_value` 里的 `${stepResponse.<case_step_id>.funcReturn}` 由
   `replace_params_class_data` 在运行期替换，**替换结果恒为字符串**
   （内部是 `str(extra_data)`）⇒ `check_bool_equal` 拿 `'True'` 与真实 bool 能对上。
3) **断言只能引用「本步骤」的 funcReturn**（`run_step_playwright` 在每步末尾写入
   `case_params.stepResponse[step_id]['funcReturn'] = return_value`）。
   ⇒ 凡是「动作本身不产生返回值」的断言，必须**额外插一条提取步骤**，
     绝不能把动作步骤的 keyword 换成提取关键字 —— 那会把动作本身丢掉
     （例如把 `fill` 换成 `get_attribute` 就等于不再输入了）。
4) `CaseSteps.step_index` 在事务内**取一次 max 再递增**，不要在循环里重算 ——
   并发导入时重算会让两个请求拿到同一下标，步骤顺序互相覆盖。
"""
import logging
import time
import uuid
from collections import OrderedDict

from django.db import transaction
from django.db.models import Max

from apps.elements.models import Element
from apps.envs.models import Module, Plant
from apps.tests.models import Case, CaseSteps, Step, default_case_data
from core.com.common import get_function_params
from core.run_case import StepType
from core.step.run_playwright import playwright_func_map

logger = logging.getLogger('recording')

# ===== 对外常量 =====
MODE_NEW_CASE = 'new_case'
MODE_APPEND_STEPS = 'append_steps'
MODE_CHOICES = (MODE_NEW_CASE, MODE_APPEND_STEPS)

# Element.web.by 的合法取值（与前端元素编辑器的 ByChoice、执行底座 _build_locator 三方对齐）
ELEMENT_BY_CHOICES = ('id', 'xpath', 'css', 'text', 'placeholder', 'role', 'label', 'alt text')

# 录制产物默认落在哪个模块前缀
RECORD_MODULE_PREFIX = '录制-'

# 标量参数类型：其余（Dict/List）执行底座会走「递归解析 children」分支，
# 而录制事件流无法还原结构化对象 ⇒ 明确报错，不静默塞空字典
_SCALAR_PARAM_TYPES = ('Str', 'Int', 'Float', 'Bool')

_VAR_REF = '${caseParams.%s}'
_ACT_REF = '${stepResponse.%s.funcReturn}'

# 校验步骤的显示名（desc 上限 100，这里都很短）
_VERIFY_DESC = {
    'url': '校验页面URL',
    'title': '校验页面标题',
    'text_content': '校验元素文本',
    'get_attribute': '校验元素属性',
    'is_visible': '校验元素可见',
    'is_enabled': '校验元素可用',
    'is_checked': '校验元素勾选',
    'tag_name': '校验元素标签',
    'css_property': '校验元素样式',
}


class RecordingImportError(Exception):
    """落库前置校验失败 —— 消息会原样回给用户（视图层转 400），必须可读。"""


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------
def _norm_by(by):
    """把定位方式收敛到 ELEMENT_BY_CHOICES 之内。

    执行底座 `_build_locator` 对无法识别的方式会退化成 `page.locator(value)`，
    那等于把 `aria/用户名` 这类描述当成 CSS 选择器用，必然找不到元素。
    所以这里主动降级为 css，并在落库前就暴露出来。
    """
    b = (by or '').strip().lower()
    if b in ELEMENT_BY_CHOICES:
        return b
    return 'css'


def _element_web_spec(locators):
    """IR 的定位器候选 → `Element.web`。

    Element.web = {'by','value','opts'}；执行底座只认这三项。
    这里额外把第 2~4 候选塞进 `opts.alternatives` —— P3 自愈链消费它做多级回退。
    老版本底座会忽略该键，前端元素编辑器重新保存时可能丢弃它（可接受的软降级），
    所以这是安全的纯增量。
    """
    ranked = [c for c in (locators or []) if isinstance(c, dict) and c.get('value') not in (None, '')]
    if not ranked:
        return None
    top = ranked[0]
    opts = dict(top.get('opts') or {})
    alts = []
    for c in ranked[1:4]:
        alts.append({
            'by': _norm_by(c.get('by')),
            'value': c.get('value'),
            'opts': dict(c.get('opts') or {}),
            'score': c.get('score'),
        })
    if alts:
        opts['alternatives'] = alts
    return {'by': _norm_by(top.get('by')), 'value': top.get('value'), 'opts': opts}


def _same_locator(web, spec):
    if not isinstance(web, dict):
        return False
    return (_norm_by(web.get('by')) == spec['by']
            and str(web.get('value')) == str(spec['value']))


def _unique_case_name(name):
    """用例名去重（口径与 Case 模型注释一致：只在「未软删除」集合内判重）。"""
    base = (name or '录制用例').strip()[:50] or '录制用例'
    if not Case.objects.filter(name=base, is_delete=False).exists():
        return base
    i = 2
    while i < 200:
        suffix = '_%d' % i
        cand = base[:50 - len(suffix)] + suffix
        if not Case.objects.filter(name=cand, is_delete=False).exists():
            return cand
        i += 1
    suffix = '_' + uuid.uuid4().hex[:6]
    return base[:50 - len(suffix)] + suffix


def resolve_plant(project_id, plant_id=None, case_obj=None):
    """解析 `Step.plant`（必填外键）—— 四级兜底，口径与
    `apps/tests/views.py::add_many_api_step_for_case` 一致：

        显式 plant → 用例既有步骤的平台 → 用例所属模块的平台 → 项目下第一个平台

    最后一级仍取不到就抛可读错误，**绝不静默落一条 plant 为空的步骤**。
    """
    if plant_id:
        obj = Plant.objects.filter(id=plant_id, is_delete=False).first()
        if obj is not None:
            return obj
    if case_obj is not None:
        cs = CaseSteps.objects.filter(case_id=case_obj.id, is_delete=False).first()
        if cs is not None:
            st = Step.objects.filter(id=cs.step_id).first()
            if st is not None and st.plant_id:
                obj = Plant.objects.filter(id=st.plant_id, is_delete=False).first()
                if obj is not None:
                    return obj
        mod = Module.objects.filter(id=case_obj.module_id, is_delete=False).first()
        if mod is not None and mod.plant_id:
            obj = Plant.objects.filter(id=mod.plant_id, is_delete=False).first()
            if obj is not None:
                return obj
    obj = Plant.objects.filter(project_id=project_id, is_delete=False).first()
    if obj is None:
        raise RecordingImportError(
            '未找到可用的平台配置，请先在「环境配置 - 平台管理」中为本项目创建平台')
    return obj


def ensure_module(project_id, plant_obj, module_id=None, user_id=None):
    """确定录制产物落在哪个用例模块（`Case.module` 是必填外键）。

    优先用调用方指定的 module_id；否则复用 / 新建「录制-YYYYMMDD」模块。
    这样做而不是随手塞进第一个模块，是为了让「录制产物」和「手工建的用例」
    在模块树上分得开 —— 用户能一眼看出哪些是用例是录出来的。
    """
    if module_id:
        mod = Module.objects.filter(id=module_id, project_id=project_id, is_delete=False).first()
        if mod is not None:
            return mod
    name = ('%s%s' % (RECORD_MODULE_PREFIX, time.strftime('%Y%m%d')))[:20]
    mod = Module.objects.filter(project_id=project_id, name=name, is_delete=False).first()
    if mod is None:
        mod = Module.objects.create(
            name=name, url='', project_id=project_id, plant=plant_obj,
            create_by_id=user_id, update_by_id=user_id,
        )
    return mod


# ---------------------------------------------------------------------------
# 元素复用器
# ---------------------------------------------------------------------------
class _ElementResolver:
    """一个导入批次内的元素复用器。

    两级缓存（顺序不能反）：
      1) by_ref    —— 同一次录制里同一 `element_ref` 视为同一元素
                      （IR 已用 by|value|opts 三重指纹保证 ref 不碰撞）；
      2) by_locate —— 元素库里已有「同名 + 同 by + 同 value」的记录直接复用。
    没有第 2 级的话，同一个登录页录 10 遍会造 10 套元素，元素库很快就不可用了。
    """

    def __init__(self, project_id, module_id, user_id=None):
        self.project_id = project_id
        self.module_id = module_id
        self.user_id = user_id
        self.by_ref = {}
        self.by_locate = {}
        self._merged = set()
        self.created = 0
        self.reused = 0

    def resolve(self, element_ir):
        """返回 Element 实例；IR 里没有可用定位器时返回 None。"""
        if not element_ir:
            return None
        spec = _element_web_spec(element_ir.get('locators') or [])
        if spec is None:
            return None

        ref = element_ir.get('element_ref')
        if ref and ref in self.by_ref:
            self.reused += 1
            return self.by_ref[ref]

        name = (element_ir.get('name') or '').strip()[:50] or '元素'
        key = (name, spec['by'], str(spec['value']))
        if key in self.by_locate:
            el = self.by_locate[key]
            self.reused += 1
            if ref:
                self.by_ref[ref] = el
            return el

        el = self._find_in_db(name, spec)
        if el is not None:
            self.reused += 1
            self._merge_alternatives(el, spec)
        else:
            el = Element.objects.create(
                name=self._unique_name(name, spec),
                project_id=self.project_id,
                module_id=self.module_id,
                type='web',
                web=spec,
                ios=[], android=[],
                status=1,                     # 1 = 已发布：录制产物应当可直接被用例引用
                create_by_id=self.user_id, update_by_id=self.user_id,
            )
            self.created += 1

        self.by_locate[key] = el
        if ref:
            self.by_ref[ref] = el
        return el

    def _find_in_db(self, name, spec):
        """在元素库里找「本来就是同一个元素」的既有记录。

        ★★ 匹配口径：**定位器优先（by + value 全等），名字只作排序偏好**。
        踩过的坑（P1 实测，元素库被静默堆爆）：
          `_find_in_db` 原来只查 `name = IR 里的原始名`（比如 `用户名`），
          而 `_unique_name` 在「同名但定位不同」时会返回**加了后缀**的名字
          （`用户名_2`）。两个口径不一致 ⇒ 一旦名字被加过后缀，
          下一次导入用原始名**永远查不到它**，于是再造一条。
          线上证据：同一个 `role=textbox` 的用户名输入框被造了 4 条，
          全叫 `用户名_2` —— 而 `用户名_3` **一条都没有**。
          那个「后缀永不推进」的现象就是本缺陷的指纹：能造出来的名字，
          每次都是 `_unique_name` 顺手返回的同一个。
        ⇒ 元素的身份本来就是它的定位器；名字是给人看的标签，
          不该参与「是不是同一个元素」的判定。
        """
        # 一次查询 + Python 内比对：项目级元素量级在千以内，代价可接受。
        # 不用 `web__by=...` 收窄是因为历史上存在 by 未归一化的老行，
        # 收窄会把它们漏掉 —— 那些行会继续「查不到 ⇒ 又造一个」，等于没修。
        same = [c for c in Element.objects.filter(project_id=self.project_id, is_delete=False)
                if _same_locator(c.web, spec)]
        if not same:
            return None
        # 同定位器可能有多条（历史重复），优先取名字一致的，其次取最早的：
        # 这样能把新导入收敛到那条「老」记录上，而不是继续扩散。
        same.sort(key=lambda c: (c.name != name, c.id))
        return same[0]

    def _unique_name(self, base, spec):
        """同名但定位不同的元素 → 加 _2/_3 后缀，避免元素库里出现一堆同名项。"""
        name, i = base, 2
        while i < 60:
            exists = Element.objects.filter(
                project_id=self.project_id, name=name, is_delete=False).first()
            if exists is None:
                return name
            if _same_locator(exists.web, spec):
                return name
            suffix = '_%d' % i
            name = base[:50 - len(suffix)] + suffix
            i += 1
        suffix = '_' + uuid.uuid4().hex[:4]
        return base[:50 - len(suffix)] + suffix

    def _merge_alternatives(self, el, spec):
        """把本次录到的新候选并进已有元素的候选链（P3 自愈链的数据来源）。

        每个元素在一次导入里只写一次库 —— 否则每命中一个动作都要 UPDATE 一次，
        一个几十步的录制会多出几十条无谓写。
        """
        if el.id in self._merged:
            return
        self._merged.add(el.id)
        new_alts = (spec.get('opts') or {}).get('alternatives') or []
        if not new_alts:
            return
        web = dict(el.web or {})
        opts = dict(web.get('opts') or {})
        old = [c for c in (opts.get('alternatives') or []) if isinstance(c, dict)]
        seen = {(c.get('by'), str(c.get('value'))) for c in old}
        added = False
        for a in new_alts:
            k = (a.get('by'), str(a.get('value')))
            if k in seen:
                continue
            old.append(a)
            seen.add(k)
            added = True
        if not added:
            return
        opts['alternatives'] = old[:6]
        web['opts'] = opts
        el.web = web
        el.save(update_fields=['web', 'update_time'])


# ---------------------------------------------------------------------------
# 用例变量（Case.params）
# ---------------------------------------------------------------------------
def _collect_variables(actions):
    """扫描 IR 动作，收集并归并用例变量。

    返回 `[{'name','value'}]`（首次出现顺序，稳定）。
    同时**就地改写**动作里 variable 型参数的 `var_name` —— 因为这里会给
    「同名不同值」分叉出 `_2` / `_3` 后缀：

    ★ 为什么必须分叉：两次录制输入了不同手机号却都提升成 `Mobile` 的话，
      后出现的值会覆盖先出现的，回放时两条步骤都用最后一个值 ——
      生成出来的用例必错，而且是「看起来跑通了但断言全过」的隐性错误。

    ★ 敏感字段（密码/令牌）的 `value` 恒为空串：IR 里本来就只有 `redacted` 标记，
      原文在归一化阶段已被丢弃，这里也绝不补写。
    """
    values = OrderedDict()

    def _assign(name, value):
        name = name or 'Variable'
        if name not in values:
            values[name] = value
            return name
        if values[name] == value:
            return name
        i = 2
        while i < 200:
            cand = '%s_%d' % (name, i)
            if cand not in values:
                values[cand] = value
                return cand
            if values[cand] == value:
                return cand
            i += 1
        return name

    for act in actions:
        for obj in (act.get('args') or {}).values():
            if not isinstance(obj, dict) or obj.get('kind') != 'variable':
                continue
            if obj.get('redacted'):
                value = ''
            else:
                v = obj.get('value')
                value = '' if v is None else str(v)
            obj['var_name'] = _assign(obj.get('var_name'), value)

    return [{'name': n, 'value': v} for n, v in values.items()]


def _merge_case_params(case_obj, new_params):
    """把新变量并入用例已有的 `params`（同名保留用户已改过的值）。

    追加模式（append_steps）必须走这里：直接覆盖会把用户在前一次导入后手工
    修正过的变量值冲掉 —— 而用户往往正是在那一步把密码填上的。
    """
    existing = list(case_obj.params or [])
    have = {p.get('name') for p in existing if isinstance(p, dict)}
    for p in new_params:
        if p['name'] not in have:
            existing.append(p)
            have.add(p['name'])
    case_obj.params = existing
    return existing


# ---------------------------------------------------------------------------
# func_params / check_params
# ---------------------------------------------------------------------------
def _build_func_params(keyword, args, element_id=''):
    """按关键字签名生成 `Step.func_params`（扁平列表）。

    与 `apps/ai_service/scenario_case_saver.py::_build_web_step` 同契约，
    区别只在值来源：这里可能是 IR 的 `{'kind':'literal'|'variable'}` 对象。
    """
    func = playwright_func_map.get(keyword)
    if func is None:
        raise RecordingImportError(
            '执行底座里没有关键字「%s」（core/step/run_playwright.py）' % keyword)

    args = args or {}
    out = []
    for sp in get_function_params(func):
        name = sp['name']
        if sp['type'] == 'EleObject':
            # 多元素动作（如 drag_and_drop）无法从单元素事件还原，明确报错而不是
            # 少传一个参数 —— 少传会导致运行期 TypeError，报错信息还很难懂。
            if name != 'obj':
                raise RecordingImportError(
                    '关键字「%s」暂不支持多元素参数 %s（请手工补该步骤）' % (keyword, name))
            if not element_id:
                if sp['value'] is None:
                    raise RecordingImportError(
                        '关键字「%s」缺少必填参数 %s（该步骤没有可用元素）' % (keyword, name))
                continue
            fvalue, ftype = str(element_id), 'EleObject'
        else:
            if sp['type'] not in _SCALAR_PARAM_TYPES:
                raise RecordingImportError(
                    '关键字「%s」的参数 %s 是 %s 类型，录制事件流无法还原（请手工补该步骤）'
                    % (keyword, name, sp['type']))
            raw = args.get(name)
            if isinstance(raw, dict) and 'kind' in raw:
                if raw.get('kind') == 'variable':
                    fvalue, ftype = _VAR_REF % raw.get('var_name'), sp['type']
                else:
                    v = raw.get('value')
                    fvalue, ftype = ('' if v is None else str(v)), sp['type']
            elif raw is None:
                if sp['value'] is None:
                    raise RecordingImportError('关键字「%s」缺少必填参数 %s' % (keyword, name))
                fvalue, ftype = sp['value'], sp['type']
            else:
                fvalue, ftype = str(raw), sp['type']

        out.append({
            'id': 'row_%s' % uuid.uuid4().hex[:8],
            'name': name,
            'value': fvalue,
            'type': ftype,
            'explain': sp['explain'],
            'children': [],
            '_X_ROW_CHILD': [],
            'function_name': keyword,
        })
    return out


def _build_check_params(specs, own_case_step_id):
    """断言规格 → `Step.check_params`。

    规格由 `core/recorder/normalizer.py::derive_assertions` 产出。
    `act_value` 统一指向**本步骤**的 funcReturn —— 所以调用方必须保证：
    这条步骤的 keyword 就是规格里的 `extract_keyword`（见模块开头的契约 3）。
    """
    out = []
    for spec in specs or []:
        expect = spec.get('expect')
        out.append({
            'id': str(uuid.uuid4()),
            'method': spec.get('method') or 'check_equal',
            'exp_value': '' if expect is None else str(expect),
            'act_value': _ACT_REF % own_case_step_id,
            'andOr': 'And',
        })
    return out


def _keyword_needs_element(keyword):
    """该关键字是否需要一个元素对象参数（obj）。"""
    func = playwright_func_map.get(keyword)
    if func is None:
        return False
    try:
        return any(sp['type'] == 'EleObject' for sp in get_function_params(func))
    except ValueError:
        # 签名里有未标注类型的参数 —— 这种情况在底座里不该出现，保守认为不需要
        return False


# ---------------------------------------------------------------------------
# 断言分组
# ---------------------------------------------------------------------------
def _group_assertions(action):
    """把一条动作的断言规格拆成「挂自己」/「需额外提取步骤」/「需人工补」。

    ★ 为什么不能一律挂在动作步骤上：`run_step_playwright` 只把**本步骤**的
      funcReturn 写进 stepResponse，而 `click` / `fill` 这类动作的 funcReturn 是 None。
      把断言挂上去只会得到「None == 预期」的假失败 —— 比没有断言更糟，
      因为它会让用户以为用例真的坏了。
    """
    own, verify, deferred = [], OrderedDict(), []
    own_kw = action.get('keyword')
    for spec in (action.get('assertions') or []):
        if not isinstance(spec, dict):
            continue
        ek = spec.get('extract_keyword')
        if not spec.get('auto'):
            deferred.append({
                'seq': action.get('seq'), 'rule': spec.get('rule'),
                'method': spec.get('method'), 'note': spec.get('note'),
            })
            continue
        if not ek or ek not in playwright_func_map:
            deferred.append({
                'seq': action.get('seq'), 'rule': spec.get('rule'),
                'method': spec.get('method'),
                'note': spec.get('note') or ('提取关键字「%s」在底座里不存在，需人工指定' % ek),
            })
            continue
        if owk_same(own_kw, ek):
            own.append(spec)
        else:
            verify.setdefault(ek, []).append(spec)
    return own, verify, deferred


def owk_same(action_keyword, extract_keyword):
    """动作自身就是提取动作吗？（此时断言直接挂它，不必多插一条步骤）"""
    return bool(action_keyword) and action_keyword == extract_keyword


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
def import_ir(ir, project_id, user_id=None, case_id=None, module_id=None,
              plant_id=None, mode=MODE_NEW_CASE, case_name=None,
              import_assertions=True, session=None):
    """把一份 IR 落库成用例步骤。

    Args:
        ir:            `core/recorder/normalizer.build_ir` 的产物
        project_id:    目标项目 ID
        user_id:       操作人 ID
        case_id:       `mode='append_steps'` 时必填
        module_id:     产物落在哪个用例模块（缺省自动用/建「录制-YYYYMMDD」）
        plant_id:      步骤所属平台（缺省走四级兜底）
        mode:          'new_case' | 'append_steps'
        case_name:     new_case 模式的用例名（缺省取 IR meta.title / meta.start_url）
        import_assertions: 是否落库自动推导出的断言（审阅台可关掉）
        session:       可选，`RecordingSession` 实例 —— 回写 imported_case_id / stats

    Returns:
        dict —— 见下方 `result` 组装处。**必须整包返回给前端**，因为
        「跳过了几条动作、有几条断言需要人工补」是用户判断产物能不能用的唯一依据。

    Raises:
        RecordingImportError: 前置校验失败（可读原因，视图层转 400）
    """
    if mode not in MODE_CHOICES:
        raise RecordingImportError('不支持的模式「%s」，可选：%s' % (mode, '、'.join(MODE_CHOICES)))
    if not isinstance(ir, dict) or not isinstance(ir.get('actions'), list):
        raise RecordingImportError('IR 结构不合法（缺少 actions 数组）')

    # ★ P1 审阅台：人工取消的动作以 `enabled=False` 标记（与归一化阶段的
    #   `stats.dropped`（**规则**丢弃）语义分开，别混）。
    #   必须把人工取消的也算进 `skipped`，否则本函数末尾的「统计自洽」
    #   断言（落库动作数 + 跳过数 == IR 动作数）会失败 —— 那条断言是对的，
    #   它拦下的正是「有分支在静默丢弃动作」这类最危险的缺陷。
    all_actions = [a for a in ir['actions'] if isinstance(a, dict)]
    actions = [a for a in all_actions if a.get('enabled', True) is not False]
    manual_off = [a for a in all_actions if a.get('enabled', True) is False]
    if not all_actions:
        raise RecordingImportError('IR 里没有任何动作，无法生成用例步骤')
    if not actions:
        raise RecordingImportError(
            '全部 %d 条动作都已在审阅台取消，没有可落库的内容。'
            '请至少保留一条，或改用新建用例模式重新导入。' % len(all_actions))

    meta = ir.get('meta') or {}
    notes = []
    skipped = [{'seq': a.get('seq'), 'reason': '审阅台人工取消（不计入用例）',
                'raw_type': a.get('raw_type')} for a in manual_off]
    for s in (meta.get('warnings') or []):
        notes.append({'level': 'warn', 'message': str(s)})

    # ---- 目标用例 / 模块 / 平台（顺序不能换：resolve_plant 依赖 case_obj 做兜底） ----
    case_obj = None
    if mode == MODE_APPEND_STEPS:
        if not case_id:
            raise RecordingImportError('追加模式下必须提供 case_id')
        case_obj = Case.objects.filter(id=case_id, is_delete=False).first()
        if case_obj is None:
            raise RecordingImportError('用例 %s 不存在或已删除' % case_id)
        if case_obj.project_id != int(project_id):
            raise RecordingImportError('用例 %s 不属于当前项目' % case_id)
        if case_obj.type != Case.FunctionCaseType.WEB_UI:
            raise RecordingImportError(
                'HAR / 录制产物只能落到「Web自动化」用例，当前用例类型是「%s」'
                % case_obj.get_type_display())

    plant_obj = resolve_plant(project_id, plant_id, case_obj)
    module_obj = ensure_module(
        project_id, plant_obj,
        module_id if module_id else (case_obj.module_id if case_obj else None),
        user_id=user_id)

    variables = _collect_variables(actions)
    for act in actions:
        for note in (act.get('notes') or []):
            notes.append({'level': 'info', 'seq': act.get('seq'), 'message': str(note)})

    resolver = _ElementResolver(project_id, module_obj.id, user_id)
    created_steps = []
    total_assertions = 0
    deferred_all = []

    with transaction.atomic():
        # ---- 1) 确定目标用例（新建 or 追加） ----
        if case_obj is None:
            title = (case_name or meta.get('title') or '').strip()
            if not title:
                start_url = (meta.get('start_url') or '').strip()
                title = ('录制_%s' % start_url[:30]) if start_url else ('录制_%s' % time.strftime('%m%d_%H%M'))
            case_obj = Case.objects.create(
                name=_unique_case_name(title),
                type=Case.FunctionCaseType.WEB_UI,
                project_id=project_id,
                module_id=module_obj.id,
                params=variables,
                data=default_case_data(),
                recent_test_result=Case.CaseResult.NoRUN,
                create_by_id=user_id, update_by_id=user_id,
            )
            case_created = True
        else:
            _merge_case_params(case_obj, variables)
            case_obj.update_by_id = user_id
            case_obj.save(update_fields=['params', 'update_by_id', 'update_time'])
            case_created = False

        # ---- 2) 取一次最大下标再递增（并发安全） ----
        cur_max = CaseSteps.objects.filter(
            case_id=case_obj.id, is_delete=False).aggregate(m=Max('step_index'))['m']
        next_index = 0 if cur_max is None else int(cur_max) + 1

        def _new_case_step(step_obj, index):
            return CaseSteps.objects.create(
                case_id=case_obj.id, step_id=step_obj.id, step_index=index,
                step_params=[], parent_id=None, is_run=True,
                fail_is_continue=CaseSteps.IsContinue.Stop,
                create_by_id=user_id, update_by_id=user_id,
            )

        step_specs = []   # 先规划，后落库（便于把「已绑定」的原语一次算清楚）

        # ---- 3) 逐动作落库 ----
        for act in actions:
            keyword = act.get('keyword')
            if not keyword:
                skipped.append({
                    'seq': act.get('seq'),
                    'reason': '该事件在归一化阶段没有映射到关键字（需人工补步骤）',
                    'raw_type': act.get('raw_type'),
                })
                continue
            if keyword not in playwright_func_map:
                skipped.append({
                    'seq': act.get('seq'),
                    'reason': '执行底座没有关键字「%s」' % keyword,
                    'raw_type': act.get('raw_type'),
                })
                continue

            el_obj = resolver.resolve(act.get('element'))
            element_id = el_obj.id if el_obj is not None else ''
            if el_obj is None and _keyword_needs_element(keyword):
                skipped.append({
                    'seq': act.get('seq'),
                    'reason': '该步骤需要元素，但 IR 里没有可用定位器（%s）' % keyword,
                    'raw_type': act.get('raw_type'),
                })
                continue
            step_specs.append((act, keyword, element_id, el_obj))

        resolver_created, resolver_reused = resolver.created, resolver.reused

        for act, keyword, element_id, el_obj in step_specs:
            try:
                func_params = _build_func_params(keyword, act.get('args'), element_id)
            except RecordingImportError as e:
                skipped.append({'seq': act.get('seq'), 'reason': str(e),
                                'raw_type': act.get('raw_type')})
                continue

            own_specs, verify_groups, deferred = ([], OrderedDict(), [])
            if import_assertions:
                own_specs, verify_groups, deferred = _group_assertions(act)
            else:
                for spec in (act.get('assertions') or []):
                    if isinstance(spec, dict) and spec.get('auto'):
                        deferred.append({'seq': act.get('seq'), 'rule': spec.get('rule'),
                                         'method': spec.get('method'),
                                         'note': '本次导入已关闭「自动落库断言」'})
            deferred_all.extend(deferred)

            step_obj = _create_web_step(
                keyword=keyword, desc=_step_desc(act, keyword),
                project_id=project_id, plant_obj=plant_obj,
                func_params=func_params, user_id=user_id,
            )
            case_step = _new_case_step(step_obj, next_index)
            next_index += 1
            created_steps.append({
                'seq': act.get('seq'), 'keyword': keyword, 'step_id': step_obj.id,
                'case_step_id': case_step.id, 'element_id': el_obj.id if el_obj else None,
                'desc': step_obj.desc, 'kind': 'action',
            })

            if own_specs:
                step_obj.check_params = _build_check_params(own_specs, case_step.id)
                step_obj.save(update_fields=['check_params', 'update_time'])
                total_assertions += len(own_specs)

            # ---- 额外提取步骤：动作本身不产生返回值时，断言必须挂到独立的提取步骤上 ----
            for ek, specs in verify_groups.items():
                v_element_id = element_id if _keyword_needs_element(ek) else ''
                v_args = dict(specs[0].get('extract_args') or {})
                try:
                    v_func_params = _build_func_params(ek, v_args, v_element_id)
                except RecordingImportError as e:
                    skipped.append({'seq': act.get('seq'),
                                    'reason': '无法生成校验步骤：%s' % e,
                                    'raw_type': act.get('raw_type')})
                    continue
                if v_element_id == '' and _keyword_needs_element(ek):
                    skipped.append({'seq': act.get('seq'),
                                    'reason': '校验步骤「%s」需要元素，但动作里没有元素定位器' % ek,
                                    'raw_type': act.get('raw_type')})
                    continue
                v_step = _create_web_step(
                    keyword=ek, desc=_VERIFY_DESC.get(ek, '校验-%s' % ek),
                    project_id=project_id, plant_obj=plant_obj,
                    func_params=v_func_params, user_id=user_id,
                )
                v_case_step = _new_case_step(v_step, next_index)
                next_index += 1
                v_step.check_params = _build_check_params(specs, v_case_step.id)
                v_step.save(update_fields=['check_params', 'update_time'])
                total_assertions += len(specs)
                created_steps.append({
                    'seq': act.get('seq'), 'keyword': ek, 'step_id': v_step.id,
                    'case_step_id': v_case_step.id,
                    'element_id': v_element_id or None,
                    'desc': v_step.desc, 'kind': 'verify',
                })

    stats = ir.get('stats') or {}
    result = {
        'case_id': case_obj.id,
        'case_name': case_obj.name,
        'case_created': case_created,
        'mode': mode,
        'module_id': module_obj.id,
        'module_name': module_obj.name,
        'plant_id': plant_obj.id,
        'plant_name': plant_obj.name,
        'step_count': len(created_steps),
        'action_step_count': len([s for s in created_steps if s['kind'] == 'action']),
        'verify_step_count': len([s for s in created_steps if s['kind'] == 'verify']),
        'assertion_count': total_assertions,
        'variables': variables,
        'elements': {'created': resolver_created, 'reused': resolver_reused},
        'steps': created_steps,
        'skipped_actions': skipped,
        'deferred_assertions': deferred_all,
        'notes': notes,
        'ir_stats': {
            'raw_events': stats.get('raw_events'),
            'kept_actions': stats.get('kept_actions'),
            'dropped': stats.get('dropped'),
            'drop_reasons': stats.get('drop_reasons') or {},
        },
    }

    # 统计口径自证：落库动作数 + 跳过数 必须等于 **IR 的动作数**（all_actions）。
    # 差额意味着有分支在静默丢弃动作 —— 那是最危险的一类缺陷（用户看不到少了东西）。
    #
    # ★★ 分母必须是 all_actions（未过滤），不能用 actions（已按 enabled 过滤）。
    #    这是 P1 引入 enabled 拆分时埋下的回归：`skipped` 里**已经包含**
    #    「审阅台人工取消」那批，若分母又用过滤后的 actions，两者同时少算一次
    #    ⇒ 只要用户取消了 n 条，gap 恒为 -n，**每次带取消的导入都误报**。
    #    安全网误报的代价比不报更大：人会开始无视它，真出静默丢弃时也看不见了。
    #    （E2E 实测：取消 2 条时打印「IR 动作 10 条，落库 10 条、跳过 2 条，差额 -2」。）
    accounted = result['action_step_count'] + len(skipped)
    if accounted != len(all_actions):
        gap = len(all_actions) - accounted
        result['notes'].append({
            'level': 'warn',
            'message': '统计不自洽：IR 动作 %d 条，实际落库 %d 条、跳过 %d 条，差额 %d 条未归因'
                       % (len(all_actions), result['action_step_count'], len(skipped), gap),
        })
        logger.warning('[REC-IMPORT] 动作计数不自洽 case=%s gap=%s', case_obj.id, gap)

    if session is not None:
        try:
            session.imported_case_id = case_obj.id
            session.status = session.Status.IMPORTED
            session.save(update_fields=['imported_case_id', 'status', 'update_time'])
        except Exception as e:      # 会话回写失败不能影响已落库的用例
            logger.warning('[REC-IMPORT] 会话回写失败 session=%s err=%s', session.id, e)

    logger.info('[REC-IMPORT] 落库完成 case=%s(%s) 动作步骤=%s 校验步骤=%s 断言=%s 跳过=%s 元素新增=%s/复用=%s',
                case_obj.id, case_obj.name, result['action_step_count'], result['verify_step_count'],
                total_assertions, len(skipped), resolver_created, resolver_reused)
    return result


def _step_desc(act, keyword):
    """步骤描述：优先用元素的可见文本，其次用关键字 + 参数，最后退回关键字本身。"""
    el = act.get('element') or {}
    if el.get('name'):
        return ('%s · %s' % (keyword, el['name']))[:100]
    snap = el.get('snapshot') or {}
    label = (snap.get('text') or snap.get('aria_label') or '').strip()
    if label:
        return ('%s · %s' % (keyword, label))[:100]
    args = act.get('args') or {}
    for key in ('uri', 'value', 'key_name', 'direction', 'name'):
        v = args.get(key)
        if isinstance(v, dict):
            v = v.get('value') or v.get('var_name')
        if v:
            return ('%s · %s' % (keyword, str(v)[:40]))[:100]
    return keyword[:100]


def _create_web_step(keyword, desc, project_id, plant_obj, func_params, user_id=None):
    """建一条 Playwright 步骤。

    注意 `Step.keyword` 在模型上是 `max_length=25`，而底座里
    `scroll_into_view_if_needed` 是 26 字符。MySQL 默认 STRICT_TRANS_TABLES，
    超长会直接报 1406 并让整批事务回滚 —— 所以这里主动拦下来，给出可执行的提示，
    而不是让用户看到一条「系统内部异常」。配套迁移见
    `apps/tests/migrations/0010_alter_step_keyword_length.py`（把列放宽到 64）。
    """
    if len(keyword) > 64:
        raise RecordingImportError('关键字「%s」长度超过 64，Step.keyword 存不下' % keyword)
    return Step.objects.create(
        desc=(desc or keyword)[:100],
        project_id=project_id,
        database_name=None,
        step_active_tab='params',
        is_check=False,
        type=StepType.Playwright,
        com_step_type=StepType.Playwright,
        timeout=7,
        allow_redirects=True,
        verify=False,
        keyword=keyword,
        plant=plant_obj,
        api_service=None,
        api_method=None,
        api_uri=None,
        api_headers=[],
        common_headers=False,
        api_json_type='object',
        json_body_deal=None,
        api_json=[],
        body_type=1,
        api_json_tree=[],
        api_data=[],
        data_body_deal=None,
        api_response=[],
        api_response_tree=[],
        api_response_type='object',
        response_body_deal=None,
        api_params=[],
        check_params=[],
        run_params=[],
        loop=[],
        until=[],
        setup='',
        script='',
        teardown='',
        func_params=func_params,
        create_by_id=user_id,
        update_by_id=user_id,
    )
