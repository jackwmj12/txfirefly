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
import asyncio

from twisted.internet import asyncioreactor

loop = asyncio.get_event_loop()
asyncioreactor.install(eventloop=loop)

import json

import aiohttp

from txfirefly.exts.ffrequest import FFrequest
from txfirefly.server import ServerNode
from txrpc.distributed.manager import RemoteUnFindedError
from txrpc.globalobject import GlobalObject
from txrpc.server import RPCServer
from txrpc.utils import logger

NODE_NAME = "SERVER"

with open("config.json","r") as f:
    GlobalObject().config = json.load(f)

logger.init()

from twisted.internet import reactor

def fun():
    d = RPCServer.callRemote("CLIENT", "client_test")
    if not d:
        reactor.stop()
    else:
        d.addCallback(logger.debug)
        d.addErrback(lambda ign : reactor.stop())
    return d

server = ServerNode("SERVER")

@server.childConnectHandle
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
    reactor.callLater(1, fun)
    
    # for i in range(100000):
    #     reactor.callLater(i * 0.2 + 1, fun)

@server.childConnectHandle
async def fun2(name, transport):
    logger.debug(64*"*")
    async with aiohttp.ClientSession() as session:
        url = 'http://httpbin.org'
        async with session.get(url) as response:
            logger.debug(response.status)
            # logger.debug(await response.text())

@server.childLostConnectHandle
def fun3(name):
    ret = yield FFrequest.get("http://httpbin.org")
    # logger.debug(ret)
    return ret

@server.childLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    logger.debug("{} lost connect".format(childId))

server.run()