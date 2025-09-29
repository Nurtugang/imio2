from django.test import TestCase
from .utils import calculate_leaching_balance, calculate_sorption


class LeachingCalculationsTest(TestCase):
    """Тесты расчетов выщелачивания"""
    
    def test_leaching_balance_calculation(self):
        """Тест расчета баланса - Опыт №6 из документа"""
        data = {
            'concentrate_mass': 50,
            'initial_mo': 25.01,
            'initial_cu': 0.91,
            'initial_fe': 3.5,
            'initial_si': 3.2,
            
            'cake_mass': 43.5,
            'cake_mo': 7.88,
            'cake_cu': 0.37,
            'cake_fe': 1.42,
            'cake_si': 3.36,
            
            'solution_volume': 250,
            'solution_mo': 36.3,
            'solution_cu': 1.18,
            'solution_fe': 4.53,
            'solution_si': 0.54,
        }
        
        result = calculate_leaching_balance(data)
        
        # Проверяем извлечение Mo в раствор (должно быть ~72.6%)
        self.assertAlmostEqual(result['extractions']['mo_to_solution'], 72.6, delta=1.0)
        
        # Проверяем выход кека (должно быть 87%)
        self.assertAlmostEqual(result['cake_yield'], 87.0, delta=1.0)
        
        # Проверяем баланс (должен быть близок к 100%)
        self.assertGreater(result['avg_balance'], 95)
        self.assertLess(result['avg_balance'], 105)


class SorptionCalculationsTest(TestCase):
    """Тесты расчетов сорбции"""
    
    def test_sorption_calculation(self):
        """Тест расчета сорбции - из таблицы 6 (80°C, 60 мин)"""
        data = {
            'solution_volume': 200,
            'initial_mo_concentration': 2.429,  # средняя концентрация
            'final_mo_concentration': 0.131,
            'anionite_mass': 10,  # условная масса
            'temperature': 80,
            'duration': 60,
        }
        
        result = calculate_sorption(data)
        
        # Проверяем извлечение (должно быть высоким)
        self.assertGreater(result['extraction'], 90)
        
        # Проверяем сорбционную емкость
        self.assertGreater(result['sorption_capacity'], 0)
        
        # Проверяем количество Mo на анионите
        self.assertGreater(result['mo_on_anionite'], 0)