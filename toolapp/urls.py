from django.conf.urls import url
from django.contrib import admin
from toolapp import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.tool, name='tool'),
    url(r'^dataFactory', views.data_factory, name='interface'),
]