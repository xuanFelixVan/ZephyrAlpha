# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §3.1
# [MODULE] scripts.backup.backup_reconciler
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcilerSpec, ReconcileResult)
# [CONSUMERS] GitCommitGateway._reconciliation_registry.register
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-08:post-commit reconciler触发非时间触发 | INV-09:双条件触发(重要文件+8h间隔) | INV-10:状态持久化backup_state.json | INV-11:ok状态写入前须过system.backup_log当窗BACKUP_CREATED交叉核验,假绿降级ch_log_missing并连带摘除last_ch_backup_status的ok,cadence-skip单独记账 | INV-12:gate裁决写入锚定主仓state真源(stdout State saved:通道),lock-skip短退出不推进计时不降级真实状态,skipped分因(cadence合法/其余degraded)
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
    """执行备份——调用PowerShell backup.ps1

    返回 ReconcileResult（auto_committed 或 warn）。
    """
    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcileResult
    except ImportError:
        # 测试环境无zephyr模块时，返回简单dict
        ReconcileResult = dict  # type: ignore

    backup_script = PROJECT_ROOT / "scripts" / "backup" / "backup.ps1"
    if not backup_script.exists():
        return ReconcileResult(
            action="warn",
            detail=f"backup.ps1 not found at {backup_script}",
        )

    try:
        run_start = datetime.now(timezone.utc)
        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(backup_script),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",  # P2-14a：非 UTF-8 字节不再炸 UnicodeDecodeError
            timeout=14400,  # 4h超时（CH ~200GiB VHDX Disk备份，见blueprint §4.3）
            cwd=str(PROJECT_ROOT),
        )
    except subprocess.TimeoutExpired:
        update_state(last_backup_status="timeout", last_run_outcome="timeout")
        return ReconcileResult(
            action="warn",
            detail="backup timed out after 14400s",
        )

    # state 真源锚定（P0-1 分家治理）：backup.ps1 在主仓跑（$ProjectRoot 硬编码
    # 主仓根），stdout 携带 "State saved:" 主仓 state 路径——gate 裁决必须写进有
    # 下游消费者的那份文件，而非 worktree 进程里的本地副本（该副本无人消费）。
    state_path_m = re.search(r"State saved:\s*(\S+)", result.stdout or "")
    resolved_state = Path(state_path_m.group(1)) if state_path_m else None

    if result.returncode == 0:
        now_iso = datetime.now(timezone.utc).isoformat()
        # 取最后200字符作为摘要
        summary = result.stdout[-200:] if result.stdout else ""
        # lock-skip 识别（P1-3）：ps1 撞锁短退出=本轮什么都没备份。不得推进 8h
        # 计时、不得降级在飞备份的真实状态，只留 outcome 观测行。
        if "Another backup is running" in (result.stdout or ""):
            update_state_at(resolved_state, last_run_outcome="lock_skipped", last_lock_skip_time=now_iso)
            return ReconcileResult(
                action="warn",
                detail="backup lock-skipped (another backup in flight); state untouched",
            )
        # ── 假绿交叉核验闸（2026-09-24 处方，INV-11）────────────────────────
        # 2026-09-22 实证：backup.ps1 CH 段轮询 system.backups（内存态）成功即写
        # verified=true，但持久真源 system.backup_log 当日零行——状态假绿会连带
        # 让 db_dumps 轮转闸（消费 last_ch_backup_status=="ok"）在 CH 断档期照删
        # 旧 dump。故 exit=0 的 ok 落账前必须过 backup_log 当窗 BACKUP_CREATED 核验。
        report = read_report_ch_status(run_start, result.stdout)
        ch_status = report.get("ch_status")
        ch_verified = report.get("ch_verified")
        probe_since = run_start - timedelta(seconds=CH_LOG_WINDOW_BUFFER_SECONDS)
        if ch_status != "skipped":
            probe = query_backup_log_created(probe_since)
            if (not probe.get("ok")) or probe.get("count", 0) == 0:
                # P2-10/P1-4：瞬时抖动/flush 边窗复查一次。立即重试而非 sleep——
                # PERM-TRIGGER 门禁字面 .sleep( 模式（宪法事件触发铁律守门），
                # 300s 回看窗 + ps1 尾段落盘耗时已给 backup_log flush 留足余量。
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
                    # P2-13：闸是 CH 状态唯一裁决者，核验通过时显式复权
                    last_ch_backup_status="ok",
                    last_ch_backup_verified=True,
                )
                ch_detail = ch_status if ch_status else "unknown"
                return ReconcileResult(
                    action="auto_committed",
                    detail=f"backup ok (clickhouse={ch_detail}, backup_log verified, "
                    f"rows={probe.get('count')}): {summary}",
                )
            # 核验不过=假绿嫌疑（P2-15b：ps1 尺寸自检 verified=false 同罪）：降级记
            # 账 + 连带摘掉 last_ch_backup_status 的 ok，下游 db_dumps 轮转闸随之
            # 停摆（宁停转，勿假绿）。
            update_state_at(
                resolved_state,
                last_backup_time=now_iso,
                last_backup_status="ch_log_missing",
                last_session_id=session_id,
                last_run_outcome="fake_green_blocked" if ch_status == "ok" else "unverified_no_log",
                last_backup_log_verified=False,
                last_ch_backup_status="ch_log_missing",
                last_ch_backup_verified=False,
            )
            if not probe.get("ok"):
                probe_state = "probe_error"
            elif ch_verified is False:
                probe_state = "size_sanity_failed"
            else:
                probe_state = "zero_rows"
            return ReconcileResult(
                action="warn",
                detail="FAKE-GREEN BLOCKED: exit=0 but system.backup_log has no "
                f"BACKUP_CREATED row in window ({probe_state}, ch_status={ch_status}); "
                "state demoted to ch_log_missing",
            )
        # CH 段 skipped 分原因甄别（P1-7）：仅 24h cadence 属合法跳过；service
        # down / config missing 记 ok_ch_degraded——代码/PG/SQLite 确已备份，但
        # CH 中断不得在 reconciler 层隐身（SLO 哨兵读 last_ch_backup_status 兜底）。
        skip_reason = str(report.get("reason") or "unknown")
        cadence_legal = skip_reason.startswith("24h cadence")
        update_state_at(
            resolved_state,
            last_backup_time=now_iso,
            last_backup_status="ok",
            last_session_id=session_id,
            last_run_outcome="ok_ch_skipped" if cadence_legal else "ok_ch_degraded",
            last_ch_skip_reason=skip_reason,
        )
        return ReconcileResult(
            action="auto_committed",
            detail=f"backup ok (clickhouse=skipped: {skip_reason}): {summary}",
        )
    if result.returncode == 2:
        # CH阶段失败但代码/PG/SQLite/CH配置同步成功（backup.ps1已持久化last_ch_backup_*
        # 到backup_state.json）。8h代码备份计时照常推进；CH 24h计时仅在成功时推进
        # （失败在下一个调度窗口重试）。返回warn使失败在commit/merge时可见——
        # CH失败禁止静默跳过（2026-07-19事件：两次自动备份记录ok但CH未备份）。
        now_iso = datetime.now(timezone.utc).isoformat()
        update_state_at(
            resolved_state,
            last_backup_time=now_iso,
            last_backup_status="ch_failed",
            last_session_id=session_id,
            last_run_outcome="ch_failed",  # P2-12：不留上一轮旧 outcome
            last_backup_log_verified=False,
        )
        ch_err = load_state_from(resolved_state or get_state_file()).get("last_ch_backup_error", "unknown")
        return ReconcileResult(
            action="warn",
            detail=f"backup ok but ClickHouse stage failed: {ch_err}",
        )
    update_state_at(resolved_state, last_backup_status="failed", last_run_outcome="failed")
    err_summary = result.stderr[-200:] if result.stderr else result.stdout[-200:]
    return ReconcileResult(
        action="warn",
        detail=f"backup failed (exit={result.returncode}): {err_summary}",
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
