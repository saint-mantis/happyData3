# HappyData - Data Visualization Platform

A modern Django web application for exploring relationships between development indicators and human well-being using real-world APIs from the World Bank and World Happiness Reports.

## Features

- **Ultra-Modern UI**: Cutting-edge design with glassmorphism effects, dark mode, and smooth animations
- **Interactive Visualizations**: Chart.js powered charts with responsive design
- **Country Indicator Trends**: Analyze how indicators change over time for specific countries
- **Happiness Correlation**: Discover relationships between happiness scores and development indicators
- **Regional Analysis**: Compare happiness levels and indicators across world regions
- **API Integration**: Real-time data from World Bank APIs and Excel-based happiness data

## Technologies Used

- **Backend**: Django 4.x with Django REST Framework
- **Frontend**: HTML5, CSS3, JavaScript (no frameworks)
- **Database**: SQLite
- **Charts**: Chart.js with custom styling
- **APIs**: World Bank Indicators API
- **Data**: World Happiness Report Excel files

## Setup Instructions

### Prerequisites

- Python 3.8+
- Conda environment (recommended)
- World Happiness Report Excel file

### Installation

1. **Clone/Navigate to the project directory**:
   ```bash
   cd "/Users/arunbabu/Desktop/Code/Happy Data 3"
   ```

2. **Activate the conda environment**:
   ```bash
   conda activate happydata
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Load World Bank data**:
   ```bash
   # Load countries and indicators
   python manage.py load_worldbank_data --countries-only
   python manage.py load_worldbank_data --indicators-only
   
   # Load country indicator data (this may take several minutes)
   python manage.py load_worldbank_data --data-only
   ```

7. **Load happiness data from Excel file**:
   ```bash
   python manage.py load_happiness_data --file-path "World_Happiness_Report_2020_2025.xlsx"
   ```

8. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

9. **Access the application**:
   - Open your browser and go to `http://127.0.0.1:8000/`
   - Admin interface: `http://127.0.0.1:8000/admin/`

## Data Sources

### World Bank API
The application fetches data from the World Bank API for the following indicators:
- GDP per capita (current US$)
- GDP per capita, PPP (current international $)
- GINI index
- Life expectancy at birth
- Health expenditure (% of GDP)
- Education expenditure (% of GDP)
- Unemployment rate
- CO2 emissions per capita
- Internet users (% of population)
- Urban population (% of total)

### World Happiness Report
The application processes Excel files containing happiness data with the following structure:
- Year (2020-2025)
- Country name
- Ladder score (happiness score 0-10)
- Upper/lower whiskers (confidence intervals)
- Contributing factors:
  - Log GDP per capita
  - Social support
  - Healthy life expectancy
  - Freedom to make life choices
  - Generosity
  - Perceptions of corruption
  - Dystopia + residual

## File Structure

```
happydata/
├── manage.py
├── requirements.txt
├── README.md
├── World_Happiness_Report_2020_2025.xlsx
├── happydata/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dashboard/
│   ├── models.py          # Data models for countries, indicators, happiness
│   ├── views.py           # Template and API views
│   ├── serializers.py     # DRF serializers
│   ├── services.py        # World Bank API integration
│   ├── urls.py            # URL routing
│   ├── admin.py           # Django admin configuration
│   └── management/
│       └── commands/      # Data loading commands
├── templates/
│   ├── base.html          # Base template with modern design
│   └── dashboard/         # Page templates
└── static/
    ├── css/
    │   └── style.css      # Ultra-modern CSS with dark mode
    └── js/
        └── dashboard.js   # Interactive JavaScript functionality
```

## Usage

### Dashboard Overview
- View key statistics and insights
- Navigate to different analysis sections
- Toggle between light and dark modes

### Country Trends
- Select a country and indicator
- View time series charts from 2020-2025
- Export charts and view raw data

### Happiness Correlation
- Analyze relationships between happiness and indicators
- View correlation coefficients and strength
- Dual-axis trend comparisons

### Regional Analysis
- Compare happiness levels across regions
- View regional trends over time
- Identify patterns and disparities

### Regional Comparison
- Compare countries within specific regions
- Switch between chart and table views
- View top performers and insights

## API Endpoints

The application provides REST API endpoints:

- `/api/countries/` - List all countries
- `/api/indicators/` - List all indicators
- `/api/happiness-data/` - Happiness data with filtering
- `/api/country-data/{country_code}/{indicator_code}/` - Time series data
- `/api/happiness-data/{country_code}/` - Country happiness data
- `/api/regional-happiness/` - Regional happiness statistics
- `/api/regional-indicators/{region}/{indicator}/{year}/` - Regional indicator data

## Features

### Modern UI/UX
- Glassmorphism design effects
- Dark/light mode toggle
- Smooth animations and transitions
- Responsive design for all devices
- Interactive hover states
- Modern typography (Inter, Poppins)

### Data Visualization
- Interactive Chart.js visualizations
- Multiple chart types (line, bar, doughnut, scatter)
- Responsive charts with animations
- Export functionality
- Custom color palettes

### Performance
- Efficient API caching
- Optimized database queries
- Fast loading with skeleton screens
- Progressive data loading

## Troubleshooting

### Common Issues

1. **No data showing**: Make sure to run the data loading commands first
2. **Excel file not found**: Ensure the World_Happiness_Report_2020_2025.xlsx file is in the project root
3. **API errors**: Check internet connection for World Bank API access
4. **Slow loading**: The initial data load can take several minutes

### Development

- Use `python manage.py check` to verify the application
- Access Django admin at `/admin/` to manage data
- Check browser console for JavaScript errors
- Use Django debug toolbar for performance analysis

## License

This project is created for educational and demonstration purposes.

## Data Attribution

- World Bank data: https://data.worldbank.org/
- World Happiness Report: https://worldhappiness.report/