import sys
import pyaudio
import queue
import wave

form_1 = pyaudio.paInt16  # 16-bit resolution
chunk = 1000  # 2^12 samples for buffer

CHANNELS = None
RATE = None


class UsbAudio:
    def __init__(self, logger, file_list):
        self.logger = logger
        self.file_list = file_list

        self.q = queue.Queue()
        self.audio = pyaudio.PyAudio()  # create pyaudio instantiation
        self.dev_index, self.chans, self.samp_rate = self.__microphone_setup()
        self.logger.info("Microphone default values")
        self.logger.info("index:{}\tchans:{}\tsample_rate:{}".format(self.dev_index, self.chans, self.samp_rate))
        if CHANNELS is not None:
            self.chans = CHANNELS
        if RATE is not None:
            self.samp_rate = RATE
        self.logger.info("used values")
        self.logger.info("index:{}\tchans:{}\tsample_rate:{}".format(self.dev_index, self.chans, self.samp_rate))
        self.wave_list = []
        self.stream = None

    def __find_usb_idx(self):
        usb = 'USB'
        usb_ix = -1
        for ii in range(self.audio.get_device_count()):
            name = self.audio.get_device_info_by_index(ii).get('name')
            self.logger.info('{}) {}'.format(ii, name))
            if name.find(usb) >= 0:
                usb_ix = ii
        return usb_ix

    def __microphone_setup(self):
        dev_index = self.__find_usb_idx()
        chans = 0
        rate = 0
        if dev_index < 0:
            self.logger.error("couldn't find USB audio device")
        else:
            audio_device = self.audio.get_device_info_by_index(dev_index)
            chans_key = "maxInputChannels"
            rate_key = "defaultSampleRate"
            if chans_key in audio_device and rate_key in audio_device:
                chans = audio_device.get(chans_key)
                rate = audio_device.get(rate_key)
        try:
            chans = int(chans)
            rate = int(rate)
        except Exception as e:
            self.logger.exception(e)
        return dev_index, chans, rate

    def __create_wave(self, filename):
        wavefile = wave.open(filename, 'wb')
        wavefile.setnchannels(self.chans)
        wavefile.setsampwidth(self.audio.get_sample_size(form_1))
        wavefile.setframerate(self.samp_rate)
        return wavefile

    def __wave_list_create(self):
        for file in self.file_list:
            wv = self.__create_wave(file)
            self.wave_list.append(wv)

    def __wave_list_write(self, data):
        for wv in self.wave_list:
            wv.writeframes(data)

    def __wave_list_close(self):
        for wv in self.wave_list:
            wv.close()

    def write_to_files(self):
        try:
            while True:
                data = self.q.get()
                self.__wave_list_write(data)
        except KeyboardInterrupt:
            self.logger.info("finished recording")
        except Exception as e:
            self.logger.exception(e)

    def set_up(self):
        if self.dev_index < 0:
            self.logger.error("no dev index")
            return False
        if self.chans < 1:
            self.logger.error("no input channels")
            return False
        if self.samp_rate < 1:
            self.logger.error("no default sample rate")
            return False
        self.__wave_list_create()
        if len(self.wave_list) < 1:
            self.logger.error("couldn't create waves to write audio")
            return False
        try:
            self.stream = self.audio.open(format=form_1, rate=self.samp_rate, channels=self.chans,
                                          input_device_index=self.dev_index, input=True,
                                          frames_per_buffer=chunk, stream_callback=self.callback)
        except (ValueError, IOError) as err:
            self.logger.exception(err)
            return False
        return True

    def start(self):
        self.stream.start_stream()
        self.logger.info("start recording")
        self.write_to_files()

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.__wave_list_close()

    def callback(self, in_data, frame_count, time_info, status):
        if status:
            self.logger.warning("audio stream status " + str(status))
        self.q.put(in_data)
        return in_data, pyaudio.paContinue
