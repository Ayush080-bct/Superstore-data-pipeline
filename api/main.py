from flask import Flask, request, jsonify
import sys
from flask_cors import CORS
from pathlib import Path
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import os
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent

from etl.extractors import extract_data
from etl.transform import transform
from etl.validate import validate_data
from etl.load import load_data
from etl.pipeline import run_pipeline
from ml.model import get_predictor

app = Flask(__name__)
CORS(app)
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========================
# HEALTH CHECK ENDPOINTS
# ========================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Superstore Data Pipeline API'
    }), 200


# ========================
# ETL PIPELINE ENDPOINTS
# ========================

@app.route('/api/pipeline/run', methods=['POST'])
def run_etl_pipeline():
    """
    Trigger the complete ETL pipeline (extract → transform → validate → load)
    """
    try:
        logger.info("Starting complete ETL pipeline")
        run_pipeline()
        return jsonify({
            'status': 'success',
            'message': 'Pipeline executed successfully',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Pipeline failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/pipeline/extract', methods=['POST'])
def extract_only():
    """
    Run only the extraction step
    """
    try:
        file_path = request.json.get('file_path', None) if request.json else None
        
        # Use default if not provided
        if not file_path:
            file_path = str(PROJECT_ROOT / 'data' / 'raw' / 'SuperstoreData.csv')
        elif not file_path.startswith('/'):
            # If relative path provided, make it absolute
            file_path = str(PROJECT_ROOT / file_path)
        
        encoding = (request.json.get('encoding', 'ISO-8859-1') if request.json else 'ISO-8859-1')
        
        logger.info(f"Extracting data from {file_path}")
        df = extract_data(file_path, encoded_system=encoding)
        
        return jsonify({
            'status': 'success',
            'message': 'Data extracted successfully',
            'rows': len(df),
            'columns': len(df.columns),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Extraction failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/pipeline/validate', methods=['POST'])
def validate_only():
    """
    Run only the validation step on processed data
    """
    try:
        file_path = request.json.get('file_path', None) if request.json else None
        
        # Use default if not provided
        if not file_path:
            file_path = str(PROJECT_ROOT / 'data' / 'processed' / 'cleansuperstoredata.csv')
        elif not file_path.startswith('/'):
            # If relative path provided, make it absolute
            file_path = str(PROJECT_ROOT / file_path)
        
        logger.info(f"Validating data from {file_path}")
        df = pd.read_csv(file_path)
        validate_data(df)
        
        return jsonify({
            'status': 'success',
            'message': 'Data validation passed',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Validation failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/pipeline/transform', methods=['POST'])
def transform_only():
    """
    Run only the transformation step on extracted data
    Accepts optional parameters:
    - file_path: path to extracted data file
    - order_date_col: name of order date column (default: 'Order_Date')
    - ship_date_col: name of ship date column (default: 'Ship_Date')
    - lowercase_categories: convert categories to lowercase (default: true)
    - remove_duplicates: remove duplicate rows (default: true)
    """
    try:
        request_data = request.json or {}
        file_path = request_data.get('file_path', None)
        
        # Use default if not provided
        if not file_path:
            file_path = str(PROJECT_ROOT / 'data' / 'raw' / 'SuperstoreData.csv')
        elif not file_path.startswith('/'):
            # If relative path provided, make it absolute
            file_path = str(PROJECT_ROOT / file_path)
        
        order_date_col = request_data.get('order_date_col', 'Order_Date')
        ship_date_col = request_data.get('ship_date_col', 'Ship_Date')
        lowercase_categories = request_data.get('lowercase_categories', True)
        remove_duplicates = request_data.get('remove_duplicates', True)
        # Same default as /api/pipeline/extract — the source CSV is not UTF-8.
        encoding = request_data.get('encoding', 'ISO-8859-1')
        
        logger.info(f"Transforming data from {file_path}")
        df = pd.read_csv(file_path, encoding=encoding)
        
        df_transformed = transform(
            df,
            order_date_col=order_date_col,
            ship_date_col=ship_date_col,
            lowercase_categories=lowercase_categories,
            remove_duplicates=remove_duplicates
        )

        # Persist so /api/model/retrain (and auto-train) actually see the new
        # columns (e.g. Shipping_Days) instead of silently training on the
        # previous, stale file — this step was a no-op before this fix.
        output_path = PROJECT_ROOT / 'data' / 'processed' / 'cleansuperstoredata.csv'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_transformed.to_csv(output_path, index=False)
        logger.info(f"Saved transformed data to {output_path}")
        
        return jsonify({
            'status': 'success',
            'message': 'Data transformation completed successfully',
            'rows': len(df_transformed),
            'columns': len(df_transformed.columns),
            'new_columns_added': ['Order_Year', 'Order_Month', 'Order_Weekday', 
                                 'Ship_Year', 'Ship_Month', 'Ship_Weekday', 'Shipping_Days'],
            'saved_to': str(output_path),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Transformation failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Transformation failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/pipeline/load', methods=['POST'])
def load_only():
    """
    Run only the loading step on transformed data
    Accepts optional parameters:
    - file_path: path to transformed data file (default: processed data)
    - output_path: path for output CSV file (default: 'data/processed/cleansuperstoredata.csv')
    """
    try:
        request_data = request.json or {}
        input_file_path = request_data.get('file_path', None)
        output_file_path = request_data.get('output_path', None)
        
        # Use defaults if not provided
        if not input_file_path:
            input_file_path = str(PROJECT_ROOT / 'data' / 'processed' / 'cleansuperstoredata.csv')
        elif not input_file_path.startswith('/'):
            input_file_path = str(PROJECT_ROOT / input_file_path)
        
        if not output_file_path:
            output_file_path = str(PROJECT_ROOT / 'data' / 'processed' / 'cleansuperstoredata.csv')
        elif not output_file_path.startswith('/'):
            output_file_path = str(PROJECT_ROOT / output_file_path)
        
        logger.info(f"Loading data from {input_file_path} to {output_file_path}")
        df = pd.read_csv(input_file_path)
        
        # If output path is different, save to that location
        if output_file_path != input_file_path:
            output_dir = Path(output_file_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_file_path, index=False)
            logger.info(f"Data saved to {output_file_path}")
        else:
            # Use the default load_data function
            load_data(df)
        
        return jsonify({
            'status': 'success',
            'message': 'Data loading completed successfully',
            'rows_loaded': len(df),
            'output_path': output_file_path,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Load failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Load failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


# ========================
# DATA ACCESS ENDPOINTS
# ========================

@app.route('/api/data/superstore', methods=['GET'])
def get_superstore_data():
    """
    Retrieve processed Superstore sales data with pagination and filtering
    Query params: limit, offset, category, region, segment
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        category = request.args.get('category', None)
        region = request.args.get('region', None)
        segment = request.args.get('segment', None)
        
        file_path = str(PROJECT_ROOT / 'data' / 'processed' / 'cleansuperstoredata.csv')
        df = pd.read_csv(file_path)
        
        # Apply filters
        if category:
            df = df[df['Category'].str.lower() == category.lower()]
        if region:
            df = df[df['Region'].str.lower() == region.lower()]
        if segment:
            df = df[df['Segment'].str.lower() == segment.lower()]
        
        # Pagination
        total_rows = len(df)
        df_paginated = df.iloc[offset:offset+limit]
        
        return jsonify({
            'status': 'success',
            'total_rows': total_rows,
            'returned_rows': len(df_paginated),
            'offset': offset,
            'limit': limit,
            'data': df_paginated.to_dict(orient='records'),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Data retrieval failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Data retrieval failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/data/stats', methods=['GET'])
def get_data_stats():
    """
    Get basic statistics about the processed dataset
    """
    try:
        file_path = str(PROJECT_ROOT / 'data' / 'processed' / 'cleansuperstoredata.csv')
        df = pd.read_csv(file_path)
        
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': df.columns.tolist(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isna().sum().to_dict(),
            'numeric_stats': {
                'sales': {
                    'min': float(df['Sales'].min()),
                    'max': float(df['Sales'].max()),
                    'mean': float(df['Sales'].mean()),
                    'median': float(df['Sales'].median())
                }
            },
            'unique_categories': {
                'Category': df['Category'].nunique(),
                'Region': df['Region'].nunique(),
                'Segment': df['Segment'].nunique()
            }
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Stats retrieval failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


# ========================
# ANALYTICS ENDPOINTS
# ========================

@app.route('/api/analytics/sales-trends', methods=['GET'])
def sales_trends():
    """
    Get sales trends by time period (year/month)
    Query params: period (year, month)
    """
    try:
        period = request.args.get('period', 'year')
        file_path = str(PROJECT_ROOT / 'data' / 'processed' / 'cleansuperstoredata.csv')
        df = pd.read_csv(file_path)
        
        if period == 'month':
            trends = df.groupby('Order_Month')['Sales'].agg(['sum', 'mean', 'count']).to_dict()
        else:
            trends = df.groupby('Order_Year')['Sales'].agg(['sum', 'mean', 'count']).to_dict()
        
        return jsonify({
            'status': 'success',
            'period': period,
            'trends': {k: v for k, v in trends.items()},
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Trends analysis failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Trends analysis failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/analytics/category-performance', methods=['GET'])
def category_performance():
    """
    Sales performance by category and sub-category
    """
    try:
        file_path = str(PROJECT_ROOT / 'data' / 'processed' / 'cleansuperstoredata.csv')
        df = pd.read_csv(file_path)
        
        category_stats = df.groupby(['Category', 'Sub_Category']).agg({
            'Sales': ['sum', 'mean', 'count']
        }).round(2)
        
        # Convert to JSON-serializable format (avoid NaN issues)
        category_dict = {}
        for (category, sub_cat), row in category_stats.iterrows():
            key = f"{category}|{sub_cat}"
            category_dict[key] = {
                'sales_sum': float(row[('Sales', 'sum')]) if pd.notna(row[('Sales', 'sum')]) else 0,
                'sales_mean': float(row[('Sales', 'mean')]) if pd.notna(row[('Sales', 'mean')]) else 0,
                'count': int(row[('Sales', 'count')]) if pd.notna(row[('Sales', 'count')]) else 0
            }
        
        return jsonify({
            'status': 'success',
            'category_performance': category_dict,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Category analysis failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Category analysis failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/analytics/regional-analysis', methods=['GET'])
def regional_analysis():
    """
    Sales analysis by region and segment
    """
    try:
        file_path = str(PROJECT_ROOT / 'data' / 'processed' / 'cleansuperstoredata.csv')
        df = pd.read_csv(file_path)
        
        regional_stats = df.groupby(['Region', 'Segment']).agg({
            'Sales': ['sum', 'mean', 'count']
        }).round(2)
        
        # Convert to JSON-serializable format (avoid NaN issues)
        regional_dict = {}
        for (region, segment), row in regional_stats.iterrows():
            key = f"{region}|{segment}"
            regional_dict[key] = {
                'sales_sum': float(row[('Sales', 'sum')]) if pd.notna(row[('Sales', 'sum')]) else 0,
                'sales_mean': float(row[('Sales', 'mean')]) if pd.notna(row[('Sales', 'mean')]) else 0,
                'count': int(row[('Sales', 'count')]) if pd.notna(row[('Sales', 'count')]) else 0
            }
        
        return jsonify({
            'status': 'success',
            'regional_performance': regional_dict,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Regional analysis failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Regional analysis failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


# ========================
# ML MODEL ENDPOINTS
# ========================

@app.route('/api/model/info', methods=['GET'])
def get_model_info():
    """
    Get detailed information about the trained ML model
    """
    try:
        predictor = get_predictor()
        
        if not predictor.is_model_trained():
            return jsonify({
                'status': 'warning',
                'message': 'Model not trained yet. Please train the model first.',
                'timestamp': datetime.now().isoformat()
            }), 202
        
        info = predictor.get_model_info()
        return jsonify({
            'status': 'success',
            'model_info': info,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Model info retrieval failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Model info retrieval failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/model/metrics', methods=['GET'])
def get_model_metrics():
    """
    Get model performance metrics (MAE, RMSE, R² score)
    """
    try:
        predictor = get_predictor()
        
        if not predictor.is_model_trained():
            return jsonify({
                'status': 'warning',
                'message': 'Model not trained yet',
                'timestamp': datetime.now().isoformat()
            }), 202
        
        metrics = predictor.get_metrics()
        return jsonify({
            'status': 'success',
            'metrics': metrics['metrics'],
            'training_date': metrics['training_date'],
            'model_type': metrics['model_type'],
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Metrics retrieval failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/model/retrain', methods=['POST'])
def retrain_model():
    """
    Retrain the ML model with latest data
    
    Request body:
    {
      "data_path": "data/processed/cleansuperstoredata.csv"
    }
    """
    try:
        request_data = request.json or {}
        data_path = request_data.get('data_path', None)
        if not data_path:
            data_path = str(PROJECT_ROOT / 'data' / 'processed' / 'cleansuperstoredata.csv')
        elif not data_path.startswith('/'):
            data_path = str(PROJECT_ROOT / data_path)
        
        logger.info(f"Retraining model with data from {data_path}")
        predictor = get_predictor()
        result = predictor.train_model(data_path)
        
        return jsonify({
            'status': 'success',
            'message': result['message'],
            'metrics': result['metrics'],
            'feature_count': result['feature_count'],
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Model retraining failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Model retraining failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/predict/sales', methods=['POST'])
def predict_sales():
    """
    Make a sales prediction using the trained ML model
    
    Request body:
    {
      "Segment": "Consumer",
      "Region": "West",
      "Category": "Furniture",
      "Sub_Category": "Chairs",
      "Quantity": 2,
      "Discount": 0.1,
      "Profit": 50.5
    }
    
    Or provide a list of predictions:
    {
      "predictions": [
        {"Segment": "Consumer", ...},
        {"Segment": "Corporate", ...}
      ]
    }
    """
    try:
        request_data = request.json
        
        if not request_data:
            return jsonify({
                'status': 'error',
                'message': 'Request body is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        predictor = get_predictor()
        
        if not predictor.is_model_trained():
            return jsonify({
                'status': 'error',
                'message': 'Model not trained yet. Please retrain the model first.',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        # Handle batch predictions
        if 'predictions' in request_data:
            predictions_list = request_data['predictions']
            predictions = predictor.predict_batch(predictions_list)
            
            return jsonify({
                'status': 'success',
                'predictions': predictions,
                'count': len(predictions),
                'timestamp': datetime.now().isoformat()
            }), 200
        
        # Single prediction
        else:
            prediction = predictor.predict(request_data)
            
            return jsonify({
                'status': 'success',
                'predicted_sales': round(prediction, 2),
                'input_features': request_data,
                'timestamp': datetime.now().isoformat()
            }), 200
            
    except ValueError as e:
        logger.error(f"Prediction validation failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Prediction failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 400
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Prediction failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


# ========================
# ERROR HANDLERS
# ========================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500


# ========================
# MAIN
# ========================

if __name__ == '__main__':
    logger.info("Starting Flask API server")
    app.run(debug=True, host='0.0.0.0', port=5000)