from datetime import datetime
import requests
import json
import struct
import concurrent.futures
import time
from config import API_KEY

# Etherscan API Key and URL
ETHERSCAN_API_KEY = API_KEY
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
    """ Fetch transactions for a given Ethereum address and throw error if not able to """
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
        'apikey': ETHERSCAN_API_KEY
    }
    try:
        response = requests.get(ETHERSCAN_API_URL, params=params)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching transactions for address {address}: {e}")
        return None

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

def save_to_file(data, filename):
    """ Save the data to a JSON file """
    with open(filename, 'a') as file:
        json.dump(data, file, indent=4)


def save_to_binary_file(data, filename):
    """ Append data to a binary file """
    with open(filename, 'ab') as file:  # 'ab' mode for appending in binary format
        for tx in data:
             try:
                value_str = str(tx['value'])
                value_len = len(value_str)
                file.write(value_len.to_bytes(2, byteorder='little'))  # Writing the length of the string
                file.write(value_str.encode())  # Writing the string itself
             except struct.error:
                print(f"Value out of range: {tx['value']}")

"""Parallel Processing function"""
processed_addresses = set()  # Global set to track processed addresses

def process_address(address, binary_filename, json_filename, depth=0, max_depth=3):
    global processed_addresses
    if address in processed_addresses or depth > max_depth:
        return  # Skip if address is already processed or max depth is reached
    
    processed_addresses.add(address)  # Add address to processed set

    try:
        if address:  
            transactions = get_transactions_by_address(address)
            if transactions and 'result' in transactions and isinstance(transactions['result'], list):
                save_to_binary_file(transactions['result'], binary_filename)
                save_to_file(transactions['result'], json_filename)
                print(f"Processed {len(transactions['result'])} transactions for address {address}")

            # # Recursive call for each recipient in the transactions
            # for tx in transactions['result']:
            #     if 'to' in tx:
            #         print(f"Processing subsequent transactions...")
            #         # process_address(tx['to'], binary_filename, json_filename, depth + 1, max_depth)

            # print(f"Completed processing for address: {address}, waiting for next call...")
        else:
            print(f"Invalid or empty transactions for address {address}")
        time.sleep(1.2)  # wait ~ 1sec to make subsequent calls
    except Exception as e:
        print(f"Error processing address {address}: {e}")

def main():
    address_or_hash = input("Enter an Ethereum address or transaction hash: ")
    result = None
    target_address = None\
    

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")


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
            eth_to_usd_rate = 2163  # Replace this with the actual rate
            balance_usd = eth_balance * eth_to_usd_rate
            total_sent_usd = total_sent_eth * eth_to_usd_rate

            print(f"Total ETH sent from {target_address}(based on today ETH price): {total_sent_eth} ETH (${total_sent_usd})")
            print(f"Current balance: {eth_balance} ETH (${balance_usd})")
            if receiver_counts:
                print(f"Most frequent receiver: {most_frequent_receiver}")

        json_filename = f"address_transactions_{target_address[-6:]}_{timestamp}.json"
        save_to_file(result, json_filename)
        print(f"Data saved to {json_filename}")
        # Save to binary file
        binary_filename = f"transactions_{target_address[-6:]}_{timestamp}.bin"
        save_to_binary_file(result['result'], binary_filename)
        print(f"Binary Data saved to {binary_filename}")
    else:
        print("No data found or an error occurred.")

    # Parallel processing of subsequent addresses
    try:
        addresses_to_process = {tx['to'] for tx in result['result']} - {target_address}  # Extract addresses
        print("Addresses to process:", addresses_to_process)  # Debugging line just to see where we are at in console and where error might be 
        # binary_filename = f"transactions_{target_address[-6:]}.bin"
        # json_filename = f"address_transactions_{target_address[-6:]}.json"
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            # Filename for the binary file
            binary_filename = f"transactions_{target_address[-6:]}.bin"
            # Schedule the execution of each address processing
            futures = [executor.submit(process_address, addr, binary_filename, json_filename) for addr in addresses_to_process]
            for future in concurrent.futures.as_completed(futures):
                future.result()  # Wait for each thread to complete
    except Exception as e:
        print(f"Error during parallel processing: {e}")

if __name__ == "__main__":
    main()


#     import json
# import requests
# from config import API_KEY

# # Constants and Functions (get_eth_balance, get_transactions_by_address, etc.)

# def send_data_to_fpga(data):
#     # Convert data to FPGA compatible format
#     # Send data to FPGA via chosen interface
#     pass

# def main():
#     # Fetch initial transaction data
#     address = input("Enter an Ethereum address or transaction hash: ")
#     transactions = get_transactions_by_address(address)
    
#     # Process and send initial data to FPGA
#     send_data_to_fpga(transactions['result'])

#     # Fetch and process subsequent transactions
#     processed_addresses = set(address)
#     while True:
#         new_addresses = extract_new_addresses(transactions)
#         for addr in new_addresses:
#             if addr not in processed_addresses:
#                 processed_addresses.add(addr)
#                 sub_transactions = get_transactions_by_address(addr)
#                 send_data_to_fpga(sub_transactions['result'])

# # Main execution
# if __name__ == "__main__":
#     main()
