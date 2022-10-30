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
import binascii

from twisted.internet.protocol import Factory
from loguru import logger

from txfirefly.net.mqtt.core.connmanager import ConnectionManager, ConnIsExistException
from txfirefly.net.mqtt.core.mqtt import MQTT

CONNACK_ACCEPTED = 0x00
CONNACK_REJECT = 0x05

GRANTED_QOS = 1
""" QoS 1 is used in this implementation """

class MQTTProtocol(MQTT):
    """
    MQTT broker connection handler.
    """
    factory: "MQTTFactory"

    def connectReceived(self, clientID, keepalive, willTopic, willMessage,
                        willQoS, willRetain, cleanStart,userName,password):
        '''
            MQTT 连接建立
        :param clientID:
        :param keepalive:
        :param willTopic:
        :param willMessage:
        :param willQoS:
        :param willRetain:
        :param cleanStart:
        :return:
        '''
        self.clientID = clientID
        self.keepalive = keepalive
        self.willTopic = willTopic
        self.willMessage = willMessage
        self.willQoS = willQoS
        self.willRetain = willRetain
        self.cleanStart = cleanStart
        self.userName = userName
        self.password = password
        if self.factory.authorization(self): # 登录校验成功
            if self.factory.connmanager.isInConnections(clientID): # 当前是否在连接池内
                # logger.debug('client which name is: %s is in connmanager' % clientID)
                # self.factory.connmanager.getConnectionByID(clientID).loseConnection()
                # logger.debug('client which name is: %s is broken' % clientID)
                # self.factory.connmanager.dropConnectionByID(clientID)
                # logger.debug('client which name is: %s is removed from connmanager' % clientID)
                raise ConnIsExistException()

            self.connack(CONNACK_ACCEPTED)
            self.factory.onConnect(self)
        else:
            self.connack(CONNACK_REJECT)

    def subscribeReceived(self, topics, messageId):
        '''

        :param topics:
        :param messageId:
        :return:
        '''
        newtopics = [i[0] for i in topics[::2]]
        # topics are like {'topic','QoS'}
        for topic in newtopics:
            if topic in self.topics:
                logger.warning("User %s sent dublicate subscribe on topic %s" % (self.clientID, topic))
            else:
                self.topics.append(topic)
        self.suback(len(topics), messageId)

    def unsubscribeReceived(self, topics, messageId):
        '''

        :param topics:
        :param messageId:
        :return:
        '''
        for removetopic in topics:
            if removetopic not in self.topics:
                logger.warning("User %s unsubscribe topic %s failed" % (self.clientID, removetopic))
            else:
                self.topics.remove(removetopic)
        self.unsuback(messageId)

    def publishReceived(self, topic, message : bytearray, qos=0, dup=False, retain=False, messageId=None):
        '''

        :param topic:
        :param message:
        :param qos:
        :param dup:
        :param retain:
        :param messageId:
        :return:
        '''
        logger.debug('Publish msg<%d> received (%d bytes) from %s on topic %s = %s' % (messageId,len(message),self.clientID, topic,message))
        self.puback(messageId)
        for connection in self.factory.connmanager.connections:
            if topic in connection.instance.topics:
                connection.getInstance().publish(topic, message, qosLevel=qos, retain=retain, dup=dup, messageId=messageId)

    def pingreqReceived(self):
        self.pingresp()

    def disconnectReceived(self):
        self.factory.onDisconnect(self)

class MQTTFactory(Factory):

    protocol = MQTTProtocol

    def __init__(self):
        '''
        初始化
        '''
        self.service = None
        self.connmanager = ConnectionManager()  # 连接管理器

    def authorization(self,conn : MQTTProtocol):
        return True

    def addServiceChannel(self, service):
        '''
        添加服务通道
        '''
        self.service = service

    def onConnect(self, conn):
        ''':param'''
        logger.debug('client %s added into the online_clients' % conn.clientID)
        self.connmanager.addConnection(conn, conn.clientID)

    def onDisconnect(self, conn):
        '''
            连接断开后出发
        :param conn:
        :return:
        '''
        logger.debug('client %s droped from the online_clients' % conn.clientID)
        self.connmanager.dropConnectionByID(conn.clientID)
