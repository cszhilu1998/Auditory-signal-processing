import wave
from pyaudio import PyAudio,paInt16
import sys

framerate = 44100  # 频率
NUM_SAMPLES = 1024  # 缓存快大小
channels = 2  # 声道
sampwidth = 2  # 量化字长
RECORD_SECONDS = 3  # 时间3s


'''保存录音文件'''
def save_wave_file(filename,data):
    wf = wave.open(filename,'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(data))
    wf.close()
    print('文件已保存在 '+filename)


'''录音'''
def my_record(filename):
    pa = PyAudio()
    stream = pa.open(format=paInt16, channels=2, rate=framerate, input=True, frames_per_buffer=NUM_SAMPLES)
    my_buf = []
    for i in range(0, int(framerate/NUM_SAMPLES*RECORD_SECONDS)):#控制录音时间
        string_audio_data = stream.read(NUM_SAMPLES)
        my_buf.append(string_audio_data)
        sys.stdout.write('. ')
        sys.stdout.flush()
    save_wave_file(filename,my_buf)
    stream.close()


'''播放录音'''
def play(filename):
    wf = wave.open(filename,'rb')
    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
    while True:
        data = wf.readframes(NUM_SAMPLES)
        if data == b'':
            break
        stream.write(data)
    stream.close()
    p.terminate()


