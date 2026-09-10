from django_filters import rest_framework

from apps.scripts.models import PythonScript, EnumScript, File


class PythonScriptFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    module = rest_framework.BaseInFilter(lookup_expr='in')

    class Meta:
        model = PythonScript
        fields = '__all__'


class EnumScriptFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')
    module = rest_framework.BaseInFilter(lookup_expr='in')

    class Meta:
        model = EnumScript
        fields = ['name', 'module', 'create_by', 'update_by', 'project']


class FileFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = File
        fields = ['name', 'project', 'create_by', 'update_by']
