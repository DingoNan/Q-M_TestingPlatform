# Generated for ai_service app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('envs', '0001_initial'),
        ('projects', '0001_initial'),
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AiConversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_delete', models.BooleanField(default=False, help_text='逻辑删除', verbose_name='逻辑删除')),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='更新时间', verbose_name='更新时间')),
                ('title', models.CharField(default='新对话', max_length=200, verbose_name='会话标题')),
                ('ai_config', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='projects.aiconfig', verbose_name='AI模型配置')),
                ('module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='envs.module', verbose_name='关联模块')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_conversations', to='projects.project', verbose_name='所属项目')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_conversations', to=settings.AUTH_USER_MODEL, verbose_name='所属用户')),
                ('create_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_create_by', to=settings.AUTH_USER_MODEL)),
                ('update_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_update_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'AI对话会话',
                'verbose_name_plural': 'AI对话会话',
                'db_table': 'tb_ai_conversation',
                'ordering': ['-update_time'],
            },
        ),
        migrations.CreateModel(
            name='AiMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_delete', models.BooleanField(default=False, help_text='逻辑删除', verbose_name='逻辑删除')),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='更新时间', verbose_name='更新时间')),
                ('role', models.CharField(choices=[('user', '用户'), ('assistant', 'AI助手')], default='user', max_length=20, verbose_name='消息角色')),
                ('content', models.TextField(verbose_name='消息内容')),
                ('cases_data', models.JSONField(blank=True, default=list, verbose_name='解析的用例数据')),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='ai_service.aiconversation', verbose_name='所属会话')),
                ('create_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_create_by', to=settings.AUTH_USER_MODEL)),
                ('update_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_update_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'AI对话消息',
                'verbose_name_plural': 'AI对话消息',
                'db_table': 'tb_ai_message',
                'ordering': ['create_time'],
            },
        ),
    ]
