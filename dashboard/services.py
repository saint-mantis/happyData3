import requests
import pandas as pd
import logging
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, List, Any
from django.core.cache import cache
from django.conf import settings
from .models import Country, Indicator, CountryData, HappinessData, COUNTRY_NAME_TO_CODE_MAPPING

logger = logging.getLogger(__name__)


class WorldBankAPIService:
    """Service for interacting with World Bank APIs"""
    
    BASE_URL = "https://api.worldbank.org/v2"
    CACHE_TIMEOUT = 3600  # 1 hour
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HappyData-Dashboard/1.0'
        })

    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to World Bank API with error handling"""
        try:
            params = params or {}
            params.update({'format': 'json', 'per_page': 1000})
            
            logger.info(f"Making request to: {url}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if len(data) >= 2:
                return data
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except ValueError as e:
            logger.error(f"JSON parsing failed: {e}")
            return None

    def fetch_countries(self) -> List[Dict]:
        """Fetch all countries from World Bank API"""
        cache_key = 'wb_countries'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        url = f"{self.BASE_URL}/country"
        response_data = self._make_request(url)
        
        if not response_data:
            return []

        countries = []
        for country in response_data[1]:  # Skip metadata
            # Filter out aggregates
            if country.get('region', {}).get('value') == 'Aggregates':
                continue
                
            try:
                country_data = {
                    'id': country['id'],
                    'iso2_code': country.get('iso2Code', ''),
                    'name': country['name'],
                    'capital_city': country.get('capitalCity', ''),
                    'longitude': self._safe_decimal(country.get('longitude')),
                    'latitude': self._safe_decimal(country.get('latitude')),
                    'region_id': country.get('region', {}).get('id', '') if country.get('region') else '',
                    'region_value': country.get('region', {}).get('value', '') if country.get('region') else '',
                    'admin_region_id': country.get('adminregion', {}).get('id', '') if country.get('adminregion') else '',
                    'admin_region_value': country.get('adminregion', {}).get('value', '') if country.get('adminregion') else '',
                    'income_level_id': country.get('incomeLevel', {}).get('id', '') if country.get('incomeLevel') else '',
                    'income_level_value': country.get('incomeLevel', {}).get('value', '') if country.get('incomeLevel') else '',
                    'lending_type_id': country.get('lendingType', {}).get('id', '') if country.get('lendingType') else '',
                    'lending_type_value': country.get('lendingType', {}).get('value', '') if country.get('lendingType') else '',
                }
                countries.append(country_data)
            except Exception as e:
                logger.error(f"Error processing country {country.get('name', 'Unknown')}: {e}")
                continue

        cache.set(cache_key, countries, self.CACHE_TIMEOUT)
        return countries

    def fetch_indicators(self) -> List[Dict]:
        """Fetch key indicators for happiness analysis"""
        indicators_to_fetch = [
            'NY.GDP.PCAP.CD',  # GDP per capita (current US$)
            'NY.GDP.PCAP.PP.CD',  # GDP per capita, PPP (current international $)
            'SI.POV.GINI',  # GINI index
            'SP.DYN.LE00.IN',  # Life expectancy at birth
            'SH.XPD.CHEX.GD.ZS',  # Current health expenditure (% of GDP)
            'SE.XPD.TOTL.GD.ZS',  # Government expenditure on education (% of GDP)
            'SL.UEM.TOTL.ZS',  # Unemployment rate
            'EN.ATM.CO2E.PC',  # CO2 emissions (metric tons per capita)
            'IT.NET.USER.ZS',  # Internet users (% of population)
            'SP.URB.TOTL.IN.ZS',  # Urban population (% of total)
        ]

        cache_key = 'wb_indicators'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        indicators = []
        for indicator_id in indicators_to_fetch:
            url = f"{self.BASE_URL}/indicator/{indicator_id}"
            response_data = self._make_request(url)
            
            if response_data and len(response_data) >= 2:
                indicator_info = response_data[1][0]  # Get first (only) result
                try:
                    indicator_data = {
                        'id': indicator_info['id'],
                        'name': indicator_info['name'],
                        'unit': indicator_info.get('unit', ''),
                        'source_id': indicator_info.get('source', {}).get('id', '') if indicator_info.get('source') else '',
                        'source_value': indicator_info.get('source', {}).get('value', '') if indicator_info.get('source') else '',
                        'source_note': indicator_info.get('sourceNote', ''),
                        'source_organization': indicator_info.get('sourceOrganization', ''),
                    }
                    indicators.append(indicator_data)
                except Exception as e:
                    logger.error(f"Error processing indicator {indicator_id}: {e}")
                    continue

        cache.set(cache_key, indicators, self.CACHE_TIMEOUT)
        return indicators

    def fetch_country_indicator_data(self, country_code: str, indicator_code: str, 
                                   start_year: int = 2020, end_year: int = 2025) -> List[Dict]:
        """Fetch indicator data for a specific country"""
        cache_key = f'wb_data_{country_code}_{indicator_code}_{start_year}_{end_year}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        url = f"{self.BASE_URL}/country/{country_code}/indicator/{indicator_code}"
        params = {'date': f'{start_year}:{end_year}'}
        response_data = self._make_request(url, params)
        
        if not response_data:
            return []

        data_points = []
        for record in response_data[1]:  # Skip metadata
            if record['value'] is not None:
                try:
                    data_point = {
                        'country_id': record['country']['id'],
                        'country_iso3_code': record.get('countryiso3code', ''),
                        'indicator_id': record['indicator']['id'],
                        'date': record['date'],
                        'value': self._safe_decimal(record['value']),
                        'unit': record.get('unit', ''),
                        'obs_status': record.get('obs_status', ''),
                        'decimal_places': record.get('decimal', 0)
                    }
                    data_points.append(data_point)
                except Exception as e:
                    logger.error(f"Error processing data point: {e}")
                    continue

        cache.set(cache_key, data_points, self.CACHE_TIMEOUT // 2)  # Shorter cache for data
        return data_points

    def _safe_decimal(self, value) -> Optional[Decimal]:
        """Safely convert value to Decimal"""
        if value is None or value == '':
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None


class HappinessDataService:
    """Service for processing World Happiness Report Excel data"""
    
    def __init__(self, excel_file_path: str):
        self.excel_file_path = excel_file_path

    def process_happiness_excel_file(self) -> List[Dict]:
        """Load and process World Happiness Report Excel file"""
        try:
            logger.info(f"Loading happiness data from: {self.excel_file_path}")
            
            # Try reading the Excel file (could be single sheet or multiple sheets)
            excel_file = pd.ExcelFile(self.excel_file_path)
            logger.info(f"Excel sheets found: {excel_file.sheet_names}")
            
            all_data = []
            
            # If there's only one sheet, assume it contains all years
            if len(excel_file.sheet_names) == 1:
                df = pd.read_excel(self.excel_file_path, sheet_name=0)
                all_data = self._process_dataframe(df)
            else:
                # Multiple sheets, process each one
                for sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(self.excel_file_path, sheet_name=sheet_name)
                        sheet_data = self._process_dataframe(df, sheet_name)
                        all_data.extend(sheet_data)
                    except Exception as e:
                        logger.error(f"Error processing sheet {sheet_name}: {e}")
                        continue
            
            logger.info(f"Processed {len(all_data)} happiness data records")
            return all_data
            
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            return []

    def _process_dataframe(self, df: pd.DataFrame, sheet_name: str = None) -> List[Dict]:
        """Process a single DataFrame from Excel"""
        data_records = []
        
        # Standardize column names
        df.columns = df.columns.str.strip()
        
        # Check if 'Year' column exists, if not try to infer from sheet name
        if 'Year' not in df.columns and sheet_name:
            # Try to extract year from sheet name (e.g., "2020", "Data2021", etc.)
            import re
            year_match = re.search(r'(\d{4})', sheet_name)
            if year_match:
                df['Year'] = int(year_match.group(1))
            else:
                logger.warning(f"Could not determine year for sheet: {sheet_name}")
                return []
        
        # Filter for years 2020-2025
        if 'Year' in df.columns:
            df = df[df['Year'].between(2020, 2025)]
        
        for _, row in df.iterrows():
            try:
                country_name = str(row.get('Country name', '')).strip()
                if not country_name or country_name.lower() in ['nan', 'none']:
                    continue
                
                # Clean country name (remove asterisks and extra spaces)
                country_name = country_name.rstrip('*').strip()
                
                # Map country name to World Bank code
                wb_country_code = COUNTRY_NAME_TO_CODE_MAPPING.get(country_name)
                
                data_record = {
                    'country_name': country_name,
                    'wb_country_code': wb_country_code,
                    'year': int(row.get('Year', 0)),
                    'ladder_score': self._safe_decimal(row.get('Ladder score')),
                    'upper_whisker': self._safe_decimal(row.get('upperwhisker')),
                    'lower_whisker': self._safe_decimal(row.get('lowerwhisker')),
                    'explained_by_freedom_to_make_life_choices': self._safe_decimal(
                        row.get('Explained by: Freedom to make life choices')
                    ),
                    'explained_by_generosity': self._safe_decimal(
                        row.get('Explained by: Generosity')
                    ),
                    'explained_by_perceptions_of_corruption': self._safe_decimal(
                        row.get('Explained by: Perceptions of corruption')
                    ),
                    'dystopia_plus_residual': self._safe_decimal(
                        row.get('Dystopia + residual')
                    ),
                    'explained_by_log_gdp_per_capita': self._safe_decimal(
                        row.get('Explained by: Log GDP per capita')
                    ),
                    'explained_by_social_support': self._safe_decimal(
                        row.get('Explained by: Social support')
                    ),
                    'explained_by_healthy_life_expectancy': self._safe_decimal(
                        row.get('Explained by: Healthy life expectancy')
                    ),
                }
                
                # Skip if essential data is missing
                if not data_record['ladder_score'] or data_record['year'] < 2020:
                    continue
                
                data_records.append(data_record)
                
            except Exception as e:
                logger.error(f"Error processing row: {e}")
                continue
        
        return data_records

    def _safe_decimal(self, value) -> Optional[Decimal]:
        """Safely convert value to Decimal, handling zeros as None for missing data"""
        if pd.isna(value) or value is None or value == '':
            return None
        try:
            decimal_value = Decimal(str(value))
            # Convert 0.000000 to None (indicates missing data in happiness report)
            if decimal_value == Decimal('0.000000'):
                return None
            return decimal_value
        except (InvalidOperation, ValueError):
            return None


def populate_countries():
    """Populate Country model with World Bank data"""
    wb_service = WorldBankAPIService()
    countries_data = wb_service.fetch_countries()
    
    created_count = 0
    updated_count = 0
    
    for country_data in countries_data:
        country, created = Country.objects.update_or_create(
            id=country_data['id'],
            defaults=country_data
        )
        if created:
            created_count += 1
        else:
            updated_count += 1
    
    logger.info(f"Countries: {created_count} created, {updated_count} updated")
    return created_count, updated_count


def populate_indicators():
    """Populate Indicator model with World Bank data"""
    wb_service = WorldBankAPIService()
    indicators_data = wb_service.fetch_indicators()
    
    created_count = 0
    updated_count = 0
    
    for indicator_data in indicators_data:
        indicator, created = Indicator.objects.update_or_create(
            id=indicator_data['id'],
            defaults=indicator_data
        )
        if created:
            created_count += 1
        else:
            updated_count += 1
    
    logger.info(f"Indicators: {created_count} created, {updated_count} updated")
    return created_count, updated_count


def populate_country_data():
    """Populate CountryData model with indicator data for all countries"""
    wb_service = WorldBankAPIService()
    
    countries = Country.objects.all()
    indicators = Indicator.objects.all()
    
    created_count = 0
    updated_count = 0
    
    for country in countries:
        for indicator in indicators:
            data_points = wb_service.fetch_country_indicator_data(
                country.id, indicator.id, 2020, 2025
            )
            
            for data_point in data_points:
                if data_point['value'] is not None:
                    country_data, created = CountryData.objects.update_or_create(
                        country=country,
                        indicator=indicator,
                        date=data_point['date'],
                        defaults={
                            'country_iso3_code': data_point['country_iso3_code'],
                            'value': data_point['value'],
                            'unit': data_point['unit'],
                            'obs_status': data_point['obs_status'],
                            'decimal_places': data_point['decimal_places'],
                        }
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
    
    logger.info(f"Country Data: {created_count} created, {updated_count} updated")
    return created_count, updated_count


def populate_happiness_data(excel_file_path: str):
    """Populate HappinessData model with Excel data"""
    happiness_service = HappinessDataService(excel_file_path)
    happiness_records = happiness_service.process_happiness_excel_file()
    
    created_count = 0
    updated_count = 0
    unmapped_countries = set()
    
    for record in happiness_records:
        try:
            # Get the mapped country if available
            mapped_country = None
            if record['wb_country_code']:
                try:
                    mapped_country = Country.objects.get(id=record['wb_country_code'])
                except Country.DoesNotExist:
                    unmapped_countries.add(record['country_name'])
            else:
                unmapped_countries.add(record['country_name'])
            
            happiness_data, created = HappinessData.objects.update_or_create(
                country_name=record['country_name'],
                year=record['year'],
                defaults={
                    'country': mapped_country,
                    'ladder_score': record['ladder_score'],
                    'upper_whisker': record['upper_whisker'],
                    'lower_whisker': record['lower_whisker'],
                    'explained_by_freedom_to_make_life_choices': record['explained_by_freedom_to_make_life_choices'],
                    'explained_by_generosity': record['explained_by_generosity'],
                    'explained_by_perceptions_of_corruption': record['explained_by_perceptions_of_corruption'],
                    'dystopia_plus_residual': record['dystopia_plus_residual'],
                    'explained_by_log_gdp_per_capita': record['explained_by_log_gdp_per_capita'],
                    'explained_by_social_support': record['explained_by_social_support'],
                    'explained_by_healthy_life_expectancy': record['explained_by_healthy_life_expectancy'],
                    'region': mapped_country.region_value if mapped_country else '',
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        except Exception as e:
            logger.error(f"Error processing happiness record for {record['country_name']}: {e}")
            continue
    
    if unmapped_countries:
        logger.warning(f"Unmapped countries: {', '.join(sorted(unmapped_countries))}")
    
    logger.info(f"Happiness Data: {created_count} created, {updated_count} updated")
    return created_count, updated_count, unmapped_countries