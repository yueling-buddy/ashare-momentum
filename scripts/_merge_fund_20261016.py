import json, os, datetime

PATH = "data/fundamentals.json"
TODAY = "2026-10-16"

with open(PATH, encoding="utf-8") as f:
    d = json.load(f)

new = {
    "300369": {
        "name": "绿盟科技",
        "updated": TODAY,
        "business": "主营信息安全产品研发、生产、销售及专业安全服务，覆盖安全产品（抗DDoS/IDS/WAF/漏洞管理等）与安全运营服务，为政企、金融、运营商、能源等行业提供全线网络安全产品与解决方案。",
        "position": "国内网络安全头部厂商，八大安全实验室（星云/格物/伏影等）支撑研发，海外设硅谷、东京、伦敦、新加坡等子公司；2025年营收25.41亿元，仍小幅亏损但同比大幅减亏。",
        "financial": "2025年营收25.41亿元（同比+7.78%），归母净利润-4525万元（同比减亏87.6%，2024年亏3.65亿）；毛利率53.88%；2026中报营收4.48亿、归母-3084万（同比减亏55.7%）。",
        "logic": "网络安全自主可控主题，亏损持续收窄、经营现金流转正（2025经营现金流2.16亿/+58.6%）；当前股价贴近MA50、RPS高位、量比放量，动量信号强但需看扭亏节奏。",
        "risk": "连续年度亏损、净利尚未转正；政府/大客户占比高、回款周期长；行业竞争与价格战；2025年营收3年CAGR为负。",
    },
    "601083": {
        "name": "锦江航运",
        "updated": TODAY,
        "business": "主营国际、国内海上集装箱运输，深耕东北亚、东南亚及国内航线，提供班轮运输服务；2025年运输服务收入占比超98%。",
        "position": "综合性集装箱航运公司，截至2025年末经营55艘船舶（28艘自有+27艘租赁），持续新船投放与运力更新（“2+2”1100箱、“4+4”1800箱建造项目）。",
        "financial": "2025年营收70.1亿元（同比+17.43%），归母净利润15.0亿元（同比+47.0%），毛利率31.82%，ROE16.63%，拟10派6.12元（分红率约70%）；2026中报营收19.9亿、归母4.16亿（同比-4.95%）。",
        "logic": "高股息+盈利稳健的航运标的，受益东北亚航线景气与运力扩张；当前价处阶段新高附近、RPS高位、量比放量，兼具动量与安全边际。",
        "risk": "运价周期波动大；燃油/汇率风险；2026中报净利小幅回落（-4.95%），需关注后续运价与新船交付节奏；行业运力供给上行。",
    },
}

added = []
for code, info in new.items():
    if code not in d:
        d[code] = info
        added.append(code)
    else:
        # preserve existing, only refresh listed fields if missing
        for k, v in info.items():
            if k not in d[code] or not d[code][k]:
                d[code][k] = v
        d[code]["updated"] = TODAY

tmp = PATH + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
os.replace(tmp, PATH)
print("added:", added, "total:", len(d))
