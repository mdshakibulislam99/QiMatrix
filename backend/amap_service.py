# Service layer for wrapping all AMap API calls and handling map data retrieval

import requests
import logging
from typing import Dict, List, Optional, Tuple
import time

from config import config

logger = logging.getLogger(__name__)


def geocode_address(address: str, city: Optional[str] = None) -> Optional[Dict]:
    """
    Call AMap Geocoding API to convert address to coordinates.
    
    Args:
        address: The address to geocode
        city: Optional city name to narrow search
    
    Returns:
        Dictionary with latitude, longitude, and formatted_address
        or None if geocoding fails
    """
    try:
        params = {
            'key': config.AMAP_API_KEY,
            'address': address,
            'output': 'json'
        }
        
        if city:
            params['city'] = city
        
        logger.info(f"Geocoding address: {address}")
        
        response = requests.get(config.AMAP_GEOCODE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == '1' and data.get('geocodes'):
            geocode = data['geocodes'][0]
            location = geocode['location'].split(',')
            
            result = {
                'longitude': float(location[0]),
                'latitude': float(location[1]),
                'formatted_address': geocode.get('formatted_address', address)
            }
            
            logger.info(f"Geocoding successful: {result}")
            return result
        else:
            logger.warning(f"Geocoding failed: {data.get('info')}")
            return None
            
    except Exception as e:
        logger.error(f"Error calling geocoding API: {str(e)}")
        return None


def search_nearby_pois(longitude: float, latitude: float, radius: int = 500) -> Dict[str, List[Dict]]:
    """
    Search for nearby Points of Interest (POI) around a location.
    
    Args:
        longitude: Longitude of center point
        latitude: Latitude of center point
        radius: Search radius in meters
    
    Returns:
        Dictionary with categorized POI data:
        {
            'parks': [...],
            'water': [...],
            'buildings': [...],
            ...
        }
    """
    logger.info(f"Searching POIs near ({longitude}, {latitude}) with radius {radius}m")
    
    poi_results = {}
    location_str = f"{longitude},{latitude}"
    
    # Search for each POI category
    for category_name, category_code in config.POI_CATEGORIES.items():
        try:
            params = {
                'key': config.AMAP_API_KEY,
                'location': location_str,
                'radius': radius,
                'types': category_code,
                'offset': config.POI_PAGE_SIZE,
                'output': 'json',
                'extensions': 'all'
            }
            
            response = requests.get(config.AMAP_POI_SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == '1':
                pois = data.get('pois', [])
                poi_results[category_name] = parse_pois(pois)
                logger.info(f"Found {len(pois)} POIs for category: {category_name}")
            else:
                logger.warning(f"POI search failed for {category_name}: {data.get('info')}")
                poi_results[category_name] = []
            
            # Rate limiting - avoid hitting API too quickly
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error searching POIs for {category_name}: {str(e)}")
            poi_results[category_name] = []
    
    return poi_results


def parse_pois(pois: List[Dict]) -> List[Dict]:
    """
    Parse POI data from AMap API response.
    
    Args:
        pois: List of POI dictionaries from API
    
    Returns:
        List of simplified POI dictionaries
    """
    parsed = []
    
    for poi in pois:
        try:
            location = poi.get('location', '').split(',')
            if len(location) == 2:
                parsed.append({
                    'name': poi.get('name', ''),
                    'type': poi.get('type', ''),
                    'longitude': float(location[0]),
                    'latitude': float(location[1]),
                    'address': poi.get('address', ''),
                    'distance': float(poi.get('distance', 0)),
                    'area': poi.get('area', ''),
                })
        except Exception as e:
            logger.warning(f"Error parsing POI: {str(e)}")
            continue
    
    return parsed


def get_road_network_data(longitude: float, latitude: float, radius: int = 500) -> Dict:
    """
    Fetch nearby road network data including road geometry and intersections.
    
    Note: AMap doesn't have a direct road network API. We approximate this
    by searching for transportation-related POIs and road features.
    
    Args:
        longitude: Longitude of center point
        latitude: Latitude of center point
        radius: Search radius in meters
    
    Returns:
        Dictionary with road network data:
        {
            'roads': [...],
            'intersections': [...],
            'road_count': int
        }
    """
    logger.info(f"Fetching road network data near ({longitude}, {latitude})")
    
    try:
        # Search for road and transportation features
        location_str = f"{longitude},{latitude}"
        
        params = {
            'key': config.AMAP_API_KEY,
            'location': location_str,
            'radius': radius,
            'types': '150700|150701|150702',  # Roads and intersections
            'offset': config.POI_PAGE_SIZE,
            'output': 'json'
        }
        
        response = requests.get(config.AMAP_POI_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == '1':
            pois = data.get('pois', [])
            roads = parse_road_features(pois)
            
            # Extract intersection points (simplified)
            intersections = extract_intersections(roads)
            
            return {
                'roads': roads,
                'intersections': intersections,
                'road_count': len(roads)
            }
        else:
            logger.warning(f"Road network search failed: {data.get('info')}")
            return {'roads': [], 'intersections': [], 'road_count': 0}
            
    except Exception as e:
        logger.error(f"Error fetching road network data: {str(e)}")
        return {'roads': [], 'intersections': [], 'road_count': 0}


def parse_road_features(pois: List[Dict]) -> List[Dict]:
    """
    Parse road features from POI data.
    
    Args:
        pois: List of POI dictionaries
    
    Returns:
        List of road feature dictionaries
    """
    roads = []
    
    for poi in pois:
        try:
            location = poi.get('location', '').split(',')
            if len(location) == 2:
                roads.append({
                    'name': poi.get('name', ''),
                    'type': poi.get('type', ''),
                    'longitude': float(location[0]),
                    'latitude': float(location[1]),
                })
        except Exception as e:
            logger.warning(f"Error parsing road feature: {str(e)}")
            continue
    
    return roads


def extract_intersections(roads: List[Dict]) -> List[Dict]:
    """
    Extract intersection points from road data (simplified approach).
    
    Args:
        roads: List of road dictionaries
    
    Returns:
        List of intersection points
    """
    # Simplified: treat each road point as a potential intersection
    # In a real implementation, you'd need actual road geometry data
    intersections = []
    
    for road in roads:
        if 'intersection' in road.get('name', '').lower() or \
           'junction' in road.get('name', '').lower():
            intersections.append({
                'longitude': road['longitude'],
                'latitude': road['latitude'],
                'name': road.get('name', '')
            })
    
    return intersections


def calculate_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lon1, lat1: First coordinate
        lon2, lat2: Second coordinate
    
    Returns:
        Distance in meters
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371000  # Earth radius in meters
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c
