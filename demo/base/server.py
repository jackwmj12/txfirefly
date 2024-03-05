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


from twisted.internet import asyncioreactor, defer

import asyncio

loop = asyncio.get_event_loop()
asyncioreactor.install(eventloop=loop)

import json

import aiohttp
import treq
from txfirefly.rpc.server import Server
from txrpc.globalobject import GlobalObject, rootWhenLeafConnectHandle, rootWhenLeafLostConnectHandle, \
    startServiceHandle
from txrpc.server import RPCServer
from loguru import logger

NODE_NAME = "SERVER"

with open("config.json","r") as f:
    GlobalObject().config = json.load(f)

def fun():
    from twisted.internet import reactor
    
    d = RPCServer.callRemote("CLIENT", "client_test")
    if not d:
        reactor.stop()
    else:
        d.addCallback(logger.debug)
        d.addErrback(lambda ign : reactor.stop())
    return d

server = Server("SERVER")

@rootWhenLeafConnectHandle
def doChildConnect(name, transport):
    '''
    :return
    '''
    from twisted.internet import reactor
    
    logger.debug("{} connected".format(name))
    
    # d = RPCServer.callRemote("CLIENT", "client_test")
    # if not d:
    #     return None
    # d.addCallback(logger.debug)
    # d.addErrback(logger.error)
    reactor.callLater(1, fun)
    
    # for i in range(100000):
    #     reactor.callLater(i * 0.2 + 1, fun)

@rootWhenLeafConnectHandle
async def fun2(name, transport):
    async with aiohttp.ClientSession() as session:
        url = 'http://httpbin.org'
        async with session.get(url) as response:
            logger.debug(response.status)
            # logger.debug(await response.text())

@startServiceHandle
@defer.inlineCallbacks
def fun3():
    resp = yield treq.get("http://httpbin.org")
    ret = yield treq.content(resp)
    logger.debug(ret)
    return ret

@rootWhenLeafLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    logger.debug("{} lost connect".format(childId))

server.run()