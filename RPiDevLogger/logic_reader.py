import os
import subprocess

from SETUP import *
from file_writer import FileListWriter

cmd_template = "sigrok-cli --driver {} --channels {} --config samplerate={}k --continuous -P LogicFilter -B LogicFilter"
cmd_tee_template = "tee {} >/dev/null"
scan_template = "sigrok-cli --driver {} --scan"


class LogicReader:
    def __init__(self, logger, file_list, frequency):
        self.logger = logger
        self.file_writer = FileListWriter(file_list)
        self.cmd_logic = cmd_template.format(SALEAE_LOGIC_DRIVER, SALEAE_LOGIC_CHANNELS, int(frequency))
        self.logger.info(self.cmd_logic)
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
        while True:
            self.cmd_output = cmd_tee_template.format(self.file_writer.get_files_str())
            self.logger.info(self.cmd_output)
            cmd = "{} | {}".format(self.cmd_logic, self.cmd_output)
            exit_code = os.system(cmd)
            self.logger.info("sigrok reading finished with code {}".format(exit_code))

    def set_up(self):
        if self.file_writer.create_list() < 1:
            self.logger.error("couldn't open files to write gps data")
            return False
        if self.__check_device():
            self.is_ok = True
            return True
        return False

    def start(self):
        if self.is_ok:
            self.logger.info("start reading saleae logic")
            try:
                while True:
                    self.__get_data()
            except KeyboardInterrupt:
                self.logger.info("finish reading saleae logic")
            except Exception as e:
                self.logger.exception(e)
            self.stop()

    def stop(self):
        self.file_writer.close()
