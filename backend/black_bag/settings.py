import os
import time
import sys
import faulthandler
from datetime import timedelta
from pathlib import Path

# 注册 faulthandler：进程发生 C 层崩溃（段错误/abort，如 torch/onnxruntime/playwright driver）
# 时，向 stderr 输出 Python 栈，便于定位 Django Q worker 静默退出/任务丢失的根因。
# 对 fork 出来的 worker 子进程同样生效（异常处理器随进程继承）。
faulthandler.enable()

os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'

# ===== HuggingFace / ChromaDB 环境变量（必须在任何第三方库导入前设置）=====
# 不设置 HF_ENDPOINT：hf-mirror.com 对模型文件的 308 重定向会让 huggingface_hub
# 报 "Distant resource does not seem to be on huggingface.co"，模型已固化进镜像，运行时离线加载。
# 禁用 ChromaDB 遥测（避免 posthog 版本不兼容导致 capture() 报错）
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
# 禁用 Windows 符号链接警告
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
# 模型已固化进镜像（Dockerfile snapshot_download），运行时强制离线加载：
# 不设离线标志时 huggingface_hub 解析模型名会联网检查，而容器运行时网络不可达
# （构建期代理不保留），导致 AI 元素任务在向量去重阶段静默卡死。
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+zq4f)u852#!qz5abbjv6(4lm0=ct4653=ogwa!))+j+&+^-^='


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'django_q',
    'channels',
    'apps.users.apps.UsersConfig',
    'apps.projects.apps.ProjectsConfig',
    'apps.envs.apps.EnvsConfig',
    'apps.interfaces.apps.InterfacesConfig',
    'apps.elements.apps.ElementsConfig',
    'apps.scripts.apps.ScriptsConfig',
    'apps.suites.apps.SuitesConfig',
    'apps.tests.apps.TestsConfig',
    'apps.reports.apps.ReportsConfig',
    'apps.defects.apps.DefectsConfig',
    'apps.tools.apps.ToolsConfig',
    'apps.messages.apps.MessagesConfig',
    'apps.ai_service.apps.AiServiceConfig',
    'apps.audit.apps.AuditConfig',
    'simple_history',
]

AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'apps.audit.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'black_bag.urls'

# Channels 配置
ASGI_APPLICATION = 'black_bag.asgi.application'

# Redis 地址(本地开发默认 127.0.0.1，Docker 内用服务名 redis)
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '') or None
REDIS_DB = 0

# Channels channel layer(WebSocket 跨进程消息分发，依赖 Redis)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [{
                'address': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
                'password': REDIS_PASSWORD,
            }],
        },
    },
}


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'black_bag.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 日志
log_path = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(log_path):
    os.mkdir(log_path)  # 如果不存在这个logs文件夹，创建


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'django.db.backends': {
        'handlers': ['console'],
        'propagate': True,
        'level': 'INFO',
    },
    'formatters': {
        # 日志格式
        'standard': {
            'format': '[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] '
                      '[%(levelname)s]- %(message)s'},
        'myconsole': {
            'format': '[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s]- %(message)s'},
        'simple': {  # 简单格式
            'format': '%(levelname)s %(message)s'
        },
    },
    # 过滤
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    # 定义具体处理日志的方式
    'handlers': {
        # 默认记录所有日志
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_path, 'all-{}.log'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 5,  # 文件大小
            'backupCount': 5,  # 备份数
            'formatter': 'standard',  # 输出格式
            'encoding': 'utf-8',  # 设置默认编码，否则打印出来汉字乱码
        },
        # 输出错误日志
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_path, 'error-{}.log'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 5,  # 文件大小
            'backupCount': 5,  # 备份数
            'formatter': 'standard',  # 输出格式
            'encoding': 'utf-8',  # 设置默认编码
        },
        # 控制台输出
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            # 'stream': open(os.path.join(log_path, 'print-{}.log'.format(time.strftime('%Y-%m-%d'))), 'a'),
            # 虽然成功了，但是并没有将所有内容全部写入文件，目前还不清楚为什么
            'formatter': 'standard',  # 制定输出的格式，注意 在上面的formatters配置里面选择一个，否则会报错
            # 'encoding': 'utf-8',  # 设置默认编码
        },
        # 输出info日志
        'info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_path, 'info-{}.log'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf-8',  # 设置默认编码
        },  # 输出警告日志
        'warning': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_path, 'warning-{}.log'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf-8',  # 设置默认编码
        },  # 输出严重错误日志
        'critical': {
            'level': 'CRITICAL',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_path, 'critical-{}.log'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'myconsole',
            'encoding': 'utf-8',  # 设置默认编码
        },  # 输出警告日志
        'django_q': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_path, 'django-q-{}.log'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'myconsole',
            'encoding': 'utf-8',
        },
    },
    # 配置用哪几种 handlers 来处理日志
    'loggers': {
        # 类型 为 django 处理所有类型的日志， 默认调用
        'django': {
            'handlers': ['console', 'error', 'info', 'warning', 'critical', 'console'],
            'level': 'INFO',
            'propagate': False
        },
        'django_q': {
            'handlers': ['console', 'django_q'],
            'level': 'DEBUG',
            'propagate': False
        },
        # log 调用时需要当作参数传入
        'log': {
            'handlers': ['error', 'info', 'console', 'default'],
            'level': 'INFO',
            'propagate': True
        },
        # AI服务日志
        'ai_service': {
            'handlers': ['console', 'info', 'error'],
            'level': 'INFO',
            'propagate': False
        },
        # 元素服务日志
        'elements': {
            'handlers': ['console', 'info', 'error'],
            'level': 'INFO',
            'propagate': False
        },
        # 测试任务日志
        'apps.tests.tasks': {
            'handlers': ['console', 'info', 'error'],
            'level': 'INFO',
            'propagate': False
        },
        # 消息推送日志
        'apps.messages.push': {
            'handlers': ['console', 'info', 'error'],
            'level': 'INFO',
            'propagate': False
        },
        # 消息消费者日志
        'apps.messages.consumers': {
            'handlers': ['console', 'info', 'error'],
            'level': 'INFO',
            'propagate': False
        },
    }
}

# ===== AI服务配置 =====
# ChromaDB 向量数据库持久化目录
CHROMA_DIR = os.path.join(BASE_DIR, 'chroma_db')
# 本地Embedding模型
AI_EMBEDDING_MODEL = 'BAAI/bge-small-zh-v1.5'
# AI生成用例最大重试次数
AI_MAX_RETRIES = 2
# AI任务缓存超时（秒）
AI_TASK_CACHE_TIMEOUT = 3600

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ],
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticated',
    # ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_RENDERER_CLASSES': [
        'utils.base.CustomRender',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ],
    'EXCEPTION_HANDLER': 'utils.api_exception.custom_exception_handler',

}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    # 'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    # 'USER_ID_FIELD': 'id',
    # 'USER_ID_CLAIM': 'user_code',
    # 'ALGORITHM': 'HS256',
    # 'SIGNING_KEY': SECRET_KEY,
    # 'AUTH_HEADER_TYPES': ('Token',),
}

MEDIA_ROOT = BASE_DIR / 'upload_files'

IMG_HOST = 'http://192.168.2.15:18000'

MEDIA_URL = '/upload_files/'  # 图片的访问 URL 前缀

# Django Q2 配置
Q_CLUSTER = {
    'name': 'black_bag',
    'workers': 2,
    'recycle': 500,
    'timeout': 3600,
    'retry': 7200,  # 按需调整
    'max_attempts': 4,  # 允许重试最多2次，第3次失败后则不再重试
    'compress': True,
    'save_limit': 1000,
    'queue_limit': 500,
    'label': 'Django Q',
    'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
    }
}
