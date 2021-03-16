# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : __init__.py
# @Time     : 2021-02-21 18:07
# @Software : tiseal_app
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
from txfirefly.utils.rpcrestful import RpcRestful
from txrpc.utils.log import logger


def DefferedErrorHandle(err,tag = None):
    '''延迟对象的错误处理'''

    if tag:
        msg = "客户端 : {} :{}".format(tag, err)
        logger.error(msg)
    else:
        msg = "服务器内部错误 : {}".format(err)
        logger.error(msg)

def RpcDefferedErrorHandle(err,tag = None):
    '''延迟对象的错误处理'''

    if tag:
        msg = "客户端:{} :{}".format(tag, err)
        logger.error(msg)
    else:
        msg = "服务器内部错误:{}".format(err)
        logger.error(msg)
    return RpcRestful.error()