# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : post.py
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
from twisted.internet import task

from txfirefly.exts.ffrequest import FFrequest


def doPost(**kwargs):
	'''
	:param kwargs:
		url 路径
			params 参数内容
				（该参数会随着url一起明文发送）
			header 头
			form 主体
				（该参数会在body处发送）
	:return:
	'''
	
	def fun(x):
		''':return
		'''
		d = FFrequest.post(
			url=kwargs.get('url', None),
			json=kwargs.get('json', None),
		)
		d.addCallback(print)
		
		return d
	
	# task.react(fun)


if __name__ == '__main__':
	url = ""
	form = {
	
	}
	
	doPost(
		url=url,
		json=form,
		params=form,
	)
	