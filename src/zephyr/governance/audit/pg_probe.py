# [BLUEPRINT] MOD-GOV_PG_PROBE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.audit.pg_probe
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.depgraph_schema (_load_pg_config 连接参数真源); zephyr.governance.audit.reconciliation_registry (log_gate_failure/_governance_db_path 留痕链); zephyr.shared.utils.time_utils (now_utc); stdlib(socket/json)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.commit (pre-commit 前置探测); zephyr.gov_enforcement.commit_gates.rename_depgraph_sync_gate / new_file_depgraph_gate / depgraph_pre_registration_gate / depgraph_freshness_gate (降级留痕联动); zephyr.gov_enforcement.rule_bridge.session_worktree._run_pre_merge_topo_check (降级留痕联动)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 探测永不阻断主流程（任何异常内部吞掉只落状态/日志）；状态文件 .runtime/pg_probe_state.json 原子写（tmp+replace）；探测为纯 TCP 连接（≤1s 超时，不认证不查询）；host/port 唯一真源=depgraph_schema._load_pg_config（DATABASE_URL > config/.env.postgres，禁复制解析逻辑）；留痕统一走 reconciliation_registry.log_gate_failure（critical_warn，与 GATE-PANORAMA-ALIGNMENT 同款签名），本模块只做当日同签名去重，不修改 log_gate_failure 本体；governance.db schema 不变
# [MODIFY-GUARD] gate 放行语义由调用方保持（本模块只提供状态判定与留痕，永不返回阻断指令）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 所有公开函数永不抛异常——探测/读状态/去重查询/落库任一失败均降级为保守默认值（offline 判定=False 即不误导门卡走"DB 离线"路径；留痕失败仅 logger.warning）
# [TESTS] tests/governance/audit/test_pg_probe.py
# [A_module] module_id=MOD-PG_PROBE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# 治本（2026-08-17）：module_id MOD-GOV_PG_PROBE→MOD-PG_PROBE——N-17 域片段须与
# DOMAIN 头部声明一致：旧片段 GOV_PG_PROBE≠GOV_AUDIT 且共享 token GOV 触发违例；
# 新 id 片段 PG_PROBE 与 GOV_AUDIT 零共享 token（N-17 跳过）且过 N-06 派生轨格式；
# FOPEN-001 新建时经 merge 通道绕过 GATE-11 落入（commit 通道会阻断新违规），顺手治本。
# （注释禁用 [DOMAIN] 方括号写法——GATE-DOMAIN-FK 会误解析为域头，2026-08-17 实证）
# [TTL] permanent
# [ARCH] ARCH-119
"""pg_probe.py — PG 可用性前置探针 + DB 降级留痕统一入口（tracker #116 / #ARCH-119）

Owner 裁定（2026-08-17，fail-open 敞口治理 B1+B2 全量，方案真源
docs/_working/reports/2026-08-17-fail-open-analysis.md）：

- B2（本模块主体）：PG 可用性前置探针——网关 commit 前置执行 TCP 5432 探测
  （≤1s 超时，失败不阻断只落状态），结果落 ``.runtime/pg_probe_state.json``；
  depgraph 类门禁（#1 RENAME-DEPGRAPH-SYNC / #2 NEW-FILE-DEPGRAPH-ENFORCEMENT /
  #3 DEPGRAPH-PRE-REGISTRATION / #5 PRE-MERGE-TOPO-CHECK）的 fail-open 分支读
  探针状态区分「DB 离线降级」vs「真无违规/真实错误」；DEPGRAPH-FRESHNESS 在
  探针证实离线超 24h 时豁免 saved_at 停更误伤（报告 §1.3 联动修复）。
- B1（留痕统一入口 ``log_db_failopen``）：fail-open 放行统一接
  ``log_gate_failure`` 持久化（sqlite reconcile_execution_log，critical_warn，
  下次 commit 网关 banner 自动浮现）——与 #4 GATE-PANORAMA-ALIGNMENT 既有先例
  同构；同签名当日去重（防 PG 长期离线告警疲劳，报告 §3 缓解条）。

设计权衡
--------
1. **纯 TCP 探测而非 psycopg2 连接**：探测目标是「服务是否监听」而非「凭证
   是否正确」——TCP 探测无认证开销、无连接池副作用、≤1s 超时可控；
   DB 凭证/库名问题由 gate 自身连接路径按「真实错误」语义暴露（探针在线而
   gate 连接失败 → 不静默，逐次留痕）。
2. **状态文件而非进程内缓存**：commit 网关、merge 链路、reconciler 是不同
   进程，进程内缓存无法共享；``.runtime/`` 是既有仓级瞬态状态目录
   （depgraph_scan_cache.json 同款），文件即跨进程单真源。
3. **first_offline_at / last_reachable_at 双锚点**：FRESHNESS 豁免需要
   「离线时长」证据——单次探测只能证明「现在离线」，不能证明「离线超 24h」。
   状态文件跨探测保留两个锚点，离线时长 = now - first_offline_at。
4. **当日同签名去重**：签名 = gate_id + 降级类别（failover_sig），当日（UTC）
   已在 reconcile_execution_log 存在同签名 critical_warn 则跳过——PG 长期
   离线时每次 commit 都触发降级，不去重会淹没审计视图（告警疲劳）。
5. **去重失败=照样留痕**：去重查询本身失败（库锁/缺表）时宁可多记不可漏记
   （fail-open 对审计有利方向）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: PG 连接参数与探测目标
#   fields: host/port（真源 depgraph_schema._load_pg_config：DATABASE_URL > config/.env.postgres）
#   code: probe_pg / pg_probe_shows_offline 入口
# - id: I2
#   name: fail-open 留痕请求
#   fields: project_root / gate_id / db_offline / reason / affected_files / session_id / stack_trace
#   code: log_db_failopen 入口参数
# 层: 处理
# - id: F1
#   name: TCP 探测 + 状态原子写
#   code: socket 连接 5432（≤1s 超时）→ .runtime/pg_probe_state.json（tmp+replace，双锚点 first_offline_at/last_reachable_at）
# - id: F2
#   name: 降级留痕 + 当日同签名去重
#   code: log_db_failopen → failover_sig=gate_id:category 查 reconcile_execution_log 去重 → log_gate_failure 落 critical_warn
# 层: 输出
# - id: O1
#   name: 探针状态与留痕记录
#   fields: pg_probe_state.json（offline 判定）+ reconcile_execution_log critical_warn 行
#   code: pg_probe_shows_offline 返回 bool / log_db_failopen 返回 None（永不抛异常）
"""

from __future__ import annotations

import json
import logging
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "PG_PROBE_STATE_REL",
    "probe_pg_tcp",
    "refresh_pg_probe_state",
    "read_pg_probe_state",
    "pg_probe_shows_offline",
    "pg_offline_beyond",
    "log_db_failopen",
]

# 探针状态文件（仓级瞬态目录，与 depgraph_scan_cache.json 同区位）
PG_PROBE_STATE_REL = ".runtime/pg_probe_state.json"

# 探测超时（秒）——commit 前置路径上探针必须足够便宜
_PROBE_TIMEOUT_SECONDS = 1.0

# 探针状态新鲜度窗口（秒）——超过视为「未知」，不据此判定 DB 离线
_PROBE_FRESH_SECONDS = 600

# FRESHNESS 豁免锚点字段
_STATE_KEY_LAST_REACHABLE = "last_reachable_at"
_STATE_KEY_FIRST_OFFLINE = "first_offline_at"

# SQL 集中化（§5.160.2）——留痕当日同签名去重查询
_SQL_DEDUP_SAME_DAY = (
    "SELECT 1 FROM reconcile_execution_log "
    "WHERE gate_id = ? AND action = 'critical_warn' "
    "AND detail LIKE ? AND logged_at >= ? LIMIT 1"
)


def _utc_now() -> datetime:
    """当前 UTC 时间——走 time_utils.now_utc 真源（freeze_time 测试可冻结）。"""
    from zephyr.shared.utils.time_utils import now_utc

    return now_utc()


def _parse_iso(raw: object) -> datetime | None:
    """解析 ISO8601 时间戳（带时区）；失败返回 None。"""
    if not isinstance(raw, str) or not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.astimezone(timezone.utc)
    return dt.astimezone(timezone.utc)


def _resolve_pg_endpoint() -> tuple[str, int]:
    """解析 PG host/port——唯一真源 depgraph_schema._load_pg_config（禁复制解析）。

    Raises:
        配置缺失/非法时抛异常（由调用方捕获降级，本函数不吞）。
    """
    from zephyr.governance.depgraph_schema import _load_pg_config

    config = _load_pg_config()
    return config["POSTGRES_HOST"], int(config["POSTGRES_PORT"])


def probe_pg_tcp(host: str, port: int, timeout: float = _PROBE_TIMEOUT_SECONDS) -> tuple[bool, str]:
    """纯 TCP 探测 PG 端口可达性（不认证不查询）。

    Returns:
        (reachable, error) —— reachable=True 时 error 为空串。
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, ""
    except OSError as e:
        return False, f"{type(e).__name__}: {e}"


def read_pg_probe_state(project_root: object) -> dict | None:
    """读取探针状态文件；缺失/损坏返回 None（调用方按「未知」处理）。"""
    try:
        path = Path(str(project_root)) / PG_PROBE_STATE_REL
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("pg_probe: 状态文件读取失败: %s", e)
        return None


def refresh_pg_probe_state(project_root: object, timeout: float = _PROBE_TIMEOUT_SECONDS) -> dict:
    """执行探测并原子写状态文件。永不抛异常（探针失败不阻断主流程）。

    网关 commit 前置 / merge 前置 / reconciler 复跑共用入口。
    状态字段：reachable/checked_at/host/port/error/last_reachable_at/first_offline_at。
    """
    root = Path(str(project_root))
    now = _utc_now().isoformat()
    prev = read_pg_probe_state(root) or {}

    host: str = ""
    port: int = 0
    try:
        host, port = _resolve_pg_endpoint()
        reachable, error = probe_pg_tcp(host, port, timeout)
    except Exception as e:  # noqa: BLE001 — 配置解析失败同样落状态（不阻断）
        reachable, error = False, f"config_unresolved: {type(e).__name__}: {e}"

    state = {
        "reachable": reachable,
        "checked_at": now,
        "host": host,
        "port": port,
        "error": error,
        _STATE_KEY_LAST_REACHABLE: now if reachable else prev.get(_STATE_KEY_LAST_REACHABLE),
        _STATE_KEY_FIRST_OFFLINE: (None if reachable else (prev.get(_STATE_KEY_FIRST_OFFLINE) or now)),
    }
    try:
        path = root / PG_PROBE_STATE_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_name(path.name + ".tmp")
        tmp_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_path.replace(path)
    except OSError as e:
        logger.warning("pg_probe: 状态文件写入失败: %s", e)
    return state


def pg_probe_shows_offline(project_root: object, max_age_seconds: float = _PROBE_FRESH_SECONDS) -> bool:
    """探针是否证实 DB 离线（状态新鲜且 reachable=False）。

    状态缺失/陈旧/可达 → False（保守：不把「未知/在线」误判为离线）。
    """
    state = read_pg_probe_state(project_root)
    if not state or state.get("reachable") is not False:
        return False
    checked_at = _parse_iso(state.get("checked_at"))
    if checked_at is None:
        return False
    return (_utc_now() - checked_at).total_seconds() <= max_age_seconds


def pg_offline_beyond(project_root: object, seconds: float) -> bool:
    """探针证实离线且离线时长超过 seconds（DEPGRAPH-FRESHNESS 24h 豁免判据）。

    离线时长锚点：first_offline_at（首次观测离线）；无该锚点时退 checked_at
    （至少已离线到本次观测）。状态缺失/在线 → False（不误豁免）。
    """
    state = read_pg_probe_state(project_root)
    if not state or state.get("reachable") is not False:
        return False
    anchor = _parse_iso(state.get(_STATE_KEY_FIRST_OFFLINE)) or _parse_iso(state.get("checked_at"))
    if anchor is None:
        return False
    return (_utc_now() - anchor).total_seconds() >= seconds


def _already_logged_today(project_root: object, gate_id: str, signature: str) -> bool:
    """当日（UTC）是否已存在同 gate_id+同签名 critical_warn（防告警疲劳）。

    查询失败返回 False（宁可多记不可漏记）。
    """
    import sqlite3

    from zephyr.governance.audit.reconciliation_registry import _governance_db_path
    from zephyr.shared.utils.time_utils import now_utc

    try:
        db_path = _governance_db_path(project_root)
        if not Path(db_path).is_file():
            return False
        day_start = now_utc().replace(hour=0, minute=0, second=0, microsecond=0)
        conn = sqlite3.connect(db_path, timeout=10.0)
        try:
            row = conn.execute(
                _SQL_DEDUP_SAME_DAY,
                (gate_id, f"%{signature}%", day_start),
            ).fetchone()
            return row is not None
        finally:
            conn.close()
    except Exception as e:  # noqa: BLE001 — 去重查询失败不阻断留痕
        logger.warning("pg_probe: 留痕去重查询失败（照样留痕）: %s", e)
        return False


def log_db_failopen(
    project_root: object,
    gate_id: str,
    *,
    db_offline: bool,
    reason: str,
    affected_files: list[str] | None = None,
    session_id: str = "",
    trigger_source: str = "pre_commit_gate",
    stack_trace: str = "",
) -> None:
    """B1 统一留痕入口：fail-open 放行持久化到 reconcile_execution_log（critical_warn）。

    与 GATE-PANORAMA-ALIGNMENT 的 log_gate_failure 同款签名；附加统一格式：
    放行原因（DB 离线降级 / 真实错误）+ 受影响文件清单 + failover_sig 签名
    （当日同签名去重，防 PG 长期离线告警疲劳）。

    Args:
        project_root: 仓根（gateway.project_root；governance.db 锚定主仓）。
        gate_id: 放行的 gate ID。
        db_offline: True=探针证实 DB 离线（环境降级）；False=探针在线/未知但
            gate 自身连接/执行失败（真实错误，不静默）。
        reason: 人类可读放行原因。
        affected_files: 受影响文件清单（被降级放行的文件）。
        session_id: commit/merge session_id（可空）。
        trigger_source: 触发源标识。
        stack_trace: 异常堆栈（可空）——治本（2026-08-17 #118）：补形参对齐
            log_gate_failure 同款签名（设计声明）并透传；此前缺失致
            depgraph_pre_registration_gate L243 传 stack_trace 时本函数 TypeError，
            fail-open 留痕路径 fail-crash（FOPEN-001 fa25c19e49 引入）。
            （AI-AUDIT11 同义补记：B1 落地时 docstring 声明「与 log_gate_failure 同款签名」
            但漏本参数，调用方 REAL_ERROR 路径传入即 TypeError 反而阻断留痕——补齐使契约声明为真。）
    """
    from zephyr.governance.audit.reconciliation_registry import log_gate_failure

    # 防御：project_root 非真实目录时（如 mock gateway）不落盘——
    # 避免锚定失败后在 CWD 下创建垃圾目录；留痕缺失仅 warning（fail-open 语义不变）。
    if not Path(str(project_root)).is_dir():
        logger.warning(
            "pg_probe: log_db_failopen 跳过——project_root 非真实目录: %r",
            str(project_root)[:80],
        )
        return

    category = "DB_OFFLINE" if db_offline else "REAL_ERROR"
    signature = f"failover_sig={gate_id}:{category}"
    # 当日同签名去重只针对 DB_OFFLINE（防 PG 长期离线告警疲劳，报告 §3 缓解条）；
    # REAL_ERROR（探针在线而 gate 自身失败）逐次留痕——真实错误不静默。
    if db_offline and _already_logged_today(project_root, gate_id, signature):
        logger.info(
            "%s fail-open 留痕当日同签名已存在（%s），跳过去重。",
            gate_id,
            signature,
        )
        return
    files_summary = ""
    if affected_files:
        shown = affected_files[:10]
        suffix = f" (还有 {len(affected_files) - 10} 个)" if len(affected_files) > 10 else ""
        files_summary = f"受影响文件: {', '.join(shown)}{suffix}"
    detail = (
        f"[{signature}] {gate_id} fail-open 放行留痕（tracker #116 B1/B2）。"
        f"放行原因: {reason}（{'DB 离线降级' if db_offline else '真实错误（探针未证实离线）'}）。" + files_summary
    )
    try:
        log_gate_failure(
            project_root,
            gate_id,
            detail,
            session_id=session_id,
            trigger_source=trigger_source,
            stack_trace=stack_trace,
        )
    except Exception as e:  # noqa: BLE001 — 留痕失败不阻断 gate 主流程
        logger.warning("pg_probe: log_db_failopen 落库失败: %s", e)
