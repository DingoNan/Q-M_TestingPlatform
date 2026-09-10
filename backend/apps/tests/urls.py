from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.tests import views

route = DefaultRouter()
route.register('case', views.CaseViewSet)
route.register('func_case', views.FuncCaseViewSet)
route.register('caseDetail', views.CaseDetailViewSet, basename='case_detail')
route.register('step', views.StepViewSet)
route.register('logs', views.CaseRunLogsViewSet)
route.register('tag', views.TagViewSet)
route.register('casesteps', views.CaseStepsViewSet)


urlpatterns = [
    path('test/', include(route.urls), name='test'),
    path('test/actions/', views.action_keys),
    path('test/selenium/', views.get_selenium_keys),
    path('test/playwright/', views.get_playwright_keys),
    path('test/func_cases/', views.get_logs_by_report),
    path('test/get_locust_run_data', views.get_locust_run_data),
    path('test/appium/', views.get_appium_keys),
    path('test/funcs/', views.function_keys),
    path('test/run/', views.case_run),
    path('test/step_run/', views.step_run),
    path('test/locust_run/', views.locust_run),
    path('test/init_data/', views.get_init_data),
    path('test/download/windows', views.download_windows),
    path('test/download/linux', views.download_linux),
    path('test/download/macos', views.download_macos),
    path('test/copyCase/', views.copy_case),
    path('test/update_is_run/', views.update_step_is_run),
    path('test/change_step_index/', views.change_step_index),
    path('test/check/', views.get_check_list),
    path('test/system_function_doc/', views.get_system_function_params_doc),
    path('test/run_system_function/', views.run_system_function),
    path('test/run_user_function/', views.run_user_function),
    path('test/add_many_step/', views.add_many_step_for_case),

]
