# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : test_db.py
# @Time     : 2021-02-20 0:38
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


import time

from txfirefly.exts.task import Task, PARALLEL_STYLE, SchedulTask, TaskManager, runSchedul
from loguru import logger

SCHEDUL_TIME = 5


# def test(*args, **kwargs):
#     '''
#
#     '''
#     time.sleep(20)
#     print("task1 over")
#     return 1

# def test2(*args, **kwargs):
#     '''
#
#     '''
#     print("task2 over")
#     return 2

# def test3(*args, **kwargs):
#     '''
#
#     '''
#     print("task3 over")
#     return 3

class test1(Task):
	runstyle = PARALLEL_STYLE
	
	def _run(self, *args, **kwargs):
		time.sleep(20)
		print("task1 over")
		return 1


class test2(Task):
	runstyle = PARALLEL_STYLE
	
	def _run(self, *args, **kwargs):
		print("task2 over")
		return 2


class test3(Task):
	runstyle = PARALLEL_STYLE
	
	def _run(self, *args, **kwargs):
		print("task3 over")
		return 3


class test4(SchedulTask):
	runstyle = PARALLEL_STYLE
	op_int = 1
	
	def _run(self, *args, **kwargs):
		print("task3 over")
		return 3


if __name__ == '__main__':
	from twisted.internet import reactor
	
	task = test4()
	reactor.callLater(1, task.run)
	reactor.callLater(5, task.cancel)
	
	task_manager = TaskManager("task1")
	
	task_manager.mapFunction(test1())
	task_manager.mapFunction(test2())
	task_manager.mapFunction(test3())
	
	runSchedul(task_manager, 5)
	
	from twisted.internet import reactor
	
	#
	reactor.run()