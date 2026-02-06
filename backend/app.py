# Main Flask server application - handles API routes and request/response logic

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

from amap_service import (
    geocode_address,
    search_nearby_pois,
    get_road_network_data
)
from feature_extractor import extract_features
from scorer import calculate_feng_shui_score

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for frontend communication

@app.route('/api/analyze', methods=['POST'])
def analyze_location():
    """
    Main endpoint to analyze a location's Feng Shui score.
    
    Expected JSON input:
    {
        "latitude": float,
        "longitude": float,
        "radius": int (meters)
    }
    
    Returns JSON:
    {
        "final_score": float,
        "category_scores": dict,
        "explanations": list,
        "location": dict
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        radius = data.get('radius', 500)
        
        # Validate input
        if latitude is None or longitude is None:
            return jsonify({"error": "latitude and longitude are required"}), 400
        
        logger.info(f"Analyzing location: lat={latitude}, lng={longitude}, radius={radius}m")
        
        # Step 1: Fetch POI data from AMap
        poi_data = search_nearby_pois(longitude, latitude, radius)
        
        # Step 2: Fetch road network data
        road_data = get_road_network_data(longitude, latitude, radius)
        
        # Step 3: Extract features from map data
        features = extract_features(poi_data, road_data, longitude, latitude, radius)
        
        # Step 4: Calculate Feng Shui score
        result = calculate_feng_shui_score(features)
        
        # Add location info to response
        result['location'] = {
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius
        }
        
        logger.info(f"Analysis complete. Final score: {result['final_score']}")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error analyzing location: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/geocode', methods=['POST'])
def geocode():
    """
    Geocode an address to get latitude and longitude.
    
    Expected JSON input:
    {
        "address": string
    }
    
    Returns JSON:
    {
        "latitude": float,
        "longitude": float,
        "formatted_address": string
    }
    """
    try:
        data = request.get_json()
        address = data.get('address')
        
        if not address:
            return jsonify({"error": "address is required"}), 400
        
        logger.info(f"Geocoding address: {address}")
        
        result = geocode_address(address)
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({"error": "Address not found"}), 404
            
    except Exception as e:
        logger.error(f"Error geocoding address: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    logger.info("Starting Feng Shui Analysis API Server...")
    app.run(debug=False, host='0.0.0.0', port=5000)

