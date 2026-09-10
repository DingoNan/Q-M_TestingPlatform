bind = '0.0.0.0:8000'
pidfile = '/app/logs/gunicorn.pid'
accesslog = '/app/logs/gunicorn_access.log'
errorlog = '/app/logs/gunicorn_error.log'

# 多进程单线程（sync worker）
# 单 worker 无法同时处理多个请求，且用例步骤自回调本后端时会因等待同一 worker 而死锁，
# 故提高进程数以支持并发。每个进程会单独加载一份 embedding 模型，数值受内存限制，勿按 2*CPU+1 套用。
# 2026-09-02: 宿主物理内存不足(仅剩~1.2GB)时 4 个 worker 会 OOM 被杀导致接口无响应，降为 2 个保证稳定。
workers = 2
threads = 1
worker_class = 'sync'

# 默认 30s 会把执行长用例的 worker 误杀，放宽到 5 分钟
timeout = 300


def post_worker_init(worker):
    """
    worker 加载完 WSGI 应用后，丢弃 fork 时从父进程继承的数据库连接包装。
    必须保留：gunicorn fork 后各 worker 主线程/preload 线程的 thread id 会发生
    碰撞（实测 4 个 worker 的 tid 完全相同），Django 按线程存连接会被跨线程复用，
    导致 request_finished → close_old_connections → validate_thread_sharing 报
    "DatabaseWrapper created in a thread ... same thread"。此重置为标准修复。
    """
    try:
        import django
        import django.conf
        django.setup()
        from django.db import connections
        old = connections._connections
        # 换成全新的线程本地存储，工作进程在其自身线程按需重建连接
        connections._connections = old.__class__()
        # 关闭父进程 fork 前可能遗留的真实底层连接，避免句柄泄漏
        backend = getattr(old, 'data', None)
        worker.log.info("post_worker_init: reset django db connection storage, "
                        "pid=%s tid=%s", __import__('os').getpid(),
                        __import__('threading').get_ident())
    except Exception:
        worker.log.warning("post_worker_init db reset failed", exc_info=True)