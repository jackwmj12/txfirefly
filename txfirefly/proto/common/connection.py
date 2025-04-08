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
from twisted.internet import protocol


class Connection:
    '''
        连接实例
    '''

    def __init__(self, _conn  : protocol.Protocol = None,peer_info= None):
        '''
            id 连接的ID
            _conn 连接的通道
        '''
        self.peer_info = peer_info
        self.instance: protocol.Protocol= _conn

    def loseConnection(self):
        '''
            断开与客户端的连接
        '''
        self.instance.transport.loseConnection()

    def safeToWriteData(self, msg):
        """
            发送消息
        """
        return self.instance.safeToWriteData(msg)