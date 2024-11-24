from scapy.all import ARP, Ether, srp
import json
import socket
from threading import Thread
total_active_ips=[]
def getTotalActiveIps():
    return total_active_ips
def addActiveIp(ip):
    total_active_ips.append(ip)
def get_local_ip():
    # Get the local IP address to determine the network
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

def connectNode(ip):
    port = 9999
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        request_data = {'operation': 'hello'}
        s.send(json.dumps(request_data).encode("utf-8"))
        response = s.recv(1024).decode("utf-8")
        print(f"Ack from server: {response}")
        if ip not in total_active_ips:
            total_active_ips.append(ip)
    except Exception as e:
        pass
        #print(f"Error sending request: {str(e)}")
    s.close()
    
def scan_network():
    
    # Get the local IP and calculate the network prefix
    local_ip = get_local_ip()
    network_prefix = local_ip.rsplit('.', 1)[0]
    print(f"Scanning network: {network_prefix}")
    for i in range(1 , 254):
        ip = network_prefix + "." + str(i)
        print(ip)
        Thread(target=connectNode, args=(ip,)).start()



