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
from twisted.internet import defer

from txfirefly.client import ClientNode
from txfirefly.exts.ffrequest import FFrequest
from txrpc.globalobject import GlobalObject
from txrpc.utils import logger, asDeferred

with open("config.json","r") as f:
	GlobalObject().config = json.load(f)

logger.init()

app = ClientNode("CLIENT")

@app.startServiceHandle
def start():
	logger.debug("i am start")

@app.startServiceHandle
@defer.inlineCallbacks
def start2():
	# async with aiohttp.ClientSession() as session:
	# 	url = 'http://httpbin.org'
	# 	async with session.get(url) as response:
	# 		logger.debug(response.status)
	# 		logger.debug(response.text())
	ret = yield FFrequest.get("http://httpbin.org")
	# logger.debug(ret)
	defer.returnValue(ret)

@app.startServiceHandle
async def start3():
	async with aiohttp.ClientSession() as session:
		url = 'http://httpbin.org'
		async with session.get(url) as response:
			logger.debug(response.status)
			# logger.debug(await response.text())

app.run()