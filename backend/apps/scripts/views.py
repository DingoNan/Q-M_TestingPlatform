import os
import base64
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
        # 之前用 pop('raw')，字段缺失时直接 KeyError -> 500；改为取值 + 显式校验
        file_raw = request.data.get('raw')
        if not file_raw:
            return Response({'raw': ['文件内容不能为空']}, status=400)
        project = request.data.get('project')
        if not project:
            return Response({'project': ['项目ID不能为空']}, status=400)
        if not request.data.get('name'):
            return Response({'name': ['文件名称不能为空']}, status=400)

        dir_path = os.path.join(os.path.join(BASE_DIR, 'data'), str(project))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        try:
            file_data = base64.b64decode(file_raw)
        except Exception:
            return Response({'raw': ['文件内容不是合法的 base64 编码']}, status=400)

        # 写入文件
        file_name = os.path.basename(str(request.data.get('name')))
        with open(os.path.join(dir_path, file_name), 'wb') as file:
            file.write(file_data)

        # 只把序列化器需要的字段传进去，raw 属于上传辅助字段不落库
        payload = {k: v for k, v in request.data.items() if k != 'raw'}
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def destroy(self, request, *args, **kwargs):
        file_id = self.kwargs.get('pk')
        file_obj = File.objects.filter(id=file_id).first()
        if file_obj is None:
            return Response({'detail': '文件不存在'}, status=404)
        dir_path = os.path.join(os.path.join(BASE_DIR, 'data'), str(file_obj.project.id))
        if os.path.exists(os.path.join(dir_path, file_obj.name)):
            os.remove(os.path.join(dir_path, file_obj.name))
        response = super().destroy(request, *args, **kwargs)
        return response