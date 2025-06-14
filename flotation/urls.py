from django.urls import path
from . import views

app_name = 'flotation'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reagents/', views.reagents, name='reagents'),
    path('tests/', views.tests, name='tests'),
    path('analytics/', views.analytics, name='analytics'),
    path('calculator/', views.calculator, name='calculator'),
]