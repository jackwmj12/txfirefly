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
from typing import Dict

from twisted.internet import protocol

from txfirefly.net.common.connection import Connection
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
        self._connections : Dict[str,Connection] = {}

    def getNowConnCnt(self):
        '''
            获取当前连接数量
        '''
        cnt = len(self._connections.items())
        return cnt

    def addConnection(self, conn : protocol.Protocol = None, id : str = None):
        '''
            加入一条连接
            @param _conn: Conn object
        '''
        logger.debug(f"Connections add Connection: <{id}>")
        if id and conn :
            if self.isInConnections(id):
                logger.warning(f"连接池 系统记录冲突: <{id}> 已经存在于 <{self._connections.keys()}>")
                try:
                    self.loseConnectionByConnID(id)
                    logger.debug(f"连接池 断开并移除原连接: <{id}>")
                except Exception as e:
                    logger.error(f"连接池 移除连接失败 {e}")
            self._connections[id] = Connection(conn, id)

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

    def dropConnectionByID(self, connID):
        '''
            通过连接id 删除连接实例
            @param connID: int 连接的id
        '''
        try:
            del self._connections[connID]
        except Exception as e:
            logger.error(f"连接池 连接 <{connID}> 删除 失败 {e}")

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
        self.dropConnectionByID(connID)

    def pushObject(self, msg, sendList):
        """
            通过连接ID,向该ID的连接发送数据
        """
        logger.debug(f"NET端口 向 : {sendList} 推送数据 : {msg}")
        if sendList:
            if isinstance(sendList, list):
                for target in sendList:
                    try:
                        conn = self.getConnectionByID(target)
                        # logger.debug(f"连接池 获取到端口:{conn}")
                        if conn:
                            try:
                                conn.safeToWriteData(msg)
                            except Exception as e:
                                logger.error(e)
                        else:
                            logger.debug(f"连接池 查无该对象 : {target}")
                    except Exception as e:
                        logger.error(str(e))
                return True
            else:
                try:
                    conn = self.getConnectionByID(sendList)
                    # logger.debug(f"连接池 获取到端口 : {conn}")
                    if conn:
                        try:
                            conn.safeToWriteData(msg)
                            return True
                        except Exception as e:
                            logger.error(e)
                    else:
                        logger.debug(f"连接池 查无该对象:{sendList}")
                except Exception as e:
                    logger.error(str(e))
            return False