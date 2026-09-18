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
        # 【健壮性修复】用户函数体由用户在界面上自由书写，语法错误 / 函数名不匹配 /
        # 未标注入参类型 / 注解类型不在 ParamsTypeMap 中，都会在反序列化响应体时抛异常。
        # 旧实现让异常直接冒到 DRF，前端只能看到「系统内部异常」，用户无从下手。
        # 这里统一转成 400 + 可读原因，指明具体是哪一类问题。
        namespace = {}
        try:
            exec(obj.script, namespace)
        except Exception as e:
            raise ValidationError('函数体语法错误，无法解析：%s: %s' % (e.__class__.__name__, e))
        if obj.name not in namespace:
            raise ValidationError('函数体中未找到名为「%s」的函数，请保持函数名与函数体一致' % obj.name)
        try:
            params = get_function_params(namespace[obj.name])
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError('函数入参解析失败：%s: %s' % (e.__class__.__name__, e))
        return params

    def validate(self, attrs):
        name = attrs.get('name')
        script = attrs.get('script')
        pattern = r'^\s*def\s+([a-zA-Z_]\w*)\s*\('
        match_func_name = None
        # 【缺陷修复】原正则 r'def\s+[a-zA-Z_]\w*\s*\(([\s\S]*?)\)\s*:' 要求
        # 右括号后紧跟冒号。当函数带返回值类型注解（def f(x: str) -> str:）时，
        # 括号后是 '-> str' 而非 ':'，正则匹配为空列表，导致下方 for 循环中
        # 的 params 变量从未被赋值 -> UnboundLocalError -> 接口 500（且无友好提示）。
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

        # 【健壮性修复①】默认空列表，避免正则无匹配时 params 未定义引发 UnboundLocalError。
        # 【健壮性修复②】改为「逐行」匹配：原实现对整个 script 做 re.findall，
        # 由于 [\s\S]*? 可跨行，当 def 行本身匹配不上时会一路吞到后面某个 ')' ，
        # 把 docstring、函数体正文统统当成入参说明写进 params，静默产生错误数据。
        # 函数签名必然在单行内（def 行），因此逐行匹配既能命中，也不会跨行误捕获。
        params = []
        for raw_line in script.splitlines():
            line = raw_line.split('#')[0]
            params_matches = re.findall(params_pattern, line)
            for param_list in params_matches:
                # 移除多余空格
                param_list = ' '.join(param_list.split())
                if not param_list:
                    continue
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