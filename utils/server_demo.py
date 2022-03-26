#!coding=utf-8
from socket import *
import struct
import json
import pickle
import pydicom

class TestData():

    def __init__(self):
        self.name = "abc"
        self.des = "this is a test data"
        self.value = 45423

    def __str__(self):
        return  "data \n data.name: {0} \n data.des: {1} \n data.value: {2}".format(self.name, self.des, self.value)

def server_service():

    def get_host_ip():
        """
        查询本机ip地址
        :return: ip
        """
        try:
            s = socket(AF_INET, SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
            return ip

    tcp_server = socket(AF_INET, SOCK_STREAM)
    #如果是本机调试，改成 localhost
    print(get_host_ip())
    ip_port = ((get_host_ip(),9999))

    tcp_server.bind(ip_port)
    tcp_server.listen(5)
    print("等待链接...")

    while True:
        '''
        链接循环
        '''
        conn, addr = tcp_server.accept()
        print('链接成功！')
        print('链接来自于',addr)

        while True:
            print('正在传输数据')
            if not conn:
                print("客户端中断链接！")
                break
            '''
            通信循环
            '''
            # test_data = TestData()
            test_data = pydicom.dcmread(r"D:\respository\MRViewer_Scource\study_Test_data\localizer\ZYZHANG.MR.IMR-SJTU_ZSJ.0045.0002.2021.11.13.18.20.59.250882.20617477.IMA")
            test_data_byte = pickle.dumps(test_data)

            filename = str(test_data.PatientName)
            filesize = len(test_data_byte)
            dirc = {
                'filename':filename,
                'filesize':filesize
            }
            print(dirc)
            head_info = json.dumps(dirc)
            head_info_size = struct.pack('i', len(head_info))

            conn.send(head_info_size)
            conn.send(head_info.encode('utf-8'))
            conn.sendall(test_data_byte)

            print('数据传输结束')
            break

        break

    tcp_server.close()

if __name__ == "__main__":
    server_service()