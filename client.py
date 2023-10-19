import sys
import socket

global_buffer = ""

DEBUG = False

if "-d" in sys.argv:
    DEBUG = True
    
class TerminalColors:
    ORANGE = '\033[38;5;214m'
    ENDC = '\033[0m'
    
def debug_print(msg):
    if DEBUG:
        print(f"[client.py] {msg}")
        
def sendMessage(sock, message):
    # Escape any dots and backslashes in the message
    message = message.replace("\\", "\\\\").replace(".", "\\.")
    sock.send(message.encode("ascii"))
    sock.send("\.\r\n".encode("ascii"))  # end of message indicator

def receiveMessage(sock):
    global global_buffer
    
    while "\.\r\n" not in global_buffer:
        data = sock.recv(1024).decode()
        global_buffer += data

    # Split the buffer at the first end-of-message indicator
    message, global_buffer = global_buffer.split("\.\r\n", 1)
    
    # Unescape any escaped dots and backslashes in the message
    message = message.replace("\\.", ".").replace("\\\\", "\\")
    
    return message

def main(serverName, serverPort, filename, signatureFile):
    
    messages = parseMessagesFromFile(filename)
    signatures = loadSignaturesFromFile(signatureFile)
    socketTCP = createTCPsocket(serverName, serverPort)

    try:
        # handshake
        debug_print(f"Sending HELLO handshake")
        sendMessage(socketTCP, "HELLO")

        response = receiveMessage(socketTCP)
        debug_print(response) if DEBUG else print(response)
        if response == "260 OK":
            
            # send messages
            for msg_index, msg in enumerate(messages):
                
                debug_print(f"Sending DATA command")
                sendMessage(socketTCP, "DATA")  
                
                debug_print(f"Sending message: {msg}")
                sendMessage(socketTCP, msg)   
  
                # check status
                status = receiveMessage(socketTCP)
                debug_print(status) if DEBUG else print(status)
                if status != "270 SIG":
                    print(f"[client.py] Error: Invalid response from server: {status}. expected '270 SIG'. Exiting")
                    sys.exit(1)
                
                # signatures pass/fail
                received_signature = receiveMessage(socketTCP)
                debug_print(received_signature) if DEBUG else print(received_signature)
                
                if received_signature == signatures[msg_index]:
                    debug_print(f"Sending PASS")
                    sendMessage(socketTCP, "PASS")
                else:
                    debug_print(f"Recieved invalid hash")
                    debug_print(f"Expected hash: {TerminalColors.ORANGE}{signatures[msg_index]}{TerminalColors.ENDC}")
                    debug_print(f"Sending FAIL")
                    sendMessage(socketTCP, "FAIL")

                response = receiveMessage(socketTCP)
                debug_print(response) if DEBUG else print (response)

                if response != "260 OK":
                    print(f"[client.py] Error: Invalid response after FAIL: {response} expected '260 OK'")
                    sys.exit(1)
                
            debug_print(f"Sending QUIT")
            sendMessage(socketTCP, "QUIT")
        else:
            print(f"[client.py] Connection error: Invalid handshake response: {response} Exiting")
            sys.exit(1)
            
    except Exception as e:
        print(f"[client.py] Error occurred: {e}")
    finally:
        socketTCP.close()
        
def createTCPsocket(serverName, serverPort):
    try:
        socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketTCP.connect((serverName, int(serverPort)))
    except socket.error as e:
        print(f"[client.py] Socket error: {e}")
        sys.exit(1)
        
    return socketTCP
        
def parseMessagesFromFile(fileName):
    try:
        message = open(fileName, "r")
    except FileNotFoundError:
        print(f"[client.py] Error: Unable to open message file '{fileName}'")
        sys.exit(1)

    # parse messages into array of byte strings
    messages = []
    line = message.readline().strip()  
    while line:
        length = int(line)  
        msg = message.read(length).strip()
        messages.append(msg)  
        line = message.readline().strip() 
    
    return messages

def loadSignaturesFromFile(fileName):
    try:
        signature = open(fileName, "r")
    except FileNotFoundError:
        print(f"[client.py] Error: Unable to open signature file '{fileName}'")
        sys.exit(1)

    signatures = []
    while True:
        line = signature.readline().strip()  # strip newline characters
        if not line:
            break
        signatures.append(line)
        
    return signatures

if __name__ == "__main__":
    if len(sys.argv) != 5:
        if (len(sys.argv) != 6) and ("-d" not in sys.argv): # extra condition for debug
            debug_print("Usage: python client.py <serverName> <serverPort> <filename> <signatureFile> [-d]")
            sys.exit(1)
    debug_print(f"Usage: serverName: {sys.argv[1]} serverPort: {sys.argv[2]} fileName: {sys.argv[3]} signatureFile: {sys.argv[4]}")
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
