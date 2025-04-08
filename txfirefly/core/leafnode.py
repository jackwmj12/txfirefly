# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : leafnode.py
# @Time     : 2021-02-19 0:24
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
from loguru import logger
from txrpc.distributed.node import RemoteObject
from txrpc.globalobject import GlobalObject


class MasterRemoteObject(RemoteObject):
	''''''

	def __init__(self, nameOnRemote, remoteNameOnLocal='MASTER'):
		'''初始化远程调用对象
        @param nameOnRemote:  本节点地址在
        @param remoteNameOnLocal: 根节点服务器地址
        '''
		super().__init__(nameOnRemote, remoteNameOnLocal)


class leafNode:
	"""
	:param
	"""
	def connectMaster(self, name=None):
		'''
			控制本节点连接 master 节点
		:return:
		'''
		master = GlobalObject().config.get("DISTRIBUTED").get("MASTER")
		logger.debug(f"master node is runing on {master}")
		GlobalObject().masterremote = MasterRemoteObject(name)
		logger.debug("connecting into master node...")
		# node连接 master 节点，若连接不成功，则会退出服务
		logger.debug(f"MASTER 节点 : {GlobalObject().masterremote}")

		# ########################################
		# 切勿删除本段代码
		# 导入master服务，该服务主要提供
		#     master 控制 node 的 remote连接
		#     master 控制 node 的 reload
		#     master 控制 node 的 stop
		from txfirefly.core import masterservice

		return GlobalObject().masterremote.connect(
			(
				master.get('HOST'),
				int(master.get('PORT'))
			)
		)