from django_filters import rest_framework
from django.db.models.expressions import RawSQL

from apps.tests.models import Case, Step, CaseRunLog, Tag, FuncCase


class FuncCaseFilter(rest_framework.FilterSet):
    module = rest_framework.BaseInFilter(lookup_expr='in')

    class Meta:
        model = FuncCase
        fields = ['name', 'module', 'tag', 'project', 'create_by', 'update_by', 'auto_status', 'case_status', 'owner']


class CaseFilter(rest_framework.FilterSet):
    ids = rest_framework.BaseInFilter(field_name='id', lookup_expr='in')
    name = rest_framework.CharFilter(lookup_expr='contains')
    module = rest_framework.BaseInFilter(lookup_expr='in')
    tag = rest_framework.BaseInFilter(lookup_expr='in')

    #
    # def filter_type(self, queryset, name, value):
    #     return queryset.filter(type__contains=[value])

    class Meta:
        model = Case
        fields = ['name', 'module', 'tag', 'project', 'recent_test_result',
                  'create_by', 'update_by', 'type', 'ids']


class TagFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = Tag
        fields = '__all__'


class StepFilter(rest_framework.FilterSet):
    desc = rest_framework.CharFilter(lookup_expr='contains')
    module = rest_framework.BaseInFilter(field_name='case_steps__case__module', lookup_expr='in')
    case = rest_framework.BaseInFilter(field_name='case_steps__case', lookup_expr='in')
    
    # 自定义过滤器：com_step_type等于某个值或者type等于某个值
    type = rest_framework.NumberFilter(method='filter_type')
    
    def filter_type(self, queryset, name, value):
        """
        过滤条件：com_step_type等于value或者type等于value
        """
        if value is not None:
            # 使用Q对象实现OR条件
            from django.db.models import Q
            queryset = queryset.filter(Q(com_step_type=value) | Q(type=value))
        return queryset

    class Meta:
        model = Step
        fields = ['desc', 'type', 'project', 'create_by', 'update_by', 'module', 'case']


class CaseRunLogsFilter(rest_framework.FilterSet):
    result = rest_framework.BaseInFilter(lookup_expr='in')
    module = rest_framework.BaseInFilter(field_name='case__module', lookup_expr='in')
    plant = rest_framework.BaseInFilter(field_name='case__module__plant', lookup_expr='in')
    tag = rest_framework.BaseInFilter(field_name='case__tag', lookup_expr='in')
    project = rest_framework.BaseInFilter(field_name='case__project')
    plan = rest_framework.NumberFilter(field_name='plan')
    distinct_case = rest_framework.BooleanFilter(method='filter_distinct_case')

    def filter_distinct_case(self, queryset, name, value):
        """
        当根据报告过滤且没有func_case时，按case去重，只保留每个case的最新记录
        """
        if value and 'report' in self.data:
            # 检查是否没有func_case过滤
            if 'func_case' not in self.data or not self.data['func_case']:
                from django.db.models import Max
                
                # 获取每个case的最新记录ID（兼容所有数据库）
                # 先按case_id分组，获取每个case的最大create_time
                latest_times = CaseRunLog.objects.filter(
                    report_id=self.data['report']
                ).values('case_name').annotate(
                    max_time=Max('create_time')
                ).values('case_name', 'max_time')
                
                # 构建查询条件：(case_id, create_time) 匹配最新记录
                from django.db.models import Q
                query = Q()
                for item in latest_times:
                    query |= Q(case_name=item['case_name'], create_time=item['max_time'])
                
                # 过滤出最新记录
                queryset = queryset.filter(query)
        
        return queryset

    class Meta:
        model = CaseRunLog
        fields = ['id', 'case', 'report', 'result', 'module', 'plant', 'tag', 'create_by', 'case_name', 'func_case', 'project', 'plan', 'distinct_case']
