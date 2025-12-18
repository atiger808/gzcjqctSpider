# -*- coding: utf-8 -*-
# @File   :get_list.py
# @Time   :2025/11/28 20:36
# @Author :admin


# -*- coding: utf-8 -*-
# @File   :baidu_paddle_ocr.py
# @Time   :2025/11/4 13:09
# @Author :admin


import datetime

from loguru import logger
import json
import os
import execjs
import urllib3
from pathlib import Path
import time
import threading
import random
import sys
import hashlib

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 或者只针对 requests
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


# 确保 output 目录存在
OUTPUT_DIR = get_app_dir() / Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


class GzcjqctSpider():
    def __init__(self, loginAccount='', password='', duction_sec=10, js_code_path='get_sign.js'):
        self.loginAccount = loginAccount or os.environ.get('LOGIN_ACCOUNT')
        self.password = password or os.environ.get('PASSWORD')
        self.userId = '57866'
        self.sessionStr = ''
        self.url_prefix = 'https://jxht.gzcjs.cn'
        self.api_addMember_url = 'https://mall.luokalux.cn/mysf/api/jys/addMember'
        self.api_addOrder_url = 'https://mall.luokalux.cn/mysf/api/jys/addOrder'
        self.js_code_path = js_code_path
        self.config_path = 'config.json'
        self.user_total_path = 'userTotal.json'
        self.user_total_list = []
        self.has_send_user_total_path = 'has_send_userTotal.json'
        self.has_send_user_list = []
        self.session = requests.session()
        self.re_login = True
        self.count = 0
        self.duction_sec = duction_sec
        self.config = {}
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://jxht.gzcjqct.com',
            'Pragma': 'no-cache',
            'Referer': 'https://jxht.gzcjqct.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'terminalType': '5',
        }
        self.session.headers.update(self.headers)
        self.session.verify = False
        self.init()

    def init(self):
        self.config = self.load_json(filepath=self.config_path)
        if self.config:
            logger.info(f'读取配置信息')
            self.api_addOrder_url = self.config.get('api_addOrder_url') or self.api_addOrder_url
            self.api_addMember_url = self.config.get('api_addMember_url') or self.api_addMember_url
            count = self.config.get(self.loginAccount, {}).get('count')
            value = self.config.get(self.loginAccount, {}).get('value', {})
            userId = value.get('userId')
            sessionStr = value.get('sessionStr') or self.sessionStr
            if not sessionStr:
                logger.info(f'{self.loginAccount} 初始化cookie失败')
                return
            self.count = count or 0
            self.userId = userId
            self.sessionStr = sessionStr
            self.session.headers.update(self.headers)
            self.session.verify = False
        else:
            logger.info(f'{self.loginAccount} 初始化cookie失败')

        if os.path.exists(self.user_total_path):
            lines = self.read_lines_json(self.user_total_path) or []
            self.user_total_list = [i.get('userId') for i in lines if i.get('userId')]
        if os.path.exists(self.has_send_user_total_path):
            lines = self.read_lines_json(self.has_send_user_total_path) or []
            self.has_send_user_list = [i.get('userId') for i in lines if i.get('userId')]

    def save_json(self, data, filepath='config.json'):
        filepath = OUTPUT_DIR / os.path.basename(filepath)
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)

    def load_json(self, filepath='config.json'):
        filepath = OUTPUT_DIR / os.path.basename(filepath)
        if not os.path.exists(filepath):
            logger.error(f'文件不存在 filepath: {filepath}')
            return {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = f.read()
                return json.loads(data)
            logger.info(f'读取成功 filepath: {filepath}')
        except Exception as e:
            logger.error(f'读取失败：{e} filepath: {filepath}')
            return {}

    def to_json(self, data, filepath='data.json'):
        filepath = OUTPUT_DIR / os.path.basename(filepath)
        if not isinstance(data, dict):
            logger.error(f'格式不对，需字典格式')
            return False

        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data) + '\n')
        return True

    def read_lines_json(self, filepath='data.json'):
        filepath = OUTPUT_DIR / os.path.basename(filepath)
        if not os.path.exists(filepath):
            logger.info(f'文件不存在 filepath: {filepath}')
            return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [json.loads(i) for i in f.readlines()]
                return lines
            logger.info(f'读取成功 filepath: {filepath}')
        except Exception as e:
            logger.error(f'读取失败：{e} filepath: {filepath}')
            return []

    def export_addMember(self, data):
        try:
            res = requests.post(self.api_addMember_url, json=data)
            logger.info(f'status_code: {res.status_code} res: {res.text}')
            if res.status_code == 200:
                return True
        except Exception as e:
            logger.error(f'{e}')
        return False

    def export_addOrder(self, data):
        try:
            res = requests.post(self.api_addOrder_url, json=data)
            logger.info(f'status_code: {res.status_code} res: {res.text}')
            if res.status_code == 200:
                return True
        except Exception as e:
            logger.error(f'{e}')
        return False

    def generate_chaptcha(self):
        try:
            url = f'{self.url_prefix}/apigateway/authn/authn/generateCaptcha'
            response = self.session.get(url,
                                        headers=self.headers)
            return response.json()
        except Exception as e:
            logger.info(f'error: {e}')
        return {}

    def get_sign(self, password):
        return hashlib.md5((f'47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU={password}').encode('utf-8')).hexdigest()
        # code_path = OUTPUT_DIR / os.path.basename(self.js_code_path)
        # with open(code_path) as f:
        #     return execjs.compile(f.read()).call('getSign', password)

    def update_headers_json_data(self, headers, json_data):
        if 'Authorization' in headers.keys():
            uri = ','.join(headers.get('Authorization').split(',')[2:])
            headers['Authorization'] = f'{self.userId},{self.sessionStr},{uri}'
        headers['UserId'] = self.userId
        headers['sessionStr'] = self.sessionStr
        json_data['userStr'] = self.userId
        json_data['sessionStr'] = self.sessionStr
        return headers, json_data

    def login(self):
        if not self.re_login:
            logger.info(f'{self.loginAccount} 在线')
            return self.session.cookies
        self.count += 1
        logger.info(f'第 {self.count}次 {self.loginAccount} 登录中...')

        encode_pass = self.get_sign(self.password)
        result = self.generate_chaptcha().get('value')
        captcha_code = result.get('code')
        captcha_id = result.get('id')

        json_data = {
            'loginAccount': f'{self.loginAccount}',
            'clientIp': '',
            'password': f'{encode_pass}',
            'captchaId': f'{captcha_id}',
            'captchaCode': f'{captcha_code}',
            'marketId': '28',
            'terminalType': '5',
            'loginType': 'X',
        }

        logger.info(f'json_data: {json_data}')
        try:
            url = f'{self.url_prefix}/apigateway/authn/authn/v1/backSimpleLogin'
            res = self.session.post(url, headers=self.headers,
                                    json=json_data)

            if res.status_code == 200:
                # 200 {"code":"base_register_028","message":"账号或密码错误","value":null}
                # 200 {"code":"base_authn_002","message":"图形验证码错误","value":null}
                # 200 {"code":"0","message":"成功","value":{"firmId":null,"userId":"57866","sessionStr":"6F4C7018AAAA8B556A96207EB87481E5","type":"X","userCode":"1368","userName":"茗易四方","nickName":"1368_admin","lnvitationCode":"1368","banTime":null}}

                data = res.json()
                if data.get('code') == '0':
                    logger.info(f'{self.loginAccount} 登录成功')
                    self.re_login = False
                    value = data.get('value', {})
                    self.userId = value.get('userId')
                    self.sessionStr = value.get('sessionStr')
                    logger.info(
                        f'loginAccount: {self.loginAccount} userId: {self.userId} sessionStr: {self.sessionStr}')
                    # self.insert_csrf()
                    cookies = self.session.cookies.get_dict()
                    first_login = self.config.get(self.loginAccount, {}).get('first_login') or str(
                        datetime.datetime.now())[:19]
                    login_time = self.config.get(self.loginAccount, {}).get('login_time')
                    self.config['api_addOrder_url'] = self.api_addOrder_url
                    self.config['api_addMember_url'] = self.api_addMember_url
                    self.config[self.loginAccount] = {
                        'loginAccount': self.loginAccount,
                        'value': value,
                        'count': self.count,
                        'cookies': cookies,
                        'first_login': first_login,
                        'last_login': login_time,
                        'login_time': str(datetime.datetime.now())[:19],
                    }
                    self.save_json(self.config, filepath=self.config_path)
                    return self.config
                else:
                    logger.info(f'{self.loginAccount} 登录失败 statuc_code: {res.status_code} text: {res.text}')
            else:
                logger.info(f'{self.loginAccount} 登录失败 statuc_code: {res.status_code} text: {res.text}')
        except Exception as e:
            logger.error(f'error: {e}')
        return {}

    def parsequeryUser(self, content=[]):
        new_content = []
        for i in content:
            item = {
                'userId': i.get('userId'),  # 会员代码
                'userCode': i.get('userCode'),  # 用户编码
                'userName': i.get('userName'),  # 用户名称
                'cellphone': i.get('cellphone'),  # 账户
                'phoneNum': i.get('phoneNum'),  # 联系方式
                'createTime': i.get('createTime'),  # 注册时间
            }
            new_content.append(item)
        return new_content

    def queryUserTransactionClient(self, cellphone=None, page=0, size=15, createTimeStart=None, createTimeEnd=None,
                                   direction='DESC'):

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en',
            'Authorization': f'{self.userId},{self.sessionStr},/base-admin-query/accountManagement/v1/queryUserTransactionClient,0',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://jxht.gzcjqct.com',
            'Pragma': 'no-cache',
            'Referer': 'https://jxht.gzcjqct.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'UserId': f'{self.userId}',
            'marketId': '0',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sessionStr': f'{self.sessionStr}',
            'terminalType': '5',
        }

        json_data = {
            'size': size,
            'page': page,
            'userId': None,
            'userCode': None,
            'userName': None,
            'cellphone': cellphone,
            'personOrOrgFlag': None,
            'l1code': None,
            'l2code': None,
            'l3code': None,
            'userStatus': None,
            'auditStatus': None,
            'signFlag': None,
            'change': '0',
            'createTimeStart': createTimeStart,
            'createTimeEnd': createTimeEnd,
            'tradeOpenTimeStart': None,
            'tradeOpenTimeEnd': None,
            'signTimeStart': None,
            'signTimeEnd': None,
            'sort': [
                {
                    'direction': f'{direction}',
                    'property': 'createTime',
                },
            ],
            'userStr': f'{self.userId}',
            'sessionStr': f'{self.sessionStr}',
        }

        try:
            url = f'{self.url_prefix}/apigateway/base-admin-query/accountManagement/v1/queryUserTransactionClient'
            response = self.session.post(
                url,
                headers=headers,
                json=json_data,
            )
            result = response.json()
            logger.info(
                f'status_code: {response.status_code} code: {result.get("code")} message: {result.get("message")}')
            if result.get('code') != '0':
                self.re_login = True
                logger.info(f'{self.loginAccount} 需要重新登录')
                self.login()
                headers, json_data = self.update_headers_json_data(headers, json_data)
                response = self.session.post(
                    url,
                    headers=headers,
                    json=json_data,
                )
                result = response.json()
                logger.info(
                    f'status_code: {response.status_code} code: {result.get("code")} message: {result.get("message")}')
        except Exception as e:
            logger.info(f'error: {e}')
            return None
        return result

    def findShopOrderSum(self, orderStatus=0):
        """
        :param orderStatus: 状态
        :return:
        """
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en',
            'Authorization': f'{self.userId},{self.sessionStr},/tea-shop-admin/shopOrderInfo/findShopOrderSum,3',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://jxht.gzcjqct.com',
            'Pragma': 'no-cache',
            'Referer': 'https://jxht.gzcjqct.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'UserId': f'{self.userId}',
            'marketId': '3',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sessionStr': f'{self.sessionStr}',
            'terminalType': '5',
        }

        json_data = {
            'userStr': f'{self.userId}',
            'sessionStr': f'{self.sessionStr}',
            'orderCode': None,
            'firmCode': None,
            'irreversiblePhone': None,
            'userName': None,
            'storeName': None,
            'className': None,
            'commodityName': None,
            'orderStatus': f'{orderStatus}',
            'payTimeStart': None,
            'payTimeEnd': None,
            'deliveryTimeStart': None,
            'deliveryTimeEnd': None,
            'l3Code': None,
        }
        try:
            url = f'{self.url_prefix}/apigateway/tea-shop-admin/shopOrderInfo/findShopOrderSum'
            response = self.session.post(
                url,
                headers=headers,
                json=json_data,
            )
            result = response.json()
            logger.info(
                f'status_code: {response.status_code} code: {result.get("code")} message: {result.get("message")}')
            if result.get('code') != '0':
                self.re_login = True
                logger.info(f'{self.loginAccount} 需要重新登录')
                self.login()
                headers, json_data = self.update_headers_json_data(headers, json_data)
                response = self.session.post(
                    url,
                    headers=headers,
                    json=json_data,
                )
                result = response.json()
                logger.info(
                    f'status_code: {response.status_code} code: {result.get("code")} message: {result.get("message")}')
        except Exception as e:
            logger.info(f'error: {e}')
            return None
        return result

    def findShopOrderInfo(self, orderCode=None, firmCode=None, irreversiblePhone=None,
                          userName=None, storeName=None, className=None, commodityName=None, l3Code=None,
                          orderStatus=None, page=0, size=15,
                          payTimeStart=None, payTimeEnd=None,
                          createTimeStart=None, createTimeEnd=None,
                          deliveryTimeStart=None, deliveryTimeEnd=None,
                          direction='DESC'):
        """

        :param orderStatus: 订单状态 0:待发货，1:待收货，2：已完成，9：退款中，3:退款完成
        :param page: 当前页
        :param size: 数量
        :param direction: 排序
        :return:
        """

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en',
            'Authorization': f'{self.userId},{self.sessionStr},/tea-shop-admin/shopOrderInfo/findShopOrderInfo,3',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://jxht.gzcjqct.com',
            'Pragma': 'no-cache',
            'Referer': 'https://jxht.gzcjqct.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'UserId': f'{self.userId}',
            'marketId': '3',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sessionStr': f'{self.sessionStr}',
            'terminalType': '5',
        }

        json_data = {
            'page': page,
            'size': size,
            'sort': [
                {
                    'direction': f'{direction}',
                    'property': 'payTime',
                },
            ],
            'userStr': f'{self.userId}',
            'sessionStr': f'{self.sessionStr}',
            'orderCode': orderCode,
            'firmCode': firmCode,
            'irreversiblePhone': irreversiblePhone,
            'userName': userName,
            'storeName': storeName,
            'className': className,
            'commodityName': commodityName,
            'l3Code': l3Code,
            'orderStatus': f'{orderStatus}' if orderStatus else orderStatus,
            'payTimeStart': payTimeStart or createTimeStart,
            'payTimeEnd': payTimeEnd or createTimeEnd,
            'deliveryTimeStart': deliveryTimeStart,
            'deliveryTimeEnd': deliveryTimeEnd,
        }

        try:
            url = f'{self.url_prefix}/apigateway/tea-shop-admin/shopOrderInfo/findShopOrderInfo'
            response = self.session.post(
                url,
                headers=headers,
                json=json_data,
            )
            result = response.json()
            logger.info(
                f'status_code: {response.status_code} code: {result.get("code")} message: {result.get("message")}')

            if result.get('code') != '0':
                self.re_login = True
                logger.info(f'{self.loginAccount} 需要重新登录')
                self.login()
                headers, json_data = self.update_headers_json_data(headers, json_data)
                response = self.session.post(
                    url,
                    headers=headers,
                    json=json_data,
                )
                result = response.json()
                logger.info(
                    f'status_code: {response.status_code} code: {result.get("code")} message: {result.get("message")}')
        except Exception as e:
            logger.info(f'error: {e}')
            return None
        return result

    def getFirmFlowH(self, page=0, size=15, createTimeStart=None, createTimeEnd=None,
                     direction='DESC'):
        """
        :param page: 当前页
        :param size: 数量
        :param direction: 排序
        :return:
        """

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en',
            'Authorization': f'{self.userId},{self.sessionStr},/tea-sec-admin-querybak/quotation/getFirmFlowH,32',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://jxht.gzcjqct.com',
            'Pragma': 'no-cache',
            'Referer': 'https://jxht.gzcjqct.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'UserId': f'{self.userId}',
            'marketId': '32',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sessionStr': f'{self.sessionStr}',
            'terminalType': '5',
        }

        json_data = {
            'page': page,
            'size': size,
            'userStr': f'{self.userId}',
            'sessionStr': f'{self.sessionStr}'
        }

        try:
            url = f'{self.url_prefix}/apigateway/tea-sec-admin-querybak/quotation/getFirmFlowH'
            response = self.session.post(
                url,
                headers=headers,
                json=json_data,
            )
            result = response.json()
            logger.info(
                f'status_code: {response.status_code} code: {result.get("code")} message: {result.get("message")}')
            if result.get('code') != '0':
                self.re_login = True
                logger.info(f'{self.loginAccount} 需要重新登录')
                self.login()
                headers, json_data = self.update_headers_json_data(headers, json_data)
                response = self.session.post(
                    url,
                    headers=headers,
                    json=json_data,
                )
                result = response.json()
                logger.info(
                    f'status_code: {response.status_code} code: {result.get("code")} message: {result.get("message")}')
        except Exception as e:
            logger.info(f'error: {e}')
            return None
        return result

    def crawlUser(self):
        for page in range(0, 21):
            logger.info(f'page: {page}')
            result = self.queryUserTransactionClient(page=page)
            if result is not None:
                content = result.get('value', {}).get('content', [])
                for item in content:
                    is_success = self.to_json(item, filepath=self.user_total_path)
                    if is_success:
                        logger.info('保存成功')
                    else:
                        logger.error('保存失败')
            else:
                logger.info(f'result is None')
                break

    def loop_member(self):
        logger.info(f'Member start ...')
        while True:
            logger.info(f'{len(self.has_send_user_list)}/{len(self.user_total_list)}')
            result = self.queryUserTransactionClient()
            if result is not None:
                self.save_json(result, 'queryUserTransactionClient.json')
                content = result.get('value', {}).get('content', [])

                new_content = []
                for item in content:
                    userId = item.get('userId')
                    if userId:
                        if userId not in self.user_total_list:
                            self.to_json(item, filepath=self.user_total_path)
                            self.user_total_list.append(userId)
                        if userId not in self.has_send_user_list:
                            new_content.append(item)
                if new_content:
                    content = self.parsequeryUser(new_content)
                    data = {
                        'content': content
                    }
                    is_success = self.export_addMember(data)
                    if is_success:
                        logger.info(f'发送成功 member')
                        for item in new_content:
                            userId = item.get('userId')
                            if userId not in self.has_send_user_list:
                                self.to_json(item, filepath=self.has_send_user_total_path)
                                self.has_send_user_list.append(userId)
                    else:
                        logger.error(f'发送失败 member')

            self.duction_sec = random.randint(3, 10)
            time.sleep(self.duction_sec)

    def loop_order(self):
        logger.info(f'Order start ...')
        while True:
            result = d.findShopOrderInfo()
            if result is not None:
                self.save_json(result, 'findShopOrderInfo.json')
                content = result.get('value', {}).get('content', [])
                data = {
                    "content": content  # 是列表形式
                }

                is_success = self.export_addOrder(data)
                if is_success:
                    logger.info(f'发送成功 order')
                else:
                    logger.error(f'发送失败 order')

            self.duction_sec = random.randint(3, 10)
            time.sleep(self.duction_sec)

    def test(self):
        pass

    def run(self):
        t = threading.Thread(target=self.loop_member)
        t.start()
        self.loop_order()


if __name__ == '__main__':
    d = GzcjqctSpider()
    d.run()
