import serial

from SETUP import *
from file_writer import FileListWriter


class GpsReader:
    def __init__(self, logger, file_list):
        self.logger = logger

        self.gps = None
        self.file_writer = FileListWriter(file_list)

    def __write(self, data):
        if data.startswith(b'$GNGGA') or data.startswith(b'$GNRMC'):
            self.file_writer.write(data.decode("utf-8"))

    def set_up(self):
        ret = False

        if self.file_writer.create_list() < 1:
            self.logger.error("couldn't open files to write gps data")
            return ret

        try:
            self.gps = serial.Serial(GPS_SERIAL_PORT, baudrate=GPS_BAUDRATE, timeout=0.5)
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
        self.file_writer.close()


