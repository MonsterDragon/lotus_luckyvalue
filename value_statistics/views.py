import os
import sys
import json
import time
import pymysql
import datetime

from django.shortcuts import render, render_to_response
from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

# Create your views here.

conn = pymysql.connect(
    host="10.1.2.65",
    user="root",
    password="123",
    database="miner_info",
    charset="utf8"
)


class LuckyView(View):

    def get(self, request):
        return render_to_response("show.html")

    def post(self, request):
        lucky_dict = {}
        # cur_date = str(datetime.date.today())
        miner_dict = json.loads(request.body.decode())
        miner_id = miner_dict['miner']
        cur_date = str(miner_dict['date'])
        cur = conn.cursor(pymysql.cursors.DictCursor)
        select_24h = "select m.miner_id, lucky24h_1.lucky_value, lucky24h_1.quality_power_str from lucky24h_1 join miners_1 as m on lucky24h_1.refer=m.id where create_at between \'{} 00:00:00\' and \'{} 23:59:59\' and m.miner_id=\'{}\';".format(
            cur_date, cur_date, miner_id)
        select_7d = "select m.miner_id, lucky7d_1.lucky_value, lucky7d_1.quality_power_str from lucky7d_1 join miners_1 as m on lucky7d_1.refer=m.id where create_at between \'{} 00:00:00\' and \'{} 23:59:59\' and m.miner_id=\'{}\';".format(
            cur_date, cur_date, miner_id)
        select_30d = "select m.miner_id, lucky30d_1.lucky_value from lucky30d_1 join miners_1 as m on lucky30d_1.refer=m.id where create_at between \'{} 00:00:00\' and \'{} 23:59:59\' and m.miner_id=\'{}\';".format(
            cur_date, cur_date, miner_id)
        cur.execute(select_24h)
        result_24h = cur.fetchall()
        print(result_24h)
        cur.execute(select_7d)
        result_7d = cur.fetchall()
        cur.execute(select_30d)
        result_30d = cur.fetchall()
        lucky_dict['miner'] = miner_id
        lucky_dict['con'] = result_7d[0]['quality_power_str']

        if result_24h:
            lucky_dict['24h'] = result_24h[0]['lucky_value']
        else:
            lucky_dict['24h'] = 'null'
        if result_7d:
            lucky_dict['7d'] = result_7d[0]['lucky_value']
        else:
            lucky_dict['7d'] = 'null'
        if result_30d:
            lucky_dict['30d'] = result_30d[0]['lucky_value']
        else:
            lucky_dict['30d'] = 'null'

        store_huge = result_7d[0]['quality_power_str']
        str_list = store_huge[:-4].split('.')
        fir_str = str_list[0]
        sec_str = str_list[1][0]
        search_str = fir_str + '.' + sec_str + '%PiB'
        store = search_str.split("%")[0]
        store_next = store[:-1] + str(int(store[-1]) + 1) + 'PiB'
        store_num = store + "-" + store_next
        path_24h = '/static/' + cur_date + '/' + store_num + '_24h.png'
        path_7d = '/static/' + cur_date + '/' + store_num + '_7d.png'
        path_30d = '/static/' + cur_date + '/' + store_num + '_30d.png'
        lucky_dict['24h_path'] = path_24h
        lucky_dict['7d_path'] = path_7d
        lucky_dict['30d_path'] = path_30d

        return JsonResponse(lucky_dict)
