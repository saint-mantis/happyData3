from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'countries', views.CountryViewSet)
router.register(r'indicators', views.IndicatorViewSet)
router.register(r'happiness-data', views.HappinessDataViewSet)

app_name = 'dashboard'

urlpatterns = [
    # Template views
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('country-trends/', views.CountryTrendsView.as_view(), name='country_trends'),
    path('happiness-correlation/', views.HappinessCorrelationView.as_view(), name='happiness_correlation'),
    path('regional-happiness/', views.RegionalHappinessView.as_view(), name='regional_happiness'),
    path('regional-comparison/', views.RegionalComparisonView.as_view(), name='regional_comparison'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/country-data/<str:country_code>/<str:indicator_code>/', 
         views.CountryIndicatorDataView.as_view(), name='country_indicator_data'),
    path('api/happiness-data/<str:country_code>/', 
         views.CountryHappinessDataView.as_view(), name='country_happiness_data'),
    path('api/regional-happiness/', 
         views.RegionalHappinessAPIView.as_view(), name='regional_happiness_api'),
    path('api/regional-indicators/<str:region>/<str:indicator_code>/<int:year>/', 
         views.RegionalIndicatorDataView.as_view(), name='regional_indicator_data'),
]