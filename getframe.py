#encoding:utf-8  

import cv2
import os

import config

def main(videoname):
    conf = config.getConfig(videoname)

    videoDir = conf['videoDir']
    outputDir = conf['imgDir'] + '/'

    if not(os.path.exists(outputDir)):
        os.mkdir(outputDir)

    vc = cv2.VideoCapture(videoDir) #读入视频文件  

    c = 1  
    
    if vc.isOpened(): #判断是否正常打开  
        rval , frame = vc.read()  
    else:  
        rval = False  

    timeF = vc.get(5) * 1  #视频帧计数间隔频率 = 帧率 * 切片时间间隔  
    
    while rval:   #循环读取视频帧  
        rval, frame = vc.read()  
        if(c%timeF == 0): #每隔timeF帧进行存储操作  
            print c
            cv2.imwrite(outputDir+str(c).zfill(10) + '.jpg',frame) #存储为图像  
        c = c + 1  
        cv2.waitKey(1)
    vc.release()  

# main()