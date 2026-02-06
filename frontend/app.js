// Main JavaScript application file for handling UI interactions and API calls

let map = null;
let marker = null;
let circle = null;
let selectedLocation = null;

// Initialize the map when the page loads
window.onload = function() {
    initMap();
    setupEventListeners();
    console.log('Feng Shui Analysis System initialized');
};

// Initialize AMap
function initMap() {
    // Default location: Beijing (you can change this to any location)
    const defaultCenter = [116.397428, 39.90923]; // [longitude, latitude]
    
    map = new AMap.Map('map-container', {
        zoom: 13,
        center: defaultCenter,
        viewMode: '2D',
        layers: [
            new AMap.TileLayer.Satellite(), // Satellite imagery
            new AMap.TileLayer.RoadNet()    // Road network overlay
        ]
    });

    // Add layer switcher control for users to switch between satellite and normal view
    AMap.plugin(['AMap.MapType'], function() {
        const mapType = new AMap.MapType({
            defaultType: 1, // 0 for normal, 1 for satellite
            showRoad: true  // Show road network on satellite view
        });
        map.addControl(mapType);
    });

    // Add click event listener to the map
    map.on('click', handleMapClick);
    
    console.log('Map initialized at:', defaultCenter, 'in satellite view');
}

// Handle map click events
async function handleMapClick(e) {
    const lng = e.lnglat.getLng();
    const lat = e.lnglat.getLat();
    
    console.log('Clicked location - Latitude:', lat, 'Longitude:', lng);
    
    // Store the selected location
    selectedLocation = { lat, lng, address: 'Loading address...' };
    
    // Display the selected location with coordinates first
    displaySelectedLocation(lat, lng, 'Loading address...');
    
    // Remove existing marker and circle if any
    if (marker) {
        map.remove(marker);
    }
    if (circle) {
        map.remove(circle);
    }
    
    // Reverse geocode to get address name
    getAddressFromCoordinates(lng, lat).then(address => {
        selectedLocation.address = address;
        displaySelectedLocation(lat, lng, address);
    }).catch(error => {
        console.error('Reverse geocoding failed:', error);
        displaySelectedLocation(lat, lng, `${lat.toFixed(6)}, ${lng.toFixed(6)}`);
    });
    
    // Create new marker at clicked location
    marker = new AMap.Marker({
        position: [lng, lat],
        map: map,
        title: 'Selected Location'
    });
    
    // Get radius value from input
    const radius = parseInt(document.getElementById('radius').value) || 500;
    
    // Draw circle around the marker
    drawCircle(lng, lat, radius);
    
    // Enable the analyze button
    document.getElementById('analyzeBtn').disabled = false;
}

// Draw a circular radius around the location
function drawCircle(lng, lat, radius) {
    circle = new AMap.Circle({
        center: [lng, lat],
        radius: radius, // in meters
        fillColor: '#00b2d5',
        fillOpacity: 0.2,
        strokeColor: '#00b2d5',
        strokeWeight: 2,
        strokeOpacity: 0.5,
        map: map
    });
    
    console.log(`Circle drawn with radius: ${radius} meters`);
}

// Update circle radius when input changes
function updateCircleRadius() {
    if (selectedLocation && circle) {
        const newRadius = parseInt(document.getElementById('radius').value) || 500;
        circle.setRadius(newRadius);
        
        // Update the displayed value
        const radiusValueSpan = document.getElementById('radiusValue');
        if (radiusValueSpan) {
            radiusValueSpan.textContent = newRadius;
        }
        
        // Update slider background gradient
        const slider = document.getElementById('radius');
        const percentage = ((newRadius - 100) / (5000 - 100)) * 100;
        slider.style.background = `linear-gradient(to right, #00A99D 0%, #00A99D ${percentage}%, #E2E8F0 ${percentage}%, #E2E8F0 100%)`;
        
        console.log(`Circle radius updated to: ${newRadius} meters`);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Analyze button click
    document.getElementById('analyzeBtn').addEventListener('click', analyzeLocation);
    
    // Radius slider input - real-time update
    document.getElementById('radius').addEventListener('input', function(e) {
        const value = parseInt(e.target.value);
        const radiusValueSpan = document.getElementById('radiusValue');
        if (radiusValueSpan) {
            radiusValueSpan.textContent = value;
        }
        
        // Update slider background gradient
        const percentage = ((value - 100) / (5000 - 100)) * 100;
        e.target.style.background = `linear-gradient(to right, #00A99D 0%, #00A99D ${percentage}%, #E2E8F0 ${percentage}%, #E2E8F0 100%)`;
        
        updateCircleRadius();
    });
    
    // Radius input change
    document.getElementById('radius').addEventListener('change', updateCircleRadius);
    
    // Search button click
    document.getElementById('searchBtn').addEventListener('click', function(e) {
        e.preventDefault();
        searchLocation();
    });
    
    // Enter key in search input
    document.getElementById('locationInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            searchLocation();
        }
    });
    
    // Add input event listener for better UX
    document.getElementById('locationInput').addEventListener('input', function(e) {
        const value = e.target.value;
        console.log('Search input:', value);
    });
}

// Display selected location with address
function displaySelectedLocation(lat, lng, address = null) {
    const displayDiv = document.getElementById('selectedLocationDisplay');
    displayDiv.style.display = 'block';
    
    const addressText = address || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    const coordsText = `(${lat.toFixed(5)}, ${lng.toFixed(5)})`;
    
    displayDiv.innerHTML = `
        <span class="location-icon">📍</span>
        <span class="location-name">${addressText}</span>
        <span class="location-coords">${coordsText}</span>
    `;
    console.log('Location displayed:', addressText, lat, lng);
}

// Reverse geocode coordinates to get address name
async function getAddressFromCoordinates(lng, lat) {
    try {
        // Use AMap's built-in geocoder
        return new Promise((resolve, reject) => {
            AMap.plugin('AMap.Geocoder', function() {
                const geocoder = new AMap.Geocoder();
                geocoder.getAddress([lng, lat], function(status, result) {
                    if (status === 'complete' && result.info === 'OK') {
                        const address = result.regeocode.formattedAddress;
                        console.log('Reverse geocoded address:', address);
                        resolve(address);
                    } else {
                        reject(new Error('Reverse geocoding failed'));
                    }
                });
            });
        });
    } catch (error) {
        console.error('Error in reverse geocoding:', error);
        return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    }
}

// Search for location by address or place name
function searchLocation() {
    const query = document.getElementById('locationInput').value.trim();
    if (!query) {
        alert('Please enter a location to search');
        return;
    }
    
    console.log('🔍 Searching for location:', query);
    
    // Show loading indicator
    const searchBtn = document.getElementById('searchBtn');
    const originalText = searchBtn.textContent;
    searchBtn.textContent = '🔄 Searching...';
    searchBtn.disabled = true;
    
    // Use AMap's geocoder - no city restriction for better international support
    AMap.plugin('AMap.Geocoder', function() {
        const geocoder = new AMap.Geocoder({
            // No city restriction - allows searching anywhere
        });
        
        geocoder.getLocation(query, function(status, result) {
            // Reset button
            searchBtn.textContent = originalText;
            searchBtn.disabled = false;
            
            if (status === 'complete' && result.info === 'OK') {
                if (result.geocodes && result.geocodes.length > 0) {
                    const location = result.geocodes[0];
                    const lng = location.location.lng;
                    const lat = location.location.lat;
                    const address = location.formattedAddress;
                    
                    console.log('✅ Found location:', address);
                    console.log('   Coordinates:', lat, lng);
                    
                    // Store location with address
                    selectedLocation = { lat, lng, address };
                    
                    // Move map to the location
                    map.setCenter([lng, lat]);
                    map.setZoom(15);
                    
                    // Remove existing marker and circle
                    if (marker) {
                        map.remove(marker);
                    }
                    if (circle) {
                        map.remove(circle);
                    }
                    
                    // Create marker
                    marker = new AMap.Marker({
                        position: [lng, lat],
                        map: map,
                        title: address
                    });
                    
                    // Draw circle
                    const radius = parseInt(document.getElementById('radius').value) || 500;
                    drawCircle(lng, lat, radius);
                    
                    // Display location
                    displaySelectedLocation(lat, lng, address);
                    
                    // Enable analyze button
                    document.getElementById('analyzeBtn').disabled = false;
                    
                    console.log('✅ Search complete!');
                } else {
                    console.error('No geocoding results found');
                    alert('Location not found. Please try:\n• 天安门 (Chinese)\n• Tiananmen Square (English)\n• Full address with city name');
                }
            } else {
                console.error('Geocoding failed:', status, result);
                alert('Location not found. Please try:\n• Chinese: 天安门, 故宫, 北京大学\n• English: Tiananmen, Forbidden City, Peking University\n• Include city name for better results');
            }
        });
    });
}

// Send location data to backend API
async function analyzeLocation() {
    if (!selectedLocation) {
        alert('Please click on the map or search for a location first!');
        console.error('No location selected');
        return;
    }
    
    const radius = parseInt(document.getElementById('radius').value) || 500;
    
    // Use the current selectedLocation
    const requestData = {
        latitude: selectedLocation.lat,
        longitude: selectedLocation.lng,
        radius: radius
    };
    
    console.log('🚀 Analyzing location:', requestData);
    console.log('Selected location object:', selectedLocation);
    
    try {
        // Show loading state
        displayLoading();
        
        // Send POST request to backend
        const response = await fetch('http://localhost:5000/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Response from backend:', data);
        
        // Display the results in the dashboard
        displayResults(data);
        
    } catch (error) {
        console.error('Error analyzing location:', error);
        displayError(error.message);
    }
}

// Display loading state
function displayLoading() {
    const dashboard = document.getElementById('dashboard');
    dashboard.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <h3>Analyzing Feng Shui...</h3>
            <p>Evaluating environmental factors and energy patterns</p>
        </div>
    `;
}

// Display error message
function displayError(message) {
    const dashboard = document.getElementById('dashboard');
    dashboard.innerHTML = `
        <div class="error">
            <h3>❌ Error</h3>
            <p>${message}</p>
            <p>Make sure the backend server is running.</p>
        </div>
    `;
}

// Display analysis results in the dashboard
function displayResults(data) {
    const dashboard = document.getElementById('dashboard');
    
    // Extract data from response
    const finalScore = data.final_score || 0;
    const traditionalScore = data.traditional_score || 0;
    const aiScore = data.ai_score;
    const categoryScores = data.category_scores || {};
    const explanations = data.explanations || [];
    const suggestions = data.suggestions || [];
    const yinYangBalance = data.yin_yang_balance || 0;
    const fiveElements = data.five_elements || {};
    const qiFlowScore = data.qi_flow_score || 0;
    const location = data.location || {};
    
    console.log('📊 Displaying results for:', location);
    console.log('Final Score:', finalScore);
    
    // Build HTML for the comprehensive dashboard
    let html = `
        <div class="results">
            <!-- Location Info -->
            <div class="location-info">
                <h4>📍 Analyzed Location</h4>
                <p><strong>Coordinates:</strong> ${location.latitude?.toFixed(6) || 'N/A'}, ${location.longitude?.toFixed(6) || 'N/A'}</p>
                <p><strong>Analysis Radius:</strong> ${location.radius || 'N/A'}m</p>
            </div>
            
            <!-- Final Score Section -->
            <div class="final-score">
                <h3>Overall Feng Shui Score</h3>
                <div class="score-display">
                    <div class="score-circle ${getScoreClass(finalScore)}">
                        <span class="score-value">${finalScore.toFixed(1)}</span>
                        <span class="score-label">/ 100</span>
                    </div>
                    <div class="score-details">
                        <p class="score-description">${getScoreDescription(finalScore)}</p>
                        <div class="sub-scores">
                            <span class="sub-score">Traditional: ${traditionalScore.toFixed(1)}</span>
                            ${aiScore ? `<span class="sub-score">AI: ${aiScore.toFixed(1)}</span>` : ''}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Core Feng Shui Metrics -->
            <div class="feng-shui-core">
                <h3>Core Feng Shui Metrics</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon">☯️</div>
                        <div class="metric-name">Yin-Yang Balance</div>
                        <div class="metric-value ${getScoreClass(yinYangBalance)}">${yinYangBalance.toFixed(1)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">💨</div>
                        <div class="metric-name">Qi Flow</div>
                        <div class="metric-value ${getScoreClass(qiFlowScore)}">${qiFlowScore.toFixed(1)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">🌟</div>
                        <div class="metric-name">Five Elements</div>
                        <div class="metric-value ${getScoreClass(fiveElements.overall_score || 0)}">${(fiveElements.overall_score || 0).toFixed(1)}</div>
                    </div>
                </div>
            </div>
            
            <!-- Five Elements Chart -->
            <div class="five-elements-section">
                <h3>Five Elements (Wu Xing) Analysis</h3>
                <canvas id="fiveElementsChart"></canvas>
            </div>
            
            <!-- Category Scores Chart -->
            <div class="category-scores">
                <h3>Category Breakdown</h3>
                <canvas id="categoryChart"></canvas>
            </div>
            
            <!-- Detailed Explanations -->
            <div class="explanations">
                <h3>📝 Detailed Analysis</h3>
                <ul class="explanation-list">
    `;
    
    // Add each explanation
    if (explanations.length > 0) {
        explanations.forEach(explanation => {
            html += `<li>${explanation}</li>`;
        });
    } else {
        html += `<li>No detailed explanations available.</li>`;
    }
    
    html += `
                </ul>
            </div>
            
            <!-- Improvement Suggestions -->
            <div class="suggestions">
                <h3>💡 Improvement Suggestions</h3>
                <ul class="suggestion-list">
    `;
    
    // Add each suggestion
    if (suggestions.length > 0) {
        suggestions.forEach(suggestion => {
            html += `<li>${suggestion}</li>`;
        });
    } else {
        html += `<li>No suggestions available.</li>`;
    }
    
    html += `
                </ul>
            </div>
        </div>
    `;
    
    dashboard.innerHTML = html;
    
    // Render charts
    renderFiveElementsChart(fiveElements);
    renderCategoryChart(categoryScores);
}

// Helper function to get score class for styling
function getScoreClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'average';
    return 'poor';
}

// Helper function to get score description
function getScoreDescription(score) {
    if (score >= 80) return 'Excellent Feng Shui - Highly auspicious location!';
    if (score >= 60) return 'Good Feng Shui - Favorable location with positive energy.';
    if (score >= 40) return 'Average Feng Shui - Neutral location with mixed influences.';
    return 'Poor Feng Shui - Consider alternative locations or remedies.';
}

// Helper function to format category names
function formatCategoryName(category) {
    return category
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Render Five Elements radar chart
function renderFiveElementsChart(fiveElements) {
    const canvas = document.getElementById('fiveElementsChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if any
    if (canvas.chart) {
        canvas.chart.destroy();
    }
    
    const elementData = {
        'Wood 🌳': fiveElements.wood || 0,
        'Fire 🔥': fiveElements.fire || 0,
        'Earth ⛰️': fiveElements.earth || 0,
        'Metal ⚔️': fiveElements.metal || 0,
        'Water 💧': fiveElements.water || 0
    };
    
    canvas.chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: Object.keys(elementData),
            datasets: [{
                label: 'Element Strength',
                data: Object.values(elementData),
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(102, 126, 234, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    },
                    pointLabels: {
                        font: {
                            size: 12
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.r.toFixed(1) + '/100';
                        }
                    }
                }
            }
        }
    });
}

// Render category scores horizontal bar chart
function renderCategoryChart(categoryScores) {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if any
    if (canvas.chart) {
        canvas.chart.destroy();
    }
    
    // Filter out the special categories and get main categories
    const mainCategories = {};
    for (const [key, value] of Object.entries(categoryScores)) {
        if (!['yin_yang_balance', 'five_elements_harmony', 'qi_flow'].includes(key)) {
            mainCategories[key] = value;
        }
    }
    
    const labels = Object.keys(mainCategories).map(formatCategoryName);
    const data = Object.values(mainCategories);
    
    // Color code based on score
    const backgroundColors = data.map(score => {
        if (score >= 80) return 'rgba(40, 167, 69, 0.8)';  // Green
        if (score >= 60) return 'rgba(23, 162, 184, 0.8)';  // Blue
        if (score >= 40) return 'rgba(255, 193, 7, 0.8)';   // Yellow
        return 'rgba(220, 53, 69, 0.8)';  // Red
    });
    
    canvas.chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score',
                data: data,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value;
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.x.toFixed(1) + '/100';
                        }
                    }
                }
            }
        }
    });
}
