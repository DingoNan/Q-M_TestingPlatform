import re
import inspect
import json
import core.com.faker as sys_function
from openai import OpenAI
from core.com.common import (
    formatter_log,
    get_function_params,
    func_list_to_dict,
    lis2dict,
)
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions
from apps.elements.serializers import ElementSerializers
from apps.envs.models import EnvPlant, EnvWebExecutor, Cookies
from apps.elements.models import Element
from core.com.step_model import action_group
from core.com.check import loop_assert_by_check_list
from core.step.run_python_script import exec_and_return
from core.com.step_model import SeleniumStepType, SeleniumStepTypeName
from utils.user_exception import EnvPlantNotExistException


def generate_loc_path_by_ai(desc, code, case_logs_obj):
    system_role_msg = '你是一个资深的自动化测试工程师,擅长网页HTML元素定位分析,请帮我分析网页并提取元素定位表达式,并以json格式返回'
    content = '请帮我根据下面的代码, 自动生成{desc}元素定位表达式并以json格式返回,格式为"by": "xpath", "value": ""\n{code}'.format(desc=desc, code=code)
    client = OpenAI(api_key='',
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    )

    completion = client.chat.completions.create(model="qwen-plus",
                                                messages=[
                                                    {"role": "system", "content": system_role_msg},
                                                    {"role": "user", "content": content}],
                                                response_format={"type": "json_object"})
    case_logs_obj.logs[-1]['logs'].append(
        {'title': formatter_log('INFO', 'AI原始返回'), 'value': completion.model_dump_json()})
    ai_response = json.loads(completion.model_dump_json())
    ai_loc_obj = json.loads(ai_response['choices'][0]['message']['content'])
    case_logs_obj.logs[-1]['logs'].append(
        {'title': formatter_log('INFO', 'AI自动识别元素'), 'value': f'AI生成定位表达式为：{str(ai_loc_obj)}'})
    return ai_loc_obj


class SeleniumBaseAction:

    def __init__(self, case_params: object, case_logs_obj: object, host, executor_id, plant_id, manager_obj, step_id):

        executor_obj = EnvWebExecutor.objects.get(id=executor_id)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument('--no-sandbox')
        # if executor_obj.type != EnvWebExecutor.ExecutorType.StandAlone:

        self.plant_id = plant_id
        self.step_id = step_id
        self.manager_obj = manager_obj
        self.driver = webdriver.Remote(command_executor=executor_obj.url, options=chrome_options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(7)
        self.case_params = case_params
        self.case_logs_obj = case_logs_obj
        self.host = host
        self.code = None

    @property
    def _log(self):
        return self.case_logs_obj.logs[-1]['logs']

    def __deal_cookies(self):
        if self.manager_obj.report_id:
            env_cookie_query = Cookies.objects.filter(plant=self.plant_id, is_delete=False, is_all_run=True)
        else:
            env_cookie_query = Cookies.objects.filter(plant=self.plant_id, is_delete=False, is_all_run=False,
                                                      create_by=self.manager_obj.user_id)
        env_cookie_obj = env_cookie_query[0] if env_cookie_query else None
        if env_cookie_obj:
            cookie_values, _ = lis2dict(env_cookie_obj.value, self.case_params, self.case_logs_obj, self.step_id, 'tmp')
            if env_cookie_obj.type == Cookies.CookieType.Cookie:
                self.driver.add_cookie(cookie_values)
            elif env_cookie_obj.type == Cookies.CookieType.Session:
                for session_key, session_value in cookie_values.items():
                    if isinstance(session_value, dict) or isinstance(session_value, list):
                        session_value = json.dumps(session_value)
                    self.driver.execute_script("sessionStorage.setItem(arguments[0], arguments[1]);",
                                               session_key, session_value)
            else:
                for local_key, local_value in cookie_values.items():
                    if isinstance(local_value, dict) or isinstance(local_value, list):
                        local_value = json.dumps(local_value)
                    self.driver.execute_script("localStorage.setItem(arguments[0], arguments[1]);",
                                               local_key, local_value)

    @staticmethod
    def __text(obj):
        return '【{}_{}_{}_{}】'.format(obj['plant_name'], obj['module_name'], obj['page_name'], obj['name'])

    # 浏览器操作
    @action_group(SeleniumStepType.DriverAction, SeleniumStepTypeName.DriverAction)
    def get(self, uri: str, need_add_cookie: bool = False):
        """
        打开浏览器并访问URL
        uri: 页面路径, 必填
        need_add_cookie: 是否需要添加Cookie，如果是,则从环境管理中的Cookie中自动添加Cookie绕过登录操作
        return: None
        """
        url = self.host + uri
        if need_add_cookie:
            self.driver.get(url)
            self.__deal_cookies()
        self.driver.get(url)
        self._log.append({'title': formatter_log('INFO', '打开浏览器并访问URL'), 'value': f'{url}'})

    @action_group(SeleniumStepType.DriverAction, SeleniumStepTypeName.DriverAction)
    def get_current_url(self):
        """
        获取当前页面URL
        return: str 当前页面的URL地址
        """
        url = self.driver.current_url
        self._log.append({'title': formatter_log('INFO', '获取当前页面URL'), 'value': f'{url}'})
        return url

    @action_group(SeleniumStepType.DriverAction, SeleniumStepTypeName.DriverAction)
    def get_title(self):
        """
        获取当前页面标题
        return: str 当前页面的标题
        """
        title = self.driver.title
        self._log.append({'title': formatter_log('INFO', '获取当前页面标题'), 'value': f'{title}'})
        return title

    @action_group(SeleniumStepType.DriverAction, SeleniumStepTypeName.DriverAction)
    def back(self):
        """
        返回浏览器上一页
        return: None
        """
        self.driver.back()
        self._log.append({'title': formatter_log('INFO', '返回浏览器上一页'), 'value': '成功返回浏览器上一页'})

    @action_group(SeleniumStepType.DriverAction, SeleniumStepTypeName.DriverAction)
    def forward(self):
        """
        返回浏览器下一页
        return: None
        """
        self.driver.forward()
        self._log.append({'title': formatter_log('INFO', '返回浏览器下一页'), 'value': '成功返回浏览器下一页'})

    @action_group(SeleniumStepType.DriverAction, SeleniumStepTypeName.DriverAction)
    def refresh(self):
        """
        刷新浏览器
        return: None
        """
        self.driver.refresh()
        self._log.append({'title': formatter_log('INFO', '刷新浏览器'), 'value': '成功刷新浏览器'})

    @action_group(SeleniumStepType.DriverAction, SeleniumStepTypeName.DriverAction)
    def get_page_source(self):
        """
        获取页面源码
        return: str 返回当前页面的html内容
        """
        page_source = self.driver.page_source
        self._log.append({'title': formatter_log('INFO', '获取页面源码'), 'value': f'{page_source}'})

    @action_group(SeleniumStepType.DriverAction, SeleniumStepTypeName.DriverAction)
    def maximize_window(self):
        """
        最大化窗口
        return: None
        """
        self.driver.maximize_window()
        self._log.append({'title': formatter_log('INFO', '最大化窗口'), 'value': f'成功最大化窗口'})

    @action_group(SeleniumStepType.DriverAction, SeleniumStepTypeName.DriverAction)
    def minimize_window(self):
        """
        最小化窗口
        return: None
        """
        self.driver.minimize_window()
        self._log.append({'title': formatter_log('INFO', '最小化窗口'), 'value': f'成功最小化窗口'})

    @action_group(SeleniumStepType.DriverAction, SeleniumStepTypeName.DriverAction)
    def full_screen_window(self):
        """
        全屏
        return: None
        """
        self.driver.fullscreen_window()
        self._log.append({'title': formatter_log('INFO', '全屏'), 'value': f'成功全屏'})

    def _quit(self):
        self.driver.quit()

    # 元素操作
    @action_group(SeleniumStepType.ElementAction, SeleniumStepTypeName.ElementAction)
    def click(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        点击元素
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                element.click()
        else:
            self.find_elements(obj, element_index, timeout).click()
        self._log.append({'title': formatter_log('INFO', '点击元素'), 'value': f'鼠 标点击成功'})

    @action_group(SeleniumStepType.ElementAction, SeleniumStepTypeName.ElementAction)
    def send_keys(self, obj: ElementSerializers, value: str, element_index: int =0, timeout: int = 5):
        """
        输入文本
        obj: 元素对象, 必填
        value: 输入得内容， 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                element.send_keys(value)
        else:
            self.find_elements(obj, element_index, timeout).send_keys(value)
        self._log.append({'title': formatter_log('INFO', '输入文本'), 'value': f'{value}'})

    @action_group(SeleniumStepType.ElementAction, SeleniumStepTypeName.ElementAction)
    def clear(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        清空文本
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                element.clear()
        else:
            self.find_elements(obj, element_index, timeout).clear()
        self._log.append({'title': formatter_log('INFO', '清空文本'), 'value': f'成功清空内容'})

    @action_group(SeleniumStepType.ElementAction, SeleniumStepTypeName.ElementAction)
    def get_text(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        获取文本
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: list[str] or str 元素文本内容, list[str] 多个元素, str 单个元素 文本内容
        """
        if element_index == -1:
            text_list = []
            for element in self.find_elements(obj, element_index, timeout):
                text_list.append(element.text)
            self._log.append({'title': formatter_log('INFO', '获取文本'), 'value': f'{text_list.join("-")}'})
            return text_list
        else:
            text = self.find_elements(obj, element_index, timeout).text
            self._log.append({'title': formatter_log('INFO', '获取文本'), 'value': f'{text}'})
            return text

    @action_group(SeleniumStepType.ElementAction, SeleniumStepTypeName.ElementAction)
    def get_tag_name(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        获取标签名
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: list[str] or str 元素标签名, list[str] 多个元素, str 单个元素 标签内容
        """
        if element_index == -1:
            tag_name_list = []
            for element in self.find_elements(obj, element_index, timeout):
                tag_name_list.append(element.tag_name)
            self._log.append({'title': formatter_log('INFO', '获取标签名'), 'value': f'{tag_name_list.join("-")}'})
            return tag_name_list
        else:
            tag_name = self.find_elements(obj, element_index, timeout).tag_name
            self._log.append({'title': formatter_log('INFO', '获取标签名'), 'value': f'{tag_name}'})
            return tag_name

    @action_group(SeleniumStepType.ElementAction, SeleniumStepTypeName.ElementAction)
    def get_attribute(self, obj: ElementSerializers, name: str, element_index: int =0, timeout: int = 5):
        """
        获取属性
        obj: 元素对象, 必填
        name: 元素属性名称, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: list[str] or str 元素属性值, list[str] 多个元素, str 单个元素 属性内容
        """
        if element_index == -1:
            attr_value_list = []
            for element in self.find_elements(obj, element_index, timeout):
                attr_value_list.append(element.get_attribute(name))
            self._log.append({'title': formatter_log('INFO', '获取属性'), 'value': f'{attr_value_list.join("-")}'})
            return attr_value_list
        else:
            attr_value = self.find_elements(obj, element_index, timeout).get_attribute(name)
            self._log.append({'title': formatter_log('INFO', '获取属性'), 'value': f'{attr_value}'})
            return attr_value

    @action_group(SeleniumStepType.ElementAction, SeleniumStepTypeName.ElementAction)
    def get_css_property(self, obj: ElementSerializers, name: str, element_index: int =0, timeout: int = 5):
        """
        获取CSS属性
        obj: 元素对象, 必填
        name: CSS属性名称, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: list[str] or str CSS属性值, list[str] 多个元素, str 单个元素 CSS属性值
        """
        if element_index == -1:
            attr_value_list = []
            for element in self.find_elements(obj, element_index, timeout):
                attr_value_list.append(element.value_of_css_property(name))
            self._log.append({'title': formatter_log('INFO', '获取CSS属性'), 'value': f'{attr_value_list.join("-")}'})
            return attr_value_list
        else:
            attr_value = self.find_elements(obj, element_index, timeout).value_of_css_property(name)
            self._log.append({'title': formatter_log('INFO', '获取CSS属性'), 'value': f'{attr_value}'})
            return attr_value

    @action_group(SeleniumStepType.ElementAction, SeleniumStepTypeName.ElementAction)
    def scroll_into_view(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        将元素移动到屏幕可见区域
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        self.driver.execute_script("arguments[0].scrollIntoView();", self.find_elements(obj, element_index, timeout))
        self._log.append({'title': formatter_log('INFO', '将元素移动到屏幕可见区域'), 'value': '将元素移动到屏幕可见区域成功'})

    @action_group(SeleniumStepType.ElementAction, SeleniumStepTypeName.ElementAction)
    def is_displayed(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        元素是否显示
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: list[bool] or bool 元素是否显示, True 显示, False 不显示
        """
        result_list = []
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                result_list.append(element.is_displayed())
            self._log.append({'title': formatter_log('INFO', '元素是否显示'), 'value': f'{result_list.join("-")}'})
            return result_list
        else:
            result = self.find_elements(obj, element_index, timeout).is_displayed()
            self._log.append({'title': formatter_log('INFO', '元素是否显示'), 'value': f'{result}'})
            return result

    @action_group(SeleniumStepType.ElementAction, SeleniumStepTypeName.ElementAction)
    def is_enabled(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        元素是否可用
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: list[bool] or bool 元素是否可用, True 可用, False 不可用
        """
        if element_index == -1:
            result_list = []
            for element in self.find_elements(obj, element_index, timeout):
                result_list.append(element.is_enabled())
            self._log.append({'title': formatter_log('INFO', '元素是否可用'), 'value': f'{result_list.join("-")}'})
            return result_list
        else:
            result = self.find_elements(obj, element_index, timeout).is_enabled()
            self._log.append({'title': formatter_log('INFO', '元素是否可用'), 'value': f'{result}'})
            return result

    @action_group(SeleniumStepType.ElementAction, SeleniumStepTypeName.ElementAction)
    def is_selected(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        元素是否选中
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: list[bool] or bool 元素是否选中, True 选中, False 非选中
        """
        result_list = []
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                result_list.append(element.is_selected())
            self._log.append({'title': formatter_log('INFO', '元素是否选中'), 'value': f'{result_list.join("-")}'})
            return result_list
        else:
            result = self.find_elements(obj, element_index, timeout).is_selected()
            self._log.append({'title': formatter_log('INFO', '元素是否选中'), 'value': f'{result}'})
            return result

    @action_group(SeleniumStepType.ElementAction, SeleniumStepTypeName.ElementAction)
    def submit(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        提交表单
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                element.submit()
        else:
            self.find_elements(obj, element_index, timeout).submit()
        self._log.append({'title': formatter_log('INFO', '提交表单'), 'value': '提交表单成功'})

    # 鼠标操作
    @action_group(SeleniumStepType.MouseAction, SeleniumStepTypeName.MouseAction)
    def click_perform(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        鼠标单击
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                ActionChains(self.driver).click(element).perform()
        else:
            ActionChains(self.driver).click(self.find_elements(obj, element_index, timeout)).perform()
        self._log.append({'title': formatter_log('INFO', '鼠标单击'), 'value': '鼠标单击成功'})

    @action_group(SeleniumStepType.MouseAction, SeleniumStepTypeName.MouseAction)
    def double_click(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        鼠标双击
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                ActionChains(self.driver).double_click(element).perform()
        else:
            ActionChains(self.driver).double_click(self.find_elements(obj, element_index, timeout)).perform()
        self._log.append({'title': formatter_log('INFO', '鼠标双击'), 'value': f'鼠标双击成功'})

    @action_group(SeleniumStepType.MouseAction, SeleniumStepTypeName.MouseAction)
    def move_to_element(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        鼠标悬停
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                ActionChains(self.driver).move_to_element(element).perform()
        else:
            ActionChains(self.driver).move_to_element(self.find_elements(obj, element_index, timeout)).perform()
        self._log.append({'title': formatter_log('INFO', '鼠标悬停'), 'value': f'鼠标悬停成功'})

    @action_group(SeleniumStepType.MouseAction, SeleniumStepTypeName.MouseAction)
    def context_click(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        右键点击
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                ActionChains(self.driver).context_click(element).perform()
        else:
            ActionChains(self.driver).context_click(self.find_elements(obj, element_index, timeout)).perform()
        self._log.append({'title': formatter_log('INFO', '右键点击'), 'value': '鼠标右键点击成功'})

    @action_group(SeleniumStepType.MouseAction, SeleniumStepTypeName.MouseAction)
    def click_and_hold(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        点击并按住
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                ActionChains(self.driver).click_and_hold(element).perform()
        else:
            ActionChains(self.driver).click_and_hold(self.find_elements(obj, element_index, timeout)).perform()
        self._log.append({'title': formatter_log('INFO', '点击并按住'), 'value': '点击并按住成功'})

    @action_group(SeleniumStepType.MouseAction, SeleniumStepTypeName.MouseAction)
    def release(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        释放
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                ActionChains(self.driver).release(element).perform()
        else:
            ActionChains(self.driver).release(self.find_elements(obj, element_index, timeout)).perform()
        self._log.append({'title': formatter_log('INFO', '释放'), 'value': '释放成功'})

    @action_group(SeleniumStepType.MouseAction, SeleniumStepTypeName.MouseAction)
    def drag_and_drop(self, obj1: ElementSerializers, obj2: ElementSerializers, element1_index: int =0, element2_index: int =0, timeout: int = 5):
        """
        拖放
        obj1: 元素对象, 必填
        obj2: 元素对象, 必填
        element1_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        element2_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        """
        ActionChains(self.driver).drag_and_drop(self.find_elements(obj1, element1_index, timeout), self.find_elements(obj2, element2_index, timeout)).perform()
        self._log.append({'title': formatter_log('INFO', '拖放'), 'value': f'拖放成功'})

    @action_group(SeleniumStepType.MouseAction, SeleniumStepTypeName.MouseAction)
    def drag_and_drop_by_offset(self, obj: ElementSerializers, element_index: int =0, x_offset: int =0, y_offset: int =0, timeout: int = 5):
        """
        拖放偏移
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        x_offset: x轴偏移量
        y_offset: y轴偏移量
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        source = None
        if element_index == -1:
            for element in self.find_elements(obj, element_index, timeout):
                ActionChains(self.driver).drag_and_drop_by_offset(element, x_offset, y_offset).perform()
        else:
            source = self.find_elements(obj, element_index, timeout)
        ActionChains(self.driver).drag_and_drop_by_offset(source, x_offset, y_offset).perform()
        self._log.append({'title': formatter_log('INFO', '拖放偏移'), 'value': f'拖放偏移成功'})

    # 键盘操作
    @action_group(SeleniumStepType.KeyboardAction, SeleniumStepTypeName.KeyboardAction)
    def press_enter(self):
        """
        按回车键
        return: None
        """
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        self._log.append({'title': formatter_log('INFO', '按回车键'), 'value': f'按回车键成功'})

    @action_group(SeleniumStepType.KeyboardAction, SeleniumStepTypeName.KeyboardAction)
    def press_tab(self):
        """
        按Tab键
        return: None
        """
        ActionChains(self.driver).send_keys(Keys.TAB).perform()
        self._log.append({'title': formatter_log('INFO', '按Tab键'), 'value': f'按Tab键成功'})

    @action_group(SeleniumStepType.KeyboardAction, SeleniumStepTypeName.KeyboardAction)
    def press_esc(self):
        """
        按ESC键
        return: None
        """
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        self._log.append({'title': formatter_log('INFO', '按Esc键'), 'value': f'按Esc键成功'})

    @action_group(SeleniumStepType.KeyboardAction, SeleniumStepTypeName.KeyboardAction)
    def press_other(self, key_name: str):
        """
        按其他按键
        key_name: 键名称
        return: None
        """
        ActionChains(self.driver).send_keys(key_name).perform()
        self._log.append({'title': formatter_log('INFO', '按其他键'), 'value': f'{key_name}'})

    @action_group(SeleniumStepType.KeyboardAction, SeleniumStepTypeName.KeyboardAction)
    def press_ctrl_a(self):
        """
        按Ctrl+A
        return: None
        """
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        self._log.append({'title': formatter_log('INFO', '按Ctrl+A'), 'value': f'按Ctrl+A成功'})

    @action_group(SeleniumStepType.KeyboardAction, SeleniumStepTypeName.KeyboardAction)
    def press_ctrl_c(self):
        """
        按Ctrl+C
        return: None
        """
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        self._log.append({'title': formatter_log('INFO', '按Ctrl+C'), 'value': f'按Ctrl+C成功'})

    @action_group(SeleniumStepType.KeyboardAction, SeleniumStepTypeName.KeyboardAction)
    def press_ctrl_v(self):
        """
        按Ctrl+V
        return: None
        """
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('V').key_up(Keys.CONTROL).perform()
        self._log.append({'title': formatter_log('INFO', '按Ctrl+V'), 'value': f'按Ctrl+V成功'})

    # 弹窗操作
    @action_group(SeleniumStepType.AlertHandling, SeleniumStepTypeName.AlertHandling)
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

    @action_group(SeleniumStepType.AlertHandling, SeleniumStepTypeName.AlertHandling)
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

    @action_group(SeleniumStepType.AlertHandling, SeleniumStepTypeName.AlertHandling)
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

    @action_group(SeleniumStepType.AlertHandling, SeleniumStepTypeName.AlertHandling)
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

    @action_group(SeleniumStepType.JavaScriptExecution, SeleniumStepTypeName.JavaScriptExecution)
    def execute_script(self, script: str):
        """
        执行js脚本
        script: 执行的脚本, str, 必填
        return None
        """
        self.driver.execute_script(script)
        self.case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', 'Selenium关键字【execute_script】执行成功'),
                                                    'value': f'执行脚本：{script}'})

    def wait_element_located(self, obj: ElementSerializers, timeout: int = 5):
        """
        等待元素被加载到Dom树中，并且可见
        obj: 元素对象, 必填
        timeout: 超时时间, int, 非必填，默认5s
        return None
        """
        loc_method = obj['by']
        loc_value = obj['value']
        WebDriverWait(self.driver, timeout, 0.5).until(
            expected_conditions.visibility_of_element_located((loc_method, loc_value)))

    @staticmethod
    def _update_loc(obj, ai_loc_by, ai_loc_value):
        element_obj = Element.objects.get(id=obj['id'])
        element_obj.web = {'by': ai_loc_by, 'value': ai_loc_value}
        element_obj.save()

    def _get_driver_by_ai(self, obj):
        try:
            ai_loc_obj = generate_loc_path_by_ai(obj['name'], self.code, self.case_logs_obj)
            ai_loc_by, ai_loc_value = ai_loc_obj['by'],  ai_loc_obj['value']
            driver_obj = self.driver.find_element(ai_loc_by, ai_loc_value)
            self._update_loc(obj, ai_loc_by, ai_loc_value)
            return driver_obj
        except Exception:
            raise NoSuchElementException

    def find_elements(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        查找元素列表
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return list 元素对象列表
        """
        web_loc = obj['web']
        # 兼容旧版本：曾用列表存储单条或多条定位，取第一条
        if isinstance(web_loc, list):
            web_loc = web_loc[0] if web_loc else {}
        self._update_page_content()
        try:
            self.wait_element_located(web_loc, timeout)
            element_list = self.driver.find_elements(web_loc['by'], web_loc['value'])
            if element_index == -1:
                return element_list
            elif len(element_list) == 0 or element_index >= len(element_list):
                raise NoSuchElementException
            else:
                return element_list[element_index]
        except (NoSuchElementException, TimeoutException):
            base64_str = 'data:image/png;base64,' + self.driver.get_screenshot_as_base64()
            self._log.append({'title': formatter_log('ERROR', f'查找元素失败'), 'value': f'', 'uri': base64_str})
            return self._get_driver_by_ai(obj)

    def _update_page_content(self):
        self.code = self.driver.page_source
        self.code = re.search(r'<body.*?>.*?</body>', self.code, re.DOTALL).group()

    @action_group(SeleniumStepType.Screenshots, SeleniumStepTypeName.Screenshots)
    def screenshot(self):
        """
        屏幕截图
        return str
        """
        base64_str = 'data:image/png;base64,' + self.driver.get_screenshot_as_base64()
        self._log.append({'title': formatter_log('INFO', '屏幕截图'), 'value': '', 'uri': base64_str})

    @action_group(SeleniumStepType.CookiesManagement, SeleniumStepTypeName.CookiesManagement)
    def add_cookie(self, cookie_value: dict):
        """
        添加cookie
        cookie_value: cookie值， dict类型， 必填
        return: None
        """
        self.driver.add_cookie(cookie_value)
        cookie_value = json.dumps(cookie_value)
        self._log.append({'title': formatter_log('INFO', '添加cookie'), 'value': f'{cookie_value}'})

    @action_group(SeleniumStepType.CookiesManagement, SeleniumStepTypeName.CookiesManagement)
    def get_cookie(self, cookie_name: str):
        """
        获取cookie
        cookie_name: cookie名， str类型， 必填
        return: cookie的值
        """
        cookie = self.driver.get_cookie(cookie_name)
        cookie_value = json.dumps(cookie)
        self._log.append({'title': formatter_log('INFO', '获取cookie'), 'value': f'{cookie_value}'})
        return cookie

    @action_group(SeleniumStepType.CookiesManagement, SeleniumStepTypeName.CookiesManagement)
    def get_cookies(self):
        """
        获取所有cookie
        return: list 所有cookie的值
        """
        cookies = self.driver.get_cookies()
        cookie_value = json.dumps(cookies)
        self._log.append({'title': formatter_log('INFO', '获取所有cookie'), 'value': f'{cookie_value}'})
        return cookies

    @action_group(SeleniumStepType.CookiesManagement, SeleniumStepTypeName.CookiesManagement)
    def delete_cookie(self, cookie_name: str):
        """
        删除指定cookie
        cookie_name： str cookie名称
        return: None
        """
        self.driver.delete_cookie(cookie_name)
        self._log.append({'title': formatter_log('INFO', '删除指定cookie'), 'value': f'删除指定cookie成功'})

    @action_group(SeleniumStepType.CookiesManagement, SeleniumStepTypeName.CookiesManagement)
    def delete_cookies(self):
        """
        删除所有cookies
        obj: 元素对象, 必填
        return: None
        """
        self.driver.delete_all_cookies()
        self._log.append({'title': formatter_log('INFO', '删除所有cookies'), 'value': f'删除所有cookies成功'})

    @action_group(SeleniumStepType.WindowSwitching, SeleniumStepTypeName.WindowSwitching)
    def switch_frame(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        进入指定frame
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找Frame元素超时时间, int, 非必填，默认5s
        return: None
        """
        frame = self.find_elements(obj, element_index, timeout)
        self.driver.switch_to.frame(frame)
        self._log.append({'title': formatter_log('INFO', '进入指定frame'), 'value': '进入指定frame成功'})

    @action_group(SeleniumStepType.WindowSwitching, SeleniumStepTypeName.WindowSwitching)
    def exit_frame(self):
        """
        退出frame
        return: None
        """
        self.driver.switch_to.default_content()
        self._log.append({'title': formatter_log('INFO', '退出frame'), 'value': '退出frame成功'})

    @action_group(SeleniumStepType.WindowSwitching, SeleniumStepTypeName.WindowSwitching)
    def get_current_window_name(self):
        """
        获取当前窗口句柄的名称
        return: Str 返回当前窗口的名称
        """
        name = self.driver.current_window_handle
        self._log.append({'title': formatter_log('INFO', '获取当前窗口句柄的名称'), 'value': f'{name}'})

    @action_group(SeleniumStepType.WindowSwitching, SeleniumStepTypeName.WindowSwitching)
    def get_window_handles(self):
        """
        获取当前会话所有窗口句柄的名称
        return: Str 获取当前会话所有窗口句柄的名称
        """
        name = self.driver.window_handles
        self._log.append({'title': formatter_log('INFO', '获取当前会话所有窗口句柄的名称'), 'value': f'{name}'})

    @action_group(SeleniumStepType.WindowSwitching, SeleniumStepTypeName.WindowSwitching)
    def get_window_handles(self, handler_name: str):
        """
        切换指定窗口
        handler_name: str 切换窗口的句柄名称
        return: None
        """
        self.driver.switch_to.window(handler_name)
        self._log.append({'title': formatter_log('INFO', '切换指定窗口'), 'value': f'{handler_name}'})

    @action_group(SeleniumStepType.SelectClass, SeleniumStepTypeName.SelectClass)
    def select_by_label(self, obj: ElementSerializers, label_text: str, element_index: int =0, timeout: int = 5):
        """
        按文本选择下拉列表选项
        obj: 元素对象, 必填
        label_text: str, 下拉列表的文本值
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: None
        """
        Select(self.find_elements(obj, element_index, timeout)).select_by_visible_text(label_text)
        self._log.append( {'title': formatter_log('INFO', '按文本选择下拉列表选项'), 'value': f'按文本选中成功:{label_text}'})

    @action_group(SeleniumStepType.SelectClass, SeleniumStepTypeName.SelectClass)
    def deselect_by_label(self, obj: ElementSerializers, label_text: str, element_index: int =0, timeout: int = 5):
        """
        按文本取消选择下拉列表选项
        obj: 元素对象, 必填
        label_text: str, 下拉列表的文本值
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: None
        """
        Select(self.find_elements(obj, element_index, timeout)).deselect_by_visible_text(label_text)
        self._log.append({'title': formatter_log('INFO', '按文本取消选择下拉列表选项'), 'value': f'按文本取消选中成功:{label_text}'})

    @action_group(SeleniumStepType.SelectClass, SeleniumStepTypeName.SelectClass)
    def select_by_value(self, obj: ElementSerializers, value: str, element_index: int =0, timeout: int = 5):
        """
        按值选择下拉列表选项
        obj: 元素对象, 必填
        value: str, 下拉列表的值
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: None
        """

        Select(self.find_elements(obj, element_index, timeout)).select_by_value(value)
        self._log.append({'title': formatter_log('INFO', '按值选择下拉列表选项'), 'value': f'按值选中成功:{value}'})

    @action_group(SeleniumStepType.SelectClass, SeleniumStepTypeName.SelectClass)
    def deselect_by_value(self, obj: ElementSerializers, value: str, element_index: int =0, timeout: int = 5):
        """
        按值取消选择下拉列表选项
        obj: 元素对象, 必填
        value: str, 下拉列表的值
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: None
        """

        Select(self.find_elements(obj, element_index, timeout)).deselect_by_value(value)
        self._log.append({'title': formatter_log('INFO', '按值取消选择下拉列表选项'), 'value': f'按值取消选中成功:{value}'})

    @action_group(SeleniumStepType.SelectClass, SeleniumStepTypeName.SelectClass)
    def select_by_index(self, obj: ElementSerializers, index: int, element_index: int =0, timeout: int = 5):
        """
        按索引选择下拉列表选项
        obj: 元素对象, 必填
        index: index, 下拉列表的索引
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: None
        """

        Select(self.find_elements(obj, element_index, timeout)).select_by_index(index)
        self._log.append({'title': formatter_log('INFO', '按索引选择下拉列表选项'), 'value': f'按索引选中成功:{index}'})

    @action_group(SeleniumStepType.SelectClass, SeleniumStepTypeName.SelectClass)
    def deselect_by_index(self, obj: ElementSerializers, index: int, element_index: int =0, timeout: int = 5):
        """
        按索引取消选择下拉列表选项
        obj: 元素对象, 必填
        index: index, 下拉列表的索引
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: None
        """

        Select(self.find_elements(obj, element_index, timeout)).deselect_by_index(index)
        self._log.append({'title': formatter_log('INFO', '按索引取消选择下拉列表选项'), 'value': f'按索引取消选中成功:{index}'})

    @action_group(SeleniumStepType.SelectClass, SeleniumStepTypeName.SelectClass)
    def deselect_all(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        取消所有选中项
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: None
        """
        Select(self.find_elements(obj, element_index, timeout)).deselect_all()
        self._log.append({'title': formatter_log('INFO', '取消所有选中项'), 'value': '取消所有选中项成功'})

    @action_group(SeleniumStepType.SelectClass, SeleniumStepTypeName.SelectClass)
    def get_all_options(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        获取所有选项元素对象
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: List 所有选项的元素对象
        """
        options = Select(self.find_elements(obj, element_index, timeout)).options
        self._log.append({'title': formatter_log('INFO', '获取所有选项'), 'value': '获取所有选项成功'})
        return options

    @action_group(SeleniumStepType.SelectClass, SeleniumStepTypeName.SelectClass)
    def get_selected_options(self, obj: ElementSerializers, element_index: int =0, timeout: int = 5):
        """
        获取所有选中的选项元素对象
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: List 所有选中选项的元素对象
        """
        options = Select(self.find_elements(obj, element_index, timeout)).all_selected_options
        self._log.append({'title': formatter_log('INFO', '获取所有选中的选项元素对象'), 'value': '获取所有选中的选项元素对象成功'})
        return options


selenium_actions = [{
                    'id': key,
                    'script': inspect.getsource(value),
                    'params': get_function_params(value),
                    'name': [new_str.strip() for new_str in value.__doc__.strip().split('\n')][0],
                    'group': value.__dict__.get('group_id'),
                    'group_name': value.__dict__.get('group_name')}
                    for key, value in SeleniumBaseAction.__dict__.items()
                    if not key.startswith('_')]

selenium_func_map = {key: value for key, value in SeleniumBaseAction.__dict__.items()
                     if not key.startswith('_')}

selenium_func_doc = {key: [new_str.strip() for new_str in value.__doc__.strip().split('\n')]
                     for key, value in SeleniumBaseAction.__dict__.items()
                     if not key.startswith('_')}


def run_step_selenium(manager_obj, env_id, step, case_params, case_logs_obj, run_times, run_element):
    step_id = step["case_step_id"]
    plant_id = step['plant']
    env_plant_query = EnvPlant.objects.all().filter(env=env_id, plant=plant_id, is_delete=False)
    if not env_plant_query.exists():
        raise EnvPlantNotExistException()
    host = env_plant_query[0].host
    case_params.stepResponse[f'{step_id}']['runTimes'] = run_times
    case_params.stepResponse[f'{step_id}']['runElement'] = run_element
    keyword = step['keyword']
    func_params = func_list_to_dict(step['func_params'], {}, case_params, case_logs_obj)
    case_params.stepResponse[f'{step_id}']['funcParams'] = func_params
    if host not in manager_obj.driver_manager and host is not None:
        manager_obj.driver_manager[host] = SeleniumBaseAction(case_params, case_logs_obj, host,
                                                              manager_obj.web_executor_id, plant_id,
                                                              manager_obj, step_id)
    exec_and_return(manager_obj, step['setup'], case_logs_obj, formatter_log, case_params, sys_function)
    return_value = selenium_func_map[keyword](manager_obj.driver_manager[host], **func_params)
    case_params.stepResponse[f'{step_id}']['funcReturn'] = return_value
    exec_and_return(manager_obj, step['teardown'], case_logs_obj, formatter_log, case_params, sys_function)

    # 执行步骤的断言参数,如果步骤中有断言数据则忽略接口的断言数据
    loop_assert_by_check_list(step['check_params'], case_params, case_logs_obj)
