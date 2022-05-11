from multiprocessing import Process, Queue
from swo_parser import Stream, StreamManager
import time
import socket
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

tlm_queue = Queue()

HOST = "localhost"
PORT = 6666

def rec_tlm(tqueue):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcl_socket:
        tcl_socket.connect((HOST, PORT))
        tcl_socket.settimeout(0)
        
        # Create a stream manager and add three streams
        streams = StreamManager()
        streams.add_stream(Stream(0, '', tcl_socket, tqueue))
        #streams.add_stream(Stream(1, 'WARNING: '))
        #streams.add_stream(Stream(2, 'ERROR: ', tcl_socket))
        
        # Enable the tcl_trace output
        tcl_socket.sendall(b'tcl_trace on\n\x1a')

        
        tcl_buf = b''
        while True:
            # Wait for new data from the socket
            data = b''
            while len(data) == 0:
                try:
                    data = tcl_socket.recv(1024)
                except BlockingIOError:
                    time.sleep(0.1)

            tcl_buf = tcl_buf + data

            # Tcl messages are terminated with a 0x1A byte
            temp = tcl_buf.split(b'\x1a',1)
            while len(temp) == 2:
                # Parse the Tcl message
                try:
                    streams.parse_tcl(temp[0])
            
                except:
                    continue
                
                 # Remove that message from tcl_buf and grab another message from
                # the buffer if the is one
                tcl_buf = temp[1]
                temp = tcl_buf.split(b'\x1a',1)
        
        # Turn off the trace data before closing the port
        # XXX: There currently isn't a way for the code to actually reach this line
        tcl_socket.sendall(b'tcl_trace off\n\x1a')

# plot class
class AnalogPlot:
  # constr
    def __init__(self, tlm_qeue, maxLen):
        # open serial port
        # self.ser = serial.Serial(strPort, 9600)

        self.ax = deque([0.0]*maxLen)
        self.ay = deque([0.0]*maxLen)
        self.maxLen = maxLen
        self.queue = tlm_queue

    # add to buffer
    def addToBuf(self, buf, val):
        if len(buf) < self.maxLen:
            buf.append(val)
        else:
            buf.pop()
            buf.appendleft(val)

    # add data
    def add(self, data):
        assert(len(data) == 2)
        self.addToBuf(self.ax, data[0])
        self.addToBuf(self.ay, data[1])

    # update plot
    def update(self, frameNum, a0, a1):
        try:
            line = tlm_queue.get()
            print(line)
            
            data = [float(line.split(",")[0]), float(line.split(",")[1])]
            # print data
            print(data)
            if(len(data) == 2):
                self.add(data)
                a0.set_data(range(self.maxLen), self.ax)
                a1.set_data(range(self.maxLen), self.ay)
        except KeyboardInterrupt:
            print('exiting')
        except:
            return None

        return a0, 

    # clean up
    def close(self):
        # close serial
        self.ser.flush()
        self.ser.close()  

if __name__ == "__main__":
    recorder = Process(target=rec_tlm, args=(tlm_queue,))
    recorder.start()
    analogPlot = AnalogPlot(tlm_queue, 300)

    fig = plt.figure()
    ax = plt.axes(xlim=(0, 300), ylim=(15000, 30023))
    a0, = ax.plot([], [])
    a1, = ax.plot([], [])
    anim = animation.FuncAnimation(fig, analogPlot.update, 
                fargs=(a0, a1), 
                interval=1)

    # show plot
    plt.show()

    # clean up
    analogPlot.close()

    print('exiting.')
  
    
  

