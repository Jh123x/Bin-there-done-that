import cv2 #Computer vision capabilities
import time #Add time delay
import multiprocessing #Process frames in another thread
import numpy as np #numpy functions
import socket #For the use of networking capabilities

class Server():
    def __init__(self, hostname = 'localhost' ,port = 1234):
        '''Load the server object'''
        self.port = port
        self.hostname = hostname
        self.connected = False
        self.client = None

        #Bind the socket go the ip
        self.start()
    
    def start(self):
        '''Start the server object'''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname,self.port))
        print("Server started:\nIP:", self.hostname, "\nPort:", self.port)

    def listen(self):
        '''Listen to the socket'''
        self.socket.listen(5)
        while(True):
            if(not self.connected):
                self.client,self.addr = self.socket.accept()
                print(f"Client {self.addr} has connected")
                self.connected = True
            else:
                return
    
    def send(self,message):
        """Send a  message to the client"""
        print(f"{str(time.ctime(int(time.time())))}: {message}")
        data = "".join(str(message) + "\n").encode()
        try:
            self.client.send(data)
        except:
            print("Client not available")
            print("Conection Closed")
            self.client.close()
            self.connected = False
            self.client = None
            self.addr = None
            return True

    def close(self):
        '''Closes the connection to the client and remove client from the connected client list'''
        if(self.client):
            self.client.close()
        else:
            pass

    def __del__(self):
        """Destructor"""
        self.close()


def update(self,queue):
    '''Update the next few frames to fill up the queue'''

    #Capture object
    cap = cv2.VideoCapture(1)
    
    #Loop to update the queues
    while cap.isOpened():

        #If the thread should be stopped return
        if self.stopped or cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # otherwise, ensure the queue has room in it
        if not queue.full():

            #Read the next frame from the file
            item = cap.read()

            # Check if the frame is valid
            if not item[0]:
                return

            # add the frame to the queue
            queue.put(item)

    #Release the capture device
    cap.release()

class VideoC():
    def __init__(self, queue):
        '''Initialiser for the capture'''
        self.prev = []
        self.time = 0
        self.count = 0
        self.queue = queue
        self.stopped = False
        self.server = Server('192.168.1.47',1234)

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
            cframe = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            #Getting the difference in the frame in terms of gray scale
            frame = cv2.absdiff(pframe,cframe)
            
            #Return the frame
            return frame

        else:
            #If there is no previous frame, there is no need to process it
            # self.time = time.time()
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

                #Do modifications to the frame here/ Other operations
                nframe = self.process(frame)

                #Show the original image
                cv2.imshow('Video', frame)

                #Show the Img delta
                cv2.imshow('Delta', nframe)

                #Print the x midpt
                # print(self.calculate(nframe))

                #Listen for the arduino
                self.server.listen()

                #Send the midpt to the arduino
                sector = self.calculate(nframe)
                if(self.server.send(sector)):
                    self.queue_clear()

                #Set the current frame as prev frame
                self.count += 1
                if(self.count % 4 == 0):
                    self.prev = frame
                    self.count = 0

        #To close the camera properly
        self.quit()

    def queue_clear(self):
        """Empty the queue"""
        while not self.queue.empty():
            self.queue.get()

    def calculate(self,frame):
        """Calculate the midpoint of the white pixels in frame"""
        white_pixels = np.where(frame > [100])

        #If there are pixels get the coord of the first white and the last white
        try:
            left_white = white_pixels[1][0]
            right_white = white_pixels[1][-1]
            return int(round((right_white + left_white)/640*3,0))

        except:
            return -1
        
    def quit(self):
        '''Release all of the cams which are active'''
        
        #Stop the thread
        self.stopped = True

        #Close all of the windows
        cv2.destroyAllWindows()

    def __del__(self):
        '''Destructor for the VideoC object'''
        self.quit()

def main():
    '''Main function to run'''
    #Queue 
    queue = multiprocessing.Manager().Queue(120)

    #Create the video capture object
    vc = VideoC(queue)

    #Create a separate process to render the frames into a queue
    p = multiprocessing.Process(target = update, args= (vc,queue))
    p.start()

    #Display the video frame by frame
    vc.display()


#Check if it is the main file before running
if __name__ == '__main__':
    main()
