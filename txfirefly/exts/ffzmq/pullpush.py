# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : pullpush.py
# @Time     : 2021-02-20 0:10
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
from txzmq import ZmqPubConnection, ZmqFactory, ZmqEndpoint, ZmqSubConnection, ZmqPullConnection, ZmqPushConnection

from txrpc.utils.log import logger


class pushMode():
	'''
	zmq 推送者模型
	'''
	
	def __init__(self, endpoint):
		if endpoint:
			logger.debug("开始运行 PUSH 服务器,监听地址为:{}...".format(endpoint))
			self._push = ZmqPushConnection(ZmqFactory(), ZmqEndpoint('connect', endpoint))
		else:
			self._push = None
	
	def pushData(self, data):
		'''

        :param data:
        :return:
        '''
		if self._push:
			self._push.push(data)
		else:
			logger.error("Skipping, no pull consumers...")


class pullMode():
	'''
	zmq 接受者模型
    '''
	
	def __init__(self, endpoint, callBack=None):
		if endpoint:
			logger.debug("开始运行 PULL 服务器,连接地址为:{}...".format(endpoint))
			self._pull = ZmqPullConnection(ZmqFactory(), ZmqEndpoint('bind', endpoint))
			if callBack:
				self._pull.onPull = callBack
			else:
				self._pull.onPull = self.doDataReceived
		else:
			self._pull = None
	
	def doDataReceived(self, *args):
		'''
        当接收到广播数据时,会触发该函数
        :param data:
        :return:
        '''
		# defer_tool = self.service.callTarget(*args)
		# return defer_tool
		logger.info(args)
