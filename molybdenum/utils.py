"""
Утилиты для расчетов процессов переработки молибденита
"""


def calculate_leaching_balance(data):
    """
    Расчет материального баланса выщелачивания молибденитового концентрата
    
    Args:
        data (dict): Словарь с входными данными
            - concentrate_mass: масса концентрата (г)
            - initial_mo, initial_cu, initial_fe, initial_si: исходные содержания (%)
            - cake_mass: масса кека (г)
            - cake_mo, cake_cu, cake_fe, cake_si: содержания в кеке (%)
            - solution_volume: объем раствора (мл)
            - solution_mo, solution_cu, solution_fe, solution_si: концентрации в растворе (г/л)
    
    Returns:
        dict: Результаты расчета с материальным балансом
    """
    
    # === ИСХОДНОЕ КОЛИЧЕСТВО ЭЛЕМЕНТОВ (г) ===
    concentrate_mass = float(data['concentrate_mass'])
    
    initial_elements = {
        'mo': concentrate_mass * float(data['initial_mo']) / 100,
        'cu': concentrate_mass * float(data['initial_cu']) / 100,
        'fe': concentrate_mass * float(data['initial_fe']) / 100,
        'si': concentrate_mass * float(data['initial_si']) / 100,
    }
    
    # === КЕК: КОЛИЧЕСТВО ЭЛЕМЕНТОВ (г) ===
    cake_mass = float(data['cake_mass'])
    
    cake_elements = {
        'mo': cake_mass * float(data['cake_mo']) / 100,
        'cu': cake_mass * float(data['cake_cu']) / 100,
        'fe': cake_mass * float(data['cake_fe']) / 100,
        'si': cake_mass * float(data['cake_si']) / 100,
    }
    
    # === РАСТВОР: КОЛИЧЕСТВО ЭЛЕМЕНТОВ (г) ===
    # Формула: концентрация (г/л) × объем (мл) / 1000
    solution_volume = float(data['solution_volume'])
    
    solution_elements = {
        'mo': float(data['solution_mo']) * solution_volume / 1000,
        'cu': float(data['solution_cu']) * solution_volume / 1000,
        'fe': float(data['solution_fe']) * solution_volume / 1000,
        'si': float(data['solution_si']) * solution_volume / 1000,
    }
    
    # === ИЗВЛЕЧЕНИЯ (%) ===
    extractions = {}
    
    for element in ['mo', 'cu', 'fe', 'si']:
        if initial_elements[element] > 0:
            # Извлечение в кек
            cake_extraction = (cake_elements[element] / initial_elements[element]) * 100
            
            # Извлечение в раствор
            solution_extraction = (solution_elements[element] / initial_elements[element]) * 100
            
            extractions[f'{element}_to_cake'] = cake_extraction
            extractions[f'{element}_to_solution'] = solution_extraction
        else:
            extractions[f'{element}_to_cake'] = 0
            extractions[f'{element}_to_solution'] = 0
    
    # === ВЫХОД КЕКА (%) ===
    cake_yield = (cake_mass / concentrate_mass) * 100
    
    # === ПРОВЕРКА БАЛАНСА ===
    # Сумма элементов в продуктах / Исходное × 100
    balance_check = {}
    
    for element in ['mo', 'cu', 'fe', 'si']:
        if initial_elements[element] > 0:
            total_in_products = cake_elements[element] + solution_elements[element]
            balance = (total_in_products / initial_elements[element]) * 100
            balance_check[element] = balance
        else:
            balance_check[element] = 0
    
    # Средний баланс
    avg_balance = sum(balance_check.values()) / len(balance_check)
    
    # === ВАЛИДАЦИИ ===
    validations = []
    
    # Проверка баланса
    if avg_balance < 95:
        validations.append({
            'type': 'warning',
            'message': f'Баланс ниже нормы: {avg_balance:.1f}% (норма >95%)'
        })
    elif avg_balance > 105:
        validations.append({
            'type': 'warning',
            'message': f'Баланс выше нормы: {avg_balance:.1f}% (норма <105%)'
        })
    else:
        validations.append({
            'type': 'success',
            'message': f'Баланс в норме: {avg_balance:.1f}%'
        })
    
    # Проверка извлечения Mo
    mo_to_solution = extractions['mo_to_solution']
    if mo_to_solution > 70:
        validations.append({
            'type': 'success',
            'message': f'Отличное извлечение Mo в раствор: {mo_to_solution:.1f}%'
        })
    elif mo_to_solution > 50:
        validations.append({
            'type': 'info',
            'message': f'Хорошее извлечение Mo в раствор: {mo_to_solution:.1f}%'
        })
    else:
        validations.append({
            'type': 'warning',
            'message': f'Низкое извлечение Mo в раствор: {mo_to_solution:.1f}%'
        })
    
    # === ФОРМИРУЕМ РЕЗУЛЬТАТ ===
    return {
        'initial': initial_elements,
        'cake': cake_elements,
        'solution': solution_elements,
        'extractions': extractions,
        'cake_yield': cake_yield,
        'balance_check': balance_check,
        'avg_balance': avg_balance,
        'validations': validations,
        
        # Дополнительная информация
        'concentrate_mass': concentrate_mass,
        'cake_mass': cake_mass,
        'solution_volume': solution_volume,
    }


def calculate_sorption(data):
    """
    Расчет сорбции молибдена на анионите
    
    Args:
        data (dict): Словарь с входными данными
            - solution_volume: объем раствора (мл)
            - initial_mo_concentration: начальная концентрация Mo (г/л)
            - final_mo_concentration: конечная концентрация Mo (г/л)
            - anionite_mass: масса анионита (г)
            - temperature: температура (°C)
            - duration: продолжительность (мин)
    
    Returns:
        dict: Результаты расчета сорбции
    """
    
    # === ИЗВЛЕКАЕМ ДАННЫЕ ===
    volume = float(data['solution_volume'])  # мл
    c_initial = float(data['initial_mo_concentration'])  # г/л
    c_final = float(data['final_mo_concentration'])  # г/л
    anionite_mass = float(data['anionite_mass'])  # г
    temperature = float(data.get('temperature', 25))  # °C
    duration = float(data.get('duration', 60))  # мин
    
    # === РАСЧЕТ ИЗВЛЕЧЕНИЯ (%) ===
    if c_initial > 0:
        extraction = ((c_initial - c_final) / c_initial) * 100
    else:
        extraction = 0
    
    # === КОЛИЧЕСТВО Mo НА АНИОНИТЕ (г) ===
    # Формула: (C_начальное - C_конечное) × V / 1000
    mo_on_anionite = (c_initial - c_final) * volume / 1000
    
    # === СОРБЦИОННАЯ ЕМКОСТЬ (г-атом/г) ===
    # Формула: количество_Mo / масса_анионита / атомная_масса_Mo
    ATOMIC_MASS_MO = 95.95  # г/моль
    
    if anionite_mass > 0:
        sorption_capacity = mo_on_anionite / anionite_mass / ATOMIC_MASS_MO
    else:
        sorption_capacity = 0
    
    # === СТЕПЕНЬ ЗАПОЛНЕНИЯ АНИОНИТА ===
    # Условная максимальная емкость: 0.002 г-атом/г (из литературы)
    max_capacity = 0.002
    
    if sorption_capacity > 0:
        filling_degree = (sorption_capacity / max_capacity) * 100
    else:
        filling_degree = 0
    
    # === УДЕЛЬНАЯ СОРБЦИЯ (мг Mo/г анионита) ===
    if anionite_mass > 0:
        specific_sorption = (mo_on_anionite * 1000) / anionite_mass  # мг/г
    else:
        specific_sorption = 0
    
    # === КИНЕТИЧЕСКИЙ КОЭФФИЦИЕНТ ===
    # k = ln(C0/C) / t (условная формула для оценки)
    if c_final > 0 and duration > 0:
        import math
        kinetic_coefficient = math.log(c_initial / c_final) / duration
    else:
        kinetic_coefficient = 0
    
    # === ВАЛИДАЦИИ ===
    validations = []
    
    # Проверка извлечения
    if extraction > 90:
        validations.append({
            'type': 'success',
            'message': f'Отличное извлечение Mo: {extraction:.1f}%'
        })
    elif extraction > 70:
        validations.append({
            'type': 'info',
            'message': f'Хорошее извлечение Mo: {extraction:.1f}%'
        })
    elif extraction > 50:
        validations.append({
            'type': 'warning',
            'message': f'Среднее извлечение Mo: {extraction:.1f}%'
        })
    else:
        validations.append({
            'type': 'error',
            'message': f'Низкое извлечение Mo: {extraction:.1f}%'
        })
    
    # Проверка сорбционной емкости
    if sorption_capacity > 0.0015:
        validations.append({
            'type': 'success',
            'message': f'Высокая сорбционная емкость: {sorption_capacity:.2e} г-атом/г'
        })
    elif sorption_capacity > 0.0005:
        validations.append({
            'type': 'info',
            'message': f'Нормальная сорбционная емкость: {sorption_capacity:.2e} г-атом/г'
        })
    else:
        validations.append({
            'type': 'warning',
            'message': f'Низкая сорбционная емкость: {sorption_capacity:.2e} г-атом/г'
        })
    
    # Проверка заполнения
    if filling_degree > 90:
        validations.append({
            'type': 'warning',
            'message': f'Анионит близок к насыщению: {filling_degree:.1f}% от максимума'
        })
    
    # === РЕКОМЕНДАЦИИ ===
    recommendations = []
    
    if temperature < 60 and extraction < 70:
        recommendations.append('Попробуйте повысить температуру до 60-80°C для улучшения сорбции')
    
    if duration < 60 and extraction < 80:
        recommendations.append('Увеличьте время сорбции для достижения равновесия')
    
    if c_initial < 1.0:
        recommendations.append('При низких концентрациях Mo (<1 г/л) сорбция более эффективна')
    
    if extraction > 90 and duration > 180:
        recommendations.append('Сорбция достигла максимума, дальнейшее увеличение времени нецелесообразно')
    
    # === ФОРМИРУЕМ РЕЗУЛЬТАТ ===
    return {
        'extraction': extraction,
        'mo_on_anionite': mo_on_anionite,
        'sorption_capacity': sorption_capacity,
        'specific_sorption': specific_sorption,
        'filling_degree': filling_degree,
        'kinetic_coefficient': kinetic_coefficient,
        'final_concentration': c_final,
        'mo_removed': c_initial - c_final,  # г/л
        'validations': validations,
        'recommendations': recommendations,
        
        # Исходные данные для справки
        'initial_concentration': c_initial,
        'volume': volume,
        'anionite_mass': anionite_mass,
        'temperature': temperature,
        'duration': duration,
    }


def calculate_kinetic_series(base_data, time_points):
    """
    Расчет кинетической серии сорбции для построения графиков
    
    Args:
        base_data (dict): Базовые данные (температура, концентрация и т.д.)
        time_points (list): Список временных точек (мин)
    
    Returns:
        list: Список результатов для каждой временной точки
    """
    
    results = []
    
    for time in time_points:
        # Копируем базовые данные
        data = base_data.copy()
        data['duration'] = time
        
        # Упрощенная модель: C(t) = C0 × exp(-k×t)
        # k зависит от температуры (из экспериментальных данных)
        temperature = float(base_data['temperature'])
        
        # Коэффициенты скорости для разных температур (из документов)
        if temperature >= 80:
            k = 0.015  # быстрая сорбция
        elif temperature >= 60:
            k = 0.008
        elif temperature >= 40:
            k = 0.005
        else:
            k = 0.003  # медленная сорбция
        
        import math
        c_initial = float(base_data['initial_mo_concentration'])
        c_final = c_initial * math.exp(-k * time)
        
        data['final_mo_concentration'] = c_final
        
        # Рассчитываем сорбцию для этой точки
        result = calculate_sorption(data)
        result['time'] = time
        
        results.append(result)
    
    return results


def format_number(value, decimals=2):
    """Форматирование числа с заданным количеством знаков после запятой"""
    try:
        return round(float(value), decimals)
    except (ValueError, TypeError):
        return 0


def validate_leaching_data(data):
    """
    Валидация входных данных для выщелачивания
    
    Returns:
        tuple: (is_valid, errors)
    """
    errors = []
    
    # Проверка массы концентрата
    if float(data.get('concentrate_mass', 0)) <= 0:
        errors.append('Масса концентрата должна быть больше 0')
    
    # Проверка содержаний
    for element in ['mo', 'cu', 'fe', 'si']:
        initial = float(data.get(f'initial_{element}', 0))
        if initial < 0 or initial > 100:
            errors.append(f'Содержание {element.upper()} должно быть от 0 до 100%')
    
    # Проверка условий
    if float(data.get('temperature', 0)) < 0 or float(data.get('temperature', 0)) > 200:
        errors.append('Температура должна быть от 0 до 200°C')
    
    if float(data.get('duration', 0)) <= 0:
        errors.append('Продолжительность должна быть больше 0')
    
    # Проверка продуктов
    if float(data.get('cake_mass', 0)) <= 0:
        errors.append('Масса кека должна быть больше 0')
    
    if float(data.get('solution_volume', 0)) <= 0:
        errors.append('Объем раствора должен быть больше 0')
    
    return (len(errors) == 0, errors)


def validate_sorption_data(data):
    """
    Валидация входных данных для сорбции
    
    Returns:
        tuple: (is_valid, errors)
    """
    errors = []
    
    # Проверка объема
    if float(data.get('solution_volume', 0)) <= 0:
        errors.append('Объем раствора должен быть больше 0')
    
    # Проверка концентраций
    c_initial = float(data.get('initial_mo_concentration', 0))
    c_final = float(data.get('final_mo_concentration', 0))
    
    if c_initial <= 0:
        errors.append('Начальная концентрация Mo должна быть больше 0')
    
    if c_final < 0:
        errors.append('Конечная концентрация Mo не может быть отрицательной')
    
    if c_final > c_initial:
        errors.append('Конечная концентрация не может быть больше начальной')
    
    # Проверка массы анионита
    if float(data.get('anionite_mass', 0)) <= 0:
        errors.append('Масса анионита должна быть больше 0')
    
    # Проверка условий
    temp = float(data.get('temperature', 25))
    if temp < 0 or temp > 100:
        errors.append('Температура должна быть от 0 до 100°C')
    
    duration = float(data.get('duration', 0))
    if duration <= 0:
        errors.append('Продолжительность должна быть больше 0')
    
    return (len(errors) == 0, errors)