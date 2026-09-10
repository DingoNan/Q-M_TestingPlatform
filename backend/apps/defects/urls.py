from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.defects import views

route = DefaultRouter()
route.register('defect', views.DefectViewSet, basename='defect')
route.register('defect_comment', views.DefectCommentViewSet, basename='defect_comment')

urlpatterns = [
    path('defect/', include(route.urls), name='defect'),
]
