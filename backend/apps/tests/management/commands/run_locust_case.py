"""性能压测执行入口（独立进程）。

被 `apps/tests/views.locust_run` 通过 `subprocess` 拉起：

    python manage.py run_locust_case <case_id> <env_id> <user_id> <run_times> <rate> <user_num> <report_id>

为什么要独立进程：locust 在 import 时会执行 `gevent.monkey.patch_all()`，若在 web
进程（uvicorn worker）内触发，会 patch 掉该 worker 的 ssl/threading/socket 并把 asyncio
事件循环弄坏，导致该 worker 之后所有请求 500、压测 greenlet 永不调度、报告永久停留在
「压测中」。放到独立进程后 monkey-patch 只作用于本进程。

本命令还会把自己的 PID 写入 `logs/locust_<report_id>.pid`，供
`locust_report_watchdog` 守护进程判断「报告仍压测中但进程已死」的情形。
"""
import os
import sys

from django.core.management.base import BaseCommand

from apps.reports.models import LocustReport


def pid_file_path(report_id):
    from black_bag.settings import BASE_DIR
    return os.path.join(BASE_DIR, 'logs', 'locust_%s.pid' % report_id)


class Command(BaseCommand):
    help = '在独立进程中执行一次 Locust 性能压测（避免 gevent monkey-patch 污染 web 进程）'

    def add_arguments(self, parser):
        parser.add_argument('case_id', type=int)
        parser.add_argument('env_id', type=int)
        parser.add_argument('user_id', type=int)
        parser.add_argument('run_times', type=int)
        parser.add_argument('rate', type=int)
        parser.add_argument('user_num', type=int)
        parser.add_argument('report_id', type=int)

    def handle(self, *args, **options):
        report_id = options['report_id']

        # 落地 PID 文件：守护进程据此判断「报告仍在压测中，但对应进程已经不存在」
        pid_path = pid_file_path(report_id)
        try:
            os.makedirs(os.path.dirname(pid_path), exist_ok=True)
            with open(pid_path, 'w') as f:
                f.write(str(os.getpid()))
        except Exception as e:
            print('[locust] 写入 PID 文件失败：%s' % e, flush=True)

        try:
            # 延迟到 handle 内导入：本模块被 Django 自动发现时不应触发 locust 导入
            from apps.tests.views import run_locust_standalone
            run_locust_standalone(
                options['case_id'], options['env_id'], options['user_id'],
                options['run_times'], options['rate'], options['user_num'],
                report_id,
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            # 失败收口：标为「失败」而不是「已完成」—— 这类报告没有任何统计数据，
            # 标成已完成会误导用户；同时把原因写进异常统计，前端「异常统计」表会直接展示。
            try:
                report = LocustReport.objects.filter(id=report_id).first()
                if report is not None:
                    exceptions = list(report.exceptions_statistics or [])
                    exceptions.append({
                        'count': 1,
                        'msg': '压测执行失败：%s' % e,
                        'traceback': traceback.format_exc()[-2000:],
                    })
                    LocustReport.objects.filter(id=report_id).update(
                        test_process=LocustReport.TestProcess.Failed,
                        exceptions_statistics=exceptions,
                    )
            except Exception as e2:
                print('[locust] 失败收口写库也失败了：%s' % e2, flush=True)
            self.stderr.write('压测执行失败：%s' % e)
            sys.exit(1)
        finally:
            # 正常或异常结束都清掉 PID 文件，避免守护进程误判
            try:
                os.remove(pid_path)
            except Exception:
                pass
