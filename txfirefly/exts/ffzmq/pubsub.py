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
from typing import List

from txzmq import ZmqPubConnection, ZmqFactory, ZmqEndpoint, ZmqSubConnection, ZmqRequestTimeoutError

from loguru import logger


def onTimeout(fail):
    fail.trap(ZmqRequestTimeoutError)
    print("Timeout on request, is reply server running?")

class PubModel():
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
    
    def publish(self,tag,data):
        '''
        从push服务器向外推送数据
        :param tag:
        :param data:
        :return:
        '''
        self._pub.publish(data,tag)

class SubModel():
    '''
    zmq 订阅者模型
    '''

    def __init__(self,endpoint,callBack = None):
        try:
            if endpoint:
                logger.debug("开始运行 SUB 客户端 , 连接的服务器地址为:{}...".format(endpoint))
                self._sub = ZmqSubConnection(ZmqFactory(), ZmqEndpoint("connect", endpoint))
                if callBack:
                    self.setCallback(callBack)
                else:
                    self.setCallback(self.doDataReceived)
        except Exception as e:
            logger.error(e)
    
    def subscribe(self,topics=None):
        if self._sub:
            if isinstance(topics,List):
                for topic in topics:
                    self._subscribe(topic)
            else:
                self._subscribe(topics)
        else:
            logger.error("设置过滤器之前请初始化 SUB 端口")
    
    def _subscribe(self,topic=None):
        if topic:
            if isinstance(topic, bytes):
                self._sub.subscribe(topic)
            elif isinstance(topic, str):
                self._sub.subscribe(topic.encode())
    
    def subscribeAll(self):
        self._sub.subscribe(b'')
    
    def setCallback(self,callBack):
        if self._sub:
            self._sub.gotMessage = callBack
        else:
            logger.error("绑定回调前请初始化 SUB 端口")

    def doDataReceived(self,*args):
        '''
        当接收到广播数据时,会触发该函数
        :param data:
        :return:
        '''
        logger.debug(f"rcev zmq msg : {args}")
        
        
    def shutdown(self):
        self._sub.shutdown()