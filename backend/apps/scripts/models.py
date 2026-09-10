from django.db import models

from utils.base import BaseModel
from simple_history.models import HistoricalRecords


class PythonScript(BaseModel):
    name = models.CharField(verbose_name='函数名称', max_length=20, unique=True, error_messages={'unique': '函数名称不能重复'})
    desc = models.CharField(verbose_name='函数描述', max_length=300)
    package = models.TextField(verbose_name='导包信息')
    script = models.TextField(verbose_name='函数体')
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    module = models.ForeignKey('envs.Module', on_delete=models.PROTECT)

    history = HistoricalRecords()

    class Meta:
        db_table = 'tb_python'
        verbose_name = '函数表'
        verbose_name_plural = verbose_name


class EnumScript(BaseModel):
    name = models.CharField(verbose_name='枚举值名称', max_length=20, unique=True, error_messages={'unique': '常量类名不能重复'})
    desc = models.CharField(verbose_name='枚举值描述', max_length=300)
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    module = models.ForeignKey('envs.Module', on_delete=models.PROTECT)
    value = models.JSONField(verbose_name='枚举值', default=list)

    class Meta:
        db_table = 'tb_script_enum'
        verbose_name = '枚举值表'
        ordering = ['-create_time']
        verbose_name_plural = verbose_name


class File(BaseModel):

    name = models.CharField(verbose_name='文件名称', max_length=50)
    desc = models.CharField(verbose_name='文件描述', max_length=300)
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)

    class Meta:
        db_table = 'tb_file'
        verbose_name = '文件上传'
        ordering = ['-create_time']
        verbose_name_plural = verbose_name
