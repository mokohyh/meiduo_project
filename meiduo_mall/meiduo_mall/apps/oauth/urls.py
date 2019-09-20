from django.conf.urls import url
from .views import QQAuthURLView, QQAuthUserView

urlpatterns = [
    url(r'^qq/login/$', QQAuthURLView.as_view()),
    url(r'^oauth_callback/$', QQAuthUserView.as_view()),
]
