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
from typing import Dict, List, KeysView, ValuesView, Optional, Union

from twisted.internet import protocol

from loguru import logger

from txfirefly.proto.mqtt.core.conn import Connection


class ConnIsExistException(Exception):
    pass

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

    def getNowConnCnt(self) -> int:
        '''
            获取当前连接数量
        '''
        cnt = len(self._connections.items())
        return cnt

    def addConnection(self, conn : protocol.Protocol = None, id : str = None):
        '''
            将连接加入连接池
        :param conn:
        :param id:
        :return:
        '''
        # logger.debug(f"Connections add Connection<{id}>")
        if id is not None and conn :
            if self.isInConnections(id):
                logger.warning(f"连接池 系统记录冲突: <{id}> 已经存在于 <{self._connections.keys()}>")
                raise ConnIsExistException()
            self._connections[id] = Connection(conn)

    def isInConnections(self, id) -> bool:
        ''''''
        if id in self._connections.keys():
            return True
        else:
            return False

    @property
    def connections(self) -> ValuesView[Connection]:
        '''

        :return:
        '''
        return self._connections.values()

    @property
    def clinetIDs(self) -> KeysView[str]:
        '''

        :return:
        '''
        return self._connections.keys()

    def dropConnectionByID(self, clinetID : str):
        '''
            通过连接id 删除连接实例
        :param clinetID:
        :return:
        '''
        try:
            if self.isInConnections(clinetID):
                del self._connections[clinetID]
                logger.error(f"连接池 连接 <{clinetID}> 删除 成功")
        except Exception as e:
            logger.error(f"连接池 连接 <{clinetID}> 删除 失败 {e}")

    def getConnectionByID(self, clinetID) -> Connection:
        """
            通过连接ID获取一条连接
            @param connID: int 连接的id
        """
        return self._connections.get(clinetID, None)

    def loseConnectionByclinetID(self, clinetID):
        """
            通过连接ID 主动 断开与客户端的连接
        :param connID:
        :return:
        """
        conn = self.getConnectionByID(clinetID)
        if conn:
            try:
                conn.loseConnection()
            except Exception as e:
                logger.error(f"连接池 连接 <{clinetID}> 断开失败 {e}")
        self.dropConnectionByID(clinetID)