from database import SqliteConn
import pandas as pd
import pickle
import  random
import numpy as np
from flask import  request
from functools import lru_cache

screnn_mapeer = {
    'checkout_main_screen':'Варианты оплаты',
    'checkout_thankyou_screen':'Спасибо за покупку',
    'checkout_quantity_screen':'Checkout',
    'price_list_screen':'Варианты покупки',
    'deal_details_screen':'Детали акции',
    'cashback_main_screen':'Кэшбэк',
    'profile_screen':'Профиль (Мои купоны)',
    'tours_screen':'Каталог Туров (2-й уровень)',
    'hotels_screen':'Каталог Отелей (2-й уровень)',
    'services_screen':'Каталог Услуг (2-й уровень)',
    'search_screen':'Поиск',
    'tours_root_screen':'Отели и Туры',
    'services_root_screen':'Услуги',
    'main_screen':'Главная'
}

screnn_colors = {
    'checkout_main_screen':'#C8CA4D',
    'checkout_thankyou_screen':'#C8CA4D',
    'checkout_quantity_screen':'#327520',
    'price_list_screen':'#9F35BC',
    'deal_details_screen':'#02DCFC',
    'cashback_main_screen':'#51993B',
    'profile_screen':'#2AD85C',
    'tours_screen':'#67D18F',
    'hotels_screen':'#4C67C5',
    'services_screen':'#E438A9',
    'search_screen':'#64ABB3',
    'tours_root_screen':'#E3C491',
    'services_root_screen':'#95D8B8',
    'main_screen':'#CF1783'
}

colors = [
     '#C8CA4D',
     '#24A03A',
     '#327520',
     '#9F35BC',
     '#02DCFC',
     '#51993B',
     '#2AD85C',
     '#67D18F',
     '#4C67C5',
     '#E438A9',
     '#64ABB3',
     '#E3C491',
     '#95D8B8',
     '#CF1783',
     '#33AF73',
     '#2DBC48'
]


@lru_cache(maxsize=None)
def getNetwork(type,os_name,  date_from , date_to, **args):


    code = args.get('code',None)
    getkey = args.get('getkey',None)

    if(code is None):
        codeSql = ''
    else:
        codeSql = ' AND `from`="{code}" '.format(code=code)



    probadf = pd.read_sql_query('''
        SELECT
            `from` , `to`, max(type) as type,  count(`index`) as proba, date, count( DISTINCT appid) as unique_devices, avg(delayed_second) as avg_delay
        FROM events_chains

        WHERE date BETWEEN '{date_from}' AND '{date_to}'
        AND `from`!=`to`
        AND type='{type}'
        AND os_name='{os_name}'
        {code}
        GROUP BY `from` , `to`
        ORDER BY `from` ,  proba DESC
    '''.format(type=type,date_from=date_from,date_to=date_to, code=codeSql,os_name=os_name), SqliteConn)

    nodeIndex = {}
    nodeColor = {}
    nodeDataArray = []

    events_names = np.unique(np.hstack([probadf['from'].unique(), probadf['to'].unique()]))


    probadf['thick'] = (probadf.proba / probadf.proba.max()) * 20
    probadf['frequency'] =  probadf.proba
    probadf['frequency_percent'] =  (probadf['frequency']/probadf['frequency'].sum())*100
    probadf['unique_devices_percent'] =  (probadf.unique_devices / probadf.unique_devices.sum())*100

    for i, x in enumerate(events_names):
        nodeIndex[x] = i
        nodeColor[x] = colors[i]

        elem = {
            'id': i,
            'text': screnn_mapeer[x],
            'code': x,
            'color': colors[i],
        }

        # if (code != x):
        #     item = probadf[probadf['to'] == x].to_dict('records')[0]
        #
        #     item['avg_delay'] = (item['avg_delay']-probadf['avg_delay'].min()) / (probadf['avg_delay'].max()-probadf['avg_delay'].min())
        #     item['frequency'] = (item['frequency']-probadf['frequency'].min()) / (probadf['frequency'].max()-probadf['frequency'].min())
        #     item['avg_delay'] = random.randint(100,500)
        #     item['frequency'] = (1-item['frequency'])*500
        #
        #     # item['avg_delay'] = ( 1 - (item['avg_delay'] / probadf['avg_delay'].max())  )*800
        #     # item['frequency'] = ( 1 - (item['frequency'] / probadf['frequency'].max())  )*800
        #
        #     elem.update({
        #         'loc':"{} {}".format(item['avg_delay'], item['frequency'])
        #     })

        nodeDataArray.append(elem)

    linkDataArray = []
    for i, rows in probadf.iterrows():

        linkDataArray.append({
            'from': nodeIndex[rows['from']],
            'to': nodeIndex[rows['to']],
            'thick': rows['thick'],
            "progress": "true",
            'curviness': 20,
            'color': nodeColor[rows['from']],
            'frequency': rows['frequency'],
            'frequency_percent': int(rows['frequency_percent']),
            'avg_delay': int(rows['avg_delay']),
            'text': 'time:{}\nfreq:{}%'.format(int(rows['avg_delay']), int(rows['frequency_percent'])),
            'unique_devices': rows['unique_devices'],
            'unique_devices_percent': rows['unique_devices_percent'],
        })

    fullDict = {"class": "go.GraphLinksModel",
                "nodeKeyProperty": "id",
                "nodeDataArray": nodeDataArray,
                "linkDataArray": linkDataArray
                }

    if(getkey!=None):
        return fullDict[getkey]

    return fullDict


def getEventsLineCnt(type,date_from,date_to):

    probadf = pd.read_sql_query('''
            SELECT event_line, count(event_line) as cnt FROM (
                SELECT * FROM events_line
                WHERE event_line!=''
                AND type='{type}' and event_line!='checkout_thankyou_screen'
                AND session_start BETWEEN '{date_from}' AND '{date_to}'
            )
            GROUP BY event_line
            ORDER BY cnt DESC
            LIMIT 30 
    '''.format(type=type,date_from=date_from,date_to=date_to), SqliteConn)
    return probadf


def transitionFrequency(type, date_from, date_to):
    probadf = pd.read_sql_query('''
        SELECT event_len `Кол-во переходов`, count(event_len) as `Частота` FROM (
                      SELECT 
                             event_len 
                      FROM events_line
                      WHERE type='{type}' 
                      AND session_start BETWEEN '{date_from}' AND '{date_to}'
        ) as t
        GROUP BY event_len
        LIMIT 50 
    '''.format(type=type,date_from=date_from,date_to=date_to), SqliteConn)

    return probadf