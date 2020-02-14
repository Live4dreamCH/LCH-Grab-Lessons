# -*- coding: utf-8 -*-

from pickle import dump, load

with open('/RegistrationTemp/rkeys.dat', 'rb') as f:
    p = load(f)
    rkey_list = load(f)

print(rkey_list[p])
p += 1

with open('/RegistrationTemp/rkeys.dat', 'wb') as f:
    dump(p, f)
    dump(rkey_list, f)

input('enter')