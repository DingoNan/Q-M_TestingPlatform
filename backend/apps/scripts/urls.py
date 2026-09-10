from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.scripts import views

route = DefaultRouter()
route.register('python', views.PythonScriptViewSet)
route.register('enum', views.EnumScriptViewSet)
route.register('file', views.FileViewSet)


urlpatterns = [
    path('script/', include(route.urls), name='python'),
]
