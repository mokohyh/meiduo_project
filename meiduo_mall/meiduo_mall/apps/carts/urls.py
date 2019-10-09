from django.conf.urls import url

from carts.views import CartsView, CartsSelectAllView

urlpatterns = [
    # 购物车
    url(r'carts/$', CartsView.as_view(), name='cart'),
    # 全选购物车
    url(r'carts/selection/$', CartsSelectAllView.as_view()),
    ]