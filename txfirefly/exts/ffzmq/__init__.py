# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : __init__.py
# @Time     : 2021-02-20 0:12
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
import zmq
from txzmq import ZmqRequestTimeoutError, ZmqPubConnection, ZmqFactory, ZmqEndpoint, ZmqSubConnection, ZmqREQConnection, \
	ZmqREPConnection, ZmqPushConnection, ZmqPullConnection

from txrpc.utils.log import logger


def onPrint(reply):
	logger.info("Got reply: %s" % (reply))

def onTimeout(fail):
	fail.trap(ZmqRequestTimeoutError)
	print("Timeout on request, is reply server running?")

class ZMQfactory():
	
	def __init__(self):
		self.pub_ = None
		self.sub_ = None
		self.req_ = None
		self.rep_ = None
		self.push_ = None
		self.pull_ = None
		self.timeout = 0.95
	
	def set_timeout(self, timeout):
		self.timeout = timeout
	
	# pub sub 相关
	def add_pub(self, endpoint):
		if endpoint:
			logger.debug("开始运行 PUB 服务器,服务地址为:{}...".format(endpoint))
			self.pub_ = ZmqPubConnection(ZmqFactory(), ZmqEndpoint("bind", endpoint))
	
	def add_sub(self, endpoint):
		if endpoint:
			logger.debug("开始运行 SUB 服务器,连接地址为:{}...".format(endpoint))
			self.sub_ = ZmqSubConnection(ZmqFactory(), ZmqEndpoint("connect", endpoint))
			self.set_callback()
	
	def set_filter(self, filter_=None):
		'''
		请输入需要接受的主题（必须调用该函数，否则无法收到任何数据）
		:param filter_:  type str_list
		:return:
		'''
		if self.sub_:
			if filter_:
				for item in filter_:
					self.sub_.subscribe(item.encode())
			else:
				self.sub_.subscribe(b'')
		else:
			logger.error("请初始化SUB端口")
	
	def set_callback(self):
		if self.sub_:
			self.sub_.gotMessage = self.subscribeReceived
		else:
			logger.error("请初始化SUB端口")
	
	def subscribeReceived(self, *args):
		'''
		当接收到广播数据时,会触发该函数
		:param data:
		:return:
		'''
	
	def publishData(self, tag, data):
		'''
		从push服务器向外推送数据
		:param tag:
		:param data:
		:return:
		'''
	
	# req-rep 相关
	def add_req(self, endpoint):
		'''
		设置 req 对象
		:param endpoint:
		:return:
		'''
		if endpoint:
			logger.debug("开始运行 REQ 服务器,连接地址为:{}...".format(endpoint))
			self.req_ = ZmqREQConnection(ZmqFactory(), ZmqEndpoint('connect', endpoint))
	
	def add_rep(self, endpoint, callBack=onPrint):
		'''
		设置 rep 对象
		:param endpoint:
		:param callBack:
		:return:
		'''
		if endpoint:
			logger.debug("开始运行 REP 服务器,监听地址为:{}...".format(endpoint))
			self.rep_ = ZmqREPConnection(ZmqFactory(), ZmqEndpoint('bind', endpoint))
			self.rep_.gotMessage = callBack
	
	def sendReq(self, data, callBack=onPrint, errBack=onTimeout):
		'''
		发送 req 信息
		:param data:
		:param callBack:
		:param errBack:
		:return:
		'''
		try:
			d = self.req_.sendMsg(data, timeout=self.timeout)
			d.addCallback(callBack).addErrback(errBack)
		except Exception as e:
			logger.error(e)
	
	# push pull 相关
	def add_push(self, endpoint):
		'''

		:param endpoint:
		:return:
		'''
		if endpoint:
			logger.debug("开始运行 PUSH 服务器,监听地址为:{}...".format(endpoint))
			self.push_ = ZmqPushConnection(ZmqFactory(), ZmqEndpoint('connect', endpoint))
	
	def add_pull(self, endpoint, callBack=onPrint):
		'''

		:param endpoint:
		:param callBack:
		:return:
		'''
		if endpoint:
			logger.debug("开始运行 PULL 服务器,连接地址为:{}...".format(endpoint))
			self.pull_ = ZmqPullConnection(ZmqFactory(), ZmqEndpoint('bind', endpoint))
			self.pull_.onPull = callBack
	
	def pushData(self, data):
		'''

		:param data:
		:return:
		'''
		try:
			self.push_.push(data)
		except zmq.error.Again:
			logger.error("Skipping, no pull consumers...")