# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : get.py
# @Time     : 2021-02-20 0:33
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

import hashlib

from twisted.internet import reactor, task

from txfirefly.exts.ffrequest import Request


def doGet(**kwargs):
	'''
	:param kwargs:
		url 路径
		params 参数内容
		header 头
		body 主体
	:return:
	:return
	'''
	
	def fun(ign):
		''':return
		'''
		
		d = Request.get(
			url=kwargs.get('url', None),
			params=kwargs.get('params', None),
			header=kwargs.get('header', None),
			body=kwargs.get('body', '')
		)
		
		d.addCallback(print)
		
		return d
	
	task.react(fun)


if __name__ == '__main__':
	url = ""
	
	params = dict(
	)
	doGet(url=url, params=params)
