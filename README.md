# grey_spider
 
## 抓取源
- 详情页抓取: http://hotels.ctrip.com/domestic-1.html 北京热门地标（下文简称 detail）
- 列表页抓取: http://hotels.ctrip.com/top/beijing1/zuixinyuding 所有最新预订榜（下文简称 list）


- 详情页
早期是先找到网站的站点地图，然后以热本地标为列表，遍历抓取详情页信息，例如：
内嵌图片 2
内嵌图片 1

- 列表页
之后发现了一个更好的入口，在北京酒店排行榜中找到了“最新预订酒店排行榜”，可以获得更完整的数据：
内嵌图片 3


## 附件
备注：其中部分图表是对 top5 地区进行汇总
dashboard_detail.html  ：详情页所得数据产出的各式图表
detail_sum_bookings.html  ：详情页总预订数的变化趋势
list_sum_bookings.html ：列表页总预订数的变化趋势
zone.txt ：地区ID 对应的 地区名称
booking_records：所有预订记录 & 获取的信息​
booking_records.csv
