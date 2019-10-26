#!/usr/bin/env python 
# -*- encoding:utf-8 -*-
import os
import sys
import time
from datetime import datetime
import subprocess
import random

from daemon import Daemon

from conf.base_config import Config
from logger import spider_logger
from crawler import detail_page_disposal, list_page_disposal


class Spider(Daemon):
    
    def __init__(self, pid_file,
                 logger,
                 stdin_file='/dev/null',
                 stdout_file='/dev/null',
                 stderr_file='/dev/null'
                 ):
        Daemon.__init__(self, pid_file, logger, stdin_file, stdout_file, stderr_file)

    def run(self, _interval):
        count = 0
        time_sleep = 0
        while True:
            self.logger.info(datetime.now())
            self.logger.info("------Start------")
            self.logger.info("------List-----")
            list_page_disposal(time_sleep)
            self.logger.info("------Detail-----")
            detail_page_disposal(time_sleep)
            self.logger.info("------End------")
        
            # dynamic_sleep_time
            current_hour = datetime.strftime(datetime.now(), "%H")
            if current_hour <= '01' and current_hour <= '07':
                time_sleep = random.choice(range(3000, 3540))
            elif current_hour >= '08' and current_hour <= '24':
                time_sleep = random.choice(range(500, 700))
            time.sleep(time_sleep)


if __name__ == "__main__":
    Spider(
            pid_file="/tmp/spider.pid",
            logger=spider_logger,
            stderr_file=Config["log_path"] + "spider.stderr"
        ).start(300)
