from django.shortcuts import render
from .models import Reagent, FlotationTest, FlotationProduct
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json


def tests(request):
    """Список тестов"""
    # Получаем все тесты с фильтрацией
    tests_queryset = FlotationTest.objects.prefetch_related('products').all()
    
    # Фильтры
    configuration = request.GET.get('configuration')
    min_extraction = request.GET.get('min_extraction')
    max_extraction = request.GET.get('max_extraction')
    is_microflotation = request.GET.get('microflotation')
    
    if configuration:
        tests_queryset = tests_queryset.filter(configuration__icontains=configuration)
    if is_microflotation:
        tests_queryset = tests_queryset.filter(is_microflotation=True)
    
    # Фильтрация по извлечению - нужно делать в Python, так как это property
    filtered_tests = []
    extraction_values = []
    best_test = None
    best_extraction = 0
    
    for test in tests_queryset:
        extraction = test.extraction
        
        # Применяем фильтры извлечения
        if min_extraction and extraction < float(min_extraction):
            continue
        if max_extraction and extraction > float(max_extraction):
            continue
            
        filtered_tests.append(test)
        extraction_values.append(extraction)
        
        if extraction > best_extraction:
            best_extraction = extraction
            best_test = test
    
    avg_extraction = sum(extraction_values) / len(extraction_values) if extraction_values else 0
    
    # Статистика
    test_stats = {
        'total': FlotationTest.objects.count(),
        'microflotation': FlotationTest.objects.filter(is_microflotation=True).count(),
        'avg_extraction': avg_extraction,
        'best_test': best_test
    }
    
    context = {
        'tests': filtered_tests,
        'test_stats': test_stats,
        'configurations': FlotationTest.objects.values_list('configuration', flat=True).distinct(),
        'filters': {
            'configuration': configuration,
            'min_extraction': min_extraction,
            'max_extraction': max_extraction,
            'is_microflotation': is_microflotation,
        }
    }
    return render(request, 'flotation/tests.html', context)

def analytics(request):
    """Аналитика флотации"""
    # Получаем все тесты с продуктами
    all_tests = FlotationTest.objects.prefetch_related('products').all()
    
    # Группируем по конфигурациям
    config_stats = {}
    for test in all_tests:
        config = test.configuration or 'Без конфигурации'
        if config not in config_stats:
            config_stats[config] = {'extractions': [], 'count': 0}
        
        extraction = test.extraction
        config_stats[config]['extractions'].append(extraction)
        config_stats[config]['count'] += 1
    
    # Рассчитываем средние значения
    extraction_by_config = []
    for config, data in config_stats.items():
        avg_extraction = sum(data['extractions']) / len(data['extractions']) if data['extractions'] else 0
        extraction_by_config.append({
            'configuration': config,
            'avg_extraction': avg_extraction,
            'count': data['count']
        })
    
    # Сортируем по среднему извлечению
    extraction_by_config.sort(key=lambda x: x['avg_extraction'], reverse=True)
    
    # Успешные тесты (извлечение >= 85%)
    successful_tests_count = sum(1 for test in all_tests if test.extraction >= 85)
    
    # Последние 50 тестов для тренда
    recent_tests = list(FlotationTest.objects.prefetch_related('products').order_by('-number')[:50])
    recent_tests.reverse()
    
    context = {
        'extraction_by_config': extraction_by_config,
        'successful_tests_count': successful_tests_count,
        'recent_tests': recent_tests,
        'avg_extraction_trend': [test.extraction for test in recent_tests],
        'test_numbers': [test.number for test in recent_tests]
    }
    return render(request, 'flotation/analytics.html', context)

# Остальные функции остаются без изменений...
def tests(request):
    """Список тестов"""
    tests_queryset = FlotationTest.objects.prefetch_related('products').all()
    
    # Фильтры
    configuration = request.GET.get('configuration')
    min_extraction = request.GET.get('min_extraction')
    max_extraction = request.GET.get('max_extraction')
    is_microflotation = request.GET.get('microflotation')
    
    if configuration:
        tests_queryset = tests_queryset.filter(configuration__icontains=configuration)
    if is_microflotation:
        tests_queryset = tests_queryset.filter(is_microflotation=True)
    
    # Фильтрация по извлечению
    filtered_tests = []
    extraction_values = []
    best_test = None
    best_extraction = 0
    
    for test in tests_queryset:
        extraction = test.extraction
        
        if min_extraction and extraction < float(min_extraction):
            continue
        if max_extraction and extraction > float(max_extraction):
            continue
            
        filtered_tests.append(test)
        extraction_values.append(extraction)
        
        if extraction > best_extraction:
            best_extraction = extraction
            best_test = test
    
    avg_extraction = sum(extraction_values) / len(extraction_values) if extraction_values else 0
    
    test_stats = {
        'total': FlotationTest.objects.count(),
        'microflotation': FlotationTest.objects.filter(is_microflotation=True).count(),
        'avg_extraction': avg_extraction,
        'best_test': best_test
    }
    
    context = {
        'tests': filtered_tests,
        'test_stats': test_stats,
        'configurations': FlotationTest.objects.values_list('configuration', flat=True).distinct(),
        'filters': {
            'configuration': configuration,
            'min_extraction': min_extraction,
            'max_extraction': max_extraction,
            'is_microflotation': is_microflotation,
        }
    }
    return render(request, 'flotation/tests.html', context)


def reagents(request):
    """Управление реагентами"""
    # Получаем все реагенты
    all_reagents = Reagent.objects.all()
    
    # Статистика по типам
    reagent_stats = {
        'total': all_reagents.count(),
        'collectors': all_reagents.filter(type='collector').count(),
        'frothers': all_reagents.filter(type='frother').count(),
        'activators': all_reagents.filter(type='activator').count(),
        'experimental': all_reagents.filter(type='experimental').count(),
    }
    
    # Лучшие реагенты по эффективности
    top_reagents = all_reagents.filter(max_extraction__isnull=False).order_by('-max_extraction')[:3]
    
    context = {
        'reagents': all_reagents,
        'reagent_stats': reagent_stats,
        'top_reagents': top_reagents,
        'reagent_types': [
            {'value': 'all', 'label': 'Все'},
            {'value': 'collector', 'label': 'Собиратели'},
            {'value': 'frother', 'label': 'Пенообразователи'},
            {'value': 'activator', 'label': 'Активаторы'},
            {'value': 'experimental', 'label': 'MP Серия'},
        ]
    }
    return render(request, 'flotation/reagents.html', context)



def calculator(request):
    """Калькулятор флотации"""
    if request.method == 'POST':
        try:
            # Получаем данные из AJAX запроса
            data = json.loads(request.body)
            
            # Производим расчеты
            results = calculate_flotation_results(data)
            
            # Если есть флаг сохранения - создаем тест
            if data.get('save_test', False):
                test = save_flotation_test(data, results)
                results['test_id'] = test.id
                results['test_number'] = test.number
                results['saved'] = True
            
            return JsonResponse({
                'success': True,
                'results': results
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # GET запрос - показываем форму
    context = {
        'page_title': 'Калькулятор флотации',
        'breadcrumbs': [
            {'title': 'Главная', 'url': 'core:home'},
            {'title': 'Флотация', 'url': 'flotation:dashboard'},
            {'title': 'Калькулятор', 'url': None}
        ]
    }
    return render(request, 'flotation/calculator.html', context)


def calculate_flotation_results(data):
    """Расчет показателей флотации"""
    
    # Извлекаем данные продуктов
    products = {
        'final_concentrate': data.get('final_concentrate', {}),
        'tails': data.get('tails', {}),
        'cleaner_tails': data.get('cleaner_tails', {}),
        'control_concentrate': data.get('control_concentrate', {})
    }
    
    # Рассчитываем Au в каждом продукте
    au_content = {}
    total_mass = 0
    total_au = 0
    
    for product_type, product_data in products.items():
        mass = float(product_data.get('mass', 0))
        grade = float(product_data.get('grade', 0))
        au = mass * grade  # Au (мкг) = масса (г) × содержание (г/т)
        
        au_content[product_type] = {
            'mass': mass,
            'grade': grade,
            'au': au
        }
        
        total_mass += mass
        total_au += au
    
    # Основные расчеты
    results = {}
    
    # 1. Расчетное исходное содержание
    results['calculated_initial_grade'] = float(data.get('calculated_initial_grade', 0))
    
    # 2. Выход концентрата
    final_mass = au_content['final_concentrate']['mass']
    results['concentrate_yield'] = (final_mass / total_mass * 100) if total_mass > 0 else 0
    
    # 3. Извлечение (все кроме отвальных хвостов)
    useful_au = (au_content['final_concentrate']['au'] + 
                 au_content['cleaner_tails']['au'] + 
                 au_content['control_concentrate']['au'])
    results['extraction'] = (useful_au / total_au * 100) if total_au > 0 else 0
    
    # 4. Эффективность обогащения
    initial_grade = float(data.get('initial_grade_analysis', 0))
    extraction = results['extraction']
    yield_val = results['concentrate_yield']
    
    if initial_grade != 100:
        results['efficiency'] = ((extraction - yield_val) / (100 - initial_grade)) * 100
    else:
        results['efficiency'] = 0
    
    # 5. Материальные балансы
    results['material_balance'] = {
        'total_mass': total_mass,
        'total_au': total_au,
        'products': au_content
    }
    
    # 6. Проверки валидности
    results['validations'] = validate_results(data, results)
    
    return results


def validate_results(data, results):
    """Валидация результатов расчета"""
    validations = []
    
    # Проверка материального баланса
    total_mass = results['material_balance']['total_mass']
    if total_mass < 100:
        validations.append({
            'type': 'warning',
            'message': f'Малая общая масса пробы: {total_mass:.1f}г'
        })
    
    # Проверка извлечения
    extraction = results['extraction']
    if extraction > 100:
        validations.append({
            'type': 'error',
            'message': f'Извлечение больше 100%: {extraction:.1f}%'
        })
    elif extraction > 95:
        validations.append({
            'type': 'success',
            'message': f'Отличное извлечение: {extraction:.1f}%'
        })
    
    # Проверка эффективности
    efficiency = results['efficiency']
    if efficiency < 0:
        validations.append({
            'type': 'warning',
            'message': f'Отрицательная эффективность: {efficiency:.1f}%'
        })
    
    return validations


@transaction.atomic
def save_flotation_test(data, results):
    """Сохранение теста в базу данных"""
    
    # Генерируем номер теста
    last_test = FlotationTest.objects.order_by('-number').first()
    test_number = (last_test.number + 1) if last_test else 1
    
    # Создаем тест
    test = FlotationTest.objects.create(
        number=test_number,
        initial_grade_analysis=float(data.get('initial_grade_analysis', 0)),
        calculated_initial_grade=results['calculated_initial_grade'],
        reagent_regime=data.get('reagent_regime', ''),
        is_microflotation=data.get('is_microflotation', False),
        configuration=data.get('configuration', '')
    )
    
    # Создаем продукты флотации
    product_types = {
        'final_concentrate': 'final_concentrate',
        'tails': 'tails',
        'cleaner_tails': 'cleaner_tails',
        'control_concentrate': 'control_concentrate'
    }
    
    product_names = {
        'final_concentrate': 'Финальный концентрат',
        'tails': 'Отвальные хвосты',
        'cleaner_tails': 'Хвосты перечистки',
        'control_concentrate': 'Концентрат контрольной'
    }
    
    for product_key, product_type in product_types.items():
        product_data = results['material_balance']['products'][product_key]
        
        FlotationProduct.objects.create(
            test=test,
            name=product_names[product_key],
            product_type=product_type,
            mass=product_data['mass'],
            grade=product_data['grade'],
            au_content=product_data['au']
        )
    
    return test


def dashboard(request):
    """Дашборд флотации с графиками"""
    # Статистика тестов
    tests_stats = {
        'total': FlotationTest.objects.count(),
        'microflotation': FlotationTest.objects.filter(is_microflotation=True).count(),
        'standard': FlotationTest.objects.filter(is_microflotation=False).count(),
    }
    
    # Получаем все тесты для расчета статистики
    all_tests = FlotationTest.objects.prefetch_related('products').all()
    
    # Рассчитываем статистику извлечения
    extraction_values = []
    best_test = None
    best_extraction = 0
    
    for test in all_tests:
        extraction = test.extraction
        if extraction:
            extraction_values.append(extraction)
            if extraction > best_extraction:
                best_extraction = extraction
                best_test = test
    
    avg_extraction = sum(extraction_values) / len(extraction_values) if extraction_values else 0
    
    # ДАННЫЕ ДЛЯ ГРАФИКА ТРЕНДА ИЗВЛЕЧЕНИЯ
    recent_tests = FlotationTest.objects.prefetch_related('products').order_by('-number')[:20]
    recent_tests_list = list(recent_tests)
    recent_tests_list.reverse()  # Переворачиваем для правильного порядка
    
    trend_data = {
        'labels': [f"Тест {test.number}" for test in recent_tests_list],
        'data': [test.extraction for test in recent_tests_list],
        'test_numbers': [test.number for test in recent_tests_list]
    }
    
    # ДАННЫЕ ДЛЯ КРУГОВОЙ ДИАГРАММЫ КОНФИГУРАЦИЙ
    config_stats = {}
    for test in all_tests:
        # Определяем тип конфигурации
        if test.is_microflotation:
            config_type = 'Микрофлотация'
        elif test.configuration:
            config_type = test.configuration
        else:
            config_type = 'Базовая'
        
        if config_type not in config_stats:
            config_stats[config_type] = 0
        config_stats[config_type] += 1
    
    # Подготавливаем данные для Chart.js
    pie_data = {
        'labels': list(config_stats.keys()),
        'data': list(config_stats.values()),
        'colors': [
            '#3B82F6',  # Синий для микрофлотации
            '#10B981',  # Зеленый для конфигураций
            '#F59E0B',  # Желтый для базовой
            '#EF4444',  # Красный для других
            '#8B5CF6',  # Фиолетовый
            '#06B6D4'   # Голубой
        ]
    }
    
    # Последние тесты (5 штук)
    recent_tests_display = FlotationTest.objects.prefetch_related('products').order_by('-number')[:5]
    
    # Топ реагенты
    top_reagents = []
    try:
        top_reagents = Reagent.objects.filter(
            max_extraction__isnull=False
        ).order_by('-max_extraction')[:5]
    except:
        pass
    
    # Общая статистика реагентов
    reagents_count = 0
    try:
        reagents_count = Reagent.objects.count()
    except:
        pass
    
    context = {
        # Основная статистика
        'total_tests': tests_stats['total'],
        'avg_extraction': avg_extraction,
        'best_extraction': best_extraction,
        'total_reagents': reagents_count,
        
        # Детальные данные
        'recent_tests': recent_tests_display,
        'top_reagents': top_reagents,
        'best_test': best_test,
        
        # Статистика по типам
        'microflotation_count': tests_stats['microflotation'],
        'standard_count': tests_stats['standard'],
        
        # ДАННЫЕ ДЛЯ ГРАФИКОВ
        'trend_chart_data': json.dumps(trend_data),
        'pie_chart_data': json.dumps(pie_data),
        
        # Метаданные для шаблона
        'page_title': 'Дашборд флотации',
        'breadcrumbs': [
            {'title': 'Главная', 'url': 'core:home'},
            {'title': 'Флотация', 'url': 'flotation:dashboard'},
            {'title': 'Дашборд', 'url': None}
        ]
    }
    return render(request, 'flotation/dashboard.html', context)