# # !/usr/bin/env Python3
# # -*- coding: utf-8 -*-
# # @Author   : joe lin
# # @FILE     : tasks.py
# # @Time     : 2021-02-20 0:27
# # @Software : od_gateway
# # @Email    : jackwmj12@163.com
# # @Github   :
# # @Desc     :
# #            ┏┓      ┏┓
# #          ┏┛┻━━━┛┻┓
# #          ┃      ━      ┃
# #          ┃  ┳┛  ┗┳  ┃
# #          ┃              ┃
# #          ┃      ┻      ┃
# #          ┗━┓      ┏━┛
# #              ┃      ┃
# #              ┃      ┗━━━┓
# #              ┃              ┣┓
# #              ┃              ┏┛
# #              ┗┓┓┏━┳┓┏┛
# #                ┃┫┫  ┃┫┫
# #                ┗┻┛  ┗┻┛
# #                 神兽保佑，代码无BUG!
# #
# #
# #
# from twisted.internet import reactor
# from txcelery.defer import DeferrableTask
#
# from txfirefly.exts.ffcelery import create_celery
#
# celery_app = create_celery(config["testing"])
#
# # demo
#
# @DeferrableTask
# @celery_app.task
# def substract(x,y):
#     '''
#
#     :param x:
#     :param y:
#     :return:
#     '''
#
# @DeferrableTask
# @celery_app.task
# def send_email(to,subject,template,**kwargs):
#     '''
#     '''
#
# def main(x,y):
#     print("执行任务，等待结果:")
#
# if __name__ == '__main__':
#
#
#     reactor.callLater(0.1, main, 3, 2)
#     # reactor.callLater(0.1, main, 3, 2)
#     # reactor.callLater(0.1, main, 3, 2)
#     # reactor.callLater(0.1, main, 3, 2)
#     # reactor.callLater(0.1, main, 3, 2)
#     # main.addCallback(print)
#     # main.addCallback(print)
#     # substract.delay(3, 2).addCallback(print)
#     # substract.delay(3, 2).addCallback(print)
#     # reactor.run()
#     # task.react(substract, (3, 2))
#     reactor.run()
# #
