# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : baseprotocol.py
# @Time     : 2021-02-19 23:40
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
import threading
from typing import Union, List, Dict

from twisted.internet.defer import DeferredLock
from twisted.protocols import policies
from twisted.internet import protocol

from txfirefly.proto.common.manager import ConnectionManager
from txfirefly.proto.common.datapack import DataPackProtocol
from txrpc.globalobject import GlobalObject
from loguru import logger

class BaseProtocol(protocol.DatagramProtocol,policies.TimeoutMixin):
    '''
    自定义协议
    '''
    _recv_buffer = b""                                               # 用于暂时存放接收到的数据

    def datagramReceived(self, datagram, address):
        logger.debug(f"Received {datagram} from {address}")


    # def safeToWriteData(self,messages: Union[bytes,List[bytes]]):
    #     '''
    #     线程安全的向客户端发送数据
    #     @param data: str 要向客户端写的数据
    #     '''
    #     from twisted.internet import reactor
    #     if not self.transport.connected or not messages:
    #         return
    #     if isinstance(messages,list):
    #         for message in messages:
    #             reactor.callFromThread(self._send_message, message)
    #     else:
    #         reactor.callFromThread(self._send_message, messages)
    #
    # def safeWriteData(self,messages: bytes):
    #     '''
    #     线程安全的向客户端发送数据
    #     @param data: str 要向客户端写的数据
    #     '''
    #     from twisted.internet import reactor
    #     if not self.transport.connected or not messages:
    #         return
    #     reactor.callFromThread(self._send_message, messages)

            