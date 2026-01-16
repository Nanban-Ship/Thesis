#Webscoket endpoint
WSS_PROVIDER = "wss://eth-mainnet.g.alchemy.com/v2/ALCH_KEY_HERE" # Seems like Alchemy isnt cooperating currently, Infura and Quicknode don't seem to work either, might be free tier limitation 
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

MODEL_PATH = "mev_model.pkl"
SCALER_PATH = "scaler.pkl"  

UNISWAP_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "payable",
        "type": "function"
    }

]
