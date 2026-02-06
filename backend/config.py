# Configuration file for storing API keys, environment variables, and application settings

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""
    
    # AMap API Configuration
    AMAP_API_KEY = os.getenv('AMAP_API_KEY', 'YOUR_AMAP_API_KEY_HERE')
    AMAP_SECURITY_KEY = os.getenv('AMAP_SECURITY_KEY', 'YOUR_AMAP_SECURITY_KEY_HERE')
    
    # API Endpoints
    AMAP_GEOCODE_URL = 'https://restapi.amap.com/v3/geocode/geo'
    AMAP_POI_SEARCH_URL = 'https://restapi.amap.com/v3/place/around'
    AMAP_ROAD_URL = 'https://restapi.amap.com/v3/direction/walking'  # Can be adjusted
    
    # Search Parameters
    DEFAULT_RADIUS = 500  # meters
    MAX_RADIUS = 5000
    POI_PAGE_SIZE = 50  # Maximum results per request
    
    # POI Categories for Feng Shui Analysis
    POI_CATEGORIES = {
        'parks': '110100|140700',  # Parks and green spaces
        'water': '150500|150600',  # Rivers, lakes, water bodies
        'buildings': '120000',  # Commercial buildings
        'residential': '120300',  # Residential areas
        'transportation': '150700',  # Transportation facilities
        'hospitals': '090000',  # Medical facilities
        'schools': '141200',  # Educational facilities
        'temples': '140800',  # Religious sites
    }
    
    # Feature Weights for Scoring (can be adjusted)
    FEATURE_WEIGHTS = {
        'green_area_ratio': 0.20,
        'water_proximity': 0.15,
        'building_density': 0.15,
        'road_density': 0.10,
        'orientation': 0.15,
        'environmental': 0.15,
        'spiritual': 0.10
    }
    
    # Flask Configuration
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))


# Create a config instance
config = Config()
