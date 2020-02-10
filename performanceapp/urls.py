from django.conf.urls import url
from django.contrib import admin
from performanceapp import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.LocustView.as_view(), name='performance'),
    #url(r'^interfaceGroup', views.interface_group, name='interface'),
    #url(r'^edit-project/(\d+)', views.interface_edit_project, name='interface'),
]