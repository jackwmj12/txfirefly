# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : run.py
# @Time     : 2024-01-22 16:31
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

from demo.tcp.protocol import TcpFactory

LISTEN_PORT = 8001

tcp_factory = TcpFactory()
logger.debug("build tcp_factory success...")
# 监听TCP端口
from twisted.internet import reactor
reactor.listenTCP(LISTEN_PORT, tcp_factory)
logger.info("服务器配置完毕，准备运行，运行地址为{}:{}".format("localhost",LISTEN_PORT))
reactor.run()