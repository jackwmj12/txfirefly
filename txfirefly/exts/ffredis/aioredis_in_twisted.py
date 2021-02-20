# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : aioredis_in_twisted.py
# @Time     : 2021-02-20 0:29
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
import asyncio
from twisted.internet import asyncioreactor
asyncioreactor.install(asyncio.get_event_loop())
from twisted.internet.task import react
from twisted.internet.defer import ensureDeferred, Deferred
    # print("finish")

def as_deferred(d):
    return Deferred.fromFuture(asyncio.ensure_future(d))

async def f():
    print("start")
    await asyncio.sleep(2)
    print("end")

def _main():
    # await some_deferred_fun()
    d : Deferred = as_deferred(f)
    d.callback(0)

def main():
    return react(_main())

if __name__ == '__main__':
    main()