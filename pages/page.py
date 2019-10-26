# -*- encoding: utf8 -*-
import os
import re
import sys
import json
import ujson
import traceback
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import OrderedDict
from acquire_dicts import *

from dao import Records
from conf.base_config import Config


class Page(object):
    def __init__(self, response, logger):
        self.logger = logger
        doc = response["content"]
        self.soup = BeautifulSoup(doc.decode('utf8'))
        self.record_time = response.get("record_time", None)
        self.dt_hotels = OrderedDict()
        self.labels = None
        self.logger.info("Title: %s", self.soup.title)

    def extract(self): pass

    def dump(self, time_sleep, initialize=False):
        last_book_dict = init_dict("book_{}".format(self.labels)) 
        self.logger.info("Start Dump: %s - %s" % (len(self.dt_hotels), time_sleep))
        for k, v in self.dt_hotels.items():
            try:
                last_book = last_book_dict.get(v["title"], {"time":None, "delta":0})
                if not initialize:
                    # 第一次注释这个，之后都开启
                    # 如果 delta 处于小时区间，直接跳过
                    if not v["new_book_delta"] or \
                        v["new_book_delta"].seconds >= 3600:
                        continue
                    # d2 >= d1 + time_sleep
                    if v["new_book_delta"].seconds >= last_book["delta"] + time_sleep:
                        continue
                # 更新 book_dict
                self.logger.info("Dump\t%s\t( %s\t%s )\t( %s\t%s )" % (v["title"], v["new_book_delta"], v["new_book"], last_book["delta"], last_book["time"]))
                last_book_dict[v["title"]] = {
                    "time": v["new_book"],
                    "delta": v["new_book_delta"].seconds if v["new_book_delta"] else -1
                }
                Records.insert(
                    k, v["title"], v["star"], self.labels,
                    v["low_price"], v["judge_score"], v["judge_users"],
                    v["new_book"], v["new_book_delta"].seconds if v["new_book_delta"] else -1,
                    datetime.strftime(self.record_time, "%Y-%m-%dT%H:%M"),
                    self.zone_id
                    )
            except:
                print >> sys.stderr, traceback.format_exc()
                continue
        dump_dict(last_book_dict, "book_{}".format(self.labels))

