import json
import time

import botpy
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


async def rt(websocket, path):
    global logger, logger2
    print("---Server Activated---")
    while True:
        try:
            r = await websocket.recv()
            r = request_to_json(r)
            print('\n', r)
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
            threading.Thread(
                target=lambda js, ft: asyncio.new_event_loop().run_until_complete(
                    send(
                        websocket, sup.configure(
                            js=js, st=ft))), args=(
                    r, time.time())).start()
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
            logger2.warning(e)


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


if __name__ == '__main__':
    try:
        re_log(rtm=time.localtime(time.time()))
        print('---Data Pre Loading---')
        market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, \
            abbr_list, desc_list, trans_version_df, npc_cor_list, dogma_list, plaSch_list, traits_list, ship_data_list, plaSch_id_list, logger, logger2, skill_dict = sup.pre_load()
        server = websockets.serve(rt, 'localhost', 5705)
        print('---Group Bot Server Started---')
        intent = botpy.Intents(public_guild_messages=True)
        client = GuildBot(intents=intent)
        print('---Guild Bot Server Started---')
        # client.run(appid="102022324", token="CNahqy40gZbst062nFOe1DNOLaA74rm2")
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_until_complete(guild_bot_start())
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt as __e:
        print('---end service---')

# 测试发送图片！！
