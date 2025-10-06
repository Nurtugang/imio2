"""
Расчетные функции для восстановительной плавки антимоната натрия
"""


def calculate_smelting(data):
    """
    Основная функция расчета плавки антимоната натрия
    
    Входные параметры:
        data (dict): {
            'antimonite_mass': float,           # Масса антимоната (г)
            'sb_content': float,                 # Содержание Sb (%)
            'na_content': float,                 # Содержание Na (%)
            'as_content': float,                 # Содержание As (%)
            'moisture': float,                   # Влажность (%)
            'temperature': int,                  # Температура (°C): 900 или 1000
            'reducer_type': str,                 # Тип: 'coke' или 'charcoal'
            'reducer_amount': float,             # Расход восстановителя (%)
            'coke_ash': float,                   # Зольность коксика (%)
            'lead_addition': float,              # Добавка свинца (г), 0 если нет
        }
    
    Возвращает:
        dict: Полный материальный баланс и показатели
    """
    
    # Извлекаем данные
    antimonite_mass = float(data.get('antimonite_mass', 0))
    sb_content = float(data.get('sb_content', 60.39))
    na_content = float(data.get('na_content', 7.66))
    as_content = float(data.get('as_content', 0.60))
    moisture = float(data.get('moisture', 2.0))
    
    temperature = int(data.get('temperature', 900))
    reducer_type = data.get('reducer_type', 'coke')
    reducer_amount = float(data.get('reducer_amount', 10.0))
    coke_ash = float(data.get('coke_ash', 15.0))
    lead_addition = float(data.get('lead_addition', 0))
    
    # Проверка на нулевые значения
    if antimonite_mass <= 0:
        return {'error': 'Масса антимоната должна быть больше 0'}
    
    # 1. РАСЧЕТ СУХОЙ МАССЫ
    dry_antimonite = antimonite_mass * (1 - moisture / 100)
    
    # 2. КОЛИЧЕСТВО ЗАГРУЖЕННЫХ ЭЛЕМЕНТОВ
    sb_loaded = dry_antimonite * sb_content / 100
    na_loaded = dry_antimonite * na_content / 100
    as_loaded = dry_antimonite * as_content / 100
    
    # 3. МАССА ВОССТАНОВИТЕЛЯ
    reducer_mass = dry_antimonite * reducer_amount / 100
    
    # 4. ОБЩАЯ МАССА ШИХТЫ
    total_charge = dry_antimonite + reducer_mass + lead_addition
    
    # 5. ИЗВЛЕЧЕНИЕ СУРЬМЫ (по экспериментальным данным)
    if lead_addition > 0:
        # С добавкой свинца
        sb_extraction = get_extraction_with_lead(lead_addition, dry_antimonite)
    else:
        # Без свинца
        sb_extraction = get_extraction_no_lead(temperature, reducer_type)
    
    # 6. СОДЕРЖАНИЕ Sb В ЧЕРНОВОЙ СУРЬМЕ
    sb_in_crude = get_sb_content_in_crude(temperature, reducer_type, reducer_amount)
    
    # 7. МАССА ЧЕРНОВОЙ СУРЬМЫ
    crude_sb_mass = (sb_loaded * sb_extraction / 100) / (sb_in_crude / 100)
    
    # 8. РАСПРЕДЕЛЕНИЕ НАТРИЯ
    na_distribution = get_na_distribution(reducer_type)
    na_to_crude = na_loaded * na_distribution['to_crude'] / 100
    na_to_slag = na_loaded * na_distribution['to_slag'] / 100
    
    # 9. РАСПРЕДЕЛЕНИЕ МЫШЬЯКА
    as_to_crude = as_loaded * 0.50  # ~50% в черновую
    as_to_slag = as_loaded * 0.15   # ~15% в шлак
    as_to_gas = as_loaded * 0.35    # ~35% в газы
    
    # 10. ПРИМЕСИ В ЧЕРНОВОЙ СУРЬМЕ
    na_content_crude = (na_to_crude / crude_sb_mass) * 100
    as_content_crude = (as_to_crude / crude_sb_mass) * 100
    pb_content_crude = 0.70  # Средняя примесь свинца
    fe_content_crude = 0.55  # Средняя примесь железа
    
    # 11. МАССА И СОСТАВ ШЛАКА
    slag_mass = calculate_slag_mass(
        dry_antimonite, reducer_mass, crude_sb_mass, reducer_type, coke_ash
    )
    
    sb_in_slag = get_sb_in_slag(reducer_amount)  # Содержание Sb в шлаке (%)
    na_in_slag = 30.0  # Содержание Na в шлаке (~30%)
    
    # 12. ПОТЕРИ
    sb_to_slag = slag_mass * sb_in_slag / 100
    sb_losses = sb_loaded - (crude_sb_mass * sb_in_crude / 100) - sb_to_slag
    total_losses = total_charge - crude_sb_mass - slag_mass
    
    # 13. ТЕХНИКО-ЭКОНОМИЧЕСКИЕ ПОКАЗАТЕЛИ
    crude_yield = (crude_sb_mass / total_charge) * 100
    slag_yield = (slag_mass / total_charge) * 100
    
    # ФОРМИРУЕМ РЕЗУЛЬТАТ
    results = {
        'success': True,
        
        # Входные данные (для отображения)
        'input': {
            'antimonite_mass': antimonite_mass,
            'dry_antimonite': round(dry_antimonite, 2),
            'sb_content': sb_content,
            'na_content': na_content,
            'as_content': as_content,
            'temperature': temperature,
            'reducer_type_display': 'Коксик' if reducer_type == 'coke' else 'Древесный уголь',
            'reducer_amount': reducer_amount,
            'reducer_mass': round(reducer_mass, 2),
            'lead_addition': lead_addition,
            'total_charge': round(total_charge, 2),
        },
        
        # Загружено элементов
        'loaded': {
            'sb': round(sb_loaded, 2),
            'na': round(na_loaded, 2),
            'as': round(as_loaded, 2),
        },
        
        # ЧЕРНОВАЯ СУРЬМА
        'crude_antimony': {
            'mass': round(crude_sb_mass, 2),
            'yield_percent': round(crude_yield, 2),
            'sb_content': round(sb_in_crude, 2),
            'sb_extraction': round(sb_extraction, 2),
            'impurities': {
                'na': round(na_content_crude, 2),
                'as': round(as_content_crude, 2),
                'pb': pb_content_crude,
                'fe': fe_content_crude,
            }
        },
        
        # ШЛАК
        'slag': {
            'mass': round(slag_mass, 2),
            'yield_percent': round(slag_yield, 2),
            'sb_content': round(sb_in_slag, 2),
            'na_content': na_in_slag,
            'sb_losses': round(sb_to_slag, 2),
        },
        
        # ПОТЕРИ
        'losses': {
            'sb_to_gas': round(sb_losses, 2),
            'as_to_gas': round(as_to_gas, 2),
            'total_balance_diff': round(total_losses, 2),
            'total_losses_percent': round((total_losses / total_charge) * 100, 2),
        },
        
        # МАТЕРИАЛЬНЫЙ БАЛАНС
        'balance': {
            'sb': {
                'loaded': round(sb_loaded, 2),
                'to_crude': round(crude_sb_mass * sb_in_crude / 100, 2),
                'to_slag': round(sb_to_slag, 2),
                'to_gas': round(sb_losses, 2),
                'extraction_percent': round(sb_extraction, 2),
            },
            'na': {
                'loaded': round(na_loaded, 2),
                'to_crude': round(na_to_crude, 2),
                'to_slag': round(na_to_slag, 2),
            },
            'as': {
                'loaded': round(as_loaded, 2),
                'to_crude': round(as_to_crude, 2),
                'to_slag': round(as_to_slag, 2),
                'to_gas': round(as_to_gas, 2),
            }
        },
        
        # ОЦЕНКА И РЕКОМЕНДАЦИИ
        'recommendations': generate_recommendations(
            sb_extraction, reducer_amount, temperature, reducer_type, na_content_crude
        )
    }
    
    return results


# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def get_extraction_no_lead(temperature, reducer_type):
    """Извлечение Sb без добавки свинца"""
    if temperature == 900:
        return 71.0 if reducer_type == 'charcoal' else 72.35
    else:  # 1000°C
        return 75.85 if reducer_type == 'charcoal' else 71.49


def get_extraction_with_lead(lead_mass, antimonite_mass):
    """Извлечение Sb с добавкой свинца"""
    pb_ratio = lead_mass / antimonite_mass
    if pb_ratio > 1.0:  # Много свинца
        return 80.09
    else:
        return 84.83


def get_sb_content_in_crude(temperature, reducer_type, reducer_amount):
    """Содержание Sb в черновой сурьме"""
    if reducer_amount < 10:
        return 97.90
    elif reducer_amount > 10:
        return 92.42
    else:
        if temperature == 900:
            return 88.73 if reducer_type == 'charcoal' else 94.05
        else:
            return 90.52 if reducer_type == 'charcoal' else 87.32


def get_na_distribution(reducer_type):
    """Распределение натрия"""
    if reducer_type == 'coke':
        return {'to_crude': 4.5, 'to_slag': 95.5}  # Коксик
    else:
        return {'to_crude': 35.0, 'to_slag': 65.0}  # Древесный уголь


def get_sb_in_slag(reducer_amount):
    """Содержание Sb в шлаке в зависимости от расхода восстановителя"""
    if reducer_amount < 10:
        return 55.83
    elif reducer_amount > 10:
        return 0.56
    else:
        return 1.0


def calculate_slag_mass(antimonite, reducer, crude, reducer_type, ash):
    """Расчет массы шлака"""
    # Упрощенная формула на основе экспериментальных данных
    base_slag = antimonite * 0.20  # Базовая масса ~20% от антимоната
    ash_contribution = reducer * (ash / 100) if reducer_type == 'coke' else 0
    return base_slag + ash_contribution


def generate_recommendations(extraction, reducer_amount, temp, reducer_type, na_crude):
    """Генерация рекомендаций"""
    recommendations = []
    
    # Оценка извлечения
    if extraction >= 85:
        recommendations.append({
            'type': 'success',
            'title': 'Отличное извлечение!',
            'text': f'Извлечение {extraction:.1f}% превышает промышленный уровень (70-76%).'
        })
    elif extraction >= 70:
        recommendations.append({
            'type': 'info',
            'title': 'Хорошее извлечение',
            'text': f'Извлечение {extraction:.1f}% соответствует промышленным показателям.'
        })
    else:
        recommendations.append({
            'type': 'warning',
            'title': 'Низкое извлечение',
            'text': f'Извлечение {extraction:.1f}% ниже нормы. Проверьте параметры плавки.'
        })
    
    # Расход восстановителя
    if reducer_amount < 10:
        recommendations.append({
            'type': 'warning',
            'title': 'Недостаточно восстановителя',
            'text': 'При расходе <10% возможны большие потери Sb в шлаке. Рекомендуется 10%.'
        })
    elif reducer_amount > 15:
        recommendations.append({
            'type': 'warning',
            'title': 'Избыток восстановителя',
            'text': 'При расходе >15% резко возрастает содержание Na в черновой сурьме.'
        })
    else:
        recommendations.append({
            'type': 'success',
            'title': 'Оптимальный расход восстановителя',
            'text': 'Расход 10-15% обеспечивает лучшие показатели.'
        })
    
    # Натрий в черновой сурьме
    if na_crude > 5:
        recommendations.append({
            'type': 'error',
            'title': 'Высокое содержание натрия!',
            'text': f'Na в черновой сурьме: {na_crude:.2f}%. Рекомендуется использовать коксик вместо угля.'
        })
    elif na_crude > 3:
        recommendations.append({
            'type': 'warning',
            'title': 'Повышенное содержание натрия',
            'text': f'Na в черновой сурьме: {na_crude:.2f}%. Требуется дополнительное рафинирование.'
        })
    
    # Температура
    if temp < 900:
        recommendations.append({
            'type': 'error',
            'title': 'Слишком низкая температура',
            'text': 'При температуре <900°C возможно неполное расплавление шихты.'
        })
    
    # Тип восстановителя
    if reducer_type == 'charcoal':
        recommendations.append({
            'type': 'info',
            'title': 'Древесный уголь',
            'text': 'При использовании угля повышается содержание Na. Рекомендуется коксик.'
        })
    
    return recommendations