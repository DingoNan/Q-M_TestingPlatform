# -*- coding: utf-8 -*-
"""环境连通性自检（P2-1，2026-10-15 甘肃 242 实测后新增）。

★ 为什么要有这个模块：
  配置环境（服务域名 / 数据库）时平台**完全不探活**，配置错了要等到「跑用例」
  才暴露，而那时的报错往往是执行引擎内部的异常，与「连不上」没有字面关联，
  排查成本极高（本次 242 上就是靠人工 SSH + curl 才能确认端口通不通）。
  这里把探活独立成一个只读模块：只连接、只跑一句探针语句，不写任何业务数据，
  与执行链路（core/step/run_sql.py）解耦，避免影响线上执行行为。

★ 设计约束：
  1) 任何异常都要被吞掉并转成「可读结论」，绝不让接口 500；
  2) 返回体里**绝不能出现口令**（password 只会来自配置，错误信息一律清洗后再返回）；
  3) 每次探活都带超时，且对外统一返回耗时，便于判断「慢」还是「不通」。
"""
import re
import time

# 口令等敏感串的清洗规则：把 password/pwd/口令 相关片段整体抹掉，
# 避免驱动把连接串原样打进异常信息时被带出去。
_SENSITIVE = re.compile(
    r'(password|passwd|pwd|token|secret)\s*[=:]\s*[^\s,\'")]+', re.IGNORECASE)


def _clean(text):
    """异常信息脱敏 + 截短，保证返回体可以直接展示给用户。"""
    if text is None:
        return ''
    text = _SENSITIVE.sub(lambda m: '%s=<已隐藏>' % m.group(1), str(text))
    return text[:300]


def _cost_ms(started):
    return int((time.time() - started) * 1000)


def probe_service(url, timeout=8):
    """HTTP 探活：只要能拿到 HTTP 响应就认为「通」。

    ★ 401/403/404/500 都算通 —— 它们证明服务进程活着、网络可达；
      只有连接失败 / 超时 / DNS 失败才算不通。这条判定很关键，
      否则登录态接口永远会被误判成「服务挂了」。
    """
    started = time.time()
    if not url:
        return {'ok': False, 'cost_ms': 0, 'error': '未配置服务地址'}
    try:
        import requests
        resp = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
        return {
            'ok': True,
            'cost_ms': _cost_ms(started),
            'status_code': resp.status_code,
            'error': '',
        }
    except Exception as exc:
        return {
            'ok': False,
            'cost_ms': _cost_ms(started),
            'status_code': None,
            'error': _clean(exc),
        }


def probe_env_db(env_db, timeout=5):
    """数据库探活：按类型建一次连接并执行一句探针语句。

    返回 dict(ok, cost_ms, error, driver)；不抛异常。
    """
    started = time.time()
    host = getattr(env_db, 'host', '')
    port = getattr(env_db, 'port', None)
    name = getattr(env_db, 'name', '')
    user = getattr(env_db, 'username', '')
    pwd = getattr(env_db, 'password', '')
    db_type = getattr(env_db, 'type', None)

    # 延迟导入：与 run_sql.py 保持一致的字母表，避免循环依赖
    from apps.envs.models import EnvDb

    try:
        if db_type == EnvDb.SQLType.MYSQL:
            import pymysql
            conn = pymysql.connect(host=host, port=int(port), user=user, password=pwd,
                                   database=name, connect_timeout=timeout)
            cur = conn.cursor()
            cur.execute('select 1')
            cur.fetchone()
            conn.close()
        elif db_type == EnvDb.SQLType.POSTGRESQL:
            import psycopg2
            conn = psycopg2.connect(host=host, port=int(port), user=user, password=pwd,
                                    database=name, connect_timeout=timeout)
            cur = conn.cursor()
            cur.execute('select 1')
            cur.fetchone()
            conn.close()
        elif db_type == EnvDb.SQLType.REDIS:
            import redis
            client = redis.Redis(host=host, port=int(port), password=pwd or None,
                                 db=int(name or 0), decode_responses=True,
                                 socket_connect_timeout=timeout, socket_timeout=timeout)
            client.ping()
        elif db_type == EnvDb.SQLType.ORACLE:
            import oracledb
            service_name = name or ''
            if '/' in service_name:
                service_name = service_name.split('/', 1)[1]
            try:
                conn = oracledb.connect(user=user, password=pwd, host=host,
                                        port=int(port), service_name=service_name,
                                        tcp_connect_timeout=timeout)
            except TypeError:
                # 老版本驱动不认 tcp_connect_timeout，降级不带超时重试
                conn = oracledb.connect(user=user, password=pwd, host=host,
                                        port=int(port), service_name=service_name)
            cur = conn.cursor()
            cur.execute('select 1 from dual')
            cur.fetchone()
            conn.close()
        elif db_type == EnvDb.SQLType.DM8:
            import dmPython
            conn = dmPython.connect(user=user, password=pwd, server=host, port=int(port))
            cur = conn.cursor()
            cur.execute('select 1 from dual')
            cur.fetchone()
            conn.close()
        else:
            return {'ok': False, 'cost_ms': 0, 'error': '暂不支持的数据库类型：%s' % db_type}
    except Exception as exc:
        return {'ok': False, 'cost_ms': _cost_ms(started), 'error': _clean(exc)}
    return {'ok': True, 'cost_ms': _cost_ms(started), 'error': ''}
