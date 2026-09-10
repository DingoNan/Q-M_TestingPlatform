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

    class Meta:
        ordering = ['-create_time']
        db_table = 'tb_locust_report'
        verbose_name = '性能测试报告'
        verbose_name_plural = verbose_name