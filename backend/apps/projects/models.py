from django.db import models

from utils.base import BaseModel
from simple_history.models import HistoricalRecords


class Project(BaseModel):

    name = models.CharField(max_length=50, help_text='项目名称')
    desc = models.CharField(max_length=200, help_text='项目描述', verbose_name='项目描述')

    history = HistoricalRecords()

    class Meta:
        db_table = 'tb_project'
        verbose_name = '项目表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ProjectMember(BaseModel):
    """
    项目成员表
    管理项目成员及其在项目中的角色
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='project_memberships')
    role = models.ForeignKey('users.Role', on_delete=models.DO_NOTHING, help_text='项目内角色')

    class Meta:
        db_table = 'tb_project_member'
        verbose_name = '项目成员表'
        verbose_name_plural = verbose_name
        # 确保一个用户在一个项目中只有一个未删除的成员记录
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'user'],
                condition=models.Q(is_delete=False),
                name='unique_active_project_member'
            )
        ]

    def __str__(self):
        return f"{self.project.name} - {self.user.username} - {self.role.name}"


class ProjectAppeal(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    status = models.BooleanField(verbose_name='审核状态', default=False)

    class Meta:
        db_table = 'tb_project_appeal'
        verbose_name = '项目成员申请表'
        unique_together = [['project', 'user']]  # 确保一个用户在一个项目中只有一个申请


class AiConfig(BaseModel):
    """
    AI 大模型接入配置表
    用于存储项目下各个 AI 供应商的 API 配置信息
    """
    # 关联项目（必填）
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='ai_configs',      # 便于反向查询：project.ai_configs.all()
        verbose_name='所属项目',
        help_text='配置所属的项目'
    )

    # 供应商显示名称（如 'DeepSeek', '腾讯混元'）
    provider_name = models.CharField(
        max_length=100,
        verbose_name='供应商名称',
        help_text='前端显示的供应商名称'
    )

    # API 密钥（敏感信息，建议加密存储，此处仅做基本设计）
    api_key = models.CharField(
        max_length=512,                   # 根据实际密钥长度调整
        verbose_name='API Key',
        help_text='调用 API 所需的密钥'
    )

    # API 地址
    api_url = models.URLField(
        max_length=500,
        verbose_name='API URL',
        help_text='API 的请求地址'
    )

    # 模型名称
    model_name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='模型名称',
        help_text='使用的具体模型，如 deepseek-chat'
    )

    # 启用状态（可用于控制配置是否生效）
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='勾选表示该配置可用，否则不可用'
    )

    # 默认配置（同项目下仅一个）
    is_default = models.BooleanField(
        default=False,
        verbose_name='是否默认',
        help_text='设为默认后，同项目下其他配置自动取消默认'
    )

    class Meta:
        db_table = 'tb_project_ai_config'           # 保持与原有代码一致
        verbose_name = 'AI大模型接入配置'
        verbose_name_plural = verbose_name
        # 联合唯一约束：同一个项目下，不允许相同的供应商+模型重复配置（可根据业务需求调整）
        unique_together = [['project', 'provider_name', 'model_name']]
        # 索引优化
        indexes = [
            models.Index(fields=['project', 'is_active']),
        ]

    def __str__(self):
        return f"{self.project.name} - {self.provider_name} - {self.model_name}"


class ProjectMsgPush(BaseModel):
    """
    项目消息推送配置表
    用于存储项目的消息推送配置（飞书、钉钉、邮箱）
    """
    class PushType(models.IntegerChoices):
        FeiShu = 1, '飞书'
        DingDing = 2, '钉钉'
        Email = 3, '邮箱'

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='msg_push_configs',
        verbose_name='所属项目',
        help_text='配置所属的项目'
    )

    push_type = models.IntegerField(
        verbose_name='推送类型',
        choices=PushType.choices,
        help_text='推送渠道类型'
    )

    webhook_url = models.CharField(
        max_length=500,
        verbose_name='Webhook地址',
        help_text='飞书或钉钉的Webhook地址',
        blank=True,
        default=''
    )

    email_host = models.CharField(
        max_length=100,
        verbose_name='邮箱SMTP主机',
        help_text='SMTP服务器地址',
        blank=True,
        default=''
    )

    email_port = models.IntegerField(
        verbose_name='邮箱SMTP端口',
        help_text='SMTP服务器端口',
        default=25
    )

    email_user = models.CharField(
        max_length=100,
        verbose_name='邮箱账号',
        help_text='发送邮件的邮箱账号',
        blank=True,
        default=''
    )

    email_password = models.CharField(
        max_length=200,
        verbose_name='邮箱密码或授权码',
        help_text='邮箱密码或授权码（钉钉/飞书用作签名密钥，邮箱用作SMTP认证）',
        blank=True,
        default=''
    )

    email_to = models.CharField(
        max_length=500,
        verbose_name='收件人邮箱',
        help_text='接收消息的邮箱地址，多个邮箱用逗号分隔',
        blank=True,
        default=''
    )

    is_active = models.BooleanField(
        verbose_name='是否启用',
        help_text='勾选表示该配置可用，否则不可用',
        default=True
    )

    class Meta:
        db_table = 'tb_project_msg_push'
        verbose_name = '项目消息推送配置'
        verbose_name_plural = verbose_name
        unique_together = [['project', 'push_type']]

    def __str__(self):
        push_type_name = self.get_push_type_display()
        return f"{self.project.name} - {push_type_name}"


class ProjectGeneralSetting(BaseModel):
    """
    项目通用设置表
    存储项目级通用配置项（如回放文件清理保留天数）
    """
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='general_setting',
        verbose_name='所属项目',
        help_text='配置所属的项目'
    )

    trace_retention_days = models.IntegerField(
        verbose_name='回放文件保留天数',
        help_text='Trace/视频回放文件保留天数，超期后由定时任务自动清理',
        default=30
    )

    class Meta:
        db_table = 'tb_project_general_setting'
        verbose_name = '项目通用设置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.project.name} - 通用设置"
