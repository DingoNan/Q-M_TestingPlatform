from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.envs import views

route = DefaultRouter()
route.register('env', views.EnvViewSet)
route.register('params', views.EnvGlobalParamsSet)
route.register('global', views.GlobalParamsSet)
route.register('service', views.ServiceViewSet)
route.register('db', views.DbViewSet)
route.register('env_service', views.EnvServiceViewSet)
route.register('env_db', views.EnvDbViewSet)
route.register('plant', views.PlantViewSet)
route.register('env_plant', views.EnvPlantViewSet)
route.register('module', views.ModuleViewSet)
route.register('service_module', views.ServiceModuleViewSet)
route.register('page', views.PageViewSet)
route.register('header', views.HeadersViewSet)
route.register('cookie', views.CookiesViewSet)
route.register('web_executor', views.EnvWebExecutorViewSet)
route.register('app_executor', views.EnvAppExecutorViewSet)


urlpatterns = [
    path('env/', include(route.urls), name='env'),
    path('env/allPlantModule/', views.get_all_plant_module, name='all_plant_module'),
    path('env/allServiceModule/', views.get_all_service_module, name='all_service_module'),
    path('env/allPlantModuleTwo/', views.get_all_plant_module_two, name='all_plant_module_two'),
    path('env/allServiceModuleTwo/', views.get_all_service_module_two, name='all_service_module_two'),
    path('env/allPlantModuleCase/', views.get_all_plant_module_case, name='all_plant_module_case'),
    path('env/allModulePage/', views.get_all_plant_module_page, name='all_plant_module_page'),
    path('env/allPlantElement/', views.get_all_plant_element, name='all_plant_element'),
    path('env/get_request_host/', views.get_request_host, name='get_request_host'),

]
