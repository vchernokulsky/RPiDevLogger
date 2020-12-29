import logging
import logging.handlers
import sys

from FileManager import FileManager
from UartLogger import UartLogger
from SETUP import *

FREQ = 0
MIN_MEM_FREE = 1
RM_KOEF = 2

keys = ['uart_rx_channel', 'file_name', 'baudrate']


logger = logging.getLogger("RPiDevLogger2")


def set_logger():
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = logging.handlers.RotatingFileHandler(LOG_FILE_NAME, maxBytes=20480, backupCount=10)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # logger.setLevel(logging.ERROR)
    logger.setLevel(logging.INFO)


def exit_gracefully(signum, frame):
    print("Buy!")
    logger.info("Program finished")
    sys.exit(0)


def read_config():
    decoder_config_list = DECODER_CONFIG
    if decoder_config_list is None:
        logger.error("No Decoder config in setup file")
        return None
    if len(decoder_config_list) <= 0:
        logger.error("No uart for decoding specified in setup file")
        return None
    for uart_dict in decoder_config_list:
        for key in keys:
            if key not in uart_dict:
                logger.error('key "{}" missed in configuration file'.format(key))
                return None
            if uart_dict[key] is None:
                logger.error('{} value couldn\'t be converted to float'.format(key))
                return None
    return decoder_config_list


def main():
    # ======= READ CONFIG ===================
    set_logger()
    logger.info("******** START ***********")
    config = read_config()
    if config is None:
        return
    logger.info("configuration: {}".format(config))

    # ========= CHECK MEMORY =================
    fm = FileManager(logger, MIN_FREE_SPACE_GB, FILE_REMOVE_KOEF, config)
    if not fm.check_folders():
        return
    if not fm.check_memory():
        return

    # ============ GET SESSION ID ===============
    if not fm.find_session_id():
        return
    logger.info("Current session id: {}".format(fm.session_id))

    # ============ UART LOGGER =============
    logic = UartLogger(logger, fm)
    logic.start()


if __name__ == "__main__":
    main()
