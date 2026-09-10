from rest_framework.views import exception_handler
from django.db.models import ProtectedError
from django.http import JsonResponse


def custom_exception_handler(exc, context):
    # 处理 ProtectedError（保护性删除错误）
    if isinstance(exc, ProtectedError):
        custom_message = None

        # 尝试从异常参数中获取自定义消息
        if exc.args and isinstance(exc.args[0], str):
            custom_message = exc.args[0]

        return JsonResponse({
            'code': 'protected_objects',
            'msg': custom_message,
            'result': {
                'error': [custom_message]
            }
        }, status=400)

    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    # if response is not None:
    #     print(response.__dict__, 33)
    #     response.data['desc'] = response.data.get('detail')

    return response
