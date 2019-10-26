# -*- encoding: utf8 -*-
import re
import sys
import time
from datetime import datetime

import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.tools import FigureFactory as FF 

import numpy as np
from dao import Records
from dao import BaseData

from acquire_dicts import init_dict, dump_dict

def __init__():
    py.sign_in('vortex0305', 'h4BoHrAXpyuEeIRluRVm')

def time_series_range((min_dt, max_dt), ts_range=1800):
    min_ts = int(time.mktime(min_dt.timetuple()))
    max_ts = int(time.mktime(max_dt.timetuple()))
    print min_ts, max_ts
    return [datetime.fromtimestamp(i) for i in range(min_ts, max_ts + ts_range, ts_range)]

def to_ts(dt):
    return int(time.mktime(dt.timetuple()))


def get_dataset_from_batches(lines, x_batches):
    '''
        lines: datetime-list，代表传入的所有时间点,
        x_batches: 时间段-list，代表X轴所有的区间
    '''
    if len(x_batches) == 0:
        return None, None
    y_dataset = [0 for i in range(len(x_batches))]
    i, j = 1, 0
    while j < len(lines) and i < len(x_batches):
        # [,)
        if lines[j] >= x_batches[i-1] \
                and lines[j] < x_batches[i]:
            y_dataset[i] += 1
            j += 1
        else:
            i += 1
    return y_dataset


def get_datasets_by_zone(top, source="detail"):
    x_batches = time_series_range(Records.select_time_range(source))
    for zone_id in Records.select_all_zones(top, source=source):
        datasets = list()
        for title, lines in Records.select_all_by_zone(zone_id, key_with_title=False, source=source).items():
            print "---", zone_id, title.encode('utf8'), len(lines)
            y_dataset = get_dataset_from_batches(lines, x_batches)
            print y_dataset
            if not x_batches:
                continue
            yield zone_id, title, x_batches, y_dataset


def layout_dict(type, filename, width=2000):
    dt = {
        "scatter": go.Layout(title=filename, width=width),
        "bar": go.Layout(title=filename, width=width, barmode="stack"),
        "pie": go.Layout(title=filename)
    }
    return dt[type]


def return_html(filename):
    pat = re.compile('.*<body>(.*)</body>.*')
    with open(filename, "r") as fp:
        lines = fp.readlines()
    text = ''.join(lines)
    mat = re.findall(pat, text.replace('\n', '\t'))
    if mat:
        return mat[0] + '</br>'
    else:
        return ""

def graph_scatter(filename, datasets, width=2000):
    ''' zone_id, title
        all, zone_id
    '''
    graph = list()
    layout = layout_dict("scatter", filename, width)
    for name, ds in datasets.items():
        # title, x_bathces, y_dataset
        graph.append(
                go.Scatter(
                    x = np.array(ds["time_range"]),
                    y = np.array(ds["num_books"]),
                    mode = "lines",
                    name = name
                ))
    plotly.offline.plot({
        "data": graph,
        "layout": layout
    }, filename="htmls/line_{}".format(filename))
    return return_html("htmls/line_{}.html".format(filename))

def graph_bar(filename, datasets, width=2000):
    ''' zone_id, title
        all, zone_id
    '''
    graph = list()
    layout = layout_dict("bar", filename, width)
    for name, ds in datasets.items():
        # title, x_bathces, y_dataset
        graph.append(
                go.Bar(
                    x = np.array(ds["time_range"]),
                    y = np.array(ds["num_books"]),
                    name = name
                ))
    plotly.offline.plot({
        "data": graph,
        "layout": layout
    }, filename="htmls/bar_{}".format(filename))
    return return_html("htmls/bar_{}.html".format(filename))


def graph_pie(filename, datasets):
    graph = list()
    layout = layout_dict("pie", filename)
    for name, ds in datasets.items():
        graph.append(
                go.Pie(
                    labels=ds["zones"],
                    values=ds["num_books"]
                ))
    plotly.offline.plot({
        "data": graph,
        "layout": layout
    }, filename="htmls/pie_{}".format(filename))
    return return_html("htmls/pie_{}.html".format(filename))


def graph_table(filename, datasets):
    table = FF.create_table(datasets["all"])
    plotly.offline.plot(table, filename="htmls/table_{}".format(filename))    
    return return_html("htmls/table_{}.html".format(filename))


def main(source):
    # 读出"预订行为数据"，转化为以时间段维度的数据
    # graph1: 不同地区对应的预订数曲线
    # graph2: 每个地区，分不同酒店的预订曲线
    # graph3: 某个酒店的预订曲线
    # 暂时作为全量的写入，之后可以改为例行增量导入
    BaseData.delete_all()
    with open("data/base_{}.csv".format(source), "w") as fp:
        for zone_id, title, x_bathces, y_dataset in get_datasets_by_zone(top=False, source=source):
            dataset = list()
            for i in range(len(y_dataset)):
                # 文件输出为4列， zone_id，title，时间段，预订数
                # 之后也可以根据需求添加其他已经收集到的维度
                dataset.append(','.join([zone_id, title, str(x_bathces[i]), str(y_dataset[i])]).encode('utf8'))
            fp.write('\n'.join(dataset))
            fp.write('\n')
            BaseData.bulk_insert(dataset)

def graph_generator(source):
    header = '<html><head><meta charset="utf-8" /></head><body>'
    body = ''
    footer = '</body></html>'
    main(source)
    graph_all_dataset = BaseData.select_graph_all()
    body += graph_scatter("all_预订数变化_{}".format(source), graph_all_dataset, width=1200)
    with open('htmls/dashboard_{}.html'.format(source), 'w') as fp:
        fp.write('\n'.join([header, body, footer]))

if __name__ == "__main__":
#    graph_generator("detail")
#    graph_generator("list")
## -- load data --
#    main()
    header = '<html><head><meta charset="utf-8" /></head><body>'
    body = ''
    footer = '</body></html>'
# -- graph1 --
    graph_zone_percent = BaseData.select_zone_percent()
    body += graph_pie("分地区预订数占比", graph_zone_percent)
# -- graph2 --
    graph_all_dataset = BaseData.select_graph_all()
    body += graph_scatter("all_预订数变化", graph_all_dataset, width=1200)
# -- graph3 --
    graph_all_dataset_by_zone = BaseData.select_graph_all_by_zone(top=True)
    body += graph_scatter("all_zone_预订数波动_top5_zones", graph_all_dataset_by_zone)
    body += graph_bar("all_zone_预订数波动_top5_zones", graph_all_dataset_by_zone)
# -- graph4 --
    graph_title_books = BaseData.select_title_books()
    body += graph_table("酒店预订数排序", graph_title_books)
# -- combine --
    with open('htmls/dashboard.html', 'w') as fp:
        fp.write('\n'.join([header, body, footer]))

