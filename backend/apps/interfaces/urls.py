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
    path('api_run/', views.api_run),
    path('mock_api_run/', views.mock_api_run),
]


