import sys
import socket
def main(listenPort, fileName):
    keyFile = open(fileName, "r")
    keys= []
    line = keyFile.readline()
    while(line != ""):  #loops through the keys
        keys.append(line) #adds each key to eh array of keys
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create TCP socket
    serverSocket.bind(listenPort)
    handshake = serverSocket.recv(1024)
    if(handshake != "HELLO"):
        print("ERROR")
        serverSocket.close()
        quit()
    

if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2])