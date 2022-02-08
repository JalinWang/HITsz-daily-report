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

    class ReportExistError(Exception):
        """已经上报"""


class Report(object):
    def __init__(self, args, proxy_on=False, ports=None):
        """参数初始化"""

        if not args.username or not args.password:
            raise ReportException("请先设置 Actions Secrets！")

        self.proxy_on = proxy_on
        self.proxy_ports = [] if ports is None else ports

        self.username = args.username
        self.password = args.password
        self.graduating = '1' if args.graduating else '0'

        logging.info(f"微信提醒{'开启' if args.sckey else '关闭'}，"
                     f"VPN {'开启' if args.proxy else '关闭'}。")

        self.proxies = self.config_proxies()
        self.session = requests.session()


        self.urls = {
            'Token':'https://student.hitsz.edu.cn/xg_common/getToken',
            'get': 'https://student.hitsz.edu.cn/xg_common/getDmx1',
            # 'sso': 'https://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/shsj/common',
            # 'uid': 'https://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xsHome/getGrxx',
            'check': 'https://student.hitsz.edu.cn/xg_mobile/xsMrsbNew/checkTodayData',

            'save': 'https://student.hitsz.edu.cn/xg_mobile/xsMrsbNew/save',
            'loc_update': 'https://webapi.amap.com/maps/ipLocation?key=be8762efdce0ddfbb9e2165a7cc776bd&callback=jsonp_123456_',
            'loc_convert':'https://restapi.amap.com/v3/geocode/regeo?key=be8762efdce0ddfbb9e2165a7cc776bd&s=rsv3&language=zh_cn&location={},{}',
            'login': 'https://sso.hitsz.edu.cn:7002/cas/login?service=https%3A%2F%2Fstudent.hitsz.edu.cn%2Fcommon%2FcasLogin%3Fparams%3DL3hnX21vYmlsZS94c01yc2JOZXcvaW5kZXg%3D',
        }

        self.keys = [
            'brfsgktt', 'brjyyymc', 'brsfjy', 'brzdjlbz', 'brzdjlm', 'brzgtw', 'dqszd', 'dqszdqu',
            'dqszdsheng', 'dqszdshi', 'dqztbz', 'dqztm', 'gnxxdz', 'gpsxx', 'hwcs', 'hwgj', 'hwxxdz',
            'qtbgsx', 'sffwwhhb', 'sfjcqthbwhry', 'sfjcqthbwhrybz', 'sfjdwhhbry', 'sftjwhjhb', 'stzkm',
            'sftzrychbwhhl', 'tccx', 'tchbcc', 'tcjcms', 'tcjtfs', 'tcjtfsbz', 'tcyhbwhrysfjc', 'tczwh',
            # 'gpswzxx'
        ]

    def start_new_session(self):
        sess = requests.session()
        sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                                           '(KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'})
        self.session = sess

    def config_proxies(self, port: int = None):
        if port and self.proxy_on:
            socks5 = f'socks5h://127.0.0.1:{port}'
            proxies = {'http': socks5, 'https': socks5}
            return proxies
        else:
            return None

    def switch_proxies(self, func):
        for p in self.proxy_ports:
            try:
                self.config_proxies(p)
                func()
            except Exception as error:
                logging.debug(error)
            else:
                logging.info(f"代理端口设定为：{p}")
                break
        else:
            raise ReportException.LoginError("无可用代理。")

    def student_login(self):
        """登录统一认证系统"""

        self.start_new_session()
        url_login = self.urls['login']
        response = self.session.get(url_login, proxies=self.proxies)
        # jsessionid = dict_from_cookiejar(response.cookies)['JSESSIONID']
        # url_login = self.urls['login'].format(jsessionid)
        # logging.debug(f'GET {url_sso} {response.status_code}')

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
        url_csh = self.urls['check']
        response = self.session.post(url_csh, proxies=self.proxies)
        result = response.json()
        if not result.get('isSuccess'):
            logging.warning("新增每日上报信息失败！")
        elif result.get('module') == '0':
            logging.info('上报未提交')
        elif result.get('module') == '1':
            ReportException.ReportExistError("上报信息已审核，无需重复提交。")
        else:
            raise ReportException.SubmitError(f"上报失败，module:{result.get('mudule')}")


    # def student_report_submit(self, module):
    #     """上报当日疫情信息"""

    #     # 获取每日上报信息的模板
    #     url_msg = self.urls['get']
    #     params = {'info': json.dumps({'id': module})}
    #     response = self.session.post(url_msg, params=params, proxies=self.proxies)

    #     data_orig = response.json()['module']['data'][0]
    #     logging.debug(f'POST {url_msg} {response.status_code}')

    #     temperature = format(random.uniform(361, 368) / 10, '.1f')
    #     model = {key: data_orig[key] for key in self.keys}
    #     model |= {'id': module, 'brzgtw': temperature, 'sffwwhhb': self.graduating}
    #     model |= {'gpswzxx': "广东省深圳市南山区桃源街道平山二路大园工业区北区"}
    #     model |= {'stzkm': '01'}  # 其他需要报告的事项
    #     model |= {'dqztm': '01'}  # 当前状态
    #     report_info = {'info': json.dumps({'model': model})}
    #     logging.info(f"生成上报信息成功。今日体温：{temperature}℃")

    #     url_loc = self.urls['loc_update']
    #     loc_info = {'id': module, 'gpswzxx': "广东省", 'gpswzjd': 113.97132, 'gpswzwd': 22.58469}
    #     response = self.session.post(url_loc, params={'info': json.dumps(loc_info)}, proxies=self.proxies)
    #     logging.debug(f'POST {url_loc} {response.status_code}')

    #     if not response.json().get('isSuccess'):
    #         logging.warning("更新地址失败！（但似乎没啥影响）")

    #     url_save = self.urls['save']
    #     response = self.session.post(url_save, params=report_info, proxies=self.proxies)
    #     logging.debug(f'POST {url_save} {response.status_code}')

    #     if not response.json().get('isSuccess'):
    #         raise ReportException.SubmitError("上报信息提交失败。")

    #     logging.info("上报信息提交成功。")
    
    
    def simple_submit(self,token):
        url_save = self.urls['save']
        info = {"model":{"dqzt":"99","gpsjd":117.647728,"gpswd":26.280749,"kzl1":"1","kzl2":"","kzl3":"","kzl4":"","kzl5":"","kzl6":"福建省","kzl7":"三明市","kzl8":"三元区","kzl9":"列东街1150号","kzl10":"福建省三明市三元区列东街1150号","kzl11":"","kzl12":"","kzl13":"0","kzl14":"","kzl15":"0","kzl16":"","kzl17":"1","kzl18":"0;","kzl19":"","kzl20":"","kzl21":"","kzl22":"","kzl23":"0","kzl24":"0","kzl25":"","kzl26":"","kzl27":"","kzl28":"0","kzl29":"","kzl30":"","kzl31":"","kzl32":"2","kzl33":"","kzl34":{},"kzl38":"福建省","kzl39":"三明市","kzl40":"三元区"}}
        info |= {"token":token}
        report_info = {'info': json.dumps(info)}
        response = self.session.post(url_save,params=report_info, proxies=self.proxies)
        logging.debug(f'POST save_url {response.status_code}')


    def get_token(self):
        url_token = self.urls['Token']
        response = self.session.post(url_token, proxies=self.proxies)
        return response.text


def main(args):
    def wait_a_minute(prompt, extra_minutes=0):
        wait = 60 * extra_minutes + random.randint(0, 60)
        logging.warning(prompt.format(wait))
        time.sleep(wait)

    r = Report(args, proxy_on=args.proxy, ports=[1080, 2080])

    try:
        r.student_login()
    except ReportException.LoginError:
        wait_a_minute("登录失败，将在 {} 秒后重试。", 1)
        r.student_login()

    except Exception as err:
        if not r.proxy_on:
            raise err
        logging.error(err)
        wait_a_minute("开启代理，将在 {} 秒后重试。")
        r.switch_proxies(r.student_login)

    try:
        r.student_report_check()
    except ReportException.ReportExistError as err:
        logging.error(err)
        return
    
    try:
        token = r.get_token()
    except Exception as err:
        logging.error(err)

    try:
        r.simple_submit(token)
    except Exception as err:
        logging.error(err)

    # try:
    #     r.student_report_submit(module_id)
    # except ReportException.SubmitError:
    #     wait_a_minute("提交失败，将在 {} 秒后重试。", 1)
    #     r.student_report_submit(module_id)


if __name__ == '__main__':
    parser = ArgumentParser(description='HITsz疫情上报')
    parser.add_argument('username', help='登录用户名')
    parser.add_argument('password', help='登录密码')
    parser.add_argument('-g', '--graduating', help='是否毕业班', nargs='?')
    parser.add_argument('-k', '--sckey', help='Server酱的sckey', nargs='?')
    parser.add_argument('-p', '--proxy', help='是否开启EasyConnect代理', action='store_true')
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
        current = datetime.today().strftime('%Y-%m-%d_%H:%M:%S')
        if arguments.sckey:
            requests.get(f'https://sc.ftqq.com/{arguments.sckey}.send?text={report_msg}{current}')
            logging.info("微信提醒消息已发送。")
