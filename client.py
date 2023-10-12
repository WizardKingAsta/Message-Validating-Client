import sys
import socket
def main(serverName, serverPort, filename, signatureFile):
    message = open(filename, "r")  #open file
    signatures = []
    messages = []
    line = message.readline()
    while(line != ""):  #loop through message file
        arr = list(line.encode("ascii"))  #convert line into bytes
        messages.append(arr)   #add to byte array
        line = message.readline()

    signature = open(signatureFile,"r") #open signature file
    line = signature.readline()
    while(line != ""): #loop through all signatures in file
        signatures.append(line)
        line = signature.readline()
    socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create TCP socket
    socketTCP.bind(serverName, serverPort)
    handshake = "HELLO"
    socketTCP.send(handshake.encode()) #send handshake
    handshakeRecv = socketTCP.recv(1024)
    if(handshakeRecv.decode() == "260 OK"): #checks for proper response
        counter = 0
        for msg in messages:
            counter+=1
            socketTCP.send("DATA".encode("ascii")) # send data over TCP socket
            socketTCP.send(msg) # send message over socket
            if(socketTCP.recv(1024).decode != "270 SIG"):
                print("ERROR")
                quit()
            if(socketTCP.recv(1024).decode == signatures[counter]):
                socket.send("PASS".encode())
            else:
                socketTCP.send("FAIL".encode())
                if(socketTCP.recv(1024).decode() != "260 OK"):
                    print("ERROR")
                    quit()
            counter+=1
        socketTCP.send("QUIT".encode())
        socketTCP.close()
    else:
        print("Connection ERROR")
        quit()


if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4] )