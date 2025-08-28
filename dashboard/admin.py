from django.contrib import admin
from .models import Country, Indicator, CountryData, HappinessData


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'region_value', 'income_level_value', 'capital_city']
    list_filter = ['region_value', 'income_level_value']
    search_fields = ['name', 'id', 'iso2_code']
    ordering = ['name']


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'unit', 'source_value']
    list_filter = ['source_value']
    search_fields = ['name', 'id']
    ordering = ['name']


@admin.register(CountryData)
class CountryDataAdmin(admin.ModelAdmin):
    list_display = ['country', 'indicator', 'date', 'value']
    list_filter = ['country', 'indicator', 'date']
    search_fields = ['country__name', 'indicator__name']
    ordering = ['country', 'indicator', 'date']


@admin.register(HappinessData)
class HappinessDataAdmin(admin.ModelAdmin):
    list_display = ['country_name', 'year', 'ladder_score', 'region']
    list_filter = ['year', 'region']
    search_fields = ['country_name']
    ordering = ['-ladder_score', 'year']