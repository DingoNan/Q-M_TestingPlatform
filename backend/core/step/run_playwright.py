import os
import re
import inspect
import json
import base64
import shutil
import time
import uuid
from django.conf import settings
import core.com.faker as sys_function
from openai import OpenAI
from core.com.common import (
    formatter_log,
    get_function_params,
    lis2dict,
)
from playwright.sync_api import sync_playwright
from core.com.common import func_list_to_dict
from apps.elements.serializers import ElementSerializers
from apps.envs.models import EnvPlant, Cookies
from apps.elements.models import Element
from core.com.step_model import action_group
from core.com.check import loop_assert_by_check_list
from core.step.run_python_script import exec_and_return
from core.com.step_model import PlaywrightStepType, PlaywrightStepTypeName
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


class PlaywrightBaseAction:

    def __init__(self, case_params: object, case_logs_obj: object, host, plant_id, manager_obj, step_id):

        self.playwright = sync_playwright().start()
        # Trace/视频录制目录: 位于 MEDIA_ROOT 持久卷, 供测试历史页直接回放
        self._trace_dir = os.path.join(str(settings.MEDIA_ROOT), 'traces')
        os.makedirs(self._trace_dir, exist_ok=True)
        safe_host = re.sub(r'[^a-zA-Z0-9_-]', '_', str(host))
        self._trace_prefix = f"pw_r{manager_obj.report_id or 0}_{safe_host}_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self._video_tmp_dir = os.path.join(self._trace_dir, f'{self._trace_prefix}_vidtmp')
        os.makedirs(self._video_tmp_dir, exist_ok=True)
        # 窗口尺寸: 优先读环境变量 PLAYWRIGHT_WINDOW_SIZE(如 1920x1080), 无显示器(Docker headless)时作为屏幕尺寸兜底
        self._window_size = self._resolve_window_size()
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-features=VizDisplayCompositor",
                "--ignore-certificate-errors",
                # 启动即最大化: 有显示器时最大化到真实屏幕, headless 下配合 --window-size 生效
                "--start-maximized",
                f"--window-size={self._window_size['width']},{self._window_size['height']}"
            ]
        )
        self.context = self.browser.new_context(
            no_viewport=True,
            record_video_dir=self._video_tmp_dir
        )
        self._trace_started = False
        try:
            self.context.tracing.start(screenshots=True, snapshots=True, sources=True)
            self._trace_started = True
        except Exception:
            pass
        self.page = self.context.new_page()
        # 不设置 set_default_timeout(7000)：页面加载(goto)可能超过 7s，默认 7s 会导致访问慢页面
        # 直接超时。去掉后恢复 Playwright 默认超时(30s)，慢页面也能正常加载。
        # 弹窗队列: playwright 默认自动关闭弹窗, 注册监听后弹窗挂起等待步骤处理(accept/dismiss)
        self._dialog_queue = []
        self.page.on('dialog', self._on_dialog)
        # 窗口句柄注册表: playwright 无原生窗口句柄(Selenium概念), 用自增ID映射Page对象
        self._window_registry = {}
        self._window_seq = 0
        self._register_windows()

        self.plant_id = plant_id
        self.step_id = step_id
        self.manager_obj = manager_obj
        self.case_params = case_params
        self.case_logs_obj = case_logs_obj
        self.host = host
        self.code = None

    @staticmethod
    def _resolve_window_size():
        """解析窗口尺寸: 环境变量 PLAYWRIGHT_WINDOW_SIZE(格式 WxH), 默认 1920x1080"""
        raw = os.environ.get('PLAYWRIGHT_WINDOW_SIZE', '1920x1080')
        try:
            w, h = str(raw).lower().split('x', 1)
            return {'width': max(int(w), 1), 'height': max(int(h), 1)}
        except (ValueError, TypeError):
            return {'width': 1920, 'height': 1080}

    def _on_dialog(self, dialog):
        """弹窗事件回调: 挂起到队列, 由弹窗操作关键字消费"""
        self._dialog_queue.append(dialog)

    def _register_windows(self):
        """为 context 中新出现的页面分配窗口句柄并挂载弹窗监听"""
        for page in self.context.pages:
            if not any(registered is page for registered in self._window_registry.values()):
                self._window_seq += 1
                self._window_registry[f'win_{self._window_seq}'] = page
                page.on('dialog', self._on_dialog)

    def _current_page(self):
        """switch_frame 后 self.page 可能是 Frame, 解析出其所属的顶层 Page 对象"""
        return getattr(self.page, 'page', None) or self.page

    def _ensure_dialog(self, timeout: int = 5):
        """等待弹窗出现在队列中, 超时抛出异常"""
        deadline = time.time() + timeout
        # 注意: 同步API仅在等待Playwright调用时分发事件回调, 必须用 wait_for_timeout 而非 time.sleep
        while time.time() < deadline:
            if self._dialog_queue:
                return
            remaining = min(max(deadline - time.time(), 0), 0.1)
            self._current_page().wait_for_timeout(remaining * 1000)
        raise TimeoutError(f'等待弹窗超时({timeout}s)')

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
                if isinstance(cookie_values, list):
                    for cookie in cookie_values:
                        self.context.add_cookies([cookie])
                else:
                    self.context.add_cookies([cookie_values])
            elif env_cookie_obj.type == Cookies.CookieType.Session:
                for session_key, session_value in cookie_values.items():
                    if isinstance(session_value, dict) or isinstance(session_value, list):
                        session_value = json.dumps(session_value)
                    self.page.evaluate(f"sessionStorage.setItem('{session_key}', '{session_value}')")
            else:
                for local_key, local_value in cookie_values.items():
                    if isinstance(local_value, dict) or isinstance(local_value, list):
                        local_value = json.dumps(local_value)
                    self.page.evaluate(f"localStorage.setItem('{local_key}', '{local_value}')")

    @staticmethod
    def __text(obj):
        return '【{}_{}_{}_{}】'.format(obj['plant_name'], obj['module_name'], obj['page_name'], obj['name'])

    # 浏览器操作
    @action_group(PlaywrightStepType.DriverAction, PlaywrightStepTypeName.DriverAction)
    def goto(self, uri: str, need_add_cookie: bool = False):
        """
        打开浏览器并访问URL
        uri: 页面路径, 必填
        need_add_cookie: 是否需要添加Cookie，如果是,则从环境管理中的Cookie中自动添加Cookie绕过登录操作
        return: None
        """
        url = self.host + uri
        if need_add_cookie:
            self.page.goto(url)
            self.__deal_cookies()
        self.page.goto(url)
        self._log.append({'title': formatter_log('INFO', '打开浏览器并访问URL'), 'value': f'{url}'})

    @action_group(PlaywrightStepType.DriverAction, PlaywrightStepTypeName.DriverAction)
    def url(self):
        """
        获取当前页面URL
        return: str 当前页面的URL地址
        """
        current_url = self.page.url
        self._log.append({'title': formatter_log('INFO', '获取当前页面URL'), 'value': f'{current_url}'})
        return current_url

    @action_group(PlaywrightStepType.DriverAction, PlaywrightStepTypeName.DriverAction)
    def title(self):
        """
        获取当前页面标题
        return: str 当前页面的标题
        """
        page_title = self.page.title()
        self._log.append({'title': formatter_log('INFO', '获取当前页面标题'), 'value': f'{page_title}'})
        return page_title

    @action_group(PlaywrightStepType.DriverAction, PlaywrightStepTypeName.DriverAction)
    def go_back(self):
        """
        返回浏览器上一页
        return: None
        """
        self.page.go_back()
        self._log.append({'title': formatter_log('INFO', '返回浏览器上一页'), 'value': '成功返回浏览器上一页'})

    @action_group(PlaywrightStepType.DriverAction, PlaywrightStepTypeName.DriverAction)
    def go_forward(self):
        """
        返回浏览器下一页
        return: None
        """
        self.page.go_forward()
        self._log.append({'title': formatter_log('INFO', '返回浏览器下一页'), 'value': '成功返回浏览器下一页'})

    @action_group(PlaywrightStepType.DriverAction, PlaywrightStepTypeName.DriverAction)
    def reload(self):
        """
        刷新浏览器
        return: None
        """
        self.page.reload()
        self._log.append({'title': formatter_log('INFO', '刷新浏览器'), 'value': '成功刷新浏览器'})

    @action_group(PlaywrightStepType.DriverAction, PlaywrightStepTypeName.DriverAction)
    def content(self):
        """
        获取页面源码
        return: str 返回当前页面的html内容
        """
        page_content = self.page.content()
        self._log.append({'title': formatter_log('INFO', '获取页面源码'), 'value': f'{page_content}'})

    @action_group(PlaywrightStepType.DriverAction, PlaywrightStepTypeName.DriverAction)
    def maximize_window(self):
        """
        最大化窗口
        return: None
        """
        self.page.set_viewport_size(self._window_size)
        self._log.append({'title': formatter_log('INFO', '最大化窗口'), 'value': f'成功最大化窗口'})

    @action_group(PlaywrightStepType.DriverAction, PlaywrightStepTypeName.DriverAction)
    def minimize_window(self):
        """
        最小化窗口
        return: None
        """
        self.page.set_viewport_size({"width": 800, "height": 600})
        self._log.append({'title': formatter_log('INFO', '最小化窗口'), 'value': f'成功最小化窗口'})

    @action_group(PlaywrightStepType.DriverAction, PlaywrightStepTypeName.DriverAction)
    def full_screen_window(self):
        """
        全屏
        return: None
        """
        self.page.set_viewport_size(self._window_size)
        self._log.append({'title': formatter_log('INFO', '全屏'), 'value': f'成功全屏'})

    def _quit(self):
        # 0. 等待末帧落盘: screencast 按重绘产帧, 最后一个操作的画面可能还没送达,
        #    立即关闭页面会把它掐掉(表现为视频里最后一步操作不可见)
        try:
            self._current_page().wait_for_timeout(1000)
        except Exception:
            pass
        # 1. 提前持有视频句柄(context 关闭后无法再从 page 获取)
        video = None
        try:
            if self.page:
                video = self.page.video
        except Exception:
            video = None
        # 2. 停止 Trace 录制并保存 zip(必须在 context.close 之前)
        trace_url = ''
        try:
            if self.context and self._trace_started:
                zip_name = f'{self._trace_prefix}.zip'
                self.context.tracing.stop(path=os.path.join(self._trace_dir, zip_name))
                trace_url = f'/traces/{zip_name}'
        except Exception:
            pass
        # 3. 关闭页面与上下文(视频在 context 关闭后完成写盘)
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        # 4. 归档视频文件到 traces 目录
        video_url = ''
        if video is not None:
            try:
                video_name = f'{self._trace_prefix}.webm'
                shutil.move(str(video.path()), os.path.join(self._trace_dir, video_name))
                video_url = f'/traces/{video_name}'
            except Exception:
                pass
        shutil.rmtree(self._video_tmp_dir, ignore_errors=True)
        # 5. 关闭浏览器与 playwright
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        # 6. 写入测试历史日志(前端渲染视频回放与 Trace 入口)
        try:
            if trace_url or video_url:
                self.case_logs_obj.logs.append({
                    'step_desc': '执行过程回放(Trace/视频)',
                    'logs': [{'title': formatter_log('INFO', '执行过程回放'), 'value': '',
                              'trace_url': trace_url, 'video_url': video_url}]
                })
        except Exception:
            pass

    # 元素操作
    @action_group(PlaywrightStepType.ElementAction, PlaywrightStepTypeName.ElementAction)
    def click(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        点击元素
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.locator(obj, element_index, timeout):
                element.click()
        else:
            self.locator(obj, element_index, timeout).click()
        self._log.append({'title': formatter_log('INFO', '点击元素'), 'value': f'鼠标点击成功'})

    @action_group(PlaywrightStepType.ElementAction, PlaywrightStepTypeName.ElementAction)
    def fill(self, obj: ElementSerializers, value: str, element_index: int = 0, timeout: int = 5):
        """
        输入文本
        obj: 元素对象, 必填
        value: 输入得内容， 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.locator(obj, element_index, timeout):
                element.fill(value)
        else:
            self.locator(obj, element_index, timeout).fill(value)
        self._log.append({'title': formatter_log('INFO', '输入文本'), 'value': f'{value}'})

    @action_group(PlaywrightStepType.ElementAction, PlaywrightStepTypeName.ElementAction)
    def clear(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        清空文本
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.locator(obj, element_index, timeout):
                element.clear()
        else:
            self.locator(obj, element_index, timeout).clear()
        self._log.append({'title': formatter_log('INFO', '清空文本'), 'value': f'成功清空内容'})

    @action_group(PlaywrightStepType.ElementAction, PlaywrightStepTypeName.ElementAction)
    def text_content(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        获取文本
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: list[str] or str 元素文本内容, list[str] 多个元素, str 单个元素 文本内容
        """
        if element_index == -1:
            text_list = []
            for element in self.locator(obj, element_index, timeout):
                text_list.append(element.text_content())
            self._log.append({'title': formatter_log('INFO', '获取文本'), 'value': f'{"-".join(map(str, text_list))}'})
            return text_list
        else:
            text = self.locator(obj, element_index, timeout).text_content()
            self._log.append({'title': formatter_log('INFO', '获取文本'), 'value': f'{text}'})
            return text

    @action_group(PlaywrightStepType.ElementAction, PlaywrightStepTypeName.ElementAction)
    def tag_name(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        获取标签名
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: list[str] or str 元素标签名, list[str] 多个元素, str 单个元素 标签内容
        """
        if element_index == -1:
            tag_name_list = []
            for element in self.locator(obj, element_index, timeout):
                tag_name_list.append(element.evaluate("el => el.tagName"))
            self._log.append({'title': formatter_log('INFO', '获取标签名'), 'value': f'{"-".join(tag_name_list)}'})
            return tag_name_list
        else:
            tag_name = self.locator(obj, element_index, timeout).evaluate("el => el.tagName")
            self._log.append({'title': formatter_log('INFO', '获取标签名'), 'value': f'{tag_name}'})
            return tag_name

    @action_group(PlaywrightStepType.ElementAction, PlaywrightStepTypeName.ElementAction)
    def get_attribute(self, obj: ElementSerializers, name: str, element_index: int = 0, timeout: int = 5):
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
            for element in self.locator(obj, element_index, timeout):
                attr_value_list.append(element.get_attribute(name))
            self._log.append({'title': formatter_log('INFO', '获取属性'), 'value': f'{"-".join(map(str, attr_value_list))}'})
            return attr_value_list
        else:
            attr_value = self.locator(obj, element_index, timeout).get_attribute(name)
            self._log.append({'title': formatter_log('INFO', '获取属性'), 'value': f'{attr_value}'})
            return attr_value

    @action_group(PlaywrightStepType.ElementAction, PlaywrightStepTypeName.ElementAction)
    def css_property(self, obj: ElementSerializers, name: str, element_index: int = 0, timeout: int = 5):
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
            for element in self.locator(obj, element_index, timeout):
                attr_value_list.append(element.evaluate(f"el => getComputedStyle(el).getPropertyValue('{name}')"))
            self._log.append({'title': formatter_log('INFO', '获取CSS属性'), 'value': f'{"-".join(attr_value_list)}'})
            return attr_value_list
        else:
            attr_value = self.locator(obj, element_index, timeout).evaluate(f"el => getComputedStyle(el).getPropertyValue('{name}')")
            self._log.append({'title': formatter_log('INFO', '获取CSS属性'), 'value': f'{attr_value}'})
            return attr_value

    @action_group(PlaywrightStepType.ElementAction, PlaywrightStepTypeName.ElementAction)
    def scroll_into_view_if_needed(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        将元素移动到屏幕可见区域
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        element = self.locator(obj, element_index, timeout)
        element.scroll_into_view_if_needed()
        self._log.append({'title': formatter_log('INFO', '将元素移动到屏幕可见区域'), 'value': '将元素移动到屏幕可见区域成功'})

    @action_group(PlaywrightStepType.ElementAction, PlaywrightStepTypeName.ElementAction)
    def is_visible(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        元素是否显示
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: list[bool] or bool 元素是否显示, True 显示, False 不显示
        """
        result_list = []
        if element_index == -1:
            for element in self.locator(obj, element_index, timeout):
                result_list.append(element.is_visible())
            self._log.append({'title': formatter_log('INFO', '元素是否显示'), 'value': f'{"-".join(map(str, result_list))}'})
            return result_list
        else:
            result = self.locator(obj, element_index, timeout).is_visible()
            self._log.append({'title': formatter_log('INFO', '元素是否显示'), 'value': f'{result}'})
            return result

    @action_group(PlaywrightStepType.ElementAction, PlaywrightStepTypeName.ElementAction)
    def is_enabled(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        元素是否可用
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: list[bool] or bool 元素是否可用, True 可用, False 不可用
        """
        if element_index == -1:
            result_list = []
            for element in self.locator(obj, element_index, timeout):
                result_list.append(element.is_enabled())
            self._log.append({'title': formatter_log('INFO', '元素是否可用'), 'value': f'{"-".join(map(str, result_list))}'})
            return result_list
        else:
            result = self.locator(obj, element_index, timeout).is_enabled()
            self._log.append({'title': formatter_log('INFO', '元素是否可用'), 'value': f'{result}'})
            return result

    @action_group(PlaywrightStepType.ElementAction, PlaywrightStepTypeName.ElementAction)
    def is_checked(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        元素是否选中
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: list[bool] or bool 元素是否选中, True 选中, False 非选中
        """
        result_list = []
        if element_index == -1:
            for element in self.locator(obj, element_index, timeout):
                result_list.append(element.is_checked())
            self._log.append({'title': formatter_log('INFO', '元素是否选中'), 'value': f'{"-".join(map(str, result_list))}'})
            return result_list
        else:
            result = self.locator(obj, element_index, timeout).is_checked()
            self._log.append({'title': formatter_log('INFO', '元素是否选中'), 'value': f'{result}'})
            return result

    @action_group(PlaywrightStepType.ElementAction, PlaywrightStepTypeName.ElementAction)
    def submit(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        提交表单
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.locator(obj, element_index, timeout):
                element.evaluate("el => el.submit()")
        else:
            self.locator(obj, element_index, timeout).evaluate("el => el.submit()")
        self._log.append({'title': formatter_log('INFO', '提交表单'), 'value': '提交表单成功'})

    # 鼠标操作
    @action_group(PlaywrightStepType.MouseAction, PlaywrightStepTypeName.MouseAction)
    def click_perform(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        鼠标单击
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.locator(obj, element_index, timeout):
                element.click()
        else:
            self.locator(obj, element_index, timeout).click()
        self._log.append({'title': formatter_log('INFO', '鼠标单击'), 'value': '鼠标单击成功'})

    @action_group(PlaywrightStepType.MouseAction, PlaywrightStepTypeName.MouseAction)
    def double_click(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        鼠标双击
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.locator(obj, element_index, timeout):
                element.dblclick()
        else:
            self.locator(obj, element_index, timeout).dblclick()
        self._log.append({'title': formatter_log('INFO', '鼠标双击'), 'value': f'鼠标双击成功'})

    @action_group(PlaywrightStepType.MouseAction, PlaywrightStepTypeName.MouseAction)
    def move_to_element(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        鼠标悬停
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.locator(obj, element_index, timeout):
                element.hover()
        else:
            self.locator(obj, element_index, timeout).hover()
        self._log.append({'title': formatter_log('INFO', '鼠标悬停'), 'value': f'鼠标悬停成功'})

    @action_group(PlaywrightStepType.MouseAction, PlaywrightStepTypeName.MouseAction)
    def context_click(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        右键点击
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        if element_index == -1:
            for element in self.locator(obj, element_index, timeout):
                element.click(button="right")
        else:
            self.locator(obj, element_index, timeout).click(button="right")
        self._log.append({'title': formatter_log('INFO', '右键点击'), 'value': '鼠标右键点击成功'})

    @action_group(PlaywrightStepType.MouseAction, PlaywrightStepTypeName.MouseAction)
    def click_and_hold(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        点击并按住
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        # playwright 无 click(down=True), 移动到元素中心后按下鼠标左键保持按住
        locator = self.locator(obj, element_index if element_index != -1 else 0, timeout)
        element = locator[0] if isinstance(locator, list) else locator
        box = element.bounding_box()
        mouse = self._current_page().mouse
        if box:
            mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        mouse.down()
        self._log.append({'title': formatter_log('INFO', '点击并按住'), 'value': '点击并按住成功'})

    @action_group(PlaywrightStepType.MouseAction, PlaywrightStepTypeName.MouseAction)
    def release(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        释放
        obj: 元素对象, 非必填，保留参数兼容已有步骤
        element_index: 元素索引, int, 非必填
        timeout: 查找元素超时时间, int, 非必填，默认5s
        return: None
        """
        # 释放当前按住的鼠标左键(与点击并按住配套使用, 无需定位元素)
        self._current_page().mouse.up()
        self._log.append({'title': formatter_log('INFO', '释放'), 'value': '释放成功'})

    @action_group(PlaywrightStepType.MouseAction, PlaywrightStepTypeName.MouseAction)
    def drag_and_drop(self, obj1: ElementSerializers, obj2: ElementSerializers, element1_index: int = 0,
                      element2_index: int = 0, timeout: int = 5):
        """
        拖放
        obj1: 元素对象, 必填
        obj2: 元素对象, 必填
        element1_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        element2_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找元素超时时间, int, 非必填，默认5s
        """
        source = self.locator(obj1, element1_index, timeout)
        target = self.locator(obj2, element2_index, timeout)
        source.drag_to(target)
        self._log.append({'title': formatter_log('INFO', '拖放'), 'value': f'拖放成功'})

    @action_group(PlaywrightStepType.MouseAction, PlaywrightStepTypeName.MouseAction)
    def drag_and_drop_by_offset(self, obj: ElementSerializers, element_index: int = 0, x_offset: int = 0,
                                y_offset: int = 0, timeout: int = 5):
        """
        拖放偏移
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        x_offset: x轴偏移量
        y_offset: y轴偏移量
        timeout: 查找元素超时时间, int, 必填，默认5s
        return: None
        """
        # playwright 无 drag_by, 通过鼠标事件模拟: 移动到元素中心 -> 按下 -> 拖动偏移 -> 释放
        locator = self.locator(obj, element_index if element_index != -1 else 0, timeout)
        element = locator[0] if isinstance(locator, list) else locator
        box = element.bounding_box()
        if not box:
            raise Exception('无法获取元素位置信息，拖放失败')
        mouse = self._current_page().mouse
        start_x = box['x'] + box['width'] / 2
        start_y = box['y'] + box['height'] / 2
        mouse.move(start_x, start_y)
        mouse.down()
        mouse.move(start_x + x_offset, start_y + y_offset, steps=10)
        mouse.up()
        self._log.append({'title': formatter_log('INFO', '拖放偏移'), 'value': f'拖放偏移({x_offset}, {y_offset})成功'})

    # 键盘操作
    @action_group(PlaywrightStepType.KeyboardAction, PlaywrightStepTypeName.KeyboardAction)
    def press_enter(self):
        """
        按回车键
        return: None
        """
        self.page.keyboard.press("Enter")
        self._log.append({'title': formatter_log('INFO', '按回车键'), 'value': f'按回车键成功'})

    @action_group(PlaywrightStepType.KeyboardAction, PlaywrightStepTypeName.KeyboardAction)
    def press_tab(self):
        """
        按Tab键
        return: None
        """
        self.page.keyboard.press("Tab")
        self._log.append({'title': formatter_log('INFO', '按Tab键'), 'value': f'按Tab键成功'})

    @action_group(PlaywrightStepType.KeyboardAction, PlaywrightStepTypeName.KeyboardAction)
    def press_esc(self):
        """
        按ESC键
        return: None
        """
        self.page.keyboard.press("Escape")
        self._log.append({'title': formatter_log('INFO', '按Esc键'), 'value': f'按Esc键成功'})

    @action_group(PlaywrightStepType.KeyboardAction, PlaywrightStepTypeName.KeyboardAction)
    def press_other(self, key_name: str):
        """
        按其他按键
        key_name: 键名称
        return: None
        """
        self.page.keyboard.press(key_name)
        self._log.append({'title': formatter_log('INFO', '按其他键'), 'value': f'{key_name}'})

    @action_group(PlaywrightStepType.KeyboardAction, PlaywrightStepTypeName.KeyboardAction)
    def press_ctrl_a(self):
        """
        按Ctrl+A
        return: None
        """
        self.page.keyboard.press("Control+A")
        self._log.append({'title': formatter_log('INFO', '按Ctrl+A'), 'value': f'按Ctrl+A成功'})

    @action_group(PlaywrightStepType.KeyboardAction, PlaywrightStepTypeName.KeyboardAction)
    def press_ctrl_c(self):
        """
        按Ctrl+C
        return: None
        """
        self.page.keyboard.press("Control+C")
        self._log.append({'title': formatter_log('INFO', '按Ctrl+C'), 'value': f'按Ctrl+C成功'})

    @action_group(PlaywrightStepType.KeyboardAction, PlaywrightStepTypeName.KeyboardAction)
    def press_ctrl_v(self):
        """
        按Ctrl+V
        return: None
        """
        self.page.keyboard.press("Control+V")
        self._log.append({'title': formatter_log('INFO', '按Ctrl+V'), 'value': f'按Ctrl+V成功'})

    # 弹窗操作
    @action_group(PlaywrightStepType.AlertHandling, PlaywrightStepTypeName.AlertHandling)
    def get_alert_text(self, timeout: int = 5):
        """
        获取弹窗文本内容
        timeout: 等待弹窗出现超时时间, int, 必填，默认5s
        return: str 弹框的文本内容
        """
        self._ensure_dialog(timeout)
        text = self._dialog_queue[0].message
        self._log.append({'title': formatter_log('INFO', '获取弹窗文本内容'), 'value': f'{text}'})
        return text

    @action_group(PlaywrightStepType.AlertHandling, PlaywrightStepTypeName.AlertHandling)
    def alert_accept(self, timeout: int = 5):
        """
        点击弹窗中的接受/确定按钮
        timeout: 等待弹窗出现超时时间, int, 必填，默认5s
        return: None
        """
        self._ensure_dialog(timeout)
        self._dialog_queue.pop(0).accept()
        self._log.append({'title': formatter_log('INFO', '点击弹窗中的接受/确定按钮'), 'value': '点击弹窗中的接受/确定按钮成功'})

    @action_group(PlaywrightStepType.AlertHandling, PlaywrightStepTypeName.AlertHandling)
    def alert_dismiss(self, timeout: int = 5):
        """
        点击弹框的取消/拒绝按钮
        timeout: 等待弹窗出现超时时间, int, 必填，默认5s
        return: None
        """
        self._ensure_dialog(timeout)
        self._dialog_queue.pop(0).dismiss()
        self._log.append({'title': formatter_log('INFO', '点击弹框的取消/拒绝按钮'), 'value': '点击弹框的取消/拒绝按钮成功'})

    @action_group(PlaywrightStepType.AlertHandling, PlaywrightStepTypeName.AlertHandling)
    def alert_send_keys(self, value: str, timeout: int = 5):
        """
        在弹框中输入内容
        value: 输入的内容
        timeout: 等待弹窗出现超时时间, int, 必填，默认5s
        return: None
        """
        self._ensure_dialog(timeout)
        self._dialog_queue.pop(0).accept(value)
        self._log.append({'title': formatter_log('INFO', '在弹框中输入内容'), 'value': f'{value}'})

    @action_group(PlaywrightStepType.JavaScriptExecution, PlaywrightStepTypeName.JavaScriptExecution)
    def execute_script(self, script: str):
        """
        执行js脚本
        script: 执行的脚本, str, 必填
        return None
        """
        self.page.evaluate(script)
        self.case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', 'Playwright关键字【execute_script】执行成功'),
                                                    'value': f'执行脚本：{script}'})

    def _build_locator(self, loc_method: str, loc_value: str, loc_opts: dict = None):
        """
        根据定位方式构建 playwright Locator（统一入口，按 playwright 推荐定位顺序）：
            role → label → placeholder → text → alt text → css → xpath → id

        role:        get_by_role(role, name=可见文本, exact=精确)
        label:       get_by_label(text, exact)
        placeholder: get_by_placeholder(text)
        text:        get_by_text(text, exact)
        alt text:    get_by_alt_text(text)
        css:         locator(css)
        xpath:       locator(xpath=...)
        id:          locator(#id)（playwright 将 id 归入 CSS）
        """
        loc_opts = loc_opts or {}
        loc_method = (loc_method or '').strip()

        # playwright 推荐的文本/角色类定位器（get_by_*）
        text_locator = {
            'role': lambda: self.page.get_by_role(
                loc_value,
                name=loc_opts.get('name') or None,
                exact=bool(loc_opts.get('exact', False)),
            ),
            'label': lambda: self.page.get_by_label(
                loc_value, exact=bool(loc_opts.get('exact', False))),
            'placeholder': lambda: self.page.get_by_placeholder(loc_value),
            'text': lambda: self.page.get_by_text(
                loc_value, exact=bool(loc_opts.get('exact', False))),
            'alt text': lambda: self.page.get_by_alt_text(loc_value),
        }
        if loc_method in text_locator:
            return text_locator[loc_method]()

        # 通用 locator 入口（playwright 推荐统一用 locator 处理 CSS/XPath/ID）
        if loc_method == 'css':
            return self.page.locator(loc_value)
        if loc_method == 'xpath':
            return self.page.locator(f"xpath={loc_value}")
        if loc_method == 'id':
            return self.page.locator(f"#{loc_value}")

        return self.page.locator(loc_value)

    def wait_element_located(self, obj: ElementSerializers, timeout: int = 5):
        """
        等待元素被加载到Dom树中，并且可见
        obj: 元素对象, 必填
        timeout: 超时时间, int, 非必填，默认5s
        return None
        """
        loc_method = obj['by']
        loc_value = obj['value']
        self._build_locator(loc_method, loc_value, obj.get('opts', {})).first.wait_for(state="visible", timeout=timeout*1000)

    @staticmethod
    def _update_loc(obj, ai_loc_by, ai_loc_value, ai_loc_opts=None):
        element_obj = Element.objects.get(id=obj['id'])
        element_obj.web = {
            'by': ai_loc_by,
            'value': ai_loc_value,
            'opts': ai_loc_opts or {'name': '', 'exact': False},
        }
        element_obj.save()

    def _get_driver_by_ai(self, obj):
        try:
            ai_loc_obj = generate_loc_path_by_ai(obj['name'], self.code, self.case_logs_obj)
            ai_loc_by, ai_loc_value = ai_loc_obj['by'],  ai_loc_obj['value']
            driver_obj = self._build_locator(ai_loc_by, ai_loc_value, ai_loc_obj.get('opts', {}))
            self._update_loc(obj, ai_loc_by, ai_loc_value, ai_loc_obj.get('opts'))
            return driver_obj
        except Exception as e:
            raise e

    def locator(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        查找元素列表
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素, -1 返回所有元素
        timeout: 查找元素超时时间, int, 必填，默认5s
        return list 元素对象列表
        """
        web_loc = obj['web']
        self._update_page_content()
        try:
            self.wait_element_located(web_loc, timeout)
            loc_method = web_loc['by']
            loc_value = web_loc['value']
            element_list = self._build_locator(loc_method, loc_value, web_loc.get('opts', {}))

            count = element_list.count()
            if element_index == -1:
                elements = []
                for i in range(count):
                    elements.append(element_list.nth(i))
                return elements
            elif count == 0 or element_index >= count:
                raise Exception("Element not found")
            else:
                return element_list.nth(element_index)
        except Exception as e:
            # Frame 无 screenshot 方法, 截图始终用顶层 Page
            screenshot_bytes = self._current_page().screenshot()
            base64_str = 'data:image/png;base64,' + base64.b64encode(screenshot_bytes).decode('utf-8')
            self._log.append({'title': formatter_log('ERROR', f'查找元素失败'), 'value': f'', 'uri': base64_str})
            return self._get_driver_by_ai(obj)

    def _update_page_content(self):
        self.code = self.page.content()
        match = re.search(r'<body.*?>.*?</body>', self.code, re.DOTALL)
        self.code = match.group() if match else self.code

    @action_group(PlaywrightStepType.Screenshots, PlaywrightStepTypeName.Screenshots)
    def screenshot(self):
        """
        屏幕截图
        return str
        """
        screenshot_bytes = self._current_page().screenshot()
        base64_str = 'data:image/png;base64,' + base64.b64encode(screenshot_bytes).decode('utf-8')
        self._log.append({'title': formatter_log('INFO', '屏幕截图'), 'value': f'', 'uri': base64_str})

    @action_group(PlaywrightStepType.CookiesManagement, PlaywrightStepTypeName.CookiesManagement)
    def add_cookie(self, cookie_value: dict):
        """
        添加cookie
        cookie_value: cookie值， dict类型， 必填
        return: None
        """
        self.context.add_cookies([cookie_value])
        cookie_value = json.dumps(cookie_value)
        self._log.append({'title': formatter_log('INFO', '添加cookie'), 'value': f'{cookie_value}'})

    @action_group(PlaywrightStepType.CookiesManagement, PlaywrightStepTypeName.CookiesManagement)
    def get_cookie(self, cookie_name: str):
        """
        获取cookie
        cookie_name: cookie名， str类型， 必填
        return: cookie的值
        """
        cookies = self.context.cookies()
        for cookie in cookies:
            if cookie['name'] == cookie_name:
                cookie_value = json.dumps(cookie)
                self._log.append({'title': formatter_log('INFO', '获取cookie'), 'value': f'{cookie_value}'})
                return cookie
        return None

    @action_group(PlaywrightStepType.CookiesManagement, PlaywrightStepTypeName.CookiesManagement)
    def get_cookies(self):
        """
        获取所有cookie
        return: list 所有cookie的值
        """
        cookies = self.context.cookies()
        cookie_value = json.dumps(cookies)
        self._log.append({'title': formatter_log('INFO', '获取所有cookie'), 'value': f'{cookie_value}'})
        return cookies

    @action_group(PlaywrightStepType.CookiesManagement, PlaywrightStepTypeName.CookiesManagement)
    def delete_cookie(self, cookie_name: str):
        """
        删除指定cookie
        cookie_name： str cookie名称
        return: None
        """
        cookies = self.context.cookies()
        for cookie in cookies:
            if cookie['name'] == cookie_name:
                self.context.clear_cookies(name=cookie_name)
                break
        self._log.append({'title': formatter_log('INFO', '删除指定cookie'), 'value': f'删除指定cookie成功'})

    @action_group(PlaywrightStepType.CookiesManagement, PlaywrightStepTypeName.CookiesManagement)
    def delete_cookies(self):
        """
        删除所有cookies
        obj: 元素对象, 必填
        return: None
        """
        self.context.clear_cookies()
        self._log.append({'title': formatter_log('INFO', '删除所有cookies'), 'value': f'删除所有cookies成功'})

    @action_group(PlaywrightStepType.WindowSwitching, PlaywrightStepTypeName.WindowSwitching)
    def switch_frame(self, obj: ElementSerializers, element_index: int = 0, timeout: int = 5):
        """
        进入指定frame
        obj: 元素对象, 必填
        element_index: 元素索引, int, 非必填，默认0，用于获取指定索引的元素
        timeout: 查找Frame元素超时时间, int, 非必填，默认5s
        return: None
        """
        locator = self.locator(obj, element_index if element_index != -1 else 0, timeout)
        element = locator[0] if isinstance(locator, list) else locator
        frame_content = element.element_handle().content_frame()
        if not frame_content:
            raise Exception('该元素不是frame/iframe，无法进入')
        self.page = frame_content
        self._log.append({'title': formatter_log('INFO', '进入指定frame'), 'value': '进入指定frame成功'})

    @action_group(PlaywrightStepType.WindowSwitching, PlaywrightStepTypeName.WindowSwitching)
    def exit_frame(self):
        """
        退出frame
        return: None
        """
        # self.page 可能是 Frame(有 parent_frame) 或顶层 Page(没有该属性)
        parent_frame = getattr(self.page, 'parent_frame', None)
        if parent_frame:
            self.page = parent_frame
            self._log.append({'title': formatter_log('INFO', '退出frame'), 'value': '退出frame成功'})
        else:
            self._log.append({'title': formatter_log('INFO', '退出frame'), 'value': '当前已是顶层页面，无需退出'})

    @action_group(PlaywrightStepType.WindowSwitching, PlaywrightStepTypeName.WindowSwitching)
    def get_current_window_name(self):
        """
        获取当前窗口句柄的名称
        return: str 当前窗口句柄的名称
        """
        self._register_windows()
        current_page = self._current_page()
        window_handle = None
        for handle, page in self._window_registry.items():
            if page is current_page:
                window_handle = handle
                break
        if window_handle is None:
            raise Exception('当前窗口不存在或已关闭')
        self._log.append({'title': formatter_log('INFO', '获取当前窗口句柄的名称'), 'value': f'{window_handle}'})
        return window_handle

    @action_group(PlaywrightStepType.WindowSwitching, PlaywrightStepTypeName.WindowSwitching)
    def switch_window(self, window_name: str):
        """
        切换到指定窗口
        window_name: 窗口句柄的名称
        return: None
        """
        self._register_windows()
        page = self._window_registry.get(window_name)
        if not page:
            raise Exception(f'窗口句柄 {window_name} 不存在，当前所有窗口: {list(self._window_registry.keys())}')
        self.page = page
        self._log.append({'title': formatter_log('INFO', '切换到指定窗口'), 'value': f'切换到窗口：{window_name}'})

    @action_group(PlaywrightStepType.WindowSwitching, PlaywrightStepTypeName.WindowSwitching)
    def get_window_handles(self):
        """
        获取所有窗口句柄
        return: list 所有窗口句柄的列表
        """
        self._register_windows()
        window_handles = list(self._window_registry.keys())
        self._log.append({'title': formatter_log('INFO', '获取所有窗口句柄'), 'value': f'{window_handles}'})
        return window_handles

    @action_group(PlaywrightStepType.WindowSwitching, PlaywrightStepTypeName.WindowSwitching)
    def switch_to_new_window(self):
        """
        切换到新打开的窗口
        return: None
        """
        known_pages = list(self._window_registry.values())
        new_pages = [page for page in self.context.pages
                     if not any(page is known for known in known_pages)]
        if new_pages:
            self._register_windows()
            target_page = new_pages[-1]
            for handle, page in self._window_registry.items():
                if page is target_page:
                    self.page = page
                    self._log.append({'title': formatter_log('INFO', '切换到新打开的窗口'),
                                      'value': f'切换到新窗口：{handle}'})
                    return
        # 无新窗口时退回最后一个页面
        pages = self.context.pages
        if len(pages) > 0:
            self.page = pages[-1]
        self._log.append({'title': formatter_log('INFO', '切换到新打开的窗口'), 'value': '切换到新打开的窗口成功'})


playwright_actions = [{
                    'id': key,
                    'script': inspect.getsource(value),
                    'params': get_function_params(value),
                    'name': [new_str.strip() for new_str in value.__doc__.strip().split('\n')][0],
                    'group': value.__dict__.get('group_id'),
                    'group_name': value.__dict__.get('group_name')}
                    for key, value in PlaywrightBaseAction.__dict__.items()
                    if not key.startswith('_')]

playwright_func_map = {key: value for key, value in PlaywrightBaseAction.__dict__.items()
                       if not key.startswith('_')}

playwright_func_doc = {key: [new_str.strip() for new_str in value.__doc__.strip().split('\n')]
                       for key, value in PlaywrightBaseAction.__dict__.items()
                       if not key.startswith('_')}


def run_step_playwright(manager_obj, env_id, step, case_params, case_logs_obj, run_times, run_element):
    step_id = step["case_step_id"]
    plant_id = step['plant']
    env_plant_query = EnvPlant.objects.all().filter(env=env_id, plant=plant_id, is_delete=False)
    if not env_plant_query.exists():
        raise EnvPlantNotExistException()
    host = env_plant_query[0].host
    func_params = func_list_to_dict(step['func_params'], {}, case_params, case_logs_obj)
    
    case_params.stepResponse[f'{step_id}']['runTimes'] = run_times
    case_params.stepResponse[f'{step_id}']['runElement'] = run_element
    keyword = step['keyword']
    case_params.stepResponse[f'{step_id}']['funcParams'] = func_params
    
    if host not in manager_obj.driver_manager and host is not None:
        manager_obj.driver_manager[host] = PlaywrightBaseAction(case_params, case_logs_obj, host, plant_id,
                                                                manager_obj, step_id)
    exec_and_return(manager_obj, step['setup'], case_logs_obj, formatter_log, case_params, sys_function)

    return_value = playwright_func_map[keyword](manager_obj.driver_manager[host], **func_params)
    case_params.stepResponse[f'{step_id}']['funcReturn'] = return_value
    exec_and_return(manager_obj, step['teardown'], case_logs_obj, formatter_log, case_params, sys_function)

    # 执行步骤的断言参数,如果步骤中有断言数据则忽略接口的断言数据
    loop_assert_by_check_list(step['check_params'], case_params, case_logs_obj)