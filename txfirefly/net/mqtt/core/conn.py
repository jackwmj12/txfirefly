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
from typing import List

class Connection:
    '''
        连接实例
    '''

    def __init__(self, _conn = None, clientID = None):
        '''

        :param _conn:   连接实例
        :param clinetId:   客户端ID
        '''
        if not clientID:
            self.id = f"sessionno:{_conn.transport.sessionno}"
        else:
            self.id = clientID
        self.instance = _conn
        self.subs : List[str] = []

    def loseConnection(self):
        '''
            断开与客户端的连接
        '''
        self.instance.transport.loseConnection()

    def getInstance(self):
        return self.instance