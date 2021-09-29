import time
import serial
import serial.tools.list_ports
import threading


class Reciever:
    def __init__(self, timing=.01):
        ports = serial.tools.list_ports.comports(include_links=False)
        if len(ports) == 0:
            raise RuntimeError('No available COM ports detected.')
        self.reciever = None
        for port in ports:
            if port.description.startswith('Arduino NANO Every'):
                self.reciever = serial.Serial(port=port.device, baudrate=115200, timeout=.2)
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
        self.streaming = True
        t = threading.Timer(0, self.fetch_data)
        t.start()

    def end_stream(self):
        self.streaming = False

    def write_data(self, char):
        self.reciever.write(char.encode('utf8'))

    def read_data(self):
        return self.mode, self.x, self.y, self.z

    def fetch_data(self):
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
        self.streaming = False
        time.sleep(1)
        self.reciever.close()


def main():
    reciever = Reciever(timing=0.01)
    reciever.start_stream()

    # for i in range(100):
    while True:
        mode, x, y, z = reciever.read_data()
        print(mode, x, y, z)
        time.sleep(.25)

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
