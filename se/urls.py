from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.search, name='search'),
    url(r'^(?P<rest_id>.+)/$', views.detail, name='detail'),
]
