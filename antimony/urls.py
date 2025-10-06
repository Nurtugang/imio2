from django.urls import path
from . import views

app_name = 'antimony'

urlpatterns = [
    path('', views.calculator, name='calculator'),
    path('calculate/', views.calculate, name='calculate'),
]