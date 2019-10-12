from django.conf.urls import url

from orders.views import OrderSettlementView, OrderCommitView, OrderSuccessView

urlpatterns = [
    # 订单信息
    url(r'^orders/settlement/$', OrderSettlementView.as_view(), name='info'),
    # 提交订单
    url(r'^orders/commit/$', OrderCommitView.as_view(), name='commit'),
    # 提交成功页面
    url(r'^orders/success/$', OrderSuccessView.as_view(), name='success'),

]