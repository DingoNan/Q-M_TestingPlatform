from datetime import timedelta, timezone
from utils.base import BaseSerializer
from apps.reports.models import Report, LocustReport
from apps.tests.serializers import FuncCaseSerializer
from apps.suites.models import Suite

from rest_framework import serializers


class ReportSerializer(BaseSerializer):

    suite_name = serializers.SerializerMethodField()
    suite_type = serializers.SerializerMethodField()
    suite_model = serializers.SerializerMethodField()
    suite_func_cases = FuncCaseSerializer(source='suite.func_cases', many=True, read_only=True)
    env_name = serializers.CharField(source='env.name', read_only=True)
    success_percent = serializers.SerializerMethodField()
    error_percent = serializers.SerializerMethodField()
    fail_percent = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    def get_suite_name(self, obj):
        return obj.suite.name if obj.suite else ''

    def get_suite_type(self, obj):
        if obj.suite:
            return obj.suite.plant_type
        elif obj.plan:
            return Suite.PlanType.FUNCTION
        else:
            return Suite.PlanType.AUTO

    def get_suite_model(self, obj):
        return obj.suite.plant_model if obj.suite else Suite.PlanModel.STATIC

    def get_history(self, obj):
        x_data, s_data, f_data, e_data = [], [], [], []
        report_set = Report.objects.filter(is_delete=False, suite=obj.suite)[:15]
        for report_obj in report_set[::-1]:
            x_data.append(report_obj.create_time.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'))
            s_time_data = round(report_obj.success_case_number / report_obj.all_case_number, 2) if report_obj.all_case_number else 0
            f_time_data = round(report_obj.fail_case_number / report_obj.all_case_number, 2) if report_obj.all_case_number else 0
            e_time_data = round(report_obj.error_case_number / report_obj.all_case_number, 2) if report_obj.all_case_number else 0
            f_data.append(f_time_data * 100)
            s_data.append(s_time_data * 100)
            e_data.append(e_time_data * 100)
        return {'x_data': x_data, 's_data': s_data, 'f_data': f_data, 'e_data': e_data}

    def get_success_percent(self, obj):
        if obj.all_case_number:
            return round((obj.success_case_number / obj.all_case_number) * 100, 2)
        else:
            return 0

    def get_error_percent(self, obj):
        if obj.all_case_number:
            return round((obj.error_case_number / obj.all_case_number) * 100, 2)
        else:
            return 0

    def get_fail_percent(self, obj):
        if obj.all_case_number:
            return round((obj.fail_case_number / obj.all_case_number) * 100, 2)
        else:
            return 0

    def get_modules(self, obj):
        return obj.detail['module'].values()

    def get_tags(self, obj):
        return obj.detail['tag'].values()

    class Meta:
        model = Report
        fields = '__all__'


class LocustReportSerializer(BaseSerializer):
    case_name = serializers.CharField(source='case.name', read_only=True)
    env_name = serializers.CharField(source='env.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    end_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    test_process_name = serializers.CharField(source='get_test_process_display', read_only=True)

    class Meta:
        model = LocustReport
        fields = '__all__'
