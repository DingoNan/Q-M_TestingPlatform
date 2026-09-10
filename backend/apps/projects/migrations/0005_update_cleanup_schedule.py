from django.db import migrations


def update_cleanup_schedule(apps, schema_editor):
    """定时任务入口改为 cleanup_project_data（回放文件 + 用例执行日志一并清理）"""
    Schedule = apps.get_model('django_q', 'Schedule')
    Schedule.objects.filter(name='trace_files_daily_cleanup').update(
        name='project_data_daily_cleanup',
        func='apps.projects.tasks.cleanup_project_data',
    )


def revert_cleanup_schedule(apps, schema_editor):
    Schedule = apps.get_model('django_q', 'Schedule')
    Schedule.objects.filter(name='project_data_daily_cleanup').update(
        name='trace_files_daily_cleanup',
        func='apps.projects.tasks.cleanup_trace_files',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_aiconfig_is_default'),
    ]

    operations = [
        migrations.RunPython(update_cleanup_schedule, revert_cleanup_schedule),
    ]
