from django import forms
from .models import InterfaceGroup


class InterfaceGroupForm(forms.Form):
    category = (
        ('0', "主动营销"),
        ('1', "数据平台"),
        ('2', "事件营销"),
        ('3', "互动赢家"),
    )
    interface_group_name = forms.CharField(label="接口组名称", max_length=128,
                                   widget=forms.TextInput(attrs={'class': 'form-control', "placeholder": "请输入接口组名称"}),
                                   required=True)
    interface_group_desc = forms.CharField(label="接口组描述", max_length=256,
                                   widget=forms.Textarea(attrs={'class': 'form-control', "placeholder": "请输入接口组描述"}),
                                   required=False)
    project_category = forms.ChoiceField(label='所属项目', choices=category, required=True)


class InterfaceForm(forms.Form):
    type = (
        ('get', "GET"),
        ('post', "POST"),
        ('put', "PUT"),
        ('delete', "DELETE"),
        ('head', "HEAD"),
        ('options', "OPTIONS"),
        ('trace', "TRACE"),
        ('patch', "PATCH"),
        ('connect', "CONNECT"),
    )
    status = (
        ('valid', '有效'),
        ('invalid', '无效'),
    )
    category = {}
    objs = InterfaceGroup.objects.all().iterator()
    for obj in objs:
        category[obj.interface_group_id] = obj.interface_group_name
    category_value = tuple(category.items())

    interface_name = forms.CharField(label="接口名称", max_length=128,
                                     widget=forms.TextInput(attrs={'class': 'form-control', "placeholder": "请输入接口名称"}),
                                     required=True)
    interface_category_id = forms.ChoiceField(label='所属接口组', required=True, choices=category_value)
    interface_desc = forms.CharField(label="接口描述", max_length=128,
                                     widget=forms.TextInput(attrs={'class': 'form-control', "placeholder": "请输入接口描述"}),
                                     required=False)
    interface_request_type = forms.ChoiceField(label='请求方式', choices=type, required=True)
    interface_address = forms.CharField(label="接口地址", max_length=128,
                                        widget=forms.TextInput(attrs={'class': 'form-control', "placeholder": "请输入接口地址"}),
                                        required=True)
    interface_status = forms.ChoiceField(label='接口状态', choices=status, required=True)
    interface_headers = forms.CharField(label="接口头信息", max_length=256,
                                        widget=forms.Textarea(
                                            attrs={'class': 'form-control', "placeholder": '{"Content-Type": "application/json"}'}),
                                        required=False)
    interface_parameters = forms.CharField(label="接口参数", max_length=256,
                                           widget=forms.Textarea(
                                               attrs={'class': 'form-control', "placeholder": '{"pageSize":5,"pageNum":1}'}),
                                           required=False)
    interface_body = forms.CharField(label="接口信息体", max_length=256,
                                     widget=forms.Textarea(
                                               attrs={'class': 'form-control', "placeholder": '{"code":"notEmpty2_test","name":"非空字符串校验器"}'}),
                                     required=False)


class InterfaceParamTemplateForm(forms.Form):
    template_name = forms.CharField(label="模版名称", max_length=128,
                                    widget=forms.TextInput(attrs={'class': 'form-control',
                                                                  "placeholder": "请输入模版名称"}),
                                    required=True)
    template_desc = forms.CharField(label="模版描述", max_length=256,
                                    widget=forms.Textarea(attrs={'class': 'form-control',
                                                                 "placeholder": "请输入模版描述"}),
                                    required=False)
    string = forms.CharField(label="string", max_length=128,
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                           "placeholder": "["", None, ~!@#$%^&*()_+]"}),
                             required=True)
    int = forms.CharField(label="int", max_length=128,
                          widget=forms.TextInput(attrs={'class': 'form-control', "placeholder": "0, 1"}),
                          required=True)
    number = forms.CharField(label="number", max_length=128,
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                           "placeholder": "12567890123456781234567123451234567, "
                                                                          "-12567890123456781234567123451234567, 0"}),
                             required=True)
    date = forms.CharField(label="date", max_length=128,
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         "placeholder": "0000-01-01, 1600-01-01, 2010-13-30, "
                                                                        "2010-02-30, not_date"}),
                           required=True)
    bool = forms.CharField(label="bool", max_length=128,
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         "placeholder": "not_bool, true, false"}),
                           required=True)
    decimal = forms.CharField(label="decimal", max_length=128,
                              widget=forms.TextInput(attrs={'class': 'form-control',
                                                            "placeholder": "not_decimal, "
                                                                           "12567890123456781234567123451234567.88, "
                                                                           "-12345678912345678912345678901234567.50, "
                                                                           "0.00"}),
                              required=True)


class TestSuitForm(forms.Form):
    test_suit_name = forms.CharField(label="测试集名称", max_length=128,
                                     widget=forms.TextInput(attrs={'class': 'form-control',
                                                                   "placeholder": "请输入测试集名称"}),
                                     required=True)




