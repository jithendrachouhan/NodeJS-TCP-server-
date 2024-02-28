import socket

identifyByte = 126
protoV = 1
authCode = [10,10,10,10,10,10,10,10,10,10]

reqData = [];

resAccordingToIDs = {
    "1,0": [[0x81,0x0], lambda: registrationBody()],
    "1,2": [[0x0,0x1], lambda: generalBody()]
}

def responseData():
    completeData = [];
    if (','.join(map(str, [reqData[1], reqData[2]]))) in resAccordingToIDs:
        resHeader = responseHeader()
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

def responseHeader():
    resHeader = []
    resHeader.extend(resAccordingToIDs.get(','.join(map(str, [reqData[1], reqData[2]])))[0])  # Fetch from dict using get method
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

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('192.168.0.104', 8766)
server_socket.bind(server_address)

server_socket.listen(5)

print('Server is listening on', server_address)

while True:
    connection, client_address = server_socket.accept()

    try:
        print('Client connected:', client_address)

        # Receive data from the client
        while True:
            reqData.clear()
            data = connection.recv(1024)
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

            connection.sendall(response_data)

    finally:
        # Clean up the connection
        print("Connection closed");
        connection.close()
    







