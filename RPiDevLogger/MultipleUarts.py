from UartReader import UartReader
from multiprocessing import Process


class MultipleUarts:

    def __init__(self, logger, uart_config_list):
        self.uart_readers = []
        self.uart_processes = []
        for uart_config in uart_config_list:
            uart_reader = UartReader(logger, uart_config)
            self.uart_readers.append(uart_reader)
            uart_proc = Process(target=uart_reader.start, args=())
            self.uart_processes.append(uart_proc)

    def start(self):
        for uart_proc in self.uart_processes:
            uart_proc.start()

    def join(self):
        for proc in self.uart_processes:
            proc.join()

    def stop(self):
        for uart in self.uart_readers:
            uart.stop()
