"""压测报告守护进程：自动收口「僵尸报告」，让「永远压测中」不再出现。

## 背景

压测跑在独立子进程里（见 run_locust_case 的说明）。如果子进程被 OOM kill、
被手动 kill、或写回报告时网络/鉴权失败，报告就会永远停在 `test_process=2「压测中」`：

* 前端详情页每 2s 轮询一次，页面一直转（用户看到的是一条"没有结果"的报告）；
* 报告列表上这条记录永远显示「压测中」，既占位又误导。

## 判据（满足任一即判定该报告已中断）

1. **进程已死**：存在 `logs/locust_<id>.pid` 且其中 PID 已不存在 → 立即判定中断；
2. **超时未收口**：`now > start_time + 压测时长 + 宽限期` → 判定中断；
3. **进程存活但远超预期**：进程还在、但已超过 `start_time + 压测时长 + 硬上限`
   （默认 1800s）→ 判定中断（防止进程挂死导致报告永远不收口）。

## 收口动作

* `test_process` → `3 失败`（**不是**「已完成」：这类报告没有任何统计数据，
  标成已完成会误导用户；前端 `getStatusType` 已有 '失败' → danger 的映射）；
* `end_time` → 当前时间；
* 中断原因写入 `exceptions_statistics`，前端「异常统计」表会直接展示给用户。

## 用法

    python manage.py locust_report_watchdog --once          # 只扫一次（自测/人工巡检）
    python manage.py locust_report_watchdog --interval 30   # 常驻（由 supervisor 拉起）
"""
import os
import re
import time
import traceback
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.reports.models import LocustReport

LOG_DIR = None


def _log_dir():
    """压测日志/PID 文件所在目录（与 run_locust_case 落盘位置保持一致）。"""
    global LOG_DIR
    if LOG_DIR:
        return LOG_DIR
    try:
        from django.conf import settings
        base = getattr(settings, 'BASE_DIR', None)
    except Exception:
        base = None
    LOG_DIR = os.path.join(base or '/app', 'logs')
    return LOG_DIR


def _pid_file(report_id):
    return os.path.join(_log_dir(), 'locust_%s.pid' % report_id)


def _pid_alive(pid):
    """判断 PID 是否仍然存在（只探测存在性，不发信号）。"""
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # 进程存在但不属于当前用户（本项目同容器同用户，基本不会走到）
        return True
    except Exception:
        # 判不准时保守认为「还活着」，交给超时规则兜底，避免误杀正在跑的压测
        return True
    return True


def _duration_seconds(text, default=300):
    """解析压测时长（秒）。

    该字段的取值有两种形态：
      * 压测刚创建时是前端原始入参，如 '5' / '600'；
      * 压测写回后是 locust 的结果，如 '20 seconds'。
    统一取开头的整数即可，取不到则用默认值。
    """
    m = re.match(r'\s*(\d+)', str(text or ''))
    return int(m.group(1)) if m else default


def scan_and_close(grace_seconds=300, hard_limit_seconds=1800, now=None):
    """扫描并收口僵尸报告，返回 [(report_id, reason), ...]。"""
    now = now or timezone.now()
    closed = []

    doing = LocustReport.objects.filter(test_process=LocustReport.TestProcess.Doing)
    for r in doing:
        reason = None
        pid_path = _pid_file(r.id)
        pid = 0
        if os.path.exists(pid_path):
            try:
                pid = int((open(pid_path).read() or '').strip() or 0)
            except Exception:
                pid = 0

        dur = _duration_seconds(r.duration)
        start = r.start_time
        deadline = start + timedelta(seconds=dur + grace_seconds)
        hard_deadline = start + timedelta(seconds=dur + grace_seconds + hard_limit_seconds)

        if os.path.exists(pid_path) and not _pid_alive(pid):
            reason = ('压测进程已退出但报告未收口（PID %s 已不存在）。'
                      '通常是子进程被 OOM/被 kill，或写回报告时失败。' % pid)
        elif now >= hard_deadline:
            reason = ('压测进程长时间未收口（开始于 %s，预期时长 %s 秒，'
                      '已超过宽限期 %s 秒 + 硬上限 %s 秒）。'
                      % (timezone.localtime(start).strftime('%Y-%m-%d %H:%M:%S'),
                         dur, grace_seconds, hard_limit_seconds))
        elif not os.path.exists(pid_path) and now >= deadline:
            # 兼容早于本特性创建的历史报告：没有 PID 文件，只能用时间判据
            reason = ('压测超时未收口（开始于 %s，预期时长 %s 秒，已超过宽限期 %s 秒）。'
                      % (timezone.localtime(start).strftime('%Y-%m-%d %H:%M:%S'),
                         dur, grace_seconds))

        if reason is None:
            continue

        exceptions = list(r.exceptions_statistics or [])
        exceptions.append({
            'count': 1,
            'msg': '压测异常中断（守护进程自动判定）：' + reason,
            'traceback': '',
        })
        LocustReport.objects.filter(id=r.id).update(
            test_process=LocustReport.TestProcess.Failed,
            end_time=now,
            exceptions_statistics=exceptions,
        )
        closed.append((r.id, reason))

        try:
            os.remove(pid_path)
        except Exception:
            pass

    return closed


class Command(BaseCommand):
    help = '压测报告守护进程：周期性收口「压测中」但实际已中断的僵尸报告'

    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, default=30,
                            help='常驻模式下的扫描间隔（秒），默认 30')
        parser.add_argument('--grace', type=int, default=300,
                            help='压测时长之外额外给予的宽限期（秒），默认 300')
        parser.add_argument('--hard-limit', type=int, default=1800,
                            help='进程仍存活时的额外硬上限（秒），默认 1800')
        parser.add_argument('--once', action='store_true',
                            help='只扫描一次后退出（自测/人工巡检用）')

    def handle(self, *args, **options):
        interval = options['interval']
        grace = options['grace']
        hard_limit = options['hard_limit']

        if options['once']:
            closed = scan_and_close(grace, hard_limit)
            if closed:
                for rid, reason in closed:
                    self.stdout.write('已收口报告 %s：%s' % (rid, reason))
            self.stdout.write('本次共收口 %d 条僵尸报告' % len(closed))
            return

        self.stdout.write('[locust-watchdog] 启动：间隔 %ss / 宽限期 %ss / 硬上限 %ss'
                          % (interval, grace, hard_limit))
        self.stdout.flush()
        while True:
            try:
                closed = scan_and_close(grace, hard_limit)
                for rid, reason in closed:
                    self.stdout.write('[locust-watchdog] 已收口报告 %s（%s）'
                                      % (rid, timezone.localtime(timezone.now()).strftime('%H:%M:%S')), )
                    self.stdout.write('    原因：%s' % reason)
                if closed:
                    self.stdout.flush()
            except Exception:
                traceback.print_exc()
            time.sleep(interval)
