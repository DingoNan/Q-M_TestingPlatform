import re
from rest_framework.serializers import ValidationError
from rest_framework import serializers
from utils.base import BaseSerializer
from apps.scripts.models import PythonScript, EnumScript, File
from core.com.common import get_function_params


class PythonScriptSerializers(BaseSerializer):
    module_name = serializers.CharField(source='module.name', read_only=True)
    plant_name = serializers.CharField(source='module.plant.name', read_only=True)
    params = serializers.SerializerMethodField()

    class Meta:
        model = PythonScript
        fields = '__all__'

    def get_params(self, obj):
        namespace = {}
        exec(obj.script, namespace)
        params = get_function_params(namespace[obj.name])
        return params

    def validate(self, attrs):
        name = attrs.get('name')
        script = attrs.get('script')
        pattern = r'^\s*def\s+([a-zA-Z_]\w*)\s*\('
        match_func_name = None
        # 【缺陷修复】原正则 r'def\s+[a-zA-Z_]\w*\s*\(([\s\S]*?)\)\s*:' 要求
        # 右括号后紧跟冒号。当函数带返回值类型注解（def f(x: str) -> str:）时，
        # 括号后是 '-> str' 而非 ':'，正则匹配为空列表，导致下方 for 循环中
        # 的 params 变量从未被赋值 -> NameError -> 接口 500（且无友好提示）。
        # 现放宽为：允许右括号后存在任意返回值注解，再以冒号结尾。
        params_pattern = r'def\s+[a-zA-Z_]\w*\s*\(([\s\S]*?)\)\s*(?:->\s*[^:]+)?:'

        if name.startswith('faker'):
            raise ValidationError('函数名不能以系统函数名faker开头')

        for line in script.splitlines():
            line = line.split('#')[0].strip()  # 移除注释
            match = re.search(pattern, line)
            if match:
                match_func_name = match.group(1)
        if match_func_name is None:
            raise ValidationError('函数体中函数命名不规范')
        if match_func_name != name:
            raise ValidationError('函数名称请和函数体中的函数名称保持一致')

        # 【健壮性修复】默认空列表，避免正则无匹配时 params 未定义引发 NameError
        params = []
        params_matches = re.findall(params_pattern, script)
        for param_list in params_matches:
            # 移除换行符和多余空格
            param_list = ' '.join(param_list.split())
            # 按逗号拆分参数
            params = [p.strip() for p in param_list.split(',')]

        for params_key in params:
            if ':' not in params_key and params_key != '':
                raise ValidationError(f'{params_key} : 函数入参请标注入参类型')

        return attrs


class EnumScriptSerializers(BaseSerializer):
    module_name = serializers.CharField(source='module.name', read_only=True)
    plant_name = serializers.CharField(source='module.plant.name', read_only=True)

    class Meta:
        model = EnumScript
        fields = '__all__'


class FileSerializers(BaseSerializer):

    class Meta:
        model = File
        fields = '__all__'

    def validate(self, attrs):
        if not self.instance:
            name = attrs.get('name')
            project = attrs.get('project')
            if File.objects.filter(project=project, name=name, is_delete=False).exists():
                raise ValidationError('文件名称已存在')
        return attrs