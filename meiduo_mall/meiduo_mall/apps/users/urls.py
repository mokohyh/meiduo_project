from django.conf.urls import url
from .views import Register,UsernameCountView,MobileCountView,LoginView,LoginOutView,UserInfoView,EmailsView

urlpatterns = [
    url(r'^register/$', Register.as_view(),name='register'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$',UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',MobileCountView.as_view()),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LoginOutView.as_view(), name='logout'),
    url(r'^info/$', UserInfoView.as_view(), name='info'),
    url(r'^emails/$', EmailsView.as_view(), name='emails'),
]