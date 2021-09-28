import time
import serial
import threading


class Reciever:
    def __init__(self, timing=.5):
        self.arduino = serial.Serial(port='COM5', baudrate=115200, timeout=2)
        self.timing = timing
        self.streaming = False
        self.mode = 1
        self.x = 0
        self.y = 0
        self.z = 0

    def start_stream(self):
        self.streaming = True
        t = threading.Timer(self.timing, self.fetch_data)
        t.start()

    def end_stream(self):
        self.streaming = False

    def write_data(self):
        self.arduino.write('w'.encode('utf8'))

    def read_data(self):
        return self.mode, self.x, self.y, self.z

    def fetch_data(self):
        self.arduino.flushInput()
        time.sleep(0.01)
        data = self.arduino.read_until(bytes('\n', 'utf-8')).decode("utf-8")
        parsed = data.split('\t')
        if len(parsed) == 4:
            parsed = [int(item) for item in parsed]
            mode = parsed[0]
            x = parsed[1]
            y = parsed[2]
            z = parsed[3]

            self.mode = mode
            self.x = x
            self.y = y
            self.z = z

        if self.timing > 0 and self.streaming:
            # t = threading.Timer(self.timing, self.fetch_data)
            # t.start()
            time.sleep(self.timing)
            self.fetch_data()

        return self.mode, self.x, self.y, self.z

    def close(self):
        self.streaming = False
        self.arduino.close()


def main():
    reciever = Reciever()
    reciever.start_stream()

    # reciever.write_data()
    # reciever.close()

    while True:
        mode, x, y, z = reciever.read_data()
        print(mode, x, y, z)
        time.sleep(2)



if __name__ == '__main__':
    main()
