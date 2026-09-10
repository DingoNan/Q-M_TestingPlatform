from django.db import models
from utils.base import BaseModel
from appium.webdriver.common.appiumby import AppiumBy
from simple_history.models import HistoricalRecords


class Element(BaseModel):

    class ElementStatus(models.IntegerChoices):
        TO_MODIFY = 0, '待修改'
        PUBLISHED = 1, '已发布'
        TO_DEPRECATE = 2, '待废弃'

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

    history = HistoricalRecords()

    class Meta:
        ordering = ['-create_time']
        db_table = 'tb_element'
        verbose_name = '元素表'
        verbose_name_plural = verbose_name
