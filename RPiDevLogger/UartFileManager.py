import glob
import os
from os import path


class UartFileManager:

    template = "{:02d}_uart{}.log"

    def __init__(self, logger):
        self.logger = logger

    def delete_files(self, session_id, directory):
        file_mask = path.join(directory, self.template.format(session_id, '*'))
        for file in glob.glob(file_mask):
            if path.isfile(file):
                try:
                    os.remove(file)
                except Exception as e:
                    self.logger.exception(e)

    def exists(self, session_id, directory):
        file_mask = path.join(directory, self.template.format(session_id, '*'))
        return len(glob.glob(file_mask)) > 0

    def get_file_name(self, session_id, directory, uart_num):
        file_name = path.join(directory, self.template.format(session_id, uart_num))
        return file_name
