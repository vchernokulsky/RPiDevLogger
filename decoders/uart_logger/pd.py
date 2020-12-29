import sigrokdecode as srd

# sigrok-cli --driver saleae-logic16 --config samplerate=500k --channels 14=RX,3 --continuous
# -P uart:rx=RX,uart_logger:file_name=1.bin
# -P uart:rx=3,uart_logger:file_name=2.bin
# -A uart_logger


class Decoder(srd.Decoder):
    api_version = 3
    id = 'uart_logger'
    name = 'uart_logger'
    longname = 'uart_logger'
    desc = 'uart_logger'
    license = 'lgpl'
    inputs = ['uart']
    outputs = []
    tags = ['Embedded/industrial']
    options = (
        {'id': 'file_name', 'desc': 'binary file to save data from uart', 'default': ''},
    )
    annotations = (
        ('b', 'byte'),
        ('n', 'num'),

    )
    annotation_rows = (
        ('byte_output', 'ReadBytesOutput', (0, )),
        ('num_output', 'ReadNumOutput', (1, )),
    )

    def __init__(self):
        self.filename = ''
        self.count = 0
        self.out_ann = None
        self.file = None

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.count = 0
        self.filename = self.options['file_name']
        if self.filename is None or len(self.filename) <= 0:
            raise Exception('specify file_name option')
        self.file = open(self.filename, 'wb', buffering=0)

    def put_char(self, bit):
        self.put(self.count, self.count, self.out_ann, [0, [bit]])

    def put_num(self, num):
        self.put(self.count, self.count, self.out_ann, [1, [str(num)]])

    def decode(self, ss, es, data):
        self.count += 1
        ptype, rxtx, pdata = data
        if ptype != 'DATA':
            return
        num = pdata[0]
        self.put_num(num)
        self.put_char(chr(num))
        try:
            self.file.write(bytes([num]))
        except Exception as e:
            print(e)
