# -*- coding: utf-8 -*-
"""Web 自动化录制（P0-②）

把浏览器录制的操作流转成平台可执行的步骤用例。

模块分工
    models.py    RecordingSession —— 录制会话（原始事件流 + 归一化 IR + 统计 + AI 记录）
    importer.py  IR → Step / CaseSteps / Element / Case 的落库（唯一写库入口）
    views.py     9 个端点（会话 / 动作增量推送 / 结束 / 预览 / 编辑 / 落库 / AI / 列表 / 扩展授权）
    urls.py      挂在 /recording/ 前缀下

★ 归一化逻辑**不在本 app 里**，在 `core/recorder/`（纯 Python，无 Django 依赖，可离线单测）。
  本 app 只负责「存」与「落库」，不承担转换逻辑 —— 这样转换逻辑才能被完整测到。
"""
