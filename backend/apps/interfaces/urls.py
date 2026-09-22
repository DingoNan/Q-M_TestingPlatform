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
    # ★ 2026-09-22 新增：HAR 轨迹 → 规则式分析 → LLM 归因（阶段一最小闭环）
    #   规则式 _har_analyze 给事实，LLM 做业务归因与用例草稿，两条链在此汇合
    path('har_analyze_ai/', views.har_analyze_ai),
    path('api_run/', views.api_run),
    path('mock_api_run/', views.mock_api_run),
]


