import string
import time
import json
import smbus
import logging

BUS = None
address = 0x42
gpsReadInterval = 0.1
LOG = logging.getLogger()


def connect_bus():
    global BUS
    BUS = smbus.SMBus(1)


def __check_nmea_message(msg, chk):
    chk_val = 0
    for ch in msg[1:]:  # Remove the $
        chk_val ^= ord(ch)
    try:
        if chk_val != int(chk, 16):
            # print("wrong checksum: " + msg + "*" + chk)
            LOG.info('incorrect checksum in MSG: ' + msg)
            return False
    except ValueError as ex:
        LOG.info('incorrect character in NMEA checksum: ' + chk)
    return True


def __get_nmea_data(nmea_string):
    result = None, None
    nmea_data_array = nmea_string.split('*')
    if len(nmea_data_array) != 2:
        pass
        # print("NMEA checksum contain wrong character:")
        # print("[ " + nmea_string + " ]")
    else:
        nmea_msg = nmea_data_array[0]
        nmea_chk = nmea_data_array[1]
        if __check_nmea_message(nmea_msg, nmea_chk):
            nmea_data = nmea_msg.split(',')
            result = nmea_data[0], nmea_data[1:]
    return result


def parse_response(gps_data_array):
    gps_data_string = ''.join(chr(c) for c in gps_data_array)
    header, param = __get_nmea_data(gps_data_string)
    if header is not None:
        if header not in ["$GNRMC", "$GNGGA"]:
            return True
        if header == "$GNRMC":
            if len(param) != 12:
                print("wrong fields number")
                return False
        if header == "$GNGGA":
            if len(param) != 14:
                print("wrong fields number")
                return False
        print(gps_data_string)
    return True


def gps_reading_loop():
    c = None
    response = []
    try:
        while True:  # Newline, or bad char.
            c = BUS.read_byte(address)
            if c == 255:
                return False
            elif c == 10:
                break
            else:
                response.append(c)
        parse_response(response)
    except IOError:
        time.sleep(0.5)
        connect_bus()
    except Exception as e:
        print(e)
        LOG.error(e)


connect_bus()
while True:
    gps_reading_loop()
    time.sleep(gpsReadInterval)
