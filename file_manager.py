import os
from os import path
import shutil


def get_free_memory_gb():
    total, used, free = shutil.disk_usage("/")
    return used // (2 ** 30)


class FileManager:
    def __init__(self, logger, min_mem, rm_koef):
        self.logger = logger
        self.min_memory = min_mem
        self.rm_koef = rm_koef
        self.directories = ['/home/pi/data', '/home/pi/data1']
        self.file_template = ['{:02d}_logic.log', '{:02d}_GPS.log', '{:02d}_audio.wav']

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
        for i in range(100):
            for dir in self.directories:
                for file in self.file_template:
                    file_path = path.join(dir, file.format(i))
                    if path.isfile(file_path):
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            self.logger.exception(e)
                            return
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
        for i in range(99, -1, -1):
            id_exist = False
            for dir in self.directories:
                for file in self.file_template:
                    file_path = path.join(dir, file.format(i))
                    if path.isfile(file_path):
                        id_exist = True
                        break
                if id_exist:
                    break
            if id_exist:
                last_session = i
                break
        return last_session + 1

    def __get_min_id(self):
        session_id = -1
        for i in range(99):
            id_exist = False
            for dir in self.directories:
                for file in self.file_template:
                    file_path = path.join(dir, file.format(i))
                    if path.isfile(file_path):
                        id_exist = True
                        break
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
        if session_id > 99:
            self.logger.warning("reached max session id")
            session_id = self.__get_min_id()
            if session_id < 0:
                self.logger.error("no free session number")
        return session_id





