import os
import select
import subprocess
from time import sleep

from SETUP import *
from file_writer import FileListWriter

cmd_template = "sigrok-cli -d {} {}--config samplerate={} --samples 100000000000000 -P samples512hz -B samples512hz"
scan_template = "sigrok-cli --driver {} --scan"


class LogicReader:
    def __init__(self, logger, file_list, frequency):
        self.logger = logger
        self.file_writer = FileListWriter(file_list)
        chan_str = ""
        if SALEAE_LOGIC_CHANNELS is not None:
            chan_str = "--channels {} ".format(SALEAE_LOGIC_CHANNELS)
        self.cmd = cmd_template.format(SALEAE_LOGIC_DRIVER, chan_str, frequency)
        self.logger.info(self.cmd)
        self.process = None
        self.is_ok = False

    def __write(self, data):
        self.file_writer.write(data)

    def __check_device(self):
        cmd = scan_template.format(SALEAE_LOGIC_DRIVER)
        process = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, universal_newlines=True)
        data = process.communicate()
        self.logger.info("sigrok scan result: " + str(data))
        return len(data[0]) > 0

    def __get_data(self):

        exec_env = {}
        exec_env.update(os.environ)

        # create a pipe to receive stdout and stderr from process
        (pipe_r, pipe_w) = os.pipe()
        p = subprocess.Popen(self.cmd.split(" "),
                             shell=False,
                             env=exec_env,
                             stdout=pipe_w,
                             stderr=pipe_w)

        sleep(1)
        while p.poll() is None:
            while True:
                s = select.select([pipe_r], [], [], 0)
                if len(s[0]) == 1:
                    output = os.read(pipe_r, 1024)
                    self.__write(output)
                else:
                    sleep(1)
                    break

        os.close(pipe_r)
        os.close(pipe_w)
        self.logger.info('sigrok cli output RETURN CODE ' + str(p.returncode))

    def set_up(self):
        if self.file_writer.create_list() < 1:
            self.logger.error("couldn't open files to write gps data")
            return False
        if self.__check_device():
            self.is_ok = True
            return True
        return False

    def start(self):
        if self.set_up():
            self.logger.info("start reading saleae logic")
            try:
                while True:
                    self.__get_data()
            except KeyboardInterrupt:
                self.process.kill()
                self.logger.info("finish reading saleae logic")
            except Exception as e:
                self.logger.exception(e)
            self.stop()
        else:
            self.logger.error("couldn't setup saleae logic")

    def stop(self):
        self.file_writer.close()
