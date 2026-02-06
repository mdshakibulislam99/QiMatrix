# AI model module for training, loading, and predicting Feng Shui scores

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import logging
import os
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# Model file path
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'feng_shui_rf_model.pkl')


def generate_synthetic_data(n_samples: int = 1000) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Generate synthetic urban environmental data for training.
    
    Features:
    - green_area_ratio: 0-1 (higher is better)
    - water_proximity: 0-1 (higher is better)
    - building_density: 0-1 (lower is better)
    - road_intersection_density: 0-1 (moderate is best)
    - orientation_score: 0-1 (higher is better)
    - environmental_quality: 0-1 (higher is better)
    - spiritual_presence: 0-1 (higher is better)
    
    Labels: Feng Shui score 0-100 (rule-based logic)
    
    Args:
        n_samples: Number of samples to generate
    
    Returns:
        Tuple of (features DataFrame, labels array)
    """
    logger.info(f"Generating {n_samples} synthetic training samples...")
    
    np.random.seed(42)
    
    # Generate features with realistic distributions
    data = {
        'green_area_ratio': np.random.beta(2, 5, n_samples),  # Skewed toward lower values
        'water_proximity': np.random.beta(2, 3, n_samples),
        'building_density': np.random.beta(5, 2, n_samples),  # Skewed toward higher values (urban)
        'road_intersection_density': np.random.beta(3, 3, n_samples),
        'orientation_score': np.random.beta(3, 2, n_samples),
        'environmental_quality': np.random.beta(3, 3, n_samples),
        'spiritual_presence': np.random.beta(2, 5, n_samples)
    }
    
    features_df = pd.DataFrame(data)
    
    # Generate labels using rule-based logic
    labels = generate_rule_based_scores(features_df)
    
    logger.info(f"Synthetic data generated. Score range: {labels.min():.1f} - {labels.max():.1f}")
    
    return features_df, labels


def generate_rule_based_scores(features_df: pd.DataFrame) -> np.ndarray:
    """
    Generate Feng Shui scores using rule-based logic.
    
    Args:
        features_df: DataFrame with feature columns
    
    Returns:
        Array of scores (0-100)
    """
    scores = []
    
    for _, row in features_df.iterrows():
        # Base score from features
        score = 0
        
        # Green space (0-20 points)
        score += row['green_area_ratio'] * 20
        
        # Water proximity (0-15 points)
        score += row['water_proximity'] * 15
        
        # Building density (0-15 points, inverted)
        score += (1 - row['building_density']) * 15
        
        # Road density (0-10 points, optimal at 0.5)
        road_score = 1 - abs(row['road_intersection_density'] - 0.5) * 2
        score += max(road_score, 0) * 10
        
        # Orientation (0-15 points)
        score += row['orientation_score'] * 15
        
        # Environmental quality (0-15 points)
        score += row['environmental_quality'] * 15
        
        # Spiritual presence (0-10 points)
        score += row['spiritual_presence'] * 10
        
        # Add some noise for realism
        noise = np.random.normal(0, 3)
        score += noise
        
        # Ensure score is in valid range
        score = np.clip(score, 0, 100)
        
        scores.append(score)
    
    return np.array(scores)


def train_model(n_samples: int = 1000, test_size: float = 0.2) -> Dict:
    """
    Train a Random Forest Regressor on synthetic data.
    
    Args:
        n_samples: Number of synthetic samples to generate
        test_size: Proportion of data for testing
    
    Returns:
        Dictionary with training metrics and model info
    """
    logger.info("Starting Random Forest model training...")
    
    # Generate synthetic data
    X, y = generate_synthetic_data(n_samples)
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    logger.info(f"Training set size: {len(X_train)}, Test set size: {len(X_test)}")
    
    # Initialize Random Forest model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    # Train the model
    logger.info("Training model...")
    model.fit(X_train, y_train)
    
    # Evaluate on test set
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    logger.info(f"Model training complete. MSE: {mse:.2f}, R²: {r2:.3f}")
    
    # Save the model
    save_model(model, X.columns.tolist())
    
    return {
        'mse': mse,
        'r2': r2,
        'feature_names': X.columns.tolist(),
        'n_samples': n_samples,
        'model_path': MODEL_PATH
    }


def save_model(model: RandomForestRegressor, feature_names: List[str]):
    """
    Save the trained model to disk.
    
    Args:
        model: Trained RandomForestRegressor
        feature_names: List of feature names
    """
    # Create models directory if it doesn't exist
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    # Save model and metadata
    model_data = {
        'model': model,
        'feature_names': feature_names
    }
    
    joblib.dump(model_data, MODEL_PATH)
    logger.info(f"Model saved to {MODEL_PATH}")


def load_model() -> Optional[Tuple[RandomForestRegressor, List[str]]]:
    """
    Load the trained model from disk.
    
    Returns:
        Tuple of (model, feature_names) or None if model doesn't exist
    """
    if not os.path.exists(MODEL_PATH):
        logger.warning(f"Model file not found at {MODEL_PATH}")
        return None
    
    try:
        model_data = joblib.load(MODEL_PATH)
        logger.info("Model loaded successfully")
        return model_data['model'], model_data['feature_names']
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return None


def predict_feng_shui_score(features: Dict) -> Optional[Dict]:
    """
    Predict Feng Shui score using the trained Random Forest model.
    
    Args:
        features: Dictionary of extracted features
    
    Returns:
        Dictionary with prediction and feature importance,
        or None if model is not available
    """
    # Load the model
    model_data = load_model()
    
    if model_data is None:
        logger.warning("Model not found. Training a new model...")
        train_model()
        model_data = load_model()
        
        if model_data is None:
            logger.error("Failed to train and load model")
            return None
    
    model, feature_names = model_data
    
    # Prepare features in correct order
    try:
        feature_values = [features.get(name, 0.0) for name in feature_names]
        X = np.array(feature_values).reshape(1, -1)
        
        # Make prediction
        predicted_score = model.predict(X)[0]
        
        # Ensure score is in valid range
        predicted_score = np.clip(predicted_score, 0, 100)
        
        # Get feature importance
        feature_importance = get_feature_importance(model, feature_names, feature_values)
        
        logger.info(f"AI predicted score: {predicted_score:.2f}")
        
        return {
            'ai_score': predicted_score,
            'feature_importance': feature_importance
        }
        
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        return None


def get_feature_importance(model: RandomForestRegressor,
                          feature_names: List[str],
                          feature_values: List[float]) -> Dict:
    """
    Extract feature importance from Random Forest model.
    
    Args:
        model: Trained RandomForestRegressor
        feature_names: List of feature names
        feature_values: List of feature values for current prediction
    
    Returns:
        Dictionary with feature importance and explanations
    """
    # Get feature importance from model
    importances = model.feature_importances_
    
    # Combine with feature names and values
    importance_data = []
    for name, importance, value in zip(feature_names, importances, feature_values):
        importance_data.append({
            'feature': name,
            'importance': float(importance),
            'value': float(value),
            'contribution': float(importance * value * 100)  # Approximate contribution to score
        })
    
    # Sort by importance
    importance_data.sort(key=lambda x: x['importance'], reverse=True)
    
    return {
        'feature_importance': importance_data,
        'explanations': generate_ai_explanations(importance_data)
    }


def generate_ai_explanations(importance_data: List[Dict]) -> List[str]:
    """
    Generate human-readable explanations based on feature importance.
    
    Args:
        importance_data: List of feature importance dictionaries
    
    Returns:
        List of explanation strings
    """
    explanations = []
    
    # Get top 3 most important features
    top_features = importance_data[:3]
    
    feature_descriptions = {
        'green_area_ratio': ('green space coverage', 'vegetation and parks'),
        'water_proximity': ('water element proximity', 'rivers and lakes'),
        'building_density': ('building density', 'urban crowding'),
        'road_intersection_density': ('road network density', 'traffic flow'),
        'orientation_score': ('building orientation', 'directional alignment'),
        'environmental_quality': ('environmental quality', 'nearby amenities'),
        'spiritual_presence': ('spiritual energy', 'sacred sites')
    }
    
    explanations.append("🤖 AI Model Analysis:")
    
    for i, item in enumerate(top_features, 1):
        feature = item['feature']
        importance = item['importance']
        value = item['value']
        
        desc, detail = feature_descriptions.get(feature, (feature, feature))
        
        if value > 0.7:
            quality = "excellent"
        elif value > 0.5:
            quality = "good"
        elif value > 0.3:
            quality = "moderate"
        else:
            quality = "low"
        
        explanations.append(
            f"  {i}. {desc.title()} is the {'most' if i == 1 else 'next'} influential factor "
            f"(importance: {importance:.1%}), with {quality} value ({value:.2f})."
        )
    
    return explanations
