import wave
import math
import numpy as np

params = () #文件格式组元
step = 256 #帧长256个采样点


'''读入文件，提取数据'''
def filedata(filename):
    f = wave.open(filename, "rb")
    global params
    params = f.getparams()
    # 返回一个tuple:
    # (声道数nchannels,量化位数sampwidth(byte),采样频率framerate,采样点数nframes,...)
    # print(params)
    str_data = f.readframes(params[3])
    # readframes返回的是二进制数据（一大堆bytes，且不包含文件头)
    f.close()
    wave_data_origin = np.fromstring(str_data, dtype=np.short)
    # 根据声道数和量化单位，将读取的二进制数据转换为一个可以计算的数组
    # 由于我们的声音格式是以两个字节表示一个取样值，因此采用short数据类型转换。
    return wave_data_origin


'''计算能量'''
def energy(waveData):
    wlen = len(waveData)
    step = 256 # 每帧采样点数
    frameNum = math.ceil(wlen/step) #函数返回数字的上入整数,帧数
    ener = []
    for i in range(frameNum):
        curFrame = waveData[np.arange(i*step,min(i*step+step,wlen))]
        sum=np.longlong(0) #防止溢出
        for j in range(len(curFrame)):
            n = np.longlong(curFrame[j])**2 #np.longlong防止计算时溢出
            sum = sum + n
        ener.append(sum)
    return ener


'''符号函数'''
def sign(list):
    for i in range(len(list)):
        if list[i] >= 0:
            list[i] = 1
        else:
            list[i] = -1
    return list


'''计算过零率'''
def zero_cross_ratio(waveData):
    wlen = len(waveData)
    step = 256 #每帧采样点数
    frameNum = math.ceil(wlen/step) #函数返回数字的上入整数,帧数
    zcr = []
    for i in range(frameNum):
        curFrame = waveData[np.arange(i*step,min(i*step+step,wlen))]
        zcr.append(sum(abs(sign(curFrame[0:-1])-sign(curFrame[1::])))/(2*256))
    return zcr


'''去除静音'''
def vad(wave_data_origin, ener, enerlimit):
    wave_vad = []
    for i in range(len(ener)-1):
        if ener[i] > enerlimit:
            for j in range(256):
                wave_vad.append(wave_data_origin[i*256+j])
    return wave_vad


'''写能量文件'''
def write_ener(filename, ener):
    fw = open(filename, 'w')
    for i in range(len(ener)):
        m = "ener[" + str(i) + "] = " + str(ener[i]) + "\n"
        fw.writelines(m)
    fw.close()


'''写过零率文件'''
def write_zcr(filename, zcr):
    fw = open(filename, 'w')
    for i in range(len(zcr)):
        m = "zcr[" + str(i) + "] = " + str(zcr[i]) + "\n"
        fw.writelines(m)
    fw.close()


'''写去除静音后的语音文件'''
def write_vad(filename, wave_vad_final):
    fw = wave.open(filename,'wb')
    fw.setnchannels(params[0]) #配置声道数
    fw.setsampwidth(params[1]) #配置量化位数
    fw.setframerate(params[2]) #配置取样频率
    fw.writeframes(wave_vad_final.tostring()) #转换为二进制数据写入文件
    fw.close()


'''
去除静音主模块
filename1：需要读的文件（.wav）
filename2：需要写的文件（.wav）
'''
def remove_mute(filename1, filename2):
    wave_data = filedata(filename1)
    ener = energy(wave_data)
    enerlimit = 32500000 #能量门限
    wave_vad = vad(wave_data, ener ,enerlimit)
    wave_vad_final = np.array(wave_vad).astype(np.short)
    write_vad(filename2, wave_vad_final)

