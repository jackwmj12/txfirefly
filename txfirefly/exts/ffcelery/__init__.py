# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : __init__.py
# @Time     : 2021-02-20 0:25
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
from celery import Celery
from utils import logger

def create_celery(config):
	logger.debug("create celery program:{name} ".format(name = config["CELERY_NAME"]))
	# print("create celery program:{name} ".format(name=config["CELERY_NAME"]))
	celery_app = Celery(config["CELERY_NAME"])
	# Log.debug("update celery program:{config} ".format(config=config))
	# print("update celery program:{config} ".format(config=config))
	celery_app.conf.update(config)
	return celery_app