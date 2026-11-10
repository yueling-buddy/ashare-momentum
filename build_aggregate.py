# -*- coding: utf-8 -*-
"""生成 A股选股聚合门户 + 高成长股票子页。

数据源：
  - 动量看板快照 : a-share-dashboard/data/meta.json
  - 高成长       : ../_screen/growth_full.json
  - 稳健股息     : ../_screen/高股息稳健资产_主表.csv

输出：
  - aggregate.html : 门户入口，选股功能 3 卡（动量看板 / 高成长股票 / 稳健股息票）
  - growth.html    : 高成长股票明细表（按净利同比均值排序，涨红跌绿配色）
"""
import os, json, csv
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                 # A股大作战
SCREEN = os.path.join(ROOT, "_screen")
DATA = os.path.join(HERE, "data")

# ---------- 读取 ----------
meta = json.load(open(os.path.join(DATA, "meta.json"), encoding="utf-8"))
g = json.load(open(os.path.join(SCREEN, "growth_full.json"), encoding="utf-8"))
div_rows = list(csv.DictReader(open(os.path.join(SCREEN, "高股息稳健资产_主表.csv"), encoding="utf-8-sig")))

def fnum(r, k):
    v = r.get(k)
    try:
        return float(v)
    except Exception:
        return None

gd = g["data"]

# ---- EPS 4-quarter single-quarter YoY trend (from _screen/eps_trend.json) ----
ET = os.path.join(SCREEN, "eps_trend.json")
if not os.path.exists(ET):
    raise RuntimeError("eps_trend.json missing: run _screen/eps_trend.py first")
et = json.load(open(ET, encoding="utf-8"))["data"]
if len(et) != len(gd):
    raise RuntimeError("eps_trend count mismatch: %d vs %d" % (len(et), len(gd)))
for r in gd:
    v = et.get(str(r.get("code", "")).zfill(6), {})
    r["eps_q_yoys"] = v.get("g", [None, None, None, None])
    r["eps_trend_score"] = v.get("score")
    r["eps_stars"] = v.get("stars", 0)
    r["eps_valid"] = v.get("valid", 0)

# 高成长筛选：营收同比均值>20 且 净利同比均值>20，按净利同比均值降序，最多 200
hi = [r for r in gd if (fnum(r, "np_yoy_avg") or -1e9) > 20 and (fnum(r, "rev_yoy_avg") or -1e9) > 20]
hi.sort(key=lambda r: fnum(r, "np_yoy_avg"), reverse=True)
if len(hi) < 30:
    hi = [r for r in gd if fnum(r, "np_yoy_avg") is not None]
    hi.sort(key=lambda r: fnum(r, "np_yoy_avg"), reverse=True)
growth_sel = hi[:200]

grades = Counter(r["稳健分级"] for r in div_rows)

m_asof = (meta.get("asof") or meta.get("generated_at") or "").split(" ")[0]
m_count = meta.get("count", "")
g_count = g.get("count", len(gd))
g_date = str(g.get("generated_at", "")).split(" ")[0]
div_total = len(div_rows)

# ---------- 颜色（A股口径：涨红跌绿） ----------
def color_cls(v):
    if v is None:
        return "neu"
    return "up" if v > 0 else ("down" if v < 0 else "neu")

def pct(v):
    if v is None:
        return "—"
    return ("+%.1f" % v if v > 0 else "%.1f" % v) + "%"

# ================= growth.html (full universe + filters + one-click std) =================
# Rendered from growth_template.html so the full data table survives every rebuild.
_gjson_js = json.dumps(gd, ensure_ascii=False).replace("</", "<\\/")
with open(os.path.join(HERE, "growth_template.html"), encoding="utf-8") as f:
    _tpl = f.read()
_growth_html = (_tpl.replace("__GJSON__", _gjson_js)
                    .replace("__GGEN__", str(g.get("generated_at", "")))
                    .replace("__GTOTAL__", str(g_count)))
with open(os.path.join(HERE, "growth.html"), "w", encoding="utf-8") as f:
    f.write(_growth_html)


CSS_PORTAL = """
:root{
  --bg:#f5f7fa; --card:#ffffff; --ink:#1f2937; --muted:#6b7280;
  --line:#e5e7eb; --accent:#2563eb; --accent-soft:#eff6ff;
  --green:#16a34a; --amber:#d97706; --gray:#9ca3af;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
     background:var(--bg);color:var(--ink);line-height:1.6;}
.wrap{max-width:1080px;margin:0 auto;padding:34px 20px 60px;}
header h1{font-size:26px;font-weight:700;letter-spacing:.5px;}
header p{color:var(--muted);margin-top:6px;font-size:14px;}
.group{margin-top:26px;}
.group h2{font-size:18px;margin-bottom:14px;display:flex;align-items:center;gap:8px;}
.group h2 .cnt{font-size:12px;color:var(--muted);font-weight:400;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;
    text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:10px;
    transition:.15s;position:relative;}
.card:hover{transform:translateY(-3px);box-shadow:0 10px 28px rgba(0,0,0,.08);border-color:var(--accent);}
.card .ico{font-size:26px;}
.card h3{font-size:17px;font-weight:700;}
.card p{font-size:13px;color:var(--muted);flex:1;}
.card .meta{font-size:12px;color:var(--accent);font-weight:600;background:var(--accent-soft);
    padding:5px 9px;border-radius:8px;line-height:1.4;}
.tag{align-self:flex-start;font-size:11px;font-weight:700;padding:3px 9px;border-radius:999px;}
.tag.pub{background:#dcfce7;color:var(--green);}
.card .go{font-size:13px;color:var(--accent);font-weight:600;}
footer{margin-top:42px;font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:16px;}
"""

# ================= aggregate.html (门户) =================
portal = (
    "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1.0'>"
    "<title>A股研究终端 · 聚合入口</title>"
    "<meta name='description' content='A股选股工具统一入口：动量看板、高成长股票、稳健股息票。'>"
    "<meta name='theme-color' content='#2563eb'>"
    "<link rel='icon' href='favicon.png' type='image/png'>"
    "<style>" + CSS_PORTAL + "</style></head><body><div class='wrap'>"
    "<header><h1>A股研究终端</h1>"
    "<p>选股工具统一入口 · 子工具均在新标签页打开</p></header>"
    "<section class='group'><h2>选股功能 <span class='cnt'>(3)</span></h2>"
    "<div class='grid'>"
    "<a class='card' href='index.html' target='_blank' rel='noopener'>"
    "<div class='ico'>📊</div><h3>动量看板</h3>"
    "<p>全市场 RPS×FIP 动量排名、板块强度与个股强度分布总看板。</p>"
    "<div class='meta'>覆盖 " + str(m_count) + " 只 · asof " + m_asof + " · 全市场 RPS×FIP 动量排名</div>"
    "<span class='tag pub'>公开</span><span class='go'>打开 →</span></a>"
    "<a class='card' href='growth.html' target='_blank' rel='noopener'>"
    "<div class='ico'>🚀</div><h3>高成长股票</h3>"
    "<p>全量 A 股业绩数据 + 8 项阈值交互筛选，一键套用「高成长」标准；含 PE TTM 估值区间与指标口径速查。</p>"
    "<div class='meta'>全量 " + str(g_count) + " 只 · 净利/营收同比可排 · " + g_date + "</div>"
    "<span class='tag pub'>公开</span><span class='go'>打开 →</span></a>"
    "<a class='card' href='high-dividend/index.html' target='_blank' rel='noopener'>"
    "<div class='ico'>💰</div><h3>稳健股息票</h3>"
    "<p>高股息扫描：稳健分级（核心/观察/一般）+ 连续分红、TTM 股息率与 5 年累计派息率。</p>"
    "<div class='meta'>" + str(div_total) + " 只 · 稳健核心 " + str(grades.get('稳健核心', 0)) + " / 观察 " + str(grades.get('稳健观察', 0)) + "</div>"
    "<span class='tag pub'>公开</span><span class='go'>打开 →</span></a>"
    "</div></section>"
    "<footer>点击卡片在新标签页打开对应工具；子工具地址更新时本页自动保持最新。<br>"
    "收藏本页网址即可，无需记住各子工具地址。</footer>"
    "</div></body></html>"
)
with open(os.path.join(HERE, "aggregate.html"), "w", encoding="utf-8") as f:
    f.write(portal)

print("OK -> aggregate.html (%d bytes), growth.html (%d bytes), growth rows=%d"
      % (os.path.getsize(os.path.join(HERE, "aggregate.html")),
         os.path.getsize(os.path.join(HERE, "growth.html")),
         len(gd)))
