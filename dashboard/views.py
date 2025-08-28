from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Avg, Count
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
import logging
import traceback

from .models import Country, Indicator, CountryData, HappinessData
from .serializers import (
    CountrySerializer, IndicatorSerializer, CountryDataSerializer,
    HappinessDataSerializer, RegionalHappinessSerializer
)

logger = logging.getLogger('dashboard')


# Template Views
class DashboardHomeView(TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get some basic statistics for the dashboard
        context.update({
            'total_countries': Country.objects.count(),
            'total_indicators': Indicator.objects.count(),
            'happiness_years': HappinessData.objects.values_list('year', flat=True).distinct().order_by('year'),
            'regions': Country.objects.values_list('region_value', flat=True).distinct().exclude(region_value=''),
        })
        
        return context


class CountryTrendsView(TemplateView):
    template_name = 'dashboard/country_trends.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'countries': Country.objects.all().order_by('name'),
            'indicators': Indicator.objects.all().order_by('name'),
        })
        return context


class HappinessCorrelationView(TemplateView):
    template_name = 'dashboard/happiness_correlation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'countries': Country.objects.all().order_by('name'),
            'indicators': Indicator.objects.all().order_by('name'),
            'years': list(range(2020, 2026)),
        })
        return context


class RegionalHappinessView(TemplateView):
    template_name = 'dashboard/regional_happiness.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'regions': Country.objects.values_list('region_value', flat=True).distinct().exclude(region_value=''),
            'years': list(range(2020, 2026)),
        })
        return context


class RegionalComparisonView(TemplateView):
    template_name = 'dashboard/regional_comparison.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'regions': Country.objects.values_list('region_value', flat=True).distinct().exclude(region_value=''),
            'indicators': Indicator.objects.all().order_by('name'),
            'years': list(range(2020, 2026)),
        })
        return context


# API ViewSets
class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all().order_by('name')
    serializer_class = CountrySerializer
    
    @action(detail=False, methods=['get'])
    def by_region(self, request):
        region = request.query_params.get('region')
        if region:
            queryset = self.queryset.filter(region_value=region)
        else:
            queryset = self.queryset
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class IndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Indicator.objects.all().order_by('name')
    serializer_class = IndicatorSerializer


class HappinessDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HappinessData.objects.all().order_by('-ladder_score', 'year')
    serializer_class = HappinessDataSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
        
        # Filter by region
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(region=region)
        
        # Filter by country
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country__id=country)
        
        return queryset


# API Views
class CountryIndicatorDataView(APIView):
    """Get time series data for a specific country and indicator"""
    
    def get(self, request, country_code, indicator_code):
        logger.info(f"CountryIndicatorDataView called with country: {country_code}, indicator: {indicator_code}")
        
        try:
            # Check if country exists
            try:
                country = Country.objects.get(id=country_code)
                logger.info(f"Found country: {country.name}")
            except Country.DoesNotExist:
                logger.error(f"Country not found: {country_code}")
                available_countries = list(Country.objects.values_list('id', 'name')[:10])
                logger.info(f"Available countries (first 10): {available_countries}")
                return Response(
                    {'error': f'Country not found: {country_code}', 'available_countries': available_countries}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if indicator exists
            try:
                indicator = Indicator.objects.get(id=indicator_code)
                logger.info(f"Found indicator: {indicator.name}")
            except Indicator.DoesNotExist:
                logger.error(f"Indicator not found: {indicator_code}")
                available_indicators = list(Indicator.objects.values_list('id', 'name'))
                logger.info(f"Available indicators: {available_indicators}")
                return Response(
                    {'error': f'Indicator not found: {indicator_code}', 'available_indicators': available_indicators}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get the data
            data = CountryData.objects.filter(
                country=country,
                indicator=indicator
            ).order_by('date')
            
            logger.info(f"Found {data.count()} data points for {country.name} - {indicator.name}")
            
            if data.count() == 0:
                logger.warning(f"No data found for {country.name} - {indicator.name}")
                # Show what data is available for this country
                available_data = CountryData.objects.filter(country=country).values_list('indicator__name', flat=True).distinct()
                logger.info(f"Available indicators for {country.name}: {list(available_data)}")
                return Response({
                    'error': 'No data available for this country/indicator combination',
                    'country': country.name,
                    'indicator': indicator.name,
                    'available_indicators_for_country': list(available_data)
                })
            
            serializer = CountryDataSerializer(data, many=True)
            logger.info(f"Serialized data successfully, returning {len(serializer.data)} records")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Unexpected error in CountryIndicatorDataView: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CountryHappinessDataView(APIView):
    """Get happiness data for a specific country across all years"""
    
    def get(self, request, country_code):
        try:
            country = Country.objects.get(id=country_code)
        except Country.DoesNotExist:
            return Response(
                {'error': 'Country not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Try to get data by mapped country first, then by country name
        happiness_data = HappinessData.objects.filter(country=country).order_by('year')
        
        if not happiness_data.exists():
            # Fallback to country name matching
            happiness_data = HappinessData.objects.filter(
                country_name=country.name
            ).order_by('year')
        
        serializer = HappinessDataSerializer(happiness_data, many=True)
        return Response(serializer.data)


class RegionalHappinessAPIView(APIView):
    """Get regional happiness statistics"""
    
    def get(self, request):
        logger.info(f"RegionalHappinessAPIView called with params: {request.query_params}")
        
        try:
            year = request.query_params.get('year')
            
            # Since HappinessData.region is empty, we need to join with Country model
            # to get region information from World Bank data
            queryset = HappinessData.objects.select_related('country').filter(
                country__isnull=False,
                country__region_value__isnull=False
            ).exclude(country__region_value='')
            
            logger.info(f"Initial queryset count (with country regions): {queryset.count()}")
            
            if year:
                queryset = queryset.filter(year=year)
                logger.info(f"Filtered queryset for year {year}: {queryset.count()}")
            
            # Group by country region and year, calculate averages
            regional_data = queryset.values('country__region_value', 'year').annotate(
                avg_ladder_score=Avg('ladder_score'),
                country_count=Count('id')
            ).order_by('country__region_value', 'year')
            
            logger.info(f"Regional data aggregation result: {len(regional_data)} records")
            
            if len(regional_data) == 0:
                logger.warning("No regional data found")
                # Show what happiness data is available
                available_regions = list(Country.objects.exclude(region_value='').values_list('region_value', flat=True).distinct())
                available_years = list(HappinessData.objects.values_list('year', flat=True).distinct())
                logger.info(f"Available regions: {available_regions}")
                logger.info(f"Available years: {available_years}")
                return Response({
                    'error': 'No regional happiness data found',
                    'available_regions': available_regions,
                    'available_years': available_years
                })
            
            # Transform the data to match the expected format
            transformed_data = []
            for item in regional_data:
                transformed_data.append({
                    'region': item['country__region_value'],
                    'year': item['year'],
                    'avg_ladder_score': item['avg_ladder_score'],
                    'country_count': item['country_count']
                })
            
            logger.info(f"Transformed regional data successfully, returning {len(transformed_data)} records")
            return Response(transformed_data)
            
        except Exception as e:
            logger.error(f"Unexpected error in RegionalHappinessAPIView: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegionalIndicatorDataView(APIView):
    """Get indicator data for all countries in a region for a specific year"""
    
    def get(self, request, region, indicator_code, year):
        try:
            indicator = Indicator.objects.get(id=indicator_code)
        except Indicator.DoesNotExist:
            return Response(
                {'error': 'Indicator not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get countries in the region
        countries = Country.objects.filter(region_value=region)
        
        # Get indicator data for these countries
        data = CountryData.objects.filter(
            country__in=countries,
            indicator=indicator,
            date=str(year)
        ).select_related('country').order_by('-value')
        
        serializer = CountryDataSerializer(data, many=True)
        return Response(serializer.data)