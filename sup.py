import csv
import json
import logging
import os
import random
import string
import time
import traceback
from typing import *
import pandas as pd
import requests
import ruamel.yaml as yaml
from PIL import Image, ImageFont, ImageDraw
from bs4 import BeautifulSoup
from thefuzz import process, fuzz
import mplfinance as mpf
import matplotlib as mpl
import matplotlib.dates as mdates
import datetime

from typing import List

import adm

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, logger, logger2, \
    desc_list, trans_version_df, npc_cor_list, dogma_list, plaSch_list, traits_list, ship_data_list, plaSch_id_list, skill_dict, skill_point, \
    skill_base_point
'''supporting databases'''
BASE_DATA_PATH = 'supporting_files/data.csv'
BASE_BLP_PATHr = 'supporting_files/blueprints.yaml'
BASE_REGION_PATH = 'supporting_files/region.csv'
BASE_MKTD_PATH = 'supporting_files/md.csv'
BASE_PROD_PATH = 'supporting_files/prod.csv'
BASE_BLPTYPE_PATH = 'supporting_files/blp.csv'
BASE_BLPDETAIL_PATH = 'supporting_files/blpd.yaml'
BASE_ABBR_PATH = 'supporting_files/abbr_list.yaml'
BASE_DESC_PATH = 'supporting_files/description.csv'
BASE_TRANS_PATH = 'supporting_files/trans.csv'
BASE_NPC_COR_PATH = 'supporting_files/npc.csv'
BASE_DOGMA_PATH = 'supporting_files/dogma.csv'
BASE_PLANET_SCH_PATH = 'supporting_files/planetSchematics.yaml'
BASE_PLANET_SCH_NAME_PATH = 'supporting_files/plaSch.csv'
BASE_TRAITS_PATH = 'supporting_files/traits.yaml'
BASE_SHIP_LIST_PATH = 'supporting_files/shipList.csv'
BASE_IMAGE_CACHE_PATH = 'data/images/cache'
BASE_LOG_PATH = 'bot_logs/logs'
BASE_ISSLOG_PATH = 'bot_logs/issue_logs'
BASE_HELPER_PATH = 'sup_images/helper_image.png'
BASE_ADMIN_HELPER_PATH = 'sup_images/helper_admin_image.png'
BASE_SKILL_LIST_PATH = 'supporting_files/skill.yaml'

skill_base_point = [0, 250, 1414, 8000, 45254, 256000]

'''supporting websites(base)'''
# market
BASE_URL_MARKET = 'https://www.ceve-market.org/api/market/region/{reg}/type/{id}.json'
BASE_URL_MARKET_TQ = 'https://www.ceve-market.org/tqapi/market/region/{reg}/type/{id}.json'
BASE_SKILL_MARKET = 'https://www.ceve-market.org/api/market/type/40520.json'
BASE_SKILL_MARKET_TQ = 'https://www.ceve-market.org/tqapi/market/type/40520.json'
BASE_SKILL_S_MARKET = 'https://www.ceve-market.org/api/market/type/45635.json'
BASE_SKILL_S_MARKET_TQ = 'https://www.ceve-market.org/tqapi/market/type/45635.json'
# corporation lp shop offers
BASE_COR_LP_SHOP = 'https://esi.evepc.163.com/latest/loyalty/stores/{corporation_id}/offers/'
COR_LP_MARKET = 'http://101.34.37.178/loyalty/market/corp/{corporation_id}/sorted/?server={server}&from={fm}&amo={amo}'
# search
BASE_SEARCH = 'https://esi.evepc.163.com/latest/search/'
BASE_SEARCH_TQ = 'https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en'
# universal type
BASE_UNI_TYPEID = 'https://esi.evepc.163.com/latest/universe/types/{type_id}/'
# status
BASE_STATUS_SERENITY = 'https://esi.evepc.163.com/latest/status/'
BASE_STATUS_TQ = 'https://esi.evetech.net/latest/status/'
# image server
BASE_IMAGE_SERVER_SERENITY = 'https://image.evepc.163.com/{api_name}/{ID}_{width}.{format}'
BASE_IMAGE_SERVER_TQ = 'https://image.eveonline.com/{api_name}/{ID}_{width}.{format}'
# alliance
BASE_ALLIANCE_SERENITY = 'https://esi.evepc.163.com/latest/alliances/{alliance_id}/'
BASE_ALLIANCE_TQ = 'https://esi.evetech.net/latest/alliances/{alliance_id}/'
# corporation
BASE_COR_SERENITY = 'https://esi.evepc.163.com/latest/corporations/{corporation_id}/'
BASE_COR_TQ = 'https://esi.evetech.net/latest/corporations/{corporation_id}/'
# character
BASE_CHARACTER_SERENITY = 'https://esi.evepc.163.com/latest/characters/{character_id}/'
BASE_CHARACTER_TQ = 'https://esi.evetech.net/latest/characters/{character_id}/'
# universe
BASE_SYS_URL = 'https://esi.evepc.163.com/latest/universe/systems/{id}/'
BASE_TYPE_URL = 'https://esi.evepc.163.com/latest/universe/types/{id}/'
# kb
BASE_KB = 'https://kb.ceve-market.org'
BASE_KB_TQ = 'https://tq.ceve-market.org'
BASE_KB_DETAIL = 'https://kb.ceve-market.org/{type}/{id}/'
BASE_KB_SEARCH = 'https://kb.ceve-market.org/ajax_search/'
BASE_KB_DETAIL_TQ = 'https://tq.ceve-market.org/{type}/{id}/'
BASE_KB_SEARCH_TQ = 'https://tq.ceve-market.org/ajax_search/'
KB_SEARCH_MODEL = 'https://kb.ceve-market.org/ajax_search/#searchtype={searchtype}' \
                  '&name={name}&type={type}&shiptype={shiptype}&ship={ship}&systemtype={systemtype}&system={system}' \
                  '&starttime={starttime}&endtime={endtime}&prev={prev}&next={next}'
KB_SEARCH_MODEL_TQ = 'https://tq.ceve-market.org/ajax_search/#searchtype={searchtype}' \
                     '&name={name}&type={type}&shiptype={shiptype}&ship={ship}&systemtype={systemtype}&system={system}' \
                     '&starttime={starttime}&endtime={endtime}&prev={prev}&next={next}'
KB_PARSER = 'searchtype={searchtype}&name={name}&type={type}&shiptype={shiptype}&ship={ship}&systemtype={systemtype}&system={system}' \
            '&starttime={starttime}&endtime={endtime}&prev={prev}&next={next}'
'''supported apis'''
API_DICT = json.load(
    open(
        'supporting_files/enabled_apis.json',
        mode='r',
        encoding='utf-8'))
API_GROUP_DICT = API_DICT['group']
API_GUILD_DICT = API_DICT['guild']

'''punctuation list'''
PUNC_LIST = [',', '，']

'''font styles'''
simhei_20 = ImageFont.truetype("fonts/msyh.ttc", 20, encoding='utf-8')
simhei_b_20 = ImageFont.truetype('fonts/msyhbd.ttc', 20, encoding='utf-8')
simhei_l_20 = ImageFont.truetype('fonts/msyhl.ttc', 20, encoding='utf-8')
simhei_15 = ImageFont.truetype("fonts/msyh.ttc", 15, encoding='utf-8')
simhei_b_15 = ImageFont.truetype('fonts/msyhbd.ttc', 15, encoding='utf-8')
simhei_l_15 = ImageFont.truetype('fonts/msyhl.ttc', 15, encoding='utf-8')

'''advertisement'''
ADV_TEXT = ""

'''text platform'''
GUILD_HELP = """********************
由于国服代理网易游戏更改了部分舰船翻译，
机器人数据库更新将同步欧服，
并且短期内不会进行翻译跟进
********************
=============
工具列表：
 /help 查看帮助
 /search 搜索
 /desc 查看物品描述
 /trans 翻译
 /status 查询服务器状态
查询功能列表：
  /jita 查询国服伏尔戈市场订单
  /ojita 查询世界服伏尔戈市场订单
  /col 查询国服伏尔戈市场物品组订单
  /ocol 查询世界服伏尔戈市场物品组订单
  /wtb 查询国服特定星域市场订单
  /owtb 查询世界服特定星域市场订单
  /blp 查询蓝图基本属性
  /trait 查询物品加成
  /mkd 查询物品市场分类
  /sch 查询行星资源
=====备注=====
直接发送api获取使用方法
=============
新API服务器：http://101.34.37.178
=============
"""
KM_SHOWING_TEXT = '{victim} 在 {sys} 损失的 {ship} (于{tm})\nKB网链接：{kb_link}\n'
STATUS_TEXT = """服务器当前状态：
宁静服（世界服）：
  在线人数：{online_tq}
  启动时间：{start_tq}
  服务器版本：{version_tq}
晨曦服（国服）：
  在线人数：{online_se}
  启动时间：{start_se}
  服务器版本：{version_se}"""
ALLIANCE_TEXT = """
联盟名：{alliance_name}
联盟缩写：{alliance_ticker}
创建时间：{date_founded}
执行军团名：{executor_corporation_name}
创建者：{creator_name}
创建军团：{creator_corporation_name}
来源：{server}"""
CORPORATION_TEXT = """
军团名：{corporation_name}
军团缩写：{corporation_ticker}
创建时间：{date_founded}
CEO：{ceo_name}
所在联盟：{alliance_name}
创建者：{creator_name}
成员数：{member_count}
来源：{server}"""
CHARACTER_TEXT = """
人物名：{name}
安全等级：{security_status}
所处军团：{corporation_name}
所处联盟：{alliance_name}
性别：{gender}
创建日期：{birthday}
来源：{server}"""
ACC_TEXT = """加速器作用效果：
属性点加成：{point_plus}
--------------
0技能作用时长：{pure_time}
等效技能点：{pure_point}
--------------
生物学V作用时长：{v_time}
等效技能点：{v_point}
--------------
生物学V+BY-810作用时长：{by_time}
等效技能点：{by_point}"""
ACC_MARKET_TEXT = """服务器：{server_name}
加速器价值：
属性点加成：{point_plus}
实际作用时长：{e_time}
--------------
吉他市场大型技能注入器平均价格：{ave_skill}
实际注入技能点：{e_point}
等值技能点价格：{isk_per_point}
--------------
加速器实际增加技能点：{e_point_increase}
加速器预估价值：{expect_worth}"""
HELP_TEXT = """=============
管理员工具
 .admin help 查看管理员帮助列表
工具列表：
 .help 查看帮助
 .iss 留言
 .abtype 添加物品简称
 .abcol 添加物品组简称
 .search 搜索
 .desc 查看物品描述
 .trans 翻译
 .status 查询服务器状态
查询功能列表：
  .jita 查询国服伏尔戈市场订单
  .ojita 查询世界服伏尔戈市场订单
  .col 查询国服伏尔戈市场物品组订单
  .ocol 查询世界服伏尔戈市场物品组订单
  .wtb 查询国服特定星域市场订单
  .owtb 查询世界服特定星域市场订单
  .blp 查询蓝图基本属性
  .mkd 查询物品市场分类
  .blpe 查询蓝图详细信息
  .blpem 查询国服伏尔戈市场蓝图基础材料订单
  .oblpem 查询世界服伏尔戈市场蓝图基础材料订单
  .blpm 查询国服伏尔戈市场蓝图材料订单
  .oblpm 查询世界服伏尔戈市场蓝图材料订单
  .lp 查询国服特定军团伏尔戈市场忠诚点价值（有延迟）
  .olp 查询世界服特定军团伏尔戈市场忠诚点价值（有延迟）
  .dogma 查询物品属性
  .trait 查询物品加成
=====备注=====
api的“.”可以省略
直接发送api获取使用方法
=============
新API服务器：http://101.34.37.178
============="""


# '''image bases'''
# HELP_IMAGE = Image.open(BASE_HELPER_PATH)


def new_log():
    global logger, logger2
    fn = time.strftime('%Y%m%d', time.localtime(time.time())) + 'Issues.log'
    fn2 = time.strftime('%Y%m%d', time.localtime(time.time())) + '.log'
    logger = logging.getLogger('issue_log')
    logger.setLevel(logging.DEBUG)
    log = logging.FileHandler(
        filename="./bot_logs/issue_logs/{}".format(fn),
        mode='a+',
        encoding='utf-8')
    log.setLevel(logging.DEBUG)
    fmtter = logging.Formatter(
        '%(asctime)s|%(levelname)s|%(name)s|%(message)s')
    log.setFormatter(fmtter)
    logger.addHandler(log)
    logger2 = logging.getLogger('main')
    logger2.setLevel(logging.DEBUG)
    log = logging.FileHandler(
        filename="./bot_logs/logs/{}".format(fn2),
        mode='a+',
        encoding='utf-8')
    log.setLevel(logging.DEBUG)
    fmtter = logging.Formatter(
        '%(asctime)s|%(levelname)s|%(name)s|%(message)s')
    log.setFormatter(fmtter)
    logger2.addHandler(log)
    return logger, logger2


def pre_load():
    """
    :::::::: market_type_list: {type_name:id} -> e.g. {'三钛合金':34}
    """
    """
    :yaml:
        --- time:int -- skills Union(level:int, typeID:int) -- materials/products Union(quantity:int typeID:int)
    -> activities -> copying? -> time, materials?, skills?
                  -> manufacturing? -> materials, products, skills, time
                  -> reaction? -> materials, time, skills
                  -> invention? -> materials, products, skills, time
                  -> research_material? -> skills?, time, materials?
                  -> research_time? -> skills?, time, materials?
    -> blueprintTypeID:int
    -> maxProductionLimit:int
    """
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, logger, logger2, \
        desc_list, trans_version_df, npc_cor_list, dogma_list, plaSch_list, traits_list, ship_data_list, plaSch_id_list, skill_dict, skill_point, skill_base_point
    if not os.path.exists(BASE_LOG_PATH):
        os.makedirs(BASE_LOG_PATH)
    if not os.path.exists(BASE_ISSLOG_PATH):
        os.makedirs(BASE_ISSLOG_PATH)
    if not os.path.exists(BASE_IMAGE_CACHE_PATH):
        os.makedirs(BASE_IMAGE_CACHE_PATH)
    fn = time.strftime('%Y%m%d', time.localtime(time.time())) + 'Issues.log'
    fn2 = time.strftime('%Y%m%d', time.localtime(time.time())) + '.log'
    logger = logging.getLogger('issue_log')
    logger.setLevel(logging.DEBUG)
    log = logging.FileHandler(
        filename="./bot_logs/issue_logs/{}".format(fn),
        mode='a+',
        encoding='utf-8')
    log.setLevel(logging.DEBUG)
    fmtter = logging.Formatter(
        '%(asctime)s|%(levelname)s|%(name)s|%(message)s')
    log.setFormatter(fmtter)
    logger.addHandler(log)
    logger2 = logging.getLogger('main')
    logger2.setLevel(logging.DEBUG)
    log = logging.FileHandler(
        filename="./bot_logs/logs/{}".format(fn2),
        mode='a+',
        encoding='utf-8')
    log.setLevel(logging.DEBUG)
    fmtter = logging.Formatter(
        '%(asctime)s|%(levelname)s|%(name)s|%(message)s')
    log.setFormatter(fmtter)
    logger2.addHandler(log)
    with open(BASE_DATA_PATH, mode='r', encoding='utf-8') as data, \
            open(BASE_REGION_PATH, mode='r', encoding='utf-8') as region, \
            open(BASE_MKTD_PATH, mode='r', encoding='utf-8') as mdf, \
            open(BASE_PROD_PATH, mode='r', encoding='utf-8-sig') as pr, \
            open(BASE_BLPTYPE_PATH, mode='r', encoding='utf-8-sig') as bt, \
            open(BASE_BLP_PATHr, mode='r', encoding='utf-8') as blpf, \
            open(BASE_BLPDETAIL_PATH, mode='r', encoding='utf-8') as blpd, \
            open(BASE_ABBR_PATH, mode='r', encoding='utf-8') as abbr, \
            open(BASE_DESC_PATH, mode='r', encoding='utf-8') as descf, \
            open(BASE_NPC_COR_PATH, mode='r', encoding='utf-8') as npcf, \
            open(BASE_DOGMA_PATH, mode='r', encoding='utf-8') as dgm, \
            open(BASE_PLANET_SCH_PATH, mode='r', encoding='utf-8') as plcf, \
            open(BASE_TRAITS_PATH, mode='r', encoding='utf-8') as traitf, \
            open(BASE_SHIP_LIST_PATH, mode='r', encoding='utf-8') as slpf, \
            open(BASE_PLANET_SCH_NAME_PATH, mode='r', encoding='utf-8') as psnpf, \
            open(BASE_SKILL_LIST_PATH, mode='r', encoding='utf-8') as skf:
        c = csv.reader(data)
        keys = next(c)
        data_list = {}
        id_list = {}
        for row in c:
            data_list[row[0]] = row[1]
            id_list[row[1]] = row[0]
        rr = csv.reader(region)
        keys = next(rr)
        reg_list = {}
        for row in rr:
            reg_list[row[1]] = row[0]
        m = csv.reader(mdf)
        keys = next(m)
        market_type_list = {}
        mkd_list = {}
        for row in m:
            mkd_list[row[0]] = row[2:]
            market_type_list[row[0]] = row[1]
        p = csv.reader(pr)
        keys = next(p)
        prod_list = {}
        for row in p:
            prod_list[row[0]] = row[1]
        t = csv.reader(bt)
        keys = next(t)
        blpt_list = {}
        for row in t:
            blpt_list[row[1]] = row[0]
        desc_list = {}
        des = csv.reader(descf)
        keys = next(des)
        for row in des:
            desc_list[row[0]] = row[1]
        ncf = csv.reader(npcf)
        keys = next(ncf)
        npc_cor_list = {}
        for row in ncf:
            npc_cor_list[row[1]] = row[0]
        dcf = csv.reader(dgm)
        keys = next(dcf)
        dogma_list = {}
        for row in dcf:
            dogma_list[row[0]] = row[1]
        s = csv.reader(slpf)
        ship_data_list = {}
        for row in s:
            ship_data_list[row[0]] = row[1]
        p = csv.reader(psnpf)
        keys = next(p)
        plaSch_id_list = {}
        for row in p:
            plaSch_id_list[row[1]] = row[0]
        blp_list = yaml.safe_load(blpf)
        blp_detail_list = yaml.safe_load(blpd)
        abbr_list = yaml.safe_load(abbr)
        trans_version_df = pd.read_csv(
            BASE_TRANS_PATH, header=0, encoding='utf-8')
        # print(blp_list)
        plaSch_list = yaml.safe_load(plcf)
        traits_list = yaml.safe_load(traitf)
        skill_dict = yaml.safe_load(skf)
        del c, rr, m, p, t
        return market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, \
               abbr_list, desc_list, trans_version_df, npc_cor_list, dogma_list, plaSch_list, traits_list, ship_data_list, plaSch_id_list, logger, logger2, skill_dict


def admin(command: list, group_id: int, sender: dict, *args, **kwargs):
    print('using admin')
    command = command[0].split(' ')
    if command[0]:
        adm.admin(command[0], command[1:], group_id, sender['user_id'])
    else:
        text = '请指定二级调用'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'image', 'data': {'type': 'image', "file": f"{BASE_ADMIN_HELPER_PATH}"}}]}, 'echo': 'apiCallBack'}


def marketing(region, typename, server='zh'):
    """
    :param typename: the name of the thing you want to check
    :param region: the name of the region you want to search in
    :param server: 'zh' for chinese server and 'tq' for universal server
    :return: a dict in type of json
    """
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, desc_list, dogma_list, logger
    try:
        type_id = market_type_list[typename]
        reg_id = reg_list[region]
        # print(type_id, reg_id)
        req_url = (
            BASE_URL_MARKET if server == 'zh' else BASE_URL_MARKET_TQ).format(
            id=type_id, reg=reg_id)
        # print('request url', req_url)
        data = requests.get(req_url).json()
        # print('market:', data)
    except BaseException as e:
        logger.warning(f"Error getting market data from {typename}: {e}")
        data = {
            "all": {
                "max": 0, "min": 0, "volume": 0}, "buy": {
                "max": 0, "min": 0, "volume": 0}, "sell": {
                "max": 0, "min": 0, "volume": 0}}
    return data


def help(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    print('using help')
    if len(command) < 1 or command[0] == "" or (
            command[0] not in API_GROUP_DICT.keys() and command[0] not in API_GROUP_DICT.values()):
        # text = HELP_TEXT
        if group_id == -1:
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'text', 'data': {"text": GUILD_HELP}}]}, 'echo': 'apiCallBack'}
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'image', 'data': {'type': 'image', "file": f"{BASE_HELPER_PATH}"}}]}, 'echo': 'apiCallBack'}
    elif command[0] in API_GROUP_DICT.keys():
        rt = eval(command[0][1:] + "([]," + str(group_id) + ")")
        return rt
    else:
        rt = eval(command[0] + "([]," + str(group_id) + ")")
        return rt


def kb(command: list, group_id: int, *args, **kwargs) -> dict:
    print('using kb')
    tp = ('char', 'alli', 'corp')
    if len(command) < 1 or command[0] == "":
        text = '用法(kb)：.kb 查询名（，类型<char, corp, alli> 默认为char）'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}},
        ]}, 'echo': 'apiCallBack'}
    else:
        _to_search = command[0]
        _type = command[1] if len(command) > 1 else 'char'
        if _type not in tp:
            text = '参数有误'
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'text', 'data': {'text': text}},
            ]}, 'echo': 'apiCallBack'}
        req_url = KB_SEARCH_MODEL.format(searchtype=_type, name=_to_search, type='lost', shiptype='shiptype', ship='', systemtype='sys', system='',
                                         starttime='', endtime='',
                                         prev='', next='')
        sess = requests.session()
        _re = sess.get('https://kb.ceve-market.org')
        _re = sess.get('https://kb.ceve-market.org/ajax_search/')
        _re = sess.get(req_url)
        header = {'accept': 'text/html, */*; q=0.01',
                  'accept-encoding': 'gzip, deflate, br',
                  'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                  'content-length': '218',
                  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                  'dnt': '1',
                  'origin': 'https://kb.ceve-market.org',
                  'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
                  'sec-ch-ua-mobile': '?0',
                  'sec-ch-ua-platform': 'Windows',
                  'sec-fetch-dest': 'empty',
                  'sec-fetch-mode': 'cors',
                  'sec-fetch-site': 'same-origin',
                  'sec-gpc': '1',
                  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77',
                  'x-csrftoken': _re.cookies['csrftoken'],
                  'referer': 'https://kb.ceve-market.org/ajax_search/',
                  'x-requested-with': 'XMLHttpRequest'}
        html_rec = sess.post(req_url, headers=header,
                             data=KB_PARSER.format(searchtype=_type, name=_to_search, type='lost', shiptype='shiptype', ship='', systemtype='sys',
                                                   system='', starttime='',
                                                   endtime='', prev='',
                                                   next='').encode('utf-8'))
        b_search_result = BeautifulSoup(html_rec.text, 'html.parser')
        try:
            _to_link = b_search_result.table.select('.kb-table-cell')[1].select('a')[tp.index(_type)].attrs['href']
        except IndexError:
            text = '未查询到相关记录，可能为角色id错误或30天内没有击毁记录'
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'text', 'data': {'text': text}},
            ]}, 'echo': 'apiCallBack'}
        _in_to_link = BASE_KB + _to_link
        _relink_res = requests.get(_in_to_link)
        _relink_soup = BeautifulSoup(_relink_res.text, 'html.parser')
        text = '\n'
        base_kb = _relink_soup.select_one('.nobackground').find(class_='content').find(class_='col-lg-10').p
        text += ''.join(x.text.replace(' ', '').replace('\n', '') for x in base_kb.contents)
        _ph_link = 'https:' + _relink_soup.select_one('.nobackground').find(class_='content').find(class_='col-lg-10').div.h1.img.attrs['src']
        __tplnk = _relink_soup.select_one('.nobackground').find(class_='content').find(class_='col-lg-10').select_one('h4').select('a')
        latest_lost_web_link = _in_to_link + '/losts/'
        _lost_res = requests.get(latest_lost_web_link)
        _lost_soup = BeautifulSoup(_lost_res.text, 'html.parser')
        latest_atk_web_link = _in_to_link + '/atk/'
        _atk_res = requests.get(latest_atk_web_link)
        _atk_soup = BeautifulSoup(_atk_res.text, 'html.parser')
        text += '\n===最新击坠===\n'
        try:
            latest_kill_link = BASE_KB + \
                               _relink_soup.select_one('.nobackground').find(class_='content').find(class_='col-lg-10').select_one(
                                   'table#kbtable.table.table-striped.table-hover') \
                                   .tbody.tr.attrs['onclick'][13:-2]
            lt_kill_km_link = BeautifulSoup(requests.get(latest_kill_link).text, 'html.parser') \
                .select_one('div.container.nobackground').select_one('div.content').div.h3.small.a.attrs['href']
            try:
                lt_kill_km_json = requests.get(lt_kill_km_link).json()
            except:
                lt_kill_km_link = BeautifulSoup(requests.get(latest_kill_link).text, 'html.parser') \
                    .select_one('div.container.nobackground').select_one('div.content').div.h3.small.select('a')[1].attrs['href']
                lt_kill_km_json = requests.get(lt_kill_km_link).json()
            kill_text = KM_SHOWING_TEXT.format(
                victim=requests.get(BASE_CHARACTER_SERENITY.format(character_id=lt_kill_km_json['victim']['character_id'])).json()['name'],
                sys=requests.get(BASE_SYS_URL.format(id=lt_kill_km_json['solar_system_id']), params={'language': 'zh'}).json()['name'],
                ship=requests.get(BASE_TYPE_URL.format(id=lt_kill_km_json['victim']['ship_type_id']), params={'language': 'zh'}).json()['name'],
                tm=lt_kill_km_json['killmail_time'],
                kb_link=latest_kill_link)
            text += kill_text
        except AttributeError:
            latest_kill_link = latest_kill_km_link = ''
        text += '===最新损失===\n'
        try:
            latest_lost_link = BASE_KB + \
                               _lost_soup.select_one('.nobackground').find(class_='content').find(class_='col-lg-10').select_one(
                                   'table#kbtable.table.table-striped.table-hover') \
                                   .tbody.tr.attrs['onclick'][13:-2]
            lt_lost_km_link = BeautifulSoup(requests.get(latest_lost_link).text, 'html.parser') \
                .select_one('div.container.nobackground').select_one('div.content').div.h3.small.a.attrs['href']
            try:
                lt_lost_km_json = requests.get(lt_lost_km_link).json()
            except:
                lt_lost_km_link = BeautifulSoup(requests.get(latest_lost_link).text, 'html.parser') \
                    .select_one('div.container.nobackground').select_one('div.content').div.h3.small.select('a')[1].attrs['href']
                lt_lost_km_json = requests.get(lt_lost_km_link).json()
            lost_text = KM_SHOWING_TEXT.format(
                victim=requests.get(BASE_CHARACTER_SERENITY.format(character_id=lt_lost_km_json['victim']['character_id'])).json()['name'],
                sys=requests.get(BASE_SYS_URL.format(id=lt_lost_km_json['solar_system_id']), params={'language': 'zh'}).json()['name'],
                ship=requests.get(BASE_TYPE_URL.format(id=lt_lost_km_json['victim']['ship_type_id']), params={'language': 'zh'}).json()['name'],
                tm=lt_lost_km_json['killmail_time'],
                kb_link=latest_lost_link)
            text += lost_text
        except AttributeError:
            lt_lost_km_link = latest_lost_link = ''
        text += '===参与击坠===\n'
        try:
            latest_atk_link = BASE_KB + \
                              _atk_soup.select_one('.nobackground').find(class_='content').find(class_='col-lg-10').select_one(
                                  'table#kbtable.table.table-striped.table-hover') \
                                  .tbody.tr.attrs['onclick'][13:-2]
            lt_atk_km_link = BeautifulSoup(requests.get(latest_atk_link).text, 'html.parser') \
                .select_one('div.container.nobackground').select_one('div.content').div.h3.small.a.attrs['href']
            try:
                lt_atk_km_json = requests.get(lt_atk_km_link).json()
            except:
                lt_atk_km_link = BeautifulSoup(requests.get(latest_lost_link).text, 'html.parser') \
                    .select_one('div.container.nobackground').select_one('div.content').div.h3.small.select('a')[1].attrs['href']
                lt_atk_km_json = requests.get(lt_atk_km_link).json()
            atk_text = KM_SHOWING_TEXT.format(
                victim=requests.get(BASE_CHARACTER_SERENITY.format(character_id=lt_atk_km_json['victim']['character_id'])).json()['name'],
                sys=requests.get(BASE_SYS_URL.format(id=lt_atk_km_json['solar_system_id']), params={'language': 'zh'}).json()['name'],
                ship=requests.get(BASE_TYPE_URL.format(id=lt_atk_km_json['victim']['ship_type_id']), params={'language': 'zh'}).json()['name'],
                tm=lt_atk_km_json['killmail_time'],
                kb_link=latest_atk_link)
            text += atk_text
        except AttributeError:
            traceback.print_exc()
            lt_lost_km_link = latest_atk_link = ''
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': '国服数据：\n'}},
            {'type': 'image', 'data': {'url': _ph_link}},
            {'type': 'text', 'data': {'text': text}},
            {'type': 'text', 'data': {'text': f'\n数据来源自 {BASE_KB}'}}
        ]}, 'echo': 'apiCallBack'}


def okb(command: list, group_id: int, *args, **kwargs) -> dict:
    print('using okb')
    tp = ('char', 'alli', 'corp')
    if len(command) < 1 or command[0] == "":
        text = '用法(okb)：.okb 查询名（，类型<char, corp, alli> 默认为char）'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}},
        ]}, 'echo': 'apiCallBack'}
    else:
        _to_search = command[0]
        _type = command[1] if len(command) > 1 else 'char'
        if _type not in tp:
            text = '参数有误'
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'text', 'data': {'text': text}},
            ]}, 'echo': 'apiCallBack'}
        req_url = KB_SEARCH_MODEL_TQ.format(searchtype=_type, name=_to_search, type='lost', shiptype='shiptype', ship='', systemtype='sys', system='',
                                            starttime='', endtime='',
                                            prev='', next='')
        sess = requests.session()
        _re = sess.get('https://tq.ceve-market.org')
        _re = sess.get('https://tq.ceve-market.org/ajax_search/')
        _re = sess.get(req_url)
        header = {'accept': 'text/html, */*; q=0.01',
                  'accept-encoding': 'gzip, deflate, br',
                  'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                  'content-length': '218',
                  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                  'dnt': '1',
                  'origin': 'https://tq.ceve-market.org',
                  'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
                  'sec-ch-ua-mobile': '?0',
                  'sec-ch-ua-platform': 'Windows',
                  'sec-fetch-dest': 'empty',
                  'sec-fetch-mode': 'cors',
                  'sec-fetch-site': 'same-origin',
                  'sec-gpc': '1',
                  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77',
                  'x-csrftoken': _re.cookies['csrftoken'],
                  'referer': 'https://tq.ceve-market.org/ajax_search/',
                  'x-requested-with': 'XMLHttpRequest'}
        html_rec = sess.post(req_url, headers=header,
                             data=KB_PARSER.format(searchtype=_type, name=_to_search, type='lost', shiptype='shiptype', ship='', systemtype='sys',
                                                   system='', starttime='',
                                                   endtime='', prev='',
                                                   next='').encode('utf-8'))
        # print(html_rec.text)
        b_search_result = BeautifulSoup(html_rec.text, 'html.parser')
        try:
            _to_link = b_search_result.table.select('.kb-table-cell')[1].select('a')[tp.index(_type)].attrs['href']
        except IndexError:
            text = '未查询到相关记录，可能为角色id错误或30天内没有击毁记录'
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'text', 'data': {'text': text}},
            ]}, 'echo': 'apiCallBack'}
        _in_to_link = BASE_KB_TQ + _to_link
        _relink_res = requests.get(_in_to_link)
        _relink_soup = BeautifulSoup(_relink_res.text, 'html.parser')
        text = '\n'
        base_kb = _relink_soup.select_one('.nobackground').find(class_='content').find(class_='col-lg-10').p
        text += ''.join(x.text.replace(' ', '').replace('\n', '') for x in base_kb.contents)
        _ph_link = 'https:' + _relink_soup.select_one('.nobackground').find(class_='content').find(class_='col-lg-10').div.h1.img.attrs['src']
        __tplnk = _relink_soup.select_one('.nobackground').find(class_='content').find(class_='col-lg-10').select_one('h4').select('a')
        latest_lost_web_link = _in_to_link + '/losts/'
        _lost_res = requests.get(latest_lost_web_link)
        _lost_soup = BeautifulSoup(_lost_res.text, 'html.parser')
        latest_atk_web_link = _in_to_link + '/atk/'
        _atk_res = requests.get(latest_atk_web_link)
        _atk_soup = BeautifulSoup(_atk_res.text, 'html.parser')
        text += '\n===最新击坠===\n'
        try:
            latest_kill_link = BASE_KB_TQ + \
                               _relink_soup.select_one('.nobackground').find(class_='content').find(class_='col-lg-10').select_one(
                                   'table#kbtable.table.table-striped.table-hover') \
                                   .tbody.tr.attrs['onclick'][13:-2]
            lt_kill_km_link = BeautifulSoup(requests.get(latest_kill_link).text, 'html.parser') \
                .select_one('div.container.nobackground').select_one('div.content').div.h3.small.a.attrs['href']
            try:
                lt_kill_km_json = requests.get(lt_kill_km_link).json()
            except:
                lt_kill_km_link = BeautifulSoup(requests.get(latest_kill_link).text, 'html.parser') \
                    .select_one('div.container.nobackground').select_one('div.content').div.h3.small.select('a')[1].attrs['href']
                lt_kill_km_json = requests.get(lt_kill_km_link).json()
            kill_text = KM_SHOWING_TEXT.format(
                victim=requests.get(BASE_CHARACTER_TQ.format(character_id=lt_kill_km_json['victim']['character_id'])).json()['name'],
                sys=requests.get(BASE_SYS_URL.format(id=lt_kill_km_json['solar_system_id']), params={'language': 'zh'}).json()['name'],
                ship=requests.get(BASE_TYPE_URL.format(id=lt_kill_km_json['victim']['ship_type_id']), params={'language': 'zh'}).json()['name'],
                tm=lt_kill_km_json['killmail_time'],
                kb_link=latest_kill_link)
            text += kill_text
        except AttributeError:
            latest_kill_link = latest_kill_km_link = ''
        text += '===最新损失===\n'
        try:
            latest_lost_link = BASE_KB_TQ + \
                               _lost_soup.select_one('.nobackground').find(class_='content').find(class_='col-lg-10').select_one(
                                   'table#kbtable.table.table-striped.table-hover') \
                                   .tbody.tr.attrs['onclick'][13:-2]
            lt_lost_km_link = BeautifulSoup(requests.get(latest_lost_link).text, 'html.parser') \
                .select_one('div.container.nobackground').select_one('div.content').div.h3.small.a.attrs['href']
            # print(latest_lost_link, lt_lost_km_link)
            try:
                lt_lost_km_json = requests.get(lt_lost_km_link).json()
            except:
                lt_lost_km_link = BeautifulSoup(requests.get(latest_lost_link).text, 'html.parser') \
                    .select_one('div.container.nobackground').select_one('div.content').div.h3.small.select('a')[1].attrs['href']
                lt_lost_km_json = requests.get(lt_lost_km_link).json()
            lost_text = KM_SHOWING_TEXT.format(
                victim=requests.get(BASE_CHARACTER_TQ.format(character_id=lt_lost_km_json['victim']['character_id'])).json()['name'],
                sys=requests.get(BASE_SYS_URL.format(id=lt_lost_km_json['solar_system_id']), params={'language': 'zh'}).json()['name'],
                ship=requests.get(BASE_TYPE_URL.format(id=lt_lost_km_json['victim']['ship_type_id']), params={'language': 'zh'}).json()['name'],
                tm=lt_lost_km_json['killmail_time'],
                kb_link=latest_lost_link)
            text += lost_text
        except AttributeError:
            lt_lost_km_link = latest_lost_link = ''
        text += '===参与击坠===\n'
        try:
            latest_atk_link = BASE_KB_TQ + \
                              _atk_soup.select_one('.nobackground').find(class_='content').find(class_='col-lg-10').select_one(
                                  'table#kbtable.table.table-striped.table-hover') \
                                  .tbody.tr.attrs['onclick'][13:-2]
            lt_atk_km_link = BeautifulSoup(requests.get(latest_atk_link).text, 'html.parser') \
                .select_one('div.container.nobackground').select_one('div.content').div.h3.small.a.attrs['href']
            # print(latest_atk_link, lt_atk_km_link)
            try:
                lt_atk_km_json = requests.get(lt_atk_km_link).json()
            except:
                lt_atk_km_link = BeautifulSoup(requests.get(latest_atk_link).text, 'html.parser') \
                    .select_one('div.container.nobackground').select_one('div.content').div.h3.small.select('a')[1].attrs['href']
                lt_atk_km_json = requests.get(lt_atk_km_link).json()
            atk_text = KM_SHOWING_TEXT.format(
                victim=requests.get(BASE_CHARACTER_TQ.format(character_id=lt_atk_km_json['victim']['character_id'])).json()['name'],
                sys=requests.get(BASE_SYS_URL.format(id=lt_atk_km_json['solar_system_id']), params={'language': 'zh'}).json()['name'],
                ship=requests.get(BASE_TYPE_URL.format(id=lt_atk_km_json['victim']['ship_type_id']), params={'language': 'zh'}).json()['name'],
                tm=lt_atk_km_json['killmail_time'],
                kb_link=latest_atk_link)
            text += atk_text
        except AttributeError:
            lt_lost_km_link = latest_atk_link = ''
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': '世界服数据：\n'}},
            {'type': 'image', 'data': {'url': _ph_link}},
            {'type': 'text', 'data': {'text': text}},
            {'type': 'text', 'data': {'text': f'\n数据来源自 {BASE_KB_TQ}'}}
        ]}, 'echo': 'apiCallBack'}


def status(command: list, group_id: int, *args, **kwargs) -> dict:
    print('using status')
    try:
        r1 = requests.get(BASE_STATUS_SERENITY, timeout=2).json()
    except requests.exceptions.ReadTimeout:
        r1 = {'players': None, 'start_time': None, 'server_version': None}
    # r2 = requests.get(BASE_STATUS_TQ, timeout=2).json()
    try:
        r2 = requests.get(BASE_STATUS_TQ, timeout=2).json()
    except requests.exceptions.ReadTimeout:
        r2 = {'players': None, 'start_time': None, 'server_version': None}
    text = STATUS_TEXT.format(online_tq=r2['players'], start_tq=r2['start_time'], version_tq=r2['server_version'],
                              online_se=r1['players'], start_se=r1['start_time'], version_se=r1['server_version'])
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def iss(command: list, group_id: int, sender: dict, *args, **kwargs) -> dict:
    global logger, logger2
    print('using iss')
    log_text = ",".join(
        command) + "<Sender:{0}<<Group:{1}".format(sender['user_id'], group_id)
    logger.info(log_text)
    text = '已提交'
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def iAll(command: list, group_id: int, *args, **kwargs) -> dict:
    print('using iAll')
    if len(command) < 1 or len(command[0]) < 3:
        text = '用法(iAll)：.iAll 想要查询的联盟(大于等于3个字符)'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        all_id = requests.get(BASE_SEARCH, params={
            'categories': 'alliance',
            'language': 'zh',
            'strict': 'true',
            'search': command[0]
        }).json()
        if all_id == {}:
            all_id = requests.get(BASE_SEARCH, params={
                'categories': 'alliance',
                'language': 'zh',
                'strict': 'false',
                'search': command[0]
            }).json()
        if all_id == {}:
            text = '名称未搜索到'
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [{'type': 'text', 'data': {'text': text}}]},
                    'echo': 'apiCallBack'}
        all_id = all_id['alliance'][0]
        all_data = requests.get(BASE_ALLIANCE_SERENITY.format(alliance_id=all_id)).json()
        # text = '联盟名：{}'
        text = ALLIANCE_TEXT.format(alliance_name=all_data['name'],
                                    alliance_ticker=all_data['ticker'],
                                    date_founded=all_data['date_founded'],
                                    creator_name=requests.get(BASE_CHARACTER_SERENITY.format(character_id=all_data['creator_id'])).json()['name'],
                                    creator_corporation_name=
                                    requests.get(BASE_COR_SERENITY.format(corporation_id=all_data['creator_corporation_id'])).json()['name'],
                                    executor_corporation_name=
                                    requests.get(BASE_COR_SERENITY.format(corporation_id=all_data['executor_corporation_id'])).json()['name'],
                                    server='晨曦')
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'image', 'data': {'file': BASE_IMAGE_SERVER_SERENITY.format(api_name='Alliance', ID=all_id, width=128, format='png')}},
            {'type': 'text', 'data': {'text': text}}
        ]}}


def oiAll(command: list, group_id: int, *args, **kwargs) -> dict:
    print('using oiAll')
    if len(command) < 1 or len(command[0]) == '':
        text = '用法(oiAll)：.oiAll 想要查询的联盟精确名'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        all_name = command[0]
        al_rcv: dict = requests.post(BASE_SEARCH_TQ, data=json.dumps([all_name])).json()
        if 'alliances' in al_rcv.keys():
            all_id = al_rcv['alliances'][0]['id']
        else:
            text = f'未搜寻到联盟 {command[0]}'
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
        all_data = requests.get(BASE_ALLIANCE_TQ.format(alliance_id=all_id)).json()
        # text = '联盟名：{}'
        # if 'error' in all_data.keys():
        #     text = 'ID错误'
        #     return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [{'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
        text = ALLIANCE_TEXT.format(alliance_name=all_data['name'],
                                    alliance_ticker=all_data['ticker'],
                                    date_founded=all_data['date_founded'],
                                    creator_name=requests.get(BASE_CHARACTER_TQ.format(character_id=all_data['creator_id'])).json()['name'],
                                    creator_corporation_name=
                                    requests.get(BASE_COR_TQ.format(corporation_id=all_data['creator_corporation_id'])).json()['name'],
                                    executor_corporation_name=
                                    requests.get(BASE_COR_TQ.format(corporation_id=all_data['executor_corporation_id'])).json()['name'],
                                    server='宁静')
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'image', 'data': {'file': BASE_IMAGE_SERVER_TQ.format(api_name='Alliance', ID=all_id, width=128, format='png')}},
            {'type': 'text', 'data': {'text': text}}
        ]}}


def iCor(command: list, group_id: int, *args, **kwargs) -> dict:
    print('using iCor')
    if len(command) < 1 or len(command[0]) < 3:
        text = '用法(iCor)：.iCor 想要查询的军团(大于等于3个字符)'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        cor_id = requests.get(BASE_SEARCH, params={
            'categories': 'corporation',
            'language': 'zh',
            'strict': 'true',
            'search': command[0]
        }).json()
        if cor_id == {}:
            cor_id = requests.get(BASE_SEARCH, params={
                'categories': 'corporation',
                'language': 'zh',
                'strict': 'false',
                'search': command[0]
            }).json()
        if cor_id == {}:
            text = '名称未搜索到'
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [{'type': 'text', 'data': {'text': text}}]},
                    'echo': 'apiCallBack'}
        cor_id = cor_id['corporation'][0]
        cor_data: dict = requests.get(BASE_COR_SERENITY.format(corporation_id=cor_id)).json()
        text = CORPORATION_TEXT.format(
            corporation_name=cor_data['name'],
            corporation_ticker=cor_data['ticker'],
            date_founded='未知' if 'date_founded' not in cor_data.keys() else cor_data['date_founded'],
            ceo_name=requests.get(BASE_CHARACTER_SERENITY.format(character_id=cor_data['ceo_id'])).json()['name'],
            alliance_name='无' if 'alliance_id' not in cor_data.keys() else
            requests.get(BASE_ALLIANCE_SERENITY.format(alliance_id=cor_data['alliance_id'])).json()['name'],
            creator_name='未知' if 'name' not in requests.get(BASE_CHARACTER_SERENITY.format(character_id=cor_data['creator_id'])).json().keys()
            else requests.get(BASE_CHARACTER_SERENITY.format(character_id=cor_data['creator_id'])).json()['name'],
            member_count=cor_data['member_count'],
            server='晨曦'
        )
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'image', 'data': {'file': BASE_IMAGE_SERVER_SERENITY.format(api_name='Corporation', ID=cor_id, width=128, format='png')}},
            {'type': 'text', 'data': {'text': text}}
        ]}}


def oiCor(command: list, group_id: int, *args, **kwargs) -> dict:
    print('using oiCor')
    if len(command) < 1 or len(command[0]) < 5:
        text = '用法(oiCor)：.oiCor 想要查询的军团精确名'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        cor_name = command[0]
        cor_rcv: dict = requests.post(BASE_SEARCH_TQ, data=json.dumps([cor_name])).json()
        if 'corporations' in cor_rcv.keys():
            cor_id = cor_rcv['corporations'][0]['id']
        else:
            text = f'未搜寻到军团 {command[0]}'
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
        cor_data = requests.get(BASE_COR_TQ.format(corporation_id=cor_id)).json()
        text = CORPORATION_TEXT.format(
            corporation_name=cor_data['name'],
            corporation_ticker=cor_data['ticker'],
            date_founded=cor_data['date_founded'],
            ceo_name=requests.get(BASE_CHARACTER_TQ.format(character_id=cor_data['ceo_id'])).json()['name'],
            alliance_name='无' if 'alliance_id' not in cor_data.keys() else
            requests.get(BASE_ALLIANCE_TQ.format(alliance_id=cor_data['alliance_id'])).json()['name'],
            creator_name='未知' if 'name' not in requests.get(BASE_CHARACTER_TQ.format(character_id=cor_data['creator_id'])).json().keys()
            else requests.get(BASE_CHARACTER_TQ.format(character_id=cor_data['creator_id'])).json()['name'],
            member_count=cor_data['member_count'],
            server='宁静'
        )
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'image', 'data': {'file': BASE_IMAGE_SERVER_TQ.format(api_name='Corporation', ID=cor_id, width=128, format='png')}},
            {'type': 'text', 'data': {'text': text}}
        ]}}


def iCha(command: list, group_id: int, *args, **kwargs) -> dict:
    print('using iCha')
    if len(command) < 1 or len(command[0]) < 3:
        text = '用法(iCha)：.iCha 想要查询的人物名(大于等于3个字符)'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        cha_id = requests.get(BASE_SEARCH, params={
            'categories': 'character',
            'language': 'zh',
            'strict': 'true',
            'search': command[0]
        }).json()
        if cha_id == {}:
            cha_id = requests.get(BASE_SEARCH, params={
                'categories': 'character',
                'language': 'zh',
                'strict': 'false',
                'search': command[0]
            }).json()
        if cha_id == {}:
            text = '名称未搜索到'
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [{'type': 'text', 'data': {'text': text}}]},
                    'echo': 'apiCallBack'}
        cha_id = cha_id['character'][0]
        cha_data = requests.get(BASE_CHARACTER_SERENITY.format(character_id=cha_id)).json()
        text = CHARACTER_TEXT.format(name=cha_data['name'],
                                     security_status=cha_data['security_status'],
                                     corporation_name=requests.get(BASE_COR_SERENITY.format(corporation_id=cha_data['corporation_id'])).json()[
                                         'name'],
                                     alliance_name='无' if 'alliance_id' not in cha_data.keys()
                                     else requests.get(BASE_ALLIANCE_SERENITY.format(alliance_id=cha_data['alliance_id'])).json()['name'],
                                     gender=cha_data['gender'],
                                     birthday=cha_data['birthday'],
                                     server='晨曦')
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'image', 'data': {'file': BASE_IMAGE_SERVER_SERENITY.format(api_name='Character', ID=cha_id, width=128, format='jpg')}},
            {'type': 'text', 'data': {'text': text}}
        ]}}


def oiCha(command: list, group_id: int, *args, **kwargs) -> dict:
    print('using oiCha')
    if len(command) < 1 or len(command[0]) < 3:
        text = '用法(oiCha)：.oiCha 想要查询的人物代号(应为数字)'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        cha_name = command[0]
        cha_rcv: dict = requests.post(BASE_SEARCH_TQ, data=json.dumps([cha_name])).json()
        if 'characters' in cha_rcv.keys():
            cha_id = cha_rcv['characters'][0]['id']
        else:
            text = f'未搜寻到角色 {command[0]}'
            return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
        cha_data = requests.get(BASE_CHARACTER_TQ.format(character_id=cha_id)).json()
        text = CHARACTER_TEXT.format(name=cha_data['name'],
                                     security_status=cha_data['security_status'],
                                     corporation_name=requests.get(BASE_COR_TQ.format(corporation_id=cha_data['corporation_id'])).json()['name'],
                                     alliance_name='无' if 'alliance_id' not in cha_data.keys()
                                     else requests.get(BASE_ALLIANCE_TQ.format(alliance_id=cha_data['alliance_id'])).json()['name'],
                                     gender=cha_data['gender'],
                                     birthday=cha_data['birthday'],
                                     server='宁静')
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'image', 'data': {'file': BASE_IMAGE_SERVER_TQ.format(api_name='Character', ID=cha_id, width=128, format='jpg')}},
            {'type': 'text', 'data': {'text': text}}
        ]}}


def search(command: list, group_id: int, *args, **kwargs) -> dict:
    print('using search')
    if len(command) < 1 or len(command[0]) < 3:
        text = '用法(search)：.search 想要搜索的字符串(大于等于3个字符)（，条目数量<不超过8>）'
    else:
        text = '搜索结果：'
        eve_search_res = requests.get(
            BASE_SEARCH,
            params={
                'categories': 'inventory_type',
                'language': 'zh',
                'strict': 'false',
                'search': command[0]}).json()
        tm_sea = 6 if len(command) == 1 else min(int(command[1]), 8)
        if 'inventory_type' not in eve_search_res.keys():
            eve_search_res['inventory_type'] = []
        if len(eve_search_res['inventory_type']) > tm_sea:
            eve_search_res['inventory_type'] = eve_search_res['inventory_type'][:tm_sea]
        text += "\n EVE api 搜索结果：\n  |"
        text += "\n  |".join(id_list[str(x)]
                             for x in eve_search_res['inventory_type'])
        lev_d = process.extract(
            command[0],
            market_type_list.keys(),
            limit=tm_sea)
        lev_a = process.extract(
            command[0],
            abbr_list['type'].keys(),
            limit=tm_sea)
        tr_d = sorted([i for i in lev_d if i[1] >= 50],
                      key=lambda x: x[1], reverse=True)
        tr_a = sorted([i for i in lev_a if i[1] >= 50],
                      key=lambda x: x[1], reverse=True)
        text += "\n 基础数据库模糊匹配结果：\n  |"
        text += "\n  |".join([x[0] for x in tr_d])
        if tr_a:
            text += "\n 简称数据库模糊匹配结果：\n  |"
            text += "\n  |".join([x[0] + "->" +
                                  abbr_list['type'][x[0]] for x in tr_a])
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def abtype(command: list, group_id: int, sender: dict, *args, **kwargs) -> dict:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, logger, logger2, dogma_list
    print('using abtype')
    if len(command) < 2 or command[0] == '':
        text = '用法（abtype）：.abtype 物品简称，物品名'
    else:
        typename = command[1]
        if typename not in market_type_list.keys():
            text = '不能确认目标物品名'
        else:
            abbr_list['type'][command[0]] = command[1]
            yaml.dump(
                abbr_list,
                open(
                    BASE_ABBR_PATH,
                    mode='w+',
                    encoding='utf-8'),
                default_flow_style=False,
                allow_unicode=True,
                Dumper=yaml.RoundTripDumper,
                width=1000)
            text = '添加简称：\n{0}->{1}'.format(command[0], command[1])
            logger.info(
                "".join(
                    text.split("\n")) +
                "<Sender:{0}<<Group:{1}".format(
                    sender['user_id'],
                    group_id))
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def abcol(command: list, group_id: int, sender: dict, *args, **kwargs) -> dict:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, logger, logger2
    print('using abcol')
    if len(command) < 2 or command[0] == "":
        text = '用法（abcol）：.abcol 物品类简称，物品名1、物品名2...'
    else:
        text = ""
        for i in command[1].split('、'):
            if i not in market_type_list.keys():
                text += "{0}不存在".format(i)
        if text == "":
            abbr_list['col'][command[0]] = command[1].split('、')
            yaml.dump(
                abbr_list,
                open(
                    BASE_ABBR_PATH,
                    mode='w+',
                    encoding='utf-8'),
                default_flow_style=False,
                allow_unicode=True,
                Dumper=yaml.RoundTripDumper,
                width=1000)
            text = '添加简称：\n{}->\n'.format(command[0])
            # for i in command[1].split('、'):
            #     text += '{}\n'.format(i)
            text += "\n".join(command[1].split('、'))
            logger.info(
                "".join(
                    text.split("\n")) +
                "<Sender:{0}<<Group:{1}".format(
                    sender['user_id'],
                    group_id))
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def desc(command: list, group_id: int, *args, **kwargs) -> dict:
    global id_list, data_list, desc_list
    print('using desc')
    if len(command) < 1 or command[0] == "":
        text = '用法(desc)：.desc 物品名'
    else:
        typename = command[0]
        if typename not in desc_list.keys():
            typename = max(
                process.extract(
                    typename,
                    market_type_list.keys(),
                    limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))[0]
        de = desc_list[typename]
        if de == "":
            text = '该物品无描述'
        else:
            text = typename + '\n' + de
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def dogma(command: list, group_id: int, *args, **kwargs) -> dict:
    global id_list, data_list, dogma_list
    print('using dogma')
    if len(command) < 1 or command[0] == "":
        text = '用法(dogma)：.dogma 物品名'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        typename = command[0]
        if typename not in data_list.keys():
            typename = max(
                process.extract(
                    typename,
                    data_list.keys(),
                    limit=25
                ),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]
                )
            )[0]
        typeid = data_list[typename]
        det = requests.get(BASE_UNI_TYPEID.format(
            type_id=typeid), params={'datasource': 'serenity', 'language': 'zh'}).json()
        title = f'{typename}'
        try:
            dog = det['dogma_attributes']
            # text = f'{typename}：\n'
            text = ""
            for at in dog:
                if dogma_list[str(at["attribute_id"])][0] in string.ascii_letters:
                    continue
                elif dogma_list[str(at["attribute_id"])] in ['主技能需求', '副技能需求', '三级技能需求', '四级技能需求', '五级技能需求', '六级技能需求']:
                    at['value'] = id_list[str(int(at['value']))]
                text += f' {dogma_list[str(at["attribute_id"])]} -> {at["value"]}\n'
        except KeyError:
            text = '无属性数据'
        text += '\n\n备注：\n会忽略一切英文的属性，可能包括一些CCP和\n网易并未给出明确中文翻译的属性，因此仅供参考'
        # width = len(max(text.split("\n"), key=len)) * 15 + 130
        # height = len(text.split("\n")) * 21 + 100
        img_base = Image.new("RGB", (1, 1), 'white')
        draw = ImageDraw.Draw(img_base)
        main_text_geo = draw.textsize(text, simhei_l_15)
        img_base = img_base.resize((25 + main_text_geo[0] + 75, 50 + main_text_geo[1] + 50))
        draw = ImageDraw.Draw(img_base)
        draw.text((25, 25), text=title, fill='black', font=simhei_b_20)
        draw.text((25, 50), text=text, fill='black', font=simhei_l_15)
        # print('drawn')
        # img_base.show()
        fp = '$' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + \
             str(random.randint(random.randint(0, 150), random.randint(200, 300)))
        img_base.save('data/images/cache/' + fp + ".png")
        return {'action': 'send_group_msg',
                'params': {'group_id': group_id,
                           'message': [{'type': 'image',
                                        'data': {'file': 'cache\\' + fp + '.png'}}]},
                'echo': 'IMAGE' + 'data/images/cache/' + fp + ".png"}


def trait(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global data_list, id_list, traits_list, ship_data_list
    print('using trait')
    if len(command) < 1 or command[0] == '':
        text = '用法(trait)：.trait 物品名'
    else:
        typename = command[0]
        if typename in ship_data_list.keys():
            pass
        else:
            typename = max(
                process.extract(typename, ship_data_list.keys(), limit=5),
                key=lambda x: fuzz.ratio(typename, x[0])
            )[0]
        type_traits: dict = traits_list[int(ship_data_list[typename])]
        text = f'{typename}:\n'
        for i in type_traits.values():
            if type(i) == dict:
                text += ' {0}\n'.format(i['header'])
                for j in i['bonuses']:
                    if 'number' in j.keys():
                        text += '  {0} {1}\n'.format(j['number'], j['text'])
                    else:
                        text += '  {0}\n'.format(j['text'])
            elif type(i) == list:
                for k in i:
                    text += ' {0}\n'.format(k['header'])
                    for j in k['bonuses']:
                        if 'number' in j.keys():
                            text += '  {0} {1}\n'.format(j['number'], j['text'])
                        else:
                            text += '  {0}\n'.format(j['text'])
        # print(text)
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def trans(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global data_list, id_list, trans_version_df
    print('using trans')
    langs = {
        'zh': '中文',
        'en': '英文',
        'ja': '日文',
        'ru': '俄文',
        'fr': '法文',
        'de': '德文',
        'es': '西班牙文',
        'it': '意大利文'}
    if len(command) < 1 or command[0] == '':
        text = '用法(trans)：.trans 物品名（，源语言类型）<zh,en,ja,ru,fr,de,es,it>'
    else:
        typename = command[0]
        if len(command) >= 2 and command[1] in langs.keys():
            from_type = command[1]
        elif command[0][0] in string.ascii_letters:
            from_type = 'en'
        else:
            from_type = 'zh'
        tofind = trans_version_df[from_type]
        if typename in tofind.to_list():
            idx = tofind.to_list().index(typename)
        else:
            typename = max(
                process.extract(
                    typename,
                    tofind.to_list(),
                    limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))[0]
            idx = tofind.to_list().index(typename)
        searching_list = trans_version_df.loc[idx, :].to_list()
        if from_type != 'zh':
            text = '物品名称：\n 中文：{0}\n {1}：{2}'.format(
                searching_list[2], langs[from_type], typename)
        elif len(command) == 1:
            text = '物品名称：\n 中文：{0}\n 英文：{1}'.format(
                typename, searching_list[3])
        else:
            text = '物品名称：\n 中文：{0}\n 英文：{1}\n 日文：{2} \n 俄文：{3}\n 法文：{4}\n 德文：{5}\n 西班牙文：{6}\n 意大利文：{7}'.format(
                typename,
                searching_list[3],
                searching_list[4],
                searching_list[5],
                searching_list[6],
                searching_list[7],
                searching_list[8],
                searching_list[9])
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def jita(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, desc_list
    print('using jita')
    if len(command) < 1 or command[0] == "":
        text = '用法(jita)：.jita 物品名'
        clo = 0
    else:
        typename = command[0]
        if typename not in market_type_list.keys():
            r1 = max(
                process.extract(
                    typename,
                    market_type_list.keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            r2 = max(
                process.extract(
                    typename,
                    abbr_list['type'].keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            clo = max(r1[1], r2[1])
            if r1[1] > r2[1]:
                typename = r1[0]
            else:
                typename = r2[0]
                typename = abbr_list['type'][r2[0]]
        else:
            clo = 100
        jita_market = marketing('伏尔戈', typename, server='zh')
        # print('jita market', jita_market)
        bm = float("%.2f" % float(jita_market['buy']['max']))
        sm = float("%.2f" % float(jita_market['sell']['min']))
        ave = float("%.2f" % float((bm + sm) / 2))
        bm = format(bm, ",")
        sm = format(sm, ",")
        ave = format(ave, ",")
        text = '物品国服售价（伏尔戈）：\n物品名称：{0}\n收单价：{1}\n卖单价：{2}\n中位价：{3}'.format(
            typename, bm, sm, ave)
    if clo <= 50:
        text += '\n\n备注：\n如果想添加物品简称以供快捷查询，请参考.abtype功能（频道不支持）'
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def ojita(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, desc_list
    print('using ojita')
    if len(command) < 1 or command[0] == "":
        text = "用法(ojita)：.ojita 物品名"
        clo = 0
    else:
        typename = command[0]
        if typename not in market_type_list.keys():
            r1 = max(
                process.extract(
                    typename,
                    market_type_list.keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            r2 = max(
                process.extract(
                    typename,
                    abbr_list['type'].keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            clo = max(r1[1], r2[1])
            if r1[1] > r2[1]:
                typename = r1[0]
            else:
                typename = r2[0]
                typename = abbr_list['type'][r2[0]]
        else:
            clo = 100
        ojita_market = marketing('伏尔戈', typename, server='en')
        # print('ojita market', ojita_market)
        bm = float("%.2f" % float(ojita_market['buy']['max']))
        sm = float("%.2f" % float(ojita_market['sell']['min']))
        ave = float("%.2f" % float((bm + sm) / 2))
        bm = format(bm, ",")
        sm = format(sm, ",")
        ave = format(ave, ",")
        text = '物品世界服售价（伏尔戈）：\n物品名称：{0}\n收单价：{1}\n卖单价：{2}\n中位价：{3}'.format(
            typename, bm, sm, ave)
    if clo <= 50:
        text += '\n\n备注：\n如果想添加物品简称以供快捷查询，请参考.abtype功能（频道不支持）'
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def wtb(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, desc_list
    print('using wtb')
    if len(command) < 2 or command[0] == '' or command[1] == '':
        text = "用法(wtb)：.wtb 物品名，星域名"
        clo = 0
    else:
        typename = command[0]
        if typename not in market_type_list.keys():
            r1 = max(
                process.extract(
                    typename,
                    market_type_list.keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            r2 = max(
                process.extract(
                    typename,
                    abbr_list['type'].keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            clo = max(r1[1], r2[1])
            if r1[1] > r2[1]:
                typename = r1[0]
            else:
                typename = r2[0]
                typename = abbr_list['type'][r2[0]]
        else:
            clo = 100
        reg_name = command[1]
        if reg_name not in reg_list.keys():
            reg_name, clo = max(
                process.extract(
                    reg_name, reg_list.keys(), limit=25), key=lambda x: fuzz.ratio(
                    typename, x[0]))
            if clo <= 40:
                text = "星域名称未搜寻到"
                return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                    {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
        _market = marketing(reg_name, typename, server='zh')
        # print('ojita market', ojita_market)
        bm = float("%.2f" % float(_market['buy']['max']))
        sm = float("%.2f" % float(_market['sell']['min']))
        ave = float("%.2f" % float((bm + sm) / 2))
        bm = format(bm, ",")
        sm = format(sm, ",")
        ave = format(ave, ",")
        text = '物品国服售价（{0}）：\n物品名称：{1}\n收单价：{2}\n卖单价：{3}\n中位价：{4}'.format(
            reg_name, typename, bm, sm, ave)
    if clo <= 50:
        text += '\n\n备注：\n如果想添加物品简称以供快捷查询，请参考.abtype功能（频道不支持）'
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def owtb(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, desc_list
    print('using owtb')
    if len(command) < 2 or command[0] == '' or command[1] == '':
        text = "用法(owtb)：.owtb 物品名，星域名"
        clo = 0
    else:
        typename = command[0]
        if typename not in market_type_list.keys():
            r1 = max(
                process.extract(
                    typename,
                    market_type_list.keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            r2 = max(
                process.extract(
                    typename,
                    abbr_list['type'].keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            clo = max(r1[1], r2[1])
            if r1[1] > r2[1]:
                typename = r1[0]
            else:
                typename = r2[0]
                typename = abbr_list['type'][r2[0]]
        else:
            clo = 100
        reg_name = command[1]
        if reg_name not in reg_list.keys():
            reg_name, clo = max(
                process.extract(
                    reg_name, reg_list.keys(), limit=25), key=lambda x: fuzz.ratio(
                    typename, x[0]))
            if clo <= 40:
                text = "星域名称未搜寻到"
                return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
                    {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
        _market = marketing(reg_name, typename, server='en')
        # print('ojita market', ojita_market)
        bm = float("%.2f" % float(_market['buy']['max']))
        sm = float("%.2f" % float(_market['sell']['min']))
        ave = float("%.2f" % float((bm + sm) / 2))
        bm = format(bm, ",")
        sm = format(sm, ",")
        ave = format(ave, ",")
        text = '物品世界服售价（{0}）：\n物品名称：{1}\n收单价：{2}\n卖单价：{3}\n中位价：{4}'.format(
            reg_name, typename, bm, sm, ave)
    if clo <= 50:
        text += '\n\n备注：\n如果想添加物品简称以供快捷查询，请参考.abtype功能（频道不支持）'
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def col(command: list, group_id: int, *args, **kwargs) -> dict:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, desc_list
    print('using col')
    if len(command) < 1 or command[0] == '':
        text = '用法(col)：.col 搜索字段（，匹配条目数）'
        clo = 0
    else:
        typename = command[0]
        if typename in abbr_list['col'].keys():
            typename = abbr_list['col'][typename]
            clo = 1
            # print('typename in abbrs')
        else:
            rc = max(
                process.extract(
                    typename,
                    abbr_list['col'].keys(), limit=15),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            # print(f'rc: {rc}')
            if rc[1] >= 80:
                typename = abbr_list['col'][rc[0]]
                clo = 1
                # print('rc[1] >= 80')
            else:
                # print('rc[1] < 80')
                if len(command) == 2:
                    tic = int(command[1])
                else:
                    tic = 6
                typename = [
                    x[0] for x in process.extract(
                        typename,
                        market_type_list.keys(),
                        limit=tic)]
                clo = 1
        text = "物品组国服（伏尔戈）价格：\n"
        cb = 0
        cs = 0
        for i in typename:
            jd = marketing('伏尔戈', i, server='zh')
            bm = format(float("%.2f" % float(jd['buy']['max'])), ",")
            sm = format(float("%.2f" % float(jd['sell']['min'])), ",")
            cb += float("%.2f" % float(jd['buy']['max']))
            cs += float("%.2f" % float(jd['sell']['min']))
            text += "{0}:\n 收单价：{1}\n 卖单价：{2}\n".format(i, bm, sm)
        text += "总收单价：{0}\n总卖单价：{1}\n总中位价：{2}".format(
            format(
                cb, ','), format(
                cs, ','), format(
                float(
                    '%.2f' %
                    ((cb + cs) / 2)), ','))
    if clo == 0:
        text += '\n\n备注：\n如果想添加物品组以供快捷查询，请参考.abcol功能（频道不支持）'
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def ocol(command: list, group_id: int, *args, **kwargs) -> dict:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, desc_list
    print('using ocol')
    if len(command) < 1 or command[0] == '':
        text = '用法(ocol)：.ocol 搜索字段（，匹配条目数）'
        clo = 0
    else:
        typename = command[0]
        if typename in abbr_list['col'].keys():
            typename = abbr_list['col'][typename]
            clo = 1
            # print('typename in abbrs')
        else:
            rc = max(
                process.extract(
                    typename,
                    abbr_list['col'].keys(), limit=15),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            # print(f'rc: {rc}')
            if rc[1] >= 80:
                typename = abbr_list['col'][rc[0]]
                clo = 1
                # print('rc[1] >= 80')
            else:
                # print('rc[1] < 80')
                if len(command) == 2:
                    tic = int(command[1])
                else:
                    tic = 6
                typename = [
                    x[0] for x in process.extract(
                        typename,
                        market_type_list.keys(),
                        limit=tic)]
                clo = 1
        text = "物品组世界服（伏尔戈）价格：\n"
        cb = 0
        cs = 0
        for i in typename:
            jd = marketing('伏尔戈', i, server='en')
            bm = format(float("%.2f" % float(jd['buy']['max'])), ",")
            sm = format(float("%.2f" % float(jd['sell']['min'])), ",")
            cb += float("%.2f" % float(jd['buy']['max']))
            cs += float("%.2f" % float(jd['sell']['min']))
            text += "{0}:\n 收单价：{1}\n 卖单价：{2}\n".format(i, bm, sm)
        text += "总收单价：{0}\n总卖单价：{1}\n总中位价：{2}".format(
            format(
                cb, ','), format(
                cs, ','), format(
                float(
                    '%.2f' %
                    ((cb + cs) / 2)), ','))
    if clo == 0:
        text += '\n\n备注：\n如果想添加物品组以供快捷查询，请参考.abcol功能（频道不支持）'
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def mkd(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, desc_list
    print('using md')
    if len(command) < 1 or command[0] == "":
        text = '用法(mkd)：.mkd 物品名'
    else:
        typename = command[0]
        if typename not in market_type_list.keys():
            r1 = max(
                process.extract(
                    typename,
                    market_type_list.keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            r2 = max(
                process.extract(
                    typename,
                    abbr_list['type'].keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            if r1[1] > r2[1]:
                typename = r1[0]
            else:
                typename = r2[0]
        text = '物品名称：' + typename + '\n市场类型：\n'
        tpl = mkd_list[typename]
        for i in range(len(tpl)):
            if tpl[i] == "":
                break
            text += '|' + '-' * (i + 1) + tpl[i] + '\n'
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def sch(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global data_list, id_list, plaSch_id_list, plaSch_list
    print('using sch')
    if len(command) < 1 or command[0] == '':
        text = '用法(sch)： .sch 行星产物名'
    else:
        typename = command[0]
        try:
            tp_id = plaSch_id_list[typename]
        except KeyError:
            typename = max(
                process.extract(
                    typename, plaSch_list.keys(), limit=5
                ),
                key=lambda x: fuzz.ratio(typename, x[0])
            )[0]
            tp_id = plaSch_id_list[typename]
        sch_data = plaSch_list[int(tp_id)]
        text = f'物品名称：{typename}\n'
        text += ' 加工用时：{}\n'.format(sch_data['cycleTime'])
        # text += ' 加工过程：\n'
        for i, o in sch_data['types'].items():
            text += '  {0}：{1}×{2}\n'.format((o['isInput'] == 'true' and '输入') or (o['isInput'] == 'false' or '输出'),
                                             id_list[str(i)], o['quantity'])
        text += ' 相关建筑：\n'
        for i in sch_data['pins']:
            text += '  {}\n'.format(id_list[str(i)])
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def lp(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global market_type_list, data_list, id_list, npc_cor_list, blp_list
    print('using lp')
    if len(command) < 1 or command[0] == '':
        text = '用法(lp)：.lp npc军团名'
    else:
        cor_name = command[0]
        if cor_name in npc_cor_list.keys():
            pass
        else:
            cor_name = max(
                process.extract(
                    cor_name, npc_cor_list.keys(), limit=20
                ),
                key=lambda x: fuzz.ratio(cor_name, x[0])
            )[0]
        lp_shop_d_min = requests.get(COR_LP_MARKET.format(corporation_id=npc_cor_list[cor_name],
                                                          server='serenity',
                                                          amo='3',
                                                          fm='min')).json()
        lp_shop_d_max = requests.get(COR_LP_MARKET.format(corporation_id=npc_cor_list[cor_name],
                                                          server='serenity',
                                                          amo='3',
                                                          fm='max')).json()
        text = '军团：{}（国服数据）\n'.format(cor_name)
        text += '| 最大收益：\n'
        for o in lp_shop_d_max['message']['data']:
            text += ' - {0} × {1} : {2} isk/lp\n'.format(id_list[str(o['type_id'])], o['quantity'], "%.2f" % o['profit']['per_point']['max'])
        text += '| 常规收益：\n'
        for o in lp_shop_d_min['message']['data']:
            text += ' - {0} × {1} : {2} isk/lp\n'.format(id_list[str(o['type_id'])], o['quantity'], "%.2f" % o['profit']['per_point']['min'])
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def olp(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global market_type_list, data_list, id_list, npc_cor_list, blp_list
    print('using olp')
    if len(command) < 1 or command[0] == '':
        text = '用法(olp)：.olp npc军团名'
    else:
        cor_name = command[0]
        if cor_name in npc_cor_list.keys():
            pass
        else:
            cor_name = max(
                process.extract(
                    cor_name, npc_cor_list.keys(), limit=20
                ),
                key=lambda x: fuzz.ratio(cor_name, x[0])
            )[0]
        lp_shop_d_min = requests.get(COR_LP_MARKET.format(corporation_id=npc_cor_list[cor_name],
                                                          server='tranquility',
                                                          amo='3',
                                                          fm='min')).json()
        lp_shop_d_max = requests.get(COR_LP_MARKET.format(corporation_id=npc_cor_list[cor_name],
                                                          server='tranquility',
                                                          amo='3',
                                                          fm='max')).json()
        text = '军团：{}（世界服数据）\n'.format(cor_name)
        text += '| 最大收益：\n'
        for o in lp_shop_d_max['message']['data']:
            text += ' - {0} × {1} : {2} isk/lp\n'.format(id_list[str(o['type_id'])], o['quantity'], "%.2f" % o['profit']['per_point']['max'])
        text += '| 常规收益：\n'
        for o in lp_shop_d_min['message']['data']:
            text += ' - {0} × {1} : {2} isk/lp\n'.format(id_list[str(o['type_id'])], o['quantity'], "%.2f" % o['profit']['per_point']['min'])
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def blp(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, desc_list
    print('using blp')
    ext = {'reaction': '反应\n', 'manufacturing': '制造\n', 'invention': '发明:\n',
           'materials': '材料：\n', 'time': '用时：', 'products': '产出：'}
    if len(command) < 1 or command[0] == "":
        text = '用法(blp)：.blp 蓝图名（，材料等级）（，时间等级）（，材料消耗额外加成）（，制造时间额外加成）\n' \
               '例：.blp 阿斯特罗级，5，3，1.5，2（即5-2的阿斯特罗级蓝图，1.5%额外材料效率，2%额外时间加成）'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        typename = command[0]
        if typename not in blp_list.keys():
            typename = max(
                process.extract(
                    typename,
                    blpt_list.keys(),
                    limit=10),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))[0]
        b = blp_list[int(blpt_list[typename])]
        text = '物品名称：' + typename + "\n蓝图属性：\n"
        if 'manufacturing' in b['activities'].keys():
            # if len(command) == 2:
            #     tm_value = 0
            #     mat_value = max(min(int(command[1]), 10), 0)
            # elif len(command) == 3:
            #     tm_value = max(min(int(command[2]), 10), 0)
            #     mat_value = max(min(int(command[1]), 10), 0)
            # elif len(command) == 4:
            #     tm_value = max(min(int(command[1])))
            # elif len(command) == 1:
            #     tm_value = mat_value = 0
            param_list = [0, 0, 0, 0]
            for i in range(1, len(command)):
                try:
                    param_list[i - 1] = float(command[i])
                except ValueError:
                    continue
            mat_value = max(min(param_list[0], 10), 0)
            tm_value = max(min(param_list[1], 10), 0)
            mat_e_value = param_list[2]
            tm_e_value = param_list[3]
            text += '-制造：\n--材料需求：\n'
            for req in b['activities']['manufacturing']['materials']:
                text += '  -{0} × {1}\n'.format(id_list[str(req['typeID'])], "%.2f" % (
                        req['quantity'] * (1 - mat_value * 0.01) * (1 - mat_e_value * 0.01)))
            tm: int = b['activities']['manufacturing']['time'] * \
                      (1 - tm_value * 0.01) * (1 - tm_e_value * 0.01)
            text += '--用时：{}\n'.format(time.strftime("%d:%H:%M:%S",
                                                     time.gmtime(tm)))
            text += '--产出：{0} × {1}\n'.format(id_list[str(b['activities']['manufacturing']['products'][0]['typeID'])],
                                              b['activities']['manufacturing']['products'][0]['quantity'])
            # text += '--用时：{0}:{1}:{2}\n'.format(tm // 3600, tm % 3600 // 60, tm % 60)
        if 'reaction' in b['activities'].keys():
            text += '-反应：\n--材料需求：\n'
            for req in b['activities']['reaction']['materials']:
                text += '  -{0} × {1}\n'.format(
                    id_list[str(req['typeID'])], "%.2f" % req['quantity'])
            text += '--产出：{0} × {1}\n'.format(id_list[str(b['activities']['reaction']['products'][0]['typeID'])],
                                              b['activities']['reaction']['products'][0]['quantity'])
            tm: int = b['activities']['reaction']['time']
            text += '--用时：{}\n'.format(time.strftime('%d:%H:%M:%S', time.localtime(tm)))
        if 'invention' in b['activities'].keys():
            text += '-发明：\n--材料需求：\n'
            for req in b['activities']['invention']['materials']:
                text += '  -{0} × {1}\n'.format(
                    id_list[str(req['typeID'])], req['quantity'])
            for inv in b['activities']['invention']['products']:
                text += '--成功率：{0}\n--产出：{1} × {2}\n'.format(
                    inv['probability'], id_list[str(inv['typeID'])], inv['quantity'])
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def blpm(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, desc_list
    print('using blpm')
    ext = {'reaction': '反应\n', 'manufacturing': '制造\n', 'invention': '发明:\n',
           'materials': '材料：\n', 'time': '用时：', 'products': '产出：'}
    if len(command) < 1 or command[0] == "":
        text = '用法(blpm)：.blpm 蓝图名（，材料等级）（，时间等级）（，材料消耗额外加成）（，制造时间额外加成）'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        typename = command[0]
        if typename not in blp_list.keys():
            typename = max(
                process.extract(
                    typename,
                    blpt_list.keys(),
                    limit=10),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))[0]
        b = blp_list[int(blpt_list[typename])]
        text = "蓝图国服材料价格(伏尔戈)：\n"
        title_text = f'物品名称：{typename} （来自：晨曦）\n'
        if 'manufacturing' in b['activities'].keys():
            param_list = [0, 0, 0, 0]
            for i in range(1, len(command)):
                try:
                    param_list[i - 1] = float(command[i])
                except ValueError:
                    continue
            mat_value = max(min(param_list[0], 10), 0)
            tm_value = max(min(param_list[1], 10), 0)
            mat_e_value = param_list[2]
            tm_e_value = param_list[3]
            text += '-制造：\n--材料需求：\n'
            req_cost_bm = req_cost_sm = req_cost_ave = 0
            for req in b['activities']['manufacturing']['materials']:
                text += '  -{0} × {1}\n'.format(id_list[str(req['typeID'])], "%.2f" % (
                        req['quantity'] * (1 - mat_value * 0.01) * (1 - mat_e_value * 0.01)))
                jd = marketing('伏尔戈', id_list[str(req['typeID'])], 'zh')
                bm = float("%.2f" %
                           float(jd['buy']['max'] *
                                 req['quantity'] *
                                 (1 -
                                  mat_value *
                                  0.01) *
                                 (1 -
                                  mat_e_value *
                                  0.01)))
                sm = float("%.2f" %
                           float(jd['sell']['min'] *
                                 req['quantity'] *
                                 (1 -
                                  mat_value *
                                  0.01) *
                                 (1 -
                                  mat_e_value *
                                  0.01)))
                ave = float("%.2f" % float((bm + sm) / 2))
                req_cost_bm += bm
                req_cost_sm += sm
                req_cost_ave += ave
                bm = format(bm, ",")
                sm = format(sm, ",")
                ave = format(ave, ",")
                text += '  |收单价：{0}\n  |卖单价：{1}\n  |中位价：{2}\n'.format(
                    bm, sm, ave)
            rc_bm = format(req_cost_bm, ",")
            rc_sm = format(req_cost_sm, ",")
            rc_ave = format(req_cost_ave, ",")
            text += ' |总收单价：{0}\n |总卖单价：{1}\n |总中位价：{2}\n'.format(
                rc_bm, rc_sm, rc_ave)
            prod_id = b['activities']['manufacturing']['products'][0]['typeID']
            tm = b['activities']['manufacturing']['time'] * \
                 (1 - tm_value * 0.01) * (1 - tm_e_value * 0.01)
            text += " -用时：{}\n".format(time.strftime('%d:%H:%M:%S',
                                                     time.gmtime(tm)))
            text += '--产出：{0} × {1}\n'.format(id_list[str(prod_id)],
                                              b['activities']['manufacturing']['products'][0]['quantity'])
            if id_list[str(prod_id)] in market_type_list.keys():
                # req_cost_bm = req_cost_sm = req_cost_ave = 0
                jd = marketing('伏尔戈', id_list[str(prod_id)], 'zh')
                bm = float(
                    "%.2f" %
                    float(
                        jd['buy']['max'] *
                        b['activities']['manufacturing']['products'][0]['quantity']))
                sm = float(
                    "%.2f" %
                    float(
                        jd['sell']['min'] *
                        b['activities']['manufacturing']['products'][0]['quantity']))
                ave = float("%.2f" % float((bm + sm) / 2))
                pr_bm = bm
                pr_sm = sm
                pr_ave = ave
                bm = format(bm, ",")
                sm = format(sm, ",")
                ave = format(ave, ",")
                text += ' |产出收单价：{0}\n |产出卖单价：{1}\n |产出中位价：{2}\n'.format(
                    bm, sm, ave)
                # mph_max = (pr_sm - req_cost_bm) / (tm / 3600)
                text += '--收益：\n |最大收益：{0}/小时\n |最快收益：{1}/小时\n |中位收益：{2}/小时\n'.format(
                    format(float("%.2f" %
                                 ((pr_sm - req_cost_bm) / (tm / 3600))), ','),
                    format(float("%.2f" %
                                 ((pr_bm - req_cost_sm) / (tm / 3600))), ','),
                    format(float("%.2f" %
                                 ((pr_ave - req_cost_ave) / (tm / 3600))), ',')
                )
            else:
                text += '该物品不可在市场上交易\n'
        elif 'reaction' in b['activities'].keys():
            text += '-反应：\n--材料需求：\n'
            req_cost_bm = req_cost_sm = req_cost_ave = 0
            for req in b['activities']['reaction']['materials']:
                text += '  -{0} × {1}\n'.format(
                    id_list[str(req['typeID'])], req['quantity'])
                jd = marketing('伏尔戈', id_list[str(req['typeID'])], 'zh')
                bm = float("%.2f" % float(jd['buy']['max'] * req['quantity']))
                sm = float("%.2f" % float(jd['sell']['min'] * req['quantity']))
                ave = float("%.2f" % float((bm + sm) / 2))
                req_cost_bm += bm
                req_cost_sm += sm
                req_cost_ave += ave
                bm = format(bm, ",")
                sm = format(sm, ",")
                ave = format(ave, ",")
                text += '  |收单价：{0}\n  |卖单价：{1}\n  |中位价：{2}\n'.format(
                    bm, sm, ave)
            rc_bm = format(req_cost_bm, ",")
            rc_sm = format(req_cost_sm, ",")
            rc_ave = format(req_cost_ave, ",")
            text += ' |总收单价：{0}\n |总卖单价：{1}\n |总中位价：{2}\n'.format(
                rc_bm, rc_sm, rc_ave)
            prod_id = b['activities']['reaction']['products'][0]['typeID']
            text += '--产出：{0} × {1}\n'.format(
                id_list[str(prod_id)], b['activities']['reaction']['products'][0]['quantity'])
            tm = b['activities']['reaction']['time']
            if id_list[str(prod_id)] in market_type_list.keys():
                # req_cost_bm = req_cost_sm = req_cost_ave = 0
                jd = marketing('伏尔戈', id_list[str(prod_id)], 'zh')
                bm = float(
                    "%.2f" %
                    float(
                        jd['buy']['max'] *
                        b['activities']['reaction']['products'][0]['quantity']))
                sm = float(
                    "%.2f" %
                    float(
                        jd['sell']['min'] *
                        b['activities']['reaction']['products'][0]['quantity']))
                ave = float("%.2f" % float((bm + sm) / 2))
                pr_bm = bm
                pr_sm = sm
                pr_ave = ave
                bm = format(float("%.2f" % bm), ",")
                sm = format(float("%.2f" % sm), ",")
                ave = format(float("%.2f" % ave), ",")
                text += '--|产出收单价：{0}\n--|产出卖单价：{1}\n--|产出中位价：{2}'.format(
                    bm, sm, ave)
                text += '--收益：\n |最大收益：{0}/小时\n |最快收益：{1}/小时\n |中位收益：{2}/小时\n'.format(
                    format(float("%.2f" %
                                 ((pr_sm - req_cost_bm) / (tm / 3600))), ','),
                    format(float("%.2f" %
                                 ((pr_bm - req_cost_sm) / (tm / 3600))), ','),
                    format(float("%.2f" %
                                 ((pr_ave - req_cost_ave) / (tm / 3600))), ',')
                )
            else:
                text += '该物品不可在市场上交易\n'
        if 'invention' in b['activities'].keys():
            text += '-发明：\n--材料需求：\n'
            req_cost_bm = req_cost_sm = req_cost_ave = 0
            for req in b['activities']['invention']['materials']:
                text += '  -{0} × {1}\n'.format(
                    id_list[str(req['typeID'])], req['quantity'])
                jd = marketing('伏尔戈', id_list[str(req['typeID'])], 'zh')
                bm = float("%.2f" %
                           (float(jd['buy']['max']) * req['quantity']))
                sm = float("%.2f" %
                           (float(jd['sell']['min']) * req['quantity']))
                ave = float("%.2f" % (float((bm + sm) / 2)))
                req_cost_bm += bm
                req_cost_sm += sm
                req_cost_ave += ave
                bm = format(bm, ",")
                sm = format(sm, ",")
                ave = format(ave, ",")
                text += '  |收单价：{0}\n  |卖单价：{1}\n  |中位价：{2}\n'.format(
                    bm, sm, ave)
            rc_bm = format(req_cost_bm, ",")
            rc_sm = format(req_cost_sm, ",")
            rc_ave = format(req_cost_ave, ",")
            text += ' |总收单价：{0}\n |总卖单价：{1}\n |总中位价：{2}\n'.format(
                rc_bm, rc_sm, rc_ave)
            for inv in b['activities']['invention']['products']:
                text += '--成功率：{0}\n--产出：{1} × {2}\n'.format(
                    inv['probability'], id_list[str(inv['typeID'])], inv['quantity'])
        img_base = Image.new("RGB", (1, 1), 'white')
        draw = ImageDraw.Draw(img_base)
        main_text_geo = draw.textsize(text, simhei_l_15)
        img_base = img_base.resize((25 + main_text_geo[0] + 100, 50 + main_text_geo[1] + 50))
        draw = ImageDraw.Draw(img_base)
        draw.text((25, 25), text=title_text, fill='black', font=simhei_b_20)
        draw.text((25, 50), text=text, fill='black', font=simhei_l_15)
        # print('drawn')
        # img_base.show()
        fp = '$' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + \
             str(random.randint(random.randint(0, 150), random.randint(200, 300)))
        img_base.save('data/images/cache/' + fp + ".png")
        return {'action': 'send_group_msg',
                'params': {'group_id': group_id,
                           'message': [{'type': 'image',
                                        'data': {'file': 'cache\\' + fp + '.png'}}]},
                'echo': 'IMAGE' + 'data/images/cache/' + fp + ".png"}


def oblpm(command: list, group_id: int, *args, **kwargs) -> Union[dict, bool]:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, abbr_list, desc_list
    print('using oblpm')
    ext = {'reaction': '反应\n', 'manufacturing': '制造\n', 'invention': '发明:\n',
           'materials': '材料：\n', 'time': '用时：', 'products': '产出：'}
    if len(command) < 1 or command[0] == "":
        text = '用法(oblpm)：.oblpm 蓝图名（，材料等级）（，时间等级）（，材料消耗额外加成）（，制造时间额外加成）'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        typename = command[0]
        if typename not in blp_list.keys():
            typename = max(
                process.extract(
                    typename,
                    blpt_list.keys(),
                    limit=10),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))[0]
        b = blp_list[int(blpt_list[typename])]
        text = "蓝图国服材料价格(伏尔戈)：\n"
        title_text = f'物品名称：{typename} （来自：宁静）\n'
        if 'manufacturing' in b['activities'].keys():
            param_list = [0, 0, 0, 0]
            for i in range(1, len(command)):
                try:
                    param_list[i - 1] = float(command[i])
                except ValueError:
                    continue
            mat_value = max(min(param_list[0], 10), 0)
            tm_value = max(min(param_list[1], 10), 0)
            mat_e_value = param_list[2]
            tm_e_value = param_list[3]
            text += '-制造：\n--材料需求：\n'
            req_cost_bm = req_cost_sm = req_cost_ave = 0
            for req in b['activities']['manufacturing']['materials']:
                text += '  -{0} × {1}\n'.format(id_list[str(req['typeID'])], "%.2f" % (
                        req['quantity'] * (1 - mat_value * 0.01) * (1 - mat_e_value * 0.01)))
                jd = marketing('伏尔戈', id_list[str(req['typeID'])], 'en')
                bm = float("%.2f" %
                           float(jd['buy']['max'] *
                                 req['quantity'] *
                                 (1 -
                                  mat_value *
                                  0.01) *
                                 (1 -
                                  mat_e_value *
                                  0.01)))
                sm = float("%.2f" %
                           float(jd['sell']['min'] *
                                 req['quantity'] *
                                 (1 -
                                  mat_value *
                                  0.01) *
                                 (1 -
                                  mat_e_value *
                                  0.01)))
                ave = float("%.2f" % float((bm + sm) / 2))
                req_cost_bm += bm
                req_cost_sm += sm
                req_cost_ave += ave
                bm = format(bm, ",")
                sm = format(sm, ",")
                ave = format(ave, ",")
                text += '  |收单价：{0}\n  |卖单价：{1}\n  |中位价：{2}\n'.format(
                    bm, sm, ave)
            rc_bm = format(req_cost_bm, ",")
            rc_sm = format(req_cost_sm, ",")
            rc_ave = format(req_cost_ave, ",")
            text += ' |总收单价：{0}\n |总卖单价：{1}\n |总中位价：{2}\n'.format(
                rc_bm, rc_sm, rc_ave)
            prod_id = b['activities']['manufacturing']['products'][0]['typeID']
            tm = b['activities']['manufacturing']['time'] * \
                 (1 - tm_value * 0.01) * (1 - tm_e_value * 0.01)
            text += '--用时：{}\n'.format(time.strftime('%d:%H:%M:%S',
                                                     time.gmtime(tm)))
            text += '--产出：{0} × {1}\n'.format(id_list[str(prod_id)],
                                              b['activities']['manufacturing']['products'][0]['quantity'])
            if id_list[str(prod_id)] in market_type_list.keys():
                # req_cost_bm = req_cost_sm = req_cost_ave = 0
                jd = marketing('伏尔戈', id_list[str(prod_id)], 'en')
                bm = float(
                    "%.2f" %
                    float(
                        jd['buy']['max'] *
                        b['activities']['manufacturing']['products'][0]['quantity']))
                sm = float(
                    "%.2f" %
                    float(
                        jd['sell']['min'] *
                        b['activities']['manufacturing']['products'][0]['quantity']))
                ave = float("%.2f" % float((bm + sm) / 2))
                pr_bm = bm
                pr_sm = sm
                pr_ave = ave
                bm = format(float("%.2f" % bm), ",")
                sm = format(float("%.2f" % sm), ",")
                ave = format(float("%.2f" % ave), ",")
                text += ' |产出收单价：{0}\n |产出卖单价：{1}\n |产出中位价：{2}\n'.format(
                    bm, sm, ave)
                # mph_max = (pr_sm - req_cost_bm) / (tm / 3600)
                text += '--收益：\n |最大收益：{0}/小时\n |最快收益：{1}/小时\n |中位收益：{2}/小时\n'.format(
                    format(float("%.2f" %
                                 ((pr_sm - req_cost_bm) / (tm / 3600))), ','),
                    format(float("%.2f" %
                                 ((pr_bm - req_cost_sm) / (tm / 3600))), ','),
                    format(float("%.2f" %
                                 ((pr_ave - req_cost_ave) / (tm / 3600))), ',')
                )
            else:
                text += '该物品不可在市场上交易\n'
        elif 'reaction' in b['activities'].keys():
            text += '-反应：\n--材料需求：\n'
            req_cost_bm = req_cost_sm = req_cost_ave = 0
            for req in b['activities']['reaction']['materials']:
                text += '  -{0} × {1}\n'.format(
                    id_list[str(req['typeID'])], req['quantity'])
                jd = marketing('伏尔戈', id_list[str(req['typeID'])], 'en')
                bm = float("%.2f" % float(jd['buy']['max'] * req['quantity']))
                sm = float("%.2f" % float(jd['sell']['min'] * req['quantity']))
                ave = float("%.2f" % float((bm + sm) / 2))
                req_cost_bm += bm
                req_cost_sm += sm
                req_cost_ave += ave
                bm = format(bm, ",")
                sm = format(sm, ",")
                ave = format(ave, ",")
                text += '  |收单价：{0}\n  |卖单价：{1}\n  |中位价：{2}\n'.format(
                    bm, sm, ave)
            req_cost_bm = format(float("%.2f" % req_cost_bm), ",")
            req_cost_sm = format(float("%.2f" % req_cost_sm), ",")
            req_cost_ave = format(float("%.2f" % req_cost_ave), ",")
            text += ' |总收单价：{0}\n |总卖单价：{1}\n |总中位价：{2}\n'.format(
                req_cost_bm, req_cost_sm, req_cost_ave)
            prod_id = b['activities']['reaction']['products'][0]['typeID']
            text += '--产出：{0} × {1}\n'.format(
                id_list[str(prod_id)], b['activities']['reaction']['products'][0]['quantity'])
            tm = b['activities']['reaction']['time']
            if id_list[str(prod_id)] in market_type_list.keys():
                # req_cost_bm = req_cost_sm = req_cost_ave = 0
                jd = marketing('伏尔戈', id_list[str(prod_id)], 'en')
                bm = float(
                    "%.2f" %
                    float(
                        jd['buy']['max'] *
                        b['activities']['reaction']['products'][0]['quantity']))
                sm = float(
                    "%.2f" %
                    float(
                        jd['sell']['min'] *
                        b['activities']['reaction']['products'][0]['quantity']))
                ave = float("%.2f" % float((bm + sm) / 2))
                pr_bm = bm
                pr_sm = sm
                pr_ave = ave
                bm = format(bm, ",")
                sm = format(sm, ",")
                ave = format(ave, ",")
                text += '--|产出收单价：{0}\n--|产出卖单价：{1}\n--|产出中位价：{2}\n'.format(
                    bm, sm, ave)
                text += '--收益：\n |最大收益：{0}/小时\n |最快收益：{1}/小时\n |中位收益：{2}/小时\n'.format(
                    format(float("%.2f" %
                                 ((pr_sm - req_cost_bm) / (tm / 3600))), ','),
                    format(float("%.2f" %
                                 ((pr_bm - req_cost_sm) / (tm / 3600))), ','),
                    format(float("%.2f" %
                                 ((pr_ave - req_cost_ave) / (tm / 3600))), ',')
                )
            else:
                text += '该物品不可在市场上交易\n'
        if 'invention' in b['activities'].keys():
            text += '-发明：\n--材料需求：\n'
            req_cost_bm = req_cost_sm = req_cost_ave = 0
            for req in b['activities']['invention']['materials']:
                text += '  -{0} × {1}\n'.format(
                    id_list[str(req['typeID'])], req['quantity'])
                jd = marketing('伏尔戈', id_list[str(req['typeID'])], 'en')
                bm = float("%.2f" %
                           (float(jd['buy']['max']) * req['quantity']))
                sm = float("%.2f" %
                           (float(jd['sell']['min']) * req['quantity']))
                ave = float("%.2f" % (float((bm + sm) / 2)))
                req_cost_bm += bm
                req_cost_sm += sm
                req_cost_ave += ave
                bm = format(bm, ",")
                sm = format(sm, ",")
                ave = format(ave, ",")
                text += '  |收单价：{0}\n  |卖单价：{1}\n  |中位价：{2}\n'.format(
                    bm, sm, ave)
            rc_bm = format(req_cost_bm, ",")
            rc_sm = format(req_cost_sm, ",")
            rc_ave = format(req_cost_ave, ",")
            text += ' |总收单价：{0}\n |总卖单价：{1}\n |总中位价：{2}\n'.format(
                rc_bm, rc_sm, rc_ave)
            for inv in b['activities']['invention']['products']:
                text += '--成功率：{0}\n--产出：{1} × {2}\n'.format(
                    inv['probability'], id_list[str(inv['typeID'])], inv['quantity'])
        img_base = Image.new("RGB", (1, 1), 'white')
        draw = ImageDraw.Draw(img_base)
        main_text_geo = draw.textsize(text, simhei_l_15)
        img_base = img_base.resize((25 + main_text_geo[0] + 100, 50 + main_text_geo[1] + 50))
        draw = ImageDraw.Draw(img_base)
        draw.text((25, 25), text=title_text, fill='black', font=simhei_b_20)
        draw.text((25, 50), text=text, fill='black', font=simhei_l_15)
        # print('drawn')
        # img_base.show()
        fp = '$' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + \
             str(random.randint(random.randint(0, 150), random.randint(200, 300)))
        img_base.save('data/images/cache/' + fp + ".png")
        return {'action': 'send_group_msg',
                'params': {'group_id': group_id,
                           'message': [{'type': 'image',
                                        'data': {'file': 'cache\\' + fp + '.png'}}]},
                'echo': 'IMAGE' + 'data/images/cache/' + fp + ".png"}


def blp_expander(key: int, quantity: int, mat_value: int = 0,
                 *args, **kwargs) -> Union[dict, bool]:
    """
    :param mat_value: material value
    :param quantity: the amount of the materials
    :param key: an int object stands for the typeID of the thing to check
    :return: (bool or list) {'mat name': name,'materials': [{'mat name': name1, 'id': id1, 'quantity': qua1},
    {'mat name': name2, 'id': id2, 'quantity': qua2, 'materials': [...]}, ...]
    """
    rt = {'mat name': id_list[str(key)], 'id': int(key), 'quantity': quantity}
    # if key in [4312, 4247, 4246, 4051]:
    #     return rt
    # try:
    #     key = blpt_list[prod_list[id_list[str(key)]]]
    # except KeyError as e:
    #     return rt
    k = int(blpt_list[prod_list[id_list[str(key)]]])
    if k in blp_list.keys():
        # print('egs')
        b = blp_list[k]
        if 'activities' not in b.keys():
            return False
        rt['materials'] = []
        if 'manufacturing' in b['activities'].keys():
            cpl = b['activities']['manufacturing']['materials']
            # print('-', cpl, rt['quantity'])
            for mat in cpl:
                mat_name = id_list[str(mat['typeID'])]
                # print('--', mat_name)
                try:
                    mat_id = int(blpt_list[prod_list[mat_name]])
                    m = blp_expander(
                        key=data_list[mat_name],
                        quantity=rt['quantity'] *
                                 mat['quantity'] *
                                 (
                                         1 -
                                         mat_value *
                                         0.01) /
                                 b['activities']['manufacturing']['products'][0]['quantity'],
                        mat_value=mat_value)
                    rt['materials'].append(m)
                except KeyError as e:
                    rt['materials'].append(
                        {
                            'mat name': mat_name,
                            'id': int(
                                mat['typeID']),
                            'quantity': rt['quantity'] *
                                        mat['quantity'] *
                                        (
                                                1 -
                                                mat_value *
                                                0.01) /
                                        b['activities']['manufacturing']['products'][0]['quantity']})
            return rt
        elif 'reaction' in b['activities'].keys():
            cpl = b['activities']['reaction']['materials']
            # print('-', cpl, rt['quantity'])
            for mat in cpl:
                mat_name = id_list[str(mat['typeID'])]
                # print('--', mat_name)
                try:
                    mat_id = int(blpt_list[prod_list[mat_name]])
                    m = blp_expander(
                        key=data_list[mat_name],
                        quantity=rt['quantity'] *
                                 mat['quantity'] /
                                 b['activities']['reaction']['products'][0]['quantity'],
                        mat_value=mat_value)
                    rt['materials'].append(m)
                except KeyError as e:
                    rt['materials'].append(
                        {
                            'mat name': mat_name,
                            'id': int(
                                mat['typeID']),
                            'quantity': rt['quantity'] *
                                        mat['quantity'] /
                                        b['activities']['reaction']['products'][0]['quantity']})
            return rt
        else:
            del rt['materials']
            return rt
    else:
        return rt


def blp_expander_toString(blpD: dict,
                          plate: int,
                          used: list,
                          base: dict,
                          newline: bool = True,
                          baseline: str = '',
                          headline: bool = False,
                          *args,
                          **kwargs) -> Optional[Tuple[str, dict, list]]:
    """
    :param headline: whether it's the headline
    :param blpD: the dict that contains the data of the blueprint(part)
    :param plate: the number of whitespace
    :param used: a list contains the materials which have been showed details
    :param base: a dict shows how many of each kind of basic materials
    :param newline: whether to create the new line
    :param baseline: the text to add newlines
    :return: str->see param newline; dict->see base; list->see used; dict->see market_cache
    """
    if int(blpD['id']) in used:
        nextline = False
    else:
        used.append(int(blpD['id']))
        nextline = True
    if 'materials' not in blpD.keys():
        if newline and not headline:
            baseline += " " * plate + \
                        "|--{0}×{1}\n".format(blpD['mat name'],
                                              "%.2f" % blpD['quantity'])
        if int(blpD['id']) in base.keys():
            base[int(blpD['id'])] += float(blpD['quantity'])
        else:
            base[int(blpD['id'])] = float(blpD['quantity'])
    else:
        if newline and not headline:
            baseline += " " * plate + \
                        "|--{0}×{1}\n".format(blpD['mat name'],
                                              "%.2f" % blpD['quantity'])
        for mat in blpD['materials']:
            baseline, base, used = blp_expander_toString(
                blpD=mat, plate=plate + 1, used=used, base=base, newline=nextline, baseline=baseline)
    return baseline, base, used


def blpe(command: list, group_id: int, *args, **kwargs) -> dict:
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list
    print('using blpe')
    if len(command) < 1 or command[0] == "":
        title_text = ""
        text = '用法(blpe)：.blpe 蓝图名（，材料等级）（，时间等级）（，材料消耗额外加成）（，制造时间额外加成）'
        return {'action': 'send_group_msg', 'params': {
            'group_id': group_id, 'message': [{'type': 'text', 'data': {'text': text}}]}}
    else:
        # img_base = Image.new("RGB")
        typename = command[0]
        if typename not in blp_list.keys():
            typename = max(
                process.extract(
                    typename,
                    blpt_list.keys(),
                    limit=10),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))[0]
        b = blp_list[int(blpt_list[typename])]
        title_text = '物品名称：' + typename + "\n"
        text = "蓝图属性：\n"
        param_list = [0, 0, 0, 0]
        for i in range(1, len(command)):
            try:
                param_list[i - 1] = float(command[i])
            except ValueError:
                continue
        mat_value = max(min(param_list[0], 10), 0)
        tm_value = max(min(param_list[1], 10), 0)
        mat_e_value = param_list[2]
        tm_e_value = param_list[3]
        if 'manufacturing' in b['activities'].keys():
            text += '-制造：\n--材料需求：\n'
            if 'products' in b['activities']['manufacturing'].keys() and b['activities']['manufacturing']['products'] != []:
                if b['activities']['manufacturing']['products'][0]['typeID'] in [x['typeID'] for x in b['activities']['manufacturing']['materials']]:
                    u = {}
                    for x in b['activities']['manufacturing']['materials']:
                        u[x['typeID']] = float("%.2f" % (x['quantity'] * (1 - mat_value * 0.01) * (
                                1 - mat_e_value * 0.01)))
                        text += '  |--{0}×{1}\n'.format(x['typeID'], float("%.2f" % (x['quantity'] * (
                                1 - mat_value * 0.01) * (1 - mat_e_value * 0.01))))
                else:
                    blpD = blp_expander(
                        b['activities']['manufacturing']['products'][0]['typeID'],
                        b['activities']['manufacturing']['products'][0]['quantity'],
                        mat_value=mat_value)
                    R = blp_expander_toString(
                        blpD=blpD, plate=3, used=[], base={}, headline=True)
                    text += R[0]
                    u = R[1]
            else:
                u = {}
                for x in b['activities']['manufacturing']['materials']:
                    u[x['typeID']] = float("%.2f" % x['quantity'])
                    text += "  |--{0}×{1}\n".format(x['typeID'],
                                                    float("%.2f" % x['quantity']))
            text += " -用时：{}\n".format(time.strftime("%d:%H:%M:%S", time.gmtime(
                b['activities']['manufacturing']['time'] * (1 - tm_value * 0.01) * (1 - tm_e_value * 0.01))))
        elif 'reaction' in b['activities'].keys():
            text += '-反应：\n--材料需求：\n'
            if 'products' in b['activities']['reaction'].keys() and b['activities']['reaction']['products'] != []:
                if b['activities']['reaction']['products'][0]['typeID'] in [x['typeID'] for x in b['activities']['reaction']['materials']]:
                    u = {}
                    for x in b['activities']['reaction']['materials']:
                        u[x['typeID']] = float("%.2f" % (
                            x['quantity']))
                        text += '  |--{0}×{1}\n'.format(
                            x['typeID'], float(
                                "%.2f" %
                                (x['quantity'])))
                else:
                    blpD = blp_expander(
                        b['activities']['reaction']['products'][0]['typeID'],
                        b['activities']['reaction']['products'][0]['quantity'],
                        mat_value=mat_value)
                    R = blp_expander_toString(
                        blpD=blpD, plate=3, used=[], base={}, headline=True)
                    text += R[0]
                    u = R[1]
            else:
                u = {}
                for x in b['activities']['reaction']['materials']:
                    u[x['typeID']] = float("%.2f" % x['quantity'])
                    text += "  |--{0}×{1}\n".format(x['typeID'],
                                                    float("%.2f" % x['quantity']))
            text += " -用时：{}\n".format(time.strftime("%d:%H:%M:%S",
                                                     time.gmtime(b['activities']['reaction']['time'])))
        if 'invention' in b['activities'].keys():
            text += '-发明：\n--材料需求：\n'
            for req in b['activities']['invention']['materials']:
                text += '  -{0} × {1}\n'.format(
                    id_list[str(req['typeID'])], req['quantity'])
            for inv in b['activities']['invention']['products']:
                text += '--成功率：{0}\n--产出：{1} × {2}\n'.format(
                    inv['probability'], id_list[str(inv['typeID'])], inv['quantity'])
        if 'research_material' in b['activities'].keys(
        ) and 'research_time' in b['activities'].keys():
            text += '-材料效率研究：\n--用时：{0}\n'.format(
                b['activities']['research_material']['time'])
            if 'materials' in b['activities']['research_material'].keys(
            ) and b['activities']['research_material']['materials'] != []:
                text += '--材料消耗：\n'
                for req in b['activities']['research_material']['materials']:
                    text += '  -{0} × {1}\n'.format(
                        id_list[str(req['typeID'])], req['quantity'])
            text += '-时间效率研究：\n--用时：{0}\n'.format(
                b['activities']['research_time']['time'])
            if 'materials' in b['activities']['research_time'].keys() \
                    and b['activities']['research_time']['materials'] != []:
                text += '--材料消耗：\n'
                for req in b['activities']['research_time']['materials']:
                    text += '  -{0} × {1}\n'.format(
                        id_list[str(req['typeID'])], req['quantity'])
        text += '-最大生产上限：{0}'.format(b['maxProductionLimit'])
        # print(u)
        if 'u' in locals():
            # print(u, type(u))
            use = ["{0}×{1}".format(id_list[str(x)], "%.2f" % u[x])
                   for x in u.keys()]
            img_base = Image.new("RGB", (1, 1), 'white')
            draw = ImageDraw.Draw(img_base)
            rtt = "\n".join(use)
            title_geo = draw.textsize(title_text, simhei_b_20)
            use_list_geo = draw.textsize(text, simhei_l_15)
            all_geo = draw.textsize(rtt, simhei_l_15)
            img_base = img_base.resize((max(25 + use_list_geo[0] + 20 + all_geo[0] + 25, 25 + title_geo[0] + 25),
                                        max(50 + use_list_geo[1] + 50, 75 + all_geo[1] + 50)))
            draw = ImageDraw.Draw(img_base)
            draw.text((25, 25), text=title_text, fill='black', font=simhei_b_20)
            draw.text((25, 50), text=text, fill='black', font=simhei_l_15)
            # print(rtt)
            draw.text((25 + use_list_geo[0] + 20, 50), text='材料总览：',
                      fill='black', font=simhei_20)
            draw.text((25 + use_list_geo[0] + 20, 75), text=rtt,
                      fill='black', font=simhei_l_15)
            # draw.text((55, 30), text=rtt, font=simhei_20)
            # print('drawn')
            # img_base.show()
        else:
            img_base = Image.new("RGB", (1, 1), 'white')
            draw = ImageDraw.Draw(img_base)
            main_text_geo = draw.textsize(text, simhei_l_15)
            img_base = img_base.resize((25 + main_text_geo[0] + 75, 50 + main_text_geo[1] + 50))
            draw = ImageDraw.Draw(img_base)
            draw.text((25, 25), text=title_text, fill='black', font=simhei_b_20)
            draw.text((25, 50), text=text, fill='black', font=simhei_l_15)
            # print('drawn')
            # img_base.show()
        fp = '$' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + \
             str(random.randint(random.randint(0, 150), random.randint(200, 300)))
        img_base.save('data/images/cache/' + fp + ".png")
        return {'action': 'send_group_msg',
                'params': {'group_id': group_id,
                           'message': [{'type': 'image',
                                        'data': {'file': 'cache\\' + fp + '.png'}}]},
                'echo': 'IMAGE' + 'data/images/cache/' + fp + ".png"}


def blpem(command: list, group_id: int, *args, **kwargs):
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list
    print('using blpem')
    if len(command) < 1 or command[0] == "":
        title_text = ""
        text = '用法(blpem)：.blpem 蓝图名（，材料等级）（，时间等级）（，材料消耗额外加成）（，制造时间额外加成）'
        return {'action': 'send_group_msg', 'params': {
            'group_id': group_id, 'message': [{'type': 'text', 'data': {'text': text}}]}}
    else:
        # img_base = Image.new("RGB")
        typename = command[0]
        if typename not in blp_list.keys():
            typename = max(
                process.extract(
                    typename,
                    blpt_list.keys(),
                    limit=10),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))[0]
        b = blp_list[int(blpt_list[typename])]
        title_text = f'物品名称：{typename} （来自：晨曦）\n'
        text = "蓝图材料：\n"
        param_list = [0, 0, 0, 0]
        for i in range(1, len(command)):
            try:
                param_list[i - 1] = float(command[i])
            except ValueError:
                continue
        mat_value = max(min(param_list[0], 10), 0)
        tm_value = max(min(param_list[1], 10), 0)
        mat_e_value = param_list[2]
        tm_e_value = param_list[3]
        if 'manufacturing' in b['activities'].keys():
            text += '-制造：\n--材料需求：\n'
            if 'products' in b['activities']['manufacturing'].keys(
            ) and b['activities']['manufacturing']['products'] != []:
                if b['activities']['manufacturing']['products'][0]['typeID'] in [x['typeID'] for x in b['activities']['manufacturing']['materials']]:
                    u = {}
                    for x in b['activities']['manufacturing']['materials']:
                        u[x['typeID']] = float("%.2f" % (
                                x['quantity'] * (1 - mat_value * 0.01) * (1 - mat_e_value * 0.01)))
                else:
                    blpD = blp_expander(
                        b['activities']['manufacturing']['products'][0]['typeID'],
                        b['activities']['manufacturing']['products'][0]['quantity'],
                        mat_value=mat_value)
                    R = blp_expander_toString(
                        blpD=blpD, plate=3, used=[], base={}, headline=True, newline=False)
                    u = R[1]
                prod_amo = b['activities']['manufacturing']['products'][0]['quantity']
                utm = b['activities']['manufacturing']['time'] * \
                      (1 - tm_value * 0.01) * (1 - tm_e_value * 0.01)
            else:
                u = {}
                for x in b['activities']['manufacturing']['materials']:
                    u[x['typeID']] = float("%.2f" % x['quantity'])
                prod_amo = 0
                utm = 0
        elif 'reaction' in b['activities'].keys():
            text += '-反应：\n--材料需求：\n'
            if 'products' in b['activities']['reaction'].keys(
            ) and b['activities']['reaction']['products'] != []:
                if b['activities']['reaction']['products'][0]['typeID'] in [x['typeID'] for x in b['activities']['reaction']['materials']]:
                    u = {}
                    for x in b['activities']['reaction']['materials']:
                        u[x['typeID']] = float("%.2f" % (x['quantity']))
                else:
                    blpD = blp_expander(
                        b['activities']['reaction']['products'][0]['typeID'],
                        b['activities']['reaction']['products'][0]['quantity'],
                        mat_value=mat_value)
                    R = blp_expander_toString(
                        blpD=blpD, plate=3, used=[], base={}, headline=True, newline=False)
                    u = R[1]
                prod_amo = b['activities']['reaction']['products'][0]['quantity']
                utm = b['activities']['reaction']['time']
            else:
                u = {}
                for x in b['activities']['reaction']['materials']:
                    u[x['typeID']] = float("%.2f" % x['quantity'])
                prod_amo = 0
                utm = 0
        if 'u' in locals():
            all_bm = 0
            all_sm = 0
            for i in u.keys():
                if id_list[str(i)] in market_type_list.keys():
                    mkt = marketing('伏尔戈', id_list[str(i)], server='zh')
                    bm = float("%.2f" % (float(mkt['buy']['max']) * u[i]))
                    sm = float("%.2f" % (float(mkt['sell']['min']) * u[i]))
                    all_bm += bm
                    all_sm += sm
                    text += " {0}×{1}\n|收单价：{2}\n|卖单价：{3}\n|中位价：{4}\n".format(id_list[str(i)], "%.2f" % u[i], format(
                        bm, ","), format(sm, ","), format(float("%.2f" % ((bm + sm) / 2)), ","))
                else:
                    text += "该物品无法在市场上交易"
                # mkt = marketing('伏尔戈', id_list[str(i)], 'zh')
            price_tag1 = "材料总价："
            price1 = "|收单价：{0}\n|卖单价：{1}\n|中位价：{2}".format(
                format(
                    float(
                        "%.2f" %
                        all_bm), ","), format(
                    float(
                        "%.2f" %
                        all_sm), ","), format(
                    float(
                        "%.2f" %
                        ((all_bm + all_sm) / 2)), ","))
            try:
                mat_type = id_list[str(blp_list[int(
                    data_list[typename])]['activities']['manufacturing']['products'][0]['typeID'])]
            except KeyError:
                try:
                    mat_type = id_list[str(blp_list[int(
                        data_list[typename])]['activities']['reaction']['products'][0]['typeID'])]
                except KeyError:
                    mat_type = None
            price_tag2 = "产出总价：{0}×{1}".format(mat_type, prod_amo)  # 总价的title
            if mat_type and mat_type in market_type_list.keys():
                mkt = marketing('伏尔戈', mat_type, 'zh')
                bm = float("%.2f" % (float(mkt['buy']['max']) * prod_amo))
                sm = float("%.2f" % (float(mkt['sell']['min']) * prod_amo))
                ave = float("%.2f" % ((bm + sm) / 2))
                price2 = "|收单价：{0}\n|卖单价：{1}\n|中位价：{2}\n".format(
                    format(bm, ','), format(sm, ','), format(ave, ','))
            else:
                price2 = "该物品无法在市场上交易"
                bm = sm = ave = 0
            time_tag = "每流程用时：{}\n".format(
                time.strftime("%d:%H:%M:%S", time.gmtime(utm)))
            profit_title = "收益："
            profit_text = "|最大收益：{0}/小时\n|最快收益：{1}/小时\n|中位收益：{2}/小时".format(
                format(float("%.2f" % ((sm - all_bm) / (utm / 3600))), ','),
                format(float("%.2f" % ((bm - all_sm) / (utm / 3600))), ','),
                format(float("%.2f" %
                             ((ave - (all_bm + all_sm) / 2) / (utm / 3600))), ',')
            )
            img_base = Image.new("RGB", (1, 1), 'white')
            draw = ImageDraw.Draw(img_base)
            main_geo = draw.textsize(text, simhei_l_15)
            img_base = img_base.resize((25 + main_geo[0] + 20 + max(len(max(price1.split("\n"), key=len)) * 20,
                                                                    len(max(price2.split("\n"), key=len)) * 20,
                                                                    len(price_tag2) * 25,
                                                                    len(max(profit_text.split("\n"), key=len)) * 20) + 35,
                                        max(600, 50 + main_geo[1] + 50)))
            draw = ImageDraw.Draw(img_base)
            draw.text((25, 25), text=title_text,
                      fill='black', font=simhei_b_20)
            draw.text((25, 50), text=text, fill='black', font=simhei_l_15)
            draw.text((25 + main_geo[0] + 20, 75), text=price_tag1,
                      fill='black', font=simhei_20)
            draw.text((25 + main_geo[0] + 20, 100), text=price1,
                      fill='black', font=simhei_l_20)
            draw.text((25 + main_geo[0] + 20, 225), text=price_tag2,
                      fill='black', font=simhei_20)
            draw.text((25 + main_geo[0] + 20, 250), text=price2,
                      fill='black', font=simhei_l_20)
            draw.text((25 + main_geo[0] + 20, 375), text=time_tag,
                      fill='black', font=simhei_20)
            draw.text((25 + main_geo[0] + 20, 400), text=profit_title,
                      fill='black', font=simhei_20)
            draw.text((25 + main_geo[0] + 20, 425), text=profit_text,
                      fill='black', font=simhei_l_20)
            draw.text((25 + main_geo[0] + 20, 550), text=ADV_TEXT,
                      fill='#ed7070', font=simhei_20)
            fp = '$' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + \
                 str(random.randint(random.randint(0, 150), random.randint(200, 300)))
            img_base.save('data/images/cache/' + fp + ".png")
            return {'action': 'send_group_msg',
                    'params': {'group_id': group_id,
                               'message': [{'type': 'image',
                                            'data': {'file': 'cache\\' + fp + '.png'}}]},
                    'echo': 'IMAGE' + 'data/images/cache/' + fp + ".png"}
        else:
            text = "该物品无制造材料数据"
            img_base = Image.new("RGB", (300, 300), 'white')
            draw = ImageDraw.Draw(img_base)
            draw.text((25, 25), text=title_text,
                      fill='black', font=simhei_b_20)
            draw.text((25, 50), text=text, fill='black', font=simhei_b_20)
            draw.text((25, 75), text=ADV_TEXT,
                      fill='#ed7070', font=simhei_l_20)
            fp = '$' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + \
                 str(random.randint(random.randint(0, 150), random.randint(200, 300)))
            img_base.save('data/images/cache/' + fp + ".png")
            return {'action': 'send_group_msg',
                    'params': {'group_id': group_id,
                               'message': [{'type': 'image',
                                            'data': {'file': 'cache\\' + fp + '.png'}}]},
                    'echo': 'IMAGE' + 'data/images/cache/' + fp + ".png"}


def oblpem(command: list, group_id: int, *args, **kwargs):
    global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list
    print('using oblpem')
    if len(command) < 1 or command[0] == "":
        title_text = ""
        text = '用法(oblpem)：.oblpem 蓝图名（，材料等级）（，时间等级）（，材料消耗额外加成）（，制造时间额外加成）'
        return {'action': 'send_group_msg', 'params': {
            'group_id': group_id, 'message': [{'type': 'text', 'data': {'text': text}}]}}
    else:
        # img_base = Image.new("RGB")
        typename = command[0]
        if typename not in blp_list.keys():
            typename = max(
                process.extract(
                    typename,
                    blpt_list.keys(),
                    limit=10),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))[0]
        b = blp_list[int(blpt_list[typename])]
        title_text = f'物品名称：{typename} （来自：宁静）\n'
        text = "蓝图材料：\n"
        param_list = [0, 0, 0, 0]
        for i in range(1, len(command)):
            try:
                param_list[i - 1] = float(command[i])
            except ValueError:
                continue
        mat_value = max(min(param_list[0], 10), 0)
        tm_value = max(min(param_list[1], 10), 0)
        mat_e_value = param_list[2]
        tm_e_value = param_list[3]
        if 'manufacturing' in b['activities'].keys():
            text += '-制造：\n--材料需求：\n'
            if 'products' in b['activities']['manufacturing'].keys(
            ) and b['activities']['manufacturing']['products'] != []:
                if b['activities']['manufacturing']['products'][0]['typeID'] in [x['typeID'] for x in b['activities']['manufacturing']['materials']]:
                    u = {}
                    for x in b['activities']['manufacturing']['materials']:
                        u[x['typeID']] = float("%.2f" % (
                                x['quantity'] * (1 - mat_value * 0.01) * (1 - mat_e_value * 0.01)))
                else:
                    blpD = blp_expander(
                        b['activities']['manufacturing']['products'][0]['typeID'],
                        b['activities']['manufacturing']['products'][0]['quantity'],
                        mat_value=mat_value)
                    R = blp_expander_toString(
                        blpD=blpD, plate=3, used=[], base={}, headline=True, newline=False)
                    u = R[1]
                prod_amo = b['activities']['manufacturing']['products'][0]['quantity']
                utm = b['activities']['manufacturing']['time'] * \
                      (1 - tm_value * 0.01) * (1 - tm_e_value * 0.01)
            else:
                u = {}
                for x in b['activities']['manufacturing']['materials']:
                    u[x['typeID']] = float("%.2f" % x['quantity'])
                prod_amo = 0
                utm = 0
        elif 'reaction' in b['activities'].keys():
            text += '-反应：\n--材料需求：\n'
            if 'products' in b['activities']['reaction'].keys(
            ) and b['activities']['reaction']['products'] != []:
                if b['activities']['reaction']['products'][0]['typeID'] in [x['typeID'] for x in b['activities']['reaction']['materials']]:
                    u = {}
                    for x in b['activities']['reaction']['materials']:
                        u[x['typeID']] = float("%.2f" % (x['quantity']))
                else:
                    blpD = blp_expander(
                        b['activities']['reaction']['products'][0]['typeID'],
                        b['activities']['reaction']['products'][0]['quantity'],
                        mat_value=mat_value)
                    R = blp_expander_toString(
                        blpD=blpD, plate=3, used=[], base={}, headline=True, newline=False)
                    u = R[1]
                prod_amo = b['activities']['reaction']['products'][0]['quantity']
                utm = b['activities']['reaction']['time']
            else:
                u = {}
                for x in b['activities']['reaction']['materials']:
                    u[x['typeID']] = float("%.2f" % x['quantity'])
                prod_amo = 0
                utm = 0
        if 'u' in locals():
            all_bm = 0
            all_sm = 0
            for i in u.keys():
                if id_list[str(i)] in market_type_list.keys():
                    mkt = marketing('伏尔戈', id_list[str(i)], server='en')
                    bm = float("%.2f" % (float(mkt['buy']['max']) * u[i]))
                    sm = float("%.2f" % (float(mkt['sell']['min']) * u[i]))
                    all_bm += bm
                    all_sm += sm
                    text += " {0}×{1}\n|收单价：{2}\n|卖单价：{3}\n|中位价：{4}\n".format(id_list[str(i)], "%.2f" % u[i], format(
                        bm, ","), format(sm, ","), format(float("%.2f" % ((bm + sm) / 2)), ","))
                else:
                    text += "该物品无法在市场上交易"
                # mkt = marketing('伏尔戈', id_list[str(i)], 'en')
            price_tag1 = "材料总价："
            price1 = "|收单价：{0}\n|卖单价：{1}\n|中位价：{2}".format(
                format(
                    float(
                        "%.2f" %
                        all_bm), ","), format(
                    float(
                        "%.2f" %
                        all_sm), ","), format(
                    float(
                        "%.2f" %
                        ((all_bm + all_sm) / 2)), ","))
            try:
                mat_type = id_list[str(blp_list[int(
                    data_list[typename])]['activities']['manufacturing']['products'][0]['typeID'])]
            except KeyError:
                try:
                    mat_type = id_list[str(blp_list[int(
                        data_list[typename])]['activities']['reaction']['products'][0]['typeID'])]
                except KeyError:
                    mat_type = None
            price_tag2 = "产出总价：{0}×{1}".format(mat_type, prod_amo)  # 总价的title
            if mat_type and mat_type in market_type_list.keys():
                mkt = marketing('伏尔戈', mat_type, 'en')
                bm = float("%.2f" % (float(mkt['buy']['max']) * prod_amo))
                sm = float("%.2f" % (float(mkt['sell']['min']) * prod_amo))
                ave = float("%.2f" % ((bm + sm) / 2))
                ave = float("%.2f" % ((bm + sm) / 2))
                price2 = "|收单价：{0}\n|卖单价：{1}\n|中位价：{2}\n".format(
                    format(bm, ','), format(sm, ','), format(ave, ','))
            else:
                price2 = "该物品无法在市场上交易"
                bm = sm = ave = 0
            time_tag = "每流程用时：{}\n".format(
                time.strftime("%d:%H:%M:%S", time.gmtime(utm)))
            profit_title = "收益："
            profit_text = "|最大收益：{0}/小时\n|最快收益：{1}/小时\n|中位收益：{2}/小时".format(
                format(float("%.2f" % ((sm - all_bm) / (utm / 3600))), ','),
                format(float("%.2f" % ((bm - all_sm) / (utm / 3600))), ','),
                format(float("%.2f" %
                             ((ave - (all_bm + all_sm) / 2) / (utm / 3600))), ',')
            )
            img_base = Image.new("RGB", (1, 1), 'white')
            draw = ImageDraw.Draw(img_base)
            main_geo = draw.textsize(text, simhei_l_15)
            img_base = img_base.resize((25 + main_geo[0] + 20 + max(len(max(price1.split("\n"), key=len)) * 20,
                                                                    len(max(price2.split("\n"), key=len)) * 20,
                                                                    len(price_tag2) * 25,
                                                                    len(max(profit_text.split("\n"), key=len)) * 20) + 35,
                                        max(600, 50 + main_geo[1] + 50)))
            draw = ImageDraw.Draw(img_base)
            draw.text((25, 25), text=title_text,
                      fill='black', font=simhei_b_20)
            draw.text((25, 50), text=text, fill='black', font=simhei_l_15)
            draw.text((25 + main_geo[0] + 20, 75), text=price_tag1,
                      fill='black', font=simhei_20)
            draw.text((25 + main_geo[0] + 20, 100), text=price1,
                      fill='black', font=simhei_l_20)
            draw.text((25 + main_geo[0] + 20, 225), text=price_tag2,
                      fill='black', font=simhei_20)
            draw.text((25 + main_geo[0] + 20, 250), text=price2,
                      fill='black', font=simhei_l_20)
            draw.text((25 + main_geo[0] + 20, 375), text=time_tag,
                      fill='black', font=simhei_20)
            draw.text((25 + main_geo[0] + 20, 400), text=profit_title,
                      fill='black', font=simhei_20)
            draw.text((25 + main_geo[0] + 20, 425), text=profit_text,
                      fill='black', font=simhei_l_20)
            draw.text((25 + main_geo[0] + 20, 550), text=ADV_TEXT,
                      fill='#ed7070', font=simhei_20)
            fp = '$' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + \
                 str(random.randint(random.randint(0, 150), random.randint(200, 300)))
            img_base.save('data/images/cache/' + fp + ".png")
            return {'action': 'send_group_msg',
                    'params': {'group_id': group_id,
                               'message': [{'type': 'image',
                                            'data': {'file': 'cache\\' + fp + '.png'}}]},
                    'echo': 'IMAGE' + 'data/images/cache/' + fp + ".png"}
        else:
            text = "该物品无制造材料数据"
            img_base = Image.new("RGB", (300, 300), 'white')
            draw = ImageDraw.Draw(img_base)
            draw.text((25, 25), text=title_text,
                      fill='black', font=simhei_b_20)
            draw.text((25, 50), text=text, fill='black', font=simhei_b_20)
            draw.text((25, 75), text=ADV_TEXT,
                      fill='#ed7070', font=simhei_l_20)
            fp = '$' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + \
                 str(random.randint(random.randint(0, 150), random.randint(200, 300)))
            img_base.save('data/images/cache/' + fp + ".png")
            return {'action': 'send_group_msg',
                    'params': {'group_id': group_id,
                               'message': [{'type': 'image',
                                            'data': {'file': 'cache\\' + fp + '.png'}}]},
                    'echo': 'IMAGE' + 'data/images/cache/' + fp + ".png"}


def acc(command: list, group_id: int, *args, **kwargs):
    print('using acc')
    if len(command) < 2 or int(command[0]) * int(command[1]) == 0:
        text = '用法(acc)：.acc 属性加成，基础作用时长\n例：.acc 4，7\n即：基础7天+4加速器'
    else:
        plus = int(command[0])
        day = float(command[1])
        text = ACC_TEXT.format(point_plus='+' + str(plus),
                               pure_time=str(day) + '天',
                               pure_point="%.2f" % (plus * 1.5 * 24 * 60 * day),
                               v_time="%.2f" % (2 * day) + '天',
                               v_point="%.2f" % (plus * 3 * 24 * 60 * day),
                               by_time="%.2f" % (2.2 * day) + '天',
                               by_point="%.2f" % (plus * 3.3 * 24 * 60 * day))
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def accm(command: list, group_id: int, *args, **kwargs):
    print('using accm')
    if len(command) < 2 or int(command[0]) * int(command[1]) == 0:
        text = '用法(accm)：.accm 属性加成，实际作用时长，（脑浆衰减档次）\n' \
               '例：.accm 4，7\n即：应用加成后7天+4加速器\n.accm, 5，5，3\n即：应用加成后5天+5加速器，档次3(500,000→150,000)'
    else:
        plus = int(command[0])
        day = float(command[1])
        if len(command) == 2:
            level = 0
        else:
            level = int(command[2]) if (3 >= int(command[2]) > 0) else (0 if int(command[2]) < 0 else 3)
        if level == 0:
            dec = 500_000
        elif level == 1:
            dec = 400_000
        elif level == 2:
            dec = 300_000
        else:
            dec = 150_000
        l_skill = requests.get(BASE_SKILL_MARKET).json()
        s_skill = requests.get(BASE_SKILL_S_MARKET).json()
        v_point = plus * 3 * 24 * 60 * day
        ave_skill_m = (l_skill['sell']['min'] + l_skill['buy']['max'] + 5 * s_skill['sell']['min'] + 5 * s_skill['buy']['max']) / 4
        isk_per_point = ave_skill_m / dec
        v_worth = v_point * isk_per_point
        text = ACC_MARKET_TEXT.format(server_name='晨曦',
                                      point_plus='+' + str(plus),
                                      e_time=str(day) + '天',
                                      ave_skill=format(float("%.2f" % ave_skill_m), ','),
                                      e_point=format(dec, ','),
                                      isk_per_point=format(float("%.2f" % isk_per_point), ','),
                                      e_point_increase="%.2f" % v_point,
                                      expect_worth=format(float("%.2f" % v_worth), ','))
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def oaccm(command: list, group_id: int, *args, **kwargs):
    print('using oaccm')
    if len(command) < 2 or int(command[0]) * int(command[1]) == 0:
        text = '用法(oaccm)：.oaccm 属性加成，实际作用时长，（脑浆衰减档次）\n' \
               '例：.oaccm 4，7\n即：应用加成后7天+4加速器\n.oaccm, 5，5，3\n即：应用加成后5天+5加速器，档次3(500,000→150,000)'
    else:
        plus = int(command[0])
        day = float(command[1])
        if len(command) == 2:
            level = 0
        else:
            level = int(command[2]) if (3 >= int(command[2]) > 0) else (0 if int(command[2]) < 0 else 3)
        if level == 0:
            dec = 500_000
        elif level == 1:
            dec = 400_000
        elif level == 2:
            dec = 300_000
        else:
            dec = 150_000
        l_skill = requests.get(BASE_SKILL_MARKET_TQ).json()
        s_skill = requests.get(BASE_SKILL_S_MARKET_TQ).json()
        v_point = plus * 3 * 24 * 60 * day
        ave_skill_m = (l_skill['sell']['min'] + l_skill['buy']['max'] + 5 * s_skill['sell']['min'] + 5 * s_skill['buy']['max']) / 4
        isk_per_point = ave_skill_m / dec
        v_worth = v_point * isk_per_point
        text = ACC_MARKET_TEXT.format(server_name='宁静',
                                      point_plus='+' + str(plus),
                                      e_time=str(day) + '天',
                                      ave_skill=format(float("%.2f" % ave_skill_m), ','),
                                      e_point=format(dec, ','),
                                      isk_per_point=format(float("%.2f" % isk_per_point), ','),
                                      e_point_increase="%.2f" % v_point,
                                      expect_worth=format(float("%.2f" % v_worth), ','))
    return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
        {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}


def skill_expand(id_: int, c: int, level: int, fn: bool, dlevel: dict, title: bool = False) -> Tuple[str, str, List[dict], dict]:
    global skill_dict, data_list, id_list, skill_base_point
    if id_ not in skill_dict.keys():
        if fn:
            return ('    ' * c + '└ %s' % id_list[str(id_)] + '\n', '- ' + '■ ' * level + '\n', [], dlevel)\
                if not title else ('', '', [], dlevel)
        else:
            return ('    ' * c + '├ %s' % id_list[str(id_)] + '\n', '- ' + '■ ' * level + '\n', [], dlevel)\
                if not title else ('', '', [], dlevel)
    else:
        if fn:
            n_t = '    ' * c + '└ %s' % id_list[str(id_)] + '\n' if not title else ''
            n_l = '- ' + '■ ' * level + '\n' if not title else ''
        else:
            n_t = '    ' * c + '├ %s' % id_list[str(id_)] + '\n' if not title else ''
            n_l = '- ' + '■ ' * level + '\n' if not title else ''
        if 'time' in skill_dict[id_].keys():
            if not title:
                n_p = [{'skill': id_, 'level': level, 'point': skill_base_point[level] * skill_dict[id_]['time']}]
            else:
                n_p = []
        else:
            if not title:
                n_p = [{'skill': 'x', 'level': 0, 'point': 0}]
            else:
                n_p = []
        if id_ in dlevel.keys():
            if level >= dlevel[id_]:
                dlevel[id_] = level
        else:
            dlevel[id_] = level
        if 'skill' in skill_dict[id_].keys() and skill_dict[id_]['skill'] != []:
            for i in range(len(skill_dict[id_]['skill']) - 1):
                n_tn, n_ln, n_pn, lv = skill_expand(skill_dict[id_]['skill'][i]['skillId'], c + 1, skill_dict[id_]['skill'][i]['skillLevel'],
                                                          False, dlevel)
                n_t += n_tn
                n_l += n_ln
                n_p += n_pn
                dlevel = lv
            n_tn, n_ln, n_pn, lv = skill_expand(skill_dict[id_]['skill'][-1]['skillId'], c + 1, skill_dict[id_]['skill'][-1]['skillLevel'],
                                                      True, dlevel)
            n_t += n_tn
            n_l += n_ln
            n_p += n_pn
            dlevel = lv
        return n_t, n_l, n_p, dlevel


def sktree(command: list, group_id: int, *args, **kwargs) -> Union[bool, dict]:
    global skill_dict, data_list, id_list, skill_base_point
    print('using sktree')
    if len(command) < 1 or command[0] == 0:
        text = '用法(sktree)：.sktree 技能/物品名'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        typename = command[0]
        if typename not in data_list.keys():
            typename = max(
                process.extract(
                    typename,
                    data_list.keys(),
                    limit=10),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))[0]
        id_ = int(data_list[typename])
        # inf_data = skill_expand(28659, 0, 0, True, True)
        inf_data = skill_expand(id_, 0, 0, True, {}, True)
        img_base = Image.new("RGB", (1, 1), 'white')
        img_draw = ImageDraw.Draw(img_base)
        title = '物品名：%s' % typename
        title_width = img_draw.textsize(title, simhei_b_20)[0]
        if inf_data != ('', '', [], 0, []):
            dl = inf_data[3]
            gbt: int = sum([(skill_base_point[level]
                            * (skill_dict[id_]['time'] if 'time' in skill_dict[id_].keys() else 0)) for id_, level in dl.items()])
            m_skill_text = '总技能点需求：%s' % format(gbt, ',')
            m_t = gbt / 0.5
            m_time_text = '预估训练用时：{0}年{1}天{2}小时{3}分钟{4}秒'.format(int(m_t // (3600 * 24 * 365)),
                                                                 int(m_t % (3600 * 24 * 365) // (3600 * 24)),
                                                                 int(m_t % (3600 * 24 * 365) % (3600 * 24) // 3600),
                                                                 int(m_t % (3600 * 24 * 365) % (3600 * 24) % 3600 // 60),
                                                                 int(m_t % (3600 * 24 * 365) % (3600 * 24) % 3600 % 60))
            m_time_width = img_draw.textsize(m_time_text, simhei_20)[0]
            name_width = img_draw.textsize(inf_data[0], simhei_15)[0]
            level_width = img_draw.textsize(inf_data[1], simhei_15)[0]
            m_skill_width = img_draw.textsize(m_skill_text, simhei_20)[0]
            # print(inf_data[2])
            # print(dl)
            point_text = '\n'.join([('- %s' % ('×' if x['skill'] not in dl.keys() or x['level'] < dl[x['skill']] else x['point'])) for x in inf_data[2]])
            point_width = img_draw.textsize(point_text, simhei_15)[0]
            m_height = img_draw.textsize(inf_data[0], simhei_15)[1]
            img_base = img_base.resize((
                max(50 + name_width + 50 + level_width + 50 + point_width + 50, 50 + title_width + 50, 75 + m_skill_width + 75,
                    75 + m_time_width + 75),
                100 + m_height + 25 + 25 + 25 + 25 + 50))
            img_draw = ImageDraw.Draw(img_base)
            img_draw.text((50, 50), text=title, fill='black', font=simhei_b_20)
            img_draw.text((50, 100), text=inf_data[0], fill='black', font=simhei_15)
            img_draw.text((50 + name_width + 50, 100), text=inf_data[1], fill='black', font=simhei_15)
            img_draw.text((50 + name_width + 50 + point_width + 50, 100), text=point_text, fill='black', font=simhei_15)
            img_draw.text((75, 100 + m_height + 25), text=m_skill_text, fill='black', font=simhei_20)
            img_draw.text((75, 100 + m_height + 25 + 25 + 25), text=m_time_text, fill='black', font=simhei_20)
        else:
            text = '无技能数据'
            width = max(50 + title_width + 50, img_draw.textsize(text, font=simhei_20)[0])
            img_base = img_base.resize((width, 200))
            img_draw = ImageDraw.Draw(img_base)
            img_draw.text((50, 50), text=title, fill='black', font=simhei_b_20)
            img_draw.text((50, 100), text=text, fill='black', font=simhei_20)
        fp = '$' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + \
             str(random.randint(random.randint(0, 150), random.randint(200, 300)))
        img_base.save('data/images/cache/' + fp + ".png")
        return {'action': 'send_group_msg',
                'params': {'group_id': group_id,
                           'message': [{'type': 'image',
                                        'data': {'file': 'cache\\' + fp + '.png'}}]},
                'echo': 'IMAGE' + 'data/images/cache/' + fp + ".png"}


def market_grapic_maker(js: dict, title: str, svp: str) -> bool:
    data = pd.DataFrame(js)
    data['Date'] = list(map(lambda x: mdates.date2num(datetime.datetime.strptime(x, '%Y-%m-%d')), data['date'].tolist()))
    data['date'] = pd.to_datetime(data['date'])
    data_price = data.set_index('date')
    data_price.sort_index(ascending=True, inplace=True)
    s = mpf.make_mpf_style(base_mpf_style='binance', rc={'font.family': 'SimHei', 'axes.unicode_minus': 'False'})
    mpf.plot(data_price[['Date', 'open', 'high', 'low', 'close', 'volume']], type="candle", title=title, ylabel="价格/isk", style=s,
             volume=True,
             figscale=1.5,
             figratio=(8, 5), ylabel_lower='交易量',
             mav=(10, 20, 50),
             savefig=svp)


def prev(command: list, group_id: int, *args, **kwargs) -> Union[bool, dict]:
    print('using prev')
    global data_list, id_list, market_type_list
    if len(command) < 1 or command[0] == '':
        text = '用法(prev)：.prev 物品名'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        typename = command[0]
        if typename not in market_type_list.keys():
            r1 = max(
                process.extract(
                    typename,
                    market_type_list.keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            r2 = max(
                process.extract(
                    typename,
                    abbr_list['type'].keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            if r1[1] > r2[1]:
                typename = r1[0]
            else:
                typename = r2[0]
                typename = abbr_list['type'][r2[0]]
        id_ = int(data_list[typename])
        r_source = requests.get('https://www.ceve-market.org/query_history/',
                                params={'typeid': id_, 'tq': 0, 'regionid': 0}, headers={"referer": "https://www.ceve-market.org/home/"}).json()
        fp = '$' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + \
             str(random.randint(random.randint(0, 150), random.randint(200, 300)))
        # img_base.save('data/images/cache/' + fp + ".png")
        market_grapic_maker(js=r_source, title=typename, svp='./data/images/cache/' + fp + '.png')
        return {'action': 'send_group_msg',
                'params': {'group_id': group_id,
                           'message': [{'type': 'image',
                                        'data': {'file': 'cache\\' + fp + '.png'}}]},
                'echo': 'IMAGE' + 'data/images/cache/' + fp + ".png"}


def oprev(command: list, group_id: int, *args, **kwargs) -> Union[bool, dict]:
    print('using oprev')
    global data_list, id_list, market_type_list
    if len(command) < 1 or command[0] == '':
        text = '用法(oprev)：.oprev 物品名'
        return {'action': 'send_group_msg', 'params': {'group_id': group_id, 'message': [
            {'type': 'text', 'data': {'text': text}}]}, 'echo': 'apiCallBack'}
    else:
        typename = command[0]
        if typename not in market_type_list.keys():
            r1 = max(
                process.extract(
                    typename,
                    market_type_list.keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            r2 = max(
                process.extract(
                    typename,
                    abbr_list['type'].keys(), limit=25),
                key=lambda x: fuzz.ratio(
                    typename,
                    x[0]))
            if r1[1] > r2[1]:
                typename = r1[0]
            else:
                typename = r2[0]
                typename = abbr_list['type'][r2[0]]
        id_ = int(data_list[typename])
        r_source = requests.get('https://www.ceve-market.org/query_history/',
                                params={'typeid': id_, 'tq': 1, 'regionid': 0}, headers={"referer": "https://www.ceve-market.org/home/"}).json()
        fp = '$' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + \
             str(random.randint(random.randint(0, 150), random.randint(200, 300)))
        # img_base.save('data/images/cache/' + fp + ".png")
        market_grapic_maker(js=r_source, title=typename, svp='./data/images/cache/' + fp + '.png')
        return {'action': 'send_group_msg',
                'params': {'group_id': group_id,
                           'message': [{'type': 'image',
                                        'data': {'file': 'cache\\' + fp + '.png'}}]},
                'echo': 'IMAGE' + 'data/images/cache/' + fp + ".png"}


def cut(command: str) -> dict:
    cmd = {'bref': "", 'command': []}
    cache = ""
    co = []
    bref = "."
    for i in command:
        if bref != "" and i != " ":
            if i == "." or i == "/":
                continue
            bref += i
            continue
        elif bref != "" and i == " ":
            cmd['bref'] = bref
            bref = ""
            continue
        if i in PUNC_LIST:
            if cache != "":
                co.append(cache)
                cache = ""
            continue
        cache += i
    if cache != "":
        co.append(cache)
    cmd['command'] = co
    if bref != "":
        cmd['bref'] = bref
    return cmd


def guild_configure(n, st) -> Union[dict, bool]:
    if not n:
        return False
    command = cut(n)
    print(command)
    if command['bref'] not in API_GUILD_DICT.keys():
        return False
    return eval(API_GUILD_DICT[command['bref']] + "(command=command['command'], group_id=-1, sender=-1)")


def configure(js: dict, st) -> Union[str, bool]:
    if not js:
        return False
    try:
        if js['post_type'] == 'message' and js['message_type'] == 'group':
            # search for function
            try:
                message = js['message'][0]['data']['text']
            except KeyError as e:
                return False
            command = cut(message)
            print(command)
            try:
                # res = sys.modules[__name__].__dict__[API_GROUP_DICT[command['bref']]](command['command'], js['group_id'])
                if command['bref'] not in API_GROUP_DICT.keys():
                    return False
                res = eval(API_GROUP_DICT[command['bref']] +
                           "(command=command['command'], group_id=js['group_id'], sender=js['sender'])")
                if not res:
                    return False
                # res = str(res)
            except KeyError:
                traceback.print_exc()
                return False
            # print(res)
            # res = res.replace("'", '"')
            res = json.dumps(res)
            # print(res)
            print(time.time() - st)
            return res
        elif js['post_type'] == 'notice' and js['notice_type'] == 'group_increase':
            res = json.dumps({'action': 'send_group_msg', 'params': {'group_id': js['group_id'], 'message': [
                {'type': 'at', 'data': {'qq': js['user_id']}}, {'type': 'text', 'data': {'text': '欢迎入群\n发送help获取帮助列表'}}
            ]}})
            return res
        else:
            return False
        # {'action': 'send_group_msg',
        #  'params': {'group_id': 794396722, 'command': [
        #             {'type': 'text', 'data': {'text': '物品国服售价（伏尔戈）'}}]}}
    except KeyError:
        return False


begin_time = time.time()

if __name__ == '__main__':
    pre_load()
    # r = marketing('伏尔戈', '三钛合金',  'zh')
    # r1 = jita('三钛合金', 404)
    # print(r)
    # r = oiCor(['Ministry of Internal Order'], 404)
    # r = acc(['4', '7'], 404)
    # r = oaccm(['4', '5', '2'], 404)
    # r = sktree(['帕拉丁级'], 404)
    r = prev(['帕拉丁级'], 404)
    print(r)
    # r1 = kb(['自由蛋蛋'], 404)
    # r2 = okb(['icehuang Odunen'], 404)
    # print(r1['params']['message'][2]['data']['text'])
    # print(r2['params']['message'][2]['data']['text'])
    ...
    # print(sys.modules['__main__'].__dict__['jita'](
    #     {'post_type': 'command', 'message_type': 'group', 'time': 1655366778, 'self_id': 758948668,
    #      'sub_type': 'normal', 'anonymous': None, 'command': [{'type': 'text', 'data': {'text': '.jita 帕拉丁级'}}],
    #      'message_seq': 713518, 'font': 0, 'group_id': 940157939, 'raw_message': '.jita 帕拉丁级',
    #      'sender': {'age': 0, 'area': '', 'card': '◆姐妹会 阿斯特罗级', 'level': '', 'nickname': '◆姐妹会 阿斯特罗级',
    #                 'role': 'member', 'sex': 'unknown', 'title': '', 'user_id': 3562377918}, 'user_id': 3562377918,
    #                 'message_id': 1712097179}))
