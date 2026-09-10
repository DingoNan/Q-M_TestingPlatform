from django.db import models
from utils.base import BaseModel
from simple_history.models import HistoricalRecords


def default_case_data():
    return {'name': ['params_1'], 'value': []}


class FuncCase(BaseModel):

    class StepType(models.IntegerChoices):
        TEXT = 1, '文本描述'
        STEP = 2, '步骤描述'

    class IsAutoed(models.IntegerChoices):
        CAN = 1, '全自动化'
        HalfDone = 2, '半自动化'
        NoCan = 3, '手工测试'

    class AutoStatus(models.IntegerChoices):
        Done = 1, '已完成'
        HalfDone = 2, '进行中'
        NoDone = 3, '待开始'
        NoAuto = 4, '手工测试'

    class CaseStatus(models.IntegerChoices):
        DESIGNING = 1, '待修改'
        PENDING = 2, '待评审'
        REVIEWED = 3, '已评审'

    name = models.CharField(verbose_name='用例名称', max_length=50, unique=True, error_messages={'unique': '用例名称不能重复'})
    tag = models.ManyToManyField('Tag', help_text='标签')
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    owner = models.ForeignKey('users.User', on_delete=models.PROTECT, help_text='用例负责人')
    module = models.ForeignKey('envs.Module', on_delete=models.PROTECT)
    setup_condition = models.TextField(help_text='前置条件', null=True, blank=True)
    case_mark = models.TextField(help_text='用例备注', null=True, blank=True)
    step_type = models.IntegerField(verbose_name='步骤类型', default=StepType.STEP, choices=StepType.choices)
    step_text = models.TextField(verbose_name='文本步骤类型', null=True, blank=True)
    exp_text = models.TextField(verbose_name='期望结果', null=True, blank=True)
    step_table = models.JSONField(verbose_name='表格步骤描述', default=list)
    can_autoed = models.IntegerField(verbose_name='是否可实现自动化', default=IsAutoed.NoCan, choices=IsAutoed.choices)
    case = models.ManyToManyField('Case', help_text='关联自动化用例')
    auto_status = models.IntegerField(verbose_name='自动化状态', default=AutoStatus.NoDone, choices=AutoStatus.choices)
    case_status = models.IntegerField(verbose_name='用例状态', default=CaseStatus.PENDING, choices=CaseStatus.choices)

    history = HistoricalRecords()

    class Meta:
        db_table = 'tb_func_case'
        verbose_name = '功能用例表'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']


class Case(BaseModel):

    class CaseResult(models.IntegerChoices):
        SUCCESS = 1, '成功'
        FAIL = 2, '失败'
        ERROR = 3, '错误'
        NoRUN = 4, '未执行'

    class FunctionCaseType(models.IntegerChoices):
        API = 1, 'API Case'
        WEB_UI = 2, 'WEB_UI Case'
        APP_UI = 3, 'APP_UI Case'
        CREATE_DATA = 4, 'DATA CASE'
        Performer = 5, 'Performance Case'

    name = models.CharField(verbose_name='用例名称', max_length=50, unique=True, error_messages={'unique': '用例名称不能重复'})
    type = models.IntegerField(verbose_name='用例类型', default=FunctionCaseType.API, choices=FunctionCaseType.choices)
    tag = models.ManyToManyField('Tag', help_text='标签', blank=True)
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    module = models.ForeignKey('envs.Module', on_delete=models.PROTECT)
    params = models.JSONField(verbose_name='用例全局变量设置', default=list)
    data = models.JSONField(verbose_name='测试数据集合',  default=default_case_data, blank=True, null=True)
    step = models.ManyToManyField('Step', help_text='步骤信息', through='CaseSteps')
    recent_test_result = models.IntegerField(verbose_name='用例执行结果', default=CaseResult.NoRUN,
                                             choices=CaseResult.choices, blank=True)

    history = HistoricalRecords()

    class Meta:
        db_table = 'tb_case'
        verbose_name = '用例表'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']


class CaseSteps(BaseModel):


    class IsContinue(models.IntegerChoices):
        Stop = 0, '停止测试'
        Continue = 1, '继续执行'
        Ignore = 2, '继续执行并忽略失败'

    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    step = models.ForeignKey('Step', on_delete=models.DO_NOTHING, related_name='case_steps')
    step_index = models.IntegerField(verbose_name='所属用例的第几步')
    step_params = models.JSONField(verbose_name='步骤变量参数')
    parent_id = models.IntegerField(verbose_name='父步骤的ID', null=True, default=None)
    is_run = models.BooleanField(default=True, help_text='是否执行该步骤', verbose_name='是否执行该步骤')
    fail_is_continue = models.IntegerField(verbose_name='步骤执行失败是否继续下一步并忽略失败', default=IsContinue.Stop,
                                           choices=IsContinue.choices)

    class Meta:
        db_table = 'tb_case_steps'
        verbose_name = '用例步骤表'
        ordering = ['step_index']
        verbose_name_plural = verbose_name


class Step(BaseModel):

    class BodyType(models.IntegerChoices):
        Json = 1, 'JSON'
        Data = 2, 'Form-data'

    desc = models.CharField(verbose_name='步骤描述', max_length=100)
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    database_name = models.ForeignKey('envs.Db', on_delete=models.PROTECT, null=True, blank=True)
    step_active_tab = models.CharField(max_length=30, help_text='测试步骤默认的Tab页')
    is_check = models.BooleanField(default=False, help_text='是否校验JSON文档结构', verbose_name='是否校验JSON文档结构')
    type = models.IntegerField(verbose_name='步骤类型')
    timeout = models.IntegerField(verbose_name='步骤超时时间', default=7)
    allow_redirects = models.BooleanField(default=True, help_text='是否重定向', verbose_name='是否重定向')
    verify = models.BooleanField(default=False, help_text='是否验证SSL证书', verbose_name='是否验证SSL证书')
    com_step_type = models.IntegerField(verbose_name='共用步骤类型', default=5)
    keyword = models.CharField(verbose_name='步骤关键字', max_length=25, null=True, blank=True)
    plant = models.ForeignKey('envs.Plant', verbose_name='步骤所属平台', on_delete=models.PROTECT)
    api_service = models.ForeignKey('envs.Service', verbose_name='所属服务', on_delete=models.PROTECT, null=True, blank=True)
    api_method = models.CharField(max_length=10, verbose_name='请求方法', help_text='请求方法', null=True, blank=True)
    api_uri = models.CharField(max_length=100, verbose_name='请求uri', help_text='请求uri', null=True, blank=True)
    api_headers = models.JSONField(verbose_name='API的请求头')
    common_headers = models.BooleanField(verbose_name='是否设置为公共请求头', default=False)
    api_json_type = models.CharField(verbose_name='json请求的根模式', max_length=20, default='object')
    json_body_deal = models.CharField(verbose_name='json请求体处理', max_length=100, null=True, blank=True)
    api_json = models.JSONField(verbose_name='API的Json请求体')
    body_type = models.IntegerField(verbose_name='body类型', default=BodyType.Json, choices=BodyType.choices)
    api_json_tree = models.JSONField(verbose_name='APIJson请求体结构树')
    api_data = models.JSONField(verbose_name='API请求体')
    data_body_deal = models.CharField(verbose_name='data请求体处理', max_length=100, null=True, blank=True)
    api_response = models.JSONField(verbose_name='API响应体')
    api_response_tree = models.JSONField(verbose_name='API响应体结构树')
    api_response_type = models.CharField(verbose_name='response请求的根模式', max_length=20, default='object')
    response_body_deal = models.CharField(verbose_name='response响应体处理', max_length=100, null=True, blank=True)
    api_params = models.JSONField(verbose_name='API的查询参数')
    check_params = models.JSONField(verbose_name='断言参数')
    run_params = models.JSONField(verbose_name='执行条件参数')
    loop = models.JSONField(verbose_name='循环执行参数')
    until = models.JSONField(verbose_name='跳出循环参数')
    setup = models.TextField(verbose_name='前置python脚本', null=True, blank=True, default='')
    script = models.TextField(verbose_name='python脚本', null=True, blank=True, default='')
    teardown = models.TextField(verbose_name='后置python脚本', null=True, blank=True)
    func_params = models.JSONField(verbose_name='函数入参')

    def case_num(self):
        return CaseSteps.objects.filter(step_id=self.id, is_delete=False).values('case_id').distinct().count()

    history = HistoricalRecords()

    class Meta:
        ordering = ['-create_time']
        db_table = 'tb_step'
        verbose_name = '步骤表'
        verbose_name_plural = verbose_name


class Tag(BaseModel):
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    name = models.CharField(verbose_name='标签名称', max_length=20)

    class Meta:
        ordering = ['-create_time']
        db_table = 'tb_tag'
        verbose_name = '标签表'
        verbose_name_plural = verbose_name


class CaseRunLog(BaseModel):

    class CaseResult(models.IntegerChoices):
        SUCCESS = 1, '成功'
        FAIL = 2, '失败'
        ERROR = 3, '错误'

    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    func_case = models.ForeignKey(FuncCase, on_delete=models.CASCADE, null=True)
    plan = models.ForeignKey('suites.TestPlan', on_delete=models.DO_NOTHING, null=True)
    case_name = models.CharField(max_length=200, help_text='测试用例名称')
    env = models.ForeignKey('envs.Env',  on_delete=models.DO_NOTHING)
    report = models.ForeignKey('reports.Report', on_delete=models.DO_NOTHING, null=True)
    logs = models.JSONField(verbose_name='用例执行日志')
    result = models.IntegerField(verbose_name='用例执行结果', default=CaseResult.SUCCESS, choices=CaseResult.choices)
    time = models.FloatField(verbose_name='用例执行时间')

    class Meta:
        db_table = 'tb_case_run_log'
        verbose_name = '用例执行日志表'
        ordering = ['-create_time']
        verbose_name_plural = verbose_name
