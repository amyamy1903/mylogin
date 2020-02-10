from django.shortcuts import render, render_to_response
from django.views.decorators.cache import cache_page
# Create your views here.

from commons.UtilScript import ConnMySql
from django.http import HttpResponse, JsonResponse
from conf import read_config


def index(request):
    """
    绑定网站首页，这个绑定的是测试用bug模块展示的首页
    :param request:
    :return:
    """
    return render(request, 'bug_statistics_date.html')


def get_monitor_type_names_bak(request):
    """
    返回指标维度数据，数据在数据库中存储，指标维度数据获取的一种方式，这个先不用，在这写着
    :param request:
    :return:
    """
    sql = 'select data_type from monitor_data_type;'
    monitor_type_Names = {}
    try:
        ConnMySql_instance = ConnMySql(read_config.DATABASE2, sql)
        result = list(ConnMySql_instance.get_data())
        result = [r[0] for r in result]
        for key in result:
            monitor_type_Names[key] = key
            print("monitor_type_Name is:", key)
    except Exception as e:
        print('get_monitor_type_names ERROR: ' + str(e))
    return JsonResponse(monitor_type_Names)


def get_tenant_name(request):
    """
    动态获取数据库结果表中所有的租户，这个暂时也还没有用
    :param request:
    :return:
    """
    beginDate = request.GET.get("beginDate", "2019-01-07 00:00:00")
    endDate = request.GET.get("endDate", "2019-01-23 18:00:00")
    print("beginDate0", beginDate)
    print("endDate0", endDate)
    platName = request.GET.get("platName", "TAOBAO")
    print("platName0 is:", platName)
    sql = 'select distinct(tenant) from es_daily_monitor_data where plat_code = "{plat_code}" and start_date = "{start_date}" and end_date = "{end_date}";'.format(
        plat_code=platName, start_date=beginDate, end_date=endDate)
    print("sql is", sql)
    tenantNames = {}
    try:
        ConnMySql_instance = ConnMySql(read_config.DATABASE2, sql)
        result = list(ConnMySql_instance.get_data())
        result = [r[0] for r in result]
        for key in result:
            tenantNames[key] = key
            #print("tenant name is:", key)
    except Exception as e:
        print('get_tenant_name ERROR: ' + str(e))
    return JsonResponse(tenantNames)


def get_time_interval(request):
    """
    结果表中时间维度，返回值为start_date和end_date，由前端组装
    :param request:
    :return:
    """
    sql = 'select start_date, end_date from es_daily_monitor_data group by start_date,end_date;'
    time_interval = {}
    try:
        ConnMySql_instance = ConnMySql(read_config.DATABASE2, sql)
        result = ConnMySql_instance.get_data()
        for i in result:
            key = str(i[0]) + '|' + str(i[1])
            time_interval[key] = key
    except Exception as e:
        print("get_time_interval ERROR:" + str(e))
    return JsonResponse(time_interval)


def get_time_interval_and_plat_code(request):
    """
    结果表中时间维度，返回值为start_date和end_date和plat_code由前端组装,这么返回的原因是这样直接就能知道所有数据分组，不用再去勾选平台
    :param request:
    :return:
    """
    sql = 'select start_date, end_date, plat_code from es_daily_monitor_data group by start_date,end_date,plat_code;'
    time_interval_and_plat_code = {}
    try:
        ConnMySql_instance = ConnMySql(read_config.DATABASE2, sql)
        result = ConnMySql_instance.get_data()
        print("result:", result)
        for i in result:
            key = str(i[0]) + '|' + str(i[1]) + '|' + str(i[2])
            print("key:", key)
            time_interval_and_plat_code[key] = key
    except Exception as e:
        print("get_time_interval ERROR:" + str(e))
    return JsonResponse(time_interval_and_plat_code)


#@cache_page(60 * 5)
def get_date_tenant_monitor_statics(request):
    """
    维度数据展示主方法PRIMARY KEY(`tenant`, `plat_code`, `start_date`, `end_date`)
    :param request:
    :return:
    """
    beginDate = request.GET.get("beginDate", "2019-01-07 00:00:00")
    endDate = request.GET.get("endDate", "2019-01-23 18:00:00")
    print("beginDate", beginDate)
    print("endDate", endDate)
    index_names = request.GET.get("monitor_type_Name", "trade_created_interval_count").split("@")
    print("index_names", index_names)
    platName = request.GET.get("platName", "TAOBAO")
    print("platName is:", platName)
    tenants = request.GET.get("tenantName", "sjyj").split("@")
    print("tenants is:", tenants)
    dataType = request.GET.get("dataType")
    print("dataType is:", dataType)
    index_number = {}
    #最后的结果{tenant1:[指标1数值,指标2数值...],}
    #获取指标，将指标连接在一起
    index_names_str = ''
    for index_name in index_names:
        index_names_str = index_names_str + index_name + ','
    index_names_str = index_names_str.strip(',')
    print("index_names_str is:", index_names_str)
    tenant_names_str = ''
    for tenant_name in tenants:
        tenant_names_str = tenant_names_str + "'" + tenant_name + "'" + ','
    tenant_names_str = tenant_names_str.strip(',')
    print("tenant_names_str is:", tenant_names_str)
    sql = 'select tenant,{index_names} from {dataType}_daily_monitor_data where plat_code = "{plat_code}" and start_date = "{start_date}" and end_date = "{end_date}" and tenant in ({tenants}) group by tenant;'.format(index_names=index_names_str, dataType=dataType, plat_code=platName, start_date=beginDate, end_date=endDate, tenants=tenant_names_str)
    print(sql)
    try:
        ConnMySql_instance = ConnMySql(read_config.DATABASE2, sql)
        result = list(ConnMySql_instance.get_data())
        tenant = [r[0] for r in result]
        index_result = [r[1:11] for r in result]
        for i in range(len(tenant)):
            key = tenant[i]
            # tuple转list
            value = list(index_result[i])
            # 字符转数值
            value = [int(x) for x in value]
            index_number[key] = value
    except Exception as e:
        print('get_module_number ERROR: ' + str(e))
    return JsonResponse(index_number)


def monitor_index(request):
    """
    监控数据网页
    :param request:
    :return:
    """
    return render(request, 'monitor/monitor_statistics_date.html')
