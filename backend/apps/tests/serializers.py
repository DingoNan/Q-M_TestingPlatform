import copy
from utils.base import BaseSerializer
from rest_framework.validators import ValidationError
from apps.tests.models import Case, Step, CaseRunLog, Tag, CaseSteps, FuncCase
from apps.projects.models import Project

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
        case_set = Case.objects.filter(name=case_name)
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
