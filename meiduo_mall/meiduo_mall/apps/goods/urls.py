from django.conf.urls import url

from goods.views import ListView, HotGoodsView, DetailView, DetailVisitView

urlpatterns = [
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', ListView.as_view(), name='list'),
    url(r'^hot/(?P<category_id>\d+)/$', HotGoodsView.as_view(), name='hot'),
    url(r'^detail/(?P<sku_id>\d+)/$', DetailView.as_view(), name='detail'),
    # 统计访问量
    url(r'^detail/visit/(?P<category_id>\d+)/$', DetailVisitView.as_view(), name='visit'),


]