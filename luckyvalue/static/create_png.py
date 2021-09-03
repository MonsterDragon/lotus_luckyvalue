import os
import pymysql
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal
import datetime

# 输出公司全部节点相对应存储大小的全网分布统计图
# connect to mysql
conn = pymysql.connect(
    host="10.1.2.65",
    user="root",
    password="123",
    database="miner_info",
    charset="utf8"
)

# miner_id
minerid_list = ["f0417893", "f0490501", "f0151536", "f0227531", "f0151436", "f0151366", "f0396732", "f0396720",
                "f0227472", "f0227684", "f0150782", "f0417709", "f0396684", "f0396352", "f0227660", "f0396751",
                "f0151468", "f054420", "f0227567", "f0417767", "f057618", "f054418", "f054417", "f054414", "f054415",
                "f054422", "f0158993", "f0109040", "f0417918", "f085777", "f0151341", "f054412", "f079370", "f0133763",
                "f023198", "f017193", "f0162183", "f0109606", "f0151487", "f0417826", "f0151453"]


# return selected dataframe parameters
def select_sql(select_str):
    select_result = pd.read_sql(select_str, con=conn)
    return select_result


# create Normal distribution original list
def create_list(one_pb_2):
    max_value = one_pb_2[0:1]['lucky_value'][0]
    max_value = round(max_value, 1)
    i = 0.0
    value_list = []
    max_num = 0
    while i < max_value:
        b = i + 0.1
        b = round(b, 1)
        num = 0
        value_dict = {}
        for index, row in one_pb_2.iterrows():
            if row[1] >= i and row[1] < b:
                num += 1
            else:
                pass
        if num > max_num:
            max_num = num
        value_dict["range"] = str(i) + '-' + str(b)
        value_dict["num"] = num
        value_list.append(value_dict)
        i += 0.1
        i = round(i, 1)
    orig = value_list[-1]["num"]
    value_list[-1]["num"] = orig + 1
    return value_list, max_num


# create statistics picture
def create_statistics(create_list, huge, date_range, cur_date, num):
    put_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), cur_date)
    range_data = pd.DataFrame(create_list)
    statistics = range_data.set_index("range")
    plt.figure(figsize=(300, 300), dpi=600)  # dpi是分辨率
    y_ticks = np.arange(num)
    plt.yticks(y_ticks)
    statistics.plot(kind='bar', title="statistics: {} {}".format(huge, date_range))
    if not os.path.exists(put_path):
        os.mkdir(put_path)
    plt.savefig("./" + str(datetime.date.today()) + "/{}_{}.png".format(huge, date_range), dpi=600, bbox_inches='tight')
#     plt.show()


def store_list(params):
    select_list = []
    q_30d = pd.read_sql(
        "select m.miner_id, lucky30d_1.lucky_value, lucky30d_1.quality_power_str as store from lucky30d_1 join miners_1 as m on lucky30d_1.refer=m.id where create_at between \'{} 00:00:00\' and \'{} 23:59:59\' and tag=\'qyys\' order by lucky30d_1.lucky_value desc;".format(
            params, params), con=conn)
    for index, row in q_30d.iterrows():
        if 'PiB' in row[2]:
            store_huge = row[2]
            str_list = store_huge[:-4].split('.')
            fir_str = str_list[0]
            sec_str = str_list[1][0]
            search_str = fir_str + '.' + sec_str + '%PiB'
            if search_str not in select_list:
                select_list.append(search_str)
    return select_list


def all_runner(params):
    select_list = store_list(params)
    print(select_list)
    for i in select_list:
        select_str_24h = 'select m.miner_id, lucky24h_1.lucky_value from lucky24h_1 join miners_1 as m on lucky24h_1.refer=m.id where create_at between \'{} 00:00:00\' and \'{} 23:59:59\' and quality_power_str like \'{}\' order by lucky24h_1.lucky_value desc;'.format(
            params, params, i)
        select_str_7d = 'select m.miner_id, lucky7d_1.lucky_value from lucky7d_1 join miners_1 as m on lucky7d_1.refer=m.id where create_at between \'{} 00:00:00\' and \'{} 23:59:59\' and quality_power_str like \'{}\' order by lucky7d_1.lucky_value desc;'.format(
            params, params, i)
        select_str_30d = 'select m.miner_id, lucky30d_1.lucky_value from lucky30d_1 join miners_1 as m on lucky30d_1.refer=m.id where create_at between \'{} 00:00:00\' and \'{} 23:59:59\' and quality_power_str like \'{}\' order by lucky30d_1.lucky_value desc;'.format(
            params, params, i)
        result_24h = select_sql(select_str_24h)
        result_7d = select_sql(select_str_7d)
        result_30d = select_sql(select_str_30d)
        value_24h, max_24h = create_list(result_24h)
        value_7d, max_7d = create_list(result_7d)
        value_30d, max_30d = create_list(result_30d)
        store = i.split("%")[0]
        store_next = store[:-1] + str(int(store[-1]) + 1) + 'PiB'
        store_num = store + "-" + store_next
        create_statistics(value_24h, store_num, "24h", params, max_24h)
        create_statistics(value_7d, store_num, "7d", params, max_7d)
        create_statistics(value_30d, store_num, "30d", params, max_30d)


def miner_value(params):
    cur = conn.cursor(pymysql.cursors.DictCursor)
    total_value = []
    for i in minerid_list:
        current_dict = {}
        select_24h = "select m.miner_id, lucky24h_1.lucky_value, lucky24h_1.quality_power_str from lucky24h_1 join miners_1 as m on lucky24h_1.refer=m.id where create_at between \'{} 00:00:00\' and \'{} 23:59:59\' and m.miner_id=\'{}\';".format(
            params, params, i)
        select_7d = "select m.miner_id, lucky7d_1.lucky_value from lucky7d_1 join miners_1 as m on lucky7d_1.refer=m.id where create_at between \'{} 00:00:00\' and \'{} 23:59:59\' and m.miner_id=\'{}\';".format(
            params, params, i)
        select_30d = "select m.miner_id, lucky30d_1.lucky_value from lucky30d_1 join miners_1 as m on lucky30d_1.refer=m.id where create_at between \'{} 00:00:00\' and \'{} 23:59:59\' and m.miner_id=\'{}\';".format(
            params, params, i)
        cur.execute(select_24h)
        result_24h = cur.fetchall()
        cur.execute(select_7d)
        result_7d = cur.fetchall()
        cur.execute(select_30d)
        result_30d = cur.fetchall()
        current_dict['miner_id'] = i
        current_dict['store'] = result_24h[0]['quality_power_str']
        current_dict['value_24h'] = result_24h[0]['lucky_value']
        current_dict['value_7d'] = result_7d[0]['lucky_value']
        current_dict['value_30d'] = result_30d[0]['lucky_value']
        total_value.append(current_dict)
    return total_value


def main():
    cur_date = str(datetime.date.today())
    all_runner(cur_date)
    # miner_value(cur_date)


if __name__ == "__main__":
    main()
