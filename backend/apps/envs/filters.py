from django_filters import rest_framework

from apps.envs.models import (
    Env,
    Service,
    Db,
    EnvDb,
    EnvService,
    Plant,
    EnvPlant,
    Module,
    ServiceModule,
    Page,
    Headers,
    Cookies,
    EnvGlobalParams,
    GlobalParams,
    EnvWebExecutor,
    EnvAppExecutor
)


class EnvFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = Env
        fields = '__all__'


class EnvWebExecutorFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    type = rest_framework.BaseInFilter(lookup_expr='in')

    class Meta:
        model = EnvWebExecutor
        fields = '__all__'


class EnvAppExecutorFilter(rest_framework.FilterSet):
    device_name = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = EnvAppExecutor
        fields = '__all__'

class GlobalParamsFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    remark = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = GlobalParams
        fields = '__all__'

class EnvGlobalParamsFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    remark = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = EnvGlobalParams
        fields = '__all__'


class ServiceFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = Service
        fields = '__all__'


class DbFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = Db
        fields = '__all__'


class HeadersFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = Headers
        fields = ['plant', 'project', 'create_by', 'update_by', 'is_all_run', 'env']


class CookiesFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = Cookies
        fields = ['plant', 'project', 'create_by', 'update_by', 'is_all_run', 'env']


class EnvServiceFilter(rest_framework.FilterSet):
    project = rest_framework.CharFilter(field_name='env__project')

    class Meta:
        model = EnvService
        fields = ['service', 'create_by', 'update_by', 'env']


class EnvDbFilter(rest_framework.FilterSet):
    host = rest_framework.CharFilter(lookup_expr='contains')
    project = rest_framework.CharFilter(field_name='env__project')

    class Meta:
        model = EnvDb
        fields = '__all__'


class PlantFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = Plant
        fields = '__all__'


class EnvPlantFilter(rest_framework.FilterSet):
    host = rest_framework.CharFilter(lookup_expr='contains')
    project = rest_framework.CharFilter(field_name='env__project')

    class Meta:
        model = EnvPlant
        fields = '__all__'


class ModuleFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    id = rest_framework.BaseInFilter(lookup_expr='in')

    class Meta:
        model = Module
        fields = '__all__'


class ServiceModuleFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    id = rest_framework.BaseInFilter(lookup_expr='in')

    class Meta:
        model = ServiceModule
        fields = '__all__'


class PageFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    module = rest_framework.BaseInFilter(lookup_expr='in')

    class Meta:
        model = Page
        fields = '__all__'
