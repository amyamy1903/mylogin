from django.core.paginator import Paginator
from django.forms import model_to_dict
from django.shortcuts import render, redirect, HttpResponse, reverse
from django.http import HttpResponse, JsonResponse
import json
from commons.UtilScript import ConnMySql
from conf import read_config
import datetime
from django.views import View
from django.core import serializers


class LocustView(View):

    def get(self, request):
        return render(request, 'performance/performance_base.html', {'message': "我在测试"})

    def post(self, request):
        pass