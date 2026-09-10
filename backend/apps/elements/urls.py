from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.elements import views

route = DefaultRouter()
route.register('', views.ElementViewSet)


urlpatterns = [
    path('element/', include(route.urls), name='element'),
    path('import_element/', views.import_element),
    path('ai_generate_elements/', views.ai_generate_elements),
]
