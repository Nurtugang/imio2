import json
import os
from django.core.management.base import BaseCommand
from flotation.models import FlotationTest, FlotationProduct
from flotation.views import calculate_flotation_results, save_flotation_test

class Command(BaseCommand):
    help = 'Импортирует тесты из нового чистого JSON файла и рассчитывает показатели'

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str, help='Путь к новому JSON файлу с экспериментами')

    def handle(self, *args, **options):
        json_path = options['json_path']
        
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f"Файл не найден: {json_path}"))
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.stdout.write(self.style.SUCCESS(f"Загружено {len(data)} записей"))
        
        for entry in data:
            try:
                calc_data = {
                    'initial_grade_analysis': self._to_float(entry.get('initial_grade_analysis')),
                    'calculated_initial_grade': self._to_float(entry.get('calculated_initial_grade')),
                    'reagent_regime': 'Импорт из JSON',
                    'is_microflotation': False,
                    'configuration': '',
                    
                    'final_concentrate': {
                        'mass': self._to_float(entry.get('final_concentrate_mass')),
                        'grade': self._to_float(entry.get('final_concentrate_grade')),
                    },
                    'tails': {
                        'mass': self._to_float(entry.get('tails_mass')),
                        'grade': self._to_float(entry.get('tails_grade')),
                    },
                    'cleaner_tails': {
                        'mass': self._to_float(entry.get('cleaner_tails_mass')),
                        'grade': self._to_float(entry.get('cleaner_tails_grade')),
                    },
                    'control_concentrate': {
                        'mass': self._to_float(entry.get('control_concentrate_mass')),
                        'grade': self._to_float(entry.get('control_concentrate_grade')),
                    },
                }

                results = calculate_flotation_results(calc_data)
                test = save_flotation_test(calc_data, results)
                self.stdout.write(self.style.SUCCESS(f"Тест №{test.number} успешно создан"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Ошибка при обработке записи: {e}"))
    
    def _to_float(self, value):
        if value is None:
            return 0.0
        if isinstance(value, str):
            value = value.replace(',', '.').replace('%', '').strip()
        try:
            return float(value)
        except:
            return 0.0
