# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : master.py
# @Time     : 2021-02-18 23:15
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
import json

from twisted.internet import defer
from typing import List

from txfirefly.proto.http import KleinApp
from txfirefly.proto.http.utils import Form
from txfirefly.utils import restful
from txrpc.distributed.child import NodeChild
from txrpc.distributed.manager import Node
from txrpc.globalobject import GlobalObject, onRootWhenLeafConnectHandle, onRootWhenLeafLostConnectHandle
from txrpc.server import RPCServer
from txfirefly.core import *
from functools import wraps

from loguru import logger


class NotFound(Exception):
    pass


def errorBack(reason):
    pass


app = KleinApp()


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        logger.debug("当前URL 需要登录")
        return func(*args, **kwargs)
        # if g.user:
        #     return func(*args,**kwargs)
        # else:
        #     return restful.unauth_error(message="请登录")

    return inner


@app.route('/')
def home(request):
    return 'Hello, world!'


with app.subroute("/apis") as app:
    @app.handle_errors(NotFound)
    def notfound(request, failure):
        request.setResponseCode(404)
        return 'Not found, I say'


    @app.route("/get-nodes", methods=["GET"])
    def get_nodes(request):
        """
        :parameter
        """
        return restful.success(
            data=list(
                GlobalObject().leafRemoteMap.keys()
            )
        )


    @app.route("/get-config", methods=["GET"])
    def get_config(request):
        """
        :parameter
        """
        # logger.debug(request)
        # logger.debug(request.method)
        # logger.debug(request.json)
        return restful.success(data=GlobalObject().config)


    @app.route("/set-config", methods=["POST"])
    def set_config(request):
        """
        :parameter
        """
        return restful.server_error(message="暂无此功能")


    @app.route("/stop-all", methods=["POST"])
    def stop_all(request):
        """
        :parameter
        """
        deferred_list = []
        for node in GlobalObject().app.pbRoot.dnsmanager._nodes.values():
            for remote in node.children:
                if remote:
                    deferred_list.append(
                        remote.callbackNodeChild(
                            'serverStop'
                        ).addCallback(errorBack)
                    )
        from twisted.internet import reactor
        return defer.DeferredList(
            deferred_list,
            consumeErrors=True
        ).addCallback(
            lambda x: reactor.stop()
        )


    @app.route("/reload-all", methods=["POST"])
    def reload_all(request):
        """
        :parameter
        """
        deferred_list = []
        for node in GlobalObject().app.pbRoot.dnsmanager._nodes.values():
            for remote in node.children:
                if remote:
                    deferred_list.append(
                        remote.callbackNodeChild(
                            'serverReload'
                        ).addCallback(
                            errorBack
                        )
                    )
        return defer.DeferredList(
            deferred_list,
            consumeErrors=True
        ).addCallback(
            lambda x: restful.success(message="指令下发成功")
        ).addErrback(
            lambda x: restful.server_error(message="指令下发失败")
        )


    @app.route("/start-node", methods=["POST"])
    def start_node(request):
        """
        :parameter
        """
        return restful.server_error(message="暂无此功能")


    @app.route("/stop-nodes", methods=["POST"])
    def stop_nodes(request):
        """
        :parameter
        """
        defer_list = []
        form = Form(request)
        nodeNameStr = form.get("name", None)
        if nodeNameStr:
            nodeNames = nodeNameStr.split(",")

            for nodeName in nodeNames:
                node: Node = GlobalObject().app.pbRoot.dnsmanager.getNode(nodeName)
                if node and node.children:
                    for remote in node.children:
                        if remote:
                            d = remote.callbackNodeChild('serverStop').addCallback(errorBack)
                            defer_list.append(d)

        return defer.DeferredList(
            defer_list,
            consumeErrors=True
        ).addCallback(
            lambda x: restful.success(message="指令下发成功")
        ).addErrback(
            lambda x: restful.server_error(message="指令下发失败")
        )


    @app.route("/stop-node", methods=["POST"])
    def stop_node(request):
        """
		:parameter
		"""
        form = Form(request)
        nodeId = form.get("id", None, int)
        remote: NodeChild = GlobalObject().app.pbRoot.dnsmanager.getChildById(nodeId)
        if remote:
            return remote.callbackNodeChild(
                'serverStop'
            ).addCallback(
                lambda x: restful.success(message="指令下发成功")
            ).addErrback(
                lambda x: restful.server_error(message="指令下发失败")
            )
        return restful.server_error(message="指令下发失败")


@onRootWhenLeafConnectHandle
def doChildConnect(name, transport):
    '''
    :return
    '''
    
    current_leaf_name = name.upper()
    current_leaf_id = transport.broker.transport.sessionno
    current_leaf_key = ":".join([current_leaf_name, str(current_leaf_id)])
    logger.debug(f"当前节点 <{current_leaf_key}> 连接成功")
    current_leaf_config = GlobalObject().config.get("DISTRIBUTED", {}).get(current_leaf_name, {})
    # 远程端口信息存入root_list
    # 获取远程端口配置，以及名称 一般为10000，gate_od
    current_leaf_remotes = current_leaf_config.get('REMOTE', [])
    current_leaf_remote_names = [current_leaf_remote.upper() for current_leaf_remote in current_leaf_remotes]  # 获取root节点名字信息
    # 本端口信息存入global对象
    # 包含子节点的IP信息 子节点的父节点信息
    GlobalObject().leafRemoteMap[current_leaf_key] = dict(current_leaf_config, **{"ID": current_leaf_id})
    logger.debug(f"当前总节点信息: {GlobalObject().leafRemoteMap.keys()}")

    logger.debug(f"节点检查一：{current_leaf_key} 节点检查需要主动连接的节点 {current_leaf_remote_names}")
    # 通知该节点去连接所有他需要连接的节点
    for current_leaf_remote_name in current_leaf_remote_names:
        # 判断需要连接的节点是否正在线
        for master_leaf_remote in GlobalObject().leafRemoteMap.values():
            if current_leaf_remote_name == master_leaf_remote["NAME"]:
                master_leaf_remote_key = ":".join([master_leaf_remote["NAME"], str(master_leaf_remote["ID"])])
                logger.debug(f"节点检查一：{current_leaf_key} 节点连接 remote 节点 : {current_leaf_remote_name}")
                GlobalObject().callLeafByID(
                    current_leaf_id,
                    "remoteConnect",
                    current_leaf_name, # 当前节点名称
                    GlobalObject().leafRemoteMap.get(master_leaf_remote_key), # 对象节点KEY
                    GlobalObject().leafRemoteMap[current_leaf_key].get("APP", []) # 挂载的服务路径
                ).addCallback(logger.debug).addErrback(logger.error)
            # else:
            #     logger.error(f"节点：{current_leaf_key} 连接:{master_leaf_remote_name} 失败。原因 ：节点 {master_leaf_remote_name} 暂未在线，连接失败")

    logger.debug(f"节点检查二：{current_leaf_key} 节点检查需要被动连接的节点")
    # 通知有需要连的node节点连接到此root节点
    for master_leaf_remote in GlobalObject().leafRemoteMap.values():
        master_leaf_remote_remote_names = master_leaf_remote.get("REMOTE", [])
        if current_leaf_name in master_leaf_remote_remote_names:
            master_leaf_remote_name = master_leaf_remote.get("NAME", "")
            master_leaf_remote_id = master_leaf_remote.get("ID", None)
            # leaf_remote_key = ":".join([name, str(leaf_remote["ID"])])
            logger.debug(f"节点检查二 发起：{master_leaf_remote_name}:{master_leaf_remote_id} 节点连接 remote节点 : {current_leaf_name}")
            GlobalObject().callLeafByID(
                master_leaf_remote_id,
                "remoteConnect",
                master_leaf_remote_name, # 当前节点名称
                GlobalObject().leafRemoteMap[current_leaf_key],  # 对象节点KEY
                master_leaf_remote.get("APP", [])# 挂载的服务路径
            ).addCallback(logger.debug).addErrback(logger.error)



@onRootWhenLeafLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    try:
        logger.debug("{} lost connect".format(childId))
        for remote_item in GlobalObject().leafRemoteMap.values():
            if childId == remote_item.get("ID"):
                remote_key = ":".join([remote_item.get("NAME"), str(childId)])
                del GlobalObject().leafRemoteMap[remote_key]
                break
    except Exception as e:
        logger.error(str(e))


class Master(RPCServer):
    '''
    远程master调用对象
    :param
    '''

    def __init__(self, name: str, service_path = None, port=None):
        '''
        :return
        '''
        # root对象监听制定端口
        super().__init__(name, service_path, port)
        GlobalObject().app = self
        GlobalObject().webapp = app
        

    def run(self):
        from twisted.internet import reactor
        reactor.addSystemEventTrigger('after', 'startup', self._doWhenStart) # 绑定系统启动触发的hook函数
        reactor.addSystemEventTrigger('before', 'shutdown', self._doWhenStop) # 绑定系统关闭触发的hook函数
        
        GlobalObject().webapp.run(
            host=GlobalObject().config.get("WEB_HOST", "0.0.0.0"),
            port=GlobalObject().config.get("WEB_PORT", 1024)
        )
        