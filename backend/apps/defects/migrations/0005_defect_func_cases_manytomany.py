from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defects', '0004_update_defect_module_assignee'),
        ('tests', '0005_historicalcase_historicalfunccase_historicalstep'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='defect',
            name='case',
        ),
        migrations.AddField(
            model_name='defect',
            name='func_cases',
            field=models.ManyToManyField(blank=True, help_text='关联功能用例', related_name='defects', to='tests.funccase'),
        ),
    ]
