from apps.users.models import User, Permission, RolePermission, Role


permissions = [
    {
        'name': '环境管理',
        'level': 1,
        'path': 'env',
        'icon': 'HelpFilled',
        'parent': 0,
        'children': [
            {
                'name': '环境配置',
                'level': 2,
                'path': '/env/env',
                'icon': 'Share',
                'parent': 1,
            },
            {
                'name': '服务配置',
                'level': 2,
                'path': '/env/service',
                'icon': 'SwitchFilled',
                'parent': 1,
            },
            {
                'name': '产品配置',
                'level': 2,
                'path': '/env/plant',
                'icon': 'Box',
                'parent': 1,
            },
            {
                'name': '数据库配置',
                'level': 2,
                'path': '/env/db',
                'icon': 'Setting',
                'parent': 1,
            },
        ]

    },
    {
        'name': '公共资源',
        'level': 1,
        'path': 'common',
        'icon': 'Reading',
        'parent': 0,
        'children': [
            {
                'name': '文件管理',
                'level': 2,
                'path': '/common/file',
                'icon': 'Files',
                'parent': 1,
            },
            {
                'name': '元素配置',
                'level': 2,
                'path': '/common/element',
                'icon': 'Grape',
                'parent': 1,
            },
            {
                'name': '常量配置',
                'level': 2,
                'path': '/common/enum',
                'icon': 'TakeawayBox',
                'parent': 1,
            },
            {
                'name': '用户函数',
                'level': 2,
                'path': '/common/python',
                'icon': 'EditPen',
                'parent': 1,
            },
            {
                'name': '步骤管理',
                'level': 2,
                'path': '/common/step',
                'icon': 'Connection',
                'parent': 1,
            },
        ]
    },
    {
        'name': '测试资产',
        'level': 1,
        'path': 'case',
        'icon': 'SetUp',
        'parent': 0,
        'children': [
            {
                'name': '向量智仓',
                'level': 2,
                'path': '/resource/knowledgeBase',
                'icon': 'Collection',
                'parent': 1,
            },
            {
                'name': '标签管理',
                'level': 2,
                'path': '/resource/tag',
                'icon': 'CollectionTag',
                'parent': 1,
            },
            {
                'name': '接口管理',
                'level': 2,
                'path': '/resource/api',
                'icon': 'Link',
                'parent': 1,
            },
            {
                'name': '功能用例',
                'level': 2,
                'path': '/resource/funcCase',
                'icon': 'Briefcase',
                'parent': 1,
            },
            {
                'name': '脚本用例',
                'level': 2,
                'path': '/resource/scriptCase',
                'icon': 'Coin',
                'parent': 1,
            },
        ]
    },
    {
        'name': '执行中心',
        'level': 1,
        'path': 'suite',
        'icon': 'Film',
        'parent': 0,
        'children': [
             {
                'name': '测试计划',
                'level': 2,
                'path': '/exec/plan',
                'icon': 'Filter',
                'parent': 1,
            },
            {
                'name': '套件管理',
                'level': 2,
                'path': '/exec/suite',
                'icon': 'Orange',
                'parent': 1,
            },
            {
                'name': '定时任务',
                'level': 2,
                'path': '/exec/task',
                'icon': 'AlarmClock',
                'parent': 1,
            },
        ]
    },
    {
        'name': '报告管理',
        'level': 1,
        'path': 'report',
        'icon': 'Histogram',
        'parent': 0,
        'children': [
            {
                'name': '日志列表',
                'level': 2,
                'path': '/report/log',
                'icon': 'VideoCameraFilled',
                'parent': 1
            },
            {
                'name': '功能报告',
                'level': 2,
                'path': '/report/list',
                'icon': 'PieChart',
                'parent': 1
             },
            {
                'name': '性能报告',
                'level': 2,
                'path': '/report/locust',
                'icon': 'TrendCharts',
                'parent': 1
             },
        ]
    },
    {
        'name': '缺陷管理',
        'level': 1,
        'path': 'defect',
        'icon': 'DataLine',
        'parent': 0,
        'children': [
            {
                'name': '缺陷列表',
                'level': 2,
                'path': '/defect/list',
                'icon': 'List',
                'parent': 1,
            },
        ]
    },
]


def create_permissions():
    if not Permission.objects.exists():
        permission_ids = []
        for permission_data in permissions:
            children = permission_data.pop('children')
            permission_obj = Permission.objects.create(**permission_data)
            permission_ids.append(permission_obj.id)
            for children_permission_data in children:
                children_permission_data['parent'] = permission_obj.id
                permission_children_obj = Permission.objects.create(**children_permission_data)
                permission_ids.append(permission_children_obj.id)
        return permission_ids


def create_role(permissions_ids):
    if not Role.objects.exists():
        all_obj = Role.objects.create(name='全部权限')
        read_obj = Role.objects.create(name='只读权限')
        for permission_id in permissions_ids:
            RolePermission.objects.create(role_id=all_obj.id, permission_id=permission_id, has_permission=True,
                                          has_read_permission=True, has_delete_permission=True, has_add_permission=True,
                                          has_edit_permission=True)
            RolePermission.objects.create(role_id=read_obj.id, permission_id=permission_id, has_permission=True,
                                          has_read_permission=True, has_delete_permission=False,
                                          has_add_permission=False,
                                          has_edit_permission=False)


def create_super_user():
    if not User.objects.exists():
        permissions_ids = create_permissions()
        create_role(permissions_ids)
        user_obj = User.objects.create_superuser(username='admin', password='admin', email='admin@qq.com')
        Permission.objects.update(create_by=user_obj.id, update_by=user_obj.id)
        Role.objects.update(create_by=user_obj.id, update_by=user_obj.id)
        User.objects.update(create_by=user_obj.id, update_by=user_obj.id)