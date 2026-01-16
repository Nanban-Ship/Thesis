import pandas as pd
import numpy as np
import lightgbm as lgb
import joblib
import os
import ast

# Silence the CPU warning
os.environ['LOKY_MAX_CPU_COUNT'] = '4' 

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import config
import utils

DATA_FILE = "training_data.csv"

def load_and_process_data():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        exit()

    df = pd.read_csv(DATA_FILE)
    print(f"Raw CSV loaded. Rows: {len(df)}")
    
    # Check if we have labels
    print(f"Label distribution:\n{df['label'].value_counts()}")

    features_list = []
    labels_list = []

    print("Processing rows...")
    for index, row in df.iterrows():
        try:
            # 1. Basic Features (Always available)
            gas_price_gwei = float(row['gas_price']) / 10**9
            value_eth = float(row['value']) / 10**18
            
            # 2. Complex Feature: Slippage (Maybe available)
            # If decoding fails (because it's a bot contract), we use -1.
            # This teaches the model: "Weird function signature = Suspicious"
            decoded = utils.decode_transaction_input(row['input_data'])
            
            if decoded:
                amount_out_min = float(decoded['amountOutMin'])
                is_standard_swap = 1 # Feature: Is it a normal Uniswap call?
            else:
                amount_out_min = -1  # Placeholder for "Unknown/Bot Contract"
                is_standard_swap = 0

            # Add to list
            features_list.append([gas_price_gwei, value_eth, amount_out_min, is_standard_swap])
            labels_list.append(row['label'])

        except Exception as e:
            # Only skip if the row is truly broken (missing columns)
            continue

    # Create DataFrame
    # Note: We added a 4th feature 'is_standard_swap'
    X = pd.DataFrame(features_list, columns=['gas_price', 'value_eth', 'amount_out_min', 'is_standard_swap'])
    y = pd.Series(labels_list)
    
    return X, y

def train():
    X, y = load_and_process_data()

    print(f"\nFinal Training Set: {len(X)} rows")
    print(f"Attacks: {sum(y)} | Normal: {len(y) - sum(y)}")

    if sum(y) < 10:
        print("[ERROR] Still not enough attacks. Something is wrong with the CSV.")
        return

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Imbalance Weight
    n_pos = sum(y_train)
    n_neg = len(y_train) - n_pos
    class_weight = n_neg / n_pos if n_pos > 0 else 1

    print(f"Training LightGBM (Weight: {class_weight:.2f})...")

    clf = lgb.LGBMClassifier(
        n_estimators=200,
        learning_rate=0.05,
        num_leaves=31,
        scale_pos_weight=class_weight,
        random_state=42,
        verbose=-1
    )
    clf.fit(X_train, y_train)

    # Evaluation
    y_pred = clf.predict(X_test)
    
    # Handle case where test set might miss a class (rare now)
    labels = np.unique(y_test)
    target_names = ['Normal', 'Attack'] if len(labels) == 2 else [str(x) for x in labels]
    
    print("\n--- Model Results ---")
    print(classification_report(y_test, y_pred, target_names=target_names))

    joblib.dump(clf, config.MODEL_PATH)
    print("Model saved successfully.")

if __name__ == "__main__":
    train()