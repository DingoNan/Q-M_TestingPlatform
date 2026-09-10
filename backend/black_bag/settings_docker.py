from .settings import *

# 让 Django 的 mysql 后端使用 PyMySQL（requirements 中安装的是 PyMySQL 而非 mysqlclient）
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# ===== Docker 部署配置（所有参数从环境变量读取，便于 docker-compose 注入）=====

DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 静态文件收集目录（容器内收集后由 gunicorn/后端直接提供）
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/upload_files/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'upload_files')
IMG_HOST = os.environ.get('IMG_HOST', '')

# ===== MySQL 数据库（从环境变量读取）=====
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.environ.get('MYSQL_HOST', 'mysql'),
        'PORT': os.environ.get('MYSQL_PORT', '3306'),
        'USER': os.environ.get('MYSQL_USER', 'root'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'blackbag'),
        'NAME': os.environ.get('MYSQL_DATABASE', 'blackbag'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# ===== Django Q2：Redis 配置（从环境变量读取）=====
Q_CLUSTER = {
    'name': 'black_bag',
    'workers': 2,
    'recycle': 500,
    'timeout': 3600,
    'retry': 7200,
    'max_attempts': 4,
    'compress': True,
    'save_limit': 1000,
    'queue_limit': 500,
    'label': 'Django Q',
    'redis': {
        'host': os.environ.get('REDIS_HOST', 'redis'),
        'port': int(os.environ.get('REDIS_PORT', '6379')),
        'db': int(os.environ.get('REDIS_DB', '0')),
        'password': os.environ.get('REDIS_PASSWORD', '') or None,
    }
}
