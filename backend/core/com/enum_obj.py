from apps.elements.serializers import ElementSerializers


class ParamsType:
    STRING = "Str"
    INT = 'Int'
    FLOAT = 'Float'
    BOOL = 'Bool'
    DICT = 'Dict'
    LIST = "List"
    TUPLE = 'Tuple'
    EleObject = 'EleObject'


class StepType:
    PlatformSystemFunction = -1  # 平台自带的系统函数
    UserCustomizeFunction = 1    # 用户自定义函数
    Request = 5                  # request 类型的Api请求
    Selenium = 2                 # selenium 类型的步骤
    ComStep = 3                  # 用户定义的公共步骤
    UserCustomizeScript = 4      # 用户定义一次性脚本


ParamsTypeMap = {
    int: ParamsType.INT,
    float: ParamsType.FLOAT,
    str: ParamsType.STRING,
    bool: ParamsType.BOOL,
    dict: ParamsType.DICT,
    list: ParamsType.LIST,
    tuple: ParamsType.TUPLE,
    ElementSerializers:  ParamsType.EleObject
}
