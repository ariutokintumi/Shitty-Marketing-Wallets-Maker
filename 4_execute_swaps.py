import time
import json
from web3 import Web3

# Web3 configuration
infura_url = "https://base-mainnet.infura.io/v3/AQUI!!!"
chain_id = 8453  # Base Mainnet
web3 = Web3(Web3.HTTPProvider(infura_url))
usdc_contract_address = web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
uniswap_router_address = web3.to_checksum_address("0x4752Ba5Dbc23F44D87826276Bf6fd6B1c372AD24")
notusd_contract_address = web3.to_checksum_address("0x386509960a4f10796894b09CA98647DF93943a28")

# Load ABIs
with open("usdc_abi.json", "r") as f:
    usdc_abi = json.load(f)

with open("uniswap_router_abi.json", "r") as f:
    uniswap_router_abi = json.load(f)

# Contract instances
usdc_contract = web3.eth.contract(address=usdc_contract_address, abi=usdc_abi)
uniswap_router_contract = web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

# Load addresses from CSV
with open("addresses.txt", "r") as f:
    recipients = [line.strip().split(",") for line in f]

def approve_and_swap(private_key, recipient_address):
    # Retrieve USDC balance
    usdc_balance = usdc_contract.functions.balanceOf(recipient_address).call()
    
    if usdc_balance == 0:
        print(f"No USDC balance for {recipient_address}, skipping.")
        return

    # Approve the USDC balance for swap
    nonce = web3.eth.get_transaction_count(recipient_address)
    gas_price = web3.eth.gas_price

    # Approve transaction
    approve_tx = usdc_contract.functions.approve(
        uniswap_router_address, 
        usdc_balance
    ).build_transaction({
        'from': recipient_address,
        'nonce': nonce,
        'gas': 100000,  # Adjust as needed, this can be improved
        'gasPrice': gas_price,
        'chainId': chain_id
    })
    
    signed_approve_tx = web3.eth.account.sign_transaction(approve_tx, private_key)
    web3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)
    print(f"Approval transaction sent for address {recipient_address}")

    # Prepare and send the swap transaction
    swap_tx = uniswap_router_contract.functions.swapExactTokensForTokens(
        usdc_balance,                                # amountIn
        1,                                           # amountOutMin: Accept any amount of NOTUSD but 0 is not possible because it returns error
        [usdc_contract_address, notusd_contract_address],  # path: USDC -> NOTUSD
        recipient_address,                           # to: The recipient address
        int(time.time()) + 600                       # deadline: 10 minutes from now
    ).build_transaction({
        'from': recipient_address,
        'gas': 200000,  # Adjusted gas limit, this can be improved
        'gasPrice': web3.eth.gas_price,  # Dynamic gas price
        'nonce': nonce + 1,
        'chainId': chain_id
    })

    # Sign and send the transaction
    signed_swap_tx = web3.eth.account.sign_transaction(swap_tx, private_key)
    
    try:
        tx_hash = web3.eth.send_raw_transaction(signed_swap_tx.raw_transaction)
        print(f"Swap transaction sent for address {recipient_address} with tx hash: {tx_hash.hex()}")
    except Exception as e:
        print(f"Failed to send swap transaction for {recipient_address}: {str(e)}")
	
# Each recipient approves USDC and performs the swap to NOTUSD without delays
for recipient_address, recipient_private_key in recipients:
    approve_and_swap(recipient_private_key, recipient_address)


print("All transactions sent.")
