from dao import *
import scipy.stats as stats
import numpy

def acquire():
    results = dict()
    hotel_nums = None
    with get_session_scope() as scope:
    #    sql = "select time_range, count(distinct title), sum(num_books) from base_data where zone_id in ('zone37', 'zone31', 'zone133') group by time_range"
        sql = "select time_range, 1, sum(num_books) from base_data group by time_range"
        for res in scope.execute(sql):
            time_range = res[0][:10]
            hotel_nums = res[1]
            book_nums = res[2]
            results.setdefault(time_range, 0)
            results[time_range] += book_nums
    
    
    for k, v in results.items():
        print k, v 

def calc():
    a, b, c = list(), list(), list()
    for line in sys.stdin:
        f = line.strip().split(' ')
        a.append(float(f[1]))
        b.append(float(f[2]))
        c.append(float(f[3]))
    print a
    print b
    print c
    covariance_ab = numpy.cov(a, b)[0][1]
    covariance_ac = numpy.cov(a, c)[0][1]
    covariance_bc = numpy.cov(b, c)[0][1]
    std_ab = numpy.std(a) * numpy.std(b)
    std_ac = numpy.std(a) * numpy.std(c)
    std_bc = numpy.std(b) * numpy.std(c)
    print covariance_ab, std_ab, covariance_ab/std_ab, numpy.correlate(a, b)[0]
    print covariance_ac, std_ac, covariance_ac/std_ac, numpy.correlate(a, c)[0]
    print covariance_bc, std_bc, covariance_bc/std_bc, numpy.correlate(b, c)[0]
    print stats.pearsonr(a, b)
    print stats.pearsonr(a, c)
    print stats.pearsonr(b, c)

if __name__ == "__main__":
    calc()
# --------- top 3 -----------
#    [6821.0, 10037.0, 10019.0, 10405.0, 8602.0, 7594.0, 9574.0, 9755.0, 9761.0, 9428.0, 9186.0, 8655.0, 7121.0, 7033.0, 9628.0, 10533.0, 10624.0, 9099.0]
#    [40.86, 42.5, 40.07, 39.98, 40.15, 40.15, 40.15, 40.15, 39.97, 39.99, 40.0, 40.49, 40.49, 40.49, 40.49, 41.34, 42.8, 42.5]
#    [41.15, 41.16, 40.53, 40.17, 40.62, 40.62, 40.62, 40.62, 40.43, 40.11, 40.8, 41.1, 41.1, 41.1, 41.1, 41.69, 43.0, 42.8]
#    262.182647059 1089.57328239 0.240628740898 6673896.48
#    92.6629411765 903.492693515 0.102560808562 6727005.27
#    0.648735294118 0.698101672505 0.929284830088 30075.7013
#    (0.2272604775148766, 0.36445304021266212)
#    (0.096862985863854154, 0.70219950314563939)
#    (0.87765789508265235, 1.7075120791826117e-06)
# -------- all ---------
#    (venv) zhuxujia@n6-129-086:~/data_anylasis/spider$ cat 2 | python analyse.py
#    [1251.0, 1811.0, 1839.0, 1806.0, 1550.0, 1491.0, 1788.0, 1828.0, 1903.0, 1754.0, 1672.0, 1579.0, 1323.0, 1381.0, 1859.0, 1888.0, 1935.0, 1746.0]
#    [40.86, 42.5, 40.07, 39.98, 40.15, 40.15, 40.15, 40.15, 39.97, 39.99, 40.0, 40.49, 40.49, 40.49, 40.49, 41.34, 42.8, 42.5]
#    [41.15, 41.16, 40.53, 40.17, 40.62, 40.62, 40.62, 40.62, 40.43, 40.11, 40.8, 41.1, 41.1, 41.1, 41.1, 41.69, 43.0, 42.8]
#    41.7801960784 187.79839436 0.222473659696 1238102.39
#    18.6958823529 155.725622039 0.120056559146 1248097.99
#    0.648735294118 0.698101672505 0.929284830088 30075.7013
#    (0.21011401193540452, 0.40268111211015278)
#    (0.1133867503047357, 0.65417271198047899)
#    (0.87765789508265235, 1.7075120791826117e-06)
