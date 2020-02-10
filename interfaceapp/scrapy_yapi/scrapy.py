import requests
import logging
import json
import time
import pandas as pd
from commons.UtilScript import ExecuteData


class Yapi(object):

    def __init__(self, userapi, passwdapi):
        """连接yapi初始化信息

        :param userapi: yapi的登录账号
        :param passwdapi: yapi的登录密码
        :param group_id: yapi中所属产品的id(base:35    团购:176)
        """
        self.logger = logging.getLogger("运行日志:")
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.FileHandler("log.txt")
        self.handler.setLevel(logging.DEBUG)
        self.conhandler = logging.StreamHandler()
        self.conhandler.setLevel(logging.INFO)
        self.formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger.addHandler(self.handler)
        self.logger.addHandler(self.conhandler)
        self.handler.setFormatter(self.formater)
        self.conhandler.setFormatter(self.formater)
        self.userapi = userapi
        self.passwdapi = passwdapi
        self.apiurl = "http://yapi.platform.shuyun.com"  # yapi对应域名
        self.api = requests.session()
        self.pathmodlename = ""  # yapi上接口所属的模块名称
        self.pathname = ""  # 接口名称
        self.path_data_lists = []  # 接口数据(list)   其中列表中的每个值是一个字典
        self.path_key_dicts = {}  # 用于生成Excel中第一行值对应的参数
        self.list_params_path_address = []  # 所有的接口地址列表
        self.list_params_up_time = []  # 所有的接口更新时间列表
        self.list_params_add_time = []  # 所有的接口添加时间列表
        self.list_params_method = []  # 所有的参数方法列表
        self.list_params_modle_name = []  # 所有的接口所属模块名称列表
        self.list_params_request_form_data = []  # 所有的请求参数列表
        self.list_params_expected_response = []  # 所有的请求预期响应
        self.list_params_path_name = []  # 所有的请求接口名称
        self.list_params_path_creat_user = []  # 所有的接口创建者列表
        self.group_name = ""
        self.count = 0
        loginjson = {'email': self.userapi,
                     'password': self.passwdapi}
        loginheader = {'Content-Type': 'application/json;charset=UTF-8'}
        # http://yapi.platform.shuyun.com/api/user/login_by_ldap
        self.logger.info("api后台登录状态:" +
                         str(self.api.post(url=self.apiurl + "/api/user/login_by_ldap", data=json.dumps(loginjson),
                                           verify=False, headers=loginheader).json().get("errmsg")))

    def get_path_data(self, group_id):
        """获取path信息 根据产品id(group_id) 获取对应的模块id"""
        try:
            getid = {'group_id': group_id, 'page': '1', 'limit': '500000'}
            # http://yapi.platform.shuyun.com/api/project/list?group_id=533&page=1&limit=10
            ids = self.api.get(url=self.apiurl + "/api/project/list", verify=False, params=getid).json().get("data").get(
                "list")
            print("ahhahahha ids:", ids)

            for i in range(0, len(ids)):
                self.pathmodlename = ids[i].get("name")
                self.get_pathid_by_mouled_id(ids[i].get("_id"))
        except Exception as e:
            self.logger.info("get_path_data error,message is", e.args)
        return self.path_data_lists

    def get_pathid_by_mouled_id(self, _id):
        """通过模块id找寻path—id

        :param _id: 模块id
        """
        result_list = []
        # http://yapi.platform.shuyun.com/api/interface/list?page=1&limit=20&project_id=514
        details = self.api.get(self.apiurl + "/api/interface/list?page=1&limit=9999&project_id=%s" % _id,
                               verify=False).json()
        for j in range(0, len(details.get("data").get("list"))):
            pathid = details.get("data").get("list")[j].get("_id")
            print("pathid started",_id, pathid)
            self.get_pathdata_by_pathid(pathid)
        print("path_data_lists:", self.path_data_lists, len(self.path_data_lists))


    def get_pathdata_by_pathid(self, pathid):
        """根据pathid获取每个接口的详细信息

        :param pathid: 接口id
        """

        pathdicts = {}  # 记录每个接口的信息
        # http://yapi.platform.shuyun.com/api/interface/get?id=7878
        pathdata = self.api.get(url=self.apiurl + "/api/interface/get?id=%s" % pathid, verify=False).json()
        pathdicts["path_address"] = pathdata.get("data").get("path")  # 接口地址
        pathdicts["up_time"] = time.strftime("%Y-%m-%d %H:%M:%S",
                                             time.localtime(int(pathdata.get("data").get("up_time"))))  # 接口变更时间
        pathdicts["add_time"] = time.strftime("%Y-%m-%d %H:%M:%S",
                                              time.localtime(int(pathdata.get("data").get("add_time"))))  # 接口添加时间
        pathdicts["method"] = pathdata.get("data").get("method")  # 接口请求方法
        pathdicts["model_name"] = self.pathmodlename  # 接口所属模块名称
        pathdicts["title"] = pathdata.get("data").get("title")
        key_value_dict = {}  # 请求表单的表单数据
        for requestdatas in pathdata.get("data").get("req_query"):
            flag = requestdatas.get("required")
            #key_value_dict[requestdatas.get("name")] = requestdatas.get("desc") + "(%s)" % ("必填" if flag else "非必填")
            key_value_dict[requestdatas.get("name")] = flag
        if key_value_dict == {}:
            pathdicts["request_form_data"] = ""
        else:
            pathdicts["request_form_data"] = key_value_dict  # 请求表单数据 key为参数名 value为字段说明(必填/非必填)
        result_request_header = pathdata.get("data").get("req_headers")
        if result_request_header == []:
            pathdicts["request_header"] = ""
        else:
            pathdicts["request_header"] = pathdata.get("data").get("req_headers")  # 请求header
        result_request_body = {}
        request_body = pathdata.get("data").get("req_body_other")   # 请求body
        #print("request_body:", type(request_body))
        if request_body is not None:
            if len(request_body) == 0:
                result_request_body = ""
            else:
                if ExecuteData.is_json(request_body) is True:
                    req_body_other_dic = json.loads(request_body)
                    if isinstance(req_body_other_dic, list):
                        result_request_body = ""
                    else:
                        # 有body是list，字典情况，需要查看有没有items字段，如果有就是
                        check_items = req_body_other_dic.get("items", 0)
                        if check_items != 0:
                            if len(req_body_other_dic["items"]) != 0:
                                a = req_body_other_dic["items"].get("properties", 0)
                                if a != 0:
                                    if len(req_body_other_dic["items"]["properties"]) != 0:
                                        for k, v in req_body_other_dic["items"]["properties"].items():
                                            result_request_body.update({k: v["type"]})
                                    else:
                                        result_request_body = ""
                                else:
                                    result_request_body = ""
                            else:
                                result_request_body = ""
                        else:
                            a = req_body_other_dic.get("properties", 0)
                            if a != 0:
                                if len(req_body_other_dic["properties"]) != 0:
                                    #print('req_body_other_dic["properties"]', req_body_other_dic["properties"])
                                    for k, v in req_body_other_dic["properties"].items():
                                        if isinstance(v, str):
                                            result_request_body = ""
                                        else:
                                            result_request_body.update({k: v["type"]})

                                else:
                                    result_request_body = ""
                            else:
                                result_request_body = ""
                else:#此种场景是body是直接写的具体的数据，先不处理
                    result_request_body = ""
        else:
            result_request_body = ""
        #pathdicts["request_body"] = json.dumps(result_request_body)
        pathdicts["request_body"] = result_request_body
        pathdicts["expected_response"] = pathdata.get("data").get("res_body")  # 预期响应
        pathdicts["path_name"] = pathdata.get("data").get("title")  # 接口名称
        pathdicts["path_create_user"] = pathdata.get("data").get("username")  # 接口创建者
        pathdicts["pathmodlename"] = self.pathmodlename

        self.path_data_lists.append(pathdicts)  # 追加每个接口的数据信息到列表中
        self.count += 1
        self.logger.info("模块%s第%d个接口%s的数据已经抓取完毕,数据是%s" % (self.pathmodlename, self.count, pathdicts["path_address"], pathdicts))


    def pathdata_to_excel(self):
        """将api数据写入excel"""
        for pathdata in self.path_data_lists:
            self.list_params_path_address.append(pathdata.get("path_address"))
            self.list_params_up_time.append(pathdata.get("up_time"))
            self.list_params_add_time.append(pathdata.get("add_time"))
            self.list_params_method.append(pathdata.get("method"))
            self.list_params_modle_name.append(pathdata.get("modle_name"))
            self.list_params_request_form_data.append(pathdata.get("request_form_data"))
            self.list_params_expected_response.append(pathdata.get("expected_response"))
            self.list_params_path_name.append(pathdata.get("path_name"))
            self.list_params_path_creat_user.append(pathdata.get("path_creat_user"))
        self.path_key_dicts["接口名称"] = self.list_params_path_name
        self.path_key_dicts["接口地址"] = self.list_params_path_address
        self.path_key_dicts["接口请求方法"] = self.list_params_method
        self.path_key_dicts["接口请求参数"] = self.list_params_request_form_data
        self.path_key_dicts["接口预期响应"] = self.list_params_expected_response
        self.path_key_dicts["接口所属模块名称"] = self.list_params_modle_name
        self.path_key_dicts["接口创建时间"] = self.list_params_add_time
        self.path_key_dicts["接口创建者"] = self.list_params_path_creat_user
        self.path_key_dicts["接口最新修改时间"] = self.list_params_up_time
        file_path = r'file/apidata.xlsx'  # 文件需要保存路径
        writer = pd.ExcelWriter(file_path)
        df = pd.DataFrame(self.path_key_dicts)
        df.to_excel(writer, columns=self.path_key_dicts.keys(), index=False, encoding='utf-8',
                    sheet_name='base接口数据')
        writer.save()

    def get_group(self):
        groups = {}
        group_data = self.api.get(url=self.apiurl + "/api/group/list", verify=False).json()
        for item in group_data['data']:
            if item["role"] == "owner":
                pass
            else:
                groups.update({item["_id"]:item["group_name"]})
                self.group_name = item["group_name"]
        print("groups:", groups)
        return groups


if __name__ == "__main__":
    # xiejiangpeng = Yapi(userapi="chune.wen@shuyun.com", passwdapi="Wce*2017", group_id="533")
    # xiejiangpeng.get_path_data()
    # aipdatalist = xiejiangpeng.path_data_lists  # api数据都在list中
    yapi_obj = Yapi(userapi="chune.wen@shuyun.com", passwdapi="Wce*2017")
    # group = yapi_obj.get_group()
    # for group_id, group_name in group.items():
    #     yapi_obj.get_path_data(group_id)
    # yapi_obj.get_path_data('21')
    yapi_obj.get_path_data('533')



