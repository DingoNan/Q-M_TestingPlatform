from django_filters import rest_framework
from utils.base import NumberInFilter
from .models import TestPlan, TestPlanFuncCase, Suite, CrontabTask, TestPlanFuncCaseComment


class TestPlanFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    desc = rest_framework.CharFilter(lookup_expr='contains')
    project = rest_framework.NumberFilter(field_name='project')

    class Meta:
        model = TestPlan
        fields = ['name', 'desc', 'project']


class TestPlanFuncCaseFilter(rest_framework.FilterSet):
    test_plan = rest_framework.NumberFilter(field_name='test_plan')
    func_case = rest_framework.NumberFilter(field_name='func_case')
    exec_status = rest_framework.NumberFilter(field_name='exec_status')
    added_by = rest_framework.NumberFilter(field_name='added_by')
    executed_by = rest_framework.NumberFilter(field_name='executed_by')
    func_case_name = rest_framework.CharFilter(lookup_expr='contains', field_name='func_case__name')
    module = NumberInFilter(field_name='func_case__module', lookup_expr='in')

    class Meta:
        model = TestPlanFuncCase
        fields = ['test_plan', 'func_case', 'exec_status', 'added_by', 'executed_by', 'func_case_name', 'module']


class TestPlanFuncCaseCommentFilter(rest_framework.FilterSet):
    test_plan_func_case = rest_framework.NumberFilter(field_name='test_plan_func_case')
    comment_by = rest_framework.NumberFilter(field_name='comment_by')
    content = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = TestPlanFuncCaseComment
        fields = ['test_plan_func_case', 'comment_by', 'content']


class SuiteFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = Suite
        fields = ['name', 'project']


class CrontabTaskFilter(rest_framework.FilterSet):

    suite_name = rest_framework.CharFilter(lookup_expr='contains', field_name='suite__name')

    class Meta:
        model = CrontabTask
        fields = ['project', 'suite', 'env']