import os
import shutil
import time
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

# 未配置时的默认保留天数
DEFAULT_TRACE_RETENTION_DAYS = 30


def get_project_retention_map():
    """项目ID -> 回放文件保留天数 映射"""
    from apps.projects.models import ProjectGeneralSetting

    return dict(
        ProjectGeneralSetting.objects.filter(is_delete=False)
        .values_list('project_id', 'trace_retention_days')
    )


def _parse_report_id(name):
    """
    从回放文件名解析报告ID
    文件名格式: pw_r{report_id}_{host}_{timestamp}_{uuid}.zip/.webm(/_vidtmp)
    """
    if not name.startswith('pw_r'):
        return None
    try:
        return int(name.split('_')[1][1:])
    except (IndexError, ValueError):
        return None


def cleanup_trace_files():
    """
    定时清理 Trace/视频回放文件（django-q 每日调度）
    按文件所属项目（通过报告 pw_r{report_id}_... 映射）配置的保留天数清理：
    - 清理 MEDIA_ROOT/traces 下超过保留天数的 .zip(Trace) 与 .webm(视频)
    - 顺带清理用例异常中断残留的 *_vidtmp 临时视频目录
    - 所属项目未配置保留天数时按默认天数清理；无法识别所属项目的文件按最保守的最长保留天数清理
    """
    from apps.reports.models import Report

    traces_dir = os.path.join(str(settings.MEDIA_ROOT), 'traces')
    if not os.path.isdir(traces_dir):
        return 'traces dir not found, skip'

    now = time.time()
    retention_map = get_project_retention_map()
    entries = os.listdir(traces_dir)

    # 批量映射 报告ID -> 项目ID（不过滤软删除，保证历史文件仍可归属项目）
    report_ids = {rid for rid in (_parse_report_id(name) for name in entries) if rid}
    report_project_map = dict(
        Report.objects.filter(id__in=report_ids).values_list('id', 'project_id')
    ) if report_ids else {}

    # 孤儿文件的兜底保留天数：取所有有效配置与默认值中的最大值
    orphan_days = max(retention_map.values(), default=DEFAULT_TRACE_RETENTION_DAYS)
    orphan_days = max(orphan_days, DEFAULT_TRACE_RETENTION_DAYS)

    removed_files, removed_dirs, freed_bytes = 0, 0, 0
    for name in entries:
        path = os.path.join(traces_dir, name)
        try:
            # 异常中断残留的临时视频目录
            if os.path.isdir(path):
                if not name.endswith('_vidtmp'):
                    continue
                report_id = _parse_report_id(name)
                days = orphan_days
                if report_id:
                    project_id = report_project_map.get(report_id)
                    days = retention_map.get(project_id, DEFAULT_TRACE_RETENTION_DAYS) if project_id else orphan_days
                if os.path.getmtime(path) < now - days * 86400:
                    shutil.rmtree(path, ignore_errors=True)
                    removed_dirs += 1
                continue

            if not name.lower().endswith(('.zip', '.webm')):
                continue

            # 解析 文件 -> 报告 -> 项目 -> 保留天数
            report_id = _parse_report_id(name)
            days = orphan_days
            if report_id:
                project_id = report_project_map.get(report_id)
                days = retention_map.get(project_id, DEFAULT_TRACE_RETENTION_DAYS) if project_id else orphan_days

            if os.path.getmtime(path) < now - days * 86400:
                freed_bytes += os.path.getsize(path)
                os.remove(path)
                removed_files += 1
        except OSError:
            continue

    summary = (
        f'projects={len(retention_map)}, '
        f'removed {removed_files} files({freed_bytes / 1024 / 1024:.1f}MB), '
        f'{removed_dirs} tmp dirs'
    )
    print(f'[cleanup_trace_files] {summary}')
    return summary


def cleanup_case_run_logs():
    """
    定时清理用例执行日志数据（django-q 每日调度）
    日志 JSON 内含 base64 截图，体积较大：
    - 按日志所属项目（CaseRunLog.case -> Case.project）配置的保留天数清理
    - 项目未配置时按默认天数清理
    - 直接物理删除（含已软删除记录）；报告本身不删除
    """
    from apps.projects.models import Project
    from apps.tests.models import CaseRunLog

    retention_map = get_project_retention_map()
    project_ids = list(Project.objects.filter(is_delete=False).values_list('id', flat=True))
    now = timezone.now()
    total_deleted = 0

    for project_id in project_ids:
        days = retention_map.get(project_id, DEFAULT_TRACE_RETENTION_DAYS)
        cutoff = now - timedelta(days=days)
        # 分批删除，避免大表长事务/长锁
        while True:
            ids = list(
                CaseRunLog.objects
                .filter(case__project_id=project_id, create_time__lt=cutoff)
                .values_list('id', flat=True)[:500]
            )
            if not ids:
                break
            deleted, _ = CaseRunLog.objects.filter(id__in=ids).delete()
            total_deleted += deleted

    print(f'[cleanup_case_run_logs] projects={len(project_ids)}, deleted {total_deleted} logs')
    return total_deleted


def cleanup_project_data():
    """每日定时任务统一入口：清理回放文件 + 用例执行日志数据"""
    files_summary = cleanup_trace_files()
    logs_deleted = cleanup_case_run_logs()
    return f'{files_summary}; logs_deleted={logs_deleted}'
