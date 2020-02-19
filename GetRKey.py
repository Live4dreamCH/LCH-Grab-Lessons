# -*- coding: utf-8 -*-

# 用于从服务器端获取取验证码
from pickle import dump, load

# 读取下标
with open('/RegistrationTemp/rkeys.dat', 'rb') as f:
    p = load(f)
    rkey_list = load(f)

# 打印验证码，更改下标
print(rkey_list[p])
p += 1

# 写入新下标和原验证码序列
with open('/RegistrationTemp/rkeys.dat', 'wb') as f:
    dump(p, f)
    dump(rkey_list, f)

# 其实没用，避免闪退
input('enter')