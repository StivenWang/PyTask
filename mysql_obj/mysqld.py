#!/bin/env python
# -*- coding:utf-8 -*-

'''
MySQL多实例启动程序
'''
import os,sys,time
import subprocess

class Mysql_init:
    def __init__(self):
        self.user = 'root'
        self.port = '3306'      # 根据不同实例更改端口即可
        self.passwd = 'q.123456'
        self.Cmd_path = '/usr/local/mysql/bin'
        self.sock = '/db/%s/mysql.sock'%self.port

    def jindu(self):
        for i in range(2):
            sys.stdout.write('.')
            time.sleep(1)
            sys.stdout.flush()
        time.sleep(1)
        return '.'

    def start(self):
        if os.path.exists(self.sock):
            print 'MySQL already running.'
        else:
            val = subprocess.call('/bin/sh %s/mysqld_safe --defaults-file=/db/%s/my.cnf 2>&1 >/dev/null &'%(self.Cmd_path,self.port),shell=True)
            if val == 0:
                print 'Starting MySQL',
                print '%s'% self.jindu(),
                print 'SUCCESS!'.strip()
                return True
            else:
                print 'MySQL start failed.'

    def stop(self):
        if os.path.exists(self.sock):
            val = subprocess.call('%s/mysqladmin -u%s -p%s -S %s shutdown'%(self.Cmd_path, self.user,self.passwd,self.sock),shell=True)
            if val == 0:
                print 'Shutting down MySQL',
                print '%s'%self.jindu(),
                print 'SUCCESS!'.strip()
                return True
            else:
                print 'MySQL stop failed.'
        else:
            print 'MySQL already stopped.'

    def restart(self):
        self.stop()
        self.start()

    def main(self):
        if sys.argv[1] == 'start':
            self.start()
        elif sys.argv[1] == 'stop':
            self.stop()
        elif sys.argv[1] == 'restart':
            self.restart()
        else:
            print 'Usage: mysqld  {start|stop|restart}  [ MySQL server options ]'

if __name__ == '__main__':
    ret = Mysql_init()
    ret.main()