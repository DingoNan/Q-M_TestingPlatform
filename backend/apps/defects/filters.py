from django_filters import rest_framework
from apps.defects.models import Defect, DefectComment


class DefectFilter(rest_framework.FilterSet):
    title = rest_framework.CharFilter(lookup_expr='contains')
    severity = rest_framework.NumberFilter(field_name='severity')
    priority = rest_framework.NumberFilter(field_name='priority')
    defect_type = rest_framework.NumberFilter(field_name='defect_type')
    status = rest_framework.NumberFilter(field_name='status')
    project = rest_framework.NumberFilter(field_name='project')
    plan = rest_framework.NumberFilter(field_name='plan')
    module = rest_framework.BaseInFilter(field_name='module', lookup_expr='in')
    assignee = rest_framework.NumberFilter(field_name='assignee')
    owner = rest_framework.NumberFilter(field_name='owner')
    func_case = rest_framework.CharFilter(field_name='func_cases', method='filter_func_case')

    class Meta:
        model = Defect
        fields = ['title', 'severity', 'priority', 'defect_type', 'status', 'project', 'plan', 'module', 'assignee', 'owner', 'func_case']

    def filter_func_case(self, queryset, name, value):
        """支持多选功能用例ID过滤"""
        if isinstance(value, str):
            ids = [v for v in value.split(',') if v]
        else:
            ids = list(value)
        return queryset.filter(func_cases__in=ids).distinct()


class DefectCommentFilter(rest_framework.FilterSet):
    defect = rest_framework.NumberFilter(field_name='defect')
    comment_by = rest_framework.NumberFilter(field_name='comment_by')
    content = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = DefectComment
        fields = ['defect', 'comment_by', 'content']
