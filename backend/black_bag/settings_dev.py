from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


MEDIA_URL = '/upload_files/'  # 图片的访问 URL 前缀
MEDIA_ROOT = os.path.join(BASE_DIR, 'upload_files')  # 图片的存储路径
IMG_HOST = 'http://192.168.2.202:8000'

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True
# 允许cookies跨域
CORS_ALLOW_CREDENTIALS = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'release3.db'
    }
}