from django.conf.urls import url

from carts.views import CartsView, CartsSelectAllView, CartsSimpleView

urlpatterns = [
    # 购物车
    url(r'carts/$', CartsView.as_view(), name='cart'),
    # 全选购物车
    url(r'carts/selection/$', CartsSelectAllView.as_view()),
    # 是展示简单购物车
    url(r'carts/simple/$', CartsSimpleView.as_view()),
    ]