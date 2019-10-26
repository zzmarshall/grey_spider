# -*- encoding: utf8 -*-
import sys
import json
import time
import random
import requests
import traceback
from pages.detail_page import DetailPage
from pages.list_page import ListPage
from datetime import datetime

from logger import spider_logger
from conf.base_config import Config

from acquire_dicts import init_dict

def detail_page_disposal(time_sleep, initialize=False):
    client = Crawler(spider_logger)
    for response in client.request("detail"):
        page = DetailPage(response, spider_logger)
        page.extract()
        page.dump(time_sleep, initialize)

def list_page_disposal(time_sleep, initialize=False):
    client = Crawler(spider_logger)
    for response in client.request("list"):
        page = ListPage(response, spider_logger)
        page.extract()
        page.dump(time_sleep, initialize)


class Crawler(object):

    user_agent = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)"
    ]

    def __init__(self, logger=None):
        self.logger = logger
        self.zone_dict = init_dict("zone")

    def request(self, page):
        page2func = {
            "detail": self._detail_new_book,
            "list": self._list_new_book
        }
        for url, headers, zone in page2func[page]():
            try:
                response = self._get(url, headers)
                if response.status_code/100 != 2:
                    raise Exception(response.reason)
                yield {
                    "content": response.content,
                    "record_time": datetime.now(),
                    "zone_id": zone
                }
            except Exception as e:
                print >> sys.stderr, "Fetch error", traceback.format_exc()
                continue

    def _get(self, url, headers):
        return requests.get(url, headers=headers)

    def _get_header(self):
        header = {
            # 伪造下UA
            "User-Agent": random.choice(self.user_agent),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            # 伪造下Referer
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4"
        }
        return header

    def _list_new_book(self):
        # page 递增 1- end
        header = self._get_header()
        url = "http://hotels.ctrip.com/top/beijing1/zuixinyuding"
        response = self._get(url, header)
        page = ListPage({"content": response.content}, self.logger)
        end = page.get_page_numbers()
        id_list = range(1, int(end)+1)
        for idx in range(len(id_list)):
            url = "http://hotels.ctrip.com/top/beijing1/zuixinyuding"
            random.shuffle(id_list)
            page_id = id_list.pop()
            if page_id != 1:
                url = "{}-p{}".format(url, page_id)
            self.logger.info("URL: %s" % url)
            time.sleep(random.choice(range(0,3)))
            yield (url, header, "all")

    def _detail_new_book(self):
        # zoneXX 循环
        # 根据地标来搞，地标再分用户类型 holiday or business
        # zone_list:  url = "http://hotels.ctrip.com/domestic-1.html"
        for zone in self.zone_dict:
            self.logger.info("Zone: %s %s" % (zone, self.zone_dict[zone]))
            url = "http://hotels.ctrip.com/hotel/beijing1/{}".format(zone)
            header = self._get_header()

            time.sleep(random.choice(range(0,3)))
            yield (url, header, zone)

if __name__ == "__main__":
    detail_page_disposal(0, initialize=False)
    list_page_disposal(0, initialize=False)
