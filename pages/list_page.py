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

from conf.base_config import Config

from acquire_dicts import init_dict, dump_dict
from pages.page import Page

        
class ListPage(Page):

    _patterns = {
        "low_price": re.compile(r'(\d+)'),
        "judge_paras": re.compile(r'([\d\.]+)分.*自(\d+)位'),
        "new_book": re.compile(r'最新预订：(\d+)(\S+)'),
        "star": re.compile(r'为([\d\.]+)钻')
    }

    def __init__(self, response, logger):
        super(ListPage, self).__init__(response, logger)
        self.labels = "list"

    def _get_hotel_id_title(self, hotel):    
        a = hotel.find('a', attrs={'class': 'title'})
        id = a["href"].split('/')[-1].split('.')[0]
        title = a["title"].encode('utf8')
        return id, title

    def _get_zone_id(self, hotel):
        a = hotel.find('p', attrs={'class': 'location'}).find('a')
        zone_id = a["href"].split('/')[-1]
        return zone_id

    def _get_low_price(self, hotel):
        a = hotel.find('div', attrs={'class': 'price_htl price_htl_pos'})
        low_price_str = a.getText().encode('utf8')
        low_price = re.findall(self._patterns["low_price"], low_price_str)[0]
        return low_price

    def _get_judge_paras(self, hotel):
        a = hotel.find('p', attrs={'class': 'comment'})
        judge_paras = a.getText().encode('utf8')
        score, users = re.findall(self._patterns["judge_paras"], judge_paras)[0]
        return users, score

    def _get_new_book(self, hotel):
        new_book_str = hotel.find('p', attrs={'class': 'title'}).getText().encode('utf8')
        res = re.findall(self._patterns["new_book"], new_book_str)[0]
        if "分钟" in res[1]:
            return timedelta(minutes=int(res[0]))
        elif "小时" in res[1]:
            return timedelta(hours=int(res[0]))

    def _get_star(self, hotel):
        star_str = hotel.find('p', attrs={'class': 'star'})["title"].encode('utf8')
        if star_str == "":
            star = 0
        else:
            star = re.findall(self._patterns['star'], star_str)[0]
        return star

    def extract(self):
        self.hotel_list = self.soup.find('ul', attrs={'class': 'htl_list_cont clearfix'}) 
        for li in self.hotel_list.findChildren('li'):
            try:
                id, title = self._get_hotel_id_title(li)
                self.zone_id = self._get_zone_id(li)
                low_price = self._get_low_price(li)
                judge_users, judge_score = self._get_judge_paras(li)
                star = self._get_star(li)
                new_book_delta = self._get_new_book(li)
                new_book = datetime.strftime(
                        self.record_time - new_book_delta,
                        "%Y-%m-%dT%H:%M"
                        )
                self.dt_hotels[id] = {
                    "star": star,
                    "title": title,
                    "low_price": low_price,
                    "judge_score": judge_score,
                    "judge_users": judge_users,
                    "new_book": new_book,
                    "new_book_delta": new_book_delta
                }
            except Exception as e:
                print >> sys.stderr, e
                continue
        return self.dt_hotels

    def get_page_numbers(self):
        div = self.soup.find('div', attrs={'class': 'c_page_list layoutfix'})
        last = div.findChildren('a')[-1]
        return last.getText()


