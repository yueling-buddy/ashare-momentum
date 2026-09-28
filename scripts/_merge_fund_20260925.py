# -*- coding: utf-8 -*-
import json, os
from datetime import date

PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fundamentals.json")
PATH = os.path.abspath(PATH)

with open(PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

new = {
    "688512": {
        "name": "慧智微",
        "updated": date.today().strftime("%Y-%m-%d"),
        "business": "射频前端芯片及模组（5G/4G 射频前端）的研发、设计与销售；产品应用于智能手机与物联网无线通信模组，客户含三星、vivo、小米、OPPO、荣耀等头部手机品牌，以及华勤通讯、龙旗科技等一线 ODM 厂和移远通信、广和通、日海智能等头部模组厂。",
        "position": "国产射频前端芯片设计商，创新性提出可重构射频前端平台；产品线覆盖 L-PAMiF、L-FEM、PAMiD/L-PAMiD、5G PAM 等高集成模组，进入国内外头部手机机型与一线 ODM/模组供应链，是射频前端国产替代标的。",
        "financial": "2025 年营收 8.07 亿元（+54.06%）、归母净亏损 2.29 亿元（同比减亏 47.76%）；2026Q1 营收 2.15 亿元（+56.87%），自 2025Q1 起连续多季单季营收同比+30%以上；2026H1 营收 4.68 亿元（+32.14%）、归母净亏损 1.37 亿元。尚未盈利，毛利率约 7%，但营收高增、亏损持续收窄（2025 全年）。",
        "logic": "射频前端国产替代+高端模组量产出货，营收连续高增、亏损收窄；今日 RPS91.9、量比 2.14，处强度区间（vsMA50 约 29%）入选盘中复筛。",
        "risk": "仍处亏损（毛利率仅约 7%）、经营现金流为负；前五大客户销售占比约 76%、客户集中度高；盈利兑现与下游智能手机需求、终端客户导入节奏强相关，波动风险大。",
    }
}

data.update(new)
n = len(data)

tmp = PATH + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
os.replace(tmp, PATH)
print(f"merged 688512; total entries={n}")
