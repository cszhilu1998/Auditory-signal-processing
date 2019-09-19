import wave
import numpy as np
import struct
params = ()  #文件格式组元
u = 0.91  # 系数权值

'''读入文件，提取数据'''
def filedata(filename):
    f = wave.open(filename, "rb")
    global params
    params = f.getparams()
    # 返回一个tuple:
    # (声道数nchannels,量化位数sampwidth(byte),采样频率framerate,采样点数nframes,...)
    str_data = f.readframes(params[3])
    # readframes返回的是二进制数据（一大堆bytes，且不包含文件头)
    f.close()
    wave_data_origin = np.fromstring(str_data, dtype=np.short)
    # 根据声道数和量化单位，将读取的二进制数据转换为一个可以计算的数组
    # 由于我们的声音格式是以两个字节表示一个取样值，因此采用short数据类型转换。
    return wave_data_origin

'''量化'''
def quantification(x, a):
    if x > 7*a:
        final_code = 7.5
    elif x < -7*a:
        final_code = -7.5
    else:
        for j in range(-8,8):
            if x>(j-1)*a and x<=j*a:
                final_code = (2*j-1)/2
                break
    final_code = final_code+7.5
    return final_code

'''解码'''
def decode(code, a):
    length = len(code)
    decode = list(range(length))
    decode[0] = np.longlong(code[0])
    for i in range(length-1):
        decode[i+1] = np.longlong(decode[i])*u +(code[i+1]-7.5)*a
    return decode

'''dpcm编码'''
def dpcm(waveData, a):
    length = len(waveData)
    code = list(range(length))
    decode = list(range(length))
    code[0] = waveData[0]
    decode[0] = waveData[0]
    for i in range(length-1):
        code[i+1] = waveData[i+1] - decode[i]*u  # 编码
        code[i+1] = quantification(code[i+1], a)  # 量化
        decode[i+1] = decode[i]*u + (code[i+1]-7.5)*a  # 解码，用于反馈
    return code

'''封装编码数据，打包'''
def package(code):
    length = len(code)
    w = np.int8(np.ones(length//2))*int('11111111', 2)
    for i in range(1, length-1, 2):
        tmp = w[i//2] & np.int8(code[i])
        tmp = tmp << 4
        w[i//2] = tmp | np.int8(code[i+1])
    return w

'''保存dpc文件'''
def savetofile_dpc(filename, w, code):
    fw = open(filename, 'wb')
    fw.write(struct.pack('h',code[0]))  # 转换为字节流
    for i in range(len(w)):
        bytes = struct.pack('B',w[i])
        fw.write(bytes)
    fw.close()

'''读取编码文件，进行解码'''
def readencode(filename):
    code = []
    with open(filename,'rb') as f:
        a = struct.unpack('h',f.read(2))  # 前两个字节为第一个采样点值
        code.append(a[0])
        while True:
            ff = f.read(1)  # 按字节读
            if not ff:  # 文件末尾
                break
            else:
                a = struct.unpack('B',ff)  # 字节流转换，返回一个元组
                code.append(a[0])
    finalcode = []
    finalcode.append(code[0])
    for i in range(len(code)-1):
        finalcode.append(code[i+1]//16)  # 前4位
        finalcode.append(code[i+1]%16)  # 后4位
    return finalcode


'''写去除静音后的pcm语音文件'''
def savetofile_pcm(filename,code):
    fw = wave.open(filename,'wb')
    fw.setnchannels(1) #配置声道数
    fw.setsampwidth(2) #配置量化位数
    fw.setframerate(params[2]) #配置取样频率
    fw.writeframes(np.array(code).astype(np.short).tostring()) #转换为二进制数据写入文件
    fw.close()

'''计算信噪比'''
def snr(data1, data2):
    length = len(data1)
    sum1 = np.longlong(0)
    sum2 = np.longlong(0)
    for i in range(length-1):
        n1 = np.longlong(data1[i])**2/length #np.longlong防止计算时溢出
        sum1 = sum1 + n1
        n2 = np.longlong(data1[i]-data2[i])**2/length
        sum2 = sum2 + n2
    return 10*np.log10(sum1/sum2)

'''主模块'''
for i in range(1,2,1):
    a = 869  # 量化因子
    filename = '1.wav'
    filename_dpc = '1.dpc'
    filename_pcm = '1.pcm'

    waveData = filedata(filename)  # 读取数据
    m = dpcm(waveData, a)  # 编码
    savetofile_dpc(filename_dpc, package(m), m)  # 存dpc压缩文件

    d = decode(readencode(filename_dpc), a)  # 读dpc文件，解码
    savetofile_pcm(filename_pcm, d)  # 写解码后的pcm文件

    print(a)  # 量化因子
    print(snr(d, waveData))  # 信噪比

