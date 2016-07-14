#!/bin/env python
# -*- coding:utf-8 -*-
import socket

sk = socket.socket()
sk.bind(('127.0.0.1',8002))
sk.listen()

while True:
    conn,addr = sk.accept()
    data = conn.recv(1024)
    print(str(data,encoding='utf-8'))
    conn.sendall(bytes('OK',encoding='utf-8'))

    conn.close()