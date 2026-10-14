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
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    # ★ P3 元素健康度：fallback / (hit + fallback)，分母为 0 记 0.0。
    #   用 SerializerMethodField 而不是 FloatField —— 普通列表接口不带该 annotation，
    #   用 getattr 兜底可保证「非 health 接口也永远不报错」。
    degrade_rate = serializers.SerializerMethodField()

    def get_degrade_rate(self, obj):
        value = getattr(obj, 'degrade_rate', None)
        if value is None:
            return 0.0
        try:
            return round(float(value), 4)
        except (TypeError, ValueError):
            return 0.0

    class Meta:
        model = Element
        fields = '__all__'
