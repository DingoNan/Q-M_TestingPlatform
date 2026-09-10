import json
import time
from django.utils import timezone
from croniter import croniter
from datetime import datetime
from utils.base import BaseSerializer
from django_q.models import Schedule
from rest_framework.validators import ValidationError
from apps.suites.models import Suite, CrontabTask, TestPlanFuncCase, TestPlan, TestPlanFuncCaseComment
from apps.tests.models import Case, FuncCase
from apps.reports.models import Report
from apps.tests.serializers import CaseSerializer, FuncCaseSerializer
from rest_framework import serializers


class TestPlanFuncCaseCommentSerializer(BaseSerializer):
    comment_by_name = serializers.CharField(source='comment_by.username', read_only=True)
    comment_by_id = serializers.IntegerField(source='comment_by.id', read_only=True)
    mentioned_users = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = TestPlanFuncCaseComment
        fields = '__all__'

    def create(self, validated_data):
        mentioned_users = validated_data.pop('mentioned_users', [])
        validated_data['comment_by'] = self.context['user']
        comment = super().create(validated_data)
        self._create_mention_messages(comment, mentioned_users)
        return comment

    def _create_mention_messages(self, comment, mentioned_users):
        """为被@提及的用户发送系统通知站内信"""
        from apps.messages.models import Message
        from apps.users.models import User
        if not mentioned_users:
            return
        plan_case = comment.test_plan_func_case
        test_plan = plan_case.test_plan
        project = test_plan.project
        users = User.objects.filter(id__in=mentioned_users)
        if not users.exists():
            return
        commenter_name = comment.comment_by.username if comment.comment_by else '系统'
        case_name = plan_case.func_case.name if hasattr(plan_case, 'func_case') and plan_case.func_case else ''
        title = '您在测试计划执行动态中被@提及'
        content = f'{commenter_name} 在测试计划【{test_plan.name}】的用例【{case_name}】执行动态中@了您'
        related_url = f'/exec/plan/detail/{test_plan.id}?case_id={plan_case.id}'
        Message.objects.bulk_create([
            Message(
                user=u,
                project=project,
                title=title,
                content=content,
                message_type=Message.MessageType.SYSTEM,
                related_url=related_url,
                create_by=comment.comment_by,
                update_by=comment.comment_by,
            ) for u in users
        ])


class TestPlanFuncCaseSerializer(BaseSerializer):
    func_case_name = serializers.CharField(source='func_case.name', read_only=True)
    func_case_detail = FuncCaseSerializer(source='func_case', read_only=True)
    func_case_tag_names = serializers.SerializerMethodField()
    added_by_name = serializers.CharField(source='added_by.username', read_only=True)
    added_by_id = serializers.IntegerField(source='added_by.id', read_only=True)
    executed_by_name = serializers.CharField(source='executed_by.username', read_only=True)
    executed_by_id = serializers.IntegerField(source='executed_by.id', read_only=True)
    exec_status_name = serializers.CharField(source='get_exec_status_display', read_only=True)
    comments = TestPlanFuncCaseCommentSerializer(many=True, read_only=True)

    class Meta:
        model = TestPlanFuncCase
        fields = '__all__'

    def to_representation(self, instance):
        # 将 plan_id 和 func_case_id 传递到嵌套的 serializer context 中
        self.context['plan_id'] = instance.test_plan_id
        self.context['func_case_id'] = instance.func_case_id
        return super().to_representation(instance)

    def get_func_case_tag_names(self, obj):
        return [tag.name for tag in obj.func_case.tag.all()]

    def validate(self, attrs):
        test_plan = attrs.get('test_plan')
        func_case = attrs.get('func_case')

        if test_plan and func_case and self.instance is None:
            existing = TestPlanFuncCase.objects.filter(
                test_plan=test_plan,
                func_case=func_case,
                is_delete=False
            ).first()

            if existing:
                raise serializers.ValidationError('该测试计划中已存在此用例')

        return attrs

    def create(self, validated_data):
        validated_data['added_by'] = self.context['user']
        return super().create(validated_data)


class TestPlanSerializer(BaseSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    status = serializers.SerializerMethodField()
    status_name = serializers.SerializerMethodField()
    pass_rate = serializers.SerializerMethodField()
    passed_count = serializers.SerializerMethodField()
    failed_count = serializers.SerializerMethodField()
    in_progress_count = serializers.SerializerMethodField()
    not_executed_count = serializers.SerializerMethodField()
    postponed_count = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()
    report_id = serializers.SerializerMethodField()

    class Meta:
        model = TestPlan
        fields = '__all__'

    def get_report_id(self, obj):
        latest_report = Report.objects.filter(plan=obj).order_by('-create_time').first()
        return latest_report.id if latest_report else None

    def _get_case_stats(self, obj):
        cases = obj.test_plan_func_cases.filter(is_delete=False)
        return {
            'total': cases.count(),
            'not_executed': cases.filter(exec_status=TestPlanFuncCase.ExecStatus.NOT_EXECUTED).count(),
            'postponed': cases.filter(exec_status=TestPlanFuncCase.ExecStatus.POSTPONED).count(),
            'passed': cases.filter(exec_status=TestPlanFuncCase.ExecStatus.PASSED).count(),
            'failed': cases.filter(exec_status=TestPlanFuncCase.ExecStatus.FAILED).count(),
            'in_progress': cases.filter(exec_status=TestPlanFuncCase.ExecStatus.TESTING).count()
        }

    def get_status(self, obj):
        stats = self._get_case_stats(obj)
        if stats['total'] == 0 or stats['not_executed'] == stats['total']:
            return 1
        elif stats['passed'] + stats['failed'] == stats['total']:
            return 3
        else:
            return 2

    def get_status_name(self, obj):
        status = self.get_status(obj)
        status_map = {1: '未开始', 2: '进行中', 3: '已完成'}
        return status_map.get(status, '未知')

    def get_pass_rate(self, obj):
        stats = self._get_case_stats(obj)
        if stats['total'] == 0:
            return 0
        return round(stats['passed'] / stats['total'] * 100, 2)

    def get_passed_count(self, obj):
        return self._get_case_stats(obj)['passed']

    def get_failed_count(self, obj):
        return self._get_case_stats(obj)['failed']

    def get_in_progress_count(self, obj):
        return self._get_case_stats(obj)['in_progress']

    def get_not_executed_count(self, obj):
        return self._get_case_stats(obj)['not_executed']

    def get_postponed_count(self, obj):
        return self._get_case_stats(obj)['postponed']

    def get_total_count(self, obj):
        return self._get_case_stats(obj)['total']


class SuiteSerializer(BaseSerializer):
    type_name = serializers.CharField(source='get_type_display', read_only=True)
    auto_cases = serializers.PrimaryKeyRelatedField(queryset=Case.objects.all(), many=True, required=False)
    auto_cases_detail = CaseSerializer(source='auto_cases', many=True, read_only=True)
    func_cases = serializers.PrimaryKeyRelatedField(queryset=FuncCase.objects.all(), many=True, required=False)
    func_cases_detail = FuncCaseSerializer(source='func_cases', many=True, read_only=True)

    class Meta:
        model = Suite
        fields = '__all__'


class CrontabTaskSerializer(BaseSerializer):
    suite_name = serializers.CharField(source='suite.name', read_only=True)
    env_name = serializers.CharField(source='env.name', read_only=True)
    schedule_name = serializers.CharField(source='schedule.name', read_only=True)

    class Meta:
        model = CrontabTask
        fields = '__all__'
        read_only_fields = ['schedule']

    def validate_crontab(self, value):
        value = value.strip()
        if len(value.split(' ')) != 5:
            raise ValidationError('定时策略格式不正确')
        return value

    def get_schedule(self):
        if self.schedule:
            return self.schedule

    def get_kwargs(self, validated_data):
        env_id = validated_data['env'] if isinstance(validated_data['env'], int) else validated_data['env'].id
        suite_id = validated_data['suite'] if isinstance(validated_data['suite'], int) else validated_data['suite'].id

        return {
            'env_id': env_id,
            'user_id': self.context['user'].id,
            'suite_id': suite_id
        }

    def create(self, validated_data):
        instance = super().create(validated_data)
        name = str(time.time()) + '_' + str(self.context['user'].id)

        minute, hour, day_of_week, day_of_month, month_of_year = validated_data['crontab'].split(' ')

        cron_expr = f"{minute} {hour} {day_of_week} {day_of_month} {month_of_year}"
        now = timezone.localtime()
        next_run = croniter(cron_expr, now).get_next(datetime)

        instance.schedule = Schedule.objects.create(
            name=name,
            func='core.run_case.run_task_suite_async',
            kwargs=json.dumps(self.get_kwargs(validated_data)),
            schedule_type=Schedule.CRON,
            cron=cron_expr,
            next_run=next_run,
            repeats=-1 if validated_data.get('enabled', True) else 0
        )
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        minute, hour, day_of_week, day_of_month, month_of_year = validated_data['crontab'].split(' ')

        cron_expr = f"{minute} {hour} {day_of_week} {day_of_month} {month_of_year}"
        now = timezone.localtime()
        next_run = croniter(cron_expr, now).get_next(datetime)

        if instance.schedule is None:
            name = str(time.time()) + '_' + str(self.context['user'].id)
            instance.schedule = Schedule.objects.create(
                name=name,
                func='core.run_case.run_task_suite_async',
                kwargs=json.dumps(self.get_kwargs(validated_data)),
                schedule_type=Schedule.CRON,
                cron=cron_expr,
                next_run=next_run,
                repeats=-1 if validated_data.get('enabled', True) else 0
            )
            instance.save()
        else:
            schedule_obj = instance.schedule
            schedule_obj.kwargs = json.dumps(self.get_kwargs(validated_data))
            schedule_obj.repeats = -1 if validated_data.get('enabled', True) else 0
            schedule_obj.schedule_type = Schedule.CRON
            schedule_obj.cron = cron_expr
            schedule_obj.next_run = next_run
            schedule_obj.save()
        return instance


