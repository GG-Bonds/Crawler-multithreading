#coding:utf8
import os
from PIL import Image,ImageDraw,ImageFile
import numpy
import pytesseract
import cv2
import imagehash
import collections
import os

'''
文件数据的问题：
1.存在打不开的图片
2.存在相同的图片

解决方法：
A. 针对问题1，可以逐个遍历文件，发现当前文件打不开则删除
B. 针对问题2，可以发现相同图片的名字序号是挨在一起的，例如有这样两种相同的图片，他们的名字为 2.jpg 和 3.jpg；
    利用这个特点，当遍历到第J文件时，将第J文件和第J + 1文件进行比较，如果连个文件相差不大，则删除第J文件
'''


folder = ''

def getSaveImgPath(floder, index):
    '''输入文件名，返回文件所在的路径'''
    return os.path.join(folder, str(index) + ".jpg")



def filterImageWithHash(image_file1="data/34.jpg",
                                image_file2="data/35.jpg", max_dif=0):
        """
        对文件进行过滤
        max_dif: 允许最大hash差值, 越小越精确,最小为0
        """
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        hash_1 = None
        hash_2 = None
        try:    # 如果文件打开错误， 则删除， 并返回； 如果文件不存在， 则返回
            with open(image_file1, 'rb') as fp:     # 有时路径错误，会报错
                hash_1 = imagehash.average_hash(Image.open(fp))     # 有些图片不能打开会报错
                # print(hash_1)

        except:
            if os.path.exists(image_file1):     # 先判断这个路径是否存在
                fp.close()
                os.remove(image_file1)
            # print(111)
            return False

        try:
            with open(image_file2, 'rb') as fp:
                hash_2 = imagehash.average_hash(Image.open(fp))
        except:
            if os.path.exists(image_file2):
                fp.close()
                os.remove(image_file2)
            # return False
        fp.close()
        dif = hash_1 - hash_2
        if dif < 0:
            dif = -dif
        if dif > max_dif:      # 如果文件差异较不大， 则判断为 False， 进行删除
            return True
        else:
            os.remove(image_file1)      # 删掉其中一个图片
            return False

