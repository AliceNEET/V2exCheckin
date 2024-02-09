#!/usr/bin/env python
# coding=utf-8
'''
Author: JY
Date: 2023-10-23 23:07:13
LastEditTime: 2023-12-10 12:44:22
LastEditors: JY
Description: 
FilePath: /v2ex-checkin/main.py
'''
# -*- coding: utf-8 -*-
import json
import os
import re

import requests
import urllib3
from requests import utils

urllib3.disable_warnings()
env = os.environ.get("CONFIG")

class V2ex():
    name = "V2EX 论坛"

    def __init__(self, check_item):
        self.check_item = check_item

    @staticmethod
    def sign(session):
        msg = []
        response = session.get(url="https://www.v2ex.com/mission/daily", verify=False)
        pattern = (
            r"<input type=\"button\" class=\"super normal button\""
            r" value=\".*?\" onclick=\"location\.href = \'(.*?)\';\" />"
        )
        urls = re.findall(pattern=pattern, string=response.text)
        url = urls[0] if urls else None
        if url is None:
            return "cookie 可能过期"
        elif url != "/balance":
            headers = {"Referer": "https://www.v2ex.com/mission/daily"}
            data = {"once": url.split("=")[-1]}
            _ = session.get(
                url="https://www.v2ex.com" + url,
                verify=False,
                headers=headers,
                params=data,
            )
        response = session.get(url="https://www.v2ex.com/balance", verify=False)
        total = re.findall(
            pattern=r"<td class=\"d\" style=\"text-align: right;\">(\d+\.\d+)</td>",
            string=response.text,
        )
        total = total[0] if total else "签到失败"
        today = re.findall(
            pattern=r'<td class="d"><span class="gray">(.*?)</span></td>',
            string=response.text,
        )
        today = today[0] if today else "签到失败"
        username = re.findall(
            pattern=r"<a href=\"/member/.*?\" class=\"top\">(.*?)</a>",
            string=response.text,
        )
        username = username[0] if username else "用户名获取失败"
        msg += [
            {"name": "帐号信息", "value": username},
            {"name": "今日签到", "value": today},
            {"name": "帐号余额", "value": total},
        ]
        response = session.get(url="https://www.v2ex.com/mission/daily", verify=False)
        data = re.findall(
            pattern=r"<div class=\"cell\">(.*?)天</div>", string=response.text
        )
        data = data[0] + "天" if data else "获取连续签到天数失败"
        msg += [
            {"name": "签到天数", "value": data},
        ]
        return msg

    def main(self):
        cookie = {
            item.split("=")[0]: item.split("=")[1]
            for item in self.check_item.get("cookie").split("; ")
        }
        session = requests.session()
        if self.check_item.get("proxy", ""):
            proxies = {
                "http": self.check_item.get("proxy", ""),
                "https": self.check_item.get("proxy", ""),
            }
            session.proxies.update(proxies)
        requests.utils.add_dict_to_cookiejar(session.cookies, cookie)
        session.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
                "accept-language": "zh",
            }
        )
        msg = self.sign(session=session)
        print(msg)
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.loads(f.read())
    else:
        config = json.loads(env)

    _check_item = config.get("V2EX", [])[0]
    pushToken = config.get("PUSHTOKEN", [])
    if pushToken != None:
        msg1 = V2ex(check_item=_check_item).main()
        content = "今日V2ex论坛签到！\n"+msg1
        requests.post('https://www.pushplus.plus/send', { 'token': pushToken, 'title': 'V2ex论坛签到', 'content': content });
