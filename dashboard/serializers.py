from rest_framework import serializers
from .models import Country, Indicator, CountryData, HappinessData


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            'id', 'name', 'region_value', 'income_level_value', 
            'capital_city', 'longitude', 'latitude'
        ]


class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        fields = ['id', 'name', 'unit', 'source_value', 'source_organization']


class CountryDataSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    year = serializers.SerializerMethodField()

    class Meta:
        model = CountryData
        fields = [
            'country', 'country_name', 'indicator', 'indicator_name', 
            'date', 'year', 'value', 'unit'
        ]
    
    def get_year(self, obj):
        return int(obj.date) if obj.date.isdigit() else None


class HappinessDataSerializer(serializers.ModelSerializer):
    country_code = serializers.CharField(source='country.id', read_only=True)

    class Meta:
        model = HappinessData
        fields = [
            'country_name', 'country_code', 'year', 'ladder_score', 
            'upper_whisker', 'lower_whisker', 'region',
            'explained_by_freedom_to_make_life_choices',
            'explained_by_generosity',
            'explained_by_perceptions_of_corruption',
            'dystopia_plus_residual',
            'explained_by_log_gdp_per_capita',
            'explained_by_social_support',
            'explained_by_healthy_life_expectancy'
        ]


class RegionalHappinessSerializer(serializers.Serializer):
    region = serializers.CharField()
    avg_ladder_score = serializers.DecimalField(max_digits=8, decimal_places=4)
    country_count = serializers.IntegerField()
    year = serializers.IntegerField()


class CountryTrendSerializer(serializers.Serializer):
    country = serializers.CharField()
    indicator = serializers.CharField()
    data = serializers.ListField(
        child=serializers.DictField(
            child=serializers.DecimalField(max_digits=20, decimal_places=4)
        )
    )