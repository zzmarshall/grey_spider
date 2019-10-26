#!/bin/env/python

dataplatform_write_host = "10.4.24.231"
dataplatform_write_port = 3316
dataplatform_write_user = "dataplatform_w"
dataplatform_write_password = "RSndEcLEMa1lL8CcOd5Q_ucqrOcCgjKk"
dataplatform_db_name = "dataplatform"
Config = {
    "url": "mysql://{}:{}@{}:{}/{}?charset=utf8".format(
            dataplatform_write_user,
            dataplatform_write_password,
            dataplatform_write_host,
            dataplatform_write_port,
            dataplatform_db_name
            ),
    "username": dataplatform_write_user,
    "password": dataplatform_write_password,
    "host": dataplatform_write_host,
    "port": dataplatform_write_port,
}
Config["bin_path"] = "/home/zhuxujia/data_anylasis/spider/"
Config["data_path"] = Config["bin_path"] + "data/"
Config["log_path"] = Config["bin_path"] + "logs/"

Config["spider_logger"] = {
    "name": "spider_logger_new",
    "log_file": Config["log_path"] + "new_spider.log",
    "fmt": "%(asctime)s - %(filename)s:%(lineno)s - FUNC:%(funcName)s - %(levelname)s - %(message)s"
}

