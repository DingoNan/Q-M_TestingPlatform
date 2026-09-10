"""数据迁移：把审计日志 module 字段从旧中文名更新为菜单二级模块名称"""

from django.db import migrations


# 旧名 → 新名（与前端菜单二级模块名称对齐）
MODULE_NAME_MIGRATION = {
    '环境': '环境配置',
    '服务': '服务配置',
    '产品': '产品配置',
    '数据库': '数据库配置',
    '文件': '文件管理',
    '元素': '元素配置',
    '枚举': '常量配置',
    'Python脚本': '用户函数',
    '步骤': '步骤管理',
    '标签': '标签管理',
    '接口': '接口管理',
    '测试套件': '套件管理',
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
        ('audit', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(update_module_names, reverse_update),
    ]
