# -*- coding: utf-8 -*-
"""Atomic-merge 3 missing fundamentals for 2026-10-15 intraday re-screen.
Preserves all existing entries; only adds/overwrites the 3 missing codes.
"""
import json, os

PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fundamentals.json")
PATH = os.path.abspath(PATH)
TODAY = "2026-10-15"

new_entries = {
    "601857": {
        "name": "中国石油",
        "business": "原油及天然气勘探、开发、生产、输送、销售及新能源业务；原油及石油产品炼制、化工与新材料生产销售；成品油及天然气销售与贸易。国内最大油气生产商之一。",
        "position": "上证50/沪深300权重蓝筹，A+H（00857）两地上市，中石油集团控股；国内油气勘探开发龙头，油气管网与炼化一体化布局完整。",
        "financial": "2025年营收28,644.69亿元（同比-2.5%），归母净利润1,573.02亿元（同比-4.48%），EPS 0.86元；毛利率21.59%，ROE 10.10%，资产负债率36.37%；拟10派2.5元，全年派息率54.7%。",
        "logic": "高股息防御属性+油气当量产量同比+2.5%、风光发电量+68%新能源提速；布伦特油价同比-14.6%致利润小幅下滑，但现金流与分红稳健，低估值避险配置价值。",
        "risk": "国际油价大幅波动；炼化毛利受价差挤压；新能源转型资本开支压力；宏观需求走弱拖累化工品与成品油销量。",
        "updated": TODAY,
    },
    "600901": {
        "name": "江苏金租",
        "business": "融资租赁业务（金融租赁），覆盖基础设施、交通运输、能源环保、设备等领域；国内唯一A股上市金融租赁公司。",
        "position": "国有控股非银行金融机构（江苏交通控股、南京银行、IFC、法巴租赁等股东），2018年上市；多元金融板块高ROE标的。",
        "financial": "2025年营收61.09亿元（同比+15.75%），归母净利润32.41亿元（同比+10.12%），EPS 0.56元；净利率53.22%，ROE 13.11%，资产负债率84.14%；拟10派1.7元。",
        "logic": "业绩连续双位数稳健增长、高ROE、低估值（TTM PE约12.8倍）；应收融资租赁款+17.5%扩张，能源环保/交通设备租赁需求韧性支撑。",
        "risk": "资产负债率偏高（84%）；利率与信用周期影响租金回收；经营活动现金流为负（投放扩张期）；监管对金融租赁资本约束趋严。",
        "updated": TODAY,
    },
    "002003": {
        "name": "伟星股份",
        "business": "中高档服饰及箱包辅料（拉链、钮扣等）研发、制造与销售；拉链占比约53%、钮扣约41%（注：区别于002372伟星新材塑料管道）。",
        "position": "国内服饰辅料龙头，全球知名服装品牌核心供应商；出口占比约35%，客户分散（前五大客户销售占比<9%）。",
        "financial": "2025年营收48.00亿元（同比+2.69%），归母净利润6.45亿元（同比-7.96%），EPS 0.55元；毛利率42.03%，ROE 14.41%，资产负债率32.38%；拟10派4元。",
        "logic": "高毛利（42%）辅料赛道龙头，品牌黏性强、现金流健康；营收小幅增长但净利受费用/汇兑拖累下滑，海外产能与客户结构优化支撑长期稳健。",
        "risk": "下游服装消费景气波动；出口受海外需求与贸易摩擦影响；原材料（铜、锌合金）价格上行；净利连续下滑需观察拐点。",
        "updated": TODAY,
    },
}

# load
with open(PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

before = len(data)
for code, ent in new_entries.items():
    data[code] = ent  # add or overwrite
after = len(data)

# atomic write
tmp = PATH + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
os.replace(tmp, PATH)

print(f"merged {len(new_entries)} entries: {list(new_entries.keys())}")
print(f"fundamentals.json size: before={before} after={after}")
