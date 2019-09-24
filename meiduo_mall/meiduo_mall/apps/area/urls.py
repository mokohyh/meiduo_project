from django.conf.urls import url

from area.views import AreasView


urlpatterns = [
    url(r'^areas/', AreasView.as_view(), name='areas')
]