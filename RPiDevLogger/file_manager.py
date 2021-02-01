import os
from os import path
import shutil

import SETUP
from UartFileManager import UartFileManager
from SETUP import DAT_DIR


def get_free_memory_gb():
    total, used, free = shutil.disk_usage("/")
    return free // (2 ** 30)


class FileManager:

    LOGIC_FILE = 0
    GPS_FILE = 1
    AUDIO_FILE = 2

    UART_KEYS = ['id', 'port', 'baudrate']
    UART_INT_KEYS = ['id', 'baudrate']

    def __init__(self, logger, min_mem, rm_koef):
        self.logger = logger

        self.min_memory = min_mem
        self.rm_koef = rm_koef
        self.directories = DAT_DIR
        self.max_session = SETUP.MAX_SESSION_ID
        session_digits = "{:0" + str(len(str(SETUP.MAX_SESSION_ID))) + "d}"
        self.file_template = ['{}_logic.log'.format(session_digits), '{}_GPS.log'.format(session_digits),
                              '{}_audio.wav'.format(session_digits)]
        self.uart_files = UartFileManager(logger, session_digits)

    def __memory_enough(self):
        total, used, free = shutil.disk_usage("/")
        self.logger.info("Total: %d GiB" % (total // (2 ** 30)))
        self.logger.info("Used: %d GiB" % (used // (2 ** 30)))
        if free // (2 ** 30) < self.min_memory:
            return False
        else:
            return True

    def __clear_memory(self):
        self.logger.info("memory clearing...")
        for i in range(self.max_session):
            for dir in self.directories:
                for file in self.file_template:
                    file_path = path.join(dir, file.format(i))
                    if path.isfile(file_path):
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            self.logger.exception(e)
                            return
                self.uart_files.delete_files(i, dir)
            if get_free_memory_gb() > self.rm_koef * self.min_memory:
                break

    def __check_directory(self, dir):
        ret = True
        if not path.isdir(dir):
            try:
                os.mkdir(dir)
            except OSError as e:
                ret = False
                self.logger.error("Creation of the directory %s failed" % dir)
                self.logger.exception(e)
            else:
                self.logger.info("Successfully created the directory %s " % dir)
        else:
            self.logger.info(dir + " exist")
        return ret

    def __get_max_id(self):
        last_session = -1
        for i in range(self.max_session, -1, -1):
            id_exist = False
            for dir in self.directories:
                for file in self.file_template:
                    file_path = path.join(dir, file.format(i))
                    if path.isfile(file_path):
                        id_exist = True
                        break
                if not id_exist:
                    id_exist = self.uart_files.exists(i, dir)
                if id_exist:
                    break
            if id_exist:
                last_session = i
                break
        return last_session + 1

    def __get_min_id(self):
        session_id = -1
        for i in range(self.max_session):
            id_exist = False
            for dir in self.directories:
                for file in self.file_template:
                    file_path = path.join(dir, file.format(i))
                    if path.isfile(file_path):
                        id_exist = True
                        break
                if not id_exist:
                    id_exist = self.uart_files.exists(i, dir)
                if id_exist:
                    break
            if not id_exist:
                session_id = i
                break
        return session_id

    def check_folders(self):
        for directory in self.directories:
            if not self.__check_directory(directory):
                self.logger.error("fail open directory " + directory)
                return False
        return True

    def check_memory(self):
        if not self.__memory_enough():
            self.logger.warning("not enough free space")
            self.__clear_memory()
            if not self.__memory_enough():
                self.logger.error("can not remove enough files")
                return False
        return True

    def find_session_id(self):
        session_id = self.__get_max_id()
        if session_id > self.max_session:
            self.logger.warning("reached max session id")
            session_id = self.__get_min_id()
            if session_id < 0:
                self.logger.error("no free session number")
        return session_id

    def get_file_list(self, file_type, session_id):
        file_list = []
        for dir in self.directories:
            file_name = path.join(dir, self.file_template[file_type].format(session_id))
            file_list.append(file_name)
        return file_list

    def get_uart_file_list(self, session_id):
        result = None
        uart_config = SETUP.UART_CONFIG
        if self.__check_uart_config(uart_config):
            for uart in uart_config:
                file_list = []
                for dir in self.directories:
                    file_list.append(self.uart_files.get_file_name(session_id, dir, uart['id']))
                uart["file_list"] = file_list
            result = uart_config
        return result

    def __check_uart_config(self, uart_config):
        for uart in uart_config:
            for key in self.UART_KEYS:
                if key not in uart:
                    self.logger.error('in uart config missed {} key'.format(key))
                    return False
                try:
                    if key in self.UART_INT_KEYS:
                        uart[key] = int(uart[key])
                    else:
                        uart[key] = str(uart[key])
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error("type mismatch for key {} in uart config".format(key))
                    return False
        return True
