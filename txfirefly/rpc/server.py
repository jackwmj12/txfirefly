# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : server.py
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
from loguru import logger
from txfirefly.core.leafnode import leafNode, GlobalObject
from txrpc.server import RPCServer

class Server(RPCServer, leafNode):
    """
    :param
    """
    def __init__(self, name: str):
        super(Server, self).__init__(name)

    def run(self):
        self.beforeRun()
        from twisted.internet import reactor
        reactor.run()

    def prepare(self):
        return self._doWhenStart().addCallback(
            lambda ign: self.connectMaster(
                self.name
            )
        )

    def beforeRun(self):
        return self._doWhenStart().addCallback(
            lambda ign: self.connectMaster(
                self.name
            )
        )