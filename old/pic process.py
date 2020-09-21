import cv2
import socket #For the use of networking capabilities
import pickle #To send files/other data over socket 
import multiprocessing as mp
import numpy as np

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
        '''Listen to the socket and allocate the client to a separate thread'''
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

    def close(self,client):
        '''Closes the connection to the client and remove client from the connected client list'''
        client.close()
        self.clients.remove(client)

    def __del__(self):
        """Destructor"""
        self.close()
        super().__del__()


class VideoC():
    def __init__(self, queue):
        '''Initialiser for the capture'''
        self.prev = []
        self.time = 0
        self.queue = queue
        self.stopped = False

    def read(self):
        '''Get the next frame in the queue'''
        if(self.queue.qsize() > 0):
            return self.queue.get()
        else:
            return False,[]

    def process(self, frame):
        '''Process the frame'''

        #If there is a previous frame captured
        if len(self.prev) > 0:

            #Gray previous frame
            pframe = cv2.cvtColor(self.prev,cv2.COLOR_BGR2GRAY)

            #Gray current frame
            cframe = cv2.cvtColor(frame.copy(),cv2.COLOR_BGR2GRAY)

            #Getting the difference in the frame in terms of gray scale
            frame = cv2.absdiff(pframe,cframe)

            #Getting the FPS of the frame
            ctime = time.time()

            #If fps is undefined
            fps = str(round(1/(ctime- self.time),2))

            #Place the text within the frame
            frame = cv2.putText(frame, fps, (0,15), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA) 

            #Setting the prev to current time
            self.time = ctime
            
            #Return the frame
            return frame

        else:
            #If there is no previous frame, there is no need to process it
            self.time = time.time()
            return frame

    def display(self):
        '''Display what is being captured'''

        #Loop to display the frames 1 by 1
        while True:
            
            #Reading the next frame from the input
            ret,frame = self.read()

            #Check if the btn q is pressed (Quit if the button us pressed)
            if cv2.waitKey(1) & 0xFF == ord('q'): #The 0xFF is needed when dealing with 64 bit operating system
                break

            #If there is an image that is captured (Ret will return true if there is input and False if otherwise)
            if ret:
                #Flip the frame to make it the correct side
                frame = np.fliplr(frame)

                #Do modifications to the frame here/ Other operations
                nframe = self.process(frame)

                #Show the original image
                cv2.imshow('Video', frame)

                #Show the Img delta
                cv2.imshow('Delta', nframe)

                #Set the current frame as prev frame
                self.prev = frame

        #To close the camera properly
        self.quit()
        
    def quit(self):
        '''Release all of the cams which are active'''
        
        #Stop the thread
        self.stopped = True

        #Close all of the windows
        cv2.destroyAllWindows()

    def __del__(self):
        '''Destructor for the VideoC object'''
        self.quit()
        super().__del__()


def get_frames(queue, cap, serv):
    """Getting the frame from the rasp pi"""
    pass


def main():
    """Main function for the code"""

    #Initialise the server object
    s = Server("localhost",1234)

    #Create the queue to be executed in another thread
    queue = mp.Manager.Queue(120)

    #Create the opencv object
    cap = VideoC(queue)

