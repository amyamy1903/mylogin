from django.conf.urls import url
from django.contrib import admin
from monitorapp import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.monitor_index, name='monitor'),
    url(r'get_tenant_name', views.get_tenant_name, name='monitor'),
    url(r'get_time_interval_and_plat_code', views.get_time_interval_and_plat_code, name='monitor'),
    url(r'get_date_tenant_monitor_statics', views.get_date_tenant_monitor_statics, name='monitor'),

]