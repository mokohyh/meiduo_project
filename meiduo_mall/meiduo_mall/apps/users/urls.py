from django.conf.urls import url
from .views import Register, ChangePasswordView,DefaultAddressView,UpdateTitleAddressView,UpdateDestroyAddressView,AddressView,CreateAddressView,VerifyEmailView,UsernameCountView,MobileCountView,LoginView,LoginOutView,UserInfoView,EmailsView, \
    UserBrowseHistory

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
    url(r'^addresses/(?P<address4_id>\d+)/$', UpdateDestroyAddressView.as_view(), name='upate'),
    # 设置默认地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', DefaultAddressView.as_view(), name='default'),
    # 修改地址标题
    url(r'^addresses/(?P<address_id>\d+)/title/$', UpdateTitleAddressView.as_view(), name='updatetitle'),
    # 修改密码
    url(r'^info/updatepwd/$', ChangePasswordView.as_view(), name='updatepwd'),
    # 保存用户浏览记录
    url(r'^browse_histories/$', UserBrowseHistory.as_view(), name='history'),

]