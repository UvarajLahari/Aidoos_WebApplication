from django.conf.urls import url

from . import views

urlpatterns = [
	url('pre_index', views.pre_index, name='pre_index'),
    #url('index', views.index, name='index'),
    url('Parse_Data', views.Parse_Data, name='Parse_Data'),
    url('Parse_Json', views.Parse_Json, name='Parse_Json'),
    #url('AfterSearch', views.AfterSearch, name='AfterSearch'),
    #url('Upd_Index', views.Upd_Index, name='Upd_Index'),
]