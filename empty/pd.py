import sigrokdecode as srd

IDLE = 0
SAVE = 1
WRITE = 2

class Decoder(srd.Decoder):
    api_version = 2
    id = 'empty'
    name = 'empty'
    longname = 'empty decoder'
    desc = 'Empty decoder that can be loaded by sigrok.'
    license = 'mit'
    inputs = ['logic']
    outputs = ['empty']
    tags = ['Embedded/industrial']
    channels = (
        {'id': 'd0', 'name': 'D0', 'desc': 'Clock'},
        {'id': 'd1', 'name': 'D1', 'desc': 'Data'},
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
        self.state = IDLE
        self.sample_buf = []
        self.start_num = 0

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.out_binary = self.register(srd.OUTPUT_BINARY)

    def reset(self):
        pass

    def set_to_save(self, pins):
        self.start_num = self.samplenum
        self.sample_buf = [pins]
        self.state = SAVE

    def save(self, pins):
        self.sample_buf.append(pins)

    def write(self):
        self.state = IDLE
        sample_avg = round(len(self.sample_buf) / 2)
        print(self.sample_buf[sample_avg])
        self.put(self.start_num, self.samplenum, self.out_ann, [0, [""]])
        self.put(self.start_num + sample_avg, self.start_num + sample_avg, self.out_ann, [1, [""]])
        self.put(self.start_num + sample_avg, self.start_num + sample_avg,
                 self.out_binary, (0, self.sample_buf[sample_avg]))

    def decode(self, ss, es, data):
        for (self.samplenum, pins) in data:
            if self.state == IDLE:
                if pins[0] == 1:
                    self.set_to_save(pins)
            elif self.state == SAVE:
                if pins[0] == 1:
                    self.save(pins)
                else:
                    self.write()

    # def decode(self):
    #     while True:
    #         if self.state == IDLE:
    #             pins = self.wait({0: 'h'})
    #             print(pins)
    #             self.set_to_save(pins)
    #         elif self.state == SAVE:
    #             pins = self.wait([{0: 'h'}, {0: 'l'}])
    #             if pins[0] == 1:
    #                 self.save(pins)
    #             else:
    #                 self.write()
