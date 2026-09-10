from django.db import models
from utils.base import BaseModel
from apps.interfaces.models import Api
from simple_history.models import HistoricalRecords


class Env(BaseModel):
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    name = models.CharField(verbose_name='环境名称', max_length=20, unique=True, error_messages={'unique': '环境名称已存在'})
    service = models.ManyToManyField('Service', through='EnvService')
    plant = models.ManyToManyField('Plant', through='EnvPlant')
    db = models.ManyToManyField('Db', through='EnvDb')
    setup = models.TextField(verbose_name='前置python脚本', null=True, blank=True, default='')
    teardown = models.TextField(verbose_name='后置python脚本', null=True, blank=True, default='')

    history = HistoricalRecords()

    class Meta:
        db_table = 'tb_env'
        verbose_name = '环境表'
        verbose_name_plural = verbose_name

    def delete(self, *args, **kwargs):
        # 检查是否存在关联的环境变量
        if self.env_global_params.exists():
            raise models.ProtectedError("无法删除该环境，因为存在关联的环境变量", self.env_global_params.all())
        if self.env_service.exists():
            raise models.ProtectedError("无法删除该环境，因为存在关联的环境服务", self.env_service.all())
        if self.env_plant.exists():
            raise models.ProtectedError("无法删除该环境，因为存在关联的环境平台", self.env_plant.all())
        super().delete(*args, **kwargs)


class GlobalParams(BaseModel):
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    name = models.CharField(verbose_name='变量名称', max_length=50)
    value = models.TextField(verbose_name='变量值')
    remark = models.CharField(verbose_name='变量备注', max_length=200, null=True)

    class Meta:
        db_table = 'tb_global_params'
        verbose_name = '全局变量表'
        ordering = ['-create_time']
        verbose_name_plural = verbose_name


class EnvGlobalParams(BaseModel):
    env = models.ForeignKey(Env, on_delete=models.PROTECT, verbose_name='所属环境', related_name='env_global_params')
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    name = models.CharField(verbose_name='变量名称', max_length=50)
    value = models.TextField(verbose_name='变量值')
    remark = models.CharField(verbose_name='变量备注', max_length=200, null=True)

    class Meta:
        db_table = 'tb_env_params'
        verbose_name = '环境全局变量表'
        ordering = ['-create_time']
        verbose_name_plural = verbose_name


class EnvWebExecutor(BaseModel):

    class ExecutorType(models.IntegerChoices):
        StandAlone = 1, 'StandAlone'
        Hub = 2, 'Hub'
        Node = 3, 'Node'

    class ExecutorStatus(models.IntegerChoices):
        Enable = 1, '启用'
        Disable = 2, '禁用'

    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    name = models.CharField(verbose_name='执行机名称', max_length=50)
    status = models.IntegerField(verbose_name='状态', default=ExecutorStatus.Enable, choices=ExecutorStatus.choices)
    url = models.URLField(verbose_name='执行机地址')
    vnc_url = models.URLField(verbose_name='vnc地址')
    type = models.IntegerField(verbose_name='执行机类型', default=ExecutorType.StandAlone, choices=ExecutorType.choices)

    class Meta:
        db_table = 'tb_env_web_executor'
        verbose_name = 'selenium执行机'
        verbose_name_plural = verbose_name


class EnvAppExecutor(BaseModel):

    class DeviceType(models.IntegerChoices):
        Android = 1, 'Android'
        iOS = 2, 'iOS'

    class ExecutorStatus(models.IntegerChoices):
        Enable = 1, '启用'
        Disable = 2, '禁用'

    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    platform_name = models.IntegerField(default=DeviceType.Android, choices=DeviceType.choices)
    status = models.IntegerField(verbose_name='状态', default=ExecutorStatus.Enable, choices=ExecutorStatus.choices)
    platform_version = models.CharField(verbose_name='系统版本号', max_length=10)
    device_name = models.CharField(verbose_name='设备名称', max_length=50, unique=True)
    device_desc = models.CharField(verbose_name='设备描述', max_length=200)
    hub_url = models.URLField(verbose_name='hub执行地址')
    node_url = models.URLField(verbose_name='node地址')

    class Meta:
        db_table = 'tb_env_app_executor'
        verbose_name = 'app执行机'
        verbose_name_plural = verbose_name


class EnvService(BaseModel):
    env = models.ForeignKey(Env, on_delete=models.PROTECT, verbose_name='所属环境', related_name='env_service')
    service = models.ForeignKey('Service', on_delete=models.PROTECT, verbose_name='所属后端服务', related_name='env_service')
    host = models.URLField(verbose_name='服务域名配置')

    class Meta:
        db_table = 'tb_env_service'
        ordering = ['-update_time']
        verbose_name = '环境服务表'
        verbose_name_plural = verbose_name


class EnvPlant(BaseModel):

    env = models.ForeignKey(Env, on_delete=models.PROTECT, verbose_name='所属环境', related_name='env_plant')
    plant = models.ForeignKey('Plant', on_delete=models.PROTECT, verbose_name='所属前端服务', related_name='env_plant')
    host = models.URLField(verbose_name='WEB平台域名', null=True, blank=True)
    package = models.CharField(verbose_name='APP包名', max_length=50, null=True, blank=True)
    activity = models.CharField(verbose_name='app主页面入口名', max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'tb_env_plant'
        verbose_name = '环境平台表'
        verbose_name_plural = verbose_name


class Service(BaseModel):

    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True)
    name = models.CharField(verbose_name='服务名称', max_length=50)
    is_server_host = models.BooleanField(default=False, help_text='接口请求是否跟随服务', verbose_name='接口请求是否跟随服务')

    class Meta:
        db_table = 'tb_service'
        verbose_name = '后端微服务表'
        verbose_name_plural = verbose_name

    def delete(self, *args, **kwargs):
        # 检查是否存在关联的环境配置
        query = EnvService.objects.filter(is_delete=False, service=self.id)
        if query.exists():
            raise models.ProtectedError("无法删除该服务，因为该服务已配置关联环境", query)
        query = ServiceModule.objects.filter(is_delete=False, service=self.id)
        if query.exists():
            raise models.ProtectedError("无法删除该服务，因为该服务已配置子模块", query)
        super().delete(*args, **kwargs)


class Headers(BaseModel):
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True)
    env = models.ForeignKey(Env, on_delete=models.PROTECT, verbose_name='所属环境')
    plant = models.ForeignKey('envs.Plant', verbose_name='所属平台的', on_delete=models.PROTECT)
    is_all_run = models.BooleanField(default=False, verbose_name='是否批跑的headers')
    name = models.CharField(verbose_name='请求体配置名称', max_length=50)
    value = models.JSONField(verbose_name='请求头值')

    class Meta:
        db_table = 'tb_headers'
        verbose_name = '后端请求头配置'
        ordering = ['-create_time']
        verbose_name_plural = verbose_name


class Cookies(BaseModel):
    class CookieType(models.IntegerChoices):
        Cookie = 1, 'Cookie'
        Session = 2, 'Session'
        LocalStorage = 3, 'LocalStorage'
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True)
    plant = models.ForeignKey('envs.Plant', verbose_name='所属平台的', on_delete=models.PROTECT)
    env = models.ForeignKey(Env, on_delete=models.PROTECT, verbose_name='所属环境')
    type = models.IntegerField(verbose_name='类型', default=CookieType.Cookie, choices=CookieType.choices)
    is_all_run = models.BooleanField(default=False, verbose_name='是否批跑的Cookie')
    name = models.CharField(verbose_name='cookies名称', max_length=50)
    value = models.JSONField(verbose_name='cookies名称值')

    class Meta:
        db_table = 'tb_cookies'
        verbose_name = '后端cookies配置'
        ordering = ['-create_time']
        verbose_name_plural = verbose_name


class Plant(BaseModel):
    class PlantType(models.IntegerChoices):
        WEB = 1, 'WEB'
        PHONE_APP = 2, 'PHONE_APP'
        H5 = 3, 'H5'
        MINI = 4, 'MINI'
        DESKTOP_APP = 5, 'DESKTOP_APP'

    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True)
    name = models.CharField(verbose_name='平台名称', max_length=20)
    type = models.IntegerField(verbose_name='平台类型', default=PlantType.WEB, choices=PlantType.choices)

    class Meta:
        db_table = 'tb_plant'
        verbose_name = '平台表'
        verbose_name_plural = verbose_name

    def delete(self, *args, **kwargs):
        # 检查是否存在关联的环境变量
        query = EnvPlant.objects.filter(is_delete=False, plant=self.id)
        if query.exists():
            raise models.ProtectedError("无法删除该产品，因为该产品已配置关联环境", query)
        query = Module.objects.filter(is_delete=False, plant=self.id)
        if query.exists():
            raise models.ProtectedError("无法删除该产品，因为该产品已配置子模块", query)
        super().delete(*args, **kwargs)


class Module(BaseModel):
    name = models.CharField(verbose_name='模块名称', max_length=20)
    url = models.CharField(verbose_name='页面地址', max_length=200, null=True, blank=True, default='')
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    plant = models.ForeignKey(Plant, on_delete=models.PROTECT)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'tb_module'
        verbose_name = '模块表'
        verbose_name_plural = verbose_name


class ServiceModule(BaseModel):
    name = models.CharField(verbose_name='服务模块名称', max_length=20)
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'tb_service_module'
        verbose_name = '服务模块表'
        verbose_name_plural = verbose_name


class Page(BaseModel):
    name = models.CharField(verbose_name='页面名称', max_length=20)
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    url = models.CharField(verbose_name='页面地址或Activity', max_length=100)
    module = models.ForeignKey(Module, on_delete=models.PROTECT)

    class Meta:
        db_table = 'tb_page'
        verbose_name = '模块表'
        verbose_name_plural = verbose_name


class EnvDb(BaseModel):

    class SQLType(models.IntegerChoices):
        MYSQL = 1, 'MySQL'
        POSTGRESQL = 2, 'PostgreSQL'
        REDIS = 3, 'REDIS'
    env = models.ForeignKey(Env, on_delete=models.CASCADE, verbose_name='所属环境')
    db = models.ForeignKey('Db', on_delete=models.CASCADE, verbose_name='所属数据库')
    host = models.CharField(verbose_name='数据库地址', max_length=100)
    username = models.CharField(verbose_name='数据库用户名', max_length=20)
    password = models.CharField(verbose_name='数据库密码', max_length=20)
    port = models.IntegerField(verbose_name='数据库端口号')
    name = models.CharField(verbose_name='连接的数据库名', max_length=20)
    type = models.IntegerField(verbose_name='数据库类型', choices=SQLType.choices, default=SQLType.MYSQL)

    class Meta:
        db_table = 'tb_env_db'
        verbose_name = '数据库环境表'
        verbose_name_plural = verbose_name


class Db(BaseModel):
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True)
    name = models.CharField(verbose_name='数据库名称', max_length=50)

    class Meta:
        db_table = 'tb_db'
        verbose_name = '数据库表'
        verbose_name_plural = verbose_name

    def delete(self, *args, **kwargs):
        # 检查是否存在关联的环境变量
        query = EnvDb.objects.filter(is_delete=False, db=self.id)
        if query.exists():
            raise models.ProtectedError("无法删除该数据库，因为该数据库已配置关联环境", query)
        super().delete(*args, **kwargs)
