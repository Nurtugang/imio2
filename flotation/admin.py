from django.contrib import admin
from .models import Reagent, FlotationTest, FlotationProduct

@admin.register(Reagent)
class ReagentAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'dosage_min', 'dosage_max', 'average_extraction', 'is_experimental']
    list_filter = ['type', 'is_experimental', 'is_high_efficiency']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(FlotationTest)
class FlotationTestAdmin(admin.ModelAdmin):
    list_display = ['number', 'extraction', 'efficiency', 'concentrate_yield', 'is_microflotation', 'configuration']
    list_filter = ['is_microflotation', 'configuration']
    search_fields = ['number', 'reagent_regime']
    ordering = ['-number']

@admin.register(FlotationProduct)
class FlotationProductAdmin(admin.ModelAdmin):
    list_display = ['test', 'name', 'mass', 'grade', 'au_content']
    list_filter = ['name']
    search_fields = ['test__number', 'name']