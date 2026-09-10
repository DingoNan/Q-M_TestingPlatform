from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils.base import BasePageNumberPagination
from utils.base_view import BaseModelViewSet
from apps.envs.models import (
    Env,
    EnvGlobalParams,
    GlobalParams,
    Db,
    EnvDb,
    EnvPlant,
    EnvService,
    Service,
    Plant,
    Module,
    Page,
    Headers,
    Cookies,
    EnvWebExecutor,
    EnvAppExecutor,
    ServiceModule
)
from apps.interfaces.models import Api
from apps.tests.models import Case
from apps.elements.models import Element
from apps.envs.serializers import (
    EnvSerializers,
    EnvGlobalParamsSerializers,
    GlobalParamsSerializers,
    HeadersSerializers,
    CookiesSerializers,
    ServiceSerializers,
    EnvServiceSerializers,
    PlantSerializers,
    EnvPlantSerializers,
    ModuleSerializers,
    PageSerializers,
    EnvWebExecutorSerializers,
    EnvAppExecutorSerializers,
    DbSerializers,
    EnvDbSerializers,
    ServiceModuleSerializers,
    EnvNamePlantSerializers,
    EnvNameServiceSerializers
)
from apps.envs.filters import (
    EnvFilter,
    EnvGlobalParamsFilter,
    HeadersFilter,
    ServiceFilter,
    EnvServiceFilter,
    PlantFilter,
    EnvPlantFilter,
    ModuleFilter,
    GlobalParamsFilter,
    PageFilter,
    CookiesFilter,
    EnvWebExecutorFilter,
    EnvAppExecutorFilter,
    DbFilter,
    EnvDbFilter,
    ServiceModuleFilter
)


class EnvViewSet(BaseModelViewSet):
    serializer_class = EnvSerializers
    queryset = Env.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = EnvFilter


class EnvWebExecutorViewSet(BaseModelViewSet):
    serializer_class = EnvWebExecutorSerializers
    queryset = EnvWebExecutor.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = EnvWebExecutorFilter


class EnvAppExecutorViewSet(BaseModelViewSet):
    serializer_class = EnvAppExecutorSerializers
    queryset = EnvAppExecutor.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = EnvAppExecutorFilter


class EnvGlobalParamsSet(BaseModelViewSet):
    serializer_class = EnvGlobalParamsSerializers
    queryset = EnvGlobalParams.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = EnvGlobalParamsFilter


class GlobalParamsSet(BaseModelViewSet):
    serializer_class = GlobalParamsSerializers
    queryset = GlobalParams.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = GlobalParamsFilter


class ServiceViewSet(BaseModelViewSet):
    serializer_class = ServiceSerializers
    queryset = Service.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = ServiceFilter


class DbViewSet(BaseModelViewSet):
    serializer_class = DbSerializers
    queryset = Db.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = DbFilter


class HeadersViewSet(BaseModelViewSet):
    serializer_class = HeadersSerializers
    queryset = Headers.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = HeadersFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            Q(create_by=self.request.user) | Q(is_all_run=True)
        )


class CookiesViewSet(BaseModelViewSet):
    serializer_class = CookiesSerializers
    queryset = Cookies.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = CookiesFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            Q(create_by=self.request.user) | Q(is_all_run=True)
        )


class EnvServiceViewSet(BaseModelViewSet):
    serializer_class = EnvServiceSerializers
    queryset = EnvService.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = EnvServiceFilter


class EnvDbViewSet(BaseModelViewSet):
    serializer_class = EnvDbSerializers
    queryset = EnvDb.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = EnvDbFilter


class PlantViewSet(BaseModelViewSet):
    serializer_class = PlantSerializers
    queryset = Plant.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = PlantFilter


class EnvPlantViewSet(BaseModelViewSet):
    serializer_class = EnvPlantSerializers
    queryset = EnvPlant.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = EnvPlantFilter


class ModuleViewSet(BaseModelViewSet):
    serializer_class = ModuleSerializers
    queryset = Module.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = ModuleFilter

    def destroy(self, request, *args, **kwargs):
        """
        重写删除方法，添加权限检查
        """
        instance = self.get_object()
        if Module.objects.filter(is_delete=False, parent=instance.id).exists():
            return Response(
                {"msg": ['该模块下存在子模块不能删除']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Case.objects.filter(is_delete=False, module=instance.id).exists():
            return Response(
                {"msg": ['该模块下存在用例不能删除']},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(self, request, *args, **kwargs)


class ServiceModuleViewSet(BaseModelViewSet):
    serializer_class = ServiceModuleSerializers
    queryset = ServiceModule.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = ServiceModuleFilter

    def destroy(self, request, *args, **kwargs):
        """
        重写删除方法，添加权限检查
        """
        instance = self.get_object()
        if ServiceModule.objects.filter(is_delete=False, parent=instance.id).exists():
            return Response(
                {"msg": ['该模块下存在子模块不能删除']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Api.objects.filter(is_delete=False, module=instance.id).exists():
            return Response(
                {"msg": ['该模块下存在接口不能删除']},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(self, request, *args, **kwargs)


class PageViewSet(BaseModelViewSet):
    serializer_class = PageSerializers
    queryset = Page.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = PageFilter


@api_view(['GET'])
def get_all_plant_module(request):
    project_id = request.query_params.get('project')
    disabled = request.query_params.get('disabled')
    all_plant = []
    plants = Plant.objects.all().filter(is_delete=False, project=project_id).values()
    for plant in plants:
        plant['children'] = Module.objects.all().filter(is_delete=False, plant=plant['id'], parent_id=None).values()
        for module in plant['children']:
            if module.get('children'):
                module['children'].extend(get_children(plant['id'], module['id']))
            else:
                module['children'] = get_children(plant['id'], module['id'])
        plant['id'] = -plant['id']
        all_plant.append(plant)
    return Response(all_plant)


@api_view(['GET'])
def get_all_service_module(request):
    project_id = request.query_params.get('project')
    all_service = []
    # 一次性查出所有服务与模块，内存构建树，避免逐层递归查询（原 N+1 导致接口列表页 3-5s）
    services = list(Service.objects.filter(is_delete=False, project=project_id).values())
    modules = list(ServiceModule.objects.filter(is_delete=False, service__project=project_id).values())
    module_map = {m['id']: m for m in modules}
    for m in modules:
        m['children'] = []
    # 先挂子模块，再挂父模块；服务作为根节点
    for m in modules:
        parent = m.get('parent_id')
        if parent and parent in module_map:
            module_map[parent]['children'].append(m)
    # 顶层模块（parent_id 为空）按 service 分组挂到对应服务下
    top_by_service = {}
    for m in modules:
        if not m.get('parent_id'):
            top_by_service.setdefault(m['service_id'], []).append(m)
    for service in services:
        service['children'] = top_by_service.get(service['id'], [])
        service['id'] = -service['id']
        all_service.append(service)
    return Response(all_service)


def get_children(plant_id, module_id):
    # 递归获取子节点
    children = Module.objects.all().filter(is_delete=False, plant=plant_id, parent_id=module_id).values()
    for child in children:
        if child.get('children'):
            child['children'].extend(get_children(plant_id, child['id']))
        else:
            child['children'] = get_children(plant_id, child['id'])
    return children


@api_view(['GET'])
def get_all_plant_module_two(request):
    """
    获取平级结构模块列表
    """
    project_id = request.query_params.get('project')
    all_plant = []
    plants = Plant.objects.all().filter(is_delete=False, project=project_id).values()
    for plant in plants:
        modules = Module.objects.all().filter(is_delete=False, plant=plant['id']).values()
        for module in modules:
            if not module['parent_id']:
                module['parent_id'] = -plant['id']
            all_plant.append(module)
        plant['parent_id'] = 0
        plant['id'] = -plant['id']
        all_plant.append(plant)
    return Response(all_plant)


@api_view(['GET'])
def get_request_host(request):
    """
    根据服务ID和产品ID获取步骤的接口请求域名
    """
    module = request.query_params.get('module')
    service = request.query_params.get('service')
    plant = request.query_params.get('plant')
    if module:
        module = int(module)
        if module > 0:
            service = ServiceModule.objects.get(id=module).service_id
        else:
            service = -module
    if Service.objects.get(id=service).is_server_host:
        env_service_hosts = EnvNameServiceSerializers(EnvService.objects.filter(is_delete=False, service=service),
                                                      many=True).data
        return Response({'is_server_host': True, 'env_hosts': env_service_hosts})
    else:
        env_plant_hosts = EnvNamePlantSerializers(EnvPlant.objects.filter(is_delete=False, plant=plant), many=True).data
        return Response({'is_server_host': False, 'env_hosts': env_plant_hosts})


@api_view(['GET'])
def get_all_service_module_two(request):
    """
    获取平级结构模块列表
    """
    project_id = request.query_params.get('project')
    all_service = []
    services = Service.objects.all().filter(is_delete=False, project=project_id).values()
    for service in services:
        modules = ServiceModule.objects.all().filter(is_delete=False, service=service['id']).values()
        for module in modules:
            if not module['parent_id']:
                module['parent_id'] = -service['id']
            all_service.append(module)
        service['parent_id'] = 0
        service['id'] = -service['id']
        all_service.append(service)
    return Response(all_service)


@api_view(['GET'])
def get_all_plant_module_case(request):
    """
    获取平级结构模块用例列表
    """
    project_id = request.query_params.get('project')
    all_plant = []
    plants = Plant.objects.all().filter(is_delete=False, project=project_id).values()
    for plant in plants:
        modules = Module.objects.all().filter(is_delete=False, plant=plant['id']).values()
        for module in modules:
            if not module['parent_id']:
                module['parent_id'] = -plant['id']
            all_plant.append(module)
            # cases = Case.objects.all().filter(is_delete=False, is_data_factory=True, module=module['id']).values()
            # for case in cases:
            #     case['parent_id'] = module['id']
            #     case['id'] = f'{module["id"]}_{case["id"]}'
            #     all_plant.append(case)
        plant['parent_id'] = 0
        plant['id'] = -plant['id']
        all_plant.append(plant)
    return Response(all_plant)


@api_view(['GET'])
def get_all_plant_module_page(request):
    project_id = request.query_params.get('project')
    all_plant = []
    plants = Plant.objects.all().filter(is_delete=False, project=project_id).values()
    for plant in plants:
        has_page = False
        modules = Module.objects.all().filter(is_delete=False, plant=plant['id']).values()
        all_module = []
        for module in modules:
            pages = Page.objects.all().filter(is_delete=False, module=module['id']).values()
            if pages:
                module['children'] = pages
                has_page = True
                all_module.append(module)
        if has_page:
            plant['children'] = all_module
            all_plant.append(plant)

    return Response(all_plant)


@api_view(['GET'])
def get_all_plant_element(request):
    project_id = request.query_params.get('project')
    all_plant = []
    plants = Plant.objects.all().filter(is_delete=False, project=project_id).values()
    for plant in plants:
        has_element = False
        modules = Module.objects.all().filter(is_delete=False, plant=plant['id']).values()
        all_module = []
        for module in modules:
            pages = Page.objects.all().filter(is_delete=False, module=module['id']).values()
            all_page = []
            for page in pages:
                elements = Element.objects.all().filter(is_delete=False, page=page['id']).values()
                if elements:
                    page['children'] = elements
                    has_element = True
                all_page.append(page)
            if has_element:
                module['children'] = all_page
                all_module.append(module)
        if has_element:
            plant['children'] = all_module
            all_plant.append(plant)

    return Response(all_plant)
