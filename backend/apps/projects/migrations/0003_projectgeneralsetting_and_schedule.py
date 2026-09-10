from datetime import datetime

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


def create_cleanup_schedule(apps, schema_editor):
    """创建每日回放文件清理定时任务（django-q）"""
    Schedule = apps.get_model('django_q', 'Schedule')
    cron_expr = '30 3 * * *'
    try:
        from croniter import croniter
        next_run = croniter(cron_expr, timezone.localtime()).get_next(datetime)
    except Exception:
        next_run = timezone.now()

    Schedule.objects.get_or_create(
        name='trace_files_daily_cleanup',
        defaults={
            'func': 'apps.projects.tasks.cleanup_trace_files',
            'schedule_type': 'C',  # Schedule.CRON
            'cron': cron_expr,
            'next_run': next_run,
            'repeats': -1,
        }
    )


def remove_cleanup_schedule(apps, schema_editor):
    Schedule = apps.get_model('django_q', 'Schedule')
    Schedule.objects.filter(name='trace_files_daily_cleanup').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_historicalproject'),
        ('django_q', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectGeneralSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_delete', models.BooleanField(default=False, help_text='逻辑删除', verbose_name='逻辑删除')),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='更新时间', verbose_name='更新时间')),
                ('trace_retention_days', models.IntegerField(default=30, help_text='Trace/视频回放文件保留天数，超期后由定时任务自动清理', verbose_name='回放文件保留天数')),
                ('create_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_create_by', to=settings.AUTH_USER_MODEL)),
                ('update_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_update_by', to=settings.AUTH_USER_MODEL)),
                ('project', models.OneToOneField(help_text='配置所属的项目', on_delete=django.db.models.deletion.CASCADE, related_name='general_setting', to='projects.project', verbose_name='所属项目')),
            ],
            options={
                'db_table': 'tb_project_general_setting',
                'verbose_name': '项目通用设置',
                'verbose_name_plural': '项目通用设置',
            },
        ),
        migrations.RunPython(create_cleanup_schedule, remove_cleanup_schedule),
    ]
