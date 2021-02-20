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
from typing import List


class RpcRestful():
	'''

    200 正常回复,通过 gateway 经过 net 将 message 回复给客户端
    201 登录指令 通过 gateway 在 net 保存客户端连接信息
    300 relay 经过 zmq 广播出去
    400 断开连接

	:param

	'''

	LOGIN = 100

	SUCCESS = 200

	RELAY = 300

	CLOSE = 400

	ERROR = 500

	@classmethod
	def success(cls,data=None,messages : List = []):
		return {
			"code": cls.SUCCESS,
			"data": data,
			"message": messages,
		}

	@classmethod
	def login(cls,data=None,messages : List = []):
		return {
			"code": cls.LOGIN,
			"data": data,
			"message": messages,
		}

	@classmethod
	def relay(cls,data=None,messages : List = []):
		return {
			"code" : cls.RELAY,
			"data": data,
			"message": messages,
		}

	@classmethod
	def close(cls, data=None, messages : List = []):
		return {
			"code": cls.CLOSE,
			"data": data,
			"message": messages,
		}

	@classmethod
	def error(cls, data=None, messages : List = []):
		return {
			"code": cls.ERROR,
			"data": data,
			"message": messages,
		}