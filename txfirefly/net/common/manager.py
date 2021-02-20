# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : manager.py
# @Time     : 2021-02-20 0:54
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
from txfirefly.net.common.connection import Connection
from txrpc.utils import logger


class ConnectionManager:
	''' 连接管理器
	@param _connections: dict {connID:conn Object}管理的所有连接
	'''
	
	def __init__(self):
		'''初始化
		@param _connections: dict {connID:conn Object}
		'''
		self._connections = {}
	
	def getNowConnCnt(self):
		'''获取当前连接数量'''
		return len(self._connections.items())
	
	def addConnection(self, conn, id=None):
		'''加入一条连接
		@param _conn: Conn object
		'''
		_conn = Connection(conn, id)
		if _conn.id in self._connections.keys():
			logger.warning("系统记录冲突...")
			self.dropConnectionByID(id)
			self.loseConnection(id)
		
		self._connections[_conn.id] = _conn
	
	def isInConnections(self, id):
		if id in self._connections.keys():
			return True
		else:
			return False
	
	@property
	def connections(self):
		return self._connections.values()
	
	@property
	def connectionsID(self):
		return self._connections.keys()
	
	def dropConnectionByID(self, connID, conn=None):
		'''更加连接的id删除连接实例
		@param connID: int 连接的id
		'''
		if conn == None:
			try:
				del self._connections[connID]
			except Exception as e:
				logger.msg(str(e))
		else:
			if self.getConnectionByID(connID) == conn:
				try:
					del self._connections[connID]
				except Exception as e:
					logger.msg(str(e))
	
	def getConnectionByID(self, connID):
		"""根据ID获取一条连接
		@param connID: int 连接的id
		"""
		return self._connections.get(connID, None)
	
	def loseConnection(self, connID):
		"""根据连接ID主动端口与客户端的连接
		"""
		conn = self.getConnectionByID(connID)
		if conn:
			try:
				conn.loseConnection()
			except Exception as e:
				logger.err(e)
	
	def pushObject(self, msg, sendList):
		"""
		主动推送消息
		"""
		logger.debug("NET端口 向:{}推送数据:{}".format(sendList, msg))
		if sendList:
			if isinstance(sendList, list):
				for target in sendList:
					try:
						conn = self.getConnectionByID(target)
						logger.debug("获取到端口:{con}".format(con=conn))
						if conn:
							try:
								conn.safeToWriteOriginalData(msg)
							except Exception as e:
								logger.err(e)
						else:
							logger.debug("查无该用户:{}".format(target))
					except Exception as e:
						logger.err(str(e))
				return True
			else:
				try:
					conn = self.getConnectionByID(sendList)
					logger.debug("获取到端口:{con}".format(con=conn))
					if conn:
						try:
							conn.safeToWriteOriginalData(msg)
							return True
						except Exception as e:
							logger.err(e)
					else:
						logger.debug("查无该用户:{}".format(sendList))
				except Exception as e:
					logger.err(str(e))
			
			return False