#coding:utf8
import os
import pytesseract
import multiprocessing
import socket
import urllib.request
import asyncio
import time



imageUrlsPath =r'bird-urls-copy.txt'        # txt 的路径
imageSavePath = "bird-image-data"       # 保存文件的目录
imageSaveChildFoldorNum = 8         # 子文件的个数， 由于一个文件夹能装入的文件数是有限的
connectMaxTime = 5      # 通信的最大时长， 超时及断开连接


f = open(imageUrlsPath, "r")

headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
header = headers.encode() # 不进行类型转换，传入urlretrieve()后会报错，需转换成bytes类型

async def Download(url, filename, callback, header):
    """
    封装了 urlretrieve()的自定义函数，递归调用urlretrieve(),当下载失败时，重新下载
    :param url: path to download from
    :param savepath: path to save files
    :return: None
    """
    try:
        urllib.request.urlretrieve(url, filename, callback, header)
    except Exception as e:
        pass


def Callback(a1, a2, a3):     # 用于urllib.request.urlretrieve的回调函数
    pass

async def Request(imgName, imgSaveChildFoldor,url):
    '''根据url下载图片，同时设置了连接的最大时间'''
    # 设置超时时间
    socket.setdefaulttimeout(connectMaxTime)     # 如果通信超时就断开，
    try:
        await Download(url, os.path.join(imageSavePath, str(imgSaveChildFoldor),  str(imgName) + ".jpg"), Callback, header) # 这里用于下载图片， 加上awit是当下载的任务处于等待时，将其挂起
    except socket.timeout:  # 超过设定的时长就跳过
        pass


def ThreadProcessImgurl(img_info):
    '''一个进程负责处理一行数据 '''
    tasks = [asyncio.ensure_future(Request(img_info[0], img_info[2], url)) for url in img_info[1]]   # 将一行中的不同网址放入不同的协程中
    loop = asyncio.get_event_loop()     # 循环事件
    loop.run_until_complete(asyncio.wait(tasks))        # 开始运行这个协程队列


def GetImgInfo():
    '''递归遍历每行的数据'''
    child = 0       # 判断当前图片应该装入的子文件夹
    for i, ps in enumerate(f.readlines()):
        child = (child + 1) % imageSaveChildFoldorNum
        yield (i, ps.split(",")[1:], child)


def Init():
    '''初始化，创建保存数据图片的文件夹'''
    os.makedirs(imageSavePath, exist_ok=True)
    for i in range(imageSaveChildFoldorNum):
        os.makedirs(os.path.join(imageSavePath, str(i)), exist_ok=True)

if __name__ == '__main__':

    start = time.time()
    Init()
    data = GetImgInfo()         # 每行数据的迭代器
    cpu_count = multiprocessing.cpu_count()         # cpu的进程数量

    pool = multiprocessing.Pool(cpu_count)      # 设置进程池的数量

    pool.map(ThreadProcessImgurl, data)     # 进程处理

    end = time.time()
    print('Cost time:', end - start)