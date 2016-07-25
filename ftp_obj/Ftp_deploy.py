#!/bin/env python
# -*- coding:utf-8 -*-
'''
基于CentOS 6 平台部署vsftpd(粗糙版)
'''
import subprocess
import os, sys, time,re


class Ftp_init:
    def __init__(self):
        self.user = ''
        self.passwd = ''
        self.ftpuser= 'task'
        self.ftpsswd = 'q.123456'
        self.ftpath = ''
        self.file = '/etc/vsftpd/vsftpd.conf'
        self.path = '/etc/vsftpd/'
        self.userconf_list = []


    def ftp_install(self):
        '''
        安装vsftpd
        :return:
        '''
        ret = subprocess.call('rpm -qa | grep vsftpd', shell=True)
        if ret == 0:
            print '#Info vsftpd is already installed.'
            return True
        else:
            subprocess.call('yum install vsftpd -y', shell=True)
            subprocess.call('chkconfig vsftpd on', shell=True)
            print '#Info vsftpd successful installation.'


    def modify_conf(self):
        '''
        修改vsfptd主配置文件
        :return:
        '''
        ret = subprocess.call('wget -c ftp://%s:%s@114.55.129.223:43121/ftp_install/ftp.conf' % (self.ftpuser, self.ftpsswd),
                              shell=True)
        if ret == 0:
            print '#Info ftp.conf download success.'
        else:
            print '#Info ftp.conf download failed.'
            return False
        with open('ftp.conf', 'r+') as h:
            with open(self.file, 'w+') as f:
                f.write('# Example config file /etc/vsftpd/vsftpd.conf created by shaw.\n')
                for lines in h:
                    if 'xferlog_file' in lines:
                        subprocess.call('touch %s'%lines.split('=')[1],shell=True)
                    f.write(lines)
        os.remove('ftp.conf')


    def pam_auth(self):
        rets = subprocess.call('rpm -qa | grep db4',shell=True)
        if rets == 0:
            print '#INFO db4 install success.'
        else:
            ret = subprocess.call('yum –y install db4 db4-utils',shell=True)
            if ret != 0:
                print '#INFO db4 install failed.'
                return False
        with open('%s/vuser_passwd'%self.path,'w+') as f:
            self.user = raw_input('请输入要创建的FTP用户名:').strip()
            self.passwd = raw_input('请输入FTP密码:').strip()
            f.write('%s,'%self.user)
            f.write(self.passwd)
            subprocess.call('db_load -T -t hash -f %s/vuser_passwd %s/vuser_passwd.db'%(self.path,self.path),shell=True)
            f = open('/etc/pam.d/vsftpd','w+')
            f.write('auth required pam_userdb.so db=/etc/vsftpd/vuser_passwd\n')
            f.write('account required pam_userdb.so db=/etc/vsftpd/vuser_passwd')
            f.close()



    def create_ftpath(self):
        self.ftpath = raw_input('请输入要创建的FTP根目录:').strip()
        subprocess.call('mkdir -p %s/%s'%(self.ftpath,self.user),shell=True)
        subprocess.call('touch %s/chroot_list'%self.path, shell=True)
        subprocess.call('chown -R ftp.ftp %s'%self.ftpath,shell=True)



    def create_user(self):
        os.system('mkdir %s/vuser_conf'%self.path)
        subprocess.call('wget -c ftp://%s:%s@114.55.129.223:43121/ftp_install/vuser.conf'%(self.ftpuser, self.ftpsswd),shell=True)
        os.rename('vuser.conf','%s/vuser_conf/%s'%(self.path,self.user))
        with open('%s/vuser_conf/%s' % (self.path, self.user), 'r+') as h:
            for line in h:
                self.userconf_list.append(line)
            self.userconf_list[0] = 'local_root=%s/%s\n'%(self.ftpath,self.user)
        with open('%s/vuser_conf/%s' % (self.path, self.user), 'w+') as f:
            for i in self.userconf_list:
                f.write(i)


if __name__ == '__main__':
    val = Ftp_init()
    val.ftp_install()
    val.modify_conf()
    val.pam_auth()
    val.create_ftpath()
    val.create_user()
    try:
        subprocess.check_call('/etc/init.d/vsftpd restart',shell=True)
    except Exception as e:
        print 'VSFTP installed filed'
