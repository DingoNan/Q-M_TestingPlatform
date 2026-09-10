from django_filters import rest_framework
from .models import Project, ProjectAppeal, ProjectMsgPush, ProjectMember
from django.db.models import Q


class ProjectFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    desc = rest_framework.CharFilter(lookup_expr='contains')
    user = rest_framework.CharFilter(method='filter_by_user')

    def filter_by_user(self, queryset, name, value):
        """
        根据用户过滤项目：返回用户创建的项目或用户是成员的项目
        如果用户是超级管理员，返回所有项目
        """
        if value:
            # 检查用户是否是超级管理员
            from apps.users.models import User
            try:
                user = User.objects.get(id=value)
                if user.is_superuser:
                    # 超级管理员返回所有项目
                    return queryset
            except User.DoesNotExist:
                pass
            
            # 普通用户：用户创建的项目 OR 用户是成员的项目
            queryset = queryset.filter(
                Q(create_by_id=value) |  # 用户创建的项目
                Q(members__user_id=value, members__is_delete=False)  # 用户是成员的项目
            ).distinct()
        return queryset

    class Meta:
        model = Project
        fields = ['name', 'desc', 'create_by', 'user']


class ProjectAppealFilter(rest_framework.FilterSet):
    project_name = rest_framework.CharFilter(lookup_expr='contains', field_name='project__name')
    project_create_by_id = rest_framework.CharFilter(field_name='project__create_by_id')
    project_create_by = rest_framework.CharFilter(field_name='project__create_by__username', lookup_expr='contains')

    class Meta:
        model = ProjectAppeal
        fields = ['project_name', 'user', 'project_create_by_id', 'user', 'project_create_by']


class ProjectMsgPushFilter(rest_framework.FilterSet):

    class Meta:
        model = ProjectMsgPush
        fields = ['is_active', 'project']


class ProjectMemberFilter(rest_framework.FilterSet):
    
    class Meta:
        model = ProjectMember
        fields = ['project', 'user', 'role']