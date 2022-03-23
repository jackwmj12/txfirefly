# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : __init__.py
# @Time     : 2021-02-18 23:53
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

from txrpc.distributed.node import RemoteObject
from txrpc.globalobject import GlobalObject
from loguru import logger

def master_conncet(name : str,master : dict = None):
    '''
    :param
        master : dict {
            SRC_NAME : str,
	        PORT : int,
	        HOST : str,
        }
    '''
    # master_config = GlobalObject().config.get("DISTRIBUTED", {}).get("MASTER", {})
    logger.debug(f"master node is runing on {master}")
    # # GlobalObject().masterremote = RemoteMasterObject(service_config.get("NAME"))
    GlobalObject().masterremote = RemoteObject(name)
    logger.debug("connecting into master node...")
    # node连接 master 节点，若连接不成功，则会退出服务
    GlobalObject().masterremote.connect((master.get('HOST'), int(master.get('PORT'))))
    logger.debug("connect master node success...")
    logger.debug("providing methods to the master node")
    logger.debug("provide methods to the master node success")
    # ########################################
    # 切勿删除本段代码
    # 导入master服务，该服务主要提供
    #     master 控制 node 的 remote连接
    #     master 控制 node 的 reload
    #     master 控制 node 的 stop
    from txfirefly.core import masterservice

