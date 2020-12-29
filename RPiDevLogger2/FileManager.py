import os
from os import path
import shutil

from SETUP import *

file_name_key = 'file_name'

def get_free_memory_gb():
    total, used, free = shutil.disk_usage("/")
    return used // (2 ** 30)


class FileManager:
    def __init__(self, logger, min_mem, rm_koef, uart_config):
        self.logger = logger
        self.min_memory = min_mem
        self.rm_koef = rm_koef
        self.directory = DAT_DIR
        self.sesion_dir = SESSION_DIR_NAME
        self.uart_config = uart_config
        self.__create_file_name_templates()
        self.session_dir_template = "{}_{:02d}"
        self.session_id = 0

    def __create_file_name_templates(self):
        for uart_dict in self.uart_config:
            uart_dict[file_name_key] = '{}_{}'.format('{:02d}', uart_dict[file_name_key])


    def __memory_enough(self):
        total, used, free = shutil.disk_usage("/")
        self.logger.info("Total: %d GiB" % (total // (2 ** 30)))
        self.logger.info("Used: %d GiB" % (used // (2 ** 30)))
        if free // (2 ** 30) < self.min_memory:
            return False
        else:
            return True

    def __remove_file(self, file_name):
        try:
            os.remove(file_name)
        except Exception as e:
            self.logger.warning(e)

    def __remove_empty_dir(self, dir_name):
        try:
            os.rmdir(dir_name)
        except Exception as e:
            self.logger.warning(e)

    def __remove_directory(self, directory):
        if path.isdir(directory):
            for cur_item in os.listdir(directory):
                cur_name = path.join(directory, cur_item)
                if path.isdir(cur_name):
                    self.__remove_directory(cur_name)
                else:
                    self.__remove_file(cur_name)
            self.__remove_empty_dir(directory)
        else:
            self.logger.warning('{} is not a directory'.format(directory))

    def __clear_memory(self):
        self.logger.info("memory clearing...")
        for i in range(100):
            cur_dir = path.join(self.directory, self.session_dir_template.format(self.sesion_dir,i))
            if path.isdir(cur_dir):
                self.__remove_directory(cur_dir)
            if get_free_memory_gb() > self.rm_koef * self.min_memory:
                break

    def __check_directory(self, directory):
        ret = True
        if not path.isdir(directory):
            try:
                os.mkdir(directory)
            except OSError as e:
                ret = False
                self.logger.error("Creation of the directory %s failed" % directory)
                self.logger.exception(e)
            else:
                self.logger.info("Successfully created the directory %s " % directory)
        else:
            self.logger.info(directory + " exist")
        return ret

    def __get_max_id(self):
        last_session = -1
        for i in range(99, -1, -1):
            session_path = path.join(self.directory, self.session_dir_template.format(self.sesion_dir, i))
            if path.isfile(session_path):
                self.logger.warning('{} reserved name for session directory. remove this file')
            else:
                if path.isdir(session_path):
                    last_session = i
                    break
        return last_session + 1

    def __get_min_id(self):
        session_id = -1
        for i in range(99):
            id_exist = False
            session_path = path.join(self.directory, self.session_dir_template.format(self.sesion_dir, i))
            if path.isfile(session_path):
                self.logger.warning('{} reserved name for session directory. remove this file')
            elif not path.isdir(session_path):
                session_id = i
                break
        return session_id

    def __create_session_folder(self, session_id, rec_level):
        cur_session = session_id
        session_path = path.join(self.directory, self.session_dir_template.format(self.sesion_dir, session_id))
        try:
            os.mkdir(session_path)
        except OSError as e:
            self.logger.error('could not create session folder {}'.format(session_path))
            self.logger.exception(e)
            if rec_level > 0:
                min_id = self.__get_min_id()
                cur_session = self.__create_session_folder(min_id, rec_level - 1)
            else:
                cur_session = -1
        return cur_session

    def check_folders(self):
        if not self.__check_directory(self.directory):
            self.logger.error("fail open directory " + self.directory)
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
        if session_id >= 99:
            self.logger.warning("reached max session id")
            session_id = self.__get_min_id()
            if session_id < 0:
                self.logger.error("no free session number")
            else:
                session_id = self.__create_session_folder(session_id, 0)
        else:
            session_id = self.__create_session_folder(session_id, 1)

        self.session_id = session_id
        return path.isdir(path.join(self.directory, self.session_dir_template.format(self.sesion_dir, session_id)))

    def get_session_dir(self):
        return path.join(self.directory, self.session_dir_template.format(self.sesion_dir, self.session_id))

