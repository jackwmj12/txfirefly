# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : pubsub.py
# @Time     : 2021-02-20 0:09
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

from txzmq import ZmqPubConnection, ZmqFactory, ZmqEndpoint, ZmqSubConnection, ZmqRequestTimeoutError

from txrpc.utils import logger


def onTimeout(fail):
    fail.trap(ZmqRequestTimeoutError)
    print("Timeout on request, is reply server running?")

class pubModel():
    '''
    zmq 发布者模型
    '''

    def __init__(self,endpoint):
        if endpoint:
            logger.debug("开始运行 PUB 服务器,服务地址为:{}...".format(endpoint))
            self._pub = ZmqPubConnection(ZmqFactory(), ZmqEndpoint("bind", endpoint))

    def publishData(self,tag,data):
        '''
        从push服务器向外推送数据
        :param tag:
        :param data:
        :return:
        '''
        self._pub.publish(data,tag)

class subModel():
    '''
    zmq 订阅者模型
    '''

    def __init__(self,endpoint,callBack = None):
        try:
            if endpoint:
                logger.debug("开始运行 SUB 服务器,连接地址为:{}...".format(endpoint))
                self._sub = ZmqSubConnection(ZmqFactory(), ZmqEndpoint("connect", endpoint))
                if callBack:
                    self.setCallback(callBack)
                else:
                    self.setCallback(self.doDataReceived)
        except Exception as e:
            logger.err(e)

    def setFilter(self,filter_=None):
        if self._sub:
            if filter_:
                for item in filter_:
                    self._sub.subscribe(item.encode())
            else:
                self._sub.subscribe(b'')
        else:
            logger.err("设置过滤器之前请初始化SUB端口")

    def setCallback(self,callBack):
        if self._sub:
            self._sub.gotMessage = callBack
        else:
            logger.err("绑定回调前请初始化SUB端口")

    def doDataReceived(self,*args):
        '''
        当接收到广播数据时,会触发该函数
        :param data:
        :return:
        '''
        # defer_tool = self.service.callTarget(*args)
        # return defer_tool
        # Log.msg(args)