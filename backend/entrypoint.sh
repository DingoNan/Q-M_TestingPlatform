#!/bin/sh
set -e

echo "[entrypoint] waiting for MySQL at ${MYSQL_HOST:-mysql}:${MYSQL_PORT:-3306} ..."
python - <<'PY'
import os, socket, time, sys
host = os.environ.get('MYSQL_HOST', 'mysql')
port = int(os.environ.get('MYSQL_PORT', '3306'))
for i in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"[entrypoint] MySQL reachable at {host}:{port}")
            sys.exit(0)
    except Exception:
        if i == 59:
            print("[entrypoint] MySQL not reachable, giving up")
            sys.exit(1)
        time.sleep(2)
PY

echo "[entrypoint] running migrate ..."
python manage.py migrate --noinput

echo "[entrypoint] collecting static files ..."
python manage.py collectstatic --noinput || true

echo "[entrypoint] creating superuser / permissions ..."
echo "from create_super_user import create_super_user; create_super_user();" | python manage.py shell || true

# 关闭以上步骤在此进程线程中打开的数据库连接，
# 避免被 fork 的 gunicorn worker 继承后出现 "DatabaseWrapper objects created
# in a thread can only be used in that same thread" 错误。
echo "[entrypoint] closing database connections ..."
python - <<'PY'
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'black_bag.settings_docker'))
django.setup()
from django.db import connections
connections.close_all()
PY

echo "[entrypoint] starting supervisord ..."
exec supervisord -c supervisord.conf
