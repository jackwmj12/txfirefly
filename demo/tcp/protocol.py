# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : protocol.py
# @Time     : 2024-01-22 15:52
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
# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : protocol.py
# @Time     : 2021-02-21 14:50
# @Software : tiseal_app
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
from struct import unpack, pack
from typing import Union, Optional, List
from loguru import logger
from typing import Dict

from twisted.internet import protocol
from twisted.protocols import policies

from demo.tcp.baseprotocol import BaseProtocol, BaseFactory, PROTOCOL_CHECK_FAILED
from txrpc.globalobject import GlobalObject, localservice

PROTOCOL_MIN_LENGTH = 1 # 

class TcpProtocol(BaseProtocol):
    '''
    协议
    '''
    factory: Union["TcpFactory", None]
    _recv_buffer = b""
    
    def getMinProtocolLength(self):
        '''
            协议最小解析长度,超过 PROTOCOL_MIN_LENGTH 才能加入解析
        :return: 
        '''
        return 1
    
class TcpFactory(BaseFactory):
    '''协议工厂'''

    protocol = TcpProtocol

    def __init__(self):
        '''
        初始化
        '''
        super(TcpFactory, self).__init__()

    def onDataReceived(self, conn, data):
        '''
        数据到达时的处理
            在这个系统内，这里的数据全部都通过 forwarding 发送给 gateway
            通过gateway分发
        '''

    def unpackData(self, data):
        '''
            数据到达时的校验
            - 数据不足,返回数据不足标志 -2, 以及数据偏移量 0
            - 校验失败,返回校验失败标志 -1, 以及数据偏移量 1
            - 校验成功,返回校验成功标志 1, 以及数据偏移量 X
        '''
        raise NotImplementedError()

