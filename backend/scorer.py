# Module for calculating final weighted Feng Shui scores and generating suggestions

import logging
from typing import Dict, List
import math

from config import config
from ai_model import predict_feng_shui_score

logger = logging.getLogger(__name__)


def calculate_feng_shui_score(features: Dict) -> Dict:
    """
    Calculate final Feng Shui score based on extracted features.
    Combines traditional Feng Shui principles with AI predictions.
    
    Args:
        features: Dictionary of extracted features
    
    Returns:
        Dictionary with:
        {
            'final_score': float (0-100),
            'category_scores': dict,
            'explanations': list,
            'suggestions': list,
            'yin_yang_balance': float,
            'five_elements': dict,
            'qi_flow_score': float
        }
    """
    logger.info("Calculating comprehensive Feng Shui score...")
    
    # Calculate individual category scores (0-100 scale)
    category_scores = {
        'green_space': calculate_green_space_score(features),
        'water_element': calculate_water_score(features),
        'building_harmony': calculate_building_score(features),
        'road_accessibility': calculate_road_score(features),
        'orientation': calculate_orientation_category_score(features),
        'environment': calculate_environment_score(features),
        'spiritual_energy': calculate_spiritual_score(features)
    }
    
    # Calculate Yin-Yang balance
    yin_yang_balance = calculate_yin_yang_balance(features, category_scores)
    category_scores['yin_yang_balance'] = yin_yang_balance
    
    # Calculate Five Elements harmony
    five_elements = calculate_five_elements(features, category_scores)
    category_scores['five_elements_harmony'] = five_elements['overall_score']
    
    # Calculate Qi flow score
    qi_flow_score = calculate_qi_flow(features, category_scores)
    category_scores['qi_flow'] = qi_flow_score
    
    # Calculate traditional weighted score
    weights = config.FEATURE_WEIGHTS
    traditional_score = (
        category_scores['green_space'] * weights['green_area_ratio'] +
        category_scores['water_element'] * weights['water_proximity'] +
        category_scores['building_harmony'] * weights['building_density'] +
        category_scores['road_accessibility'] * weights['road_density'] +
        category_scores['orientation'] * weights['orientation'] +
        category_scores['environment'] * weights['environmental'] +
        category_scores['spiritual_energy'] * weights['spiritual']
    )
    
    # Get AI prediction
    ai_result = predict_feng_shui_score(features)
    
    # Combine traditional and AI scores (70% traditional, 30% AI)
    if ai_result:
        ai_score = ai_result['ai_score']
        final_score = traditional_score * 0.7 + ai_score * 0.3
        ai_explanations = ai_result.get('feature_importance', {}).get('explanations', [])
    else:
        final_score = traditional_score
        ai_score = None
        ai_explanations = []
    
    # Apply Yin-Yang and Five Elements modifiers
    final_score = apply_feng_shui_modifiers(final_score, yin_yang_balance, five_elements['overall_score'])
    
    # Generate explanations
    explanations = generate_explanations(features, category_scores, final_score)
    explanations.extend(ai_explanations)
    
    # Generate improvement suggestions
    suggestions = generate_improvement_suggestions(features, category_scores)
    
    result = {
        'final_score': round(final_score, 2),
        'traditional_score': round(traditional_score, 2),
        'ai_score': round(ai_score, 2) if ai_score else None,
        'category_scores': {k: round(v, 2) for k, v in category_scores.items()},
        'yin_yang_balance': round(yin_yang_balance, 2),
        'five_elements': {k: round(v, 2) for k, v in five_elements.items()},
        'qi_flow_score': round(qi_flow_score, 2),
        'explanations': explanations,
        'suggestions': suggestions
    }
    
    logger.info(f"Final Feng Shui score: {result['final_score']:.2f} (Traditional: {traditional_score:.2f}, AI: {ai_score})")
    return result


def calculate_green_space_score(features: Dict) -> float:
    """Calculate green space category score (0-100)."""
    ratio = features.get('green_area_ratio', 0)
    # Linear scale: 0.3 ratio = 100 points
    score = min(ratio / 0.3 * 100, 100)
    return score


def calculate_water_score(features: Dict) -> float:
    """Calculate water element score (0-100)."""
    proximity = features.get('water_proximity', 0)
    # Direct conversion to 0-100 scale
    return proximity * 100


def calculate_building_score(features: Dict) -> float:
    """Calculate building harmony score (0-100)."""
    density = features.get('building_density', 0)
    # Lower density is better for Feng Shui
    # Invert the score: low density = high score
    score = (1 - density) * 100
    return score


def calculate_road_score(features: Dict) -> float:
    """Calculate road accessibility score (0-100)."""
    density = features.get('road_intersection_density', 0)
    # Moderate density is best (too low = isolated, too high = chaotic)
    if density < 0.3:
        score = density / 0.3 * 70  # Low density = moderate score
    elif density < 0.7:
        score = 70 + (density - 0.3) / 0.4 * 30  # Optimal range
    else:
        score = 100 - (density - 0.7) / 0.3 * 30  # Too high = lower score
    return max(0, min(score, 100))


def calculate_orientation_category_score(features: Dict) -> float:
    """Calculate orientation category score (0-100)."""
    orientation = features.get('orientation_score', 0.5)
    return orientation * 100


def calculate_environment_score(features: Dict) -> float:
    """Calculate environmental quality score (0-100)."""
    quality = features.get('environmental_quality', 0)
    return quality * 100


def calculate_spiritual_score(features: Dict) -> float:
    """Calculate spiritual energy score (0-100)."""
    presence = features.get('spiritual_presence', 0)
    return presence * 100


def generate_explanations(features: Dict, 
                         category_scores: Dict,
                         final_score: float) -> List[str]:
    """
    Generate human-readable explanations for the Feng Shui analysis.
    
    Args:
        features: Extracted features
        category_scores: Category scores
        final_score: Final weighted score
    
    Returns:
        List of explanation strings
    """
    explanations = []
    
    # Overall assessment
    if final_score >= 80:
        explanations.append(
            "🌟 This location has excellent Feng Shui characteristics with strong positive energy flow."
        )
    elif final_score >= 60:
        explanations.append(
            "✨ This location has good Feng Shui with favorable environmental balance."
        )
    elif final_score >= 40:
        explanations.append(
            "⚖️ This location has average Feng Shui with mixed positive and negative influences."
        )
    else:
        explanations.append(
            "⚠️ This location has challenging Feng Shui characteristics that may benefit from remedies."
        )
    
    # Green space analysis
    green_score = category_scores['green_space']
    if green_score >= 70:
        explanations.append(
            f"🌳 Excellent green space coverage ({green_score:.0f}/100) promotes vitality and fresh chi energy."
        )
    elif green_score >= 40:
        explanations.append(
            f"🌿 Moderate green space presence ({green_score:.0f}/100) provides adequate natural balance."
        )
    else:
        explanations.append(
            f"🏙️ Limited green space ({green_score:.0f}/100). Consider adding plants or visiting nearby parks regularly."
        )
    
    # Water element analysis
    water_score = category_scores['water_element']
    if water_score >= 70:
        explanations.append(
            f"💧 Water element is well-positioned ({water_score:.0f}/100), bringing prosperity and wealth energy."
        )
    elif water_score >= 40:
        explanations.append(
            f"🌊 Water element is present ({water_score:.0f}/100) but could be optimized for better flow."
        )
    else:
        explanations.append(
            f"🏜️ Water element is distant ({water_score:.0f}/100). Consider water features to enhance energy."
        )
    
    # Building harmony
    building_score = category_scores['building_harmony']
    if building_score >= 70:
        explanations.append(
            f"🏘️ Building density is balanced ({building_score:.0f}/100), allowing energy to flow freely."
        )
    elif building_score >= 40:
        explanations.append(
            f"🏢 Building density is moderate ({building_score:.0f}/100) with acceptable energy circulation."
        )
    else:
        explanations.append(
            f"🌆 High building density ({building_score:.0f}/100) may restrict energy flow. Ensure good ventilation."
        )
    
    # Orientation
    orientation_score = category_scores['orientation']
    if orientation_score >= 70:
        explanations.append(
            f"🧭 Building orientations are favorable ({orientation_score:.0f}/100) for capturing positive energy."
        )
    elif orientation_score < 50:
        explanations.append(
            f"🔄 Building orientations could be improved ({orientation_score:.0f}/100). Use mirrors or adjustments."
        )
    
    # Environmental quality
    env_score = category_scores['environment']
    if env_score >= 60:
        explanations.append(
            f"🏥 Good access to essential services ({env_score:.0f}/100) supports overall wellbeing."
        )
    
    # Spiritual energy
    spiritual_score = category_scores['spiritual_energy']
    if spiritual_score >= 60:
        explanations.append(
            f"🕉️ Spiritual presence is strong ({spiritual_score:.0f}/100), providing grounding energy."
        )
    
    return explanations


def calculate_yin_yang_balance(features: Dict, category_scores: Dict) -> float:
    """
    Calculate Yin-Yang balance score.
    
    Yin elements: Water, stillness, green spaces
    Yang elements: Buildings, roads, activity
    
    Perfect balance = 100, complete imbalance = 0
    
    Args:
        features: Extracted features
        category_scores: Category scores
    
    Returns:
        Yin-Yang balance score (0-100)
    """
    # Yin score (calm, natural elements)
    yin_score = (
        features.get('green_area_ratio', 0) * 0.4 +
        features.get('water_proximity', 0) * 0.4 +
        features.get('spiritual_presence', 0) * 0.2
    )
    
    # Yang score (active, built elements)
    yang_score = (
        features.get('building_density', 0) * 0.5 +
        features.get('road_intersection_density', 0) * 0.5
    )
    
    # Calculate balance (closer to 0.5 = better balance)
    balance_ratio = yin_score / (yin_score + yang_score + 0.001)  # Avoid division by zero
    
    # Score balance: optimal ratio is 0.4-0.6
    if 0.4 <= balance_ratio <= 0.6:
        balance_score = 100
    else:
        deviation = abs(balance_ratio - 0.5) * 2  # 0-1 scale
        balance_score = (1 - deviation) * 100
    
    logger.info(f"Yin-Yang balance: {balance_score:.2f} (Yin: {yin_score:.2f}, Yang: {yang_score:.2f})")
    return balance_score


def calculate_five_elements(features: Dict, category_scores: Dict) -> Dict:
    """
    Calculate Five Elements (Wu Xing) harmony score.
    
    Five Elements:
    - Wood: Green spaces, growth
    - Fire: Orientation, sun exposure
    - Earth: Buildings, stability
    - Metal: Roads, structure
    - Water: Water bodies, flow
    
    Args:
        features: Extracted features
        category_scores: Category scores
    
    Returns:
        Dictionary with individual element scores and overall harmony
    """
    # Wood element (growth, vitality)
    wood_score = features.get('green_area_ratio', 0) * 100
    
    # Fire element (energy, light)
    fire_score = features.get('orientation_score', 0) * 100
    
    # Earth element (stability, grounding)
    earth_score = category_scores.get('building_harmony', 50)
    
    # Metal element (structure, organization)
    metal_score = category_scores.get('road_accessibility', 50)
    
    # Water element (flow, wealth)
    water_score = features.get('water_proximity', 0) * 100
    
    # Calculate harmony (balance among all elements)
    element_scores = [wood_score, fire_score, earth_score, metal_score, water_score]
    avg_score = sum(element_scores) / len(element_scores)
    
    # Penalty for extreme imbalance
    variance = sum((score - avg_score) ** 2 for score in element_scores) / len(element_scores)
    std_dev = math.sqrt(variance)
    
    # Lower standard deviation = better harmony
    harmony_penalty = min(std_dev / 30, 1.0)  # Normalize
    overall_harmony = avg_score * (1 - harmony_penalty * 0.3)
    
    logger.info(f"Five Elements harmony: {overall_harmony:.2f}")
    
    return {
        'wood': wood_score,
        'fire': fire_score,
        'earth': earth_score,
        'metal': metal_score,
        'water': water_score,
        'overall_score': overall_harmony
    }


def calculate_qi_flow(features: Dict, category_scores: Dict) -> float:
    """
    Calculate Qi (energy) flow score.
    
    Good Qi flow requires:
    - Not too dense (allows movement)
    - Good orientation (captures positive energy)
    - Balance between open and enclosed spaces
    
    Args:
        features: Extracted features
        category_scores: Category scores
    
    Returns:
        Qi flow score (0-100)
    """
    # Factors affecting Qi flow
    
    # 1. Building density (too high blocks Qi)
    density = features.get('building_density', 0)
    density_score = (1 - density) * 100
    
    # 2. Road network (facilitates Qi circulation)
    road_score = category_scores.get('road_accessibility', 50)
    
    # 3. Green spaces (generate positive Qi)
    green_score = category_scores.get('green_space', 50)
    
    # 4. Water (channels Qi)
    water_score = category_scores.get('water_element', 50)
    
    # Weighted combination
    qi_flow = (
        density_score * 0.3 +
        road_score * 0.2 +
        green_score * 0.3 +
        water_score * 0.2
    )
    
    logger.info(f"Qi flow score: {qi_flow:.2f}")
    return qi_flow


def apply_feng_shui_modifiers(base_score: float, 
                              yin_yang_balance: float,
                              five_elements_harmony: float) -> float:
    """
    Apply Yin-Yang and Five Elements modifiers to base score.
    
    Args:
        base_score: Base Feng Shui score
        yin_yang_balance: Yin-Yang balance score
        five_elements_harmony: Five Elements harmony score
    
    Returns:
        Modified final score
    """
    # Apply modifiers (each can boost or reduce score by up to 10%)
    yin_yang_modifier = (yin_yang_balance / 100 - 0.5) * 0.1
    elements_modifier = (five_elements_harmony / 100 - 0.5) * 0.1
    
    modified_score = base_score * (1 + yin_yang_modifier + elements_modifier)
    
    # Ensure score stays in valid range
    return max(0, min(modified_score, 100))


def generate_improvement_suggestions(features: Dict, category_scores: Dict) -> List[str]:
    """
    Generate actionable improvement suggestions based on low-scoring factors.
    
    Args:
        features: Extracted features
        category_scores: Category scores
    
    Returns:
        List of suggestion strings
    """
    suggestions = []
    
    # Green space suggestions
    if category_scores.get('green_space', 100) < 50:
        suggestions.append(
            "🌱 Increase greenery: Add indoor plants, visit nearby parks regularly, "
            "or create a small garden to enhance Wood element and positive Qi."
        )
    
    # Water element suggestions
    if category_scores.get('water_element', 100) < 50:
        suggestions.append(
            "💧 Enhance water element: Place a small water fountain near the entrance, "
            "add an aquarium, or display water imagery to attract wealth energy."
        )
    
    # Building density suggestions
    if category_scores.get('building_harmony', 100) < 50:
        suggestions.append(
            "🏢 Improve space harmony: Use mirrors to create sense of openness, "
            "ensure good ventilation, and declutter to allow Qi to flow freely."
        )
    
    # Road accessibility suggestions
    road_score = category_scores.get('road_accessibility', 50)
    if road_score < 40:
        suggestions.append(
            "🚗 Improve accessibility: This area may be too isolated. "
            "Consider locations with better transportation connections."
        )
    elif road_score > 80:
        suggestions.append(
            "🔇 Reduce noise impact: High traffic density may bring excessive Yang energy. "
            "Use sound barriers, plants, or water features to create a buffer."
        )
    
    # Orientation suggestions
    if category_scores.get('orientation', 100) < 50:
        suggestions.append(
            "🧭 Optimize orientation: Use mirrors to redirect energy flow, "
            "place important furniture facing auspicious directions (south/southeast)."
        )
    
    # Environmental quality suggestions
    if category_scores.get('environment', 100) < 50:
        suggestions.append(
            "🏥 Enhance environment: Ensure access to healthcare and educational facilities. "
            "Choose locations with good community infrastructure."
        )
    
    # Spiritual energy suggestions
    if category_scores.get('spiritual_energy', 100) < 30:
        suggestions.append(
            "🙏 Strengthen spiritual energy: Display religious or spiritual symbols, "
            "practice meditation, or visit nearby temples to enhance spiritual connection."
        )
    
    # Yin-Yang balance suggestions
    yin_yang = category_scores.get('yin_yang_balance', 100)
    if yin_yang < 70:
        yin_ratio = features.get('green_area_ratio', 0) + features.get('water_proximity', 0)
        yang_ratio = features.get('building_density', 0) + features.get('road_intersection_density', 0)
        
        if yin_ratio < yang_ratio:
            suggestions.append(
                "☯️ Balance Yin-Yang: Too much Yang (activity) energy. "
                "Add calm elements like plants, water, and quiet spaces."
            )
        else:
            suggestions.append(
                "☯️ Balance Yin-Yang: Too much Yin (stillness) energy. "
                "Add active elements like bright lights and social activities."
            )
    
    # Five Elements harmony suggestions
    if category_scores.get('five_elements_harmony', 100) < 60:
        suggestions.append(
            "🌟 Harmonize Five Elements: Ensure presence of all five elements - "
            "Wood (plants), Fire (light), Earth (ceramics), Metal (decor), Water (fountains)."
        )
    
    # Qi flow suggestions
    if category_scores.get('qi_flow', 100) < 60:
        suggestions.append(
            "💨 Improve Qi flow: Remove obstacles blocking pathways, "
            "keep spaces clean and organized, ensure good air circulation."
        )
    
    # If score is already high, provide maintenance suggestions
    if not suggestions:
        suggestions.append(
            "✨ Excellent Feng Shui! Maintain this positive energy by keeping spaces clean, "
            "refreshing plants regularly, and practicing gratitude."
        )
    
    logger.info(f"Generated {len(suggestions)} improvement suggestions")
    return suggestions
