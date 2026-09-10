import logging
from django.apps import AppConfig

logger = logging.getLogger('ai_service')


class AiServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_service'
    verbose_name = 'AI测试服务'

    def ready(self):
        """注册向量库同步信号。

        Embedding 模型改为纯懒加载（首次真正写入/检索时才加载一次），
        不要在 worker 启动时预加载：每 worker 单独预加载会占用大量内存，
        且后台线程初始化 embedding 曾导致 gunicorn 启动死锁、接口无响应。
        """
        import apps.ai_service.signals  # noqa: F401 - 导入以触发信号注册
