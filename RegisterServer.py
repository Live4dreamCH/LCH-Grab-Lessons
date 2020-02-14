# -*- coding: utf-8 -*-

import socketserver
from time import sleep
import random
import string
from pickle import dump, load
from traceback import print_exc
import os

def my_encode(mac):
    maclist = list(mac)
    for i in range(len(maclist)):
        maclist[i] = chr((ord(maclist[i])+i**3) % 128)
    newmac = "".join(maclist) + ''.join(random.sample(string.ascii_letters + string.digits, 10))
    return newmac.encode('utf-8')

def my_decode(newmac):
    newmac = newmac.decode('utf-8')
    l = len(newmac) - 10
    mac = newmac[:l]
    maclist = list(mac)
    for i in range(len(maclist)):
        maclist[i] = chr((ord(maclist[i])-i**3) % 128)
    newmac = "".join(maclist)
    return newmac

class MyServer(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            global mac_list
            global rkey_list
            # global l
            link = self.request
            address = self.client_address
            print('连接成功:', address)
            mac = my_decode(link.recv(1024))
            if mac in mac_list:
                print('老用户访问，MAC=', mac)
                link.send(my_encode('1'))
            else:
                print('新用户注册，MAC=', mac)
                link.send(my_encode('0'))
                rkey = my_decode(link.recv(1024))
                if rkey in rkey_list:
                    print('新用户注册成功！MAC=', mac, '注册码=', rkey)
                    rkey_list.remove(rkey)
                    rkey_list.append(''.join(random.sample(string.ascii_letters + string.digits, 10)))
                    with open('/RegistrationTemp/rkeys.dat', 'rb') as f:
                        t = load(f)
                        t -= 1
                    with open('/RegistrationTemp/rkeys.dat', 'wb') as f:
                        dump(t, f)
                        dump(rkey_list, f)
                    print('rkeys.dat 更新成功！')

                    mac_list.append(mac)
                    with open('/RegistrationTemp/macs.dat', 'ab') as f:
                        dump(mac, f)
                    print('macs.dat 添加成功！')

                    with open('/RegistrationTemp/len.dat', 'rb') as f:
                        l = load(f)
                    l += 1
                    with open('/RegistrationTemp/len.dat', 'wb') as f:
                        dump(l, f)
                    print('len.dat 自增成功！')
                    link.send(my_encode('1'))
                else:
                    print('新用户注册失败！MAC=', mac)
                    link.send(my_encode('0'))
            print('连接断开:', address)
        except Exception:
            print(print_exc())
        

if __name__ == '__main__':
    # 重新打开问题：文件尚存，内存清空，如何是好？
    # log日志文件需要写     不需要了，感谢Linux系统 https://blog.csdn.net/TiLongZS/article/details/78991178
    # rkeys.dat：指针（用于读取）+列表
    # macs.dat：各单独的mac字符串
    # len.dat: macs.dat的总长度（用于遍历）
    if os.path.exists('/RegistrationTemp') == False:
        os.mkdir('/RegistrationTemp')
        print('/RegistrationTemp 创建成功！')

    rkey_list = list()
    if os.path.exists('/RegistrationTemp/rkeys.dat') == False:
        for i in range(100):
            rkey_list.append(''.join(random.sample(string.ascii_letters + string.digits, 10)))
        with open('/RegistrationTemp/rkeys.dat', 'wb') as f:
            dump(0, f)
            dump(rkey_list, f)
            print('rkeys.dat 创建成功！')
    else:
        with open('/RegistrationTemp/rkeys.dat', 'rb') as f:
            load(f)
            rkey_list = load(f)
            print('rkey_list 从 rkeys.dat 中恢复成功！')

    if os.path.exists('/RegistrationTemp/len.dat') == False:
        with open('/RegistrationTemp/len.dat', 'wb') as f:
            l = 0
            dump(l, f)
            print('len.dat 创建成功！')
    else:
        with open('/RegistrationTemp/len.dat', 'rb') as f:
            l = load(f)
            print('l 从 len.dat 中恢复成功！')

    mac_list = list()
    if os.path.exists('/RegistrationTemp/macs.dat') == False:
        with open('/RegistrationTemp/macs.dat', 'ab') as f:
            print('macs.dat 创建成功！')
    else:
        with open('/RegistrationTemp/macs.dat', 'rb') as f:
            for i in range(l):
                mac_list.append(load(f))
            # print('mac_list 无需从 macs.dat 中恢复，因为其中没有数据233（以下异常如果为读取失败则为正常情况）')
            # print(print_exc())
            print('mac_list 从 macs.dat 中恢复成功！')
    LAN = '127.0.0.1'
    port = 15973
    add = (LAN, port)
    server = socketserver.ThreadingTCPServer(add, MyServer)
    print('server started')    
    server.serve_forever()
