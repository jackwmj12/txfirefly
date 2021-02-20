# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : connection.py
# @Time     : 2021-02-19 23:43
# @Software : od_gateway
# @Email    : jackwmj12@163.com
# @Github   : 
# @Desc     : 
#            ┏┓      ┏┓
#          ┏┛┻━━━┛┻┓
#          ┃      ━      ┃
#          ┃  ┳┛  ┗┳  ┃
#          ┃              ┃
#          ┃      ┻      ┃
#          ┗━┓      ┏━┛
#              ┃      ┃
#              ┃      ┗━━━┓
#              ┃              ┣┓
#              ┃              ┏┛
#              ┗┓┓┏━┳┓┏┛
#                ┃┫┫  ┃┫┫
#                ┗┻┛  ┗┻┛
#                 神兽保佑，代码无BUG!
#
#
#


class Connection:
    '''
    '''

    def __init__(self, _conn,id=None):
        '''
        id 连接的ID
        transport 连接的通道
        '''
        if not id:
            self.id = _conn.transport.sessionno
        else:
            self.id =id
        self.instance = _conn

    def loseConnection(self):
        '''断开与客户端的连接
        '''
        self.instance.transport.loseConnection()

    def safeToWriteData(self,msg):
        """发送消息
        """
        self.instance.safeToWriteData(msg)

    def safeToWriteOriginalData(self,msg):
        """发送消息
        """
        self.instance.safeToWriteOriginalData(msg)