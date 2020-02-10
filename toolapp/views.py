from django.shortcuts import render
from commons.UtilScript import ConnMySql
from conf import read_config
import datetime

# Create your views here.


def tool(request):
    return render(request, 'tool/index.html', {'message': "我在测试"})


def data_factory(request):
    return render(request, 'tool/data_factory.html', {'message': "我在测试"})

