import sys
import socket
import hashlib

def main(listenPort, fileName):
    
    keys = loadKeysFromFile(fileName)
    
    serverSocket = createTPCsocket(listenPort)
    serverSocket.listen(1)
    debug_print("Server is listening for connections...")

    client_socket, client_address = serverSocket.accept()
    debug_print(f"Connection from {client_address}")

    try:
        # HELLO handshake
        message = receiveMessage(client_socket)
        debug_print(message) if DEBUG else print(message)
        if message != "HELLO":
            print("[server.py] Error: Invalid handshake")
            serverSocket.close()
            sys.exit(1)

        debug_print("Sending 260 OK")
        sendMessage(client_socket, "260 OK")

        failedFlag, failedCounter, = False, 0
        
        # message loop
        key_index = 0
        while True:
            
            message = receiveMessage(client_socket)
            debug_print(message) if DEBUG else print(message)
            
            if message == "DATA":
                message = receiveMessage(client_socket)
                debug_print(message) if DEBUG else print(message)
                
                # generate sha256 hash
                hasher = hashlib.sha256()
                
                debug_print(f"Adding message to hash: {message}")
                hasher.update(message.encode("ascii"))
                
                debug_print(f"Adding key to hash: {keys[key_index]}")
                hasher.update(keys[key_index].encode('ascii'))
                
                signature = hasher.hexdigest()
                key_index += 1
                
                # Compare hash with client
                debug_print("Sending 270 SIG")
                sendMessage(client_socket, "270 SIG")
                
                debug_print(f"Sending hash: {TerminalColors.WARNING}{signature}{TerminalColors.ENDC}")
                sendMessage(client_socket, signature)
 
                response = receiveMessage(client_socket)
                debug_print(response) if DEBUG else print(response)

                if response == "PASS":
                    debug_print(f"Received {TerminalColors.OKGREEN}PASS{TerminalColors.ENDC}")
                elif response == "FAIL":
                    debug_print(f"Received {TerminalColors.FAIL}FAIL{TerminalColors.ENDC}. Sending 260 OK")
                    failedFlag = True
                    failedCounter += 1
                else:
                    print("[server.py] Error: Unexpected response from client")
                    client_socket.close()
                    sys.exit(1)

                sendMessage(client_socket, "260 OK")
                
            elif message == "QUIT":
                debug_print("Client initiated a quit. Closing connection.")
                client_socket.close()
                break
            else:
                print(f"[server.py] Error: Invalid command received: {message}. Exiting")
                client_socket.close()
                sys.exit(1)
                
        if DEBUG and failedFlag:
            print(f"\n{TerminalColors.FAIL}Failed{TerminalColors.ENDC}. {failedCounter}/{len(keys)} test cases failed\n")
        elif DEBUG and not failedFlag:
            print(f"\n{TerminalColors.OKGREEN}Succeded{TerminalColors.ENDC}. {len(keys)}/{len(keys)} messages passed\n")
            
    except Exception as e:
        print(f"[server.py] Error occurred: {e}")
    finally:
        serverSocket.close()
        
def createTPCsocket(listenPort):
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # for testing, allows to reuse socket if it wasnt properly closed
        if DEBUG:
            serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
            
        serverSocket.bind(("localhost", int(listenPort)))
        return serverSocket
    except socket.error as e:
        print(f"[server.py] Socket error: {e}")
        sys.exit(1)
        
global_buffer = ""
         
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
        
def loadKeysFromFile(fileName):
    try:
        keyFile = open(fileName, "r")
    except FileNotFoundError:
        print(f"[server.py] Error: Unable to open key file '{fileName}'")
        sys.exit(1)

    keys = []
    while True: 
        line = keyFile.readline().strip()  # Strip newline characters
        if not line:
            break
        keys.append(line)
        
    return keys

### DEBUG ###
DEBUG = False

if "-d" in sys.argv:
    DEBUG = True
    
class TerminalColors:  
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def debug_print(msg):
    if DEBUG:
        print(f"[server.py] {msg}")
### DEBUG ###

if __name__ == "__main__":
    if len(sys.argv) != 3:
         if (len(sys.argv) != 4) and ("-d" not in sys.argv): # extra condition for debug
            debug_print("Usage: python server.py <listenPort> <fileName> [-d]")
            sys.exit(1)
    debug_print(f"Usage: port: {sys.argv[1]} fileName: {sys.argv[2]}")
    main(sys.argv[1], sys.argv[2])
