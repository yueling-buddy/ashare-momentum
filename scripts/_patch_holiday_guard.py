"""One-shot patch: re-add the non-trading-day guard to scripts/refresh.py.

Lost after the working tree was reset to HEAD (the 2026-09-25 fix was never
committed). Idempotent: every replacement is skipped if already applied.
"""
import io
import os
import sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "refresh.py")
NL = "\r\n"

raw = open(P, "rb").read()
try:
    t = raw.decode("utf-8")
except Exception:
    print("refresh.py is not utf-8, abort")
    sys.exit(1)

def ins(anchor, added, after=True):
    """anchor: exact substring already in t (no newline). added: list of lines."""
    if anchor not in t:
        print("ANCHOR MISSING:", anchor[:70])
        sys.exit(2)
    i = t.index(anchor)
    # find end of that physical line
    j = t.find(NL, i)
    if j < 0:
        j = len(t)
    if after:
        return t[:j] + NL + NL.join(added) + t[j:]
    # insert BEFORE the physical line that contains the anchor
    i2 = t.rfind(NL, 0, i) + 1
    return t[:i2] + NL.join(added) + NL + NL + t[i2:]

HELPER = [
    'def _is_static_snapshot(frames: dict, spot: pd.DataFrame) -> bool:',
    '    """Holiday guard: on a non-trading day Sina spot returns a FROZEN snapshot of',
    '    the previous session (close and volume identical tick by tick). Writing that as',
    '    "today" would create a fake trading day in kline_cache and poison the 5-day',
    '    volume baseline / MA / RSI / RPS used by pick_daily.py.',
    '    Rule: close+volume of spot vs the last cached bar, >99% identical => not a',
    '    trading day. Fail-safe: any error => False (treat as a normal trading day).',
    '    """',
    '    try:',
    '        if spot is None or spot.empty or not frames:',
    '            return False',
    '        if not all(c in spot.columns for c in ("code", "\\u6700\\u65b0\\u4ef7", "\\u6210\\u4ea4\\u91cf")):',
    '            return False',
    '        s = spot.copy()',
    '        s["code"] = s["code"].astype(str).str.zfill(6)',
    '        s = s.set_index("code")',
    '        tot = same = 0',
    '        for code, df in frames.items():',
    '            if df is None or len(df) == 0 or code not in s.index:',
    '                continue',
    '            r = s.loc[code]',
    '            if isinstance(r, pd.DataFrame):',
    '                r = r.iloc[0]',
    '            try:',
    '                sc = float(r.get("\\u6700\\u65b0\\u4ef7")); sv = float(r.get("\\u6210\\u4ea4\\u91cf"))',
    '                lc = float(df["close"].iloc[-1]); lv = float(df["volume"].iloc[-1])',
    '            except Exception:',
    '                continue',
    '            if not (np.isfinite(sc) and np.isfinite(sv) and np.isfinite(lc) and np.isfinite(lv)):',
    '                continue',
    '            tot += 1',
    '            if abs(sc - lc) < 1e-6 and abs(sv - lv) < 1e-6:',
    '                same += 1',
    '        if tot < 100:',
    '            return False',
    '        return (same / tot) > 0.99',
    '    except Exception:',
    '        return False',
]

# 1) module flag
if "HOLIDAY_SNAPSHOT = False" not in t:
    t = ins('KLINE_SEED = DATA_DIR / "kline_cache_seed.parquet"',
            ['HOLIDAY_SNAPSHOT = False   # set by the non-trading-day guard in close mode'])

# 2) signature + trade_date override
t = t.replace(
    'def apply_spot_to_frames(frames: dict, spot: pd.DataFrame, names: dict, now_bj: datetime):',
    'def apply_spot_to_frames(frames: dict, spot: pd.DataFrame, names: dict, now_bj: datetime, force_history: bool = False):')
t = t.replace(
    '    trade_date = trade_date_for(now_bj)',
    '    trade_date = None if force_history else trade_date_for(now_bj)')

# 3) helper function
if "_is_static_snapshot" not in t:
    t = ins('def apply_spot_to_frames(frames: dict, spot: pd.DataFrame, names: dict, now_bj: datetime, force_history: bool = False):',
            HELPER, after=False)

# 4) main: detect + force history
old_main = '    updated, calc_date = apply_spot_to_frames(frames, spot, names, now_bj)'
new_main = (
    '    # Non-trading-day guard (close mode only): if spot is a frozen snapshot of the'
    ' previous session, drop the fake bar and fall back to the last cached trading day.'
    + NL +
    '    global HOLIDAY_SNAPSHOT' + NL +
    '    HOLIDAY_SNAPSHOT = False' + NL +
    '    if args.mode == "close" and _is_static_snapshot(frames, spot):' + NL +
    '        _lc = [pd.Timestamp(fr["date"].iloc[-1]).date() for fr in frames.values() if len(fr)]' + NL +
    '        _last = max(_lc) if _lc else now_bj.date()' + NL +
    '        print("[guard] non-trading day: spot is a frozen snapshot of %s; dropping fake bar %s" % (_last, now_bj.date()))' + NL +
    '        HOLIDAY_SNAPSHOT = True' + NL +
    '    updated, calc_date = apply_spot_to_frames(frames, spot, names, now_bj, force_history=HOLIDAY_SNAPSHOT)'
)
if "force_history=HOLIDAY_SNAPSHOT" not in t:
    if old_main not in t:
        print("ANCHOR MISSING: apply_spot_to_frames call")
        sys.exit(2)
    t = t.replace(old_main, new_main)

# 5) bypass the anti-regression guard on a holiday (asof legitimately goes back)
old_g = '    if RPS_JSON.exists():' + NL
new_g = '    if RPS_JSON.exists() and not HOLIDAY_SNAPSHOT:' + NL
if new_g not in t:
    if old_g not in t:
        print("ANCHOR MISSING: RPS_JSON.exists")
        sys.exit(2)
    t = t.replace(old_g, new_g, 1)

# 6) atomic cache write
old_w = '            pd.concat(out, ignore_index=True).to_parquet(KLINE_CACHE, index=False)'
new_w = (
    '            _merged = pd.concat(out, ignore_index=True)' + NL +
    '            _tmp = str(KLINE_CACHE) + ".tmp"' + NL +
    '            _merged.to_parquet(_tmp, index=False)' + NL +
    '            os.replace(_tmp, KLINE_CACHE)   # atomic: never leave a truncated cache'
)
if new_w not in t:
    if old_w not in t:
        print("ANCHOR MISSING: to_parquet(KLINE_CACHE")
        sys.exit(2)
    t = t.replace(old_w, new_w)

open(P, "wb").write(t.encode("utf-8"))
print("patched OK")
print("has helper:", "_is_static_snapshot" in t)
print("has force_history:", "force_history=HOLIDAY_SNAPSHOT" in t)
print("has atomic write:", "os.replace(_tmp, KLINE_CACHE)" in t)
