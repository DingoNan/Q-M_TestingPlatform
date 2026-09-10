from functools import lru_cache

from django.db.models import Q
from django_filters import rest_framework
from apps.audit.models import AuditLog


# 自定义一级模块 → 二级模块映射（不在 Permission 菜单表中的模块分组）
CUSTOM_PARENT_MODULES = {
    '系统管理': ['用户列表', '权限列表', '角色列表'],
}

# 模块关联映射：查询某模块时同时包含其关联模块
# （如查询"服务配置"时同时返回"服务域名配置"记录）
MODULE_ASSOCIATIONS = {
    '服务配置': ['服务配置', '服务域名配置'],
    '产品配置': ['产品配置', '产品域名配置'],
    '数据库配置': ['数据库配置', '数据库环境配置'],
    '环境配置': ['环境配置', '请求头', '会话', '全局变量', '环境变量', '浏览器集群配置', '手机设备配置'],
    '脚本用例': ['脚本用例', '步骤管理'],
}


@lru_cache(maxsize=1)
def _get_parent_menu_children():
    """从 Permission 表读取真实菜单结构：{一级菜单名: [二级菜单名, ...]}"""
    try:
        from apps.users.models import Permission
        first_level = {
            p.id: p.name
            for p in Permission.objects.filter(level=1, is_delete=False).only('id', 'name')
        }
        result = {}
        for child in Permission.objects.filter(level=2, is_delete=False).only('id', 'name', 'parent'):
            parent_name = first_level.get(child.parent)
            if parent_name:
                result.setdefault(parent_name, []).append(child.name)
        return result
    except Exception:
        return {}


def _expand_module_value(value):
    """如果 value 命中一级菜单名（含自定义分组），展开为其下所有二级模块名列表；否则返回 [value]"""
    # 先检查自定义分组
    if value in CUSTOM_PARENT_MODULES:
        return CUSTOM_PARENT_MODULES[value]
    # 再查 Permission 菜单表
    mapping = _get_parent_menu_children()
    if value in mapping:
        return list(mapping[value])
    return [value]


class AuditLogFilter(rest_framework.FilterSet):
    """审计日志过滤器 — 支持按用户、操作类型、模块、项目、时间范围筛选"""
    username = rest_framework.CharFilter(lookup_expr='icontains')
    action = rest_framework.CharFilter(field_name='action', lookup_expr='exact')
    method = rest_framework.CharFilter(field_name='method', lookup_expr='exact')
    # 模块过滤：支持一级菜单名（自动展开为下属二级名 in 查询）和二级菜单名（icontains 模糊匹配）
    module = rest_framework.CharFilter(method='filter_module')
    path = rest_framework.CharFilter(lookup_expr='icontains')
    project = rest_framework.NumberFilter(field_name='project_id')
    status_code = rest_framework.NumberFilter(field_name='status_code')
    create_time_start = rest_framework.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_end = rest_framework.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = AuditLog
        fields = ['username', 'action', 'method', 'module', 'path',
                  'project', 'status_code', 'create_time_start', 'create_time_end']

    def filter_module(self, queryset, name, value):
        if not value:
            return queryset
        value = value.strip()
        # 关联模块：查询"服务配置"时同时包含"服务域名配置"等
        if value in MODULE_ASSOCIATIONS:
            return queryset.filter(module__in=MODULE_ASSOCIATIONS[value])
        modules = _expand_module_value(value)
        if len(modules) > 1:
            # 一级菜单：精确匹配下属二级模块名
            return queryset.filter(module__in=modules)
        # 二级菜单/自定义关键词：icontains 模糊匹配
        return queryset.filter(module__icontains=modules[0])
