import time
import sys
sys.path.append('D:\\OneDrive - University of Pittsburgh\\Fall 2021\\Ece 1896\\Project\\3D Mouse Project\\Github\\3dmouse\\Testing\\Scripts\\Libraries')
sys.path.append('D:\\OneDrive - University of Pittsburgh\\Fall 2021\\Ece 1896\\Project\\3D Mouse Project\\Github\\3dmouse\\Testing\\Scripts\\Libraries\\matplotlib')
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import threading


class Reciever:
    """
    A class used to represent the USB Reciever module
    ...
    Attributes
    ----------
    reciever : serial.Serial
        a pyserial serial communication object responsible for fetching and sending data to reciever
    timing : float
        the timing delay between fetch data requests when streaming is enabled (default value is 0.01)
    streaming : bool
        bool value that enables/disables automatic data fetching, if disabled fetch_data can be called manually
    mode : int
        the mode of operation the mouse is in (valid values: 1, 2, or 3)
    x : int
        relative x delta displacement from last data fetch (valid values: 0-1023)
    y : int
        relative y delta displacement from last data fetch (valid values: 0-1023)
    z : int
        relative z delta displacement from last data fetch (valid values: 0-1023)

    Methods
    -------
    start_stream()
        start streaming data from reciever through a new threaded timer
    end_stream()
        stop streaming data from reciever
    write_data()
        send single char data to reciever
    read_data()
        read current mode, x, y, and z stored in object
    fetch_data()
        send 'w' request to reciever and in turn fetch new mode, x, y, z data to update the object"
    close()
        stop streaming and close serial connection with reciever
    """

    def __init__(self, timing=.01):
        """
        Parameters
        ----------
        timing : float, optional
            The timing delay between fetch data requests when streaming is enabled (default value is 0.01)

        Raises
        ------
        RuntimeError
            If no available COM ports detected or reciever not found in the available COM ports.
        """
        ports = serial.tools.list_ports.comports(include_links=False)
        if len(ports) == 0:
            raise RuntimeError('No available COM ports detected.')
        self.reciever = None
        for port in ports:
            if port.description.startswith('Arduino NANO Every'):
                self.reciever = serial.Serial(port=port.device, baudrate=115200, timeout=.1)
                break
        if self.reciever is None:
            raise RuntimeError('Reciever not found in available COM ports')
        self.timing = timing
        self.streaming = False
        self.mode = 1
        self.x = 0
        self.y = 0
        self.z = 0

    def start_stream(self):
        """function to start streaming data from reciever through a new threaded timer"""
        self.streaming = True
        t = threading.Timer(0, self.fetch_data)
        t.start()

    def end_stream(self):
        """function to stop streaming data from reciever"""
        self.streaming = False

    def write_data(self, char):
        """function to send single char data to reciever

        Parameters
        ----------
        char : char
            The character to write to the reciever
        """
        self.reciever.write(char.encode('utf8'))

    def read_data(self):
        """function to read current mode, x, y, and z stored in object"""
        return self.mode, self.x, self.y, self.z

    def fetch_data(self):
        """function to send 'w' request to reciever and in turn fetch new mode, x, y, z data to update the object"""
        self.write_data('w')
        data = self.reciever.read_until(bytes('\n', 'utf-8')).decode("utf-8")
        parsed = data.split('\t')
        if len(parsed) == 4:
            try:
                parsed = [int(item) for item in parsed]
                mode = parsed[0]
                x = parsed[1]
                y = parsed[2]
                z = parsed[3]

                self.mode = mode
                self.x = x
                self.y = y
                self.z = z
            except Exception as e:
                print(e)
                pass
        if self.timing > 0 and self.streaming:
            t = threading.Timer(self.timing, self.fetch_data)
            t.start()

        return self.mode, self.x, self.y, self.z

    def close(self):
        """function to stop streaming and close serial connection with reciever"""
        self.streaming = False
        time.sleep(1)
        self.reciever.close()


def main():
    reciever = Reciever(timing=0.01)
    reciever.start_stream()

    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.set_ylim([-8192,8192])
    ax.set_xlim([-8192,8192])    

    while True:
        mode, x, y, z = reciever.read_data()
        ax.clear()
        ax.set_ylim([-8192,8192])
        ax.set_xlim([-8192,8192])
        plt.scatter(-x,-y)
        plt.show()
        plt.pause(0.001)
        print(mode, x, y, z)
        time.sleep(.01)

    reciever.end_stream()
    print('Ending Stream')

    for i in range(8):
        mode, x, y, z = reciever.read_data()
        print(mode, x, y, z)
        time.sleep(.5)

    reciever.start_stream()
    print('Starting Stream')

    for i in range(20):
        mode, x, y, z = reciever.read_data()
        print(mode, x, y, z)
        time.sleep(.5)

    reciever.close()


if __name__ == '__main__':
    main()
