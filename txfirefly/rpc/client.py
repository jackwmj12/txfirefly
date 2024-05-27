# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : client.py
# @Time     : 2021-02-18 23:26
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
from twisted.internet import defer

from txfirefly.core.leafnode import leafNode
from txrpc.client import RPCClient
from txrpc.globalobject import GlobalObject


class Client(RPCClient, leafNode):
    """
    :param
    """
    def __init__(self, name : str):
        '''
            节点对象
        :param name:
        :param single:
        '''
        super(Client, self).__init__(name)

    def run(self):
        from twisted.internet import reactor
        reactor.run()

    def _doWhenStart(self) -> defer.Deferred:
        '''
                程序开始时,将会运行该函数
        :return:
        '''

        deferList = []
        for service in GlobalObject().startService:
            deferList.append(
                GlobalObject().startService.callFunction(service)
            )
        deferList.append(
            lambda ign: self.connectMaster(
                self.name
            )
        )
        return defer.DeferredList(deferList, consumeErrors=True)

