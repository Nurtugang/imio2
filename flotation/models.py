from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class ReagentType(models.TextChoices):
    COLLECTOR = 'collector', 'Собиратель'
    FROTHER = 'frother', 'Пенообразователь'
    ACTIVATOR = 'activator', 'Активатор'
    EXPERIMENTAL = 'experimental', 'Экспериментальный'

class Reagent(models.Model):
    """Модель реагента"""
    name = models.CharField('Название', max_length=100, unique=True)
    type = models.CharField('Тип', max_length=20, choices=ReagentType.choices)
    description = models.TextField('Описание', blank=True)
    
    # Дозировки
    dosage_min = models.FloatField('Мин. дозировка (г/т)', validators=[MinValueValidator(0)])
    dosage_max = models.FloatField('Макс. дозировка (г/т)', validators=[MinValueValidator(0)])
    dosage_cleaner_min = models.FloatField('Мин. дозировка перечистки (г/т)', null=True, blank=True)
    dosage_cleaner_max = models.FloatField('Макс. дозировка перечистки (г/т)', null=True, blank=True)
    
    # Характеристики
    average_extraction = models.FloatField('Среднее извлечение (%)', null=True, blank=True, 
                                         validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_extraction = models.FloatField('Максимальное извлечение (%)', null=True, blank=True,
                                     validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Свойства
    is_standard = models.BooleanField('Стандартный', default=True)
    is_high_efficiency = models.BooleanField('Высокая эффективность', default=False)
    is_experimental = models.BooleanField('Экспериментальный', default=False)
    
    # Дополнительные параметры
    working_ph_min = models.FloatField('Мин. рабочий pH', null=True, blank=True)
    working_ph_max = models.FloatField('Макс. рабочий pH', null=True, blank=True)
    
    # Метаданные
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Реагент'
        verbose_name_plural = 'Реагенты'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    @property
    def icon(self):
        """Иконка реагента в зависимости от типа"""
        icons = {
            'collector': '🔹',
            'frother': '🫧',
            'activator': '⚡',
            'experimental': '🧬'
        }
        return icons.get(self.type, '🧪')
    
    @property
    def tags(self):
        """Теги реагента"""
        tags = []
        if self.is_standard:
            tags.append(('Стандартный', 'standard'))
        if self.is_high_efficiency:
            tags.append(('Высокая эффективность', 'high-efficiency'))
        if self.is_experimental:
            tags.append(('Экспериментальный', 'experimental'))
        
        # Дополнительные теги на основе данных
        if self.max_extraction and self.max_extraction > 95:
            tags.append(('Рекордсмен', 'record'))
        if self.type == 'experimental':
            tags.append(('MP Серия', 'mp-series'))
            
        return tags
    
    @property
    def dosage_range(self):
        """Диапазон дозировок для отображения"""
        if self.dosage_cleaner_min and self.dosage_cleaner_max:
            return {
                'main': f"{self.dosage_min}-{self.dosage_max}",
                'cleaner': f"{self.dosage_cleaner_min}-{self.dosage_cleaner_max}"
            }
        return {
            'main': f"{self.dosage_min}-{self.dosage_max}",
            'cleaner': None
        }


class FlotationTest(models.Model):
    """Модель флотационного теста"""
    number = models.IntegerField('Номер теста', unique=True)
    date_conducted = models.DateField('Дата проведения', auto_now_add=True)
    
    # Исходные данные
    initial_grade_analysis = models.FloatField('Исходное содержание по анализу (г/т)')
    calculated_initial_grade = models.FloatField('Расчетное исходное содержание (г/т)')
    
    # Реагентный режим
    reagent_regime = models.TextField('Реагентный режим')
    is_microflotation = models.BooleanField('Микрофлотация', default=False)
    
    # Категория теста
    configuration = models.CharField('Конфигурация', max_length=50, blank=True)
    
    @property
    def extraction(self):
        """Рассчитанное извлечение"""
        useful_products = self.products.exclude(product_type='tails')
        total_au = self.products.aggregate(total=models.Sum('au_content'))['total'] or 0
        useful_au = useful_products.aggregate(total=models.Sum('au_content'))['total'] or 0
        return (useful_au / total_au * 100) if total_au > 0 else 0
    
    @property 
    def concentrate_yield(self):
        """Рассчитанный выход концентрата"""
        concentrate = self.products.filter(product_type='final_concentrate').first()
        total_mass = self.products.aggregate(total=models.Sum('mass'))['total'] or 0
        return (concentrate.mass / total_mass * 100) if concentrate and total_mass > 0 else 0
    
    @property
    def efficiency(self):
        """Рассчитанная эффективность"""
        extraction = self.extraction
        yield_val = self.concentrate_yield
        initial = self.initial_grade_analysis
        return ((extraction - yield_val) / (100 - initial) * 100) if initial != 100 else 0
    
    class Meta:
        verbose_name = 'Флотационный тест'
        verbose_name_plural = 'Флотационные тесты'
        ordering = ['number']
    
    def __str__(self):
        return f"Тест №{self.number} - {self.extraction}% извлечение"


class FlotationProduct(models.Model):
    """Продукты флотации"""
    test = models.ForeignKey(FlotationTest, on_delete=models.CASCADE, related_name='products')
    name = models.CharField('Название продукта', max_length=100)
    mass = models.FloatField('Масса (г)')
    grade = models.FloatField('Содержание (г/т)')
    au_content = models.FloatField('Содержание Au (мкг)')
    
    product_type = models.CharField('Тип продукта', max_length=20, choices=[
        ('final_concentrate', 'Финальный концентрат'),
        ('tails', 'Отвальные хвосты'),
        ('cleaner_tails', 'Хвосты перечистки'),
        ('control_concentrate', 'Концентрат контрольной')
    ])
    
    class Meta:
        verbose_name = 'Продукт флотации'
        verbose_name_plural = 'Продукты флотации'
    
    def __str__(self):
        return f"{self.test.number} - {self.name}"
