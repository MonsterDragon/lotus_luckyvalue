from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^statistics/value/$', views.LuckyView.as_view(), name='value'),
]