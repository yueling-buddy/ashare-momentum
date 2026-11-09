# -*- coding: utf-8 -*-
"""生成 A股选股聚合门户（风格对齐 yueling-buddy.github.io/us-stock-portal）。

门户为链接卡片式入口（非内嵌大页）：顶部品牌 + 吸顶胶囊导航切换分组，
每组模块以卡片呈现，点击在新标签页打开对应工具/子页。
- 选股功能：选股盘 / 动量看板 / 高股息 / 预选筛选
- 待拓展：净利润逐年 / 分红质量·再融资比 / 盘前盘后调度 / 聚合页自动刷新
- 栏目：选股日报（盘前/盘中/盘后三档）

同时生成 prescreen.html（预选筛选子页，自包含表格）。
输出： a-share-dashboard/aggregate.html + prescreen.html
"""
import os, json, csv, collections
import pandas as pd

ROOT = r"D:\Workbuddy Space\A股大作战"
DASH = os.path.join(ROOT, "a-share-dashboard")
SCREEN = os.path.join(ROOT, "_screen")

PICK = os.path.join(DASH, "data", "pick_latest.json")
DIV  = os.path.join(SCREEN, "高股息稳健资产_主表.csv")
PRE  = os.path.join(SCREEN, "A股预选筛选结果_20261104.xlsx")
GROWTH = os.path.join(SCREEN, "业绩快速增长企业_筛选结果.csv")
GROWTH_JSON = os.path.join(SCREEN, "growth_full.json")
OUT_PORTAL = os.path.join(DASH, "aggregate.html")
OUT_PRE    = os.path.join(DASH, "prescreen.html")


def esc(x):
    s = "" if x is None else str(x)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def fmt(x, nd=2):
    try:
        return f"{float(x):.{nd}f}"
    except:
        return esc(x)

# ---------- 读取快照数据（仅用于卡片上的「最新快照」一行） ----------
def snapshots():
    out = {}
    try:
        P = json.load(open(PICK, encoding="utf-8"))
        m = P["meta"]; dp = m.get("dpwd", {})
        zone = dp.get("zone", "").split(" ")[0] or "—"
        out["pick"] = f"快照 {esc(m.get('asof','-'))} · 候选 {m.get('n_pool','-')} 只 · DPWD {esc(zone)} (TEMP10 {fmt(dp.get('TEMP10','-'),1)})"
    except Exception as e:
        out["pick"] = "数据读取失败"
    try:
        rows = list(csv.DictReader(open(DIV, encoding="utf-8-sig")))
        g = collections.Counter(r["稳健分级"] for r in rows)
        def yld(r):
            try: return float(r["TTM股息率(%)"])
            except: return -1
        top = max(rows, key=yld)
        out["div"] = f"{len(rows)} 只 · 稳健核心 {g.get('稳健核心',0)} / 观察 {g.get('稳健观察',0)} · 最高 TTM 股息率 {fmt(top['TTM股息率(%)'],2)}%"
    except Exception:
        out["div"] = "数据读取失败"
    out["pre"] = "2026-11-04 · 23 只 · 财务+动量综合预选"
    try:
        _gj = json.load(open(GROWTH_JSON, encoding="utf-8"))
        out["growth"] = f"{_gj.get('count',0)} 只 · 全量可筛 · 一键标准：市值≥50亿+三年双增≥20%+最新季度三20%"
    except Exception:
        out["growth"] = "数据读取失败"
    out["mom"] = "全市场 RPS×FIP 动量排名 · 板块强度"
    out["col"] = "每个交易日 10:00 / 10:30 / 14:00 三档发布"
    return out

S = snapshots()

# ---------- 卡片 ----------
def card(ico, title, desc, meta, href, tag, tagtype):
    if href:
        return (f'<a class="card" href="{esc(href)}" target="_blank" rel="noopener">'
                f'<div class="ico">{ico}</div><h3>{esc(title)}</h3>'
                f'<p>{esc(desc)}</p>'
                f'<div class="meta">{esc(meta)}</div>'
                f'<span class="tag {tagtype}">{esc(tag)}</span>'
                f'<span class="go">打开 →</span></a>')
    else:
        return (f'<div class="card disabled">'
                f'<div class="ico">{ico}</div><h3>{esc(title)}</h3>'
                f'<p>{esc(desc)}</p>'
                f'<div class="meta">{esc(meta)}</div>'
                f'<span class="tag soon">敬请期待</span>'
                f'<span class="go">即将上线</span></div>')

tools_cards = "".join([
    card("🔍", "A股选股盘", "盘中 RPS×FIP 选股日报：综合RPS>85 · FIP250≤0 · 市值>50亿 · 量比>1.5 等多重筛选，含 9 级漏斗与强势板块。",
         S["pick"], "pick.html", "实时", "pub"),
    card("📊", "动量看板", "全市场 RPS×FIP 动量排名、板块强度与个股强度分布的总看板。",
         S["mom"], "index.html", "公开", "pub"),
    card("💰", "高股息稳健资产", "854 只高股息扫描：稳健分级（核心/观察/一般）+ 连续分红、TTM 股息率、5 年累计派息率与分红质量。",
         S["div"], "high-dividend/index.html", "公开", "pub"),
    card("🧪", "预选筛选", "财务 + 动量综合预选：毛利率/净利率、营收与利润同比、分红率逐条判定。",
         S["pre"], "prescreen.html", "公开", "pub"),
    card("🚀", "业绩快速增长", "高成长扫描：近三年营收/净利同比增速均值均≥20%、规模达标，且最新季度营收/净利/EPS 同比三项均≥20%。",
         S["growth"], "growth.html", "公开", "pub"),
])

road_cards = "".join([
    card("📈", "净利润逐年追踪", "2021–2025 业绩报表逐年净利润增速与复合增长看板。",
         "数据就绪 · netprofit_yearly/ 已沉淀 2021–2025 业绩报表", None, "soon", "soon"),
    card("🔁", "分红质量 · 再融资比", "纯回报型（未再融资）筛选：分红/再融资比 survivors 看板。",
         "数据就绪 · bulk_financing.csv + f5_dividend_detail.csv", None, "soon", "soon"),
    card("⏱️", "盘前 / 盘后调度", "选股日报当前为盘中快照；待建盘前预选 + 盘后回顾双频调度。",
         "规划中", None, "soon", "soon"),
    card("🔄", "聚合页自动刷新", "本门户为静态快照聚合；待建随各数据源刷新自动重渲并发布。",
         "规划中", None, "soon", "soon"),
])

cols_cards = "".join([
    card("📰", "选股日报", "A股盘中选股日报栏目：每交易日 10:00 / 10:30 / 14:00 三档发布，含候选池与强势板块。",
         S["col"], "pick.html", "公开", "pub"),
])

# ---------- 门户 HTML ----------
PORTAL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>A股研究终端 · 聚合入口</title>
<meta name="description" content="一个网址聚合全部 A股 选股工具与栏目：选股盘、动量看板、高股息、预选筛选。">
<meta name="theme-color" content="#2563eb">
<link rel="icon" href="favicon.png" type="image/png">
<style>
  :root{
    --bg:#f5f7fa; --card:#ffffff; --ink:#1f2937; --muted:#6b7280;
    --line:#e5e7eb; --accent:#2563eb; --accent-soft:#eff6ff;
    --green:#16a34a; --amber:#d97706; --gray:#9ca3af;
    --violet:#7c3aed; --blue:#2563eb;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
       background:var(--bg);color:var(--ink);line-height:1.6;}
  .wrap{max-width:1080px;margin:0 auto;padding:34px 20px 60px;}
  header h1{font-size:26px;font-weight:700;letter-spacing:.5px;}
  header p{color:var(--muted);margin-top:6px;font-size:14px;}
  nav{position:sticky;top:0;background:rgba(245,247,250,.92);backdrop-filter:blur(8px);
      z-index:10;padding:14px 0;margin:22px 0 6px;border-bottom:1px solid var(--line);
      display:flex;gap:10px;flex-wrap:wrap;}
  nav button{border:1px solid var(--line);background:var(--card);color:var(--ink);
      padding:8px 18px;border-radius:999px;cursor:pointer;font-size:14px;font-weight:600;transition:.15s;}
  nav button.active{background:var(--accent);color:#fff;border-color:var(--accent);}
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
  .tag.local{background:#fef3c7;color:var(--amber);}
  .tag.soon{background:#f3f4f6;color:var(--gray);}
  .card .go{font-size:13px;color:var(--accent);font-weight:600;}
  .card.disabled{opacity:.72;cursor:default;}
  .card.disabled:hover{transform:none;box-shadow:none;border-color:var(--line);}
  footer{margin-top:42px;font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:16px;}
  .hidden{display:none;}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>A股研究终端</h1>
    <p>选股工具与定期栏目的统一入口 · 所有子工具在新标签页打开</p>
  </header>

  <nav>
    <button data-g="tools" class="active">选股功能</button>
    <button data-g="road">待拓展</button>
    <button data-g="cols">栏目</button>
  </nav>

  <section class="group" id="g-tools">
    <h2>选股功能 <span class="cnt">（5）</span></h2>
    <div class="grid">__TOOLS__</div>
  </section>

  <section class="group hidden" id="g-road">
    <h2>待拓展 <span class="cnt">（4）</span></h2>
    <div class="grid">__ROAD__</div>
  </section>

  <section class="group hidden" id="g-cols">
    <h2>栏目 <span class="cnt">（1）</span></h2>
    <div class="grid">__COLS__</div>
  </section>

  <footer>
    点击卡片会在新标签页打开对应工具或栏目；若某个功能卡片暂时打不开，刷新或稍后再试即可。<br>
    收藏本页网址就够了，子工具地址更新时这里会自动保持最新。
  </footer>
</div>
<script>
document.querySelectorAll('nav button').forEach(function(b){
  b.onclick=function(){
    document.querySelectorAll('nav button').forEach(function(x){x.classList.remove('active');});
    b.classList.add('active');
    document.querySelectorAll('.group').forEach(function(g){g.classList.add('hidden');});
    var el=document.getElementById('g-'+b.dataset.g); if(el) el.classList.remove('hidden');
  };
});
</script>
</body>
</html>
"""
PORTAL = (PORTAL.replace("__TOOLS__", tools_cards)
                 .replace("__ROAD__", road_cards)
                 .replace("__COLS__", cols_cards))
with open(OUT_PORTAL, "w", encoding="utf-8") as f:
    f.write(PORTAL)

# ---------- 预选筛选子页 ----------
def load_prescreen():
    import openpyxl
    wb = openpyxl.load_workbook(PRE, read_only=True)
    ws = wb[wb.sheetnames[0]]
    it = ws.iter_rows(values_only=True)
    hdr = [str(h) for h in next(it)]
    rows = []
    for row in it:
        if row is None or all(c is None for c in row):
            continue
        rows.append({hdr[i]: (row[i] if i < len(row) else None) for i in range(len(hdr))})
    return hdr, rows

hdr, rows = load_prescreen()
show = ["代码","名称","细分行业","财务更新","市值(亿)","综合RPS","RPS50","毛利率%","净利率%","营收(亿)","营收同比%","利润同比%","三年分红率%","年数","备注"]
show = [h for h in show if h in hdr]
def chg_cls(x):
    try:
        f=float(x); return "up" if f>0 else ("down" if f<0 else "")
    except: return ""
th = "".join(f"<th>{esc(h)}</th>" for h in show)
tr = ""
for r in rows:
    tds = ""
    for h in show:
        v = r.get(h)
        if h in ("综合RPS","RPS50"): tds += f"<td>{fmt(v,2)}</td>"
        elif h in ("营收同比%","利润同比%","毛利率%","净利率%"): tds += f'<td class="{chg_cls(v)}">{fmt(v,1)}</td>'
        elif h == "备注": tds += f'<td class="rem">{esc(v)}</td>'
        else: tds += f"<td>{esc(v)}</td>"
    tr += f"<tr>{tds}</tr>"

PRE_HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>A股预选筛选结果</title>
<meta name="theme-color" content="#2563eb">
<link rel="icon" href="favicon.png" type="image/png">
<style>
  :root{{--bg:#f5f7fa;--card:#fff;--ink:#1f2937;--muted:#6b7280;--line:#e5e7eb;--accent:#2563eb;--up:#d4380d;--down:#16a34a;}}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink);line-height:1.6;}}
  .wrap{{max-width:1280px;margin:0 auto;padding:30px 20px 60px;}}
  .crumb{{font-size:13px;color:var(--muted);margin-bottom:6px;}}
  .crumb a{{color:var(--accent);text-decoration:none;}}
  header h1{{font-size:22px;font-weight:700;}}
  header p{{color:var(--muted);font-size:13px;margin-top:4px;}}
  .block{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin-top:16px;}}
  .tablescroll{{overflow-x:auto;}}
  table{{border-collapse:collapse;width:100%;font-size:13px;}}
  th{{background:#eff6ff;color:var(--accent);text-align:right;padding:8px 10px;border-bottom:2px solid #bfdbfe;white-space:nowrap;}}
  th:first-child,td:first-child,th:nth-child(2),td:nth-child(2),th:nth-child(3),td:nth-child(3),th:nth-child(4),td:nth-child(4){{text-align:left;}}
  td{{padding:7px 10px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap;}}
  tbody tr:hover{{background:#f7fafd;}}
  .up{{color:var(--up);font-weight:600;}}
  .down{{color:var(--down);font-weight:600;}}
  .rem{{color:var(--muted);font-size:12px;max-width:200px;white-space:normal;}}
  .note{{margin-top:10px;font-size:12px;color:var(--muted);}}
</style>
</head>
<body>
<div class="wrap">
  <div class="crumb"><a href="aggregate.html">A股研究终端</a> › 预选筛选</div>
  <header>
    <h1>A股预选筛选结果</h1>
    <p>财务 + 动量综合预选 · 数据日期 2026-11-04 · 共 {len(rows)} 只（逐条判定）</p>
  </header>
  <div class="block">
    <div class="tablescroll"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>
    <div class="note">来源：<code>A股预选筛选结果_20261104.xlsx</code>（23 只明细）。本页为聚合门户「预选筛选」模块的独立子页；该模块尚在整合中，后续将接入自动化刷新。</div>
  </div>
</div>
</body>
</html>
"""
with open(OUT_PRE, "w", encoding="utf-8") as f:
    f.write(PRE_HTML)

# ---------- 业绩快速增长子页（全量 + 交互式筛选 + 一键标准） ----------
def load_growth_full():
    try:
        with open(GROWTH_JSON, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"generated_at": "", "count": 0, "data": []}

_gj = load_growth_full()
_gdata = _gj.get("data", [])
_ggen = _gj.get("generated_at", "") or "2026-11-09"
_gtotal = _gj.get("count", 0)
_gjson_js = json.dumps(_gdata, ensure_ascii=False).replace("</", "<\\/")

GROWTH_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>A股业绩快速增长 · 全量筛选</title>
<meta name="theme-color" content="#2563eb">
<link rel="icon" href="favicon.png" type="image/png">
<style>
  :root{--bg:#f5f7fa;--card:#fff;--ink:#1f2937;--muted:#6b7280;--line:#e5e7eb;--accent:#2563eb;--up:#d4380d;--down:#16a34a;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink);line-height:1.6;}
  .wrap{max-width:1360px;margin:0 auto;padding:30px 20px 60px;}
  .crumb{font-size:13px;color:var(--muted);margin-bottom:6px;}
  .crumb a{color:var(--accent);text-decoration:none;}
  header h1{font-size:22px;font-weight:700;}
  header p{color:var(--muted);font-size:13px;margin-top:4px;}
  .block{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin-top:16px;}
  .filters{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:flex-end;margin-bottom:6px;}
  .fitem{display:flex;flex-direction:column;gap:3px;}
  .fitem label{font-size:11px;color:var(--muted);}
  .fitem .inp{display:flex;align-items:center;gap:4px;}
  .fitem input{width:88px;border:1px solid var(--line);border-radius:7px;padding:6px 8px;font-size:13px;outline:none;}
  .fitem input:focus{border-color:var(--accent);}
  .bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:8px 0 12px;}
  .bar input.search{flex:1;min-width:220px;border:1px solid var(--line);border-radius:8px;padding:8px 12px;font-size:13px;outline:none;}
  .bar input.search:focus{border-color:var(--accent);}
  .btn{border:none;border-radius:8px;padding:8px 14px;font-size:13px;cursor:pointer;font-weight:600;}
  .btn.std{background:var(--accent);color:#fff;}
  .btn.reset{background:#eef2f7;color:var(--ink);}
  .btn.onlystd{background:#fff;color:var(--accent);border:1px solid var(--accent);}
  .btn:hover{opacity:.9;}
  .cnt{font-size:13px;color:var(--accent);font-weight:600;margin-left:auto;}
  .tablescroll{overflow-x:auto;max-height:72vh;overflow-y:auto;}
  table{border-collapse:collapse;width:100%;font-size:13px;}
  thead th{position:sticky;top:0;background:#eff6ff;color:var(--accent);text-align:right;padding:8px 10px;border-bottom:2px solid #bfdbfe;white-space:nowrap;z-index:1;cursor:pointer;user-select:none;}
  thead th .ar{font-size:10px;color:#93c5fd;}
  th:first-child,td:first-child,th:nth-child(2),td:nth-child(2),th:nth-child(3),td:nth-child(3){text-align:left;}
  td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap;}
  tbody tr:hover{background:#f7fafd;}
  .up{color:var(--up);font-weight:600;}
  .na{color:var(--muted);}
  .tagstd{display:inline-block;background:#fde8e8;color:var(--up);font-size:12px;padding:1px 8px;border-radius:6px;margin-left:8px;vertical-align:middle;}
  .note{margin-top:12px;font-size:12px;color:var(--muted);line-height:1.7;}
  code{background:#eef2f7;padding:1px 5px;border-radius:4px;}
</style>
</head>
<body>
<div class="wrap">
  <div class="crumb"><a href="aggregate.html">A股研究终端</a> › 业绩快速增长（全量筛选）</div>
  <header>
    <h1>A股业绩快速增长 · 全量筛选<span id="stdmark"></span></h1>
    <p>高成长扫描 · 数据日期 __GGEN__ · 全量 __GTOTAL__ 只标的（含全部指标，可自由筛选）；一键套用「业绩快速增长标准」。</p>
  </header>
  <div class="block">
    <div class="filters" id="filters">
      <div class="fitem"><label>市值(亿) ≥</label><div class="inp"><input id="f_mcap_yi" type="number" step="any" placeholder="不限"></div></div>
      <div class="fitem"><label>营收均值(亿) ≥</label><div class="inp"><input id="f_rev_avg_yi" type="number" step="any" placeholder="不限"></div></div>
      <div class="fitem"><label>净利均值(万) ≥</label><div class="inp"><input id="f_np_avg_wan" type="number" step="any" placeholder="不限"></div></div>
      <div class="fitem"><label>营收增速均值% ≥</label><div class="inp"><input id="f_rev_yoy_avg" type="number" step="any" placeholder="不限"></div></div>
      <div class="fitem"><label>净利增速均值% ≥</label><div class="inp"><input id="f_np_yoy_avg" type="number" step="any" placeholder="不限"></div></div>
      <div class="fitem"><label>营收Q同比% ≥</label><div class="inp"><input id="f_rev_q_yoy" type="number" step="any" placeholder="不限"></div></div>
      <div class="fitem"><label>净利Q同比% ≥</label><div class="inp"><input id="f_np_q_yoy" type="number" step="any" placeholder="不限"></div></div>
      <div class="fitem"><label>EPS同比% ≥</label><div class="inp"><input id="f_eps_yoy" type="number" step="any" placeholder="不限"></div></div>
    </div>
    <div class="bar">
      <input class="search" id="q" placeholder="搜索代码 / 名称 / 行业…" oninput="apply()">
      <button class="btn std" onclick="oneClick()">⚡ 一键筛选（业绩快速增长标准）</button>
      <button class="btn onlystd" onclick="onlyStd()">仅看标准达标</button>
      <button class="btn reset" onclick="resetAll()">重置</button>
      <span class="cnt" id="cnt"></span>
    </div>
    <div class="tablescroll"><table><thead><tr id="thead"></tr></thead><tbody id="tb"></tbody></table></div>
    <div class="note">
      口径：市值取 2026-11-09 实时行情总市值快照（腾讯行情，单位亿元；已剔除 ST/退市；原静态 mcap.csv 已停用）；营收=营业总收入、净利润=净利润（元，展示时营收→亿、净利→万元）；
      同比取报表披露「同比增长」（年报=全年同比，季报=1–9月累计同比）；EPS 同比=(最新季度累计EPS−去年同期累计EPS)/去年同期EPS；
      去年同期 EPS≤0 视为无法判定而剔除。近三年=2023/2024/2025 年报，任一年缺失或同比无法计算者剔除。
      来源：akshare 东财业绩报表。金融类（银行/券商/保险）未单独剔除，其营收口径不同请自行甄别。<br>
      「业绩快速增长标准」= 市值≥50亿 且 近三年营收均值≥1亿、净利均值≥1000万、营收/净利同比增速均值均≥20% 且 最新季度营收/净利/EPS 同比均≥20%（与一键按钮一致）。<br>数据体检：EPS 同比因去年同期 EPS≤0 或缺失而无法判定者约占 21.6%，显示为空且不参与该项筛选；增速极端值来自亏损/低基数或重组，为披露口径原值。
    </div>
  </div>
</div>
<script>
const DATA = __GJSON__;
const STD = {mcap_yi:50, rev_avg_yi:1, np_avg_wan:1000, rev_yoy_avg:20, np_yoy_avg:20, rev_q_yoy:20, np_q_yoy:20, eps_yoy:20};
const COLS = [
  {k:"code", t:"代码"},
  {k:"name", t:"名称"},
  {k:"industry", t:"行业"},
  {k:"mcap_yi", t:"市值(亿)", d:1},
  {k:"rev_avg_yi", t:"营收均值(亿)", d:1},
  {k:"rev_yoy_avg", t:"营收增速均值%", d:1, up:true},
  {k:"np_avg_wan", t:"净利均值(万)", d:1},
  {k:"np_yoy_avg", t:"净利增速均值%", d:1, up:true},
  {k:"rev_q_yoy", t:"营收Q同比%", d:1, up:true},
  {k:"np_q_yoy", t:"净利Q同比%", d:1, up:true},
  {k:"eps_yoy", t:"EPS同比%", d:1, up:true}
];
let sortKey=null, sortDir=-1;
function fmt(v, d){
  if(v===null||v===undefined||(typeof v==="number"&&isNaN(v))) return null;
  return Number(v).toFixed(d);
}
function buildHead(){
  const tr=document.getElementById("thead");
  tr.innerHTML = COLS.map(c=>{
    let ar="";
    if(sortKey===c.k) ar = sortDir<0 ? " ▼" : " ▲";
    return '<th data-k="'+c.k+'">'+c.t+'<span class="ar">'+ar+'</span></th>';
  }).join("");
  tr.querySelectorAll("th").forEach(function(th){
    th.onclick=function(){
      const k=th.getAttribute("data-k");
      if(sortKey===k) sortDir=-sortDir; else {sortKey=k; sortDir=-1;}
      buildHead(); apply();
    };
  });
}
function getMin(id){
  const v=document.getElementById(id).value.trim();
  if(v==="") return null;
  const n=parseFloat(v);
  return isNaN(n)?null:n;
}
function apply(){
  const q=(document.getElementById("q").value||"").trim().toLowerCase();
  const mins={
    mcap_yi:getMin("f_mcap_yi"), rev_avg_yi:getMin("f_rev_avg_yi"),
    np_avg_wan:getMin("f_np_avg_wan"), rev_yoy_avg:getMin("f_rev_yoy_avg"),
    np_yoy_avg:getMin("f_np_yoy_avg"), rev_q_yoy:getMin("f_rev_q_yoy"),
    np_q_yoy:getMin("f_np_q_yoy"), eps_yoy:getMin("f_eps_yoy")
  };
  let rows=DATA.filter(function(r){
    for(const k in mins){ const m=mins[k]; if(m!=null && !(r[k]!=null && r[k]>=m)) return false; }
    if(q){ const t=(r.code+" "+(r.name||"")+" "+(r.industry||"")).toLowerCase(); if(t.indexOf(q)<0) return false; }
    return true;
  });
  if(sortKey){
    rows=rows.slice().sort(function(a,b){
      let x=a[sortKey], y=b[sortKey];
      if(x==null&&y==null) return 0;
      if(x==null) return 1; if(y==null) return -1;
      if(typeof x==="string"){ return x.localeCompare(y,"zh")*sortDir; }
      return (x-y)*sortDir;
    });
  }
  const tb=document.getElementById("tb");
  tb.innerHTML = rows.map(function(r){
    const tds=COLS.map(function(c){
      const v=fmt(r[c.k], c.d||0);
      if(v===null) return '<td class="na">—</td>';
      if(c.up) return '<td class="up">'+v+'</td>';
      return '<td>'+v+'</td>';
    }).join("");
    return '<tr>'+tds+'</tr>';
  }).join("");
  document.getElementById("cnt").textContent='显示 '+rows.length+' / 共 '+DATA.length+' 只';
}
function oneClick(){
  for(const k in STD){ const el=document.getElementById("f_"+k); if(el) el.value=STD[k]; }
  document.getElementById("q").value="";
  document.getElementById("stdmark").innerHTML='<span class="tagstd">已套用标准</span>';
  apply();
}
function onlyStd(){
  for(const k in STD){ const el=document.getElementById("f_"+k); if(el) el.value=STD[k]; }
  document.getElementById("q").value="";
  document.getElementById("stdmark").innerHTML='<span class="tagstd">标准达标</span>';
  apply();
}
function resetAll(){
  ["f_mcap_yi","f_rev_avg_yi","f_np_avg_wan","f_rev_yoy_avg","f_np_yoy_avg","f_rev_q_yoy","f_np_q_yoy","f_eps_yoy"].forEach(function(id){ document.getElementById(id).value=""; });
  document.getElementById("q").value="";
  document.getElementById("stdmark").innerHTML="";
  apply();
}
buildHead();
apply();
</script>
</body>
</html>
"""
GROWTH_HTML = (GROWTH_HTML.replace("__GJSON__", _gjson_js)
                           .replace("__GGEN__", _ggen)
                           .replace("__GTOTAL__", str(_gtotal)))
OUT_GROWTH = os.path.join(DASH, "growth.html")
with open(OUT_GROWTH, "w", encoding="utf-8") as f:
    f.write(GROWTH_HTML)


print("OK portal ->", OUT_PORTAL)
print("OK prescreen ->", OUT_PRE)
print("OK growth ->", OUT_GROWTH)
print("tools cards:", tools_cards.count('<a class="card"'), "| road:", road_cards.count('<div class="card disabled"'), "| cols:", cols_cards.count('<a class="card"'))
