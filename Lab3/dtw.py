import numpy as np
import struct
import sys
import librosa


'''读取.mfc二进制文件'''
def readmfcc(filename):
    fid = open(filename, 'rb')
    nframes,frate,nbytes,feakind = struct.unpack('>IIHH',fid.read(12))
    '''
    nframes: number of frames 采样点数
    frate: frame rate in 100 nano-seconds unit
    nbytes: number of bytes per feature value
    feakind: 9 is USER
    '''
    #print(nframes,frate,nbytes,feakind)
    ndim = nbytes//4  # feature dimension(4 bytes per value) 39维度

    mfcc0 = np.empty((nframes,ndim))
    for i in range(nframes):
        for j in range(ndim):
            mf = fid.read(4)
            c = struct.unpack('>f',mf)
            mfcc0[i][j] = c[0]
    fid.close()
    return mfcc0


'''
dtw算法
wavedata1: mfc文件1
wavedata2: mfc文件2
'''
def dtw(wavedata1, wavedata2):
    # 初始化
    len1 = len(wavedata1)
    len2 = len(wavedata2)
    D = np.empty((len1+1,len2+1))  # 记录代价
    P = np.empty((len1+1,len2+1,2))  # 记录路径
    D[0][0] = 0
    P[0][0] = [0, 0]
    for i in range(1,len1+1):
        D[i][0] = sys.maxsize
    for j in range(1,len2+1):
        D[0][j] = sys.maxsize
    # 计算
    for i in range(1,len1+1):
        for j in range(1,len2+1):
            d = euclidean(wavedata1[i-1], wavedata2[j-1])  # 欧氏距离
            a1 = 2*d + D[i-1][j-1]
            a2 = d + D[i-1][j]
            a3 = d + D[i][j-1]
            minD = min(a1, a2, a3)
            if minD == a1:
                P[i][j] = [i-1, j-1]
            elif minD == a2:
                P[i][j] = [i-1, j]
            else:
                P[i][j] = [i, j-1]
            D[i][j] = minD
    # 回溯路径
    w = 0
    m = P[len1][len2]
    while True:
        pm = P[int(m[0])][int(m[1])]
        if pm[0]+1 == m[0] and pm[1]+1 == m[0]:
            w += 2
        else:
            w += 1
        if pm[0] == 0 and pm[1] == 0:
            break
        m = pm
    return D[len1][len2]/w


'''欧氏距离'''
def euclidean(a, b):
    return np.sqrt(np.sum(np.square(a-b)))


'''利用librosa库，提取mfcc特征'''
def mfcc(filename):
    y, sr = librosa.load(filename, sr=None)  # Load a wav file
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=15)  # extract mfcc feature
    return mfccs.transpose()

