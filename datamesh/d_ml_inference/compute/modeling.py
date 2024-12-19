import warnings
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from lightgbm import LGBMRegressor
from shap import TreeExplainer, summary_plot

warnings.filterwarnings('ignore')

DATASET = './datamesh/c_features/datasets/mobility_regression_training.csv'
MODEL_PATH = './datamesh/d_ml_inference/models/mobility_regressor.joblib'
PLOT_PATH = './datamesh/d_ml_inference/plots/mobility_regressor_shap.png'

# 1. load data
df = pd.read_csv(DATASET)

# 2. split data into train and test
y = df['number_of_sessions_per_hour'].values
X = df.drop(columns=['number_of_sessions_per_hour'])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. preprocess data
preprocessor = ColumnTransformer(
    transformers=[
        ('hour_slice_encoder', OrdinalEncoder(), ['hour_slice']) 
    ],
    remainder='passthrough'
)

model = Pipeline([
    ('cat_pipeline', preprocessor),
    ('model', LGBMRegressor(
        random_state=42,
        min_child_samples=20,  # Add minimum samples per leaf
        subsample=0.8,         # Use bagging
        colsample_bytree=0.8   # Use feature fraction
    ))
])

# 4. train model
model.fit(X_train, y_train)

# 5. evaluate model
y_pred = model.predict(X_test)

print("Model Performance Metrics:")
print("-" * 30)
print(f"Mean Absolute Error: {mean_absolute_error(y_test, y_pred):.2f}")
print(f"Root Mean Squared Error: {root_mean_squared_error(y_test, y_pred):.2f}")

# 6. export model
joblib.dump(model, MODEL_PATH)

# 7. export shap plot
explainer = TreeExplainer(model.named_steps['model'])
X_test_encoded = preprocessor.transform(X_test)
X_test_encoded = pd.DataFrame(X_test_encoded, columns=X.columns)
summary_plot(explainer.shap_values(X_test_encoded), X_test_encoded, show=False)
plt.savefig(PLOT_PATH)
