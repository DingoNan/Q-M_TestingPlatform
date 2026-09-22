from django.db import models
from utils.base import BaseModel
from simple_history.models import HistoricalRecords


class Api(BaseModel):

    class BodyType(models.IntegerChoices):
        Json = 1, 'JSON'
        Data = 2, 'Form-data'

    # 已发布 设计中 待确定 开发 对接 测试 完成 异常 维护 废弃
    class ApiStatus(models.IntegerChoices):
        StatusOne = 1, '已发布'
        StatusTwo = 2, '设计中'
        StatusThree = 3, '待确定'
        StatusFour = 4, '开发'
        StatusFive = 5, '对接'
        StatusSix = 6, '测试'
        StatusSeven = 7, '完成'
        StatusEight = 8, '异常'
        StatusNine = 9, '维护'
        StatusTen = 10, '废弃'

    status = models.IntegerField(verbose_name='接口状态', default=ApiStatus.StatusOne, choices=ApiStatus.choices)
    service = models.ForeignKey('envs.Service', verbose_name='所属服务', on_delete=models.PROTECT)
    module = models.ForeignKey('envs.ServiceModule', on_delete=models.PROTECT)
    name = models.CharField(verbose_name='接口名称', max_length=50)
    url = models.CharField(verbose_name='请求地址', max_length=200)
    method = models.CharField(verbose_name='请求方法', max_length=10)
    headers = models.JSONField(verbose_name='请求头')
    body_type = models.IntegerField(verbose_name='body类型', default=BodyType.Json, choices=BodyType.choices)
    json = models.JSONField(verbose_name='json/application')
    api_json_type = models.CharField(verbose_name='json根类型', default='object', max_length=15)
    api_response_type = models.CharField(verbose_name='response根类型', default='object', max_length=15)
    data = models.JSONField(verbose_name='form-data')
    params = models.JSONField(verbose_name='查询参数')
    response = models.JSONField(verbose_name='数据返回体')
    response_tree = models.JSONField(verbose_name='数据返回体', default=list)

    history = HistoricalRecords()

    class Meta:
        db_table = 'tb_api'
        verbose_name = '接口表'
        verbose_name_plural = verbose_name
        # ★ 2026-09-22：补稳定二级排序键。
        #   update_time 是 auto_now，同一批导入的接口常常落在同一秒，
        #   只按 -update_time 排序时同秒内的相对顺序不确定（取决于数据库物理顺序），
        #   表现为「导入后列表顺序时对时错」。加上 -id 后顺序稳定，
        #   并与 _parse_har_v2 的「逆序落库」配合，还原 HAR 里的真实发起顺序。
        ordering = ['-update_time', '-id']


class ApiMock(BaseModel):

    class BodyType(models.IntegerChoices):
        Json = 1, 'JSON'
        Data = 2, 'Form-data'

    class ResBodyType(models.IntegerChoices):
        Json = 1, 'JSON'
        Doc = 2, '跟随API文档'

    api = models.ForeignKey(Api, verbose_name='所属接口', on_delete=models.PROTECT)
    name = models.CharField(verbose_name='mock名称', max_length=50)
    desc = models.CharField(verbose_name='mock描述', max_length=200)
    is_enable = models.BooleanField(default=False, help_text='是否启用', verbose_name='是否启用')
    headers = models.JSONField(verbose_name='请求头')
    json = models.JSONField(verbose_name='json/application', default=list)
    status_code = models.IntegerField(verbose_name='mock响应状态码', default=200)
    timeout = models.IntegerField(verbose_name='mock延长响应时间', default=0)
    json_tree = models.JSONField(verbose_name='json_tree', default=list)
    body_type = models.IntegerField(verbose_name='body类型', default=BodyType.Json, choices=BodyType.choices)
    response_type = models.IntegerField(verbose_name='resbody类型', default=ResBodyType.Doc, choices=ResBodyType.choices)
    api_json_type = models.CharField(verbose_name='json根类型', default='object', max_length=15)
    api_response_type = models.CharField(verbose_name='response根类型', default='object', max_length=15)
    data = models.JSONField(verbose_name='form-data')
    params = models.JSONField(verbose_name='查询参数')
    response = models.JSONField(verbose_name='数据返回体', default=list)
    response_headers = models.JSONField(verbose_name='请求头', default=list)
    response_tree = models.JSONField(verbose_name='数据返回体', default=list)

    class Meta:
        db_table = 'tb_api_mock'
        verbose_name = '接口Mock表'
        verbose_name_plural = verbose_name
        # ★ 2026-09-22：补稳定二级排序键。
        #   update_time 是 auto_now，同一批导入的接口常常落在同一秒，
        #   只按 -update_time 排序时同秒内的相对顺序不确定（取决于数据库物理顺序），
        #   表现为「导入后列表顺序时对时错」。加上 -id 后顺序稳定，
        #   并与 _parse_har_v2 的「逆序落库」配合，还原 HAR 里的真实发起顺序。
        ordering = ['-update_time', '-id']