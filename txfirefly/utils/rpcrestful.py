# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : rpcrestful.py
# @Time     : 2021-02-20 0:03
# @Software : od_gateway
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
import enum
from typing import List, Union, Optional, Dict


class RpcRestfulMethodEnum(enum.IntEnum):
	CONNECT = 101

	PUSH = 200

	PUB = 300
	SUB = 301

	ERROR = 400

	DISCONNECT = 500


class RpcRestful():
	'''
	:param

	'''
	def __init__(
		self,
		method: RpcRestfulMethodEnum=RpcRestfulMethodEnum.PUSH,
		data: Union[List[bytes],bytes,None]=None,
		payload: Optional[Dict]=None
	):
		''''''
		self.method: RpcRestfulMethodEnum = method
		self.data: Union[List[bytes],bytes,None] = data
		self.payload: Optional[Dict] = payload

