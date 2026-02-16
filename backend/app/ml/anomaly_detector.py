"""
Anomaly Detection Model using Isolation Forest.
Detects unusual patterns in system behavior.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Dict, Tuple
from ..core.config import settings


class AnomalyDetector:
    """Anomaly detection model using Isolation Forest."""

    def __init__(self, model_path: str = None):
        """
        Initialize the anomaly detector.

        Args:
            model_path: Path to saved model file
        """
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'process_count',
            'file_access_count',
            'network_connection_count',
            'failed_login_attempts',
            'cpu_usage',
            'memory_usage',
            'disk_io_count'
        ]

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.model = IsolationForest(
                contamination=0.1,  # Expected proportion of outliers
                random_state=42,
                n_estimators=100
            )

    def generate_synthetic_data(self, n_samples: int = 5000) -> pd.DataFrame:
        """
        Generate synthetic training data for anomaly detection.

        Args:
            n_samples: Number of samples to generate

        Returns:
            DataFrame with synthetic behavior data
        """
        np.random.seed(42)

        # Generate mostly normal behavior (90%)
        n_normal = int(n_samples * 0.9)
        normal_data = {
            'process_count': np.random.poisson(5, n_normal),
            'file_access_count': np.random.poisson(10, n_normal),
            'network_connection_count': np.random.poisson(3, n_normal),
            'failed_login_attempts': np.random.poisson(0.3, n_normal),
            'cpu_usage': np.random.normal(40, 15, n_normal).clip(0, 100),
            'memory_usage': np.random.normal(50, 20, n_normal).clip(0, 100),
            'disk_io_count': np.random.poisson(20, n_normal)
        }

        # Generate anomalous behavior (10%)
        n_anomaly = n_samples - n_normal
        anomaly_data = {
            'process_count': np.random.poisson(50, n_anomaly),  # Unusual spike
            'file_access_count': np.random.poisson(100, n_anomaly),  # High access
            'network_connection_count': np.random.poisson(50, n_anomaly),  # Many connections
            'failed_login_attempts': np.random.poisson(10, n_anomaly),  # Many failures
            'cpu_usage': np.random.normal(85, 10, n_anomaly).clip(0, 100),  # High CPU
            'memory_usage': np.random.normal(90, 5, n_anomaly).clip(0, 100),  # High memory
            'disk_io_count': np.random.poisson(200, n_anomaly)  # High I/O
        }

        # Combine data
        df_normal = pd.DataFrame(normal_data)
        df_anomaly = pd.DataFrame(anomaly_data)
        df = pd.concat([df_normal, df_anomaly], ignore_index=True)

        # Shuffle
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)

        return df

    def preprocess_features(self, df: pd.DataFrame, fit: bool = False) -> np.ndarray:
        """
        Preprocess and scale features.

        Args:
            df: Input DataFrame
            fit: Whether to fit the scaler (True for training)

        Returns:
            Scaled feature array
        """
        X = df[self.feature_names].copy()

        if fit:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)

        return X_scaled

    def train(self, df: pd.DataFrame = None) -> Dict[str, float]:
        """
        Train the anomaly detection model.

        Args:
            df: Training data DataFrame (if None, generates synthetic data)

        Returns:
            Dictionary of training metrics
        """
        # Generate or use provided data
        if df is None:
            print("Generating synthetic training data for anomaly detection...")
            df = self.generate_synthetic_data(n_samples=5000)

        # Prepare and scale features
        X = self.preprocess_features(df, fit=True)

        # Train model
        print(f"Training Isolation Forest with {len(X)} samples...")
        self.model.fit(X)

        # Evaluate on training data
        predictions = self.model.predict(X)
        anomaly_count = np.sum(predictions == -1)
        normal_count = np.sum(predictions == 1)

        metrics = {
            'training_samples': len(X),
            'anomalies_detected': int(anomaly_count),
            'normal_detected': int(normal_count),
            'anomaly_percentage': float(anomaly_count / len(X) * 100)
        }

        print(f"✓ Anomaly detection training complete!")
        print(f"  Anomalies detected: {anomaly_count} ({metrics['anomaly_percentage']:.1f}%)")

        return metrics

    def predict(self, features: Dict) -> Tuple[bool, float]:
        """
        Predict if behavior is anomalous.

        Args:
            features: Dictionary of behavior features

        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        if self.model is None:
            raise ValueError("Model not trained. Please train or load a model first.")

        # Create DataFrame from features
        df = pd.DataFrame([features])

        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in df.columns:
                df[feature] = 0

        # Preprocess
        X = self.preprocess_features(df, fit=False)

        # Predict (-1 for anomaly, 1 for normal)
        prediction = self.model.predict(X)[0]
        anomaly_score = self.model.score_samples(X)[0]

        # Convert to boolean and normalize score
        is_anomaly = prediction == -1
        # Anomaly score is negative, convert to confidence (0-1)
        confidence = float(1.0 / (1.0 + np.exp(anomaly_score)))

        return is_anomaly, confidence

    def save_model(self, path: str):
        """
        Save model to disk.

        Args:
            path: Path to save model
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        joblib.dump(model_data, path)
        print(f"✓ Anomaly detector saved to {path}")

    def load_model(self, path: str):
        """
        Load model from disk.

        Args:
            path: Path to model file
        """
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        print(f"✓ Anomaly detector loaded from {path}")
