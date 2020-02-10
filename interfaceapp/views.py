from django.core.paginator import Paginator
from django.forms import model_to_dict
from django.shortcuts import render, redirect, HttpResponse, reverse
from django.http import HttpResponse, JsonResponse
from .forms import InterfaceGroupForm, InterfaceForm, InterfaceParamTemplateForm
from .models import InterfaceGroup, Interface, InterfaceParamTemplate, TestCaseSuit as ModelTestCaseSuit, TestCase as ModelTestCase
import json
from commons.UtilScript import ConnMySql
from commons.common import jsonPropt
from conf import read_config
import datetime
from django.views import View
from interfaceapp.generate_basic_test_cases import generator
from interfaceapp.scrapy_yapi.scrapy import Yapi
from django.core import serializers


def interface(request):
    print(InterfaceGroup.objects.filter(interface_group_name="数据质量"))
    print(InterfaceGroup.objects.filter(interface_group_name="数据质量1"))
    return render(request, 'interface/index.html', {'message': "我在测试"})


def interface_group(request):
    """
    接口组总览
    :param request:
    :return:
    """
    return render(request, 'interface/interface_group.html', {'message': "我在测试"})


def add_interface_group(request):
    """
    新增接口组
    :param request:
    :return:
    """
    if request.session.get('is_login', None):
        creator = request.session.get('user_name')
        if request.method == "GET":
            interface_group_form = InterfaceGroupForm()
            return render(request, 'interface/add_interface_group.html', {'interface_group_form': interface_group_form})

        if request.method == "POST":
            interface_group_form = InterfaceGroupForm(request.POST)
            if interface_group_form.is_valid():
                # 调试打印内容
                interface_group_name = interface_group_form.cleaned_data['interface_group_name']
                project_category = interface_group_form.cleaned_data['project_category']
                interface_group_desc = interface_group_form.cleaned_data["interface_group_desc"]
                sql = 'select * from interfaceapp_interfacegroup where interface_group_name = "{interface_group_name}"'.format(interface_group_name=interface_group_name)
                ConnMySql_instance = ConnMySql(read_config.DATABASE, sql)
                result = ConnMySql_instance.get_data()
                if len(result) == 0:
                    try:
                        obj = InterfaceGroup.objects.create(**interface_group_form.cleaned_data, interface_group_creator=creator)
                        print("obj:", obj)
                        message = "创建成功"
                        print(message)
                        return redirect("/interface/interfaceGroup")
                    except Exception as e:
                        message = e.args
                        print(message)
                        interface_group_form = InterfaceGroupForm()
                        return render(request, 'interface/add_interface_group.html', {'interface_group_form': interface_group_form,
                                                                                        'message': message})
                else:
                    message = "名字重复，请重新创建"
                    interface_group_form = InterfaceGroupForm()
                    return render(request, 'interface/add_interface_group.html', {'interface_group_form': interface_group_form,
                                                                                    'message': message})


def edit_interface_group(request):
    """
    编辑接口组
    :param request:
    :return:
    """
    if request.session.get('is_login', None):
        creator = request.session.get('user_name')
        print("creator:", creator)
        if request.method == "POST":
            update_id = request.POST.get('update_id')
            update_interface_group_name = request.POST.get('update_interface_group_name')
            update_project_category = request.POST.get('update_project_category')
            update_interface_group_desc = request.POST.get("update_interface_group_desc")
            try:
                data = {'interface_group_name': update_interface_group_name,
                        'interface_group_desc': update_interface_group_desc, 'project_category':
                        update_project_category, 'interface_group_creator': creator,
                        'interface_group_update_time': datetime.datetime.now()}
                obj = InterfaceGroup.objects.filter(interface_group_id=update_id).update(**data)
                print("obj:", obj)
                msg="success"
                return HttpResponse(json.dumps({'msg': msg}))
            except Exception as e:
                print("e.args", e.args[0])
                if e.args[0] == 1062:
                    msg = "duplicate"
                    print("msg:", msg)
                    return HttpResponse(json.dumps({'msg': msg}))
                else:
                    msg = "error"
                    print("msg:", msg)
                    return HttpResponse(json.dumps({'msg': msg}))


def del_interface_group(request):
    """
    删除接口组
    :param request:
    :return:
    """
    if request.session.get('is_login', None):
        if request.method == "POST":
            delete_id = request.POST.get('delete_id')
            print("post delete_id:", delete_id)
            try:
                InterfaceGroup.objects.filter(interface_group_id=delete_id).delete()
                status = "success"
                return HttpResponse(json.dumps({'status': status}))
            except Exception as e:
                return HttpResponse(json.dumps({'status': e.args}))


def get_interface_group(request):
    """
       根据条件获取接口组
       :param request:
       :return:
    """
    if request.session.get('is_login', None):
        creator = request.session.get('user_name')
        print("creator:", creator)
        search_kw = request.GET.get('search_kw', None)
        print("search_kw:", search_kw)
        checked = request.GET.get('creator', None)
        print("checked:", checked)
        # 获取分页参数用于查询对应页面数据，page为第几页，num为每页数据条数,right_boundary为数据切片的右侧边界
        page = request.GET.get('page')
        num = request.GET.get('rows')
        print("page:", page)
        print("num:", num)
        rows = []
        result_total = 0
        left = (int(page)-1) * int(num)
        right = num
        print("left:", left)
        print("right", right)
        if search_kw and checked:
            sql = 'select interface_group_id, interface_group_name,interface_group_desc,case project_category when 0 then "主动营销" when 1 then "数据平台" ' \
              'when 2 then "事件营销" when 3 then "互动赢家" else "nothing" end, interface_group_creator, date_format(interface_group_create_time, "%Y-%m-%d %H:%i:%s"), ' \
              'interface_group_update_time from interfaceapp_interfacegroup where interface_group_name like "%{kw}%" and interface_group_creator = "{creator}" order by interface_group_id desc limit ' \
              '{left}, {right}'.format(left=left, right=right, creator=creator, kw=search_kw)
            sql_total = 'select count(1) from interfaceapp_interfacegroup where interface_group_name like "%{kw}%" and interface_group_creator = "{creator}"'.format(kw=search_kw, creator=creator)
            print("sql=", sql)
        elif search_kw:
            sql = 'select interface_group_id,interface_group_name,interface_group_desc,case project_category when 0 then "主动营销" when 1 then "数据平台" ' \
                  'when 2 then "事件营销" when 3 then "互动赢家" else "nothing" end, interface_group_creator, date_format(interface_group_create_time, "%Y-%m-%d %H:%i:%s"), ' \
                  'interface_group_update_time from interfaceapp_interfacegroup where interface_group_name like "%{kw}%" order by interface_group_id desc limit ' \
                  '{left}, {right}'.format(left=left, right=right, creator=creator, kw=search_kw)
            sql_total = 'select count(1) from interfaceapp_interfacegroup where interface_group_name like "%{kw}%"'.format(kw=search_kw)
            print("sql=", sql)
        elif checked:
            sql = 'select interface_group_id,interface_group_name,interface_group_desc,case project_category when 0 then "主动营销" when 1 then "数据平台" ' \
                  'when 2 then "事件营销" when 3 then "互动赢家" else "nothing" end, interface_group_creator, date_format(interface_group_create_time, "%Y-%m-%d %H:%i:%s"), ' \
                  'interface_group_update_time from interfaceapp_interfacegroup where interface_group_creator = "{creator}" order by interface_group_id desc limit {left},{right}'.format(
                creator=creator, left=left,
                right=right)
            sql_total = 'select count(1) from interfaceapp_interfacegroup where interface_group_creator = "{creator}"'.format(creator=creator)
            print("sql=", sql)
        else:
            sql = 'select interface_group_id,interface_group_name,interface_group_desc,case project_category when 0 then "主动营销" when 1 then "数据平台" ' \
              'when 2 then "事件营销" when 3 then "互动赢家" else "nothing" end, interface_group_creator, date_format(interface_group_create_time, "%Y-%m-%d %H:%i:%s"), ' \
              'interface_group_update_time from interfaceapp_interfacegroup order by interface_group_id desc limit {left},{right}'.format(left=left,
                                                                                                           right=right)
            sql_total = "select count(1) from interfaceapp_interfacegroup"
            print("sql=", sql)
        try:
            ConnMySql_instance = ConnMySql(read_config.DATABASE, sql)
            result = ConnMySql_instance.get_data()
            ConnMySql_instance_total = ConnMySql(read_config.DATABASE, sql_total)
            result_total = ConnMySql_instance_total.get_data()

            for i in result:
                id = i[0]
                interface_group_name = str(i[1])
                interface_group_desc = str(i[2])
                project_category = str(i[3])
                interface_group_creator = str(i[4])
                create_time = str(i[5])
                rows.append({'id': id, 'interface_group_name': interface_group_name, 'interface_group_desc': interface_group_desc,
                         'project_category': project_category, 'interface_group_creator': interface_group_creator,
                         'interface_group_create_time': create_time})
        except Exception as e:
            print("get_project ERROR:" + str(e))
        return HttpResponse(json.dumps({'total': result_total, 'rows': rows}, ensure_ascii=False))


def get_project_category(request):
    """
    所有的项目组
    :param request:
    :return:
    """
    sql = 'select id,project_category from project_category'
    print("sql is", sql)
    get_interface_project_category = {}
    try:
        ConnMySql_instance = ConnMySql(read_config.DATABASE, sql)
        result = list(ConnMySql_instance.get_data())
        get_interface_project_category = dict(result)
        print("get_interface_project_category:", get_interface_project_category)
    except Exception as e:
        print('interface_project_category ERROR: ' + str(e))
    return JsonResponse(get_interface_project_category)


def get_all_interface_group(request):
    """
    所有的接口组
    :param request:
    :return:
    """
    sql = 'select interface_group_id, interface_group_name from interfaceapp_interfacegroup'
    print("sql is", sql)
    get_interface_group_category = {}
    try:
        ConnMySql_instance = ConnMySql(read_config.DATABASE, sql)
        result = list(ConnMySql_instance.get_data())
        get_interface_group_category = dict(result)
        print("get_interface_group_category:", get_interface_group_category)
    except Exception as e:
        print('get_interface_group_category ERROR: ' + str(e))
    return JsonResponse(get_interface_group_category)


def interface_list(request):
    """
    接口总览
    :param request:
    :return:
    """
    return render(request, 'interface/interface.html', {'message': "我在测试"})


def add_interface(request):
    """
    新增接口
    :param request:
    :return:
    """
    if request.session.get('is_login', None):
        creator = request.session.get('user_name')
        if request.method == "GET":
            interface_form = InterfaceForm()
            return render(request, 'interface/add_interface.html', {'interface_form': interface_form})

        if request.method == "POST":
            interface_form = InterfaceForm(request.POST)
            if interface_form.is_valid():
                # 调试打印内容
                interface_name = interface_form.cleaned_data['interface_name']
                interface_category = interface_form.cleaned_data['interface_category_id']
                sql = 'select * from interfaceapp_interface where interface_name = "{interface_name}" and ' \
                      'interface_category_id = "{interface_category}"'.format(interface_name=interface_name,
                                                                           interface_category=interface_category)
                print("sql:", sql)
                ConnMySql_instance = ConnMySql(read_config.DATABASE, sql)
                result = ConnMySql_instance.get_data()
                print("result:", result)
                if len(result) == 0:
                    try:
                        obj = Interface.objects.create(**interface_form.cleaned_data, interface_creator=creator)
                        print("obj:", obj)
                        message = "创建成功"
                        print(message)
                        return redirect("/interface/interfaceList")
                    except Exception as e:
                        message = e.args
                        print(message)
                        interface_form = InterfaceForm()
                        return render(request, 'interface/add_interface.html', {'interface_form': interface_form,
                                                                                'message': message})
                else:
                    message = "名字重复，请重新创建"
                    interface_form = InterfaceForm()
                    return render(request, 'interface/add_interface_group.html', {'interface_form': interface_form,
                                                                                  'message': message})
            else:
                print("errors:", interface_form.errors)
                return render(request, 'interface/add_interface.html', {'interface_form': interface_form})


def get_interface_list(request):
    """
    根据条件获取接口
    :param reqeust:
    :return:
    """
    if request.session.get('is_login', None):
        creator = request.session.get('user_name')
        print("creator:", creator)
        search_kw = request.GET.get('search_kw', None)
        print("search_kw:", search_kw)
        checked = request.GET.get('creator', None)
        print("checked:", checked)
        # 获取分页参数用于查询对应页面数据，page为第几页，num为每页数据条数,right_boundary为数据切片的右侧边界
        page = request.GET.get('page')
        num = request.GET.get('rows')
        rows = []
        result_total = 0
        left = (int(page)-1) * int(num)
        right = num
        print("left:", left)
        print("right", right)
        if search_kw and checked:
            sql = 'select interface_group_id, interface_group_name,interface_group_desc,case project_category when 0 then "主动营销" when 1 then "数据平台" ' \
              'when 2 then "事件营销" when 3 then "互动赢家" else "nothing" end, interface_group_creator, date_format(interface_group_create_time, "%Y-%m-%d %H:%i:%s"), ' \
              'interface_group_update_time from interfaceapp_interfacegroup where interface_group_name like "%{kw}%" and interface_group_creator = "{creator}" order by interface_group_id desc limit ' \
              '{left}, {right}'.format(left=left, right=right, creator=creator, kw=search_kw)
            sql_total = 'select count(1) from interfaceapp_interface where interface_group_name like "%{kw}%" and interface_group_creator = "{creator}"'.format(kw=search_kw, creator=creator)
            print("sql=", sql)
        elif search_kw:
            sql = 'select interface_group_id,interface_group_name,interface_group_desc,case project_category when 0 then "主动营销" when 1 then "数据平台" ' \
                  'when 2 then "事件营销" when 3 then "互动赢家" else "nothing" end, interface_group_creator, date_format(interface_group_create_time, "%Y-%m-%d %H:%i:%s"), ' \
                  'interface_group_update_time from interfaceapp_interfacegroup where interface_group_name like "%{kw}%" order by interface_group_id desc limit ' \
                  '{left}, {right}'.format(left=left, right=right, creator=creator, kw=search_kw)
            sql_total = 'select count(1) from interfaceapp_interface where interface_group_name like "%{kw}%"'.format(kw=search_kw)
            print("sql=", sql)
        elif checked:
            sql = 'select interface_group_id,interface_group_name,interface_group_desc,case project_category when 0 then "主动营销" when 1 then "数据平台" ' \
                  'when 2 then "事件营销" when 3 then "互动赢家" else "nothing" end, interface_group_creator, date_format(interface_group_create_time, "%Y-%m-%d %H:%i:%s"), ' \
                  'interface_group_update_time from interfaceapp_interfacegroup where interface_group_creator = "{creator}" order by interface_group_id desc limit {left},{right}'.format(
                creator=creator, left=left,
                right=right)
            sql_total = 'select count(1) from interfaceapp_interface where interface_creator = "{creator}"'.format(creator=creator)
            print("sql=", sql)
        else:
            sql = 'select a.interface_id,a.interface_name,b.interface_group_name,a.interface_desc,a.interface_request_type,a.interface_address,case a.interface_status when "valid" then "有效" when "invalid" then "无效" end as status,a.interface_headers, a.interface_parameters, a.interface_body,a.interface_creator,date_format(a.interface_create_time, "%Y-%m-%d %H:%i:%s"),date_format(a.interface_update_time, "%Y-%m-%d %H:%i:%s") from interfaceapp_interface a join interfaceapp_interfacegroup b on a.interface_category_id = b.interface_group_id order by a.interface_id desc limit {left},{right}'.format(
                left=left,
                right=right)
            sql_total = "select count(1) from interfaceapp_interface"
            print("sql=", sql)
        try:
            ConnMySql_instance = ConnMySql(read_config.DATABASE, sql)
            result = ConnMySql_instance.get_data()
            ConnMySql_instance_total = ConnMySql(read_config.DATABASE, sql_total)
            result_total = ConnMySql_instance_total.get_data()

            for i in result:
                id = i[0]
                interface_name = str(i[1])
                interface_group_name = str(i[2])
                interface_desc = str(i[3])
                interface_request_type = str(i[4])
                interface_address = str(i[5])
                interface_status = str(i[6])
                interface_headers = str(i[7])
                interface_parameters = str(i[8])
                interface_body = str(i[9])
                interface_creator = str(i[10])
                interface_create_time = str(i[11])

                rows.append({'id': id,
                             'interface_name': interface_name,
                             'interface_group_name': interface_group_name,
                             'interface_desc': interface_desc,
                             'interface_request_type': interface_request_type,
                             'interface_address': interface_address,
                             'interface_status': interface_status,
                             'interface_headers': interface_headers,
                             'interface_parameters':interface_parameters,
                             'interface_body': interface_body,
                             'interface_creator': interface_creator,
                             'interface_create_time': interface_create_time})
        except Exception as e:
            print("get_project ERROR:" + str(e))
        return HttpResponse(json.dumps({'total': result_total, 'rows': rows}, ensure_ascii=False))


def edit_interface(request):
    """
    编辑接口
    :param request:
    :return:
    """
    if request.session.get('is_login', None):
        creator = request.session.get('user_name')
        print("creator:", creator)
        if request.method == "POST":
            update_id = request.POST.get('update_id')
            update_interface_name = request.POST.get('update_interface_name')
            update_interface_group = request.POST.get('update_interface_group')
            update_interface_address = request.POST.get('update_interface_address')
            update_interface_request_type = request.POST.get("update_interface_request_type")
            update_interface_header = request.POST.get("update_interface_header")
            update_interface_param = request.POST.get("update_interface_param")
            update_interface_body = request.POST.get("update_interface_body")
            update_interface_desc = request.POST.get("update_interface_desc")
            update_interface_status = request.POST.get("update_interface_status")
            try:
                data = {'interface_name': update_interface_name,
                        'interface_category': update_interface_group,
                        'interface_desc': update_interface_desc,
                        'interface_request_type': update_interface_request_type,
                        'interface_address': update_interface_address,
                        'interface_status': update_interface_status,
                        'interface_headers': update_interface_header,
                        'interface_parameters': update_interface_param,
                        'interface_body': update_interface_body,
                        'interface_creator': creator,
                        'interface_update_time': datetime.datetime.now()}
                obj = Interface.objects.filter(interface_id=update_id).update(**data)
                print("obj:", obj)
                msg = "success"
                return HttpResponse(json.dumps({'msg': msg}))
            except Exception as e:
                print("e.args", e.args[0])
                if e.args[0] == 1062:
                    msg = "duplicate"
                    print("msg:", msg)
                    return HttpResponse(json.dumps({'msg': msg}))
                else:
                    msg = "error"
                    print("msg:", msg)
                    return HttpResponse(json.dumps({'msg': msg}))


def del_interface(request):
    """
    删除接口组
    :param request:
    :return:
    """
    if request.session.get('is_login', None):
        if request.method == "POST":
            delete_id = request.POST.get('delete_id')
            print("post delete_id:", delete_id)
            try:
                Interface.objects.filter(interface_id=delete_id).delete()
                status = "success"
                return HttpResponse(json.dumps({'status': status}))
            except Exception as e:
                return HttpResponse(json.dumps({'status': e.args}))


def get_test_case(requst):
    pass


def get_test_case_report(request):
    pass


def all_template(request):
    return render(request, 'interface/interface_param_template.html', {'message': "我在测试"})


class TestCaseParamTemplate(View):
    """"""
    def get(self, request):
        # <view logic>
        """
               根据条件获取接口组
               :param request:
               :return:
            """
        if request.session.get('is_login', None):
            creator = request.session.get('user_name')
            print("creator:", creator)
            search_kw = request.GET.get('search_kw', None)
            print("search_kw:", search_kw)
            # 获取分页参数用于查询对应页面数据，page为第几页，num为每页数据条数,right为数据切片的右侧边界
            page = request.GET.get('page')
            print("page:", page)
            num = request.GET.get('rows')
            print("num:", num)
            rows = []
            result_total = 0
            if page is None or num is None:
                id = InterfaceParamTemplate.objects.values_list('interface_param_template_id', flat=True)
                template_name = InterfaceParamTemplate.objects.values_list('template_name', flat=True)
                d = zip(id, template_name)
                return HttpResponse(json.dumps(dict(d), ensure_ascii=False))
            else:
                left = (int(page) - 1) * int(num)
                right = num
                print("left:", left)
                print("right", right)
                if search_kw:
                    sql = 'select * from interfaceapp_interfaceparamtemplate where template_name like "%{kw}%" order by interface_param_template_id desc limit ' \
                      '{left}, {right}'.format(left=left, right=right, kw=search_kw)
                    sql_total = 'select count(1) from interfaceapp_interfaceparamtemplate where template_name' \
                            ' like "%{kw}%"'.format(kw=search_kw)
                    print("sql=", sql)
                else:
                    sql = 'select * from interfaceapp_interfaceparamtemplate order by interface_param_template_id desc limit {left},{right}'.format(left=left, right=right)
                    sql_total = "select count(1) from interfaceapp_interfaceparamtemplate"
                    print("sql=", sql)
                try:
                    ConnMySql_instance = ConnMySql(read_config.DATABASE, sql)
                    result = ConnMySql_instance.get_data()
                    ConnMySql_instance_total = ConnMySql(read_config.DATABASE, sql_total)
                    result_total = ConnMySql_instance_total.get_data()
                    # goods = InterfaceParamTemplate.objects.all()[:10]
                    # json_data = serializers.serialize('json', goods)
                    # json_data = json.loads(json_data)
                    # print("json_data", json_data)

                    for i in result:
                        print("i", i)
                        id = i[0]
                        template_name = str(i[1])
                        template_desc = str(i[2])
                        string = str(i[3])
                        int_data = str(i[4])
                        number = str(i[5])
                        date = str(i[6])
                        bool = str(i[7])
                        decimal = str(i[8])
                        creator = str(i[9])
                        create_time = str(i[10])[:-7]
                        update_time = str(i[11])[:-7]

                        rows.append({'id': id,
                                 'template_name': template_name,
                                 'template_desc': template_desc,
                                 'string': string,
                                 'int': int_data,
                                 'number': number,
                                 'date': date,
                                 'bool': bool,
                                 'decimal': decimal,
                                 'creator': creator,
                                 'create_time': create_time,
                                 'update_time':update_time
                                 })
                        print(HttpResponse(json.dumps({'total': result_total, 'rows': rows}, ensure_ascii=False)))
                except Exception as e:
                    print("get_TestCaseParamTemplate ERROR:" + str(e))
                return HttpResponse(json.dumps({'total': result_total, 'rows': rows}, ensure_ascii=False))

    def post(self, request):
        if request.session.get('is_login', None):
            creator = request.session.get('user_name')
            print("creator:", creator)
            if request.method == "POST":
                delete_id = request.POST.get('delete_id')
                update_id = request.POST.get('update_id')
                if delete_id is not None:

                    print("post delete_id:", delete_id)
                    try:
                        InterfaceParamTemplate.objects.filter(interface_param_template_id=delete_id).delete()
                        status = "success"
                        return HttpResponse(json.dumps({'status': status}))
                    except Exception as e:
                        return HttpResponse(json.dumps({'status': e.args}))
                if update_id is not None:
                    update_template_name = request.POST.get('update_template_name')
                    update_template_desc = request.POST.get('update_template_desc')
                    update_string = request.POST.get('update_string')
                    update_int = request.POST.get("update_int")
                    update_number = request.POST.get("update_number")
                    update_date = request.POST.get("update_date")
                    update_bool = request.POST.get("update_bool")
                    update_decimal = request.POST.get("update_decimal")
                    try:
                        data = {'template_name': update_template_name,
                            'template_desc': update_template_desc,
                            'string': update_string,
                            'int': update_int,
                            'number': update_number,
                            'date': update_date,
                            'bool': update_bool,
                            'decimal': update_decimal,
                            'creator': creator,
                            'update_time': datetime.datetime.now()}
                        obj = InterfaceParamTemplate.objects.filter(interface_param_template_id=update_id).update(**data)
                        print("obj:", obj)
                        msg = "success"
                        return HttpResponse(json.dumps({'msg': msg}))
                    except Exception as e:
                        print("e.args", e.args[0])
                        if e.args[0] == 1062:
                            msg = "duplicate"
                            print("msg:", msg)
                            return HttpResponse(json.dumps({'msg': msg}))
                        else:
                            msg = "error"
                            print("msg:", msg)
                            return HttpResponse(json.dumps({'msg': msg}))

    # def delete(self, request):
    #     if request.session.get('is_login', None):
    #         if request.method == "DELETE":
    #             delete_id = request.POST.get('delete_id')
    #             print("post delete_id:", delete_id)
    #             try:
    #                 InterfaceParamTemplate.objects.filter(id=delete_id).delete()
    #                 status = "success"
    #                 return HttpResponse(json.dumps({'status': status}))
    #             except Exception as e:
    #                 return HttpResponse(json.dumps({'status': e.args}))


class AddTestCaseParam(View):

    def get(self, request):
        test_case_param_template = InterfaceParamTemplateForm()
        return render(request, 'interface/add_interface_param.html',
                      {'test_case_param_template': test_case_param_template})

    def post(self, request):
        creator = request.session.get('user_name')
        test_case_param_template = InterfaceParamTemplateForm(request.POST)
        if test_case_param_template.is_valid():
            template_name = request.POST.get('template_name')
            template_desc = request.POST.get('template_desc')
            string = request.POST.get('string')
            create_int = request.POST.get('int')
            number = request.POST.get("number")
            date = request.POST.get("date")
            bool = request.POST.get("bool")
            decimal = request.POST.get("decimal")
            obj = InterfaceParamTemplate.objects.filter(template_name=template_name)
            print("template_name:", template_name)
            print("obj:", obj, type(obj), len(obj))
            if len(obj) == 0:
                try:
                    data = {
                        'template_name': template_name,
                        'template_desc': template_desc,
                        'string': string,
                        'int': create_int,
                        'number': number,
                        'date': date,
                        'bool': bool,
                        'decimal': decimal,
                        'creator': creator,
                        }
                    InterfaceParamTemplate.objects.create(**data)
                    return redirect("/interface/allTemplate")
                except Exception as e:
                    message = e.args
                    print(message)
                    interface_param_template_form = InterfaceParamTemplateForm()
                    return render(request, 'interface/add_interface_param.html',
                              {'test_case_param_template': interface_param_template_form,
                               'message': message})
            else:
                message = "名字重复，请重新创建"
                interface_param_template_form = InterfaceParamTemplateForm()
                return render(request, 'interface/add_interface_param.html',
                              {'test_case_param_template': interface_param_template_form,
                               'message': message})


class BasicTestCase(View):

    def get(self, request):
        if request.session.get('is_login', None):
            creator = request.session.get('user_name')
            print("creator:", creator)
            interface_id = request.GET.get('interface_id', None)
            print("interface_id:", interface_id)
            test_suit_id = request.GET.get('test_suit_id', None)
            print("test_suit_id:", test_suit_id)
            # 获取分页参数用于查询对应页面数据，page为第几页，num为每页数据条数,right为数据切片的右侧边界
            page = request.GET.get('page')
            print("page:", page)
            num = request.GET.get('rows')
            print("num:", num)
            rows = []
            total = 0
            if test_suit_id:
                try:
                    test_suit_obj = ModelTestCaseSuit.objects.filter(test_suit_id=test_suit_id).first()
                    test_case_obj = test_suit_obj.test_case.all().values('test_case_id', 'test_case_name','test_case_data')
                    print("test_case_obj:", test_case_obj, type(test_case_obj))
                    p = Paginator(test_suit_obj.test_case.all().values('test_case_id', 'test_case_name','test_case_data').order_by("-test_case_id"), num)
                    total = test_suit_obj.test_case.all().count()
                    print('p:', p)
                    print('total:', total)
                    all_test_case = p.page(page).object_list
                    for test_case in all_test_case:
                        print("json_dict:", test_case)
                        rows.append(test_case)
                except Exception as e:
                    print("get_BasicTestCase ERROR:" + str(e))
                    return HttpResponse(json.dumps({'total': total, 'rows': rows}, ensure_ascii=False))
                return HttpResponse(json.dumps({'total': total, 'rows': rows}, ensure_ascii=False))
            else:
                try:
                    p = Paginator(ModelTestCase.objects.all().order_by('-test_case_id'), num)
                    total = ModelTestCase.objects.count()
                    all_test_case = p.page(page).object_list
                    for test_case in all_test_case:
                        json_dict = model_to_dict(test_case, exclude=["test_case", "interface"])
                        print("json_dict:", json_dict)
                        rows.append(json_dict)
                except Exception as e:
                    print("get_BasicTestCase ERROR:" + str(e))
                    return HttpResponse(json.dumps({'total': total, 'rows': rows}, ensure_ascii=False))
                return HttpResponse(json.dumps({'total': total, 'rows': rows}, ensure_ascii=False))

    def post(self, request):
        if request.session.get('is_login', None):
            creator = request.session.get('user_name')
            print("creator:", creator)
            param = {}
            interface_body = {}
            interface_id = {}
            param_template_name = request.POST.get('param_template_name')
            print("param_template_name:", param_template_name)
            test_suit_id = request.POST.get('test_suit_id')
            print('test_suit_id:', test_suit_id)
            # 根据模板名称获取模板配置
            param_obj = InterfaceParamTemplate.objects.filter(template_name=param_template_name).values('string', 'int', 'date', 'decimal', 'bool', 'number')
            print("param_obj:", param_obj, type(param_obj))
            for i in param_obj:
                param = i
            print("param:", param, type(param))
            # 根据用例集合查询接口配置
            # select * from interfaceapp_interface where interface_id = (select interface_id from interfaceapp_testcasesuit_interface where testcasesuit_id = '9')
            # 获取此test_suit下所有接口
            test_suit_obj = ModelTestCaseSuit.objects.filter(test_suit_id=test_suit_id).first()
            interface_obj = test_suit_obj.interface.all().values('interface_body', 'interface_id')
            print("interface_obj:", interface_obj, type(interface_obj))
            for i in interface_obj:
                interface_body = i['interface_body']
                interface_id = i['interface_id']
            print("interface_body:", interface_body, type(interface_body))
            print("aa:", json.loads(interface_body), type(json.loads(interface_body)))
            print("interface_id:", interface_id, type(interface_id))
            # 创建基础用例
            mydict = json.loads(interface_body)
            print("mydict:", mydict, type(mydict))
            case_dict = generator.create_base_case(mydict, param)
            try:
                for k, v in case_dict.items():
                    test_case_name = k
                    test_case_body = v
                    print("test_case_name is:", test_case_name)
                    print("test_case_body is:", test_case_body)
                    obj = ModelTestCase.objects.filter(interface_id=interface_id, test_case_name=test_case_name)
                    print(obj, len(obj))
                    if len(obj) == 0:
                        data = {
                            'test_case_name': test_case_name,
                            'test_case_data': test_case_body,
                            'creator': creator,
                            'interface_id': interface_id
                        }
                        test_case_obj = ModelTestCase.objects.create(**data)
                        test_case_id = ModelTestCase.objects.filter(test_case_name=test_case_name).first()
                        test_suit_obj.test_case.add(test_case_id)
                    else:
                        msg = "duplicate"
                        return HttpResponse(json.dumps({'msg': msg}))
                msg = "success"
                return HttpResponse(json.dumps({'msg': msg, 'test_suit_id': test_suit_id}))
            except Exception as e:
                msg = e.args
                print("create test cases failed, error message is:", e.args)
                return HttpResponse(json.dumps({'msg': msg}))


def all_basic_test_case(request):

    return render(request, 'interface/basic_test_case.html', {'test_suit_id': request.GET.get("test_suit_id")})


def all_test_suit(request):

    return render(request, 'interface/test_case_suit.html',  {'message': "我在测试"})


class TestCaseSuit(View):

    def get(self, request):
        if request.session.get('is_login', None):
            creator = request.session.get('user_name')
            print("creator:", creator)
            search_kw = request.GET.get('search_kw', None)
            print("search_kw:", search_kw)
            # 获取分页参数用于查询对应页面数据，page为第几页，num为每页数据条数,right为数据切片的右侧边界
            page = request.GET.get('page')
            print("page:", page)
            num = request.GET.get('rows')
            print("num:", num)
            rows = []
            total = 0
            try:
                p = Paginator(ModelTestCaseSuit.objects.all().order_by('-test_suit_id'), num)
                total = ModelTestCaseSuit.objects.count()
                all_test_suit = p.page(page).object_list
                for test_suit in all_test_suit:
                    json_dict = model_to_dict(test_suit, exclude=["test_case", "interface"])
                    print("json_dict:", json_dict)
                    rows.append(json_dict)
            except Exception as e:
                print("get_TestCaseParamTemplate ERROR:" + str(e))
                return HttpResponse(json.dumps({'total': total, 'rows': rows}, ensure_ascii=False))
            return HttpResponse(json.dumps({'total': total, 'rows': rows}, ensure_ascii=False))

    def post(self, request):
        creator = request.session.get('user_name')
        if request.session.get('is_login', None):
            test_suit_name = request.POST.get('add_test_suit_name')
            print("test_suit_name:", test_suit_name)
            param_template = request.POST.get('add_param_template')
            print("param_template:", param_template, type(param_template))
            apply_interface_name = request.POST.get('add_apply_interface_name')
            print("apply_interface_name:", apply_interface_name)
            obj = ModelTestCaseSuit.objects.filter(test_suit_name=test_suit_name)
            print('test_case_suit obj:', obj)
            if param_template is None:
                param_template = ''
            print("obj:", obj, type(obj), len(obj))
            if len(obj) == 0:
                try:
                    data = {
                        'test_suit_name': test_suit_name,
                        'param_template': param_template,
                        'creator': creator,
                    }
                    print("data:", data)
                    test_suit_obj = ModelTestCaseSuit.objects.create(**data)
                    apply_interface_id = Interface.objects.filter(interface_name=apply_interface_name).first()
                    print("apply_interface_id:", apply_interface_id)
                    test_suit_obj.interface.add(apply_interface_id)
                    msg = "success"
                    return HttpResponse(json.dumps({'msg': msg}))
                except Exception as e:
                    msg = e.args
                    print(msg)
                    return HttpResponse(json.dumps({'msg': msg}))
            else:
                msg = "duplicate"
                return HttpResponse(json.dumps({'msg': msg}))

    # def put(self, request):
    #     if request.session.get('is_login', None):
    #         creator = request.session.get('user_name')
    #         print("creator:", creator)
    #         if request.method == "PUT":
    #             update_id = request.POST.get('update_id')
    #             update_interface_name = request.POST.get('update_interface_name')
    #             try:
    #                 data = {'interface_name': update_interface_name,
    #                         'interface_creator': creator,
    #                         'interface_update_time': datetime.datetime.now()}
    #                 obj = Interface.objects.filter(id=update_id).update(**data)
    #                 print("obj:", obj)
    #                 msg = "success"
    #                 return HttpResponse(json.dumps({'msg': msg}))
    #             except Exception as e:
    #                 print("e.args", e.args[0])
    #                 if e.args[0] == 1062:
    #                     msg = "duplicate"
    #                     print("msg:", msg)
    #                     return HttpResponse(json.dumps({'msg': msg}))
    #                 else:
    #                     msg = "error"
    #                     print("msg:", msg)
    #                     return HttpResponse(json.dumps({'msg': msg}))


class TestCase(View):
    def get(self, request, id):
        pass


class AutoAddInterfaces(View):
    def get(self):
        pass


class AutoAddInterfaceGroup(View):
    def post(self, request):
        interface_group_list_to_insert = list()
        creator = request.session.get('user_name')
        if request.session.get('is_login', None):
            yapi_obj = Yapi(userapi=read_config.YAPI_USERNAME, passwdapi=read_config.YAPI_PASSWORD)
            groups = yapi_obj.get_group()
            # 目前所属项目组固定写到数据平台，因为目前没有项目组和group之间的关系，数据也比较少，写进去后手动可以update一下所属项目
            for group_id, group_name in groups.items():
                obj = InterfaceGroup.objects.filter(interface_group_name=group_name)
                if len(obj) == 0:
                    interface_group_list_to_insert.append(InterfaceGroup(interface_group_name=group_name,
                                                                         interface_group_desc='auto_detect_' + group_name,
                                                                         project_category=1,
                                                                         interface_group_creator=creator))

            print('interface_group_list_to_insert:', interface_group_list_to_insert)
            try:
                interface_group_obj = InterfaceGroup.objects.bulk_create(interface_group_list_to_insert)
                msg = "success"
                return HttpResponse(json.dumps({'msg': msg}))
            except Exception as e:
                msg = e.args
                print(msg)
                return HttpResponse(json.dumps({'msg': msg}))


class AutoAddInterfaces(View):
    def post(self, request):
        interface_list_to_insert = list()
        creator = request.session.get('user_name')
        if request.session.get('is_login', None):
            yapi_obj = Yapi(userapi=read_config.YAPI_USERNAME, passwdapi=read_config.YAPI_PASSWORD)
            groups = yapi_obj.get_group()
            # for group_id, group_name in groups.items():
            #     tmp_result = yapi_obj.get_path_data(group_id)
            tmp_result = yapi_obj.get_path_data('533')
            for result_dict in tmp_result:
                interface_group_obj = InterfaceGroup.objects.filter(interface_group_name="数据质量").values(
                    "interface_group_id")
                print("interface_group_obj", interface_group_obj, type(interface_group_obj))
                for i in interface_group_obj:
                    interface_group_id = i["interface_group_id"]
                interface_name = result_dict["model_name"] + "-" + result_dict['title']
                print("interface_name:", interface_name)
                interface_request_type = result_dict["method"]
                print("interface_request_type:", interface_request_type)
                interface_address = result_dict["path_address"]
                print("interface_address:", interface_address)
                if len(result_dict["request_header"]) > 0:
                    interface_headers = json.dumps(result_dict["request_header"][0])
                else:
                    interface_headers = result_dict["request_header"]

                print("interface_headers:", interface_headers)
                interface_parameters = result_dict["request_form_data"]
                print("interface_parameters:", interface_parameters)
                if len(result_dict["request_body"]) > 0:
                    interface_body = json.dumps(result_dict["request_body"])
                else:
                    interface_body = result_dict["request_body"]
                print("interface_body:", interface_body)
                print("###############################")

                obj = Interface.objects.filter(interface_category_id=interface_group_id,
                                               interface_name=interface_name,
                                               interface_address=interface_address)
                if len(obj) == 0:
                    interface_list_to_insert.append(Interface(interface_name=interface_name,
                                                              interface_category_id=interface_group_id,
                                                                interface_desc='Auto_detect' + interface_name,
                                                                   interface_request_type=interface_request_type,
                                                                   interface_address=interface_address,
                                                                   interface_status="valid",
                                                                   interface_headers=interface_headers,
                                                                   interface_parameters=interface_parameters,
                                                                   interface_body=interface_body,
                                                                   interface_creator=creator))

            print('interface_list_to_insert:', interface_list_to_insert)
            try:
                interface_obj = Interface.objects.bulk_create(interface_list_to_insert)
                msg = "success"
                return HttpResponse(json.dumps({'msg': msg}))
            except Exception as e:
                msg = e.args
                print(msg)
                return HttpResponse(json.dumps({'msg': msg}))


class ExportTestCases(View):
    def get(self, request):
        if request.session.get('is_login', None):
            creator = request.session.get('user_name')
            print("creator:", creator)
            interface_id = request.GET.get('interface_id', None)
            print("interface_id:", interface_id)
            test_suit_id = request.GET.get('test_suit_id', None)
            print("test_suit_id:", test_suit_id)
            # 获取分页参数用于查询对应页面数据，page为第几页，num为每页数据条数,right为数据切片的右侧边界
            page = request.GET.get('page')
            print("page:", page)
            num = request.GET.get('rows')
            print("num:", num)
            rows = []
            total = 0
            if test_suit_id:
                try:
                    test_suit_obj = ModelTestCaseSuit.objects.filter(test_suit_id=test_suit_id).first()
                    test_case_obj = test_suit_obj.test_case.all().values('test_case_id', 'test_case_name','test_case_data')
                    print("test_case_obj:", test_case_obj, type(test_case_obj))
                    p = Paginator(test_suit_obj.test_case.all().values('test_case_id', 'test_case_name','test_case_data').order_by("-test_case_id"), num)
                    total = test_suit_obj.test_case.all().count()
                    print('p:', p)
                    print('total:', total)
                    all_test_case = p.page(page).object_list
                    for test_case in all_test_case:
                        print("json_dict:", test_case)
                        rows.append(test_case)
                except Exception as e:
                    print("get_BasicTestCase ERROR:" + str(e))
                    return HttpResponse(json.dumps({'total': total, 'rows': rows}, ensure_ascii=False))
                return HttpResponse(json.dumps({'total': total, 'rows': rows}, ensure_ascii=False))
            else:
                try:
                    p = Paginator(ModelTestCase.objects.all().order_by('-test_case_id'), num)
                    total = ModelTestCase.objects.count()
                    all_test_case = p.page(page).object_list
                    for test_case in all_test_case:
                        json_dict = model_to_dict(test_case, exclude=["test_case", "interface"])
                        print("json_dict:", json_dict)
                        rows.append(json_dict)
                except Exception as e:
                    print("get_BasicTestCase ERROR:" + str(e))
                    return HttpResponse(json.dumps({'total': total, 'rows': rows}, ensure_ascii=False))
                return HttpResponse(json.dumps({'total': total, 'rows': rows}, ensure_ascii=False))




