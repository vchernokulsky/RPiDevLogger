import json
import logging
import logging.handlers
import signal
import sys
import time
from multiprocessing import Process

from RPiDevLogger.MultipleUarts import MultipleUarts
from SETUP import *
from file_manager import FileManager
from gps_reader import GpsReader
from logic_reader import LogicReader
from usb_audio import UsbAudio

from RPiDevLogger.makeFly import make_fly

FREQ = 0
MIN_MEM_FREE = 1
RM_KOEF = 2

keys = ['frequency', 'min_free_space_gb', 'file_remove_koef']
float_keys = ['min_free_space_gb', 'file_remove_koef']


logger = logging.getLogger("RPiDevLogger")


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
    j_dict = None
    try:
        with open(CONFIG_FILE) as f:
            j_dict = json.load(f)
    except Exception as e:
        logger.exception(e)
    return j_dict


def format_config(j_dict):
    params = {}
    if j_dict is None:
        logger.error("fail to read configuration file")
        return None
    for key in keys:
        if key not in j_dict:
            logger.error('key "{}" missed in configuration file'.format(key))
            return None
        val = validate_value(j_dict[key], key)
        if val is None:
            logger.error('{} value couldn\'t be converted to float'.format(key))
            return None
        params[key] = val
    return params


def validate_value(val, key):
    ret = None
    try:
        if key in float_keys:
            ret = float(val)
        else:
            ret = str(val)
    except Exception as e:
        logger.exception(e)
    finally:
        return ret


def main():
    # ======= READ CONFIG ===================
    set_logger()
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    logger.info("******** START ***********")
    config = format_config(read_config())
    if config is None:
        return
    logger.info("configuration: {}".format(config))

    # ========= CHECK MEMORY =================
    fm = FileManager(logger, config[keys[MIN_MEM_FREE]], config[keys[RM_KOEF]])
    if not fm.check_folders():
        return
    if not fm.check_memory():
        return

    # ============ GET SESSION ID ===============
    session_id = fm.find_session_id()
    if session_id < 0:
        return
    logger.info("Current session id: {}".format(session_id))

    # =========== REWRITE LOGIC DATA ============
    logger.info("start rewriting logic data")
    try:
        make_fly()
        logger.info("finish rewriting logic data")
    except Exception as e:
        logger.exception(e)

    # =========== GET AUDIO FILES ==================
    audio_list = fm.get_file_list(fm.AUDIO_FILE, session_id)
    if len(audio_list) <= 0:
        logger.error("cannot create audio files")
        return
    logger.info("audio will be written into files : {}".format(audio_list))

    # =========== GET GPS FILES ====================
    gps_list = fm.get_file_list(fm.GPS_FILE, session_id)
    if len(gps_list) <= 0:
        logger.error("cannot create gps files")
        return
    logger.info("gps data will be written into files : {}".format(gps_list))

    # =========== GET SALEAE LOGIC FILES ====================
    logic_list = fm.get_file_list(fm.LOGIC_FILE, session_id)
    if len(logic_list) <= 0:
        logger.error("cannot create saleae logic files")
        return
    logger.info("saleae logic data will be written into files : {}".format(logic_list))

    # =========== GET UART CONFIG AND FILES ====================
    uart_files = fm.get_uart_file_list(session_id)
    if uart_files is None or len(uart_files) <= 0:
        logger.error("cannot create uart files")
        return
    logger.info("uart config : {}".format(uart_files))

    # ============ START AUDIO RECORDING ===============
    audio = UsbAudio(logger, audio_list)
    audio_proc = Process(target=audio.start, args=())
    audio_proc.start()

    # ============ GPS RECORD =============
    gps = GpsReader(logger, gps_list)
    gps_proc = Process(target=gps.start, args=())
    gps_proc.start()

    # ============ LOGIC RECORD =============
    logic = LogicReader(logger, logic_list, config[keys[FREQ]])
    logic_proc = Process(target=logic.start, args=())
    logic_proc.start()

    # ============ UART RECORD =============
    uart = MultipleUarts(logger, uart_files)
    uart.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("finished")
    except Exception as e:
        logger.exception(e)

    audio_proc.join()
    gps_proc.join()
    logic_proc.join()
    uart.join()

    audio.stop()
    gps.stop()
    logic.stop()
    uart.stop()


if __name__ == "__main__":
    main()
