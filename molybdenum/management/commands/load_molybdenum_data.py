from django.core.management.base import BaseCommand
from molybdenum.models import LeachingTest, LeachingProduct, SorptionTest
from molybdenum.utils import calculate_leaching_balance


class Command(BaseCommand):
    help = 'Загружает тестовые данные из документов (6 опытов выщелачивания)'
    
    def handle(self, *args, **options):
        # Данные из "Таблица по выщелачиванию.docx"
        experiments = [
            # Опыт №1
            {
                'number': 1,
                'acid_type': 'hno3',
                'hno3_concentration': 50,
                'h2so4_concentration': None,
                'has_oxygen': False,
                'concentrate': {
                    'mass': 50,
                    'mo': 20.3, 'cu': 1.99, 'fe': 2.33, 'si': 2.47
                },
                'cake': {
                    'mass': 43.5,
                    'mo': 18.86, 'cu': 0.508, 'fe': 0.611, 'si': 1.74
                },
                'solution': {
                    'volume': 300,
                    'mo': 6.5, 'cu': 2.58, 'fe': 3.01, 'si': 1.61
                },
                'conditions': {
                    'temperature': 95, 'duration': 4, 'stirring_speed': 300
                }
            },
            # Опыт №2
            {
                'number': 2,
                'acid_type': 'h2so4',
                'hno3_concentration': None,
                'h2so4_concentration': 200,
                'has_oxygen': False,
                'concentrate': {
                    'mass': 50,
                    'mo': 20.3, 'cu': 1.99, 'fe': 2.33, 'si': 2.47
                },
                'cake': {
                    'mass': 47.52,
                    'mo': 18.166, 'cu': 1.206, 'fe': 1.443, 'si': 2.46
                },
                'solution': {
                    'volume': 300,
                    'mo': 5.1, 'cu': 1.4, 'fe': 1.61, 'si': 0.23
                },
                'conditions': {
                    'temperature': 95, 'duration': 4, 'stirring_speed': 300
                }
            },
            # Опыт №3
            {
                'number': 3,
                'acid_type': 'hno3',
                'hno3_concentration': 50,
                'h2so4_concentration': None,
                'has_oxygen': True,
                'oxygen_flow': 0.85,
                'concentrate': {
                    'mass': 50,
                    'mo': 20.3, 'cu': 1.99, 'fe': 2.33, 'si': 2.47
                },
                'cake': {
                    'mass': 42.5,
                    'mo': 13.088, 'cu': 0.323, 'fe': 0.411, 'si': 1.742
                },
                'solution': {
                    'volume': 300,
                    'mo': 18.0, 'cu': 3.4, 'fe': 3.9, 'si': 1.96
                },
                'conditions': {
                    'temperature': 95, 'duration': 4, 'stirring_speed': 300
                }
            },
            # Опыт №4
            {
                'number': 4,
                'acid_type': 'h2so4',
                'hno3_concentration': None,
                'h2so4_concentration': 200,
                'has_oxygen': True,
                'oxygen_flow': 0.85,
                'concentrate': {
                    'mass': 50,
                    'mo': 20.3, 'cu': 1.99, 'fe': 2.33, 'si': 2.47
                },
                'cake': {
                    'mass': 49.18,
                    'mo': 16.6, 'cu': 1.166, 'fe': 1.385, 'si': 2.25
                },
                'solution': {
                    'volume': 300,
                    'mo': 7.65, 'cu': 1.62, 'fe': 1.88, 'si': 0.54
                },
                'conditions': {
                    'temperature': 95, 'duration': 4, 'stirring_speed': 300
                }
            },
            # Опыт №5
            {
                'number': 5,
                'acid_type': 'mixed',
                'hno3_concentration': 50,
                'h2so4_concentration': 200,
                'has_oxygen': False,
                'concentrate': {
                    'mass': 50,
                    'mo': 25.01, 'cu': 0.91, 'fe': 3.5, 'si': 3.2
                },
                'cake': {
                    'mass': 45.0,
                    'mo': 13.8, 'cu': 0.42, 'fe': 1.98, 'si': 3.37
                },
                'solution': {
                    'volume': 265,
                    'mo': 23.6, 'cu': 1.0, 'fe': 3.23, 'si': 0.3
                },
                'conditions': {
                    'temperature': 95, 'duration': 4, 'stirring_speed': 300
                }
            },
            # Опыт №6 - лучший результат
            {
                'number': 6,
                'acid_type': 'mixed',
                'hno3_concentration': 50,
                'h2so4_concentration': 200,
                'has_oxygen': True,
                'oxygen_flow': 0.85,
                'concentrate': {
                    'mass': 50,
                    'mo': 25.01, 'cu': 0.91, 'fe': 3.5, 'si': 3.2
                },
                'cake': {
                    'mass': 43.5,
                    'mo': 7.88, 'cu': 0.37, 'fe': 1.42, 'si': 3.36
                },
                'solution': {
                    'volume': 250,
                    'mo': 36.3, 'cu': 1.18, 'fe': 4.53, 'si': 0.54
                },
                'conditions': {
                    'temperature': 95, 'duration': 4, 'stirring_speed': 300
                }
            },
        ]
        
        for exp in experiments:
            # Создаем тест
            test, created = LeachingTest.objects.get_or_create(
                number=exp['number'],
                defaults={
                    'concentrate_mass': exp['concentrate']['mass'],
                    'initial_mo': exp['concentrate']['mo'],
                    'initial_cu': exp['concentrate']['cu'],
                    'initial_fe': exp['concentrate']['fe'],
                    'initial_si': exp['concentrate']['si'],
                    'acid_type': exp['acid_type'],
                    'hno3_concentration': exp.get('hno3_concentration'),
                    'h2so4_concentration': exp.get('h2so4_concentration'),
                    'solution_volume': exp['solution']['volume'],
                    'temperature': exp['conditions']['temperature'],
                    'duration': exp['conditions']['duration'],
                    'stirring_speed': exp['conditions']['stirring_speed'],
                    'has_oxygen': exp['has_oxygen'],
                    'oxygen_flow': exp.get('oxygen_flow'),
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан тест №{exp["number"]}'))
                
                # Рассчитываем баланс
                calc_data = {
                    'concentrate_mass': exp['concentrate']['mass'],
                    'initial_mo': exp['concentrate']['mo'],
                    'initial_cu': exp['concentrate']['cu'],
                    'initial_fe': exp['concentrate']['fe'],
                    'initial_si': exp['concentrate']['si'],
                    'cake_mass': exp['cake']['mass'],
                    'cake_mo': exp['cake']['mo'],
                    'cake_cu': exp['cake']['cu'],
                    'cake_fe': exp['cake']['fe'],
                    'cake_si': exp['cake']['si'],
                    'solution_volume': exp['solution']['volume'],
                    'solution_mo': exp['solution']['mo'],
                    'solution_cu': exp['solution']['cu'],
                    'solution_fe': exp['solution']['fe'],
                    'solution_si': exp['solution']['si'],
                    }
                
                balance = calculate_leaching_balance(calc_data)
                
                # Создаем продукты: Кек
                LeachingProduct.objects.create(
                    test=test,
                    product_type='cake',
                    mass_or_volume=exp['cake']['mass'],
                    yield_percentage=balance['cake_yield'],
                    mo_content=exp['cake']['mo'],
                    cu_content=exp['cake']['cu'],
                    fe_content=exp['cake']['fe'],
                    si_content=exp['cake']['si'],
                    mo_grams=balance['cake']['mo'],
                    cu_grams=balance['cake']['cu'],
                    fe_grams=balance['cake']['fe'],
                    si_grams=balance['cake']['si'],
                    mo_extraction=balance['extractions']['mo_to_cake'],
                    cu_extraction=balance['extractions']['cu_to_cake'],
                    fe_extraction=balance['extractions']['fe_to_cake'],
                    si_extraction=balance['extractions']['si_to_cake'],
                )
                
                # Создаем продукты: Раствор
                LeachingProduct.objects.create(
                    test=test,
                    product_type='solution',
                    mass_or_volume=exp['solution']['volume'],
                    yield_percentage=None,
                    mo_content=exp['solution']['mo'],
                    cu_content=exp['solution']['cu'],
                    fe_content=exp['solution']['fe'],
                    si_content=exp['solution']['si'],
                    mo_grams=balance['solution']['mo'],
                    cu_grams=balance['solution']['cu'],
                    fe_grams=balance['solution']['fe'],
                    si_grams=balance['solution']['si'],
                    mo_extraction=balance['extractions']['mo_to_solution'],
                    cu_extraction=balance['extractions']['cu_to_solution'],
                    fe_extraction=balance['extractions']['fe_to_solution'],
                    si_extraction=balance['extractions']['si_to_solution'],
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  → Извлечение Mo в раствор: {balance["extractions"]["mo_to_solution"]:.1f}%'
                    )
                )
            else:
                self.stdout.write(self.style.WARNING(f'Тест №{exp["number"]} уже существует'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Загрузка тестов выщелачивания завершена!'))
        
        # === ЗАГРУЗКА ДАННЫХ СОРБЦИИ ===
        self.stdout.write('\n📊 Загрузка данных сорбции...\n')
        
        # Данные из таблицы 3 (20°C) - выборочно
        sorption_data_20c = [
            {'duration': 15, 'concentration': 1.226, 'capacity': 7.37e-4},
            {'duration': 60, 'concentration': 1.435, 'capacity': 6.09e-4},
            {'duration': 180, 'concentration': 1.641, 'capacity': 4.828e-4},
            {'duration': 540, 'concentration': 1.697, 'capacity': 4.485e-4},
        ]
        
        # Данные из таблицы 6 (80°C) - выборочно
        sorption_data_80c = [
            {'duration': 60, 'concentration': 0.131, 'capacity': 1.41e-3},
            {'duration': 180, 'concentration': 0.516, 'capacity': 1.17e-3},
            {'duration': 540, 'concentration': 0.612, 'capacity': 1.11e-3},
        ]
        
        test_number = 1
        initial_concentration = 2.429  # средняя начальная концентрация
        
        # Загружаем данные 20°C
        for data in sorption_data_20c:
            test, created = SorptionTest.objects.get_or_create(
                number=test_number,
                defaults={
                    'solution_volume': 200,
                    'initial_mo_concentration': initial_concentration,
                    'final_mo_concentration': data['concentration'],
                    'h2so4_concentration': 200,
                    'anionite_type': 'purolite_a100',
                    'anionite_mass': 10,
                    'temperature': 20,
                    'duration': data['duration'],
                    'stirring_speed': 200,
                    'mo_extraction': ((initial_concentration - data['concentration']) / initial_concentration) * 100,
                    'sorption_capacity': data['capacity'],
                    'mo_on_anionite': (initial_concentration - data['concentration']) * 200 / 1000,
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Создан тест сорбции №{test_number}: 20°C, {data["duration"]} мин, извл. {test.mo_extraction:.1f}%'
                    )
                )
            test_number += 1
        
        # Загружаем данные 80°C
        for data in sorption_data_80c:
            test, created = SorptionTest.objects.get_or_create(
                number=test_number,
                defaults={
                    'solution_volume': 200,
                    'initial_mo_concentration': initial_concentration,
                    'final_mo_concentration': data['concentration'],
                    'h2so4_concentration': 200,
                    'anionite_type': 'purolite_a100',
                    'anionite_mass': 10,
                    'temperature': 80,
                    'duration': data['duration'],
                    'stirring_speed': 200,
                    'mo_extraction': ((initial_concentration - data['concentration']) / initial_concentration) * 100,
                    'sorption_capacity': data['capacity'],
                    'mo_on_anionite': (initial_concentration - data['concentration']) * 200 / 1000,
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Создан тест сорбции №{test_number}: 80°C, {data["duration"]} мин, извл. {test.mo_extraction:.1f}%'
                    )
                )
            test_number += 1
        
        self.stdout.write(self.style.SUCCESS('\n✅ Загрузка данных сорбции завершена!'))
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Всего загружено: {LeachingTest.objects.count()} тестов выщелачивания, {SorptionTest.objects.count()} тестов сорбции'))