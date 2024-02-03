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
from txfirefly.core.leafnode import leafNode
from txrpc.client import RPCClient
from txrpc.globalobject import GlobalObject


class ClientNode(RPCClient,leafNode):
    """
    :param
    """
    def __init__(self, name : str, single=False):
        '''
            节点对象
        :param name:
        :param single:
        '''
        super(ClientNode, self).__init__(name)
        self.single = single

    def run(self):
        self.beforeRun()
        from twisted.internet import reactor
        reactor.run()

    def install(self):
        d = self._doWhenStart()
        if not self.single:
            d.addCallback(lambda ign: self.connectMaster())

    def prepare(self):
        d = self._doWhenStart()
        if not self.single:
            d.addCallback(lambda ign: self.connectMaster())

    def beforeRun(self):
        d = self._doWhenStart()
        if not self.single:
            d.addCallback(lambda ign: self.connectMaster())