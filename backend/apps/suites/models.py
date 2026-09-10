from django.db import models
from django_q.models import Schedule

from utils.base import BaseModel
from simple_history.models import HistoricalRecords


class Suite(BaseModel):
    class AutoType(models.IntegerChoices):
        API = 1, 'API'
        WEB_UI = 2, "WEB_UI"
        APP_UI = 3, 'APP_UI'

    class PlanType(models.IntegerChoices):
        FUNCTION = 1, '功能用例'
        AUTO = 2, "脚本用例"

    class PlanModel(models.IntegerChoices):
        STATIC = 1, '静态模式'
        Dynamic = 2, "动态模式"

    plant_type = models.IntegerField(verbose_name='计划类型', default=PlanType.AUTO, choices=PlanType.choices)
    plant_model = models.IntegerField(verbose_name='计划模式', default=PlanModel.Dynamic, choices=PlanModel.choices)
    auto_type = models.IntegerField(verbose_name='脚本用例类型', default=AutoType.API, choices=AutoType.choices)
    name = models.CharField(verbose_name='计划名称', max_length=50)
    desc = models.CharField(verbose_name='计划描述', max_length=200)
    rerun_times = models.IntegerField(verbose_name='脚本用例失败重试次数', default=0)
    web_executor = models.ForeignKey('envs.EnvWebExecutor', verbose_name='所属web执行器节点', on_delete=models.DO_NOTHING,
                                     null=True, blank=True, default=None)
    app_executor = models.ForeignKey('envs.EnvAppExecutor', verbose_name='所属app执行器节点', on_delete=models.DO_NOTHING,
                                     null=True, blank=True, default=None)
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    push_msg = models.BooleanField(default=True, verbose_name='用例执行完是否推送消息', help_text='用例执行完是否推送消息')
    dynamic_conditions = models.JSONField(verbose_name='动态模式筛选用例条件')
    auto_cases = models.ManyToManyField('tests.Case', help_text='关联自动化用例')
    func_cases = models.ManyToManyField('tests.FuncCase', help_text='关联功能用例')
    start_end_time = models.JSONField(verbose_name='计划起止时间', help_text='计划起止时间')

    history = HistoricalRecords()

    class Meta:
        ordering = ['-create_time']
        db_table = 'tb_suite'
        verbose_name = '计划表'
        verbose_name_plural = verbose_name


class TestPlan(BaseModel):
    """
    测试计划表
    用于管理功能用例测试计划，包含用例执行状态和执行人信息
    """
    name = models.CharField(
        max_length=100,
        verbose_name='计划名称',
        help_text='测试计划的名称'
    )

    start_end_time = models.JSONField(verbose_name='计划起止时间', help_text='计划起止时间')

    conclusion = models.TextField(
        verbose_name='测试结论',
        help_text='测试计划的总结结论',
        blank=True,
        default=''
    )

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='test_plans',
        verbose_name='所属项目',
        help_text='测试计划所属的项目'
    )

    desc = models.TextField(
        verbose_name='计划描述',
        help_text='测试计划的详细描述',
        blank=True,
        default=''
    )

    func_cases = models.ManyToManyField(
        'tests.FuncCase',
        through='TestPlanFuncCase',
        related_name='test_plans',
        help_text='关联的功能用例'
    )

    history = HistoricalRecords()

    class Meta:
        db_table = 'tb_test_plan'
        verbose_name = '测试计划'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.name


class TestPlanFuncCase(BaseModel):
    """
    测试计划与功能用例关联表
    存储每个测试计划中功能用例的执行状态、执行人等信息
    """
    class ExecStatus(models.IntegerChoices):
        NOT_EXECUTED = 1, '未执行'
        POSTPONED = 2, '暂缓'
        PASSED = 3, '已通过'
        FAILED = 4, '未通过'
        TESTING = 5, '进行中'

    test_plan = models.ForeignKey(
        TestPlan,
        on_delete=models.CASCADE,
        related_name='test_plan_func_cases',
        verbose_name='所属测试计划'
    )

    func_case = models.ForeignKey(
        'tests.FuncCase',
        on_delete=models.CASCADE,
        related_name='test_plan_func_cases',
        verbose_name='功能用例'
    )

    added_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='added_test_plan_cases',
        verbose_name='添加用例的人',
        null=True,
        blank=True
    )

    executed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='executed_test_plan_cases',
        verbose_name='执行用例的人',
        null=True,
        blank=True
    )

    exec_status = models.IntegerField(
        verbose_name='执行状态',
        choices=ExecStatus.choices,
        default=ExecStatus.NOT_EXECUTED,
        help_text='用例在该测试计划中的执行状态'
    )

    executed_time = models.DateTimeField(
        verbose_name='执行时间',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'tb_test_plan_func_case'
        verbose_name = '测试计划功能用例'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.test_plan.name} - {self.func_case.name}"


class TestPlanFuncCaseComment(BaseModel):
    """
    测试计划功能用例评论表
    存储每条用例执行过程中的多条动态评论
    """
    test_plan_func_case = models.ForeignKey(
        TestPlanFuncCase,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='所属测试计划用例'
    )

    content = models.TextField(
        verbose_name='评论内容',
        help_text='评论或备注内容'
    )

    comment_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='test_plan_comments',
        verbose_name='评论人',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'tb_test_plan_func_case_comment'
        verbose_name = '测试计划用例评论'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return f"{self.test_plan_func_case} - {self.content[:20]}"


class CrontabTask(BaseModel):
    """
    定时任务模型
    """
    class ScheduleType(models.IntegerChoices):
        ONCE = 0, '只执行一次'
        MINUTES = 1, '分钟'
        HOURLY = 2, '小时'
        DAILY = 3, '每天'
        WEEKLY = 4, '每周'
        MONTHLY = 5, '每月'
        CRON = 6, '自定义Cron'

    project = models.ForeignKey('projects.Project', verbose_name='所属项目', on_delete=models.CASCADE)
    desc = models.TextField(verbose_name='定时任务描述', null=True, blank=True)
    suite = models.ForeignKey(Suite, verbose_name='套件名称', on_delete=models.CASCADE)
    env = models.ForeignKey('envs.Env', verbose_name='环境名称', on_delete=models.PROTECT)
    crontab = models.CharField('定时策略', max_length=256)
    enabled = models.BooleanField(default=True, verbose_name='启用', help_text='是否启用')
    schedule = models.OneToOneField(Schedule, on_delete=models.SET_NULL, null=True, blank=True)
    # is_async = models.BooleanField(default=False, help_text='是否并发执行', verbose_name='是否并发执行')
    # count = models.IntegerField(verbose_name='并发数', default=1)

    class Meta:
        db_table = 'tb_crontab_task'
        verbose_name = '定时任务'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']
