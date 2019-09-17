from django.conf.urls import url
from .views import Register,UsernameCountView,MobileCountView

urlpatterns = [
    url(r'register/$', Register.as_view(),name='register'),
    url(r'usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$',UsernameCountView.as_view()),
    url(r'mobiles/(?P<mobile>1[3-9]\d{9})/count/$',MobileCountView.as_view())
]