#!coding=utf-8
import sys
import os
import threading
from socket import *
import struct
import json
import pickle
import time
from utils.server_demo import TestData
import pydicom

def client_service():
    tcp_client = socket(AF_INET, SOCK_STREAM)
    ip_port = (('localhost', 9999))
    buffsize = 8192
    tcp_client.connect_ex(ip_port)
    print("等待链接服务端")
    while True:
        head_struct = tcp_client.recv(4)
        if head_struct:
            print('已成功链接服务端，等待接收数据')
        head_len = struct.unpack('i', head_struct)[0]
        head_data = tcp_client.recv(head_len)

        head_dirc = json.loads(head_data.decode('utf-8'))
        filename = head_dirc['filename']
        filesize_b = head_dirc['filesize']

        print(head_dirc)

        #接收真正的数据部分
        print("开始传输数据")
        recv_len = 0
        recv_mesg = b''
        old = time.time()
        while recv_len < filesize_b:
            percent = recv_len / filesize_b
            print("当前传输进度", percent*100, "%")

            if filesize_b - recv_len > buffsize:
                recv_mesg_tmp = tcp_client.recv(buffsize)
                recv_mesg += recv_mesg_tmp
                recv_len += len(recv_mesg_tmp)
            else:
                recv_mesg_tmp = tcp_client.recv(filesize_b - recv_len)
                recv_mesg += recv_mesg_tmp
                recv_len += len(recv_mesg_tmp)
        print("数据传输完成")
        print('正在解析数据')
        data = pickle.loads(recv_mesg)
        try:
            print("数据解析成功")
            print(data.Modality)
            print(data.PatientName)
        except:
            print("数据解析失败")

        stamp =int(time.time() - old)
        print('本次链接共用时%ds'%stamp)
        break

    tcp_client.shutdown(1)
    tcp_client.close()


if __name__ == "__main__":
    client_service()