from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.interfaces import views


router = DefaultRouter()
router.register('api', views.ApiViewSet)
router.register('mock', views.ApiMockViewSet)

urlpatterns = [
    path('interface/', include(router.urls), name='interface'),
    path('json_to_list/', views.json_obj_to_list),
    path('import_api/', views.import_api),
    path('import_api_v2/', views.import_api_v2),
    path('har_preview/', views.har_preview),
    # ★ 2026-09-22 新增：同步版 HAR 导入，回传落库接口 id（按真实发起顺序）
    #   供「用例内 HAR 导入」拿到 id 后接着调 /test/add_many_api_step/ 建步骤
    path('import_har_sync/', views.import_har_sync),
    path('api_run/', views.api_run),
    path('mock_api_run/', views.mock_api_run),
]


