import sigrokdecode as srd
from functools import reduce
IDLE = 0
SAVE = 1
WRITE = 2

# sudo cp -r LogicFilter/ /usr/share/libsigrokdecode/decoders/
# sigrok-cli -d demo --channels D0,D1,D2,D3,D4,D5,D6,D7 --config samplerate=100 --time 1000 -P LogicFilter -B LogicFilter > example.log

OUTPUT_FREQUENCY = 512

class Decoder(srd.Decoder):
    api_version = 3
    id = 'samples512hz'
    name = 'samples512hz'
    longname = 'saleae logic decoder'
    desc = 'samples512hz decoder reduce signal to 512hz'
    license = 'mit'
    inputs = ['logic']
    outputs = ['samples512hz']
    tags = ['Embedded/industrial']
    channels = (
        {'id': 'd0', 'name': 'D0', 'desc': 'Data'},
        {'id': 'd1', 'name': 'D1', 'desc': 'Data'},
        {'id': 'd2', 'name': 'D2', 'desc': 'Data'},
        {'id': 'd3', 'name': 'D3', 'desc': 'Data'},
        # {'id': 'd4', 'name': 'D4', 'desc': 'Data'},
        # {'id': 'd5', 'name': 'D5', 'desc': 'Data'},
        # {'id': 'd6', 'name': 'D6', 'desc': 'Data'},
        # {'id': 'd7', 'name': 'D7', 'desc': 'Data'},
    )
    annotations = (
       ('sample', 'SampleCaptured'),

    )
    annotation_rows = (
        ('sample', 'SampleCaptured', (0,)),
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
            self.freq_num = int(value / OUTPUT_FREQUENCY)

    def write(self, pins, sample_id):

        bit_tuple = pins + (0, 0, 0, 0)
        bit_int = reduce(lambda a, b: (a << 1) | b, reversed(bit_tuple))
        ann_str = "{}) {} {}".format(sample_id, str(bit_tuple), bit_int)
        self.put(sample_id, sample_id, self.out_ann, [0, [ann_str, ""]])
        self.put(sample_id, sample_id, self.out_binary, [0, bytes([bit_int])])

    def write_first(self):
        sample_id = round(len(self.sample_buf) / 2)
        bit_tuple = self.sample_buf[sample_id]
        self.cur_id = self.start_num + sample_id
        self.write(bit_tuple, self.cur_id)

    def decode(self):

        start_cond = [{i: 'h'} for i in range(len(Decoder.channels))]
        pins = self.wait(start_cond)
        ch_idx = pins.index(1)
        self.start_num = self.samplenum
        self.sample_buf = [pins]

        while True:
            pins = self.wait({'skip': 1})
            if pins[ch_idx] == 1:
                self.sample_buf.append(pins)
            else:
                self.write_first()
                self.end_id = self.samplenum
                break

        while True:
            if self.end_id - self.cur_id == self.freq_num:
                self.write(pins, self.end_id)
                break
            elif self.end_id - self.cur_id > self.freq_num:
                self.cur_id += self.freq_num
                sample = self.sample_buf[self.cur_id - self.start_num]
                self.write(sample, self.cur_id)
            else:
                skip_count = self.cur_id + self.freq_num - self.end_id
                pins = self.wait({'skip': skip_count})
                self.write(pins, self.samplenum)
                break

        while True:
            pins = self.wait({'skip': self.freq_num})
            self.write(pins, self.samplenum)
