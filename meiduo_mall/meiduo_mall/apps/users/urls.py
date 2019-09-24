from django.conf.urls import url
from .views import Register,UpdateDestroyAddressView,AddressView,CreateAddressView,VerifyEmailView,UsernameCountView,MobileCountView,LoginView,LoginOutView,UserInfoView,EmailsView

urlpatterns = [
    url(r'^register/$', Register.as_view(),name='register'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$',UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',MobileCountView.as_view()),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LoginOutView.as_view(), name='logout'),
    url(r'^emails/$', EmailsView.as_view(), name='emails'),
    url(r'^emails/verification/$', VerifyEmailView.as_view(), name='verification'), url(r'^info/$', UserInfoView.as_view(), name='info'),
    # 收货地址展示
    url(r'^info/address/$', AddressView.as_view(), name='addresses'),
    # 添加地址
    url(r'^addresses/create/$', CreateAddressView.as_view(), name='address'),
    # 修改和删除地址
    url(r'^addresses/(?P<address_id>\d+)/$', UpdateDestroyAddressView.as_view(), name='upate'),


]