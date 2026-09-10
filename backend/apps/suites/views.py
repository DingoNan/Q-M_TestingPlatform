from functools import partial
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django.utils import timezone
from utils.base import BasePageNumberPagination
from apps.users.models import User
from apps.suites.filters import SuiteFilter, CrontabTaskFilter, TestPlanFilter, TestPlanFuncCaseFilter, \
    TestPlanFuncCaseCommentFilter
from apps.suites.models import Suite, CrontabTask, TestPlan, TestPlanFuncCase, TestPlanFuncCaseComment
from apps.suites.serializers import SuiteSerializer, CrontabTaskSerializer, TestPlanSerializer, \
    TestPlanFuncCaseSerializer, TestPlanFuncCaseCommentSerializer
from apps.envs.models import Env
from apps.reports.models import Report
from apps.interfaces.models import Api
from apps.messages.models import Message
import core.com.faker as sys_function
from utils.base_view import BaseModelViewSet
from core.run_case import get_suite_cases, get_all_case_num, get_plan_cases, run_env_script, \
    update_env_params_info
from django_q.tasks import async_task


class SuiteViewSet(BaseModelViewSet):
    serializer_class = SuiteSerializer
    queryset = Suite.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = SuiteFilter


class TestPlanViewSet(BaseModelViewSet):
    serializer_class = TestPlanSerializer
    queryset = TestPlan.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = TestPlanFilter

    def get_queryset(self):
        return super().get_queryset().prefetch_related('test_plan_func_cases')

    @action(detail=True, methods=['get'])
    def overview(self, request, pk=None):
        test_plan = self.get_object()

        from django.db.models import Count, Q
        from apps.envs.models import Module
        from apps.tests.models import FuncCase, Tag

        cases = test_plan.test_plan_func_cases.filter(is_delete=False)

        # 基础统计
        total = cases.count()
        not_executed = cases.filter(exec_status=TestPlanFuncCase.ExecStatus.NOT_EXECUTED).count()
        postponed = cases.filter(exec_status=TestPlanFuncCase.ExecStatus.POSTPONED).count()
        passed = cases.filter(exec_status=TestPlanFuncCase.ExecStatus.PASSED).count()
        failed = cases.filter(exec_status=TestPlanFuncCase.ExecStatus.FAILED).count()
        in_progress = cases.filter(exec_status=TestPlanFuncCase.ExecStatus.TESTING).count()

        pass_rate = round(passed / total * 100, 2) if total > 0 else 0

        if total == 0 or not_executed == total:
            status = 1
            status_name = '未开始'
        elif not_executed == 0:
            status = 3
            status_name = '已完成'
        else:
            status = 2
            status_name = '进行中'

        # 按执行人统计
        executor_stats = cases.values(
            'executed_by__id',
            'executed_by__username'
        ).annotate(
            total=Count('id'),
            passed=Count('id', filter=Q(exec_status=3)),
            failed=Count('id', filter=Q(exec_status=4)),
            in_progress=Count('id', filter=Q(exec_status=5)),
            not_executed=Count('id', filter=Q(exec_status=1)),
            postponed=Count('id', filter=Q(exec_status=2))
        ).order_by('executed_by__id')

        executor_list = []
        for stat in executor_stats:
            if stat['executed_by__id']:
                rate = round(stat['passed'] / stat['total'] * 100, 2) if stat['total'] > 0 else 0
                executor_list.append({
                    'executed_by_id': stat['executed_by__id'],
                    'executed_by_name': stat['executed_by__username'],
                    'assigned_count': stat['total'],
                    'passed': stat['passed'],
                    'failed': stat['failed'],
                    'in_progress': stat['in_progress'],
                    'not_executed': stat['not_executed'],
                    'postponed': stat['postponed'],
                    'pass_rate': rate
                })

        # 缺陷统计：按执行人/模块/标签分组的缺陷数量
        from apps.defects.models import Defect
        plan_defects = Defect.objects.filter(plan=test_plan, is_delete=False)
        defects_by_assignee = {}
        defects_by_module = {}
        defects_by_tag = {}

        for defect in plan_defects.select_related('module').prefetch_related('func_cases__tag'):
            if defect.create_by_id:
                defects_by_assignee[defect.create_by_id] = defects_by_assignee.get(defect.create_by_id, 0) + 1
            if defect.module_id:
                defects_by_module[defect.module_id] = defects_by_module.get(defect.module_id, 0) + 1
            seen_tags = set()
            for fc in defect.func_cases.all():
                for tag in fc.tag.all():
                    if tag.id not in seen_tags:
                        seen_tags.add(tag.id)
                        defects_by_tag[tag.id] = defects_by_tag.get(tag.id, 0) + 1

        for item in executor_list:
            item['defect_count'] = defects_by_assignee.get(item['executed_by_id'], 0)

        # 模块统计
        func_case_ids = list(cases.values_list('func_case_id', flat=True))
        module_ids = list(set(FuncCase.objects.filter(id__in=func_case_ids).values_list('module_id', flat=True)))
        module_ids = [mid for mid in module_ids if mid is not None]

        module_stats = []
        module_filter = []
        for module_id in module_ids:
            module_obj = Module.objects.filter(id=module_id).first()
            if module_obj:
                plant_name = module_obj.plant.name
                module_name = module_obj.name
                module_filter.append({'text': f'{plant_name}_{module_name}', 'value': module_id})

                module_case_ids = list(FuncCase.objects.filter(module_id=module_id).values_list('id', flat=True))
                module_cases = cases.filter(func_case_id__in=module_case_ids)
                module_total = module_cases.count()
                module_passed = module_cases.filter(exec_status=TestPlanFuncCase.ExecStatus.PASSED).count()
                module_failed = module_cases.filter(exec_status=TestPlanFuncCase.ExecStatus.FAILED).count()
                module_in_progress = module_cases.filter(exec_status=TestPlanFuncCase.ExecStatus.TESTING).count()
                module_not_executed = module_cases.filter(exec_status=TestPlanFuncCase.ExecStatus.NOT_EXECUTED).count()
                module_postponed = module_cases.filter(exec_status=TestPlanFuncCase.ExecStatus.POSTPONED).count()

                module_stats.append({
                    'module_id': module_id,
                    'plant_name': plant_name,
                    'module_name': module_name,
                    'all_case_number': module_total,
                    'success_number': module_passed,
                    'fail_number': module_failed,
                    'error_number': module_in_progress,
                    'not_executed_number': module_not_executed,
                    'postponed_number': module_postponed,
                    'defect_count': defects_by_module.get(module_id, 0)
                })

        # 标签统计
        tag_ids = list(set(FuncCase.objects.filter(id__in=func_case_ids).values_list('tag__id', flat=True)))
        tag_ids = [tid for tid in tag_ids if tid is not None]

        tag_stats = []
        tag_filter = []
        for tag_id in tag_ids:
            tag_obj = Tag.objects.filter(id=tag_id).first()
            if tag_obj:
                tag_filter.append({'text': tag_obj.name, 'value': tag_id})

                tag_case_ids = list(FuncCase.objects.filter(tag=tag_id).values_list('id', flat=True))
                tag_cases = cases.filter(func_case_id__in=tag_case_ids)
                tag_total = tag_cases.count()
                tag_passed = tag_cases.filter(exec_status=TestPlanFuncCase.ExecStatus.PASSED).count()
                tag_failed = tag_cases.filter(exec_status=TestPlanFuncCase.ExecStatus.FAILED).count()
                tag_in_progress = tag_cases.filter(exec_status=TestPlanFuncCase.ExecStatus.TESTING).count()
                tag_not_executed = tag_cases.filter(exec_status=TestPlanFuncCase.ExecStatus.NOT_EXECUTED).count()
                tag_postponed = tag_cases.filter(exec_status=TestPlanFuncCase.ExecStatus.POSTPONED).count()

                tag_stats.append({
                    'tag_id': tag_id,
                    'name': tag_obj.name,
                    'all_case_number': tag_total,
                    'success_number': tag_passed,
                    'fail_number': tag_failed,
                    'error_number': tag_in_progress,
                    'not_executed_number': tag_not_executed,
                    'postponed_number': tag_postponed,
                    'defect_count': defects_by_tag.get(tag_id, 0)
                })

        # 缺陷列表（概览用，精简字段）
        defect_list_data = []
        for defect in plan_defects.select_related('module', 'assignee', 'owner', 'create_by', 'update_by').order_by('-create_time'):
            defect_list_data.append({
                'id': defect.id,
                'title': defect.title,
                'severity': defect.severity,
                'severity_name': defect.get_severity_display(),
                'priority': defect.priority,
                'priority_name': defect.get_priority_display(),
                'defect_type': defect.defect_type,
                'defect_type_name': defect.get_defect_type_display(),
                'status': defect.status,
                'status_name': defect.get_status_display(),
                'owner': defect.owner_id,
                'owner_name': defect.owner.username if defect.owner else '',
                'assignee': defect.assignee_id,
                'assignee_name': defect.assignee.username if defect.assignee else '',
                'module_name': defect.module.name if defect.module else '',
                'plan': defect.plan_id,
                'plan_name': defect.plan.name if defect.plan else '',
                'create_by_name': defect.create_by.username if defect.create_by else '',
                'create_time': defect.create_time.strftime('%Y-%m-%d %H:%M:%S') if defect.create_time else '',
                'update_by_name': defect.update_by.username if defect.update_by else '',
                'update_time': defect.update_time.strftime('%Y-%m-%d %H:%M:%S') if defect.update_time else '',
            })

        return Response({
            'basic_info': {
                'id': test_plan.id,
                'name': test_plan.name,
                'start_end_time': test_plan.start_end_time,
                'conclusion': test_plan.conclusion,
                'desc': test_plan.desc,
                'project_id': test_plan.project_id,
                'project_name': test_plan.project.name,
                'create_time': test_plan.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'create_by_name': test_plan.create_by.username if test_plan.create_by else ''
            },
            'status_info': {
                'status': status,
                'status_name': status_name,
                'pass_rate': pass_rate,
                'total_count': total,
                'passed_count': passed,
                'failed_count': failed,
                'in_progress_count': in_progress,
                'not_executed_count': not_executed,
                'postponed_count': postponed
            },
            'executor_stats': executor_list,
            'module_stats': module_stats,
            'module_filter': module_filter,
            'tag_stats': tag_stats,
            'tag_filter': tag_filter,
            'defect_list': defect_list_data
        })

    @action(detail=True, methods=['post'])
    def add_func_case(self, request, pk=None):
        test_plan = self.get_object()
        func_case_ids = request.data.get('func_case_ids', [])

        with transaction.atomic():
            for func_case_id in func_case_ids:
                existing = TestPlanFuncCase.objects.filter(
                    test_plan=test_plan,
                    func_case_id=func_case_id
                ).first()

                if existing:
                    if existing.is_delete:
                        existing.is_delete = False
                        existing.added_by = request.user
                        existing.exec_status = TestPlanFuncCase.ExecStatus.NOT_EXECUTED
                        existing.executed_by = request.user
                        existing.update_by = request.user
                        existing.create_by = request.user
                        existing.save()
                else:
                    TestPlanFuncCase.objects.create(
                        test_plan=test_plan,
                        func_case_id=func_case_id,
                        added_by=request.user,
                        executed_by=request.user,
                        create_by=request.user,
                        update_by=request.user
                    )
        return Response({'message': '用例添加成功'})

    @action(detail=True, methods=['post'])
    def remove_func_case(self, request, pk=None):
        test_plan = self.get_object()
        func_case_ids = request.data.get('func_case_ids', [])

        TestPlanFuncCase.objects.filter(
            test_plan=test_plan,
            func_case_id__in=func_case_ids
        ).update(is_delete=True)

        return Response({'message': '用例移除成功'})


class TestPlanFuncCaseViewSet(BaseModelViewSet):
    serializer_class = TestPlanFuncCaseSerializer
    queryset = TestPlanFuncCase.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = TestPlanFuncCaseFilter

    def perform_update(self, serializer):
        instance = serializer.instance
        old_status = instance.exec_status
        new_status = serializer.validated_data.get('exec_status', old_status)

        if old_status != new_status and new_status in [
            TestPlanFuncCase.ExecStatus.PASSED,
            TestPlanFuncCase.ExecStatus.FAILED
        ]:
            serializer.save(
                executed_by=self.request.user,
                executed_time=timezone.now()
            )
        else:
            serializer.save()

    def get_queryset(self):
        return super().get_queryset().select_related('func_case', 'added_by', 'executed_by').prefetch_related(
            'func_case__tag', 'comments')

    @action(detail=False, methods=['post'])
    def modify_executed_by(self, request):
        ids = request.data.get('ids', [])
        executed_by_id = request.data.get('executed_by')

        if not ids:
            return Response({'error': '请选择要修改的用例'}, status=400)

        try:
            executed_by = User.objects.get(id=executed_by_id) if executed_by_id else None
        except User.DoesNotExist:
            return Response({'error': '执行人不存在'}, status=400)

        count = TestPlanFuncCase.objects.filter(
            id__in=ids,
            is_delete=False
        ).update(
            executed_by=executed_by,
            update_by=request.user
        )

        return Response({
            'message': f'批量修改执行人成功，共修改 {count} 条记录',
            'count': count
        })

    @action(detail=False, methods=['post'])
    def modify_exec_status(self, request):
        ids = request.data.get('ids', [])
        exec_status = request.data.get('exec_status')

        if not ids:
            return Response({'error': '请选择要修改的用例'}, status=400)

        if exec_status not in [1, 2, 3, 4]:
            return Response({'error': '执行状态参数错误，可选值：1=未执行，2=暂缓，3=已通过，4=未通过'}, status=400)

        update_data = {
            'exec_status': exec_status,
            'update_by': request.user
        }

        if exec_status in [3, 4]:
            update_data['executed_by'] = request.user
            update_data['executed_time'] = timezone.now()

        count = TestPlanFuncCase.objects.filter(
            id__in=ids,
            is_delete=False
        ).update(**update_data)

        return Response({
            'message': f'批量修改状态成功，共修改 {count} 条记录',
            'count': count
        })

    @action(detail=False, methods=['post'])
    def run_automation_cases(self, request):
        """
        执行测试计划中的自动化脚本用例
        请求参数:
        - test_plan_id: 测试计划ID
        - func_case_ids: 功能用例ID列表
        - env_id: 环境ID
        """
        test_plan_id = request.data.get('plan_id')
        func_case_ids = request.data.get('func_case_ids', [])
        env_id = request.data.get('env_id')
        env_obj = Env.objects.get(id=env_id)
        plan_obj = TestPlan.objects.get(id=test_plan_id)
        if env_obj.setup:
            run_env_script(env_obj.setup, partial(update_env_params_info, env_id), sys_function)

        # 创建"执行中"站内信
        run_msg = Message.objects.create(
            user=request.user, project=plan_obj.project,
            title='测试计划执行中', content=f'测试计划: {plan_obj.name}',
            message_type=Message.MessageType.TASK,
            task_status=Message.TaskStatus.RUNNING,
            create_by=request.user, update_by=request.user,
        )

        if func_case_ids:
            async_task(
                'core.run_case.run_test_plan',
                env_id=env_id, test_plan_id=test_plan_id, report_id=0,
                user_id=request.user.id, func_case_ids=func_case_ids,
                run_msg_id=run_msg.id)
            return Response({'message': '自动化用例执行已开始'})

        else:
            all_case_num, func_case_ids = get_plan_cases(plan_obj)

            report_obj = Report.objects.create(
                name=plan_obj.name,
                project=plan_obj.project,
                create_by_id=request.user.id,
                update_by_id=request.user.id,
                env=env_obj,
                plan=plan_obj,
                detail={
                    'plant_filter': [],
                    'tag_filter': [],
                    'module_filter': [],
                    'module': {},
                    'tag': {}
                },
                all_case_number=all_case_num
            )

            async_task(
                'core.run_case.run_test_plan',
                env_id=env_id, test_plan_id=test_plan_id, report_id=report_obj.id,
                user_id=request.user.id, func_case_ids=func_case_ids,
                run_msg_id=run_msg.id)

            return Response({'message': '自动化用例执行已开始'})


class TestPlanFuncCaseCommentViewSet(BaseModelViewSet):
    serializer_class = TestPlanFuncCaseCommentSerializer
    queryset = TestPlanFuncCaseComment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = TestPlanFuncCaseCommentFilter

    def get_queryset(self):
        return super().get_queryset().select_related('comment_by', 'test_plan_func_case')


class CrontabTaskView(BaseModelViewSet):
    queryset = CrontabTask.objects.all()
    serializer_class = CrontabTaskSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = CrontabTaskFilter

    def perform_destroy(self, instance):
        with transaction.atomic():
            schedule = instance.schedule
            if schedule:
                instance.schedule = None
                instance.save()
                schedule.delete()
            instance.delete()


@api_view(['POST'])
def run_suite_case(request: Request):
    env_id = request.data.get('env_id')
    suite_id = request.data.get('suite_id')
    report_name = request.data.get('title')
    api_id = request.data.get('api_id')
    script_cases = request.data.get('script_cases')
    rerun_times = request.data.get('rerun_times')
    env_obj = Env.objects.get(id=env_id)

    if env_obj.setup:
        run_env_script(env_obj.setup, partial(update_env_params_info, env_id), sys_function)

    run_msg = None
    # 走套件执行
    if suite_id:
        suite_obj = Suite.objects.get(id=suite_id)
        web_executor_id = suite_obj.web_executor.id if suite_obj.web_executor else 0
        app_executor_id = suite_obj.app_executor.id if suite_obj.app_executor else 0
        rerun_times = suite_obj.rerun_times

        # 创建"执行中"站内信
        run_msg = Message.objects.create(
            user=request.user, project=suite_obj.project,
            title='套件执行中', content=f'套件: {suite_obj.name}',
            message_type=Message.MessageType.TASK,
            task_status=Message.TaskStatus.RUNNING,
            create_by=request.user, update_by=request.user,
        )

        if suite_obj.plant_type == Suite.PlanType.AUTO:
            cases = get_suite_cases(suite_obj)
            all_case_num = get_all_case_num(cases)

        else:
            all_case_num, cases = get_suite_cases(suite_obj)

        report_obj = Report.objects.create(
            name=report_name,
            project=suite_obj.project,
            create_by_id=request.user.id,
            update_by_id=request.user.id,
            env=env_obj,
            suite=suite_obj,
            detail={
                'plant_filter': [],
                'tag_filter': [],
                'module_filter': [],
                'module': {},
                'tag': {}
            },
            all_case_number=all_case_num
        )

        async_task(
            'core.run_case.run_suite_async',
            env_id=env_id, user_id=request.user.id,
            report_id=report_obj.id,
            web_executor_id=web_executor_id, app_executor_id=app_executor_id,
            rerun_times=rerun_times,
            cases=list(cases),
            plant_type=suite_obj.plant_type,
            run_msg_id=run_msg.id if run_msg else 0,
        )
    # 通过接口管理用例执行
    else:
        all_case_num = get_all_case_num(script_cases)

        report_obj = Report.objects.create(
            name=report_name,
            project=env_obj.project,
            api= Api.objects.get(id=api_id),
            create_by_id=request.user.id,
            update_by_id=request.user.id,
            env=env_obj,
            detail={
                'plant_filter': [],
                'tag_filter': [],
                'module_filter': [],
                'module': {},
                'tag': {}
            },
            all_case_number=all_case_num
        )

        async_task(
            'core.run_case.run_suite_async',
            env_id=env_id, user_id=request.user.id,
            report_id=report_obj.id,
            web_executor_id=0, app_executor_id=0,
            rerun_times=rerun_times,
            cases=list(script_cases),
            plant_type=Suite.PlanType.AUTO,
            run_msg_id=0,
        )


    return Response(data={'report_id': report_obj.id, 'message': f'执行已启动, 共收集 {all_case_num} 条用例'}, status=200)
