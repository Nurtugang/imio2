from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class LeachingTest(models.Model):
    """Тест выщелачивания молибденитового концентрата"""
    
    # === ИДЕНТИФИКАЦИЯ ===
    number = models.IntegerField('Номер опыта', unique=True)
    date_conducted = models.DateField('Дата проведения', auto_now_add=True)
    
    # === ИСХОДНЫЙ МАТЕРИАЛ ===
    concentrate_mass = models.FloatField(
        'Масса концентрата (г)',
        validators=[MinValueValidator(0)]
    )
    initial_mo = models.FloatField(
        'Исходное содержание Mo (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    initial_cu = models.FloatField(
        'Исходное содержание Cu (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    initial_fe = models.FloatField(
        'Исходное содержание Fe (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    initial_si = models.FloatField(
        'Исходное содержание Si (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # === УСЛОВИЯ ВЫЩЕЛАЧИВАНИЯ ===
    ACID_CHOICES = [
        ('hno3', 'HNO₃ (азотная кислота)'),
        ('h2so4', 'H₂SO₄ (серная кислота)'),
        ('mixed', 'HNO₃ + H₂SO₄ (смесь)')
    ]
    acid_type = models.CharField(
        'Тип кислоты',
        max_length=20,
        choices=ACID_CHOICES
    )
    hno3_concentration = models.FloatField(
        'Концентрация HNO₃ (г/л)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    h2so4_concentration = models.FloatField(
        'Концентрация H₂SO₄ (г/л)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    solution_volume = models.FloatField(
        'Объем раствора (мл)',
        validators=[MinValueValidator(0)]
    )
    temperature = models.FloatField(
        'Температура (°C)',
        validators=[MinValueValidator(0), MaxValueValidator(200)]
    )
    duration = models.FloatField(
        'Продолжительность (ч)',
        validators=[MinValueValidator(0)]
    )
    stirring_speed = models.FloatField(
        'Скорость перемешивания (об/мин)',
        validators=[MinValueValidator(0)]
    )
    has_oxygen = models.BooleanField('Продувка кислородом', default=False)
    oxygen_flow = models.FloatField(
        'Расход кислорода (дм³/мин)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # === МЕТАДАННЫЕ ===
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Тест выщелачивания'
        verbose_name_plural = 'Тесты выщелачивания'
        ordering = ['number']
    
    def __str__(self):
        return f"Опыт №{self.number} - {self.get_acid_type_display()}"
    
    @property
    def solid_liquid_ratio(self):
        """Соотношение Т:Ж"""
        if self.solution_volume and self.concentrate_mass:
            ratio = self.solution_volume / self.concentrate_mass
            return f"1:{ratio:.0f}"
        return "—"
    
    @property
    def mo_extraction_to_solution(self):
        """Извлечение Mo в раствор (%)"""
        solution = self.products.filter(product_type='solution').first()
        if solution:
            return solution.mo_extraction
        return 0
    
    @property
    def mo_extraction_to_cake(self):
        """Извлечение Mo в кек (%)"""
        cake = self.products.filter(product_type='cake').first()
        if cake:
            return cake.mo_extraction
        return 0


class LeachingProduct(models.Model):
    """Продукты выщелачивания (кек и раствор)"""
    
    test = models.ForeignKey(
        LeachingTest,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Тест'
    )
    
    PRODUCT_CHOICES = [
        ('cake', 'Кек'),
        ('solution', 'Раствор (фильтрат)')
    ]
    product_type = models.CharField(
        'Тип продукта',
        max_length=20,
        choices=PRODUCT_CHOICES
    )
    
    # === ДЛЯ КЕКА: масса в граммах, ДЛЯ РАСТВОРА: объем в мл ===
    mass_or_volume = models.FloatField(
        'Масса (г) / Объем (мл)',
        validators=[MinValueValidator(0)]
    )
    yield_percentage = models.FloatField(
        'Выход (%)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # === СОДЕРЖАНИЯ ЭЛЕМЕНТОВ ===
    # Для кека: в %, для раствора: в г/л
    mo_content = models.FloatField(
        'Содержание Mo (%/г/л)',
        validators=[MinValueValidator(0)]
    )
    cu_content = models.FloatField(
        'Содержание Cu (%/г/л)',
        validators=[MinValueValidator(0)]
    )
    fe_content = models.FloatField(
        'Содержание Fe (%/г/л)',
        validators=[MinValueValidator(0)]
    )
    si_content = models.FloatField(
        'Содержание Si (%/г/л)',
        validators=[MinValueValidator(0)]
    )
    
    # === РАСЧЕТНЫЕ ПОЛЯ (граммы элементов) ===
    mo_grams = models.FloatField('Количество Mo (г)', validators=[MinValueValidator(0)])
    cu_grams = models.FloatField('Количество Cu (г)', validators=[MinValueValidator(0)])
    fe_grams = models.FloatField('Количество Fe (г)', validators=[MinValueValidator(0)])
    si_grams = models.FloatField('Количество Si (г)', validators=[MinValueValidator(0)])
    
    # === ИЗВЛЕЧЕНИЯ (%) ===
    mo_extraction = models.FloatField(
        'Извлечение Mo (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    cu_extraction = models.FloatField(
        'Извлечение Cu (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    fe_extraction = models.FloatField(
        'Извлечение Fe (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    si_extraction = models.FloatField(
        'Извлечение Si (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    class Meta:
        verbose_name = 'Продукт выщелачивания'
        verbose_name_plural = 'Продукты выщелачивания'
        unique_together = ['test', 'product_type']
    
    def __str__(self):
        return f"{self.test.number} - {self.get_product_type_display()}"


class SorptionTest(models.Model):
    """Тест сорбции молибдена на анионитах"""
    
    # === СВЯЗЬ С ВЫЩЕЛАЧИВАНИЕМ (опционально) ===
    leaching_test = models.ForeignKey(
        LeachingTest,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Тест выщелачивания'
    )
    
    # === ИДЕНТИФИКАЦИЯ ===
    number = models.IntegerField('Номер опыта', unique=True)
    date_conducted = models.DateField('Дата проведения', auto_now_add=True)
    
    # === РАСТВОР ===
    solution_volume = models.FloatField(
        'Объем раствора (мл)',
        validators=[MinValueValidator(0)]
    )
    initial_mo_concentration = models.FloatField(
        'Начальная концентрация Mo (г/л)',
        validators=[MinValueValidator(0)]
    )
    final_mo_concentration = models.FloatField(
        'Концентрация Mo после сорбции (г/л)',
        validators=[MinValueValidator(0)]
    )
    h2so4_concentration = models.FloatField(
        'Концентрация H₂SO₄ (г/л)',
        validators=[MinValueValidator(0)]
    )
    
    # === АНИОНИТ ===
    ANIONITE_CHOICES = [
        ('ankf10b', 'АНКФ-10Б(ОН)'),
        ('lewatit_m800', 'Lewatit MonoPlus M800'),
        ('ab17', 'AB-17'),
        ('ira95', 'IRA-95'),
        ('purolite_a100', 'Purolite A100')
    ]
    anionite_type = models.CharField(
        'Тип анионита',
        max_length=50,
        choices=ANIONITE_CHOICES
    )
    anionite_mass = models.FloatField(
        'Масса анионита (г)',
        validators=[MinValueValidator(0)]
    )
    
    # === УСЛОВИЯ ===
    temperature = models.FloatField(
        'Температура (°C)',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    duration = models.FloatField(
        'Продолжительность (мин)',
        validators=[MinValueValidator(0)]
    )
    stirring_speed = models.FloatField(
        'Скорость перемешивания (об/мин)',
        default=200,
        validators=[MinValueValidator(0)]
    )
    
    # === РЕЗУЛЬТАТЫ (рассчитываются автоматически) ===
    mo_extraction = models.FloatField(
        'Извлечение Mo на сорбент (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    sorption_capacity = models.FloatField(
        'Сорбционная емкость (г-атом/г)',
        validators=[MinValueValidator(0)]
    )
    mo_on_anionite = models.FloatField(
        'Количество Mo на анионите (г)',
        validators=[MinValueValidator(0)]
    )
    
    # === МЕТАДАННЫЕ ===
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Тест сорбции'
        verbose_name_plural = 'Тесты сорбции'
        ordering = ['number']
    
    def __str__(self):
        return f"Опыт №{self.number} - {self.get_anionite_type_display()}"
    
    @property
    def mo_removed_from_solution(self):
        """Удалено Mo из раствора (г/л)"""
        return self.initial_mo_concentration - self.final_mo_concentration