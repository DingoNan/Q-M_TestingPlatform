from utils.base import BaseSerializer
from apps.elements.models import Element

from rest_framework import serializers


class ElementSerializers(BaseSerializer):
    module_id = serializers.CharField(source='module.id', read_only=True)
    module_name = serializers.CharField(source='module.name', read_only=True)
    # page_url = serializers.CharField(source='page.url', read_only=True)
    # module_name = serializers.CharField(source='page.module.name', read_only=True)
    plant_name = serializers.CharField(source='page.module.plant.name', read_only=True)
    plant_id = serializers.CharField(source='page.module.plant.id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Element
        fields = '__all__'
