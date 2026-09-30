import json, os, datetime
P = r"D:\Workbuddy Space\A股大作战\a-share-dashboard\data\fundamentals.json"
today = "2026-09-30"
d = json.load(open(P, encoding="utf-8"))

entry = {
    "name": "郑州煤电",
    "business": "煤炭开采、洗选加工与销售、煤矿工程施工。主营煤炭（2026中报占比约86%），产地河南，2025年煤炭产量710万吨（同比+3.80%）、销量702万吨。",
    "position": "河南省属煤炭企业，市值偏小、股价弹性高；当前RPS强势但业绩深亏，属困境反转博弈标的。",
    "financial": "2025年营收35.52亿（同比-15.52%），归母净利润-9.27亿（同比由盈转亏-428%），EPS -0.76元，资产负债率81.88%；2026H1营收6.75亿、归母-1.43亿。公司2026年目标：煤炭产量680万吨、营收37亿、利润总额1亿。",
    "logic": "煤价低位+超化煤矿停产计提减值拖累业绩，但综合RPS强势（90.4）、量比放大（2.41）、股价站上MA50，资金博弈煤价反弹与困境反转预期。",
    "risk": "业绩持续亏损、资产负债率偏高、煤价继续下行风险、超化煤矿复产与安全生产不确定、ROE为负缺乏盈利支撑。",
    "updated": today,
}
d["600121"] = entry
assert json.loads(json.dumps(d))  # sanity
tmp = P + ".tmp"
json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
os.replace(tmp, P)
print("merged 600121, total entries:", len(d))
