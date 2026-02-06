/**
 * Indoor Feng Shui Analysis System
 * Supports 3D Design Mode and Photo Upload Mode
 */

// Global state
let currentMode = null;
let placedElements = [];
let uploadedPhotos = {
    north: null,
    south: null,
    east: null,
    west: null,
    floor: null
};

// Element data for feng shui analysis
const elementFengShuiData = {
    // Furniture
    bed: { element: 'earth', energy: 'yin', placement: 'important', bagua: 'relationship' },
    sofa: { element: 'earth', energy: 'yin', placement: 'center', bagua: 'family' },
    desk: { element: 'wood', energy: 'yang', placement: 'power', bagua: 'career' },
    table: { element: 'wood', energy: 'neutral', placement: 'center', bagua: 'health' },
    chair: { element: 'wood', energy: 'yang', placement: 'supportive', bagua: 'support' },
    wardrobe: { element: 'wood', energy: 'yin', placement: 'storage', bagua: 'wealth' },
    bookshelf: { element: 'wood', energy: 'yang', placement: 'knowledge', bagua: 'knowledge' },
    tv: { element: 'fire', energy: 'yang', placement: 'entertainment', bagua: 'fame' },
    
    // Decor
    mirror: { element: 'water', energy: 'yang', placement: 'reflective', bagua: 'expansion' },
    painting: { element: 'fire', energy: 'yang', placement: 'inspiration', bagua: 'creativity' },
    clock: { element: 'metal', energy: 'yang', placement: 'time', bagua: 'helpful' },
    vase: { element: 'earth', energy: 'yin', placement: 'decorative', bagua: 'peace' },
    rug: { element: 'earth', energy: 'yin', placement: 'grounding', bagua: 'stability' },
    curtain: { element: 'water', energy: 'yin', placement: 'privacy', bagua: 'protection' },
    window: { element: 'metal', energy: 'yang', placement: 'openness', bagua: 'opportunities' },
    door: { element: 'wood', energy: 'yang', placement: 'entry', bagua: 'career' },
    fountain: { element: 'water', energy: 'yang', placement: 'flow', bagua: 'wealth' },
    crystals: { element: 'earth', energy: 'yang', placement: 'energy', bagua: 'clarity' },
    
    // Plants
    bamboo: { element: 'wood', energy: 'yang', placement: 'growth', bagua: 'prosperity' },
    plant: { element: 'wood', energy: 'yang', placement: 'life', bagua: 'health' },
    bonsai: { element: 'wood', energy: 'yin', placement: 'balance', bagua: 'wisdom' },
    flowers: { element: 'wood', energy: 'yang', placement: 'beauty', bagua: 'love' },
    
    // Lighting
    lamp: { element: 'fire', energy: 'yang', placement: 'illumination', bagua: 'clarity' },
    chandelier: { element: 'fire', energy: 'yang', placement: 'grandeur', bagua: 'wealth' },
    candle: { element: 'fire', energy: 'yang', placement: 'warmth', bagua: 'passion' }
};

// ==================== MODE SELECTION ====================
function selectMode(mode) {
    currentMode = mode;
    document.getElementById('modeSelection').classList.remove('active');
    
    if (mode === 'design') {
        document.getElementById('designMode').classList.add('active');
    } else if (mode === 'upload') {
        document.getElementById('uploadMode').classList.add('active');
    }
}

function backToSelection() {
    currentMode = null;
    document.getElementById('modeSelection').classList.add('active');
    document.getElementById('designMode').classList.remove('active');
    document.getElementById('uploadMode').classList.remove('active');
    
    // Reset states
    clearCanvas();
    resetUpload();
}

// ==================== DESIGN MODE ====================

// Drag and Drop functionality
function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    const elementType = ev.target.getAttribute('data-element');
    ev.dataTransfer.setData("element", elementType);
}

function drop(ev) {
    ev.preventDefault();
    const canvas = document.getElementById('roomCanvas');
    const rect = canvas.getBoundingClientRect();
    
    const x = ev.clientX - rect.left;
    const y = ev.clientY - rect.top;
    const elementType = ev.dataTransfer.getData("element");
    
    if (elementType) {
        placeElement(elementType, x, y);
    }
}

function placeElement(elementType, x, y) {
    const canvas = document.getElementById('roomCanvas');
    const element = document.createElement('div');
    const elementId = 'element_' + Date.now();
    
    element.className = 'placed-element element-' + elementType;
    element.id = elementId;
    element.setAttribute('data-element-type', elementType);
    
    // Get icon from library
    const libraryItem = document.querySelector(`.element-item[data-element="${elementType}"]`);
    const icon = libraryItem.querySelector('.element-icon').textContent;
    
    // Create realistic 3D HTML structure based on element type
    const elementContent = create3DElement(elementType);
    
    element.innerHTML = `
        <div class="element-content">
            ${elementContent}
            <button class="remove-element" onclick="removeElement('${elementId}')">×</button>
        </div>
    `;
    
    element.style.left = x + 'px';
    element.style.top = y + 'px';
    
    // Make it draggable within canvas
    makeDraggable(element);
    
    canvas.appendChild(element);
    
    // Add to placed elements array
    placedElements.push({
        id: elementId,
        type: elementType,
        x: x,
        y: y,
        icon: icon
    });
    
    updatePlacedItemsList();
    updateItemCount();
    
    // Hide guide if first element
    if (placedElements.length === 1) {
        document.querySelector('.canvas-guide').style.display = 'none';
    }
}

// Create realistic 3D element HTML structure
function create3DElement(type) {
    const elementStructures = {
        'bed': `
            <div class="bed-frame">
                <div class="bed-mattress"></div>
                <div class="bed-pillow"></div>
            </div>
        `,
        'sofa': `
            <div class="sofa-base">
                <div class="sofa-back"></div>
                <div class="sofa-arm sofa-arm-left"></div>
                <div class="sofa-arm sofa-arm-right"></div>
            </div>
        `,
        'desk': `
            <div class="desk-top"></div>
            <div class="desk-leg desk-leg-1"></div>
            <div class="desk-leg desk-leg-2"></div>
        `,
        'chair': `
            <div class="chair-seat">
                <div class="chair-back"></div>
                <div class="chair-leg chair-leg-1"></div>
                <div class="chair-leg chair-leg-2"></div>
            </div>
        `,
        'table': `
            <div class="table-top"></div>
            <div class="table-leg table-leg-center"></div>
        `,
        'plant': `
            <div class="plant-pot">
                <div class="plant-stem"></div>
                <div class="plant-leaves"></div>
            </div>
        `,
        'bamboo': `
            <div class="plant-pot">
                <div class="plant-stem"></div>
                <div class="plant-leaves"></div>
            </div>
        `,
        'bonsai': `
            <div class="plant-pot">
                <div class="plant-stem"></div>
                <div class="plant-leaves"></div>
            </div>
        `,
        'flowers': `
            <div class="plant-pot">
                <div class="plant-stem"></div>
                <div class="plant-leaves"></div>
            </div>
        `,
        'lamp': `
            <div class="lamp-base">
                <div class="lamp-pole"></div>
                <div class="lamp-shade"></div>
            </div>
        `,
        'mirror': `
            <div class="mirror-frame">
                <div class="mirror-glass"></div>
            </div>
        `,
        'tv': `
            <div class="tv-screen"></div>
            <div class="tv-stand"></div>
        `,
        'window': `
            <div class="window-frame">
                <div class="window-glass"></div>
                <div class="window-divider-v"></div>
                <div class="window-divider-h"></div>
            </div>
        `
    };
    
    // Return 3D structure or fallback to icon
    return elementStructures[type] || `<span class="element-icon-large">${getElementIcon(type)}</span>`;
}

function getElementIcon(type) {
    const libraryItem = document.querySelector(`.element-item[data-element="${type}"]`);
    return libraryItem ? libraryItem.querySelector('.element-icon').textContent : '📦';
}

function makeDraggable(element) {
    let isDragging = false;
    let offsetX, offsetY;
    
    element.addEventListener('mousedown', function(e) {
        if (e.target.classList.contains('remove-element')) return;
        isDragging = true;
        offsetX = e.clientX - element.offsetLeft;
        offsetY = e.clientY - element.offsetTop;
        element.style.cursor = 'grabbing';
    });
    
    document.addEventListener('mousemove', function(e) {
        if (isDragging) {
            const canvas = document.getElementById('roomCanvas');
            const rect = canvas.getBoundingClientRect();
            let newX = e.clientX - rect.left - offsetX;
            let newY = e.clientY - rect.top - offsetY;
            
            // Keep within bounds
            newX = Math.max(0, Math.min(newX, canvas.clientWidth - element.offsetWidth));
            newY = Math.max(0, Math.min(newY, canvas.clientHeight - element.offsetHeight));
            
            element.style.left = newX + 'px';
            element.style.top = newY + 'px';
        }
    });
    
    document.addEventListener('mouseup', function() {
        if (isDragging) {
            isDragging = false;
            element.style.cursor = 'grab';
            
            // Update position in array
            const elementId = element.id;
            const item = placedElements.find(el => el.id === elementId);
            if (item) {
                item.x = parseInt(element.style.left);
                item.y = parseInt(element.style.top);
            }
        }
    });
}

function removeElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.remove();
    }
    
    placedElements = placedElements.filter(el => el.id !== elementId);
    updatePlacedItemsList();
    updateItemCount();
    
    if (placedElements.length === 0) {
        document.querySelector('.canvas-guide').style.display = 'flex';
    }
}

function clearCanvas() {
    const canvas = document.getElementById('roomCanvas');
    const elements = canvas.querySelectorAll('.placed-element');
    elements.forEach(el => el.remove());
    
    placedElements = [];
    updatePlacedItemsList();
    updateItemCount();
    document.querySelector('.canvas-guide').style.display = 'flex';
    document.getElementById('designResults').style.display = 'none';
}

function updatePlacedItemsList() {
    const list = document.getElementById('placedItemsList');
    
    if (placedElements.length === 0) {
        list.innerHTML = '<p class="empty-list">No items placed yet</p>';
        return;
    }
    
    list.innerHTML = placedElements.map(item => `
        <div class="placed-item">
            <span class="item-icon">${item.icon}</span>
            <span class="item-name">${item.type}</span>
            <button class="remove-item-btn" onclick="removeElement('${item.id}')">×</button>
        </div>
    `).join('');
}

function updateItemCount() {
    document.getElementById('itemCount').textContent = placedElements.length;
}

// Filter elements
function filterCategory(category) {
    const items = document.querySelectorAll('.element-item');
    const categories = document.querySelectorAll('.category');
    
    // Update active category
    categories.forEach(cat => cat.classList.remove('active'));
    event.target.classList.add('active');
    
    items.forEach(item => {
        if (category === 'all' || item.getAttribute('data-category') === category) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

function filterElements() {
    const searchTerm = document.getElementById('elementSearch').value.toLowerCase();
    const items = document.querySelectorAll('.element-item');
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// Analyze design
async function analyzeDesign() {
    if (placedElements.length === 0) {
        alert('Please place some elements in your room before analyzing!');
        return;
    }
    
    const roomType = document.getElementById('roomTypeDesign').value;
    
    // Show loading
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Analyzing...';
    
    // Calculate feng shui score
    const analysis = calculateDesignFengShui(placedElements, roomType);
    
    // Display results
    displayDesignResults(analysis);
    
    // Scroll to results
    setTimeout(() => {
        document.getElementById('designResults').scrollIntoView({ behavior: 'smooth' });
        btn.disabled = false;
        btn.textContent = 'Analyze Room';
    }, 1000);
}

function calculateDesignFengShui(elements, roomType) {
    // Calculate element balance
    const elementCounts = { wood: 0, fire: 0, earth: 0, metal: 0, water: 0 };
    const energyBalance = { yin: 0, yang: 0 };
    
    elements.forEach(item => {
        const data = elementFengShuiData[item.type];
        if (data) {
            elementCounts[data.element]++;
            energyBalance[data.energy === 'neutral' ? 'yin' : data.energy]++;
        }
    });
    
    // Calculate scores
    const elementBalance = calculateElementBalanceScore(elementCounts);
    const energyScore = calculateEnergyBalanceScore(energyBalance);
    const spacialScore = calculateSpacialScore(elements);
    const functionalScore = calculateFunctionalScore(elements, roomType);
    
    const overallScore = Math.round(
        (elementBalance * 0.3) +
        (energyScore * 0.25) +
        (spacialScore * 0.25) +
        (functionalScore * 0.20)
    );
    
    return {
        overallScore,
        elementBalance,
        energyScore,
        spacialScore,
        functionalScore,
        elementCounts,
        energyBalance,
        recommendations: generateRecommendations(elementCounts, energyBalance, elements, roomType)
    };
}

function calculateElementBalanceScore(counts) {
    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    if (total === 0) return 0;
    
    // Ideal is balanced distribution
    const ideal = total / 5;
    const variance = Object.values(counts).reduce((sum, count) => {
        return sum + Math.abs(count - ideal);
    }, 0);
    
    const score = Math.max(0, 100 - (variance / total) * 50);
    return Math.round(score);
}

function calculateEnergyBalanceScore(energy) {
    const total = energy.yin + energy.yang;
    if (total === 0) return 50;
    
    const ratio = energy.yang / total;
    // Ideal ratio is 40-60% yang
    if (ratio >= 0.4 && ratio <= 0.6) {
        return 100;
    } else if (ratio >= 0.3 && ratio <= 0.7) {
        return 80;
    } else {
        return 60;
    }
}

function calculateSpacialScore(elements) {
    // Check for clutter (too many elements in small space)
    const elementDensity = elements.length;
    
    if (elementDensity < 5) return 90;
    if (elementDensity < 10) return 85;
    if (elementDensity < 15) return 75;
    if (elementDensity < 20) return 65;
    return 50; // Too cluttered
}

function calculateFunctionalScore(elements, roomType) {
    const types = elements.map(e => e.type);
    let score = 70; // Base score
    
    // Room-specific requirements
    if (roomType === 'bedroom') {
        if (types.includes('bed')) score += 10;
        if (types.includes('plant')) score += 5;
        if (types.includes('mirror') && types.includes('bed')) score -= 10; // Mirror facing bed is bad
        if (types.includes('lamp')) score += 5;
    } else if (roomType === 'living') {
        if (types.includes('sofa')) score += 10;
        if (types.includes('plant')) score += 5;
        if (types.includes('lamp') || types.includes('chandelier')) score += 5;
    } else if (roomType === 'office') {
        if (types.includes('desk')) score += 10;
        if (types.includes('chair')) score += 5;
        if (types.includes('plant')) score += 5;
        if (types.includes('bookshelf')) score += 5;
    }
    
    return Math.min(100, score);
}

function generateRecommendations(elements, energy, placed, roomType) {
    const recommendations = [];
    
    // Element recommendations
    if (elements.wood < 2) recommendations.push('Add more wood elements (plants, furniture) for growth energy');
    if (elements.fire === 0) recommendations.push('Include fire elements (candles, red colors) for passion and warmth');
    if (elements.water === 0) recommendations.push('Add water elements (fountain, mirror) for flow and prosperity');
    if (elements.earth < 2) recommendations.push('Incorporate earth elements (crystals, pottery) for stability');
    if (elements.metal === 0) recommendations.push('Include metal elements (clocks, metal frames) for clarity');
    
    // Energy recommendations
    const totalEnergy = energy.yin + energy.yang;
    const yangRatio = energy.yang / totalEnergy;
    
    if (yangRatio > 0.7) {
        recommendations.push('Balance yang energy with softer, yin elements (curtains, rugs)');
    } else if (yangRatio < 0.3) {
        recommendations.push('Add more yang energy with lighting and active elements');
    }
    
    // Room-specific
    if (roomType === 'bedroom') {
        if (!placed.some(e => e.type === 'plant')) {
            recommendations.push('Add plants for fresh air and positive energy');
        }
        if (placed.some(e => e.type === 'mirror')) {
            recommendations.push('⚠️ Avoid placing mirrors directly facing the bed');
        }
    }
    
    if (placed.length > 15) {
        recommendations.push('Consider decluttering - too many items can block energy flow');
    }
    
    if (recommendations.length === 0) {
        recommendations.push('✓ Your room design shows good feng shui balance!');
    }
    
    return recommendations;
}

function displayDesignResults(analysis) {
    const resultsSection = document.getElementById('designResults');
    resultsSection.style.display = 'block';
    
    // Overall score
    document.getElementById('overallScore').textContent = analysis.overallScore;
    
    const rating = getRating(analysis.overallScore);
    document.getElementById('scoreRating').textContent = rating.text;
    document.getElementById('scoreRating').style.color = rating.color;
    
    // Detailed results
    const resultsHTML = `
        <div class="result-item">
            <h4>Five Elements Balance</h4>
            <div class="score-bar">
                <div class="score-fill" style="width: ${analysis.elementBalance}%"></div>
                <span class="score-value">${analysis.elementBalance}/100</span>
            </div>
            <div class="element-distribution">
                <span>🌳 Wood: ${analysis.elementCounts.wood}</span>
                <span>🔥 Fire: ${analysis.elementCounts.fire}</span>
                <span>🏔️ Earth: ${analysis.elementCounts.earth}</span>
                <span>⚙️ Metal: ${analysis.elementCounts.metal}</span>
                <span>💧 Water: ${analysis.elementCounts.water}</span>
            </div>
        </div>
        
        <div class="result-item">
            <h4>Yin-Yang Energy Balance</h4>
            <div class="score-bar">
                <div class="score-fill" style="width: ${analysis.energyScore}%"></div>
                <span class="score-value">${analysis.energyScore}/100</span>
            </div>
            <p>Yin: ${analysis.energyBalance.yin} | Yang: ${analysis.energyBalance.yang}</p>
        </div>
        
        <div class="result-item">
            <h4>Space Flow & Circulation</h4>
            <div class="score-bar">
                <div class="score-fill" style="width: ${analysis.spacialScore}%"></div>
                <span class="score-value">${analysis.spacialScore}/100</span>
            </div>
        </div>
        
        <div class="result-item">
            <h4>Functional Layout</h4>
            <div class="score-bar">
                <div class="score-fill" style="width: ${analysis.functionalScore}%"></div>
                <span class="score-value">${analysis.functionalScore}/100</span>
            </div>
        </div>
    `;
    
    document.getElementById('analysisResults').innerHTML = resultsHTML;
    
    // Recommendations
    const recsHTML = analysis.recommendations.map(rec => `
        <div class="recommendation-item">
            <span class="rec-icon">${rec.startsWith('⚠️') ? '⚠️' : rec.startsWith('✓') ? '✓' : '💡'}</span>
            <p>${rec.replace('⚠️', '').replace('✓', '')}</p>
        </div>
    `).join('');
    
    document.getElementById('recommendations').innerHTML = recsHTML;
}

function getRating(score) {
    if (score >= 90) return { text: 'Excellent Feng Shui!', color: '#10b981' };
    if (score >= 75) return { text: 'Good Balance', color: '#3b82f6' };
    if (score >= 60) return { text: 'Fair - Room for Improvement', color: '#f59e0b' };
    return { text: 'Needs Improvement', color: '#ef4444' };
}

// ==================== UPLOAD MODE ====================

function previewPhoto(direction, input) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById(`preview${direction.charAt(0).toUpperCase() + direction.slice(1)}`);
            const label = document.getElementById(`label${direction.charAt(0).toUpperCase() + direction.slice(1)}`);
            
            preview.innerHTML = `<img src="${e.target.result}" alt="${direction} view">`;
            preview.style.display = 'block';
            label.textContent = '✓ Uploaded';
            label.style.background = '#10b981';
            
            uploadedPhotos[direction] = e.target.result;
            checkUploadComplete();
        };
        reader.readAsDataURL(file);
    }
}

function checkUploadComplete() {
    const uploadCount = Object.values(uploadedPhotos).filter(photo => photo !== null).length;
    const btn = document.getElementById('analyzePhotosBtn');
    
    if (uploadCount >= 3) {
        btn.disabled = false;
    } else {
        btn.disabled = true;
    }
}

function resetUpload() {
    uploadedPhotos = { north: null, south: null, east: null, west: null, floor: null };
    
    ['North', 'South', 'East', 'West', 'Floor'].forEach(dir => {
        const input = document.getElementById(`photo${dir}`);
        const preview = document.getElementById(`preview${dir}`);
        const label = document.getElementById(`label${dir}`);
        
        if (input) input.value = '';
        if (preview) {
            preview.innerHTML = '';
            preview.style.display = 'none';
        }
        if (label) {
            label.textContent = 'Click to Upload';
            label.style.background = '';
        }
    });
    
    document.getElementById('analyzePhotosBtn').disabled = true;
    document.getElementById('uploadResults').style.display = 'none';
}

async function analyzePhotos() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Analyzing Photos...';
    
    // Simulate AI analysis (in production, this would call the backend API)
    setTimeout(() => {
        const analysis = simulatePhotoAnalysis();
        displayUploadResults(analysis);
        document.getElementById('uploadResults').scrollIntoView({ behavior: 'smooth' });
        btn.disabled = false;
        btn.textContent = 'Analyze Room';
    }, 2000);
}

function simulatePhotoAnalysis() {
    // Simulate AI analysis results
    const photoCount = Object.values(uploadedPhotos).filter(p => p !== null).length;
    
    // Base score on number of photos
    const baseScore = 60 + (photoCount * 5);
    
    // Random variation for demo
    const variation = Math.floor(Math.random() * 15) - 7;
    const overallScore = Math.min(100, Math.max(50, baseScore + variation));
    
    return {
        overallScore,
        categories: {
            lighting: Math.floor(Math.random() * 20) + 75,
            spaceFlow: Math.floor(Math.random() * 20) + 70,
            colorHarmony: Math.floor(Math.random() * 20) + 65,
            furniture: Math.floor(Math.random() * 20) + 70,
            declutter: Math.floor(Math.random() * 20) + 60
        },
        recommendations: [
            'Consider adding more natural light sources',
            'Balance the five elements with appropriate colors',
            'Ensure clear pathways for qi energy flow',
            'Position furniture to face auspicious directions',
            'Add plants for wood element energy'
        ]
    };
}

function displayUploadResults(analysis) {
    const resultsSection = document.getElementById('uploadResults');
    resultsSection.style.display = 'block';
    
    // Overall score
    document.getElementById('uploadOverallScore').textContent = analysis.overallScore;
    
    const rating = getRating(analysis.overallScore);
    document.getElementById('uploadScoreRating').textContent = rating.text;
    document.getElementById('uploadScoreRating').style.color = rating.color;
    
    // Detailed results
    const resultsHTML = `
        <div class="result-item">
            <h4>Lighting & Natural Energy</h4>
            <div class="score-bar">
                <div class="score-fill" style="width: ${analysis.categories.lighting}%"></div>
                <span class="score-value">${analysis.categories.lighting}/100</span>
            </div>
        </div>
        
        <div class="result-item">
            <h4>Space Flow & Circulation</h4>
            <div class="score-bar">
                <div class="score-fill" style="width: ${analysis.categories.spaceFlow}%"></div>
                <span class="score-value">${analysis.categories.spaceFlow}/100</span>
            </div>
        </div>
        
        <div class="result-item">
            <h4>Color Harmony</h4>
            <div class="score-bar">
                <div class="score-fill" style="width: ${analysis.categories.colorHarmony}%"></div>
                <span class="score-value">${analysis.categories.colorHarmony}/100</span>
            </div>
        </div>
        
        <div class="result-item">
            <h4>Furniture Placement</h4>
            <div class="score-bar">
                <div class="score-fill" style="width: ${analysis.categories.furniture}%"></div>
                <span class="score-value">${analysis.categories.furniture}/100</span>
            </div>
        </div>
        
        <div class="result-item">
            <h4>Declutter & Organization</h4>
            <div class="score-bar">
                <div class="score-fill" style="width: ${analysis.categories.declutter}%"></div>
                <span class="score-value">${analysis.categories.declutter}/100</span>
            </div>
        </div>
    `;
    
    document.getElementById('uploadAnalysisResults').innerHTML = resultsHTML;
    
    // Recommendations
    const recsHTML = analysis.recommendations.map(rec => `
        <div class="recommendation-item">
            <span class="rec-icon">💡</span>
            <p>${rec}</p>
        </div>
    `).join('');
    
    document.getElementById('uploadRecommendations').innerHTML = recsHTML;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Indoor Analysis System Initialized');
});
