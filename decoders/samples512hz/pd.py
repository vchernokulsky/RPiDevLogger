import sigrokdecode as srd
from functools import reduce


# sudo cp -r samples512hz/ /usr/share/libsigrokdecode/decoders/
# sigrok-cli -d demo --channels D0,D1,D2,D3 --config samplerate=100k --time 1000 -P samples512hz -B samples512hz > example.log

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
        {'id': 'd4', 'name': 'D4', 'desc': 'Data'},
        {'id': 'd5', 'name': 'D5', 'desc': 'Data'},
        {'id': 'd6', 'name': 'D6', 'desc': 'Data'},
        {'id': 'd7', 'name': 'D7', 'desc': 'Data'},
        {'id': 'd8', 'name': 'D8', 'desc': 'Data'},
        {'id': 'd9', 'name': 'D9', 'desc': 'Data'},
        {'id': 'd10', 'name': 'D10', 'desc': 'Data'},
        {'id': 'd11', 'name': 'D11', 'desc': 'Data'},
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
        self.out_ann = None
        self.out_binary = None
        self.first_start_num = 0
        self.first_end_num = 0
        self.cur_num = 0
        self.main_ch_idx = -1
        self.freq_num = 1
        self.sample_buf = []

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.out_binary = self.register(srd.OUTPUT_BINARY)

    def reset(self):
        self.first_start_num = 0
        self.first_end_num = 0
        self.cur_num = 0
        self.main_ch_idx = -1
        self.freq_num = 1
        self.sample_buf = []

    def metadata(self, key, value):
        if key == srd.SRD_CONF_SAMPLERATE:
            self.freq_num = int(value / OUTPUT_FREQUENCY)

    def write(self, pins, sample_id):
        bit_tuple = pins + (0, 0, 0, 0)
        bit_int = reduce(lambda a, b: (a << 1) | b, reversed(bit_tuple))
        ann_str = "{}) {} {}".format(sample_id, str(bit_tuple), bit_int)
        self.put(sample_id, sample_id, self.out_ann, [0, [ann_str, ""]])
        self.put(sample_id, sample_id, self.out_binary, [0, bit_int.to_bytes(2, byteorder='little')])

    def find_start_of_first(self):
        start_cond = [{i: 'h'} for i in range(len(Decoder.channels))]
        pins = self.wait(start_cond)
        self.main_ch_idx = pins.index(1)
        self.sample_buf = [pins]
        return self.samplenum

    def find_end_of_first(self):
        while True:
            pins = self.wait({'skip': 1})
            if pins[self.main_ch_idx] == 1:
                self.sample_buf.append(pins)
            else:
                return self.samplenum, pins

    def find_first_sample(self):
        sample_id = round(len(self.sample_buf) / 2)
        bit_tuple = self.sample_buf[sample_id]
        return self.first_start_num + sample_id, bit_tuple

    def check_buffer_for_samples(self):
        while self.first_end_num - self.cur_num > self.freq_num:
            self.cur_num += self.freq_num
            sample = self.sample_buf[self.cur_num - self.first_start_num]
            self.write(sample, self.cur_num)

    def got_to_freq_mode(self, last_pins):
        if self.first_end_num - self.cur_num == self.freq_num:
            self.write(last_pins, self.first_end_num)
        else:
            skip_count = self.cur_num + self.freq_num - self.first_end_num
            pins = self.wait({'skip': skip_count})
            self.write(pins, self.samplenum)

    def decode(self):

        self.first_start_num = self.find_start_of_first()
        self.first_end_num, first_end_sample = self.find_end_of_first()
        self.cur_num, cur_sample = self.find_first_sample()
        self.write(cur_sample, self.cur_num)

        self.check_buffer_for_samples()
        self.got_to_freq_mode(first_end_sample)

        while True:
            pins = self.wait({'skip': self.freq_num})
            self.write(pins, self.samplenum)
