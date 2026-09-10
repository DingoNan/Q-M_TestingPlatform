from django.db import models
from rest_framework.response import Response
from collections import OrderedDict
from django_filters import BaseInFilter, NumberFilter
from rest_framework.exceptions import NotFound
from django.contrib.auth.models import AnonymousUser
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class BaseSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)
    is_delete = serializers.BooleanField(read_only=True, required=False)
    create_by_name = serializers.CharField(source='create_by.username', read_only=True)
    update_by_name = serializers.CharField(source='update_by.username', read_only=True)

    def create(self, validated_data):
        validated_data['create_by'] = self.context['user']
        validated_data['update_by'] = self.context['user']
        if isinstance(validated_data['create_by'], AnonymousUser):
            validated_data.pop('create_by')
            validated_data.pop('update_by')

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 每次更新都设置 update_by 为当前用户
        user = self.context['user']
        if not isinstance(user, AnonymousUser):
            validated_data['update_by'] = user
        return super().update(instance, validated_data)

    # class Meta:
    #     fields = ['create_time', 'update_time', 'is_delete', 'create_by_name', 'update_by_name']


class BaseModel(models.Model):
    is_delete = models.BooleanField('逻辑删除', help_text='逻辑删除', default=False)
    create_time = models.DateTimeField(help_text='创建时间', auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(help_text='更新时间', auto_now=True, verbose_name='更新时间')
    create_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='%(class)s_create_by')
    update_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='%(class)s_update_by')

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """重写数据库删除方法实现逻辑删除"""
        self.is_delete = True
        self.save()


class BasePageNumberPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100
    page_size_query_param = 'size'
    page_query_param = 'page'

    def get_paginated_response(self, data):
        # 无效页面或超出范围时返回空列表
        if not data:
            return Response(OrderedDict([
                ('count', 0),
                ('results', [])
            ]))

        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def paginate_queryset(self, queryset, request, view=None):
        """重写分页方法，处理无效页面"""
        try:
            return super().paginate_queryset(queryset, request, view)
        except NotFound:
            return []


class CustomRender(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        重写render方法，并在该方法内自定义返回数据格式
        """
        status_code = renderer_context['response'].status_code
        response = {
            "code": status_code,
            "msg": "ok" if status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED] else "error",
        }
        if data:
            uri = renderer_context['request'].path
            if uri.startswith('/api_mock/'):
                response = data
            elif 'results' in data:
                response.update(data)
            elif isinstance(data, list):
                response['results'] = data
            else:
                response['result'] = data

        return super().render(response, accepted_media_type=accepted_media_type, renderer_context=renderer_context)



