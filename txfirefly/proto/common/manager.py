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
import time
from typing import Dict, Set

from twisted.internet.protocol import Protocol

from txfirefly.proto.common.connection import Connection
from loguru import logger


class ConnectionManager:
    '''
        连接管理器
        @param _connections: dict {connID:conn Object}管理的所有连接
    '''

    def __init__(self):
        '''
            初始化
            @param _connections: dict {connID:conn Object}
        '''
        self._connectionIdMap: Dict[str, str] = {}
        self._connections: Dict[str, Connection] = {}

    def getNowConnCnt(self):
        '''
            获取当前连接数量
        '''
        cnt = len(self._connections.items())
        return cnt

    def isInConnections(self, id):
        '''

        '''
        if id in self._connections.keys():
            return True
        else:
            return False

    @property
    def connections(self):
        '''

        :return:
        '''
        return self._connections.values()

    @property
    def connectionsID(self):
        '''

        :return:
        '''
        return self._connections.keys()

    def addConnection(self, protocol: Protocol = None, id: str = None):
        '''
            加入一条连接
            @param _conn: Conn object
        '''
        logger.info(f"ConnectionManager Client<{id}> add into connections")
        if id is not None and protocol is not None:
            if self.isInConnections(id):
                logger.warning(f"ConnectionManager 连接池: 连接<{id}> 添加 失败, 系统记录冲突")
                # try:
                #     self.loseConnectionByConnID(id)
                #     # logger.debug(f"连接池 断开并移除原连接: <{id}>")
                # except Exception as e:
                #     logger.error(f"连接池 移除连接失败 {e}")
                return False
            else:
                transport = protocol.transport
                peer_info = {
                    'peer_host': transport.getPeer().host,
                    'peer_port': transport.getPeer().port,
                }
                self._connections[id] = Connection(protocol, peer_info)
                # logger.debug(f"Connections add <{id}> successful")
                return True

    def dropConnectionByID(self, connID):
        '''
            通过连接id 删除连接实例
            @param connID: int 连接的id
        '''
        try:
            if self.isInConnections(connID):
                del self._connections[connID]
                logger.debug(f"ConnectionManager Connections Connection<{connID}> drop successful")
        except Exception as e:
            logger.error(f"ConnectionManager Connections Connection<{connID}> drop failed {e}")

    def getConnectionByID(self, connID) -> Connection:
        """
            通过连接ID获取一条连接
            @param connID: int 连接的id
        """
        return self._connections.get(connID, None)

    def loseConnectionByConnID(self, connID):
        """
            通过连接ID 主动 断开与客户端的连接
        """
        conn = self.getConnectionByID(connID)
        if conn:
            try:
                conn.loseConnection()
            except Exception as e:
                logger.error(f"连接池 连接 <{connID}> 断开失败 {e}")
        # self.dropConnectionByID(connID)

    def pushMessageToConn(self, conn_id, msg):
        """
            通过连接ID,向该ID的连接发送数据
        """
        logger.debug(f"NET 端口 向 : {conn_id} 推送数据 : {msg}")
        try:
            conn = self.getConnectionByID(conn_id)
            # logger.debug(f"连接池 获取到端口 : {conn}")
            if conn:
                try:
                    conn.safeToWriteData(msg)
                    return True
                except Exception as e:
                    logger.error(e)
            else:
                logger.debug(f"连接池 查无该对象:{conn_id}")
        except Exception as e:
            logger.error(str(e))
        return False
    
    def publishMessage(self, conns, msg):
        """
            通过连接ID,向该ID的连接发送数据
        """
        logger.debug(f"NET端口 向 : {conns} 推送数据 : {msg}")
        if conns:
            for conn_id in conns:
                try:
                    conn = self.getConnectionByID(conn_id)
                    # logger.debug(f"连接池 获取到端口:{conn}")
                    if conn:
                        try:
                            conn.safeToWriteData(msg)
                            return True
                        except Exception as e:
                            logger.error(e)
                    else:
                        logger.debug(f"连接池 查无该对象 : {conn_id}")
                except Exception as e:
                    logger.error(str(e))
            return False