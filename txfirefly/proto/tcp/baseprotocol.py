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

class BaseProtocol(protocol.Protocol,policies.TimeoutMixin):
    '''
    自定义协议
    '''
    factory: Union["BaseFactory", None]
    _recv_buffer = b""                                               # 用于暂时存放接收到的数据

    def __init__(self):
        self.lockBuffer: DeferredLock = DeferredLock()
        self.process_com_lock: threading.RLock = threading.RLock()
        self.conn_info: Dict = {}  # 连接信息
        self.conn_id: Union[str, int, None] = None  # 连接唯一ID
        
    def connectionMade(self):
        '''
        连接成功后自动触发的函数
        推荐重写，可以加入连接对象添加，连接数量统计
        :return:
        '''
        logger.info('Client %d login in.[%s,%d]' % (self.transport.sessionno, self.transport.client[0], self.transport.client[1]))
        self.setTimeout(GlobalObject().config.get("TIME_OUT_COUNT", 10 * 60))
        logger.info('Client : {} {} connected...'.format(self.transport.client[0], self.transport.client[1]))
        self.datahandler = self.dataHandleCoroutine()  # 创建数据生成器
        self.datahandler.__next__()  # 创建一个生成器，当数据接收时，触发生成器
        self.conn_id = self.transport.sessionno  # 连接ID
        self.factory.doConnectionMade(self, self.conn_id)
    
    def connectionLost(self, reason):
        '''
        连接中断自动触发函数
        推荐重写，可以加入连接对象移除，连接数量统计
        :param reason:
        :return:
        '''
        # logger.info(f'Client<{self.transport.sessionno}|{self.conn_id}> login out.')
        self.setTimeout(None)
        self.factory.doConnectionLost(self, self.conn_id)

    def dataReceived(self, data):
        '''
        数据到达处理
        @param data: str 客户端传送过来的数据
        '''
        self.setTimeout(GlobalObject().config.get("TIME_OUT_COUNT", 10 * 60))  # 添加超时定时器
        self.datahandler.send(data)  # 触发datahandler生成器

    def dataHandleCoroutine(self):
        """
        """
        while True:
            data = yield
            self._recv_buffer += data
            # logger.debug("TCP recv <1>:{}".format([hex(x) for x in self._recv_buffer]))

    def timeoutConnection(self):
        logger.warning("客户端:{} 超时断开连接...".format((self.transport.client[0], self.transport.client[1])))
        self.transport.loseConnection()

    def _send_message(self, data: bytes):  # 将数据构造好并发送
        '''
        发送函数的封装
        :param data:
        :return:
        '''
        self.transport.write(data)

    def safeToWriteData(self, messages: Union[bytes,List[bytes]]):
        '''
        线程安全的向客户端发送数据
        @param data: str 要向客户端写的数据
        '''
        from twisted.internet import reactor
        if not self.transport.connected or not messages:
            return False
        if isinstance(messages,list):
            for message in messages:
                reactor.callFromThread(self._send_message, message)
        else:
            reactor.callFromThread(self._send_message, messages)
        return True

    def safeWriteData(self,messages: bytes):
        '''
        线程安全的向客户端发送数据
        @param data: str 要向客户端写的数据
        '''
        from twisted.internet import reactor
        if not self.transport.connected or not messages:
            return False
        reactor.callFromThread(self._send_message, messages)
        return True

class BaseFactory(protocol.ServerFactory):
    '''
    协议工厂
    '''

    protocol = BaseProtocol

    def __init__(self, dataprotocl = DataPackProtocol()):
        '''
        初始化
        '''
        self.connmanager = ConnectionManager() # 连接管理器
        self.dataprotocl = dataprotocl         # 协议类

    def setDataProtocl(self, dataprotocl):
        '''
        '''
        self.dataprotocl = dataprotocl          # 设置协议类

    def doConnectionMade(self, conn: BaseProtocol, conn_id: str):
        '''
        当连接建立时的处理
        '''
        self.connmanager.addConnection(conn, conn_id)
    
    def doConnectionLost(self, conn : BaseProtocol, conn_id):
        '''
        连接断开时的处理
        '''
        logger.info(f"Client<{conn_id}> lost connection")
        if conn == self.connmanager.getConnectionByID(conn_id).instance:
            self.connmanager.dropConnectionByID(conn_id)
        logger.info(f"Clients residue : {self.connmanager.getNowConnCnt()}")

    def doDataReceived(self, conn, commandID, data):
        '''
        '''
        pass

    def loseConnectionByConnID(self, connID):
        """
        主动端口与客户端的连接
        """
        self.connmanager.loseConnectionByConnID(connID)

    def sendMessage(self, conn_id: str, msg: bytes):
        '''
        服务端向客户端推消息
        @param conn_id: 需要发送的目标ID
        @param msg: 消息的内容
        '''
        return self.connmanager.pushMessageToConn(conn_id, msg)

    def resetConnID(self,sourceId, dstId):
        '''
        :parameter
        '''
        source_conn = self.connmanager.getConnectionByID(sourceId)
        dst_conn = self.connmanager.getConnectionByID(dstId)
        if source_conn and not dst_conn:
            self.connmanager.dropConnectionByID(sourceId)
            source_conn.instance.conn_id = dstId
            self.connmanager.addConnection(source_conn.instance, dstId)
            # logger.debug(f"reset the conn <{sourceId}> -> <{dstId}> success")
            logger.debug(f"连接池 连接重置 <{sourceId}> -> <{dstId}> 成功")
            return True
        else:
            # logger.error("the sourceId is not exist")
            logger.debug(f"连接池 连接 <{sourceId}> 不存在 获取 连接 <{dstId}> 已存在")
            return False


    def setConnInfo(self, connId, connInfo):
        '''

        :param connId:
        :param connInfo:
        :return:
        '''
        try:
            connection = self.connmanager.getConnectionByID(connId)
            if connection and connection.instance:
                connection.instance.conn_info.update(**connInfo)
                logger.debug(f"客户端<{connId}> 重置连接信息成功 {connection.instance.conn_info}")
                return True
        except Exception as e:
            logger.error(e)
        return False