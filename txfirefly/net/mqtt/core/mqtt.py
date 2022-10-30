# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : mqtt.py
# @Time     : 2021-02-20 0:18
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

from abc import ABCMeta, abstractmethod
import binascii

import six
from twisted.internet.protocol import Protocol

import random
import logging
import base64

from twisted.protocols import policies

from txrpc.globalobject import GlobalObject
from loguru import logger

CONNACK_ACCEPTED = six.int2byte(0x00)
GRANTED_QOS = 1
# CLIENTS SHOULD CONNECT WITH QOS = 1
AES_KEY = str.upper('theverysecretkey')
PROTOCOL_NAME = "04MQTT4"
MQTT_TIME_OUT = 5 * 60

class MQTT(Protocol, policies.TimeoutMixin):
    """
    MQTT protocol library that can be used on either broker or client side.
    Based on code by adamvr (https://github.com/adamvr/MQTT-For-Twisted-Python/blob/master/MQTT.py)
    modified by anridev

    """
    __metaclass__ = ABCMeta

    _packetTypes = {0x00: "null", 0x01: "connect", 0x02: "connack",
                    0x03: "publish", 0x04: "puback", 0x05: "pubrec",
                    0x06: "pubrel", 0x07: "pubcomp", 0x08: "subscribe",
                    0x09: "suback", 0x0A: "unsubscribe", 0x0B: "unsuback",
                    0x0C: "pingreq", 0x0D: "pingresp", 0x0E: "disconnect"}

    def __init__(self):
        self.buffer = bytearray()
        self.clientID = None
        self.topics = []

    ''' def aes_encrypt(self, data):
        IV = Random.new().read(32)
        aes = AES.new(AES_KEY, AES.MODE_CFB, IV)
        return aes.encrypt(data)

    def aes_decrypt(self, data):
        IV = Random.new().read(32)
        aes = AES.new(AES_KEY, AES.MODE_CFB, IV)
        return aes.decrypt(base64.b64decode(data))
    '''

    @abstractmethod
    def connectReceived(self, clientID, keepalive, willTopic, willMessage, willQoS, willRetain, cleanStart,userName,password):
        pass

    @abstractmethod
    def connackReceived(self, status):
        pass

    @abstractmethod
    def publishReceived(self, topic, message : bytearray, qos=0, dup=False, retain=False, messageId=None):
        pass

    @abstractmethod
    def pubackReceived(self, messageId):
        pass

    @abstractmethod
    def pubrecReceived(self, messageId):
        pass

    @abstractmethod
    def pubrelReceived(self, messageId):
        pass

    @abstractmethod
    def pubcompReceived(self, messageId):
        pass

    @abstractmethod
    def subscribeReceived(self, topics, messageId):
        '''

        :param topics:
        :param messageId:
        :return:
        '''
        pass

    @abstractmethod
    def subackReceived(self, grantedQos, messageId):
        pass

    @abstractmethod
    def unsubscribeReceived(self, topics, messageId):
        pass

    @abstractmethod
    def unsubackReceived(self, messageId):
        pass

    @abstractmethod
    def pingreqReceived(self):
        pass

    @abstractmethod
    def pingrespReceived(self):
        pass

    @abstractmethod
    def disconnectReceived(self):
        pass

    def dataReceived(self, data):
        self.setTimeout(MQTT_TIME_OUT)
        self._accumulatePacket(data)

    def _accumulatePacket(self, data):
        '''
            用于TCP数据接收以及预判断
                - 送入缓存区
                - 解码
        :param data:
        :return:
        '''
        self.buffer.extend(data)
        length = None
        while len(self.buffer):
            if length is None:
                # Start on a new packet
                # Haven't got enough data to start a new packet,
                # wait for some more
                if len(self.buffer) < 2:
                    break
                lenLen = 1
                # Calculate the length of the length field
                while lenLen < len(self.buffer):
                    if not self.buffer[lenLen] & 0x80:
                        break
                    lenLen += 1
                # We still haven't got all of the remaining length field
                if lenLen < len(self.buffer) and self.buffer[lenLen] & 0x80:
                    return
                length = self._decodeLength(self.buffer[1:]) # 获取到数据长度
            if len(self.buffer) >= length + lenLen + 1: # 成功接收完一帧长度( +1 是因为长度自身一个字节)
                chunk = self.buffer[:length + lenLen + 1] # 将数据移入缓存区
                self._processPacket(chunk) # 处理数据
                self.buffer = self.buffer[length + lenLen + 1:] # 指针后移
                length = None
            else:
                break

    def _processPacket(self, packet):
        '''
            用于指令解包
                并调用指定解包Handler
        :param packet:
        :return:
        '''
        try:
            packet_type = (packet[0] & 0xF0) >> 4
            packet_type_name = self._packetTypes[packet_type]
            dup = (packet[0] & 0x08) == 0x08
            qos = (packet[0] & 0x06) >> 1
            retain = (packet[0] & 0x01) == 0x01
        except:
            # Invalid packet type, throw away this packet
            logging.error("Invalid packet type %x" % packet_type)
            return

        # Strip the fixed header
        lenLen = 1
        while packet[lenLen] & 0x80:
            lenLen += 1
        packet = packet[lenLen + 1:]
        # Get the appropriate handler function
        packetHandler = getattr(self, "_event_%s" % packet_type_name, None)
        if packetHandler:
            packetHandler(packet, qos, dup, retain)
        else:
            # Rocks fall, everyone dies
            logging.error("Invalid packet handler for %s" % packet_type_name)
            return

    def _event_connect(self, packet, qos, dup, retain):
        '''
            连接触发 回调事件
            CONNECT 协议是客户端建立连接的第一个报文，通常都要带有鉴权的字段，
            一个CONNECT报文都会对应一个服务端的CONNACK报文
            用户需要在服务器上自行实现 connectReceived 函数 且进行 connack 回复

            1.固定头
                类型 1
            2.可变头
                     ---------------------------------------------------------------------------------------------
                    |             |          描述         |  7  |  6  |  5  |  4  |  3  |   2   |   1   |   0    |
                    ----------------------------------------------------------------------------------------------
                    |  协议名称   |                                                                              |
                    ----------------------------------------------------------------------------------------------
                    |  byte1      |  Length     MSB(0)    |  0  |  0  |  0  |  0  |  0  |   0   |   0   |   0    |
                    ----------------------------------------------------------------------------------------------
                    |  byte2      |  Length     LSB(4)    |  0  |  0  |  0  |  0  |  1  |   0   |   1   |   0    |
                    ----------------------------------------------------------------------------------------------
                    |  byte3      |          'M'          |  0  |  1  |  0  |  0  |  1  |   1   |   0   |   1    |
                    ----------------------------------------------------------------------------------------------
                    |  byte4      |          'Q'          |  0  |  1  |  0  |  1  |  0  |   0   |   0   |   1    |
                    ----------------------------------------------------------------------------------------------
                    |  byte5      |          'T'          |  0  |  1  |  0  |  1  |  0  |   1   |   0   |   0    |
                    ----------------------------------------------------------------------------------------------
                    |  byte6      |          'T'          |  0  |  1  |  0  |  1  |  0  |   0   |   0   |   1    |
                    ----------------------------------------------------------------------------------------------
                    |  协议等级   |                                                                              |
                    ----------------------------------------------------------------------------------------------
                    |  byte7      |        level(4)       |  0  |  0  |  0  |  0  |  0  |   1   |   0   |   0    |
                    ----------------------------------------------------------------------------------------------
                    | Connect Flags                                                                              |
                    ----------------------------------------------------------------------------------------------
                    |  byte8      |                       |  1  |  1  |  0  |  0  |  1  |   1   |   1   |   0    |
                    |             |   User Name Flag(1)   |  1  |     |     |     |     |       |       |        |
                    |             |   Password Flag(1)    |     |  1  |     |     |     |       |       |        |
                    |             |   Will Retain(0)      |     |     |  0  |     |     |       |       |        |
                    |             |   Will QoS(01)        |     |     |     |  0  |  1  |       |       |        |
                    |             |   Will Flag(1)        |     |     |     |     |     |   1   |       |        |
                    |             |   Clean Session(1)    |     |     |     |     |     |       |   1   |        |
                    |             |   Reserved(0)         |     |     |     |     |     |       |       |   0    |
                    ----------------------------------------------------------------------------------------------
                    | Keep Alive                                                                                 |
                    ----------------------------------------------------------------------------------------------
                    |  byte9      | Keep Alive   MSB(0)   |  0  |  0  |  0  |  0  |  0  |   0   |   0   |   0    |
                    ----------------------------------------------------------------------------------------------
                    |  byte10     | Keep Alive   MSB(10)  |  0  |  0  |  0  |  0  |  1  |   0   |   1   |   0    |
                    ----------------------------------------------------------------------------------------------

                    -- 1~6个字节为协议名
                        MQTT协议名是预先规定好的，这个后续不会变。
                    -- 第7个字节为协议级别
                        其实就是mqtt协议的修订版本。对于3.1.1版协议，协议级别字段的值是4(0x04)。
                        如果发现不支持的协议级别，服务端必须给发送一个返回码为0x01（不支持的协议级别）的CONNACK报文响应CONNECT报文，然后断开客户端的连接。
                    -- 第8个字节为连接标志
                        连接标志字节包含一些用于指定MQTT连接行为的参数。它还指出有效载荷中的字段是否存在。有效荷载里有啥全看这个字节的8位字符是0还是1了。
                        |--第0位：服务端必须验证CONNECT控制报文的保留标志位（第0位）是否为0，如果不为0必须断开客户端连接。
                        |--第1位：清理会话 Clean Session
                            这个二进制位指定了会话状态的处理方式。客户端和服务端可以保存会话状态，以支持跨网络连接的可靠消息传输。这个标志位用于控制会话状态的生存时间。
                            这个值是0：服务端可以根据报文里的客户端标识符，来找之前这个客户端有没有连过，连过的话就恢复之前的会话状态，没有的话就新建一个会话。
                                就算是这个连接断开了，会话也要保存在服务端，针对这个客户端订阅的消息，会保存为会话的一部分，在这个客户端重新连接后，把这些消息再推送给这个客户端。
                            这个值是1：服务端丢弃之前所有的和这个客户端建立的会话，并开始一个新的会话，新的会话仅持续和网络连接同样长的时间。
                                与这个会话关联的状态数据不能被任何之后的会话重用。为了确保在发生故障时状态的一致性，客户端应该使用会话状态标志1重复请求连接，直到连接成功。
                                一般来说，客户端连接时总是将清理会话标志设置为0或1，并且不交替使用两种值。
                                这个选择取决于具体的应用。清理会话标志设置为1的客户端不会收到旧的应用消息，而且在每次连接成功后都需要重新订阅任何相关的主题。
                                清理会话标志设置为0的客户端会收到所有在它连接断开期间发布的QoS 1和QoS 2级别的消息。
                                因此，要确保不丢失连接断开期间的消息，需要使用QoS 1或 QoS 2级别，同时将清理会话标志设置为0。
                                清理会话标志0的客户端连接时，它请求服务端在连接断开后保留它的MQTT会话状态。
                                如果打算在之后的某个时间点重连到这个服务端，客户端连接应该只使用清理会话标志0。
                                当客户端决定之后不再使用这个会话时，应该将清理会话标志设置为1最后再连接一次，然后断开连接。
                        |--第2位：遗嘱标志 Will Flag
                            遗嘱比较有用，比如说你手机app订阅了你家扫地机器人的在线状态topic，这个在线状态扫地机器人可以通过遗嘱来实现，一旦它断开了与mqttbroker连接，mqttboker就可以发送机器人在连接时就设置好的遗嘱，通知手机机器人掉线了。
                            遗嘱标志（Will Flag）被设置为1，表示如果连接请求被接受了，遗嘱（Will Message）消息必须被存储在服务端并且与这个网络连接关联。也就是确认使用遗嘱。之后网络连接关闭时，服务端必须发布这个遗嘱消息，除非服务端收到DISCONNECT报文时删除了这个遗嘱消息。
                            如果决定启用遗嘱，那么连接标志中的Will QoS和Will Retain字段会被服务端用到，同时有效载荷中必须包含Will Topic和Will Message字段。因为你得组织服务端遗嘱的publish的报文。
                            如果被设置成了0，连接标志中的Will QoS和Will Retain字段必须设置为0，并且有效载荷中不能包含Will Topic和Will Message字段。
                        |--第3位、第4位：遗嘱QoS Will QoS
                            没啥说的，遗嘱也是一个publish的消息，需要确定的消息等级。
                        |--第5位：遗嘱保留 Will Retain
                            如果遗嘱消息被发布时需要保留，需要指定这一位的值。
                            tips：
                                保留消息是mqtt中比较重要的概念，它是统治服务器是否保留本条报文，以推送给后来订阅者的。比如描述设备状态的报文，这个就留在服务端就行，只要设备状态不改变，就没有必要修改这个报文，后续订阅设备状态的也能什么时候订阅什么时候收到，非常方便。
                        |--第6位：用户名标志 User Name Flag
                            这设置0，有效载荷就不能有了，设置1就必须有这个字段。
                        |--第7位：密码标志 Password Flag
                            同上
                    -- 第9第10个字节：保持连接 Keep Alive
                        保持连接（Keep Alive）是一个以秒为单位的时间间隔，表示为一个16位的字，它是指在客户端传输完成一个控制报文的时刻到发送下一个报文的时刻，两者之间允许空闲的最大时间间隔。客户端负责保证控制报文发送的时间间隔不超过保持连接的值。
                        如果没有任何其它的控制报文可以发送，客户端必须发送一个。保持连接的实际值是由应用指定的，一般是几分钟。允许的最大值是18小时12分15秒。
            3.有效负载
                CONNECT报文的有效载荷（payload）包含一个或多个以长度为前缀的字段，可变报头中的标志决定是否包含这些字段。
                如果包含的话，必须按这个顺序出现：客户端标识符，遗嘱主题，遗嘱消息，用户名，密码。
                有个概念必须要了解--客户端标识符 Client Identifier，也就是客户端的唯一标识。
                服务端使用客户端标识符 (ClientId) 识别客户端。
                连接服务端的每个客户端都有唯一的客户端标识符（ClientId）。
                客户端和服务端都必须使用ClientId识别两者之间的MQTT会话相关的状态。
                客户端标识符 (ClientId) 必须存在而且必须是CONNECT报文有效载荷的第一个字段 ，客户端标识符必须是1.5.3节定义的UTF-8编码字符串。

        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        # Strip the protocol name and version number
        packet = packet[len(PROTOCOL_NAME):]

        # Extract the connect flags
        willRetain = packet[0] & 0x20 == 0x20
        userNameFlag = packet[0] & 0x80 == 0x80
        passwordFlag = packet[0] & 0x40 == 0x40
        willQos = packet[0] & 0x18 >> 3
        willFlag = packet[0] & 0x04 == 0x04
        cleanStart = packet[0] & 0x02 == 0x02

        packet = packet[1:]

        # Extract the keepalive period
        keepalive = self._decodeValue(packet[:2])
        packet = packet[2:]

        # Extract the client id
        clientID = self._decodeString(packet)
        packet = packet[len(clientID) + 2:]

        # Extract the will topic and message, if applicable
        willTopic = None
        willMessage = None
        userName = None
        password = None

        if willFlag:
            # Extract the will topic
            willTopic = self._decodeString(packet)
            packet = packet[len(willTopic) + 2:]

            # Extract the will message
            # Whatever remains is the will message
            willMessage = self._decodeString(packet)
            packet = packet[len(willMessage) + 2:]

        # Extract the userName message
        if userNameFlag:
            userName = self._decodeString(packet)
            packet = packet[len(userName) + 2:]

        # Extract the password message
        if passwordFlag:
            password = self._decodeString(packet)

        logger.debug(f"unpack the connect packet:\n"
                     f"     clientID : {clientID}\n"
                     f"     keepalive : {keepalive}\n"
                     f"     willTopic : {willTopic}\n"
                     f"     willMessage : {willMessage}\n"
                     f"     willQos : {willQos}\n"
                     f"     willRetain : {willRetain}\n"
                     f"     cleanStart : {cleanStart}\n"
                     f"     userName : {userName}\n"
                     f"     password : {password}")

        self.connectReceived(clientID, keepalive, willTopic,
                             willMessage, willQos, willRetain,
                             cleanStart,userName,password)

    def connect(self, clientID, keepalive=3000, willTopic=None,
        willMessage=None, willQoS=0, willRetain=False,
        cleanStart=True):
        '''
            发起连接
        :param clientID:
        :param keepalive:
        :param willTopic:
        :param willMessage:
        :param willQoS:
        :param willRetain:
        :param cleanStart:
        :return:
        '''
        header = bytearray()
        varHeader = bytearray()
        payload = bytearray()

        varHeader.extend(self._encodeString("MQIsdp"))
        varHeader.append(3)

        if willMessage is None or willTopic is None:
            # Clean start, no will message
            varHeader.append(0 << 2 | cleanStart << 1)
        else:
            varHeader.append(willRetain << 5 | willQoS << 3
                             | 1 << 2 | cleanStart << 1)

        varHeader.extend(self._encodeValue(int(keepalive / 1000)))

        payload.extend(self._encodeString(clientID))
        if willMessage is not None and willTopic is not None:
            payload.extend(self._encodeString(willTopic))
            payload.extend(self._encodeString(willMessage))

        header.append(0x01 << 4)
        header.extend(self._encodeLength(len(varHeader) + len(payload)))

        self.writeByteArray(header)
        self.writeByteArray(varHeader)
        self.writeByteArray(payload)

    def _event_connack(self, packet, qos, dup, retain):
        '''
            连接确定 回调事件
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        self.connackReceived(packet[0])

    def connack(self, status):
        '''
            1.固定头
                报文类型 2
            2.可变头
                ------------------------------------------------------------------------------------------
                | bit                |      描述         |  7  |  6  |  5  |  4  |  3  |  2  |  1  |  0  |
                ------------------------------------------------------------------------------------------
                | 连接确认标志       |                   |             reserved保留位              | SP1 |
                ------------------------------------------------------------------------------------------
                | byte 1             |                   |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  X  |
                -----------------------------------------------------------------------------------------
                |                    连接返回码                                                          |
                -----------------------------------------------------------------------------------------
                | byte 2             |                   |  X  |  X  |  X  |  X  |  X  |  X  |  X  |  X  |
                -----------------------------------------------------------------------------------------
                主要有两个字节：
                --第一个字节是连接确认标志，8位里面就第0位有用，其他都是0不用管。
                第0位标识的是当前会话，也就是服务端告诉客户端你在我这的session是我新启动的（值是0），还是原来就有的，我只是重用（值是1）
                如果之前客户端发的连接报文，让服务端清理clientsession，那服务端的session肯定是新建的，那这个标志就是0，或者是之前客户端就没连过，那这个值也是0 。
                如果连接报文没有让服务端清理clientsession，并且之前客户端连接过，服务器用的是原来的会话，那这个值就是1 。
                --第二个字节是连接返回码
                连接返回码字段使用一个字节的无符号值【见下表】。如果服务端收到一个合法的CONNECT报文，但出于某些原因无法处理它，服务端应该尝试发送一个包含非零返回码（表格中的某一个）的CONNACK报文。
                如果服务端发送了一个包含非零返回码的CONNACK报文，那么它必须关闭网络连接 。
                -----------------------------------------------------------------------------------------------
                |  值  |      描述                           |  描述                                          |
                -----------------------------------------------------------------------------------------------
                |  0  |  连接已接受                         |             连接已接受                          |
                -----------------------------------------------------------------------------------------------
                |  1  |  连接已拒绝,不支持的协议版本        |             连接已拒绝,不支持的协议版本         |
                -----------------------------------------------------------------------------------------------
                |  2  |  连接已拒绝,不支持的客户端标识符    |             连接已拒绝,不支持的协议版本         |
                -----------------------------------------------------------------------------------------------
                |  3  |  连接已拒绝,服务端不可用            |             网络连接已建立,但MQTT服务不可用     |
                -----------------------------------------------------------------------------------------------
                |  4  |  连接已拒绝,无效用户名,密码         |              连接已拒绝,无效用户名,密码         |
                -----------------------------------------------------------------------------------------------
                |  5  |  连接已拒绝,未授权                  |              连接已拒绝,客户端未被授权          |
                -----------------------------------------------------------------------------------------------
                |  6~ |                                     |              预留                               |
                -----------------------------------------------------------------------------------------------
                如果认为上表中的所有连接返回码都不太合适，那么服务端必须关闭网络连接，不需要发送CONNACK报文。
            3.有效负载
                无
        :param status:
        :return:
        '''
        header = bytearray()
        payload = bytearray()

        header.append(0x02 << 4)
        payload.append(0x00)
        payload.append(status)

        header.extend(self._encodeLength(len(payload)))
        # logger.debug("the header is {header}".format(header=header))
        # logger.debug("the payload is {payload}".format(payload=payload))

        self.writeByteArray(header)
        self.writeByteArray(payload)

    def _event_publish(self, packet, qos, dup, retain):
        '''
            收到 发布事件 后调用的事件
            用户需要在服务器上自行实现 publishReceived 函数 且进行 puback 回复
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        topic = self._decodeString(packet)
        packet = packet[len(topic) + 2:]

        # Extract the message ID if appropriate
        messageId = None

        if qos > 0:
            messageId = self._decodeValue(packet[:2])
            packet = packet[2:]

        # Extract the message
        # Whatever remains is the message
        message = packet

        self.publishReceived(topic, message, qos, dup, retain, messageId)

    def publish(self, topic : str, message : bytearray, qosLevel : int = 0, retain : bool = False, dup : bool = False,
        messageId  : bool = None):
        '''
            1.固定头
                ----------------------------------------------------------------
                | bit   |  7  |  6  |  5  |  4  |  3  |   2   |   1   |   0    |
                ----------------------------------------------------------------
                | byte1 |    MQTT控制报文类型   | DUP | QoS-H | QoS-L | RETAIN |
                |       |  0  |  0  |  1  |  1  |  X  |   X   |   X   |   X    |
                ---------------------------------------------------------------
                | byte2 | 剩余长度                                             |
                ---------------------------------------------------------------
                推送的固定头报文类型是3。
                DUP是重发标志，如果DUP标志被设置为0，表示这是客户端或服务端第一次请求发送这个PUBLISH报文。如果DUP标志被设置为1，表示这可能是一个早前报文请求的重发。
                Qos是服务质量等级，有三种状态。
                    ----------------------------------------------------------------
                    |    QOS值    |     bit2     |     bit1     |       描述       |
                    ----------------------------------------------------------------
                    |  0          |  0           |  0           | 最多分发一次     |
                    ----------------------------------------------------------------
                    |  1          |  0           |  1           | 至少分发一次     |
                    ----------------------------------------------------------------
                    |  2          |  1           |  0           | 只分发一次       |
                    ----------------------------------------------------------------
                    |  -          |  1           |  1           | 保留位           |
                    ----------------------------------------------------------------
                RETAIN是保留位，保留位的意义上一篇已经阐述。
                值得注意的是如果想清除一个在服务端有保留有效荷载的topic，只要发送一个保留位为1切有效荷载为零字节的publish报文就行，
                服务端会把这个空报文转发给订阅者，并清除这个topic的保留信息，后续再关注这个topic的客户端不会再收到消息了。
            2.可变头
                可变报头按顺序包含主题名和报文标识符。
                主题名就是平时说的topic，推送订阅都是依靠这个标识，可以理解为其他mq的topic。
                报文标识符就是报文的id，服务端用来唯一标识报文的属性，只有当QoS等级是1或2时，报文标识符（Packet Identifier）字段才能出现在PUBLISH报文中，因为这俩需要服务端答复
                客户端，如果没有这个标识，服务端不知道要针对哪条报文进行答复。
                可变头示例：
                    ------------------------------------------------------------------------------------------
                    | bit                |      描述         |  7  |  6  |  5  |  4  |  3  |  2  |  1  |  0  |
                    ------------------------------------------------------------------------------------------
                    | Topic Name 主题名  |                                                                   |
                    ------------------------------------------------------------------------------------------
                    | byte 1             |  length MSB(0)    |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |
                    -----------------------------------------------------------------------------------------
                    | byte 2             |  length LSB(3)    |  0  |  0  |  0  |  0  |  0  |  0  |  1  |  1  |
                    -----------------------------------------------------------------------------------------
                    | byte 3             |    'a'(0x61)      |  0  |  1  |  1  |  0  |  0  |  0  |  0  |  1  |
                    -----------------------------------------------------------------------------------------
                    | byte 4             |    '/'(0x2F)      |  0  |  0  |  1  |  0  |  1  |  1  |  1  |  1  |
                    -----------------------------------------------------------------------------------------
                    | byte 5             |    'b'(0x62)      |  0  |  1  |  1  |  0  |  0  |  0  |  1  |  0  |
                    -----------------------------------------------------------------------------------------
                    | 报文标识符         |                                                                   |
                    -----------------------------------------------------------------------------------------
                    | byte 6             | 报文标识符 MSB(0) |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |
                    -----------------------------------------------------------------------------------------
                    | byte 7             | 报文标识符 LSB(10)|  0  |  0  |  0  |  0  |  1  |  0  |  1  |  0  |
                    -----------------------------------------------------------------------------------------
                 示例中的主题名为 “a/b”，长度等于3，报文标识符为 “10”
            3.有效负载
                有效载荷包含将被发布的应用消息。
                数据的内容和格式是应用特定的。
                有效载荷的长度这样计算：用固定报头中的剩余长度字段的值减去可变报头的长度。
                包含零长度有效载荷的PUBLISH报文是合法的。
                注意：根据固定头中的qos等级，接收到publish报文端需要给予响应。
                    ----------------------------------------------------------------
                    |   服务质量等级             |     预期响应                    |
                    ----------------------------------------------------------------
                    |  QoS 0                     |  无响应                         |
                    ----------------------------------------------------------------
                    |  QoS 1                     |  PUBACK报文                     |
                    ----------------------------------------------------------------
                    |  QoS 2                     |  PUBREC报文                     |
                    ----------------------------------------------------------------
                这里补充一下qos：
                qos0：最多就发送一次，你别告诉我你收没收到，你找到订阅这个主题的你就推就行。
                qos1：至少发送一次，发送完你告诉我你收没收到（PUBACK），如果你不告诉我，我就一直发。
                qos2：确保一次送达，我给你发（PUBLISH），你给我回一个你收到了（PUBREC），
                    我再给你发一个你确定你收到了吗（PUBREL），你再给我回一个收到了别发了求你了（PUBCOMP）
        :param topic:
        :param message:
        :param qosLevel:
        :param retain:
        :param dup:
        :param messageId:
        :return:
        '''
        # logger.debug(f"publish : topic : {topic} message : {message} qos : {qosLevel} retain : {retain} dup : {dup} messageId : {messageId}")

        header = bytearray()
        varHeader = bytearray()
        payload = bytearray()
        header.append(0x03 << 4 | dup << 3 | qosLevel << 1 | retain)

        varHeader.extend(self._encodeString(topic))

        if qosLevel > 0:
            if messageId is not None:
                varHeader.extend(self._encodeValue(messageId))
            else:
                varHeader.extend(self._encodeValue(random.randint(1, 0xFFFF)))

        payload.extend(message)
        header.extend(self._encodeLength(len(varHeader) + len(payload)))
        self.writeByteArray(header)
        self.writeByteArray(varHeader)
        self.writeByteArray(payload)

    def _event_puback(self, packet, qos, dup, retain):
        '''
            收到 PUBACK报文 所响应的事件
            PUBACK报文
                对QoS 1等级的PUBLISH报文的响应
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        messageId = self._decodeValue(packet[:2])
        self.pubackReceived(messageId)

    def puback(self, messageId):
        '''
            1.固定头
                类型4.
            2.可变头
                报文标识符 messageId
                -------------------------------------------------
                | bit   |  7  |  6  |  5  |  4  |  3  |  2  |  1  |
                -------------------------------------------------
                | byte1 | 报文标识符MSB                           |
                -------------------------------------------------
                | byte2 | 报文标识符LSB                           |
                -------------------------------------------------
            3.有效负载
                无
        :param messageId:
        :return:
        '''
        if not messageId:
            messageId = 1

        header = bytearray()
        varHeader = bytearray()

        header.append(0x04 << 4)
        varHeader.extend(self._encodeValue(messageId))

        header.extend(self._encodeLength(len(varHeader)))

        self.writeByteArray(header)
        self.writeByteArray(varHeader)

    def _event_pubrec(self, packet, qos, dup, retain):
        '''
            收到 PUBACK报文 所响应的事件
            报文是对QoS等级2的PUBLISH报文的响应。它是QoS 2等级协议交换的第二个报文。
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        messageId = self._decodeValue(packet[:2])
        self.pubrecReceived(messageId)

    def pubrec(self, messageId):
        '''
            1.固定头
                类型 5
            2.可变头
                报文标识符 messageId
                -------------------------------------------------
                | bit   |  7  |  6  |  5  |  4  |  3  |  2  |  1  |
                -------------------------------------------------
                | byte1 | 报文标识符MSB                           |
                -------------------------------------------------
                | byte2 | 报文标识符LSB                           |
                -------------------------------------------------
            3.有效负载
                无
        :param messageId:
        :return:
        '''
        header = bytearray()
        varHeader = bytearray()

        header.append(0x05 << 4)
        varHeader.extend(self._encodeValue(messageId))

        header.extend(self._encodeLength(len(varHeader)))

        self.writeByteArray(header)
        self.writeByteArray(varHeader)

    def _event_pubrel(self, packet, qos, dup, retain):
        '''
            收到 PUBREL报文 所响应的事件
            是对PUBREC报文的响应。它是QoS 2等级协议交换的第三个报文。
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        messageId = self._decodeValue(packet[:2])
        self.pubrelReceived(messageId)

    def pubrel(self, messageId):
        '''
            1.固定头
                类型 6
            2.可变头
                报文标识符 messageId
                -------------------------------------------------
                | bit   |  7  |  6  |  5  |  4  |  3  |  2  |  1  |
                -------------------------------------------------
                | byte1 | 报文标识符MSB                           |
                -------------------------------------------------
                | byte2 | 报文标识符LSB                           |
                -------------------------------------------------
            3.有效负载
                无
        :param messageId:
        :return:
        '''
        header = bytearray()
        varHeader = bytearray()

        header.append(0x06 << 4)
        varHeader.extend(self._encodeValue(messageId))

        header.extend(self._encodeLength(len(varHeader)))

        self.writeByteArray(header)
        self.writeByteArray(varHeader)

    def _event_pubcomp(self, packet, qos, dup, retain):
        '''
            收到 PUBCOMP报文 所响应的事件
            是对PUBREL报文的响应。它是QoS 2等级协议交换的第四个也是最后一个报文。
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        messageId = self._decodeValue(packet[:2])
        self.pubcompReceived(messageId)

    def pubcomp(self, messageId):
        '''
            1.固定头
                类型 7
            2.可变头
                报文标识符 messageId
                -------------------------------------------------
                | bit   |  7  |  6  |  5  |  4  |  3  |  2  |  1  |
                -------------------------------------------------
                | byte1 | 报文标识符MSB                           |
                -------------------------------------------------
                | byte2 | 报文标识符LSB                           |
                -------------------------------------------------
            3.有效负载
                无
        :param messageId:
        :return:
        '''
        header = bytearray()
        varHeader = bytearray()

        header.append(0x07 << 4)
        varHeader.extend(self._encodeValue(messageId))

        header.extend(self._encodeLength(len(varHeader)))

        self.writeByteArray(header)
        self.writeByteArray(varHeader)

    def _event_subscribe(self, packet, qos, dup, retain):
        '''
            订阅主题 回调事件
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        messageId = self._decodeValue(packet[:2])
        packet = packet[2:]
        # Extract the requested topics and their QoS levels
        topics = []
        while len(packet):
            # Get the topic name
            topic = self._decodeString(packet)
            qos = packet[len(topic) + 2]
            # Log.debug("the qos :{qos}".format(qos=qos))
            packet = packet[len(topic) + 3:]
            # Add them to the list of (topic, qos)s
            topics.append((topic, qos))
            logger.debug(f"subscribe topic : {topic}")

        self.subscribeReceived(topics, messageId)

    def subscribe(self, topic, requestedQoS, messageId):
        '''
            1.固定头
                ----------------------------------------------------------------
                | bit   |  7  |  6  |  5  |  4  |  3  |   2   |   1   |   0    |
                ----------------------------------------------------------------
                | byte1 | MQTT控制报文类型      | 保留位                       |
                |       |  1  |  0  |  0  |  0  |  0  |   0   |   0   |   0    |
                ---------------------------------------------------------------
                | byte2 | 剩余长度                                             |
                ---------------------------------------------------------------
                报文类型是8，其他啥也没有。
            2.可变头
                里面有一个报文标识符，前文讲过，只要需要服务端答复的，都必须有这个标识符，不然服务端不知道针对哪个报文进行答复。
                示例：假设报文标识符是10
                     ---------------------------------------------------------------------------------------------
                    |             |          描述         |  7  |  6  |  5  |  4  |  3  |   2   |   1   |   0    |
                    ----------------------------------------------------------------------------------------------
                    |  报文标识符 |                                                                              |
                    ----------------------------------------------------------------------------------------------
                    |  byte1      |  报文标识符 MSB(0)    |  0  |  0  |  0  |  0  |  0  |   0   |   0   |   0    |
                    ----------------------------------------------------------------------------------------------
                    |  byte2      |  报文标识符 LSB(10)   |  0  |  0  |  0  |  0  |  1  |   0   |   1   |   0    |
                    ----------------------------------------------------------------------------------------------
            3.有效负载
                主要包含两个东西，一个是你需要订阅的topic，这里面只是通配符标识。
                另一个是qos，这个主要是为了让服务端给你发publish报文的时候用的，publish上文说过必须要有这个东西。
                     ---------------------------------------------------------------------------------------------
                    |             |          描述         |  7  |  6  |  5  |  4  |  3  |   2   |   1   |   0    |
                    ----------------------------------------------------------------------------------------------
                    |  主题过滤器 |                                                                              |
                    ----------------------------------------------------------------------------------------------
                    |  byte1      |  Length MSB(0)        |  0  |  0  |  0  |  0  |  0  |   0   |   0   |   0    |
                    ----------------------------------------------------------------------------------------------
                    |  byte2      |  Length LSB(3)        |  0  |  0  |  0  |  0  |  0  |   0   |   1   |   1    |
                    ----------------------------------------------------------------------------------------------
                    |  byte3      |  'a'(0x61)            |  0  |  1  |  1  |  0  |  0  |   0   |   0   |   1    |
                    ----------------------------------------------------------------------------------------------
                    |  byte4      |  '/'(0x2F)            |  0  |  0  |  1  |  0  |  1  |   1   |   1   |   1    |
                    ----------------------------------------------------------------------------------------------
                    |  byte5      |  'b'(0x62)            |  0  |  1  |  1  |  0  |  0  |   0   |   1   |   0    |
                    ----------------------------------------------------------------------------------------------
                    |  服务质量要求(QOS)                                                                         |
                    ----------------------------------------------------------------------------------------------
                    |  byte6      | QoS(1)                |  0  |  0  |  0  |  0  |  0  |   0   |   0   |   1    |
                    ----------------------------------------------------------------------------------------------
                    |  主题过滤器 |                                                                              |
                    ----------------------------------------------------------------------------------------------
                    |  byte7      | Length MSB(0)         |  0  |  0  |  0  |  0  |  0  |   0   |   0   |   0    |
                    ----------------------------------------------------------------------------------------------
                    |  byte8      | Length LSB(3)         |  0  |  0  |  0  |  0  |  0  |   0   |   1   |   1    |
                    ----------------------------------------------------------------------------------------------
                    |  byte9      | 'c'(0x63)             |  0  |  1  |  1  |  0  |  0  |   0   |   1   |   1    |
                    ----------------------------------------------------------------------------------------------
                    |  byte10     | '/'(0x2F)             |  0  |  0  |  1  |  0  |  1  |   1   |   1   |   1    |
                    ----------------------------------------------------------------------------------------------
                    |  byte11     | 'd'(0x64)             |  0  |  1  |  1  |  0  |  0  |   1   |   0   |   0    |
                    ----------------------------------------------------------------------------------------------
                    |  服务质量要求(QOS)                                                                         |
                    ----------------------------------------------------------------------------------------------
                    |  byte6      | QoS                   |  0  |  0  |  0  |  0  |  0  |   0   |   1   |   0    |
                    ----------------------------------------------------------------------------------------------
        :param topic:
        :param requestedQoS:
        :param messageId:
        :return:
        '''
        header = bytearray()
        varHeader = bytearray()
        payload = bytearray()

        # Type = subscribe, QoS = 1
        header.append(0x08 << 4 | requestedQoS << 1)

        if messageId is None:
            varHeader.extend(self._encodeValue(random.randint(1, 0xFFFF)))
        else:
            varHeader.extend(self._encodeValue(messageId))

        payload.extend(self._encodeString(topic))
        payload.append(requestedQoS)

        header.extend(self._encodeLength(len(varHeader) + len(payload)))

        self.writeByteArray(header)
        self.writeByteArray(varHeader)
        self.writeByteArray(payload)

    def _event_suback(self, packet, qos, dup, retain):
        '''
            订阅确认 回调事件
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        messageId = self._decodeValue(packet[:2])
        packet = packet[2:]

        # Extract the granted QoS levels
        grantedQos = []

        while len(packet):
            grantedQos.append(packet[0])
            packet = packet[1:]

        self.subackReceived(grantedQos, messageId)

    def suback(self, len_topics, messageId):
        '''
            服务端在收到客户端的订阅报文后，会根据报文变头里带着的报文标识符，返回一个确认报文以告诉客户端是否订阅成功。
            服务端发送SUBACK报文给客户端，用于确认它已收到并且正在处理SUBSCRIBE报文。
            SUBACK报文包含一个返回码清单，它们指定了SUBSCRIBE请求的每个订阅被授予的最大QoS等级。
            1.固定头
                报文类型 9
            2.可变头
                无
            3.有效负载
                ------------------------------------------------------------------------------------------
                |          |      描述                   |  7  |  6  |  5  |  4  |  3  |  2  |  1  |  0  |
                ------------------------------------------------------------------------------------------
                | byte 1   |  Success - Maximum QoS 0    |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |
                ------------------------------------------------------------------------------------------
                | byte 2   |  Success - Maximum QoS 2    |  0  |  0  |  0  |  0  |  0  |  0  |  1  |  0  |
                -----------------------------------------------------------------------------------------
                | byte 3   |  Failure                    |  1  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |
                -----------------------------------------------------------------------------------------
                每个字节代表订阅报文中一个topic被允许的最大qos值。也就是说服务端会告诉你，你这个订阅的主题，最多能给你的服务质量等级是多少。
        :param len_topics:
        :param messageId:
        :return:
        '''
        header = bytearray()
        varHeader = bytearray()
        payload = bytearray()

        header.append(0x09 << 4)
        varHeader.extend(self._encodeValue(messageId))

        for i in range(len_topics):
            payload.append(GRANTED_QOS)

        header.extend(self._encodeLength(len(varHeader) + len(payload)))

        self.writeByteArray(header)
        self.writeByteArray(varHeader)
        self.writeByteArray(payload)

    def _event_unsubscribe(self, packet, qos, dup, retain):
        '''
            取消订阅 回调事件
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        messageId = self._decodeValue(packet[:2])
        packet = packet[2:]

        # Extract the unsubscribing topics
        topics = []

        while len(packet):
            # Get the topic name
            topic = self._decodeString(packet)
            packet = packet[len(topic) + 2:]

            # Add it to the list of topics
            topics.append(topic)

        self.unsubscribeReceived(topics, messageId)

    def unsubscribe(self, topic, messageId):
        '''
            取消订阅
            1.固定头
                ----------------------------------------------------------------
                | bit   |  7  |  6  |  5  |  4  |  3  |   2   |   1   |   0    |
                ----------------------------------------------------------------
                | byte1 | MQTT控制报文类型      | 保留位                       |
                |       |  1  |  0  |  1  |  0  |  0  |   0   |   1   |   0    |
                ---------------------------------------------------------------
                | byte2 | 剩余长度                                             |
                ---------------------------------------------------------------
            2.可变头
                无
            3.有效负载
                 ---------------------------------------------------------------------------------------------
                |             |          描述         |  7  |  6  |  5  |  4  |  3  |   2   |   1   |   0    |
                ----------------------------------------------------------------------------------------------
                |  主题过滤器 |                                                                              |
                ----------------------------------------------------------------------------------------------
                |  byte1      |  Length MSB(0)        |  0  |  0  |  0  |  0  |  0  |   0   |   0   |   0    |
                ----------------------------------------------------------------------------------------------
                |  byte2      |  Length LSB(3)        |  0  |  0  |  0  |  0  |  0  |   0   |   1   |   1    |
                ----------------------------------------------------------------------------------------------
                |  byte3      |  'a'(0x61)            |  0  |  1  |  1  |  0  |  0  |   0   |   0   |   1    |
                ----------------------------------------------------------------------------------------------
                |  byte4      |  '/'(0x2F)            |  0  |  0  |  1  |  0  |  1  |   1   |   1   |   1    |
                ----------------------------------------------------------------------------------------------
                |  byte5      |  'b'(0x62)            |  0  |  1  |  1  |  0  |  0  |   0   |   1   |   0    |
                ----------------------------------------------------------------------------------------------
                |  主题过滤器 |                                                                              |
                ----------------------------------------------------------------------------------------------
                |  byte6      |  Length MSB(0)        |  0  |  0  |  0  |  0  |  0  |   0   |   0   |   0    |
                ----------------------------------------------------------------------------------------------
                |  byte7      |  Length LSB(3)        |  0  |  0  |  0  |  0  |  0  |   0   |   1   |   1    |
                ----------------------------------------------------------------------------------------------
                |  byte8      |  'c'(0x63)            |  0  |  1  |  1  |  0  |  0  |   0   |   1   |   1    |
                ----------------------------------------------------------------------------------------------
                |  byte9      |  '/'(0x2F)            |  0  |  0  |  1  |  0  |  1  |   1   |   1   |   1    |
                ----------------------------------------------------------------------------------------------
                |  byte10     |  'd'(0x64)            |  0  |  1  |  1  |  0  |  0  |   1   |   0   |   0    |
                ----------------------------------------------------------------------------------------------
                取消订阅报文必须有有效载荷，有效载荷里面存的就是你想取消订阅的主题。
                服务器收到了取消订阅报文必须给一个答复报文，答复报文的报文标识符必须跟取消订阅的一样。
        :param topic:
        :param messageId:
        :return:
        '''
        header = bytearray()
        varHeader = bytearray()
        payload = bytearray()

        header.append(0x0A << 4 | 0x01 << 1)

        if messageId is not None:
            varHeader.extend(self._encodeValue(self.messageID))
        else:
            varHeader.extend(self._encodeValue(random.randint(1, 0xFFFF)))

        payload.extend(self._encodeString(topic))

        header.extend(self._encodeLength(len(payload) + len(varHeader)))

        self.writeByteArray(header)
        self.writeByteArray(varHeader)
        self.writeByteArray(payload)

    def _event_unsuback(self, packet, qos, dup, retain):
        '''
            取消订阅确认 回调事件
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        messageId = self._decodeValue(packet[:2])
        self.unsubackReceived(messageId)

    def unsuback(self, messageId):
        '''
            1.固定头
                类型 11
            2.可变头
                取消订阅的报文标识符
            3.有效负载
                无
        :param messageId:
        :return:
        '''
        header = bytearray()
        varHeader = bytearray()

        header.append(0x0B << 4)
        varHeader.extend(self._encodeValue(messageId))

        header.extend(self._encodeLength(len(varHeader)))

        self.writeByteArray(header)
        self.writeByteArray(varHeader)

    def _event_pingreq(self, packet, qos, dup, retain):
        '''
            心跳报文 回调事件
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        self.pingreqReceived()

    def pingreq(self):
        '''
            1.固定头
                类型12
            2.可变头
                无
            3.有效负载
                无
        :return:
        '''
        header = bytearray()
        header.append(0x0C << 4)
        header.extend(self._encodeLength(0))
        self.writeByteArray(header)

    def _event_pingresp(self, packet, qos, dup, retain):
        '''
            心跳响应 回调事件
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        self.pingrespReceived()

    def pingresp(self):
        '''
            1.固定头
                控制类型 13
            2.可变头
                取消订阅的报文标识符
            3.有效负载
                无
        :return:
        '''
        header = bytearray()
        header.append(0x0D << 4)
        header.extend(self._encodeLength(0))
        self.writeByteArray(header)

    def _event_disconnect(self, packet, qos, dup, retain):
        '''
            连接断开 触发事件
        :param packet:
        :param qos:
        :param dup:
        :param retain:
        :return:
        '''
        self.transport.loseConnection()

    def disconnect(self):
        '''
            1.固定头
                报文类型 14
            2.可变头
                无
            3.有效负载
                无
        :return:
        '''
        header = bytearray()
        header.append(0x0E << 4)
        header.extend(self._encodeLength(0))
        self.writeByteArray(header)

    def timeoutConnection(self):
        logger.warning("客户端:{} 超时断开连接...".format((self.transport.client[0], self.transport.client[1])))
        self.transport.loseConnection()

    def connectionMade(self):
        self.setTimeout(GlobalObject().config.get("TIME_OUT_COUNT", MQTT_TIME_OUT))
        logger.info('客户端 : {}:{} 连入...'.format(self.transport.client[0], self.transport.client[1]))

    def connectionLost(self, reason):
        self.setTimeout(None)
        self.disconnectReceived()
        logger.info('客户端 : {}:{} 登出...'.format(self.transport.client[0], self.transport.client[1]))

    def _encodeString(self, string):
        '''

        :param string:
        :return:
        '''
        encoded = bytearray()
        encoded.append(len(string) >> 8)
        encoded.append(len(string) & 0xFF)
        if isinstance(string,str):
            for s in string.encode():
                encoded.append(s)
        else:
            for s in string:
                encoded.append(s)
        return encoded

    def _decodeString(self, encodedString):
        '''
            对 str 进行编码
        :param encodedString:
        :return:
        '''
        length = 256 * encodedString[0] + encodedString[1]
        return encodedString[2:2 + length].decode()

    def _encodeLength(self, length):
        '''

        :param length:
        :return:
        '''
        encoded = bytearray()
        while True:
            digit = length % 128
            length //= 128
            if length > 0:
                digit |= 128
            encoded.append(digit)
            if length <= 0:
                break
        return encoded

    def _encodeValue(self, value : int):
        '''
            对数字进行编码
        :param value:
        :return:
        '''
        encoded = bytearray()
        encoded.append(value >> 8)
        encoded.append(value & 0xFF)
        return encoded

    def _decodeLength(self, lengthArray):
        '''
            解码 获取帧长度
            ─────────────────────────────────────
           │字节数│最小值                        │最大值                          │
           │1     │ 0(0x00)                      │ 127(0x7F)                      │
           │2     │ 128(0x80,0x01)               │ 16383(0xFF,0x7F)               │
           │3     │ 16384(0x80,0x80,0x01)        │ 2097151(0xFF,0xFF,0x7F)        │
           │4     │ 2097152(0x80,0x80,0x80,0x01) │ 268435455(0xFF,0xFF,0xFF,0X7F) │
            ─────────────────────────────────────
        :param lengthArray:
        :return:
        '''
        length = 0
        multiplier = 1
        for i in lengthArray:
            length += (i & 0x7F) * multiplier
            multiplier *= 0x80
            if (i & 0x80) != 0x80:
                break
        return length

    def _decodeValue(self, valueArray):
        '''
            解码获得数字
        :param valueArray:
        :return:
        '''
        value = 0
        multiplier = 1
        for i in valueArray[::-1]:
            value += i * multiplier
            multiplier = multiplier << 8
        return value

    def writeByteArray(self,message : bytearray):
        '''

        :param message:
        :return:
        '''
        # if isinstance(message,bytearray):
        #     self.transport.write(message)
        self.transport.write(bytes(message))

class MQTTClient(MQTT):

    def __init__(self, clientId=None, keepalive=None, willQos=0,
                 willTopic=None, willMessage=None, willRetain=False):
        '''

        :param clientId:
        :param keepalive:
        :param willQos:
        :param willTopic:
        :param willMessage:
        :param willRetain:
        '''
        if clientId is not None:
            self.clientId = clientId
        else:
            self.clientId = "Twisted%i" % random.randint(1, 0xFFFF)

        if keepalive is not None:
            self.keepalive = keepalive
        else:
            self.keepalive = 3000

        self.willQos = willQos
        self.willTopic = willTopic
        self.willMessage = willMessage
        self.willRetain = willRetain

    def connectionMade(self):
        '''

        :return:
        '''
        self.connect(self.clientId, self.keepalive, self.willTopic,
                     self.willMessage, self.willQos, self.willRetain, True)

    def connackReceived(self, status):
        '''

        :param status:
        :return:
        '''
        if status == 0:
            self.mqttConnected()
        else:
            # Error
            pass

    def mqttConnected(self):
        pass