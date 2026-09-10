from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from apps.projects.models import Project, ProjectAppeal, AiConfig, ProjectMsgPush, ProjectMember, ProjectGeneralSetting
from apps.projects.serializers import ProjectSerializer, ProjectAppealSerializer, AiConfigSerializer, ProjectMsgPushSerializer, ProjectMemberSerializer, ProjectGeneralSettingSerializer
from apps.projects.filters import ProjectFilter, ProjectAppealFilter, ProjectMsgPushFilter
from apps.users.models import Role, RolePermission
from utils.base import BasePageNumberPagination
from utils.base_view import BaseModelViewSet


class ProjectViewSet(BaseModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = ProjectFilter


class AiConfigViewSet(BaseModelViewSet):
    queryset = AiConfig.objects.all()
    serializer_class = AiConfigSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """设为默认AI供应商（同项目下其他配置自动取消默认）"""
        config = self.get_object()
        with transaction.atomic():
            AiConfig.objects.filter(project=config.project, is_default=True).exclude(pk=config.pk).update(is_default=False)
            config.is_default = True
            config.save(update_fields=['is_default', 'update_time'])
        return Response(self.get_serializer(config).data)


class ProjectAppealViewSet(BaseModelViewSet):
    queryset = ProjectAppeal.objects.all()
    serializer_class = ProjectAppealSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = ProjectAppealFilter

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        project_id = request.data['project']
        role_id = request.data['role_id']
        user_id = request.data['user']
        appeal = ProjectAppeal.objects.get(id=kwargs['pk'])
        # 当申请通过时，创建项目成员记录
        if appeal.status:
            ProjectMember.objects.get_or_create(
                project_id=project_id,
                user_id=user_id,
                role_id=role_id
            )
        return response


class ProjectMsgPushViewSet(BaseModelViewSet):
    queryset = ProjectMsgPush.objects.all()
    serializer_class = ProjectMsgPushSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = ProjectMsgPushFilter


class ProjectGeneralSettingViewSet(BaseModelViewSet):
    """项目通用设置视图集"""
    queryset = ProjectGeneralSetting.objects.all()
    serializer_class = ProjectGeneralSettingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_project_permission(request):
    """
    检查用户在项目中的权限
    
    Args:
        user_id: 用户ID
        project_id: 项目ID
        permission_id: 权限ID
    
    Returns:
        完整的权限信息
    """
    user_id = request.user.id
    project_id = request.data.get('project_id')
    permission_id = request.data.get('permission_id')

    if request.user.is_superuser:
        return Response({'has_permission': True, 'id': 0, 'has_read_permission': True, 'has_edit_permission': True,
                         'has_add_permission': True, 'has_delete_permission': True, 'permission_id': 0,
                         'permission_name': '所有权限', 'permission_path': '/'})
    
    if not project_id:
        return Response({'error': '缺少必要参数'}, status=400)
    
    if not all([user_id, project_id, permission_id]):
        return Response({'error': '缺少必要参数'}, status=400)

    project_obj = Project.objects.all().get(id=project_id)

    if project_obj.create_by_id == user_id:
        return Response({'has_permission': True, 'id': 0, 'has_read_permission': True, 'has_edit_permission': True,
                         'has_add_permission': True, 'has_delete_permission': True, 'permission_id': 0,
                         'permission_name': '所有权限', 'permission_path': '/'})

    
    try:
        # 检查用户是否是项目成员
        member = ProjectMember.objects.select_related('user', 'project', 'role').get(
            user_id=user_id, 
            project_id=project_id, 
            is_delete=False
        )
        
        # 检查用户角色是否有对应权限
        role_permission = RolePermission.objects.select_related('permission').get(
            role_id=member.role_id,
            permission_id=permission_id,
            has_permission=True
        )
        
        # 返回角色权限和权限相关的数据
        return Response({
            'has_permission': True,
            'id': role_permission.id,
            'has_read_permission': role_permission.has_read_permission,
            'has_edit_permission': role_permission.has_edit_permission,
            'has_add_permission': role_permission.has_add_permission,
            'has_delete_permission': role_permission.has_delete_permission,
            'permission_id': role_permission.permission.id,
            'permission_name': role_permission.permission.name,
            'permission_path': role_permission.permission.path
        })
    except ProjectMember.DoesNotExist:
        return Response({'has_permission': False, 'message': '用户不是项目成员'}, status=403)
    except RolePermission.DoesNotExist:
        return Response({'has_permission': False, 'message': '用户角色没有该权限'}, status=403)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


class ProjectMemberViewSet(BaseModelViewSet):
    """项目成员视图集"""
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination

    def get_queryset(self):
        """
        根据项目ID过滤成员列表
        """
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def create(self, request, *args, **kwargs):
        """
        创建项目成员
        """
        # 检查当前用户是否有权限添加成员
        project_id = request.data.get('project')
        if project_id:
            project = Project.objects.get(id=project_id)
            # 只有项目创建者或超级管理员可以添加成员
            if not (request.user.is_superuser or project.create_by_id == request.user.id):
                return Response({'error': '您没有权限添加项目成员'}, status=403)
        
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        更新项目成员
        """
        # 检查当前用户是否有权限修改成员
        instance = self.get_object()
        # 只有项目创建者或超级管理员可以修改成员
        if not (request.user.is_superuser or instance.project.create_by_id == request.user.id):
            return Response({'error': '您没有权限修改项目成员'}, status=403)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        删除项目成员（软删除）
        """
        # 检查当前用户是否有权限删除成员
        instance = self.get_object()
        # 只有项目创建者或超级管理员可以删除成员
        if not (request.user.is_superuser or instance.project.create_by_id == request.user.id):
            return Response({'error': '您没有权限删除项目成员'}, status=403)
        
        return super().destroy(request, *args, **kwargs)
