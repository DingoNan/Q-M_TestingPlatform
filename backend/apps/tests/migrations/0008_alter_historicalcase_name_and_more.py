from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0007_relax_case_name_unique_for_soft_delete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalcase',
            name='name',
            field=models.CharField(max_length=50, verbose_name='用例名称'),
        ),
        migrations.AlterField(
            model_name='historicalfunccase',
            name='name',
            field=models.CharField(max_length=50, verbose_name='用例名称'),
        ),
    ]
