from django_filters import rest_framework

from apps.reports.models import Report, LocustReport


class ReportFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = Report
        fields = ['name', 'project', 'create_by', 'env', 'suite', 'api']


class LocustReportFilter(rest_framework.FilterSet):
    case_name = rest_framework.CharFilter(field_name='case__name', lookup_expr='contains')

    class Meta:
        model = LocustReport
        fields = ['project', 'case_name', 'env', 'user']