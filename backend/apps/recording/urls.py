# -*- coding: utf-8 -*-
"""录制模块路由（P0-② + P1）

★ 路径一律写全（不带 `recording/` 自动前缀）—— 平台的根路由是
  `path('', include('apps.xxx.urls'))`，各 app 的 urls.py 自己负责完整前缀。
  曾经的坑：以为 include 会带前缀，结果把 `/import_har_sync/` 写成了
  `/interface/import_har_sync/`，前端 404 排查了很久。

★ 另一个坑：Django 的 `path()` 里**不写前导斜杠**，而前端 HTTP 路径**一定写**。
  做「前后端契约对齐」的自动比对时必须先归一化，否则两边永远对不上，
  会得到「前端全缺 + 后端全孤立」这种自相矛盾的结果。
"""
from django.urls import path

from apps.recording import views

urlpatterns = [
    # 会话（履历 / 实时推送）
    path('recording/session/', views.recording_session_create),
    path('recording/session/list/', views.recording_session_list),
    path('recording/session/<int:session_id>/', views.recording_session_detail),
    path('recording/session/<int:session_id>/events/', views.recording_session_events),
    path('recording/session/<int:session_id>/finish/', views.recording_session_finish),
    path('recording/session/<int:session_id>/discard/', views.recording_session_discard),
    path('recording/session/<int:session_id>/ai_enhance/', views.recording_session_ai_enhance),
    # ★ P1 审阅台：编辑只改 ir_payload，不落库（落库是 /recording/import/ 那一次原子动作）
    path('recording/session/<int:session_id>/patch/', views.recording_session_patch),

    # 录制数据入口
    path('recording/parse/', views.recording_parse),
    path('recording/import/', views.recording_import),
]
