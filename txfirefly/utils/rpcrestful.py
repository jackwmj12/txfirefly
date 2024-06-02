# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : rpcrestful.py
# @Time     : 2021-02-20 0:03
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
import enum
from typing import List, Union, Optional, Dict, Any

from twisted.spread import pb


class RpcRestfulCodeEnum(enum.IntEnum):
    SUCCESS = 200
    FAILED = 400
    DISCONNECT = 500


class RpcRestful():
    '''
    :param

    '''

    def __init__(
        self,
        code: RpcRestfulCodeEnum = RpcRestfulCodeEnum.SUCCESS,
        message: Optional[str] = None,
        payload: Optional[Any] = None,
    ):
        '''

        :param method:      RPC方法
        :param data:        需要发送的数据
        :param payload:     回复携带的参数
        '''
        self.code= int(code)
        self.message= message
        self.payload= payload

    def to_dict(self):
        return {
            "code": int(self.code),
            "message": self.message,
            "payload": self.payload
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


if __name__ == '__main__':
    from loguru import logger
    a = RpcRestful(
        code=RpcRestfulCodeEnum.SUCCESS,
        message="操作成功"
    )
    logger.debug(a)
    logger.debug(type(a))
    # logger.debug(a.message)