# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : clientapp.py
# @Time     : 2021-02-19 0:35
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

from txrpc.globalobject import remoteserviceHandle
from txrpc.rpc import RPCClient
from txrpc.utils import logger

def fun():
	d = RPCClient.callRemote("SERVER", "server_test")
	d.addCallback(logger.debug)
	d.addErrback(logger.err)
	return d

@remoteserviceHandle("SERVER")
def client_test():
	from twisted.internet import reactor
	reactor.callLater(1, fun)
	return "this is a response from client"
