"""
ML Model Management Module
Handles model training, prediction, serialization, and metrics
"""

import os
import sys
import pickle
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, List, Any

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model paths
MODEL_DIR = Path(__file__).parent / 'models'
MODEL_PATH = MODEL_DIR / 'sales_model.pkl'
SCALER_PATH = MODEL_DIR / 'scaler.pkl'
FEATURES_PATH = MODEL_DIR / 'features.pkl'
METADATA_PATH = MODEL_DIR / 'metadata.json'
DEFAULT_TRAINING_DATA_PATH = Path(__file__).parent.parent / 'data' / 'processed' / 'cleansuperstoredata.csv'


class SalesPredictor:
    """Manages ML model for sales prediction"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.metadata = None
        self.load_model()
        if not self.is_model_trained():
            self._auto_train_if_possible()
    
    def ensure_model_dir(self):
        """Ensure models directory exists"""
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    def train_model(self, data_path: str) -> Dict[str, Any]:
        """
        Train the Linear Regression model on data
        
        Args:
            data_path: Path to processed data CSV
            
        Returns:
            Dictionary with training results and metrics
        """
        try:
            self.ensure_model_dir()
            
            logger.info(f"Loading data from {data_path}")
            df = pd.read_csv(data_path)
            
            # Columns to drop (same as in notebook)
            drop_columns = [
                'Row_ID', 'Order_ID', 'Order_Date', 'Ship_Date', 'Ship_Mode',
                'Customer_ID', 'Product_ID', 'Customer_Name', 'Order_Year',
                'Order_Month', 'Order_Weekday', 'Country', 'State', 'City',
                'Postal_Code', 'Product_Name', 'Ship_Year', 'Ship_Month', 'Ship_Weekday'
            ]
            
            df_models = df.drop(
                columns=[col for col in drop_columns if col in df.columns],
                errors="ignore"
            )
            
            # Prepare features and target
            X = df_models.drop(columns=['Sales'], errors="ignore")
            y = df_models['Sales']
            
            # One-hot encode categorical features
            X_encoded = pd.get_dummies(X, drop_first=True)
            
            # Store feature names for later predictions
            self.feature_names = X_encoded.columns.tolist()
            
            logger.info(f"Training data shape: {X_encoded.shape}")
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X_encoded)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model = LinearRegression()
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            # Store metadata
            self.metadata = {
                'training_date': datetime.now().isoformat(),
                'model_type': 'LinearRegression',
                'num_features': len(self.feature_names),
                'feature_names': self.feature_names,
                'test_size': 0.2,
                'random_state': 42,
                'metrics': {
                    'mae': float(mae),
                    'rmse': float(rmse),
                    'r2_score': float(r2),
                    'test_samples': len(y_test),
                    'train_samples': len(y_train)
                }
            }
            
            # Save model and metadata
            self._save_model()
            
            logger.info(f"Model training complete. MAE: {mae:.2f}, RMSE: {rmse:.2f}, R²: {r2:.4f}")
            
            return {
                'status': 'success',
                'message': 'Model trained successfully',
                'metrics': self.metadata['metrics'],
                'feature_count': len(self.feature_names)
            }
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise
    
    def predict(self, features_dict: Dict[str, Any]) -> float:
        """
        Make prediction on new data
        
        Args:
            features_dict: Dictionary of feature values
            
        Returns:
            Predicted sales value
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Please train or load model first.")
        
        try:
            # Convert to DataFrame with same structure as training
            df_input = pd.DataFrame([features_dict])
            
            # One-hot encode
            df_encoded = pd.get_dummies(df_input)
            
            # Ensure same features as training data
            for feature in self.feature_names:
                if feature not in df_encoded.columns:
                    df_encoded[feature] = 0
            
            # Use only features that were in training
            df_encoded = df_encoded[self.feature_names]
            
            # Scale
            X_scaled = self.scaler.transform(df_encoded)
            
            # Predict
            prediction = self.model.predict(X_scaled)[0]
            
            logger.info(f"Prediction made: {prediction:.2f}")
            return float(prediction)
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def predict_batch(self, features_list: List[Dict[str, Any]]) -> List[float]:
        """
        Make predictions on multiple records
        
        Args:
            features_list: List of feature dictionaries
            
        Returns:
            List of predicted values
        """
        predictions = []
        for features in features_list:
            try:
                pred = self.predict(features)
                predictions.append(pred)
            except Exception as e:
                logger.error(f"Batch prediction item failed: {e}")
                predictions.append(None)
        
        return predictions
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get model performance metrics"""
        if self.metadata is None:
            return {'status': 'error', 'message': 'Model not trained'}
        
        return {
            'status': 'success',
            'metrics': self.metadata['metrics'],
            'training_date': self.metadata['training_date'],
            'model_type': self.metadata['model_type'],
            'feature_count': self.metadata['num_features']
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed model information"""
        if self.metadata is None:
            return {'status': 'error', 'message': 'Model not trained'}
        
        return {
            'status': 'success',
            'model_type': self.metadata['model_type'],
            'training_date': self.metadata['training_date'],
            'num_features': self.metadata['num_features'],
            'feature_names': self.metadata['feature_names'],
            'metrics': self.metadata['metrics'],
            'model_parameters': {
                'fit_intercept': True,
                'copy_X': True,
                'positive': False,
                'random_state': 42
            }
        }
    
    def _save_model(self):
        """Save model, scaler, and metadata to disk"""
        try:
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump(self.model, f)
            
            with open(SCALER_PATH, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            with open(FEATURES_PATH, 'wb') as f:
                pickle.dump(self.feature_names, f)
            
            import json
            with open(METADATA_PATH, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            logger.info(f"Model saved to {MODEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise
    
    def load_model(self):
        """Load model from disk if exists"""
        try:
            if MODEL_PATH.exists() and SCALER_PATH.exists() and FEATURES_PATH.exists():
                with open(MODEL_PATH, 'rb') as f:
                    self.model = pickle.load(f)
                
                with open(SCALER_PATH, 'rb') as f:
                    self.scaler = pickle.load(f)
                
                with open(FEATURES_PATH, 'rb') as f:
                    self.feature_names = pickle.load(f)
                
                if METADATA_PATH.exists():
                    import json
                    with open(METADATA_PATH, 'r') as f:
                        self.metadata = json.load(f)
                
                logger.info("Model loaded from disk")
            else:
                logger.warning("No saved model found")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")

    def _auto_train_if_possible(self):
        """Train a default model when no persisted artifacts exist yet."""
        try:
            if not DEFAULT_TRAINING_DATA_PATH.exists():
                logger.warning(
                    "Auto-train skipped: default data file not found at %s",
                    DEFAULT_TRAINING_DATA_PATH
                )
                return

            logger.info("No trained model found. Auto-training using default dataset.")
            self.train_model(str(DEFAULT_TRAINING_DATA_PATH))
        except Exception as e:
            logger.error(f"Auto-train failed: {e}")
    
    def is_model_trained(self) -> bool:
        """Check if model is trained and ready"""
        return self.model is not None and self.scaler is not None and self.feature_names is not None


# Global predictor instance
_predictor = None


def get_predictor() -> SalesPredictor:
    """Get or create global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = SalesPredictor()
    return _predictor
