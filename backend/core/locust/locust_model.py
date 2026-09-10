import locust
import time
import json
import os
import requests
import gevent
from html import escape
from itertools import chain
from locust import stats as stats_module
from locust.exception import LocustError
from locust.runners import STATE_STOPPED, STATE_STOPPING, MasterRunner, STATE_RUNNING, STATE_SPAWNING
from locust.stats import sort_stats, update_stats_history
from locust.user.inspectuser import get_ratio
from locust.util.date import format_duration, format_utc_timestamp
from datetime import datetime
from locust import HttpUser, task, between, events
from locust.runners import LocalRunner
from locust.clients import HttpSession
from locust.env import Environment
from locust.web import WebUI, get_html_report
from locust.log import setup_logging
from locust.stats import stats_history, stats_printer
from requests.adapters import HTTPAdapter
from core.locust.run_locust_case import run_locust_case

setup_logging("INFO")

PERCENTILES_FOR_HTML_REPORT = [0.50, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]


class LocustHttpClientMng:
    def __init__(self, user_id):
        self.user_id = user_id
        self.session_manager = {}
        self.common_headers = {}

    def add_session_manager(self, host, session_client):
        self.session_manager[host] = session_client

    def add_common_headers(self, host, headers):
        if host not in self.common_headers:
            self.common_headers[host] = headers

    def close_all(self):
        [session.close() for session in self.session_manager.values()]


steps = {}

env_params = {}

locust_client_mng = None


def set_locust_env_params(env, case_id, env_id, user_id, server_host):
    env.case_id = case_id
    env.env_id = env_id
    env.user_id = user_id
    env.server_host = server_host
    request_data = {'case_id': case_id, 'env_id': env_id, 'server_host': server_host, 'user_id': user_id}
    init_data = requests.post(url=server_host + '/test/init_data/', json=request_data).json()['result']
    env.steps = init_data['steps']
    env.env_params = init_data['env_params']
    env.global_params = init_data['global_params']
    env.host_list = init_data['host_list']

# @events.test_start.add_listener
# def on_test_start(environment, **kwargs):
#     """在整个测试开始时执行，只执行一次"""
#     if environment.mode != 'Work':


def __record_data_to_db(environment, is_done=False):
    mode = environment.mode
    case_id = environment.case_id
    env_id = environment.env_id
    user_id = environment.user_id
    cpu_info = environment.runner.current_cpu_usage
    memory_info = round(environment.runner.current_memory_usage / (1024 * 1024), 2)
    max_user = environment.max_user if hasattr(environment, 'max_user') else environment.runner.target_user_count
    if hasattr(environment, 'rate'):
        rate = environment.rate
    elif hasattr(environment.runner, 'spawn_rate'):
        rate = environment.runner.spawn_rate
    else:
        rate = max_user

    if mode != 'Work':
        stats = environment.runner.stats

        start_time = format_utc_timestamp(stats.start_time)

        if end_ts := stats.last_request_timestamp:
            end_time = format_utc_timestamp(end_ts)
        else:
            end_ts = stats.start_time
            end_time = start_time

        host = None
        if environment.host:
            host = environment.host
        elif environment.runner.user_classes:
            all_hosts = {l.host for l in environment.runner.user_classes}
            if len(all_hosts) == 1:
                host = list(all_hosts)[0]

        requests_statistics = list(chain(sort_stats(stats.entries), [stats.total]))
        failures_statistics = sort_stats(stats.errors)
        exceptions_statistics = [
            {**exc, "nodes": ", ".join(exc["nodes"])} for exc in environment.runner.exceptions.values()
        ]

        if stats.history and stats.history[-1]["time"] < end_time:
            update_stats_history(environment.runner, end_time)
        history = stats.history
        is_distributed = isinstance(environment.runner, MasterRunner)
        user_spawned = (
            environment.runner.reported_user_classes_count if is_distributed else environment.runner.user_classes_count
        )

        if environment.runner.state in [STATE_STOPPED, STATE_STOPPING]:
            user_spawned = environment.runner.final_user_classes_count

        task_data = {
            "per_class": get_ratio(environment.user_classes, user_spawned, False),
            "total": get_ratio(environment.user_classes, user_spawned, True),
        }
        report_data = {
            "requests_statistics": [stat.to_dict(escape_string_values=True) for stat in requests_statistics],
            "failures_statistics": [stat.to_dict() for stat in failures_statistics],
            "exceptions_statistics": [stat for stat in exceptions_statistics],
            "response_time_statistics": [
                {
                    "name": escape(stat.name),
                    "method": escape(stat.method or ""),
                    **{
                        str(percentile): stat.get_response_time_percentile(percentile)
                        for percentile in PERCENTILES_FOR_HTML_REPORT
                    },
                }
                for stat in requests_statistics
            ],
            "start_time": start_time,
            "end_time": end_time,
            "duration": format_duration(stats.start_time, end_ts),
            "host": escape(str(host)),
            "history": _deal_history_data(history),
            "tasks": task_data,
            'case': case_id,
            'user': user_id,
            'env': env_id,
            'max_user': max_user,
            'cpu': cpu_info,
            'memory': memory_info,
            'rate': rate,
            "percentiles_to_chart": stats_module.PERCENTILES_TO_CHART
        }
        server_host = environment.server_host
        if is_done:
            report_data['test_process'] = 1
        requests.put(url=server_host + f'/report/locust/{environment.report_id}/', json=report_data)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    __record_data_to_db(environment, is_done=True)


def _deal_history_data(history):
    new_history = {'x_time': [], 'y_rps': [], 'y_f_rps': [], 'user_count': [], 'avg_res_time': [],
                   'half_res_time': [], 'nine_five_res_time': []}

    for obj in history:
        new_history['x_time'].append(obj['time'])
        new_history['y_rps'].append(obj['current_rps'])
        new_history['y_f_rps'].append(obj['current_fail_per_sec'])
        new_history['user_count'].append(obj['user_count'])
        new_history['avg_res_time'].append(obj['total_avg_response_time'])
        new_history['half_res_time'].append(obj['response_time_percentile_0.5'])
        new_history['nine_five_res_time'].append(obj['response_time_percentile_0.95'])
    return new_history


class MyHttpUser(HttpUser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.host is None:
            raise LocustError(
                "You must specify the base host. Either in the host attribute in the User class, or on the command line using the --host option."
            )

        self.client = HttpSession(
            base_url=self.host,
            request_event=self.environment.events.request,
            user=self,
            pool_manager=self.pool_manager,
        )
        """
        Instance of HttpSession that is created upon instantiation of Locust.
        The client supports cookies, and therefore keeps the session between HTTP requests.
        """
        self.client.trust_env = False


class UserModel(HttpUser):
    # 设置等待时间（1-3秒之间随机）
    wait_time = between(0, 0)

    def on_start(self) -> None:
        self.locust_client_mng = LocustHttpClientMng(user_id=self.environment.user_id)
        for host in self.environment.host_list:
            session_client = HttpSession(base_url=host, request_event=self.environment.events.request,
                                         user=self, pool_manager=self.pool_manager)
            self.locust_client_mng.add_session_manager(host, session_client)


    @task
    def run_locust(self):
        run_locust_case(self, self.environment.steps, self.locust_client_mng, self.environment.global_params,
                        self.environment.env_params)


def start_standalone_locust_web_ui_programmatically(mode, case_id, env_id, user_id, server_host, web_port, report_id):
    # 1. 创建 Environment 和 Runner
    env = Environment(user_classes=[UserModel], events=events)
    set_locust_env_params(env, case_id, env_id, user_id, server_host)
    env.case_id = case_id
    env.mode = mode
    env.env_id = env_id
    env.user_id = user_id
    env.report_id = report_id
    env.server_host = server_host
    env.stats.reset_all()

    gevent.spawn(stats_printer(env.stats))
    # start a greenlet that save current stats to history
    runner = env.create_local_runner()
    gevent.spawn(stats_history, runner)
    gevent.spawn(record_data_to_db(env))
    # 2. 启动 Web UI
    web_ui = env.create_web_ui("127.0.0.1", web_port)

    # 3. 触发初始化事件（如果你注册了事件钩子）
    env.events.init.fire(environment=env, runner=runner, web_ui=web_ui)

    print(f"🌐 Locust Web UI 已启动: http://127.0.0.1:{web_port}")
    print(f"📋 测试用例ID: {case_id}")
    print(f"🌍 环境ID: {env_id}")
    print(f"👤 用户ID: {user_id}")
    print(f"🚀 目标服务器: {server_host}")
    print("-" * 50)

    web_ui.greenlet.join()
    return web_ui


def record_data_to_db(environment):
    def record_data_to_db_func() -> None:
        runner = environment.runner
        while True:
            __record_data_to_db(environment)
            gevent.sleep(1)
            if runner.state != STATE_RUNNING and runner.state != STATE_SPAWNING:
                break

    return record_data_to_db_func


def start_standalone_locust_headless_programmatically(mode, case_id, env_id, user_id, server_host, run_times, rate,
                                                      user_num, test_host, report_id):
    # 1. 创建 Environment 和 Runner
    env = Environment(user_classes=[UserModel], events=events)
    set_locust_env_params(env, case_id, env_id, user_id, server_host)
    env.host = test_host
    env.mode = mode
    env.case_id = case_id
    env.env_id = env_id
    env.user_id = user_id
    env.report_id = report_id
    env.server_host = server_host
    env.max_user = user_num
    env.rate = rate
    runner = env.create_local_runner()
    env.stats.reset_all()
    runner.start(user_num, spawn_rate=rate)
    gevent.spawn(stats_history, runner)
    # 3. 触发初始化事件（如果你注册了事件钩子）
    env.events.init.fire(environment=env, runner=runner)
    # start a greenlet that periodically outputs the current stats
    gevent.spawn(stats_printer(env.stats))
    gevent.spawn(record_data_to_db(env))
    # in 30 seconds stop the runner
    gevent.spawn_later(run_times, runner.quit)

    # wait for the greenlets
    runner.greenlet.join()
    # generate_html_report(env)


def start_system_standalone_locust_headless_programmatically(steps, global_params, env_params, host_list,  case_id,
                                                             env_id, user_id, run_times, rate, user_num, test_host,
                                                             report_id):
    server_host = 'http://127.0.0.1:8000'

    # 1. 创建 Environment 和 Runner
    env = Environment(user_classes=[UserModel], events=events)
    env.system_run = True
    env.case_id = case_id
    env.env_id = env_id
    env.user_id = user_id
    env.server_host = server_host
    env.report_id = report_id

    env.steps = steps
    env.env_params = env_params
    env.global_params = global_params
    env.host_list = host_list
    env.host = test_host
    env.mode = 'Standalone'
    env.case_id = case_id
    env.env_id = env_id
    env.user_id = user_id
    env.max_user = user_num
    env.rate = rate
    runner = env.create_local_runner()
    env.stats.reset_all()

    runner.start(user_num, spawn_rate=rate)
    gevent.spawn(stats_history, runner)
    # 3. 触发初始化事件（如果你注册了事件钩子）
    env.events.init.fire(environment=env, runner=runner)
    # in 30 seconds stop the runner
    # start a greenlet that periodically outputs the current stats
    gevent.spawn(record_data_to_db(env))
    gevent.spawn_later(run_times, runner.quit)

    # wait for the greenlets
    runner.greenlet.join()


def generate_html_report(env):
    # 获取当前时间
    now = datetime.now()
    # 格式化为适合文件名的字符串（避免使用Windows/Linux文件系统保留字符）
    time_str = now.strftime("%Y%m%d_%H%M%S")
    report_path = f"locust_report_{time_str}.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(get_html_report(env, show_download_link=False))

    print(f"📊 测试报告已生成: {report_path}")


def start_master_locust_web_ui_programmatically(mode, case_id, env_id, user_id, server_host, web_port):
    # 1. 创建 Environment 和 Runner
    env = Environment(user_classes=[UserModel], events=events)
    set_locust_env_params(env, case_id, env_id, user_id, server_host)
    env.case_id = case_id
    env.mode = mode
    env.env_id = env_id
    env.user_id = user_id
    env.server_host = server_host
    env.stats.reset_all()
    gevent.spawn(stats_printer(env.stats))
    runner = env.create_master_runner()

    gevent.spawn(stats_history, runner)
    # 2. 启动 Web UI
    web_ui = env.create_web_ui("127.0.0.1", web_port)
    # 3. 触发初始化事件（如果你注册了事件钩子）
    env.events.init.fire(environment=env, runner=runner, web_ui=web_ui)

    print(f"🌐 Locust Web UI 已启动: http://127.0.0.1:{web_port}")
    print(f"📋 测试用例ID: {case_id}")
    print(f"🌍 环境ID: {env_id}")
    print(f"👤 用户ID: {user_id}")
    print(f"🚀 目标服务器: {server_host}")
    print("-" * 50)

    web_ui.greenlet.join()
    return web_ui


def start_master_locust_headless_programmatically(mode, case_id, env_id, user_id, server_host, run_times, rate,
                                                  user_num, test_host, work_count, report_id):
    # 1. 创建 Environment 和 Runner
    env = Environment(user_classes=[UserModel], events=events)
    set_locust_env_params(env, case_id, env_id, user_id, server_host)
    env.host = test_host
    env.mode = mode
    env.case_id = case_id
    env.env_id = env_id
    env.user_id = user_id
    env.server_host = server_host
    env.max_user = user_num
    env.rate = rate
    env.report_id = report_id
    runner = env.create_master_runner()

    # 3. 触发初始化事件（如果你注册了事件钩子）
    env.events.init.fire(environment=env, runner=runner)
    # start a greenlet that periodically outputs the current stats
    gevent.spawn(stats_printer(env.stats))
    # start a greenlet that save current stats to history
    gevent.spawn(stats_history, runner)
    # start the test

    while len(runner.clients.ready) < work_count:
        print(f"🌐 已连接{len(runner.clients.ready)}个work节点, 等待{work_count}个work节点连接后开始执行压测")
        time.sleep(1)
    print(f"🌐 已连接{len(runner.clients.ready)}个work节点,开始执行压测")
    gevent.spawn(record_data_to_db(env))
    runner.start(user_num, spawn_rate=rate)
    # in 30 seconds stop the runner
    gevent.spawn_later(run_times, runner.quit)

    # wait for the greenlets
    runner.greenlet.join()
    # generate_html_report(env)
    runner.server.close(linger=0)


def start_work_locust_programmatically(mode, case_id, env_id, user_id, server_host, master_ip):
    # 1. 创建 Environment 和 Runner
    env = Environment(user_classes=[UserModel], events=events)
    set_locust_env_params(env, case_id, env_id, user_id, server_host)
    env.case_id = case_id
    env.mode = mode
    env.env_id = env_id
    env.user_id = user_id
    env.server_host = server_host
    runner = env.create_worker_runner(master_host=master_ip, master_port=5557)

    # 3. 触发初始化事件（如果你注册了事件钩子）
    env.events.init.fire(environment=env, runner=runner)
    gevent.spawn(stats_printer(env.stats))
    # start a greenlet that save current stats to history
    gevent.spawn(stats_history, runner)
    runner.greenlet.join()
    runner.quit()

