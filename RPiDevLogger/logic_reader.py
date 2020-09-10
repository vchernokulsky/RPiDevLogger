import subprocess

from SETUP import *
from file_writer import FileListWriter

cmd_template = "sigrok-cli --driver {} -c samplerate={}k --channels {} --continuous"
scan_template = "sigrok-cli --driver {} --scan"


class LogicReader:
    def __init__(self, logger, file_list, frequency):
        self.logger = logger
        self.file_writer = FileListWriter(file_list)
        self.cmd = cmd_template.format(SALEAE_LOGIC_DRIVER, int(frequency), SALEAE_LOGIC_CHANNELS)
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
        # self.logger.info(self.cmd)
        self.process = subprocess.Popen(self.cmd.split(" "),
                                        stdout=subprocess.PIPE,
                                        universal_newlines=True)
        while True:
            data = self.process.stdout.readline()
            self.__write(data)
            return_code = self.process.poll()
            if return_code is not None:
                # self.logger.info('sigrok cli output RETURN CODE ' + str(return_code))
                # Process has finished, read rest of the output
                for output in self.process.stdout.readlines():
                    self.__write(output)
                break

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
                self.process.kill()
                self.logger.info("finish reading saleae logic")
            except Exception as e:
                self.logger.exception(e)
            self.stop()

    def stop(self):
        self.file_writer.close()
