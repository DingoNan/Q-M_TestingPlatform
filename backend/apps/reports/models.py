from django.db import models

from utils.base import BaseModel


class Report(BaseModel):

    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    name = models.CharField(verbose_name='报告名称', max_length=200)
    suite = models.ForeignKey('suites.Suite', on_delete=models.DO_NOTHING, null=True)
    api = models.ForeignKey('interfaces.Api', on_delete=models.DO_NOTHING, null=True)
    plan = models.ForeignKey('suites.TestPlan', on_delete=models.DO_NOTHING, null=True)
    env = models.ForeignKey('envs.Env', on_delete=models.PROTECT)
    all_case_number = models.IntegerField(verbose_name='总用例数', default=0)
    success_case_number = models.IntegerField(verbose_name='成功用例数', default=0)
    error_case_number = models.IntegerField(verbose_name='错误用例数', default=0)
    fail_case_number = models.IntegerField(verbose_name='失败用例数', default=0)
    detail = models.JSONField(default=dict)

    class Meta:
        ordering = ['-create_time']
        db_table = 'tb_report'
        verbose_name = '报告表'
        verbose_name_plural = verbose_name


class LocustReport(BaseModel):

    class TestProcess(models.IntegerChoices):
        Done = 1, '已完成'
        Doing = 2, '压测中'
        # 失败：用于「压测子进程异常退出 / 超时未收口」等被守护进程判定为中断的场景。
        # 刻意区别于 Done —— 这类报告没有任何统计数据，标成「已完成」会误导用户。
        # 前端 getStatusType 已内置 '失败' → danger 的映射，无需额外改动即可正确渲染。
        Failed = 3, '失败'

    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    env = models.ForeignKey('envs.Env', on_delete=models.PROTECT)
    case = models.ForeignKey('tests.Case', on_delete=models.PROTECT)
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    test_process = models.IntegerField(help_text='压测并发用户数', default=TestProcess.Doing, choices=TestProcess.choices)
    max_user = models.IntegerField(help_text='压测并发用户数')
    rate = models.IntegerField(help_text='每秒启动用户数')
    cpu = models.FloatField(help_text='cpu使用率')
    memory = models.FloatField(help_text='内存使用M')
    duration = models.CharField(verbose_name='持续时间', max_length=50)
    requests_statistics = models.JSONField(default=list)
    failures_statistics = models.JSONField(default=list)
    start_time = models.DateTimeField(help_text='开始时间', verbose_name='开始时间')
    end_time = models.DateTimeField(help_text='结束时间', verbose_name='结束时间')
    exceptions_statistics = models.JSONField(default=list)
    response_time_statistics = models.JSONField(default=list)
    history = models.JSONField(default=list)
    # 失败原因（面向用户的一句话结论）。
    # 与 exceptions_statistics 的分工：
    #   * fail_reason          ——「为什么会失败」的结论式说明，由守护进程、压测执行进程、
    #                             视图在收口时写入，前端以独立卡片突出展示；
    #   * exceptions_statistics —— 原始异常明细（含 traceback），用于问题溯源。
    # 旧实现把「守护进程的中断判定结论」塞进 exceptions_statistics，语义偏了
    # （那是判定结论、不是异常），故独立成字段，两者不再混用。
    fail_reason = models.TextField(verbose_name='失败原因', blank=True, default='')

    class Meta:
        ordering = ['-create_time']
        db_table = 'tb_locust_report'
        verbose_name = '性能测试报告'
        verbose_name_plural = verbose_name