import sys
import socket

DEBUG = False

if "-d" in sys.argv:
    DEBUG = True

def debug_print(msg):
    if DEBUG:
        print(f"[client.py] {msg}")

def main(serverName, serverPort, filename, signatureFile):
    
    # parse message file to byte array
    try:
        message = open(filename, "r")
    except FileNotFoundError:
        print(f"[client.py] Error: Unable to open message file '{filename}'")
        sys.exit(1)

    # parse messages into array of byte strings
    messages = []
    line = message.readline().strip()  
    while line:
        length = int(line)  
        msg = message.read(length)  
        messages.append(msg.encode("ascii"))  
        line = message.readline().strip() 

    # parse signatures into array
    try:
        signature = open(signatureFile, "r")
    except FileNotFoundError:
        print(f"[client.py] Error: Unable to open signature file '{signatureFile}'")
        sys.exit(1)

    signatures = []
    while True:
        line = signature.readline().strip()  # strip newline characters
        if not line:
            break
        signatures.append(line)

    # create TCP socket
    try:
        socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketTCP.connect((serverName, int(serverPort)))
    except socket.error as e:
        print(f"[client.py] Socket error: {e}")
        sys.exit(1)

    try:
        # send handshake
        handshake = "HELLO"
        debug_print(f"Sending HELLO handshake")
        socketTCP.send(handshake.encode("ascii"))
        handshakeRecv = socketTCP.recv(1024)
        if handshakeRecv.decode("ascii") == "260 OK":
            debug_print(f"Recieved 260 OK")
            
            # send messages
            counter = 0
            for msg_index, msg in enumerate(messages):
                counter += 1
                debug_print(f"Sending DATA command")
                socketTCP.send("DATA".encode("ascii"))  
                
                debug_print(f"Sending message: {msg.decode('ascii')}")
                socketTCP.send(msg)
                
                debug_print(f"Sending end-of-message indicator")
                socketTCP.send("\.\r\n".encode("ascii"))  # send the end of message indicator
  
                # check status
                if socketTCP.recv(1024).decode("ascii") != "270 SIG":
                    print("[client.py] Error: Invalid response from server, expected '270 SIG'. Exiting")
                    sys.exit(1)
                debug_print(f"Recieved 270 SIG")
                
                # signatures pass/fail
                received_signature = socketTCP.recv(1024).decode("ascii")
                debug_print(f"Received Signature: {received_signature}")
                debug_print(f"Expected Signature: {signatures[msg_index]}")
                if received_signature == signatures[msg_index]:
                    debug_print(f"Recieved valid signature")
                    debug_print(f"Sending PASS")
                    socketTCP.send("PASS".encode("ascii"))
                else:
                    debug_print(f"Recieved invalid signature")
                    debug_print(f"Sending FAIL")
                    socketTCP.send("FAIL".encode("ascii"))
                    if socketTCP.recv(1024).decode("ascii") != "260 OK":
                        print("[client.py] Error: Invalid response after FAIL, expected '260 OK'")
                        sys.exit(1)
                    debug_print(f"Recieved 260 OK") 
                        
                counter += 1
                
            debug_print(f"Sending QUIT")
            socketTCP.send("QUIT".encode("ascii"))
        else:
            print("[client.py] Connection error: Invalid handshake response. Exiting")
            sys.exit(1)
            
    except Exception as e:
        print(f"[client.py] Error occurred: {e}")
    finally:
        socketTCP.close()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        if (len(sys.argv) != 6) and ("-d" not in sys.argv): # extra condition for debug
            debug_print("Usage: python client.py <serverName> <serverPort> <filename> <signatureFile> [-d]")
            sys.exit(1)
    debug_print(f"Usage: serverName: {sys.argv[1]} serverPort: {sys.argv[2]} fileName: {sys.argv[3]} signatureFile: {sys.argv[4]}")
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
