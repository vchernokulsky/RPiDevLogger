import subprocess

from SETUP import *
from file_writer import FileListWriter

cmd_template = "sigrok-cli --driver {} -c samplerate={}k --channels {} --continuous"


class LogicReader:
    def __init__(self, logger, file_list, frequency):
        self.logger = logger
        self.file_writer = FileListWriter(file_list)
        self.cmd = cmd_template.format(SALEAE_LOGIC_DRIVER, int(frequency), SALEAE_LOGIC_CHANNELS)
        self.logger.info(self.cmd)
        self.process = None

    def __write(self, data):
        self.file_writer.write(data)

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
        ret = True
        if self.file_writer.create_list() < 1:
            self.logger.error("couldn't open files to write gps data")
            ret = False
        return ret

    def start(self):
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
