from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.general_analytics, name='general'),
]