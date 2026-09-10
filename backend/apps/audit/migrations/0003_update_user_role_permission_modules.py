"""数据迁移：更新用户/角色/权限模块名称为列表后缀"""

from django.db import migrations


# 旧名 → 新名
MODULE_NAME_MIGRATION = {
    '用户': '用户列表',
    '角色': '角色列表',
    '权限': '权限列表',
}


def update_module_names(apps, schema_editor):
    AuditLog = apps.get_model('audit', 'AuditLog')
    for old_name, new_name in MODULE_NAME_MIGRATION.items():
        AuditLog.objects.filter(module=old_name).update(module=new_name)


def reverse_update(apps, schema_editor):
    AuditLog = apps.get_model('audit', 'AuditLog')
    for old_name, new_name in MODULE_NAME_MIGRATION.items():
        AuditLog.objects.filter(module=new_name).update(module=old_name)


class Migration(migrations.Migration):
    dependencies = [
        ('audit', '0002_update_module_names'),
    ]
    operations = [
        migrations.RunPython(update_module_names, reverse_update),
    ]
