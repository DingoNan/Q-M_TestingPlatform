# -*- coding: utf-8 -*-
"""对接外部 JMeter 执行压测（P1 性能压测增强，2026-10-15 甘肃 242 实测后新增）。

★ 为什么要有这个模块：
  平台自带的性能压测是 locust 的薄封装，只能「固定并发跑一段时间」。甘肃 242 这类
  信创项目现场**已经有成熟的 JMeter 脚本与 JMeter Server（:1099）**，让测试同学把脚本
  重写成平台用例不现实。这里提供一条「平台只做编排与结果归集，真正施压交给 JMeter」
  的路径：触发 JMeter → 等它跑完 → 解析 JTL → 写回平台报告。

★ 设计约束（与 locust 链路保持一致）：
  1) 只在**独立子进程**里执行，绝不在 web 进程内跑（JMeter 是重量级外部进程）；
  2) 任何异常都要转成可读结论写进报告的 fail_reason，绝不让「报告永久压测中」；
  3) JTL 解析只做**只读汇总**，不写任何业务数据；
  4) 命令行参数一律用列表传参（不用 shell=True），避免注入。
"""
import csv
import os
import subprocess
import time

# JMeter 默认 JTL(CSV) 列。不同版本列序可能不同，故按表头动态定位，不硬编码下标。
_JTL_REQUIRED = ('elapsed', 'label', 'success', 'responseCode')


def _percentile(sorted_values, pct):
    """取分位数（线性插值），sorted_values 必须已升序。"""
    if not sorted_values:
        return 0
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * pct
    low = int(pos)
    high = min(low + 1, len(sorted_values) - 1)
    frac = pos - low
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * frac


def summarize_jtl(jtl_path, bucket_seconds=5):
    """解析 JMeter 的 JTL(CSV)，按 label（接口/采样器名）汇总。

    返回 dict：
      {
        'total': {'count','avg','min','max','p95','fail','fail_rate','bytes'},
        'labels': [ {'label','count','avg','min','max','p95','fail','fail_rate'}, ... ],
        'history': {  # 用于前端折线图：按 bucket_seconds 聚合
            'x_time': [], 'y_rps': [], 'y_f_rps': [], 'user_count': [],
            'avg_res_time': [], 'half_res_time': [], 'nine_five_res_time': []
        },
        'duration': 秒
      }
    只读、不抛异常：任何解析问题都转成 ValueError 由调用方收口。
    """
    if not jtl_path or not os.path.exists(jtl_path):
        raise ValueError('JTL 文件不存在：%s' % jtl_path)

    rows = []
    with open(jtl_path, 'r', encoding='utf-8', errors='replace', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        missing = [c for c in _JTL_REQUIRED if c not in fieldnames]
        if missing:
            raise ValueError('JTL 缺少必需列：%s（实际列：%s）' % (missing, fieldnames[:20]))
        has_ts = 'timeStamp' in fieldnames
        has_threads = 'allThreads' in fieldnames
        for r in reader:
            try:
                elapsed = float(r.get('elapsed') or 0)
            except (TypeError, ValueError):
                continue
            success = str(r.get('success', '')).strip().lower() in ('true', '1', 'yes')
            label = (r.get('label') or '').strip() or '(unknown)'
            ts_ms = 0.0
            if has_ts:
                try:
                    ts_ms = float(r.get('timeStamp') or 0)
                except (TypeError, ValueError):
                    ts_ms = 0.0
            threads = 0
            if has_threads:
                try:
                    threads = int(float(r.get('allThreads') or 0))
                except (TypeError, ValueError):
                    threads = 0
            try:
                nbytes = int(float(r.get('bytes') or 0))
            except (TypeError, ValueError):
                nbytes = 0
            rows.append({
                'ts': ts_ms / 1000.0, 'elapsed': elapsed, 'label': label,
                'ok': success, 'bytes': nbytes, 'threads': threads,
                'code': (r.get('responseCode') or '').strip(),
            })

    if not rows:
        raise ValueError('JTL 中没有解析到任何样本（文件为空或格式不符）')

    def _agg(items):
        vals = sorted(x['elapsed'] for x in items)
        fails = len([x for x in items if not x['ok']])
        total_bytes = sum(x['bytes'] for x in items)
        return {
            'count': len(items),
            'avg': round(sum(vals) / len(vals), 2) if vals else 0,
            'min': round(vals[0], 2) if vals else 0,
            'max': round(vals[-1], 2) if vals else 0,
            'p95': round(_percentile(vals, 0.95), 2),
            'fail': fails,
            'fail_rate': round(fails * 100.0 / len(items), 2) if items else 0,
            'bytes': total_bytes,
        }

    labels = {}
    for x in rows:
        labels.setdefault(x['label'], []).append(x)

    # 时间桶聚合（前端 history 折线图）
    history = {'x_time': [], 'y_rps': [], 'y_f_rps': [], 'user_count': [],
               'avg_res_time': [], 'half_res_time': [], 'nine_five_res_time': []}
    ts_vals = [x['ts'] for x in rows if x['ts'] > 0]
    if ts_vals:
        t0, t1 = min(ts_vals), max(ts_vals)
        span = max(t1 - t0, 1.0)
        buckets = max(int(span / bucket_seconds) + 1, 1)
        acc = [[] for _ in range(buckets)]
        for x in rows:
            if x['ts'] <= 0:
                continue
            idx = min(int((x['ts'] - t0) / bucket_seconds), buckets - 1)
            acc[idx].append(x)
        for i, items in enumerate(acc):
            if not items:
                continue
            vals = sorted(x['elapsed'] for x in items)
            ok_n = len([x for x in items if x['ok']])
            fail_n = len(items) - ok_n
            history['x_time'].append(time.strftime('%H:%M:%S', time.localtime(t0 + i * bucket_seconds)))
            history['y_rps'].append(round(len(items) / float(bucket_seconds), 2))
            history['y_f_rps'].append(round(fail_n / float(bucket_seconds), 2))
            history['user_count'].append(max([x['threads'] for x in items] or [0]))
            history['avg_res_time'].append(round(sum(vals) / len(vals), 2))
            history['half_res_time'].append(round(_percentile(vals, 0.5), 2))
            history['nine_five_res_time'].append(round(_percentile(vals, 0.95), 2))
        duration = int(span)
    else:
        duration = 0

    total = _agg(rows)
    return {
        'total': total,
        'labels': [dict(label=k, **_agg(v)) for k, v in sorted(labels.items())],
        'history': history,
        'duration': duration,
    }


def build_jmeter_command(jmeter_bin, jmx_path, jtl_path, remote_hosts=None,
                         properties=None, distributed_stop=True):
    """构造 JMeter 命令行（列表形式，不用 shell=True）。"""
    cmd = [jmeter_bin, '-n', '-t', jmx_path, '-l', jtl_path]
    if remote_hosts:
        cmd += ['-R', ','.join(remote_hosts)]
        # 分布式跑完主动停掉远端引擎，否则远端 jmeter-server 会一直挂着占用资源
        if distributed_stop:
            cmd += ['-X']
    for k, v in (properties or {}).items():
        cmd += ['-J%s=%s' % (k, v)]
    return cmd


def resolve_jmeter_bin(jmeter_home=None):
    """定位 jmeter 可执行文件：优先 JMETER_HOME/bin/jmeter，其次 PATH 里的 jmeter。"""
    if jmeter_home:
        for name in ('jmeter', 'jmeter.bat', 'jmeter.sh'):
            p = os.path.join(jmeter_home, 'bin', name)
            if os.path.exists(p):
                return p
        # 也兼容直接把目录指到 bin 上的写法
        for name in ('jmeter', 'jmeter.bat', 'jmeter.sh'):
            p = os.path.join(jmeter_home, name)
            if os.path.exists(p):
                return p
    return 'jmeter'


def run_jmeter(jmeter_home, jmx_path, jtl_path, remote_hosts=None, properties=None,
               timeout=3600):
    """执行 JMeter 并等待结束。返回 dict(ok, returncode, cmd, log, error)。不抛异常。"""
    started = time.time()
    jmeter_bin = resolve_jmeter_bin(jmeter_home)
    jtl_dir = os.path.dirname(jtl_path)
    if jtl_dir:
        try:
            os.makedirs(jtl_dir, exist_ok=True)
        except Exception as e:
            return {'ok': False, 'returncode': None, 'cmd': [], 'log': '',
                    'error': '无法创建 JTL 输出目录 %s：%s' % (jtl_dir, e),
                    'cost_ms': int((time.time() - started) * 1000)}
    if not os.path.exists(jmx_path):
        return {'ok': False, 'returncode': None, 'cmd': [], 'log': '',
                'error': 'JMX 脚本不存在：%s' % jmx_path,
                'cost_ms': int((time.time() - started) * 1000)}

    cmd = build_jmeter_command(jmeter_bin, jmx_path, jtl_path, remote_hosts, properties)
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              timeout=timeout)
        log = (proc.stdout or b'').decode('utf-8', 'replace')
        return {
            'ok': proc.returncode == 0,
            'returncode': proc.returncode,
            'cmd': cmd,
            'log': log[-8000:],
            'error': '' if proc.returncode == 0 else 'JMeter 退出码=%s' % proc.returncode,
            'cost_ms': int((time.time() - started) * 1000),
        }
    except subprocess.TimeoutExpired as e:
        return {'ok': False, 'returncode': None, 'cmd': cmd,
                'log': ((e.stdout or b'').decode('utf-8', 'replace'))[-8000:],
                'error': 'JMeter 执行超时（>%ss）' % timeout,
                'cost_ms': int((time.time() - started) * 1000)}
    except FileNotFoundError:
        return {'ok': False, 'returncode': None, 'cmd': cmd, 'log': '',
                'error': '找不到 JMeter 可执行文件：%s（请检查 jmeter_home 配置）' % jmeter_bin,
                'cost_ms': int((time.time() - started) * 1000)}
    except Exception as e:
        return {'ok': False, 'returncode': None, 'cmd': cmd, 'log': '',
                'error': 'JMeter 执行异常：%s: %s' % (type(e).__name__, e),
                'cost_ms': int((time.time() - started) * 1000)}
