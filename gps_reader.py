import serial

SERIAL_PORT = "/dev/ttyACM0"


class GpsReader:
    def __init__(self, logger, file_list):
        self.logger = logger
        self.file_list = file_list

        self.gps = None
        self.writer_list = []

    def __write_list_create(self):
        for name in self.file_list:
            f = open(name, 'w')
            self.writer_list.append(f)

    def __write_list_write(self, data):
        for w in self.writer_list:
            w.write(data)

    def __write_list_close(self):
        for w in self.writer_list:
            w.close()

    def __write(self, data):
        if data.startswith(b'$GNGGA') or data.startswith(b'$GNRMC'):
            self.__write_list_write(data.decode("utf-8"))

    def set_up(self):
        ret = False

        self.__write_list_create()
        if len(self.writer_list) < 1:
            self.logger.error("couldn't open files to write gps data")
            return ret

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
        self.__write_list_close()


