# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : server.py
# @Time     : 2021-02-18 23:26
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
from txfirefly.core.leafnode import leafNode, GlobalObject
from txrpc.server import RPCServer

class ServerNode(RPCServer,leafNode):
	"""
	:param
	"""
	def __init__(self, name: str):
		super(ServerNode, self).__init__(name)
	
	def run(self):
		from twisted.internet import reactor
		d = self._doWhenStart()
		d.addCallback(lambda ign : self.connectMaster())
		reactor.run()