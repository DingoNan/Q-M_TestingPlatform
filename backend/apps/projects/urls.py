from rest_framework.routers import DefaultRouter
from django.urls import path, include

from apps.projects import views

route = DefaultRouter()
route.register('projects', views.ProjectViewSet)
route.register('ai_model_setting', views.AiConfigViewSet)
route.register('project_appeal', views.ProjectAppealViewSet)
route.register('project_msg_push', views.ProjectMsgPushViewSet)
route.register('project_general_setting', views.ProjectGeneralSettingViewSet)
route.register('project_members', views.ProjectMemberViewSet)

# urlpatterns = route.urls


urlpatterns = [
    path('', include(route.urls), name='project'),
    path('check_permission/', views.check_project_permission, name='check_project_permission'),
]
