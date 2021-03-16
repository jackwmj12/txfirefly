# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : masterservice.py
# @Time     : 2021-02-18 23:52
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
from typing import List

from txrpc.distributed.node import RemoteObject
from txrpc.globalobject import GlobalObject
from txrpc.utils import delay_import
from txrpc.utils.log import logger

def masterserviceHandle(target):
    """
    将服务添加进入master节点
    """
    assert GlobalObject().masterremote != None,"请检查master节点是否正常运行"
    GlobalObject().masterremote._reference._service.mapTarget(target)

@masterserviceHandle
def remoteConnect(name, remote : dict,app : List[str]):
    '''
        控制 节点 连接 另一个节点
        :param name:  当前节点名称
        :param remotes: dict {
            NAME : str,
            PORT : int,
            HOST : str,
            WEIGHT : int,
        }
        :app 需要导入的服务路径
        :return:
        '''
    remote_name = remote.get("NAME")
    weight = remote.get("WEIGHT", 10)
    logger.debug(f"master 指令：当前节点 : {name} 连接节点 : {remote_name}")
    port = int(remote.get("PORT"))
    host = remote.get("HOST")
    GlobalObject().remote[remote_name] = RemoteObject(name)
    GlobalObject().remote[remote_name].setWeight(weight)
    GlobalObject().remote[remote_name].connect((host, port))
    # logger.debug(f"当前节点 : {name} 连接节点 : {remote_name} 成功 准备导入服务 : {app}")
    delay_import(app)

@masterserviceHandle
def serverStop():
    """
    """
    logger.debug('service stop !!!')
    if GlobalObject().stophandler:
        GlobalObject().stophandler()
    
    from twisted.internet import reactor
    
    reactor.callLater(0.5, reactor.stop)
    return True

@masterserviceHandle
def serverReload():
    """
    
    """
    logger.debug('service reload !!!')
    
    if GlobalObject().reloadhandler:
        GlobalObject().reloadhandler()
    
    return True