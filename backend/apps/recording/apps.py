from django.apps import AppConfig


class RecordingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.recording'
    # ★ 这里**故意不写 label**，与平台其余 app（tests / interfaces / elements /
    #   ai_service）保持一致 —— 默认 label 取 name 的末段，即 `recording`。
    #   只有与 Django 内置 app 撞名时才需要显式 label（例如 apps/messages 必须
    #   写成 `app_messages`，否则会顶掉 django.contrib.messages）。
    #   显式写 `app_recording` 的后果：`manage.py makemigrations recording` 会报
    #   「No installed app with label 'recording'」，迁移依赖也得跟着写 app_recording，
    #   白白制造一处与全平台不一致的命名。
    verbose_name = 'Web自动化录制'
