from django.shortcuts import render

def home(request):
    """Главная страница"""
    context = {
        'stats': {
            'total_tests': 132,
            'best_extraction': 97.4,
            'configurations': 5,
            'reagents_count': 15,
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
                'name': 'Утилизация',
                'icon': '⚗️',
                'description': 'Анализатор зеленой утилизации медных отвалов',
                'status': 'active',
                'url': 'core:copper'
            },
            {
                'name': 'Процесс 3',
                'icon': '🔥',
                'description': 'Третий металлургический процесс. Планируется к разработке в следующих версиях платформы.',
                'status': 'coming',
                'url': '#'
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