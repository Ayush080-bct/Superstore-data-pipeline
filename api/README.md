# API Documentation

## Overview

This Flask-based REST API provides comprehensive access to the Superstore data pipeline, including ETL orchestration, data retrieval, analytics, and health monitoring.

## Getting Started

### Prerequisites

- Python 3.9+
- Flask
- pandas
- All dependencies listed in `../environment.yml`

### Installation

```bash
# Install Flask
pip install flask

# Or use conda
conda env create -f ../environment.yml
conda activate pipeline
```

### Running the API

```bash
# From the api directory
python main.py

# Or from project root
python -m flask --app api.main run
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health & Status

#### `GET /api/health`
Health check endpoint to verify API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-25T10:30:00.123456",
  "service": "Superstore Data Pipeline API"
}
```

---

## ETL Pipeline Endpoints

### Run Complete Pipeline

#### `POST /api/pipeline/run`
Executes the complete ETL pipeline (Extract → Transform → Validate → Load) sequentially.

**Request:**
```bash
curl -X POST http://localhost:5000/api/pipeline/run
```

**Response:**
```json
{
  "status": "success",
  "message": "Pipeline executed successfully",
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

### Extract Only

#### `POST /api/pipeline/extract`
Runs only the data extraction step.

**Request Body:**
```json
{
  "file_path": "../data/raw/SuperstoreData.csv",
  "encoding": "ISO-8859-1"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Data extracted successfully",
  "rows": 9994,
  "columns": 13,
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

### Validate Data

#### `POST /api/pipeline/validate`
Runs validation checks on processed data.

**Request Body:**
```json
{
  "file_path": "../data/processed/cleansuperstoredata.csv"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Data validation passed",
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

### Transform Data

#### `POST /api/pipeline/transform`
Runs only the transformation step on extracted data.

**Request Body:**
```json
{
  "file_path": "../data/raw/SuperstoreData.csv",
  "order_date_col": "Order_Date",
  "ship_date_col": "Ship_Date",
  "lowercase_categories": true,
  "remove_duplicates": true
}
```

**Parameters:**
- `file_path` (string, default: "../data/raw/SuperstoreData.csv") - Path to extracted data file
- `order_date_col` (string, default: "Order_Date") - Name of order date column
- `ship_date_col` (string, default: "Ship_Date") - Name of ship date column
- `lowercase_categories` (boolean, default: true) - Convert categorical values to lowercase
- `remove_duplicates` (boolean, default: true) - Remove duplicate rows from data

**Response:**
```json
{
  "status": "success",
  "message": "Data transformation completed successfully",
  "rows": 9994,
  "columns": 23,
  "new_columns_added": ["Order_Year", "Order_Month", "Order_Weekday", "Ship_Year", "Ship_Month", "Ship_Weekday"],
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

### Load Data

#### `POST /api/pipeline/load`
Runs only the loading step on transformed data.

**Request Body:**
```json
{
  "file_path": "../data/processed/cleansuperstoredata.csv",
  "output_path": "../data/processed/cleansuperstoredata.csv"
}
```

**Parameters:**
- `file_path` (string, default: "../data/processed/cleansuperstoredata.csv") - Path to transformed data file to load
- `output_path` (string, default: "../data/processed/cleansuperstoredata.csv") - Path where output CSV will be saved

**Response:**
```json
{
  "status": "success",
  "message": "Data loading completed successfully",
  "rows_loaded": 9994,
  "output_path": "../data/processed/cleansuperstoredata.csv",
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

---

## Data Access Endpoints

### Get Superstore Data

#### `GET /api/data/superstore`
Retrieve processed Superstore sales data with pagination and filtering.

**Query Parameters:**
- `limit` (int, default: 100) - Number of rows to return
- `offset` (int, default: 0) - Starting position for pagination
- `category` (string, optional) - Filter by category (e.g., "Furniture", "Office Supplies")
- `region` (string, optional) - Filter by region (e.g., "West", "East", "South", "Central")
- `segment` (string, optional) - Filter by segment (e.g., "Consumer", "Corporate", "Home Office")

**Example Request:**
```bash
curl "http://localhost:5000/api/data/superstore?limit=50&offset=0&category=Furniture&region=West"
```

**Response:**
```json
{
  "status": "success",
  "total_rows": 1500,
  "returned_rows": 50,
  "offset": 0,
  "limit": 50,
  "data": [
    {
      "Row_ID": 1,
      "Order_ID": "ca-2017-152156",
      "Order_Date": "2017-08-11",
      "Sales": 261.96,
      "Category": "furniture",
      "Region": "west",
      ...
    },
    ...
  ],
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

### Get Dataset Statistics

#### `GET /api/data/stats`
Get comprehensive statistics about the processed dataset.

**Request:**
```bash
curl http://localhost:5000/api/data/stats
```

**Response:**
```json
{
  "status": "success",
  "stats": {
    "total_rows": 9994,
    "total_columns": 23,
    "columns": ["Row_ID", "Order_ID", "Order_Date", "Sales", ...],
    "data_types": {
      "Row_ID": "int64",
      "Sales": "float64",
      "Order_Date": "object",
      ...
    },
    "missing_values": {
      "Row_ID": 0,
      "Sales": 0,
      "Ship_Date": 1342,
      ...
    },
    "numeric_stats": {
      "sales": {
        "min": 0.444,
        "max": 22638.48,
        "mean": 229.86,
        "median": 54.06
      }
    },
    "unique_categories": {
      "Category": 3,
      "Region": 4,
      "Segment": 3
    }
  },
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

---

## Analytics Endpoints

### Sales Trends

#### `GET /api/analytics/sales-trends`
Analyze sales trends over time periods.

**Query Parameters:**
- `period` (string, default: "year") - Time period for grouping: "year" or "month"

**Example Request:**
```bash
curl "http://localhost:5000/api/analytics/sales-trends?period=year"
```

**Response:**
```json
{
  "status": "success",
  "period": "year",
  "trends": {
    "sum": {
      "2015": 484247.13,
      "2016": 733215.66,
      "2017": 633145.22,
      "2018": 1062093.88
    },
    "mean": {
      "2015": 234.15,
      "2016": 289.45,
      "2017": 267.89,
      "2018": 301.34
    },
    "count": {
      "2015": 2067,
      "2016": 2535,
      "2017": 2354,
      "2018": 3038
    }
  },
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

### Category Performance

#### `GET /api/analytics/category-performance`
Get sales performance metrics by category and sub-category.

**Example Request:**
```bash
curl http://localhost:5000/api/analytics/category-performance
```

**Response:**
```json
{
  "status": "success",
  "category_performance": {
    "Furniture": {
      "Bookcases": {
        "Sales": {
          "sum": 232145.23,
          "mean": 156.34,
          "count": 1485
        }
      },
      "Chairs": {
        "Sales": {
          "sum": 328756.45,
          "mean": 278.91,
          "count": 1178
        }
      }
    }
  },
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

### Regional Analysis

#### `GET /api/analytics/regional-analysis`
Analyze sales performance by region and customer segment.

**Example Request:**
```bash
curl http://localhost:5000/api/analytics/regional-analysis
```

**Response:**
```json
{
  "status": "success",
  "regional_performance": {
    "East": {
      "Consumer": {
        "Sales": {
          "sum": 156234.45,
          "mean": 189.43,
          "count": 824
        }
      },
      "Corporate": {
        "Sales": {
          "sum": 234156.78,
          "mean": 267.89,
          "count": 873
        }
      }
    }
  },
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

---

## Error Handling

All endpoints return consistent error responses with HTTP status codes.

### Error Response Format

```json
{
  "status": "error",
  "message": "Description of what went wrong",
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid query parameters or request format
- `404 Not Found` - Endpoint does not exist
- `500 Internal Server Error` - Server error during processing

---

---

## ML Model Endpoints

### Get Model Information

#### `GET /api/model/info`
Get detailed information about the trained ML model, including features used and model parameters.

**Request:**
```bash
curl http://localhost:5000/api/model/info
```

**Response:**
```json
{
  "status": "success",
  "model_info": {
    "model_type": "LinearRegression",
    "training_date": "2026-03-25T10:30:00.123456",
    "num_features": 25,
    "feature_names": [
      "Quantity", "Discount", "Profit", "Segment_Corporate", 
      "Segment_Home Office", "Region_Central", "Region_East", 
      "Region_West", "Category_Office Supplies", "Category_Technology",
      ...
    ],
    "metrics": {
      "mae": 234.56,
      "rmse": 456.78,
      "r2_score": 0.7234,
      "test_samples": 2000,
      "train_samples": 7994
    }
  },
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

### Get Model Metrics

#### `GET /api/model/metrics`
Get model performance metrics without full model details.

**Request:**
```bash
curl http://localhost:5000/api/model/metrics
```

**Response:**
```json
{
  "status": "success",
  "metrics": {
    "mae": 234.56,
    "rmse": 456.78,
    "r2_score": 0.7234,
    "test_samples": 2000,
    "train_samples": 7994
  },
  "training_date": "2026-03-25T10:30:00.123456",
  "model_type": "LinearRegression",
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

### Retrain Model

#### `POST /api/model/retrain`
Retrain the ML model with latest data.

**Request Body:**
```json
{
  "data_path": "../data/processed/cleansuperstoredata.csv"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Model trained successfully",
  "metrics": {
    "mae": 234.56,
    "rmse": 456.78,
    "r2_score": 0.7234,
    "test_samples": 2000,
    "train_samples": 7994
  },
  "feature_count": 25,
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

### Make Sales Prediction

#### `POST /api/predict/sales`
Make a sales prediction for one or multiple records using the trained Linear Regression model.

**Single Prediction Request:**
```bash
curl -X POST http://localhost:5000/api/predict/sales \
  -H "Content-Type: application/json" \
  -d '{
    "Segment": "Consumer",
    "Region": "West",
    "Category": "Furniture",
    "Sub_Category": "Chairs",
    "Quantity": 2,
    "Discount": 0.1,
    "Profit": 50.5
  }'
```

**Single Prediction Response:**
```json
{
  "status": "success",
  "predicted_sales": 450.75,
  "input_features": {
    "Segment": "Consumer",
    "Region": "West",
    "Category": "Furniture",
    "Sub_Category": "Chairs",
    "Quantity": 2,
    "Discount": 0.1,
    "Profit": 50.5
  },
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

**Batch Predictions Request:**
```bash
curl -X POST http://localhost:5000/api/predict/sales \
  -H "Content-Type: application/json" \
  -d '{
    "predictions": [
      {
        "Segment": "Consumer",
        "Region": "West",
        "Category": "Furniture",
        "Quantity": 2,
        "Discount": 0.1,
        "Profit": 50.5
      },
      {
        "Segment": "Corporate",
        "Region": "East",
        "Category": "Technology",
        "Quantity": 5,
        "Discount": 0.0,
        "Profit": 150.0
      }
    ]
  }'
```

**Batch Predictions Response:**
```json
{
  "status": "success",
  "predictions": [450.75, 892.34],
  "count": 2,
  "timestamp": "2026-03-25T10:30:00.123456"
}
```

**Supported Features for Prediction:**
The model accepts any combination of the following features:
- `Quantity` (numeric)
- `Discount` (numeric, 0-1 range)
- `Profit` (numeric)
- `Postal_Code` (numeric)
- `Segment` (categorical: "Consumer", "Corporate", "Home Office")
- `Region` (categorical: "Central", "East", "South", "West")
- `Category` (categorical: "Furniture", "Office Supplies", "Technology")
- `Sub_Category` (categorical: "Chairs", "Desks", "Tables", etc.)
- `Ship_Mode` (categorical: "First Class", "Second Class", "Standard Class", "Same Day")

---

### Scenario 1: Full ETL Pipeline Execution
```bash
# Trigger a complete pipeline run
curl -X POST http://localhost:5000/api/pipeline/run

# Check dataset stats after pipeline
curl http://localhost:5000/api/data/stats
```

### Scenario 2: Data Analysis
```bash
# Get Furniture sales from West region
curl "http://localhost:5000/api/data/superstore?category=Furniture&region=West&limit=100"

# Analyze category performance
curl http://localhost:5000/api/analytics/category-performance

# Check regional sales trends
curl http://localhost:5000/api/analytics/regional-analysis
```

### Scenario 3: Pipeline Monitoring
```bash
# Health check
curl http://localhost:5000/api/health

# Extract and validate separately
curl -X POST http://localhost:5000/api/pipeline/extract \
  -H "Content-Type: application/json" \
  -d '{"file_path": "../data/raw/SuperstoreData.csv"}'

curl -X POST http://localhost:5000/api/pipeline/validate \
  -H "Content-Type: application/json" \
  -d '{"file_path": "../data/processed/cleansuperstoredata.csv"}'
```

### Scenario 4: Step-by-Step ETL Processing
```bash
# 1. Extract data
curl -X POST http://localhost:5000/api/pipeline/extract \
  -H "Content-Type: application/json" \
  -d '{"file_path": "../data/raw/SuperstoreData.csv", "encoding": "ISO-8859-1"}'

# 2. Transform with custom parameters
curl -X POST http://localhost:5000/api/pipeline/transform \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "../data/raw/SuperstoreData.csv",
    "lowercase_categories": true,
    "remove_duplicates": true
  }'

# 3. Validate transformed data
curl -X POST http://localhost:5000/api/pipeline/validate \
  -H "Content-Type: application/json" \
  -d '{"file_path": "../data/processed/cleansuperstoredata.csv"}'

# 4. Load to custom output path
curl -X POST http://localhost:5000/api/pipeline/load \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "../data/processed/cleansuperstoredata.csv",
    "output_path": "../data/processed/cleansuperstoredata_backup.csv"
  }'
```

### Scenario 5: ML Model Training and Predictions
```bash
# 1. Retrain model with latest data
curl -X POST http://localhost:5000/api/model/retrain \
  -H "Content-Type: application/json" \
  -d '{"data_path": "../data/processed/cleansuperstoredata.csv"}'

# 2. Check model performance metrics
curl http://localhost:5000/api/model/metrics

# 3. Get detailed model information
curl http://localhost:5000/api/model/info

# 4. Make a single prediction
curl -X POST http://localhost:5000/api/predict/sales \
  -H "Content-Type: application/json" \
  -d '{
    "Segment": "Consumer",
    "Region": "West",
    "Category": "Furniture",
    "Sub_Category": "Chairs",
    "Quantity": 3,
    "Discount": 0.15,
    "Profit": 75.25
  }'

# 5. Make batch predictions
curl -X POST http://localhost:5000/api/predict/sales \
  -H "Content-Type: application/json" \
  -d '{
    "predictions": [
      {"Segment": "Consumer", "Region": "West", "Category": "Furniture", "Quantity": 1, "Discount": 0.05, "Profit": 50},
      {"Segment": "Corporate", "Region": "East", "Category": "Technology", "Quantity": 2, "Discount": 0.1, "Profit": 100},
      {"Segment": "Home Office", "Region": "South", "Category": "Office Supplies", "Quantity": 5, "Discount": 0.0, "Profit": 25}
    ]
  }'
```

---

## Configuration

### Environment Variables

Create a `.env` file in the api directory for local configuration:

```bash
FLASK_ENV=development
FLASK_DEBUG=1
API_PORT=5000
DATA_PATH=../data
```

### Logging

All API operations are logged to console with timestamps and severity levels. Check server output for detailed operation logs.

---

## Future Enhancements

- [x] ML model prediction endpoints
- [ ] eBay scraping API integration
- [ ] Authentication/Authorization
- [ ] Request rate limiting
- [ ] Database integration (PostgreSQL)
- [ ] WebSocket support for real-time updates
- [ ] Comprehensive API documentation (Swagger/OpenAPI)
- [ ] Model versioning and comparison
- [ ] Advanced feature engineering endpoints

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Change port in main.py
app.run(port=5001)
```

### Module Import Errors
```bash
# Ensure you're in the correct environment
conda activate pipeline

# Reinstall dependencies
pip install -r requirements.txt
```

### Data File Not Found
- Verify file paths are relative to project root
- Check data files exist in `data/raw/` and `data/processed/`

---

## Support

For issues or questions, refer to the main project [README.md](../README.md)
