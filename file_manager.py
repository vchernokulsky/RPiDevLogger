import os
from os import path
import shutil


def get_free_memory_gb():
    total, used, free = shutil.disk_usage("/")
    return used // (2 ** 30)


def check_directory(dir):
    ret = True
    if not path.isdir(dir):
        try:
            os.mkdir(dir)
        except OSError as e:
            ret = False
            print("Creation of the directory %s failed" % dir)
            print(e)
        else:
            print("Successfully created the directory %s " % dir)
    else:
        print(dir + " exist")
    return ret


class FileManager:
    def __init__(self, min_mem, rm_koef):
        self.min_memory = min_mem
        self.rm_koef = rm_koef
        self.directories = ['/home/pi/data', '/home/pi/data1']
        self.file_template = ['{:02d}_logic.log', '{:02d}_GPS.log', '{:02d}_audio.wav']

    def memory_enough(self):
        total, used, free = shutil.disk_usage("/")
        print("Total: %d GiB" % (total // (2 ** 30)))
        print("Used: %d GiB" % (used // (2 ** 30)))
        print("Free: %d GiB" % (free // (2 ** 30)))

        if free < self.min_memory:
            return False
        else:
            return True

    def clear_memory(self):
        print("memory clearing...")
        for i in range(100):
            for dir in self.directories:
                for file in self.file_template:
                    file_path = path.join(dir, file.format(i))
                    if path.isfile(file_path):
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            print(e)
                            return
            if get_free_memory_gb() > self.rm_koef * self.min_memory:
                break

    def check_folders(self):
        for directory in self.directories:
            if not check_directory(directory):
                print("fail open directory " + directory)
                return False
        return True

    def check_memory(self):
        if not self.memory_enough():
            print("not enough free space")
            self.clear_memory()
            if not self.memory_enough():
                print("can not remove enough files")
                return False
        return True

