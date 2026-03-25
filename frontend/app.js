// Configuration
const API_BASE_URL = 'http://localhost:5000/api';
let currentPage = 0;
let chartsInitialized = {};
let allData = [];
let filteredData = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    showTab('dashboard');
    checkApiHealth();
    loadDashboardData();
});

// Tab Navigation
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active class from nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').style.display = 'block';
    
    // Add active class to clicked link
    event.target.closest('.nav-link').classList.add('active');
    
    // Load tab-specific data
    setTimeout(() => {
        if (tabName === 'dashboard') {
            loadDashboardData();
        } else if (tabName === 'data') {
            refreshData();
        } else if (tabName === 'analytics') {
            loadAnalytics();
        } else if (tabName === 'ml') {
            loadMLData();
        }
    }, 100);
}

// API Health Check
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        if (data.status === 'healthy') {
            document.getElementById('health-status').textContent = 'API Healthy';
            document.getElementById('health-status').className = 'badge bg-success';
        }
    } catch (error) {
        document.getElementById('health-status').textContent = 'API Offline';
        document.getElementById('health-status').className = 'badge bg-danger';
        showToast('API Connection Error', 'Unable to connect to backend API', 'error');
    }
}

// ==================== DASHBOARD ====================

async function loadDashboardData() {
    try {
        const response = await fetch(`${API_BASE_URL}/data/stats`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const stats = result.stats;
            
            // Update stats
            document.getElementById('total-records').textContent = stats.total_rows.toLocaleString();
            document.getElementById('total-sales').textContent = '$' + stats.numeric_stats.sales.mean.toFixed(2);
            document.getElementById('avg-sales').textContent = '$' + stats.numeric_stats.sales.mean.toFixed(2);
            document.getElementById('categories-count').textContent = stats.unique_categories.Category;
            
            // Load charts
            loadSalesTrendChart();
            loadCategoryChart();
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Error', 'Failed to load dashboard data', 'error');
    }
}

async function loadSalesTrendChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/sales-trends?period=year`);
        const result = await response.json();
        
        if (result.status === 'success' && result.trends) {
            const trends = result.trends.sum;
            
            if (chartsInitialized.yearChart) {
                chartsInitialized.yearChart.destroy();
            }
            
            const ctx = document.getElementById('yearChart').getContext('2d');
            chartsInitialized.yearChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(trends),
                    datasets: [{
                        label: 'Total Sales',
                        data: Object.values(trends),
                        backgroundColor: '#0d6efd',
                        borderRadius: 6,
                        borderSkipped: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            labels: {
                                usePointStyle: true,
                                padding: 15
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading sales trends:', error);
    }
}

async function loadCategoryChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/category-performance`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const data = result.category_performance;
            const categories = {};
            
            // Parse nested structure
            for (const [key, values] of Object.entries(data)) {
                const category = key[0];
                if (!categories[category]) {
                    categories[category] = 0;
                }
                categories[category] += values['Sales']['sum'];
            }
            
            if (chartsInitialized.categoryChart) {
                chartsInitialized.categoryChart.destroy();
            }
            
            const ctx = document.getElementById('categoryChart').getContext('2d');
            chartsInitialized.categoryChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(categories),
                    datasets: [{
                        data: Object.values(categories),
                        backgroundColor: ['#0d6efd', '#198754', '#ffc107'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                usePointStyle: true,
                                padding: 15
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading category chart:', error);
    }
}

// ==================== DATA TAB ====================

async function refreshData() {
    currentPage = 0;
    const limit = document.getElementById('limit-select').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/data/superstore?limit=${limit}&offset=0`);
        const result = await response.json();
        
        if (result.status === 'success') {
            allData = result.data;
            displayDataTable(allData);
            loadFilterOptions();
        }
    } catch (error) {
        console.error('Error loading data:', error);
        showToast('Error', 'Failed to load data', 'error');
    }
}

async function applyFilters() {
    const category = document.getElementById('filter-category').value;
    const region = document.getElementById('filter-region').value;
    const segment = document.getElementById('filter-segment').value;
    
    let params = new URLSearchParams();
    if (category) params.append('category', category);
    if (region) params.append('region', region);
    if (segment) params.append('segment', segment);
    
    try {
        const url = params.toString() ? `${API_BASE_URL}/data/superstore?${params}&limit=1000` : `${API_BASE_URL}/data/superstore?limit=1000`;
        const response = await fetch(url);
        const result = await response.json();
        
        if (result.status === 'success') {
            filteredData = result.data;
            currentPage = 0;
            displayDataTable(filteredData);
        }
    } catch (error) {
        console.error('Error applying filters:', error);
        showToast('Error', 'Failed to apply filters', 'error');
    }
}

function displayDataTable(data) {
    const tbody = document.getElementById('data-tbody');
    tbody.innerHTML = '';
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No data available</td></tr>';
        return;
    }
    
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row['Order_ID'] || '-'}</td>
            <td>${row['Customer_Name'] || '-'}</td>
            <td><span class="badge bg-primary">${row['Category'] || '-'}</span></td>
            <td>${row['Product_Name'] || '-'}</td>
            <td>${row['Region'] || '-'}</td>
            <td><strong>$${parseFloat(row['Sales']).toFixed(2)}</strong></td>
            <td>${row['Quantity'] || '-'}</td>
        `;
        tbody.appendChild(tr);
    });
    
    document.getElementById('page-info').textContent = `Page ${currentPage + 1}`;
}

async function loadFilterOptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/data/superstore?limit=1000`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const data = result.data;
            const categories = [...new Set(data.map(row => row['Category']))];
            const regions = [...new Set(data.map(row => row['Region']))];
            const segments = [...new Set(data.map(row => row['Segment']))];
            
            populateSelect('filter-category', categories);
            populateSelect('filter-region', regions);
            populateSelect('filter-segment', segments);
        }
    } catch (error) {
        console.error('Error loading filter options:', error);
    }
}

function populateSelect(selectId, options) {
    const select = document.getElementById(selectId);
    options.forEach(option => {
        const opt = document.createElement('option');
        opt.value = option;
        opt.textContent = option;
        select.appendChild(opt);
    });
}

function nextPage() {
    currentPage++;
    filteredData.length > 0 ? displayDataTable(filteredData) : displayDataTable(allData);
}

function previousPage() {
    if (currentPage > 0) {
        currentPage--;
        filteredData.length > 0 ? displayDataTable(filteredData) : displayDataTable(allData);
    }
}

// ==================== PIPELINE TAB ====================

async function runPipeline() {
    const spinner = document.getElementById('pipeline-spinner');
    const logsDiv = document.getElementById('pipeline-logs');
    
    spinner.style.display = 'flex';
    logsDiv.innerHTML = '<div class="log-entry log-info">Running full ETL pipeline...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/pipeline/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        spinner.style.display = 'none';
        
        if (data.status === 'success') {
            logsDiv.innerHTML += '<div class="log-entry log-success">✓ Pipeline executed successfully</div>';
            showToast('Success', 'Pipeline executed successfully', 'success');
        } else {
            logsDiv.innerHTML += '<div class="log-entry log-error">✗ ' + data.message + '</div>';
            showToast('Error', data.message, 'error');
        }
    } catch (error) {
        spinner.style.display = 'none';
        logsDiv.innerHTML += '<div class="log-entry log-error">✗ ' + error.message + '</div>';
        showToast('Error', 'Pipeline execution failed', 'error');
    }
}

async function runExtract() {
    addPipelineLog('Starting extraction...', 'info');
    try {
        const response = await fetch(`${API_BASE_URL}/pipeline/extract`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_path: '../data/raw/SuperstoreData.csv',
                encoding: 'ISO-8859-1'
            })
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            addPipelineLog(`Extracted ${data.rows} rows and ${data.columns} columns`, 'success');
        } else {
            addPipelineLog('Extraction failed: ' + data.message, 'error');
        }
    } catch (error) {
        addPipelineLog('Extraction error: ' + error.message, 'error');
    }
}

async function runTransform() {
    addPipelineLog('Starting transformation...', 'info');
    try {
        const response = await fetch(`${API_BASE_URL}/pipeline/transform`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_path: '../data/raw/SuperstoreData.csv',
                order_date_col: 'Order_Date',
                ship_date_col: 'Ship_Date',
                lowercase_categories: true,
                remove_duplicates: true
            })
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            addPipelineLog(`Transformed ${data.rows} rows, ${data.columns} columns`, 'success');
        } else {
            addPipelineLog('Transformation failed: ' + data.message, 'error');
        }
    } catch (error) {
        addPipelineLog('Transformation error: ' + error.message, 'error');
    }
}

async function runValidate() {
    addPipelineLog('Starting validation...', 'info');
    try {
        const response = await fetch(`${API_BASE_URL}/pipeline/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_path: '../data/processed/cleansuperstoredata.csv'
            })
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            addPipelineLog('✓ Data validation passed', 'success');
        } else {
            addPipelineLog('Validation failed: ' + data.message, 'error');
        }
    } catch (error) {
        addPipelineLog('Validation error: ' + error.message, 'error');
    }
}

function addPipelineLog(message, level = 'info') {
    const logsDiv = document.getElementById('pipeline-logs');
    const entry = document.createElement('div');
    entry.className = `log-entry log-${level}`;
    entry.textContent = '[' + new Date().toLocaleTimeString() + '] ' + message;
    logsDiv.appendChild(entry);
    logsDiv.scrollTop = logsDiv.scrollHeight;
}

// ==================== ANALYTICS TAB ====================

async function loadAnalytics() {
    loadSalesTrends();
    loadCategoryPerformance();
    loadRegionalPerformance();
}

async function loadSalesTrends() {
    const period = document.querySelector('input[name="period"]:checked').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/sales-trends?period=${period}`);
        const result = await response.json();
        
        if (result.status === 'success' && result.trends) {
            const trends = result.trends.sum;
            
            if (chartsInitialized.trendsChart) {
                chartsInitialized.trendsChart.destroy();
            }
            
            const ctx = document.getElementById('trendsChart').getContext('2d');
            chartsInitialized.trendsChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: Object.keys(trends),
                    datasets: [{
                        label: 'Total Sales',
                        data: Object.values(trends),
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointBackgroundColor: '#0d6efd'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            labels: { usePointStyle: true, padding: 15 }
                        }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading trends:', error);
    }
}

async function loadCategoryPerformance() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/category-performance`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const tbody = document.getElementById('category-tbody');
            tbody.innerHTML = '';
            
            const data = result.category_performance;
            const categories = {};
            
            for (const [key, values] of Object.entries(data)) {
                const category = key[0];
                if (!categories[category]) {
                    categories[category] = { sales: 0, count: 0 };
                }
                categories[category].sales += values['Sales']['sum'];
                categories[category].count += values['Sales']['count'];
            }
            
            for (const [cat, stats] of Object.entries(categories)) {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${cat}</strong></td>
                    <td>$${stats.sales.toFixed(2)}</td>
                    <td>${stats.count}</td>
                `;
                tbody.appendChild(tr);
            }
        }
    } catch (error) {
        console.error('Error loading category performance:', error);
    }
}

async function loadRegionalPerformance() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/regional-analysis`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const tbody = document.getElementById('region-tbody');
            tbody.innerHTML = '';
            
            const data = result.regional_performance;
            
            for (const [key, values] of Object.entries(data)) {
                const [region, segment] = key;
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${region}</strong></td>
                    <td>${segment}</td>
                    <td>$${values['Sales']['sum'].toFixed(2)}</td>
                `;
                tbody.appendChild(tr);
            }
        }
    } catch (error) {
        console.error('Error loading regional performance:', error);
    }
}

// ==================== ML TAB ====================

async function loadMLData() {
    loadModelInfo();
    loadModelMetrics();
}

async function loadModelInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/model/info`);
        const result = await response.json();
        
        const infoDiv = document.getElementById('model-info');
        
        if (result.status === 'success') {
            const info = result.model_info;
            infoDiv.innerHTML = `
                <p><strong>Model Type:</strong> Linear Regression</p>
                <p><strong>Training Status:</strong> <span class="badge bg-success">Trained</span></p>
                <p><strong>Features Used:</strong> ${info.feature_count}</p>
                <p><strong>Training Date:</strong> ${info.training_date || 'Not available'}</p>
            `;
        } else {
            infoDiv.innerHTML = '<p class="text-warning"><i class="fas fa-exclamation-triangle"></i> Model not trained yet</p>';
        }
    } catch (error) {
        console.error('Error loading model info:', error);
        document.getElementById('model-info').innerHTML = '<p class="text-danger">Error loading model info</p>';
    }
}

async function loadModelMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/model/metrics`);
        const result = await response.json();
        
        const metricsDiv = document.getElementById('model-metrics');
        
        if (result.status === 'success') {
            const metrics = result.metrics;
            metricsDiv.innerHTML = `
                <p><strong>Mean Absolute Error (MAE):</strong> $${metrics.mae || metrics.MAE}</p>
                <p><strong>Root Mean Squared Error (RMSE):</strong> $${metrics.rmse || metrics.RMSE}</p>
                <p><strong>R² Score:</strong> ${(metrics.r2_score || metrics.r2_score_value || 0).toFixed(4)}</p>
            `;
        } else {
            metricsDiv.innerHTML = '<p class="text-warning">Metrics not available</p>';
        }
    } catch (error) {
        console.error('Error loading metrics:', error);
    }
}

async function retrainModel() {
    showToast('Info', 'Retraining model...', 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/model/retrain`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                data_path: '../data/processed/cleansuperstoredata.csv'
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showToast('Success', 'Model retrained successfully', 'success');
            loadModelInfo();
            loadModelMetrics();
        } else {
            showToast('Error', result.message, 'error');
        }
    } catch (error) {
        showToast('Error', 'Model retraining failed', 'error');
    }
}

async function makePrediction() {
    const segment = document.getElementById('pred-segment').value;
    const region = document.getElementById('pred-region').value;
    const category = document.getElementById('pred-category').value;
    const quantity = parseFloat(document.getElementById('pred-quantity').value);
    const discount = parseFloat(document.getElementById('pred-discount').value);
    const profit = parseFloat(document.getElementById('pred-profit').value);
    
    if (!segment || !region || !category || !quantity || !discount || !profit) {
        showToast('Error', 'Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/sales`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'Segment': segment,
                'Region': region,
                'Category': category,
                'Quantity': quantity,
                'Discount': discount,
                'Profit': profit
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            const predictionDiv = document.getElementById('prediction-result');
            document.getElementById('predicted-value').textContent = '$' + result.predicted_sales.toFixed(2);
            predictionDiv.style.display = 'block';
            showToast('Success', 'Prediction completed', 'success');
        } else {
            showToast('Error', result.message, 'error');
        }
    } catch (error) {
        showToast('Error', 'Prediction failed', 'error');
        console.error('Prediction error:', error);
    }
}

// ==================== UTILITIES ====================

function showToast(title, message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    
    const toastHTML = `
        <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type} text-white">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    const toastDiv = document.createElement('div');
    toastDiv.innerHTML = toastHTML;
    toastContainer.appendChild(toastDiv);
    
    setTimeout(() => {
        toastDiv.remove();
    }, 5000);
}

// Check API health periodically
setInterval(checkApiHealth, 30000);
