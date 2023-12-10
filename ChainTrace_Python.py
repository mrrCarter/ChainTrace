from datetime import datetime
import requests
import json
import struct
import concurrent.futures
import time
import serial
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

# Define method mappings
method_mapping = {"0x": "00", "tether": "01", "monero": "10", "other": "11"}

# Method to Binary enumarate the file per processed transactions
def get_next_binary_number(filename):
    """ Reads the last binary number from the file and returns the next binary number """
    try:
        with open(filename, 'r') as file:
            content = file.read().split('*')  # Split the file content by '*'
            binary_numbers = [part for part in content if len(part) == 4 and part.isdigit()]  # Extract binary numbers
            if binary_numbers:
                last_number = binary_numbers[-1]  # Get the last binary number
                next_number = int(last_number, 2) + 1  # Increment the number
                return format(next_number, '04b')  # Convert back to 4-bit binary string
            else:
                return '0001'  # Start from '0001' if no binary number is found
    except FileNotFoundError:
        return '0001'  # Return '0001' if file is not found
# Function to convert transaction data to binary format and write to a text file
def process_transactions_to_binary(transactions, filename, target_address):
    next_binary_number = get_next_binary_number(filename)

    with open(filename, 'a') as file:
        ## Determine how many transactions will be processed
        # num_transactions = len(transactions) 
        # num_transactions_str = format(min(num_transactions, 15), '04b')  # limit to 15 Convert to 4-bit binary string

        # Append wallet identifier and trasaction count
        file.write(f"{next_binary_number}*{target_address}*[")  
        for i, tx in enumerate(transactions): #process the first 15 transactions
             # Check if transaction already exists in the file
            if transaction_exists_in_file(tx['hash'], filename):
                continue  # Skip if transaction already exists
            direction = '1' if tx['from'].lower() == target_address.lower() else '0'
            timestamp = struct.pack('<I', int(tx['timeStamp'])).hex()
            method = method_mapping.get(tx['input'][:10], method_mapping["other"])
            value_in_usd = struct.pack('<Q', int(float(tx['value']) / 1e18 * 2351 * 100)).hex()
            start_of_wallet = '1' if i == 0 else '0'  # '1' for the first transaction

            # Format the transaction string
            transaction_str = f"%{direction}${timestamp}${method}${value_in_usd}${start_of_wallet}"

            file.write(transaction_str)
        file.write("%]")  # End of file

# Function to check if a transaction already exists in the file
def transaction_exists_in_file(tx_hash, filename):
    try:
        with open(filename, 'r') as file:
            if tx_hash in file.read():
                return True
    except FileNotFoundError:
        # File does not exist, so the transaction doesn't exist in it
        pass
    return False


def send_file_via_uart(serial_port, file_path, baud_rate=115200):
    # Open the serial port
    with serial.Serial(serial_port, baud_rate) as ser:
        # Open the text file
        with open(file_path, 'r') as file:
            # Read the file and send it over UART
            while True:
                chunk = file.read(1024)  # Read in chunks of 1024 characters
                if not chunk:
                    break  # End of file
                ser.write(chunk.encode())  # Encode string to bytes and send
                time.sleep(0.1)  # Slight delay to ensure data integrity


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

# Function to check if a transaction already exists in the file
def transaction_exists_in_file(tx_hash, filename):
    try:
        with open(filename, 'r') as file:
            if tx_hash in file.read():
                return True
    except FileNotFoundError:
        # File does not exist, so the transaction doesn't exist in it
        pass
    return False

"""Parallel Processing function"""
processed_addresses = set()  # Global set to track processed addresses

def process_address(address, binary_filename, json_filename, long_txt_filename, depth=0, max_depth=3):
    global processed_addresses
    if address in processed_addresses or depth > max_depth:
        return  # Skip if address is already processed or max depth is reached
    
    processed_addresses.add(address)  # Add address to processed set

    try:
        if address:  
            transactions = get_transactions_by_address(address)
            if transactions and 'result' in transactions and isinstance(transactions['result'], list):
                # save_to_binary_file(transactions['result'], binary_filename)
                save_to_file(transactions['result'], json_filename)
                process_transactions_to_binary(transactions['result'], address, long_txt_filename)
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
    # result = None
    global target_address
    target_address = address_or_hash
    

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    long_txt_filename = "transactions_971361.txt" # Constant filename for all txt transactions
    # process_transactions_to_binary(result['result'], long_txt_filename, target_address)  # Process initial address


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
    json_filename = f"address_transactions_{target_address[-6:]}.json"


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
        # Process and convert transactions to binary format
        text_filename = f"transactions_971361.txt"

        process_transactions_to_binary(result['result'], long_txt_filename, target_address)
        print(f"Binary + HEX data saved to text file: {text_filename}")        

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
            futures = [executor.submit(process_address, addr, binary_filename, json_filename, long_txt_filename) for addr in addresses_to_process]
            for future in concurrent.futures.as_completed(futures):
                future.result()  # Wait for each thread to complete
    except Exception as e:
        print(f"Error during parallel processing: {e}")

if __name__ == "__main__":
    main()

# from datetime import datetime
# import requests
# import json
# import struct
# import concurrent.futures
# import time
# import serial  # New import for serial communication
# from config import API_KEY

# # Etherscan API Key and URL
# ETHERSCAN_API_KEY = API_KEY
# ETHERSCAN_API_URL = "http://api.etherscan.io/api"

# def get_eth_balance(address):
#     """ Fetch the ETH balance for a given Ethereum address """
#     params = {
#         'module': 'account',
#         'action': 'balance',
#         'address': address,
#         'tag': 'latest',
#         'apikey': ETHERSCAN_API_KEY
#     }
#     response = requests.get(ETHERSCAN_API_URL, params=params)
#     return response.json() if response.status_code == 200 else None

# def get_transactions_by_address(address):
#     """ Fetch transactions for a given Ethereum address and throw error if not able to """
#     params = {
#         'module': 'account',
#         'action': 'txlist',
#         'address': address,
#         'startblock': 0,
#         'endblock': 99999999,
#         'sort': 'asc',
#         'apikey': ETHERSCAN_API_KEY
#     }
#     try:
#         response = requests.get(ETHERSCAN_API_URL, params=params)
#         return response.json() if response.status_code == 200 else None
#     except Exception as e:
#         print(f"Error fetching transactions for address {address}: {e}")
#         return None

# def get_transaction_by_hash(txn_hash):
#     """ Fetch a transaction by its hash """
#     params = {
#         'module': 'proxy',
#         'action': 'eth_getTransactionByHash',
#         'txhash': txn_hash,
#         'apikey': ETHERSCAN_API_KEY
#     }
#     response = requests.get(ETHERSCAN_API_URL, params=params)
#     return response.json() if response.status_code == 200 else None

# def save_to_file(data, filename):
#     """ Save the data to a JSON file """
#     with open(filename, 'a') as file:
#         json.dump(data, file, indent=4)


# # def save_to_binary_file(data, filename):
# #     """ Append data to a binary file """
# #     with open(filename, 'ab') as file:  # 'ab' mode for appending in binary format
# #         for tx in data:
# #              try:
# #                 value_str = str(tx['value'])
# #                 value_len = len(value_str)
# #                 file.write(value_len.to_bytes(2, byteorder='little'))  # Writing the length of the string
# #                 file.write(value_str.encode())  # Writing the string itself
# #              except struct.error:
# #                 print(f"Value out of range: {tx['value']}")

# def convert_to_binary(data):
#     """ Convert data to binary format for FPGA """
#     binary_data = b''
#     for tx in data:
#         try:
#             value_str = str(tx['value'])
#             value_len = len(value_str)
#             binary_data += value_len.to_bytes(2, byteorder='little')
#             binary_data += value_str.encode()
#         except struct.error:
#             print(f"Value out of range: {tx['value']}")
#     return binary_data

#     # Function to convert transaction data to binary format and write to a text file
# def process_transactions_to_binary(transactions, filename, target_address):
#     with open(filename, 'w') as file:
#         file.write("[")  # Start of file
#         for i, tx in enumerate(transactions):
#             direction = '1' if tx['from'].lower() == target_address.lower() else '0'
#             timestamp = struct.pack('<I', int(tx['timeStamp'])).hex()
#             method = method_mapping.get(tx['input'][:10], method_mapping["other"])
#             value_in_usd = struct.pack('<Q', int(float(tx['value']) / 1e18 * 2351 * 100)).hex()
#             start_of_wallet = '1' if i == 0 else '0'  # '1' for the first transaction

#             # Format the transaction string
#             transaction_str = f"%{direction}${timestamp}${method}${value_in_usd}${start_of_wallet}"

#             file.write(transaction_str)
#         file.write("%]")  # End of file

# # Set up serial communication 
# # ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Change '/dev/ttyUSB0' to the correct port

# # # Function to send data to FPGA
# # def send_data_to_fpga(data):
# #     ser.write(data)
# #     time.sleep(0.1)  # Short delay to ensure data is sent properly
# def send_file_via_uart(serial_port, file_path, baud_rate=115200):
#     # Open the serial port
#     with serial.Serial(serial_port, baud_rate) as ser:
#         # Open the text file
#         with open(file_path, 'r') as file:
#             # Read the file and send it over UART
#             while True:
#                 chunk = file.read(1024)  # Read in chunks of 1024 characters
#                 if not chunk:
#                     break  # End of file
#                 ser.write(chunk.encode())  # Encode string to bytes and send
#                 time.sleep(0.1)  # Slight delay to ensure data integrity

# # # Example: Sending data
# # data_to_send = "Hello FPGA".encode()  # Convert string to bytes
# # send_data_to_fpga(data_to_send)

# # ser.close()  # Close the serial port when done 

# # """Parallel Processing function"""
# # processed_addresses = set()  # Global set to track processed addresses

# # def process_address(address, binary_filename, json_filename, depth=0, max_depth=3):
# #     global processed_addresses
# #     if address in processed_addresses or depth > max_depth:
# #         return  # Skip if address is already processed or max depth is reached
    
# #     processed_addresses.add(address)  # Add address to processed set

# #     try:
# #         if address:  
# #             transactions = get_transactions_by_address(address)
# #             if transactions and 'result' in transactions and isinstance(transactions['result'], list):
# #                 save_to_binary_file(transactions['result'], binary_filename)
# #                 save_to_file(transactions['result'], json_filename)
# #                 print(f"Processed {len(transactions['result'])} transactions for address {address}")

# #             # # Recursive call for each recipient in the transactions
# #             # for tx in transactions['result']:
# #             #     if 'to' in tx:
# #             #         print(f"Processing subsequent transactions...")
# #             #         # process_address(tx['to'], binary_filename, json_filename, depth + 1, max_depth)

# #             # print(f"Completed processing for address: {address}, waiting for next call...")
# #         else:
# #             print(f"Invalid or empty transactions for address {address}")
# #         time.sleep(1.2)  # wait ~ 1sec to make subsequent calls
# #     except Exception as e:
# #         print(f"Error processing address {address}: {e}")

# def main():

#     address_or_hash = input("Enter an Ethereum address or transaction hash: ")
#     target_address = address_or_hash if len(address_or_hash) != 66 else None

#     # Get current timestamp
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M")

#     result = get_transactions_by_address(target_address) if target_address else None
#     json_filename = f"address_transactions_{target_address[-6:]}_{timestamp}.json" if target_address else None

#     if result and 'result' in result:
#         # Process and output data
#         # ...

#         save_to_file(result, json_filename)
#         print(f"Data saved to {json_filename}")

#         # # Convert data to binary and send to FPGA
#         # binary_data = convert_to_binary(result['result'])
#         # serial_port = setup_serial_port()
#         # send_data_to_fpga(serial_port, binary_data)
#         # Convert and save the transaction data to a text file
#         text_filename = f"transactions_{target_address[-6:]}.txt"
#         process_transactions_to_binary(result['result'], text_filename, target_address)
#         print(f"Data saved to {text_filename}")

#         # Visualize the data (optional step)
#         with open(text_filename, 'r') as file:
#             print("Visualizing Data:")
#             print(file.read())

#         # Ask for confirmation before sending data to FPGA
#         confirm = input("Do you want to send this data to the FPGA? (yes/no): ")
#         if confirm.lower() == 'yes':
#             # Send the file data via UART
#             serial_port = "/dev/ttyUSB0"  # Replace with your actual COM port
#             send_file_via_uart(serial_port, text_filename)
#         else:
#             print("Data not sent to FPGA.")

#     # No recursive calls needed, focusing on initial transactions onlyk for the main function above to initiate serial comm and present MVP. Once serial comm good and we can interpret the bin data then we can parallel process the code below.
#     # address_or_hash = input("Enter an Ethereum address or transaction hash: ")
#     # result = None
#     # target_address = None\
    

#     # # Get current timestamp
#     # timestamp = datetime.now().strftime("%Y%m%d_%H%M")


#     # if len(address_or_hash) == 66:  # Length of an Ethereum transaction hash
#     #     transaction_data = get_transaction_by_hash(address_or_hash)
#     #     if transaction_data and 'result' in transaction_data and transaction_data['result']:
#     #         target_address = transaction_data['result']['from']
#     #     else:
#     #         print("Transaction hash not found or an error occurred.")
#     #         return
#     # else:
#     #     target_address = address_or_hash

#     # result = get_transactions_by_address(target_address)
#     # filename = f"address_transactions_{target_address[-6:]}.json"


#     # if result and 'result' in result:
#     #     total_sent = 0
#     #     receiver_counts = {}

#     #     for tx in result['result']:
#     #         if tx['from'].lower() == address_or_hash.lower():
#     #             total_sent += int(tx['value'])
#     #             receiver = tx['to'].lower()
#     #             receiver_counts[receiver] = receiver_counts.get(receiver, 0) + 1

#     #     total_sent_eth = total_sent / 1e18  # Convert Wei to ETH

#     #     if receiver_counts:
#     #         most_frequent_receiver = max(receiver_counts, key=receiver_counts.get)
#     #         print(f"Most frequent receiver: {most_frequent_receiver}")
#     #     else:
#     #         print("No outgoing transactions found for this address.")


#     #     # Fetching current balance
#     #     balance_data = get_eth_balance(target_address)
#     #     if balance_data and 'result' in balance_data:
#     #         eth_balance = int(balance_data['result']) / 1e18

#     #         # Placeholder for ETH to USD conversion rate
#     #         eth_to_usd_rate = 2163  # Replace this with the actual rate
#     #         balance_usd = eth_balance * eth_to_usd_rate
#     #         total_sent_usd = total_sent_eth * eth_to_usd_rate

#     #         print(f"Total ETH sent from {target_address}(based on today ETH price): {total_sent_eth} ETH (${total_sent_usd})")
#     #         print(f"Current balance: {eth_balance} ETH (${balance_usd})")
#     #         if receiver_counts:
#     #             print(f"Most frequent receiver: {most_frequent_receiver}")

#     #     json_filename = f"address_transactions_{target_address[-6:]}_{timestamp}.json"
#     #     save_to_file(result, json_filename)
#     #     print(f"Data saved to {json_filename}")
#     #     # Save to binary file
#     #     binary_filename = f"transactions_{target_address[-6:]}_{timestamp}.bin"
#     #     save_to_binary_file(result['result'], binary_filename)
#     #     print(f"Binary Data saved to {binary_filename}")
#     # else:
#     #     print("No data found or an error occurred.")

#     # # Parallel processing of subsequent addresses
#     # try:
#     #     addresses_to_process = {tx['to'] for tx in result['result']} - {target_address}  # Extract addresses
#     #     print("Addresses to process:", addresses_to_process)  # Debugging line just to see where we are at in console and where error might be 
#     #     # binary_filename = f"transactions_{target_address[-6:]}.bin"
#     #     # json_filename = f"address_transactions_{target_address[-6:]}.json"
#     #     with concurrent.futures.ThreadPoolExecutor() as executor:
#     #         futures = []
#     #         # Filename for the binary file
#     #         binary_filename = f"transactions_{target_address[-6:]}.bin"
#     #         # Schedule the execution of each address processing
#     #         futures = [executor.submit(process_address, addr, binary_filename, json_filename) for addr in addresses_to_process]
#     #         for future in concurrent.futures.as_completed(futures):
#     #             future.result()  # Wait for each thread to complete
#     # except Exception as e:
#     #     print(f"Error during parallel processing: {e}")


# if __name__ == "__main__":
#     main()
