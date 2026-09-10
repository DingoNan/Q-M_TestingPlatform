from django_filters import rest_framework

from apps.elements.models import Element


class ElementFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    module = rest_framework.BaseInFilter(lookup_expr='in')

    class Meta:
        model = Element
        fields = ['name', 'project', 'module', 'id', 'type', 'status', 'create_by', 'update_by']
