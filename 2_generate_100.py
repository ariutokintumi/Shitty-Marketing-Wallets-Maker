from eth_account import Account

def generate_multiple_addresses(n):
    accounts = []
    
    for i in range(n):
        account = Account.create()
        accounts.append({"address": account.address, "private_key": account.key.hex()})
    
    # Guardar en un archivo
    with open("addresses.txt", "w") as file:
        for i, acc in enumerate(accounts):
            file.write(f"{acc['address']},{acc['private_key']}\n")
    
    return accounts

# Generate 100 addresses
accounts = generate_multiple_addresses(100)
print("Generated 100 addresses and saved to addresses.txt")
