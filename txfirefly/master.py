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
from txrpc.server import RPCServer
from txfirefly.core import *


def doChildConnect(name, transport):
	'''
	:return
	'''
	
	logger.debug(f"{transport.broker.transport.sessionno} connected")
	
	name = name.upper()
	
	logger.debug("{} connected".format(name))
	
	distributed_config = GlobalObject().config.get("DISTRIBUTED", {})
	
	node_config = distributed_config.get(name, {})
	
	child_host = transport.broker.transport.client[0]  # 保存子节点ip信息
	
	# 远程端口信息存入root_list
	# 获取远程端口配置，以及名称 一般为10000，gate
	remotes = node_config.get('REMOTE', [])
	root_list = [remote.upper() for remote in remotes]  # 获取root节点名字信息
	
	# 本端口信息存入global对象
	# 包含子节点的IP信息 子节点的父节点信息
	GlobalObject().remote_map[name] = dict(node_config,**{"HOST": child_host, "ID": transport.broker.transport.sessionno})
	
	logger.debug(f"当前任务节点信息:{GlobalObject().remote_map[name]}")
	
	# 通知该节点去连接所有他需要连接的节点
	for root in root_list:
		# 判断需要连接的节点是否正在线
		if root in GlobalObject().remote_map.keys():
			logger.debug(f"节点检查一：{name} 节点连接 remote节点 : {root}")
			GlobalObject().root.callChildByName(name, "remoteConnect", name, GlobalObject().remote_map.get(root),
			                                    GlobalObject().remote_map[name].get("APP", []))
		else:
			logger.err(f"节点：{name} 连接:{root} 失败。原因 ：节点 {root} 暂未在线，连接失败")
	
	# 通知有需要连的node节点连接到此root节点
	for remote_item in GlobalObject().remote_map.values():
		remote_name = remote_item.get("NAME", "")
		remote_remote_names = remote_item.get("REMOTE", [])
		if name in remote_remote_names:
			logger.debug(f"节点检查二：{remote_name} 节点连接 remote节点 : {name}")
			GlobalObject().root.callChildByName(remote_name, "remoteConnect", remote_name,
			                                    GlobalObject().remote_map[name], remote_item.get("APP", []))

def doChildLostConnect(childId):
	'''
	:return
	'''
	# with open("config.json", "r") as f:
	# 	GlobalObject().config = json.load(f)
	# logger.debug(f"config reloaded \n{GlobalObject().config}")
	
	try:
		remove_key = None
		logger.debug("{} lost connect".format(childId))
		for remote_item in GlobalObject().remote_map.values():
			if childId == remote_item.get("ID"):
				remove_key = remote_item.get("NAME")
				break
		if remove_key:
			del GlobalObject().remote_map[remove_key]
	except Exception as e:
		logger.err(str(e))
		
class MasterNode(RPCServer):
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
		
		GlobalObject().root.childConnectService.mapTarget(doChildConnect)
		GlobalObject().root.childLostConnectService.mapTarget(doChildLostConnect)

