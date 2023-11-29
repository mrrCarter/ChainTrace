from datetime import datetime
import requests
import json
from config import API_KEY

# Etherscan API Key
ETHERSCAN_API_KEY = API_KEY

# Etherscan API URL
ETHERSCAN_API_URL = "http://api.etherscan.io/api"

def get_eth_balance(address):
    """ Fetch the ETH balance for a given Ethereum address """
    params = {
        'module': 'account',
        'action': 'balance',
        'address': address,
        'tag': 'latest',
        'apikey': ETHERSCAN_API_KEY
    }
    response = requests.get(ETHERSCAN_API_URL, params=params)
    return response.json() if response.status_code == 200 else None


def get_transactions_by_address(address):
    """ Fetch transactions for a given Ethereum address """
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
        'apikey': ETHERSCAN_API_KEY
    }
    response = requests.get(ETHERSCAN_API_URL, params=params)
    return response.json() if response.status_code == 200 else None

def get_transaction_by_hash(txn_hash):
    """ Fetch a transaction by its hash """
    params = {
        'module': 'proxy',
        'action': 'eth_getTransactionByHash',
        'txhash': txn_hash,
        'apikey': ETHERSCAN_API_KEY
    }
    response = requests.get(ETHERSCAN_API_URL, params=params)
    return response.json() if response.status_code == 200 else None

def save_to_file(data, filename, address):
    """ Save the data to a JSON file with the last six digits of the address """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    last_six = address[-6:]  # Extract last six characters of the address
    unique_filename = f"{filename.split('.')[0]}_{last_six}.json"
    with open(unique_filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {unique_filename}")


def main():
    address_or_hash = input("Enter an Ethereum address or transaction hash: ")
    result = None
    target_address = None

    if len(address_or_hash) == 66:  # Length of an Ethereum transaction hash
        transaction_data = get_transaction_by_hash(address_or_hash)
        if transaction_data and 'result' in transaction_data and transaction_data['result']:
            target_address = transaction_data['result']['from']
        else:
            print("Transaction hash not found or an error occurred.")
            return
    else:
        target_address = address_or_hash

    result = get_transactions_by_address(target_address)
    filename = f"address_transactions_{target_address[-6:]}.json"

    if result and 'result' in result:
        total_sent = 0
        receiver_counts = {}

        for tx in result['result']:
            if tx['from'].lower() == address_or_hash.lower():
                total_sent += int(tx['value'])
                receiver = tx['to'].lower()
                receiver_counts[receiver] = receiver_counts.get(receiver, 0) + 1

        total_sent_eth = total_sent / 1e18  # Convert Wei to ETH

        if receiver_counts:
            most_frequent_receiver = max(receiver_counts, key=receiver_counts.get)
            print(f"Most frequent receiver: {most_frequent_receiver}")
        else:
            print("No outgoing transactions found for this address.")


        # Fetching current balance
        balance_data = get_eth_balance(target_address)
        if balance_data and 'result' in balance_data:
            eth_balance = int(balance_data['result']) / 1e18

            # Placeholder for ETH to USD conversion rate
            eth_to_usd_rate = 3000  # Replace this with the actual rate
            balance_usd = eth_balance * eth_to_usd_rate
            total_sent_usd = total_sent_eth * eth_to_usd_rate

            print(f"Total ETH sent from {target_address}: {total_sent_eth} ETH (${total_sent_usd})")
            print(f"Current balance: {eth_balance} ETH (${balance_usd})")
            if receiver_counts:
                print(f"Most frequent receiver: {most_frequent_receiver}")

        save_to_file(result, filename, target_address)
        print(f"Data saved to {filename}")
    else:
        print("No data found or an error occurred.")

if __name__ == "__main__":
    main()