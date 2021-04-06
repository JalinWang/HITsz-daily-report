#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from requests.utils import dict_from_cookiejar
from lxml import etree
import json
import random
import datetime
import argparse
import logging

log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)

parser = argparse.ArgumentParser(description='HITsz疫情上报')
parser.add_argument('username', help='用户名')
parser.add_argument('password', help='密码')
parser.add_argument('graduating', help='是否毕业生班')
parser.add_argument('-k', '--api_key', help='SCKEY')


def get_report_info(session: requests.Session, module_id: str) -> dict:
    # 获取每日上报信息的模板
    logging.info('获取上报信息模板')
    params = {
        'info': json.dumps({'id': module_id})
    }
    get_msg_url = 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/getYqxx'
    response = session.post(get_msg_url, params=params)
    logging.info(f'POST {get_msg_url} {response.status_code}')

    origin_data = response.json()['module']['data'][0]
    key_list = ["stzkm", "dqszd", "hwgj", "hwcs", "hwxxdz", "dqszdsheng", "dqszdshi", "dqszdqu", "gnxxdz", "dqztm",
                "dqztbz", "brfsgktt", "brzgtw", "brsfjy", "brjyyymc", "brzdjlm", "brzdjlbz", "qtbgsx", "sffwwhhb",
                "sftjwhjhb", "tcyhbwhrysfjc", "sftzrychbwhhl", "sfjdwhhbry", "tcjtfs", "tchbcc", "tccx", "tczwh",
                "tcjcms", "gpsxx", "sfjcqthbwhry", "sfjcqthbwhrybz", "tcjtfsbz"]
    model = {key: origin_data[key] for key in key_list}
    model['id'] = module_id
    model['sffwwhhb'] = args.graduating     # 是否毕业生班

    temperature = format(random.uniform(36, 37), '.1f')     # 随机生成体温
    logging.info(f'生成今日体温 {temperature}')

    model['brzgtw'] = temperature
    report_info = {
        'info': json.dumps({'model': model})
    }
    logging.info('生成上报信息成功')
    logging.debug(report_info)
    return report_info


def main(args):
    session = requests.session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
    })

    # 登录统一认证系统
    sso_url = 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/shsj/common'
    response = session.get(sso_url)
    logging.info(f'GET {sso_url} {response.status_code}')

    html = etree.HTML(response.text)
    lt = html.xpath('//input[@name="lt"]/@value')[0]
    execution = html.xpath('//input[@name="execution"]/@value')[0]
    eventId = html.xpath('//input[@name="_eventId"]/@value')[0]
    login_params = {
        'lt': lt,
        'execution': execution,
        '_eventId': eventId,
        'username': args.username,
        'password': args.password,
    }
    jsessionid = dict_from_cookiejar(response.cookies)['JSESSIONID']

    login_url = f'https://sso.hitsz.edu.cn:7002/cas/login;jsessionid={jsessionid}?service=http://xgsm.hitsz.edu.cn/zhxy-xgzs/common/casLogin?params=L3hnX21vYmlsZS94c0hvbWU='
    response = session.post(login_url, params=login_params, allow_redirects=False)  # 禁用跳转，用于处理登录失败的问题
    logging.info(f'POST {login_url} {response.status_code}')

    if response.status_code == 200:
        # 登录失败，输出错误信息
        msg = etree.HTML(response.text).xpath('//div[@id="msg"]/text()')[0]
        return False, msg
    elif response.status_code != 302:
        msg = '其他错误'
        return False, msg

    logging.info('登录成功')

    # 登录成功，继续跳转，更新 cookie
    next_url = response.next.url
    response = session.get(next_url)
    logging.info(f'GET {next_url} {response.status_code}')

    # 获取学号，此部分非必要
    stu_id_url = 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xsHome/getGrxx'
    response = session.post(stu_id_url)
    logging.info(f'POST {stu_id_url} {response.status_code}')
    user = response.json()["module"]["xh"]
    logging.info(f'当前账号：{user}')

    # 查询今天是否已生成上报信息，并获得 ID
    csh_url = 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/csh'
    response = session.post(csh_url)
    logging.info(f'POST {csh_url} {response.status_code}')
    result = response.json()
    logging.debug(result)

    if not result['isSuccess']:
        logging.error('新增每日上报信息失败')
        check_url = 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/getYqxxList'
        response = session.post('http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/getYqxxList')
        logging.error(f'POST {check_url} {response.status_code}')
        today_report = response.json()['module']['data'][0]
        logging.debug(today_report)

        msg = ""
        if today_report['zt'] == '00':
            msg = '上报信息已存在，尚未提交'
        elif today_report['zt'] == '01':
            msg = '上报信息已提交，待审核'
            return False, msg
        elif today_report['zt'] == '02':
            msg = '上报信息已审核，无需重复提交'
            return False, msg

    report_info = get_report_info(session, result['module'])
    save_url = 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/saveYqxx'
    response = session.post(save_url, params=report_info)
    logging.info(f'POST {save_url} {response.status_code}')

    res_msg = '提交成功' if response.json()['isSuccess'] else '提交失败'
    return  response.json()['isSuccess'], res_msg


if __name__ == '__main__':
    args = parser.parse_args()
    is_successful, msg = main(args)
    logging.warning(msg)
    if args.api_key:
        txt = ""
        if is_successful:
            txt = f"疫情上报成功！{datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            txt = f"疫情上报失败，原因：{msg}{datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}"
        requests.get(f"https://sc.ftqq.com/{args.api_key}.send?text={txt}")
