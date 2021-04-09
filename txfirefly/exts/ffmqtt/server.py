# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : server.py
# @Time     : 2021-02-20 0:19
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
from twisted.internet.protocol import Factory
from txfirefly.exts.ffmqtt.mqtt import MQTTProtocol
from txfirefly.net.common.manager import ConnectionManager
from loguru import logger

CONNACK_ACCEPTED = 0x00
GRANTED_QOS = 1
""" QoS 1 is used in this implementation """

class MQTTHandler(MQTTProtocol):
	"""MQTT broker connection handler.
	"""
	
	def connectReceived(self, clientID, keepalive, willTopic, willMessage,
	                    willQoS, willRetain, cleanStart):
		
		logger.debug('Connect received, client name is: %s' % clientID)
		
		self.clientID = clientID
		self.keepalive = keepalive
		self.willTopic = willTopic
		self.willMessage = willMessage
		self.willQoS = willQoS
		self.willRetain = willRetain
		self.cleanStart = cleanStart
		
		if self.factory.connmanager.isInConnections(clientID):
			logger.debug('client which name is: %s is in connmanager' % clientID)
			self.factory.onDisconnect(self.factory.connmanager.getConnectionByID(clientID).instance)
		else:
			logger.debug('client which name is: %s is not in connmanager' % clientID)
		
		self.connack(CONNACK_ACCEPTED)
		
		logger.debug('User %s added to online_users' % self.clientID)
		
		self.factory.onConnect(self)
	
	def disconnectReceived(self):
		logger.debug('Disconnect received from %s' % (self.clientID))
		logger.info('Removed %s from online_users' % (self.clientID))
		self.factory.onDisconnect(self)
	
	def connectionLost(self, reason):
		super().connectionLost(reason)
		self.factory.doConnectionLost(self)
		logger.info("Clients residue: {}".format(self.factory.connmanager.getNowConnCnt()))
	
	def subscribeReceived(self, topics, messageId):
		newtopics = [i[0] for i in topics[::2]]
		# topics are like {'topic','QoS'}
		logger.debug('subscribeReceived on topics: %s' % newtopics)
		for topic in newtopics:
			if topic in self.topics:
				logger.warning("User %s sent dublicate subscribe on topic %s" % (self.clientID, topic))
			else:
				self.topics.append(topic)
		self.suback(len(topics), messageId)
		logger.debug('Sent suback for topics: %s' % self.topics)
		logger.debug('Now user %s is subscribed to topics %s' % (self.clientID, self.topics))
	
	def publishReceived(self, topic, message, qos=0, dup=False, retain=False, messageId=None):
		logger.debug('Publish received (%s bytes) from %s on topic %s ' % (len(message),
		                                                                self.clientID, topic))
		self.puback(messageId)
		for user in self.factory.connmanager.connections:
			logger.debug('user %s topics are: %s' % (user.instance.clientID, user.instance.topics))
			if topic in user.instance.topics:
				logger.debug('Found topic %s in %s' % (topic, user.instance.topics))
				logger.debug('Sending publish (%s bytes) to %s' % (len(message), user.instance.clientID))
				user.instance.publish(topic, message, qosLevel=GRANTED_QOS, retain=False, dup=False, messageId=None)
	
	def pingreqReceived(self):
		logger.debug("Pingreq received from %s" % (self.clientID))
		self.pingresp()
		logger.debug("Pingresp send back to %s" % (self.clientID))


class MQTTFactory(Factory):
	
	def __init__(self):
		'''
		初始化
		'''
		self.service = None
		self.connmanager = ConnectionManager()  # 连接管理器
	
	def buildProtocol(self, addr):
		protocol = MQTTHandler()
		protocol.factory = self
		return protocol
	
	def doConnectionMade(self, conn):
		'''当连接建立时的处理'''
		pass
	
	def doConnectionLost(self, conn):
		'''
		连接断开时的处理
		'''
		self.connmanager.dropConnectionByID(conn.clientID)
	
	def addServiceChannel(self, service):
		'''
		添加服务通道
		'''
		self.service = service
	
	def pushObject(self, msg, sendList):
		'''
		服务端向客户端推消息
		@param topicID: int 消息的主题id号
		@param msg: 消息的类容，protobuf 结构类型
		@param sendList: 推向的目标列表(客户端id 列表)
		'''
		logger.debug("需要向：{}发送数据\n发送的数据为:{}".format(sendList, msg))
		self.connmanager.pushObject(msg, sendList)
	
	def onConnect(self, conn):
		''':param'''
		self.connmanager.addConnection(conn, id=conn.clientID)
	
	def onDisconnect(self, conn):
		''':param'''
		try:
			if self.connmanager.isInConnections(conn.clientID):
				self.connmanager.dropConnectionByID(conn.clientID)
				logger.info('Removed %s from online_users' % (conn.clientID))
			conn.loseConnection()
		except Exception as e:
			logger.debug(e)
			logger.debug("the conn %s is already closed" % (conn.clientID))
	
	def publish(self, topic, message, qosLevel=0):
		''':param'''
		for user in self.connmanager.connections:
			logger.debug('publish methodtopics are: %s' % topic.decode())
			logger.debug('user %s topics are: %s' % (user.instance.clientID, user.instance.topics))
			if topic.decode() in user.instance.topics:
				logger.debug('Found topic %s in %s' % (topic.decode(), user.instance.topics))
				logger.debug('Sending publish (%s bytes) to %s' % (len(message), user.instance.clientID))
				user.instance.publish(topic, message, qosLevel=GRANTED_QOS, retain=False, dup=False, messageId=None)
