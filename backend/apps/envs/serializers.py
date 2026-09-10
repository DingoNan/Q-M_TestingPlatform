from utils.base import BaseSerializer
from apps.envs.models import (
    Env,
    EnvGlobalParams,
    GlobalParams,
    Service,
    Plant,
    EnvPlant,
    EnvDb,
    Db,
    EnvService,
    Module,
    ServiceModule,
    Page,
    Headers,
    Cookies,
    EnvWebExecutor,
    EnvAppExecutor
)

from rest_framework import serializers


class EnvSerializers(BaseSerializer):

    class Meta:
        model = Env
        fields = '__all__'


class EnvGlobalParamsSerializers(BaseSerializer):
    env_name = serializers.CharField(source='env.name', read_only=True)

    class Meta:
        model = EnvGlobalParams
        fields = '__all__'


class GlobalParamsSerializers(BaseSerializer):

    class Meta:
        model = GlobalParams
        fields = '__all__'


class EnvWebExecutorSerializers(BaseSerializer):
    type = serializers.IntegerField(error_messages={'required': '请选择执行机类型'})
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    name = serializers.CharField(error_messages={'required': '请输入执行机名称'})
    url = serializers.CharField(error_messages={'required': '请输入执行机地址'})
    vnc_url = serializers.CharField(error_messages={'required': '请输入执行机VNC地址'})

    class Meta:
        model = EnvWebExecutor
        fields = '__all__'


class EnvAppExecutorSerializers(BaseSerializer):
    status_name = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = EnvAppExecutor
        fields = '__all__'


class ServiceSerializers(BaseSerializer):

    class Meta:
        model = Service
        fields = '__all__'


class DbSerializers(BaseSerializer):

    class Meta:
        model = Db
        fields = '__all__'


class HeadersSerializers(BaseSerializer):
    plant_name = serializers.CharField(source='plant.name', read_only=True)
    is_all_run_tag = serializers.SerializerMethodField(read_only=True)
    env_name = serializers.CharField(source='env.name', read_only=True)

    class Meta:
        model = Headers
        fields = ['name', 'plant_name', 'id', 'create_time', 'update_time', 'create_by_name', 'update_by_name',
                  'value', 'plant', 'project', 'is_all_run', 'is_all_run_tag', 'env_name', 'env']

    def get_is_all_run_tag(self, obj):
        return '是' if obj.is_all_run else '否'

    def validate(self, attrs):
        plant = attrs.get('plant')
        is_all_run = attrs.get('is_all_run')
        env = attrs.get('env')
        user_id = self.context['request'].user.id
        # 新增
        header_set = Headers.objects.filter(plant=plant, is_delete=False, is_all_run=is_all_run, env=env)
        if not self.instance:
            if is_all_run and header_set.exists():
                raise serializers.ValidationError("同一平台,同一环境下只能存在一个批跑Headers")
            elif not is_all_run and header_set.filter(create_by=user_id).exists():
                raise serializers.ValidationError("同一用户,同一平台,同一环境下只能存在一个非批跑Headers")
        return attrs


class CookiesSerializers(BaseSerializer):
    plant_name = serializers.CharField(source='plant.name', read_only=True)
    type_name = serializers.CharField(source='get_type_display', read_only=True)
    is_all_run_tag = serializers.SerializerMethodField(read_only=True)
    env_name = serializers.CharField(source='env.name', read_only=True)

    class Meta:
        model = Cookies
        fields = ['name', 'plant_name', 'id', 'create_time', 'update_time', 'create_by_name', 'update_by_name',
                  'value', 'plant', 'project', 'type_name', 'type', 'is_all_run', 'is_all_run_tag',
                  'env_name', 'env']

    def get_is_all_run_tag(self, obj):
        return '是' if obj.is_all_run else '否'

    def validate(self, attrs):
        plant = attrs.get('plant')
        is_all_run = attrs.get('is_all_run')
        env = attrs.get('env')
        user_id = self.context['request'].user.id
        # 新增
        if not self.instance:
            if is_all_run and Cookies.objects.filter(plant=plant, is_delete=False, is_all_run=is_all_run, env=env).exists():
                raise serializers.ValidationError("同一平台,同一环境下只能存在一个批跑Cookies")
            elif not is_all_run and Cookies.objects.filter(plant=plant, is_delete=False, is_all_run=is_all_run,
                                                           create_by=user_id, env=env).exists():
                raise serializers.ValidationError("同一用户,同一平台,同一环境下只能存在一个非批跑")
        return attrs


class EnvNameServiceSerializers(BaseSerializer):
    env_name = serializers.CharField(source='env.name', read_only=True)

    class Meta:
        model = EnvService
        fields = ['env_name',  'host', 'env']


class EnvNamePlantSerializers(BaseSerializer):
    env_name = serializers.CharField(source='env.name', read_only=True)

    class Meta:
        model = EnvPlant
        fields = ['env_name',  'host', 'env']


class EnvServiceSerializers(BaseSerializer):
    env_name = serializers.CharField(source='env.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = EnvService
        fields = ['env_name', 'service_name', 'id', 'create_time', 'update_time', 'create_by_name', 'update_by_name',
                  'env', 'service', 'host']

    def validate(self, attrs):
        service = attrs.get('service')
        env = attrs.get('env')
        # 新增
        env_service_set = EnvService.objects.filter(service=service, is_delete=False, env=env)
        if not self.instance:
            if env_service_set.exists():
                raise serializers.ValidationError("同一环境下同一服务下只能有一个接口域名规则")
        # 编辑
        else:
            if env_service_set.exists() and env_service_set[0].id != self.instance.id:
                raise serializers.ValidationError("同一环境下同一服务下只能有一个接口域名规则")
        return attrs


class EnvDbSerializers(BaseSerializer):
    env_name = serializers.CharField(source='env.name', read_only=True)
    db_name = serializers.CharField(source='db.name', read_only=True)
    type_name = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = EnvDb
        fields = '__all__'

    def validate(self, attrs):
        db = attrs.get('db')
        env = attrs.get('env')
        # 新增
        env_db_set = EnvDb.objects.filter(db=db, is_delete=False, env=env)
        if not self.instance:
            if env_db_set.exists():
                raise serializers.ValidationError("同一环境同一数据库下只能有一个配置")
        # 编辑
        else:
            if env_db_set.exists() and env_db_set[0].id != self.instance.id:
                raise serializers.ValidationError("同一环境同一数据库下只能有一个配置")
        return attrs


class PlantSerializers(BaseSerializer):
    type_name = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Plant
        fields = '__all__'


class EnvPlantSerializers(BaseSerializer):
    env_name = serializers.CharField(source='env.name', read_only=True)
    plant_name = serializers.CharField(source='plant.name', read_only=True)
    type = serializers.IntegerField(source='plant.type', read_only=True)
    type_name = serializers.SerializerMethodField(read_only=True)

    def get_type_name(self, obj):
        # 使用 get_type_display() 获取枚举的显示文本
        if obj.plant and hasattr(obj.plant, 'get_type_display'):
            return obj.plant.get_type_display()
        return None

    class Meta:
        model = EnvPlant
        fields = ['env_name', 'plant_name', 'id', 'create_time', 'update_time', 'create_by_name', 'update_by_name',
                  'env', 'plant', 'host', 'activity', 'type_name', 'package', 'type']

    def validate(self, attrs):
        plant = attrs.get('plant')
        env = attrs.get('env')
        # 新增
        env_plant_set = EnvPlant.objects.filter(plant=plant, is_delete=False, env=env)
        if not self.instance:
            if env_plant_set.exists():
                raise serializers.ValidationError("同一产品同一环境只能配置一次")
        return attrs


class ModuleSerializers(BaseSerializer):

    plant_name = serializers.CharField(source='plant.name', read_only=True)

    class Meta:
        model = Module
        fields = '__all__'


class ServiceModuleSerializers(BaseSerializer):

    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = ServiceModule
        fields = '__all__'


class PageSerializers(BaseSerializer):

    module_name = serializers.CharField(source='module.name', read_only=True)
    plant_name = serializers.CharField(source='module.plant.name', read_only=True)

    class Meta:
        model = Page
        fields = '__all__'
