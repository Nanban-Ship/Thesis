from web3 import Web3
import config

w3_dummy = Web3()
contract = w3_dummy.eth.contract(address=config.UNISWAP_V2_ROUTER, abi=config.UNISWAP_ABI)

#Convert hex str
def decode_transaction_input(input_data):
    if not input_data or input_data == '0x':
        return None

    try:
        func_obj, func_params = contract.decode_function_input(input_data)
        
        if func_obj.fn_name == 'swapExactETHForTokens':
            return {
                'method': 'swapExactETHForTokens',
                'amountOutMin': func_params.get('amountOutMin', 0),
                'path': func_params.get('path', [])
            }
        return None

    except Exception:
        return None