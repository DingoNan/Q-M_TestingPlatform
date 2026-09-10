import copy
import os
import time
from threading import Thread
from django.http import StreamingHttpResponse
from django.db import models
from django_q.tasks import async_task
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.request import Request
from utils.base import BasePageNumberPagination
from apps.tests.filters import CaseFilter, StepFilter, CaseRunLogsFilter, TagFilter, FuncCaseFilter
from apps.tests.models import Case, Step, CaseRunLog, Tag, CaseSteps, FuncCase
from apps.scripts.models import PythonScript
from apps.projects.models import Project
from apps.users.models import User
from apps.reports.models import LocustReport
from apps.messages.models import Message
from apps.interfaces.models import Api
from black_bag.settings import BASE_DIR
from apps.tests.serializers import CaseSerializer, StepSerializer, CaseRunLogsSerializers, TagSerializer,\
    CaseStepsSerializer, CaseDetailSerializer, CaseStepSerializer, RunCaseSerializer, FuncCaseSerializer
from utils.base_view import BaseModelViewSet
from apps.envs.models import Plant, Module, Headers, EnvService, EnvGlobalParams, EnvPlant, Service, GlobalParams
from core.run_case import run_one_case, StepType
from core.com.check import CHECK_FUNC_MAP
from core.com.enum_obj import StepType
from core.step.run_appium import appium_actions
from core.step.run_selenium import selenium_actions
from core.step.run_playwright import playwright_actions
from core.com.faker import faker_function_list, faker_function_doc, faker_function_map, faker_function_doc_two
from core.com.common import get_function_params
from core.com.step_model import SeleniumStepType, AppiumStepType
from core.step.run_system_function import run_debug_system_function, run_debug_user_function
from utils.user_exception import EnvServiceNotExistException, EnvPlantNotExistException


class FuncCaseViewSet(BaseModelViewSet):
    serializer_class = FuncCaseSerializer
    queryset = FuncCase.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = FuncCaseFilter

    @action(methods=['post'], detail=False)
    def batch_update(self, request, *args, **kwargs):
        """
        批量更新功能用例字段
        支持批量修改: owner(负责人)、auto_status(自动化状态)、case_status(用例状态)、tag(添加标签)
        单个修改也走此接口(ids长度为1)
        """
        user = request.user
        ids = request.data.get('ids', [])
        if not ids:
            return Response(data={'error': 'ids不能为空'}, status=400)

        func_cases = FuncCase.objects.filter(id__in=ids, is_delete=False)
        if not func_cases.exists():
            return Response(data={'error': '未找到对应用例'}, status=404)

        update_fields = []
        # 用例名称
        name = request.data.get('name')
        if name:
            func_cases.update(name=name, update_by_id=user.id)
            update_fields.append('name')
        # 所属模块
        module_id = request.data.get('module')
        if module_id:
            func_cases.update(module_id=module_id, update_by_id=user.id)
            update_fields.append('module')
        # 负责人
        owner_id = request.data.get('owner')
        if owner_id:
            func_cases.update(owner_id=owner_id, update_by_id=user.id)
            update_fields.append('owner')
        # 自动化状态(联动用例类型can_autoed)
        auto_status = request.data.get('auto_status')
        if auto_status is not None:
            # 1. 先找出需要联动更新can_autoed的子集
            if auto_status == 4:
                # 新值=手工测试，原来不是手工测试的 → can_autoed改为3(手工测试)
                need_update_can_autoed = func_cases.exclude(auto_status=4)
                can_autoed_new = FuncCase.IsAutoed.NoCan  # 3
            else:
                # 新值=自动化(1/2/3)，原来是手工测试的 → can_autoed改为1(全自动化)
                need_update_can_autoed = func_cases.filter(auto_status=4)
                can_autoed_new = FuncCase.IsAutoed.CAN  # 1

            # 先更新需要联动的子集
            if need_update_can_autoed.exists():
                need_update_can_autoed.update(
                    auto_status=auto_status,
                    can_autoed=can_autoed_new,
                    update_by_id=user.id
                )
                update_fields.extend(['auto_status', 'can_autoed'])
                # 剩下不需要联动的记录单独更新
                remain = func_cases.exclude(pk__in=need_update_can_autoed.values_list('pk', flat=True))
                if remain.exists():
                    remain.update(auto_status=auto_status, update_by_id=user.id)
            else:
                # 没有需要联动的，整体更新
                func_cases.update(auto_status=auto_status, update_by_id=user.id)
                if 'auto_status' not in update_fields:
                    update_fields.append('auto_status')
        # 用例状态
        case_status = request.data.get('case_status')
        if case_status is not None:
            func_cases.update(case_status=case_status, update_by_id=user.id)
            update_fields.append('case_status')
        # 标签: tag_mode='replace'为替换模式(编辑面板用), 默认为追加模式(批量添加用)
        tag_ids = request.data.get('tag')
        if tag_ids is not None:
            tag_objs = Tag.objects.filter(id__in=tag_ids, is_delete=False)
            tag_mode = request.data.get('tag_mode', 'add')
            for func_case_obj in func_cases:
                if tag_mode == 'replace':
                    func_case_obj.tag.clear()
                func_case_obj.tag.add(*tag_objs)
                func_case_obj.update_by_id = user.id
                func_case_obj.save()
            update_fields.append('tag')

        return Response(data={'msg': '成功', 'count': func_cases.count(), 'fields': update_fields}, status=200)


# 造数平台测试用例使用,获取用例所有得测试步骤
class CaseDetailViewSet(BaseModelViewSet):
    serializer_class = CaseDetailSerializer
    queryset = Case.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = CaseFilter

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        for index in range(len(response.data['step']) - 1, -1, -1):
            if response.data['step'][index]['is_delete']:
                del response.data['step'][index]
                continue
            case_id = response.data['id']
            step_id = response.data['step'][index]['id']
            case_steps_obj = CaseSteps.objects.get(step_id=step_id, case_id=case_id, is_delete=False)
            response.data['step'][index]['step_index'] = case_steps_obj.step_index
            response.data['step'][index]['step_params'] = case_steps_obj.step_params
            response.data['step'][index]['case_step_id'] = case_steps_obj.id
        response.data['step'].sort(key=lambda x: x['step_index'])
        return response


class CaseViewSet(BaseModelViewSet):
    serializer_class = CaseSerializer
    queryset = Case.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = CaseFilter

    @action(methods=['post'], detail=False)
    def batch_update(self, request, *args, **kwargs):
        """
        批量更新脚本用例字段
        支持批量修改: tag(添加标签)
        单个修改也走此接口(ids长度为1)
        """
        user = request.user
        ids = request.data.get('ids', [])
        if not ids:
            return Response(data={'error': 'ids不能为空'}, status=400)

        cases = Case.objects.filter(id__in=ids, is_delete=False)
        if not cases.exists():
            return Response(data={'error': '未找到对应用例'}, status=404)

        update_fields = []
        # 标签: tag_mode='replace'为替换模式(编辑面板用), 默认为追加模式(批量添加用)
        tag_ids = request.data.get('tag')
        if tag_ids is not None:
            tag_objs = Tag.objects.filter(id__in=tag_ids, is_delete=False)
            tag_mode = request.data.get('tag_mode', 'add')
            for case_obj in cases:
                if tag_mode == 'replace':
                    case_obj.tag.clear()
                case_obj.tag.add(*tag_objs)
                case_obj.update_by_id = user.id
                case_obj.save()
            update_fields.append('tag')

        return Response(data={'msg': '成功', 'count': cases.count(), 'fields': update_fields}, status=200)

    def create(self, request, *args, **kwargs):
        is_performance = request.data.get('is_performance')
        response = super(CaseViewSet, self).create(request, *args, **kwargs)
        if is_performance:
            pass
        return response

    def retrieve(self, request, *args, **kwargs):
        case_id = self.kwargs.get('pk')
        response = super().retrieve(request, *args, **kwargs)
        response.data['step'] = []
        if response.data['data'] is None:
            response.data['data'] = {"name": ["params_1"], "value": []}
        case_step_set = CaseSteps.objects.filter(case_id=case_id, is_delete=False).order_by('step_index')
        for case_step_obj in case_step_set:
            step_map = {'step_index': case_step_obj.step_index, 'step_params': case_step_obj.step_params,
                        'case_step_id': case_step_obj.id, 'parent_id': case_step_obj.parent_id,
                        'is_run': case_step_obj.is_run, 'fail_is_continue': case_step_obj.fail_is_continue}
            step_set = Step.objects.filter(id=case_step_obj.step_id, is_delete=False)
            if not step_set.exists():
                continue
            step_map.update(CaseStepSerializer(step_set[0]).data)
            response.data['step'].append(step_map)
        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        for case_obj in response.data['results']:
            del case_obj['step']
        return response

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        case_id = self.kwargs.get('pk')
        step_ids = CaseSteps.objects.filter(case_id=case_id, is_delete=False).values_list('step_id', flat=True)
        new_step_ids = copy.copy(step_ids)
        CaseSteps.objects.filter(case_id=case_id, is_delete=False).update(is_delete=True, update_by=user)
        for step_id in new_step_ids:
            step_obj = Step.objects.get(id=step_id)
            if step_obj.type != StepType.ComStep:
                step_obj.is_delete = True
                step_obj.update_by_id = user.id
                step_obj.save()
            else:
                if not CaseSteps.objects.filter(step_id=step_id, is_delete=False).exists():
                    step_obj.is_delete = True
                    step_obj.update_by_id = user.id
                    step_obj.save()

        response = super().destroy(request, *args, **kwargs)
        return response


class TagViewSet(BaseModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = TagFilter


class CaseStepsViewSet(BaseModelViewSet):
    serializer_class = CaseStepsSerializer
    queryset = CaseSteps.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination


class StepViewSet(BaseModelViewSet):
    serializer_class = StepSerializer
    queryset = Step.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = StepFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 检查是否按用例过滤
        case_filter = self.request.query_params.get('case')
        
        if case_filter:
            # 如果按用例过滤，则按步骤索引排序
            queryset = queryset.annotate(
                step_index=models.Min('case_steps__step_index')
            ).order_by('step_index')
        
        # 去重：因为StepFilter中使用了case_steps关联查询，会产生重复数据
        return queryset.distinct()

    def update(self, request, *args, **kwargs):
        # 之前用 request.data['type'] 硬取值，缺字段直接 KeyError -> 500
        step_type = request.data.get('type')
        case_step_id = request.data.pop('case_step_id', None)
        request.data.pop('step_index', None)
        step_params = request.data.pop('step_params', None)
        is_run = request.data.pop('is_run', None)
        fail_is_continue = request.data.pop('fail_is_continue', None)
        user = self.request.user
        case_step_ids = self.kwargs.get('pk')
        case_id = case_step_ids.split('_')[0]
        step_id = case_step_ids.split('_')[1]
        case_step_id = int(case_step_ids.split('_')[2])
        self.kwargs['pk'] = step_id
        # 走非公共步骤逻辑
        if step_type != StepType.ComStep:
            case_step_obj = CaseSteps.objects.get(id=case_step_id, case_id=case_id, step_id=step_id, is_delete=False)
            case_step_obj.step_params = step_params
            case_step_obj.is_run = is_run
            case_step_obj.fail_is_continue = fail_is_continue
            case_step_obj.update_by_id = user.id
            case_step_obj.save()
            response = super().update(request, *args, **kwargs)

        # 走公共步骤逻辑
        else:
            response = super().update(request, *args, **kwargs)
            # 如果有case_step_id有值就走更新逻辑
            if case_step_id:
                CaseSteps.objects.filter(id=case_step_id).update(case_id=case_id, step_id=step_id, step_index=step_index,
                                         step_params=step_params, create_by_id=user.id, update_by_id=user.id,
                                         fail_is_continue=fail_is_continue, is_run=is_run)
            else:
                # if not CaseSteps.objects.filter(case_id=case_id, step_id=step_id, id=case_step_id, is_delete=False):
                step_index = len(CaseSteps.objects.filter(case_id=case_id, is_delete=False))
                obj = CaseSteps.objects.create(case_id=case_id, step_id=step_id, step_index=step_index,
                                               step_params=step_params, create_by_id=user.id, update_by_id=user.id,
                                               fail_is_continue=fail_is_continue, is_run=is_run)
                case_step_id = obj.id
        response.data['case_step_id'] = case_step_id
        return response

    def retrieve(self, request, *args, **kwargs):
        case_step_id = self.kwargs.get('pk')
        ids = case_step_id.split('_')
        case_id = ids[0]
        step_id = ids[1]
        case_step_id = int(ids[2])
        self.kwargs['pk'] = step_id
        # 从用例里获取步骤详情
        if case_step_id:
            case_step_obj = CaseSteps.objects.get(id=case_step_id, case_id=case_id, step_id=step_id, is_delete=False)
        # 从步骤列表获取
        else:
            case_step_obj = CaseSteps.objects.filter(case_id=case_id, step_id=step_id, is_delete=False)[0]
        response = super().retrieve(request, *args, **kwargs)
        response.data['step_params'] = case_step_obj.step_params
        response.data['case_step_id'] = case_step_obj.id
        response.data['fail_is_continue'] = case_step_obj.fail_is_continue
        response.data['is_run'] = case_step_obj.is_run
        response.data['step_index'] = case_step_obj.step_index
        return response

    def create(self, request, *args, **kwargs):
        user = self.request.user
        # 之前全部用 pop('x') 硬取值，缺任一字段直接 KeyError -> 500。
        # 改为带默认值取值，并对真正必填的 case_id 显式返回 400。
        request.data.pop('id', None)
        case_id = request.data.pop('case_id', None)
        step_params = request.data.pop('step_params', None)
        fail_is_continue = request.data.pop('fail_is_continue', 0)
        is_run = request.data.pop('is_run', True)
        request.data.pop('step_index', None)
        if not case_id:
            return Response({'case_id': ['所属用例ID不能为空']}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        step_obj = serializer.save()
        step_id = step_obj.id

        step_index = len(CaseSteps.objects.filter(case_id=case_id, is_delete=False))
        obj = CaseSteps.objects.create(case_id=case_id, step_id=step_id, step_index=step_index, step_params=step_params,
                                       create_by_id=user.id, update_by_id=user.id, fail_is_continue=fail_is_continue,
                                       is_run=is_run)

        return Response(data={'step_id': step_id, 'case_step_id': obj.id}, status=201)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        case_step_id = self.kwargs.get('pk')
        ids = case_step_id.split('_')
        case_id = ids[0]
        step_id = ids[1]
        step_index = ids[2]
        step_number = len(CaseSteps.objects.filter(step_id=step_id, is_delete=False))
        # case_ids = list(set(case_ids))
        # case_ids 长度=1说明该步骤只有这个测试用例引用了可以删除了
        case_step_obj = CaseSteps.objects.get(step_id=step_id, case_id=case_id, is_delete=False, step_index=step_index)
        case_step_obj.is_delete = True
        case_step_obj.update_by_id = user.id
        case_step_obj.save()
        if step_number == 1:
            step_obj = Step.objects.get(id=step_id, is_delete=False)
            step_obj.is_delete = True
            step_obj.update_by_id = user.id
            step_obj.save()

        # 更新该用例其他步骤的步骤索引关系
        case_step_query = CaseSteps.objects.filter(case=case_id, is_delete=False)
        for index, case_step_obj in enumerate(case_step_query):
            case_step_obj.step_index = index
            case_step_obj.save()

        return Response(data='成功', status=200)


class CaseRunLogsViewSet(BaseModelViewSet):
    serializer_class = CaseRunLogsSerializers
    queryset = CaseRunLog.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = CaseRunLogsFilter


@api_view(['GET'])
def get_logs_by_report(request: Request):
    """
     通过功能用例ID获取分组
    """
    page = int(request.query_params.get('page'))
    size = int(request.query_params.get('size'))
    result = request.query_params.get('result')
    result = result.split(',') if result else []
    tag = request.query_params.get('tag')
    tag = tag.split(',') if tag else []
    plant = request.query_params.get('plant')
    plant = plant.split(',') if plant else []
    module = request.query_params.get('module')
    module = module.split(',') if module else []
    report_id = request.query_params.get('report')

    case_ids = list(set(CaseRunLog.objects.all().filter(report_id=report_id).values_list('func_case_id', flat=True)))

    start = (page - 1) * size
    func_cases_obj = FuncCase.objects.filter(id__in=case_ids)
    if tag:
        func_cases_obj = func_cases_obj.filter(tag__in=tag)
    if plant:
        func_cases_obj = func_cases_obj.filter(module__plant__in=plant)
    if module:
        func_cases_obj = func_cases_obj.filter(module__in=plant)

    func_cases_data = FuncCaseSerializer(func_cases_obj, many=True).data

    # 通过功能用例执行结果过滤
    if len(result) == 1:
        tmp_func_cases_data = []
        for func_case_data in func_cases_data:
            func_case_data['log_detail'] = CaseRunLog.objects.all().filter(report_id=report_id,
                                                                           func_case_id=func_case_data['id']).values()
            func_case_data['func_result'] = 1
            func_case_data['func_result_text'] = '成功'
            func_case_data['auto_s'] = 0
            func_case_data['auto_f'] = 0
            func_case_data['auto_e'] = 0
            for auto_case_log in func_case_data['log_detail']:
                if auto_case_log['result'] == CaseRunLog.CaseResult.SUCCESS:
                    func_case_data['auto_s'] = func_case_data['auto_s'] + 1
                elif auto_case_log['result'] == CaseRunLog.CaseResult.FAIL:
                    func_case_data['auto_f'] = func_case_data['auto_f'] + 1
                    func_case_data['func_result'] = 2
                    func_case_data['func_result_text'] = '失败'
                else:
                    func_case_data['auto_e'] = func_case_data['auto_e'] + 1
                    func_case_data['func_result'] = 2
                    func_case_data['func_result_text'] = '失败'

            if func_case_data['func_result'] == int(result[0]):
                tmp_func_cases_data.append(func_case_data)


        if start + size < len(tmp_func_cases_data):
            tmp_func_cases_data = tmp_func_cases_data[start: start + size]
        else:
            tmp_func_cases_data = tmp_func_cases_data[start:]

        data = {
            'count': len(tmp_func_cases_data),
            'results': tmp_func_cases_data
        }

    else:

        if start + size < len(func_cases_data):
            func_cases_data = func_cases_data[start: start + size]
        else:
            func_cases_data = func_cases_data[start:]

        for func_case_data in func_cases_data:
            func_case_data['log_detail'] = CaseRunLog.objects.all().filter(report_id=report_id,
                                                                           func_case_id=func_case_data['id']).values()
            func_case_data['func_result'] = 1
            func_case_data['func_result_text'] = '成功'
            func_case_data['auto_s'] = 0
            func_case_data['auto_f'] = 0
            func_case_data['auto_e'] = 0
            for auto_case_log in func_case_data['log_detail']:
                if auto_case_log['result'] == CaseRunLog.CaseResult.SUCCESS:
                    func_case_data['auto_s'] = func_case_data['auto_s'] + 1
                elif auto_case_log['result'] == CaseRunLog.CaseResult.FAIL:
                    func_case_data['auto_f'] = func_case_data['auto_f'] + 1
                    func_case_data['func_result'] = 2
                    func_case_data['func_result_text'] = '失败'
                else:
                    func_case_data['auto_e'] = func_case_data['auto_e'] + 1
                    func_case_data['func_result'] = 2
                    func_case_data['func_result_text'] = '失败'


        data = {
            'count': len(func_cases_data),
            'results': func_cases_data
        }
    return Response(data=data, status=200)


def get_plant_api_action_keys(project_id):
    plants = Plant.objects.all().filter(project=project_id, is_delete=False).values()
    for plant in plants:
        plant['children'] = Module.objects.all().filter(plant=plant['id'], is_delete=False, parent_id=None).values()
        if not plant['children']:
            plant['disabled'] = True
        for module in plant['children']:
            if module.get('children'):
                module['children'].extend(get_children(plant['id'], module['id']))
            else:
                module['children'] = get_children(plant['id'], module['id'])
            # module['children'] = Api.objects.all().filter(module=module['id'], is_delete=False).values()
            if not module['children']:
                module['disabled'] = True
    return plants


def get_children(plant_id, module_id):
    # 递归获取子节点
    children = Module.objects.all().filter(is_delete=False, plant=plant_id, parent_id=module_id).values()
    for child in children:
        if child.get('children'):
            child['children'].extend(get_children(plant_id, child['id']))
        else:
            child['children'] = get_children(plant_id, child['id'])
        if not child['children']:
            child['children'] = Api.objects.all().filter(module=child['id'], is_delete=False).values()
            if not child['children']:
                child['disabled'] = True
    return children


def get_plant_step_action_keys(project_id):
    plants = Plant.objects.all().filter(project=project_id, is_delete=False).values()
    for plant_obj in plants:
        plant_obj['children'] = Module.objects.all().filter(plant=plant_obj['id'], is_delete=False).values()
        if not plant_obj['children']:
            plant_obj['disabled'] = True
        for module_obj in plant_obj['children']:
            module_obj['children'] = Step.objects.all().filter(module=module_obj['id'], is_delete=False).values()
            if not module_obj['children']:
                module_obj['disabled'] = True
    return plants


def get_plant_script_action_keys(project_id):
    plants = Plant.objects.all().filter(project=project_id, is_delete=False).values()
    for plant_obj in plants:
        plant_obj['children'] = Module.objects.all().filter(plant=plant_obj['id'], is_delete=False).values()
        if not plant_obj['children']:
            plant_obj['disabled'] = True
        for module_obj in plant_obj['children']:
            user_funcs = PythonScript.objects.all().filter(module=module_obj['id'], is_delete=False)
            module_obj['children'] = []
            for obj in user_funcs:
                module_obj['children'].append({'id': obj.id, 'name': obj.desc})
            if not module_obj['children']:
                module_obj['disabled'] = True
    return plants


@api_view(['POST'])
def case_run(request: Request):
    env_id = request.data.get('env_id')
    case_data_index = request.data.get('case_data')
    case_id = request.data.get('case_id')
    run_times = request.data.get('run_times')
    is_async = request.data.get('is_async')
    fail_is_continue = request.data.get('fail_is_continue')
    web_executor_id = request.data.get('web_executor_id')
    app_executor_id = request.data.get('app_executor_id')
    case = Case.objects.all().get(id=case_id)
    # 数据驱动用例下只执行某个用例
    if case.data['value'] and case_data_index >= 0:
        case_data = [case.data['value'][case_data_index]]
    else:
        case_data = None
    if is_async:
        # 异步执行：发送任务消息（进行中），执行完成后由任务回写状态，点击消息跳转用例详情
        message = Message.objects.create(
            user=request.user,
            project=case.project,
            title='用例执行中',
            content=f'用例: {case.name}\n执行次数: {run_times}',
            message_type=Message.MessageType.TASK,
            task_status=Message.TaskStatus.RUNNING,
            total_count=run_times,
            success_count=0,
            failed_count=0,
            create_by=request.user,
            update_by=request.user,
        )
        # 实时推送消息到前端
        try:
            from apps.messages.push import push_message_to_user, build_message_payload
            push_message_to_user(request.user.id, build_message_payload(message))
        except Exception:
            pass
        for _ in range(run_times):
            async_task('apps.tests.tasks.run_one_case_with_message', env_id, case_id, request.user.id,
                       web_executor_id, app_executor_id, fail_is_continue, case_data, message.id)
        return Response(data='成功', status=200)

    else:
        log_obj_id = None
        for _ in range(run_times):
            log_obj_id = run_one_case(env_id, case_id, request.user.id, web_executor_id, app_executor_id, 0, 0, None,
                                      fail_is_continue, case_data=case_data)
        log_obj = CaseRunLog.objects.get(id=log_obj_id).logs
        return Response(data=log_obj, status=200)


@api_view(['POST'])
def step_run(request: Request):
    env_id = request.data.get('env_id')
    case_id = request.data.get('case_id')
    run_times = request.data.get('run_times')
    case_data_index = request.data.get('case_data')
    step_index = request.data.get('step_index')
    fail_is_continue = request.data.get('fail_is_continue')
    web_executor_id = request.data.get('web_executor_id')
    app_executor_id = request.data.get('app_executor_id')
    # 数据驱动用例下只执行某个用例
    case = Case.objects.all().get(id=case_id)
    # 数据驱动用例下只执行某个用例
    if case.data['value']:
        case_data = [case.data['value'][case_data_index]]
    else:
        case_data = None
    log_obj_id = run_one_case(env_id, case_id, request.user.id, web_executor_id, app_executor_id, 0, 0, None,
                              fail_is_continue, step_index=step_index, case_data=case_data)
    log_obj = CaseRunLog.objects.get(id=log_obj_id).logs[-1]['logs']
    return Response(data=log_obj, status=200)


@api_view(['POST'])
def locust_run(request: Request):
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    env_id = request.data.get('env_id')
    case_id = request.data.get('case_id')
    project_id = request.data.get('project_id')
    users_per_second = request.data.get('users_per_second')
    concurrent_users = request.data.get('concurrent_users')
    durations = request.data.get('durations')
    report = LocustReport.objects.create(**{'case_id': case_id, 'user_id': request.user.id, 'env_id': env_id,
                                            'cpu': 0, 'memory': 0, 'rate': users_per_second, 'project_id': project_id,
                                            'max_user': concurrent_users, 'duration': durations,
                                            'start_time': start_time, 'end_time': start_time})
    thread = Thread(
        target=run_locust_standalone,
        args=(case_id, env_id, request.user.id, durations, users_per_second, concurrent_users, report.id)
    )
    thread.daemon = True  # 设置为守护线程
    thread.start()
    # run_locust_standalone(case_id, env_id, request.user.id, durations, users_per_second, concurrent_users, report.id)
    # run_locust_standalone.delay(case_id, env_id, request.user.id, durations, users_per_second, concurrent_users)
    return Response(data={'report_id': report.id}, status=200)


def run_locust_standalone(case_id, env_id, user_id, run_times, rate, user_num, report_id):
    # 惰性导入：locust 会触发 gevent monkey-patch，必须延后到真正运行压测时才加载，
    # 避免在 Django(ASGI/WSGI) 启动阶段就 patch ssl/threading/socket 破坏服务器
    from core.locust.locust_model import start_system_standalone_locust_headless_programmatically
    case = Case.objects.all().get(id=case_id)
    steps, host_set = get_run_step_data(case, env_id=env_id, user_id=user_id)
    steps = build_tree(steps)
    host_list = list(host_set)
    test_host = host_list[0]
    env_params = get_env_params_by_env_id(env_id=env_id)
    global_params = get_global_params_by_project_id(project_id=case.project)
    start_system_standalone_locust_headless_programmatically(steps, global_params, env_params, host_list,  case_id,
                                                             env_id, user_id, run_times, rate, user_num, test_host,
                                                             report_id)


@api_view(['POST'])
def get_init_data(request: Request):
    case_id = request.data.get('case_id')
    env_id = request.data.get('env_id')
    user_id = request.data.get('user_id')
    response_data = {'steps': None, 'env_params': None}
    case = Case.objects.all().get(id=case_id)
    step_data, host_set = get_run_step_data(case, env_id=env_id, user_id=user_id)
    response_data['steps'] = build_tree(step_data)
    response_data['host_list'] = list(host_set)
    response_data['env_params'] = get_env_params_by_env_id(env_id=env_id)
    response_data['global_params'] = get_global_params_by_project_id(project_id=case.project)
    return Response(response_data, status=200)


@api_view(['GET'])
def download_windows(request: Request):
    file_path = os.path.join(BASE_DIR, 'QMTestPlatform.exe')

    if not os.path.exists(file_path):
        return Response({"error": "File not found"}, status=404)

    # 创建文件流
    def file_generator():
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192 * 8):
                yield chunk

    response = StreamingHttpResponse(
        file_generator(),
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = 'attachment; filename="QMTestPlatform.exe"'
    response['Content-Length'] = str(os.path.getsize(file_path))

    return response


@api_view(['GET'])
def download_macos(request: Request):
    file_path = os.path.join(BASE_DIR, 'QMTestPlatform.exe')

    if not os.path.exists(file_path):
        return Response({"error": "File not found"}, status=404)

    # 创建文件流
    def file_generator():
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192 * 8):
                yield chunk

    response = StreamingHttpResponse(
        file_generator(),
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = 'attachment; filename="QMTestPlatform.exe"'
    response['Content-Length'] = str(os.path.getsize(file_path))

    return response


@api_view(['GET'])
def download_linux(request: Request):
    file_path = os.path.join(BASE_DIR, 'QMTestPlatform.exe')

    if not os.path.exists(file_path):
        return Response({"error": "File not found"}, status=404)

    # 创建文件流
    def file_generator():
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192 * 8):
                yield chunk

    response = StreamingHttpResponse(
        file_generator(),
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = 'attachment; filename="QMTestPlatform.exe"'
    response['Content-Length'] = str(os.path.getsize(file_path))

    return response


@api_view(['POST'])
def copy_case(request: Request):
    user = request.user
    case_id = request.data.get('case_id')
    case_obj = Case.objects.get(id=case_id)
    new_case_obj = Case.objects.create(name=case_obj.name + '副本', is_data_factory=case_obj.is_data_factory,
                                       type=case_obj.type,  project=case_obj.project, module=case_obj.module,
                                       params=case_obj.params, update_by=user, create_by=user)
    return Response(data='复制成功', status=200)


@api_view(['POST'])
def update_step_is_run(request: Request):
    case_step_id = request.data.get('id')
    case_step_ids = request.data.get('ids')
    is_run = request.data.get('is_run')
    is_all = request.data.get('is_all')
    if is_all:
        CaseSteps.objects.filter(id__in=case_step_ids, is_delete=False).update(is_run=is_run)
    else:
        case_step_obj = CaseSteps.objects.get(id=case_step_id, is_delete=False)
        case_step_obj.is_run = is_run
        case_step_obj.save()
    return Response(data='成功', status=200)


@api_view(['POST'])
def change_step_index(request: Request):
    data = request.data.get('data')
    save_case_step(data)
    return Response(data='成功', status=200)


def save_case_step(data, parent_id=None, step_index=0):
    """
    全量保存排序后的数据
    """
    for step_obj in data:
        case_step_obj = CaseSteps.objects.get(id=step_obj.get('case_step_id'), is_delete=False)
        case_step_obj.step_index = step_index
        case_step_obj.parent_id = parent_id
        case_step_obj.save()
        step_index = step_index + 1
        if step_obj.get('children'):
            step_index = save_case_step(step_obj.get('children'), parent_id=step_obj.get('case_step_id'),
                                        step_index=step_index)
    return step_index


@api_view(['GET'])
def get_check_list(request: Request):
    return Response(data=[function_name for function_name in CHECK_FUNC_MAP.keys() if
                          function_name.startswith('check') or function_name == 'no_check'], status=200)


@api_view(['GET'])
def get_system_function_params_doc(request: Request):
    """
    获取平台系统函数文档
    """
    params_doc_map = dict()
    system_function_name = request.query_params.get('step_key')
    if request.query_params.get('docs_type'):
        params_doc_map['doc'] = faker_function_doc_two[system_function_name]
    else:
        params_doc_map['doc'] = faker_function_doc[system_function_name]
    params_doc_map['params'] = get_function_params(faker_function_map[system_function_name])
    return Response(data=params_doc_map, status=200)


@api_view(['POST'])
def run_system_function(request: Request):
    """
    执行平台系统函数并返回函数执行结果
    """
    try:
        function_name = request.data.get('name')
        params_info = request.data.get('params')
        return Response(data=run_debug_system_function(function_name, params_info), status=200)
    except Exception as e:
        return Response(data={'error': [str(e)]}, status=400)


@api_view(['POST'])
def run_user_function(request: Request):
    """
    执行用户自定义函数并返回函数执行结果
    """
    python_func_obj = request.data.get('python_func_obj')
    return Response(data=run_debug_user_function(python_func_obj), status=200)


@api_view(['GET'])
def get_selenium_params_doc(request: Request):
    """
    获取selenium函数文档
    """
    step_type = request.query_params.get('step_type')
    data = FAKER_FUNC_DOC if step_type == StepType.PlatformSystemFunction else selenium_func_doc
    return Response(data=data, status=200)


@api_view(['GET'])
def function_keys(request: Request):
    project_id = request.query_params.get('project')
    user_customize_function = get_plant_script_action_keys(project_id)
    data = [
        {
            "name": '系统自带函数',
            "id": StepType.PlatformSystemFunction,
            "children": faker_function_list
        },
        {
            "name": '用户自定义函数',
            "id": StepType.UserCustomizeFunction,
            "children": user_customize_function
        },
    ]
    return Response(data=data, status=200)


@api_view(['GET'])
def get_selenium_keys(request: Request):
    is_group = request.query_params.get('group')
    is_group = True if is_group else False
    page = request.query_params.get('page')
    size = request.query_params.get('size')
    page = int(page)if page else None
    size = int(size) if size else None
    find_equal = request.query_params.get('find_equal')
    name = request.query_params.get('name')
    step_type = request.query_params.get('type')
    step_type = int(step_type) if step_type else 0

    if is_group:
        # 按group_id分组，返回所有数据
        groups_dict = {}
        
        for obj in selenium_actions:
            group_id = obj.get('group')
            group_name = obj.get('group_name', f'分组{group_id}')
            
            # 如果group_id不存在，跳过
            if group_id is None:
                continue
                
            # 创建分组结构
            if group_id not in groups_dict:
                groups_dict[group_id] = {
                    'id': group_id,
                    'name': group_name,
                    'isParent': True,
                    'children': []
                }
            
            # 将操作添加到对应分组的children中
            groups_dict[group_id]['children'].append(obj)
        
        # 转换为列表格式并返回所有数据
        data = list(groups_dict.values())
        
        return Response(data={
            'count': len(data),
            'results': data
        }, status=200)

    else:
        start = (page - 1) * size
        if name:
            if find_equal == 'true':
                old_data = [obj for obj in selenium_actions if name == obj['id']]
            else:
                old_data = [obj for obj in selenium_actions if name in obj['id']]
        else:
            old_data = selenium_actions

        if step_type != SeleniumStepType.All:
            old_data = [obj for obj in selenium_actions if step_type == obj['group']]

        if start + size < len(old_data):
            keys = old_data[start: start + size]
        else:
            keys = old_data[start:]

        data = {
            'count': len(old_data),
            'results': keys
        }
        return Response(data=data, status=200)


@api_view(['GET'])
def get_playwright_keys(request: Request):
    is_group = request.query_params.get('group')
    is_group = True if is_group else False
    page = request.query_params.get('page')
    size = request.query_params.get('size')
    page = int(page) if page else None
    size = int(size) if size else None
    find_equal = request.query_params.get('find_equal')
    name = request.query_params.get('name')
    step_type = request.query_params.get('type')
    step_type = int(step_type) if step_type else 0

    if is_group:
        # 按group_id分组，返回所有数据
        groups_dict = {}

        for obj in playwright_actions:
            group_id = obj.get('group')
            group_name = obj.get('group_name', f'分组{group_id}')

            # 如果group_id不存在，跳过
            if group_id is None:
                continue

            # 创建分组结构
            if group_id not in groups_dict:
                groups_dict[group_id] = {
                    'id': group_id,
                    'name': group_name,
                    'isParent': True,
                    'children': []
                }

            # 将操作添加到对应分组的children中
            groups_dict[group_id]['children'].append(obj)

        # 转换为列表格式并返回所有数据
        data = list(groups_dict.values())

        return Response(data={
            'count': len(data),
            'results': data
        }, status=200)

    else:
        start = (page - 1) * size
        if name:
            if find_equal == 'true':
                old_data = [obj for obj in playwright_actions if name == obj['id']]
            else:
                old_data = [obj for obj in playwright_actions if name in obj['id']]
        else:
            old_data = playwright_actions

        if step_type != SeleniumStepType.All:
            old_data = [obj for obj in playwright_actions if step_type == obj['group']]

        if start + size < len(old_data):
            keys = old_data[start: start + size]
        else:
            keys = old_data[start:]

        data = {
            'count': len(old_data),
            'results': keys
        }
        return Response(data=data, status=200)


@api_view(['GET'])
def get_appium_keys(request: Request):
    is_group = request.query_params.get('group')
    is_group = True if is_group else False
    page = request.query_params.get('page')
    size = request.query_params.get('size')
    page = int(page) if page else None
    size = int(size) if size else None
    find_equal = request.query_params.get('find_equal')
    name = request.query_params.get('name')
    step_type = request.query_params.get('type')
    step_type = int(step_type) if step_type else 0

    if is_group:
        # 按group_id分组，返回所有数据
        groups_dict = {}
        for obj in appium_actions:
            group_id = obj.get('group')
            group_name = obj.get('group_name', f'分组{group_id}')

            # 如果group_id不存在，跳过
            if group_id is None:
                continue

            # 创建分组结构
            if group_id not in groups_dict:
                groups_dict[group_id] = {
                    'id': group_id,
                    'name': group_name,
                    'isParent': True,
                    'children': []
                }

            # 将操作添加到对应分组的children中
            groups_dict[group_id]['children'].append(obj)

        # 转换为列表格式并返回所有数据
        data = list(groups_dict.values())

        return Response(data={
            'count': len(data),
            'results': data
        }, status=200)

    else:
        start = (page - 1) * size
        if name:
            if find_equal == 'true':
                old_data = [obj for obj in appium_actions if name == obj['name']]
            else:
                old_data = [obj for obj in appium_actions if name in obj['name']]
        else:
            old_data = appium_actions

        if step_type != AppiumStepType.All:
            old_data = [obj for obj in appium_actions if step_type == obj['group']]

        if start + size < len(old_data):
            keys = old_data[start: start + size]
        else:
            keys = old_data[start:]

        data = {
            'count': len(old_data),
            'results': keys
        }
        return Response(data=data, status=200)


@api_view(['GET'])
def action_keys(request: Request):
    project_id = request.query_params.get('project')
    request_apis = get_plant_api_action_keys(project_id)
    user_customize_function = get_plant_script_action_keys(project_id)
    data = [
        {
            "name": 'PlatformSystemFunction',
            "id": StepType.PlatformSystemFunction,
            "children": [
                {
                    "name": 'faker',
                    "id": 'faker',
                    "children": faker_function_list
                }
            ]
        },
        {
            "name": 'Requests',
            "id": StepType.Request,
            "children": request_apis
        },
        {
            "name": 'UserCustomizeFunction',
            "id": StepType.UserCustomizeFunction,
            "children": user_customize_function
        },
        {
            "name": 'Selenium',
            "id": StepType.Selenium,
            "children": selenium_actions
        },
    ]
    if request.query_params.get('isCase'):
        com_steps = get_plant_step_action_keys(project_id)
        data.append({
            "name": 'ComSteps',
            "id": StepType.ComStep,
            "children": com_steps
        })
    data.append(
        {
            "name": 'PythonScript',
            "id": StepType.UserCustomizeScript,
            "children": []
        }
    )
    return Response(data=data, status=200)


def get_env_params_by_env_id(env_id):
    """
    通过项目ID和环境ID获取环境下所有变量
    """
    env_params_map = {}
    env_params_set = EnvGlobalParams.objects.all().filter(env=env_id, is_delete=False)
    if env_params_set:
        for env_params_obj in env_params_set:
            env_params_map[env_params_obj.name] = env_params_obj.value

    return env_params_map


def get_global_params_by_project_id(project_id):
    """
    通过项目ID和环境ID获取环境下所有变量
    """
    global_params_map = {}
    global_params_set = GlobalParams.objects.all().filter(project=project_id, is_delete=False)
    if global_params_set:
        for env_params_obj in global_params_set:
            global_params_map[env_params_obj.name] = env_params_obj.value

    return global_params_map


def get_run_step_data(case, env_id, user_id):
    """
    获取平级的执行步骤数据
    """
    case_data = RunCaseSerializer(case).data
    case_data['step'] = []
    host_set = set()
    case_step_set = CaseSteps.objects.filter(case_id=case_data['id'], is_delete=False).order_by('step_index')
    for case_step_obj in case_step_set:
        step_map = {'step_index': case_step_obj.step_index, 'step_params': case_step_obj.step_params,
                    'case_step_id': case_step_obj.id, 'parent_id': case_step_obj.parent_id, 'children': [],
                    'is_run': case_step_obj.is_run, 'fail_is_continue': case_step_obj.fail_is_continue}
        step_set = Step.objects.filter(id=case_step_obj.step_id, is_delete=False)
        if not step_set.exists():
            continue
        step = StepSerializer(step_set[0]).data

        env_headers_query = Headers.objects.filter(plant=step['plant'], is_delete=False, is_all_run=False, env=env_id,
                                                   create_by=user_id)

        host, step['api_uri'] = get_api_host(step['api_uri'], env_id, step['api_service'], step['plant'],
                                             case_step_obj.step_index)
        if host:
            host_set.add(host)
        step['plant_headers'] = env_headers_query[0].value if env_headers_query else []
        step_map.update(step)
        case_data['step'].append(step_map)
    return case_data['step'], host_set


def get_api_host(uri, env_id, service, plant, step_index, local_host='127.0.0.1'):
    """
    根据接口请求路径匹配对应的规则
    """
    if service:
        server_obj = Service.objects.all().get(id=service)

        # 接口请求域名跟随服务域名走
        if server_obj.is_server_host:
            env_service_query = EnvService.objects.all().filter(env=env_id, service=service, is_delete=False)
            if not env_service_query.exists():
                raise EnvServiceNotExistException()
            host = env_service_query[0].host
            return host, host + uri
        # 接口请求域名跟随产品域名配置
        else:
            env_plant_query = EnvPlant.objects.all().filter(env=env_id, plant=plant, is_delete=False)
            if not env_plant_query.exists():
                raise EnvPlantNotExistException()
            host = env_plant_query[0].host
            return host, host + uri
    else:
        return None, None


def build_tree(data, id_key='case_step_id', parent_key='parent_id', children_key='children'):
    """
    将平级数据结构转换为多层树形结构

    参数:
        data: 列表，包含字典元素
        id_key: 节点ID的键名 (默认为 'id')
        parent_key: 父节点ID的键名 (默认为 'parent_id')
        children_key: 子节点列表的键名 (默认为 'children')

    返回:
        树形结构列表（森林），只包含根节点
    """
    # 创建节点字典和根节点列表
    nodes = {item[id_key]: item.copy() for item in data}
    roots = []

    # 构建树结构
    for item_id, node in nodes.items():
        parent_id = node.get(parent_key)

        # 根节点直接添加到结果
        if parent_id is None:
            roots.append(node)
        else:
            # 找到父节点并添加当前节点到其子节点列表
            parent = nodes.get(parent_id)
            if parent:
                # 初始化父节点的children列表（如果不存在）
                if children_key not in parent:
                    parent[children_key] = []
                parent[children_key].append(node)

    return roots


@api_view(['GET'])
def get_locust_run_data(request: Request):
    """
    压测工具通过接口动态获取项目， 用户， 脚本， 环境
    """
    data = {}
    project_query_set = Project.objects.all().filter(is_delete=False)
    for project_obj in project_query_set:
        data[project_obj.name] = {"users": [], "envs": [], "scripts": []}
        data[project_obj.name]["users"] = User.objects.filter(project_memberships__project=project_obj, project_memberships__is_delete=False, is_delete=False).values('id', 'username')
        data[project_obj.name]["envs"] = project_obj.env_set.all().values('id', 'name')
        data[project_obj.name]["scripts"] = project_obj.case_set.all().filter(type=5).values('id', 'name')
    return Response(data=data, status=200)


@api_view(['POST'])
def add_many_step_for_case(request: Request):
    """
    为每个测试用例批量添加测试步骤
    """
    case_id = request.data.get('case_id')
    is_com_step = request.data.get('is_com_step')
    data_steps = request.data.get('data')
    user_id = request.data.get('user_id')
    # 引用公共步骤逻辑
    if is_com_step:
        for data in data_steps:
            step_id = data['id']
            if data['type'] != 3:
                step_obj = Step.objects.get(id=step_id)
                step_obj.type = 3
                step_obj.com_step_type = data['type']
                step_obj.save()
            step_index = len(CaseSteps.objects.filter(case_id=case_id, is_delete=False))
            CaseSteps.objects.create(case_id=case_id, step_id=step_id, step_index=step_index,
                                           step_params=[], create_by_id=user_id, update_by_id=user_id)
    # 引用非公共步骤逻辑
    else:
        for data in data_steps:
            step_id = data['id']
            step_obj = Step.objects.get(id=step_id)
            step_obj.pk = None
            # 引用的步骤类型是公共步骤
            if step_obj.type == 3:
                step_obj.type = step_obj.com_step_type
            step_obj.create_by_id = user_id
            step_obj.update_by_id = user_id
            step_obj.save()
            step_index = len(CaseSteps.objects.filter(case_id=case_id, is_delete=False))
            CaseSteps.objects.create(case_id=case_id, step_id=step_obj.id, step_index=step_index,
                                     step_params=[], create_by_id=user_id, update_by_id=user_id)

    return Response(data='成功', status=200)