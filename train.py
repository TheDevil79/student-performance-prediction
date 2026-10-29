"""
Student Performance Prediction - Model Training Script
Trains a RandomForestRegressor pipeline on the Kaggle Student Performance dataset
to predict final math grade (G3) based on demographic, social, and academic attributes.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

DATA_PATH = os.path.join("data", "student-mat.csv")
MODEL_OUTPUT_PATH = "model.joblib"
REPORT_OUTPUT_PATH = "evaluation_report.json"

# Features to exclude according to requirements
EXCLUDED_COLS = ["G1", "G2", "G3"]

# Categorical features in the dataset
CATEGORICAL_FEATURES = [
    "school",
    "sex",
    "address",
    "famsize",
    "Pstatus",
    "Mjob",
    "Fjob",
    "reason",
    "guardian",
    "schoolsup",
    "famsup",
    "paid",
    "activities",
    "nursery",
    "higher",
    "internet",
    "romantic",
]

# Numerical features in the dataset
NUMERICAL_FEATURES = [
    "age",
    "Medu",
    "Fedu",
    "traveltime",
    "studytime",
    "failures",
    "famrel",
    "freetime",
    "goout",
    "Dalc",
    "Walc",
    "health",
    "absences",
]


def load_and_validate_data(file_path: str = DATA_PATH) -> pd.DataFrame:
    """Load dataset from semicolon-separated CSV and validate requirements."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Dataset not found at '{file_path}'.\n"
            "To obtain the dataset:\n"
            "1. Download it from Kaggle: https://www.kaggle.com/datasets/uciml/student-performance-data-set\n"
            "2. Extract 'student-mat.csv' into the 'data/' directory (e.g. data/student-mat.csv)."
        )

    print(f"[INFO] Loading dataset from '{file_path}' (delimiter=';')...")
    df = pd.read_csv(file_path, sep=";")

    print(f"[INFO] Raw dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns.")

    # Validation
    required_cols = CATEGORICAL_FEATURES + NUMERICAL_FEATURES + ["G3"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in dataset: {missing_cols}")

    # Check for missing values
    null_counts = df[required_cols].isnull().sum()
    total_nulls = int(null_counts.sum())
    if total_nulls > 0:
        print(f"[WARN] Found {total_nulls} missing values across features. Imputers will handle them.")
    else:
        print("[INFO] Zero missing values detected in required columns.")

    return df


def build_pipeline() -> Pipeline:
    """Build scikit-learn Pipeline with ColumnTransformer preprocessing and RandomForestRegressor."""
    # Preprocessor for numerical features: impute then standard scale
    num_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    # Preprocessor for categorical features: impute most frequent then OneHotEncode
    cat_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, NUMERICAL_FEATURES),
            ("cat", cat_transformer, CATEGORICAL_FEATURES),
        ]
    )

    # Full regression pipeline with RandomForest
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=150,
                    max_depth=12,
                    min_samples_split=4,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=None,
                ),
            ),
        ]
    )

    return pipeline


def train_and_evaluate():
    """Main training routine."""
    df = load_and_validate_data(DATA_PATH)

    # Separate features and target
    feature_cols = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
    X = df[feature_cols].copy()
    y = df["G3"].copy()

    print(f"[INFO] Predictor feature count: {X.shape[1]} features (G1 and G2 successfully excluded).")
    print(f"[INFO] Target 'G3' summary: min={y.min()}, max={y.max()}, mean={y.mean():.2f}, std={y.std():.2f}")

    # Train / Test split with fixed random seed
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"[INFO] Train split: {len(X_train)} samples | Test split: {len(X_test)} samples.")

    # Build and fit pipeline
    pipeline = build_pipeline()
    print("[INFO] Fitting scikit-learn Pipeline...")
    pipeline.fit(X_train, y_train)

    # Predictions
    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)

    # Calculate metrics (supporting scikit-learn root_mean_squared_error or manual sqrt)
    try:
        from sklearn.metrics import root_mean_squared_error
        train_rmse = float(root_mean_squared_error(y_train, y_pred_train))
        test_rmse = float(root_mean_squared_error(y_test, y_pred_test))
    except ImportError:
        train_rmse = float(np.sqrt(mean_squared_error(y_train, y_pred_train)))
        test_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))

    train_mae = float(mean_absolute_error(y_train, y_pred_train))
    train_r2 = float(r2_score(y_train, y_pred_train))

    test_mae = float(mean_absolute_error(y_test, y_pred_test))
    test_r2 = float(r2_score(y_test, y_pred_test))

    # Cross-validation score on whole dataset (5-fold)
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="neg_mean_absolute_error")
    cv_mae = float(-cv_scores.mean())

    print("\n=================== MODEL EVALUATION ===================")
    print(f"Test MAE  (Mean Absolute Error)     : {test_mae:.4f}")
    print(f"Test RMSE (Root Mean Squared Error) : {test_rmse:.4f}")
    print(f"Test R²   (Coefficient of Determ.)  : {test_r2:.4f}")
    print(f"5-Fold CV MAE                       : {cv_mae:.4f}")
    print("========================================================\n")

    # Save model pipeline
    print(f"[INFO] Saving fitted pipeline to '{MODEL_OUTPUT_PATH}'...")
    joblib.dump(pipeline, MODEL_OUTPUT_PATH)
    print("[INFO] Model saved successfully.")

    # Save evaluation report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "source": "Kaggle Student Performance (student-mat.csv)",
            "total_samples": len(df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features_count": len(feature_cols),
            "excluded_features": EXCLUDED_COLS,
            "categorical_features": CATEGORICAL_FEATURES,
            "numerical_features": NUMERICAL_FEATURES,
            "target": "G3",
        },
        "model": {
            "type": "RandomForestRegressor",
            "pipeline": "ColumnTransformer(OneHotEncoder + StandardScaler) + RandomForestRegressor",
            "hyperparameters": {
                "n_estimators": 150,
                "max_depth": 12,
                "min_samples_split": 4,
                "min_samples_leaf": 2,
                "random_state": 42,
            },
        },
        "metrics": {
            "test": {
                "MAE": round(test_mae, 4),
                "RMSE": round(test_rmse, 4),
                "R2": round(test_r2, 4),
            },
            "train": {
                "MAE": round(train_mae, 4),
                "RMSE": round(train_rmse, 4),
                "R2": round(train_r2, 4),
            },
            "cross_validation": {
                "5_fold_cv_mae": round(cv_mae, 4),
            },
        },
    }

    with open(REPORT_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[INFO] Evaluation report saved to '{REPORT_OUTPUT_PATH}'.")

    return pipeline, report


if __name__ == "__main__":
    train_and_evaluate()
