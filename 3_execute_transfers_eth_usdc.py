import time
import random
import json
from web3 import Web3

# Web3 configuration
infura_url = "https://base-mainnet.infura.io/v3/AQUI!!!"
private_key_sender = "AQUI!!!"
sender_address = "AQUI!!!"
chain_id = 8453  # Base Mainnet

# Uniswap Router and Token Contracts in BASE
usdc_contract_address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
uniswap_router_address = "0x4752Ba5Dbc23F44D87826276Bf6fd6B1c372AD24"
notusd_contract_address = "0x386509960a4f10796894b09CA98647DF93943a28"

# Initialize web3
web3 = Web3(Web3.HTTPProvider(infura_url))

# Load ABIs
with open("usdc_abi.json", "r") as f:
    usdc_abi = json.load(f)

# Contract instances
usdc_contract = web3.eth.contract(address=web3.to_checksum_address(usdc_contract_address), abi=usdc_abi)

# Function to check the USDC balance
def check_usdc_balance(address):
    return usdc_contract.functions.balanceOf(address).call()

# Function to send ETH and USDC to recipients
def send_usdc_and_eth(sender_private_key, recipient_address, amount_usdc, amount_eth):
    nonce = web3.eth.get_transaction_count(sender_address)
    
    # Check USDC balance before proceeding
    usdc_balance = check_usdc_balance(sender_address)
    if usdc_balance < int(amount_usdc * 10**6):
        raise Exception(f"Insufficient USDC balance: {usdc_balance / 10**6} USDC")

    # Get dynamic gas price
    gas_price = web3.eth.gas_price

    # Send ETH (for gas)
    eth_tx = {
        'from': sender_address,
        'to': recipient_address,
        'value': web3.to_wei(amount_eth, 'ether'),
        'gas': 21000,  # Set the correct gas limit for ETH transfer
        'gasPrice': gas_price,
        'nonce': nonce,
        'chainId': chain_id
    }


    signed_eth_tx = web3.eth.account.sign_transaction(eth_tx, sender_private_key)
    web3.eth.send_raw_transaction(signed_eth_tx.raw_transaction)
    time.sleep(10)  # Small delay to avoid nonce issues between iterations, this can be improved with a general count

    # Send USDC
    usdc_tx = usdc_contract.functions.transfer(
        web3.to_checksum_address(recipient_address),
        int(amount_usdc * 10**6)
    ).build_transaction({
        'nonce': nonce + 1,
        'gasPrice': gas_price,
        'gas': 100000,  # Increased gas limit for ERC20 transfers, this can be improved
        'chainId': chain_id
    })

    signed_usdc_tx = web3.eth.account.sign_transaction(usdc_tx, sender_private_key)
    web3.eth.send_raw_transaction(signed_usdc_tx.raw_transaction)

# Load addresses from CSV as was generated
with open("addresses.txt", "r") as f:
    recipients = [line.strip().split(",") for line in f]

# Distribute ETH and USDC (the ERC-20 token to swap later) to all recipients, in a random number just for the culture
for recipient_address, _ in recipients:
    random_usdc = round(random.uniform(0.001, 0.003), 6)
    random_eth = 0.000004  # ETH to cover gas, this can be improved
    send_usdc_and_eth(private_key_sender, recipient_address, random_usdc, random_eth)
    time.sleep(20)  # Small delay to avoid nonce issues, this can be improved a lot

print("Funds distributed.")
