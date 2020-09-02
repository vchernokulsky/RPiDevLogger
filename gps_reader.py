import serial

SERIAL_PORT = "/dev/ttyACM0"


class GpsReader:
    def __init__(self, logger, file_list):
        self.logger = logger
        self.file_list = file_list

        self.gps = None

    def __write(self, data):
        self.logger.info(data)

    def set_up(self):
        ret = False
        try:
            self.gps = serial.Serial(SERIAL_PORT, baudrate=9600, timeout=0.5)
            ret = True
        except (ValueError, IOError) as err:
            self.logger.exception(err)
        return ret

    def start(self):
        self.logger.info("start reading GPS")
        try:
            while True:
                data = self.gps.readline()
                self.__write(data)
        except KeyboardInterrupt:
            self.logger.info("finish reading GPS")
        except Exception as e:
            self.logger.exception(e)
        self.stop()

    def stop(self):
        self.gps.close()


