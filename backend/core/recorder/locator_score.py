# -*- coding: utf-8 -*-
"""定位器打分与候选链排序（P0-③）

这是设计方案第 07 章「定位器生成策略」的唯一实现。打分模型的作用不是「选一个」，
而是**给一串候选排序**：执行期按序回退（P3 自愈），审阅期给人看（P1 审阅台）。

★ 为什么要有候选链而不是单个定位器
   单个定位器 = 单点故障。UI 加个 div，`nth-child` 就全错位。候选链让系统在
   主定位失效时先用零成本方案兜住（业界的自愈对定位类失败成功率 75%+），
   只有整条链都失败才需要人或模型介入。

★ 纯函数、零依赖 ⇒ 可离线单测。
"""

import re

# ---------------------------------------------------------------------------
# 基准分：越靠前越稳。数字来自设计方案第 07 章，与 Playwright 官方推荐顺序一致
# （role → label → placeholder → text → alt text → css → xpath）。
# ---------------------------------------------------------------------------
BASE_SCORE = {
    'role': 0.96,
    'label': 0.90,
    'placeholder': 0.86,
    'text': 0.80,
    'alt text': 0.74,
    'id': 0.70,
    'css': 0.52,
    'xpath': 0.30,
}

# 中文名，用于把扣分原因写成人能看懂的话（审阅台直接展示）
BY_LABEL_CN = {
    'role': 'role+name（无障碍角色）',
    'label': 'label 关联',
    'placeholder': 'placeholder',
    'text': '可见文本',
    'alt text': 'alt 文本',
    'id': '元素 id',
    'css': 'CSS 选择器',
    'xpath': 'XPath 结构路径',
}

# by 值别名归一化：不同来源写法不同，统一成平台 ByChoice 支持的那 7 个值
# （平台 ByChoice 支持 id/xpath/css/text/placeholder/role/label/alt text）
BY_ALIASES = {
    'aria': 'role',
    'role': 'role',
    'label': 'label',
    'placeholder': 'placeholder',
    'text': 'text',
    'alt': 'alt text',
    'alt-text': 'alt text',
    'alttext': 'alt text',
    'alt text': 'alt text',
    'id': 'id',
    'css': 'css',
    'selector': 'css',
    'xpath': 'xpath',
}


def normalize_by(by):
    """把各种来源的 by 写法归一化成平台 ByChoice 支持的值；无法识别返回 None。"""
    if not by:
        return None
    key = str(by).strip().lower()
    return BY_ALIASES.get(key)


# ---------------------------------------------------------------------------
# 扣分规则
# ---------------------------------------------------------------------------
# 随机 / 构建期生成的片段：每次打包都会变，今天能定位明天就失效
RANDOM_FRAGMENT_RE = re.compile(
    r'(_[0-9a-f]{6,}'          # _a3f19c
    r'|css-[a-z0-9]{5,}'       # emotion: css-1x2y3z
    r'|sc-[a-zA-Z0-9]{5,}'     # styled-components: sc-bdVaJa
    r'|[0-9a-f]{12,}'          # 长十六进制串
    r'|[A-Za-z0-9]{20,})',     # 超长无意义 token（哈希类）
    re.I,
)
NTH_RE = re.compile(r':nth-(?:child|of-type)\s*\(', re.I)
FRAMEWORK_CLASS_RE = re.compile(
    r'(?:^|[\s>+~,.#\[])(?:el|ant|ivu|van|nut|mint|v|layui|bootstrap)-[a-zA-Z0-9_-]+',
    re.I,
)
# data-v-xxxx 是 Vue scoped 样式加的属性，跨构建稳定但语义为 0
VUE_SCOPED_RE = re.compile(r'\[data-v-[0-9a-f]{6,}\]', re.I)

MAX_VALUE_LEN = 120


def score_locator(by, value, opts=None, match_count=None, aria_guessed=False):
    """给单个候选定位器打分。

    参数
      by           定位方式（会被 normalize_by 归一化）
      value        定位表达式
      opts         附加选项，如 {'name': '用户名', 'exact': False}
      match_count  该定位器在页面上的匹配个数。1 = 唯一（有加成）；
                   >1 = 歧义（本文档在基准模型上追加了扣分，见下）；
                   None = 未知（不参与该项计算）
      aria_guessed 该候选的 role 是**猜**出来的（Chrome Recorder 的 `aria/xxx`
                   只给无障碍名、不给角色）⇒ 追加扣分，避免猜出来的 role
                   排到真·label 候选前面

    返回 (score, reasons)
      score   0.0 ~ 1.0
      reasons 中文原因列表，直接给审阅台展示
    """
    reasons = []
    norm_by = normalize_by(by)
    if norm_by is None:
        return 0.0, ['无法识别的定位方式 %r' % (by,)]

    base = BASE_SCORE.get(norm_by, 0.30)
    score = base
    reasons.append('基准 %.2f（%s）' % (base, BY_LABEL_CN.get(norm_by, norm_by)))

    text = str(value or '')
    opts = opts or {}

    # ---- 扣分 ----
    if RANDOM_FRAGMENT_RE.search(text):
        score -= 0.40
        reasons.append('-0.40 含随机/构建期生成的片段（跨次构建会变，随时失效）')

    nth_hits = len(NTH_RE.findall(text))
    if nth_hits:
        delta = 0.12 * nth_hits
        score -= delta
        reasons.append('-%.2f 含 %d 处 nth-child/nth-of-type 结构依赖'
                       % (delta, nth_hits))

    fw = FRAMEWORK_CLASS_RE.findall(text)
    if fw:
        score -= 0.20
        reasons.append('-0.20 含 UI 框架类名 %s（框架升级即失效，无语义）'
                       % ('、'.join(sorted(set(fw))[:3])))

    if VUE_SCOPED_RE.search(text):
        score -= 0.10
        reasons.append('-0.10 含 Vue scoped 属性 data-v-xxx')

    if len(text) > MAX_VALUE_LEN:
        score -= 0.10
        reasons.append('-0.10 表达式过长（%d 字符），脆弱且不可读' % len(text))

    if aria_guessed:
        score -= 0.15
        reasons.append('-0.15 该候选的 role 是从步骤类型**推测**的（源数据只给了无障碍名）')

    # ---- 加成 ----
    if match_count == 1:
        score += 0.04
        reasons.append('+0.04 页面内唯一匹配')
    elif match_count is not None and match_count > 1:
        # 设计方案只写了「唯一 +0.04」；这里补上「歧义」的反向项。
        # 理由：不唯一意味着每次执行都可能命中不同元素，是比"脆弱"更危险的问题，
        #       必须让它排到唯一候选后面，否则审阅台的默认选项就是错的。
        score -= 0.10
        reasons.append('-0.10 匹配到 %d 个元素（歧义，执行结果不确定）' % match_count)

    # ---- 语义化 id 的额外判定 ----
    # 基准表里 id=0.70 的前提是「语义化 id」。纯数字/自增 id 没有语义，应降级到 css 档。
    if norm_by == 'id' and re.fullmatch(r'\d+|[\-_]?\d{3,}', text or ''):
        score -= 0.25
        reasons.append('-0.25 id 为纯数字/自增形态，无语义（多为框架自动生成）')

    score = max(0.0, min(1.0, round(score, 4)))
    return score, reasons


def rank_candidates(candidates):
    """给候选列表打分并排序（高分在前）。

    入参 candidates: [{'by','value','opts','match_count','aria_guessed','source'}, ...]
    返回：新的列表（不修改入参），每项已补上 score / reasons

    排序键：score 降序；同分时按「定位方式的语义等级」再排一次，
    保证同分情况下 role > label > placeholder > text > alt text > id > css > xpath，
    结果是确定的（可复现，便于单测断言）。
    """
    ranked = []
    for cand in candidates or []:
        if not isinstance(cand, dict):
            continue
        by = cand.get('by')
        value = cand.get('value')
        if not by or value is None or value == '':
            continue
        score, reasons = score_locator(
            by, value,
            opts=cand.get('opts'),
            match_count=cand.get('match_count'),
            aria_guessed=bool(cand.get('aria_guessed')),
        )
        item = dict(cand)
        item['by'] = normalize_by(by) or by
        item['score'] = score
        item['reasons'] = reasons
        # 给个一句话结论，方便审阅台直接显示
        item['reason'] = reasons[0] if reasons else ''
        ranked.append(item)

    order = {name: i for i, name in enumerate(
        ['role', 'label', 'placeholder', 'text', 'alt text', 'id', 'css', 'xpath'])}
    ranked.sort(key=lambda c: (-c['score'], order.get(c['by'], 99),
                               str(c.get('value') or '')))
    return ranked


def dedupe_candidates(candidates):
    """按 (by, value) 去重，保留首个（即来源优先级更高的那个）。"""
    seen = set()
    out = []
    for cand in candidates or []:
        key = (cand.get('by'), str(cand.get('value')))
        if key in seen:
            continue
        seen.add(key)
        out.append(cand)
    return out


def score_grade(score):
    """把分数映射成审阅台用的三档色标。"""
    if score >= 0.85:
        return 'high'
    if score >= 0.60:
        return 'mid'
    return 'low'
