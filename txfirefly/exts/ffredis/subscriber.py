# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : subscriber.py
# @Time     : 2021-02-20 0:16
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

import txredisapi as redis

from loguru import logger


class subscriberProtocol(redis.SubscriberProtocol):
	
	def connectionMade(self):
		if self.passwd:
			self.auth(self.passwd)
		
		self.doWhenConection()
	
	def doWhenConection(self):
		'''
			demo
				self.psubscribe("__keyevent@*__:expired") # 监听过期事件
				self.subscribe("listen1")   # 监听listen1频道
		:return:
		'''
		pass
	
	def messageReceived(self, pattern, channel, message):
		logger.info("pattern=%s, channel=%s message=%s" % (pattern, channel, message))
	
	def connectionLost(self, reason):
		logger.info("lost connection:{}".format(reason))


class subscriberFactory(redis.SubscriberFactory):
	# SubscriberFactory is a wapper for the ReconnectingClientFactory
	maxDelay = 120
	continueTrying = True
	protocol = subscriberProtocol
	
	def init_app(self, config):
		subscriberProtocol.passwd = config.get("REDIS_PASSWORD", None)