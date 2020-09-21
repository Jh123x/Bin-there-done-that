import cv2
import socket
import pickle

class Client():
    def __init__(self,ip,port):
        """Initialise the client class"""
        self.ip = ip
        self.connected = False
        self.port = port
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()
        
    def connect(self):
        """Connect to the target ip and port"""
        try:
            self.soc.connect((self.ip,self.port))
            self.connected = True
            print("Connected")
        except:
            print(f"Connection failed")

    def receive(self, bufferSize = 1024):
        """Receive the data from the server"""
        data = pickle.loads(self.soc.recv(bufferSize))
        return data

    def send(self, msg):
        """Sends data over"""
        self.soc.send(pickle.dumps(msg))
    
    def __del__(self):
        self.soc.close()
        super().__del__()


def main():
    """Main function"""

    #Open camera
    cap = cv2.VideoCapture(0)

    #Get the port and the ip address
    client = Client("192.168.1.47",1234)

    while True:
        frame = read(cap)
        client.send(frame)


if __name__ == "__main__":
    main()
