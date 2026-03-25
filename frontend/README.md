# Superstore Data Pipeline - Frontend

A responsive web dashboard for managing and visualizing the Superstore data pipeline, ETL processes, analytics, and machine learning models.

## Features

### 1. **Dashboard**
- Real-time data statistics (total records, total sales, average sales)
- Sales trends visualization by year
- Category performance breakdown
- Quick overview of key metrics

### 2. **Data Management**
- Browse processed Superstore data with pagination
- Filter by Category, Region, and Segment
- View detailed product and customer information
- Adjustable rows per page (10, 25, 50, 100)

### 3. **ETL Pipeline Control**
- Run complete ETL pipeline (Extract → Transform → Validate → Load)
- Execute individual pipeline steps
- Real-time pipeline logging and status monitoring
- Step-by-step process tracking

### 4. **Analytics & Insights**
- Sales trends visualization (by year or month)
- Category performance analysis
- Regional and segment performance comparison
- Aggregated statistics and KPIs

### 5. **Machine Learning**
- View trained model information
- Display model performance metrics (MAE, RMSE, R² Score)
- Retrain model with latest data
- Make sales predictions with custom parameters

## Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Backend Flask API running on `http://localhost:5000`
- Python environment with required dependencies installed

### Installation

1. **Ensure the backend API is running:**
```bash
cd /home/ayush_dada/Superstore-data-pipeline
conda activate pipeline
python api/main.py
```

2. **Open the frontend:**
```bash
# Simply open index.html in your browser
# Option 1: Direct file access
file:///home/ayush_dada/Superstore-data-pipeline/frontend/index.html

# Option 2: Using Python's built-in server
cd /home/ayush_dada/Superstore-data-pipeline/frontend
python -m http.server 8000
# Then visit: http://localhost:8000
```

### Project Structure

```
frontend/
├── index.html       # Main HTML file with dashboard layout
├── styles.css       # Responsive styling
├── app.js          # JavaScript logic and API integration
└── README.md       # This file
```

## Usage Guide

### Dashboard Tab
1. Click **Dashboard** in the sidebar
2. View key statistics about your data
3. Charts update automatically on load

### Data Tab
1. Click **Data** in the sidebar
2. Use filters to search by Category, Region, or Segment
3. Adjust rows per page using the dropdown
4. Navigate pages using Previous/Next buttons

### Pipeline Tab
1. Click **Pipeline** in the sidebar
2. **Full Pipeline**: Executes complete ETL process
3. **Individual Steps**: Run Extract, Transform, or Validate separately
4. View real-time logs for each operation

### Analytics Tab
1. Click **Analytics** in the sidebar
2. Select time period for sales trends (Year/Month)
3. View category performance metrics
4. Analyze regional and segment performance

### ML Model Tab
1. Click **ML Model** in the sidebar
2. View current model information and metrics
3. **Retrain Model**: Update model with latest processed data
4. **Make Predictions**: 
   - Select Segment, Region, Category
   - Enter Quantity, Discount, and Profit
   - Click "Predict Sales" to see the predicted value

## API Endpoints Used

The frontend communicates with the following API endpoints:

### Health & Status
- `GET /api/health` - Check API status

### Data
- `GET /api/data/superstore` - Get processed data with filters
- `GET /api/data/stats` - Get dataset statistics

### Analytics
- `GET /api/analytics/sales-trends` - Sales trend analysis
- `GET /api/analytics/category-performance` - Category metrics
- `GET /api/analytics/regional-analysis` - Regional metrics

### Pipeline
- `POST /api/pipeline/run` - Execute full ETL pipeline
- `POST /api/pipeline/extract` - Run extraction step
- `POST /api/pipeline/transform` - Run transformation step
- `POST /api/pipeline/validate` - Run validation step

### ML Model
- `GET /api/model/info` - Model information
- `GET /api/model/metrics` - Model performance metrics
- `POST /api/model/retrain` - Retrain the model
- `POST /api/predict/sales` - Make sales prediction

## Technologies Used

- **Frontend Framework**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5.3
- **Icons**: Font Awesome 6.4
- **Charts**: Chart.js 3.9.1
- **API Communication**: Fetch API

## Troubleshooting

### "API Offline" Status
- Ensure the Flask backend is running: `python api/main.py`
- Check the backend is accessible at `http://localhost:5000`
- Verify no firewall is blocking the connection

### No Data Showing
- Run the ETL pipeline first (Pipeline → Run Full Pipeline)
- Ensure processed data exists in `data/processed/cleansuperstoredata.csv`
- Check browser console for error messages (F12)

### Charts Not Displaying
- Verify Chart.js library is loaded (check browser console)
- Ensure data is available in the backend
- Try refreshing the page

### Filter Issues
- Make sure you've loaded data first (Data → Refresh)
- Check that filter values match actual data values
- Clear filters and reload data if needed

## Customization

### Change API URL
Edit `app.js` line 3:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### Modify Chart Colors
Edit `styles.css` `:root` section:
```css
--primary: #0d6efd;
--success: #198754;
```

### Add New Features
- UI components are in `index.html`
- Styling is in `styles.css`
- API calls are in `app.js`
- Follow existing patterns for consistency

## College Project Notes

This is a college project dashboard designed for:
- Portfolio demonstration
- Learning web development
- Understanding ETL pipelines
- Practicing data visualization
- Exploring machine learning integration

**Not intended for production use.**

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers supported with responsive design

## License

This is a college project for educational purposes.

## Support

For issues or questions, check:
1. Browser console (F12)
2. Backend logs (terminal where Flask is running)
3. Ensure all dependencies are installed
4. Verify API endpoints are working using tools like Postman
