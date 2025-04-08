# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : gate_od.py
# @Time     : 2024-03-05 17:00
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

from txfirefly.rpc.server import Server
from txrpc.distributed.node import RemoteObject
from txrpc.distributed.reference import ProxyReference
from txrpc.globalobject import GlobalObject, onRootWhenLeafLostConnectHandle, onRootWhenLeafConnectHandle


@onRootWhenLeafConnectHandle
def doChildConnect(name, transport):
    '''
    :return
    '''
    name = name.upper()
    id = transport.broker.transport.sessionno
    remote_key = ":".join([name, str(id)])
    logger.debug(f"{remote_key} connected")


@onRootWhenLeafLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    try:
        logger.debug("{} lost connect".format(childId))
    except Exception as e:
        logger.error(str(e))


class Gate(Server):
    '''
    远程master调用对象
    :param
    '''

    def __init__(self, name: str):
        '''
        :return
        '''
        # root对象监听制定端口
        super().__init__(name)
        GlobalObject().app = self
