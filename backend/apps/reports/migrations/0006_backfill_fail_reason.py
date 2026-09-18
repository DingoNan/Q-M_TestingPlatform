# -*- coding: utf-8 -*-
"""回填历史失败报告的 fail_reason。

背景：`fail_reason` 是本版新增的独立字段。在此之前，「失败/中断原因」被塞进
`exceptions_statistics`（语义错配，那是原始异常明细）。若不回填，升级前就已经
「失败」的报告在详情页看不到「失败原因」卡片。

本迁移把历史失败（test_process=3）报告的 `exceptions_statistics[*].msg`
归并写入 `fail_reason`，使其与新写入的数据表现一致。
无失败记录时是空操作；反向操作为 noop（回填属幂等的数据订正，不回滚）。
"""
from django.db import migrations

MAX_LEN = 1000


def backfill(apps, schema_editor):
    LocustReport = apps.get_model('reports', 'LocustReport')
    # 只处理 fail_reason 还空着的失败报告
    pending = [r for r in LocustReport.objects.filter(test_process=3)
               if not (r.fail_reason or '').strip()]
    fixed = 0
    for r in pending:
        msgs = []
        stats = r.exceptions_statistics or []
        if isinstance(stats, list):
            for item in stats:
                if isinstance(item, dict) and item.get('msg'):
                    msgs.append(str(item['msg']).strip())
        if not msgs:
            continue
        reason = ' / '.join(m for m in msgs if m)[:MAX_LEN]
        LocustReport.objects.filter(id=r.id).update(fail_reason=reason)
        fixed += 1
    if fixed:
        print('\n  已回填 %d 条历史失败报告的 fail_reason' % fixed)


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_locustreport_fail_reason'),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
