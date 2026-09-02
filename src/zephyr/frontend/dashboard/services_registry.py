# [BLUEPRINT] MOD-L08-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""服务总闸——启动项注册表（Owner 2026-09-02 裁定：桌面 Dashboard 承担启动编排，本模块=唯一真源）
* 目录：16 个启动项（服务域/数据域/交易域/基础设施/守护域），大白话说明随目录走
* 状态：psutil 进程扫描 + tmp/*.heartbeat 心跳 freshness + 端口探测 + schtasks 计划任务（60s 缓存）
* 四态灯 DS-12：green=正常 / yellow=延迟 / red=断线 / gray=未启动
* 控制：分级开关（free=自由 / confirm=二次确认 / guard=保命禁操作 / external=外部程序禁操作 / self=本页宿主）
* 日志：tmp/services_control_log.jsonl（谁几点开了/关了什么，审计可查）
"""
from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[4]
_TMP = _REPO / "tmp"
_LOG = _TMP / "services_control_log.jsonl"

# ── 服务目录（16 项；desc=大白话功能说明——Owner 口径"写成人话"）──────────────
# tier: free=自由开关 / confirm=二次确认 / guard=保命禁操作 / external=外部程序只读 / self=本页宿主
# detect: heartbeat=<tmp 文件名> / port=<端口号> / proc=<cmdline|name 正则> / task=<schtasks 任务名>
# start: 拉起命令（argv 列表，cwd=仓库根）；stop: how=tree(kill 进程树)/heartbeat(kill guard+child)/port(kill 监听进程)
SERVICE_CATALOG: list[dict[str, Any]] = [
    # ── 服务域（本仓库可自由开关）──
    {"id": "api_server", "group": "services", "tier": "self", "name": "面板 API 服务",
     "desc": "本页的宿主：桌面面板所有数据的总后厨（端口 8890），它活着这页才活着",
     "detect": {"type": "self"}},
    {"id": "panel", "group": "services", "tier": "free", "name": "Panel 治理大屏",
     "desc": "旧版治理大屏（10-Tab 治理+交易+回测，端口 5006）——和新桌面面板并存，用不用随你",
     "detect": {"type": "port", "port": 5006},
     "start": ["python", "-m", "panel", "serve", "src/zephyr/frontend/dashboard/app_panel.py", "--port", "5006"],
     "stop": {"how": "port", "port": 5006}},
    {"id": "docs_serve", "group": "services", "tier": "free", "name": "本地文档服务",
     "desc": "架构文档在线浏览+按需重生成（端口 8765）——浏览器看 docs 的通道",
     "detect": {"type": "port", "port": 8765},
     "start": ["python", "scripts/serve_docs.py"],
     "stop": {"how": "port", "port": 8765}},
    {"id": "llm_dash", "group": "services", "tier": "free", "name": "LLM 安全网关面板",
     "desc": "AI 防护墙的监控面板（提示词注入拦截/安全事件记录）——streamlit 起的网页",
     "detect": {"type": "port", "port": 8501},
     "start": ["python", "-m", "streamlit", "run", "src/zephyr/security/llm_defense/llm_security/dashboard/app.py"],
     "stop": {"how": "port", "port": 8501}},
    {"id": "mcp", "group": "services", "tier": "free", "name": "MCP 服务器簇",
     "desc": "AI 干活的工具箱后台（规则查询/任务管理/网关等 9 件套）——AI 会话依赖它",
     "detect": {"type": "proc", "pattern": r"rule_discovery_server|scripts[\\/]mcp[\\/]launcher"},
     "start": ["python", "scripts/mcp/launcher.py"],
     "stop": {"how": "proc"}},
    {"id": "proto8010", "group": "services", "tier": "free", "name": "原型页静态服务",
     "desc": "docs/_working 原型页的浏览通道（端口 8010，掉线有看门狗 30 秒自愈）",
     "detect": {"type": "port", "port": 8010},
     "start": ["python", "-m", "http.server", "8010", "--directory", "docs/_working"],
     "stop": {"how": "port", "port": 8010}},
    # ── 数据域（关=丢数据，需二次确认）──
    {"id": "scheduler", "group": "data", "tier": "confirm", "name": "数据调度器",
     "desc": "8 个数据源的下载总管：每天自动下 K 线/财务/新闻/板块进数据库（61 个任务）",
     "detect": {"type": "heartbeat", "file": "scheduler.heartbeat"},
     "start": ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/start_scheduler.ps1"],
     "stop": {"how": "heartbeat"}},
    {"id": "tick_sub", "group": "data", "tier": "confirm", "name": "Tick 订阅器",
     "desc": "盘中每 3 秒抓一笔实时行情存库——模拟盘和做T 策略的口粮，盘中关掉会漏数据",
     "detect": {"type": "heartbeat", "file": "tick_subscriber.heartbeat", "biz": "tick_subscriber_biz.heartbeat"},
     "start": ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/start_tick_subscriber.ps1"],
     "stop": {"how": "heartbeat"}},
    {"id": "sector_collector", "group": "data", "tier": "confirm", "name": "板块快照采集器",
     "desc": "盘中每分钟存一张板块涨跌快照进库（板块排名/轮动分析的数据底料）",
     "detect": {"type": "proc", "pattern": r"sector_snapshot_collector"},
     "start": ["python", "-m", "zephyr.data.sector_snapshot_collector"],
     "stop": {"how": "proc"}},
    {"id": "ch_probe", "group": "data", "tier": "guard", "name": "CH 健康探针",
     "desc": "数据库哨兵：每 3 秒探一次 ClickHouse 死活，断连 6 秒就拉警报——保命进程不许关",
     "detect": {"type": "heartbeat", "file": "ch_health_probe.heartbeat"}},
    # ── 交易域 ──
    {"id": "paper_session", "group": "trading", "tier": "confirm", "name": "模拟盘会话",
     "desc": "交易日 09:25~15:05 的模拟盘值守进程（实盘前的彩排场），挂着策略接行情",
     "detect": {"type": "proc", "pattern": r"start_paper_session"},
     "start": ["python", "scripts/start_paper_session.py"],
     "stop": {"how": "proc"}},
    {"id": "qmt", "group": "trading", "tier": "external", "name": "QMT 终端",
     "desc": "券商交易终端：行情+交易+文件桥（持仓/盘口数据的生产者）——无法自动登录，只能你手动启动",
     "detect": {"type": "proc", "pattern": r"xtminiqmt|xiadan|qmt", "name_only": True}},
    {"id": "tdx", "group": "trading", "tier": "external", "name": "通达信客户端",
     "desc": "行情源之一（十源里的老牌选手）——手动启动，这里只看它的死活",
     "detect": {"type": "proc", "pattern": r"^tdx", "name_only": True}},
    # ── 基础设施（外部程序，只读）──
    {"id": "clickhouse", "group": "infra", "tier": "external", "name": "ClickHouse 数据库",
     "desc": "111 亿行行情数据的老窝（Hyper-V 虚拟机里）——所有页面取数的地基，开机自启+180 秒延迟",
     "detect": {"type": "ch"}},
    {"id": "redis", "group": "infra", "tier": "external", "name": "Redis 热缓存",
     "desc": "盘中因子链的口粮仓（和 ClickHouse 同一台虚拟机）——挂了盘中自动降级带病运行，必须有人知道",
     "detect": {"type": "env_tcp", "env": ".env.redis", "host_key": "REDIS_HOST", "port_key": "REDIS_PORT"}},
    {"id": "postgres", "group": "infra", "tier": "external", "name": "PostgreSQL 治理库",
     "desc": "项目地图/依赖图的老家（depgraph 唯一真源）——挂了整个 AI 治理链瞎眼",
     "detect": {"type": "env_tcp", "env": ".env.postgres", "host_key": "POSTGRES_HOST", "port_key": "POSTGRES_PORT"}},
    {"id": "cold_archive", "group": "infra", "tier": "external", "name": "E 盘冷存储",
     "desc": "老分区数据搬进 parquet 的冷备仓（E:\\zephyr_cold_archive，111 亿行的老窝的后悔药）——库炸了靠它重演历史",
     "detect": {"type": "cold_archive", "dir": "E:\\zephyr_cold_archive", "manifest": "archive_manifest.jsonl"}},
    {"id": "code_backup", "group": "infra", "tier": "external", "name": "F 盘代码备份仓",
     "desc": "每日六阶段备份的落盘终点（F:\\code_backup）——任务 Ready 不等于产物在位，这里看真东西",
     "detect": {"type": "daily_fresh", "dir": "F:\\code_backup"}},
    {"id": "rsshub", "group": "infra", "tier": "external", "name": "RSSHub 新闻源",
     "desc": "新闻/舆情抓取的输送管道（pm2 托管）——情绪分析和新闻页的口粮，开机自启",
     "detect": {"type": "port", "port": 1200}},
    # ── 守护域（保命进程，禁操作）──
    {"id": "drift_watchdog", "group": "guard", "tier": "guard", "name": "漂移看门狗",
     "desc": "仓库保安：盯着代码文件有没有被偷偷改动，异常就快照存证+报警——保命进程不许关",
     "detect": {"type": "proc", "pattern": r"worktree_drift_watchdog"}},
    {"id": "deadman", "group": "guard", "tier": "guard", "name": "死人开关",
     "desc": "最后的哨兵：核心服务心跳停超 10 分钟，自动给你飞书发警报（计划任务每 5 分钟查一次）",
     "detect": {"type": "task", "task": "ZephyrAlpha_DeadmanSwitch"}},
    {"id": "reaper", "group": "guard", "tier": "guard", "name": "进程收割者",
     "desc": "开机清道夫：清理项目残留的 python 僵尸进程和幽灵窗口（登录后跑一次就退出）",
     "detect": {"type": "task", "task": "ZephyrAlpha_ProcessReaper"}},
    # ── 二期补充（Owner 2026-09-02「全面盘点补全」）：盘中运行时/文件桥/定时任务族 ──
    {"id": "intraday_main", "group": "trading", "tier": "confirm", "name": "盘中运行时",
     "desc": "tick→Redis→因子→端到端盘中编排（AGENTS 348）——交易日盘中核心，依赖 QMT 先就绪",
     "detect": {"type": "proc", "pattern": r"intraday_main"},
     "start": ["python", "-m", "zephyr.runtime.intraday_main"],
     "stop": {"how": "proc"}},
    {"id": "qmt_bridge", "group": "trading", "tier": "external", "name": "QMT 文件桥",
     "desc": "QMT 自动导出的实盘数据通道（持仓/委托/成交 CSV，10 秒一茬）——QMT 开着它就活着",
     "detect": {"type": "file_fresh", "dir": "E:\\qmt_bridge"}},
    {"id": "qmt_bridge_sim", "group": "trading", "tier": "external", "name": "模拟盘文件桥",
     "desc": "模拟盘 QMT 的数据桥（E:\\qmt_bridge_sim）——模拟盘会话开着它就活着，收盘后停属正常",
     "detect": {"type": "file_fresh", "dir": "E:\\qmt_bridge_sim"}},
    {"id": "write_audit_daemon", "group": "guard", "tier": "guard", "name": "写审计守护",
     "desc": "给每次文件改动记台账的书记员（防「改了没人知道」）——保命进程不许关",
     "detect": {"type": "proc", "pattern": r"write_audit_daemon"}},
    {"id": "post_settlement", "group": "guard", "tier": "guard", "name": "盘后结算",
     "desc": "每天 15:30 自动结算+对账+审计写账（交易日才干活）——计划任务只读监控",
     "detect": {"type": "task", "task": "ZephyrAlpha_PostSettlement"}},
    {"id": "daily_backup", "group": "guard", "tier": "guard", "name": "每日灾备",
     "desc": "每天 06:00 六阶段备份保底（库+配置+代码打包）——备份断了必须有人知道",
     "detect": {"type": "task", "task": "ZephyrAlpha-DailyBackup"}},
    {"id": "weekly_vm_backup", "group": "guard", "tier": "guard", "name": "每周 VM 备份",
     "desc": "每周五 06:00 虚拟机整体快照（ClickHouse 老窝的后悔药）",
     "detect": {"type": "task", "task": "ZephyrAlpha-WeeklyVMBackup"}},
    {"id": "ch_optimize_weekly", "group": "guard", "tier": "guard", "name": "CH 周维护",
     "desc": "每周六 03:30 ClickHouse 合并优化（表碎片整理，保查询速度）",
     "detect": {"type": "task", "task": "ZephyrAlpha-CH-OptimizeMerge-Weekly"}},
    {"id": "ttl_rejudge", "group": "guard", "tier": "guard", "name": "TTL 日重判",
     "desc": "每天 18:05 数据生命周期重判（过期数据自动降级/清理的裁判）",
     "detect": {"type": "task", "task": "ZephyrAlpha_TTLRejudgeDaily"}},
    {"id": "trae_cache", "group": "guard", "tier": "guard", "name": "Trae 缓存清理",
     "desc": "开机清 Trae 编辑器缓存（防缓存膨胀吃满 C 盘）",
     "detect": {"type": "task", "task": "ZephyrAlpha_TraeCacheCleanup"}},
    {"id": "ai_wrapper_inject", "group": "guard", "tier": "guard", "name": "AI 通道防护注入",
     "desc": "每分钟给新 AI 进程打 git 安全补丁（防 AI 误操作 git）——它停了 AI 通道防护裸奔",
     "detect": {"type": "task", "task": "ZephyrAlpha-AI-Wrapper-Inject"}},
]

_GROUP_META = {
    "services": {"title": "服务域", "sub": "面板自己的服务——可自由开关"},
    "data": {"title": "数据域", "sub": "下载与实时行情——关了丢数据，需确认"},
    "trading": {"title": "交易域", "sub": "模拟盘与券商终端"},
    "infra": {"title": "基础设施", "sub": "数据库/新闻源等外部程序——只读"},
    "guard": {"title": "守护域", "sub": "保命进程——不许关"},
}

_TIER_LABEL = {"free": "可自由开关", "confirm": "需二次确认", "guard": "保命·禁操作",
               "external": "外部程序·只读", "self": "本页宿主"}

_SCHTASKS_CACHE: dict[str, tuple[float, str]] = {}   # task_name → (ts, status)
_GPU_CACHE: dict[str, tuple[float, Any]] = {}        # gpu 查询缓存（nvidia-smi 子进程 ~150ms，15s 复用）


# ── 探测原语 ──────────────────────────────────────────────────────────────
def _port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def _port_listener_pid(port: int) -> int | None:
    try:
        import psutil
        for c in psutil.net_connections(kind="tcp"):
            if c.status == psutil.CONN_LISTEN and c.laddr and c.laddr.port == port and c.pid:
                return c.pid
    except Exception:  # noqa: BLE001 — 探测失败按未启动处理
        return None
    return None


def _find_proc(pattern: str, name_only: bool = False) -> Any:
    import psutil
    rx = re.compile(pattern, re.IGNORECASE)
    me = os.getpid()
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if p.info["pid"] == me:
                continue
            hay = (p.info["name"] or "") if name_only else (
                (p.info["name"] or "") + " " + " ".join(p.info["cmdline"] or []))
            if rx.search(hay):
                return p
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None


def _read_heartbeat(fname: str) -> dict[str, Any] | None:
    """心跳格式 <ISO8601>|<guard_pid>|<child_pid>（guard 写，15s 一跳）。"""
    f = _TMP / fname
    if not f.exists():
        return None
    try:
        parts = f.read_text(encoding="utf-8-sig", errors="ignore").strip().lstrip("\ufeff").split("|")
        ts = datetime.fromisoformat(parts[0]).timestamp()
        return {"ts": ts, "guard_pid": int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None,
                "child_pid": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None}
    except Exception:  # noqa: BLE001 — 半行/损坏按无心跳
        return None


# ── 状态采集 ──────────────────────────────────────────────────────────────
def _proc_stats(pid: int | None) -> dict[str, Any]:
    """CPU%（非阻塞增量）+ 内存 MB + 存活判定。首次调用 cpu=0（psutil 语义），10s 轮询第二跳起为真值。"""
    if not pid:
        return {"alive": False, "cpu": None, "mem": None}
    try:
        import psutil
        p = psutil.Process(pid)
        if p.status() == psutil.STATUS_ZOMBIE:
            return {"alive": False, "cpu": None, "mem": None}
        with p.oneshot():
            return {"alive": True, "cpu": round(p.cpu_percent(None), 1), "mem": round(p.memory_info().rss / 1048576, 1)}
    except Exception:  # noqa: BLE001
        return {"alive": False, "cpu": None, "mem": None}


def _kill_tree(pid: int) -> None:
    """先杀子进程再杀本体（taskkill /T /F 等价，psutil 实现）。"""
    import psutil
    try:
        parent = psutil.Process(pid)
        for c in parent.children(recursive=True):
            try:
                c.kill()
            except psutil.Error:
                pass
        parent.kill()
    except psutil.Error:
        pass


def _do_stop(item: dict[str, Any]) -> str:
    how = (item.get("stop") or {}).get("how")
    if how == "port":
        pid = _port_listener_pid(item["stop"]["port"])
        if pid:
            _kill_tree(pid)
            return f"killed listener pid={pid}"
        return "no listener"
    if how == "heartbeat":
        hb = _read_heartbeat(item["detect"]["file"])
        killed = []
        if hb:
            for pid in (hb.get("guard_pid"), hb.get("child_pid")):   # 先杀 guard 防复活，再杀 child
                if pid and _proc_stats(pid)["alive"]:
                    _kill_tree(pid)
                    killed.append(str(pid))
        if not killed:
            return "no alive pid in heartbeat"
        return "killed pids=" + ",".join(killed)
    if how == "proc":
        p = _find_proc(item["detect"]["pattern"], item["detect"].get("name_only", False))
        if p:
            _kill_tree(p.pid)
            return f"killed pid={p.pid}"
        return "not found"
    return "unsupported"


def _do_start(item: dict[str, Any]) -> str:
    cmd = item.get("start")
    if not cmd:
        return "no start command"
    log = (_TMP / f"svc_{item['id']}.log").open("ab")
    exe = cmd[0]
    if exe == "python":   # 用 api_server 同一解释器，防 PATH 漂移
        import sys
        cmd = [sys.executable, *cmd[1:]]
    subprocess.Popen(cmd, cwd=str(_REPO), stdout=log, stderr=log,
                     creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)  # noqa: S603 — 命令=目录内白名单
    return "spawned: " + " ".join(cmd[:4])


def _ch_alive() -> tuple[bool, str]:
    """ClickHouse 探活：复用 ch_config 真源（#ARCH-CH-017 禁默认 IP），TCP 探 http_port。"""
    try:
        sys.path.insert(0, str(_REPO / "src"))
        from zephyr.data.ch_config import load_ch_config

        cfg = load_ch_config()
        port = int(cfg.get("http_port") or cfg.get("port") or 8123)
        host = cfg["host"]
        with socket.create_connection((host, port), timeout=1.5):
            return True, f"{host}:{port} 可达"
    except Exception as e:  # noqa: BLE001 — 探活失败=断线
        return False, str(e)[:80]


def _task_info(task: str) -> dict[str, str] | None:
    """schtasks 信息（Ready/Running/Disabled + 下次触发）——60s 缓存防拖慢轮询。
    CSV /nh 实测 3 列：TaskName,NextRunTime,Status（无 /v 无 HostName；重复注册的任务
    会输出多行——deadman 实证两行，取首行）。"""
    now = time.time()
    hit = _SCHTASKS_CACHE.get(task)
    if hit and now - hit[0] < 60:
        return hit[1] or None
    info: dict[str, str] | None = None
    reason = ""
    try:
        r = subprocess.run(["schtasks", "/query", "/tn", task, "/fo", "CSV", "/nh"],
                           capture_output=True, text=True, timeout=5)
        # 防御：无 console 的 Hidden 进程里实测 r.stdout 可能为 None（Owner 环境实证），必须 or ""
        out = (r.stdout or "").strip()
        first = out.splitlines()[0] if r.returncode == 0 and out else ""
        parts = [p.strip().strip('"') for p in first.split(",")]
        if len(parts) >= 3:
            info = {"next_run": parts[1], "status": parts[2]}
        else:
            reason = f"rc={r.returncode} out={(r.stdout or '')[:60]!r} err={(r.stderr or '')[:60]!r}"
    except Exception as e:  # noqa: BLE001
        info = None
        reason = str(e)[:100]
    _SCHTASKS_CACHE[task] = (now, info or {"error": reason})
    return info


def _file_fresh(dirpath: str) -> tuple[str, str]:
    """目录最新文件 mtime 新鲜度（QMT 文件桥用）→ (light, detail)。"""
    try:
        latest = 0.0
        n = 0
        for p in Path(dirpath).rglob("*"):
            if p.is_file():
                n += 1
                m = p.stat().st_mtime
                if m > latest:
                    latest = m
        if not n:
            return "gray", "桥目录为空（等 QMT 开启导出）"
        age = time.time() - latest
        if age < 300:
            return "green", f"桥活着：{n} 个文件，最新 {round(age)}s 前"
        if age < 1800:
            return "yellow", f"桥延迟：最新一茬 {round(age/60)} 分钟前"
        return "gray", f"桥停摆：最新一茬 {round(age/3600)} 小时前（QMT 没开？）"
    except Exception as e:  # noqa: BLE001 — 目录不可达
        return "gray", "桥目录不可达：" + str(e)[:60]


_COLD_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}   # 冷备统计缓存（rglob 2000+ 文件 ~数百 ms，5min 复用）


def _cold_archive(dirpath: str, manifest_name: str) -> tuple[str, str]:
    """冷备仓探测 → (light, detail)。在位=green；manifest/目录丢失=red（灾备事故）。
    归档节奏未知（可能分区满才触发），归档停滞天数只如实展示不判灯。"""
    now = time.time()
    hit = _COLD_CACHE.get(dirpath)
    if hit and now - hit[0] < 300:
        return hit[1]["light"], hit[1]["detail"]
    result: dict[str, Any]
    try:
        manifest = Path(dirpath) / manifest_name
        if not manifest.exists():
            result = {"light": "red", "detail": "归档清单丢失（灾备事故）：" + manifest_name}
        else:
            last_archived = ""
            with manifest.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            last_archived = json.loads(line).get("archived_at") or last_archived
                        except json.JSONDecodeError:
                            continue
            s = 0
            n = 0
            for p in Path(dirpath).rglob("*"):
                if p.is_file():
                    n += 1
                    s += p.stat().st_size
            days = ""
            if last_archived:
                age_d = round((now - datetime.fromisoformat(last_archived).timestamp()) / 86400)
                days = f" · 最新归档 {age_d} 天前"
            result = {"light": "green",
                      "detail": f"在位 {n} 个文件 / {s/1073741824:.1f} GB{days}"}
    except Exception as e:  # noqa: BLE001 — 冷备不可达=事故
        result = {"light": "red", "detail": "冷备不可达：" + str(e)[:60]}
    _COLD_CACHE[dirpath] = (now, result)
    return result["light"], result["detail"]


def _daily_fresh(dirpath: str) -> tuple[str, str]:
    """日频备份产物目录探测 → (light, detail)。<36h 绿（每日 06:00 允许一天）/ <8d 黄 / 更久红。"""
    try:
        if not Path(dirpath).exists():
            return "red", "备份产物目录不存在（灾备事故）"
        latest = 0.0
        n = 0
        for root, _dirs, files in os.walk(dirpath):   # os.walk 默认跳过无权限子目录（F 盘 ACL 文件实证），不整体炸
            for f in files:
                try:
                    m = (Path(root) / f).stat().st_mtime
                    n += 1
                    if m > latest:
                        latest = m
                except OSError:
                    continue
        if not n:
            return "red", "备份产物目录为空（灾备事故）"
        age_h = (time.time() - latest) / 3600
        when = datetime.fromtimestamp(latest).strftime("%m-%d %H:%M")
        detail = f"{n} 个文件 · 最新 {when}（{round(age_h)} 小时前）"
        if age_h < 36:
            return "green", detail
        if age_h < 8 * 24:
            return "yellow", detail + "——超 1 天没备份了"
        return "red", detail + "——超 1 周没备份（灾备事故）"
    except Exception as e:  # noqa: BLE001 — 不可达=事故
        return "red", "备份仓不可达：" + str(e)[:60]


def _env_tcp_alive(env_file: str, host_key: str, port_key: str) -> tuple[bool, str]:
    """通用 .env 真源 TCP 探活（#ARCH-CH-017 同源精神：读配置禁硬编码 IP）。"""
    try:
        cfg: dict[str, str] = {}
        for line in (_REPO / "config" / env_file).read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
        host, port = cfg[host_key], int(cfg[port_key])
        with socket.create_connection((host, port), timeout=1.5):
            return True, f"{host}:{port} 可达"
    except Exception as e:  # noqa: BLE001 — 探活失败=断线
        return False, str(e)[:80]


def _gpu_stats() -> dict[str, Any] | None:
    """GPU 水位（nvidia-smi，多卡聚合 util 取最大、显存求和）——无卡/无驱动返回 None（前端隐藏该杆）。"""
    hit = _GPU_CACHE.get("stats")
    if hit and time.time() - hit[0] < 15:
        return hit[1]
    stats: dict[str, Any] | None = None
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=4)
        if r.returncode == 0 and r.stdout.strip():
            utils, used, total = [], 0.0, 0.0
            for line in r.stdout.strip().splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) == 3:
                    utils.append(float(parts[0]))
                    used += float(parts[1])
                    total += float(parts[2])
            if total > 0:
                stats = {"util": round(max(utils), 1), "mem_used_gb": round(used / 1024, 1),
                         "mem_total_gb": round(total / 1024, 1),
                         "mem_pct": round(used / total * 100, 1), "gpus": len(utils)}
    except Exception:  # noqa: BLE001 — 无 nvidia-smi/超时=无 GPU 杆
        stats = None
    _GPU_CACHE["stats"] = (time.time(), stats)
    return stats


def get_services_status() -> dict[str, Any]:
    """全量状态（GET /api/services-status 真源）。light: green/yellow/red/gray（DS-12）。"""
    try:
        import psutil
    except ImportError:
        psutil = None  # noqa: F841 — 状态降级为端口/心跳探测
    out: list[dict[str, Any]] = []
    for item in SERVICE_CATALOG:
        det = item["detect"]
        st: dict[str, Any] = {"id": item["id"], "name": item["name"], "group": item["group"],
                              "tier": item["tier"], "tier_label": _TIER_LABEL[item["tier"]],
                              "desc": item["desc"], "light": "gray", "cpu": None, "mem": None,
                              "pid": None, "beat_age": None, "detail": ""}
        if det["type"] == "self":
            s = _proc_stats(os.getpid())
            st.update(light="green", pid=os.getpid(), cpu=s["cpu"], mem=s["mem"], detail="本服务运行中")
        elif det["type"] == "port":
            if _port_open(det["port"]):
                pid = _port_listener_pid(det["port"])
                s = _proc_stats(pid)
                st.update(light="green", pid=pid, cpu=s["cpu"], mem=s["mem"], detail=f"端口 {det['port']} 在听")
            else:
                st["detail"] = f"端口 {det['port']} 无监听"
        elif det["type"] == "heartbeat":
            hb = _read_heartbeat(det["file"])
            if hb:
                age = time.time() - hb["ts"]
                st["beat_age"] = round(age)
                child = _proc_stats(hb.get("child_pid"))
                st.update(pid=hb.get("child_pid"), cpu=child["cpu"], mem=child["mem"])
                if age < 120 and child["alive"]:
                    st["light"] = "green"; st["detail"] = f"心跳 {round(age)}s 前"
                elif age < 600:
                    st["light"] = "yellow"; st["detail"] = f"心跳延迟 {round(age)}s"
                else:
                    st["light"] = "red"; st["detail"] = f"心跳停 {round(age/60)} 分钟"
            else:
                st["detail"] = "无心跳文件"
        elif det["type"] == "proc":
            p = _find_proc(det["pattern"], det.get("name_only", False))
            if p:
                s = _proc_stats(p.pid)
                st.update(light="green", pid=p.pid, cpu=s["cpu"], mem=s["mem"], detail=f"pid={p.pid} 运行中")
            else:
                st["detail"] = "进程不在"
        elif det["type"] == "task":
            info = _task_info(det["task"])
            if info and info.get("error"):
                st["light"] = "yellow"
                st["detail"] = "计划任务查询失败：" + info["error"]
            elif info:
                status = info["status"]
                if status == "Disabled":
                    st["light"] = "red"
                    st["detail"] = f"计划任务已停用（启用=Owner 窗口）"
                elif status in ("Ready", "Running"):
                    st["light"] = "green"
                    nxt = info["next_run"]
                    st["detail"] = f"{status}" + (f" · 下次 {nxt}" if nxt and nxt != "N/A" else "")
                else:
                    st["light"] = "yellow"
                    st["detail"] = f"计划任务 {status}"
            else:
                st["light"] = "yellow"; st["detail"] = "计划任务查询失败"
        elif det["type"] == "file_fresh":
            light, msg = _file_fresh(det["dir"])
            st["light"] = light
            st["detail"] = msg
        elif det["type"] == "env_tcp":
            alive, msg = _env_tcp_alive(det["env"], det["host_key"], det["port_key"])
            if alive:
                st["light"] = "green"; st["detail"] = msg
            else:
                st["light"] = "red"; st["detail"] = "断连：" + msg
        elif det["type"] == "cold_archive":
            light, msg = _cold_archive(det["dir"], det["manifest"])
            st["light"] = light
            st["detail"] = msg
        elif det["type"] == "daily_fresh":
            light, msg = _daily_fresh(det["dir"])
            st["light"] = light
            st["detail"] = msg
        elif det["type"] == "ch":
            alive, msg = _ch_alive()
            if alive:
                st["light"] = "green"; st["detail"] = msg
            else:
                st["light"] = "red"; st["detail"] = "数据库断连：" + msg
        # 缺省灯语义：external 灰=未启动（等 Owner，正常）；可控制灰=未启动；guard 灰=异常（该活着）
        if st["light"] == "gray" and item["tier"] == "guard":
            st["light"] = "red"
            st["detail"] = st["detail"] or "守护掉线"
        out.append(st)

    counts = {"green": 0, "yellow": 0, "red": 0, "gray": 0}
    for s in out:
        counts[s["light"]] += 1
    overall = "green" if counts["red"] == 0 else ("yellow" if counts["yellow"] else "red")

    host: dict[str, Any] = {}
    try:
        import psutil
        host = {"cpu": round(psutil.cpu_percent(None), 1),
                "mem": round(psutil.virtual_memory().percent, 1),
                "mem_used_gb": round(psutil.virtual_memory().used / 1073741824, 1),
                "mem_total_gb": round(psutil.virtual_memory().total / 1073741824, 1)}
        du = psutil.disk_usage("D:\\")
        host["disk"] = round(du.percent, 1)
        host["disk_free_gb"] = round(du.free / 1073741824, 1)
        disks = []
        for label, root in (("C", "C:\\"), ("D", "D:\\"), ("E", "E:\\"), ("F", "F:\\")):
            try:
                d2 = psutil.disk_usage(root)
                disks.append({"label": label + " 盘", "pct": round(d2.percent, 1),
                              "free_gb": round(d2.free / 1073741824, 1)})
            except Exception:  # noqa: BLE001 — 盘不在则跳过
                continue
        host["disks"] = disks
        gpu = _gpu_stats()
        if gpu:
            host["gpu"] = gpu
    except Exception:  # noqa: BLE001
        pass

    return {"ok": True, "services": out, "groups": _GROUP_META, "counts": counts,
            "overall": overall, "host": host, "generated_at": datetime.now().isoformat(" ", "seconds")}


def control_service(sid: str, action: str, confirm: bool = False) -> dict[str, Any]:
    """启停控制（POST /api/services-control）。分级闸门+审计落盘。"""
    item = next((x for x in SERVICE_CATALOG if x["id"] == sid), None)
    if not item:
        return {"ok": False, "error": f"unknown service: {sid}"}
    tier = item["tier"]
    if tier in ("guard", "external", "self"):
        return {"ok": False, "error": f"「{item['name']}」是{_TIER_LABEL[tier]}，不允许在此{'停止' if action == 'stop' else '操作'}"}
    if action == "stop" and tier == "confirm" and not confirm:
        return {"ok": False, "need_confirm": True,
                "error": f"「{item['name']}」{item['desc'][:40]}…——关掉有代价，请确认"}
    if action == "start" and tier == "confirm" and not confirm:
        return {"ok": False, "need_confirm": True, "error": f"确认启动「{item['name']}」？"}
    try:
        msg = _do_stop(item) if action == "stop" else _do_start(item)
        result = {"ok": True, "id": sid, "action": action, "msg": msg}
    except Exception as e:  # noqa: BLE001 — 控制失败必须回显
        result = {"ok": False, "id": sid, "action": action, "error": str(e)}
    try:
        with _LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": datetime.now().isoformat(" ", "seconds"),
                                "id": sid, "name": item["name"], "action": action,
                                "ok": result["ok"], "msg": result.get("msg") or result.get("error", "")},
                               ensure_ascii=False) + "\n")
    except OSError:
        pass
    return result


def get_control_log(tail: int = 8) -> list[dict[str, Any]]:
    if not _LOG.exists():
        return []
    try:
        lines = _LOG.read_text(encoding="utf-8").strip().splitlines()
        return [json.loads(x) for x in lines[-tail:] if x]
    except Exception:  # noqa: BLE001
        return []
