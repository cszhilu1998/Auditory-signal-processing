import sys
import wavedection
import record
import dtw


wordlist = ['开门','关门','开灯','关灯','开空调','关空调','开电视','关电视','烧水','蒸饭']
print('正在载入模板...')
modellist = []
for i in range(1, 11):
    name = str(i) + '-' + '1.wav'
    mfcc = dtw.mfcc('pcm/'+name)
    modellist.append(mfcc)
print('载入模板完成！\n')


'''输出所有测试样例的识别结果'''
def module1():
    count = 0
    right = 0
    for i in range(1,11):
        for j in range(2,6):
            name = str(i) + '-' + str(j) + '.wav'
            filename = 'pcm/' + name
            print('正在处理文件 '+name+'...')
            mfcc = dtw.mfcc(filename)

            min = sys.maxsize
            flag = -1
            for k in range(len(modellist)):
                dtws = dtw.dtw(modellist[k], mfcc)
                if dtws < min:
                    min = dtws
                    flag = k+1
            #print(min)
            if min < 120:
                print(name+'文件识别结果为:'+wordlist[flag-1]+'\n')
            else:
                print('抱歉，未能识别出结果，请重新识别\n')

            if flag == i:
                right += 1
            count += 1
    print('正确率为：'+str(right/count*100)+'%\n')


'''在线录音并识别'''
def module2():
    filename = str(input('请输入保存文件名（例如"wave"），回车后将开始录音，录音将持续3秒：'))
    record.my_record('online/data/'+filename+'.wav')

    flag1 = int(input('是否播放录音?\n请输入1(是)或者0(否)：'))
    if flag1 == 1:
         record.play('online/data/'+filename+'.wav')

    flag2 = int(input('\n是否开始语音识别?\n请输入1(是)或者0(否)：'))
    if flag2 == 1:
        name = 'online/wavedection/'+filename+'.wav'
        wavedection.remove_mute('online/data/'+filename+'.wav', name)
        print('正在处理文件 '+filename+'...')
        mfcc = dtw.mfcc(name)

        min = sys.maxsize
        flag = -1
        for k in range(len(modellist)):
            dtws = dtw.dtw(modellist[k], mfcc)
            if dtws < min:
                min = dtws
                flag = k+1
        print('dtw = '+str(min))
        if min < 120:  # 门限
            print(filename+'文件识别结果为:'+wordlist[flag-1]+'\n')
        else:
            print('抱歉，未能识别出结果，请重新录制识别\n')
    print()


'''主函数'''
def main():
    flag = 1
    while flag == 1:
        print('1. 输出所有测试样例的识别结果')
        print('2. 在线录音并识别')
        flag1 = int(input('请选择输入1或者2：'))
        if flag1 == 1:
            print('40个样例的识别结果及正确率如下\n')
            module1()
        elif flag1 == 2:
            module2()
        else:
            print('输入错误！')
        flag = int(input('是否继续?\n请输入1(是)或者0(否)：'))
        print()

main()