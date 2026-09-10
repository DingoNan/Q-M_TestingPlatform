from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.ai_service import views

route = DefaultRouter()
route.register('ai/conversations', views.AiConversationViewSet, basename='ai-conversation')
route.register('vectorstore', views.VectorStoreViewSet, basename='vectorstore')

urlpatterns = [
    path('', include(route.urls)),
]
