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
	
	name = name.upper()
	
	id = transport.broker.transport.sessionno
	
	remote_key = ":".join([name,str(id)])
	
	logger.debug(f"{remote_key} connected")
	
	remote_config = GlobalObject().config.get("DISTRIBUTED", {}).get(name, {})
	
	child_host = transport.broker.transport.client[0]  # 保存子节点ip信息
	
	# 远程端口信息存入root_list
	# 获取远程端口配置，以及名称 一般为10000，gate
	remote_remotes = remote_config.get('REMOTE', [])
	remote_root_name_list = [remote_remote.upper() for remote_remote in remote_remotes]  # 获取root节点名字信息
	
	# 本端口信息存入global对象
	# 包含子节点的IP信息 子节点的父节点信息
	GlobalObject().remote_map[remote_key] = dict(remote_config,**{"HOST": child_host, "ID": id })
	
	logger.debug(f"当前任务总节点信息:{GlobalObject().remote_map}")
	
	# 通知该节点去连接所有他需要连接的节点
	for remote_root_name in remote_root_name_list:
		# 判断需要连接的节点是否正在线
		for root_remote in GlobalObject().remote_map.values():
			if remote_root_name == root_remote["NAME"]:
				root_remote_key = ":".join([root_remote["NAME"],str(root_remote["ID"])])
				logger.debug(f"节点检查一：{name} 节点连接 remote 节点 : {root_remote_key}")
				GlobalObject().root.callChildById(id, "remoteConnect", name, GlobalObject().remote_map.get(root_remote_key),
				                                    GlobalObject().remote_map[remote_key].get("APP", []))
				break
			else:
				logger.err(f"节点：{name} 连接:{remote_root_name} 失败。原因 ：节点 {remote_root_name} 暂未在线，连接失败")
				
		# if root in GlobalObject().remote_map.keys():
		# 	logger.debug(f"节点检查一：{name} 节点连接 remote节点 : {root}")
		# 	GlobalObject().root.callChildById(id, "remoteConnect", name, GlobalObject().remote_map.get(root),
		# 	                                    GlobalObject().remote_map[name].get("APP", []))
		# else:
		# 	logger.err(f"节点：{name} 连接:{root} 失败。原因 ：节点 {root} 暂未在线，连接失败")
	
	# 通知有需要连的node节点连接到此root节点
	for remote_item in GlobalObject().remote_map.values():
		remote_name = remote_item.get("NAME", "")
		remote_id = remote_item.get("ID", None)
		remote_remote_names = remote_item.get("REMOTE", [])
		if name in remote_remote_names:
			logger.debug(f"节点检查二：{remote_name} 节点连接 remote节点 : {name}")
			GlobalObject().root.callChildById(remote_id, "remoteConnect", remote_name,
			                                    GlobalObject().remote_map[remote_key], remote_item.get("APP", []))

def doChildLostConnect(childId):
	'''
	:return
	'''
	try:
		logger.debug("{} lost connect".format(childId))
		for remote_item in GlobalObject().remote_map.values():
			if childId == remote_item.get("ID"):
				remote_key = ":".join([remote_item.get("NAME"),str(childId)])
				del GlobalObject().remote_map[remote_key]
				break
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


