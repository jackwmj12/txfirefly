# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : __init__.py
# @Time     : 2021-02-20 0:37
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
import copy
import threading
import time
from abc import abstractmethod

from twisted.internet import defer, threads, reactor
from typing import List

from loguru import logger

SINGLE_STYLE = 1
PARALLEL_STYLE = 2


class TaskManager():
	
	def __init__(self, name):
		self._name = name
		self.unDisplay = set()
		self._lock = threading.RLock()
		self._targets = {}  # Keeps track of targets internally
	
	def __iter__(self):
		return self._targets.itervalues()
	
	def addUnDisplayTarget(self, command):
		"""
		任务黑名单，加入此处的任务将无法执行
		"""
		self.unDisplay.add(command)
	
	def mapTarget(self, target):
		"""
		Add a target to the service.
		"""
		self._lock.acquire()
		try:
			key = target.__class__.__name__
			if key in self._targets.keys():
				exist_target = self._targets.get(key)
				logger.warning("target [%s] Already exists, [%s] will be covered by [%s]" % (key, exist_target.__class__.__name__, target.__class__.__name__))
			logger.info("当前服务器 task {} 注册成功".format(key))
			self._targets[key] = target
		finally:
			self._lock.release()
	
	def unMapTarget(self, target):
		"""Remove a target from the service."""
		self._lock.acquire()
		try:
			key = target.__class__.__name__
			if key in self._targets:
				del self._targets[key]
		finally:
			self._lock.release()
	
	def unMapTargetByKey(self, targetKey):
		"""Remove a target from the service."""
		self._lock.acquire()
		try:
			del self._targets[targetKey]
		finally:
			self._lock.release()
	
	def getTarget(self, targetKey):
		"""Get a target from the service by name."""
		self._lock.acquire()
		try:
			# Log.msg("获取target：{}".format(targetKey))
			target = self._targets.get(targetKey, None)
		finally:
			self._lock.release()
		return target
	
	def callTarget(self, targetKey, *args, **kwargs):
		'''call Target
		@param conn: client connection
		@param targetKey: target ID
		@param data: client data
		'''
		target = self.getTarget(targetKey)
		
		if not target:
			return None
		
		if target.runstyle == SINGLE_STYLE:
			self._lock.acquire()
			try:
				if not target:
					logger.error('the task ' + str(targetKey) + ' not Found on tasks in ' + self._name)
					return None
				if targetKey not in self.unDisplay:
					logger.warning("call method %s on tasks [single]" % target.__class__.__name__)
					return None
				defer_data = target.run(*args, **kwargs)
				if not defer_data:
					return None
				if isinstance(defer_data, defer.Deferred):
					return defer_data
				result = defer.Deferred()
				result.callback(defer_data)
			finally:
				self._lock.release()
		else:
			self._lock.acquire()
			try:
				if not target:
					logger.error('the task ' + str(targetKey) + ' not Found on tasks in ' + self._name)
					return None
				# logger.debug("call method %s on tasks [parallel]" % target.__class__.__name__)
				result = threads.deferToThread(target.run, *args, **kwargs)
			finally:
				self._lock.release()
		return result
	
	def runAll(self):
		d_list = []
		for item in self._targets.keys():
			d_list.append(self.callTarget(item))
		return defer.DeferredList(d_list)
	
	def runSchedul(self, delta):
		reactor.callLater(delta, self._runSchedul, delta)
	
	def _runSchedul(self, delta):
		self.runAll()
		self.runSchedul(delta)
	
	def runSchedulFun(self, delta, targetKey):
		reactor.callLater(delta, self._runSchedulFun, delta, targetKey)
	
	def _runSchedulFun(self, delta, targetKey):
		self.callTarget(targetKey)
		self.runSchedulFun(delta, targetKey)

class Task():
	runstyle = SINGLE_STYLE
	
	def __init__(self):
		pass
	
	def run(self, *args, **kwargs):
		self._task_in_reactor = None
		return self._run()
	
	@abstractmethod
	def _run(self, *args, **kwargs):
		pass
	
	def callLater(self, delta, *args, **kwargs):
		self._task_in_reactor = reactor.callLater(delta, self.run, *args, **kwargs)
	
	def cancel(self):
		if self._task_in_reactor != None:
			self._task_in_reactor.cancel()

class LoopTask(Task):
	runstyle = SINGLE_STYLE
	op_int = 0
	
	def __init__(self):
		super().__init__()
		self._task_in_reactor = None
	
	def run(self, *args, **kwargs):
		logger.info("loop task {} will be called {}s later".format(self.__class__.__name__, self.op_int))
		if self._task_in_reactor:
			self._run(*args, **kwargs)
		if self.op_int != 0:
			self._task_in_reactor = reactor.callLater(self.op_int, self.run, *args, **kwargs)
		else:
			self._run(*args, **kwargs)

class SchedulTask(Task):
	'''
		schedul {
			time:0~604,800,

		}
	:param
	'''
	
	def __init__(self):
		super().__init__()
		self.schedul_manager: SchedulManager = SchedulManager(self)
	
	def next(self, time_=time.time()):
		return self.schedul_manager.next(time_)
	
	def pre(self, time_=time.time()):
		return self.schedul_manager.pre(time_)
	
	def run(self, *args, **kwargs):
		if self._task_in_reactor:
			self._run(*args, **kwargs)
		next_time = self.next()
		if next_time != 0:
			self._task_in_reactor = reactor.callLater(next_time, self.run, *args, **kwargs)
	
	def _schedulChanged(self):
		pass
	
	def addSchedul(self, time):
		self.schedul_manager.add(time)
	
	def removeSchedul(self, time):
		self.schedul_manager.remove(time)

class SchedulManager():
	
	def __init__(self, task: SchedulTask):
		self.task = task
		self._scheduls: List[Schedul] = []
		self.cur = 0
	
	def add(self, time):
		if time not in self._scheduls:
			self._scheduls.append(time)
			self._scheduls.sort()
			self.task._schedulChanged()
	
	def remove(self, time):
		if time in self._scheduls:
			self._scheduls.remove(time)
			self.task._schedulChanged()
	
	def scheduls(self):
		return self._scheduls
	
	def next(self, time):
		return None
	
	def pre(self, time):
		return None

class Schedul():
	def __init__(self):
		self.pre: Schedul = None
		self.next: Schedul = None
		self.time: int = 0
	
	def isHeader(self):
		return not self.pre
	
	def isTail(self):
		return not self.next

def runSchedul(taskmanager, delta):
	if isinstance(taskmanager, TaskManager):
		taskmanager.runAll()
		reactor.callLater(delta, runSchedul, taskmanager, delta)

def runAll(taskmanager):
	if isinstance(taskmanager, TaskManager):
		taskmanager.runAll()