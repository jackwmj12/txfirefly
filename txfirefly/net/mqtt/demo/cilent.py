# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : cilent.py
# @Time     : 2022-07-19 13:24
# @Software : od_app
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
from twisted.internet.protocol import ClientFactory, Protocol
from typing import Tuple

from txfirefly.net.mqtt.core.mqtt import MQTTClient

HOST = 'localhost'
PORT = 5982

class TSClntFactory(ClientFactory):
    protocol = MQTTClient

    def startedConnecting(self, connector):
        logger.debug(f"startedConnecting")

    def buildProtocol(self, addr: Tuple[str, int]) -> "Protocol":
        """
        Create an instance of a subclass of Protocol.

        The returned instance will handle input on an incoming server
        connection, and an attribute "factory" pointing to the creating
        factory.

        Alternatively, L{None} may be returned to immediately close the
        new connection.

        Override this method to alter how Protocol instances get created.

        @param addr: an object implementing L{twisted.internet.interfaces.IAddress}
        """
        assert self.protocol is not None
        p = self.protocol(clientId="68a890aa4f9a474f963931fe38214479")
        p.factory = self
        return p

if __name__ == '__main__':
    from twisted.internet import reactor
    from loguru import logger

    reactor.connectTCP(HOST, PORT, TSClntFactory())
    reactor.run()

