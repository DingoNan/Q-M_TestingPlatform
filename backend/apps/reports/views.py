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
    serializer_class = LocustReportSerializer
    queryset = LocustReport.objects.all()
    permission_classes = []
    pagination_class = BasePageNumberPagination
    filterset_class = LocustReportFilter

    def create(self, request, *args, **kwargs):
        env = request.data.get('env')
        request.data['project'] = Env.objects.get(id=env).project.id
        response = super(LocustReportViewSet, self).create(request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        env = request.data.get('env')
        request.data['project'] = Env.objects.get(id=env).project.id
        return super().update(request, *args, **kwargs)