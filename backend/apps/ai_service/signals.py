"""
向量库自动同步信号

监听 FuncCase / Api / Defect 的增删改事件，
自动同步到 ChromaDB 向量库。

信号触发时机:
  - post_save:    新增或更新时
  - post_delete:  硬删除时
  - pre_save:     状态变化检测（如缺陷从"处理中"→"已解决"）

注意:
  - 向量库操作包裹在 try/except 中，不影响主业务流程
  - 使用 ai_service 的 ready() 方法注册信号
"""
import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_q.tasks import async_task

logger = logging.getLogger('ai_service')


# ==================== 功能用例 ====================

@receiver(post_save, sender='tests.FuncCase')
def sync_func_case_to_vectorstore(sender, instance, created, **kwargs):
    """功能用例保存时异步同步向量库（后台执行，不阻塞主请求）"""
    try:
        action = 'delete' if instance.is_delete else ('create' if created else 'update')
        async_task(
            'apps.ai_service.vectorstore.sync_entity_async',
            'func_case', action, instance.project_id, instance.id,
        )
    except Exception as e:
        logger.error(f"[向量同步] 功能用例 {instance.id} 提交异步同步失败: {e}")


@receiver(post_delete, sender='tests.FuncCase')
def delete_func_case_from_vectorstore(sender, instance, **kwargs):
    """功能用例硬删除时异步清理向量库"""
    try:
        async_task(
            'apps.ai_service.vectorstore.sync_entity_async',
            'func_case', 'delete', instance.project_id, instance.id,
        )
    except Exception as e:
        logger.error(f"[向量同步] 功能用例 {instance.id} 提交删除失败: {e}")


# ==================== 接口文档 ====================

@receiver(post_save, sender='interfaces.Api')
def sync_api_to_vectorstore(sender, instance, created, **kwargs):
    """接口文档保存时异步同步向量库（后台执行，不阻塞主请求）"""
    try:
        project_id = instance.module.project_id if instance.module_id else None
        if not project_id:
            return
        action = 'delete' if instance.is_delete else ('create' if created else 'update')
        async_task(
            'apps.ai_service.vectorstore.sync_entity_async',
            'api', action, project_id, instance.id,
        )
    except Exception as e:
        logger.error(f"[向量同步] 接口 {instance.id} 提交异步同步失败: {e}")


@receiver(post_delete, sender='interfaces.Api')
def delete_api_from_vectorstore_signal(sender, instance, **kwargs):
    """接口文档硬删除时异步清理向量库"""
    try:
        project_id = instance.module.project_id if instance.module_id else None
        if project_id:
            async_task(
                'apps.ai_service.vectorstore.sync_entity_async',
                'api', 'delete', project_id, instance.id,
            )
    except Exception as e:
        logger.error(f"[向量同步] 接口 {instance.id} 提交删除失败: {e}")


# ==================== 缺陷 ====================

@receiver(post_save, sender='defects.Defect')
def sync_defect_to_vectorstore(sender, instance, created, **kwargs):
    """缺陷保存时异步同步向量库（后台执行，不阻塞主请求）"""
    try:
        action = 'delete' if instance.is_delete else ('create' if created else 'update')
        async_task(
            'apps.ai_service.vectorstore.sync_entity_async',
            'defect', action, instance.project_id, instance.id,
        )
    except Exception as e:
        logger.error(f"[向量同步] 缺陷 {instance.id} 提交异步同步失败: {e}")


@receiver(post_delete, sender='defects.Defect')
def delete_defect_from_vectorstore_signal(sender, instance, **kwargs):
    """缺陷硬删除时异步清理向量库"""
    try:
        async_task(
            'apps.ai_service.vectorstore.sync_entity_async',
            'defect', 'delete', instance.project_id, instance.id,
        )
    except Exception as e:
        logger.error(f"[向量同步] 缺陷 {instance.id} 提交删除失败: {e}")


# ==================== 元素 ====================

@receiver(post_save, sender='elements.Element')
def sync_element_to_vectorstore(sender, instance, created, **kwargs):
    """元素保存时异步同步向量库（后台执行，不阻塞主请求）"""
    try:
        action = 'delete' if instance.is_delete else ('create' if created else 'update')
        async_task(
            'apps.ai_service.vectorstore.sync_entity_async',
            'element', action, instance.project_id, instance.id,
        )
    except Exception as e:
        logger.error(f"[向量同步] 元素 {instance.id} 提交异步同步失败: {e}")


@receiver(post_delete, sender='elements.Element')
def delete_element_from_vectorstore_signal(sender, instance, **kwargs):
    """元素硬删除时异步清理向量库"""
    try:
        async_task(
            'apps.ai_service.vectorstore.sync_entity_async',
            'element', 'delete', instance.project_id, instance.id,
        )
    except Exception as e:
        logger.error(f"[向量同步] 元素 {instance.id} 提交删除失败: {e}")
