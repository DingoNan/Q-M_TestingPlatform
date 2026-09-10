#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

ENV = os.environ.get('RUN_ENV', 'dev')

ENVIRONMENT = {
    'dev': 'black_bag.settings_dev',
    'pro': 'black_bag.settings_pro',
    'docker': 'black_bag.settings_docker',
}


def main():
    """Run administrative tasks."""
    # 先配置 Django 设置
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", ENVIRONMENT.get(ENV))
    
    # 在 Django 设置配置之后再进行 gevent monkey patch
    import gevent.monkey
    gevent.monkey.patch_all()
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
