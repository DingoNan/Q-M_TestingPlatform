# 软删除后允许复用名称：
# 原 Case.name / FuncCase.name 带 unique=True，数据库唯一索引会把 is_delete=1 的
# 历史记录也算进去，导致同名的用例/功能用例删除后无法重建（报“用例名称不能重复”）。
# 现改为去掉数据库层唯一约束，唯一性由序列化器在 is_delete=False 集合内校验。
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0006_remove_case_web_engine_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='name',
            field=models.CharField(max_length=50, verbose_name='用例名称'),
        ),
        migrations.AlterField(
            model_name='funccase',
            name='name',
            field=models.CharField(max_length=50, verbose_name='用例名称'),
        ),
        migrations.AlterField(
            model_name='historicalcase',
            name='name',
            field=models.CharField(db_index=True, max_length=50, verbose_name='用例名称'),
        ),
        migrations.AlterField(
            model_name='historicalfunccase',
            name='name',
            field=models.CharField(db_index=True, max_length=50, verbose_name='用例名称'),
        ),
    ]
