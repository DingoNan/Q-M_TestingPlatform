from django.db import models
from utils.base import BaseModel


class AiConversation(BaseModel):
    """
    AI对话会话表
    用于存储用户与AI的对话会话
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='ai_conversations',
        verbose_name='所属用户'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='ai_conversations',
        verbose_name='所属项目'
    )
    ai_config = models.ForeignKey(
        'projects.AiConfig',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='AI模型配置'
    )
    module = models.ForeignKey(
        'envs.Module',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='关联模块'
    )
    title = models.CharField(max_length=200, verbose_name='会话标题', default='新对话')

    class Meta:
        db_table = 'tb_ai_conversation'
        verbose_name = 'AI对话会话'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class AiMessage(BaseModel):
    """
    AI对话消息表
    存储对话中的每一条消息
    """
    class Role(models.TextChoices):
        USER = 'user', '用户'
        ASSISTANT = 'assistant', 'AI助手'

    conversation = models.ForeignKey(
        AiConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='所属会话'
    )
    role = models.CharField(
        max_length=20,
        verbose_name='消息角色',
        choices=Role.choices,
        default=Role.USER
    )
    content = models.TextField(verbose_name='消息内容')
    # 存储AI解析出的测试用例JSON（仅assistant消息）
    cases_data = models.JSONField(verbose_name='解析的用例数据', default=list, blank=True)

    class Meta:
        db_table = 'tb_ai_message'
        verbose_name = 'AI对话消息'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return f"{self.conversation.title} - {self.role}"
