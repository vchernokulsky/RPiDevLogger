import smbus
import time

from SETUP import *
from file_writer import FileListWriter


class GpsReader:
    def __init__(self, logger, file_list):
        self.logger = logger
        self.is_ok = False

        self.gps = None
        self.file_writer = FileListWriter(file_list, logger)

    def __write(self, data):
        if data is not None and len(data) > 0:
            self.file_writer.write(data.encode("utf-8"))

    def set_up(self):
        ret = False

        if self.file_writer.create_list() < 1:
            self.logger.error("couldn't open files to write gps data")
            return ret

        try:
            self.gps = smbus.SMBus(GPS_I2C_LINE)
            ret = True
            self.is_ok = True
        except Exception as err:
            self.logger.exception(err)
        return ret

    def start(self):
        if self.set_up():
            self.logger.info("start reading GPS")
            try:
                while True:
                    data = self.__gps_reading_loop()
                    self.__write(data)
                    time.sleep(GPS_READING_INTERVAL)
            except KeyboardInterrupt:
                self.logger.info("finish reading GPS")
            except Exception as e:
                self.logger.exception(e)
            self.stop()
        else:
            self.logger.error("couldn't setup gps")

    def stop(self):
        if self.is_ok:
            self.gps.close()
        self.file_writer.close()

    def __gps_reading_loop(self):
        response = []
        ret = None
        try:
            while True:  # Newline, or bad char.
                c = self.gps.read_byte(GPS_I2C_ADDRESS)
                if c == 255:
                    return ret
                elif c == 10:
                    break
                else:
                    response.append(c)
            ret = self.__parse_response(response)
        except IOError as e:
            time.sleep(0.5)
            self.gps = smbus.SMBus(GPS_I2C_LINE)
            self.logger.exception(e)
        except Exception as e:
            self.logger.exception(e)
        return ret

    def __parse_response(self, gps_data_array):
        ret = None
        gps_data_string = ''.join(chr(c) for c in gps_data_array)
        header, param = self.__get_nmea_data(gps_data_string)
        if header is not None and header in ["$GNRMC", "$GNGGA"]:
            if header == "$GNRMC" and len(param) != 12:
                self.logger.warning("wrong fields number")
            elif header == "$GNGGA" and len(param) != 14:
                self.logger.warning("wrong fields number")
            else:
                ret = gps_data_string
        return ret

    def __get_nmea_data(self, nmea_string):
        result = None, None
        nmea_data_array = nmea_string.split('*')
        if len(nmea_data_array) != 2:
            self.logger.warning("cannot get checksum")
        else:
            nmea_msg = nmea_data_array[0]
            nmea_chk = nmea_data_array[1]
            if self.__check_nmea_message(nmea_msg, nmea_chk):
                nmea_data = nmea_msg.split(',')
                result = nmea_data[0], nmea_data[1:]
        return result

    def __check_nmea_message(self, msg, chk):
        ret = False
        chk_val = 0
        for ch in msg[1:]:  # Remove the $
            chk_val ^= ord(ch)
        try:
            if chk_val == int(chk, 16):
                ret = True
            else:
                self.logger.warning('incorrect checksum in MSG: ' + msg)
        except ValueError as ex:
            self.logger.warning("check sum {} is not a number".format(chk))
        return ret


