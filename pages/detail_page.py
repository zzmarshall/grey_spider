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

    
class DetailPage(Page):

    _patterns = {
        "star": re.compile(r'用户评定为(\S+)钻'),
        "judge_users": re.compile(r'\d+'),
        "new_book": re.compile(r'最新预订：(\d+)(\S+)')
    }

    def __init__(self, response, logger):
        super(DetailPage, self).__init__(response, logger)
        self.zone_id = response["zone_id"]
        self.hotel_list = self.soup.find('div', id="hotel_list")
        self.labels = "detail"

    def _get_title(self, hotel):
        return hotel\
                 .findChildren('div', 'hotel_pic')[0]\
                 .find('a')["title"]\
                 .encode('utf8')

    def _get_labels(self, hotel):
        star = float()
        special_labels = list()
        medal_list = hotel.find('p', attrs={'class': 'medal_list'})
        spans = medal_list.findChildren('span')
        for span in spans:
            if "hotel_" in span["class"][0]:
                star = float(re.findall(
                    self._patterns["star"], span["title"].encode('utf8')
                    )[0])
            elif "special_label" == span["class"][0]:
                special_labels = list()
                for i in span.findChildren('i'):
                    special_labels.append(i.getText())
        return {
            "star": star,
            "labels": special_labels
        }

    def _get_low_price(self, hotel):
        return int(hotel\
                .findChildren('div', 'hotel_price')[0]\
                .find('span', attrs={'class': 'J_price_lowList'})\
                .getText())

    def _get_judge_score(self, hotel):
        return float(hotel\
               .find('span', attrs={'class': 'hotel_value'})\
               .getText())

    def _get_judge_users(self, hotel):
        hotel_judgement = hotel.find('span', attrs={'class': 'hotel_judgement'})
        return int(re.findall(
            self._patterns["judge_users"], str(hotel_judgement)
            )[0])

    def _get_new_book(self, hotel):
        new_book = hotel.find('p', attrs={'class': 'new_book'})
        if new_book is None:
            new_book = hotel.find('span', attrs={'class': 'new_book float_right'}).getText()
        res = re.findall(self._patterns["new_book"], str(new_book.encode('utf8')))[0]
        if "分钟" in res[1]:
            return timedelta(minutes=int(res[0]))
        elif "小时" in res[1]:
            return timedelta(hours=int(res[0]))

    def extract(self):
        titles = list()
        for hotel in self.hotel_list.findChildren('div', 'searchresult_list')[:-1]:

            # title
            title = self._get_title(hotel)
            self.logger.info(title)
            # labels
            try:
                labels = self._get_labels(hotel)
            except:
                print >> sys.stderr, "Error:labels\n", hotel
                labels = None
            # low price
            try:
                low_price = self._get_low_price(hotel)
            except:
                print >> sys.stderr, "Error:low_price\n", hotel
                low_price = None
            # judge_score
            try:
                judge_score = self._get_judge_score(hotel)
            except:
                print >> sys.stderr, "Error:judge_score\n", hotel
                judge_score = None
            # judge_users
            try:
                judge_users = self._get_judge_users(hotel)
            except:
                print >> sys.stderr, "Error:judge_users\n", hotel
                judge_users = None
            try:
                new_book_delta = self._get_new_book(hotel)
                new_book = datetime.strftime(
                        self.record_time - new_book_delta,
                        "%Y-%m-%dT%H:%M"
                        )
            except:
                print >> sys.stderr, "Error:new_book\n", hotel
                new_book = None
                new_book_delta = None
            try:
                self.dt_hotels[hotel["id"]] = {
                    "title": title,
                    "low_price": low_price,
                    "judge_score": judge_score,
                    "judge_users": judge_users,
                    "new_book": new_book,
                    "new_book_delta": new_book_delta,
                    "star": labels["star"]
                }
#                self.dt_hotels[hotel["id"]].update(labels)
            except Exception as e:
                print >> sys.stderr, e
                continue
            
        return self.dt_hotels

        
if __name__ == "__main__":
    with open("1", "r") as fp:
        docs = ''.join(fp.readlines())
        page = Page(docs)
        page.extract()
