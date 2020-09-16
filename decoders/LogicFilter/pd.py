import sigrokdecode as srd
from functools import reduce
IDLE = 0
SAVE = 1
WRITE = 2

# sudo cp -r LogicFilter/ /usr/share/libsigrokdecode/decoders/
# sigrok-cli -d demo --channels D0,D1,D2,D3,D4,D5,D6,D7 --config samplerate=100 --time 1000 -P LogicFilter -B LogicFilter > example.log


class Decoder(srd.Decoder):
    api_version = 3
    id = 'LogicFilter'
    name = 'LogicFilter'
    longname = 'LogicFilter decoder'
    desc = 'LogicFilter decoder that can be loaded by sigrok.'
    license = 'mit'
    inputs = ['logic']
    outputs = ['LogicFilter']
    tags = ['Embedded/industrial']
    channels = (
        {'id': 'd0', 'name': 'D0', 'desc': 'Clock'},
        {'id': 'd1', 'name': 'D1', 'desc': 'Data'},
        {'id': 'd2', 'name': 'D2', 'desc': 'Data'},
        {'id': 'd3', 'name': 'D3', 'desc': 'Data'},
        {'id': 'd4', 'name': 'D4', 'desc': 'Data'},
        {'id': 'd5', 'name': 'D5', 'desc': 'Data'},
        {'id': 'd6', 'name': 'D6', 'desc': 'Data'},
        {'id': 'd7', 'name': 'D7', 'desc': 'Data'},
    )
    annotations = (
        ('data', 'DataPart'), ('sample', 'SampleCaptured')

    )
    annotation_rows = (
        ('data', 'Data Part', (0,)), ('sample', 'SampleCaptured', (1,))
    )
    binary = (
        ('sample', 'SampleAvg'),
    )

    def __init__(self):
        self.samplerate = None
        self.reset()

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.out_binary = self.register(srd.OUTPUT_BINARY)

    def reset(self):
        self.samplerate = None
        self.state = IDLE
        self.sample_buf = []
        self.start_num = 0

    def metadata(self, key, value):
        if key == srd.SRD_CONF_SAMPLERATE:
            self.samplerate = value

    def set_to_save(self, pins):
        self.start_num = self.samplenum
        self.state = SAVE

    def save(self, pins):
        self.sample_buf.append(pins)
        self.wait({'skip': 1})

    def write(self):
        self.state = IDLE
        sample_id = round(len(self.sample_buf) / 2)
        bit_tuple = self.sample_buf[sample_id]
        bit_int = reduce(lambda a, b: (a << 1) | b, bit_tuple)
        self.put(self.start_num, self.samplenum, self.out_ann, [0, [str(bit_tuple),""]])
        self.put(self.start_num + sample_id, self.start_num + sample_id, self.out_ann, [1, [str(bit_int), ""]])
        self.put(self.start_num + sample_id, self.start_num + sample_id,
                 self.out_binary, [0, bytes([bit_int])])

    def decode(self):
        while True:
            if self.state == IDLE:
                pins = self.wait({0: 'h'})
                self.set_to_save(pins)
            elif self.state == SAVE:
                pins = self.wait([{0: 'l'}, {0: 'h'}])
                if pins[0] == 1:
                    self.save(pins)
                else:
                    self.write()
