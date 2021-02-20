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
from twisted.internet.defer import DeferredLock
from twisted.protocols import policies
from twisted.internet import protocol

from txfirefly.net.common.manager import ConnectionManager
from txfirefly.net.tcp.datapack import DataPackProtoc
from txrpc.globalobject import GlobalObject
from txrpc.utils import logger
from twisted.internet import reactor

class BaseProtocol(protocol.Protocol,policies.TimeoutMixin):
    '''
    自定义协议
    '''
    _recv_buffer = b""                                                   # 用于暂时存放接收到的数据

    def __init__(self):
        self.lockBuffer = DeferredLock()
        self.process_com_lock = threading.RLock()
        self.conn_id = None

    def connectionLost(self, reason):
        '''
        连接中断自动触发函数
        推荐重写，可以加入连接对象移除，连接数量统计
        :param reason:
        :return:
        '''
        self.setTimeout(None)
        logger.msg('客户端: {} : {} 断开连接，当前总连接{}...'.format(self.transport.client[0], self.transport.client[1],self.factory.client_count))

    def connectionMade(self):
        '''
        连接成功后自动触发的函数
        推荐重写，可以加入连接对象添加，连接数量统计
        :return:
        '''
        self.setTimeout(GlobalObject().config.get("TIME_OUT_COUNT", 30))
        logger.msg('客户端:{} {} 连入...'.format(self.transport.client[0], self.transport.client[1]))

    def stringReceived(self, data):
        '''
        数据接受触发函数
        :param data:
        :return:
        '''
        # 重置超时定时器
        self.setTimeout(GlobalObject().config.get("TIME_OUT_COUNT", 30))

    def timeoutConnection(self):
        logger.warning("客户端:{} 超时断开连接...".format((self.transport.client[0], self.transport.client[1])))
        self.transport.loseConnection()

    def safeToWriteOriginalData(self,messages):
        '''
        线程安全的向客户端发送数据
        @param data: str 要向客户端写的数据
        '''
        if not self.transport.connected or not messages:
            return
        if isinstance(messages,list):
            for message in messages:
                reactor.callFromThread(self._send_message, message)
        else:
            reactor.callFromThread(self._send_message, messages)

class BaseFactory(protocol.ServerFactory):
    '''协议工厂'''

    protocol = BaseProtocol

    def __init__(self, dataprotocl = DataPackProtoc()):
        '''
        初始化
        '''
        self.service = None
        self.connmanager = ConnectionManager() # 连接管理器
        self.dataprotocl = dataprotocl         # 协议类

    def setDataProtocl(self, dataprotocl):
        '''
        '''
        self.dataprotocl = dataprotocl          # 设置协议类

    def doConnectionMade(self, conn):
        '''当连接建立时的处理'''
        pass

    def doConnectionLost(self, conn):
        '''
        连接断开时的处理
        '''
        pass

    def addServiceChannel(self, service):
        '''
        添加服务通道
        '''
        self.service = service

    def doDataReceived(self, conn, commandID, data):
        '''
        数据到达时的处理
            在这个系统内，这里的数据全部都通过 forwarding 发送给 gateway
            通过gateway分发
        '''
        defer_tool = self.service.callTarget("forwarding",commandID, conn, data)
        return defer_tool

    def produceResult(self, command):
        '''
        产生客户端需要的最终结果
        @param response: str 分布式客户端获取的结果
        '''
        return command.get("message",[])

    def loseConnection(self, connID):
        """
        主动端口与客户端的连接
        """
        self.connmanager.loseConnection(connID)

    def pushObject(self, msg, sendList):
        '''
        服务端向客户端推消息
        @param topicID: int 消息的主题id号
        @param msg: 消息的类容，protobuf 结构类型
        @param sendList: 推向的目标列表(客户端id 列表)
        '''
        logger.debug("需要向：{}发送数据\n发送的数据为:{}".format(sendList,msg))
        return self.connmanager.pushObject(msg, sendList)