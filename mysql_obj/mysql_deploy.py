#!/bin/env python
# -*- coding:utf-8 -*-
'''
MySQL部署py
'''

import os,sys,subprocess
import time,datetime
import socket
import shutil


class MySQL_init:
    '''
    MySQL编译安装py
    '''
    def __init__(self):
        self.url = 'ftp://task:q.123456@ftp.opsedu.com:43121/mysql'
        self.ret = []
        self.compile = []
        self.count = 0
        self.status = ' '

    def install_check(self):
        '''
        检查命令是否执行成功
        :return: True:成功 False:失败(每个方法最后统一检查)
        '''
        for s,i in enumerate(self.ret):
            self.count += i
            if self.count == 0 and s + 1 == len(self.ret):
                print('#INFO ---> The command completed successfully.')
                return True
            else:
                print('#INFO ---> The command failed.')
                return False

    @staticmethod
    def install_cmd(arg):
        '''
        收集shell命令执行结果
        :param arg: 命令字符串
        :return: 返回执行状态
        '''
        rets = MySQL_init()
        val = subprocess.call(arg, shell=True,stdout=subprocess.PIPE)
        rets.ret.append(val)
        return val

    def MySQL_download(self):
        '''
        下载安装包
        :return:False:下载执行失败
        '''
        try:
            os.makedirs('/home/tools')
        except OSError as e:
            pass
        os.chdir('/home/tools')
        MySQL_init.install_cmd('wget -c %s/mysql-5.5.50.tar.gz'%self.url)
        if self.install_check() == False:
            return False



    def MySQL_add_acc(self):
        '''
        添加账号
        :return:True:账号已存在 False:账号添加失败
        '''
        self.acc = raw_input('请输入要创建账号名:').strip()
        self.status = MySQL_init.install_cmd('id %s > /dev/null 2>1'%self.acc)
        if self.status == 0:
            return True
        else:
            MySQL_init.install_cmd('groupadd {user} && useradd -s /sbin/nologin -g {user} -M {user}'.format(user=self.acc))
            if self.install_check() == False:
                return False


    def MySQL_conf_env(self):
        '''
        配置mysql安装环境
        :return:
        '''
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
        MySQL_init.install_cmd('chown -R {user}.{user} {path1} {path2}'.format(user=self.acc,path1=self.install_path,path2=self.data_path))
        MySQL_init.install_cmd('yum -y install gcc gcc-c++ make cmake ncurses-devel bison perl')
        if self.install_check() == False:
            return False
        self.hostname = socket.getfqdn(socket.gethostname())
        self.ip = socket.gethostbyname(socket.gethostname())
        with open('/etc/hosts','a') as f:
            f.write('\n{ip}\t{hostname}'.format(ip=self.ip,hostname=self.hostname))


    def MySQL_install(self):
        os.chdir('/home/tools')
        MySQL_init.install_cmd('tar zxf mysql-5.5.50.tar.gz')
        os.chdir('mysql-5.5.50')
        MySQL_init.install_cmd('wget -c {url}/compile.conf'.format(url=self.url))
        with open('compile.conf','r+') as f:
            for lines in f:
                self.compile.append(lines.strip())
        self.compile[0] = '-DCMAKE_INSTALL_PREFIX=%s'%self.install_path
        self.compile[1] = '-DMYSQL_DATADIR=%s'%self.data_path
        self.status = ' '
        self.compile = self.status.join(self.compile)
        MySQL_init.install_cmd('cmake %s'%self.compile)
        MySQL_init.install_cmd('make -j 2 && make install')
        os.remove('compile.conf')
        if self.install_check() == False:
            return False


    def MySQL_env_init(self):
        '''
        初始化mysql
        :return:
        '''
        MySQL_init.install_cmd("echo 'export PATH={ins_path}/bin:$PATH' >>/etc/profile".format(ins_path=self.install_path))
        MySQL_init.install_cmd('source /etc/profile')
        shutil.copyfile('support-files/my-small.cnf','/etc/my.cnf')
        MySQL_init.install_cmd('{path1}/scripts/mysql_install_db --basedir={path1} --datadir={path2} --user={user}'.format(path1=self.install_path,path2=self.data_path,user=self.acc))
        if self.install_check() == False:
            return False


    def MySQL_boot(self):
        MySQL_init.install_cmd('{path}/bin/mysqld_safe --user={user} &'.format(path=self.install_path,user=self.acc))
        time.sleep(3)
        print '\r'
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ret = sock.connect_ex((self.ip, 3306))
        if ret == 0:
            print '\033[1;32m#INFO MySQL 安装成功.\033[0m'
            return True
        else:
            print '\033[1;31m#INFO MySQL 安装成功.\033[0m'
            return False
        MySQL_init.install_cmd('cp support-files/mysql.server /etc/init.d/mysqld')
        MySQL_init.install_cmd('chmod 700 /etc/init.d/mysqld')
        MySQL_init.install_cmd('chkconfig --add mysqld && chkconfig mysqld on')
        if self.install_check() == False:
            return False

    def main(self):
        ret = MySQL_init()
        if ret.MySQL_download() == False:
            print '#INFO MySQL 安装包下载失败.'
            sys.exit(1)
        elif ret.MySQL_add_acc() == False:
            print '#INFO MySQL 账号创建失败.'
            sys.exit(2)
        elif ret.MySQL_conf_env() == False:
            print '#INFO MySQL 安装环境配置失败.'
            sys.exit(3)
        elif ret.MySQL_install() == False:
            print '#INFO MySQL 安装失败.'
            sys.exit(4)
        elif ret.MySQL_env_init() == False:
            print '#INFO MySQL 初始化失败.'
            sys.exit(4)
        elif ret.MySQL_boot() == False:
            print '#INFO MySQL 启动失败.'
            sys.exit(5)

if __name__ == '__main__':
    val = MySQL_init()
    val.main()