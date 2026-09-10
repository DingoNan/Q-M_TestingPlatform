from django.db import models
from utils.base import BaseModel


class Message(BaseModel):
    """
    消息通知模型
    用于存储系统发送给用户的消息通知
    """
    class MessageType(models.IntegerChoices):
        SYSTEM = 1, '系统通知'
        TASK = 2, '任务通知'
        ALERT = 3, '告警通知'

    class TaskStatus(models.IntegerChoices):
        RUNNING = 1, '进行中'
        SUCCESS = 2, '已完成'
        FAILED = 3, '失败'

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='接收用户'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='关联项目'
    )
    title = models.CharField(max_length=200, verbose_name='消息标题')
    content = models.TextField(verbose_name='消息内容', blank=True, default='')
    message_type = models.IntegerField(
        verbose_name='消息类型',
        choices=MessageType.choices,
        default=MessageType.SYSTEM
    )
    is_read = models.BooleanField(verbose_name='是否已读', default=False)
    read_time = models.DateTimeField(verbose_name='阅读时间', null=True, blank=True)
    related_url = models.CharField(
        max_length=500,
        verbose_name='关联链接',
        blank=True,
        default=''
    )
    # 任务消息扩展字段
    task_status = models.IntegerField(
        verbose_name='任务状态',
        choices=TaskStatus.choices,
        null=True,
        blank=True
    )
    total_count = models.IntegerField(verbose_name='总数', null=True, blank=True)
    success_count = models.IntegerField(verbose_name='成功数', null=True, blank=True)
    failed_count = models.IntegerField(verbose_name='失败数', null=True, blank=True)
    fail_reason = models.TextField(verbose_name='失败原因', blank=True, default='')
    duration = models.FloatField(verbose_name='耗时(秒)', null=True, blank=True)

    class Meta:
        db_table = 'tb_message'
        verbose_name = '消息通知'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return f"{self.user.username} - {self.title}"