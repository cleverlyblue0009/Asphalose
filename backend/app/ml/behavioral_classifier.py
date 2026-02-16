"""
Behavioral Classification Model for detecting suspicious activities.
Uses RandomForestClassifier to classify activities as normal or suspicious.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from datetime import datetime
from typing import Dict, Tuple
from ..core.config import settings


class BehavioralClassifier:
    """Machine learning model for behavioral classification."""

    def __init__(self, model_path: str = None):
        """
        Initialize the behavioral classifier.

        Args:
            model_path: Path to saved model file
        """
        self.model = None
        self.label_encoders = {}
        self.feature_names = [
            'activity_type',
            'hour_of_day',
            'day_of_week',
            'process_count',
            'file_access_count',
            'network_connection_count',
            'failed_login_attempts'
        ]

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )

    def generate_synthetic_data(self, n_samples: int = 10000) -> pd.DataFrame:
        """
        Generate synthetic training data.

        Args:
            n_samples: Number of samples to generate

        Returns:
            DataFrame with synthetic activity data
        """
        np.random.seed(42)

        # Generate normal activities (70%)
        n_normal = int(n_samples * 0.7)
        normal_data = {
            'activity_type': np.random.choice(['process', 'file_access', 'login', 'network'], n_normal),
            'hour_of_day': np.random.normal(12, 4, n_normal).astype(int) % 24,
            'day_of_week': np.random.randint(0, 7, n_normal),
            'process_count': np.random.poisson(5, n_normal),
            'file_access_count': np.random.poisson(10, n_normal),
            'network_connection_count': np.random.poisson(3, n_normal),
            'failed_login_attempts': np.random.poisson(0.5, n_normal),
            'is_suspicious': np.zeros(n_normal, dtype=int)
        }

        # Generate suspicious activities (30%)
        n_suspicious = n_samples - n_normal
        suspicious_data = {
            'activity_type': np.random.choice(['process', 'file_access', 'login', 'network'], n_suspicious),
            'hour_of_day': np.random.choice([0, 1, 2, 3, 4, 22, 23], n_suspicious),  # Unusual hours
            'day_of_week': np.random.randint(0, 7, n_suspicious),
            'process_count': np.random.poisson(20, n_suspicious),  # High process count
            'file_access_count': np.random.poisson(50, n_suspicious),  # High file access
            'network_connection_count': np.random.poisson(30, n_suspicious),  # High network activity
            'failed_login_attempts': np.random.poisson(5, n_suspicious),  # Many failed logins
            'is_suspicious': np.ones(n_suspicious, dtype=int)
        }

        # Combine data
        df_normal = pd.DataFrame(normal_data)
        df_suspicious = pd.DataFrame(suspicious_data)
        df = pd.concat([df_normal, df_suspicious], ignore_index=True)

        # Shuffle
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)

        return df

    def preprocess_features(self, df: pd.DataFrame, fit: bool = False) -> np.ndarray:
        """
        Preprocess features for training or prediction.

        Args:
            df: Input DataFrame
            fit: Whether to fit label encoders (True for training)

        Returns:
            Preprocessed feature array
        """
        X = df[self.feature_names].copy()

        # Encode categorical features
        if fit:
            self.label_encoders['activity_type'] = LabelEncoder()
            X['activity_type'] = self.label_encoders['activity_type'].fit_transform(X['activity_type'])
        else:
            if 'activity_type' in self.label_encoders:
                X['activity_type'] = self.label_encoders['activity_type'].transform(X['activity_type'])

        return X.values

    def train(self, df: pd.DataFrame = None) -> Dict[str, float]:
        """
        Train the behavioral classification model.

        Args:
            df: Training data DataFrame (if None, generates synthetic data)

        Returns:
            Dictionary of training metrics
        """
        # Generate or use provided data
        if df is None:
            print("Generating synthetic training data...")
            df = self.generate_synthetic_data(n_samples=10000)

        # Prepare features and labels
        X = self.preprocess_features(df, fit=True)
        y = df['is_suspicious'].values

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Train model
        print(f"Training RandomForest with {len(X_train)} samples...")
        start_time = datetime.now()
        self.model.fit(X_train, y_train)
        training_duration = (datetime.now() - start_time).total_seconds()

        # Evaluate
        y_pred = self.model.predict(X_test)
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'training_samples': len(X_train),
            'training_duration': training_duration
        }

        print(f"✓ Training complete!")
        print(f"  Accuracy: {metrics['accuracy']:.3f}")
        print(f"  Precision: {metrics['precision']:.3f}")
        print(f"  Recall: {metrics['recall']:.3f}")
        print(f"  F1 Score: {metrics['f1_score']:.3f}")

        return metrics

    def predict(self, features: Dict) -> Tuple[bool, float]:
        """
        Predict if activity is suspicious.

        Args:
            features: Dictionary of activity features

        Returns:
            Tuple of (is_suspicious, confidence)
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

        # Predict
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        confidence = probabilities[prediction]

        return bool(prediction), float(confidence)

    def save_model(self, path: str):
        """
        Save model to disk.

        Args:
            path: Path to save model
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names
        }
        joblib.dump(model_data, path)
        print(f"✓ Model saved to {path}")

    def load_model(self, path: str):
        """
        Load model from disk.

        Args:
            path: Path to model file
        """
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.label_encoders = model_data['label_encoders']
        self.feature_names = model_data['feature_names']
        print(f"✓ Model loaded from {path}")
