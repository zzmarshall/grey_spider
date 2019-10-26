# 抓取对象
* 北京酒店预订 列表页抓取: http://hotels.ctrip.com/top/beijing1/zuixinyuding 获取所有最新预订榜
* 北京酒店预订 详情页抓取: http://hotels.ctrip.com/domestic-1.html 根据北京热门地标来搞

# 模块简介
主要模块
* 调度服务 spider.py: 继承自 daemon.py，实现了一个可以后台一直运行的进程，定时触发抓取方法
* 抓取模块 crawler.py: 提供两种抓取方法（分别对应两个源）：详情页 detail_page_disposal()  列表页 list_page_disposal()  
实现了一个 Crawler 类，用来 伪造请求 & 依次抓取页面
* 页面解析 pages/page.py: list_page.py detail_page.py 继承自 page.py 分别解析两种源对应的页面
* 导出图表 export.py: 数据聚合 & 绘制各式图表

辅助模块
* ORM dao.py: 封装数据库操作
* daemon.py: 实现后台一直运行的 daemon 进程
* acquire_dicts.py: 临时字典的读取与写入 
* analyse.py: 一些指标的相关性计算等，做后续分析完善

