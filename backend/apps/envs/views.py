from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils.base import BasePageNumberPagination
from utils.base_view import BaseModelViewSet
from utils.cascade import cascade_soft_delete_atomic
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

    def destroy(self, request, *args, **kwargs):
        """删除服务：级联软删除其下的服务模块、接口文档、服务域名配置等"""
        instance = self.get_object()
        service_name = instance.name
        stats = cascade_soft_delete_atomic(instance)
        total = sum(stats.values())
        return Response({
            'msg': f'服务「{service_name}」及其关联数据已删除，共 {total} 条',
            'detail': stats,
            'total': total,
        }, status=200)


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
        """删除服务模块：级联软删除其下的子模块、接口。
        与 ServiceViewSet.destroy 保持一致，复用 utils.cascade 的通用级联软删除。
        """
        instance = self.get_object()
        module_name = instance.name
        # 级联前先统计影响范围，回传给前端做删除结果提示
        stats = cascade_soft_delete_atomic(instance)
        total = sum(stats.values())
        self_label = f'{instance._meta.app_label}.{instance._meta.object_name}'
        # stats 中同类模型归一个键，父模块自身也计入其中；对外只报「随它一起被删的子孙」
        module_count = max(0, stats.get(self_label, 0) - 1)
        api_count = sum(v for k, v in stats.items() if k.endswith('.Api'))
        return Response({
            'msg': f'模块「{module_name}」及其关联数据已删除，共 {total} 条',
            'detail': stats,
            'total': total,
            'module_count': module_count,
            'api_count': api_count,
        }, status=200)


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
    # ★ 2026-09-22 修复 500（原报错：Service.DoesNotExist @ envs/views.py:351）
    #   原实现直接 Service.objects.get(id=service)：当前端切到「测试」页签、
    #   还没选中服务/模块（service 为空、或指向已软删的服务）时会直接抛异常。
    #   实测 12 个参数变体里有 8 个返回 500（ApiList.vue 切页签时无前置判断）。
    #   这里改为容错查询 + 空列表回退，前端可正常渲染「暂无可用域名」。
    try:
        svc = Service.objects.filter(id=service, is_delete=False).first() if service else None
    except (ValueError, TypeError):
        svc = None
    if svc is None:
        return Response({
            'is_server_host': False,
            'env_hosts': [],
            'warning': '未找到对应的服务配置，请先在服务管理中选择所属服务',
        })
    if svc.is_server_host:
        env_service_hosts = EnvNameServiceSerializers(EnvService.objects.filter(is_delete=False, service=svc.id),
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
    """获取「平台 → 模块 → 元素」三级树

    ★ 2026-09-22 修复 500（原报错：FieldError: Cannot resolve keyword 'page'）：
      原实现按「平台 → 模块 → 页面 → 元素」四层拼装，其中
        elements = Element.objects.filter(is_delete=False, page=page['id'])
      引用了一个**不存在的字段** —— Element 模型（apps/elements/models.py）只有
        project / module / name / type / web / ios / android / status
      元素是直接挂在「模块」下的，根本没有「页面」这一层外键，
      该查询必然抛 FieldError，接口稳定返回 500。
      现改为按 module 关联，返回 plant → module → element 三级结构。
      注意：返回层级由四层变三层，是本次修复带来的**结构变更**。
    """
    project_id = request.query_params.get('project')
    all_plant = []
    plants = Plant.objects.filter(is_delete=False, project=project_id).values()
    for plant in plants:
        all_module = []
        for module in Module.objects.filter(is_delete=False, plant=plant['id']).values():
            elements = list(Element.objects.filter(is_delete=False, module=module['id']).values())
            if elements:
                module['children'] = elements
                all_module.append(module)
        if all_module:
            plant['children'] = all_module
            all_plant.append(plant)

    return Response(all_plant)
