import copy
from utils.base import BaseSerializer
from rest_framework.validators import ValidationError
from apps.tests.models import Case, Step, CaseRunLog, Tag, CaseSteps, FuncCase
from apps.projects.models import Project
from apps.interfaces.api_guard import assert_api_reference_allowed

from rest_framework import serializers


class TagSerializer(BaseSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class TagNameSerializer(BaseSerializer):

    class Meta:
        model = Tag
        fields = ['name']


class CaseNameSerializer(BaseSerializer):

    class Meta:
        model = Case
        fields = ['name', 'id']


class CaseStepSerializer(BaseSerializer):
    id = serializers.IntegerField(required=False)
    plant_name = serializers.CharField(source='plant.name', read_only=True)

    class Meta:
        model = Step
        fields = ['id', 'create_time', 'update_time', 'desc', 'type', 'keyword',
                  'update_by_name', 'create_by_name', 'is_delete', 'com_step_type', 'plant_name', 'api_method']


class StepSerializer(BaseSerializer):
    id = serializers.IntegerField(required=False)
    service_name = serializers.CharField(source='service.name', read_only=True)
    step_params = serializers.JSONField(required=False)
    step_index = serializers.JSONField(required=False)
    case_id = serializers.IntegerField(required=False)
    case_info = serializers.SerializerMethodField()

    class Meta:
        model = Step
        fields = ['id', 'create_time', 'update_time', 'desc', 'project', 'step_active_tab', 'common_headers',
                  'type', 'keyword', 'api_service', 'api_method', 'api_uri', 'api_headers',
                  'api_json', 'case_num', 'api_json_tree', 'body_type', 'api_response_tree', 'api_response_type',
                  'api_json_type', 'case_info', 'com_step_type', 'is_delete', 'setup', 'teardown', 'plant',
                  'api_data', 'api_response', 'api_params', 'check_params', 'step_params', 'case_id', 'script', 'is_check',
                  'run_params', 'loop', 'until', 'func_params', 'service_name', 'step_index', 'response_body_deal',
                  'update_by_name', 'create_by_name', 'database_name', 'timeout', 'allow_redirects', 'verify',
                  'json_body_deal', 'data_body_deal']

    def get_case_info(self, obj):
        case_step_obj_set = CaseSteps.objects.filter(step_id=obj.id, is_delete=False)
        case_obj_set = Case.objects.filter(id__in=[case_step_obj.case_id for case_step_obj in case_step_obj_set])
        case_serializer = CaseNameSerializer(case_obj_set, many=True)
        return case_serializer.data

    def validate(self, attrs):
        """步骤引用接口时校验接口状态：废弃接口不允许被引用"""
        # type=5(Request) 直接引用接口；type=3(ComStep) 且 com_step_type=5 为公共请求步骤
        step_type = attrs.get('type', getattr(self.instance, 'type', None))
        com_step_type = attrs.get('com_step_type', getattr(self.instance, 'com_step_type', None))
        is_request_step = (step_type == 5) or (step_type == 3 and com_step_type == 5)
        if is_request_step:
            assert_api_reference_allowed(attrs.get('keyword'))
        # 注意：方法名不能叫 validate_check_params —— DRF 会把它当成 check_params 字段的
        # 字段级校验器，传入的是字段值(list)而非 attrs，导致 "'list' object has no attribute 'get'"。
        self.check_check_params_structure(attrs)
        return attrs

    def check_check_params_structure(self, attrs):
        """
        保存期校验断言参数结构。

        断言项必须是 {exp_value, act_value, method} 三元组，method 取自执行引擎支持的方法表。
        旧实现保存期完全不做校验：结构写错（例如用 {key, value, type}）能保存成功，
        直到运行期才抛 KeyError，而且错误标题显示的是 KeyError 的 __doc__
        （界面上就一句「Mapping key not found.」），用户根本无法定位。
        这里在保存期就把问题拦下来，并给出正确结构示例。
        """
        check_params = attrs.get('check_params', getattr(self.instance, 'check_params', None))
        if not check_params:
            return
        if not isinstance(check_params, list):
            raise ValidationError('断言参数(check_params)必须是列表，当前为 %s' % type(check_params).__name__)
        # 延迟导入，避免模块级循环依赖
        from core.com.check import CHECK_TEXT
        for index, item in enumerate(check_params):
            position = index + 1
            if not isinstance(item, dict):
                raise ValidationError('断言参数第 %d 项必须是对象，当前为 %s' % (position, type(item).__name__))
            missing = [key for key in ('exp_value', 'act_value', 'method') if key not in item]
            if missing:
                raise ValidationError(
                    '断言参数第 %d 项缺少必需字段：%s。正确结构为 '
                    '{"exp_value": "预期值", "act_value": "实际值", "method": "check_equal"}，'
                    '当前字段为：%s' % (position, '、'.join(missing),
                                       '、'.join(sorted(item.keys())) or '空对象'))
            method = item.get('method')
            if method not in CHECK_TEXT:
                raise ValidationError(
                    '断言参数第 %d 项的 method「%s」不是支持的校验方法，可选值：%s'
                    % (position, method, '、'.join(sorted(CHECK_TEXT.keys()))))
        return


class CaseSerializer(BaseSerializer):
    name = serializers.CharField(allow_blank=False, error_messages={'blank': "用例名称不能为空"})
    params = serializers.JSONField(required=False)
    # tag = serializers.CharField(many=True, read_only=True, source='tag')
    module_name = serializers.CharField(source='module.name', read_only=True)
    plant_name = serializers.CharField(source='module.plant.name', read_only=True)
    plant = serializers.IntegerField(source='module.plant.id', read_only=True)
    tag_name = TagNameSerializer(many=True, read_only=True, source='tag')
    type_name = serializers.CharField(source='get_type_display', read_only=True)
    # step = serializers.ListSerializer(child=CaseStepSerializer(), required=False, read_only=True)
    run_times = serializers.SerializerMethodField()
    all_run_times = serializers.SerializerMethodField()
    all_success_times = serializers.SerializerMethodField()
    all_fail_times = serializers.SerializerMethodField()
    all_error_times = serializers.SerializerMethodField()
    recent_test_result_name = serializers.CharField(source='get_recent_test_result_display', read_only=True)
    recent_plan_test_result = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = '__all__'

    def validate(self, attrs):
        case_type = attrs.get('type')
        case_name = attrs.get('name')
        # 查重必须排除软删除记录，否则已删除用例的名称会被永久占用，无法重建同名用例
        case_set = Case.objects.filter(name=case_name, is_delete=False)
        if not case_type:
            raise ValidationError('用例类型不能为空')
        if self.instance:
            if case_set.exists() and case_set[0].id != self.instance.id:
                raise ValidationError('用例名称不能重复')
        else:
            if case_set.exists():
                raise ValidationError('用例名称不能重复')
        return attrs

    # def get_type_name(self, obj):
    #     type_names = []
    #     for case_type in obj.type:
    #         type_names.append()

    def get_run_times(self, obj):
        return CaseRunLog.objects.filter(is_delete=False, case_id=obj.id).count()

    def get_all_run_times(self, obj):
        return CaseRunLog.objects.filter(is_delete=False, case_id=obj.id).count()

    def get_all_success_times(self, obj):
        return CaseRunLog.objects.filter(is_delete=False, result=CaseRunLog.CaseResult.SUCCESS, case_id=obj.id).count()

    def get_all_fail_times(self, obj):
        return CaseRunLog.objects.filter(is_delete=False, result=CaseRunLog.CaseResult.FAIL, case_id=obj.id).count()

    def get_all_error_times(self, obj):
        return CaseRunLog.objects.filter(is_delete=False, result=CaseRunLog.CaseResult.ERROR, case_id=obj.id).count()

    def get_recent_plan_test_result(self, obj):
        plan_id = self.context.get('plan_id')
        func_case_id = self.context.get('func_case_id')
        if not plan_id:
            return None
        filter_kwargs = {
            'case_id': obj.id,
            'plan_id': plan_id
        }
        if func_case_id:
            filter_kwargs['func_case_id'] = func_case_id
        latest_log = CaseRunLog.objects.filter(**filter_kwargs).order_by('-create_time').first()
        return latest_log.result if latest_log else None


class FuncCaseSerializer(BaseSerializer):
    step_table = serializers.JSONField(required=False)
    tag_name = TagNameSerializer(many=True, read_only=True, source='tag')
    module_name = serializers.CharField(source='module.name', read_only=True)
    plant_name = serializers.CharField(source='module.plant.name', read_only=True)
    can_autoed_name = serializers.CharField(source='get_can_autoed_display', read_only=True)
    auto_status_name = serializers.CharField(source='get_auto_status_display', read_only=True)
    case_status_name = serializers.CharField(source='get_case_status_display', read_only=True)
    setup_condition = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    case_mark = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    step_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    exp_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    case = serializers.PrimaryKeyRelatedField(queryset=Case.objects.all(), many=True, required=False)
    case_detail = CaseSerializer(source='case', many=True, read_only=True)

    class Meta:
        model = FuncCase
        fields = '__all__'

    def validate(self, attrs):
        """名称唯一性只在未软删除的集合内校验，软删除记录不再占用名称"""
        name = attrs.get('name') or getattr(self.instance, 'name', None)
        if name:
            dup = FuncCase.objects.filter(name=name, is_delete=False)
            if self.instance:
                dup = dup.exclude(id=self.instance.id)
            if dup.exists():
                raise ValidationError('用例名称不能重复')
        return attrs


class CaseDetailSerializer(BaseSerializer):
    name = serializers.CharField(allow_blank=False, error_messages={'blank': "用例名称不能为空"})
    params = serializers.JSONField(required=False)
    # tag = serializers.CharField(many=True, read_only=True, source='tag')
    # type = serializers.IntegerField(error_messages={'invalid': '用例类型不能为空'})
    module_name = serializers.CharField(source='module.name', read_only=True)
    plant_name = serializers.CharField(source='module.plant.name', read_only=True)
    type_name = serializers.CharField(source='get_type_display', read_only=True)
    tag_name = TagNameSerializer(many=True, read_only=True, source='tag')
    step = serializers.ListSerializer(child=StepSerializer(), required=False, read_only=True)
    all_run_times = serializers.SerializerMethodField()
    all_success_times = serializers.SerializerMethodField()
    all_fail_times = serializers.SerializerMethodField()
    all_error_times = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = '__all__'

    def get_all_run_times(self, obj):
        return CaseRunLog.objects.filter(is_delete=False, case_id=obj.id).count()

    def get_all_success_times(self, obj):
        return CaseRunLog.objects.filter(is_delete=False, result=CaseRunLog.CaseResult.SUCCESS, case_id=obj.id).count()

    def get_all_fail_times(self, obj):
        return CaseRunLog.objects.filter(is_delete=False, result=CaseRunLog.CaseResult.FAIL, case_id=obj.id).count()

    def get_all_error_times(self, obj):
        return CaseRunLog.objects.filter(is_delete=False, result=CaseRunLog.CaseResult.ERROR, case_id=obj.id).count()


class RunCaseSerializer(BaseSerializer):
    name = serializers.CharField(allow_blank=False, error_messages={'blank': "用例名称不能为空"})
    params = serializers.JSONField(required=False)
    # tag = serializers.CharField(many=True, read_only=True, source='tag')
    # type = serializers.IntegerField(error_messages={'invalid': '用例类型不能为空'})
    module_name = serializers.CharField(source='module.name', read_only=True)
    plant_name = serializers.CharField(source='module.plant.name', read_only=True)
    type_name = serializers.CharField(source='get_type_display', read_only=True)
    tag_name = TagNameSerializer(many=True, read_only=True, source='tag')
    step = serializers.ListSerializer(child=StepSerializer(), required=False, read_only=True)

    class Meta:
        model = Case
        fields = '__all__'


class CaseStepsSerializer(BaseSerializer):
    class Meta:
        model = CaseSteps
        fields = '__all__'


class CaseRunLogsSerializers(BaseSerializer):

    result_value = serializers.CharField(source='get_result_display', read_only=True)
    # case_type = serializers.SerializerMethodField()
    case_module = serializers.CharField(source='case.module.name', read_only=True)
    case_plant = serializers.CharField(source='case.module.plant.name', read_only=True)
    report_name = serializers.CharField(source='report.name', read_only=True)
    env_name = serializers.CharField(source='env.name', read_only=True)
    tag_name = TagNameSerializer(many=True, read_only=True, source='case.tag')

    # def get_case_type(self, obj):
    #     return '/'.join(obj.case.type)

    class Meta:
        model = CaseRunLog
        fields = '__all__'
