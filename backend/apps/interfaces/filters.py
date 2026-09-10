from django_filters import rest_framework
from django.db.models import Exists, OuterRef, Q
from apps.interfaces.models import Api, ApiMock
from apps.tests.models import Step, CaseSteps, Case
from core.run_case import StepType


class ApiFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    project = rest_framework.CharFilter(field_name='service__project')
    module = rest_framework.BaseInFilter(lookup_expr='in')
    is_autoed = rest_framework.BooleanFilter(method='filter_is_autoed')

    class Meta:
        model = Api
        fields = ['name', 'project', 'url', 'method', 'service', 'module', 'create_by', 'update_by', 'is_autoed', 'status']

    def filter_is_autoed(self, queryset, name, value):
        """
        根据是否关联用例进行过滤
        value: True - 只返回有关联用例的API, False - 只返回无关联用例的API
        """

        # 创建子查询：检查API是否关联用例
        case_subquery = CaseSteps.objects.filter(
            is_delete=False,
            step__keyword=OuterRef('id'),  # 注意这里修改为双下划线访问关联字段
            step__is_delete=False
        ).filter(
            Q(step__type=StepType.Request) |
            Q(step__type=StepType.ComStep, step__com_step_type=StepType.Request)
        )

        # 根据布尔值过滤
        if value:
            return queryset.annotate(is_autoed=Exists(case_subquery)).filter(is_autoed=True)
        else:
            return queryset.annotate(is_autoed=Exists(case_subquery)).filter(is_autoed=False)


class ApiMockFilter(rest_framework.FilterSet):
    class Meta:
        model = ApiMock
        fields = ['api']
