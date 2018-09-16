from abc import ABC, abstractmethod
import time


class Imu(ABC):
    """
    Abstract base class for IMU parts
    Must implement the abstract :func:`imu.Imu.poll`

    Each IMU may have an different package installation
    """
    def __init__(self, poll_delay):
        self.poll_delay = poll_delay
        self.accel = {'x': 0., 'y': 0., 'z': 0.}
        self.gyro = {'x': 0., 'y': 0., 'z': 0.}
        self.temp = 0.
        self.on = True

    def update(self):
        while self.on:
            self.poll()
            time.sleep(self.poll_delay)

    @abstractmethod
    def poll(self):
        pass

    def run(self):
        self.poll()
        return self.accel['x'], self.accel['y'], self.accel['z'], self.gyro['x'], self.gyro['y'], self.gyro[
            'z'], self.temp

    def run_threaded(self):
        return self.accel['x'], self.accel['y'], self.accel['z'], self.gyro['x'], self.gyro['y'], self.gyro[
            'z'], self.temp

    def shutdown(self):
        self.on = False


class MPU6050(Imu):
    '''
    Installation:
    sudo apt install python3-smbus
    or
    sudo apt-get install i2c-tools libi2c-dev python-dev python3-dev
    git clone https://github.com/pimoroni/py-smbus.git
    cd py-smbus/library
    python setup.py build
    sudo python setup.py install

    pip install mpu6050-raspberrypi
    '''

    def __init__(self, addr=0x68, poll_delay=0.0166):
        super().__init__(poll_delay)
        from mpu6050 import mpu6050
        self.sensor = mpu6050(addr)

    def poll(self):
        try:
            self.accel, self.gyro, self.temp = self.sensor.get_all_data()
        except:
            print('failed to read imu!!')


class Fxos8700(Imu):
    """
    Adafruit Precision NXP 9-DOF Breakout Board - FXOS8700 + FXAS21002  https://www.adafruit.com/product/3463
    Uses Adafruit Circuit python with blinka abstraction:

    https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi

    Installation:
    pip install RPI.GPIO
    pip install adafruit-blinka
    pip install adafruit_fxos8700

    """
    def __init__(self, poll_delay=0.0166):
        super().__init__(poll_delay)
        import board
        import busio
        import adafruit_fxos8700

        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_fxos8700.FXOS8700(i2c)

    def poll(self):
        accel_x, accel_y, accel_z = self.sensor.accelerometer
        self.accel['x'] = accel_x
        self.accel['y'] = accel_y
        self.accel['z'] = accel_z


def get_imu(type):
    if type == 'MPU6050':
        return MPU6050()
    elif type == 'FXOS8700':
        return Fxos8700()


if __name__ == "__main__":
    iter = 0
    p = Mpu6050()
    while iter < 100:
        data = p.run()
        print(data)
        time.sleep(0.1)
        iter += 1