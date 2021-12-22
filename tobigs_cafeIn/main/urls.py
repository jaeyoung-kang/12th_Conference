from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('result', views.result, name='result'),
    path('status', views.status, name='status'),
    path('getImg', views.getImg, name='getImg')
]