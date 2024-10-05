from web3 import Web3
from eth_account import Account
import os

def generate_address():
    # Generate new account
    account = Account.create()
    
    # Store private key
    private_key = account.key.hex()
    address = account.address
    
    # Save into a .txt file
    with open("account1.txt", "w") as file:
        file.write(f"Address: {address}\nPrivate Key: {private_key}")
    
    return address, private_key

address, private_key = generate_address()
print(f"Generated Address: {address}")
print(f"Private Key: {private_key}")
