from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('defects', '0001_initial'),
    ]

    operations = [
        # 这个迁移已废弃，权限数据改由 apps/users/models.py 中的 create_super_user() 统一初始化
        # 保留此文件仅为保持迁移链完整性，供 0003 依赖
        migrations.RunPython(
            lambda apps, schema_editor: None,
            lambda apps, schema_editor: None,
        )
    ]