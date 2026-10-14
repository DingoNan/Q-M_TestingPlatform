# -*- coding: utf-8 -*-
"""录制会话模型（P0-②）

设计取舍（与设计方案第 09 章一致）：
  · **能复用就不新建** —— 录制只是「产出入口」，产物（Case / Step / CaseSteps /
    Element）全部落在既有模型上。本表只存「录制过程数据」。
  · `raw_payload` 与 `ir_payload` 分开存：原始事件流是**证据**（出问题时可回溯），
    IR 是**产物**（落库的依据）。合成一个字段会导致「改了 IR 就再也还原不回去」。
  · `token` 是给浏览器扩展用的**会话级**凭据，不是用户的长期登录令牌 ——
    扩展里存长期令牌等于把账号密码交给一个网页扩展，风险不可接受。
"""

from django.db import models

from utils.base import BaseModel


class RecordingSession(BaseModel):
    class Status(models.IntegerChoices):
        RECORDING = 1, '录制中'
        FINISHED = 2, '已结束'
        REVIEWING = 3, '审阅中'
        IMPORTED = 4, '已导入'
        DISCARDED = 5, '已丢弃'

    class Source(models.TextChoices):
        MANUAL_UPLOAD = 'manual_upload', '手动导入录制文件'
        EXTENSION = 'extension', '浏览器扩展（实时推送）'
        DEVTOOLS_PLUGIN = 'devtools_plugin', 'DevTools Recorder 插件'
        CDP = 'cdp', 'CDP 接管'
        PLAYWRIGHT_SCRIPT = 'playwright_script', 'Playwright 脚本'

    name = models.CharField(verbose_name='会话名称', max_length=128)
    project = models.ForeignKey('projects.Project', verbose_name='所属项目',
                                on_delete=models.CASCADE)
    # 目标用例；为空表示「待落库为新用例」
    case = models.ForeignKey('tests.Case', verbose_name='目标用例', null=True, blank=True,
                             on_delete=models.SET_NULL, related_name='recording_sessions')
    status = models.SmallIntegerField(verbose_name='状态', choices=Status.choices,
                                      default=Status.RECORDING)
    source = models.CharField(verbose_name='录制来源', max_length=24,
                              choices=Source.choices, default=Source.MANUAL_UPLOAD)
    start_url = models.CharField(verbose_name='起始地址', max_length=512, blank=True, default='')

    # 原始事件流：增量累积，支持断点续传（每条动作到达即推，单包很小）
    raw_payload = models.JSONField(verbose_name='原始事件流', default=dict, blank=True)
    # 归一化结果（core/recorder/normalizer.py 产出的 IR）
    ir_payload = models.JSONField(verbose_name='归一化结果(IR)', default=dict, blank=True)
    # 动作数 / 丢弃原因分布 / 元素新增与复用数
    stats = models.JSONField(verbose_name='统计', default=dict, blank=True)
    # AI 增强记录：模型 / 耗时 / token / 失败原因 —— 便于按项目核算成本
    ai_meta = models.JSONField(verbose_name='AI记录', default=dict, blank=True)

    # 扩展侧上传凭据（一次性 / 可续期），避免扩展持有用户长期令牌
    token = models.CharField(verbose_name='上传凭据', max_length=64, blank=True, default='',
                             db_index=True)

    # ==================== P4 断网补传 · 幂等闸门 ====================
    # ★ 为什么必须有这个字段：/recording/session/<id>/events/ 在 append=true（默认）
    #   下是**追加**语义 —— 客户端网络恢复后重发未确认的批次，就会**重复写入**。
    #   实施计划 §07 里写的「端点已是幂等设计」是错的，这里补上真正的幂等键。
    #
    #   约定：幂等键 = (session_id, seq)。seq 由客户端在会话内单调递增、从 1 开始。
    #   收到事件时丢弃 `seq <= last_seq` 的条目，成功后把 last_seq 推进到本批最大值。
    #   初值 0 ⇒ 第一条合法 seq 是 1。
    #
    #   ★ 唯一正确性前提：客户端必须按 seq **升序**发送。乱序会让 last_seq 把后面
    #     的合法事件挡掉（宁可少收也不能错收，所以服务端按「单调推进」实现）。
    last_seq = models.IntegerField(verbose_name='已接收的最大事件序号', default=0)
    imported_case_id = models.IntegerField(verbose_name='落库生成的用例ID', null=True, blank=True)

    class Meta:
        db_table = 'tb_recording_session'
        ordering = ['-create_time', '-id']
        verbose_name = '录制会话表'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['project', 'status'], name='idx_rec_project_status'),
        ]

    def __str__(self):
        return '%s(%s)' % (self.name, self.get_status_display())
