from django.db import models
from decimal import Decimal


class Country(models.Model):
    id = models.CharField(max_length=10, primary_key=True)  # World Bank country code (e.g., "IN", "US")
    iso2_code = models.CharField(max_length=2, blank=True)  # 2-letter ISO code (e.g., "IN")
    name = models.CharField(max_length=100)  # Country name (e.g., "India")
    capital_city = models.CharField(max_length=100, blank=True)  # Capital city name
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)  # Geographic coordinate
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)  # Geographic coordinate
    region_id = models.CharField(max_length=10, blank=True)  # World Bank region code
    region_value = models.CharField(max_length=100, blank=True)  # Region name (e.g., "South Asia")
    admin_region_id = models.CharField(max_length=10, blank=True)  # Administrative region code
    admin_region_value = models.CharField(max_length=100, blank=True)  # Administrative region name
    income_level_id = models.CharField(max_length=10, blank=True)  # Income classification code
    income_level_value = models.CharField(max_length=100, blank=True)  # Income level (e.g., "Lower middle income")
    lending_type_id = models.CharField(max_length=10, blank=True)  # Lending category code
    lending_type_value = models.CharField(max_length=100, blank=True)  # Lending type description

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.id})"


class Indicator(models.Model):
    id = models.CharField(max_length=50, primary_key=True)  # Indicator code (e.g., "NY.GDP.PCAP.CD")
    name = models.CharField(max_length=255)  # Indicator name/description
    unit = models.CharField(max_length=100, blank=True)  # Measurement unit
    source_id = models.CharField(max_length=10, blank=True)  # Data source ID
    source_value = models.CharField(max_length=255, blank=True)  # Data source name
    source_note = models.TextField(blank=True)  # Detailed description
    source_organization = models.CharField(max_length=255, blank=True)  # Source organization

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.id})"


class CountryData(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='indicators_data')
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='country_data')
    country_iso3_code = models.CharField(max_length=3, blank=True)  # 3-letter ISO code
    date = models.CharField(max_length=4)  # Year as string
    value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)  # Actual indicator value
    unit = models.CharField(max_length=100, blank=True)  # Measurement unit
    obs_status = models.CharField(max_length=10, blank=True)  # Observation status
    decimal_places = models.IntegerField(default=0)  # Number of decimal places

    class Meta:
        unique_together = ['country', 'indicator', 'date']
        ordering = ['country', 'indicator', 'date']

    def __str__(self):
        return f"{self.country.name} - {self.indicator.name} ({self.date}): {self.value}"

    @property
    def year(self):
        return int(self.date) if self.date.isdigit() else None


class HappinessData(models.Model):
    country_name = models.CharField(max_length=100)  # Country name from CSV (for mapping to World Bank codes)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='happiness_data', null=True, blank=True)  # Mapped World Bank country
    year = models.IntegerField()  # Year (2020-2025)
    ladder_score = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)  # Main happiness score (0-10 scale)
    upper_whisker = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)  # Upper confidence interval
    lower_whisker = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)  # Lower confidence interval
    explained_by_freedom_to_make_life_choices = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)  # Freedom factor
    explained_by_generosity = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)  # Generosity factor
    explained_by_perceptions_of_corruption = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)  # Corruption factor
    dystopia_plus_residual = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)  # Statistical residual
    explained_by_log_gdp_per_capita = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)  # Economic factor
    explained_by_social_support = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)  # Social support factor
    explained_by_healthy_life_expectancy = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)  # Health factor
    region = models.CharField(max_length=100, blank=True)  # World Bank region (mapped from country code)

    class Meta:
        unique_together = ['country_name', 'year']
        ordering = ['-ladder_score', 'year', 'country_name']

    def __str__(self):
        return f"{self.country_name} ({self.year}): {self.ladder_score}"

    def save(self, *args, **kwargs):
        # Auto-populate region from country if mapped
        if self.country and not self.region:
            self.region = self.country.region_value
        super().save(*args, **kwargs)

    @property
    def happiness_rank(self):
        """Get the rank of this country for the given year"""
        return HappinessData.objects.filter(
            year=self.year,
            ladder_score__gt=self.ladder_score
        ).count() + 1

    @property
    def contributing_factors(self):
        """Return a dictionary of all contributing factors"""
        return {
            'log_gdp_per_capita': self.explained_by_log_gdp_per_capita,
            'social_support': self.explained_by_social_support,
            'healthy_life_expectancy': self.explained_by_healthy_life_expectancy,
            'freedom_to_make_life_choices': self.explained_by_freedom_to_make_life_choices,
            'generosity': self.explained_by_generosity,
            'perceptions_of_corruption': self.explained_by_perceptions_of_corruption,
            'dystopia_plus_residual': self.dystopia_plus_residual,
        }


# Country name to World Bank code mapping
COUNTRY_NAME_TO_CODE_MAPPING = {
    # Major countries
    "Finland": "FI", "Denmark": "DK", "Switzerland": "CH", "Iceland": "IS", 
    "Norway": "NO", "Netherlands": "NL", "Sweden": "SE", "New Zealand": "NZ",
    "Austria": "AT", "Luxembourg": "LU", "Canada": "CA", "Australia": "AU",
    "United Kingdom": "GB", "Israel": "IL", "Costa Rica": "CR", "Ireland": "IE",
    "Germany": "DE", "United States": "US", "Czech Republic": "CZ", "Belgium": "BE",
    
    # Middle East and Asia
    "United Arab Emirates": "AE", "Malta": "MT", "France": "FR", "Mexico": "MX",
    "Taiwan Province of China": "TW", "Uruguay": "UY", "Saudi Arabia": "SA", 
    "Spain": "ES", "Guatemala": "GT", "Italy": "IT", "Singapore": "SG",
    "Brazil": "BR", "Slovenia": "SI", "El Salvador": "SV", "Kosovo": "XK",
    "Panama": "PA", "Slovakia": "SK", "Uzbekistan": "UZ", "Chile": "CL",
    "Bahrain": "BH", "Lithuania": "LT", "Trinidad and Tobago": "TT", "Poland": "PL",
    
    # South America and Caribbean  
    "Colombia": "CO", "Cyprus": "CY", "Nicaragua": "NI", "Romania": "RO",
    "Kuwait": "KW", "Mauritius": "MU", "Kazakhstan": "KZ", "Estonia": "EE",
    "Philippines": "PH", "Hungary": "HU", "Thailand": "TH", "Argentina": "AR",
    "Honduras": "HN", "Latvia": "LV", "Ecuador": "EC", "Portugal": "PT",
    "Jamaica": "JM", "South Korea": "KR", "Japan": "JP", "Peru": "PE",
    "Serbia": "RS", "Bolivia": "BO", "Pakistan": "PK", "Paraguay": "PY",
    "Dominican Republic": "DO", "Bosnia and Herzegovina": "BA", "Moldova": "MD",
    
    # Eastern Europe and Central Asia
    "Tajikistan": "TJ", "Montenegro": "ME", "Russia": "RU", "Kyrgyzstan": "KG",
    "Belarus": "BY", "North Cyprus": "CY", "Greece": "GR", "Croatia": "HR",
    "Libya": "LY", "Mongolia": "MN", "Malaysia": "MY", "Vietnam": "VN",
    "Indonesia": "ID", "Ivory Coast": "CI", "Benin": "BJ", "Maldives": "MV",
    "Congo (Brazzaville)": "CG", "Azerbaijan": "AZ", "Macedonia": "MK",
    "Ghana": "GH", "Nepal": "NP", "Turkey": "TR", "China": "CN",
    "Turkmenistan": "TM", "Bulgaria": "BG", "Morocco": "MA", "Cameroon": "CM",
    
    # Africa
    "Venezuela": "VE", "Algeria": "DZ", "Senegal": "SN", "Guinea": "GN",
    "Niger": "NE", "Laos": "LA", "Albania": "AL", "Cambodia": "KH",
    "Bangladesh": "BD", "Gabon": "GA", "South Africa": "ZA", "Iraq": "IQ",
    "Lebanon": "LB", "Burkina Faso": "BF", "Gambia": "GM", "Mali": "ML",
    "Nigeria": "NG", "Armenia": "AM", "Georgia": "GE", "Iran": "IR",
    "Jordan": "JO", "Mozambique": "MZ", "Kenya": "KE", "Namibia": "NA",
    "Ukraine": "UA", "Liberia": "LR", "Palestinian Territories": "PS",
    "Uganda": "UG", "Chad": "TD", "Tunisia": "TN", "Mauritania": "MR",
    "Sri Lanka": "LK", "Congo (Kinshasa)": "CD", "Swaziland": "SZ",
    "Myanmar": "MM", "Comoros": "KM", "Togo": "TG", "Ethiopia": "ET",
    "Madagascar": "MG", "Egypt": "EG", "Sierra Leone": "SL", "Burundi": "BI",
    "Zambia": "ZM", "Haiti": "HT", "Lesotho": "LS", "India": "IN",
    "Malawi": "MW", "Yemen": "YE", "Botswana": "BW", "Tanzania": "TZ",
    "Central African Republic": "CF", "Rwanda": "RW", "Zimbabwe": "ZW",
    "South Sudan": "SS", "Afghanistan": "AF",
    
    # Handle variations and special cases
    "North Macedonia": "MK", "Czechia": "CZ", "Czech Republic": "CZ", 
    "Republic of Korea": "KR", "South Korea": "KR",
    "Russian Federation": "RU", "Russia": "RU",
    "Lao PDR": "LA", "Laos": "LA",
    "Republic of Moldova": "MD", "Moldova": "MD",
    "Türkiye": "TR", "Turkiye": "TR", "Turkey": "TR",
    "Hong Kong SAR of China": "HK", "Hong Kong S.A.R. of China": "HK",
    "Viet Nam": "VN", "Vietnam": "VN",
    "DR Congo": "CD", "Congo (Kinshasa)": "CD",
    "Congo": "CG", "Congo (Brazzaville)": "CG",
    "Eswatini": "SZ", "Eswatini, Kingdom of": "SZ", "Swaziland": "SZ",
    "State of Palestine": "PS", "Palestinian Territories": "PS",
    "Côte d'Ivoire": "CI", "Ivory Coast": "CI",
    "Egypt": "EG", "Egypt, Arab Rep.": "EG",
    "Iran": "IR", "Iran, Islamic Rep.": "IR",
    "Syria": "SY", "Syrian Arab Republic": "SY",
    "Yemen": "YE", "Yemen, Rep.": "YE",
    "Slovakia": "SK", "Slovak Republic": "SK",
    "Venezuela": "VE", "Venezuela, RB": "VE",
    "Macedonia": "MK", "North Macedonia": "MK",
    "Kyrgyzstan": "KG", "Kyrgyz Republic": "KG",
    "Gambia": "GM", "Gambia, The": "GM",
    
    # Special administrative regions and territories
    "Puerto Rico": "PR", "Qatar": "QA", "Oman": "OM", "Guyana": "GY",
    "Angola": "AO", "Belize": "BZ", "Bhutan": "BT", "Cuba": "CU",
    "Djibouti": "DJ", "Somalia": "SO", "Sudan": "SD", "Suriname": "SR",
    "Syria": "SY", "Somaliland Region": "SO",  # Map to Somalia
    
    # Handle entries with asterisks (remove asterisk, use same mapping)
    "Luxembourg*": "LU", "Guatemala*": "GT", "Kuwait*": "KW", "Belarus*": "BY",
    "Turkmenistan*": "TM", "North Cyprus*": "CY", "Libya*": "LY", 
    "Azerbaijan*": "AZ", "Gambia*": "GM", "Liberia*": "LR", "Niger*": "NE",
    "Comoros*": "KM", "Palestinian Territories*": "PS", "Madagascar*": "MG",
    "Chad*": "TD", "Yemen*": "YE", "Mauritania*": "MR", "Lesotho*": "LS",
    "Botswana*": "BW", "Rwanda*": "RW",
}