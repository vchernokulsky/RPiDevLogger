import time

import serial

from SETUP import UART_READING_INTERVAL
from file_writer import FileListWriter


class UartReader:

    def __init__(self, logger, uart_config):
        self.logger = logger
        self.id = uart_config["id"]
        self.port = uart_config["port"]
        self.baudrate = uart_config["baudrate"]
        self.file_writer = FileListWriter(uart_config["file_list"])

        self.uart = None
        self.is_ok = False

    def __set_up(self):
        ret = False

        if self.file_writer.create_list() < 1:
            self.logger.error("couldn't open files to write uart data")
            return ret
        try:
            self.uart = serial.Serial(self.port, self.baudrate, timeout=1)
            ret = True
            self.is_ok = True
        except Exception as err:
            self.logger.exception(err)
        return ret

    def __write(self, data):
        if data is not None and len(data) > 0:
            self.file_writer.write(data)

    def start(self):
        if self.__set_up():
            self.logger.info("start reading UART_{} on port {}".format(self.id, self.port))
            try:
                while True:
                    data = self.__loop()
                    self.__write(data)
                    time.sleep(UART_READING_INTERVAL)
            except KeyboardInterrupt:
                self.logger.info("finish reading UART_{}".format(self.id))
            except Exception as e:
                self.logger.exception(e)
            self.stop()
        else:
            self.logger.error("couldn't setup gps")

    def stop(self):
        if self.is_ok:
            self.uart.close()
        self.file_writer.close()

    def __loop(self):
        data = None
        try:
            if not self.uart.isOpen():
                self.uart.open()
            data = self.uart.read(1000000)
        except Exception as e:
            self.logger.exception(e)
        return data

