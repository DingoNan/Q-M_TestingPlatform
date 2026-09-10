from rest_framework.routers import DefaultRouter
from django.urls import path, include

from apps.suites import views

route = DefaultRouter()
route.register('suite', views.SuiteViewSet, basename='suite')
route.register('task', views.CrontabTaskView, basename='task')
route.register('plan', views.TestPlanViewSet, basename='plan')
route.register('plan_case', views.TestPlanFuncCaseViewSet, basename='plan_case')
route.register('plan_case_comment', views.TestPlanFuncCaseCommentViewSet, basename='plan_case_comment')


urlpatterns = [
    path('suite/run/', views.run_suite_case),
    path('', include(route.urls), name='suite'),
]
