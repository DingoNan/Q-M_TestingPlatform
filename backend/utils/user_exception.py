

class EnvServiceNotExistException(Exception):
    def __init__(self):
        error_msg = '请在【环境管理->服务配置->服务域名配置】下添加对应的服务所在环境下请求域名'
        super().__init__(error_msg)
        self.__doc__ = '该服务所在环境对应的请求域名配置不存在'


class EnvPlantNotExistException(Exception):
    def __init__(self):
        error_msg = '请在【环境管理->产品配置->产品域名配置】下添加对应的产品所在环境下请求域名'
        super().__init__(error_msg)
        self.__doc__ = '该产品所在环境对应的请求域名配置不存在'


class UserFuncNotExistException(Exception):
    def __init__(self, func_name):
        error_msg = f'请在【公共资源->自定义函数】下检查是否包含该函数 -> {func_name}'
        super().__init__(error_msg)
        self.__doc__ = '用户自定义函数不存在'


class StrToObjectException(Exception):
    def __init__(self):
        error_msg = '请检查字符串是否包含系统特殊字符【bool[], int[], float[], list[], dict[], |&|】'
        super().__init__(error_msg)
        self.__doc__ = '字符串转换成数字或布尔值或字典或数组失败'


class ParseParamsException(Exception):
    def __init__(self, path):
        error_msg = f'变量引用失败 -> {path}'
        super().__init__(error_msg)
        self.__doc__ = '变量引用失败'
