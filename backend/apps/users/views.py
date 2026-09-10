from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from rest_framework.validators import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.utils.serializer_helpers import ReturnList
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from apps.users.models import Permission, Role, RolePermission, User, Group, Navigation
from apps.projects.models import Project
from apps.users.serializers import (
    LoginSerializer,
    MyTokenRefreshSerializer,
    UserSerializers,
    GroupSerializer,
    PermissionSerializer,
    RoleSerializer,
    RolePermissionSerializer,
    NavigationSerializer,
    UserNameSerializers
)
from utils.base_view import BaseModelViewSet, BaseCreateModelViewSet
from utils.base import BasePageNumberPagination
from apps.users.filters import PermissionFilter, RoleFilter, UserFilter, GroupFilter, NavigationFilter


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer


class UserViewSet(BaseModelViewSet):
    serializer_class = UserSerializers
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = UserFilter

    def get_queryset(self):
        # 只在list操作时排除超级管理员
        if self.action == 'list':
            return super().get_queryset().exclude(username="admin")
        return super().get_queryset()


class GroupViewSet(BaseModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    permission_classes = [AllowAny]
    authentication_classes = []
    # pagination_class = BasePageNumberPagination
    filterset_class = GroupFilter

    # def list(self, request, *args, **kwargs):
    #     response = super().list(request, *args, **kwargs)
    #     for index, group_obj in enumerate(response.data):
    #         navigation_obj = Navigation.objects.filter(is_delete=False, group=group_obj['id'])
    #         response.data[index]['navagition'] = NavigationSerializer(navigation_obj, many=True).data
    #     print(response.data, 'test')
    #     return response


class NavigationViewSet(BaseModelViewSet):
    serializer_class = NavigationSerializer
    queryset = Navigation.objects.all()
    permission_classes = [AllowAny]
    authentication_classes = []
    # pagination_class = BasePageNumberPagination
    filterset_class = NavigationFilter


class RolePermissionViewSet(BaseModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated]

    def _update_role_permission(self, role_permission, user_id):
        has_permission = role_permission['has_permission']
        has_read_permission = role_permission['has_read_permission']
        has_edit_permission = role_permission['has_edit_permission']
        has_add_permission = role_permission['has_add_permission']
        has_delete_permission = role_permission['has_delete_permission']
        role_id = self.kwargs.get('pk')
        permission_id = role_permission['id']
        role_permission_obj = RolePermission.objects.all().filter(role_id=role_id, permission_id=permission_id)

        if role_permission_obj:
            role_permission_obj = role_permission_obj[0]
            role_permission_obj.has_permission = has_permission
            role_permission_obj.has_read_permission = has_read_permission
            role_permission_obj.has_edit_permission = has_edit_permission
            role_permission_obj.has_add_permission = has_add_permission
            role_permission_obj.has_delete_permission = has_delete_permission
            role_permission_obj.create_by = user_id
            role_permission_obj.save()
        else:
            self._create_role_permission(has_permission, role_id, permission_id, has_read_permission,
                                         has_edit_permission, has_add_permission, has_delete_permission, user_id)

    @staticmethod
    def _create_role_permission(has_permission, role_id, permission_id, has_read_permission, has_edit_permission,
                                has_add_permission, has_delete_permission, user_id):
        RolePermission.objects.create(has_permission=has_permission, role_id=role_id, permission_id=permission_id,
                                      has_read_permission=has_read_permission, has_edit_permission=has_edit_permission,
                                      has_delete_permission=has_delete_permission, has_add_permission=has_add_permission,
                                      create_by=user_id, update_by=user_id)

    def create(self, request, *args, **kwargs):
        role_name = request.data.get('role_name')
        if not role_name:
            raise ValidationError({'role_name': '角色名称不能为空'})
        if Role.objects.all().filter(name=role_name):
            raise ValidationError({'msg': '角色名已存在'})
        role = Role.objects.create(name=role_name, create_by=self.request.user, update_by=self.request.user)
        for role_permission in request.data.get('items') or []:
            self._create_role_permission(role_permission['has_permission'],
                                         role.id, role_permission['id'],
                                         role_permission['has_read_permission'],
                                         role_permission['has_edit_permission'],
                                         role_permission['has_add_permission'],
                                         role_permission['has_delete_permission'],
                                         self.request.user)
            for children_role_permission in role_permission['children']:
                self._create_role_permission(children_role_permission['has_permission'], role.id,
                                             children_role_permission['id'],
                                             children_role_permission['has_read_permission'],
                                             children_role_permission['has_edit_permission'],
                                             children_role_permission['has_add_permission'],
                                             children_role_permission['has_delete_permission'],
                                             self.request.user)

        return Response({'data': role.id}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        role_obj = Role.objects.all().filter(id=self.kwargs.get('pk')).first()
        if role_obj is None:
            return Response({'detail': '角色不存在'}, status=404)
        role_name = request.data.get('role_name')
        if not role_name:
            raise ValidationError({'role_name': '角色名称不能为空'})
        if Role.objects.all().filter(name=role_name) and role_obj.name != role_name:
            raise ValidationError({'msg': '角色名已存在'})
        role_obj.name = role_name
        role_obj.update_by = self.request.user
        role_obj.save()
        for role_permission in request.data.get('items') or []:
            self._update_role_permission(role_permission, self.request.user)
            for children_role_permission in role_permission['children']:
                self._update_role_permission(children_role_permission, self.request.user)

        return Response({'data': role_obj.id}, status=status.HTTP_201_CREATED)


class RoleViewSet(BaseModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = RoleFilter

    @staticmethod
    def _get_permissions(role_id, is_add):
        path_permissions = {}
        permissions = list(Permission.objects.all().filter(is_delete=False).values())
        permissions.sort(key=lambda x: x['level'])
        results = {}
        for permission_obj in permissions:
            path_permissions[permission_obj['path']] = permission_obj['id']
            if role_id:
                role_permission_obj = RolePermission.objects.all().filter(role=role_id, permission=permission_obj['id'])
                if not role_permission_obj:
                    permission_obj['has_permission'] = False
                    permission_obj['has_read_permission'] = False
                    permission_obj['has_edit_permission'] = False
                    permission_obj['has_add_permission'] = False
                    permission_obj['has_delete_permission'] = False
                else:
                    role_permission_obj = role_permission_obj[0]
                    if not role_permission_obj.has_permission and not is_add:
                        continue
                    permission_obj['role_permission_id'] = role_permission_obj.id
                    permission_obj['has_permission'] = role_permission_obj.has_permission
                    permission_obj['has_read_permission'] = role_permission_obj.has_read_permission
                    permission_obj['has_edit_permission'] = role_permission_obj.has_edit_permission
                    permission_obj['has_add_permission'] = role_permission_obj.has_add_permission
                    permission_obj['has_delete_permission'] = role_permission_obj.has_delete_permission
                if permission_obj['level'] == 1:
                    results[permission_obj['id']] = permission_obj
                    results[permission_obj['id']]['children'] = []
                else:
                    results[permission_obj['parent']]['children'].append(permission_obj)
            # 项目创建者或者超级管理员有全部角色
            else:
                permission_obj['has_permission'] = True
                permission_obj['has_read_permission'] = True
                permission_obj['has_edit_permission'] = True
                permission_obj['has_add_permission'] = True
                permission_obj['has_delete_permission'] = True
                if permission_obj['level'] == 1:
                    results[permission_obj['id']] = permission_obj
                    results[permission_obj['id']]['children'] = []
                else:
                    results[permission_obj['parent']]['children'].append(permission_obj)
        return results, path_permissions

    def retrieve(self, request, *args, **kwargs):
        role_id = int(self.kwargs.get('pk'))
        project_id = self.request.query_params.get('project_id')
        is_add = self.request.query_params.get('is_add', True)
        is_add = False if is_add == 'false' else True
        all_permissions, path_permissions = self._get_permissions(role_id, is_add)
        
        # 当 role_id 为 0 或空时，直接返回权限信息，不查询角色
        if not role_id:
            user = request.user
            if user.is_superuser:
                return Response(status=200, data={'role_permissions': all_permissions.values(),
                                                  'pathPermissions': path_permissions})
            if project_id:
                project_obj = Project.objects.all().get(id=project_id)
                if project_obj.create_by_id == user.id:
                    return Response(status=200, data={'role_permissions': all_permissions.values(),
                                                      'pathPermissions': path_permissions})
            return Response(status=403, data={'error': '您没有权限查看项目权限'})
        else:
            # 正常查询角色信息
            response = super().retrieve(request, *args, **kwargs)
            response.data['role_permissions'] = all_permissions.values()
            response.data['pathPermissions'] = path_permissions
            return response


class PermissionView(BaseModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = PermissionFilter

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if request.query_params.get('back_list'):
            return response
        response.data['results'].sort(key=lambda x: x['level'])
        results = {}
        for permission_obj in response.data['results']:
            permission_obj['has_permission'] = False
            permission_obj['has_read_permission'] = False
            permission_obj['has_edit_permission'] = False
            permission_obj['has_add_permission'] = False
            permission_obj['has_delete_permission'] = False
            if permission_obj['level'] == 1:
                results[permission_obj['id']] = permission_obj
                results[permission_obj['id']]['children'] = []
            else:
                results[permission_obj['parent']]['children'].append(permission_obj)
        response.data = results.values()
        return response


@api_view(['POST'])
def modify_pwd(request: Request):
    """修改密码。

    安全约束（此前任何人登录后都能改任意账号的密码，属于 P0 越权）：
    1. 普通用户只能改自己的密码，且必须校验原密码；
    2. 超级管理员可以改他人密码，无需原密码；
    3. 目标用户不存在 / 参数缺失时返回 400，不再抛 500。
    """
    user_id = request.data.get('id')
    password = request.data.get('password')
    password_confirm = request.data.get('password_confirm')
    old_password = request.data.get('old_password')

    if not user_id:
        return Response(data={'id': ['缺少用户ID']}, status=400)

    if not password:
        return Response(data={'password': ['新密码不能为空']}, status=400)

    if password != password_confirm:
        return Response(data={'password': ['密码和确认密码不一致']}, status=400)

    try:
        target_user = User.objects.get(id=user_id)
    except (User.DoesNotExist, ValueError, TypeError):
        return Response(data={'id': ['用户不存在']}, status=400)

    is_self = request.user and request.user.is_authenticated and request.user.id == target_user.id
    is_superuser = bool(request.user and request.user.is_authenticated and request.user.is_superuser)

    if not (is_self or is_superuser):
        return Response(data={'detail': '没有权限修改该用户的密码'}, status=403)

    if is_self and not is_superuser:
        if not old_password:
            return Response(data={'old_password': ['修改自己的密码必须填写原密码']}, status=400)
        if not target_user.check_password(old_password):
            return Response(data={'old_password': ['原密码不正确']}, status=400)

    target_user.set_password(password)
    target_user.save()

    return Response(data='成功', status=200)


@api_view(['GET'])
def get_usernames(request: Request):
    """获取所有用户的id和username列表"""
    # 获取所有用户
    users = User.objects.all()

    # 使用你的序列化器
    serializer = UserNameSerializers(users, many=True)

    return Response(data=serializer.data, status=200)


@api_view(['GET'])
@authentication_classes([])  # 明确设置空认证类，禁用所有认证
def get_online_users_count(request: Request):
    """
    获取平台在线用户数
    
    根据用户表的is_active字段判断在线状态
    此接口无需认证
    """
    # 统计活跃用户数量
    online_users_count = User.objects.filter(is_online=True, is_delete=False).count()
    
    return Response({
        'count': online_users_count,
    }, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request: Request):
    """
    用户登出接口 - 适用于 JWT 认证
    
    注意：JWT 是无状态的，真正的登出需要在客户端删除 token
    这里主要执行一些服务器端的清理操作
    """
    user = request.user
    
    # 1. 设置用户为离线状态
    user.is_online = False
    user.save()
    
    # 返回登出成功信息
    return Response({
        'message': '登出成功，请在客户端删除 JWT token',
        'success': True,
        'user_id': user.id,
        'username': user.username
    }, status=200)


class UserRegister(BaseCreateModelViewSet):
    serializer_class = UserSerializers
    queryset = User.objects.all()
    authentication_classes = []  # 无需认证
    permission_classes = [AllowAny]  # 允许任何人访问
    
    def create(self, request, *args, **kwargs):
        """
        用户注册接口
        
        请求参数:
        {
            "username": "用户名",
            "password": "密码",
            "password_confirm": "确认密码",
            "email": "邮箱（可选）"
        }
        """
        # 获取请求数据
        username = request.data.get('username')
        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')

        # 验证必填字段
        if not username or not password or not password_confirm:
            return Response({
                'success': False,
                'message': '用户名、密码和确认密码为必填项'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证密码一致性
        if password != password_confirm:
            return Response({
                'success': False,
                'message': '密码和确认密码不一致'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证密码长度
        if len(password) < 6:
            return Response({
                'success': False,
                'message': '密码长度不能少于6位'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username, is_delete=False).exists():
            return Response({
                'success': False,
                'message': '用户名已存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 创建用户
            user_data = {
                'username': username,
                'password': password,
                'password_confirm': password_confirm,
            }
            
            # 使用序列化器创建用户
            serializer = self.get_serializer(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                
                # 返回注册成功信息
                return Response({
                    'success': True,
                    'message': '注册成功',
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email
                }, status=status.HTTP_201_CREATED)
            else:
                # 序列化器验证失败
                return Response({
                    'success': False,
                    'message': '注册失败',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            # 捕获其他异常
            return Response({
                'success': False,
                'message': f'注册失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


