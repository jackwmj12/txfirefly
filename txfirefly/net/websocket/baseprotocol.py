# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : baseprotocol.py
# @Time     : 2021-02-20 0:57
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

from autobahn.twisted import WebSocketServerProtocol, WebSocketServerFactory
from twisted.internet import reactor
from twisted.protocols import policies
from txzmq import ZmqRequestTimeoutError

from txfirefly.net.common.manager import ConnectionManager
from txfirefly.net.websocket.datapack import DataPackProtoc
from txrpc.globalobject import GlobalObject
from txrpc.utils import logger


def onTimeout(fail):
    fail.trap(ZmqRequestTimeoutError)
    print("Timeout on request, is reply server running?")

class WebSocket(WebSocketServerProtocol,policies.TimeoutMixin):
    '''
        Websocket服务
    '''
    _recv_buffer = b""
    datahandler = None

    def onConnect(self, request):
        logger.msg("Client connecting: {}".format(request.peer))
        self.setTimeout(GlobalObject().config.get("TIME_OUT_COUNT", 30))
        self.factory.connmanager.addConnection(self)
        self.factory.doConnectionMade(self)
        self.datahandler = self.dataHandleCoroutine()
        self.datahandler.__next__()

    def onClose(self, wasClean, code, reason):
        '''

        :param wasClean:
        :param code:
        :param reason:
        :return:
        '''
        logger.msg('Client %d login out: %s' % (self.transport.sessionno, reason))
        self.factory.doConnectionLost(self)
        self.factory.connmanager.dropConnectionByID(self.transport.sessionno)
        self.setTimeout(None)

    def onOpen(self):
        logger.msg("WebSocket connection open.")

    def dataHandleCoroutine(self):
        """
        """


    def processCommand(self,command_):
        '''

        :param command_:
        :return:
        '''
        return command_

    def onMessage(self, payload, isBinary):
        '''
        接受websocket数据触发函数
        :param payload:
        :param isBinary:
        :return:
        '''
        self.setTimeout(GlobalObject().config.get("TIME_OUT_COUNT", 30))
        self.datahandler.send(payload)

        # if isBinary:
        #     Log.msg("Binary message received: {} bytes".format(len(payload)))
        # else:
        #     Log.msg("Text message received: {}".format(payload.decode('utf8')))
        #
        # ## echo back message verbatim
        # self.sendMessage(payload, isBinary)

    def safeToWriteData(self, data, command):
        '''线程安全的向客户端发送数据
        @param data: str 要向客户端写的数据
        '''
        if not self.transport.connected or data is None:
            return
        senddata = self.factory.produceResult(data, command)
        reactor.callFromThread(self.sendMessage, senddata, isBinary=True)

    def safeToWriteJson(self,json_):
        if not self.transport.connected or not json_:
            return
        reactor.callFromThread(self.sendMessage, json_, isBinary=False)

class WebSocketFactory(WebSocketServerFactory):
    protocol = WebSocket

    def __init__(self, dataprotocl = DataPackProtoc()):
        super(WebSocketFactory,self).__init__()
        self.service = None
        self.connmanager = ConnectionManager()
        self.dataprotocl = dataprotocl

    def setDataProtocl(self, dataprotocl):
        '''
        '''
        self.dataprotocl = dataprotocl

    def doConnectionMade(self, conn):
        '''当连接建立时的处理'''
        pass

    def doConnectionLost(self, conn):
        '''连接断开时的处理'''
        pass

    def addServiceChannel(self, service):
        '''添加服务通道'''
        self.service = service

    def doDataReceived(self, conn, commandID, data):
        '''数据到达时的处理'''
        # defer_tool = self.service.callTarget(commandID, conn, data)
        # return defer_tool

    def produceResult(self, command, response):
        '''产生客户端需要的最终结果
        @param response: str 分布式客户端获取的结果
        '''
        return self.dataprotocl.pack(command, response)

    def loseConnection(self, connID):
        """主动端口与客户端的连接
        """
        self.connmanager.loseConnection(connID)

    def pushObject(self, msg, sendList):
        '''服务端向客户端推消息
        @param msg: 消息的类容，protobuf结构类型
        @param sendList: 推向的目标列表(客户端id 列表)
        '''
        self.connmanager.pushObject(msg, sendList)
        # Log.debug("WebSocket向外推送数据:{}".format(msg))