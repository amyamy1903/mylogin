import os
import configparser

# 获取文件的当前路径（绝对路径）
cur_path = os.path.dirname(os.path.realpath(__file__))

# 获取config.ini的路径
config_path = os.path.join(cur_path, 'conf.ini')

conf = configparser.ConfigParser()
conf.read(config_path)

DATABASE = conf.get('mysql', 'database')
DATABASE2 = conf.get('mysql', 'database2')
HOST = conf.get('mysql', 'host')
PORT = conf.getint('mysql', 'port')
USER = conf.get('mysql', 'user')
PASSWORD = conf.get('mysql', 'password')
CHARSET = conf.get('mysql', 'charset')

YAPI_USERNAME = conf.get('mysql', 'yapi_username')
YAPI_PASSWORD = conf.get('mysql', 'yapi_password')