import pickle
import random
import string

# pickle 过量load时，会抛出EOFError
with open('pickle', 'ab') as f:
    pickle.dump(1, f)
    pickle.dump(2, f)
    pickle.dump(3, f)

with open('pickle', 'rb') as f:
    for i in range(4):
        x = pickle.load(f)
        
# # 新建文件夹
# import os
# if os.path.exists('/xwjx') == False:
#     # c = os.getcwd()
#     # print(c)
#     os.mkdir('/xwjx')
# with open('/xwjx/Cookies.dat', 'wb') as f:
#     print('')

# 格式化输出
print(chr(12288)+'.')
form = "{0:{7}<13}\t{1:{7}<10}\t{2:{7}<10}\t{3:{7}<10}\t{4:{7}<10}\t{5:{7}<10}\t{6:<10}"
print(form.format("课程号", "课程名称", "课程类别", '课程性质', '学分', '学时', '所属栏', chr(12288)))
form = "{0:{7}<17}\t{1:{7}<10}\t{2:{7}<10}\t{3:{7}<10}\t{4:{7}<10}\t{5:{7}<10}\t{6:<10}"
print(form.format('COMP5', '数理逻辑', '专业选修课程', '选修', 2, '32', '方案内跨年级课程', chr(12288)))

# # 打包退出程序
# input()
# exit(0)

# 生成随机码
print(''.join(random.sample(string.ascii_letters + string.digits, 10)))

# try流程控制
from traceback import print_exc
try:
    print('start')
    raise FileNotFoundError
    print('raised')
except:
    print('except')
    print(print_exc())

# 文件可以重复关闭
with open('fkjjfhre', 'wb') as b:
    pass
b.close()
print('closed')
# 格式化输出中的中文对齐问题：上下一致
print('{0:<10}{1:<10}{2:<}'.format('fewf46', '11564645', 456458, chr(12288)))
print('{0:{3}<10}{1:<10}{2:<}'.format('日了狗了我', '1', 456458, chr(12288)))
# bool是int的子类（0，1）
print(bool(int('0')))
# bytes初试
mac = '54-BF-64-56-31-69'
bmac = mac.encode('utf-8')
b2 = 'Hello world!'.encode('utf-8')
print(bmac)
print(b2)
b3 = bmac + b2
print(b3)
b4 = b' '.join([bmac , b2])
print(b4)
print(chr(bmac[0]).encode('utf-8'))
# bytes加密
strlist=list(mac)
for i in range(len(strlist)):
  if strlist[i]>='a' and strlist[i]<='z':
    if ord(strlist[i])+13<=122:
      strlist[i]=chr(ord(strlist[i])+13)
    else:
      strlist[i]=chr((ord(strlist[i])+13)%122+96)
  elif strlist[i]>='A' and strlist[i]<='Z':
    if ord(strlist[i])+13<=90:
      strlist[i]=chr(ord(strlist[i])+13)
    else:
      strlist[i]=chr((ord(strlist[i])+13)%90+64)
print("".join(strlist))
# 我的
def my_encode(mac):
    maclist = list(mac)
    for i in range(len(maclist)):
        maclist[i] = chr((ord(maclist[i])+i**3) % 128)
    newmac = "".join(maclist) + ''.join(random.sample(string.ascii_letters + string.digits, 10))
    return newmac
newmac = my_encode(mac)
print(newmac, len(newmac))
def my_decode(newmac):
    mac = newmac[:17]
    maclist = list(mac)
    for i in range(len(maclist)):
        maclist[i] = chr((ord(maclist[i])-i**3) % 128)
    newmac = "".join(maclist)
    return newmac

mac2 = my_decode(newmac)
print(mac2, len(mac2))