#!/usr/bin/env python 
# -*- encoding:utf-8 -*-

import sys
import logging
import logging.handlers

from conf.base_config import Config

def get(logger_config=dict()):
    '''
    返回各模块所对应的logger
    '''
    # 实例化handler
    handler = logging.handlers.RotatingFileHandler(
            logger_config.get("log_file", ""),
            maxBytes=1024*1024*1024,
            backupCount=3
            )

    # 实例化formatter
    formatter = logging.Formatter(logger_config.get("fmt", ""))
    # 为handler配置formatter
    handler.setFormatter(formatter)

    # 获得logger
    logger = logging.getLogger(logger_config.get("name", ""))
    # 为logger添加handler
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


def get_log_path(logger):
    return Config[logger.name]["log_file"]

spider_logger = get(Config["spider_logger"])
