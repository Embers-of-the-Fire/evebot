<h1 align="center">EVE BOT</h1>
<h5 align="center"><img src="./img/lang2.svg"> <img src="./img/lang.svg"></h5>

## 简介

这是一个基于 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 制作的eve机器人

## 主要功能

### 小工具

 - **.help** 查看帮助 &#10004;
 - **.iss** 留言（会保存在`./bot_logs/issue_logs/`下）
 - **.abtype** 添加物品简称
 - **.abcol** 添加物品组简称
 - **.search** 搜索 &#10004;

### 查询功能

 - **.desc** 查看物品描述 &#10004;
 - **.trans** 翻译 &#10004;
 - **.status** 查询服务器状态 &#10004;
 - **.jita** 查询国服伏尔戈市场订单 &#10004;
 - **.ojita** 查询世界服伏尔戈市场订单 &#10004;
 - **.prev** 查询国服伏尔戈物品历史价格 &#10004;
 - **.oprev** 查询世界服伏尔戈物品历史价格 &#10004;
 - **.col** 查询国服伏尔戈市场物品组订单 &#10004;
 - **.ocol** 查询世界服伏尔戈市场物品组订单 &#10004;
 - **.wtb** 查询国服特定星域市场订单 &#10004;
 - **.owtb** 查询世界服特定星域市场订单 &#10004;
 - **.blp** 查询蓝图基本属性 &#10004;
 - **.blpm** 查询国服伏尔戈市场蓝图材料订单
 - **.oblpm** 查询世界服伏尔戈市场蓝图材料订单
 - **.blpe** 查询蓝图详细信息
 - **.blpem** 查询国服伏尔戈市场蓝图基础材料订单
 - **.oblpem** 查询世界服伏尔戈市场蓝图基础材料订单
 - **.blpmh** 查询国服伏尔戈市场蓝图材料历史价格
 - **.oblpmh** 查询世界服伏尔戈市场蓝图材料历史价格
 - **.acc** 计算加速器作用效果
 - **.accm** 查询国服加速器价值
 - **.oaccm** 查询世界服加速器价值
 - **.sktree** 查询物品技能树 &#10004;
 - **.sch** 查询行星资源 &#10004;
 - **.sche** 查询行星资源具体制造路线
 - **.lp** 查询国服特定军团伏尔戈市场忠诚点价值 &#10004;
 - **.olp** 查询世界服特定军团伏尔戈市场忠诚点价值 &#10004;
 - **.lph** 查询国服特定军团伏尔戈市场忠诚点价值历史记录
 - **.olph** 查询世界服特定军团伏尔戈市场忠诚点价值历史记录
 - **.dogma** 查询物品属性
 - **.trait** 查询物品加成 &#10004;
 - **.mkd** 查询物品市场分类 &#10004;
 - **.sch** 查询行星资源 &#10004;
 - **.oiAll** 查询世界服联盟
 - **.iAll** 查询国服联盟
 - **.oiCor** 查询世界服军团
 - **.iCor** 查询国服军团
 - **.oiCha** 查询世界服人物
 - **.iCha** 查询国服人物
 - **.kb** 查询国服kb
 - **.okb** 查询世界服kb

备注：带有&#10004;表示支持频道

## 实现方法

### 数据源

#### WEB数据源

晨曦服游戏数据获取：[晨曦](https://esi.evepc.163.com/) [Swagger](https://esi.evepc.163.com/ui/)

宁静服游戏数据获取：[宁静](https://esi.evetech.net/) [Swagger](https://esi.evetech.net/ui/)

> 该机器人没有使用到任何需要ESI授权的部分

市场数据获取：[EVE国服市场中心](https://www.ceve-market.org/index/) [API文档](https://www.ceve-market.org/api/)

#### 其他数据

存放于`./supporting_files/`下，以`yaml`和`csv`文件为主

数据文件详细解释请见 [数据文件](./supporting_files/README.md)

> 为了维护的简便性机器人没有使用MySQL，而是直接以文件形式存储

### QQ机器人服务

使用 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) (`websocket`) 作为机器人内核

### 源程序

由于该机器人是断断续续并且开发环境不稳定，导致我已经无法理解部分代码的设计意图与后续的修改方案，所以我放弃了重构和修改，~~开始摆烂~~任其自然。所以代码中含有大量无意义的片段和低效率（重复劳动.jpg）的片段。

~~大佬轻点骂。~~

```
├─bot_logs             【自动生成】机器人的日志
│  ├─issue_logs        【自动生成】issue和abtype、abcol的日志
│  └─logs              【自动生成】其他日志
├─data                 【go-cqhttp】相关必须数据
│  └─images            【go-cqhttp】相关图片文件
│     ├─cache          【自动生成】机器人缓存图片
│     └─sup_images     【手动创建】机器人的帮助图片
├─fonts                【支持文件】机器人生成图片所用的字体文件
├─supporting_files     【重要核心数据】核心数据库
├─adm.py               【程序扩展】提供了管理员操作功能，但是还没写
├─main.py              【程序主体】与go-cqhttp的交互
├─sup.py               【程序扩展】机器人核心功能组件
└─dialog_logger.py     【程序扩展】言论记录为日志，通过'admin'功能设置，但是还没写
```

## 如何部署

### 1.安装go-cqhttp

前往 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 并根据环境下载

启动后根据提示进行配置，记得选ws模式，然后参考我的`config.yml`进行配置

> 配置请参考Go-CqHttp文档

如果用不到频道机器人（这玩意申请麻烦还不能重名，删了就完了）可以删掉相关内容，如果怕删错了，就把`main.py`中的相关段落改成这样：

```python
from main import * # 无需该行，该行仅为标注
if __name__ == '__main__':
    try:
        re_log(rtm=time.localtime(time.time()))
        print('---Data Pre Loading---')
        market_type_list, blp_list, reg_list, mkd_list, prod_list, data_list, blpt_list, id_list, blp_detail_list, \
            abbr_list, desc_list, trans_version_df, npc_cor_list, dogma_list, plaSch_list, traits_list, ship_data_list, plaSch_id_list, logger, logger2, skill_dict = sup.pre_load()
        server = websockets.serve(rt, 'localhost', 5705)
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt as __e:
        print('---end service---')
```

然后在配置完成go-cqhttp后，先打开go-cqhttp，会提示你需要登录。扫码后go-cqhttp新创建的文件记得保留，以后就不用扫码登录了。
> 该操作无法在云服务器上完成，请部署时复制token文件和设备信息

随后运行`main.py`，加载时间~~很长~~能够接受，等到提示`Group Bot Server Started`后就可以运行go-cqhttp了。

> 如仍有其它问题，请参考 [Go-CqHttp](https://github.com/Mrs4s/go-cqhttp) 相关文档

## 支持

[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)  
[EVE Online](https://eveonline.com/)  
[星战前夜：晨曦](https://evepc.163.com/)  
[国服市场中心网](https://ceve-market.org/)

## 其他

如果运行出现问题请附带报错日志提交issue或discussion中留言，最好是自己尝试修复，因为我也不见得比你有多熟悉我的代码
