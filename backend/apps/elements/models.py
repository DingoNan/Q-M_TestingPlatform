from django.db import models
from utils.base import BaseModel
from appium.webdriver.common.appiumby import AppiumBy
from simple_history.models import HistoricalRecords


class Element(BaseModel):

    class ElementStatus(models.IntegerChoices):
        TO_MODIFY = 0, '待修改'
        PUBLISHED = 1, '已发布'
        TO_DEPRECATE = 2, '待废弃'

    class SourceChoice(models.TextChoices):
        """元素来源 —— 区分「手工建的」与「录制/AI 产的」，便于治理。"""
        MANUAL = 'manual', '手工创建'
        RECORDED = 'recorded', '录制生成'
        AI = 'ai', 'AI 生成'

    class ByChoice(models.TextChoices):
        # Web 端：Playwright 定位方式
        ID = 'id', 'id'
        XPATH = 'xpath', 'xpath'
        CSS = 'css', 'css'
        TEXT = 'text', 'text'
        PLACEHOLDER = 'placeholder', 'placeholder'
        ROLE = 'role', 'role'
        LABEL = 'label', 'label'
        ALT_TEXT = 'alt text', 'alt text'
        # App 端：Appium 定位方式
        IOS_PREDICATE = AppiumBy.IOS_PREDICATE, '-ios predicate string'
        IOS_CLASS_CHAIN = AppiumBy.IOS_CLASS_CHAIN, '-ios class chain'
        ANDROID_UIAUTOMATOR = AppiumBy.ANDROID_UIAUTOMATOR, '-android uiautomator'
        ANDROID_VIEWTAG = AppiumBy.ANDROID_VIEWTAG, '-android viewtag'
        ANDROID_DATA_MATCHER = AppiumBy.ANDROID_DATA_MATCHER, '-android datamatcher'
        ANDROID_VIEW_MATCHER = AppiumBy.ANDROID_VIEW_MATCHER, '-android viewmatcher'
        ACCESSIBILITY_ID = AppiumBy.ACCESSIBILITY_ID, 'accessibility id'
        IMAGE = AppiumBy.IMAGE, '-image'
        CUSTOM = AppiumBy.CUSTOM, '-custom'
        FLUTTER_INTEGRATION_SEMANTICS_LABEL = AppiumBy.FLUTTER_INTEGRATION_SEMANTICS_LABEL, '-flutter semantics label'
        FLUTTER_INTEGRATION_TYPE = AppiumBy.FLUTTER_INTEGRATION_TYPE, '-flutter type'
        FLUTTER_INTEGRATION_KEY = AppiumBy.FLUTTER_INTEGRATION_KEY, '-flutter key'
        FLUTTER_INTEGRATION_TEXT = AppiumBy.FLUTTER_INTEGRATION_TEXT, '-flutter text'
        FLUTTER_INTEGRATION_TEXT_CONTAINING = AppiumBy.FLUTTER_INTEGRATION_TEXT_CONTAINING, '-flutter text containing'

    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    module = models.ForeignKey('envs.Module', on_delete=models.PROTECT)
    name = models.CharField(verbose_name='元素名称', max_length=50)
    type = models.CharField(verbose_name='元素类型', default='web', max_length=20)
    web = models.JSONField(verbose_name='web', default=list)
    ios = models.JSONField(verbose_name='ios', default=list)
    android = models.JSONField(verbose_name='android', default=list)
    status = models.IntegerField(verbose_name='元素状态',
                                 choices=ElementStatus.choices,
                                 default=ElementStatus.PUBLISHED)

    # ==================== P3 元素健康度（自愈与治理） ====================
    # ★ 以下计数字段由执行期自动维护，**不要手工改**：
    #   core/step/run_playwright.py::locator() → _bump_element_counter()
    #   一律用 Django F() 表达式原子自增（读-改-写在并发下会丢更新），
    #   且计数失败必须被吞掉 —— 计数是旁路，绝不能影响用例执行结果。
    #
    # 治理指标：degrade_rate = fallback_count / (hit_count + fallback_count)
    #   → 持续上升说明主定位已失效，应提示重新录制/修正定位器。
    source = models.CharField(verbose_name='元素来源', max_length=16,
                              choices=SourceChoice.choices,
                              default=SourceChoice.MANUAL)
    hit_count = models.IntegerField(verbose_name='主定位命中次数', default=0)
    fallback_count = models.IntegerField(verbose_name='降级命中次数', default=0)
    fail_count = models.IntegerField(verbose_name='定位失败次数', default=0)

    history = HistoricalRecords()

    class Meta:
        ordering = ['-create_time']
        db_table = 'tb_element'
        verbose_name = '元素表'
        verbose_name_plural = verbose_name
