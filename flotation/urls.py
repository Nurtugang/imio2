from django.urls import path
from . import views

app_name = 'flotation'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reagents/', views.reagents, name='reagents'),
    
    path('tests/', views.tests, name='tests'),
    path('test-detail/<int:test_id>/', views.test_detail, name='test_detail'),
    
    path('analytics/', views.analytics, name='analytics'),
    path('calculator/', views.calculator, name='calculator'),
]