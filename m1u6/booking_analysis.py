#################################################
#                                               
#  Booking Cancellation Analysis and Modeling   
#                                               
#   The purpose of this script is top illustrate a complete workflow for data analysis and
#   predictive modeling using a hotel booking dataset.
#   The dataset contains information about hotel ookings, including whether the booking was
#   canceled or not. The goal is to predict booking cancellations based on various features.
#                                               
#################################################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix,
                             classification_report)
from sklearn.impute import SimpleImputer

###
# Function to display the model performance metrics
# We are focusing on several important metrics for classification tasks:
#  - Accuracy: "What proportion of all classifications was actually correct?", 
#  - Precision, "Out of all predicted positives, how many were actually positive?" 
#  - Recall: "Out of all actual positives, how many were predicted correctly?"
#  - F1-score: "How good is the model in balancing between precision and recall?"
#  - ROC-AUC: "How well the model ranks positive instances higher than negative ones?"
#  - Confusion Matrix: "How many true positives, true negatives, false positives, and false negatives were there?"

def show_metrics(output_actual, output_predicted, output_probability, label):
    acc  = accuracy_score(output_actual, output_predicted)
    prec = precision_score(output_actual, output_predicted, zero_division=0)
    rec  = recall_score(output_actual, output_predicted, zero_division=0)
    f1   = f1_score(output_actual, output_predicted, zero_division=0)
    auc  = roc_auc_score(output_actual, output_probability)

    print(f"\n=== {label} ===")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1-score : {f1:.4f}")
    print(f"ROC-AUC  : {auc:.4f}\n")
    print(classification_report(output_actual, output_predicted, digits=4))

    cm = confusion_matrix(output_actual, output_predicted)
    fig, ax = plt.subplots(figsize=(4, 4))
    im = ax.imshow(cm, interpolation="nearest")
    ax.set_title(f"Confusion Matrix — {label}")
    ax.set_xticks([0,1]); ax.set_xticklabels(["Not canceled","Canceled"])
    ax.set_yticks([0,1]); ax.set_yticklabels(["Not canceled","Canceled"])
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, cm[i, j], ha="center", va="center")
    plt.xlabel("Predicted"); plt.ylabel("True"); plt.tight_layout()
    plt.show()


# Answer to life, universe, and everything
RANDOM_STATE = 42

# 1) Load two datasets and combine
# Make sure to have H1.csv and H2.csv in the same folder as this script
ds1 = pd.read_csv('H1.csv')
ds2 = pd.read_csv('H2.csv')
df = pd.concat([ds1, ds2], ignore_index=True)

### 2) Basic cleaning
# 2.1: There are columns that can be used to directly predict the target (data leakage) - they should be removed
df = df.drop(columns=['ReservationStatus', 'ReservationStatusDate'])

# 2.2 The "IsCanceled" column is the target variable - we need to remove the rows where it's missing
df = df.dropna(subset=['IsCanceled'])

### 3) Define "features" -> columns to use for prediction
# We can use most of the columns, except for "IsCanceled" (target) 
features = ['LeadTime','ArrivalDateYear','ArrivalDateMonth','ArrivalDateWeekNumber','ArrivalDateDayOfMonth',
    'StaysInWeekendNights','StaysInWeekNights','Adults','Children','Babies','Meal','Country','MarketSegment','DistributionChannel',
    'IsRepeatedGuest','PreviousCancellations','PreviousBookingsNotCanceled','ReservedRoomType','AssignedRoomType',
    'BookingChanges','DepositType','Agent','Company','DaysInWaitingList','CustomerType','ADR','RequiredCarParkingSpaces',
    'TotalOfSpecialRequests'
]
model_input = df[features].copy()
model_labels = df['IsCanceled'].astype(int)

### 4) Data preprocessing pipelines - transfomations
# Separate numeric and categorical features
numeric_features = model_input.select_dtypes(include=['int64','float64']).columns.tolist()
categorical_features = [c for c in model_input.columns if c not in numeric_features]

# Some features (columns) have missing values. We can choose to drop, ignore, or impute them.
# For this case, We'll do simple imputation inside the pipelines.

# Numeric features transformation: 
# We will use median imputation (where the values are missing, we replace them with the median of that column)
# We also need to do scaling to reduce the influence of outliers - we will use StandardScaler for that
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

# Categorical features transformation:
# We will use most_frequent imputation (where the values are missing, we replace them with the most frequent value of that column)
# We will use OneHotEncoder to convert categorical variables into binary columns.
# This is required for Logistic Regression, which cannot handle categorical variables directly.
categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocess = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ]
)

### 5) Create the train/test split using stratification
# This ensures that the proportion of classes in the target variable is maintained in both sets.
input_train, input_test, output_train, output_test = train_test_split(
    model_input, model_labels, test_size=0.2, stratify=model_labels, random_state=RANDOM_STATE
)

###  Now we can create and evaluate some models
# 6) Baseline model: Logistic Regression
# We will use 500 iterations for training
logreg = Pipeline(steps=[
    ("preprocess", preprocess),
    ("clf", LogisticRegression(max_iter=500, random_state=RANDOM_STATE, n_jobs=None))
])

startTime = pd.Timestamp.now()
print("Training Logistic Regression (baseline) model...")

# Run the training set
logreg.fit(input_train, output_train)

endTime = pd.Timestamp.now()
print("Training time (Logistic regression):", endTime - startTime)

# Run the test set and get predictions
output_pred = logreg.predict(input_test)

# Get the predicted probabilities for the positive class (class 1)
output_probability = logreg.predict_proba(input_test)[:, 1]

# Show the metrics for the baseline model
show_metrics(output_test, output_pred, output_probability, "Logistic Regression (baseline)")



# 7) Random Forest with light tuning
# It is important to include the same preprocessing steps in the pipeline
# so that the model output can be compared with the baseline.
###
# In this model, we we will use the "Grid Search" technique to find the best hyperparameters
# for the Random Forest model. We will tune the following hyperparameters:
#  - n_estimators: number of trees in the forest
#  - max_depth: maximum depth of the tree
#  - min_samples_split: minimum number of samples required to split an internal node
# For each value combination, we will use 5-fold cross-validation to evaluate the model performance.
# (The 5-fold cross-validation means that the training set is split into 5 parts,
#  and the model is trained on 4 parts and validated on the remaining part, repeated 5 times.)
# The scoring metric we will use is F1-score, which balances precision and recall.

# Create the Random Forest pipeline with the same preprocessing steps as the baseline model
rf = Pipeline(steps=[
    ("preprocess", preprocess),
    ("clf", RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1))
])

# Define the hyperparameter grid to search
param_grid = {
    "clf__n_estimators": [100, 200],
    "clf__max_depth": [None, 12, 24],
    "clf__min_samples_split": [2, 5]
}

startTime = pd.Timestamp.now()
print("Training Random Forest (tuned) model...")

#Create the folds and run the grid search
crossValFolds = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
grid = GridSearchCV(rf, param_grid=param_grid, scoring="f1", cv=crossValFolds, n_jobs=-1, verbose=2)
grid.fit(input_train, output_train)

endTime = pd.Timestamp.now()
print("Training time (Random Forest):", endTime - startTime)

print("Best parameters chosen:", grid.best_params_)
best_rf = grid.best_estimator_


# Run the test set and get predictions
output_pred_rf = best_rf.predict(input_test)
# Get the predicted probabilities for the positive class (class 1)
output_probability_rf = best_rf.predict_proba(input_test)[:, 1]

# Show the metrics for the Random Forest model
show_metrics(output_test, output_pred_rf, output_probability_rf, "Random Forest (tuned)")
