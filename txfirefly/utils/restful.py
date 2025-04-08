# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : restful.py
# @Time     : 2021-07-09 17:16
# @Software : admin_app
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

ok = 200
unautherror = 401
paramserror = 400
servererror = 500

def serialize_alchemy_encoder(obj):
    """
    处理序列化中的时间和小数
    :param obj:
    :return:
    """
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d")
    elif isinstance(obj, datetime.time):
        return obj.strftime("%H:%M:%S")
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

def restful_result(code,message,data):
    return json.dumps(
        {
            "code": code,
            "message": message,
            "data": data
        },
        ensure_ascii=False,
        allow_nan=False,
        indent=None,
        separators=(",", ":"),
        default=serialize_alchemy_encoder
    ).encode("utf-8")

def success(message="",data=None):
    return restful_result(code=ok,message=message,data=data)

def unauth_error(message=""):
    return restful_result(code=unautherror,message=message,data=None)

def params_error(message=""):
    return restful_result(code=paramserror,message=message,data=None)

def server_error(message=""):
    return restful_result(code=servererror,message=message or '服务器内部错误',data=None)