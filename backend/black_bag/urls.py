from django.contrib import admin
from django.conf import settings
from black_bag.settings import MEDIA_URL, MEDIA_ROOT
from django.conf.urls.static import static
from apps.interfaces import views
from django.urls import path, include, re_path
from django.views.static import serve as static_serve
from django.views.decorators.clickjacking import xframe_options_exempt
import os
import playwright

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.users.urls')),
    path('', include('apps.projects.urls')),
    path('', include('apps.envs.urls')),
    path('', include('apps.interfaces.urls')),
    path('', include('apps.scripts.urls')),
    path('', include('apps.tests.urls')),
    path('', include('apps.elements.urls')),
    path('', include('apps.suites.urls')),
    path('', include('apps.reports.urls')),
    path('', include('apps.defects.urls')),
    path('', include('apps.tools.urls')),
    path('', include('apps.messages.urls')),
    path('', include('apps.ai_service.urls')),
    path('', include('apps.audit.urls')),
    re_path(r'^api_mock(?P<sub_path>.*)$', views.api_mock_view),
    path('restframework/', include('rest_framework.urls')),
]

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)

# Playwright Trace 回放: trace zip 文件下载 + 官方 traceViewer 静态资源
# traceViewer 来自后端镜像内 playwright 包, 与录制版本严格一致
# viewer 页面经 iframe 嵌入前端(跨端口), 需豁免 X-Frame-Options SAMEORIGIN
TRACE_FILES_DIR = os.path.join(str(MEDIA_ROOT), 'traces')
TRACE_VIEWER_DIR = os.path.join(os.path.dirname(playwright.__file__), 'driver', 'package', 'lib', 'vite', 'traceViewer')


@xframe_options_exempt
def traceviewer_serve(request, path):
    return static_serve(request, path, document_root=TRACE_VIEWER_DIR)


def traces_serve(request, path):
    return static_serve(request, path, document_root=TRACE_FILES_DIR)


urlpatterns += [
    re_path(r'^traces/(?P<path>.*)$', traces_serve),
    re_path(r'^traceviewer/(?P<path>.*)$', traceviewer_serve),
]
