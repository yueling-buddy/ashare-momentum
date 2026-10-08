#!/usr/bin/env python3
"""Local intraday refresh + push loop for the A-share dashboard.

Why this exists:
  GitHub Actions `schedule` events are best-effort and drop runs randomly
  (observed: only 1 of ~8 intraday slots fired on 2026-09-30). cron-job.org
  as an external trigger is also unreliable and its PAT expires 2026-10-29.
  This script runs locally (user keeps WorkBuddy open during trading hours)
  and pushes fresh data every 15 minutes, so the public site stays current.

What it does each tick (only inside A-share trading sessions, Mon-Fri):
  1. fetch + reset --hard origin/main   (clean align, no merge conflicts)
  2. refresh.py --mode intraday         (rewrite data/*.json from live quotes)
  3. git add <tracked files> + commit + push (skip if no data change)
  4. on push conflict, retry once (fetch/reset/refresh/push)

Usage:
  python intraday_refresh_loop.py            # infinite loop, 15-min interval
  python intraday_refresh_loop.py --once     # single tick (for testing)
"""
import os
import sys
import subprocess
import json
import time
import datetime
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
GIT = Path(r"C:/Users/yueling.liu/.workbuddy/binaries/PortableGit/versions/1.2.0/cmd/git.exe")
SSH = Path(r"C:/Users/yueling.liu/.workbuddy/binaries/PortableGit/versions/1.2.0/usr/bin/ssh.exe")
KEY = ROOT.parent / ".workbuddy" / "github_a_share_deploy_key"
PY = Path(r"C:/Users/yueling.liu/.workbuddy/binaries/python/envs/refresh_ashare/Scripts/python.exe")
REFRESH = ROOT / "scripts" / "refresh.py"
LOG = ROOT / "scripts" / "intraday_loop.log"
BJ = ZoneInfo("Asia/Shanghai")
FILES = [
    "index.html", "data/rps.json", "data/history.json", "data/fip.json",
    "data/meta.json", "data/sector_rps.json", "data/sector_rps_history.json",
    "data/cloud_run_log.json",
]


def log(msg):
    ts = datetime.datetime.now(BJ).strftime("%Y-%m-%d %H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def in_session():
    now = datetime.datetime.now(BJ)
    if now.weekday() >= 5:
        return False
    t = now.time()
    return ((datetime.time(9, 30) <= t <= datetime.time(11, 30)) or
            (datetime.time(13, 0) <= t <= datetime.time(15, 0)))


def resolve_ssh_ip():
    for u in ("https://dns.google/resolve?name=ssh.github.com&type=A",
              "https://cloudflare-dns.com/dns-query?name=ssh.github.com&type=A&ct=application/dns-json"):
        try:
            with urllib.request.urlopen(u, timeout=8) as r:
                d = json.load(r)
            for a in d.get("Answer", []):
                if a.get("type") == 1:
                    return a["data"]
        except Exception:
            pass
    return None


def ssh_env():
    ip = resolve_ssh_ip()
    cmd = '"%s" -i "%s" -p 443' % (SSH, KEY)
    if ip:
        cmd += " -o HostName=%s" % ip
    cmd += " -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
    e = os.environ.copy()
    e["GIT_SSH_COMMAND"] = cmd
    e["PYTHONIOENCODING"] = "utf-8"
    return e


def run_once():
    env = ssh_env()
    subprocess.run([str(GIT), "fetch", "origin", "main"], cwd=str(ROOT), env=env, check=False)
    subprocess.run([str(GIT), "reset", "--hard", "origin/main"], cwd=str(ROOT), env=env, check=False)
    r = subprocess.run([str(PY), str(REFRESH), "--mode", "intraday"],
                       cwd=str(ROOT), env={**env, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        log("refresh FAILED rc=%d" % r.returncode)
        return
    subprocess.run([str(GIT), "add", *FILES], cwd=str(ROOT), env=env, check=False)
    d = subprocess.run([str(GIT), "diff", "--cached", "--quiet"], cwd=str(ROOT), env=env)
    if d.returncode == 0:
        log("no data change, skip push")
        return
    now = datetime.datetime.now(BJ)
    msg = "auto: intraday refresh %s [local-loop]" % now.strftime("%Y-%m-%d_%H:%M")
    subprocess.run([str(GIT), "commit", "-q", "-m", msg], cwd=str(ROOT), env=env, check=False)
    pr = subprocess.run([str(GIT), "push", "origin", "main"], cwd=str(ROOT), env=env)
    if pr.returncode != 0:
        log("push failed, retry once")
        subprocess.run([str(GIT), "fetch", "origin", "main"], cwd=str(ROOT), env=env, check=False)
        subprocess.run([str(GIT), "reset", "--hard", "origin/main"], cwd=str(ROOT), env=env, check=False)
        r2 = subprocess.run([str(PY), str(REFRESH), "--mode", "intraday"],
                            cwd=str(ROOT), env={**env, "PYTHONIOENCODING": "utf-8"})
        if r2.returncode == 0:
            subprocess.run([str(GIT), "add", *FILES], cwd=str(ROOT), env=env, check=False)
            subprocess.run([str(GIT), "commit", "-q", "-m", msg + " retry"], cwd=str(ROOT), env=env, check=False)
            subprocess.run([str(GIT), "push", "origin", "main"], cwd=str(ROOT), env=env, check=False)
    log("push done")


def main_loop():
    log("loop started (interval 900s)")
    while True:
        try:
            if in_session():
                log("session active -> refresh")
                run_once()
            else:
                log("outside session, skip")
        except Exception as e:
            log("EXCEPTION %r" % (e,))
        time.sleep(900)


if __name__ == "__main__":
    if "--once" in sys.argv:
        run_once()
    else:
        main_loop()
