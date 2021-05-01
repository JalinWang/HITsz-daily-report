#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import random
import logging
import requests
from lxml import etree
from datetime import datetime
from argparse import ArgumentParser
from requests.utils import dict_from_cookiejar

log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)


class ReportException(Exception):
    """上报异常错误信息"""

    class LoginError(Exception):
        """登录失败"""

    class SubmitError(Exception):
        """上报失败"""


class Report(object):
    def __init__(self, args):
        """参数初始化"""

        if not args.username or not args.password:
            raise ReportException("请先设置 Actions Secrets！")

        self.session = requests.session()
        self.username = args.username
        self.password = args.password
        self.graduating = '1' if args.graduating else '0'
        logging.info(f"{'' if args.graduating else '非'}毕业班学生，微信提醒{'开启' if args.sckey else '关闭'}。")

        self.urls = {
            'csh': 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/csh',
            'get': 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/getYqxx',
            'sso': 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/shsj/common',
            'uid': 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xsHome/getGrxx',
            'save': 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/saveYqxx',
            'check': 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/getYqxxList',
            'login': 'https://sso.hitsz.edu.cn:7002/cas/login;jsessionid={}?service='
                     'http://xgsm.hitsz.edu.cn/zhxy-xgzs/common/casLogin?params=L3hnX21vYmlsZS94c0hvbWU=',
        }

        self.keys = [
            'brfsgktt', 'brjyyymc', 'brsfjy', 'brzdjlbz', 'brzdjlm', 'brzgtw', 'dqszd', 'dqszdqu',
            'dqszdsheng', 'dqszdshi', 'dqztbz', 'dqztm', 'gnxxdz', 'gpsxx', 'hwcs', 'hwgj', 'hwxxdz',
            'qtbgsx', 'sffwwhhb', 'sfjcqthbwhry', 'sfjcqthbwhrybz', 'sfjdwhhbry', 'sftjwhjhb', 'stzkm',
            'sftzrychbwhhl', 'tccx', 'tchbcc', 'tcjcms', 'tcjtfs', 'tcjtfsbz', 'tcyhbwhrysfjc', 'tczwh',
        ]

        self.proxies = {
          "http": "socks5h://127.0.0.1:1080",
          "https": "socks5h://127.0.0.1:1080"
        }

    @staticmethod
    def new_session():
        sess = requests.session()
        sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                                           '(KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'})
        return sess

    def student_login(self):
        """登录统一认证系统"""

        self.session = self.new_session()
        url_sso = self.urls['sso']
        response = self.session.get(url_sso, proxies=self.proxies)
        jsessionid = dict_from_cookiejar(response.cookies)['JSESSIONID']
        url_login = self.urls['login'].format(jsessionid)
        logging.debug(f'GET {url_sso} {response.status_code}')

        html = etree.HTML(response.text)
        lt = html.xpath('//input[@name="lt"]/@value')[0]
        execution = html.xpath('//input[@name="execution"]/@value')[0]
        event_id = html.xpath('//input[@name="_eventId"]/@value')[0]

        params = {
            'lt': lt,
            'execution': execution,
            '_eventId': event_id,
            'username': self.username,
            'password': self.password,
        }

        # 禁用跳转，用于处理登录失败的问题
        response = self.session.post(url_login, params=params, allow_redirects=False, proxies=self.proxies)
        logging.debug(f'POST {url_login} {response.status_code}')

        if response.status_code == 200:
            err = etree.HTML(response.text).xpath('//div[@id="msg"]/text()')[0]
            raise ReportException.LoginError(f"{err}。")
        elif response.status_code != 302:
            raise ReportException.LoginError("其他错误。")

        # 登录成功，继续跳转，更新 cookie
        next_url = response.next.url
        response = self.session.get(next_url, proxies=self.proxies)
        logging.debug(f'GET {next_url} {response.status_code}')

        logging.info(f"认证系统登录成功。")

    def student_report_check(self):
        """获取当日上报信息"""

        # 查询今天是否已生成上报信息，并获得 ID
        url_csh = self.urls['csh']
        response = self.session.post(url_csh, proxies=self.proxies)
        result = response.json()
        logging.debug(f'POST {url_csh} {response.status_code}')

        if not result.get('isSuccess'):
            logging.warning("新增每日上报信息失败！")

            url_check = self.urls['check']
            response = self.session.post(url_check, proxies=self.proxies)
            today_report = response.json()['module']['data'][0]
            logging.debug(f'POST {url_check} {response.status_code}')

            if today_report['zt'] == '00':
                logging.warning("上报信息已存在，尚未提交。")
            elif today_report['zt'] == '01':
                raise ReportException.SubmitError("上报信息已提交，待审核。")
            elif today_report['zt'] == '02':
                raise ReportException.SubmitError("上报信息已审核，无需重复提交。")
            else:
                raise ReportException.SubmitError(f"上报失败，zt：{today_report['zt']}")

        return result['module']

    def student_report_submit(self, module):
        """上报当日疫情信息"""

        # 获取每日上报信息的模板
        url_msg = self.urls['get']
        params = {'info': json.dumps({'id': module})}
        response = self.session.post(url_msg, params=params, proxies=self.proxies)
        data_orig = response.json()['module']['data'][0]
        logging.debug(f'POST {url_msg} {response.status_code}')

        temperature = format(random.uniform(361, 368) / 10, '.1f')
        model = {key: data_orig[key] for key in self.keys}
        model |= {'id': module, 'brzgtw': temperature, 'sffwwhhb': self.graduating}
        report_info = {'info': json.dumps({'model': model})}
        logging.info(f"生成上报信息成功。今日体温：{temperature}℃")

        url_save = self.urls['save']
        response = self.session.post(url_save, params=report_info, proxies=self.proxies)
        logging.debug(f'POST {url_save} {response.status_code}')

        if not response.json().get('isSuccess'):
            raise ReportException.SubmitError("上报信息提交失败。")

        logging.info("上报信息提交成功。")


def main(args):
    def wait_a_minute(prompt, extra_minutes=0):
        wait = 60 * extra_minutes + random.randint(0, 60)
        logging.warning(prompt.format(wait))
        time.sleep(wait)

    r = Report(args)

    try:
        r.student_login()
    except ReportException.LoginError:
        wait_a_minute("登录失败，等待{}秒后重试。", 1)
        r.student_login()

    module_id = r.student_report_check()

    try:
        r.student_report_submit(module_id)
    except ReportException.SubmitError:
        wait_a_minute("提交失败，等待{}秒后重试。", 1)
        r.student_report_submit(module_id)


if __name__ == '__main__':
    parser = ArgumentParser(description='HITsz疫情上报')
    parser.add_argument('username', help='登录用户名')
    parser.add_argument('password', help='登录密码')
    parser.add_argument('-g', '--graduating', help='是否毕业班', action="store_true")
    parser.add_argument('-k', '--sckey', help='Server酱的sckey')
    arguments = parser.parse_args()

    try:
        main(arguments)
    except ReportException.LoginError as e:
        report_msg = f"登陆失败！原因：{e}"
        logging.error(report_msg)
        raise ReportException(report_msg)
    except ReportException.SubmitError as e:
        report_msg = f"上报失败！原因：{e}"
        logging.error(report_msg)
        raise ReportException(report_msg)
    except Exception as e:
        report_msg = f"上报失败！其他错误：{e}"
        logging.critical(report_msg)
        raise ReportException(report_msg)
    else:
        report_msg = f"今日疫情状态上报成功。"
        logging.warning(report_msg)
    finally:
        if arguments.sckey:
            current = datetime.today().strftime('%Y-%m-%d_%H:%M:%S')
            requests.get(f"https://sc.ftqq.com/{arguments.sckey}.send?text={report_msg}{current}")
            logging.info("微信提醒消息已发送。")
