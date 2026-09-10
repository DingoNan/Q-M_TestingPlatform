import os
import base64
from rest_framework.permissions import IsAuthenticated

from utils.base import BasePageNumberPagination
from apps.scripts.filters import PythonScriptFilter, EnumScriptFilter, FileFilter
from apps.scripts.models import PythonScript, EnumScript, File
from apps.scripts.serializers import PythonScriptSerializers, EnumScriptSerializers, FileSerializers
from utils.base_view import BaseModelViewSet
from black_bag.settings import BASE_DIR


class PythonScriptViewSet(BaseModelViewSet):
    serializer_class = PythonScriptSerializers
    queryset = PythonScript.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = PythonScriptFilter


class EnumScriptViewSet(BaseModelViewSet):
    serializer_class = EnumScriptSerializers
    queryset = EnumScript.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = EnumScriptFilter


class FileViewSet(BaseModelViewSet):
    serializer_class = FileSerializers
    queryset = File.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = FileFilter

    def create(self, request, *args, **kwargs):
        file_raw = request.data.pop('raw')
        project = request.data.get('project')
        dir_path = os.path.join(os.path.join(BASE_DIR, 'data'), str(project))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        file_data = base64.b64decode(file_raw)

        # 写入文件
        with open(os.path.join(dir_path, request.data.get('name')), 'wb') as file:
            file.write(file_data)
        response = super(FileViewSet, self).create(request, *args, **kwargs)
        return response

    def destroy(self, request, *args, **kwargs):
        file_id = self.kwargs.get('pk')
        file_obj = File.objects.get(id=file_id)
        dir_path = os.path.join(os.path.join(BASE_DIR, 'data'), str(file_obj.project.id))
        if os.path.exists(os.path.join(dir_path, file_obj.name)):
            os.remove(os.path.join(dir_path, file_obj.name))
        response = super().destroy(request, *args, **kwargs)
        return response