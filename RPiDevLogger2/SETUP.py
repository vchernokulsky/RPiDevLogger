LOG_FILE_NAME = '/home/pi/RPiDevLogger2/RPiDevLogger.log'
DAT_DIR = '/home/pi/RPiDevLogger2'
SESSION_DIR_NAME = 'RPiDevLogger_Session'

MIN_FREE_SPACE_GB = 1.0
FILE_REMOVE_KOEF = 5.0

DECODER_CONFIG = [
    {
        'uart_rx_channel': 0,
        'file_name': 'uart0.bin',
        'baudrate': 115200
    },
    {
        'uart_rx_channel': 1,
        'file_name': 'uart1.bin',
        'baudrate': 115200
    },
    {
        'uart_rx_channel': 2,
        'file_name': 'uart2.bin',
        'baudrate': 115200
    },
    {
        'uart_rx_channel': 3,
        'file_name': 'uart3.bin',
        'baudrate': 115200
    },
    {
        'uart_rx_channel': 4,
        'file_name': 'uart4.bin',
        'baudrate': 115200
    },
    {
        'uart_rx_channel': 5,
        'file_name': 'uart5.bin',
        'baudrate': 115200
    },

]

