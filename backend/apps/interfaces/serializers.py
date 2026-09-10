from rest_framework import serializers
from django.db.models import Q
from utils.base import BaseSerializer
from apps.interfaces.models import Api, ApiMock
from apps.tests.models import Step, Case, CaseSteps
from core.run_case import StepType


class ApiSerializers(BaseSerializer):
    module_name = serializers.CharField(source='module.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    service = serializers.PrimaryKeyRelatedField(read_only=True, help_text="服务ID（根据模块自动获取）")
    case_info = serializers.SerializerMethodField()
    case_num = serializers.SerializerMethodField()

    class Meta:
        model = Api
        fields = '__all__'

    def get_case_info(self, obj):
        # 列表页：viewset.list 已批量预取关联用例到 context，直接命中，避免逐行 N+1 查询
        ctx = self.context or {}
        api_case_map = ctx.get('api_case_map')
        if api_case_map is not None:
            return api_case_map.get(obj.id, [])
        # 详情/编辑页等无预取场景：轻量批量查询（select_related + prefetch_related），
        # 只取编辑页表格展示所需字段，避免全量 CaseSerializer 每用例 5 次 count 查询
        if getattr(obj, '_case_info_cache', None) is not None:
            return obj._case_info_cache
        step_ids = Step.objects.filter(Q(keyword=obj.id, type=StepType.Request, is_delete=False) |
                                       Q(keyword=obj.id, type=StepType.ComStep, is_delete=False,
                                         com_step_type=StepType.Request)).values_list('id', flat=True)

        case_ids = set(CaseSteps.objects.filter(is_delete=False, step_id__in=step_ids).values_list('case_id', flat=True))
        case_obj_set = (Case.objects.filter(id__in=case_ids, type=Case.FunctionCaseType.API)
                        .select_related('create_by', 'update_by')
                        .prefetch_related('tag'))
        case_list = [{
            'id': c.id,
            'name': c.name,
            'type': c.type,
            'type_name': c.get_type_display(),
            'tag_name': [{'id': t.id, 'name': t.name} for t in c.tag.all()],
            'recent_test_result': c.recent_test_result,
            'recent_test_result_name': c.get_recent_test_result_display(),
            'create_by': c.create_by_id,
            'create_by_name': c.create_by.username if c.create_by else None,
            'update_by': c.update_by_id,
            'update_by_name': c.update_by.username if c.update_by else None,
            'create_time': c.create_time,
            'update_time': c.update_time,
        } for c in case_obj_set]
        obj._case_info_cache = case_list
        return case_list

    def get_case_num(self, obj):
        return len(self.get_case_info(obj))

    def validate(self, attrs):
        """
        通过所属模块设置接口所属服务的值
        """
        # 获取模块和服务
        module = attrs.get('module')
        attrs['service'] = module.service

        return attrs


class ApiMockSerializers(BaseSerializer):

    class Meta:
        model = ApiMock
        fields = '__all__'

