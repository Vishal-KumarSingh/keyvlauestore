import socket
import threading
import json
import scan
import random
import dbstore
serv_port=9999
cli_port=12345
# In-memory dictionary to store key-value pairs
kv_store = {}

# List of IPs to which data will be replicated (excluding the current server's own IP)
scan.scan_network()
ownip=scan.get_local_ip()

# Threaded function to handle client requests
def handle_client(client_socket, client_ip):
    try:
        # Receive the request from the client
        request = client_socket.recv(1024).decode("utf-8")
        print(f"Request received from {client_ip}: {request}")
        
        data = json.loads(request)
        operation = data.get('operation')
        key = data.get('key')
        value = data.get('value')

        if operation == 'store':
            kv_store.insert(key,value)
            response = f"Stored key: {key} with value: {value}"
            # Replicate data to two random replica servers
            replicate_to_other_servers(key, value)
        elif operation == 'update':
            if key in kv_store:
                kv_store.insert(key ,  value)
                response = f"Updated key: {key} with value: {value}"
                # Replicate update to random replica servers
            else:
                response = f"Key {key} not found!"
            update_to_other_servers(key, value)
        elif operation == 'delete':
            if key in kv_store.data:
                kv_store.delete(key)
                response = f"Deleted key: {key}"
                # Replicate delete to random replica servers
            else:
                response = f"Key {key} not found!"
            delete_from_replica_servers(key)
        elif operation == 'get':
            if key in kv_store.data:
                response = f"Key: {key}, Value: {kv_store.search(key)}"
            else:
                # Try fetching from replica servers
                response = fetch_from_replica_servers(key)
                if not response:
                    response = f"Key {key} not found!"
        else:
            response = "Invalid operation!"
    except Exception as e:
        response = f"Error processing request: {str(e)}"
    
    client_socket.send(response.encode("utf-8"))
    client_socket.close()

# Function to replicate data to two random replica servers
def replicate_to_other_servers(key, value):
    print("Replicating data to other servers...")
    selected_servers = random.sample(scan.getTotalActiveIps(), min(2, len(scan.getTotalActiveIps())))  # Pick two random servers
    print(f"Selected servers for replication: {selected_servers}")
    
    for ip in selected_servers:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, serv_port))
            request_data = {'operation': 'store', 'key': key, 'value': value}
            client_socket.send(json.dumps(request_data).encode("utf-8"))
            client_socket.close()
            print(f"Replicated to server {ip}")
        except Exception as e:
            print(f"Error replicating to {ip}: {str(e)}")

# Function to replicate delete to replica servers
def delete_from_replica_servers(key):
    for ip in scan.getTotalActiveIps():
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, serv_port))
            request_data = {'operation': 'delete', 'key': key}
            client_socket.send(json.dumps(request_data).encode("utf-8"))
            client_socket.close()
            print(f"Deleted from server {ip}")
        except Exception as e:
            print(f"Error deleting from {ip}: {str(e)}")

def update_to_other_servers(key,value):
    for ip in scan.getTotalActiveIps():
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, serv_port))
            request_data = {'operation': 'update', 'key': key,'value':value}
            dumped_data=json.dumps(request_data)
            client_socket.send(dumped_data.encode("utf-8"))
            client_socket.close()
            print(f"Updated on server {ip}")
        except Exception as e:
            print(f"Error updating from {ip}: {str(e)}")

# Function to fetch data from replica servers
def fetch_from_replica_servers(key):
    for ip in scan.getTotalActiveIps():
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, serv_port))
            request_data = {'operation': 'get', 'key': key}
            client_socket.send(json.dumps(request_data).encode("utf-8"))
            response = client_socket.recv(1024).decode("utf-8")
            client_socket.close()
            if "Key" not in response:  # If the key is found in the response
                return response
        except Exception as e:
            print(f"Error fetching from {ip}: {str(e)}")
    return None

# Function to start the server on a specific IP and port
def start_server_for_client(ip, port):
    global kv_store
    kv_store = dbstore.DataBase(file_path="data/" + ip + ":" + str(port) + ".json")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(5)
    print(f"Server started for client on {ip}:{port}")

    while True:
        client_socket, client_ip = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_ip)).start()

def handle_server(s_sock,s_ip):
    request = s_sock.recv(1024).decode("utf-8")
    print(f"Request received from {s_ip}: {request}")
    data = json.loads(request)
    operation = data.get('operation')
    key = data.get('key')
    value = data.get('value')
    if operation == 'store' or operation == 'update':
        kv_store.insert(key, value)
    elif operation == 'delete':
        kv_store.delete(key)
    elif operation == 'hello':
        print("New server added " , s_ip)
        scan.addActiveIp(s_ip[0])
        response = "added successfully"
        s_sock.send(response.encode("utf-8"))
    elif operation == 'get':
        if key in kv_store.data:
            response= kv_store.search(key)
            s_sock.send(response.encode("utf-8"))
        else:
            response = "Key not found"
            s_sock.send(response.encode("utf-8"))
    s_sock.close()
        

def start_server_socket(ip,port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(5)
    print(f"Server started on {ip}:{port}")
    while True:
        other_server_sock, other_serv_ip = server_socket.accept()
        print(other_serv_ip)
        threading.Thread(target=handle_server, args=(other_server_sock, other_serv_ip)).start()

# Example of running the server on multiple IPs
server_thread = threading.Thread(target=start_server_socket, args=(ownip, 9999))
server_thread.start()
start_server_for_client(ownip,port=cli_port)
