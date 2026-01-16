import pandas as pd

# Load data
df = pd.read_csv("training_data.csv")

# Count labels
counts = df['label'].value_counts()
print("DATA COUNT:")
print(counts)