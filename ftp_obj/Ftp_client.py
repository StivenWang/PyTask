#!/bin/env python
# -*- coding:utf-8 -*-
import socket
sk = socket.socket()
sk.connect(('127.0.0.1',8001))

sk.sendall(bytes('请轰炸美国',encoding='utf-8'))
data = sk.recv(1024)
print(str(data,encoding='utf-8'))
sk.close()
