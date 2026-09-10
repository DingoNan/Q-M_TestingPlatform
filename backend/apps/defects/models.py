from django.db import models
from utils.base import BaseModel


class Defect(BaseModel):
    class Severity(models.IntegerChoices):
        CRITICAL = 1, '致命'
        SEVERE = 2, '严重'
        NORMAL = 3, '一般'
        MINOR = 4, '轻微'

    class Priority(models.IntegerChoices):
        URGENT = 1, '紧急'
        HIGH = 2, '高'
        MEDIUM = 3, '中'
        LOW = 4, '低'

    class DefectType(models.IntegerChoices):
        CODE_FRONTEND = 1, '代码问题-前端'
        CODE_BACKEND = 2, '代码问题-后端'
        BY_DESIGN = 3, '设计如此'
        DUPLICATE = 4, '重复BUG'
        REQUIREMENT_CHANGE = 5, '需求变动'
        UI_STYLE = 6, 'UI样式'
        DESIGN_FLAW = 7, '设计缺陷'

    class Status(models.IntegerChoices):
        PENDING = 1, '待处理'
        IN_PROGRESS = 2, '处理中'
        RESOLVED = 3, '已解决'
        CLOSED = 4, '已关闭'

    title = models.CharField(verbose_name='缺陷标题', max_length=500)
    description = models.TextField(verbose_name='缺陷描述', blank=True, default='')
    actual_result = models.TextField(verbose_name='实际结果', blank=True, default='')
    expected_result = models.TextField(verbose_name='预期结果', blank=True, default='')
    severity = models.IntegerField(verbose_name='严重程度', choices=Severity.choices, default=Severity.NORMAL)
    priority = models.IntegerField(verbose_name='优先级', choices=Priority.choices, default=Priority.MEDIUM)
    defect_type = models.IntegerField(verbose_name='BUG类型', choices=DefectType.choices, default=DefectType.CODE_FRONTEND)
    status = models.IntegerField(verbose_name='状态', choices=Status.choices, default=Status.PENDING)

    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    plan = models.ForeignKey('suites.TestPlan', on_delete=models.DO_NOTHING, null=True, blank=True)
    func_cases = models.ManyToManyField('tests.FuncCase', help_text='关联功能用例', blank=True)
    module = models.ForeignKey('envs.Module', on_delete=models.PROTECT, verbose_name='所属模块', null=True)
    assignee = models.ForeignKey('users.User', on_delete=models.PROTECT, verbose_name='处理人', related_name='defect_assignee', null=True)
    owner = models.ForeignKey('users.User', on_delete=models.PROTECT, verbose_name='负责人', related_name='defect_owner', null=True, blank=True)
    attachments = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-create_time']
        db_table = 'tb_defect'
        verbose_name = '缺陷表'
        verbose_name_plural = verbose_name


class DefectComment(BaseModel):
    defect = models.ForeignKey(
        Defect,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='所属缺陷'
    )
    content = models.TextField(verbose_name='评论内容')
    comment_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='defect_comments',
        verbose_name='评论人',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'tb_defect_comment'
        verbose_name = '缺陷评论'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']
