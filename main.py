import json
import time
import traceback

import botpy
import threadpool
from botpy.message import Message

import websockets
import asyncio
import sup
import os

import re

import threading

global market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, \
    abbr_list, desc_list, trans_version_df, npc_cor_list, dogma_list, plaSch_list, traits_list, ship_data_list, plaSch_id_list, logger, logger2


# *** group bot *** #

def request_to_json(msg):
    for ia in range(len(msg)):
        if msg[ia] == "{" and msg[-1] == "\n":
            return json.loads(msg[ia:])
    return None


async def send(websocket, request):
    if request:
        print('-*-Send request-*-')
        await websocket.send(request)


def send_outer(js, ft, ws, loop):
    print('-Send Wrapper Sending-')
    loop.run_until_complete(send(
        ws, sup.configure(
            js=js, st=ft)
    ))


async def rt(websocket, path):
    global logger, logger2
    print("---Server Activated---")
    tpool = threadpool.ThreadPool(4)
    loop = asyncio.new_event_loop()
    while True:
        try:
            r = await websocket.recv()
            r = request_to_json(r)
            # print('\n', r)
            if not r:
                continue
            if 'echo' in r.keys():
                try:
                    if len(r['echo']) > 5 and r['echo'][:5] == "IMAGE":
                        os.remove(r['echo'][5:])
                except Exception as e:
                    print('echo处理错误：', e)
                continue
            # ft = time.time()
            # tosend = sup.configure(js=r, ws=websocket, st=ft)
            # print(r['group_id'] in logger_list, r['group_id'], type(r['group_id']))
            task = threadpool.makeRequests(send_outer, [([r, time.time(), websocket, loop], None)])
            # task = threadpool.makeRequests(lambda *args: print('get'), ((r, time.time(), websocket), ))
            # task = threadpool.makeRequests(lambda: print('get'), (None, None))
            tpool.putRequest(task[0])
            # tpool.wait()
        except ConnectionResetError as e:
            print('connection reset')
            continue
        except ConnectionError as e:
            print("connection error")
            asyncio.get_event_loop().stop()
            return 0
        except websockets.ConnectionClosedError as e:
            print('connection closed')
            break
        except BaseException as e:
            traceback.print_exc()
            logger2.warning(e)
    tpool.wait()


def re_log(rtm: time.struct_time):
    global logger, logger2
    ntm = time.localtime(time.time())
    if rtm.tm_year != ntm.tm_year or rtm.tm_yday != ntm.tm_yday:
        logger, logger2 = sup.new_log()


# *** guild bot *** #
class GuildBot(botpy.Client):
    async def on_at_message_create(self, message: Message):
        global logger, logger2
        msarg = re.search(r'(^<@!\d+> )(.*)', message.content).group(2)
        try:
            re_back = sup.guild_configure(msarg, time.time())
            if re_back:
                r = re_back['params']['message'][0]['data']['text']
                logger2.info('send message: %s' % r)
                await message.reply(content=r)
        except Exception as e:
            logger2.error(e)
            await message.reply(content='机器人出错了')
        # print(message.content)
        # print(msarg)
        # print(re_back)


async def guild_bot_start():
    async with client as c:
        await c.start(appid="xxx", token="xxx")
        # pass


if __name__ == '__main__':
    try:
        re_log(rtm=time.localtime(time.time()))
        print('---Data Pre Loading---')
        market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, \
            abbr_list, desc_list, trans_version_df, npc_cor_list, dogma_list, plaSch_list, traits_list, ship_data_list, plaSch_id_list, logger, \
            logger2, skill_dict, sch_expand_dict, sch_prod_dict_f, sch_prod_dict_e = sup.pre_load()
        server = websockets.serve(rt, 'localhost', 5705)
        print('---Group Bot Server Started---')
        intent = botpy.Intents(public_guild_messages=True)
        client = GuildBot(intents=intent)
        print('---Guild Bot Server Started---')
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_until_complete(guild_bot_start())
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt as __e:
        print('---end service---')
