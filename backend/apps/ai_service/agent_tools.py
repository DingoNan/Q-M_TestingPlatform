"""
AI助手 Agent 工具集
定义LangChain Tool，通过Django ORM查询测试平台数据
"""
import logging
from langchain_core.tools import tool

from apps.tests.models import FuncCase, Case, CaseRunLog
from apps.interfaces.models import Api
from apps.envs.models import Module, Service
from apps.suites.models import Suite, TestPlan, TestPlanFuncCase, CrontabTask
from apps.reports.models import Report
from apps.projects.models import ProjectMember
from apps.users.models import User
from apps.defects.models import Defect

logger = logging.getLogger('ai_service')

# 状态映射
CASE_STATUS_MAP = {1: '待修改', 2: '待评审', 3: '已评审'}
AUTO_STATUS_MAP = {1: '已完成', 2: '进行中', 3: '待开始', 4: '手工测试'}
CAN_AUTO_MAP = {1: '全自动化', 2: '半自动化', 3: '手工测试'}
API_STATUS_MAP = {
    1: '已发布', 2: '设计中', 3: '待确定', 4: '开发', 5: '对接',
    6: '测试', 7: '完成', 8: '异常', 9: '维护', 10: '废弃'
}
CASE_TYPE_MAP = {1: 'API', 2: 'WEB_UI', 3: 'APP_UI', 4: 'DATA', 5: 'Performance'}
CASE_RESULT_MAP = {1: '成功', 2: '失败', 3: '错误', 4: '未执行'}
EXEC_STATUS_MAP = {1: '未执行', 2: '暂缓', 3: '已通过', 4: '未通过', 5: '进行中'}
PLANT_TYPE_MAP = {1: 'API', 2: 'WEB_UI', 3: 'APP_UI'}


def _get_case_status(value):
    return CASE_STATUS_MAP.get(value, str(value))


def _get_auto_status(value):
    return AUTO_STATUS_MAP.get(value, str(value))


def _truncate(text, length=80):
    if not text:
        return ''
    return text[:length] + '...' if len(text) > length else text


@tool
def get_project_overview(project_id: int) -> str:
    """获取项目整体统计数据概览，包括功能用例数、自动化用例数、接口数、测试报告数、测试计划数、定时任务数等。
    当用户询问项目概况、统计数据、有多少用例等概览性问题时使用此工具。

    Args:
        project_id: 项目ID
    """
    try:
        func_case_count = FuncCase.objects.filter(project_id=project_id, is_delete=False).count()
        auto_case_count = Case.objects.filter(project_id=project_id, is_delete=False).count()
        api_count = Api.objects.filter(module__project_id=project_id, is_delete=False).count()
        report_count = Report.objects.filter(project_id=project_id, is_delete=False).count()
        plan_count = TestPlan.objects.filter(project_id=project_id, is_delete=False).count()
        suite_count = Suite.objects.filter(project_id=project_id, is_delete=False).count()
        crontab_count = CrontabTask.objects.filter(project_id=project_id, is_delete=False, enabled=True).count()
        module_count = Module.objects.filter(project_id=project_id, is_delete=False).count()

        # ===== 功能用例状态分布（含占比） =====
        status_dist = {}
        for status_val, status_label in CASE_STATUS_MAP.items():
            cnt = FuncCase.objects.filter(
                project_id=project_id, is_delete=False, case_status=status_val
            ).count()
            pct = round(cnt / func_case_count * 100, 1) if func_case_count > 0 else 0
            status_dist[status_label] = {'count': cnt, 'percent': pct}

        # ===== 功能用例自动化状态分布 =====
        auto_status_dist = {}
        for auto_val, auto_label in AUTO_STATUS_MAP.items():
            cnt = FuncCase.objects.filter(
                project_id=project_id, is_delete=False, auto_status=auto_val
            ).count()
            pct = round(cnt / func_case_count * 100, 1) if func_case_count > 0 else 0
            auto_status_dist[auto_label] = {'count': cnt, 'percent': pct}

        # ===== 功能用例模块分布（Top 5） =====
        from django.db.models import Count
        module_dist_qs = (
            FuncCase.objects.filter(project_id=project_id, is_delete=False)
            .values('module_id', 'module__name')
            .annotate(cnt=Count('id'))
            .order_by('-cnt')[:5]
        )
        module_dist = []
        for md in module_dist_qs:
            module_name = md['module__name'] or '未分配'
            cnt = md['cnt']
            pct = round(cnt / func_case_count * 100, 1) if func_case_count > 0 else 0
            module_dist.append(f"  - {module_name}: {cnt}条 ({pct}%)")

        # ===== 最近5份报告的通过率 =====
        recent_reports = Report.objects.filter(project_id=project_id, is_delete=False).order_by('-create_time')[:5]
        report_list = []
        avg_pass_rate = 0
        for r in recent_reports:
            total = r.all_case_number or 0
            passed = r.success_case_number or 0
            failed = r.fail_case_number or 0
            errors = r.error_case_number or 0
            pass_rate = round(passed / total * 100, 1) if total > 0 else 0
            avg_pass_rate += pass_rate
            report_list.append(
                f"  - [ID:{r.id}] {r.name}\n"
                f"    通过率 {pass_rate}% (通过{passed}/总数{total}, 失败{failed}, 错误{errors})\n"
                f"    创建时间: {r.create_time.strftime('%Y-%m-%d %H:%M')}"
            )
        if recent_reports:
            avg_pass_rate = round(avg_pass_rate / len(recent_reports), 1)

        # ===== 组装结果 =====
        result = f"""【项目概览统计】
基础数据：
- 功能测试用例: {func_case_count} 条
- 自动化用例: {auto_case_count} 条
- 接口数: {api_count} 个
- 测试报告: {report_count} 份
- 测试计划: {plan_count} 个
- 测试套件: {suite_count} 个
- 启用的定时任务: {crontab_count} 个
- 模块数: {module_count} 个

功能用例状态分布（总数 {func_case_count} 条）：
- 待修改: {status_dist['待修改']['count']}条 ({status_dist['待修改']['percent']}%)
- 待评审: {status_dist['待评审']['count']}条 ({status_dist['待评审']['percent']}%)
- 已评审: {status_dist['已评审']['count']}条 ({status_dist['已评审']['percent']}%)

功能用例自动化状态分布：
- 已完成: {auto_status_dist['已完成']['count']}条 ({auto_status_dist['已完成']['percent']}%)
- 进行中: {auto_status_dist['进行中']['count']}条 ({auto_status_dist['进行中']['percent']}%)
- 待开始: {auto_status_dist['待开始']['count']}条 ({auto_status_dist['待开始']['percent']}%)
- 手工测试: {auto_status_dist['手工测试']['count']}条 ({auto_status_dist['手工测试']['percent']}%)

功能用例模块分布（Top 5）：
"""
        if module_dist:
            result += '\n'.join(module_dist)
        else:
            result += '  暂无数据'

        result += f"\n\n最近{len(recent_reports)}份测试报告（平均通过率 {avg_pass_rate}%）："
        if report_list:
            result += '\n' + '\n'.join(report_list)
        else:
            result += '\n  暂无测试报告'

        return result
    except Exception as e:
        logger.error(f"[Agent] get_project_overview 失败: {e}", exc_info=True)
        return f"查询项目概览失败: {str(e)}"


@tool
def query_func_cases(project_id: int, keyword: str = '', case_status: int = 0, module_id: int = 0, limit: int = 20) -> str:
    """查询功能测试用例列表。支持按名称关键词搜索、按用例状态筛选、按模块筛选。
    当用户询问有哪些功能用例、按条件查找用例时使用此工具。

    Args:
        project_id: 项目ID
        keyword: 用例名称关键词（模糊搜索），为空则不筛选
        case_status: 用例状态（1=待修改, 2=待评审, 3=已评审），0表示不筛选
        module_id: 模块ID，0表示不筛选
        limit: 返回最大条数，默认20
    """
    try:
        qs = FuncCase.objects.filter(project_id=project_id, is_delete=False)
        if keyword:
            qs = qs.filter(name__icontains=keyword)
        if case_status:
            qs = qs.filter(case_status=case_status)
        if module_id:
            qs = qs.filter(module_id=module_id)
        total = qs.count()

        if total == 0:
            filter_hint = []
            if keyword:
                filter_hint.append(f"关键词：{keyword}")
            if case_status:
                filter_hint.append(f"状态：{_get_case_status(case_status)}")
            return f"未找到匹配的功能用例。筛选条件: {', '.join(filter_hint) if filter_hint else '无'}"

        cases = qs.select_related('owner', 'module')[:limit]

        # ===== 当前筛选结果的状态分布 =====
        from django.db.models import Count
        status_stats = qs.values('case_status').annotate(cnt=Count('id'))
        status_summary = []
        for s in status_stats:
            label = _get_case_status(s['case_status'])
            cnt = s['cnt']
            pct = round(cnt / total * 100, 1) if total > 0 else 0
            status_summary.append(f"  - {label}: {cnt}条 ({pct}%)")

        # ===== 当前筛选结果的模块分布（Top 5） =====
        module_stats = qs.values('module_id', 'module__name').annotate(cnt=Count('id')).order_by('-cnt')[:5]
        module_summary = []
        for m in module_stats:
            module_name = m['module__name'] or '未分配'
            cnt = m['cnt']
            pct = round(cnt / total * 100, 1) if total > 0 else 0
            module_summary.append(f"  - {module_name}: {cnt}条 ({pct}%)")

        # ===== 当前筛选结果的自动化状态分布 =====
        auto_stats = qs.values('auto_status').annotate(cnt=Count('id'))
        auto_summary = []
        for a in auto_stats:
            label = _get_auto_status(a['auto_status'])
            cnt = a['cnt']
            pct = round(cnt / total * 100, 1) if total > 0 else 0
            auto_summary.append(f"  - {label}: {cnt}条 ({pct}%)")

        # ===== 筛选条件说明 =====
        filter_hint = []
        if keyword:
            filter_hint.append(f"关键词「{keyword}」")
        if case_status:
            filter_hint.append(f"状态「{_get_case_status(case_status)}」")
        if module_id:
            try:
                mod = Module.objects.get(id=module_id)
                filter_hint.append(f"模块「{mod.name}」")
            except Module.DoesNotExist:
                pass

        # ===== 用例列表 =====
        lines = [
            f"【功能用例查询结果】",
            f"筛选条件: {', '.join(filter_hint) if filter_hint else '全部'}",
            f"匹配总数: {total} 条（显示前 {len(cases)} 条）",
            "",
            "状态分布:",
        ]
        lines.extend(status_summary)
        lines.append("")
        lines.append("模块分布（Top 5）:")
        if module_summary:
            lines.extend(module_summary)
        else:
            lines.append("  暂无数据")
        lines.append("")
        lines.append("自动化状态:")
        lines.extend(auto_summary)
        lines.append("")
        lines.append(f"用例列表（前{len(cases)}条）:")

        for idx, c in enumerate(cases, 1):
            module_name = c.module.name if c.module else '未分配'
            owner_name = c.owner.username if c.owner else '未分配'
            tags = list(c.tag.all().values_list('name', flat=True))
            tag_str = f"标签:{','.join(tags)}" if tags else ""
            lines.append(
                f"  {idx}. [ID:{c.id}] {c.name}\n"
                f"     状态:{_get_case_status(c.case_status)} • 模块:{module_name} • 负责人:{owner_name} • 自动化:{_get_auto_status(c.auto_status)}"
                + (f" • {tag_str}" if tag_str else "")
            )

        if total > len(cases):
            lines.append(f"  ... 还有 {total - len(cases)} 条未显示，可缩小筛选范围查看更多")

        return '\n'.join(lines)
    except Exception as e:
        logger.error(f"[Agent] query_func_cases 失败: {e}", exc_info=True)
        return f"查询功能用例失败: {str(e)}"


@tool
def query_func_case_detail(project_id: int, case_id: int) -> str:
    """查询单个功能测试用例的详细信息，包括前置条件、步骤、备注等。
    当用户想查看某个具体用例的详细内容时使用此工具。

    Args:
        project_id: 项目ID
        case_id: 用例ID
    """
    try:
        c = FuncCase.objects.select_related('owner', 'module', 'project').get(
            id=case_id, project_id=project_id, is_delete=False
        )
        result = f"""用例详情 [ID:{c.id}]：
- 名称: {c.name}
- 状态: {_get_case_status(c.case_status)}
- 自动化状态: {_get_auto_status(c.auto_status)}
- 可自动化: {CAN_AUTO_MAP.get(c.can_autoed, str(c.can_autoed))}
- 模块: {c.module.name if c.module else '未分配'}
- 负责人: {c.owner.username if c.owner else '未分配'}
- 前置条件: {c.setup_condition or '无'}
- 备注: {c.case_mark or '无'}
- 步骤类型: {'文本描述' if c.step_type == 1 else '表格步骤'}"""

        if c.step_type == 1:
            result += f"\n- 文本步骤: {_truncate(c.step_text, 200)}"
            result += f"\n- 期望结果: {_truncate(c.exp_text, 200)}"
        elif c.step_table:
            result += "\n- 步骤明细:"
            for i, step in enumerate(c.step_table, 1):
                step_desc = step.get('step_desc', '')
                step_exp = step.get('step_exp', '')
                result += f"\n  {i}. {step_desc} → 预期: {step_exp}"

        # 关联标签
        tags = list(c.tag.all().values_list('name', flat=True))
        if tags:
            result += f"\n- 标签: {', '.join(tags)}"

        return result
    except FuncCase.DoesNotExist:
        return f"用例ID {case_id} 不存在。"
    except Exception as e:
        logger.error(f"[Agent] query_func_case_detail 失败: {e}")
        return f"查询用例详情失败: {str(e)}"


@tool
def query_apis(project_id: int, keyword: str = '', method: str = '', status: int = 0, limit: int = 20) -> str:
    """查询接口列表。支持按名称关键词搜索、按请求方法筛选、按接口状态筛选。
    当用户询问有哪些接口、查找某个接口时使用此工具。

    Args:
        project_id: 项目ID
        keyword: 接口名称关键词（模糊搜索），为空则不筛选
        method: 请求方法（GET/POST/PUT/DELETE等），为空则不筛选
        status: 接口状态（1=已发布,2=设计中,3=待确定,4=开发,5=对接,6=测试,7=完成,8=异常,9=维护,10=废弃），0表示不筛选
        limit: 返回最大条数，默认20
    """
    try:
        qs = Api.objects.filter(module__project_id=project_id, is_delete=False)
        if keyword:
            qs = qs.filter(name__icontains=keyword)
        if method:
            qs = qs.filter(method__iexact=method)
        if status:
            qs = qs.filter(status=status)
        total = qs.count()
        apis = qs.select_related('service', 'module')[:limit]

        if not apis.exists():
            return "未找到匹配的接口。"

        lines = [f"共找到 {total} 个接口（显示前 {len(apis)} 个）：\n"]
        for a in apis:
            service_name = a.service.name if a.service else '未分配'
            lines.append(
                f"- [ID:{a.id}] {a.name}\n"
                f"  {a.method} {a.url} | 状态: {API_STATUS_MAP.get(a.status, str(a.status))} | 服务: {service_name}"
            )
        return '\n'.join(lines)
    except Exception as e:
        logger.error(f"[Agent] query_apis 失败: {e}")
        return f"查询接口失败: {str(e)}"


@tool
def query_automation_cases(project_id: int, keyword: str = '', case_type: int = 0, result: int = 0, limit: int = 20) -> str:
    """查询自动化测试用例列表。支持按名称搜索、按用例类型（API/WEB_UI/APP_UI等）和执行结果筛选。
    当用户询问自动化用例、脚本用例时使用此工具。

    Args:
        project_id: 项目ID
        keyword: 用例名称关键词（模糊搜索），为空则不筛选
        case_type: 用例类型（1=API,2=WEB_UI,3=APP_UI,4=DATA,5=Performance），0表示不筛选
        result: 最近执行结果（1=成功,2=失败,3=错误,4=未执行），0表示不筛选
        limit: 返回最大条数，默认20
    """
    try:
        qs = Case.objects.filter(project_id=project_id, is_delete=False)
        if keyword:
            qs = qs.filter(name__icontains=keyword)
        if case_type:
            qs = qs.filter(type=case_type)
        if result:
            qs = qs.filter(recent_test_result=result)
        total = qs.count()
        cases = qs.select_related('module')[:limit]

        if not cases.exists():
            return "未找到匹配的自动化用例。"

        lines = [f"共找到 {total} 条自动化用例（显示前 {len(cases)} 条）：\n"]
        for c in cases:
            module_name = c.module.name if c.module else '未分配'
            lines.append(
                f"- [ID:{c.id}] {c.name}\n"
                f"  类型: {CASE_TYPE_MAP.get(c.type, str(c.type))} | 模块: {module_name} | "
                f"最近结果: {CASE_RESULT_MAP.get(c.recent_test_result, str(c.recent_test_result))}"
            )
        return '\n'.join(lines)
    except Exception as e:
        logger.error(f"[Agent] query_automation_cases 失败: {e}")
        return f"查询自动化用例失败: {str(e)}"


@tool
def query_test_reports(project_id: int, limit: int = 10) -> str:
    """查询测试报告列表，包括每份报告的用例总数、成功数、失败数、错误数和通过率。
    当用户询问测试报告、执行结果、通过率时使用此工具。

    Args:
        project_id: 项目ID
        limit: 返回最大条数，默认10
    """
    try:
        reports = Report.objects.filter(project_id=project_id, is_delete=False).order_by('-create_time')[:limit]
        if not reports.exists():
            return "暂无测试报告。"

        lines = [f"最近 {len(reports)} 份测试报告：\n"]
        total_pass_rate = 0
        for r in reports:
            total = r.all_case_number or 0
            passed = r.success_case_number or 0
            failed = r.fail_case_number or 0
            errors = r.error_case_number or 0
            pass_rate = round(passed / total * 100, 1) if total > 0 else 0
            total_pass_rate += pass_rate
            lines.append(
                f"- [ID:{r.id}] {r.name}\n"
                f"  总数: {total} | 成功: {passed} | 失败: {failed} | 错误: {errors} | 通过率: {pass_rate}%\n"
                f"  创建时间: {r.create_time.strftime('%Y-%m-%d %H:%M')}"
            )

        if reports:
            avg_pass_rate = round(total_pass_rate / len(reports), 1)
            lines.append(f"\n平均通过率: {avg_pass_rate}%")

        return '\n'.join(lines)
    except Exception as e:
        logger.error(f"[Agent] query_test_reports 失败: {e}")
        return f"查询测试报告失败: {str(e)}"


@tool
def query_test_plans(project_id: int, limit: int = 10) -> str:
    """查询测试计划列表，包括每个计划的用例执行进度（未执行/已通过/未通过/进行中等状态分布）。
    当用户询问测试计划、执行进度时使用此工具。

    Args:
        project_id: 项目ID
        limit: 返回最大条数，默认10
    """
    try:
        plans = TestPlan.objects.filter(project_id=project_id, is_delete=False).order_by('-create_time')[:limit]
        if not plans.exists():
            return "暂无测试计划。"

        lines = [f"最近 {len(plans)} 个测试计划：\n"]
        for p in plans:
            total_cases = TestPlanFuncCase.objects.filter(test_plan=p, is_delete=False).count()
            status_dist = {}
            for status_val, status_label in EXEC_STATUS_MAP.items():
                status_dist[status_label] = TestPlanFuncCase.objects.filter(
                    test_plan=p, is_delete=False, exec_status=status_val
                ).count()

            lines.append(
                f"- [ID:{p.id}] {p.name}\n"
                f"  总用例数: {total_cases} | 未执行: {status_dist['未执行']} | "
                f"已通过: {status_dist['已通过']} | 未通过: {status_dist['未通过']} | "
                f"进行中: {status_dist['进行中']} | 暂缓: {status_dist['暂缓']}\n"
                f"  描述: {_truncate(p.desc, 100)}"
            )
        return '\n'.join(lines)
    except Exception as e:
        logger.error(f"[Agent] query_test_plans 失败: {e}")
        return f"查询测试计划失败: {str(e)}"


@tool
def query_modules(project_id: int) -> str:
    """查询项目的模块树结构，包括模块名称和层级关系。
    当用户询问项目有哪些模块、模块结构时使用此工具。

    Args:
        project_id: 项目ID
    """
    try:
        modules = Module.objects.filter(project_id=project_id, is_delete=False).order_by('id')
        if not modules.exists():
            return "该项目暂无模块。"

        # 构建树结构
        module_map = {m.id: {'name': m.name, 'parent_id': m.parent_id, 'children': []} for m in modules}
        roots = []
        for m in modules:
            if m.parent_id and m.parent_id in module_map:
                module_map[m.parent_id]['children'].append(module_map[m.id])
            else:
                roots.append(module_map[m.id])

        def render_tree(nodes, indent=0):
            lines = []
            for node in nodes:
                prefix = '  ' * indent + ('├─ ' if indent > 0 else '')
                lines.append(f"{prefix}{node['name']}")
                if node['children']:
                    lines.extend(render_tree(node['children'], indent + 1))
            return lines

        tree_lines = render_tree(roots)
        return f"项目模块树（共 {len(modules)} 个模块）：\n" + '\n'.join(tree_lines)
    except Exception as e:
        logger.error(f"[Agent] query_modules 失败: {e}")
        return f"查询模块失败: {str(e)}"


@tool
def query_crontab_tasks(project_id: int, enabled_only: bool = True) -> str:
    """查询项目的定时任务列表，包括定时策略、关联的测试套件和环境信息。
    当用户询问定时任务、定时执行、Crontab任务时使用此工具。

    Args:
        project_id: 项目ID
        enabled_only: 是否只查询已启用的定时任务，默认True
    """
    try:
        qs = CrontabTask.objects.filter(project_id=project_id, is_delete=False)
        if enabled_only:
            qs = qs.filter(enabled=True)
        tasks = qs.select_related('suite', 'env').order_by('-create_time')

        if not tasks.exists():
            return "未找到定时任务。"

        lines = [f"共找到 {len(tasks)} 个定时任务：\n"]
        for t in tasks:
            suite_name = t.suite.name if t.suite else '未关联'
            env_name = t.env.name if t.env else '未关联'
            status_str = '启用' if t.enabled else '禁用'
            lines.append(
                f"- [ID:{t.id}] {t.desc or '无描述'}\n"
                f"  套件: {suite_name} | 环境: {env_name} | 定时策略: {t.crontab} | 状态: {status_str}"
            )
        return '\n'.join(lines)
    except Exception as e:
        logger.error(f"[Agent] query_crontab_tasks 失败: {e}")
        return f"查询定时任务失败: {str(e)}"


# 工具列表导出
DEFECT_STATUS_MAP = {1: '待处理', 2: '处理中', 3: '已解决', 4: '已关闭'}
DEFECT_SEVERITY_MAP = {1: '致命', 2: '严重', 3: '一般', 4: '轻微'}
DEFECT_TYPE_MAP = {1: '代码问题-前端', 2: '代码问题-后端', 3: '设计如此', 4: '重复BUG', 5: '需求变动', 6: 'UI样式', 7: '设计缺陷'}


@tool
def query_defects(project_id: int, keyword: str = '', status: int = 0,
                  severity: int = 0, module_id: int = 0, limit: int = 20,
                  only_resolved: bool = False) -> str:
    """查询缺陷列表。支持关键词搜索、状态/严重程度/模块筛选，可选择只看已解决缺陷。
    当用户询问BUG、缺陷、问题时使用此工具。

    Args:
        project_id: 项目ID
        keyword: 缺陷标题关键词（模糊搜索），为空则不筛选
        status: 缺陷状态（1=待处理,2=处理中,3=已解决,4=已关闭），0表示不筛选
        severity: 严重程度（1=轻微,2=一般,3=严重,4=致命），0表示不筛选
        module_id: 模块ID，0表示不筛选
        limit: 返回最大条数，默认20
        only_resolved: 是否只查询已解决/已关闭的缺陷，默认False
    """
    try:
        qs = Defect.objects.filter(project_id=project_id, is_delete=False)
        if keyword:
            qs = qs.filter(title__icontains=keyword)
        if status:
            qs = qs.filter(status=status)
        if severity:
            qs = qs.filter(severity=severity)
        if module_id:
            qs = qs.filter(module_id=module_id)
        if only_resolved:
            qs = qs.filter(status__in=[3, 4])

        total = qs.count()
        if total == 0:
            return f"未找到匹配的缺陷。"

        from django.db.models import Count
        severity_stats = qs.values('severity').annotate(cnt=Count('id')).order_by('-cnt')
        status_stats = qs.values('status').annotate(cnt=Count('id')).order_by('-cnt')

        lines = [f"【缺陷查询结果】", f"匹配总数: {total} 条", ""]

        lines.append("严重程度分布:")
        for s in severity_stats:
            label = DEFECT_SEVERITY_MAP.get(s['severity'], str(s['severity']))
            pct = round(s['cnt'] / total * 100, 1) if total > 0 else 0
            lines.append(f"  - {label}: {s['cnt']}条 ({pct}%)")

        lines.append("状态分布:")
        for s in status_stats:
            label = DEFECT_STATUS_MAP.get(s['status'], str(s['status']))
            pct = round(s['cnt'] / total * 100, 1) if total > 0 else 0
            lines.append(f"  - {label}: {s['cnt']}条 ({pct}%)")

        lines.append("")
        lines.append(f"缺陷列表（前{min(limit, total)}条）:")
        defects = qs.select_related('module')[:limit]
        for idx, d in enumerate(defects, 1):
            module_name = d.module.name if d.module else '未分配'
            lines.append(
                f"  {idx}. [ID:{d.id}] {d.title}\n"
                f"     严重度:{DEFECT_SEVERITY_MAP.get(d.severity, str(d.severity))} • "
                f"类型:{DEFECT_TYPE_MAP.get(d.defect_type, str(d.defect_type))} • "
                f"状态:{DEFECT_STATUS_MAP.get(d.status, str(d.status))} • "
                f"模块:{module_name}\n"
                f"     描述: {_truncate(d.description, 60)}"
            )

        return '\n'.join(lines)
    except Exception as e:
        logger.error(f"[Agent] query_defects 失败: {e}", exc_info=True)
        return f"查询缺陷失败: {str(e)}"


@tool
def query_knowledge_base(project_id: int, query: str, top_k: int = 5) -> str:
    """从项目知识库中语义搜索相关内容，包括功能用例、接口文档、缺陷和页面元素。
    当用户询问"某个功能/操作应该怎么做"、"如何测试某个功能"、"有没有类似的用例"、
    "有没有这个功能的记录或步骤"、"怎么预约会议室"等需要参考项目既有业务内容的问题时，
    必须使用此工具从知识库检索相关内容后回答。

    Args:
        project_id: 项目ID
        query: 自然语言查询内容
        top_k: 返回最大条数，默认5
    """
    try:
        from apps.ai_service.vectorstore import search_knowledge_base, build_rag_context
        results = search_knowledge_base(
            project_id=project_id,
            query=query,
            top_k=top_k,
        )
        if not results:
            return "知识库中未找到相关内容。"

        context = build_rag_context(results, max_items=top_k)
        return context
    except Exception as e:
        logger.error(f"[Agent] query_knowledge_base 失败: {e}", exc_info=True)
        return f"知识库查询失败: {str(e)}"


ALL_TOOLS = [
    get_project_overview,
    query_func_cases,
    query_func_case_detail,
    query_apis,
    query_automation_cases,
    query_test_reports,
    query_test_plans,
    query_modules,
    query_crontab_tasks,
    query_defects,
    query_knowledge_base,
]
