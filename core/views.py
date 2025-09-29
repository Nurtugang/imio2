from django.shortcuts import render

def home(request):
    """Главная страница"""
    context = {
        'stats': {
            'total_tests': 132 + 6,  # флотация + выщелачивание
            'best_extraction': 97.4,
            'configurations': 5 + 6,  # флотация + молибден
            'reagents_count': 15 + 5,  # флотация + анионитов
        },
        'processes': [
            {
                'name': 'Флотация',
                'icon': '🧪',
                'description': 'Анализ флотационных тестов, оптимизация реагентных режимов, расчет эффективности извлечения ценных компонентов.',
                'status': 'active',
                'url': 'flotation:dashboard'
            },
            {
                'name': 'Утилизация медных отвалов',
                'icon': '🌱',
                'description': 'Анализатор зеленой утилизации медных отвалов с био-гидрометаллургическими технологиями.',
                'status': 'active',
                'url': 'core:copper'
            },
            {
                'name': 'Переработка молибденита',  # ← НОВЫЙ ПРОЦЕСС
                'icon': '⚗️',
                'description': 'Гидрометаллургическая переработка молибденитовых концентратов: кислотное выщелачивание и сорбционное извлечение.',
                'status': 'active',
                'url': 'molybdenum:dashboard'
            },
            {
                'name': 'Процесс 4',
                'icon': '🏭',
                'description': 'Четвертый металлургический процесс. Будет реализован после сбора требований и данных.',
                'status': 'coming',
                'url': '#'
            },
        ]
    }
    return render(request, 'core/home.html', context)

def knowledge_base(request):
    """База знаний"""
    return render(request, 'core/knowledge_base.html')

def reports(request):
    """Отчеты"""
    return render(request, 'core/reports.html')

def copper(request):
    """Медь"""
    return render(request, 'core/copper.html')