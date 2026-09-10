import simplejson as json
import redis
from functools import partial
import pymysql
import psycopg2

from datetime import datetime, date
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from pymysql.cursors import DictCursor
from apps.envs.models import EnvDb
from core.com.common import replace_params_class_data, replace_all_func_value, formatter_log
from core.com.faker import faker_function_map



def json_default(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)  # 或 str(obj)
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='replace')
    # 可以继续添加其他类型的处理
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


class SQLClient:
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.sql_connect = pymysql.connect(host=host, port=port, database=database, user=user, password=password,
                                           cursorclass=DictCursor)
        self.sql_cursor = self.sql_connect.cursor()

    def run_sql_script(self, sql_script : str):
        self.sql_cursor.execute(sql_script)

    def fetchone(self, sql_script : str):
        self.sql_cursor.execute(sql_script)
        return self.sql_cursor.fetchone()

    def fetchall(self, sql_script: str):
        self.sql_cursor.execute(sql_script)
        return self.sql_cursor.fetchall()

    def close(self):
        self.sql_cursor.close()
        self.sql_connect.close()


class MysqlClient(SQLClient):
    pass


class PgClient(SQLClient):

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.sql_connect = psycopg2.connect(host=host, port=port, user=user, password=password,database=database)
        self.sql_cursor = self.sql_connect.cursor(cursor_factory=RealDictCursor)


class RedisClient(SQLClient):

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.sql_connect = redis.Redis(host=host, port=port, password=password, db=int(database), decode_responses=True)

    def get(self, key):
        return json.loads(self.sql_connect.get(key))

    def delete(self, key):
        return self.sql_connect.delete(key)

    def close(self):
        pass


def run_step_sql(manager_obj, env_id, step, case_params, case_logs_obj, run_times, run_element):
    step_id = step["case_step_id"]
    case_params.stepResponse[f'{step_id}']['runTimes'] = run_times
    case_params.stepResponse[f'{step_id}']['runElement'] = run_element
    database_id : int = step['database_name']
    env_db_obj : EnvDb = EnvDb.objects.all().get(env=env_id, db=database_id, is_delete=False)
    sql_client = None
    if env_db_obj.type == EnvDb.SQLType.MYSQL:
        sql_client = MysqlClient(host=env_db_obj.host, port=env_db_obj.port, database=env_db_obj.name,
                                   user=env_db_obj.username, password=env_db_obj.password)
    elif env_db_obj.type == EnvDb.SQLType.POSTGRESQL:
        sql_client = PgClient(host=env_db_obj.host, port=env_db_obj.port, database=env_db_obj.name,
                              user=env_db_obj.username, password=env_db_obj.password)
    elif env_db_obj.type == EnvDb.SQLType.REDIS:
        sql_client = RedisClient(host=env_db_obj.host, port=env_db_obj.port, database=env_db_obj.name,
                                 user=env_db_obj.username, password=env_db_obj.password)
    step_keyword: str = step['keyword']
    step_id: int = step["case_step_id"]
    sql_script: str = step['script']
    replace_request_data = partial(replace_params_class_data, case_params, case_logs_obj)
    sql_script = replace_request_data(sql_script)
    sql_script = replace_all_func_value(faker_function_map, sql_script)
    sql_result = {}
    if step_keyword == 'SelectFetchone':
        sql_client.run_sql_script(sql_script)
        sql_result = sql_client.fetchone(sql_script)
    elif step_keyword == 'SelectFetchall':
        sql_client.run_sql_script(sql_script)
        sql_result = sql_client.fetchall(sql_script)
    elif step_keyword == 'Update' or step_keyword == 'Delete' or step_keyword == 'Insert':
        sql_client.run_sql_script(sql_script)
        sql_client.sql_connect.commit()
    elif step_keyword == 'RedisGet':
        sql_result = sql_client.get(sql_script)
    elif step_keyword == 'RedisDelete':
        sql_result = sql_client.delete(sql_script)
    else:
        pass

    result = json.dumps(sql_result, default=json_default, indent=4, ensure_ascii=False)
    dict_result = json.loads(result)
    case_params.stepResponse[f'{step_id}']['funcReturn'] = dict_result
    case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', f'{step_keyword}执行成功'),
                                                'value': result})
    sql_client.close()



