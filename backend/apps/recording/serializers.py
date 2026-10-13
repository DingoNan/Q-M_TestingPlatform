# -*- coding: utf-8 -*-
"""录制会话序列化器（P0-②）

★ 列表与详情分开两个序列化器，不是重复代码，是刻意的带宽设计：
  `raw_payload` + `ir_payload` 实测可以到几百 KB（一段百步录制的事件流）；
  履历页一次拉 20 条就会产生十几 MB 响应，在测试内网也会明显卡顿。
  所以列表只给元信息，要看内容必须显式请求详情。
"""
from rest_framework import serializers

from apps.recording.models import RecordingSession
from utils.base import BaseSerializer


class RecordingSessionListSerializer(BaseSerializer):
    """履历页用：不含事件流与 IR（那两个字段可能很大）。"""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    case_name = serializers.CharField(source='case.name', read_only=True)

    class Meta:
        model = RecordingSession
        exclude = ('raw_payload', 'ir_payload')


class RecordingSessionSerializer(BaseSerializer):
    """详情用：全字段（含 IR，供审阅台渲染）。"""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    case_name = serializers.CharField(source='case.name', read_only=True)

    class Meta:
        model = RecordingSession
        fields = '__all__'


class RecordingSessionCreateSerializer(serializers.Serializer):
    """创建会话的入参。

    只有 `project_id` 必填 —— 其余都能在结束录制时再补（start_url 往往要等
    第一个 navigate 事件才知道）。
    """

    project_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=False, allow_blank=True, max_length=128)
    source = serializers.ChoiceField(
        required=False, choices=[c[0] for c in RecordingSession.Source.choices])
    case_id = serializers.IntegerField(required=False, allow_null=True)
    start_url = serializers.CharField(required=False, allow_blank=True, max_length=512)
