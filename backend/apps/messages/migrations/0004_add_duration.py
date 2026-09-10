from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_messages', '0003_add_task_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='duration',
            field=models.FloatField(blank=True, null=True, verbose_name='耗时(秒)'),
        ),
    ]
