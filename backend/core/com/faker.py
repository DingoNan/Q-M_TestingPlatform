import inspect
import json
import importlib
from hashlib import md5, sha1, sha256
from base64 import b64decode, b64encode
from urllib.parse import quote, unquote, quote_plus, unquote_plus
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256, MD5, SHA1
from faker import Faker
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from core.com.step_model import action_group, SystemFuncType

_faker = Faker('zh-CN')

MAX_ENCRYPT_BLOCK = 117  # RSA with PKCS1_v1_5 can encrypt 117 bytes at a time for 1024-bit key

MAX_DECRYPT_BLOCK = 128  # RSA 1024-bit密钥解密块大小


class ParamsType:
    STRING = "Str"
    INT = 'Int'
    FLOAT = 'Float'
    BOOL = 'Bool'
    DICT = 'Dict'
    LIST = "List"
    TUPLE = 'Tuple'


ParamsTypeMap = {
    int: ParamsType.INT,
    float: ParamsType.FLOAT,
    str: ParamsType.STRING,
    bool: ParamsType.BOOL,
    dict: ParamsType.DICT,
    list: ParamsType.LIST,
    tuple: ParamsType.TUPLE,
}


def _get_function_params(function_name):
    """
    获取函数名,函数参数类型,函数参数默认值
    """
    a = inspect.signature(function_name).parameters
    func_desc = [new_str.strip() for new_str in function_name.__doc__.strip().split('\n')]

    params_list = []
    index = 0
    for name, param in a.items():
        if name == 'self':
            continue
        params_info = dict()
        params_info['function_name'] = function_name.__name__
        params_info['explain'] = func_desc[index + 1][len(name) + 1:]
        params_info['name'] = name
        params_info['type'] = ParamsTypeMap[param.annotation]
        # 判断参数是否有默认值
        if param.default != param.empty:
            params_info['value'] = str(param.default)
        else:
            params_info['value'] = None
        index = index + 1
        params_list.append(params_info)
    return params_list


def _get_module_functions(module_path):
    return dict(inspect.getmembers(importlib.import_module(module_path), inspect.isfunction))


@action_group(SystemFuncType.BuildFunc)
def rsa_public_encrypt_pem(data: str = 'pwd', base64_key: str = 'key'):
    """
    rsa加密算法
    data: 默认值: pwd, 入数类型: str
    base64_key, 默认值: key, 入数类型: str
    返回值类型: Str, 返回值样式: 1
    """
    base64_key = base64_key.strip()
    key_der = b64decode(base64_key)
    pem_key = (
            "-----BEGIN PUBLIC KEY-----\n" +
            b64encode(key_der).decode('utf-8') + "\n" +
            "-----END PUBLIC KEY-----"
    )
    key = RSA.import_key(pem_key)
    cipher = PKCS1_v1_5.new(key)
    encrypted = cipher.encrypt(data.encode('utf-8'))

    return b64encode(encrypted).decode('utf-8')


@action_group(SystemFuncType.BuildFunc)
def rsa_private_decrypt(private_key: str, data: str):
    """
    rsa使用私钥解密数据
    private_key: rsa解密需要的私钥
    data: 要接密的字符串
    return: 解密后的字符串
    :raises: RuntimeError 如果解密失败
    """
    try:
        encrypted_data = b64decode(data)
        private_key_obj = RSA.import_key(b64decode(private_key))

        # 创建解密器
        cipher = PKCS1_v1_5.new(private_key_obj)

        # 分段解密
        input_len = len(encrypted_data)
        offset = 0
        decrypted_parts = []

        while input_len - offset > 0:
            if input_len - offset > MAX_DECRYPT_BLOCK:
                chunk = encrypted_data[offset:offset + MAX_DECRYPT_BLOCK]
            else:
                chunk = encrypted_data[offset:input_len]
            decrypted_part = cipher.decrypt(chunk, None)
            if decrypted_part is None:
                raise ValueError("解密失败")

            decrypted_parts.append(decrypted_part)
            offset += MAX_DECRYPT_BLOCK
        return b''.join(decrypted_parts).decode()
    except Exception as e:
        raise RuntimeError("解密失败")


@action_group(SystemFuncType.BuildFunc)
def rsa_public_encrypt(public_key: str = '', data: str = ''):
    """
    使用rsa公钥加密字符串数据
    public_key: Base64编码的公钥
    data: 要加密的字符串
    :return: rsa公钥加密结果
    """
    # 解码Base64公钥并重建公钥对象
    pub_key = RSA.import_key(b64decode(public_key))

    # 创建加密器
    cipher = PKCS1_v1_5.new(pub_key)

    # 分段加密
    input_len = len(data.encode())
    offset = 0
    encrypted_parts = []

    while input_len - offset > 0:
        if input_len - offset > MAX_ENCRYPT_BLOCK:
            chunk = data[offset:offset + MAX_ENCRYPT_BLOCK]
        else:
            chunk = data[offset:input_len]

        encrypted_part = cipher.encrypt(chunk)
        encrypted_parts.append(encrypted_part)
        offset += MAX_ENCRYPT_BLOCK

    return b64encode(b''.join(encrypted_parts)).decode('utf-8')


def _get_sign_content(sorted_param):
    """
    将字典按键排序后生成字符串（类似Java的LinkedHashMap.toString()格式）

    :param sorted_param: 输入的字典
    :return: 排序后的字符串表示，格式如 "{key1=value1, key2=value2}"
    """
    # 过滤None值并转换为字符串
    filtered_params = {k: str(v) for k, v in sorted_param.items() if v is not None}

    # 按键排序
    sorted_items = sorted(filtered_params.items(), key=lambda x: x[0])

    # 生成Java风格的字符串
    content = ", ".join(f"{k}={v}" for k, v in sorted_items)
    return f"{{{content}}}"


@action_group(SystemFuncType.BuildFunc)
def rsa_private_sign(private_key: str = '', data: dict = {}, algorithm: str = 'md5'):
    """
    使用私钥对数据进行签名
    private_key: Base64编码的私钥
    param data: 要签名的字符串数据
    algorithm 签名算法 默认md5/sha1/sha256
    return: Base64编码的签名结果
    :raises: RuntimeError 如果签名失败
    """
    try:
        data = _get_sign_content(data)
        # 解码Base64私钥并重建私钥对象
        private_key = b64decode(private_key)
        private_key_obj = RSA.import_key(private_key)

        # 创建哈希对象
        if algorithm == 'md5':
            hash_obj = MD5.new(data.encode())
        elif algorithm == 'sha2':
            hash_obj = SHA1.new(data.encode())
        else:
            hash_obj = SHA256.new(data.encode())

        # 使用PKCS#1 v1.5方案进行签名
        signer = pkcs1_15.new(private_key_obj)
        signature = signer.sign(hash_obj)
        return b64encode(signature).decode()
    except Exception as e:
        raise RuntimeError("签名失败")


"""
faker_base
"""


@action_group(SystemFuncType.StringGenerate)
def faker_bothify(text: str = '## ??', letters: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """
    生成一个字符串，其中 text 参数中的每个占位符将根据以下规则被替换
    text: str = '## ??': 包含占位符的输入字符串。默认值为 '## ??' (两个数字后跟一个空格和两个字母)
    letters: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ': 指定当替换问号 (?) 时，从中随机选取字符的字符集。默认包含所有大小写 ASCII 字母
    井号 (#): 将被替换为一个随机数字 (0 到 9)。
    百分号 (%): 将被替换为一个随机非零数字 (1 到 9)。
    美元符号 ($): 将被替换为一个随机的大于二的数字 (2 到 9)。
    感叹号 (!): 将被替换为一个随机数字或空字符串 (即可能被移除)。
    At 符号 (@): 将被替换为一个随机非零数字或空字符串 (即可能被移除)。
    问号 (?): 将被替换为 letters 参数中的一个随机字符。
    参数说明：
    """
    return _faker.bothify(text=text, letters=letters)


@action_group(SystemFuncType.StringGenerate)
def faker_hexify(text: str = '^^^^', upper: bool = False):
    """
    生成一个字符串，将 text 参数中的每个脱字符 (^) 替换为一个随机的十六进制字符
    text: str = '^^^^': 包含脱字符 (^) 占位符的输入字符串。默认值为 '^^^^' (四个十六进制字符占位符)
    upper: bool = False: 控制输出十六进制字符的大小写
    False (默认): 输出使用小写十六进制字符 (a-f)
    True: 输出使用大写十六进制字符 (A-F)
    返回值： str - 替换后的字符串。
    """
    return _faker.hexify(text=text, upper=upper)


@action_group(SystemFuncType.StringGenerate)
def faker_language_code():
    """
    生成一个随机的 i18n（国际化）语言代码（例如：en）
    return: language_code() → str
    """
    return _faker.language_code()


@action_group(SystemFuncType.StringGenerate)
def faker_lexify(text: str = '????', letters: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """
    生成一个字符串，将 text 参数中的每个问号 (?) 替换为 letters 参数中的一个随机字符
    text: str = '????': 包含问号 (?) 占位符的输入字符串。默认值为 '????' (四个字母占位符)
    letters: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ': 指定当替换问号 (?) 时，从中随机选取字符的字符集。默认包含所有大小写 ASCII 字母 (a-z, A-Z)
    返回值： str - 替换后的字符串。
    """
    return _faker.lexify(text=text, letters=letters)


@action_group(SystemFuncType.StringGenerate)
def faker_locale():
    """
    生成一个随机的、以下划线连接的 i18n（国际化）区域代码（例如：en_US）
    """
    return _faker.locale()


@action_group(SystemFuncType.StringGenerate)
def faker_numerify(text: str = '###'):
    """
    生成一个字符串，将 text 参数中的每个占位符根据以下规则替换为随机数字或空字符串
    text: str = '###': 包含数字占位符的输入字符串。默认值为 '###' (三个随机数字占位符)
    井号 (#): 替换为一个随机数字 (0 到 9)。
    百分号 (%): 替换为一个随机非零数字 (1 到 9)。
    美元符号 ($): 替换为一个随机的大于二的数字 (2 到 9)。
    感叹号 (!): 替换为一个随机数字或空字符串 (即可能被移除)。
    At 符号 (@): 替换为一个随机非零数字或空字符串 (即可能被移除)。
    返回值： str - 替换后的字符串。
    """
    return _faker.numerify(text=text)


@action_group(SystemFuncType.StringGenerate)
def faker_random_choices(elements: str = 'abc', length: int = 3):
    """
    生成一个列表，其中的对象是从 elements 参数中有放回地随机抽取的
    elements: 提供抽样来源的集合或加权字典。可以是：默认值为 ('a', 'b', 'c')
    length: int  指定要生成的随机序列的长度。如果提供整数 n，则返回包含 n 个元素的列表
    返回值： Sequence[T] - 包含随机抽取元素的序列（列表）。
    """
    return _faker.random_choices(elements=elements, length=length)


@action_group(SystemFuncType.StringGenerate)
def faker_random_digit():
    """
    生成一个随机数字（范围从 0 到 9）
    返回值：int - 一个介于 0（包含）和 9（包含）之间的随机整数
    """
    return _faker.random_digit()


@action_group(SystemFuncType.StringGenerate)
def faker_random_digit_above_two():
    """
    生成一个大于二的随机数字（范围从 2 到 9）
    返回值：int - 一个介于 2（包含） 和 9（包含） 之间的随机整数。
    """
    return _faker.random_digit_above_two()


@action_group(SystemFuncType.StringGenerate)
def faker_random_digit_not_null():
    """
    生成一个非零的随机数字（范围从 1 到 9）
    返回值： int - 一个介于 1（包含） 和 9（包含） 之间的随机整数。
    """
    return _faker.random_digit_not_null()


@action_group(SystemFuncType.StringGenerate)
def faker_random_digit_not_null_or_empty():
    """
    生成一个随机的非零数字 (1 到 9) 或一个空字符串
    返回值： int | str - 返回值有两种可能：
        一个介于 1（包含） 和 9（包含） 之间的随机整数 (int)，或者
        一个空字符串 (str，即 '')。
    """
    return _faker.random_digit_not_null_or_empty()


@action_group(SystemFuncType.StringGenerate)
def faker_random_digit_or_empty():
    """
    生成一个随机的数字 (0 到 9) 或一个空字符串
    返回值： int | str - 返回值有两种可能：
        一个介于 0（包含） 和 9（包含） 之间的随机整数 (int)，或者
        一个空字符串 (str，即 '')。
    """
    return _faker.random_digit_or_empty()


@action_group(SystemFuncType.StringGenerate)
def faker_random_element(elements: str = 'abc'):
    """
    从 elements 参数中随机抽取一个对象
    elements: 提供抽样来源的字符串。可以是：默认值为 abc
    返回值： T - 从 elements 中随机抽取的单个元素。返回值的类型 (T) 与输入集合中元素的类型一致
    """
    return _faker.random_element(elements=elements)


@action_group(SystemFuncType.StringGenerate)
def faker_random_elements(elements: str = 'abc', length: int = 3, unique: bool = False):
    """
    从 elements 参数中生成一个随机抽样对象列表
    elements (抽样来源):str 默认值为 abc
    length: int (列表长度):指定要生成的随机序列的长度 (n)
    unique: bool = False (唯一性/抽样方式):
    unique=False (默认): 进行有放回随机抽样 (random sampling with replacement)。同一个元素可以被多次抽中（即在结果列表中出现多次）。
    unique=True: 进行无放回随机抽样 (random sampling without replacement)。同一个元素最多只能在结果列表中出现一次（元素在结果中是唯一的）。
    重要限制: 如果 unique=True，则 length 的值不能大于 elements 中的元素数量（因为不可能无重复地抽取比总元素数还多的元素）。
    """
    return _faker.random_elements(elements=elements, length=length, unique=unique, use_weighting=None)


@action_group(SystemFuncType.StringGenerate)
def faker_random_int(min_value: int = 0, max_value: int = 9999, step: int = 1):
    """
    在指定的最小值 (min) 和最大值 (max) 之间（包含两端），按照给定的步长 (step) 生成一个随机整数
    min: int = 0: 随机整数范围的下限（包含）。默认值为 0
    max: int = 9999: 随机整数范围的上限（包含）。默认值为 9999
    step: int = 1: 生成随机数的步长（增量）。默认值为 1
    该值必须是一个正整数。
    它定义了从 min 到 max 范围内有效候选数的间隔（例如，step=2 时只生成偶数或奇数，取决于 min）。
    返回值： int - 满足 min <= random_number <= max 且 (random_number - min) % step == 0 的随
    """
    return _faker.random_int(min=min_value, max=max_value, step=step)


@action_group(SystemFuncType.StringGenerate)
def faker_random_letter():
    """
    生成一个随机的 ASCII 字母（a-z 或 A-Z）
    返回值： str - 一个随机的大写或小写英文字母组成的单字符字符串。
    """
    return _faker.random_letter()


@action_group(SystemFuncType.StringGenerate)
def faker_random_letters(length: int = 16):
    """
    生成一个包含指定数量 (length) 的随机 ASCII 字母（a-z 和 A-Z）的列表
    length: int = 16: 指定要生成的字母数量（即列表长度）。默认值为 16
    返回值： Sequence[str] - 一个包含 length 个随机字母字符串的序列（通常为列表）。每个元素是单
    """
    return _faker.random_letters(length=length)


@action_group(SystemFuncType.StringGenerate)
def faker_random_lowercase_letter():
    """
    生成一个随机的小写 ASCII 字母（a 到 z）
    返回值：str - 一个随机的小写英文字母组成的单字符字符串
    """
    return _faker.random_lowercase_letter()


@action_group(SystemFuncType.StringGenerate)
def faker_random_number(digits: int = 1, fix_len: bool = False):
    """
    根据以下规则生成一个随机整数：
    digits: 如果 digits 为 None (默认)，则其值会被设置为 1 到 9 之间的随机整数。 如果显式指定 digits (正整数)，则使用该值作为数字位数基准
    fix_len: fix_len=False (默认)： 生成不超过 digits 位数的随机整数
    范围从 1 到 10^digits - 1 (即最小为 1 位，最大为 digits 位的最大数)。
    例如：digits=3 可能生成 5 (1位)、42 (2位) 或 789 (3位)。
    fix_len=True： 生成严格等于 digits 位数的随机整数。
    范围从 10^(digits-1) 到 10^digits - 1。
    例如：digits=3 只会生成 100 到 999 之间的数 (始终是3位数)。
    """
    return _faker.random_number(digits=digits, fix_len=fix_len)


@action_group(SystemFuncType.StringGenerate)
def faker_random_uppercase_letter():
    """
    生成一个随机的大写 ASCII 字母（A 到 Z）
    返回值：str - 一个随机的大写英文字母组成的单字符字符串
    """
    return _faker.random_uppercase_letter()


@action_group(SystemFuncType.StringGenerate)
def faker_random_sample(elements: str = 'abc', length: int = 3):
    """
    从 elements 参数中生成一个无放回随机抽样的对象列表（即每个元素在结果中最多出现一次）
    elements: 提供抽样来源的字符串。默认值为 abc
    length: int 指定要生成的随机序列的长度
    如果提供整数 n，则返回包含 n 个元素的列表。
    重要限制： length 的值不能大于 elements 中的元素数量（因为不可能无重复地抽取比总元素数还多的元素）。
    返回值： Sequence[T] - 包含随机抽取元素的序列（列表），其中每个元素都是唯一的
    """
    return _faker.random_sample(elements=elements, length=length)


@action_group(SystemFuncType.StringGenerate)
def faker_randomize_nb_elements(number: int = 10, le: bool = False, ge: bool = False, min: int = 1, max: int = 10):
    """
    生成一个接近给定数字 number 的随机整数，遵循以下规则
    number: int = 10: 基准数字，用于计算随机范围的中心点。默认值为 10
    le: bool = False: 控制是否限制上限不超过 number
    ge: bool = False: 控制是否限制下限不低于 number
    min: int | None = None: 生成值的绝对最小值（钳制下限）。如果为 None，则不应用此钳制
    max: int | None = None: 生成值的绝对最大值（钳制上限）。如果为 None，则不应用此钳制
    基本范围规则：
        le=False (默认)： 允许生成最高达 number 的 140% 的值（即上限为 1.4 * number）。
        le=True： 生成上限被限制在 100% 的 number（即不超过 number）。
        ge=False (默认)： 允许生成最低至 number 的 60% 的值（即下限为 0.6 * number）。
        ge=True： 生成下限被限制在 100% 的 number（即不低于 number）。
        最小值/最大值钳制规则：
        如果提供了数值型 min 参数，则任何小于 min 的生成值将被钳制（clamp） 到 min。
        如果提供了数值型 max 参数，则任何大于 max 的生成值将被钳制（clamp） 到 max。
    特殊情况规则：
        如果 le=True 且 ge=True，则无论 min 和 max 的值如何，函数将直接返回 number。
    返回值： int - 根据上述规则生成的随机整数。
    """
    return _faker.randomize_nb_elements(number=number, le=le, ge=ge, min=min, max=max)


"""
faker_address
"""


@action_group(SystemFuncType.AddressInfo)
def faker_address():
    """
    用来生成一个地址数据
    返回值类型: Str,返回值样式: 重庆市芳县海港陈街B座 416844
    """
    return _faker.address()


@action_group(SystemFuncType.AddressInfo)
def faker_building_number():
    """
    返回一个表示建筑物门牌号的字符串
    返回值类型: Str,返回值样式: 791
    """
    return _faker.building_number()


@action_group(SystemFuncType.AddressInfo)
def faker_city():
    """
    返回一个表示城市名称的字符串
    返回值类型: Str,返回值样式: 哈尔滨县
    """
    return _faker.city()


@action_group(SystemFuncType.AddressInfo)
def faker_city_suffix():
    """
    一个表示城市名称常见后缀的字符串
    返回值类型: Str,返回值样式: 市/县
    """
    return _faker.city_suffix()


@action_group(SystemFuncType.AddressInfo)
def faker_country():
    """
    一个表示国家名称的字符串
    返回值类型: Str,返回值样式: 中国
    """
    return _faker.country()


@action_group(SystemFuncType.AddressInfo)
def faker_country_code(representation: str = 'alpha-2'):
    """
    根据指定的表示格式 (representation) 生成 ISO 3166-1 标准的国家代码
    representation: representation='alpha-2'）返回(如 CN, US, GB)。representation='alpha-3' 时返回三位字母代码 (如 CHN, USA, GBR)
    """
    return _faker.country_code(representation=representation)


def faker_current_country():
    """
    返回一个表示当前所在国家名称的字符串。eg：People's Republic of China
    """
    return _faker.current_country()


def faker_current_country_code():
    """
    一个表示当前所在国家代码的字符串（通常为 ISO 3166-1 alpha-2 标准的两位字母代码）
    eg:CN
    """
    return _faker.current_country_code()


def faker_postcode():
    """
    生成一个随机的、符合特定国家或地区格式的邮政编码。eg:171037
    返回值类型: Str, eg:171037
    """
    return _faker.postcode()


def faker_street_address():
    """
    一个表示街道级别地址的字符串（通常包含门牌号和街道名称）
    返回值类型: Str, eg: 林街K座
    """
    return _faker.street_address()


def faker_street_name():
    """
    一个表示街道名称的字符串（不包含门牌号）
    返回值类型: Str, eg: 林街
    """
    return _faker.street_name()


def faker_street_suffix():
    """
    一个表示街道名称常见类型后缀的字符串
    返回值类型: Str, eg: 街
    """
    return _faker.street_suffix()


"""
faker_automotive
"""


@action_group(SystemFuncType.CarInfo)
def faker_license_plate():
    """
    生成符合特定国家或地区格式的随机车辆牌照（车牌号）
    返回值类型: Str, eg: 陕X-94236
    """
    return _faker.license_plate()


@action_group(SystemFuncType.CarInfo)
def faker_vin():
    """
    一个表示车辆识别码 (VIN) 的字符串。
    返回值类型: Str, eg: JEX6RM4S11G9L2N4R
    """
    return _faker.vin()


"""
faker_bank
"""


@action_group(SystemFuncType.BankInfo)
def faker_aba():
    """
    一个符合美国银行家协会 (ABA) 标准的 9 位路由号码字符串
    返回值类型: Str, eg: 096155192
    """
    return _faker.aba()


@action_group(SystemFuncType.BankInfo)
def faker_bank_country():
    """
    生成代表银行机构注册地或主要运营国家的标准国家代码
    返回值类型: Str, eg: GB
    """
    return _faker.bank_country()


@action_group(SystemFuncType.BankInfo)
def faker_bban():
    """
    生成符合各国银行标准的随机基本银行账号（Basic Bank Account Number）
    返回值类型: Str, eg: OSPU3903149782402
    """
    return _faker.bban()


@action_group(SystemFuncType.BankInfo)
def faker_iban():
    """
    生成符合 ISO 13616 标准的随机国际银行账号（International Bank Account Number）
    返回值类型: Str, eg: GB84MYNB48764759382421
    """
    return _faker.iban()


"""
faker_phone_number
"""


@action_group(SystemFuncType.PhoneInfo)
def faker_country_calling_code():
    """
    生成一个随机的 国际电话区号（国家呼叫代码）
    返回值类型: Str, eg: +86
    """
    return _faker.country_calling_code()


@action_group(SystemFuncType.PhoneInfo)
def faker_msisdn():
    """
    表示国际格式手机号码的字符串（纯数字，无分隔符）
    返回值类型: Str, eg: 5314630552163
    """
    return _faker.msisdn()


@action_group(SystemFuncType.PhoneInfo)
def faker_phone_number():
    """
    生成一个电话号码字符串
    返回值类型: Str, eg: 18888888888
    """
    return _faker.phone_number()


"""
faker_person
"""


@action_group(SystemFuncType.PersonInfo)
def faker_ssn():
    """
    生成身份证号码
    返回值类型: Str, eg: 411103196304014858
    """
    return _faker.ssn()


@action_group(SystemFuncType.PersonInfo)
def faker_first_name():
    """
    生成通用的中文名字（不区分性别）
    返回值类型: Str, eg: 淑英
    """
    return _faker.first_name()


@action_group(SystemFuncType.PersonInfo)
def faker_first_name_female():
    """
    生成通用的中文女性名字
    返回值类型: Str, eg: 淑英
    """
    return _faker.first_name_female()


@action_group(SystemFuncType.PersonInfo)
def faker_first_name_male():
    """
    生成通用的中文男性名字
    返回值类型: Str, eg: 志强
    """
    return _faker.first_name_male()


@action_group(SystemFuncType.PersonInfo)
def faker_language_name():
    """
    生成一个随机的 国际化语言名称（符合 i18n 标准的语言名称）
    返回值类型: Str, eg: Herero
    """
    return _faker.language_name()


@action_group(SystemFuncType.PersonInfo)
def faker_last_name():
    """
    生成常见中文姓氏
    返回值类型: Str, eg: 黄
    """
    return _faker.last_name()


@action_group(SystemFuncType.PersonInfo)
def faker_last_name_female():
    """
    生成常见女性中文姓氏
    返回值类型: Str, eg: 黄
    """
    return _faker.last_name_female()


@action_group(SystemFuncType.PersonInfo)
def faker_last_name_male():
    """
    生成常见男性中文姓氏
    返回值类型: Str, eg: 黄
    """
    return _faker.last_name_male()


@action_group(SystemFuncType.PersonInfo)
def faker_name():
    """
    生成常见中文姓名
    返回值类型: Str, eg: 黄
    """
    return _faker.name()


@action_group(SystemFuncType.PersonInfo)
def faker_name_female():
    """
    生成常见女性中文姓名
    返回值类型: Str, eg: 黄
    """
    return _faker.name_female()


@action_group(SystemFuncType.PersonInfo)
def faker_name_male():
    """
    生成常见男性中文姓名
    返回值类型: Str, eg: 黄
    """
    return _faker.name_male()


"""
faker_company
"""


@action_group(SystemFuncType.CompanyInfo)
def faker_bs():
    """
    生成随机的 商业术语短语（Business Speak），模仿企业场景中的专业术语表达
    返回值类型: Str, eg: brand web-enabled platforms
    """
    return _faker.bs()


@action_group(SystemFuncType.CompanyInfo)
def faker_catch_phrase():
    """
    生成随机的 产品宣传口号（Catch Phrase），即简短有力的广告语或产品标语
    返回值类型: Str, eg: Robust 6thgeneration function
    """
    return _faker.catch_phrase()


@action_group(SystemFuncType.CompanyInfo)
def faker_company():
    """
    生成公司名称
    返回值类型: Str, eg: 同兴万点信息有限公司
    """
    return _faker.company()


@action_group(SystemFuncType.CompanyInfo)
def faker_company_suffix():
    """
    生成公司名称后缀
    返回值类型: Str, eg: 信息有限公司
    """
    return _faker.company_suffix()


"""
faker_job
"""


@action_group(SystemFuncType.JobInfo)
def faker_job():
    """
    随机生成工作名称
    返回值类型: Str, eg: 叉车司机
    """
    return _faker.job()


"""
faker_date_time
"""


@action_group(SystemFuncType.TimeInfo)
def faker_date(pattern: str = '%Y-%m-%d', end_datetime: str = 'None'):
    """
    生成一个 1970年1月1日至指定结束日期 之间的随机日期字符串
    pattern: str 默认值 '%Y-%m-%d'
    end_datetime: +1d = 加1天, +2m = 加2个月, +3y = 加3年, -1w = 减1周（过去1周）
    返回值类型: Str, eg: 1978-06-30
    """
    end_datetime = None if end_datetime == 'None' else end_datetime
    return _faker.date(pattern=pattern, end_datetime=end_datetime)


@action_group(SystemFuncType.TimeInfo)
def faker_date_between(start_date: str = 'today', end_date: str = 'today', pattern: str = '%Y-%m-%d'):
    """
    在开始时间和结束时间随机返回一个日期数据
    start_date: str 默认值 'today' ,+1d = 加1天, +2m = 加2个月, +3y = 加3年, -1w = 减1周（过去1周）
    end_datetime:  str 默认值 'today', +1d = 加1天, +2m = 加2个月, +3y = 加3年, -1w = 减1周（过去1周）
    pattern: str 默认值 '%Y-%m-%d'
    返回值类型: Str, eg: 1978-06-30
    """
    return _faker.date_between(start_date=start_date, end_date=end_date).strftime(pattern)


@action_group(SystemFuncType.TimeInfo)
def faker_date_this_month(before_today: bool = True, after_today: bool = False, pattern: str = '%Y-%m-%d'):
    """
    获取当前月份内 的随机日期对象
    before_today: bool 默认值 True 是否包含今天之前的日期
    after_today:  bool 默认值 False 是否包含今天之后的日期
    pattern: str 默认值 '%Y-%m-%d'
    返回值类型: Str, eg: 2025-06-30
    """
    return _faker.date_this_month(before_today=before_today, after_today=after_today).strftime(pattern)


@action_group(SystemFuncType.TimeInfo)
def faker_date_this_year(before_today: bool = True, after_today: bool = False, pattern: str = '%Y-%m-%d'):
    """
    获取当前年份内 的随机日期对象
    before_today: bool 默认值 True 是否包含今天之前的日期
    after_today:  bool 默认值 False 是否包含今天之后的日期
    pattern: str 默认值 '%Y-%m-%d'
    返回值类型: Str, eg: 2025-06-30
    """
    return _faker.date_this_year(before_today=before_today, after_today=after_today).strftime(pattern)


@action_group(SystemFuncType.TimeInfo)
def faker_date_time(end_datetime: str = 'None', pattern: str = '%Y-%m-%d %H-%M-%S'):
    """
    获取1970年1月1日至指定结束时间 之间的随机 日期时间字符串（包含时间部分）
    pattern: str 默认值 '%Y-%m-%d %H-%M-%S'
    end_datetime: +1d = 加1天, +2m = 加2个月, +3y = 加3年, -1w = 减1周（过去1周）
    返回值类型: Str, eg: 1978-06-30
    """
    end_datetime = None if end_datetime == 'None' else end_datetime
    return _faker.date_time(end_datetime=end_datetime).strftime(pattern)


@action_group(SystemFuncType.TimeInfo)
def faker_date_time_between(start_date: str = 'now', end_date: str = 'now',
                            pattern: str = '%Y-%m-%d %H-%M-%S', return_type: str = 'str'):
    """
    获取开始时间和结束时间之间随机时间，默认获取当前时间
    start_date: str 默认值 now, +3y = 加3年,+3M = 加3个月, -1d = 减1天, +2h = 加2小时, +2m = 加2分钟, +1s = 加1s, -1w = 减1周（过去1周）
    end_date: str 默认值 now,+3y = 加3年,+3M = 加3个月,-1d = 减1天,+2h = 加2小时,+2m = 加2分钟,+1s = 加1s, -1w = 减1周（过去1周）
    return_type : str = 'str' 'ints‘ 返回秒的整数时间戳， ’intms' 返回微妙的整数时间戳
    返回值类型: Str, eg: 2025-08-18 07-54-21
    """
    if return_type == 'str':
        return _faker.date_time_between(start_date=start_date, end_date=end_date).strftime(pattern)
    elif return_type == 'ints':
        return int(_faker.date_time_between(start_date=start_date, end_date=end_date).timestamp())
    else:
        return int(_faker.date_time_between(start_date=start_date, end_date=end_date).timestamp() * 1000)


@action_group(SystemFuncType.TimeInfo)
def faker_date_time_this_month(before_now: bool = True, after_now: bool = False, pattern: str = '%Y-%m-%d %H-%M-%S'):
    """
    获取当前月份内的随机时间
    before_now: bool 默认值 True 是否包含当前时间之前的时间
    after_now:  bool 默认值 False 是否包含当前时间之后的时间
    pattern: str 默认值 %Y-%m-%d %H-%M-%S
    返回值类型: Str, eg: 2025-08-18 07-54-21
    """
    return _faker.date_time_this_month(before_now=before_now, after_now=after_now).strftime(pattern)


@action_group(SystemFuncType.TimeInfo)
def faker_date_time_this_year(before_now: bool = True, after_now: bool = False, pattern: str = '%Y-%m-%d %H-%M-%S'):
    """
    获取当前年份内 的随机时间
    before_now: bool 默认值 True 是否包含当前时间之前的时间
    after_now:  bool 默认值 False 是否包含当前时间之后的时间
    pattern: str 默认值 %Y-%m-%d %H-%M-%S
    返回值类型: Str, eg: 2025-08-18 07-54-21
    """
    return _faker.date_time_this_year(before_now=before_now, after_now=after_now).strftime(pattern)


@action_group(SystemFuncType.TimeInfo)
def faker_day_of_month():
    """
    获取当前月份的第几天
    返回值类型: Str, eg: 04
    """
    return _faker.day_of_month()


@action_group(SystemFuncType.TimeInfo)
def faker_month():
    """
    随机获取月份
    返回值类型: Str, eg: 04
    """
    return _faker.month()


@action_group(SystemFuncType.TimeInfo)
def faker_year():
    """
    随机获取年份
    返回值类型: Str, eg: 04
    """
    return _faker.year()


"""
faker_internet
"""


@action_group(SystemFuncType.InternetInfo)
def faker_company_email():
    """
    随机生成一个公司邮箱
    返回值类型: Str, eg: 'achang@green.info'
    """
    return _faker.company_email()


@action_group(SystemFuncType.InternetInfo)
def faker_email():
    """
    随机生成一个邮箱
    返回值类型: Str, eg: 'tammy76@example.com'
    """
    return _faker.email()


@action_group(SystemFuncType.InternetInfo)
def faker_domain_name():
    """
    随机生成一个域名
    返回值类型: Str, eg: williamson-hopkins.jackson.com
    """
    return _faker.domain_name()


@action_group(SystemFuncType.InternetInfo)
def faker_http_method():
    """
    随机http请求方法
    返回值类型: Str, eg: get
    """
    return _faker.http_method()


@action_group(SystemFuncType.InternetInfo)
def faker_image_url():
    """
    随机返回一个图片访问url地址
    返回值类型: STR, eg: https://picsum.photos/788/861
    """
    return _faker.image_url()


@action_group(SystemFuncType.InternetInfo)
def faker_ipv4():
    """
    随机返回一个IPV4地址
    返回值类型: STR, eg: 171.174.170.81
    """
    return _faker.ipv4()


@action_group(SystemFuncType.InternetInfo)
def faker_ipv4_private():
    """
    随机返回一个私有IPV4地址
    返回值类型: STR, eg: 171.174.170.81
    """
    return _faker.ipv4_private()


@action_group(SystemFuncType.InternetInfo)
def faker_ipv4_public():
    """
    随机返回一个公有IPV4地址
    返回值类型: STR, eg: 171.174.170.81
    """
    return _faker.ipv4_public()


@action_group(SystemFuncType.InternetInfo)
def faker_ipv6():
    """
    随机返回一个IPV6地址
    返回值类型: STR, eg: e3e7:682:c209:4cac:629f:6fbf:d82c:7cd
    """
    return _faker.ipv6()


@action_group(SystemFuncType.InternetInfo)
def faker_mac_address():
    """
    随机返回一个mac地址
    return: string, eg: 66:c5:d7:14:84:f8
    """
    return _faker.mac_address()


@action_group(SystemFuncType.InternetInfo)
def faker_port_number():
    """
    随机返回一个端口号
    return: INT, eg: 3306
    """
    return _faker.port_number()


@action_group(SystemFuncType.InternetInfo)
def faker_uri():
    """
    随机返回一个uri地址
    return: string, eg: https://hull-gallegos.info/categorylogin.jsp
    """
    return _faker.uri()


@action_group(SystemFuncType.InternetInfo)
def faker_uri_path():
    """
    随机返回一个uri_path地址
    return: string, eg: posts/tag
    """
    return _faker.uri_path()


@action_group(SystemFuncType.InternetInfo)
def faker_url():
    """
    随机返回一个url地址
    return: string, eg: posts/tag
    """
    return _faker.url()


@action_group(SystemFuncType.InternetInfo)
def faker_user_name():
    """
    随机返回一个用户名
    return: string, 返回一个用户名
    """
    return _faker.user_name()


"""
faker_color
"""


@action_group(SystemFuncType.ColorInfo)
def faker_color_name():
    """
    随机返回颜色名称
    return: string, 返回颜色名称
    """
    return _faker.color_name()


@action_group(SystemFuncType.ColorInfo)
def faker_rgb_css_color():
    """
    随机返回GRB颜色名称
    return: string, 返回GRB颜色名称
    """
    return _faker.rgb_css_color()


@action_group(SystemFuncType.ColorInfo)
def faker_hex_color():
    """
    随机返回16进制颜色
    return: string 返回16进制颜色
    """
    return _faker.hex_color()


"""
faker_python
"""


@action_group(SystemFuncType.PythonBaseData)
def faker_pyint(min_value: int = 0, max_value: int = 9999, step: int = 1):
    """
    在最大值和最小值之间返回一个正数
    min_value: 最小值范围
    max_value: 最大值范围
    return: INT, eg: 1
    """
    return _faker.pyint(min_value=min_value, max_value=max_value, step=step)


@action_group(SystemFuncType.PythonBaseData)
def faker_pystr(min_chars: int = 8, max_chars: int = 12, prefix: str = '', suffix: str = '') -> str:
    """
    随机返回字符串
    min_chars: 返回字符串最小长度
    max_chars: 返回字符串最大长度
    prefix: 返回字符串的前缀
    suffix: 返回字符串的后最
    返回值类型: STR, eg: OliveDrab
    """
    return _faker.pystr(min_chars=min_chars, max_chars=max_chars, prefix=prefix, suffix=suffix)


@action_group(SystemFuncType.PythonBaseData)
def faker_pybool(truth_probability: int = 50) -> bool:
    """
    随机返回True或False
    truth_probability: int = 100 返回 True， 0 返回False
    返回值类型: bool, eg: True 或 False
    """
    return _faker.pybool(truth_probability=truth_probability)


"""
faker_misc
"""


@action_group(SystemFuncType.OtherInfo)
def faker_password(length: int = 10, special_chars: bool = True, digits: bool = True, upper_case: bool = True,
                   lower_case: bool = True):
    """
    生成指定长度的随机密码，可自定义字符组合规则
    length:	int	10 密码长度
    special_chars: bool True 是否包含特殊字符 !@#$%^&*()_+
    digits	bool True 是否包含数字 0-9
    upper_case bool	True 是否包含大写字母 A-Z
    lower_case bool	True 是否包含小写字母 a-z
    return: INT, eg: 1
    """
    return _faker.password(length=length, special_chars=special_chars, digits=digits, upper_case=upper_case,
                           lower_case=lower_case)


@action_group(SystemFuncType.OtherInfo)
def faker_uuid4() -> str:
    """
    随机返回uuid4字符串
    return: STR, eg: e3e70682-c209-4cac-a29f-6fbed82c07cd
    """
    return _faker.uuid4()


@action_group(SystemFuncType.OtherInfo)
def faker_null_boolean():
    """
    随机返回True或False或None
    return: True, False, None
    """
    return _faker.null_boolean()


"""
faker_lorem
"""


@action_group(SystemFuncType.TextInfo)
def faker_text(max_nb_chars: int = 200):
    """
    生成一个 自然语言文本字符串，根据指定长度自动选择最佳生成策略
    max_nb_chars int	200	返回文本信息的最大长度
    return: STR, eg: 当然一些注册进行.
    """
    return _faker.text(max_nb_chars=max_nb_chars)


@action_group(SystemFuncType.TextInfo)
def faker_word() -> str:
    """
    生成一个 随机单词
    return: STR, eg: 测试
    """
    return _faker.word()


"""
py-built-func
"""


@action_group(SystemFuncType.BuildFunc)
def add(value: int = 1, other_value: int = 1) -> int:
    """
    计算两数之和
    value: int 数字
    other_value: int 数字
    return int 两数之和
    """
    return value + other_value


@action_group(SystemFuncType.BuildFunc)
def sub(value: int = 1, other_value: int = 1) -> int:
    """
    计算两数之差
    value: int 数字
    other_value: int 数字
    return int 两数之和
    """
    return value - other_value


@action_group(SystemFuncType.BuildFunc)
def multiply(value: int = 2, other_value: int = 2):
    """
    计算两数之积
    value: int 数字
    other_value: int 数字
    return int 两数之积
    """
    return value * other_value


@action_group(SystemFuncType.BuildFunc)
def divide(value: int = 9, other_value: int = 3):
    """
    计算两数相除
    value: int 数字
    other_value: int 数字
    return int 两数相除
    """
    return value / other_value


@action_group(SystemFuncType.BuildFunc)
def py_sum(sum_map: list):
    """
    计算数组之和
    sum_map: list 数组的值
    return 数组每个值之和
    """
    return sum(sum_map)


@action_group(SystemFuncType.BuildFunc)
def py_max(max_map: list):
    """
    计算数组最大值
    max_map: list 数组值
    return 数组中最大的值
    """
    return max(max_map)


@action_group(SystemFuncType.BuildFunc)
def py_min(min_map: list):
    """
    计算数组最小值
    max_map: list 数组值
    return 数组中最小的值
    """
    return min(min_map)


@action_group(SystemFuncType.BuildFunc)
def py_abs(value: int = -1):
    """
    求绝对值
    value: int
    return int
    """
    return abs(value)


@action_group(SystemFuncType.BuildFunc)
def py_list_len(value: list) -> int:
    """
    求数组的长度
    value: list 数组
    return int 数组长度
    """
    return len(value)


@action_group(SystemFuncType.BuildFunc)
def py_str_len(value: str) -> int:
    """
    求字符串的长度
    value: str 字符串
    return int 字符串长度
    """
    return len(value)


@action_group(SystemFuncType.BuildFunc)
def url_quote(value: str = 'test', plus: bool = False, encode: str = 'utf-8'):
    """
    url编码
    value str 需要url编码的值
    plus bool True: 将空格转为+  False不将空格转为+
    encode: str = 'utf-8'
    """
    return quote_plus(value, encoding=encode) if plus else quote(value, encoding=encode)


@action_group(SystemFuncType.BuildFunc)
def url_unquote(value: str = 'test', plus: bool = False, encode: str = 'utf-8'):
    """
    url解密
    value str 需要url编码的值
    plus bool True: 将空格转为+  False不将空格转为+
    encode: str = 'utf-8'
    """
    return unquote_plus(value, encoding=encode) if plus else unquote(value, encoding=encode)


@action_group(SystemFuncType.BuildFunc)
def base64_encode(data: str = 'test') -> str:
    """
    base64 编码
    data: str 需要编辑的字符串
    return str 返回编码后的字符串
    """
    return base64.b64encode(data.encode()).decode()


@action_group(SystemFuncType.BuildFunc)
def base64_decode(data: str = 'tests') -> str:
    """
    base64 解码
    data: str 需要解码的字符串
    return str 返回解码后的字符串
    """
    return base64.b64decode(data.encode()).decode()


@action_group(SystemFuncType.BuildFunc)
def dict_to_json(data: dict) -> str:
    """
    字典对象转成json字符串
    data: dict 需要转成字符串的字典
    return str json字符串
    """
    return json.dumps(data)


@action_group(SystemFuncType.BuildFunc)
def json_to_dict(data: str = 'tests') -> str:
    """
    json字符串转成python dict对象
    data: str 需要转成字典的字符串
    return dict 返回字典
    """
    return json.loads(data)


@action_group(SystemFuncType.BuildFunc)
def hash_encrypt(text: str = 'encrypt_msg', salt: str = '', encode: str = 'utf-8', algorithm: str = 'md5'):
    """
    MD5 加密（哈希）函数
    text: 要加密的字符串
    salt 加盐的字符串
    encode 字符编码
    algorithm 加密算法 md5/sha1/sha256
    return: MD5 哈希值（32位十六进制字符串）
    """
    # 创建 MD5 哈希对象
    if algorithm == 'md5':
        hash_obj = md5(salt.encode(encode)) if salt else md5()
    elif algorithm == 'sha1':
        hash_obj = sha1(salt.encode(encode)) if salt else sha1()
    else:
        hash_obj = sha256(salt.encode(encode)) if salt else sha256()
    # 更新哈希对象（需要将字符串编码为字节）
    hash_obj.update(text.encode(encode))

    # 获取十六进制哈希值
    return hash_obj.hexdigest()


faker_function_map = _get_module_functions('core.com.faker')
faker_function_map = {k: v for k, v in faker_function_map.items() if not k.startswith('_')}

system_func_actions = [{'id': key,
                        'name': [new_str.strip() for new_str in value.__doc__.strip().split('\n')][0],
                        'script': inspect.getsource(value),
                        'params': _get_function_params(value),
                        'desc': [new_str.strip() for new_str in value.__doc__.strip().split('\n')],
                        'group': value.__dict__.get('group_id')}
                       for key, value in faker_function_map.items()
                       if hasattr(value, 'group_id')]

faker_function_doc = {key: [new_str for new_str in value.__doc__.strip().split('\n')]
                      for key, value in faker_function_map.items()}

faker_function_doc_two = {key: inspect.getsource(value) for key, value in faker_function_map.items()}

# faker_function_list = [{"id": func_name, "name": func_name}
#                        for func_name in faker_function_map.keys()]


faker_function_list = [
    {
        "name": '伪造数据',
        "id": 'faker',
        "children": [
            {
                "name": SystemFuncType.StringGenerate,
                "id": 'faker_base',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.StringGenerate]
            },
            {
                "name": SystemFuncType.AddressInfo,
                "id": 'faker_address',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.AddressInfo]
            },
            {
                "name": SystemFuncType.CarInfo,
                "id": 'faker_automotive',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.CarInfo]
            },
            {
                "name": SystemFuncType.BankInfo,
                "id": 'faker_bank',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.BankInfo]
            },
            {
                "name": SystemFuncType.PhoneInfo,
                "id": 'faker_phone_number',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.PhoneInfo]
            },
            {
                "name": SystemFuncType.PersonInfo,
                "id": 'faker_person',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.PersonInfo]
            },
            {
                "name": SystemFuncType.CompanyInfo,
                "id": 'faker_company',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.CompanyInfo]
            },
            {
                "name": SystemFuncType.JobInfo,
                "id": 'faker_job',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.JobInfo]
            },
            {
                "name": SystemFuncType.TimeInfo,
                "id": 'faker_date_time',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.TimeInfo]
            },
            {
                "name": SystemFuncType.InternetInfo,
                "id": 'faker_internet',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.InternetInfo]
            },
            {
                "name": SystemFuncType.ColorInfo,
                "id": 'faker_color',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.ColorInfo]
            },
            {
                "name": SystemFuncType.PythonBaseData,
                "id": 'faker_python',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.PythonBaseData]
            },
            {
                "name": SystemFuncType.BuildFunc,
                "id": 'faker_misc',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.BuildFunc]
            },
            {
                "name": SystemFuncType.TextInfo,
                "id": 'faker_lorem',
                "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.TextInfo]
            },
        ]
    },
    {
        "name": SystemFuncType.BuildFunc,
        "id": 'py_built_func',
        "children": [obj for obj in system_func_actions if obj['group'] == SystemFuncType.BuildFunc]
    }
]
