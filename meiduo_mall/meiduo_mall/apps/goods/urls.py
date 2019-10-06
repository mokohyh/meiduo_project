from django.conf.urls import url

from goods.views import ListView, HotGoodsView

urlpatterns = [
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', ListView.as_view(), name='list'),
    url(r'^hot/(?P<category_id>\d+)/$', HotGoodsView.as_view(), name='hot'),

]