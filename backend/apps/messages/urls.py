from rest_framework.routers import DefaultRouter
from django.urls import path, include

from apps.messages import views

route = DefaultRouter()
route.register('message', views.MessageViewSet)

urlpatterns = [
    path('message/unread-count/', views.unread_count, name='message-unread-count'),
    path('', include(route.urls)),
]