import socket #For the use of networking capabilities
import pickle #To send files/other data over socket 

class Server():
    def __init__(self, hostname = 'localhost' ,port= 1234):
        '''Load the server object'''
        self.port = port
        self.hostname = hostname
        self.connected = False
        self.start()
    
    def start(self):
        '''Start the server object'''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname,self.port))
        print("Server started:\nIP:", self.hostname, "\nPort:", self.port)

    def listen(self):
        '''Listen to the socket'''
        self.socket.listen(5)
        print("Listening on port:",self.port)
        while(True):
            if(not self.connected):
                self.client,self.addr = self.socket.accept()
                print(f"Client {self.addr} has connected")
                self.connected = True
            else:
                data = self.listen_client(self.client,self.addr)
                self.send(data)
    
    def send(self,message):
        """Send a  message to the client"""
        data = pickle.dumps(message)
        try:
            self.client.send(data)
        except:
            print("Conection Closed")
            self.client.close()
            self.connected = False
            self.client = None
            self.addr = None

    def listen_client(self,client, addr):
        '''Separate function to listen to the client on a different process'''
        try:
            data = pickle.loads(self.client.recv(1024))
            return data
        except Exception as exp:
            return "No data received"

    def close(self):
        '''Closes the connection to the client and remove client from the connected client list'''
        self.client.close()

    def __del__(self):
        """Destructor"""
        self.close()
        super().__del__()

def main():
    '''The main function for the sockets server'''
    s = Server('localhost',port = 1234)
    s.listen()


if(__name__ == '__main__'):
    '''If this file is run as the main file, run this server'''
    main()
