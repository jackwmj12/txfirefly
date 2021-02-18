# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : server.py
# @Time     : 2021-02-19 0:20
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
from txfirefly.master import MasterNode
from txfirefly.server import ServerNode
from txrpc.rpc import RPCServer
from txrpc.utils import logger

logger.init()

def fun():
    d = RPCServer.callRemote("CLIENT", "client_test")
    if not d:
        return None
    d.addCallback(logger.debug)
    d.addErrback(logger.err)
    return d

def doChildConnect(name, transport):
    '''
    :return
    '''
    logger.debug("{} connected".format(name))

    # d = RPCServer.callRemote("CLIENT", "client_test")
    # if not d:
    #     return None
    # d.addCallback(logger.debug)
    # d.addErrback(logger.err)
    
    from twisted.internet import reactor
    reactor.callLater(1, fun)

    # for i in range(1000):
    #     reactor.callLater(i * 2 + 1, fun)

def doChildLostConnect(childId):
    '''
    :return
    '''
    logger.debug("{} lost connect".format(childId))

server = ServerNode("SERVER",9999,service_path="demo.base.app.serverapp")
server.connectMaster({
    "SRC_NAME" : "server",
    "PORT" : 9998,
    "HOST" : "127.0.0.1"
})
server.setDoWhenChildConnect(doChildConnect)
server.setDoWhenChildLostConnect(doChildLostConnect)
server.run()