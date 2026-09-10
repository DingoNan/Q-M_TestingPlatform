from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0002_remove_step_fail_is_continue_remove_step_is_run_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='funccase',
            name='case_status',
            field=models.IntegerField(choices=[(1, '设计中'), (2, '待评审'), (3, '已评审')], default=2, verbose_name='用例状态'),
        ),
    ]
