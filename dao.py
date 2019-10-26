#!/bin/env/python
# -*- coding: utf-8 -*-
import sys
import ujson
import os
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from abc import abstractmethod
from sqlalchemy.ext.declarative import declarative_base
from collections import OrderedDict

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import or_
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.sql import func

from conf.base_config import Config
from acquire_dicts import init_dict

@contextmanager
def get_session_scope(
        Session=sessionmaker(bind=create_engine(Config["url"], echo=False, pool_recycle=60))
        ):
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def build_engine_from_conf(conf=dict()):
    url = "{}://{}:{}@{}:{}/{}".format(
            conf.get("protocol", "mysql"),
            conf.get("username", Config["username"]),
            conf.get("password", Config["password"]),
            conf.get("host",     Config["host"]),
            conf.get("port",     Config["port"]),
            conf.get("db",       Config["db"])
            )

    query_list = list()
    for k, v in conf.get("queries", dict()).items():
        query_list.append("{}={}".format(k, v))

    if len(query_list) > 0:
        url += '?' + '&'.join(query_list)

    engine = sessionmaker(
            bind=create_engine(url, echo=False, pool_recycle=60)
            )
    return engine


class Dao(declarative_base()):
    '''
        各种mapping类所继承的基类，实现部分公用方法与声明一些虚方法
    '''
    __abstract__ = True

class BaseData(Dao):
    __tablename__ = "base_data"

    id      = Column(Integer, autoincrement=True, primary_key=True)
    zone_id = Column(String)
    title   = Column(String)
    time_range = Column(String)
    num_books = Column(Integer)
    
    @classmethod
    def delete_all(self):
        with get_session_scope() as scope:
            # --- delete all ---
            try:
                num_rows_deleted = scope.query(BaseData).delete()
                scope.commit()
            except:
                scope.rollback()

    @classmethod
    def bulk_insert(self, dataset):
        with get_session_scope() as scope:
            inserts = list()
            for ds in dataset:
                f = ds.split(',')
                inserts.append(BaseData(
                    zone_id=f[0],
                    title=f[1],
                    time_range=f[2],
                    num_books=f[3]
                    ))
            scope.add_all(inserts)

    @classmethod
    def select_graph_all_by_zone(self, top=True):
        zone_dict=init_dict("zone")
        top_list = '"zone37", "zone31", "zone133", "zone135", "zone41"'
        with get_session_scope() as scope:
            if top:
                where_str = "where zone_id in ({})".format(top_list)
            sql = '''
                select zone_id, time_range, sum(num_books) from base_data {} group by zone_id, time_range order by zone_id, time_range
                '''.format(where_str)
            results = dict()
            for res in scope.execute(sql):
                zone = zone_dict[res[0]]
                results.setdefault(zone, {
                    "time_range": list(),
                    "num_books": list()
                })
                results[zone]["time_range"].append(res[1])
                results[zone]["num_books"].append(int(res[2]))
            return results

    @classmethod
    def select_zone_percent(self):
        zone_dict=init_dict("zone")
        with get_session_scope() as scope:
            sql = '''
                select zone_id, sum(num_books) from base_data group by zone_id order by sum(num_books) desc
                '''
            results = {
                "all": {
                    "zones": list(),
                    "num_books": list()
                }}
            for res in scope.execute(sql):
                zone = zone_dict[res[0]]
                results["all"]["zones"].append(zone)
                results["all"]["num_books"].append(int(res[1]))
            return results
    
    @classmethod
    def select_title_books(self):
        with get_session_scope() as scope:
            sql = '''
                select tb.title, tb.ct from (select title, sum(num_books) as ct from base_data group by title) tb where tb.ct > 100 order by tb.ct desc
                '''
            results = {"all": [["酒店名称", "预订数"]]}
            for res in scope.execute(sql):
                results["all"].append([res[0].encode('utf8'), int(res[1])])
            return results
        

    @classmethod
    def select_graph_all(self):
        with get_session_scope() as scope:
            sql = '''
                select time_range, sum(num_books) from base_data group by time_range order by time_range
                '''
            results = {
                "all": {
                    "time_range": list(),
                    "num_books": list()
                }}
            for res in scope.execute(sql):
                results["all"]["time_range"].append(res[0])
                results["all"]["num_books"].append(int(res[1]))
            return results

class Records(Dao):
    __tablename__ = "records"

    id      = Column(Integer, autoincrement=True, primary_key=True)
    hotel_id = Column(Integer)
    title = Column(String)
    star = Column(String)
    labels = Column(String)
    low_price = Column(Integer)
    judge_score = Column(Integer)
    judge_users = Column(Integer)
    new_book = Column(DateTime)
    new_book_delta = Column(DateTime)
    record_time = Column(String)
    zone_id = Column(Integer)

    @classmethod
    def insert(self, hotel_id, title, star, labels, low_price, judge_score, judge_users, new_book, new_book_delta, record_time, zone_id):
        with get_session_scope() as scope:
            record = Records(
                hotel_id=hotel_id,
                title=title,
                star=star,
                labels=labels,
                low_price=low_price,
                judge_score=judge_score,
                judge_users=judge_users,
                new_book=new_book,
                new_book_delta=new_book_delta,
                record_time=record_time,
                zone_id=zone_id,
            )
            scope.add(record)
            scope.flush()
            return record.id

    @classmethod
    def select_all_zones(self, top=True, source="detail"):
        top_list = ["zone37", "zone31", "zone133", "zone135", "zone41"]
        with get_session_scope() as scope:
            rows = scope.query(Records.zone_id).filter(Records.labels==source)
            if top:
                rows = rows.filter(Records.zone_id.in_(top_list))
            rows = rows.distinct()\
                    .all()
            return [i[0] for i in rows]

    @classmethod
    def select_time_range(self, source):
        with get_session_scope() as scope:
            sql = "select min(new_book), max(new_book) from records where labels = '{}'".format(source)
            rt = scope.execute(sql)
            for r in rt:
                return datetime.strptime(r[0], "%Y-%m-%dT%H:%M"), datetime.strptime(r[1], "%Y-%m-%dT%H:%M")
            
    @classmethod
    def select_all_by_zone(self, zone_id, key_with_title=True, top=-1, source="detail"):
        results = dict()
        white_list = list()
        # 获取预订数量最多的前10个酒店        
        with get_session_scope() as scope:
            rows = scope.query(Records)\
                    .filter(Records.new_book!=None)\
                    .filter_by(zone_id=zone_id)\
                    .filter_by(labels=source)
            if top > 0:
                hotel_ids = scope.query(Records.hotel_id, func.count(1))\
                            .filter(Records.new_book!=None)\
                            .filter_by(zone_id=zone_id)\
                            .group_by(Records.hotel_id)\
                            .order_by(func.count(1).desc())\
                            .limit(top)
                white_list = [i[0] for i in hotel_ids]
                rows = rows.filter(Records.hotel_id.in_(white_list))
            if key_with_title:
                for row in rows.order_by(Records.new_book).all():
                    results.setdefault(row.title, list())
                    results[row.title].append(datetime.strptime(row.new_book, "%Y-%m-%dT%H:%M"))
            else:
                for row in rows.order_by(Records.new_book).all():
                    results.setdefault(row.zone_id, list())
                    results[row.zone_id].append(datetime.strptime(row.new_book, "%Y-%m-%dT%H:%M"))
            return results

