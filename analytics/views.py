from django.shortcuts import render

def general_analytics(request):
    """Общая аналитика"""
    return render(request, 'analytics/general.html')