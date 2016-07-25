#!/bin/env python
# -*- coding:utf-8 -*-
import hashlib
user_list = {'shaw':'123'}

class auth:
    def __init__(self):
        self.__name = ''


    def hashlib_md5(self):
        '''
        返回加密后的数据
        :return:
        '''
        ret = hashlib.md5()
        ret = ret.update(bytes(self.__name, encoding='utf-8'))
        return ret.hexdigest()



    def ftp_authen(self):
        print('欢迎登陆申孚FTP Server')
        name = input('\t请输入账号:').strip()
        passwd = input('\t请输入密码:').strip()
        for k,v in user_list:
            if k == name and passwd == v:
                pass



