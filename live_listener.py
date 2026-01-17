import asyncio
import joblib
import pandas as pd
from web3 import Web3
from web3 import AsyncWeb3, WebSocketProvider
import config
import utils

# 1. Load Model
print("Loading model...")
try:
    model = joblib.load(config.MODEL_PATH)
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Error: Model not found. Run 'python train_model.py' first.")
    exit()

# 2. Connect to Alchemy (Mainnet)
# Connect using AsyncWeb3
w3 = AsyncWeb3(WebSocketProvider(config.WSS_PROVIDER))

async def process_transaction(tx_hash):
    try:
        # Fetch full transaction data
        tx = await w3.eth.get_transaction(tx_hash)
        
        # Filter: Only look at Uniswap Router
        if tx['to'] != config.UNISWAP_V2_ROUTER:
            return

        # Feature Engineering (Must match train_model.py exactly)
        decoded = utils.decode_transaction_input(tx['input'])
        
        gas_price_gwei = tx['gasPrice'] / 10**9
        value_eth = tx['value'] / 10**18
        
        if decoded:
            amount_out_min = decoded['amountOutMin']
            is_standard_swap = 1
        else:
            amount_out_min = -1
            is_standard_swap = 0

        # Create Input DataFrame
        input_df = pd.DataFrame([{
            'gas_price': gas_price_gwei,
            'value_eth': value_eth,
            'amount_out_min': amount_out_min,
            'is_standard_swap': is_standard_swap
        }])

        # Predict
        prediction = model.predict(input_df)[0]
        
        # Only print if it's an attack (Prediction == 1)
        if prediction == 1:
            probability = model.predict_proba(input_df)[0][1]
            print(f"\n[!!!] SANDWICH ATTACK DETECTED [!!!]")
            print(f"Tx Hash: {tx_hash.hex()}")
            print(f"Confidence: {probability:.2%}")
            print(f"Gas Price: {gas_price_gwei:.2f} Gwei | Value: {value_eth:.4f} ETH")

    except Exception:
        # Transactions often disappear from mempool or are invalid, skip them
        pass

async def log_loop(event_filter, poll_interval):
    print(f"Listening for transactions to {config.UNISWAP_V2_ROUTER}...")
    while True:
        try:
            new_entries = event_filter.get_new_entries()
            for tx_hash in new_entries:
                await process_transaction(tx_hash)
            await asyncio.sleep(poll_interval)
        except Exception as e:
            # Reconnect logic could go here, but not now
            await asyncio.sleep(1)

def main():
    if not w3.is_connected():
        print("Error: Could not connect to Alchemy.")
        print("Check config.py WSS_PROVIDER.")
        return

    # Filter for ALL pending transactions
    # (We filter for Uniswap inside the function to save API calls if possible, 
    # but 'pending' filter gives us hashes only, so we must fetch tx to check 'to' address)
    tx_filter = w3.eth.filter('pending')
    
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(log_loop(tx_filter, 0.1))
    except KeyboardInterrupt:
        print("\nStopping listener...")
    finally:
        loop.close()

if __name__ == "__main__":

    main()
