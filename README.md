# AI-Based Feng Shui Smart Urban Analysis System

## 🌿 Project Overview
An intelligent system for analyzing urban locations based on Feng Shui principles using AI and map data. Combines traditional Feng Shui wisdom with modern machine learning (Random Forest) and real-time map data from AMap API.

## ✨ Features

### Frontend
- 🗺️ Interactive AMap integration with marker placement
- 🎯 Configurable analysis radius (100-5000 meters)
- 📊 Comprehensive dashboard with charts (Chart.js)
- 🎨 Color-coded scoring system
- 📱 Responsive design

### Backend
- 🤖 Random Forest AI model for predictions
- 🧮 Traditional Feng Shui scoring (Yin-Yang, Five Elements, Qi Flow)
- 🗺️ AMap API integration for POI and road data
- 🔍 Feature extraction (green space, water, density, orientation)
- 💡 Intelligent improvement suggestions

### Analysis Components
1. **Green Space** - Parks and vegetation coverage
2. **Water Element** - Proximity to water bodies
3. **Building Harmony** - Building density and spatial balance
4. **Road Accessibility** - Transportation and intersection density
5. **Orientation** - Building facing directions
6. **Environmental Quality** - Nearby amenities (hospitals, schools)
7. **Spiritual Energy** - Religious and cultural sites
8. **Yin-Yang Balance** - Balance between calm and active elements
9. **Five Elements (Wu Xing)** - Wood, Fire, Earth, Metal, Water harmony
10. **Qi Flow** - Energy circulation score

## 📁 Project Structure
```
fengshui-ai/
├── frontend/
│   ├── index.html           # Main HTML page
│   ├── app.js               # Frontend logic and API calls
│   ├── styles.css           # Styling and responsive design
│   ├── components/          # Future UI components
│   └── utils/               # Helper functions
├── backend/
│   ├── app.py               # Flask server with API endpoints
│   ├── config.py            # Configuration and API keys
│   ├── amap_service.py      # AMap API integration
│   ├── feature_extractor.py # Feature extraction logic
│   ├── ai_model.py          # Random Forest model
│   ├── scorer.py            # Feng Shui scoring engine
│   ├── train_model.py       # Model training script
│   ├── models/              # Saved AI models (auto-created)
│   └── utils/               # Backend helpers
├── README.md
├── requirements.txt
└── .gitignore
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- AMap API account (for API key and security key)
- Modern web browser

### 1. Backend Setup

#### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Step 2: Configure API Keys
Create a `.env` file in the `backend` folder:
```env
AMAP_API_KEY=your_amap_api_key_here
AMAP_SECURITY_KEY=your_amap_security_key_here
DEBUG=True
PORT=5000
```

#### Step 3: Train the AI Model
```bash
python train_model.py
```
This will generate synthetic data and train the Random Forest model. The model will be saved in `backend/models/`.

#### Step 4: Run the Backend Server
```bash
python app.py
```
Server will start at `http://localhost:5000`

### 2. Frontend Setup

#### Step 1: Configure AMap Keys
Edit `frontend/index.html` and replace the placeholders:
```html
<script>
    window._AMapSecurityConfig = {
        securityJsCode: 'YOUR_SECURITY_KEY'
    };
</script>
<script src="https://webapi.amap.com/maps?v=2.0&key=YOUR_AMAP_KEY"></script>
```

#### Step 2: Open Frontend
Simply open `frontend/index.html` in your web browser, or use a local server:
```bash
# Using Python
cd frontend
python -m http.server 8000

# Then visit: http://localhost:8000
```

## 🎮 Usage

1. **Open the Application** - Load the frontend in your browser
2. **Click on the Map** - Select a location by clicking anywhere
3. **Adjust Radius** - Change the analysis radius (default 500m)
4. **Click Analyze** - Backend processes the location data
5. **View Results** - Dashboard shows comprehensive Feng Shui analysis

## 📊 API Endpoints

### POST `/api/analyze`
Analyze a location's Feng Shui score.

**Request:**
```json
{
  "latitude": 39.90923,
  "longitude": 116.397428,
  "radius": 500
}
```

**Response:**
```json
{
  "final_score": 75.2,
  "traditional_score": 73.5,
  "ai_score": 78.3,
  "category_scores": {
    "green_space": 68.5,
    "water_element": 82.3,
    ...
  },
  "yin_yang_balance": 71.2,
  "five_elements": {
    "wood": 68.5,
    "fire": 75.0,
    "earth": 80.2,
    "metal": 65.3,
    "water": 82.3,
    "overall_score": 74.3
  },
  "qi_flow_score": 72.8,
  "explanations": [...],
  "suggestions": [...]
}
```

### POST `/api/geocode`
Convert address to coordinates.

**Request:**
```json
{
  "address": "天安门, 北京"
}
```

### GET `/health`
Health check endpoint.

## 🧠 AI Model Details

### Random Forest Regressor
- **Features**: 7 environmental indicators
- **Training**: Synthetic data with rule-based labels
- **Performance**: R² > 0.9 on test set
- **Explainability**: Feature importance extraction

### Synthetic Data Generation
The model is trained on 1000-2000 synthetic samples with features:
- Green area ratio (0-1)
- Water proximity (0-1)
- Building density (0-1)
- Road intersection density (0-1)
- Orientation score (0-1)
- Environmental quality (0-1)
- Spiritual presence (0-1)

## 🎯 Feng Shui Principles Implemented

### Yin-Yang Balance
- **Yin**: Water, green spaces, spiritual sites (calm energy)
- **Yang**: Buildings, roads, activity (active energy)
- **Goal**: 40-60% balance ratio

### Five Elements (Wu Xing)
- **Wood** (木): Green spaces, growth
- **Fire** (火): Orientation, sunlight
- **Earth** (土): Buildings, stability
- **Metal** (金): Roads, structure
- **Water** (水): Water bodies, flow

### Qi Flow
Energy circulation based on:
- Building density (allows movement)
- Road network (facilitates circulation)
- Green spaces (generates positive Qi)
- Water features (channels Qi)

## 🔧 Configuration

Edit `backend/config.py` to adjust:
- POI search categories
- Feature weights for scoring
- Search radius limits
- API endpoints

## 📝 License
(To be determined)

## 🤝 Contributing
(Guidelines to be added)

## 📧 Contact
(Contact information to be added)

---

**Built with ❤️ using Flask, Chart.js, AMap API, and scikit-learn**
