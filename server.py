import sys
import socket
import hashlib

DEBUG = False

if "-d" in sys.argv:
    DEBUG = True

def debug_print(msg):
    if DEBUG:
        print(f"[server.py] {msg}")

def main(listenPort, fileName):
    
    # populate keys array
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

    # create TCP socket
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # for testing, allows to reuse socket if it wasnt properly closed
        serverSocket.bind(("localhost", int(listenPort)))
    except socket.error as e:
        print(f"[server.py] Socket error: {e}")
        sys.exit(1)

    # wait for client connection
    serverSocket.listen(1)
    debug_print("Server is listening for connections...")

    # connect to client
    client_socket, client_address = serverSocket.accept()
    debug_print(f"Connection from {client_address}")

    try:
        # check for HELLO handshake
        handshake = client_socket.recv(1024)
        if handshake.decode("ascii") != "HELLO":
            print("[server.py] Error: Invalid handshake")
            serverSocket.close()
            sys.exit(1)
        debug_print("Recieved HELLO")

        client_socket.sendall("260 OK".encode("ascii"))

        # message loop
        debug_print("Entering message loop")
        key_index = 0
        while True:
            
            data = client_socket.recv(1024).decode("ascii")
            if data == "DATA":
                debug_print(f"Received data command from {client_address}")
                
                # Start a new SHA 256 hash
                hasher = hashlib.sha256()
                
                # EXAMPLE
                # hasher.update("Ethernet cables are like the roads of the Internet, carrying data traffic to its destinations.".encode('ascii'))
                # hasher.update("186e3bdc82d21a2682ee8e82eb5fe868".encode('ascii'))
                # signature = hasher.hexdigest()
                # debug_print(f"Manual first signature: {signature}")
                
                # recieve a message
                while True:
                    line = client_socket.recv(1024).decode("ascii")
                    debug_print(f"Received line: {line}")
                    
                    # Check for the escaped end-of-message code
                    if (not line) or (line  == "\.\r\n") or (line.endswith("\.\r\n")):
                        break
                    
                    # Unescape the line
                    unescaped_line = line.replace("\\.", ".").replace("\\\\", "\\")
                    
                    hasher.update(unescaped_line.encode('ascii'))
                
                # Add the key to the hash and finish the hash
                hasher.update(keys[key_index].encode('ascii'))
                signature = hasher.hexdigest()
                key_index += 1
                
                debug_print(f"Computed Signature: {signature}")
                
                debug_print("Sending 270 SIG")
                client_socket.sendall("270 SIG".encode("ascii"))  # Send the 270 SIG response
                debug_print(f"Sending computed signature: {signature}")
                client_socket.sendall(signature.encode("ascii"))  # Send the computed signature

                debug_print(f"Computed Signature: {signature}")

                # Send the 270 SIG status code back to the client on one line
                debug_print("Sending 270 SIG")
                client_socket.sendall("270 SIG".encode("ascii"))

                # Send a hexadecimal string value on the TCP socket of the signature on one line
                debug_print(f"Sending computed signature: {signature}")
                client_socket.sendall(signature.encode("ascii"))

                # Read a line from the socket
                response = client_socket.recv(1024).decode("ascii")
                if response == "PASS":
                    debug_print("Received PASS command from client")
                elif response == "FAIL":
                    debug_print("Received FAIL command from client")
                    client_socket.sendall("260 OK".encode("ascii"))  # Send the 260 OK response
                else:
                    print("[server.py] Error: Unexpected response from client")
                    client_socket.close()
                    sys.exit(1)

            elif data == "QUIT":
                debug_print("Client initiated a quit. Closing connection.")
                break
            else:
                print("[server.py] Error: Invalid command received")
                client_socket.close()
                sys.exit(1)
             
        debug_print("Exiting message loop")
            
    except Exception as e:
        print(f"[server.py] Error occurred: {e}")
    finally:
        serverSocket.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
         if (len(sys.argv) != 4) and ("-d" not in sys.argv): # extra condition for debug
            debug_print("Usage: python server.py <listenPort> <fileName> [-d]")
            sys.exit(1)
    debug_print(f"Usage: port: {sys.argv[1]} fileName: {sys.argv[2]}")
    main(sys.argv[1], sys.argv[2])
