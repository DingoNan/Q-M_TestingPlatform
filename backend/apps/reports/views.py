from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from utils.base import BasePageNumberPagination
from apps.reports.filters import ReportFilter, LocustReportFilter
from apps.envs.models import Env
from apps.reports.models import Report, LocustReport
from apps.reports.serializers import ReportSerializer, LocustReportSerializer
from utils.base_view import BaseModelViewSet


class ReportViewSet(BaseModelViewSet):
    serializer_class = ReportSerializer
    queryset = Report.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = ReportFilter


class LocustReportViewSet(BaseModelViewSet):
    """压测报告。

    修复项：
    - permission_classes 之前为空，未登录即可读写压测报告（P0 越权），改为要求登录；
    - request.data 在部分场景是不可变 QueryDict，直接赋值会 500；
      改成拷贝到可变 dict 后再注入 project；
    - env 缺失/不存在时返回 400，不再抛 DoesNotExist 500。
    """
    serializer_class = LocustReportSerializer
    queryset = LocustReport.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = LocustReportFilter

    def _inject_project(self, request):
        """根据 env 反查 project 并写入请求体，返回 (data, error_response)"""
        env = request.data.get('env')
        if not env:
            return None, Response({'env': ['环境ID不能为空']}, status=400)
        env_obj = Env.objects.filter(id=env, is_delete=False).first()
        if env_obj is None:
            return None, Response({'env': ['环境不存在']}, status=400)
        data = request.data.dict() if hasattr(request.data, 'dict') else dict(request.data)
        data['project'] = env_obj.project.id
        return data, None

    def create(self, request, *args, **kwargs):
        data, error = self._inject_project(request)
        if error is not None:
            return error
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        data, error = self._inject_project(request)
        if error is not None:
            return error
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)