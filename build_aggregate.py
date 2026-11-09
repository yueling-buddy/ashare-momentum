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

# ================= 高成长表格行 =================
rows_html = []
for r in growth_sel:
    rev = fnum(r, "rev_yoy_avg")
    npv = fnum(r, "np_yoy_avg")
    rq = fnum(r, "rev_q_yoy")
    nq = fnum(r, "np_q_yoy")
    pe = fnum(r, "pe_ttm")
    mcap = fnum(r, "mcap_yi")
    rows_html.append(
        "<tr>"
        "<td class='code'>%s</td>"
        "<td class='name'>%s</td>"
        "<td class='ind'>%s</td>"
        "<td class='num'>%s</td>"
        "<td class='num %s'>%s</td>"
        "<td class='num %s'>%s</td>"
        "<td class='num %s'>%s</td>"
        "<td class='num %s'>%s</td>"
        "<td class='num'>%s</td>"
        "</tr>" % (
            r.get("code", ""), r.get("name", ""), r.get("industry", "") or "—",
            ("%.1f" % mcap) if mcap is not None else "—",
            color_cls(rev), pct(rev),
            color_cls(npv), pct(npv),
            color_cls(rq), pct(rq),
            color_cls(nq), pct(nq),
            ("%.1f" % pe) if pe is not None else "—",
        )
    )
rows_html = "\n".join(rows_html)

# 行业下拉选项（用于筛选框）
industries = sorted({ (r.get("industry") or "") for r in growth_sel if r.get("industry") })
ind_opts = "".join("<option value='%s'>%s</option>" % (i, i) for i in industries)

# ================= growth.html =================
CSS = """
:root{
  --bg:#f5f7fa; --card:#fff; --ink:#1f2937; --muted:#6b7280;
  --line:#e5e7eb; --accent:#2563eb; --accent-soft:#eff6ff;
  --up:#dc2626; --down:#16a34a; --neu:#9ca3af;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
     background:var(--bg);color:var(--ink);line-height:1.6;}
.wrap{max-width:1180px;margin:0 auto;padding:30px 20px 60px;}
header h1{font-size:24px;font-weight:700;}
header p{color:var(--muted);margin-top:6px;font-size:14px;}
.back{display:inline-block;margin:14px 0 4px;color:var(--accent);font-weight:600;
      text-decoration:none;font-size:14px;}
.note{background:var(--accent-soft);color:var(--accent);font-size:12px;font-weight:600;
      padding:6px 11px;border-radius:8px;display:inline-block;margin-bottom:14px;}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);
       border-radius:12px;overflow:hidden;font-size:13px;}
thead th{position:sticky;top:0;background:#f1f5f9;color:var(--ink);font-weight:700;
         padding:10px 12px;text-align:left;cursor:pointer;user-select:none;white-space:nowrap;
         border-bottom:2px solid var(--line);}
thead th:hover{color:var(--accent);}
tbody td{padding:9px 12px;border-bottom:1px solid var(--line);}
tbody tr:hover{background:#f8fafc;}
td.num{text-align:right;font-variant-numeric:tabular-nums;}
td.code{font-family:ui-monospace,Menlo,Consolas,monospace;color:var(--muted);}
td.name{font-weight:600;}
td.ind{color:var(--muted);max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.up{color:var(--up);font-weight:600;}
.down{color:var(--down);font-weight:600;}
.neu{color:var(--neu);}
.filters{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;margin:6px 0 4px;}
.filters label{display:flex;flex-direction:column;gap:5px;font-size:12px;color:var(--muted);}
.filters input,.filters select{border:1px solid var(--line);border-radius:6px;padding:7px 9px;font:inherit;font-size:13px;background:#fff;color:var(--ink);min-width:130px;}
.filters input[type=number]{min-width:96px;}
.filters button{border:1px solid var(--accent);background:var(--accent);color:#fff;border-radius:6px;padding:8px 14px;font:inherit;font-size:13px;cursor:pointer;}
.filters button.ghost{background:#fff;color:var(--accent);}
.fcount{display:inline-block;margin:6px 0 2px;color:var(--muted);font-size:12px;font-weight:600;}
footer{margin-top:34px;font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px;}
"""

growth_html = (
    "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1.0'>"
    "<title>高成长股票 · A股业绩快速增长</title>"
    "<meta name='theme-color' content='#2563eb'>"
    "<style>" + CSS + "</style></head><body><div class='wrap'>"
    "<header><h1>🚀 高成长股票</h1>"
    "<p>A股业绩快速增长扫描 · 数据源 growth_full.json（生成于 " + g_date + "）</p></header>"
    "<a class='back' href='aggregate.html'>← 返回聚合页</a><br>"
     "<span class='note'>筛选：营收同比均值 &gt; 20% 且 净利同比均值 &gt; 20%，按净利同比均值降序（最多 200 只）· 点击表头排序 · 下方可二次筛选</span>"
     "<div class='filters'>"
     "<label>关键词<input type='text' id='f_kw' placeholder='如 300641 / 正丹'></label>"
     "<label>行业<select id='f_ind'><option value=''>全部行业</option>" + ind_opts + "</select></label>"
     "<label>市值≥(亿)<input type='number' id='f_mcap' value='0' step='10' min='0'></label>"
     "<label>营收同比%≥<input type='number' id='f_rev' value='0' step='5' min='0'></label>"
     "<label>净利同比%≥<input type='number' id='f_np' value='0' step='50' min='0'></label>"
     "<label>最新季净利%≥<input type='number' id='f_nq' value='0' step='10' min='0'></label>"
     "<button class='ghost' id='f_reset' type='button'>重置</button>"
     "</div>"
     "<span class='fcount' id='fcount'></span>"
     "<table id='gt'><thead><tr>"
    "<th data-k='code'>代码</th><th data-k='name'>名称</th><th data-k='ind'>行业</th>"
    "<th data-k='mcap' class='num'>市值(亿)</th>"
    "<th data-k='rev' class='num'>营收同比%↑</th><th data-k='np' class='num'>净利同比%↑</th>"
    "<th data-k='rq' class='num'>最新季营收同比%</th><th data-k='nq' class='num'>最新季净利同比%</th>"
    "<th data-k='pe' class='num'>PE(TTM)</th>"
    "</tr></thead><tbody>" + rows_html + "</tbody></table>"
    "<footer>涨红跌绿（A股口径）：正增长标红、负增长标绿。本页为静态快照，数据更新后需重渲发布。<br>"
    "共展示 " + str(len(growth_sel)) + " 只 / 全量 " + str(g_count) + " 只。</footer>"
    "</div><script>"
    "var tbl=document.getElementById('gt');"
    "var tb=tbl.tBodies[0];"
    "var order={};"
    "tbl.querySelectorAll('thead th').forEach(function(th){"
    "  th.onclick=function(){"
    "    var k=th.dataset.k, asc=!order[k]; order={}; order[k]=asc;"
    "    var rows=Array.prototype.slice.call(tb.rows);"
    "    rows.sort(function(a,b){"
    "      var x=a.cells[th.cellIndex].textContent, y=b.cells[th.cellIndex].textContent;"
    "      if(k==='code'||k==='name'||k==='ind'){return asc?x.localeCompare(y,'zh'):y.localeCompare(x,'zh');}"
    "      x=parseFloat(x.replace(/[^0-9.\\-]/g,''))||0; y=parseFloat(y.replace(/[^0-9.\\-]/g,''))||0;"
    "      return asc?x-y:y-x;"
    "    });"
    "    rows.forEach(function(r){tb.appendChild(r);});"
    "  };"
    "});"
    "function applyFilters(){"
    "  var kw=document.getElementById('f_kw').value.trim().toLowerCase();"
    "  var ind=document.getElementById('f_ind').value;"
    "  var mcap=parseFloat(document.getElementById('f_mcap').value)||0;"
    "  var rev=parseFloat(document.getElementById('f_rev').value)||0;"
    "  var npf=parseFloat(document.getElementById('f_np').value)||0;"
    "  var nq=parseFloat(document.getElementById('f_nq').value)||0;"
    "  var shown=0;"
    "  Array.prototype.slice.call(tb.rows).forEach(function(tr){"
    "    var c=tr.children;"
    "    var code=c[0].textContent.toLowerCase(), name=c[1].textContent.toLowerCase(), industry=c[2].textContent;"
    "    var m=parseFloat(c[3].textContent.replace(/[^0-9.\\-]/g,''))||0;"
    "    var rv=parseFloat(c[4].textContent.replace(/[^0-9.\\-]/g,''))||0;"
    "    var npv=parseFloat(c[5].textContent.replace(/[^0-9.\\-]/g,''))||0;"
    "    var nqv=parseFloat(c[7].textContent.replace(/[^0-9.\\-]/g,''))||0;"
    "    var ok=true;"
    "    if(kw && !(code.indexOf(kw)>=0||name.indexOf(kw)>=0)) ok=false;"
    "    if(ind && industry!==ind) ok=false;"
    "    if(m<mcap) ok=false;"
    "    if(rv<rev) ok=false;"
    "    if(npv<npf) ok=false;"
    "    if(nqv<nq) ok=false;"
    "    tr.style.display=ok?'':'none';"
    "    if(ok) shown++;"
    "  });"
    "  document.getElementById('fcount').textContent='筛选后 '+shown+' 只';"
    "}"
    "['f_kw','f_mcap','f_rev','f_np','f_nq'].forEach(function(id){document.getElementById(id).addEventListener('input',applyFilters);});"
    "document.getElementById('f_ind').addEventListener('change',applyFilters);"
    "document.getElementById('f_reset').addEventListener('click',function(){"
    "  document.getElementById('f_kw').value='';document.getElementById('f_ind').value='';"
    "  document.getElementById('f_mcap').value=0;document.getElementById('f_rev').value=0;"
    "  document.getElementById('f_np').value=0;document.getElementById('f_nq').value=0;"
    "  applyFilters();"
    "});"
    "applyFilters();"
    "</script></body></html>"
)
with open(os.path.join(HERE, "growth.html"), "w", encoding="utf-8") as f:
    f.write(growth_html)

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
    "<p>业绩快速增长扫描：营收/净利同比均值双增，按净利同比均值排序，含最新季度同比与 PE。</p>"
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
         len(growth_sel)))
