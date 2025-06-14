from django.core.management.base import BaseCommand
from flotation.models import Reagent

class Command(BaseCommand):
    help = 'Загружает базовые реагенты в базу данных'
    
    def handle(self, *args, **options):
        reagents_data = [
            {
                'name': 'PAX',
                'type': 'collector',
                'description': 'Ксантогенат амилкалия - основной собиратель для сульфидных руд. Обеспечивает высокую селективность извлечения.',
                'dosage_min': 75,
                'dosage_max': 200,
                'dosage_cleaner_min': 25,
                'dosage_cleaner_max': 100,
                'average_extraction': 85.0,
                'max_extraction': 91.2,
                'is_standard': True,
                'is_high_efficiency': True,
            },
            {
                'name': 'X-133',
                'type': 'frother',
                'description': 'Метилизобутилкарбинол - универсальный пенообразователь, обеспечивающий стабильную пену и хорошую селективность.',
                'dosage_min': 3,
                'dosage_max': 50,
                'dosage_cleaner_min': 3,
                'dosage_cleaner_max': 50,
                'average_extraction': 86.2,
                'max_extraction': 89.5,
                'is_standard': True,
            },
            {
                'name': 'CuSO4',
                'type': 'activator',
                'description': 'Медный купорос - активатор для цинковых минералов. Улучшает флотируемость сфалерита и других сульфидов цинка.',
                'dosage_min': 20,
                'dosage_max': 40,
                'average_extraction': 84.7,
                'max_extraction': 86.9,
                'working_ph_min': 8.0,
                'working_ph_max': 11.0,
                'is_standard': True,
                'is_high_efficiency': True,
            },
            {
                'name': 'MP-1',
                'type': 'experimental',
                'description': 'Инновационный реагент серии MP. Показал рекордные результаты извлечения до 97.4% в тесте №55.',
                'dosage_min': 5,
                'dosage_max': 30,
                'dosage_cleaner_min': 5,
                'dosage_cleaner_max': 30,
                'average_extraction': 88.0,
                'max_extraction': 97.4,
                'is_experimental': True,
                'is_high_efficiency': True,
            },
            {
                'name': 'БТФ',
                'type': 'collector',
                'description': 'Дополнительный собиратель для повышения селективности флотации. Используется в комбинированных режимах.',
                'dosage_min': 25,
                'dosage_max': 50,
                'dosage_cleaner_min': 25,
                'dosage_cleaner_max': 50,
                'average_extraction': 86.5,
                'max_extraction': 87.4,
            },
            {
                'name': 'MP-102',
                'type': 'experimental',
                'description': 'Реагент серии MP для микрофлотации. Показывает стабильные результаты в малых дозировках.',
                'dosage_min': 5,
                'dosage_max': 20,
                'dosage_cleaner_min': 5,
                'dosage_cleaner_max': 20,
                'average_extraction': 84.7,
                'max_extraction': 86.2,
                'is_experimental': True,
            },
        ]
        
        for reagent_data in reagents_data:
            reagent, created = Reagent.objects.get_or_create(
                name=reagent_data['name'],
                defaults=reagent_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Создан реагент: {reagent.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Реагент уже существует: {reagent.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Загрузка реагентов завершена!')
        )