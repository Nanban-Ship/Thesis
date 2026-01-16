import pandas as pd
from dune_client.client import DuneClient
from dune_client.query import QueryBase


# Paste API Key
DUNE_API_KEY = "YOUR_KEY_HERE" # API key here

# Paste the Query ID
QUERY_ID = YOUR_QUERY_ID # Every quary has one, it's the number in the url when you open your query  

def download_dune_data():
    print("Initializing Dune Client...")
    dune = DuneClient(DUNE_API_KEY)
    
    print(f"Fetching result for Query ID: {QUERY_ID}...")
    print("This may take 1-2 minutes depending on query size...")
    
    try:
        # Get latest results
        results_df = dune.get_latest_result_dataframe(QueryBase(query_id=QUERY_ID))
        
        # Save to CSV
        filename = "training_data.csv"
        results_df.to_csv(filename, index=False)
        
        print(f"SUCCESS! Data saved to {filename}")
        print(f"Rows downloaded: {len(results_df)}")
        print("You can now run 'check_data.py' and 'python train_model.py'")
        
    except Exception as e:
        print("ERROR: Could not fetch data.")
        print(f"Details: {e}")

if __name__ == "__main__":

    download_dune_data()    
