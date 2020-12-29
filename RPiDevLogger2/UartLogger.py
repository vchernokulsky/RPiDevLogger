import os
import select
import subprocess
from os import path

RX = 'uart_rx_channel'
FILE = 'file_name'
BAUDRATE = 'baudrate'

cmd = 'sigrok-cli --driver saleae-logic16 --config samplerate=500k --channels 14=RX1,3=RX2 --continuous -P uart:rx=RX1:baudrate=115200,uart_logger:file_name=1.bin -P uart:rx=RX2:baudrate=115200,uart_logger:file_name=2.bin -A uart_logger'
cmd_template = 'sigrok-cli --driver saleae-logic16 --config samplerate=500k --channels {} --samples 1000000000000 {} -A uart_logger'


class UartLogger:
    def __init__(self, logger, file_manager):
        self.logger = logger
        self.file_manager = file_manager
        self.cmd = ''
        self.write_try_num = 0

    def __create_channels_arg(self, channel_list):
        channels_arg = None
        if channel_list is not None and len(channel_list) > 0:
            channels_arg = channel_list[0]
            for i in range(1, len(channel_list)):
                channels_arg = '{},{}'.format(channels_arg, channel_list[i])
        else:
            self.logger.error('uart rx channels not specified')
        return channels_arg

    def __create_decoder_arg(self, decoder_list):
        decoder_arg = None
        if decoder_list is not None and len(decoder_list) > 0:
            decoder_arg = decoder_list[0]
            for i in range(1, len(decoder_list)):
                decoder_arg = '{} {}'.format(decoder_arg, decoder_list[i])
        else:
            self.logger.error('cannot create decoder argument')
        return decoder_arg

    def crate_cmd(self):
        self.write_try_num += 1

        result = False
        channel_list = []
        decoder_list = []

        session_dir = self.file_manager.get_session_dir()
        for i in range(len(self.file_manager.uart_config)):
            num = i + 1
            cur_uart = self.file_manager.uart_config[i]
            channel_list.append('{}=RX{}'.format(cur_uart[RX], num))
            decoder_file_name = cur_uart[FILE].format(self.write_try_num)
            uart_output = path.join(session_dir, decoder_file_name)
            arg = '-P uart:rx=RX{}:baudrate={},uart_logger:file_name={}'.format(num, cur_uart[BAUDRATE], uart_output)
            decoder_list.append(arg)
        channel_arg = self.__create_channels_arg(channel_list)
        decoder_arg = self.__create_decoder_arg(decoder_list)
        if channel_arg is not None and len(channel_arg) > 0 and decoder_arg is not None and len(decoder_arg) > 0:
            self.cmd = cmd_template.format(channel_arg, decoder_arg)
            self.logger.info(self.cmd)
            result = True
        return result

    def start(self):
        running = True
        while running:
            if not self.crate_cmd():
                break
            exec_env = {}
            exec_env.update(os.environ)
            process = subprocess.Popen(self.cmd.split(" "), shell=False, env=exec_env, stdout=subprocess.PIPE,
                                       universal_newlines=True)
            count = 0
            while True:
                try:
                    exit_code = process.poll()
                    if exit_code is not None:
                        self.logger.info('finished with exit code {}'.format(exit_code))
                        if exit_code != 0:
                            running = False
                        break
                    output = process.stdout.readline()
                    if output is not None and len(output) > 0:
                        count += 1
                        # self.logger.info("{}) [{}] {}".format(count, process.returncode, process.stdout.readline()))
                except Exception as e:
                    self.logger.exception(e)
                    running = False
                    break
            process.stdout.close()





