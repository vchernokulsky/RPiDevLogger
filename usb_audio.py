import sys
import pyaudio
import queue
import wave

audio = None

form_1 = pyaudio.paInt16  # 16-bit resolution
chans = 1  # 1 channel
samp_rate = 44100  # 44.1kHz sampling rate
chunk = 4096  # 2^12 samples for buffer

wav_output_filename = 'test1.wav'  # name of .wav file

q = queue.Queue()


def find_usb_idx(audio):
    usb = 'USB'
    usb_ix = -1
    for ii in range(audio.get_device_count()):
        name = audio.get_device_info_by_index(ii).get('name')
        print('%d) %s' % (ii, name))
        if name.find(usb) >= 0:
            usb_ix = ii
    return usb_ix


def callback(in_data, frame_count, time_info, status):
    global audio
    print('callback')
    if status:
        print(status, file=sys.stderr)
    print('puting')
    print(type(in_data))
    q.put(in_data)
    print('put')
    return in_data, pyaudio.paContinue


def create_wave(filename):
    wavefile = wave.open(filename, 'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    return wavefile


def main():
    audio = pyaudio.PyAudio()  # create pyaudio instantiation
    dev_index = find_usb_idx(audio)
    if dev_index < 0:
        print("couldn't find USB audio device")
        return

    wavefile = create_wave(wav_output_filename)

    stream = audio.open(format=form_1, rate=samp_rate, channels=chans,
                        input_device_index=dev_index, input=True,
                        frames_per_buffer=chunk, stream_callback=callback)
    stream.start_stream()

    print("recording")

    try:
        while True:
            print('getting')
            data = q.get()
            print('read ' + str(len(data)))
            wavefile.writeframes(data)
    except KeyboardInterrupt:
        print("finished recording")
    except Exception as e:
        print(e)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        wavefile.close()


if __name__ == "__main__":
    main()
