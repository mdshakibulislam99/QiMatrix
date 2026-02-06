# Module for extracting relevant features from map data for Feng Shui analysis

import logging
from typing import Dict, List, Optional, Tuple
import math
import statistics

logger = logging.getLogger(__name__)

# Constants for feature calculations
AVERAGE_PARK_AREA = 50000  # Average park area in square meters
AVERAGE_WATER_AREA = 100000  # Average water body area in square meters
AVERAGE_BUILDING_AREA = 500  # Average building footprint in square meters


def extract_features(poi_data: Dict[str, List[Dict]], 
                    road_data: Dict,
                    longitude: float,
                    latitude: float,
                    radius: int) -> Dict:
    """
    Extract comprehensive Feng Shui-relevant features from real AMap data.
    
    This is the main orchestrator function that:
    1. Takes raw POI and road data from AMap API
    2. Calls specialized calculation functions for each feature
    3. Returns a feature dictionary suitable for AI model input
    
    All calculations are DYNAMIC and based on the actual clicked location.
    No hardcoded values - everything varies with the map location.
    
    Feature Categories:
    - Spatial: green_area_ratio, water_proximity, building_density
    - Infrastructure: road_intersection_density, environmental_quality
    - Energy: orientation_score, qi_flow_score, spiritual_presence
    
    Args:
        poi_data: Dictionary of categorized POI data from AMap API
                  Keys: 'parks', 'water', 'buildings', 'residential', 
                        'hospitals', 'schools', 'temples', etc.
                  Values: List of POI dictionaries with 'distance', 
                          'longitude', 'latitude', 'name', etc.
        road_data: Dictionary of road network data from AMap
                   Keys: 'roads', 'intersections', 'road_count'
                   Values: List of road/intersection features
        longitude: Center point longitude (clicked location)
        latitude: Center point latitude (clicked location)
        radius: Analysis radius in meters (configurable by user)
    
    Returns:
        Dictionary of extracted features with numeric values (0-1 normalized):
        {
            'green_area_ratio': float (0-1),
            'water_proximity': float (0-1),
            'building_density': float (0-1),
            'road_intersection_density': float (0-1),
            'orientation_score': float (0-1),
            'environmental_quality': float (0-1),
            'spiritual_presence': float (0-1)
        }
        
        All features are location-specific and dynamically calculated.
    """
    logger.info(f"=" * 70)
    logger.info(f"Extracting features for location: ({latitude:.6f}, {longitude:.6f})")
    logger.info(f"Analysis radius: {radius}m")
    logger.info(f"POI categories found: {', '.join([f'{k}({len(v)})' for k, v in poi_data.items() if v])}")
    logger.info(f"=" * 70)
    
    features = {}
    
    try:
        # Feature 1: Green Area Ratio
        # Based on park POIs within radius
        features['green_area_ratio'] = calculate_green_area_ratio(
            poi_data.get('parks', []), 
            radius
        )
        
        # Feature 2: Water Proximity Score
        # Distance to nearest water body and its Feng Shui significance
        features['water_proximity'] = calculate_water_proximity(
            poi_data.get('water', []), 
            longitude, 
            latitude, 
            radius
        )
        
        # Feature 3: Building Density
        # Combines commercial buildings and residential areas
        all_buildings = poi_data.get('buildings', []) + poi_data.get('residential', [])
        features['building_density'] = calculate_building_density(
            all_buildings,
            radius
        )
        
        # Feature 4: Road Intersection Density
        # Measure of traffic connectivity and accessibility
        features['road_intersection_density'] = calculate_road_density(
            road_data.get('intersections', []),
            road_data.get('road_count', 0),
            radius
        )
        
        # Feature 5: Orientation Score
        # Average building orientation relative to optimal Feng Shui directions
        features['orientation_score'] = estimate_orientation_score(
            all_buildings,
            longitude,
            latitude
        )
        
        # Feature 6: Environmental Quality
        # Proximity to hospitals and schools (essential services)
        features['environmental_quality'] = calculate_environmental_quality(
            poi_data.get('hospitals', []),
            poi_data.get('schools', []),
            radius
        )
        
        # Feature 7: Spiritual Presence
        # Nearby temples and religious sites
        features['spiritual_presence'] = calculate_spiritual_presence(
            poi_data.get('temples', []),
            radius
        )
        
        # Additional derived feature: Qi Flow
        # Not used directly by AI model but valuable for traditional scoring
        qi_flow_score = calculate_qi_flow_score(
            road_data,
            features['building_density'],
            features['green_area_ratio']
        )
        # Store for use in scorer but not passed to AI model
        features['qi_flow'] = qi_flow_score
        
    except Exception as e:
        logger.error(f"Error extracting features: {str(e)}", exc_info=True)
        # Return default neutral values on error
        features = {
            'green_area_ratio': 0.3,
            'water_proximity': 0.3,
            'building_density': 0.5,
            'road_intersection_density': 0.5,
            'orientation_score': 0.5,
            'environmental_quality': 0.3,
            'spiritual_presence': 0.2,
            'qi_flow': 0.5
        }
        logger.warning("Using default neutral feature values due to extraction error")
    
    logger.info(f"=" * 70)
    logger.info(f"Feature extraction complete. Summary:")
    for feature_name, feature_value in features.items():
        logger.info(f"  {feature_name}: {feature_value:.3f}")
    logger.info(f"=" * 70)
    
    return features
    return features


def calculate_green_area_ratio(parks: List[Dict], radius: int) -> float:
    """
    Calculate the ratio of green/park areas within the search radius.
    Uses distance-weighted area estimation based on actual POI data.
    
    Algorithm:
    - Each park POI is assigned an estimated area based on its distance
    - Closer parks have more accurate area estimates
    - Parks beyond 80% of radius have reduced contribution
    - Final ratio = total_green_area / total_search_area
    
    Args:
        parks: List of park POIs with 'distance' field (in meters)
        radius: Search radius in meters
    
    Returns:
        Green area ratio (0-1), where 0 = no parks, 1 = maximum green coverage
    """
    if not parks:
        logger.info("Green area ratio: 0.000 (no parks found)")
        return 0.0
    
    # Calculate total search area
    total_search_area = math.pi * radius * radius
    
    # Estimate green area contribution from each park
    total_green_area = 0.0
    for park in parks:
        distance = park.get('distance', radius)
        
        # Distance weight: parks closer to center count more
        # Use exponential decay: closer parks = higher weight
        distance_factor = math.exp(-2 * distance / radius)
        
        # Estimate park area based on distance
        # Assumption: closer POIs are more accurately detected
        if distance < radius * 0.3:
            # Close parks: use full estimated area
            estimated_area = AVERAGE_PARK_AREA * distance_factor
        elif distance < radius * 0.6:
            # Medium distance: moderate area
            estimated_area = AVERAGE_PARK_AREA * 0.6 * distance_factor
        else:
            # Far parks: smaller contribution
            estimated_area = AVERAGE_PARK_AREA * 0.3 * distance_factor
        
        total_green_area += estimated_area
    
    # Calculate ratio and normalize
    ratio = min(total_green_area / total_search_area, 1.0)
    
    logger.info(f"Green area ratio: {ratio:.3f} ({len(parks)} parks found, "
                f"estimated {total_green_area:.0f}m² green space in {total_search_area:.0f}m² area)")
    
    return ratio


def calculate_water_proximity(water_bodies: List[Dict], 
                              longitude: float, 
                              latitude: float,
                              radius: int) -> float:
    """
    Calculate water proximity score based on Feng Shui principles.
    Water represents wealth and prosperity but must be at optimal distance.
    
    Feng Shui Water Guidelines:
    - Too close (<100m): Risk of overwhelming energy, flooding concerns
    - Optimal (100-800m): Brings wealth energy, good for prosperity
    - Moderate (800-1500m): Still beneficial but reduced effect
    - Far (>1500m): Minimal water energy influence
    
    Args:
        water_bodies: List of water body POIs from AMap
        longitude: Center point longitude
        latitude: Center point latitude
        radius: Search radius in meters
    
    Returns:
        Water proximity score (0-1), where 1 = optimal distance
    """
    if not water_bodies:
        logger.info("Water proximity score: 0.000 (no water bodies found)")
        return 0.0
    
    # Find closest water body using real distance data
    min_distance = radius
    closest_water = None
    for water in water_bodies:
        distance = water.get('distance', radius)
        if distance < min_distance:
            min_distance = distance
            closest_water = water
    
    # Calculate score based on Feng Shui optimal distance curve
    if min_distance < 100:
        # Too close: potential negative effects (flood risk, overwhelming)
        score = 0.5 + (min_distance / 200)  # 0.5-1.0 range
    elif 100 <= min_distance <= 800:
        # Optimal range: maximum benefit
        # Peak score at 400m
        deviation_from_optimal = abs(min_distance - 400)
        score = 1.0 - (deviation_from_optimal / 400) * 0.15  # 0.85-1.0 range
    elif 800 < min_distance <= 1500:
        # Moderate range: declining benefit
        score = 0.85 - ((min_distance - 800) / 700) * 0.5  # 0.35-0.85 range
    else:
        # Far range: minimal benefit
        score = max(0.0, 0.35 - ((min_distance - 1500) / radius) * 0.35)
    
    water_name = closest_water.get('name', 'Unknown') if closest_water else 'N/A'
    logger.info(f"Water proximity score: {score:.3f} (closest: '{water_name}' at {min_distance:.0f}m)")
    
    return score


def calculate_building_density(buildings: List[Dict], radius: int) -> float:
    """
    Calculate building density as a measure of urban congestion.
    Higher density indicates more crowded energy flow (less favorable in Feng Shui).
    
    Calculation Method:
    - Count actual buildings from AMap POI data
    - Calculate density per square kilometer
    - Normalize based on typical urban density ranges:
      * Low density: <100 buildings/km² (rural/suburban)
      * Medium density: 100-300 buildings/km² (urban residential)
      * High density: 300-500 buildings/km² (dense urban)
      * Very high density: >500 buildings/km² (downtown/commercial)
    
    Args:
        buildings: List of building POIs from AMap (commercial + residential)
        radius: Search radius in meters
    
    Returns:
        Normalized density (0-1), where 0 = sparse, 1 = very dense
    """
    if not buildings:
        logger.info("Building density: 0.0 buildings/km² (normalized: 0.000)")
        return 0.0
    
    # Calculate search area in square kilometers
    area_sq_m = math.pi * radius * radius
    area_sq_km = area_sq_m / 1_000_000
    
    # Count buildings and calculate density
    building_count = len(buildings)
    density_per_sq_km = building_count / area_sq_km if area_sq_km > 0 else 0
    
    # Normalize density to 0-1 scale
    # Using sigmoid-like function for smooth normalization
    # Target: 500 buildings/km² = 0.5 normalized value
    normalized_density = 1 / (1 + math.exp(-0.01 * (density_per_sq_km - 500)))
    
    # Alternative linear normalization (commented for reference)
    # normalized_density = min(density_per_sq_km / 1000, 1.0)
    
    logger.info(f"Building density: {density_per_sq_km:.1f} buildings/km² "
                f"({building_count} buildings in {area_sq_km:.2f}km²), "
                f"normalized: {normalized_density:.3f}")
    
    return normalized_density


def calculate_road_density(intersections: List[Dict], 
                          road_count: int,
                          radius: int) -> float:
    """
    Calculate road intersection density as a measure of traffic connectivity.
    Moderate density is ideal - too low means isolated, too high means chaotic traffic.
    
    Feng Shui Road Principles:
    - Very low density (<5/km²): Isolated, poor accessibility
    - Low density (5-10/km²): Quiet, but may lack convenience
    - Optimal density (10-20/km²): Good balance of access and calm
    - High density (20-40/km²): Busy, excessive Yang energy
    - Very high density (>40/km²): Traffic chaos, cutting Qi
    
    Args:
        intersections: List of intersection POIs from AMap road data
        road_count: Total number of road features detected
        radius: Search radius in meters
    
    Returns:
        Normalized density (0-1), representing traffic intensity
    """
    # Calculate search area
    area_sq_m = math.pi * radius * radius
    area_sq_km = area_sq_m / 1_000_000
    
    # Count actual intersections from road data
    intersection_count = len(intersections)
    
    # Calculate density
    if area_sq_km > 0:
        intersection_density = intersection_count / area_sq_km
    else:
        intersection_density = 0
    
    # Normalize using optimal range (10-20 intersections/km²)
    # Below 10: gradually increase from 0
    # 10-20: peak range (high score)
    # Above 20: gradually decrease
    if intersection_density < 10:
        normalized = intersection_density / 10 * 0.7  # 0-0.7
    elif 10 <= intersection_density <= 20:
        normalized = 0.7 + (intersection_density - 10) / 10 * 0.3  # 0.7-1.0
    else:
        # Penalty for excessive density
        excess = intersection_density - 20
        normalized = max(0.0, 1.0 - excess / 20 * 0.5)  # Decrease from 1.0
    
    logger.info(f"Road intersection density: {intersection_density:.1f}/km² "
                f"({intersection_count} intersections, {road_count} roads), "
                f"normalized: {normalized:.3f}")
    
    return normalized


def estimate_orientation_score(buildings: List[Dict],
                               center_lon: float,
                               center_lat: float) -> float:
    """
    Calculate average building orientation score based on Feng Shui principles.
    
    Feng Shui Orientation Hierarchy (Northern Hemisphere):
    1. South (135-225°): Best - captures most sunlight, warm energy
    2. Southeast (90-135°): Good - morning sun, growth energy
    3. Southwest (225-270°): Good - afternoon warmth
    4. East (45-90°): Moderate - morning light
    5. West (270-315°): Moderate - afternoon sun, can be harsh
    6. North (315-45°): Less favorable - cold, less light
    7. Northeast/Northwest: Variable - depends on specific location
    
    Algorithm:
    - Calculate bearing from center point to each building
    - Treat bearing as approximate building orientation
    - Score each orientation based on Feng Shui principles
    - Return weighted average (closer buildings weighted more)
    
    Args:
        buildings: List of building POIs from AMap with coordinates
        center_lon: Center point longitude
        center_lat: Center point latitude
    
    Returns:
        Orientation score (0-1), where 1 = optimal south-facing average
    """
    if not buildings:
        logger.info("Orientation score: 0.500 (no buildings found, neutral score)")
        return 0.5  # Neutral score when no data
    
    orientations = []
    distances = []
    
    for building in buildings:
        building_lon = building.get('longitude')
        building_lat = building.get('latitude')
        distance = building.get('distance', 1000)
        
        if building_lon is None or building_lat is None:
            continue
        
        # Calculate bearing from center to building (proxy for orientation)
        angle = estimate_building_orientation(
            building_lon,
            building_lat,
            center_lon,
            center_lat
        )
        
        if angle is not None:
            orientations.append(angle)
            distances.append(distance)
    
    if not orientations:
        logger.info("Orientation score: 0.500 (no valid building orientations)")
        return 0.5
    
    # Calculate weighted average orientation score
    # Closer buildings have more influence on the score
    total_weight = 0
    weighted_score_sum = 0
    
    for angle, distance in zip(orientations, distances):
        # Distance weight: closer buildings count more
        weight = 1 / (1 + distance / 100)  # Exponential decay
        orientation_score = score_orientation(angle)
        
        weighted_score_sum += orientation_score * weight
        total_weight += weight
    
    avg_score = weighted_score_sum / total_weight if total_weight > 0 else 0.5
    avg_angle = statistics.mean(orientations)
    
    logger.info(f"Orientation score: {avg_score:.3f} "
                f"({len(orientations)} buildings analyzed, avg angle: {avg_angle:.1f}°, "
                f"dominant direction: {angle_to_direction(avg_angle)})")
    
    return avg_score


def estimate_building_orientation(lon: float, lat: float, 
                                 center_lon: float, center_lat: float) -> Optional[float]:
    """
    Estimate building facing angle based on its position.
    
    Args:
        lon, lat: Building coordinates
        center_lon, center_lat: Reference center coordinates
    
    Returns:
        Facing angle in degrees (0-360, where 0 = North), or None
    """
    if lon is None or lat is None:
        return None
    
    # Calculate bearing from center to building
    delta_lon = lon - center_lon
    delta_lat = lat - center_lat
    
    # Convert to angle (0° = North, 90° = East, etc.)
    angle_rad = math.atan2(delta_lon, delta_lat)
    angle_deg = math.degrees(angle_rad)
    
    # Normalize to 0-360
    facing_angle = (angle_deg + 360) % 360
    
    return facing_angle


def score_orientation(angle: float) -> float:
    """
    Score a building orientation based on traditional Feng Shui principles.
    Uses smooth gradient instead of discrete bins for more accurate scoring.
    
    Scoring Curve:
    - Peak at 180° (due south): 1.0
    - High from 135-225° (south range): 0.9-1.0
    - Good from 90-135° and 225-270° (SE/SW): 0.7-0.9
    - Moderate from 45-90° and 270-315° (E/W): 0.5-0.7
    - Lower from 315-45° (north range): 0.3-0.5
    
    Args:
        angle: Facing angle in degrees (0-360°)
              0° = North, 90° = East, 180° = South, 270° = West
    
    Returns:
        Score from 0-1, where 1 = optimal south-facing
    """
    # Normalize angle to 0-360 range
    angle = angle % 360
    
    # Calculate deviation from optimal south (180°)
    deviation_from_south = abs(180 - angle)
    if deviation_from_south > 180:
        deviation_from_south = 360 - deviation_from_south
    
    # Use cosine-based smooth curve for scoring
    # 0° deviation (south) = 1.0, 180° deviation (north) = 0.3
    score = 0.3 + 0.7 * math.cos(math.radians(deviation_from_south))
    
    # Ensure score is in valid range
    return max(0.3, min(1.0, score))


def angle_to_direction(angle: float) -> str:
    """
    Convert bearing angle to compass direction name.
    
    Args:
        angle: Angle in degrees (0-360)
    
    Returns:
        Direction name (e.g., 'North', 'Southeast', 'West')
    """
    directions = [
        'North', 'Northeast', 'East', 'Southeast',
        'South', 'Southwest', 'West', 'Northwest'
    ]
    # Divide 360° into 8 sectors (45° each)
    index = int((angle + 22.5) % 360 / 45)
    return directions[index]


def calculate_qi_flow_score(road_data: Dict, 
                           building_density: float,
                           green_ratio: float) -> float:
    """
    Calculate Qi (energy) flow score based on urban connectivity and openness.
    
    Qi Flow Principles in Feng Shui:
    - Qi needs pathways to circulate (roads provide channels)
    - Too many obstacles block Qi (high building density)
    - Green spaces generate and refresh Qi
    - Balance is key: moderate connectivity + adequate openness
    
    Factors:
    1. Road connectivity (from road_count): enables Qi circulation
    2. Building density (inverse): lower density allows better flow
    3. Green space ratio: generates positive Qi
    
    Args:
        road_data: Dictionary with 'road_count' and 'intersections'
        building_density: Normalized building density (0-1)
        green_ratio: Green area ratio (0-1)
    
    Returns:
        Qi flow score (0-1), where 1 = optimal energy circulation
    """
    road_count = road_data.get('road_count', 0)
    intersections = road_data.get('intersections', [])
    
    # Component 1: Road connectivity score (0-1)
    # Optimal: 5-15 roads providing good connectivity without chaos
    if road_count < 5:
        road_score = road_count / 5 * 0.6  # Low connectivity
    elif 5 <= road_count <= 15:
        road_score = 0.6 + (road_count - 5) / 10 * 0.4  # Optimal range
    else:
        road_score = max(0.4, 1.0 - (road_count - 15) / 20 * 0.6)  # Too many roads
    
    # Component 2: Openness score (inverse of building density)
    openness_score = 1.0 - building_density
    
    # Component 3: Green space contribution
    green_contribution = green_ratio
    
    # Weighted combination
    # Road connectivity: 30%, Openness: 40%, Green space: 30%
    qi_flow = (
        road_score * 0.30 +
        openness_score * 0.40 +
        green_contribution * 0.30
    )
    
    logger.info(f"Qi flow score: {qi_flow:.3f} "
                f"(roads: {road_score:.2f}, openness: {openness_score:.2f}, "
                f"green: {green_contribution:.2f})")
    
    return qi_flow


def calculate_environmental_quality(hospitals: List[Dict],
                                   schools: List[Dict],
                                   radius: int) -> float:
    """
    Calculate environmental quality based on proximity to essential services.
    Good environment = balanced access to healthcare and education.
    
    Optimal Balance:
    - 1-3 hospitals: Good healthcare access without overwhelming presence
    - 3-5 schools: Indicates family-friendly, educated neighborhood
    
    Args:
        hospitals: List of hospital POIs from AMap
        schools: List of school POIs from AMap
        radius: Search radius in meters
    
    Returns:
        Environmental quality score (0-1)
    """
    # Hospital score: optimal is 2 hospitals
    if not hospitals:
        hospital_score = 0.0
    elif len(hospitals) <= 3:
        hospital_score = min(len(hospitals) / 2, 1.0)
    else:
        # Too many hospitals may indicate medical district (not ideal for living)
        hospital_score = max(0.5, 1.0 - (len(hospitals) - 3) / 5 * 0.5)
    
    # School score: optimal is 4 schools
    if not schools:
        school_score = 0.0
    elif len(schools) <= 5:
        school_score = min(len(schools) / 4, 1.0)
    else:
        # Too many schools may mean very dense area
        school_score = max(0.5, 1.0 - (len(schools) - 5) / 10 * 0.5)
    
    # Weighted average (equal importance)
    score = (hospital_score * 0.5 + school_score * 0.5)
    
    logger.info(f"Environmental quality: {score:.3f} "
                f"({len(hospitals)} hospitals [score: {hospital_score:.2f}], "
                f"{len(schools)} schools [score: {school_score:.2f}])")
    
    return score


def calculate_spiritual_presence(temples: List[Dict], radius: int) -> float:
    """
    Calculate spiritual presence score based on nearby temples/religious sites.
    
    Args:
        temples: List of temple/religious site POIs
        radius: Search radius
    
    Returns:
        Spiritual presence score (0-1)
    """
    if not temples:
        return 0.0
    
    # Having 1-2 temples nearby is auspicious
    score = min(len(temples) / 2, 1.0)
    
    logger.info(f"Spiritual presence: {score:.3f} ({len(temples)} temples found)")
    return score
