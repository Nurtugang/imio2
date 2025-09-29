from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Avg, Max, Min, Count
import json

from .models import LeachingTest, LeachingProduct, SorptionTest
from .utils import (
    calculate_leaching_balance,
    calculate_sorption,
    validate_leaching_data,
    validate_sorption_data,
    calculate_kinetic_series
)


def dashboard(request):
    """Главная страница модуля переработки молибденита"""
    
    # Статистика по выщелачиванию
    leaching_tests = LeachingTest.objects.all()
    total_leaching = leaching_tests.count()
    
    # Рассчитываем среднее извлечение Mo
    leaching_extractions = []
    best_leaching = None
    best_leaching_extraction = 0
    
    for test in leaching_tests:
        extraction = test.mo_extraction_to_solution
        leaching_extractions.append(extraction)
        if extraction > best_leaching_extraction:
            best_leaching_extraction = extraction
            best_leaching = test
    
    avg_leaching_extraction = sum(leaching_extractions) / len(leaching_extractions) if leaching_extractions else 0
    
    # Статистика по сорбции
    sorption_tests = SorptionTest.objects.all()
    total_sorption = sorption_tests.count()
    
    sorption_stats = sorption_tests.aggregate(
        avg_extraction=Avg('mo_extraction'),
        max_extraction=Max('mo_extraction'),
        avg_capacity=Avg('sorption_capacity')
    )
    
    best_sorption = sorption_tests.order_by('-mo_extraction').first()
    
    # Последние тесты
    recent_leaching = leaching_tests.order_by('-date_conducted')[:5]
    recent_sorption = sorption_tests.order_by('-date_conducted')[:5]
    
    # Сравнение с/без кислорода
    with_oxygen = leaching_tests.filter(has_oxygen=True)
    without_oxygen = leaching_tests.filter(has_oxygen=False)
    
    oxygen_comparison = {
        'with_oxygen': {
            'count': with_oxygen.count(),
            'avg_extraction': sum([t.mo_extraction_to_solution for t in with_oxygen]) / with_oxygen.count() if with_oxygen.count() > 0 else 0
        },
        'without_oxygen': {
            'count': without_oxygen.count(),
            'avg_extraction': sum([t.mo_extraction_to_solution for t in without_oxygen]) / without_oxygen.count() if without_oxygen.count() > 0 else 0
        }
    }
    
    # Данные для графика тренда (последние 10 тестов выщелачивания)
    trend_tests = list(leaching_tests.order_by('number')[:10])
    trend_chart_data = {
        'labels': [f"Опыт {t.number}" for t in trend_tests],
        'mo_data': [t.mo_extraction_to_solution for t in trend_tests],
        'cu_data': [t.products.filter(product_type='solution').first().cu_extraction if t.products.filter(product_type='solution').exists() else 0 for t in trend_tests],
        'fe_data': [t.products.filter(product_type='solution').first().fe_extraction if t.products.filter(product_type='solution').exists() else 0 for t in trend_tests],
    }
    
    context = {
        # Общая статистика
        'total_leaching_tests': total_leaching,
        'total_sorption_tests': total_sorption,
        'avg_leaching_extraction': avg_leaching_extraction,
        'avg_sorption_extraction': sorption_stats['avg_extraction'] or 0,
        
        # Лучшие результаты
        'best_leaching_test': best_leaching,
        'best_leaching_extraction': best_leaching_extraction,
        'best_sorption_test': best_sorption,
        'best_sorption_extraction': sorption_stats['max_extraction'] or 0,
        
        # Последние тесты
        'recent_leaching_tests': recent_leaching,
        'recent_sorption_tests': recent_sorption,
        
        # Сравнения
        'oxygen_comparison': oxygen_comparison,
        
        # Графики
        'trend_chart_data': json.dumps(trend_chart_data),
    }
    
    return render(request, 'molybdenum/dashboard.html', context)


def leaching_calculator(request):
    """Калькулятор выщелачивания молибденита"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Валидация
            is_valid, errors = validate_leaching_data(data)
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'errors': errors
                })
            
            # Расчет баланса
            results = calculate_leaching_balance(data)
            
            # Сохранение теста (если указано)
            if data.get('save_test', False):
                test = save_leaching_test(data, results)
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
    
    # GET - показываем форму
    context = {
        'acid_types': LeachingTest._meta.get_field('acid_type').choices,
    }
    return render(request, 'molybdenum/leaching_calculator.html', context)


def sorption_calculator(request):
    """Калькулятор сорбции молибдена"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Валидация
            is_valid, errors = validate_sorption_data(data)
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'errors': errors
                })
            
            # Расчет сорбции
            results = calculate_sorption(data)
            
            # Сохранение теста (если указано)
            if data.get('save_test', False):
                test = save_sorption_test(data, results)
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
    
    # GET - показываем форму
    context = {
        'anionite_types': SorptionTest._meta.get_field('anionite_type').choices,
        'leaching_tests': LeachingTest.objects.all().order_by('-number'),
    }
    return render(request, 'molybdenum/sorption_calculator.html', context)


def leaching_tests(request):
    """Список всех тестов выщелачивания"""
    
    tests = LeachingTest.objects.prefetch_related('products').all()
    
    # Фильтрация
    acid_type = request.GET.get('acid_type')
    has_oxygen = request.GET.get('has_oxygen')
    min_extraction = request.GET.get('min_extraction')
    
    if acid_type:
        tests = tests.filter(acid_type=acid_type)
    
    if has_oxygen == '1':
        tests = tests.filter(has_oxygen=True)
    elif has_oxygen == '0':
        tests = tests.filter(has_oxygen=False)
    
    # Фильтрация по извлечению (в Python, т.к. это property)
    if min_extraction:
        min_val = float(min_extraction)
        tests = [t for t in tests if t.mo_extraction_to_solution >= min_val]
    else:
        tests = list(tests)
    
    # Статистика
    test_stats = {
        'total': len(tests),
        'with_oxygen': len([t for t in tests if t.has_oxygen]),
        'without_oxygen': len([t for t in tests if not t.has_oxygen]),
        'avg_extraction': sum([t.mo_extraction_to_solution for t in tests]) / len(tests) if tests else 0,
        'best_test': max(tests, key=lambda t: t.mo_extraction_to_solution) if tests else None,
    }
    
    context = {
        'tests': tests,
        'test_stats': test_stats,
        'acid_types': LeachingTest._meta.get_field('acid_type').choices,
        'filters': {
            'acid_type': acid_type,
            'has_oxygen': has_oxygen,
            'min_extraction': min_extraction,
        }
    }
    
    return render(request, 'molybdenum/leaching_tests.html', context)


def sorption_tests(request):
    """Список всех тестов сорбции"""
    
    tests = SorptionTest.objects.all()
    
    # Фильтрация
    anionite_type = request.GET.get('anionite_type')
    temperature = request.GET.get('temperature')
    
    if anionite_type:
        tests = tests.filter(anionite_type=anionite_type)
    
    if temperature:
        tests = tests.filter(temperature=float(temperature))
    
    # Статистика
    test_stats = tests.aggregate(
        total=Count('id'),
        avg_extraction=Avg('mo_extraction'),
        max_extraction=Max('mo_extraction'),
        avg_capacity=Avg('sorption_capacity')
    )
    
    # Сравнение анионитов
    anionite_comparison = {}
    for anionite_code, anionite_name in SorptionTest._meta.get_field('anionite_type').choices:
        anionite_tests = tests.filter(anionite_type=anionite_code)
        if anionite_tests.exists():
            anionite_comparison[anionite_name] = {
                'count': anionite_tests.count(),
                'avg_extraction': anionite_tests.aggregate(Avg('mo_extraction'))['mo_extraction__avg'],
                'max_extraction': anionite_tests.aggregate(Max('mo_extraction'))['mo_extraction__max'],
            }
    
    # Влияние температуры
    temperature_analysis = {}
    for temp in [20, 40, 60, 80]:
        temp_tests = tests.filter(temperature=temp)
        if temp_tests.exists():
            temperature_analysis[temp] = {
                'count': temp_tests.count(),
                'avg_extraction': temp_tests.aggregate(Avg('mo_extraction'))['mo_extraction__avg'],
                'avg_capacity': temp_tests.aggregate(Avg('sorption_capacity'))['sorption_capacity__avg'],
            }
    
    context = {
        'tests': tests,
        'test_stats': test_stats,
        'anionite_comparison': anionite_comparison,
        'temperature_analysis': temperature_analysis,
        'anionite_types': SorptionTest._meta.get_field('anionite_type').choices,
        'filters': {
            'anionite_type': anionite_type,
            'temperature': temperature,
        }
    }
    
    return render(request, 'molybdenum/sorption_tests.html', context)


def leaching_test_detail(request, test_id):
    """API для получения детальных данных теста выщелачивания"""
    
    try:
        test = get_object_or_404(LeachingTest, id=test_id)
        products = test.products.all()
        
        # Формируем данные продуктов
        products_data = {}
        for product in products:
            products_data[product.product_type] = {
                'mass_or_volume': float(product.mass_or_volume),
                'mo_content': float(product.mo_content),
                'cu_content': float(product.cu_content),
                'fe_content': float(product.fe_content),
                'si_content': float(product.si_content),
                'mo_grams': float(product.mo_grams),
                'cu_grams': float(product.cu_grams),
                'fe_grams': float(product.fe_grams),
                'si_grams': float(product.si_grams),
                'mo_extraction': float(product.mo_extraction),
                'cu_extraction': float(product.cu_extraction),
                'fe_extraction': float(product.fe_extraction),
                'si_extraction': float(product.si_extraction),
            }
        
        # Формируем ответ
        test_data = {
            'id': test.id,
            'number': test.number,
            'date_conducted': test.date_conducted.isoformat(),
            'concentrate_mass': float(test.concentrate_mass),
            'initial_mo': float(test.initial_mo),
            'initial_cu': float(test.initial_cu),
            'initial_fe': float(test.initial_fe),
            'initial_si': float(test.initial_si),
            'acid_type': test.get_acid_type_display(),
            'hno3_concentration': float(test.hno3_concentration) if test.hno3_concentration else None,
            'h2so4_concentration': float(test.h2so4_concentration) if test.h2so4_concentration else None,
            'solution_volume': float(test.solution_volume),
            'temperature': float(test.temperature),
            'duration': float(test.duration),
            'stirring_speed': float(test.stirring_speed),
            'has_oxygen': test.has_oxygen,
            'oxygen_flow': float(test.oxygen_flow) if test.oxygen_flow else None,
            'solid_liquid_ratio': test.solid_liquid_ratio,
            'mo_extraction_to_solution': test.mo_extraction_to_solution,
            'mo_extraction_to_cake': test.mo_extraction_to_cake,
            'products': products_data,
        }
        
        return JsonResponse({
            'success': True,
            'test': test_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def sorption_test_detail(request, test_id):
    """API для получения детальных данных теста сорбции"""
    
    try:
        test = get_object_or_404(SorptionTest, id=test_id)
        
        test_data = {
            'id': test.id,
            'number': test.number,
            'date_conducted': test.date_conducted.isoformat(),
            'leaching_test_number': test.leaching_test.number if test.leaching_test else None,
            'solution_volume': float(test.solution_volume),
            'initial_mo_concentration': float(test.initial_mo_concentration),
            'final_mo_concentration': float(test.final_mo_concentration),
            'h2so4_concentration': float(test.h2so4_concentration),
            'anionite_type': test.get_anionite_type_display(),
            'anionite_mass': float(test.anionite_mass),
            'temperature': float(test.temperature),
            'duration': float(test.duration),
            'stirring_speed': float(test.stirring_speed),
            'mo_extraction': float(test.mo_extraction),
            'sorption_capacity': float(test.sorption_capacity),
            'mo_on_anionite': float(test.mo_on_anionite),
            'mo_removed': test.mo_removed_from_solution,
        }
        
        return JsonResponse({
            'success': True,
            'test': test_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def analytics(request):
    """Комплексная аналитика процессов"""
    
    # === ДАННЫЕ ВЫЩЕЛАЧИВАНИЯ ===
    leaching_tests = LeachingTest.objects.prefetch_related('products').all()
    
    # Сравнение 6 опытов
    comparison_data = {
        'labels': [f"Опыт {t.number}" for t in leaching_tests],
        'mo_extraction': [t.mo_extraction_to_solution for t in leaching_tests],
        'acid_types': [t.get_acid_type_display() for t in leaching_tests],
        'has_oxygen': [t.has_oxygen for t in leaching_tests],
    }
    
    # Группировка по типу кислоты
    acid_type_stats = {}
    for acid_code, acid_name in LeachingTest._meta.get_field('acid_type').choices:
        tests = leaching_tests.filter(acid_type=acid_code)
        if tests:
            extractions = [t.mo_extraction_to_solution for t in tests]
            acid_type_stats[acid_name] = {
                'count': len(tests),
                'avg_extraction': sum(extractions) / len(extractions),
                'max_extraction': max(extractions),
            }
    
    # Эффект кислорода
    with_o2 = [t for t in leaching_tests if t.has_oxygen]
    without_o2 = [t for t in leaching_tests if not t.has_oxygen]
    
    oxygen_effect = {
        'with_oxygen': {
            'count': len(with_o2),
            'avg_extraction': sum([t.mo_extraction_to_solution for t in with_o2]) / len(with_o2) if with_o2 else 0,
        },
        'without_oxygen': {
            'count': len(without_o2),
            'avg_extraction': sum([t.mo_extraction_to_solution for t in without_o2]) / len(without_o2) if without_o2 else 0,
        }
    }
    
    # === ДАННЫЕ СОРБЦИИ ===
    sorption_tests = SorptionTest.objects.all()
    
    # Кинетические кривые (группировка по температуре)
    kinetics_data = {}
    for temp in [20, 40, 60, 80]:
        temp_tests = sorption_tests.filter(temperature=temp).order_by('duration')
        if temp_tests:
            kinetics_data[temp] = {
                'durations': [float(t.duration) for t in temp_tests],
                'extractions': [float(t.mo_extraction) for t in temp_tests],
                'capacities': [float(t.sorption_capacity) for t in temp_tests],
            }
    
    # Сравнение анионитов
    anionite_stats = {}
    for anionite_code, anionite_name in SorptionTest._meta.get_field('anionite_type').choices:
        tests = sorption_tests.filter(anionite_type=anionite_code)
        if tests:
            anionite_stats[anionite_name] = {
                'count': tests.count(),
                'avg_extraction': tests.aggregate(Avg('mo_extraction'))['mo_extraction__avg'],
                'max_extraction': tests.aggregate(Max('mo_extraction'))['mo_extraction__max'],
            }
    
    context = {
        # Выщелачивание
        'comparison_chart_data': json.dumps(comparison_data),
        'acid_type_stats': acid_type_stats,
        'oxygen_effect': oxygen_effect,
        
        # Сорбция
        'kinetics_data': json.dumps(kinetics_data),
        'anionite_stats': anionite_stats,
        
        # Общее
        'total_leaching_tests': leaching_tests.count(),
        'total_sorption_tests': sorption_tests.count(),
    }
    
    return render(request, 'molybdenum/analytics.html', context)


# === HELPER FUNCTIONS ===

@transaction.atomic
def save_leaching_test(data, results):
    """Сохранение теста выщелачивания в БД"""
    
    # Генерируем номер теста
    last_test = LeachingTest.objects.order_by('-number').first()
    test_number = (last_test.number + 1) if last_test else 1
    
    # Создаем тест
    test = LeachingTest.objects.create(
        number=test_number,
        concentrate_mass=float(data['concentrate_mass']),
        initial_mo=float(data['initial_mo']),
        initial_cu=float(data['initial_cu']),
        initial_fe=float(data['initial_fe']),
        initial_si=float(data['initial_si']),
        acid_type=data['acid_type'],
        hno3_concentration=float(data.get('hno3_concentration')) if data.get('hno3_concentration') else None,
        h2so4_concentration=float(data.get('h2so4_concentration')) if data.get('h2so4_concentration') else None,
        solution_volume=float(data['solution_volume']),
        temperature=float(data['temperature']),
        duration=float(data['duration']),
        stirring_speed=float(data['stirring_speed']),
        has_oxygen=data.get('has_oxygen', False),
        oxygen_flow=float(data.get('oxygen_flow')) if data.get('oxygen_flow') else None,
    )
    
    # Создаем продукты: Кек
    LeachingProduct.objects.create(
        test=test,
        product_type='cake',
        mass_or_volume=float(data['cake_mass']),
        yield_percentage=results['cake_yield'],
        mo_content=float(data['cake_mo']),
        cu_content=float(data['cake_cu']),
        fe_content=float(data['cake_fe']),
        si_content=float(data['cake_si']),
        mo_grams=results['cake']['mo'],
        cu_grams=results['cake']['cu'],
        fe_grams=results['cake']['fe'],
        si_grams=results['cake']['si'],
        mo_extraction=results['extractions']['mo_to_cake'],
        cu_extraction=results['extractions']['cu_to_cake'],
        fe_extraction=results['extractions']['fe_to_cake'],
        si_extraction=results['extractions']['si_to_cake'],
    )
    
    # Создаем продукты: Раствор
    LeachingProduct.objects.create(
        test=test,
        product_type='solution',
        mass_or_volume=float(data['solution_volume']),
        yield_percentage=None,
        mo_content=float(data['solution_mo']),
        cu_content=float(data['solution_cu']),
        fe_content=float(data['solution_fe']),
        si_content=float(data['solution_si']),
        mo_grams=results['solution']['mo'],
        cu_grams=results['solution']['cu'],
        fe_grams=results['solution']['fe'],
        si_grams=results['solution']['si'],
        mo_extraction=results['extractions']['mo_to_solution'],
        cu_extraction=results['extractions']['cu_to_solution'],
        fe_extraction=results['extractions']['fe_to_solution'],
        si_extraction=results['extractions']['si_to_solution'],
    )
    
    return test


@transaction.atomic
def save_sorption_test(data, results):
    """Сохранение теста сорбции в БД"""
    
    # Генерируем номер теста
    last_test = SorptionTest.objects.order_by('-number').first()
    test_number = (last_test.number + 1) if last_test else 1
    
    # Создаем тест
    test = SorptionTest.objects.create(
        number=test_number,
        leaching_test_id=data.get('leaching_test_id') if data.get('leaching_test_id') else None,
        solution_volume=float(data['solution_volume']),
        initial_mo_concentration=float(data['initial_mo_concentration']),
        final_mo_concentration=float(data['final_mo_concentration']),
        h2so4_concentration=float(data['h2so4_concentration']),
        anionite_type=data['anionite_type'],
        anionite_mass=float(data['anionite_mass']),
        temperature=float(data['temperature']),
        duration=float(data['duration']),
        stirring_speed=float(data.get('stirring_speed', 200)),
        mo_extraction=results['extraction'],
        sorption_capacity=results['sorption_capacity'],
        mo_on_anionite=results['mo_on_anionite'],
    )
    
    return test