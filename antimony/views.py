from django.shortcuts import render
from django.http import JsonResponse
from .calculations import calculate_smelting
import json


def calculator(request):
    """Главная страница калькулятора"""
    context = {
        'page_title': 'Калькулятор плавки антимоната натрия',
        'breadcrumbs': [
            {'title': 'Главная', 'url': 'core:home'},
            {'title': 'Калькулятор антимоната', 'url': None}
        ],
    }
    return render(request, 'antimony/calculator.html', context)


def calculate(request):
    """API для расчета (AJAX)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            results = calculate_smelting(data)
            return JsonResponse(results)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})