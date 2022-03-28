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
from typing import List, Union


class RpcRestful():
	'''

    200 正常回复,通过 gateway 经过 net 将 message 回复给客户端
    201 登录指令 通过 gateway 在 net 保存客户端连接信息
    202 relay 经过 zmq 广播出去
    203 断开连接
    204 请求订阅
    500 错误

	:param

	'''

	LOGIN = 201
	SUCCESS = 200
	RELAY = 202
	CLOSE = 203
	SUB = 204
	ERROR = 500

	@classmethod
	def success(cls,data=None,messages : Union[List,bytes] = []):
		'''
			正常回复,通过 gateway 经过 net 将 message 回复给客户端
		:param data:
		:param messages:
		:return:
		'''
		return {
			"code": cls.SUCCESS,
			"data": data,
			"message": messages,
		}

	@classmethod
	def login(cls,data=None,messages : Union[List,bytes] = []):
		'''
			登录指令 gate 端 将客户连接信息返回给net端, net保存客户端连接信息在内存
		:param data:
		:param messages:
		:return:
		'''
		return {
			"code": cls.LOGIN,
			"data": data,
			"message": messages,
		}

	@classmethod
	def relay(cls,data=None,messages : Union[List,bytes] = []):
		'''
			relay : gate 端 通过 net 端 使用 zmq 广播
		:param data:
		:param messages:
		:return:
		'''
		return {
			"code" : cls.RELAY,
			"data": data,
			"message": messages,
		}

	@classmethod
	def close(cls, data=None, messages : Union[List,bytes] = []):
		'''
			 gate 端 通知 net 断开连接
		:param data:
		:param messages:
		:return:
		'''
		return {
			"code": cls.CLOSE,
			"data": data,
			"message": messages,
		}

	@classmethod
	def error(cls, data=None, messages : Union[List,bytes] = []):
		'''
			gate 端 通知 net 端有报错,并将报错信息反馈给 client 端
		:param data:
		:param messages:
		:return:
		'''
		return {
			"code": cls.ERROR,
			"data": data,
			"message": messages,
		}

	@classmethod
	def sub(cls, data=None, messages: Union[List, bytes] = []):
		'''
			订阅指令
		:param data:
		:param messages:
		:return:
		'''
		return {
			"code": cls.SUB,
			"data": data,
			"message": messages,
		}