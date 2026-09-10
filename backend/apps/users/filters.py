from django_filters import rest_framework
from apps.users.models import Permission, Role, User, Group, Navigation


class PermissionFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    path = rest_framework.CharFilter(lookup_expr='contains')
    icon = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = Permission
        fields = '__all__'


class RoleFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = Role
        fields = '__all__'


class GroupFilter(rest_framework.FilterSet):
    # name = rest_framework.CharFilter(lookup_expr='contains')
    ids = rest_framework.BaseInFilter(field_name='id', lookup_expr='in')

    class Meta:
        model = Group
        fields = ['ids']


class NavigationFilter(rest_framework.FilterSet):

    class Meta:
        model = Navigation
        fields = '__all__'


class UserFilter(rest_framework.FilterSet):
    username = rest_framework.CharFilter(lookup_expr='contains')
    email = rest_framework.CharFilter(lookup_expr='contains')
    role = rest_framework.CharFilter(lookup_expr='contains', field_name='role__name')

    class Meta:
        model = User
        fields = '__all__'
