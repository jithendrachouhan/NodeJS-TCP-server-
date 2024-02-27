const identifyByte = 126;
const protoV = 1;
const authCode = [10,10,10,10,10,10,10,10,10,10];

const reqData = [126,1,0,64,100,1,0,0,0,0,85,128,99,82,133,7,1,230,
    0,0,0,0,48,48,48,48,48,48,56,49,56,57,57,83,50,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,53,53,56,48,54,51,53,50,
    56,53,48,55,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,245,126
];

const messageIDs = new Map([
    ["Hello", [0,1]]
]);

function messageReceived() {
    responseData(reqData);
}

function responseData() {
    const resHeader = responseHeader(reqData);
    const resBody = responseBody(reqData);
    resHeader[3] = resBody.length; // Use resBody.length to get the length of the array
    const checkCodeVal = checkCode();
    const completeData = completeMessage(resHeader, resBody, checkCodeVal);
    sendDataToDevice(completeData);
}

function sendDataToDevice(completeData) {
    completeData.forEach((x) => console.log(x));
}

function completeMessage(resHeader, resBody, checkCode) {
    const completeData = [];
    completeData.push(identifyByte);
    completeData.push(...resHeader, ...resBody, checkCode); // Use push and spread operator to merge arrays
    completeData.push(identifyByte);
    return completeData;
}

/////// Creation of Header //////////

function responseHeader() {
    // logic to check the response data;
    const resHeader = [];
    resHeader.push(...messageIDs.get("Hello")); // Fetch from Map using get method
    resHeader.push(reqData[0], reqData[0], protoV); // properties and protocol version
    resHeader.push(...extractTerminalNumber(reqData)); // Push extracted terminal number
    resHeader.push(reqData[0], reqData[0]);
    return resHeader;
}

function extractTerminalNumber(reqData) { // Pass reqData to the function
    const terminalNumber = [];
    for (let i = 6; i <= 15; i++)  
        terminalNumber.push(reqData[i]);
    return terminalNumber;
}

/////// Creation of Body //////////

function responseBody(reqData) { // Pass reqData to the function
    // This should be dependent on the message ID 
    const resBody = [];
    resBody.push(reqData[0], reqData[1], 0); // serial number and result
    resBody.push(...authCode); 
    return resBody;
}

messageReceived();
