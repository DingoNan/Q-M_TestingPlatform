from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defects', '0002_add_defect_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='defect',
            name='actual_result',
            field=models.TextField(blank=True, default='', verbose_name='实际结果'),
        ),
        migrations.AddField(
            model_name='defect',
            name='expected_result',
            field=models.TextField(blank=True, default='', verbose_name='预期结果'),
        ),
    ]
