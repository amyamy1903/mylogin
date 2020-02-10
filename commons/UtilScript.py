# -*- coding:utf-8 -*-
import pymysql
import json
from conf import read_config
# ----------------------------
# 错误码
# 正常返回 code : 200
# 数据连接失败 code : 400
# 请求参数有误 code : 401
# ----------------------------


class ConnMySql:
    """连接MySQL db"""
    def __init__(self, database, sql):
        self.database = database
        self.sql = sql

    def connect_db(self):
        try:
            conn = pymysql.connect(host=read_config.HOST,
                               port=read_config.PORT,
                               user=read_config.USER,
                               passwd=read_config.PASSWORD,
                               db=self.database,
                               charset=read_config.CHARSET)
        except Exception as e:
            print(e)
            conn = 400
        return conn
    """请求MySQL获取数据"""
    def get_data(self):
        conn = self.connect_db()
        if conn == 400:
            return conn
        else:
            try:
                cur = conn.cursor()
                cur.execute(self.sql)
                data = cur.fetchall()
                cur.close()
                conn.commit()
                conn.close()
                return data
            except Exception as e:
                print(e)
            return 401

    """执行文件中的多条数据"""
    def execute_many_sql(self, data):
        conn = self.connect_db()
        if conn == 400:
            return conn
        else:
            try:
                cur = conn.cursor()
                cur.executemany(self.sql, data)
                data = cur.fetchall()
                cur.close()
                conn.commit()
                conn.close()
                return data
            except Exception as e:
                print(e)
            return 401


class ExecuteData:
    @staticmethod
    def is_json(data):
        try:
            json.loads(data)
        except ValueError:
            return False
        return True

