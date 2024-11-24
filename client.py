import socket
import json
# Function to interact with the server


def get_local_ip():
    # Get the local IP address to determine the network
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

def send_request(operation, key, value=None, ip="192.168.1.115", port=12345):

    try:
        # Create a socket connection to the server
        ip=get_local_ip()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))

        # Prepare the request data
        request_data = {'operation': operation, 'key': key, 'value': value}
        client_socket.send(json.dumps(request_data).encode("utf-8"))

        # Receive the response from the server
        response = client_socket.recv(1024).decode("utf-8")
        print(f"Response from server: {response}")
        
        # Close the socket connection
        client_socket.close()
    except Exception as e:
        print(f"Error sending request: {str(e)}")

# Main function to interact with the user
def main():
    while True:
        # Prompt the user to choose an operation
        print("\nChoose an operation:")
        print("1. Store")
        print("2. Update")
        print("3. Delete")
        print("4. Get")
        print("5. Exit")
        
        operation_choice = input("Enter your choice (1/2/3/4/5): ").strip()
        
        if operation_choice == '5':
            print("Exiting...")
            break
        
        key = input("Enter the key: ").strip()

        if operation_choice == '1' or operation_choice == '2':  # Store or Update requires a value
            value = input("Enter the value: ").strip()
        else:
            value = None

        if operation_choice == '1':  # Store operation
            send_request('store', key, value)
        elif operation_choice == '2':  # Update operation
            send_request('update', key, value)
        elif operation_choice == '3':  # Delete operation
            send_request('delete', key)
        elif operation_choice == '4':  # Get operation
            send_request('get', key)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
