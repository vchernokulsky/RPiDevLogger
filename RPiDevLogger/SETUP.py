import pyaudio

CONFIG_FILE = '/home/pi/RPiDevLogger/config.json'
LOG_FILE_NAME = '/home/pi/RPiDevLogger/RPiDevLogger.log'
DAT_DIR = ['/home/pi/data', '/home/pi/data1']


GPS_I2C_LINE = 1  # find with command: ls /dev | grep i2c
GPS_I2C_ADDRESS = 0x42  # find with command: sudo i2cdetect -y <GPS_I2C_LINE>
GPS_READING_INTERVAL = 0.1


SALEAE_LOGIC_DRIVER = "saleae-logic16"

# SALEAE_LOGIC_CHANNELS specify channels parameter for sigrok cli,
# use None for default settings(use all the channels available	on  a  device)
# None value is recommended to use due to driver issue
# default value usage helps to avoid channels confusion
SALEAE_LOGIC_CHANNELS = None


MICROPHONE_CHANNELS = None  # use None for default settings (read from microphone)
MICROPHONE_RATE = None  # use None for default settings (read from microphone)
MICROPHONE_SAMPLES_FOR_BUFFER = 1000
MICROPHONE_SAMPLE_SIZE = pyaudio.paInt16  # 16-bit resolution

UART_READING_INTERVAL = 0.1
UART_CONFIG = [
    {
        "id": 1,
        "port": "/dev/ttyACM0",
        "baudrate": 115200
    },
    {
        "id": 2,
        "port": "/dev/ttyUSB0",
        "baudrate": 115200
    }
]
