from django.conf.urls import url

from carts.views import CartsView

urlpatterns = [
    url(r'carts/$', CartsView.as_view(), name='cart')
    ]