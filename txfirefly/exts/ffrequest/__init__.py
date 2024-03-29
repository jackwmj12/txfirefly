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
import os

import treq

if os.name == "nt":
    try:
        import certifi
        os.environ["SSL_CERT_FILE"] = certifi.where()
    except Exception as e:
        print(e)

import datetime
import decimal
import json
from urllib.parse import urlencode
from requests.auth import _basic_auth_str
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from zope.interface import implementer
from twisted.internet.defer import succeed
from twisted.web.iweb import IBodyProducer
from twisted.internet.ssl import ClientContextFactory
from loguru import logger


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

class FFrequest(object):
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
    def post(cls, url=None, data=None, headers=None, **kwargs):
        '''
		发起post请求
		:param kwargs:
			url 路径
			data 参数内容
			headers 头
				demo: {b'Content-Type': [b'application/json']}
				demo:{b'Content-Type': [b'application/x-www-form-urlencoded']}
		:return:
		'''

        if headers is None:
            headers = {b'Content-Type': [b'application/x-www-form-urlencoded']}

        assert url != None,"url 不能为空"

        auth = kwargs.get('auth', None)
        if auth:
            kwargs["auth"] = (auth["username"], auth["password"])

        return treq.post(
            url,
            data,
            headers=headers,
            **kwargs
        ).addCallbacks(cls._getResult, cls._getError)

    @classmethod
    def _getBody(cls,response):
        '''
        :param response:
        :param code:
        :return:
        '''
        # logger.debug(response)
        # defer.returnValue(response.decode())
        # print(response)
        # return response.decode()
        response = response.decode()
        try:
            return json.loads(response)
        except Exception as e:
            return response

    @classmethod
    def _getResult(cls,response):
        '''

        :param response:
        :return:
        '''
        # logger.debug(f'Response version : {response.version}')
        # logger.debug(f'Response code : {response.code}')
        # logger.debug(f'Response phrase : {response.phrase}')
        # logger.debug(f'Response headers : {response.headers}')
        # logger.info(pformat(list(response.headers.getAllRawHeaders())))
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
    