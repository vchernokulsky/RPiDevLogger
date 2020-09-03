import subprocess

from file_writer import FileListWriter

DRIVER = "fx2lafw"
RATE = 500
CHANNELS = "D0,D1,D2,D3,D4,D5,D6,D7"

cmd = "sigrok-cli --driver {} -c samplerate={}k --channels {} --continuous".format(DRIVER, RATE, CHANNELS)


class LogicReader:
    def __init__(self, logger, file_list):
        self.logger = logger
        self.file_writer = FileListWriter(file_list)

    def __write(self, data):
            self.file_writer.write(data)

    def __get_data(self):
        process = subprocess.Popen(cmd.split(" "),
                                   stdout=subprocess.PIPE,
                                   universal_newlines=True)
        while True:
            data = process.stdout.readline()
            self.__write(data)
            return_code = process.poll()
            if return_code is not None:
                self.logger.info('sigrok cli output RETURN CODE ' + str(return_code))
                # Process has finished, read rest of the output
                for output in process.stdout.readlines():
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
            self.logger.info("finish reading saleae logic")
        except Exception as e:
            self.logger.exception(e)
        self.stop()

    def stop(self):
        self.file_writer.close()


