from django.db import migrations, models


def init_default_configs(apps, schema_editor):
    """存量数据初始化：每个项目将最早创建的启用配置设为默认"""
    AiConfig = apps.get_model('projects', 'AiConfig')
    projects = AiConfig.objects.filter(is_delete=False).values_list('project_id', flat=True).distinct()
    for project_id in projects:
        first = AiConfig.objects.filter(
            project_id=project_id, is_delete=False, is_active=True
        ).order_by('id').first()
        if first:
            AiConfig.objects.filter(project_id=project_id, is_default=True).exclude(id=first.id).update(is_default=False)
            AiConfig.objects.filter(id=first.id).update(is_default=True)


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_projectgeneralsetting_and_schedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='aiconfig',
            name='is_default',
            field=models.BooleanField(default=False, help_text='设为默认后，同项目下其他配置自动取消默认', verbose_name='是否默认'),
        ),
        migrations.RunPython(init_default_configs, migrations.RunPython.noop),
    ]
