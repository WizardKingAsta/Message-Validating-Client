import sys
import socket
def main(listenPort, fileName):
    keyFile = open(fileName, "r")
    keys= []
    line = keyFile.readline()
    while(line != ""):  #loops through the keys
        keys.append(line) #adds each key to eh array of keys
        line = keyFile.readline()
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create TCP socket
    serverSocket.bind(("localhost",int(listenPort)))
    serverSocket.listen(1) #wait for client connection
    client_socket, client_address = serverSocket.accept() #connect to client
    handshake = client_socket.recv(1024) #check for HELLO handshake
    if(handshake.decode("ascii") != "HELLO"):
        print("ERROR") #error and quit if wrong handshake
        serverSocket.close()
        quit()
    client_socket.sendall("260 OK".encode("ascii")) 
    while(True): #loop through to recieve messaged 
        data = client_socket.recv(1024).decode("ascii")
        if(data == "DATA"):
            data = client_socket.recv(1024).decode("ascii")
            #HERE WE NEED TO CREATE NEW HASH AND COMMUNICATE WITH CLIENT ABT IT
        elif(data == "QUIT"):
            break
    

if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2])
