# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §3.1
# [MODULE] scripts.backup.backup_reconciler
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcilerSpec, ReconcileResult); scripts.governance.meta.backup_runtime_state (_is_pid_alive — 复用存活判据，勿另起炉灶)
# [CONSUMERS] GitCommitGateway._reconciliation_registry.register
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-08:post-commit reconciler触发非时间触发 | INV-09:双条件触发(重要文件+8h间隔) | INV-10:状态持久化backup_state.json | INV-11:ok状态写入前须过system.backup_log当窗BACKUP_CREATED交叉核验,假绿降级ch_log_missing并连带摘除last_ch_backup_status的ok,cadence-skip单独记账;P-7改点火-托管分离后此核验延后由"下一次事件触发"的settle_previous_ignition(读上一轮脱离日志锚定State saved:主仓state)或日检执行,点火轮本身绝不断言ok | INV-12:gate裁决写入锚定主仓state真源(脱离日志State saved:通道),lock-skip短退出不推进计时不降级真实状态,skipped分因(cadence合法/其余degraded);P-7新增点火前主动锁自查(读.runtime/backup.lock PID:+_is_pid_alive),活则直接记lock_skipped不起子进程 | INV-13(P-7非托管免疫):post-commit通道只点火不托管,backup.ps1经瞬时powershell(Start-Process -WindowStyle Hidden+落盘重定向)脱离启动,使备份进程在收割器扫描时不是worker的活的后代(psutil.children(recursive)沿活PPID链)从而免疫级联收割,不再同步subprocess.run托管长跑
# [MODIFY-GUARD] gate_id="BACKUP-RECONCILER"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile异常降级为warn ReconcileResult，不阻断其他reconciler
# [TESTS] tests/scripts/backup/test_backup_reconciler.py
# [A_module] module_id=MOD-INF-043 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""backup_reconciler.py — 灾备备份系统事件触发器（post-commit reconciler）

职责：注册为 ReconciliationRegistry 的 reconciler，post-commit 自动触发。
触发条件（双条件，同时满足）：
  1. committed_files 中存在重要文件（src/config/docs/scripts/tests/data/databases等）
  2. 距上次成功备份 ≥ 8小时（状态持久化到 backup_state.json）

满足条件后调用 PowerShell backup.ps1 执行六阶段备份流水线。

设计：
  - 事件驱动：post-commit reconciler（非 time.sleep/while True 轮询，满足PERM-TRIGGER gate）
  - 间隔保护：8小时最小间隔，避免频繁备份
  - 状态持久化：backup_state.json 记录上次备份时间/快照ID/状态
  - 容错：备份失败降级为 warn ReconcileResult，不阻断其他reconciler
  - 假绿闸（INV-11，2026-09-24）：exit=0 的 ok 落账前，以持久真源
    system.backup_log（BACKUP_CREATED 行）交叉核验 CH 段自报的 ok；核验不过
    （当窗零行/探针故障/ps1 尺寸自检 false）则降级 last_backup_status=
    ch_log_missing 并连带摘除 last_ch_backup_status 的 ok（下游 db_dumps 轮转闸
    消费该字段，宁停转勿假绿）。
    state 真源锚定（P0-1）：gate 裁决写经 stdout "State saved:" 通道解析出的
    主仓 state 文件——reconciler 在序列器 worktree 进程里跑时 PROJECT_ROOT 指
    worktree，其本地 state 副本无消费者。
    lock-skip 甄别（P1-3）：ps1 撞锁短退出只记 last_run_outcome=lock_skipped，
    不推进 8h 计时、不降级在飞备份的真实状态。
    skipped 分因（P1-7）：仅 "24h cadence" 前缀属合法 ok_ch_skipped；其余
    （service down/config missing）记 ok_ch_degraded。
    CH 段 24h cadence 跳过与"确实备份过"（backed_up）分开记账；trigger 的 8h
    节奏跳过同样单独记 last_cadence_skip_*，skip 不得被误读成备份健康。
    （2026-09-22 实证：state 记 verified=true 而 backup_log 当窗零行）

P-7 点火/托管分离（2026-09-26 灾备断链治本）：post-commit 通道此前用
``subprocess.run(backup.ps1, capture_output=True, timeout=14400)`` 同步托管整条
流水线，而承载它的 reconcile_worker 以 expected_lifetime_s=1800 登记孵化——流水线
实测 0.4~9.1 小时 ≫ 载体 0.5 小时寿限，收割器按活 PPID 链级联处决（
``_KILL_CHILD_RECURSIVE``→``psutil.children(recursive)``）会连坐它托管的备份，
留下"无报告/无 state/锁文件占盘"的死链（09-25/09-23 实证）。本车道改的是**进程
托管关系**（非任何阈值）：
  1. 点火前主动锁自查：读 ``.runtime/backup.lock``（ps1 写 ``PID:<n> START:<iso>``，
     非 JSON 故自备 PID 正则）+ 复用 ``backup_runtime_state._is_pid_alive`` 判存活，
     持锁者活则直接记 lock_skipped 返回、不起任何子进程（INV-12 前移）。
  2. 需真跑时经"瞬时 powershell + Start-Process -WindowStyle Hidden + 落盘重定向"
     完全脱离地启动 backup.ps1——powershell 装载器立即退出，真备份的 PPID 指向已
     亡装载器而非 worker，收割器扫描时它不在 worker 的活后代树里，从而免疫级联收割；
     worker 可在 30 分钟寿限内正常退出不带走备份。
  3. 原靠 stdout 的三条语义（State saved:/Another backup is running/Report saved:）
     改从落盘脱离日志解析（读取端一律 utf-8-sig 去 BOM）。
  4. 点火轮不再同步断言 ok/failed（避免假绿），只在 state 记"已点火待验"标记
     （last_backup_launch_time/last_ignite_log/last_run_outcome=ignited_pending_verification）；
     cadence 锚 last_backup_time 由 backup.ps1 STAGE 4 自写（已只读核实 line 923
     ``Add-Member -NotePropertyName last_backup_time`` 为真），真验核延后由下一次事件
     触发的 settle_previous_ignition（读上一轮脱离日志→report→backup_log 交叉核验，
     锚定 State saved: 主仓 state 落权威裁决，逻辑沿用 INV-11）或日检按 26h 窗核对。
     残留窗口：ps1 自报的乐观 last_backup_status 在被交叉核验前的短暂未证窗——由高频
     post-commit 快速收敛，非本车道新增定时任务（宪法 §9.3 禁 cron/Timer/sleep-loop）。

公共 API（无下划线前缀）为真源实现；带下划线前缀的私有名（_load_config /
_get_state_file / _load_state / _update_state / _trigger / _reconcile 等）保留为
向后兼容的薄包装，委托给同名公共函数，便于历史调用方平滑过渡。

Usage::

    from zephyr.governance.audit.reconciliation_registry import ReconciliationRegistry
    from backup_reconciler import make_backup_reconciler

    registry = ReconciliationRegistry()
    registry.register(make_backup_reconciler(project_root))
"""

from __future__ import annotations

import importlib.util
import json
import logging
import os
import re
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

__all__ = ["make_backup_reconciler"]

# ── 配置常量（从backup_config.yaml加载，此处为默认值兜底）──
# 公共名为真源；PROJECT_ROOT 与 CONFIG_FILE / STATE_FILE 同为模块级路径常量。
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # D:\ZephyrAlpha
CONFIG_FILE = PROJECT_ROOT / "scripts" / "backup" / "backup_config.yaml"
STATE_FILE = PROJECT_ROOT / "data" / "databases" / "backup_state.json"

# 重要文件路径前缀（触发条件1）
IMPORTANT_PREFIXES: tuple[str, ...] = (
    "src/",
    "config/",
    "docs/",
    "scripts/",
    "tests/",
    "architecture_model/",
    "data/databases/",
    "data/raw/bdpan/",
    "data/vector_db/",
)

# 重要根文件（触发条件1）
IMPORTANT_FILES: frozenset[str] = frozenset(
    {
        "AGENTS.md",
        "pyproject.toml",
        "docker-compose.yml",
    }
)

# 最小间隔秒数（触发条件2，默认8小时）
MIN_INTERVAL_SECONDS = 8 * 3600

# CH HTTP 端点配置真源（与 backup.ps1 同读 config/.env.clickhouse）
CH_ENV_FILE = PROJECT_ROOT / "config" / ".env.clickhouse"
# backup_log 交叉核验回看窗缓冲：system.backup_log 有 flush 延迟，且宿主机与
# CH VM 时钟允许小偏移；真实备份从点火到 BACKUP_CREATED 落行远大于此缓冲。
CH_LOG_WINDOW_BUFFER_SECONDS = 300

# ── P-7 点火/托管分离常量（2026-09-26）─────────────────────────────────────
# 只改进程托管关系，不碰任何 cadence/retention/timeout 数值语义。
IGNITE_LOG_PREFIX = "backup_reconciler_ignite_"
# 点火装载器（瞬时 powershell）的等待上限：Start-Process 立即返回，这只是等装载
# 器退出的兜底秒数，**与被托管备份的时长无关**（不再同步等待数小时的流水线）。
IGNITE_SPAWN_TIMEOUT_S = 60
# ps1 锁内容格式 "PID:<n> START:<iso>"（非 JSON，故自备 PID 正则，与 backup.ps1
# Test-BackupLock 的 'PID:(\d+)' 判据保持一致）。
_RE_LOCK_PID = re.compile(r"PID:(\d+)")
_RE_STATE_SAVED = re.compile(r"State saved:\s*(\S+)")
_LOCK_SKIP_MARKER = "Another backup is running"

# §5.160.2 SQL 集中化：CH system.backup_log 假绿交叉核验查询（唯一消费点=query_backup_log_created）。
# 列名以 CH 26.6 实测 schema 为准：判别列是 status Enum8，无 event_type 列。
_SQL_BACKUP_LOG_CREATED_PROBE = (
    "SELECT count(), max(event_time) FROM system.backup_log "
    "WHERE status = 'BACKUP_CREATED' AND event_time >= toDateTime('{literal}', 'UTC') "
    "FORMAT TSV"
)

# ── 向后兼容别名（公共名为真源；私有名为静态快照/薄包装，仅供历史调用方过渡）──
# 注意：PROJECT_ROOT / CONFIG_FILE / STATE_FILE 可被 make_backup_reconciler 重新赋值，
# 这些私有别名仅反映导入时的快照，不应在新代码中依赖。
_project_root = PROJECT_ROOT
_CONFIG_FILE = CONFIG_FILE
_STATE_FILE = STATE_FILE
_IMPORTANT_PREFIXES = IMPORTANT_PREFIXES
_IMPORTANT_FILES = IMPORTANT_FILES
_MIN_INTERVAL_SECONDS = MIN_INTERVAL_SECONDS


def load_config() -> dict[str, Any]:
    """加载backup_config.yaml配置"""
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.warning("backup_config.yaml not found, using defaults")
        return {}


def _load_config() -> dict[str, Any]:
    """向后兼容包装：委托给 load_config()。"""
    return load_config()


def rel_path(file_path: str | Path) -> str:
    """将绝对路径转为相对项目根的相对路径（正斜杠）"""
    try:
        rel = os.path.relpath(str(file_path), str(PROJECT_ROOT)).replace("\\", "/")
        return rel
    except ValueError:
        return str(file_path)


def _rel_path(file_path: str | Path) -> str:
    """向后兼容包装：委托给 rel_path()。"""
    return rel_path(file_path)


def get_state_file() -> Path:
    """获取状态文件路径（从 backup_config.yaml §trigger.state_file 读取，fallback 到 STATE_FILE）。

    F-06 Track A 治本：state_file 真源从硬编码 STATE_FILE 迁移到 YAML trigger.state_file，
    硬编码常量仅作 YAML 缺失时的 fallback。
    """
    config = load_config()
    trigger_cfg = config.get("trigger", {}) if config else {}
    state_file_rel = trigger_cfg.get("state_file")
    if state_file_rel:
        return PROJECT_ROOT / state_file_rel
    return STATE_FILE


def _get_state_file() -> Path:
    """向后兼容包装：委托给 get_state_file()。"""
    return get_state_file()


def load_state_from(state_file: Path) -> dict[str, Any]:
    """加载指定状态文件；损坏时告警并按空处理（8h 闸 fail-open 是既定语义）。"""
    try:
        with open(state_file, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        logger.warning("backup state file corrupt, treating as empty: %s (%s)", state_file, exc)
        return {}


def load_state() -> dict[str, Any]:
    """加载备份状态文件（INV-10）"""
    return load_state_from(get_state_file())


def _load_state() -> dict[str, Any]:
    """向后兼容包装：委托给 load_state()。"""
    return load_state()


def update_state_at(state_file: Path | None, **kwargs: Any) -> None:
    """更新指定状态文件；None=默认 get_state_file()（INV-10）。

    2026-09-24（P0-1 分家治理）：gate 的裁决写入必须锚定主仓真源——reconciler
    可能在序列器 worktree 进程里跑（PROJECT_ROOT=worktree 根，其 state 文件无
    任何下游消费者），路径由调用方经 backup.ps1 stdout 的 "State saved:" 通道
    解析后显式传入。写入走 safe_write_text 原子写（P1-8 半修：python 侧不再裸写）。
    """
    target = Path(state_file) if state_file else get_state_file()
    state = load_state_from(target)
    state.update(kwargs)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state, ensure_ascii=False, indent=2)
    try:
        from zephyr.shared.io.file_utils import safe_write_text
    except ImportError:
        safe_write_text = None  # type: ignore[assignment]
    if safe_write_text is not None:
        try:
            safe_write_text(target, payload, expected_base_sha256=None, newline="\n")
            return
        except (OSError, ValueError, TypeError) as exc:
            logger.warning("backup state CAS write failed (%s), falling back to plain write", exc)
    with open(target, "w", encoding="utf-8") as f:
        f.write(payload)


def update_state(**kwargs: Any) -> None:
    """更新备份状态文件（INV-10）"""
    update_state_at(None, **kwargs)


def _update_state(**kwargs: Any) -> None:
    """向后兼容包装：委托给 update_state()。"""
    return update_state(**kwargs)


def read_ch_http_endpoint() -> tuple[str, int, bool]:
    """读取 CH HTTP 端点（config/.env.clickhouse，与 backup.ps1 同一真源）。

    返回 (host, port, env_found)。2026-09-24（P1-9）：不再静默兜底 localhost——
    worktree 进程缺 env 文件时兜底值与真实 CH 分叉，会构成"对错误实例核验"的
    假绿通道；缺文件/缺键时 env_found=False，调用方必须 fail-closed。
    """
    host, port = "localhost", 8123
    env_found = False
    try:
        with open(CH_ENV_FILE, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^CLICKHOUSE_HOST=(.+)$", line.strip())
                if m:
                    host = m.group(1).strip()
                    env_found = True
                m = re.match(r"^CLICKHOUSE_HTTP_PORT=(.+)$", line.strip())
                if m:
                    port = int(m.group(1).strip())
                    env_found = True
    except (FileNotFoundError, ValueError):
        pass
    return host, port, env_found


def query_backup_log_created(since_utc: datetime) -> dict[str, Any]:
    """假绿交叉核验数据源：system.backup_log（持久 MergeTree 表）中
    status='BACKUP_CREATED' 且 event_time >= since_utc 的行数。

    列名以 CH 26.6 实测 schema 为准：判别列是 status Enum8
    ('CREATING_BACKUP'/'BACKUP_CREATED'/'BACKUP_FAILED'/...)，无 event_type 列
    （2026-09-24 活体试射实证，禁凭记忆写列名）。

    since_utc 必须是带时区的 UTC 时间（RULE-SCHEMA-TZ：显式时区，禁 naive）；
    查询字面量按 UTC 解析，与列的显示时区无关（按 epoch 比较）。

    Fail-closed：查询失败一律返回 ok=False，调用方不得把 ok 记成已核验。
    """
    host, port, env_found = read_ch_http_endpoint()
    if not env_found:
        return {
            "ok": False,
            "count": 0,
            "max_event_time": "",
            "error": "CH endpoint env missing (fail-closed, no localhost fallback)",
        }
    if since_utc.tzinfo is None:
        since_utc = since_utc.replace(tzinfo=timezone.utc)
    literal = since_utc.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    query = _SQL_BACKUP_LOG_CREATED_PROBE.format(literal=literal)
    try:
        # P2-14b：私网探针绕过 http_proxy 环境变量，防代理劫持核验数据源
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(f"http://{host}:{port}/", data=query.encode("utf-8"))
        with opener.open(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", "replace").strip()
        parts = body.split("\t")
        count = int(parts[0].strip() or 0)
        max_event_time = parts[1].strip() if len(parts) > 1 else ""
        return {"ok": True, "count": count, "max_event_time": max_event_time, "error": None}
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return {"ok": False, "count": 0, "max_event_time": "", "error": str(exc)}


def read_report_ch_status(run_start_utc: datetime, stdout: str = "") -> dict[str, Any]:
    """读 backup.ps1 STAGE 4 落盘的本轮报告，取 databases.clickhouse 段。

    报告路径发现双通道：
      1. stdout 里的 "Report saved: <path>"（backup.ps1 自报路径，最可靠——
         reconciler 可能在序列器 worktree 进程里跑，其 PROJECT_ROOT 指向
         worktree，而 backup.ps1 内部硬编码主仓根，报告永远落在主仓 logs/）；
      2. 兜底 glob PROJECT_ROOT/logs/backup_report_*.json。
    只认 run_start_utc（容差 90s）之后新写的报告，防止吃到上一轮旧报告。
    found=False 表示本轮无可用报告（含 lock-skip 短退出，本就不产报告），
    调用方走 fail-closed。
    """
    threshold = run_start_utc - timedelta(seconds=90)
    candidates: list[Path] = []
    m = re.search(r"Report saved:\s*(\S+\.json)", stdout or "")
    if m:
        candidates.append(Path(m.group(1)))
    logs_dir = Path(PROJECT_ROOT) / "logs"
    try:
        candidates.extend(sorted(logs_dir.glob("backup_report_*.json"), key=lambda p: p.stat().st_mtime, reverse=True))
    except OSError:
        pass
    for path in candidates:
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        except OSError:
            continue
        if mtime < threshold:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        ch = (data.get("databases") or {}).get("clickhouse") or {}
        return {
            "found": True,
            "ch_status": ch.get("status"),
            "ch_verified": ch.get("verified"),
            "reason": ch.get("reason"),
            "report": str(path),
        }
    return {"found": False, "ch_status": None, "ch_verified": None, "reason": None, "report": None}


# ── P-7 点火/托管分离辅助（2026-09-26 灾备断链治本）─────────────────────────
def get_backup_lock_file() -> Path:
    """backup.ps1 的并发锁路径（.runtime/backup.lock，ps1 硬编码主仓根写）。

    与 get_state_file() 同源——都用 PROJECT_ROOT；在 worktree 里可能读到 worktree
    副本（无消费者），故主动锁自查只是"少起一个注定撞锁的子进程"的优化，真正的
    并发仲裁仍在 backup.ps1 侧 Test-BackupLock（本函数误判不影响 INV-12 正确性）。
    """
    return Path(PROJECT_ROOT) / ".runtime" / "backup.lock"


def get_ignite_log_dir() -> Path:
    """脱离点火日志落盘目录（PROJECT_ROOT/logs，与 backup.ps1 报告同侧）。"""
    return Path(PROJECT_ROOT) / "logs"


_pid_alive_checker: Any = None


def _load_pid_alive_checker() -> Any:
    """复用 backup_runtime_state._is_pid_alive（跨平台、失败保守判活的既有实现），
    不另起炉灶。importlib 从文件路径加载该模块（它自带 sys.path 引导）；失败返回
    None 由调用方走保守判活。"""
    global _pid_alive_checker
    if _pid_alive_checker is not None:
        return _pid_alive_checker
    helper = Path(PROJECT_ROOT) / "scripts" / "governance" / "meta" / "backup_runtime_state.py"
    if not helper.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location("_backup_runtime_state_probe", str(helper))
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = getattr(mod, "_is_pid_alive", None)
        if callable(fn):
            _pid_alive_checker = fn
        return fn
    except Exception:  # noqa: BLE001  # 复用件加载失败非致命，退到保守判活
        logger.warning("加载 backup_runtime_state._is_pid_alive 失败，退到保守判活", exc_info=True)
        return None


def _is_pid_alive(pid: int) -> bool:
    """持锁进程存活判定——委托复用的跨平台实现；复用件不可用时保守判活。

    保守方向=判活：宁可本轮不点火（记 lock_skipped 是诚实观测），也不冒并发双跑险；
    真并发由 ps1 侧锁最终仲裁。测试通过 monkeypatch 本名控制存活。
    """
    fn = _load_pid_alive_checker()
    if fn is None:
        logger.warning("_is_pid_alive：复用件不可用，保守判活 pid=%s", pid)
        return True
    return bool(fn(pid))


def read_backup_lock_holder_pid(lock_file: Path | None = None) -> int | None:
    """解析 .runtime/backup.lock 的持有者 PID（ps1 格式 "PID:<n> START:<iso>"）。

    锁缺失/损坏（无 PID 段）返回 None——调用方据此走点火支路（撞锁甄别交 ps1）。
    注：不能复用 backup_runtime_state._read_lock_holder_pid，那读的是 JSON 锁
    （.backup_pg.lock 等），与 ps1 的 "PID:" 文本格式不同源，故此处按 ps1 判据自解析。
    """
    path = Path(lock_file) if lock_file else get_backup_lock_file()
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return None
    except OSError as exc:
        logger.debug("read backup lock failed (%s): %s", path, exc)
        return None
    m = _RE_LOCK_PID.search(raw)
    if not m:
        return None
    try:
        return int(m.group(1))
    except (TypeError, ValueError):
        return None


def is_backup_lock_held(lock_file: Path | None = None) -> tuple[bool, int | None]:
    """主动锁自查：持锁者存活 → (True, pid)；锁损坏/持锁者死 → (False, ...)。"""
    holder = read_backup_lock_holder_pid(lock_file)
    if holder is None or holder <= 0:
        return False, holder
    return _is_pid_alive(holder), holder


def read_ignition_log(log_path: Path | str) -> str:
    """读取脱离点火的落盘日志（含 State saved:/Report saved:/lock-skip 语义）。

    读取端一律 utf-8-sig 去 BOM（ps1 用 UTF8Encoding($false) 写=无 BOM，但 Write-Host
    经控制台重定向可能带 BOM/换行差异，utf-8-sig 两种都稳）。
    """
    try:
        return Path(log_path).read_text(encoding="utf-8-sig", errors="replace")
    except (FileNotFoundError, OSError) as exc:
        logger.debug("ignition log unreadable (%s): %s", log_path, exc)
        return ""


def launch_detached_backup(
    backup_script: Path | str,
    log_path: Path | str,
    err_path: Path | str | None = None,
    root: Path | str | None = None,
) -> Any:
    """完全脱离地启动 backup.ps1——只点火不托管。

    经"瞬时 powershell 装载器 + Start-Process -WindowStyle Hidden + 落盘重定向"启动：
    装载进程在 Start-Process 返回后立即退出，真备份进程的父 PID 因此指向已亡装载器，
    而非本次 reconcile_worker——收割器 ``psutil.children(recursive)`` 沿**活** PPID 链
    扫描时取不到它，从而免疫级联收割（这就是本函数不同于旧 subprocess.run 直接托管的
    关键）。本调用只等装载器退出（上限 IGNITE_SPAWN_TIMEOUT_S，秒级），绝不等流水线。
    """
    root = Path(root) if root else PROJECT_ROOT
    log_path = Path(log_path)
    err_path = Path(err_path) if err_path else log_path.with_name(log_path.stem + ".err.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    err_path.parent.mkdir(parents=True, exist_ok=True)
    arg_list = f"-NoProfile -ExecutionPolicy Bypass -File {backup_script}"
    ps_cmd = (
        "$null = Start-Process -FilePath 'powershell.exe' "
        f"-ArgumentList '{arg_list}' "
        f"-WorkingDirectory '{root}' "
        "-WindowStyle Hidden "
        f"-RedirectStandardOutput '{log_path}' "
        f"-RedirectStandardError '{err_path}'"
    )
    return subprocess.run(  # noqa: S603  固定 powershell + 我方拼装命令，无外部输入注入面
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
        capture_output=True,
        text=True,
        encoding="utf-8-sig",
        errors="replace",
        timeout=IGNITE_SPAWN_TIMEOUT_S,
        cwd=str(root),
    )


def _adjudicate_completed_run(
    run_start: datetime,
    session_id: str,
    resolved_state: Path | None,
    log_text: str,
    ReconcileResult: Any,
) -> Any:
    """对"已跑到 STAGE 4 的一轮备份"落 INV-11 权威裁决（原 reconcile 同步决策树移植）。

    语义一字不改，仅数据源从同步 stdout/returncode 换成脱离日志文本 + report +
    backup_log 交叉核验：
      - report.clickhouse.status=="failed" → ch_failed（旧 exit=2 分支）
      - status!="skipped" 且 backup_log 当窗有 BACKUP_CREATED 且尺寸自检非 false → ok
      - 否则 → 假绿嫌疑，降级 ch_log_missing + 连带摘 CH ok
      - status=="skipped" → 合法 ok，分因 ok_ch_skipped / ok_ch_degraded
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    summary = (log_text or "")[-200:]
    report = read_report_ch_status(run_start, log_text)
    ch_status = report.get("ch_status")
    ch_verified = report.get("ch_verified")

    if ch_status == "failed":
        # CH 阶段失败（backup.ps1 已持久化 last_ch_backup_* 到 state）。8h 代码备份计时
        # 照常推进；CH 24h 仅在成功时推进。返回 warn 使失败在 commit/merge 可见
        # （2026-07-19 事件：两次自动备份记 ok 但 CH 未备份，禁止静默跳过）。
        update_state_at(
            resolved_state,
            last_backup_time=now_iso,
            last_backup_status="ch_failed",
            last_session_id=session_id,
            last_run_outcome="ch_failed",
            last_backup_log_verified=False,
            last_ignite_log=None,
        )
        ch_err = load_state_from(resolved_state or get_state_file()).get("last_ch_backup_error", "unknown")
        return ReconcileResult(
            action="warn",
            detail=f"backup ok but ClickHouse stage failed: {ch_err}",
        )

    probe_since = run_start - timedelta(seconds=CH_LOG_WINDOW_BUFFER_SECONDS)
    if ch_status != "skipped":
        probe = query_backup_log_created(probe_since)
        if (not probe.get("ok")) or probe.get("count", 0) == 0:
            # P2-10/P1-4：瞬时抖动/flush 边窗立即复查一次（非 sleep——宪法事件触发铁律）。
            probe = query_backup_log_created(probe_since)
        if probe.get("ok") and probe.get("count", 0) > 0 and ch_verified is not False:
            update_state_at(
                resolved_state,
                last_backup_time=now_iso,
                last_backup_status="ok",
                last_session_id=session_id,
                last_run_outcome="backed_up",
                last_backup_log_verified=True,
                last_backup_log_count=probe.get("count"),
                last_backup_log_max_event_time=probe.get("max_event_time"),
                last_ch_backup_status="ok",
                last_ch_backup_verified=True,
                last_ignite_log=None,
            )
            ch_detail = ch_status if ch_status else "unknown"
            return ReconcileResult(
                action="auto_committed",
                detail=f"backup ok (clickhouse={ch_detail}, backup_log verified, rows={probe.get('count')}): {summary}",
            )
        # 核验不过=假绿嫌疑（P2-15b：ps1 尺寸自检 false 同罪）：降级 + 连带摘 CH ok。
        if not probe.get("ok"):
            probe_state = "probe_error"
        elif ch_verified is False:
            probe_state = "size_sanity_failed"
        else:
            probe_state = "zero_rows"
        return _fake_green_verdict(
            resolved_state, session_id, now_iso, summary, ch_status, probe_state, ReconcileResult
        )

    # CH 段 skipped 分因（P1-7）：仅 24h cadence 合法；service down/config missing 记 degraded。
    skip_reason = str(report.get("reason") or "unknown")
    cadence_legal = skip_reason.startswith("24h cadence")
    update_state_at(
        resolved_state,
        last_backup_time=now_iso,
        last_backup_status="ok",
        last_session_id=session_id,
        last_run_outcome="ok_ch_skipped" if cadence_legal else "ok_ch_degraded",
        last_ch_skip_reason=skip_reason,
        last_ignite_log=None,
    )
    return ReconcileResult(
        action="auto_committed",
        detail=f"backup ok (clickhouse=skipped: {skip_reason}): {summary}",
    )


def _fake_green_verdict(
    resolved_state: Path | None,
    session_id: str,
    now_iso: str,
    summary: str,
    ch_status: Any,
    probe_state: str,
    ReconcileResult: Any,
) -> Any:
    """假绿嫌疑分支的落库+裁决（从 _adjudicate_completed_run 拆出，语义零改动）。

    拆分理由＝COMPLEXITY-GUARD（§5.158）：父函数裁决分支多、嵌套判断压线。
    """
    update_state_at(
        resolved_state,
        last_backup_time=now_iso,
        last_backup_status="ch_log_missing",
        last_session_id=session_id,
        last_run_outcome="fake_green_blocked" if ch_status == "ok" else "unverified_no_log",
        last_backup_log_verified=False,
        last_ch_backup_status="ch_log_missing",
        last_ch_backup_verified=False,
        last_ignite_log=None,
    )
    detail = (
        "FAKE-GREEN BLOCKED: detached run reached STAGE4 but system.backup_log "
        f"has no BACKUP_CREATED row in window ({probe_state}, ch_status={ch_status}); "
        "state demoted to ch_log_missing"
    )
    return ReconcileResult(action="warn", detail=detail)


def settle_previous_ignition(session_id: str) -> Any:
    """延后验核（INV-11）：结算上一轮"已点火待验"——由下一次事件触发调用。

    读 state 的 last_ignite_log/last_backup_launch_time，解析脱离落盘日志：
      - 含 "Another backup is running" → 本轮 ps1 自撞锁短退出（INV-12）→ 记
        lock_skipped、不推进计时、清 pending（ps1 撞锁 exit 早于 STAGE 4，无 State
        saved 锚 → 落本地 state 仅作观测）。
      - 含 "State saved:"（到 STAGE 4）→ 走 _adjudicate_completed_run 交叉核验落权威
        裁决（锚定主仓 state）；worktree 情形额外清本地 pending 指针防重复结算。
      - 无 STAGE 4 痕迹（崩溃/被杀/仍在跑）→ fail-closed：不记 ok，保留 pending 等下轮。
    以 last_ignite_log 指针是否存在判"有无待结算轮"（点火写、结算后清）。
    """
    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcileResult
    except ImportError:
        ReconcileResult = dict  # type: ignore

    state = load_state()
    log_str = state.get("last_ignite_log")
    launch_str = state.get("last_backup_launch_time")
    if not log_str or not launch_str:
        return None
    try:
        run_start = datetime.fromisoformat(launch_str)
    except (ValueError, TypeError):
        update_state_at(None, last_ignite_log=None)  # 坏标记不卡死后续点火
        return None
    if run_start.tzinfo is None:
        run_start = run_start.replace(tzinfo=timezone.utc)

    log_text = read_ignition_log(log_str)
    m = _RE_STATE_SAVED.search(log_text)
    resolved_state = Path(m.group(1)) if m else None

    if _LOCK_SKIP_MARKER in log_text:
        now_iso = datetime.now(timezone.utc).isoformat()
        # 撞锁短退出无主仓锚：写本地 state 观测行即可（不推进计时）。
        update_state_at(
            None,
            last_run_outcome="lock_skipped",
            last_lock_skip_time=now_iso,
            last_ignite_log=None,
        )
        return ReconcileResult(
            action="warn",
            detail="prior ignition lock-skipped per detached log; state cadence untouched",
        )

    if not m:
        # 未到 STAGE 4：可能在跑或已夭折——fail-closed 不记 ok，保留 pending。
        logger.debug("settle_previous_ignition: 脱离日志未见 State saved:，保持 pending")
        return None

    result = _adjudicate_completed_run(run_start, session_id, resolved_state, log_text, ReconcileResult)
    # worktree 情形权威裁决写在主仓 resolved_state，本地 pending 指针须显式清，防重复结算。
    if resolved_state is not None and Path(resolved_state) != get_state_file():
        update_state_at(None, last_ignite_log=None)
    return result


def trigger(committed_files: list[str]) -> bool:
    """触发条件判断（INV-09：双条件触发）

    条件1：committed_files 中存在重要文件
    条件2：距上次成功备份 ≥ 8小时（首次备份无状态时视为满足）

    F-06 Track A 治本（2026-07-17）：触发参数（prefixes/files/min_interval）真源
    从硬编码常量迁移到 backup_config.yaml §trigger（load_config 加载），硬编码
    常量仅作 YAML 缺失时的 fallback（消除 load_config 定义但未调用的死代码）。
    """
    # 加载配置（YAML 真源 + 硬编码 fallback）
    config = load_config()
    trigger_cfg = config.get("trigger", {}) if config else {}

    # 条件1：检测重要文件变更（prefixes/files 从 YAML 读取，fallback 到硬编码）
    prefixes = tuple(trigger_cfg.get("important_prefixes", IMPORTANT_PREFIXES))
    important_files = frozenset(trigger_cfg.get("important_files", IMPORTANT_FILES))
    has_important = False
    for f in committed_files:
        rel = rel_path(f)
        if rel.startswith(prefixes) or rel in important_files:
            has_important = True
            break
    if not has_important:
        return False

    # 条件2：检查最小间隔（min_interval_seconds 从 YAML 读取，fallback 到硬编码）
    min_interval = trigger_cfg.get("min_interval_seconds", MIN_INTERVAL_SECONDS)
    state = load_state()
    last_backup_str = state.get("last_backup_time")
    if last_backup_str:
        try:
            last_backup = datetime.fromisoformat(last_backup_str)
            if last_backup.tzinfo is None:
                last_backup = last_backup.replace(tzinfo=timezone.utc)
            elapsed = (datetime.now(timezone.utc) - last_backup).total_seconds()
            if elapsed < min_interval:
                # cadence-skip 单独记账（2026-09-24 假绿处方）：重要文件在飞但被
                # 节奏闸挡住 ≠ 备过份；与"当日确实备份过"（last_backup_log_verified）
                # 分开记，避免 skip 被误读成健康。写失败降级 debug，不碰触发链。
                try:
                    update_state(
                        last_cadence_skip_time=datetime.now(timezone.utc).isoformat(),
                        last_cadence_skip_reason=(f"min_interval elapsed={int(elapsed)}s < {int(min_interval)}s"),
                    )
                except (OSError, TypeError, ValueError):
                    logger.debug("cadence-skip state write failed", exc_info=True)
                logger.debug(
                    "backup_reconciler: skip (elapsed=%.0fs < %ds)",
                    elapsed,
                    min_interval,
                )
                return False
        except (ValueError, TypeError):
            # 状态文件损坏，视为无状态，允许触发
            logger.warning("backup_state.json has invalid last_backup_time, allowing trigger")

    return True


def _trigger(committed_files: list[str]) -> bool:
    """向后兼容包装：委托给 trigger()。"""
    return trigger(committed_files)


def reconcile(committed_files: list[str], session_id: str) -> Any:
    """post-commit 点火通道（P-7：只点火、不托管）。

    流程：
      0. 结算上一轮"已点火待验"（读脱离日志→report→backup_log 交叉核验，落 INV-11
         权威裁决；下一次事件触发即收敛）。
      1. 主动锁自查：持锁者存活则直接记 lock_skipped 返回，**不起任何子进程**（INV-12）。
      2. 需真跑时经完全脱离的方式启动 backup.ps1，立即返回，不等流水线。
      3. 记"已点火待验"标记（last_backup_launch_time/last_ignite_log），绝不同步断言
         ok/failed（避免假绿，INV-11）；cadence 锚 last_backup_time 由 ps1 STAGE 4 自写。

    返回 ReconcileResult：lock_skipped / ignited 均为 warn（未核验不冒领 auto_committed）。
    """
    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcileResult
    except ImportError:
        # 测试环境无 zephyr 模块时，返回简单 dict
        ReconcileResult = dict  # type: ignore

    backup_script = PROJECT_ROOT / "scripts" / "backup" / "backup.ps1"
    if not backup_script.exists():
        return ReconcileResult(
            action="warn",
            detail=f"backup.ps1 not found at {backup_script}",
        )

    # (0) 延后验核：结算上一轮点火（INV-11 权威裁决在此落账，best-effort 不阻断点火）。
    try:
        settle_previous_ignition(session_id)
    except Exception:  # noqa: BLE001  # 结算失败不得影响本轮点火，只降级日志
        logger.warning("settle_previous_ignition failed", exc_info=True)

    # (1) 点火前主动锁自查（INV-12 前移）：持锁者活 → 记 lock_skipped、不起子进程。
    held, holder = is_backup_lock_held()
    if held:
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            # 只留观测行：不推进 8h 计时（last_backup_time 不动）、不降级在飞备份状态。
            update_state(last_run_outcome="lock_skipped", last_lock_skip_time=now_iso)
        except (OSError, TypeError, ValueError):
            logger.debug("lock_skipped state write failed", exc_info=True)
        return ReconcileResult(
            action="warn",
            detail=f"backup lock held by live PID {holder}; ignition skipped, cadence untouched",
        )

    # (2) 完全脱离地点火（DETACHED via Start-Process，非 subprocess.run 同步托管长跑）。
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    ignite_log = get_ignite_log_dir() / f"{IGNITE_LOG_PREFIX}{ts}.log"
    try:
        launch_detached_backup(backup_script, ignite_log)
    except (subprocess.SubprocessError, OSError) as exc:
        # 装载器本身失败（罕见）：诚实记 ignite_failed，不冒领任何备份状态。
        update_state(last_run_outcome="ignite_failed", last_ignite_error=str(exc)[:200])
        return ReconcileResult(
            action="warn",
            detail=f"backup ignition failed (loader error): {exc}",
        )

    # (3) 记"已点火待验"标记，真验核延后（下一次触发/日检按 backup_log 交叉核对）。
    now_iso = datetime.now(timezone.utc).isoformat()
    update_state(
        last_backup_launch_time=now_iso,
        last_ignite_log=str(ignite_log),
        last_run_outcome="ignited_pending_verification",
        last_ignite_session_id=session_id,
    )
    return ReconcileResult(
        action="warn",
        detail=(
            f"backup ignited detached (non-hosting, log={ignite_log.name}); "
            "ok/failed deferred to next trigger/daily backup_log cross-check (INV-11)"
        ),
    )


def _reconcile(committed_files: list[str], session_id: str) -> Any:
    """向后兼容包装：委托给 reconcile()。"""
    return reconcile(committed_files, session_id)


def make_backup_reconciler(project_root: Path | None = None):
    """工厂函数：创建backup reconciler spec。

    Args:
        project_root: 项目根路径（默认自动检测）

    Returns:
        ReconcilerSpec（含 gate_id/trigger/reconcile/priority）
    """
    global PROJECT_ROOT, STATE_FILE, CONFIG_FILE
    if project_root is not None:
        PROJECT_ROOT = Path(project_root)
        CONFIG_FILE = PROJECT_ROOT / "scripts" / "backup" / "backup_config.yaml"
        STATE_FILE = PROJECT_ROOT / "data" / "databases" / "backup_state.json"

    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcilerSpec
    except ImportError:
        # 测试环境无zephyr模块时，使用fallback类（避开ARCH-034 CLASS-UNIQUENESS冲突）
        class _ReconcilerSpecFallback:  # type: ignore
            def __init__(self, gate_id, trigger, reconcile, priority=100):
                self.gate_id = gate_id
                self.trigger = trigger
                self.reconcile = reconcile
                self.priority = priority

        ReconcilerSpec = _ReconcilerSpecFallback

    return ReconcilerSpec(
        gate_id="BACKUP-RECONCILER",
        trigger=trigger,
        reconcile=reconcile,
        priority=200,  # 低优先级（晚于其他reconciler执行）
        file_ops=frozenset({"read", "write"}),
    )


if __name__ == "__main__":
    # 手动测试入口
    spec = make_backup_reconciler()
    print(f"gate_id={spec.gate_id}, priority={spec.priority}")
    print(f"trigger(['{PROJECT_ROOT / 'src' / 'test.py'}']) = {spec.trigger([str(PROJECT_ROOT / 'src' / 'test.py')])}")
