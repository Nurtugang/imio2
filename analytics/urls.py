from django.urls import path
from . import views
from flotation.views import analytics
app_name = 'analytics'

urlpatterns = [
    path('', analytics, name='general'),
]