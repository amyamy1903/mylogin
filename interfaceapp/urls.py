from django.conf.urls import url
from django.contrib import admin
from interfaceapp import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.interface, name='interface'),
    url(r'^interfaceGroup', views.interface_group, name='interface'),
    url(r'^addInterfaceGroup', views.add_interface_group, name='interface'),
    url(r'^getInterfaceGroup', views.get_interface_group, name='interface'),
    #url(r'^edit-project/(\d+)', views.interface_edit_project, name='interface'),
    url(r'^editInterfaceGroup', views.edit_interface_group, name='interface'),
    url(r'^delInterfaceGroup', views.del_interface_group, name='interface'),
    url(r'^getProjectCategory', views.get_project_category, name='interface'),
    url(r'^getAllInterfaceGroup', views.get_all_interface_group, name='interface'),
    url(r'^interfaceList', views.interface_list, name='interface'),
    url(r'^getInterfaceList', views.get_interface_list, name='interface'),
    url(r'^addInterfaces$', views.add_interface, name='interface'),
    url(r'^editInterfaces', views.edit_interface, name='interface'),
    url(r'^delInterfaces', views.del_interface, name='interface'),
    url(r'^getTestCase$', views.get_test_case, name='interface'),
    url(r'^getTestCaseReport', views.get_test_case_report, name='interface'),
    url(r'^allTemplate', views.all_template, name='interface'),
    url(r'^template', views.TestCaseParamTemplate.as_view(), name='interface'),
    url(r'^addInterfaceParam', views.AddTestCaseParam.as_view(), name='interface'),
    url(r'^basicTestCase', views.BasicTestCase.as_view(), name='interface'),
    url(r'^allBasicTestCase', views.all_basic_test_case, name='interface'),
    url(r'^allTestCaseSuit', views.all_test_suit, name='interface'),
    url(r'^testCaseSuit', views.TestCaseSuit.as_view(), name='interface'),
    url(r'autoAddInterfaceGroup', views.AutoAddInterfaceGroup.as_view(), name='interface'),
    url(r'autoAddInterfaces', views.AutoAddInterfaces.as_view(), name='interface'),
    url(r'exportTestCases', views.ExportTestCases.as_view(),name='interface'),
    #url(r'^basicTestCase/<int:id>/', views.BasicTestCase.as_view(), name='interface'),
]