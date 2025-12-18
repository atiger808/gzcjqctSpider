# -*- coding: utf-8 -*-
# @File   :app.py
# @Time   :2025/11/30 13:15
# @Author :admin

from flask import Flask, request, jsonify
import time
import argparse
from functools import wraps
from loguru import logger
from gzcjs_spider import GzcjqctSpider
import sys
import datetime
import logging

# logging.basicConfig(format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s',
#                     level=logging.INFO,
#                     filename='log.log',
#                     filemode='a'
#                     )

import os

app = Flask(__name__)


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_salt = request.headers.get('salt')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]
        SECRET_KEY = os.environ.get('SECRET_KEY')
        if not SECRET_KEY:
            raise EnvironmentError("Missing required environment variable: SECRET_KEY")
        # 模拟合法 token（实际应从数据库或 Redis 中查询）
        VALID_TOKENS = {SECRET_KEY}
        if token not in VALID_TOKENS:
            return jsonify({"error": "Invalid token"}), 403


        return f(*args, **kwargs)

    return decorated_function


@app.route('/query/member', methods=['POST'])
@require_auth
def get_member():
    # 获取 IP（支持代理）
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0]
    else:
        ip = request.remote_addr
    # 获取 Headers
    headers = dict(request.headers)
    logger.info(f'ip: {ip} headers: {headers}')

    data = request.get_json()
    logger.info(f'data: {data}')
    page = data.get('page') or 0
    size = data.get('size') or 15
    cellphone = data.get('cellphone')
    createTimeStart = data.get('createTimeStart')
    createTimeEnd = data.get('createTimeEnd')
    direction = data.get('direction') or 'DESC'

    if not str(page).isdigit() or not str(size).isdigit():
        return jsonify({"msg": "page或size 参数不合法"}), 400
    elif createTimeStart and not str(createTimeStart).isdigit():
        return jsonify({"msg": "createTimeStart 参数不合法"}), 400
    elif createTimeEnd and not str(createTimeEnd).isdigit():
        return jsonify({"msg": "createTimeEnd 参数不合法"}), 400
    elif direction and direction not in ['DESC', '-DESC']:
        return jsonify({"msg": "DESC 参数不合法"}), 400

    gz = GzcjqctSpider()
    result = gz.queryUserTransactionClient(cellphone=cellphone, page=page, size=size, createTimeStart=createTimeStart,
                                           createTimeEnd=createTimeEnd, direction=direction)
    logger.info(f'result code: {result.get("code")}')
    if result is not None:
        content = result.get('value', {}).get('content', [])
        content = gz.parsequeryUser(content)
    else:
        content = []
    return jsonify({"msg": "success", "content": content}), 200


@app.route('/query/order', methods=['POST'])
@require_auth
def get_order():
    # 获取 IP（支持代理）
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0]
    else:
        ip = request.remote_addr
    # 获取 Headers
    headers = dict(request.headers)
    logger.info(f'ip: {ip} headers: {headers}')

    data = request.get_json()
    logger.info(f'data: {data}')
    page = data.get('page') or 0
    size = data.get('size') or 15
    orderCode = data.get('orderCode')  # 订单编号
    firmCode = data.get('firmCode')  # 用户编码
    irreversiblePhone = data.get('irreversiblePhone')  # 账户

    payTimeStart = data.get('payTimeStart')  # 支付开始时间
    payTimeEnd = data.get('payTimeEnd')  # 支付结束时间

    deliveryTimeStart = data.get('deliveryTimeStart')
    deliveryTimeEnd = data.get('deliveryTimeEnd')

    direction = data.get('direction') or 'DESC'
    orderStatus = data.get('orderStatus')

    if not str(page).isdigit() or not str(size).isdigit():
        return jsonify({"msg": "page或size 参数不合法"}), 400
    elif payTimeStart and not str(payTimeStart).isdigit():
        return jsonify({"msg": "payTimeStart 参数不合法"}), 400
    elif payTimeEnd and not str(payTimeEnd).isdigit():
        return jsonify({"msg": "payTimeEnd 参数不合法"}), 400
    elif deliveryTimeStart and not str(deliveryTimeStart).isdigit():
        return jsonify({"msg": "deliveryTimeStart 参数不合法"}), 400
    elif deliveryTimeEnd and not str(deliveryTimeEnd).isdigit():
        return jsonify({"msg": "deliveryTimeEnd 参数不合法"}), 400
    elif orderStatus not in [None, "", 0, 1, 2, 3, 9]:
        return jsonify({"msg": "orderStatus 参数不合法"}), 400
    elif direction and direction not in ['DESC', '-DESC']:
        return jsonify({"msg": "DESC 参数不合法"}), 400

    gz = GzcjqctSpider()
    result = gz.findShopOrderInfo(orderCode=orderCode, firmCode=firmCode, irreversiblePhone=irreversiblePhone,
                                  orderStatus=orderStatus, page=page, size=size,
                                  payTimeStart=payTimeStart, payTimeEnd=payTimeEnd,
                                  deliveryTimeStart=deliveryTimeStart, deliveryTimeEnd=deliveryTimeEnd,
                                  direction=direction)
    logger.info(f'result: {result.get("code")}')
    if result is not None:
        content = result.get('value', {}).get('content', [])
    else:
        content = []
    return jsonify({"msg": "success", "content": content}), 200


@app.route('/query/firm/flow', methods=['POST'])
@require_auth
def get_firm_flow():
    # 获取 IP（支持代理）
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0]
    else:
        ip = request.remote_addr
    # 获取 Headers
    headers = dict(request.headers)
    logger.info(f'ip: {ip} headers: {headers}')

    data = request.get_json()
    logger.info(f'data: {data}')
    page = data.get('page') or 0
    size = data.get('size') or 15

    if not str(page).isdigit() or not str(size).isdigit():
        return jsonify({"msg": "page或size 参数不合法"}), 400

    gz = GzcjqctSpider()
    result = gz.getFirmFlowH(page=page, size=size)
    logger.info(f'result: {result.get("code")}')
    if result is not None:
        content = result.get('value', {}).get('content', [])
    else:
        content = []
    return jsonify({"msg": "success", "content": content}), 200


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run Flask API server")
    parser.add_argument('-H', '--host', type=str, default='0.0.0.0', help='Host to bind (default: 0.0.0.0)')
    parser.add_argument('-P', '--port', type=int, default=5000, help='Port to listen on (default: 5000)')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode (default: False)')

    # 如果被打包（PyInstaller），sys.frozen 为 True，此时不解析参数（可选）
    # 如果你希望打包后仍支持命令行参数，请保留解析逻辑（推荐）
    args = parser.parse_args()
    print(f'Flask API server started at {args.host}:{args.port} debug:{args.debug}...')
    app.run(host=args.host, port=args.port, debug=args.debug)
