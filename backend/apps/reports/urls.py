from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.reports import views

route = DefaultRouter()
route.register('func', views.ReportViewSet)
route.register('locust', views.LocustReportViewSet)


urlpatterns = [
    path('report/', include(route.urls), name='report'),
]
