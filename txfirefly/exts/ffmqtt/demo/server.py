# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : server.py
# @Time     : 2021-02-20 0:21
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
import sys

from txfirefly.exts.ffmqtt.server import MQTTFactory

PORT = 5982

def loopSendMessage(factory):
	''':param'''
	from twisted.internet import reactor
	factory.publish(topic=b"test", message=b"hello world")
	reactor.callLater(300, loopSendMessage, factory)

if __name__ == '__main__':
	from twisted.internet import reactor
	from loguru import logger
	
	factory = MQTTFactory()
	
	reactor.listenTCP(PORT, factory)
	
	reactor.callLater(5, loopSendMessage, factory)
	
	logger.debug('Started server at: *:%s' % PORT)
	
	reactor.run()