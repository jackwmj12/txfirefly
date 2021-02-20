# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : reqresp.py
# @Time     : 2021-02-20 0:11
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

from txzmq import ZmqPubConnection, ZmqFactory, ZmqEndpoint, ZmqSubConnection, ZmqREQConnection, \
	ZmqRequestTimeoutError, \
	ZmqREPConnection, ZmqPushConnection, ZmqPullConnection

from txrpc.utils import logger


def onTimeout(fail):
	fail.trap(ZmqRequestTimeoutError)
	print("Timeout on request, is reply server running?")


class reqModel():
	'''

	'''
	
	def __init__(self, endpoint):
		if endpoint:
			logger.debug("开始运行 REQ 服务器,连接地址为:{}...".format(endpoint))
			self._req = ZmqREQConnection(ZmqFactory(), ZmqEndpoint('connect', endpoint))
		else:
			self._req = None
		self.timeout = 0.95
	
	def sendReq(self, data):
		'''
		发送 req 信息
		:param data:
		:param callBack:
		:param errBack:
		:return: 返回defer对象
		'''
		if self._req:
			d = self._req.sendMsg(data, timeout=self.timeout)
			return d
		else:
			logger.err("请创建请求者实例")
		return None


class repModel():
	'''
	zmq 回复者模型
	'''
	
	def __init__(self):
		self.rep_ = None
		self.timeout = 0.95
	
	def set_timeout(self, timeout):
		self.timeout = timeout
	
	def add_rep(self, endpoint, callBack=None):
		'''
		设置 rep 对象
		:param endpoint:
		:param callBack:
		:return:
		'''
		if endpoint:
			logger.debug("开始运行 REP 服务器,监听地址为:{}...".format(endpoint))
			self._rep = ZmqREPConnection(ZmqFactory(), ZmqEndpoint('bind', endpoint))
			if callBack:
				self._rep.gotMessage = callBack
			else:
				self._rep.gotMessage = self.doDataReceived
	
	def doDataReceived(self, *args):
		'''
		当接收到广播数据时,会触发该函数
		:param data:
		:return:
		'''
		# defer_tool = self.service.callTarget(*args)
		# return defer_tool
		logger.msg(args)