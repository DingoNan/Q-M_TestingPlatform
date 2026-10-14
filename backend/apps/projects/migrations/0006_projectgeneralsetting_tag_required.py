from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_update_cleanup_schedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectgeneralsetting',
            name='tag_required',
            field=models.BooleanField(default=True, help_text='开启后新建/编辑用例时「用例标签」为必填项；关闭则允许不打标签', verbose_name='用例标签必填'),
        ),
    ]
