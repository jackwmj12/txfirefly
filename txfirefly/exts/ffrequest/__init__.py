# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : __init__.py
# @Time     : 2021-02-20 0:31
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
import datetime
import decimal
import json
from urllib.parse import urlencode

import treq
from requests.auth import _basic_auth_str
from twisted.internet import reactor
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from zope.interface import implementer
from twisted.internet.defer import succeed
from twisted.web.iweb import IBodyProducer
from twisted.internet.ssl import ClientContextFactory

from txrpc.utils import logger


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o,datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        super(JsonEncoder, self).default(o)

class WebClientContextFactory(ClientContextFactory):
    '''
    提供https支持
    '''
    def getContext(self, hostname, port):
        return ClientContextFactory.getContext(self)

@implementer(IBodyProducer)
class BytesProducer(object):
    '''
    生成http请求的body部分
    '''
    def __init__(self, body):
        self.body = body if body != None else b""
        self.length = len(self.body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass

class Request(object):
    '''
        twisted异步HTTP请求
    '''

    @classmethod
    def get(cls,url=None,**kwargs):
        '''
        发起get请求
        :param kwargs:
            url 路径
            params 参数内容
            header 头
            body 主体
        :return:
        '''
        assert url != None,"url 不能为空"

        return treq.get(
            url.encode(),
            **kwargs
        ).addCallbacks(cls._getResult, cls._getError)

    @classmethod
    def post(cls,url=None,data=None, **kwargs):
        '''
		发起post请求
		:param kwargs:
			url 路径
			params 参数内容
				（该参数会随着url一起明文发送）
			header 头
				demo:[{
					'Content-Type': ['application/json', "charset=UTF-8"]
				}]
				demo:[{
					'Content-Type': ['application/x-www-form-urlencoded']
				}]
			form 主体
				（该参数会在body处发送）
		:return:
		'''

        assert url != None,"url 不能为空"

        auth = kwargs.get('auth', None)
        if auth:
            kwargs["auth"] = (auth["username"], auth["password"])

        return treq.post(
            url.encode(),
            data,
            **kwargs
        ).addCallbacks(cls._getResult, cls._getError)

    @classmethod
    def _getBody(cls,response):
        '''
        :param response:
        :param code:
        :return:
        '''
        # defer.returnValue(response.decode())
        # print(response)
        # return response.decode()
        return json.loads(response.decode())

    @classmethod
    def _getResult(cls,response):
        '''

        :param response:
        :return:
        '''
        # print('Response version:', response.version)
        # print('Response code:', response.code)
        # print('Response phrase:', response.phrase)
        # print('Response headers:')
        # logger.msg(pformat(list(response.headers.getAllRawHeaders())))
        # d = readBody(response)
        # d.addCallback(cls._getBody)
        # return d
        # logger.debug(response)
        # print(response)
        return readBody(response)\
            .addCallback(cls._getBody).addErrback(logger.error)

    @classmethod
    def _getError(cls,err):
        '''
        :param err:
        :return:
        '''
        # print(err)
        raise Exception(err)

# class Request(object):
#     '''
#         twisted异步HTTP请求
#     '''
#
#     @classmethod
#     def get(cls,**kwargs):
#         '''
#         发起get请求
#         :param kwargs:
#             url 路径
#             params 参数内容
#             header 头
#             body 主体
#         :return:
#         '''
#         agent = Agent(reactor,WebClientContextFactory())
#         url = kwargs.get('url',None)
#         params = urlencode(kwargs.get('params',None))
#         body = kwargs.get('form', None)
#         auth = kwargs.get('auth', None)
#
#         header = kwargs.get('header', {
#             'Content-Type': ['application/x-www-form-urlencoded']
#         })
#
#         if auth:
#             header['Authorization'] = [_basic_auth_str(auth["username"], auth["password"])]
#
#         if params:
#             url = "%s?%s" % (url, params)
#
#         if body:
#             body = urlencode(body).encode()
#
#         return agent.request(
#             b'GET',
#             url.encode(),
#             Headers(header),
#             BytesProducer(body)
#         ).addCallbacks(cls._getResult, cls._getError)
#
#     @classmethod
#     def post(cls,**kwargs):
#         '''
#         发起post请求
#         :param kwargs:
#             url 路径
#             params 参数内容
#                 （该参数会随着url一起明文发送）
#             header 头
#                 demo:[{
#                     'Content-Type': ['application/json', "charset=UTF-8"]
#                 }]
#                 demo:[{
#                     'Content-Type': ['application/x-www-form-urlencoded']
#                 }]
#             form 主体
#                 （该参数会在body处发送）
#         :return:
#         '''
#
#         agent = Agent(reactor,WebClientContextFactory())
#         url = kwargs.get('url', None)
#         params = kwargs.get('params', None)
#         body = kwargs.get('form', None)
#         auth = kwargs.get('auth',None)
#
#         header = kwargs.get('header', {
#             'Content-Type': ['application/x-www-form-urlencoded']
#         })
#
#         if auth:
#             header['Authorization'] = [_basic_auth_str(auth["username"], auth["password"])]
#
#         if params:
#             params = urlencode(params)
#             url = "%s?%s" % (url, params)
#
#         if body:
#             body = urlencode(body).encode()
#
#         return agent.request(
#             b'POST',
#             url.encode(),
#             Headers(header),
#             BytesProducer(body),
#         ).addCallbacks(cls._getResult, cls._getError)
#
#     @classmethod
#     def _getBody(cls,response):
#         '''
#         :param response:
#         :param code:
#         :return:
#         '''
#         # defer.returnValue(response.decode())
#         return json.loads(response.decode())
#
#     @classmethod
#     def _getResult(cls,response):
#         '''
#
#         :param response:
#         :return:
#         '''
#         # print('Response version:', response.version)
#         # print('Response code:', response.code)
#         # print('Response phrase:', response.phrase)
#         # print('Response headers:')
#         # logger.msg(pformat(list(response.headers.getAllRawHeaders())))
#         # d = readBody(response)
#         # d.addCallback(cls._getBody)
#         # return d
#         return readBody(response)\
#             .addCallback(cls._getBody).addErrback(DefferedErrorHandle)
#
#     @classmethod
#     def _getError(cls,err):
#         '''
#         :param err:
#         :return:
#         '''
#         print(err)
#         raise Exception(err)