from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from apps.users.models import User, Permission, RolePermission, Role, Group, Navigation
from apps.projects.models import ProjectMember, Project
from utils.base import BaseSerializer


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attr):
        data = super().validate(attr)
        self.user.last_login = timezone.now()
        self.user.is_online = True
        self.user.save(update_fields=['last_login', 'is_online'])
        data['token_refresh'] = data.pop('refresh')
        data['token_access'] = data.pop('access')
        data['user_id'] = self.user.id
        data['is_superuser'] = self.user.is_superuser
        data['user_name'] = self.user.username
        return data


class PermissionSerializer(BaseSerializer):

    class Meta:
        model = Permission
        fields = '__all__'


class NavigationSerializer(BaseSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Navigation
        fields = '__all__'


class GroupSerializer(BaseSerializer):
    navigation_set = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = '__all__'

    def get_navigation_set(self, obj):
        request = self.context.get('request')
        name = request.query_params.get('key')
        queryset = obj.navigation_set.all().filter(is_delete=False)

        # 获取查询参数
        if name:
            queryset = queryset.filter(name__icontains=name)

        return NavigationSerializer(queryset, many=True).data


class RoleSerializer(BaseSerializer):
    role_permissions = serializers.SerializerMethodField()
    link_num = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'create_time', 'update_time', 'permissions', 'role_permissions',
                  'update_by_name', 'create_by_name', 'link_num']

    def get_link_num(self, obj):
        # 返回角色关联的项目字典：项目名称 -> 对应的用户数
        
        # 获取角色关联的所有项目ID
        project_ids = ProjectMember.objects.filter(
            role_id=obj.id, 
            is_delete=False
        ).values_list('project_id', flat=True).distinct()
        
        # 构建项目字典：项目名称 -> 用户数
        project_dict = {}
        for project_id in project_ids:
            try:
                project = Project.objects.get(id=project_id, is_delete=False)
                # 统计该项目中使用该角色的用户数
                user_count = ProjectMember.objects.filter(
                    project_id=project_id, 
                    role_id=obj.id, 
                    is_delete=False
                ).count()
                project_dict[project.name] = user_count
            except Project.DoesNotExist:
                continue
        
        return project_dict

    def get_role_permissions(self, obj):
        role_permissions = obj.rolepermission_set.select_related('permission').all()
        permission_serializer = RolePermissionListSerializer(role_permissions, many=True)
        return permission_serializer.data


class RolePermissionListSerializer(BaseSerializer):
    permission = PermissionSerializer(read_only=True)

    class Meta:
        model = RolePermission
        fields = '__all__'


class RolePermissionSerializer(BaseSerializer):

    # permission_id = serializers.
    # role = RoleSerializer()

    class Meta:
        model = RolePermission
        fields = '__all__'


class MyTokenRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attr):
        data = super().validate(attr)
        data['token_access'] = data.pop('access')
        return data


class RoleNameSerializer(BaseSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserNameSerializers(BaseSerializer):

    class Meta:
        model = User
        fields = ['username', 'id']


class UserSerializers(BaseSerializer):
    password_confirm = serializers.CharField(label='确认密码', help_text='确认密码', write_only=True, required=True)
    last_login = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password_confirm', 'email', 'create_time', 'update_time',
                  'create_by_name', 'update_by_name', 'last_login', 'is_superuser']

    def get_role_info(self, obj):
        # 只有在详情请求时才序列化role_info
        request = self.context.get('request')
        if request and hasattr(request, 'parser_context') and request.parser_context.get('kwargs'):
            return RoleSerializer(obj.role).data
        # 列表请求时返回None，避免序列化开销
        return None

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')

        if password and password_confirm != password:
            raise ValidationError('密码和确认密码不一致')

        return attrs

    def create(self, validated_data):
        obj = super().create(validated_data)
        obj.set_password(obj.password)
        obj.save()
        return obj

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance