# 数据文件详情
```
 ├─ abbr_list.yaml          【bot数据】简称库（动态添加）
 ├─ blp.csv                 【游戏数据】蓝图名称<->id 映射
 ├─ blpd.yaml               【衍生数据】蓝图制造根材料
 ├─ blueprints.yaml         【游戏源数据】蓝图属性
 ├─ data.csv                【游戏数据】物品名称<->id 映射 
 ├─ description.csv         【游戏数据】物品名称<->描述 映射
 ├─ dogma.csv               【游戏数据】属性名称<->id 映射
 ├─ enabled_apis.json       【bot数据】启用的api
 ├─ md.csv                  【游戏数据】物品名称<->市场分类 映射
 ├─ npc.csv                 【游戏数据】NPC军团名称<->id 映射
 ├─ planetSchematics.yaml   【游戏源数据】行星产物数据
 ├─ plaSch.csv              【游戏数据】行星产物名称<->id 映射
 ├─ prod.csv                【游戏数据】蓝图产物名称<->蓝图名称 映射
 ├─ region.csv              【游戏数据】星域名称<->id 映射
 ├─ shipList.csv            【游戏数据】舰船名称<->id 映射
 ├─ skill.yaml              【游戏数据】物品技能需求
 ├─ te.csv                  【游戏数据】星系、星域、星座翻译
 ├─ traits.json             【游戏数据】舰船加成
 ├─ traits.yaml             【游戏数据】舰船加成
 └─ trans.csv               【游戏数据】翻译列表
```

<details>
<summary>注释</summary>
 - 【bot数据】机器人运行逻辑所需的文件
 - 【游戏数据】根据公开数据转换成用于机器人API提供的文件
 - 【游戏源数据】公开的数据
</details>


> traits.json的生成可以参照[Phobos](https://github.com/pyfa-org/Phobos)

同样是由于重装电脑，这些文件的批处理我已经找不到了，所以。。。以后CCP的更新就凑合着用吧

> 另附CCP公开的数据文件地址：[resource-eveonline](https://developers.eveonline.com/resource)
