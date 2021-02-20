# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : utils.py
# @Time     : 2021-02-20 0:44
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

import json


class FFdict():
	
	def __init__(self):
		self._data = {}
	
	def get_from(self, args):
		''':param'''
		for k, v in args.items():
			if k is not None:
				self.set(k.decode(), v[0].decode())
		return self
	
	def set(self, k, v):
		self._data[k] = v
	
	def get(self, key, default=None, type=str):
		# ret = self._data[key]
		ret = self._data.get(key, None)
		if ret != None:
			ret = type(ret)
		else:
			ret = default
		return ret
	
	@property
	def data(self):
		return self._data


class FFform(FFdict):
	
	def __init__(self, request):
		'''
		request:
		:param
		'''
		super().__init__()
		self.get_from(json.loads(request.content.getvalue().decode()))
	
	def get_from(self, args):
		''':param'''
		for k, v in args.items():
			if k is not None:
				self.set(k, v)
		return self
	
	@property
	def form(self):
		return self._data
	
	@staticmethod
	def get_item(request, key, default=None, type=str):
		'''
		:return
		'''
		ret = json.loads(request.content.getvalue().decode()).get(key, default)
		return type(ret)


class FFargs(FFdict):
	
	def __init__(self, request):
		'''
		request:
		:param
		'''
		super().__init__()
		self.get_from(request.args)
	
	@property
	def args(self):
		return self._data
	
	@staticmethod
	def get_item(request, key, default=None, type=str):
		'''
		:return
		'''
		ret = request.args.get(key.decode(), default)
		return type(ret)