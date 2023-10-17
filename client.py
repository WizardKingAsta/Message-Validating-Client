import sys
import socket
def main(serverName, serverPort, filename, signatureFile):
    message = open(filename, "r")  #open file
    signatures = []
    messages = []
    line = message.readline()
    while(line != ""):  #loop through message file
        line = message.readline()
        arr = line.encode("ascii")  #convert line into bytes
        messages.append(arr)   #add to byte array
        line = message.readline()

    signature = open(signatureFile,"r") #open signature file
    line = signature.readline()
    while(line != ""): #loop through all signatures in file
        signatures.append(line)
        line = signature.readline()
    socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create TCP socket
    socketTCP.connect((serverName, int(serverPort)))
    handshake = "HELLO"
    socketTCP.send(handshake.encode("ascii")) #send handshake
    handshakeRecv = socketTCP.recv(1024)
    if(handshakeRecv.decode("ascii") == "260 OK"): #checks for proper response
        counter = 0
        for msg in messages:
            counter+=1
            socketTCP.send("DATA".encode("ascii")) # send data over TCP socket
            socketTCP.send(str(msg).encode("ascii")) # send message over socket
    
            if(socketTCP.recv(1024).decode("ascii") != "270 SIG"):
                print("ERROR")
                quit()
            if(socketTCP.recv(1024).decode("ascii") == signatures[counter]):
                socketTCP.send("PASS".encode("ascii"))
            else:
                socketTCP.send("FAIL".encode("ascii"))
                if(socketTCP.recv(1024).decode("ascii") != "260 OK"):
                    print("ERROR")
                    quit()
            counter+=1
        socketTCP.send("QUIT".encode("ascii"))
        socketTCP.close()
    else:
        print("Connection ERROR")
        quit()


if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4] )
