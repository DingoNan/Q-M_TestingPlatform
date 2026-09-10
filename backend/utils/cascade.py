"""
级联软删除工具
================
平台里的模型基本都继承 utils.base.BaseModel，带 is_delete 逻辑删除标记，
但 ORM 层的 on_delete=PROTECT/DO_NOTHING 只作用于物理删除，软删除完全不触发，
导致「删了项目，下面的一堆模块/用例/计划还挂着」这种孤儿数据。

本模块提供通用的**级联软删除**：沿反向外键递归，把下游所有带 is_delete 的记录
一并置为 is_delete=True，并返回删除统计，便于接口回传明细给前端提示。

设计要点：
- 只沿 one_to_one / one_to_many（反向外键）递归，跳过 many_to_many，
  避免把共享的 Tag / Step 等公共记录误删。
- 跳过 simple_history 生成的 Historical* 镜像表。
- 用 visited 集合防环。
"""

from django.db import transaction


# 这些表属于跨项目共享或用户主数据，级联时不跟随
DEFAULT_EXCLUDE_LABELS = {
    'users.User',
}


def _is_historical(model):
    return model._meta.object_name.startswith('Historical')


def cascade_soft_delete(instance, exclude_labels=None, visited=None, stats=None):
    """级联软删除一个对象及其下游对象。

    :param instance: 待删除的模型实例（需带 is_delete 字段）
    :param exclude_labels: 不跟随的模型标签集合，如 {'users.User'}
    :param visited: 内部防环用的集合
    :param stats: 内部统计 dict，{model_label: count}
    :return: 统计 dict
    """
    exclude_labels = DEFAULT_EXCLUDE_LABELS if exclude_labels is None else set(exclude_labels)
    visited = set() if visited is None else visited
    stats = {} if stats is None else stats

    obj_label = f'{instance._meta.app_label}.{instance._meta.object_name}'
    obj_key = (obj_label, instance.pk)
    if obj_key in visited:
        return stats
    visited.add(obj_key)

    for rel in instance._meta.related_objects:
        # 只处理反向外键(ManyToOneRel) / 一对一(OneToOneRel)，
        # M2M(ManyToManyRel) 属于共享关系，级联会把公共数据误删，跳过
        if rel.many_to_many:
            continue

        model = rel.related_model
        if _is_historical(model):
            continue
        label = f'{model._meta.app_label}.{model._meta.object_name}'
        if label in exclude_labels:
            continue
        if not hasattr(model, 'is_delete'):
            continue

        accessor = rel.get_accessor_name()
        try:
            related_manager = getattr(instance, accessor)
        except AttributeError:
            continue

        try:
            children = list(related_manager.filter(is_delete=False))
        except Exception:
            # 极少数自定义 manager 不支持 filter，直接跳过，不让主流程失败
            continue

        for child in children:
            cascade_soft_delete(child, exclude_labels, visited, stats)

        if children:
            related_manager.filter(is_delete=False).update(is_delete=True)
            stats[label] = stats.get(label, 0) + len(children)

    # 最后删除自身
    if hasattr(instance, 'is_delete'):
        model = type(instance)
        model.objects.filter(pk=instance.pk, is_delete=False).update(is_delete=True)
        stats[obj_label] = stats.get(obj_label, 0) + 1

    return stats


def cascade_soft_delete_atomic(instance, exclude_labels=None):
    """事务包裹的级联软删除，返回统计 dict"""
    with transaction.atomic():
        return cascade_soft_delete(instance, exclude_labels)
