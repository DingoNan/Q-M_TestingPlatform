"""URL前缀到模型的映射注册表，用于中间件自动识别操作目标模型"""

# URL前缀 → 'app_label.ModelName'
# 注意：messages 应用的 label 是 app_messages
AUDIT_MODEL_REGISTRY = {
    # users app (URL prefix: user/)
    'user/users': 'users.User',
    'user/role': 'users.Role',
    'user/role_permission': 'users.RolePermission',
    'user/permission': 'users.Permission',
    'user/group': 'users.Group',
    'user/navigation': 'users.Navigation',
    # projects app
    'projects': 'projects.Project',
    'project_members': 'projects.ProjectMember',
    'project_appeal': 'projects.ProjectAppeal',
    'ai_model_setting': 'projects.AiConfig',
    'project_msg_push': 'projects.ProjectMsgPush',
    # envs app
    'env/env': 'envs.Env',
    'env/global': 'envs.GlobalParams',
    'env/params': 'envs.EnvGlobalParams',
    'env/service': 'envs.Service',
    'env/db': 'envs.Db',
    'env/plant': 'envs.Plant',
    'env/module': 'envs.Module',
    'env/service_module': 'envs.ServiceModule',
    'env/page': 'envs.Page',
    'env/header': 'envs.Headers',
    'env/cookie': 'envs.Cookies',
    'env/env_service': 'envs.EnvService',
    'env/env_db': 'envs.EnvDb',
    'env/env_plant': 'envs.EnvPlant',
    'env/web_executor': 'envs.EnvWebExecutor',
    'env/app_executor': 'envs.EnvAppExecutor',
    # interfaces app
    'interface/api': 'interfaces.Api',
    'interface/mock': 'interfaces.ApiMock',
    # tests app
    'test/case': 'tests.Case',
    'test/func_case': 'tests.FuncCase',
    'test/step': 'tests.Step',
    'test/tag': 'tests.Tag',
    'test/casesteps': 'tests.CaseSteps',
    'test/logs': 'tests.CaseRunLog',
    # elements app
    'element': 'elements.Element',
    # scripts app
    'script/python': 'scripts.PythonScript',
    'script/enum': 'scripts.EnumScript',
    'script/file': 'scripts.File',
    # suites app
    'suite': 'suites.Suite',
    'plan': 'suites.TestPlan',
    'task': 'suites.CrontabTask',
    'plan_case': 'suites.TestPlanFuncCase',
    'plan_case_comment': 'suites.TestPlanFuncCaseComment',
    # reports app
    'report/func': 'reports.Report',
    'report/locust': 'reports.LocustReport',
    # defects app
    'defect/defect': 'defects.Defect',
    'defect/defect_comment': 'defects.DefectComment',
    # messages app (label=app_messages)
    'message': 'app_messages.Message',
}

# 复合ID模型：URL使用复合对象ID（如步骤 case_id_step_id_case_step_id），
# 真实主键所在段索引（从0开始），用于 before_data 捕获与版本回退时定位对象
COMPOSITE_PK_SEGMENT = {
    'test/step': 1,  # 4_7_11 → step_id 是第2段（索引1）
}

# 模块中文名映射 — 与前端菜单二级模块名称对齐
MODULE_CN = {
    'users': '用户列表', 'role': '角色列表', 'role_permission': '角色权限',
    'permission': '权限列表', 'check_permission': '权限列表', 'group': '分组', 'navigation': '导航',
    'projects': '项目管理', 'project_members': '项目成员',
    'project_appeal': '项目申请', 'ai_model_setting': 'AI配置',
    'project_msg_push': '消息推送',
    'env': '环境配置', 'global': '全局变量', 'params': '环境变量',
    'service': '服务配置', 'db': '数据库配置', 'plant': '产品配置',
    'env_service': '服务域名配置', 'env_db': '数据库环境配置', 'env_plant': '产品域名配置',
    'web_executor': '浏览器集群配置', 'app_executor': '手机设备配置',
    'module': '模块', 'page': '页面', 'header': '请求头',
    'cookie': '会话', 'api': '接口管理', 'mock': 'Mock',
    'case': '脚本用例', 'func_case': '功能用例', 'step': '步骤管理',
    'tag': '标签管理', 'element': '元素配置', 'python': '用户函数',
    'enum': '常量配置', 'file': '文件管理', 'suite': '套件管理',
    'plan': '测试计划', 'task': '定时任务',
    'report': '报告', 'message': '消息',
    'defect': '缺陷列表', 'defect_comment': '缺陷评论',
}


def get_model_for_url(url_prefix):
    """根据URL前缀获取模型类"""
    from django.apps import apps
    model_path = AUDIT_MODEL_REGISTRY.get(url_prefix)
    if not model_path:
        return None
    app_label, model_name = model_path.split('.')
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


def get_module_cn(segment):
    """获取模块中文名"""
    return MODULE_CN.get(segment, segment)
