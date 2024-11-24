import socket
import json
import sys


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

def send_request(operation, key, value=None, ip="192.168.1.115", port=12345):

    try:
        ip=get_local_ip()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        request_data = {'operation': operation, 'key': key, 'value': value}
        client_socket.send(json.dumps(request_data).encode("utf-8"))
        response = client_socket.recv(1024).decode("utf-8")
        print(f"Response from server: {response}")
        client_socket.close()
    except Exception as e:
        print(f"Error sending request: {str(e)}")

def load_test(test_file):
    try:
        with open(test_file, 'r') as file:
            test_operations = json.load(file)
        
        for operation_data in test_operations:
            operation = operation_data.get("operation")
            key = operation_data.get("key")
            value = operation_data.get("value", None)

            if operation == "store":
                print(f"Performing 'store' operation for key: {key}, value: {value}")
                send_request('store', key, value)
            elif operation == "update":
                print(f"Performing 'update' operation for key: {key}, value: {value}")
                send_request('update', key, value)
            elif operation == "get":
                print(f"Performing 'get' operation for key: {key}")
                send_request('get', key)
            elif operation == "delete":
                print(f"Performing 'delete' operation for key: {key}")
                send_request('delete', key)
            else:
                print(f"Unknown operation: {operation}")
    except Exception as e:
            print(f"Error reading test file: {str(e)}")
  
  
if __name__ == "__main__":
    load_test(test_file=sys.argv[1])
