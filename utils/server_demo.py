#!coding=utf-8
import sys
import os
import threading
import socket
import struct

def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定端口为9001
        s.bind(('127.0.0.1', 9001))
        # 设置监听数
        s.listen(10)
    except socket.error as msg:
        print (msg)
        sys.exit(1)
    print ('Waiting connection...')

    while 1:
        # 等待请求并接受(程序会停留在这一旦收到连接请求即开启接受数据的线程)
        conn, addr = s.accept()
        # 接收数据
        t = threading.Thread(target=send_data, args=(conn, addr))
        t.start()

def send_data(conn, addr):
    print ('Accept new connection from {0}'.format(addr))
    print("开始传输文件...")
    # 需要传输的文件路径
    filepath = r'D:\respository\MRViewer_Scource\Study_vessel_test_data\LOCALIZER_0018\WANGYJ_20211104_PHANTOM.MR.ABDOMEN_CLINICAL_LIBRARIES.0018.0003.2021.11.04.13.00.19.318110.27169993.IMA'
    # 判断是否为文件
    if os.path.isfile(filepath):
        # 定义定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
        fileinfo_size = struct.calcsize('128sl')
        # 定义文件头信息，包含文件名和文件大小
        fhead = struct.pack('128sl', os.path.basename(filepath).encode('utf-8'), os.stat(filepath).st_size)
        # 发送文件名称与文件大小
        conn.send(fhead)

        # 将传输文件以二进制的形式分多次上传至服务器
        fp = open(filepath, 'rb')
        while 1:
            data = fp.read(1024)
            if not data:
                print ('{0} file send over...'.format(os.path.basename(filepath)))
                break
            conn.send(data)
        # 关闭当期的套接字对象
        conn.close()

if __name__ == "__main__":
    socket_service()