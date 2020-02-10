from django.db import models
from django.utils import timezone
import datetime


class InterfaceGroup(models.Model):
    category = (
        ('0', "主动营销"),
        ('1', "数据平台"),
        ('2', "事件营销"),
        ('3', "互动赢家"),
    )
    interface_group_id = models.AutoField(verbose_name="测试用例编号", primary_key=True)
    interface_group_name = models.CharField(max_length=128, unique=True)
    interface_group_desc = models.CharField(max_length=256)
    project_category = models.IntegerField(choices=category)
    interface_group_creator = models.CharField(max_length=128)
    # interface_group_create_time = models.DateTimeField(verbose_name='创建时间',
    #                                                    default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #interface_group_update_time = models.DateTimeField('更新时间', auto_now=True)
    interface_group_create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    interface_group_update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')


class Interface(models.Model):
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
    interface_id = models.AutoField(verbose_name="测试用例编号", primary_key=True)
    interface_name = models.CharField(verbose_name="接口名称", max_length=128)
    #interface_category = models.CharField(verbose_name='所属接口组', max_length=128)
    interface_category = models.ForeignKey(to=InterfaceGroup, to_field="interface_group_id", verbose_name='所属接口组', on_delete=models.CASCADE)
    interface_desc = models.CharField(verbose_name="接口描述", max_length=256)
    interface_request_type = models.CharField(verbose_name='请求方式', choices=type, max_length=20)
    interface_address = models.CharField(verbose_name="接口地址", max_length=128)
    interface_status = models.CharField(verbose_name='接口状态', choices=status, max_length=20)
    interface_headers = models.CharField(verbose_name="接口头信息", max_length=256)
    interface_parameters = models.CharField(verbose_name="接口参数", max_length=256)
    interface_body = models.CharField(verbose_name="接口信息体", max_length=256)
    # interface_create_time = models.DateTimeField(verbose_name='创建时间',
    #                                              default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    interface_creator = models.CharField(verbose_name="创建用户", max_length=128)
    interface_create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    interface_update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.interface_name

    class Meta:
        unique_together = (("interface_name", "interface_category", "interface_address"),)
        verbose_name_plural = u"接口总表"


class InterfaceParamTemplate(models.Model):
    interface_param_template_id = models.AutoField(verbose_name="测试用例编号", primary_key=True)
    template_name = models.CharField(verbose_name="template_name", max_length=128)
    template_desc = models.CharField(verbose_name="tempalte_desc", max_length=256)
    string = models.CharField(verbose_name="string", max_length=128)
    int = models.CharField(verbose_name="int", max_length=128)
    number = models.CharField(verbose_name="number", max_length=128)
    date = models.CharField(verbose_name="date", max_length=128)
    bool = models.CharField(verbose_name="bool", max_length=128)
    decimal = models.CharField(verbose_name="decimal", max_length=128)
    creator = models.CharField(verbose_name="创建用户", max_length=128)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')


#接口测试平台，就不可能是简单的接口请求和检测；还需要接口文档管理，测试用例管理，测试用例集管理，测试执行调度，结果展示和统计，错误预警等功能的结合
class TestCase(models.Model):
    test_case_id = models.AutoField(verbose_name="测试用例编号", primary_key=True)
    #外键字段建立在多的一方
    interface = models.ForeignKey(Interface, related_name='interface_test_case', on_delete=models.CASCADE)
    test_case_name = models.CharField(verbose_name="用例名称", max_length=128)
    test_case_data = models.CharField(verbose_name="用例数据", max_length=128)
    creator = models.CharField(verbose_name="创建用户", max_length=128)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        unique_together = (("test_case_name", "interface"),)
        verbose_name_plural = u"测试用例总表"


class TestCaseSuit(models.Model):
    test_suit_id = models.AutoField(verbose_name="测试集编号", primary_key=True)
    test_suit_name = models.CharField(verbose_name="用例集名称", max_length=128)
    param_template = models.CharField(verbose_name="参数模版", max_length=128, default=None)#需要想一想到底在哪一层，感觉应该在用例层，用例可以有模版也可以没有模版，也可以有多个模版，还要不要模版。。不要这么复杂了
    #ManyToManyField可以建在两个模型中的任意一个，自动创建第三张表
    test_case = models.ManyToManyField(to=TestCase)
    interface = models.ManyToManyField(to=Interface)
    creator = models.CharField(verbose_name="创建用户", max_length=128)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.test_suit_name


class TestPlan(models.Model):
    test_plan_id = models.AutoField(verbose_name="测试计划编号", primary_key=True)
    test_plan_name = models.CharField(verbose_name="测试计划名称", max_length=128)
    test_plan_desc = models.CharField(verbose_name="测试计划描述", max_length=128)
    test_case_suit = models.ManyToManyField(to=TestCaseSuit)
    creator = models.CharField(verbose_name="创建用户", max_length=128)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.test_plan_name


# class ThreeRelation(models.Model):
#     relation_id = models.AutoField(verbose_name="关系ID", primary_key=True)
#     interface_id = models.CharField(verbose_name="测试用例编号", max_length=128)
#     interface_name = models.CharField(verbose_name="接口名称", max_length=128)
#     test_case_id = models.CharField(verbose_name="测试用例编号", max_length=128)
#     test_case_name = models.CharField(verbose_name="用例名称", max_length=128)
#     test_suit_id = models.CharField(verbose_name="测试集编号", max_length=128)
#     test_suit_name = models.CharField(verbose_name="用例集名称", max_length=128)


# class TestPlanTestCaseSuitRelationShip(models.Model):
#     status = (
#         ('executing', '执行中'),
#         ('success', '执行成功'),
#         ('failed', '执行失败'),
#         ('suspend', '执行中断'),
#     )
#     test_plan_test_suit_relation_id = models.AutoField(verbose_name="测试集和测试计划关系id", primary_key=True)
#     test_plan_name = models.ForeignKey(TestPlan, on_delete=models.CASCADE)
#     test_suit_name = models.ForeignKey(TestCaseSuit, on_delete=models.CASCADE)
#     date_joined = models.DateField()  # 测试集合被加入测试计划的时间
#     execute_count = models.IntegerField(verbose_name="执行次数")
#     execute_status = models.CharField(verbose_name="执行状态", max_length=128)
#     creator = models.CharField(verbose_name="创建用户", max_length=128)
#     create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
#     update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')


"""
接口
用例
用例集
测试计划
一对多关系：
一个接口对应多个用例，一个用例只有一个接口
多对多关系：
一个用例集对应多个接口，一个接口可以对应多个用例集
一个用例集对应多个用例，一个用例对应可以对应多个用例集
一个用例集对对应多个测试计划，一个测试计划可以有多个用例集

测试计划--测试集--测试用例--接口
"""

#接口-用例集-用例