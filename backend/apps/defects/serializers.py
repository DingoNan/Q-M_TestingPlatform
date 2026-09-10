from rest_framework import serializers
from utils.base import BaseSerializer
from apps.defects.models import Defect, DefectComment
from apps.tests.models import FuncCase
from apps.tests.serializers import FuncCaseSerializer


class DefectCommentSerializer(BaseSerializer):
    comment_by_name = serializers.CharField(source='comment_by.username', read_only=True)
    comment_by_id = serializers.IntegerField(source='comment_by.id', read_only=True)
    mentioned_users = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = DefectComment
        fields = '__all__'

    def create(self, validated_data):
        mentioned_users = validated_data.pop('mentioned_users', [])
        validated_data['comment_by'] = self.context['user']
        comment = super().create(validated_data)
        self._create_mention_messages(comment, mentioned_users)
        return comment

    def _create_mention_messages(self, comment, mentioned_users):
        """为被@提及的用户发送系统通知站内信"""
        from apps.messages.models import Message
        from apps.users.models import User
        if not mentioned_users:
            return
        defect = comment.defect
        project = defect.project
        users = User.objects.filter(id__in=mentioned_users)
        if not users.exists():
            return
        commenter_name = comment.comment_by.username if comment.comment_by else '系统'
        title = '您在缺陷评论中被@提及'
        content = f'{commenter_name} 在缺陷【{defect.title}】的评论中@了您'
        related_url = f'/defect/list?action=view&id={defect.id}'
        Message.objects.bulk_create([
            Message(
                user=u,
                project=project,
                title=title,
                content=content,
                message_type=Message.MessageType.SYSTEM,
                related_url=related_url,
                create_by=comment.comment_by,
                update_by=comment.comment_by,
            ) for u in users
        ])


class DefectSerializer(BaseSerializer):
    severity_name = serializers.CharField(source='get_severity_display', read_only=True)
    priority_name = serializers.CharField(source='get_priority_display', read_only=True)
    defect_type_name = serializers.CharField(source='get_defect_type_display', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True, default='')
    module_name = serializers.CharField(source='module.name', read_only=True)
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)
    assignee_id = serializers.IntegerField(source='assignee.id', read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    func_cases = serializers.PrimaryKeyRelatedField(many=True, queryset=FuncCase.objects.all(), required=False)
    func_cases_info = FuncCaseSerializer(source='func_cases', many=True, read_only=True)
    comments = DefectCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Defect
        fields = '__all__'
