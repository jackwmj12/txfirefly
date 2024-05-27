# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : baseprotocol.py
# @Time     : 2024-01-22 16:31
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
import threading
from typing import Union, List
from twisted.internet.defer import DeferredLock
from twisted.protocols import policies
from twisted.internet import protocol
from loguru import logger

from demo.tcp.connmanager import ConnectionManager

TIME_OUT_COUNT = 300 # 超时计数器300秒

PROTOCOL_CHECK_SUCCESS = 1 # 单帧校验成功
PROTOCOL_CHECK_FAILED = -1 # 单帧协议校验失败
PROTOCOL_CHECK_UNKNOWN = -2 # 单帧协议未接受完全

class BaseProtocol(protocol.Protocol, policies.TimeoutMixin):
    '''
    自定义协议
    '''
    factory: Union["BaseFactory", None]
    _recv_buffer = b""  # 用于暂时存放接收到的数据

    def __init__(self):
        self.lockBuffer = DeferredLock()
        self.process_com_lock = threading.RLock()
        self.conn_info = {}  # 连接信息
        self.conn_id = None  # 连接唯一ID

    def connectionMade(self):
        '''
        连接成功后自动触发的函数
        推荐重写，可以加入连接对象添加，连接数量统计
        :return:
        '''
        logger.info('Client %d login in.[%s,%d]' % (
        self.transport.sessionno, self.transport.client[0], self.transport.client[1]))
        self.conn_id = self.transport.sessionno  # 连接ID
        self.setTimeout(TIME_OUT_COUNT)
        logger.info('Client : {} {} connected...'.format(self.transport.client[0], self.transport.client[1]))
        self.datahandler = self.dataHandleCoroutine()  # 创建数据生成器
        self.datahandler.__next__()  # 创建一个生成器，当数据接收时，触发生成器
        self.factory.doConnectionMade(self, self.conn_id)

    def connectionLost(self, reason):
        '''
        连接中断自动触发函数
        推荐重写，可以加入连接对象移除，连接数量统计
        :param reason:
        :return:
        '''
        logger.info('Client %d login out.' % (self.transport.sessionno))
        self.setTimeout(None)
        self.factory.doConnectionLost(self, self.conn_id)

    def timeoutConnection(self):
        logger.warning("客户端:{} 超时断开连接...".format((self.transport.client[0], self.transport.client[1])))
        self.transport.loseConnection()

    def dataReceived(self, data):
        '''
        数据到达处理
        @param data: str 客户端传送过来的数据
        '''
        self.setTimeout(TIME_OUT_COUNT)  # 添加超时定时器
        self.datahandler.send(data)  # 触发datahandler生成器

    def dataHandleCoroutine(self):
        """
        """
        while True:
            data = yield
            self._recv_buffer += data
            # logger.debug("TCP recv <1>:{}".format(
            #     [hex(x) for x in data]))
            while len(self._recv_buffer) >= self.getProtocolMinLength():
                state, offset = self.factory.unpackData(self, data)
                if state == PROTOCOL_CHECK_SUCCESS:  # 协议校验成功,收到一条完整协议
                    receivedData = self._recv_buffer[0, offset]
                    self.factory.doDataReceived(self, receivedData)
                    self._recv_buffer = self._recv_buffer[offset:]
                elif state == PROTOCOL_CHECK_FAILED:
                    self._recv_buffer = self._recv_buffer[offset:]


    def getProtocolMinLength(self):
        '''
            协议最小解析长度,超过 PROTOCOL_MIN_LENGTH 才能加入解析
        :return:
        '''
        raise NotImplementedError()

    def _send_message(self, data: bytes):  # 将数据构造好并发送
        '''
        发送函数的封装
        :param data:
        :return:
        '''
        self.transport.write(data)

    def safeToWriteData(self, messages: bytes):
        '''
        线程安全的向客户端发送数据
        @param data: str 要向客户端写的数据
        '''
        from twisted.internet import reactor
        if not self.transport.connected or not messages:
            return
        reactor.callFromThread(self._send_message, messages)

class BaseFactory(protocol.ServerFactory):
    '''
    协议工厂
    '''

    protocol = BaseProtocol

    def __init__(self):
        '''
        初始化
        '''
        self.connmanager = ConnectionManager()  # 连接管理器

    def setDataProtocl(self, dataprotocl):
        '''
        '''
        self.dataprotocl = dataprotocl  # 设置协议类

    def doConnectionMade(self, conn: BaseProtocol, conn_id: str):
        '''
        当连接建立时的处理
        '''
        self.connmanager.addConnection(conn, conn_id)

    def doConnectionLost(self, conn: BaseProtocol, conn_id):
        '''
        连接断开时的处理
        '''
        # logger.debug(conn)
        # logger.debug(conn_id)
        # logger.debug(self.connmanager.connections)
        if conn == self.connmanager.getConnectionByID(conn_id).instance:
            self.connmanager.dropConnectionByID(conn_id)
        logger.info("Clients residue : {}".format(self.connmanager.getNowConnCnt()))

    def doDataReceived(self, conn, data):
        '''
        数据到达时的处理
            在这个系统内，这里的数据全部都通过 forwarding 发送给 gateway
            通过gateway分发
        '''

    def loseConnectionByConnID(self, connID):
        """
        主动端口与客户端的连接
        """
        self.connmanager.loseConnectionByConnID(connID)

    def pushDataTo(self, msg: bytes, sendList: Union[str, List[str]]):
        '''
        服务端向客户端推消息
        @param topicID: int 消息的主题id号
        @param msg: 消息的类容，protobuf 结构类型
        @param sendList: 推向的目标列表(客户端id 列表)
        '''
        logger.debug("需要向：{}发送数据\n发送的数据为:{}".format(sendList, msg))
        return self.connmanager.pushMessageToConn(msg, sendList)

    def resetConnID(self, sourceId, dstId):
        '''
        :parameter
        '''
        coon = self.connmanager.getConnectionByID(sourceId)
        if coon:
            self.connmanager.dropConnectionByID(sourceId)
            self.connmanager.addConnection(coon.instance, dstId)
            # logger.debug(f"reset the conn <{sourceId}> -> <{dstId}> success")
            logger.debug(f"连接池 连接重置 <{sourceId}> -> <{dstId}> 成功")
        else:
            # logger.error("the sourceId is not exist")
            logger.debug(f"连接池 初始连接 <{sourceId}> 不存在")