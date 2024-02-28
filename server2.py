import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO

identifyByte = 126
protoV = 1
authCode = [10,10,10,10,10,10,10,10,10,10]

liveFeedServerIP = [0x31, 0x30, 0x36, 0x2e, 0x35, 0x31, 0x2e, 0x30, 0x2e, 0x36, 0x30]; #106.51.0.60 converted to hex
liveFeedServerPort = [0x1f, 0x40] #8000 converted to hex

tcp_connections = {}  # Dictionary to store TCP connections and their client identifiers
tcp_client_counter = 0  # Counter to assign unique client identifiers

reqData = [];

resAccordingToIDs = {
    "1,0": [[0x81,0x0], lambda: registrationBody()],
    "1,2": [[0x0,0x1], lambda: generalBody()],              # Auth Response 
    "0,1": [[0x0,0x1], lambda: generalBody()],              # HeartBeat Response 
    "2,0": [[0x0,0x1], lambda: generalBody()],              
    "7,4": [[0x0,0x1], lambda: generalBody()], 
    "7,2": [[0x0,0x1], lambda: generalBody()], 

}

def responseData():
    completeData = [];
    if (','.join(map(str, [reqData[1], reqData[2]]))) in resAccordingToIDs:
        resHeader = responseHeader(resAccordingToIDs.get(','.join(map(str, [reqData[1], reqData[2]])))[0])
        resBody = resAccordingToIDs.get(','.join(map(str, [reqData[1], reqData[2]])))[1]()
        resHeader[3] = len(resBody)  # Use len(resBody) to get the length of the list
        checkCodeVal = checkCode(resHeader + resBody)
        completeData = completeMessage(resHeader, resBody, checkCodeVal)
    return bytes(completeData)

def checkCode(arr):
    data = 0
    for i in arr:
        data ^= i
    return data


def completeMessage(resHeader, resBody, checkCode):
    completeData = []
    completeData.append(identifyByte)
    completeData.extend(resHeader + resBody + [checkCode])  # Use append and extend method to merge lists
    completeData.append(identifyByte)
    return completeData

def responseHeader(messageID):
    resHeader = []
    resHeader.extend(messageID)  # Fetch from dict using get method
    resHeader.extend([reqData[3], reqData[4], protoV])  # properties and protocol version
    resHeader.extend(extractTerminalNumber())  # Push extracted terminal number
    resHeader.extend([reqData[16], reqData[17]])
    return resHeader

def extractTerminalNumber():
    terminalNumber = []
    for i in range(6, 16):  
        terminalNumber.append(reqData[i])
    return terminalNumber

def registrationBody(): 
    resBody = []
    resBody.extend([reqData[16], reqData[17], 0])  # serial number and result
    resBody.extend(authCode) 
    return resBody

def generalBody(): 
    resBody = []
    resBody.extend([reqData[16], reqData[17]])  # serial number
    resBody.extend([reqData[1], reqData[2], 0])  # messageID and success result 
    return resBody

def completeLiveReq():
    completeliveData = []
    resHeader = responseHeader([0x91,0x01])
    resBody = getLiveRequestBody()
    resHeader[3] = len(resBody) 
    checkCodeVal = checkCode(resHeader + resBody)
    completeliveData = completeMessage(resHeader, resBody, checkCodeVal)
    return completeliveData

def getLiveRequestBody():
    liveReqData = []
    liveReqData.extend(len(liveFeedServerIP))
    liveReqData.extend(liveFeedServerIP)
    liveReqData.extend(liveFeedServerPort)  #Tcp port
    liveReqData.extend(liveFeedServerPort)  #Udp port
    liveReqData.extend(1)  # channel- 1
    liveReqData.extend(0)  # select audio and video
    liveReqData.extend(1)  # sub stream 
    return liveReqData



class TCPRequestHandler(threading.Thread):
    def __init__(self, connection, client_address, client_id):
        threading.Thread.__init__(self)
        self.connection = connection
        self.client_address = client_address
        self.client_id = client_id

    def run(self):
        while True:
            reqData.clear()
            data = self.connection.recv(1024)
            if not data:
                break
            hex_data = " ".join("{:02x}".format(byte) for byte in data)
            print("Received:", hex_data)

            for x in data:
                reqData.append(x);

            # Process the received data and send the response back to the client
            response_data = responseData()
            hex_response_data = " ".join("{:02x}".format(byte) for byte in response_data)
            print("Response:", hex_response_data)
            self.connection.sendall(response_data)
        self.connection.close()


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode("utf-8")
        handle_http_request(body)
        self.send_response(200)
        self.end_headers()

def handle_http_request(data):
    # Process HTTP request data
    # Send the received data to the first TCP client
    if tcp_connections:
        if data == "live feed":
            client_id, tcp_conn = next(iter(tcp_connections.items()))
            liveRequestData = completeLiveReq()
            tcp_conn.sendall(data)
            response = tcp_conn.recv(1024)
            print(f"Response from TCP client: {response.decode()}")
        
def start_tcp_server(host, port):
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind((host, port))
    tcp_server_socket.listen(5)
    print('TCP Server is listening on', (host, port))
    
    while True:
        connection, client_address = tcp_server_socket.accept()
        print('Client connected:', client_address)
        global tcp_client_counter
        tcp_client_counter += 1
        tcp_connections[tcp_client_counter] = connection
        tcp_thread = TCPRequestHandler(connection, client_address, tcp_client_counter)
        tcp_thread.start()

def start_http_server(host, port):
    http_server = HTTPServer((host, port), HTTPRequestHandler)
    print('HTTP Server is listening on', (host, port))
    http_server.serve_forever()

if __name__ == "__main__":
    tcp_server_thread = threading.Thread(target=start_tcp_server, args=('192.168.0.104', 8000))
    tcp_server_thread.start()

    http_server_thread = threading.Thread(target=start_http_server, args=('192.168.0.104', 8080))
    http_server_thread.start()
