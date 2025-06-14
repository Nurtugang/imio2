from django.shortcuts import render

def calculators_list(request):
    """Список калькуляторов"""
    return render(request, 'calculators/list.html')