# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : monitor.py
# @Time     : 2021-02-20 0:17
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
from __future__ import print_function

import txredisapi

from txrpc.utils import logger


class monitorProtocol(txredisapi.MonitorProtocol):
	def connectionMade(self):
		if self.passwd:
			self.auth(self.passwd)
		
		self.doWhenConection()
	
	def doWhenConection(self):
		'''

		:return:
		'''
		self.monitor()
	
	def messageReceived(self, message):
		logger.msg(">> %s" % message)
	
	def connectionLost(self, reason):
		logger.msg("lost connection:{}".format(reason))


class monitorFactory(txredisapi.MonitorFactory):
	# also a wapper for the ReconnectingClientFactory
	maxDelay = 120
	continueTrying = True
	protocol = monitorProtocol
	
	def init_app(self, config):
		monitorProtocol.passwd = config.get("REDIS_PASSWORD", None)