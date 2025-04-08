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
from loguru import logger
from twisted.internet import protocol


class Connection:
    '''
        连接实例
    '''

    def __init__(self, _conn  : protocol.Protocol = None,id=None):
        '''
            id 连接的ID
            _conn 连接的通道
        '''
        if not id:
            self.id = _conn.transport.sessionno
        else:
            self.id =id
        self.instance : protocol.Protocol= _conn

    def loseConnection(self):
        '''
            断开与客户端的连接
        '''
        self.instance.transport.loseConnection()

    def safeToWriteData(self,msg):
        """
            发送消息
        """
        # logger.debug(f"TCP send msg {msg}")
        self.instance.safeToWriteData(msg)