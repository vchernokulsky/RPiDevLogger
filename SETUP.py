import pyaudio

CONFIG_FILE = 'config.json'
LOG_FILE_NAME = 'RPiDevLogger.log'
DAT_DIR = ['/home/pi/data', '/home/pi/data1']

GPS_SERIAL_PORT = "/dev/ttyACM0"
GPS_BAUDRATE = 9600

SALEAE_LOGIC_DRIVER = "fx2lafw"
SALEAE_LOGIC_CHANNELS = "D0,D1,D2,D3,D4,D5,D6,D7"


MICROPHONE_CHANNELS = None  # use None for default settings (read from microphone)
MICROPHONE_RATE = None  # use None for default settings (read from microphone)
MICROPHONE_SAMPLES_FOR_BUFFER = 1000
MICROPHONE_SAMPLE_SIZE = pyaudio.paInt16  # 16-bit resolution
