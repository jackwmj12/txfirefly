# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : fastapiclient.py
# @Time     : 2021-03-09 3:26
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
import json

import aiohttp
import treq
from fastapi import FastAPI
from loguru import logger

client = None

app = FastAPI()


@app.get("/")
def read_root():
	return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
	return {"item_id": item_id, "q": q}

def register_rpc(app: FastAPI) -> None:
	"""
	把redis挂载到app对象上面
	:param app:
	:return:
	"""
	
	@app.on_event('startup')
	async def startup_event():
		"""
		获取链接
		:return:
		"""
		import asyncio
		loop = asyncio.get_event_loop()
		
		from twisted.internet import asyncioreactor
		asyncioreactor.install(eventloop=loop)
		
		from txfirefly.client import ClientNode
		from txrpc.globalobject import GlobalObject
		from twisted.internet import defer
		
		with open("config.json", "r") as f:
			GlobalObject().config = json.load(f)

		app.state.client = ClientNode("CLIENT")
		
		@app.state.client.startServiceHandle
		def start():
			logger.debug("i am start")
		
		@app.state.client.startServiceHandle
		@defer.inlineCallbacks
		def start2():
			ret = yield treq.get("http://httpbin.org")
			logger.debug(ret)
			defer.returnValue(ret)
			
		@app.state.client.startServiceHandle
		async def start3():
			pass
			# async with aiohttp.ClientSession() as session:
			# 	url = 'http://httpbin.org'
			# 	async with session.get(url) as response:
			# 		logger.debug(response.status)
			# logger.debug(await response.text())
		
		app.state.client.install()
	
	@app.on_event('shutdown')
	async def shutdown_event():
		"""
		关闭
		:return:
		"""
	# app.state.rpc_client.close()
	# await app.state.rpc_client.wait_closed()


register_rpc(app)

if __name__ == "__main__":
	import uvicorn
	
	uvicorn.run(app='demo.base.fastapiclient:app', host="0.0.0.0", port=5000, reload=True, debug=True)