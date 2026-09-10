from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

MEDIA_URL = '/upload_files/'        # URL 前缀（必须斜杠开头/结尾）
MEDIA_ROOT = os.path.join(BASE_DIR, 'upload_files')

CORS_ALLOW_ALL_ORIGINS = True
# 允许cookies跨域
CORS_ALLOW_CREDENTIALS = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # 'zqc_db'/39.101.141.162
        'HOST': '192.168.2.31',
        'PORT': 33306,
        'USER': 'root',
        'PASSWORD': 'Test#Platform',
        'NAME': 'blackbag',
    }
}