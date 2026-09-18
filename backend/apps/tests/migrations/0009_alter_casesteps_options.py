from django.db import migrations


class Migration(migrations.Migration):
    """
    把 CaseSteps 的默认排序从单键 ['step_index'] 改为全序键 ['case_id', 'step_index', 'id']。

    原因：step_index 只表示「在某条用例内是第几步」，不同用例之间必然大量重复
    （每条用例都有 0/1/2…）。仅按 step_index 排序时，相同键记录的物理顺序由数据库决定，
    在 LIMIT/OFFSET 分页下会出现**跨页重复与漏行**（实测总 565 条、page_size=500 时复现），
    调用方据此删除步骤会删不干净，残留步骤与新步骤混跑。
    补上 case_id、id 后排序唯一，分页稳定。
    """

    dependencies = [
        ('tests', '0008_alter_historicalcase_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='casesteps',
            options={'ordering': ['case_id', 'step_index', 'id'],
                     'verbose_name': '用例步骤表',
                     'verbose_name_plural': '用例步骤表'},
        ),
    ]
