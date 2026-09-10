from django.db import models
from django.contrib.auth.models import AbstractUser

from utils.base import BaseModel
from simple_history.models import HistoricalRecords


class User(AbstractUser, BaseModel):
    email = models.EmailField(help_text='邮箱', blank=True, null=True)
    is_online = models.BooleanField(help_text='是否在线', default=False)

    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    REQUIRED_FIELDS = []
    history = HistoricalRecords()


class Group(BaseModel):
    name = models.CharField('分组名称', help_text='分组名称', max_length=20)
    sort = models.IntegerField('排序值', default=0)

    class Meta:
        db_table = 'tb_group'
        verbose_name = '分组表'
        verbose_name_plural = verbose_name
        ordering = ['sort']


class Navigation(BaseModel):
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    name = models.CharField('导航名称', help_text='导航名称', max_length=20)
    color = models.CharField('背景颜色', help_text='背景颜色', max_length=30)
    icon_url = models.URLField(verbose_name='图标地址')
    url = models.URLField(verbose_name='跳转地址')

    class Meta:
        db_table = 'tb_navigation'
        verbose_name = '导航表'
        verbose_name_plural = verbose_name


class Role(BaseModel):
    name = models.CharField('角色名称', help_text='角色名称', max_length=20, unique=True)
    permission = models.ManyToManyField('Permission', help_text='所属角色', through='RolePermission')

    def permissions(self):
        return RolePermission.objects.filter(role_id=self, has_permission=True).count()

    history = HistoricalRecords()

    class Meta:
        db_table = 'tb_role'
        verbose_name = '角色表'
        verbose_name_plural = verbose_name


class RolePermission(BaseModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey('Permission', on_delete=models.DO_NOTHING)
    has_permission = models.BooleanField('是否有权限', default=False)
    has_read_permission = models.BooleanField('是否有读的权限', default=False)
    has_edit_permission = models.BooleanField('是否有编辑权限', default=False)
    has_add_permission = models.BooleanField('是否有新增权限', default=False)
    has_delete_permission = models.BooleanField('是否有删除权限', default=False)

    class Meta:
        db_table = 'tb_role_permission'
        verbose_name = '角色权限表'
        verbose_name_plural = verbose_name


class Permission(BaseModel):
    class MenuLevel(models.IntegerChoices):
        FIRST_MENU = 1, '一级菜单'
        SECOND_MENU = 2, '二级菜单'

    name = models.CharField('菜单名称', max_length=20, help_text='权限名称')
    level = models.IntegerField(choices=MenuLevel.choices, default=MenuLevel.FIRST_MENU, help_text='菜单类型')
    parent = models.IntegerField('父ID', help_text='父ID', default=0)
    path = models.CharField('菜单跳转路径', max_length=50, help_text='菜单跳转路径')
    icon = models.CharField('菜单图标', max_length=20, help_text='菜单图标')

    history = HistoricalRecords()

    class Meta:
        db_table = 'tb_permission'
        verbose_name = '权限表'
        verbose_name_plural = verbose_name

