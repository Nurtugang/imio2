from django.contrib import admin
from .models import LeachingTest, LeachingProduct, SorptionTest


@admin.register(LeachingTest)
class LeachingTestAdmin(admin.ModelAdmin):
    list_display = [
        'number',
        'acid_type',
        'has_oxygen',
        'temperature',
        'duration',
        'concentrate_mass',
        'mo_extraction_to_solution',
        'date_conducted'
    ]
    list_filter = [
        'acid_type',
        'has_oxygen',
        'temperature',
        'date_conducted'
    ]
    search_fields = ['number']
    ordering = ['number']
    
    fieldsets = (
        ('Идентификация', {
            'fields': ('number', 'date_conducted')
        }),
        ('Исходный материал', {
            'fields': (
                'concentrate_mass',
                ('initial_mo', 'initial_cu'),
                ('initial_fe', 'initial_si')
            )
        }),
        ('Условия выщелачивания', {
            'fields': (
                'acid_type',
                ('hno3_concentration', 'h2so4_concentration'),
                'solution_volume',
                ('temperature', 'duration'),
                'stirring_speed',
                ('has_oxygen', 'oxygen_flow')
            )
        })
    )
    
    readonly_fields = ['date_conducted']


@admin.register(LeachingProduct)
class LeachingProductAdmin(admin.ModelAdmin):
    list_display = [
        'test',
        'product_type',
        'mass_or_volume',
        'mo_content',
        'mo_extraction',
        'cu_extraction',
        'fe_extraction'
    ]
    list_filter = ['product_type', 'test__acid_type']
    search_fields = ['test__number']
    ordering = ['test__number', 'product_type']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('test', 'product_type', 'mass_or_volume', 'yield_percentage')
        }),
        ('Содержания элементов (%/г/л)', {
            'fields': (
                ('mo_content', 'cu_content'),
                ('fe_content', 'si_content')
            )
        }),
        ('Количество элементов (г)', {
            'fields': (
                ('mo_grams', 'cu_grams'),
                ('fe_grams', 'si_grams')
            )
        }),
        ('Извлечения (%)', {
            'fields': (
                ('mo_extraction', 'cu_extraction'),
                ('fe_extraction', 'si_extraction')
            )
        })
    )


@admin.register(SorptionTest)
class SorptionTestAdmin(admin.ModelAdmin):
    list_display = [
        'number',
        'anionite_type',
        'temperature',
        'duration',
        'initial_mo_concentration',
        'mo_extraction',
        'sorption_capacity',
        'date_conducted'
    ]
    list_filter = [
        'anionite_type',
        'temperature',
        'date_conducted'
    ]
    search_fields = ['number']
    ordering = ['number']
    
    fieldsets = (
        ('Идентификация', {
            'fields': ('number', 'leaching_test', 'date_conducted')
        }),
        ('Раствор', {
            'fields': (
                'solution_volume',
                ('initial_mo_concentration', 'final_mo_concentration'),
                'h2so4_concentration'
            )
        }),
        ('Анионит', {
            'fields': (
                'anionite_type',
                'anionite_mass'
            )
        }),
        ('Условия', {
            'fields': (
                ('temperature', 'duration'),
                'stirring_speed'
            )
        }),
        ('Результаты', {
            'fields': (
                'mo_extraction',
                'sorption_capacity',
                'mo_on_anionite'
            )
        })
    )
    
    readonly_fields = ['date_conducted']