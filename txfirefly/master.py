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
from txrpc.globalobject import GlobalObject, rootWhenLeafConnectHandle, rootWhenLeafLostConnectHandle
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
                GlobalObject().rootRemoteMap.keys()
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
        for node in GlobalObject().root.pbRoot.dnsmanager._nodes.values():
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
        for node in GlobalObject().root.pbRoot.dnsmanager._nodes.values():
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
                node: Node = GlobalObject().root.pbRoot.dnsmanager.getNode(nodeName)
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
        remote: NodeChild = GlobalObject().root.pbRoot.dnsmanager.getChildById(nodeId)
        if remote:
            return remote.callbackNodeChild(
                'serverStop'
            ).addCallback(
                lambda x: restful.success(message="指令下发成功")
            ).addErrback(
                lambda x: restful.server_error(message="指令下发失败")
            )
        return restful.server_error(message="指令下发失败")


@rootWhenLeafConnectHandle
def doChildConnect(name, transport):
    '''
    :return
    '''

    name = name.upper()
    id = transport.broker.transport.sessionno
    remote_key = ":".join([name, str(id)])
    logger.debug(f"{remote_key} connected")
    remote_config = GlobalObject().config.get("DISTRIBUTED", {}).get(name, {})
    child_host = transport.broker.transport.client[0]  # 保存子节点ip信息
    # 远程端口信息存入root_list
    # 获取远程端口配置，以及名称 一般为10000，gate
    remote_remotes = remote_config.get('REMOTE', [])
    remote_root_name_list = [remote_remote.upper() for remote_remote in remote_remotes]  # 获取root节点名字信息
    # 本端口信息存入global对象
    # 包含子节点的IP信息 子节点的父节点信息
    GlobalObject().rootRemoteMap[remote_key] = dict(remote_config, **{"HOST": child_host, "ID": id})
    logger.debug(f"当前任务总节点信息:{GlobalObject().rootRemoteMap}")
    # 通知该节点去连接所有他需要连接的节点
    for remote_root_name in remote_root_name_list:
        # 判断需要连接的节点是否正在线
        for root_remote in GlobalObject().rootRemoteMap.values():
            if remote_root_name == root_remote["NAME"]:
                root_remote_key = ":".join([root_remote["NAME"], str(root_remote["ID"])])
                logger.debug(f"节点检查一：{name} 节点连接 remote 节点 : {root_remote_key}")
                GlobalObject().callLeafByID(
                    id, "remoteConnect", name,
                    GlobalObject().rootRemoteMap.get(root_remote_key),
                    GlobalObject().rootRemoteMap[remote_key].get("APP", [])
                )
                break
            else:
                logger.error(f"节点：{name} 连接:{remote_root_name} 失败。原因 ：节点 {remote_root_name} 暂未在线，连接失败")

    # 通知有需要连的node节点连接到此root节点
    for remote_item in GlobalObject().rootRemoteMap.values():
        remote_name = remote_item.get("NAME", "")
        remote_id = remote_item.get("ID", None)
        remote_remote_names = remote_item.get("REMOTE", [])
        if name in remote_remote_names:
            logger.debug(f"节点检查二：{remote_name} 节点连接 remote节点 : {name}")
            GlobalObject().callLeafByID(
                remote_id,
                "remoteConnect",
                remote_name,
                GlobalObject().rootRemoteMap[remote_key],
                remote_item.get("APP", [])
            )


@rootWhenLeafLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    try:
        logger.debug("{} lost connect".format(childId))
        for remote_item in GlobalObject().rootRemoteMap.values():
            if childId == remote_item.get("ID"):
                remote_key = ":".join([remote_item.get("NAME"), str(childId)])
                del GlobalObject().rootRemoteMap[remote_key]
                break
    except Exception as e:
        logger.error(str(e))


class Master(RPCServer):
    '''
    远程master调用对象
    :param
    '''

    def __init__(self, name: str):
        '''
        :return
        '''
        # root对象监听制定端口
        super().__init__(name)
        GlobalObject().root = self

    def run(self):
        GlobalObject().webapp = app
        GlobalObject().webapp.run(host=GlobalObject().config.get("WEB_HOST", "0.0.0.0"),
                                  port=GlobalObject().config.get("WEB_PORT", 1024))