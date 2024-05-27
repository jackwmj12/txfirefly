# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : service.py
# @Time     : 2024-03-05 17:03
# @Software : txfirefly
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
from txfirefly.rpc.client import Client
from txrpc.distributed.node import RemoteObject
from txrpc.distributed.reference import ProxyReference
from txrpc.globalobject import GlobalObject, onLeafWhenConnectRootSuccessHandle, onLeafWhenLostConnectRootHandle, onLeafWhenConnectRootFailedHandle

class Service(Client):
    ''''''
    def __init__(self, name : str):
        '''
            节点对象
        :param name:
        :param single:
        '''
        super(Client, self).__init__(name)
        GlobalObject().app = self