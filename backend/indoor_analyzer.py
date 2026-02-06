"""
Indoor Room Feng Shui Analysis Backend
Handles design-based and photo-based room analysis
"""

def analyze_room_design(elements, room_type):
    """
    Analyze a room based on placed design elements
    
    Args:
        elements: List of placed elements with types and positions
        room_type: Type of room (bedroom, living, office, etc.)
    
    Returns:
        dict: Analysis results with scores and recommendations
    """
    
    # Count elements by category
    element_counts = {
        'wood': 0,
        'fire': 0,
        'earth': 0,
        'metal': 0,
        'water': 0
    }
    
    energy_balance = {
        'yin': 0,
        'yang': 0
    }
    
    # Element feng shui properties
    element_properties = {
        # Furniture
        'bed': {'element': 'earth', 'energy': 'yin'},
        'sofa': {'element': 'earth', 'energy': 'yin'},
        'desk': {'element': 'wood', 'energy': 'yang'},
        'table': {'element': 'wood', 'energy': 'neutral'},
        'chair': {'element': 'wood', 'energy': 'yang'},
        'wardrobe': {'element': 'wood', 'energy': 'yin'},
        'bookshelf': {'element': 'wood', 'energy': 'yang'},
        'tv': {'element': 'fire', 'energy': 'yang'},
        
        # Decor
        'mirror': {'element': 'water', 'energy': 'yang'},
        'painting': {'element': 'fire', 'energy': 'yang'},
        'clock': {'element': 'metal', 'energy': 'yang'},
        'vase': {'element': 'earth', 'energy': 'yin'},
        'rug': {'element': 'earth', 'energy': 'yin'},
        'curtain': {'element': 'water', 'energy': 'yin'},
        'window': {'element': 'metal', 'energy': 'yang'},
        'door': {'element': 'wood', 'energy': 'yang'},
        'fountain': {'element': 'water', 'energy': 'yang'},
        'crystals': {'element': 'earth', 'energy': 'yang'},
        
        # Plants
        'bamboo': {'element': 'wood', 'energy': 'yang'},
        'plant': {'element': 'wood', 'energy': 'yang'},
        'bonsai': {'element': 'wood', 'energy': 'yin'},
        'flowers': {'element': 'wood', 'energy': 'yang'},
        
        # Lighting
        'lamp': {'element': 'fire', 'energy': 'yang'},
        'chandelier': {'element': 'fire', 'energy': 'yang'},
        'candle': {'element': 'fire', 'energy': 'yang'}
    }
    
    # Count elements
    for element in elements:
        element_type = element['type']
        if element_type in element_properties:
            props = element_properties[element_type]
            element_counts[props['element']] += 1
            if props['energy'] != 'neutral':
                energy_balance[props['energy']] += 1
    
    # Calculate scores
    element_balance_score = calculate_element_balance(element_counts)
    energy_score = calculate_energy_balance(energy_balance)
    spacial_score = calculate_spacial_score(len(elements))
    functional_score = calculate_functional_score(elements, room_type)
    
    overall_score = int(
        element_balance_score * 0.3 +
        energy_score * 0.25 +
        spacial_score * 0.25 +
        functional_score * 0.20
    )
    
    # Generate recommendations
    recommendations = generate_design_recommendations(
        element_counts,
        energy_balance,
        elements,
        room_type
    )
    
    return {
        'overall_score': overall_score,
        'element_balance': element_balance_score,
        'energy_score': energy_score,
        'spacial_score': spacial_score,
        'functional_score': functional_score,
        'element_counts': element_counts,
        'energy_balance': energy_balance,
        'recommendations': recommendations
    }


def calculate_element_balance(counts):
    """Calculate five elements balance score"""
    total = sum(counts.values())
    if total == 0:
        return 0
    
    # Ideal is balanced distribution
    ideal = total / 5
    variance = sum(abs(count - ideal) for count in counts.values())
    score = max(0, 100 - (variance / total) * 50)
    
    return int(score)


def calculate_energy_balance(energy):
    """Calculate yin-yang balance score"""
    total = energy['yin'] + energy['yang']
    if total == 0:
        return 50
    
    ratio = energy['yang'] / total
    
    # Ideal ratio is 40-60% yang
    if 0.4 <= ratio <= 0.6:
        return 100
    elif 0.3 <= ratio <= 0.7:
        return 80
    else:
        return 60


def calculate_spacial_score(element_count):
    """Calculate space flow score based on element density"""
    if element_count < 5:
        return 90
    elif element_count < 10:
        return 85
    elif element_count < 15:
        return 75
    elif element_count < 20:
        return 65
    else:
        return 50  # Too cluttered


def calculate_functional_score(elements, room_type):
    """Calculate functional layout score based on room type"""
    element_types = [e['type'] for e in elements]
    score = 70  # Base score
    
    # Room-specific requirements
    if room_type == 'bedroom':
        if 'bed' in element_types:
            score += 10
        if 'plant' in element_types:
            score += 5
        if 'mirror' in element_types and 'bed' in element_types:
            score -= 10  # Mirror facing bed is inauspicious
        if 'lamp' in element_types:
            score += 5
    
    elif room_type == 'living':
        if 'sofa' in element_types:
            score += 10
        if 'plant' in element_types:
            score += 5
        if 'lamp' in element_types or 'chandelier' in element_types:
            score += 5
    
    elif room_type == 'office':
        if 'desk' in element_types:
            score += 10
        if 'chair' in element_types:
            score += 5
        if 'plant' in element_types:
            score += 5
        if 'bookshelf' in element_types:
            score += 5
    
    return min(100, score)


def generate_design_recommendations(elements, energy, placed_elements, room_type):
    """Generate feng shui recommendations"""
    recommendations = []
    
    # Element recommendations
    if elements['wood'] < 2:
        recommendations.append('Add more wood elements (plants, furniture) for growth energy')
    
    if elements['fire'] == 0:
        recommendations.append('Include fire elements (candles, red colors) for passion and warmth')
    
    if elements['water'] == 0:
        recommendations.append('Add water elements (fountain, mirror) for flow and prosperity')
    
    if elements['earth'] < 2:
        recommendations.append('Incorporate earth elements (crystals, pottery) for stability')
    
    if elements['metal'] == 0:
        recommendations.append('Include metal elements (clocks, metal frames) for clarity')
    
    # Energy balance recommendations
    total_energy = energy['yin'] + energy['yang']
    if total_energy > 0:
        yang_ratio = energy['yang'] / total_energy
        
        if yang_ratio > 0.7:
            recommendations.append('Balance yang energy with softer, yin elements (curtains, rugs)')
        elif yang_ratio < 0.3:
            recommendations.append('Add more yang energy with lighting and active elements')
    
    # Room-specific recommendations
    element_types = [e['type'] for e in placed_elements]
    
    if room_type == 'bedroom':
        if 'plant' not in element_types:
            recommendations.append('Add plants for fresh air and positive energy')
        if 'mirror' in element_types:
            recommendations.append('⚠️ Avoid placing mirrors directly facing the bed')
    
    if len(placed_elements) > 15:
        recommendations.append('Consider decluttering - too many items can block energy flow')
    
    if not recommendations:
        recommendations.append('✓ Your room design shows good feng shui balance!')
    
    return recommendations


def analyze_room_photos(photos):
    """
    Analyze room based on uploaded photos (simulated AI analysis)
    In production, this would use computer vision AI
    
    Args:
        photos: Dict of photo data (north, south, east, west, floor)
    
    Returns:
        dict: Analysis results with scores and recommendations
    """
    import random
    
    # Count uploaded photos
    photo_count = sum(1 for p in photos.values() if p is not None)
    
    # Simulate AI analysis with base score
    base_score = 60 + (photo_count * 5)
    
    # Add variation
    overall_score = min(100, max(50, base_score + random.randint(-7, 7)))
    
    # Generate category scores
    categories = {
        'lighting': random.randint(70, 95),
        'space_flow': random.randint(65, 90),
        'color_harmony': random.randint(60, 85),
        'furniture_placement': random.randint(65, 90),
        'declutter': random.randint(55, 80)
    }
    
    # Generate recommendations
    recommendations = [
        'Consider adding more natural light sources to enhance positive energy',
        'Balance the five elements with appropriate colors and materials',
        'Ensure clear pathways for qi energy flow throughout the room',
        'Position furniture to face auspicious directions based on Bagua',
        'Add plants for wood element energy and air purification',
        'Use mirrors strategically to expand space and reflect positive energy',
        'Incorporate water features for wealth and prosperity energy'
    ]
    
    # Select random recommendations
    selected_recs = random.sample(recommendations, min(5, len(recommendations)))
    
    return {
        'overall_score': overall_score,
        'categories': categories,
        'recommendations': selected_recs
    }
