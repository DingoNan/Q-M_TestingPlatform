from django.db import models
from django.contrib.contenttypes.models import ContentType
from utils.base import BaseModel


class AuditLog(BaseModel):
    """审计日志模型 — 记录用户的所有写操作"""

    class Action(models.TextChoices):
        CREATE = 'create', '新增'
        UPDATE = 'update', '修改'
        DELETE = 'delete', '删除'
        LOGIN = 'login', '登录'
        LOGOUT = 'logout', '登出'

    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs',
        verbose_name='操作人'
    )
    username = models.CharField(max_length=150, verbose_name='操作人用户名', default='')
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        verbose_name='操作类型'
    )
    method = models.CharField(max_length=10, verbose_name='HTTP方法')
    path = models.CharField(max_length=500, verbose_name='请求路径')
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='客户端IP')
    module = models.CharField(max_length=50, verbose_name='操作模块', default='')
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='关联项目'
    )
    request_body = models.TextField(blank=True, default='', verbose_name='请求体')
    response_body = models.TextField(blank=True, default='', verbose_name='响应体')
    before_data = models.TextField(blank=True, default='', verbose_name='操作前数据')
    after_data = models.TextField(blank=True, default='', verbose_name='操作后数据')
    status_code = models.IntegerField(default=200, verbose_name='响应状态码')
    description = models.CharField(max_length=500, blank=True, default='', verbose_name='操作描述')
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='模型类型'
    )
    object_id = models.CharField(max_length=50, blank=True, default='', verbose_name='对象ID')

    class Meta:
        db_table = 'tb_audit_log'
        verbose_name = '审计日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.username} - {self.get_action_display()} - {self.path}'
