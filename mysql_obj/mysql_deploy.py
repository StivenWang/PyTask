#!/bin/env python
# -*- coding:utf-8 -*-
'''
MySQL部署py
'''

import os, sys, subprocess
import time, datetime
import socket
import shutil


class MySQL_init:
    '''
    MySQL编译安装py
    '''

    def __init__(self):
        self.url = 'ftp://task:q.123456@ftp.opsdev.tech:43121/mysql'
        self.ret = []
        self.compile = []
        self.count = 0
        self.status = ' '

    @staticmethod
    def get_local_ip():
        '''
        获取服务器IP，如果有公网地址就取公网IP，没有公网地址就取私网IP
        :return:
        '''
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(('8.8.8.8', 80))
            (addr, port) = sock.getsockname()
            sock.close()
            return addr
        except socket.error:
            return "127.0.0.1"

    def install_check(self):
        '''
        检查命令是否执行成功
        :return: True:成功 False:失败(每个方法最后统一检查)
        '''
        for i in self.ret:
            self.count += i
        if self.count == 0:
            print('#INFO ############### \033[1;32mThe command execution success.\033[0m ###############')
            time.sleep(3)
            return True
        else:
            print('#INFO ############### \033[1;31mThe command execution failed.\033[0m ###############')
            time.sleep(3)
            return False


    def install_cmd(self, arg):
        '''
        收集shell命令执行结果
        :param arg: 命令字符串
        :return: 返回执行状态
        '''
        val = subprocess.call(arg, shell=True, stdout=subprocess.PIPE)
        self.ret.append(val)
        return val


    def MySQL_download(self):
        '''
        下载安装包
        :return:False:下载执行失败
        '''
        print '#INFO ############### \033[1;33m开始下载MySQL安装包\033[0m ###############'
        time.sleep(3)
        try:
            os.makedirs('/home/tools')
        except OSError as e:
            pass
        os.chdir('/home/tools')
        self.install_cmd('wget -c %s/mysql-5.5.50.tar.gz' % self.url)
        if self.install_check() == False:
            return False


    def MySQL_add_acc(self):
        '''
        添加账号
        :return:True:账号已存在 False:账号添加失败
        '''
        print '#INFO ############### \033[1;33m开始建立MySQL账号\033[0m ###############'
        time.sleep(3)
        self.acc = raw_input('请输入要创建账号名:').strip()
        self.status = subprocess.call('id %s > /dev/null 2>1' %self.acc,shell=True)
        if self.status == 0:
            print('#INFO ############### \033[1;32mThe command execution success.\033[0m ###############')
            time.sleep(3)
            return True
        else:
            self.install_cmd('groupadd {user} && useradd -s /sbin/nologin -g {user} -M {user}'.format(user=self.acc))
            if self.install_check() == False:
                return False



    def MySQL_conf_env(self):
        '''
        配置mysql安装环境
        :return:
        '''
        print '#INFO ############### \033[1;33m开始配置MySQL安装环境\033[0m ###############'
        time.sleep(3)
        self.install_path = raw_input('请输入一个不存在的目录(安装目录):').strip()
        self.data_path = raw_input('请输入一个不存在的目录(数据存放目录):').strip()
        if os.path.isdir(self.install_path) and os.path.isdir(self.data_path):
            pass
        else:
            try:
                os.makedirs(self.install_path)
                os.makedirs(self.data_path)
            except OSError as e:
                pass
        self.install_cmd('chown -R {user}.{user} {path1} {path2}'.format(user=self.acc, path1=self.install_path,path2=self.data_path))
        ret = subprocess.call('yum -y install gcc gcc-c++ make cmake ncurses-devel bison perl', shell=True)
        if self.install_check() == True and ret == 0:
            pass
        else:
            return False
        self.hostname = socket.getfqdn(socket.gethostname())
        # self.ip = socket.gethostbyname(socket.gethostname())      # 不知怎么回事，不同linux OS,有时可以获取到IP，有时会报‘socket.gaierror’错误
        self.ip = MySQL_init.get_local_ip()
        with open('/etc/hosts', 'a') as f:
            f.write('\n{ip}\t{hostname}'.format(ip=self.ip, hostname=self.hostname))



    def MySQL_install(self):
        '''
        安装MySQL
        :return:
        '''
        print '#INFO ############### \033[1;33m开始安装MySQL\033[0m ###############'
        time.sleep(3)
        os.chdir('/home/tools')
        self.install_cmd('tar zxf mysql-5.5.50.tar.gz')
        os.chdir('mysql-5.5.50')
        self.install_cmd('wget -c {url}/compile.conf'.format(url=self.url))
        with open('compile.conf', 'r+') as f:
            for lines in f:
                self.compile.append(lines.strip())
        self.compile[0] = '-DCMAKE_INSTALL_PREFIX=%s' % self.install_path
        self.compile[1] = '-DMYSQL_DATADIR=%s' % self.data_path
        self.status = ' '
        self.compile = self.status.join(self.compile)
        rets = subprocess.call('cmake %s' % self.compile, shell=True)
        vals = subprocess.call('make -j 2 && make install', shell=True)
        if rets == vals == 0:
            return True
        else:
            return False
        os.remove('compile.conf')
        if self.install_check() == False:
            return False

    def MySQL_env_init(self):
        '''
        初始化mysql
        :return:
        '''
        print '#INFO ############### \033[1;33m开始初始化MySQL\033[0m ###############'
        time.sleep(3)
        self.install_cmd("echo 'export PATH={ins_path}/bin:$PATH' >>/etc/profile".format(ins_path=self.install_path))
        self.install_cmd('source /etc/profile')
        shutil.copyfile('support-files/my-small.cnf', '/etc/my.cnf')
        self.install_cmd('{path1}/scripts/mysql_install_db --basedir={path1} --datadir={path2} --user={user}'.format(path1=self.install_path, path2=self.data_path, user=self.acc))
        if self.install_check() == False:
            return False


    def MySQL_boot(self):
        '''
        启动MySQL
        :return:
        '''
        print '#INFO ############### \033[1;33m开始启动MySQL\033[0m ###############'
        self.install_cmd('{path}/bin/mysqld_safe --user={user} &'.format(path=self.install_path, user=self.acc))
        print '\r'
        time.sleep(5)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ret = sock.connect_ex((self.ip, 3306))
        if ret == 0:
            pass
        else:
            return False
        self.install_cmd('/bin/cp support-files/mysql.server /etc/init.d/mysqld')
        self.install_cmd('chmod 700 /etc/init.d/mysqld')
        self.install_cmd('chkconfig --add mysqld && chkconfig mysqld on')
        if self.install_check() == False:
            return False
        else:
            print '\033[1;33m#INFO 命令执行结果 \033[0m: %s'%self.ret
            print '\033[1;32m#INFO MySQL 安装成功.\033[0m'


    def main(self):
        ret = MySQL_init()
        if ret.MySQL_download() == False:
            print '\033[1;31m#INFO ==========> MySQL 安装包下载失败\033[0m.'
            sys.exit(1)
        elif ret.MySQL_add_acc() == False:
            print '\033[1;31m#INFO ==========> MySQL 账号创建失败\033[0m.'
            sys.exit(2)
        elif ret.MySQL_conf_env() == False:
            print '\033[1;31m#INFO ==========> MySQL 安装环境配置失败\033[0m.'
            sys.exit(3)
        elif ret.MySQL_install() == False:
            print '\033[1;31m#INFO ==========> MySQL 安装失败\033[0m.'
            sys.exit(4)
        elif ret.MySQL_env_init() == False:
            print '\033[1;31m#INFO ==========> MySQL 初始化失败\033[0m.'
            sys.exit(4)
        elif ret.MySQL_boot() == False:
            print '\033[1;31m#INFO ==========> MySQL 启动失败\033[0m.'
            sys.exit(5)


if __name__ == '__main__':
    val = MySQL_init()
    val.main()
