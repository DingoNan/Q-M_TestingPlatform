from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tools.views import tool_id_card_view


urlpatterns = [
    path('tools/id_card', tool_id_card_view, name='tool_id_card'),
]
