from datetime import timezone, timedelta
from rest_framework import serializers
from django.db.models import Count
from django.db.models import Exists, OuterRef, Q
from rest_framework.validators import UniqueTogetherValidator

from .models import Project, ProjectAppeal, AiConfig, ProjectMsgPush, ProjectMember, ProjectGeneralSetting
from utils.base import BaseSerializer
from apps.users.models import User
from apps.interfaces.models import Api
from apps.tests.models import Case, FuncCase, CaseSteps
from apps.reports.models import Report
from core.run_case import StepType

type_list = [Case.FunctionCaseType.API, Case.FunctionCaseType.WEB_UI, Case.FunctionCaseType.APP_UI]


class ProjectSerializer(BaseSerializer):
    user_names = serializers.SerializerMethodField()
    has_appeal = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    role_id = serializers.SerializerMethodField()
    env_number = serializers.SerializerMethodField()
    service_number = serializers.SerializerMethodField()
    plant_number = serializers.SerializerMethodField()
    db_number = serializers.SerializerMethodField()
    file_number = serializers.SerializerMethodField()
    element_number = serializers.SerializerMethodField()
    api_info = serializers.SerializerMethodField()
    step_number = serializers.SerializerMethodField()
    tag_number = serializers.SerializerMethodField()
    suite_number = serializers.SerializerMethodField()
    script_number = serializers.SerializerMethodField()
    report_number = serializers.SerializerMethodField()
    p_report_number = serializers.SerializerMethodField()
    # module_detail = serializers.SerializerMethodField()
    tag_info = serializers.SerializerMethodField()
    recent_test_result = serializers.SerializerMethodField()
    case_info = serializers.SerializerMethodField()
    suite_info = serializers.SerializerMethodField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # 判断是否是列表请求（通过context判断）
        request = self.context.get('request')
        if request and request.method == 'GET' and not request.parser_context.get('kwargs'):
            # 列表请求，移除role_info字段
            representation.pop('suite_info', None)
            representation.pop('case_info', None)
            representation.pop('recent_test_result', None)
            representation.pop('tag_info', None)
            representation.pop('api_info', None)
            representation.pop('p_report_number', None)
            representation.pop('report_number', None)
            representation.pop('script_number', None)
            representation.pop('suite_number', None)
            representation.pop('tag_number', None)
            representation.pop('step_number', None)
        return representation

    def get_suite_info(self, obj):
        x_data, s_data, f_data, e_data = [], [], [], []
        # obj.report_set.filter()
        # last_report_obj = Report.objects.last()
        report_set = Report.objects.filter(is_delete=False)[:15]
        for report_obj in report_set[::-1]:
            x_data.append(report_obj.create_time.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'))
            s_time_data = round(report_obj.success_case_number / report_obj.all_case_number,
                                2) if report_obj.all_case_number else 0
            f_time_data = round(report_obj.fail_case_number / report_obj.all_case_number,
                                2) if report_obj.all_case_number else 0
            e_time_data = round(report_obj.error_case_number / report_obj.all_case_number,
                                2) if report_obj.all_case_number else 0
            f_data.append(f_time_data * 100)
            s_data.append(s_time_data * 100)
            e_data.append(e_time_data * 100)
        return {'x_data': x_data, 's_data': s_data, 'f_data': f_data, 'e_data': e_data}

    def get_tag_info(self, obj):
        result = Case.objects.all().filter(
            project=obj, is_delete=False).order_by().values('tag', 'tag__name').annotate(count=Count('tag'))
        tag_names = []
        tag_count = []
        for case_obj in result:
            tag_names.append(case_obj['tag__name'])
            tag_count.append(case_obj['count'])

        result = FuncCase.objects.all().filter(
            project=obj, is_delete=False).order_by().values('tag', 'tag__name').annotate(count=Count('tag'))
        f_tag_names = []
        f_tag_count = []
        for case_obj in result:
            f_tag_names.append(case_obj['tag__name'])
            f_tag_count.append(case_obj['count'])

        return {'tag_names': tag_names, 'tag_count': tag_count, 'f_tag_names': f_tag_names, 'f_tag_count': f_tag_count}

    # def get_module_detail(self, obj):
    #     result = Case.objects.all().filter(project=obj, is_delete=False, is_data_factory=False
    #                                        ).order_by().values('module', 'module__name',
    #                                                            'module__plant__name').annotate(count=Count('module'))
    #     for case_obj in result:
    #         case_obj['api_count'] = Case.objects.all().annotate(type_str=Concat(Value(",", output_field=CharField()),
    #                                                                             F("type"),
    #                                                                             Value(",", output_field=CharField()),
    #                                                                             output_field=CharField())). \
    #             filter(project=obj, is_delete=False, is_data_factory=False, module=case_obj['module'],
    #                    type_str__contains='API').count()
    #         case_obj['ui_count'] = case_obj['count'] - case_obj['api_count']
    #     return result

    def get_report_number(self, obj):
        return obj.report_set.filter(is_delete=False).count()

    def get_p_report_number(self, obj):
        return obj.locustreport_set.filter(is_delete=False).count()

    def get_script_number(self, obj):
        return obj.pythonscript_set.filter(is_delete=False).count()

    def get_suite_number(self, obj):
        return obj.suite_set.filter(is_delete=False).count()

    def get_tag_number(self, obj):
        return obj.tag_set.filter(is_delete=False).count()

    def get_step_number(self, obj):
        return obj.step_set.filter(is_delete=False).count()

    def get_case_info(self, obj):
        api_count = obj.case_set.filter(type=Case.FunctionCaseType.API, is_delete=False).count()
        web_count = obj.case_set.filter(type=Case.FunctionCaseType.WEB_UI, is_delete=False).count()
        app_count = obj.case_set.filter(type=Case.FunctionCaseType.APP_UI, is_delete=False).count()
        data_count = obj.case_set.filter(type=Case.FunctionCaseType.CREATE_DATA, is_delete=False).count()
        perfmon_count = obj.case_set.filter(type=Case.FunctionCaseType.Performer, is_delete=False).count()
        f_num = obj.funccase_set.filter(is_delete=False).count()
        autoed_case_count = obj.funccase_set.filter(is_delete=False, auto_status=1).count()
        no_autoed_case_count = f_num - autoed_case_count
        a_num = obj.case_set.filter(is_delete=False).count()
        return {
            'count': [f_num, a_num, api_count, web_count, app_count, data_count, perfmon_count],
            'name': ['功能用例数', '脚本用例数', '接口用例数', 'WEB用例数', 'APP用例数', '造数用例数', '性能用例数'],
            'case_type': [
                {'value': api_count, 'name': '接口用例数'},
                {'value': web_count, 'name': 'WEB用例数'},
                {'value': app_count, 'name': 'APP用例数'},
                {'value': data_count, 'name': '造数用例数'},
                {'value': perfmon_count, 'name': '性能用例数'},
            ],
            'func_case_autoed_persent': [
                {'value': autoed_case_count, 'name': '已覆盖'},
                {'value': no_autoed_case_count, 'name': '未覆盖'}
            ],
            'test_case_type': [
                {'value': f_num, 'name': '功能用例'},
                {'value': a_num, 'name': '脚本用例'},
            ]
        }

    def get_api_info(self, obj):
        api_query_set = Api.objects.all()

        # 创建子查询：检查API是否关联用例
        case_subquery = CaseSteps.objects.filter(
            is_delete=False,
            step__keyword=OuterRef('id'),  # 注意这里修改为双下划线访问关联字段
            step__is_delete=False
        ).filter(
            Q(step__type=StepType.Request) |
            Q(step__type=StepType.ComStep, step__com_step_type=StepType.Request)
        )

        autoed_api_count = api_query_set.annotate(is_autoed=Exists(case_subquery)).filter(is_autoed=True).count()
        no_autoed_api_count = api_query_set.annotate(is_autoed=Exists(case_subquery)).filter(is_autoed=False).count()

        api_count = api_query_set.filter(module__project=obj, is_delete=False).count()
        get_count = api_query_set.filter(module__project=obj, is_delete=False, method='GET').count()
        post_count = api_query_set.filter(module__project=obj, is_delete=False, method='POST').count()
        put_count = api_query_set.filter(module__project=obj, is_delete=False, method='PUT').count()
        delete_count = api_query_set.filter(module__project=obj, is_delete=False, method='DELETE').count()
        head_count = api_query_set.filter(module__project=obj, is_delete=False, method='HEAD').count()
        options_count = api_query_set.filter(module__project=obj, is_delete=False, method='OPTIONS').count()
        patch_count = api_query_set.filter(module__project=obj, is_delete=False, method='PATCH').count()
        service_stats = api_query_set.filter(is_delete=False, service__project=obj).values('service__name').annotate(
            api_count=Count('id')
        ).order_by('-api_count')

        # 提取服务名称和对应数量
        services = [item['service__name'] for item in service_stats]
        services.append('接口总数量')
        counts = [item['api_count'] for item in service_stats]
        counts.append(api_count)
        return {
            'api_count': api_count,
            'api_type': [
                {'value': get_count, 'name': 'GET'},
                {'value': post_count, 'name': 'POST'},
                {'value': put_count, 'name': 'PUT'},
                {'value': delete_count, 'name': 'DELETE'},
                {'value': head_count, 'name': 'HEAD'},
                {'value': options_count, 'name': 'OPTIONS'},
                {'value': patch_count, 'name': 'PATCH'},

            ],
            'api_coverage_type':  [
                {'value': autoed_api_count, 'name': '已覆盖'},
                {'value': no_autoed_api_count, 'name': '未覆盖'}
            ],
            'services': services,
            'service_count': counts
        }

    def get_recent_test_result(self, obj):
        success_num = obj.case_set.filter(is_delete=False, type__in=type_list, recent_test_result=1).count()
        fail_num = obj.case_set.filter(is_delete=False, type__in=type_list, recent_test_result=2).count()
        error_num = obj.case_set.filter(is_delete=False, type__in=type_list, recent_test_result=3).count()
        no_run_num = obj.case_set.filter(is_delete=False, type__in=type_list, recent_test_result=4).count()
        return [
            {'value': success_num, 'name': '成功'},
            {'value': fail_num, 'name': '失败'},
            {'value': error_num, 'name': '错误'},
            {'value': no_run_num, 'name': '未执行'},
        ]

    def get_test_case_type(self, obj):
        f_num = obj.case_set.filter(is_delete=False, type__in=type_list).count()
        p_num = obj.case_set.filter(is_delete=False, type=Case.FunctionCaseType.Performer).count()
        return [
            {'value': f_num, 'name': '功能测试用例'},
            {'value': p_num, 'name': '性能测试用例'},
        ]

    def get_case_number(self, obj):
        return obj.case_set.filter(is_delete=False, type__in=type_list).count()

    def get_p_case_number(self, obj):
        return obj.case_set.filter(is_delete=False, type=Case.FunctionCaseType.Performer).count()

    def get_interface_number(self, obj):
        return Api.objects.all().filter(module__project=obj, is_delete=False).count()

    def get_element_number(self, obj):
        return obj.element_set.filter(is_delete=False).count()

    def get_file_number(self, obj):
        return obj.file_set.filter(is_delete=False).count()

    def get_db_number(self, obj):
        return obj.db_set.filter(is_delete=False).count()

    def get_plant_number(self, obj):
        return obj.plant_set.filter(is_delete=False).count()

    def get_service_number(self, obj):
        return obj.service_set.filter(is_delete=False).count()

    def get_env_number(self, obj):
        return obj.env_set.filter(is_delete=False).count()

    def get_user_names(self, obj):
        return User.objects.filter(project_memberships__project=obj, project_memberships__is_delete=False, is_delete=False).values('id', 'username')

    def get_user(self, obj):
        return User.objects.filter(project_memberships__project=obj, project_memberships__is_delete=False, is_delete=False).values_list('id', flat=True)

    def get_role_id(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            try:
                if user.is_superuser or user.id == obj.create_by_id:
                    return 0
                member = ProjectMember.objects.get(project=obj, user=user, is_delete=False)
                return member.role_id
            except ProjectMember.DoesNotExist:
                return None
        return None

    def get_has_appeal(self, obj):
        appeals = ProjectAppeal.objects.all().filter(project=obj, is_delete=False,
                                                     user=self.context['request'].user.id)
        if appeals:
            return appeals[0].status
        return '未申请'

    class Meta:
        model = Project
        fields = '__all__'


class ProjectAppealSerializer(BaseSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_create_by = serializers.CharField(source='project.create_by', read_only=True)
    project_create_by_id = serializers.IntegerField(source='project.create_by_id', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = ProjectAppeal
        fields = '__all__'


class AiConfigSerializer(BaseSerializer):
    class Meta:
        model = AiConfig
        fields = '__all__'
        # 显式定义唯一性验证器，并自定义错误消息
        validators = [
            UniqueTogetherValidator(
                queryset=AiConfig.objects.filter(is_delete=False),
                fields=['project', 'provider_name', 'model_name'],
                message='该模型已存在，请勿重复添加')]  # 您想要的提示

    def _clear_other_defaults(self, project, exclude_pk=None):
        """保证同项目下仅一个默认配置"""
        qs = AiConfig.objects.filter(project=project, is_default=True)
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        qs.update(is_default=False)

    def create(self, validated_data):
        instance = super().create(validated_data)
        if instance.is_default:
            self._clear_other_defaults(instance.project, exclude_pk=instance.pk)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if instance.is_default:
            self._clear_other_defaults(instance.project, exclude_pk=instance.pk)
        return instance


class ProjectMemberSerializer(BaseSerializer):
    """项目成员序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = ProjectMember
        fields = '__all__'
        # 确保一个用户在一个项目中只有一个成员记录
        validators = [
            UniqueTogetherValidator(
                queryset=ProjectMember.objects.filter(is_delete=False),
                fields=['project', 'user'],
                message='该用户已经是项目成员，请勿重复添加')]


class ProjectMsgPushSerializer(BaseSerializer):
    push_type_name = serializers.CharField(source='get_push_type_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = ProjectMsgPush
        fields = '__all__'

    def validate(self, attrs):
        project = attrs.get('project')
        push_type = attrs.get('push_type')
        
        if project and push_type:
            existing = ProjectMsgPush.objects.filter(
                project=project, 
                push_type=push_type,
                is_delete=False
            ).first()
            
            if existing and self.instance is None:
                self.existing_instance = existing
                attrs['id'] = existing.id
                attrs['is_delete'] = False
        
        return attrs

    def create(self, validated_data):
        if hasattr(self, 'existing_instance'):
            return self.update(self.existing_instance, validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.webhook_url = validated_data.get('webhook_url', instance.webhook_url)
        instance.email_host = validated_data.get('email_host', instance.email_host)
        instance.email_port = validated_data.get('email_port', instance.email_port)
        instance.email_user = validated_data.get('email_user', instance.email_user)
        instance.email_password = validated_data.get('email_password', instance.email_password)
        instance.email_to = validated_data.get('email_to', instance.email_to)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance


class ProjectGeneralSettingSerializer(BaseSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = ProjectGeneralSetting
        fields = '__all__'

    def validate_trace_retention_days(self, value):
        if value is not None and (value < 1 or value > 365):
            raise serializers.ValidationError('保留天数需在 1~365 之间')
        return value

    def validate(self, attrs):
        project = attrs.get('project')
        # OneToOne 唯一约束：同项目已有记录（含软删除）时复用该记录，避免唯一冲突
        if project and self.instance is None:
            existing = ProjectGeneralSetting.objects.filter(project=project).first()
            if existing:
                self.existing_instance = existing
        return attrs

    def create(self, validated_data):
        if hasattr(self, 'existing_instance'):
            validated_data['is_delete'] = False
            return self.update(self.existing_instance, validated_data)
        return super().create(validated_data)
