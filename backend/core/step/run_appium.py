import json
import inspect

from appium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from apps.elements.serializers import ElementSerializers
from apps.envs.models import EnvPlant, EnvAppExecutor
from apps.elements.models import Element
import core.com.faker as sys_function
from core.com.common import formatter_log
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from core.com.common import get_function_params, func_list_to_dict
from core.com.check import loop_assert_by_check_list
from core.step.run_python_script import exec_and_return
from core.com.step_model import action_group, AppiumStepType, AppiumStepTypeName


class AppiumBaseAction:

    def __init__(self, case_params: object, case_logs_obj: object, package_name, activity_name, executor_id):

        self.package_name = package_name
        self.activity_name = activity_name

        app_obj = EnvAppExecutor.objects.get(id=executor_id)
        if app_obj.platform_name == EnvAppExecutor.DeviceType.Android:
            self.platform_name = 'Android'
            self.isAndroid = True
            self.device_driver = 'UiAutomator2'
        else:
            self.isAndroid = False
            self.platform_name = 'iOS'
            self.device_driver = 'xcuitest'
        desired_caps = {
            "platformName": self.platform_name,
            "appium:automationName": self.device_driver,
            "appium:appPackage": self.package_name,
            "appium:appActivity": self.activity_name,
            "appium:noReset": True,
            "appium:forceAppLaunch": True,
            # "chromedriverExecutable": 'D:\PythonProject\AutoTest\chromedriver.exe'
        }
        if case_logs_obj.report is None:
            desired_caps['appium:udid'] = app_obj.device_name
        self.device_options = UiAutomator2Options().load_capabilities(desired_caps) if app_obj.platform_name == 1 \
            else XCUITestOptions().load_capabilities(desired_caps)
        self.driver = webdriver.Remote(command_executor=app_obj.hub_url, options=self.device_options)
        self.case_params = case_params
        self.case_logs_obj = case_logs_obj

    @property
    def _log(self):
        return self.case_logs_obj.logs[-1]['logs']

    def _quit(self):
        self.__terminate_app()
        self.driver.quit()

    def __loc(self, obj):
        if self.isAndroid:
            loc_method = obj['by']
            loc_value = obj['value']
        else:
            loc_method = obj['ios_by']
            loc_value = obj['ios_value']
        return loc_method, loc_value

    def wait_element_located(self, obj: ElementSerializers, timeout: int = 5):
        """
        等待元素被加载到Dom树中，并且可见
        obj: 元素对象, 必填
        timeout: 等待元素出现超时时间, int, 必填，默认5s
        return None
        """

        WebDriverWait(self.driver, timeout, 0.5).until(
            expected_conditions.visibility_of_element_located((obj['by'], obj['value'])))

    def find_element(self, obj: ElementSerializers, timeout: int = 5):
        """
        查找元素
        obj: 元素对象, 必填
        timeout: 查找元素超时时间, int, 必填，默认5s
        return obj 元素对象
        """
        app_loc = obj['android'] if self.isAndroid else obj['ios']
        # 兼容旧版本：曾用列表存储多条定位，取第一条
        if isinstance(app_loc, list):
            app_loc = app_loc[0] if app_loc else {}
        try:
            self.wait_element_located(app_loc, timeout)
            return self.driver.find_element(app_loc['by'], app_loc['value'])
        except TimeoutException:
            base64_str = 'data:image/png;base64,' + self.driver.get_screenshot_as_base64()
            self._log.append({'title': formatter_log('ERROR', f'查找元素失败'), 'value': f'', 'uri': base64_str})
            raise

    @action_group(AppiumStepType.ElementAction, AppiumStepTypeName.ElementAction)
    def click(self, obj: ElementSerializers, timeout: int = 5):
        """
        点击元素
        obj: 元素对象, 必填
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        self.find_element(obj, timeout).click()
        self._log.append({'title': formatter_log('INFO', '点击元素'), 'value': f'鼠标点击成功'})

    @action_group(AppiumStepType.ElementAction, AppiumStepTypeName.ElementAction)
    def send_keys(self, obj: ElementSerializers, value: str, timeout: int = 5):
        """
        输入内容
        obj: 元素对象, 必填
        value: 输入得内容， 必填
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        self.find_element(obj, timeout).send_keys(value)
        self._log.append({'title': formatter_log('INFO', '输入内容'), 'value': f'{value}'})

    @action_group(AppiumStepType.ElementAction, AppiumStepTypeName.ElementAction)
    def clear(self, obj: ElementSerializers, timeout: int = 5):
        """
        清空元素的文本内容
        obj: 元素对象, 必填
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: None
        """
        self.find_element(obj, timeout).clear()
        self._log.append({'title': formatter_log('INFO', '清空内容'), 'value': f'清空内容成功'})

    @action_group(AppiumStepType.ElementAction, AppiumStepTypeName.ElementAction)
    def get_text(self, obj: ElementSerializers, timeout: int = 5):
        """
        获取文本
        obj: 元素对象, 必填
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: str 文本内容
        """
        text = self.find_element(obj, timeout).text
        self._log.append({'title': formatter_log('INFO', '获取文本'), 'value': f'{text}'})
        return text

    @action_group(AppiumStepType.ElementAction, AppiumStepTypeName.ElementAction)
    def get_page_source(self):
        """
        获取页面源码
        return: str 返回当前页面的html内容
        """
        page_source = self.driver.page_source
        self._log.append({'title': formatter_log('INFO', '获取页面源码'), 'value': f'{page_source}'})

    @action_group(AppiumStepType.ElementAction, AppiumStepTypeName.ElementAction)
    def get_tag_name(self, obj: ElementSerializers, timeout: int = 5):
        """
        获取标签名
        obj: 元素对象, 必填
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: str 元素标签名
        """
        tag_name = self.find_element(obj, timeout).tag_name
        self._log.append({'title': formatter_log('INFO', '获取标签名'), 'value': f'{tag_name}'})
        return tag_name

    @action_group(AppiumStepType.ElementAction, AppiumStepTypeName.ElementAction)
    def get_attribute(self, obj: ElementSerializers, name: str, timeout: int = 5):
        """
        获取属性
        obj: 元素对象, 必填
        name: 元素属性名称, 必填
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: str 元素属性值
        """
        attr_value = self.find_element(obj, timeout).get_attribute(name)
        self._log.append({'title': formatter_log('INFO', '获取属性'), 'value': f'{attr_value}'})
        return attr_value

    @action_group(AppiumStepType.ElementAction, AppiumStepTypeName.ElementAction)
    def get_css_property(self, obj: ElementSerializers, name: str, timeout: int = 5):
        """
        获取CSS属性
        obj: 元素对象, 必填
        name: CSS属性名称, 必填
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: str CSS属性值
        """
        attr_value = self.find_element(obj, timeout).value_of_css_property(name)
        self._log.append({'title': formatter_log('INFO', '获取CSS属性'), 'value': f'{attr_value}'})
        return attr_value

    @action_group(AppiumStepType.ElementAction, AppiumStepTypeName.ElementAction)
    def scroll_into_view(self, obj: ElementSerializers, timeout: int = 5):
        """
        将元素移动到屏幕可见区域
        obj: 元素对象, 必填
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        self.driver.execute_script("arguments[0].scrollIntoView();", self.find_element(obj, timeout))
        self._log.append({'title': formatter_log('INFO', '将元素移动到屏幕可见区域'), 'value': '将元素移动到屏幕可见区域成功'})

    @action_group(AppiumStepType.ElementAction, AppiumStepTypeName.ElementAction)
    def is_displayed(self, obj: ElementSerializers, timeout: int = 5):
        """
        元素是否显示
        obj: 元素对象, 必填
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: bool True 显示, False 不显示
        """
        result = self.find_element(obj, timeout).is_displayed()
        self._log.append({'title': formatter_log('INFO', '元素是否显示'), 'value': f'{result}'})
        return result

    @action_group(AppiumStepType.ElementAction, AppiumStepTypeName.ElementAction)
    def is_enabled(self, obj: ElementSerializers, timeout: int = 5):
        """
        元素是否可用
        obj: 元素对象, 必填
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: bool True 可用, False 不可用
        """
        result = self.find_element(obj, timeout).is_enabled()
        self._log.append({'title': formatter_log('INFO', '获取CSS属性'), 'value': f'{result}'})
        return attr_value

    @action_group(AppiumStepType.ElementAction, AppiumStepTypeName.ElementAction)
    def is_selected(self, obj: ElementSerializers, timeout: int = 5):
        """
        元素是否选中
        obj: 元素对象, 必填
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: bool True 选中, False 非选中
        """
        result = self.find_element(obj, timeout).is_selected()
        self._log.append({'title': formatter_log('INFO', '元素是否选中'), 'value': f'{result}'})
        return attr_value

    @action_group(AppiumStepType.Screenshots, AppiumStepTypeName.Screenshots)
    def screenshot(self):
        """
        屏幕截图
        return str
        """
        base64_str = 'data:image/png;base64,' + self.driver.get_screenshot_as_base64()
        self._log.append({'title': formatter_log('INFO', '屏幕截图'), 'value': '', 'uri': base64_str})

    def __terminate_app(self):
        """
        关闭app
        obj: 元素对象, 必填
        timeout: 超时时间, int, 非必填，默认5s
        return: None
        """
        self.driver.terminate_app(self.package_name)

    # 手机操作
    @action_group(AppiumStepType.PhoneAction, AppiumStepTypeName.PhoneAction)
    def back(self):
        """
        返回上一页
        return: None
        """
        self.driver.back()
        self._log.append({'title': formatter_log('INFO', '返回上一页'), 'value': '成功返回上一页'})

    @action_group(AppiumStepType.PhoneAction, AppiumStepTypeName.PhoneAction)
    def forward(self):
        """
        返回下一页
        return: None
        """
        self.driver.forward()
        self._log.append({'title': formatter_log('INFO', '返回下一页'), 'value': '成功返回下一页'})

    @action_group(AppiumStepType.PhoneAction, AppiumStepTypeName.PhoneAction)
    def swipe_down(self, start_x: float = 0.5, start_y: float = 0.7, end_x: float = 0.5, end_y: float = 0.3,
                   duration_ms: int = 1000):
        """
        向下滑动
        :start_x 屏幕宽度的比例 0-1
        :start_y 屏幕高度的比例 0-1
        :end_x 屏幕宽度的比例 0-1
        :end_y 屏幕高度的比例 0-1
        :duration_ms: 滑动持续时间（毫秒），时间越长滑动越慢
        """
        # 获取屏幕尺寸
        window_size = self.driver.get_window_size()
        width = window_size['width']
        height = window_size['height']

        # 计算起点和终点坐标
        # 起点：屏幕水平中点，垂直方向70%位置（靠下）
        # 终点：屏幕水平中点，垂直方向30%位置（靠上）
        start_x = width * start_x
        start_y = height * start_y
        end_x = width * end_x
        end_y = height * end_y

        # 执行滑动
        self.driver.swipe(start_x, start_y, end_x, end_y, duration_ms)
        self._log.append({'title': formatter_log('INFO', '向下滑动'), 'value': '成功向下滑动'})

    @action_group(AppiumStepType.PhoneAction, AppiumStepTypeName.PhoneAction)
    def swipe_up(self, start_x: float = 0.5, start_y: float = 0.3, end_x: float = 0.5, end_y: float = 0.7,
                 duration_ms: int = 1000):
        """
        向上滑动
        :start_x 屏幕宽度的比例 0-1
        :start_y 屏幕高度的比例 0-1
        :end_x 屏幕宽度的比例 0-1
        :end_y 屏幕高度的比例 0-1
        :duration_ms: 滑动持续时间（毫秒），时间越长滑动越慢
        """
        # 获取屏幕尺寸
        window_size = self.driver.get_window_size()
        width = window_size['width']
        height = window_size['height']

        # 计算起点和终点坐标
        # 起点：屏幕水平中点，垂直方向70%位置（靠下）
        # 终点：屏幕水平中点，垂直方向30%位置（靠上）
        start_x = width * start_x
        start_y = height * start_y
        end_x = width * end_x
        end_y = height * end_y

        # 执行滑动
        self.driver.swipe(start_x, start_y, end_x, end_y, duration_ms)
        self._log.append({'title': formatter_log('INFO', '向上滑动'), 'value': '成功向上滑动'})

    @action_group(AppiumStepType.PhoneAction, AppiumStepTypeName.PhoneAction)
    def swipe_left(self, start_x: float = 0.8, start_y: float = 0.5, end_x: float = 0.2, end_y: float = 0.5,
                   duration_ms: int = 800):
        """
        向左滑动
        :start_x 屏幕宽度的比例 0-1
        :start_y 屏幕高度的比例 0-1
        :end_x 屏幕宽度的比例 0-1
        :end_y 屏幕高度的比例 0-1
        :duration_ms 滑动持续时间（毫秒），时间越长滑动越慢
        """
        # 获取屏幕尺寸
        window_size = self.driver.get_window_size()
        width = window_size['width']
        height = window_size['height']

        start_x = width * start_x
        start_y = height * start_y
        end_x = width * end_x
        end_y = height * end_y

        # 执行滑动
        self.driver.swipe(start_x, start_y, end_x, end_y, duration_ms)
        self._log.append({'title': formatter_log('INFO', '向左滑动'), 'value': '成功向左滑动'})

    @action_group(AppiumStepType.PhoneAction, AppiumStepTypeName.PhoneAction)
    def swipe_right(self, start_x: float = 0.2, start_y: float = 0.5, end_x: float = 0.8, end_y: float = 0.5,
                    duration_ms: int = 800):
        """
        向右滑动
        :start_x 屏幕宽度的比例 0-1
        :start_y 屏幕高度的比例 0-1
        :end_x 屏幕宽度的比例 0-1
        :end_y 屏幕高度的比例 0-1
        :duration_ms 滑动持续时间（毫秒），时间越长滑动越慢
        """
        # 获取屏幕尺寸
        window_size = self.driver.get_window_size()
        width = window_size['width']
        height = window_size['height']

        # 计算起点和终点坐标
        # 起点：屏幕水平方向80%位置，垂直中点（靠右）
        # 终点：屏幕水平方向20%位置，垂直中点（靠左）
        start_x = width * start_x
        start_y = height * start_y
        end_x = width * end_x
        end_y = height * end_y

        # 执行滑动
        self.driver.swipe(start_x, start_y, end_x, end_y, duration_ms)
        self._log.append({'title': formatter_log('INFO', '向右滑动'), 'value': '成功向右滑动'})

    # 上下文操作
    @action_group(AppiumStepType.Content, AppiumStepTypeName.Content)
    def get_contexts(self):
        """
        获取所有上下文
        return: 所有上下文列表
        """
        contexts = self.driver.contexts
        _contexts = json.dumps(contexts)
        self._log.append({'title': formatter_log('INFO', '获取上下文'), 'value': f'{_contexts}'})

    @action_group(AppiumStepType.Content, AppiumStepTypeName.Content)
    def get_current_context(self):
        """
        获取当前上下文
        return: 当前所属上下文
        """
        context = self.driver.current_context
        self._log.append({'title': formatter_log('INFO', '获取当前上下文'), 'value': f'{context}'})

    @action_group(AppiumStepType.Content, AppiumStepTypeName.Content)
    def switch_to_context(self, content_name: str):
        """
        切换上下文
        :content_name: 上下文名称
        return: 上下文列表
        """
        self.driver.switch_to.context(content_name)
        self._log.append({'title': formatter_log('INFO', '切换上下文'), 'value': f'{content_name}'})

    # 弹窗操作
    @action_group(AppiumStepType.AlertHandling, AppiumStepTypeName.AlertHandling)
    def get_alert_text(self, timeout: int = 5):
        """
        获取弹窗文本内容
        timeout: 等待弹窗出现超时时间, int, 必填，默认5s
        return: str 弹框的文本内容
        """
        WebDriverWait(self.driver, timeout, 0.5).until(expected_conditions.alert_is_present())
        alter = self.driver.switch_to.alert
        text = alter.text
        self._log.append({'title': formatter_log('INFO', '获取弹窗文本内容'), 'value': f'{text}'})
        return text

    @action_group(AppiumStepType.AlertHandling, AppiumStepTypeName.AlertHandling)
    def alert_accept(self, timeout: int = 5):
        """
        点击弹窗中的接受/确定按钮
        timeout: 等待弹窗出现超时时间, int, 必填，默认5s
        return: None
        """
        WebDriverWait(self.driver, timeout, 0.5).until(expected_conditions.alert_is_present())
        alter = self.driver.switch_to.alert
        alter.accept()
        self._log.append({'title': formatter_log('INFO', '点击弹窗中的接受/确定按钮'), 'value': '点击弹窗中的接受/确定按钮成功'})

    @action_group(AppiumStepType.AlertHandling, AppiumStepTypeName.AlertHandling)
    def alert_dismiss(self, timeout: int = 5):
        """
        点击弹框的取消/拒绝按钮
        timeout: 等待弹窗出现超时时间, int, 必填，默认5s
        return: None
        """
        WebDriverWait(self.driver, timeout, 0.5).until(expected_conditions.alert_is_present())
        alter = self.driver.switch_to.alert
        alter.dismiss()
        self._log.append({'title': formatter_log('INFO', '点击弹框的取消/拒绝按钮'), 'value': '点击弹框的取消/拒绝按钮成功'})

    @action_group(AppiumStepType.AlertHandling, AppiumStepTypeName.AlertHandling)
    def alert_send_keys(self, value: str, timeout: int = 5):
        """
        在弹框中输入内容
        value: 输入的内容
        timeout: 等待弹窗出现超时时间, int, 必填，默认5s
        return: None
        """
        WebDriverWait(self.driver, timeout, 0.5).until(expected_conditions.alert_is_present())
        alter = self.driver.switch_to.alert
        alter.send_keys(value)
        self._log.append({'title': formatter_log('INFO', '在弹框中输入内容'), 'value': f'{value}'})


appium_actions = [{
    'id': key,
    'script': inspect.getsource(value),
    'params': get_function_params(value),
    'name': [new_str.strip() for new_str in value.__doc__.strip().split('\n')][0],
    'group': value.__dict__.get('group_id'),
    'group_name': value.__dict__.get('group_name'),
    }
    for key, value in AppiumBaseAction.__dict__.items()
    if not key.startswith('_')]


appium_func_map = {key: value for key, value in AppiumBaseAction.__dict__.items()
                   if not key.startswith('_')}

appium_func_doc = {key: [new_str.strip() for new_str in value.__doc__.strip().split('\n')]
                   for key, value in AppiumBaseAction.__dict__.items()
                   if not key.startswith('_')}


def get_obj_params_value(element_id, env_id):
    data = ElementSerializers(Element.objects.all().get(id=element_id, is_delete=False)).data
    env_plant_obj = EnvPlant.objects.all().get(env=env_id, plant=data.get('plant_id'), is_delete=False)
    return env_plant_obj.package, env_plant_obj.activity, data


def run_step_appium(manager_obj, env_id, step, case_params, case_logs_obj, run_times, run_element):
    step_id = step["case_step_id"]
    plant_id = step['plant']
    env_plant_obj = EnvPlant.objects.all().get(env=env_id, plant=plant_id, is_delete=False)
    package_name = env_plant_obj.package
    activity_name = env_plant_obj.activity

    case_params.stepResponse[f'{step_id}']['runTimes'] = run_times
    case_params.stepResponse[f'{step_id}']['runElement'] = run_element
    keyword = step['keyword']
    func_params = func_list_to_dict(step['func_params'], {}, case_params, case_logs_obj)
    case_params.stepResponse[f'{step_id}']['funcParams'] = func_params

    if package_name not in manager_obj.driver_manager and package_name is not None:
        manager_obj.driver_manager[package_name] = AppiumBaseAction(case_params, case_logs_obj, package_name,
                                                                    activity_name, manager_obj.app_executor_id)
    exec_and_return(manager_obj, step['setup'], case_logs_obj, formatter_log, case_params, sys_function)
    return_value = appium_func_map[keyword](manager_obj.driver_manager[package_name], **func_params)
    case_params.stepResponse[f'{step_id}']['funcReturn'] = return_value
    exec_and_return(manager_obj, step['teardown'], case_logs_obj, formatter_log, case_params, sys_function)

    # 执行步骤的断言参数,如果步骤中有断言数据则忽略接口的断言数据
    loop_assert_by_check_list(step['check_params'], case_params, case_logs_obj)