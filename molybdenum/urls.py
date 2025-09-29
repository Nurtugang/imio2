from django.urls import path
from . import views

app_name = 'molybdenum'

urlpatterns = [
    # Главная страница модуля
    path('', views.dashboard, name='dashboard'),
    
    # Калькуляторы
    path('leaching-calculator/', views.leaching_calculator, name='leaching_calculator'),
    path('sorption-calculator/', views.sorption_calculator, name='sorption_calculator'),
    
    # Списки тестов
    path('leaching-tests/', views.leaching_tests, name='leaching_tests'),
    path('sorption-tests/', views.sorption_tests, name='sorption_tests'),
    
    # Детали тестов (API)
    path('leaching-test/<int:test_id>/', views.leaching_test_detail, name='leaching_test_detail'),
    path('sorption-test/<int:test_id>/', views.sorption_test_detail, name='sorption_test_detail'),
    
    # Аналитика
    path('analytics/', views.analytics, name='analytics'),
]