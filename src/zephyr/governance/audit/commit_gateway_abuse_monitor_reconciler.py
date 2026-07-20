# [BLUEPRINT] MOD-GOV_commit_gateway_abuse_monitor | docs/03_modules/_domain_governance/blueprint.md | §ARCH-TOOL-HEALTH-V1 Phase 5b
# [MODULE] zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec, _write_reconcile_report); stdlib (json, logging, subprocess, time, pathlib)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] post-commit 事件触发（任何 commit 都触发，滥用监控是全局关注）；reconciler 永不抛异常（异常降级为 warn）；只读 post_commit_guard/commit_gateway_audit 报告，不修改它们
# [MODIFY-GUARD] _GATE_ID / _PRIORITY / 阈值常量
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile 永不抛异常——读取/解析失败降级为 ReconcileResult(action="warn")
# [TESTS] tests/governance/audit/test_commit_gateway_abuse_monitor_reconciler.py
# [A_module] module_id=MOD-GOV-commit_gateway_abuse_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)
"""commit_gateway_abuse_monitor_reconciler.py — commit gateway 持续滥用监控（ARCH-TOOL-HEALTH-V1 Phase 5b，2026-07-19）。

post-commit 事件触发，扫描 ``.runtime/reconcile_reports/`` 下 ``post_commit_guard_*``
与 ``commit_gateway_audit_*`` 报告 + ``git log`` 中 emergency 标记，检测 **持续滥用模式**
（24h/7d 长窗口），补强 POST-COMMIT-GUARD 的 1h 短窗口盲区。

治本动机（第一性原理）
--------------------
POST-COMMIT-GUARD（Phase 5a，裁定 B）在 per-commit 层做 per-hour aggregate 阈值阻断
（默认 10/h）——能捕获**短时高频**滥用。但有 3 类**持续低频**滥用 per-hour 阈值永远抓不到：

1. **持续 warn-only 低频**：5/h × 24h = 120 次 warn-only，但每小时都 <10 不触发 block
2. **emergency_commit 持续滥用**：[GW:*:emergency] 是合法逃生通道，但 5/天 × 7天 = 35 次
   = 系统性问题（应为罕见逃生，非日常工具）
3. **forged_gw_marker 持续低频**：3/天 × 7天 = 21 次伪造 = 严重治理失效（任何伪造都是
   intentional，不应有"低频容忍"）

reconciler 是 post-commit（commit 已入历史不可逆），故只能 warn / critical_warn，
不能 block。但 critical_warn 会打印横幅强制 AI 看到，确保失败不被忽视。

五维滥用检测（warn-only，阈值见下方常量）
-----------------------------------------
1. **warn_only sustained (24h)**: >50 warn_only 事件/24h = 持续低频逃生通道滥用
2. **emergency_commit abuse (24h)**: >5 [GW:*:emergency] commits/24h = 逃生通道日常化
3. **allow_overlap abuse (7d)**: >30 次真实 allow_overlap=True 提交/7d（gate 层审计
   ``.runtime/gate_audit/allow_overlap_usage.jsonl`` 计数）= 逃生通道日常化
4. **forged_gw_marker rate (24h)**: >3 forged_gw_marker/24h = 严重伪造（任何伪造都 serious）
5. **non-GW commit sustained (24h)**: >10 non-GW commits/24h（commit_gw_audit violations
   sum）= 持续绕过 GitCommitGateway

判定
----
- 0 个维度触发 → clean
- 1-2 个维度触发 → warn
- 3+ 个维度触发 OR forged_gw_marker 维度触发 → critical_warn（横幅强制 AI 看到）

priority=875（晚于 git_performance_monitor(870)，早于 remediation_progress(900)）

Usage
-----
::

    from zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler import (
        make_commit_gateway_abuse_monitor_reconciler,
    )

    registry.register(make_commit_gateway_abuse_monitor_reconciler(gateway))
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
    _write_reconcile_report,
)

logger = logging.getLogger(__name__)

_GATE_ID = "GATE-COMMIT-GW-ABUSE-MONITOR"
# priority=875: 晚于 git_performance_monitor(870)，早于 remediation_progress(900)
_PRIORITY = 875

# === 五维滥用阈值（warn-only，reconciler 不能 block post-commit）===
# P3-1 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
# 阈值真源已提取到 trae_069_commit_gateway_abuse_thresholds.yaml（SSoT 铁律：
# 规则数据真源是 YAML 文件）。代码常量改为从此文件加载（fail-open：
# YAML 缺失/解析失败时使用代码内默认值，不阻断 reconciler）。
#
# 历史（裁定 R3/R5/R6 + P1 治本链）：
#   2026-07-19: 原阈值散落在代码常量（_WARN_ONLY_24H_THRESHOLD = 50 等）
#   2026-07-20 P1-4: emergency 10→5 回滚（heartbeat 已落地 + scenario 过滤已引入）
#   2026-07-20 P3-1: 提取到 YAML，代码常量改为 _load_thresholds_from_yaml() 返回值
_THRESHOLDS_YAML_PATH = (
    Path(__file__).resolve().parents[4]  # src/zephyr/governance/audit → repo root
    / "docs" / "01_policies_and_standards" / "rules"
    / "trae_069_commit_gateway_abuse_thresholds.yaml"
)

# 代码内默认值（YAML 缺失/解析失败时 fallback，与 P1 治本后的值一致）
_DEFAULT_THRESHOLDS = {
    "warn_only_sustained_24h": 50,
    "emergency_commit_abuse_24h": 5,
    "allow_overlap_abuse_7d": 30,
    "forged_gw_marker_rate_24h": 3,
    "non_gw_commit_sustained_24h": 10,
}


def _load_thresholds_from_yaml() -> dict[str, int]:
    """从 trae_069_commit_gateway_abuse_thresholds.yaml 加载阈值（P3-1 治本）。

    SSoT 铁律（trae_062）：规则数据真源是 YAML 文件。本函数从 YAML 加载阈值，
    替代原硬编码常量。fail-open：YAML 缺失/解析失败时返回 _DEFAULT_THRESHOLDS
    （不阻断 reconciler，但记录 WARNING）。

    Returns:
        dict[str, int] — 5 维阈值字典，key 为维度名，value 为阈值 int。
    """
    try:
        if not _THRESHOLDS_YAML_PATH.exists():
            logger.warning(
                "P3-1: thresholds YAML not found at %s, using defaults",
                _THRESHOLDS_YAML_PATH,
            )
            return dict(_DEFAULT_THRESHOLDS)
        import yaml
        with _THRESHOLDS_YAML_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        thresholds_section = data.get("thresholds", {})
        result: dict[str, int] = {}
        for dim_name in _DEFAULT_THRESHOLDS:
            dim_config = thresholds_section.get(dim_name, {})
            value = dim_config.get("value", _DEFAULT_THRESHOLDS[dim_name])
            if not isinstance(value, int) or value < 0:
                logger.warning(
                    "P3-1: invalid threshold for %s (%r), using default %d",
                    dim_name, value, _DEFAULT_THRESHOLDS[dim_name],
                )
                value = _DEFAULT_THRESHOLDS[dim_name]
            result[dim_name] = value
        return result
    except Exception as e:  # noqa: BLE001 — YAML 加载失败不阻断 reconciler
        logger.warning(
            "P3-1: failed to load thresholds YAML (%s), using defaults", e,
        )
        return dict(_DEFAULT_THRESHOLDS)


# 启动时加载阈值（fail-open：YAML 缺失时使用默认值）
_THRESHOLD_CONFIG = _load_thresholds_from_yaml()

# 维度1: warn_only 持续低频（24h）——per-hour POST-COMMIT-GUARD 阈值 10/h 抓不到 5/h 持续
_WARN_ONLY_24H_THRESHOLD = _THRESHOLD_CONFIG["warn_only_sustained_24h"]
# 维度2: emergency_commit 滥用（24h）—— P1-4 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）
# 历史：原阈值 5 → bc3cad107c 放松到 30（掩盖滥用）→ R1 回滚到 10（过渡期 2026-07-19~2026-08-02）
# P1-4 治本（2026-07-20）：heartbeat 已落地（#ARCH-HEARTBEAT-001），R1 过渡期不再需要。
# 同时 P1-3 已引入 scenario 过滤，dogfood/test/governance_fix 不计入 24h 计数，
# production 场景的真实 emergency_commit 应 < 5/24h（GitCommitGateway timeout 治本前允许极值）。
# 直接回滚到 5（原值）。
_EMERGENCY_24H_THRESHOLD = _THRESHOLD_CONFIG["emergency_commit_abuse_24h"]
# 维度3: allow_overlap 滥用（7d）——gw_env=1 warn_only 持续 7d = session 注册表 bug
_ALLOW_OVERLAP_7D_THRESHOLD = _THRESHOLD_CONFIG["allow_overlap_abuse_7d"]
# 维度4: forged_gw_marker 伪造率（24h）——任何伪造都 serious，3/天即 critical
_FORGED_24H_THRESHOLD = _THRESHOLD_CONFIG["forged_gw_marker_rate_24h"]
# 维度5: non-GW commit 持续率（24h）——commit_gw_audit violations sum
_NON_GW_24H_THRESHOLD = _THRESHOLD_CONFIG["non_gw_commit_sustained_24h"]

# 时间窗口（秒）
_WINDOW_24H_SECONDS = 24 * 3600
_WINDOW_7D_SECONDS = 7 * 24 * 3600

# git log 超时（秒）
_GIT_LOG_TIMEOUT = 15


def _reports_dir(repo_root: Path) -> Path:
    """reconcile_reports 目录路径：.runtime/reconcile_reports/。"""
    return repo_root / ".runtime" / "reconcile_reports"


def _read_json_reports(repo_root: Path, prefix: str, since_ts: int) -> list[dict]:
    """读取指定前缀的报告文件，返回 timestamp >= since_ts 的报告列表。

    fail-open：目录不存在/读取失败返回空列表（滥用检测降级为无数据不触发）。

    Args:
        repo_root: 仓库根路径。
        prefix: 报告文件名前缀（如 "post_commit_guard" / "commit_gateway_audit"）。
        since_ts: Unix 时间戳，仅返回 timestamp >= since_ts 的报告。

    Returns:
        报告字典列表（每条含解析后的 timestamp 字段）。损坏的 JSON 跳过。
    """
    rdir = _reports_dir(repo_root)
    if not rdir.exists():
        return []
    reports: list[dict] = []
    try:
        for path in rdir.glob(f"{prefix}_*.json"):
            try:
                raw = path.read_text(encoding="utf-8")
                data = json.loads(raw)
            except (OSError, json.JSONDecodeError):
                continue  # 跳过损坏文件
            ts = data.get("timestamp", 0)
            if not isinstance(ts, (int, float)):
                continue
            if ts >= since_ts:
                reports.append(data)
    except OSError as e:
        logger.warning("commit_gateway_abuse_monitor: read %s reports failed: %s", prefix, e)
        return []
    return reports


def _count_emergency_commits(repo_root: Path, since_hours: int) -> int:
    """统计最近 N 小时内 production 场景的 emergency_commit 数（维度2 真源）。

    emergency_commit 是 P2-1 合法逃生通道，但反复使用 = 系统性问题。

    P1-3 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
    按 scenario 过滤——只统计 commit message 含 [SCENARIO:production] 或
    不含 [SCENARIO:...] 标记的 emergency_commit（向后兼容）。
    dogfood / test / governance_fix 场景豁免，避免治本工作污染 24h 滥用计数。

    fail-open：git log 失败返回 0（降级为不触发维度2）。
    """
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since_hours} hours ago", "--format=%B%x1f"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_GIT_LOG_TIMEOUT,
        )
        if result.returncode != 0:
            return 0
        # %x1f (unit separator) 分隔 commit bodies
        count = 0
        for body in result.stdout.split("\x1f"):
            if "[GW:" not in body or "emergency" not in body:
                continue
            # P1-3: scenario 过滤——非 production 场景豁免
            # 向后兼容：无 [SCENARIO:...] 标记视为 production（旧 commit）
            if "[SCENARIO:" in body:
                # 提取 scenario 值
                start = body.find("[SCENARIO:") + len("[SCENARIO:")
                end = body.find("]", start)
                if end > start:
                    scenario = body[start:end].strip()
                    if scenario != "production":
                        continue  # dogfood/test/governance_fix 豁免
            count += 1
        return count
    except (subprocess.TimeoutExpired, Exception) as e:  # noqa: BLE001 — 计数失败不阻断
        logger.warning("commit_gateway_abuse_monitor: count emergency commits failed: %s", e)
        return 0


def _count_allow_overlap_usage(repo_root: Path, since_ts: int) -> int:
    """统计 7d 窗口内真实 allow_overlap=True 提交数（维度3 真源）。

    治本（2026-07-20，sess-23300-20260720092540）：原实现以 post_commit_guard
    warn_only(gw_env=1) 事件反推 allow_overlap 滥用，混入 merge 后 reconciler
    auto-commit 的注册表生命周期伪影（1829/7d 持续误报，结构性必然超阈值）。
    改为读取 gate 层审计 ``.runtime/gate_audit/allow_overlap_usage.jsonl``
    （commit_gate_registry.check_all 在 allow_overlap=True 时落盘），只计真实逃生。

    fail-open：文件缺失/解析失败返回 0（无审计=无证据，不误报）。
    """
    audit_file = repo_root / ".runtime" / "gate_audit" / "allow_overlap_usage.jsonl"
    if not audit_file.exists():
        return 0
    count = 0
    try:
        with audit_file.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if int(rec.get("timestamp", 0)) >= since_ts:
                    count += 1
    except OSError as e:
        logger.warning("commit_gateway_abuse_monitor: read allow_overlap audit failed: %s", e)
        return 0
    return count


def _classify_abuse(
    post_commit_reports: list[dict],
    audit_reports: list[dict],
    emergency_count: int,
    now_ts: int,
    allow_overlap_count: int = 0,
) -> dict:
    """五维滥用分类（纯函数，无副作用，便于单测）。

    Args:
        post_commit_reports: 7d 内的 post_commit_guard 报告列表。
        audit_reports: 24h 内的 commit_gateway_audit 报告列表。
        emergency_count: 24h 内 emergency_commit 数量。
        now_ts: 当前 Unix 时间戳。
        allow_overlap_count: 7d 内真实 allow_overlap=True 提交数（gate 层审计，
            由调用方经 _count_allow_overlap_usage 传入）。

    Returns:
        {
            "dimensions_triggered": list[str],  # 触发的维度名
            "details": list[str],               # 每个维度的告警消息
            "metrics": dict,                    # 所有维度的原始数值（供报告落盘）
        }
    """
    # 计算各窗口的 since_ts
    since_24h = now_ts - _WINDOW_24H_SECONDS

    # === 维度1: warn_only 持续低频（24h）===
    warn_only_24h = sum(
        1 for r in post_commit_reports
        if r.get("timestamp", 0) >= since_24h
        and r.get("action") == "warn_only"
        and r.get("violation") == "unregistered_session_id"
    )

    # === 维度3: allow_overlap 滥用（7d）—— gate 层审计真实计数（由调用方传入）===
    allow_overlap_7d = allow_overlap_count

    # === 维度4: forged_gw_marker 伪造率（24h）===
    forged_24h = sum(
        1 for r in post_commit_reports
        if r.get("timestamp", 0) >= since_24h
        and r.get("violation") == "forged_gw_marker"
    )

    # === 维度5: non-GW commit 持续率（24h）——按 commit hash distinct 计数 ===
    # P3 (2026-07-20): 治本——原 sum(violations_count) 会重复计数（audit_window=20,
    # 多个报告覆盖同一 commit,导致 non_gw_24h 膨胀）。改为收集 violations[].hash
    # 去重后计数,精确反映 24h 内实际 non-GW commit 数。
    non_gw_hashes: set[str] = set()
    for r in audit_reports:
        if r.get("timestamp", 0) >= since_24h:
            vlist = r.get("violations", [])
            if isinstance(vlist, list):
                for v in vlist:
                    if isinstance(v, dict):
                        h = v.get("hash")
                        if h:
                            non_gw_hashes.add(h)
    non_gw_24h = len(non_gw_hashes)

    # === 维度2: emergency_commit 滥用（24h）—— 由调用方传入 emergency_count ===

    dimensions_triggered: list[str] = []
    details: list[str] = []

    if warn_only_24h > _WARN_ONLY_24H_THRESHOLD:
        dimensions_triggered.append("warn_only_sustained_24h")
        details.append(
            f"warn_only 持续低频: {warn_only_24h}/24h > {_WARN_ONLY_24H_THRESHOLD} 阈值"
            f"——POST-COMMIT-GUARD per-hour 阈值抓不到的持续逃生通道滥用"
        )

    if emergency_count > _EMERGENCY_24H_THRESHOLD:
        dimensions_triggered.append("emergency_commit_abuse_24h")
        details.append(
            f"emergency_commit 滥用: {emergency_count}/24h > {_EMERGENCY_24H_THRESHOLD} 阈值"
            f"——逃生通道日常化（应为罕见），排查 session_worktree_merge 跨进程失效根因"
        )

    if allow_overlap_7d > _ALLOW_OVERLAP_7D_THRESHOLD:
        dimensions_triggered.append("allow_overlap_abuse_7d")
        details.append(
            f"allow_overlap 滥用: {allow_overlap_7d}/7d > {_ALLOW_OVERLAP_7D_THRESHOLD} 阈值"
            f"——逃生通道日常化（gate 层审计真实计数），排查为何频繁 HELD-OVERLAP 撞车"
        )

    if forged_24h > _FORGED_24H_THRESHOLD:
        dimensions_triggered.append("forged_gw_marker_rate_24h")
        details.append(
            f"forged_gw_marker 伪造率: {forged_24h}/24h > {_FORGED_24H_THRESHOLD} 阈值"
            f"——严重治理失效（任何伪造都是 intentional），需立即排查"
        )

    if non_gw_24h > _NON_GW_24H_THRESHOLD:
        dimensions_triggered.append("non_gw_commit_sustained_24h")
        details.append(
            f"non-GW commit 持续率: {non_gw_24h}/24h > {_NON_GW_24H_THRESHOLD} 阈值"
            f"——持续绕过 GitCommitGateway，排查 --no-verify 滥用或 commit-tree 绕过"
        )

    return {
        "dimensions_triggered": dimensions_triggered,
        "details": details,
        "metrics": {
            "warn_only_24h": warn_only_24h,
            "emergency_commit_24h": emergency_count,
            "allow_overlap_7d": allow_overlap_7d,
            "forged_gw_marker_24h": forged_24h,
            "non_gw_commit_24h": non_gw_24h,
            "thresholds": {
                "warn_only_24h": _WARN_ONLY_24H_THRESHOLD,
                "emergency_commit_24h": _EMERGENCY_24H_THRESHOLD,
                "allow_overlap_7d": _ALLOW_OVERLAP_7D_THRESHOLD,
                "forged_gw_marker_24h": _FORGED_24H_THRESHOLD,
                "non_gw_commit_24h": _NON_GW_24H_THRESHOLD,
            },
        },
    }


def make_commit_gateway_abuse_monitor_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-COMMIT-GW-ABUSE-MONITOR post-commit 持续滥用监控 reconciler。

    Args:
        gateway: GitCommitGateway 实例（仅用其 project_root）。

    Returns:
        ReconcilerSpec(gate_id=_GATE_ID, priority=_PRIORITY)。
        trigger 永远返回 True（任何 commit 都触发滥用监控——全局关注）。
    """
    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        # 任何 commit 都触发——滥用监控是全局关注，不限文件类型
        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        try:
            now_ts = int(time.time())
            since_24h = now_ts - _WINDOW_24H_SECONDS
            since_7d = now_ts - _WINDOW_7D_SECONDS

            # 1. 读取 7d 内的 post_commit_guard 报告（覆盖维度1/3/4）
            post_commit_reports = _read_json_reports(
                project_root, "post_commit_guard", since_7d,
            )

            # 2. 读取 24h 内的 commit_gateway_audit 报告（覆盖维度5）
            audit_reports = _read_json_reports(
                project_root, "commit_gateway_audit", since_24h,
            )

            # 3. 统计 24h 内 emergency_commit 数量（覆盖维度2）
            emergency_count = _count_emergency_commits(project_root, 24)

            # 3.5 统计 7d 内真实 allow_overlap=True 使用次数（覆盖维度3 真源）
            # P1-1 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
            # 原实现未调用 _count_allow_overlap_usage，allow_overlap_count 默认 0，
            # 导致维度3 永远不触发（实际误报来自 L214 之前的 warn_only+gw_env=1 反推）。
            # 现改为读取 gate 层审计 .runtime/gate_audit/allow_overlap_usage.jsonl
            allow_overlap_count = _count_allow_overlap_usage(project_root, since_7d)

            # 4. 五维分类
            classification = _classify_abuse(
                post_commit_reports, audit_reports, emergency_count, now_ts,
                allow_overlap_count=allow_overlap_count,
            )

            triggered = classification["dimensions_triggered"]
            details = classification["details"]
            metrics = classification["metrics"]

            # 5. 落盘审计报告（无论是否触发滥用都记录，供趋势追踪）
            report = {
                "gate_id": _GATE_ID,
                "session_id": session_id,
                "dimensions_triggered": triggered,
                "metrics": metrics,
                "details": details,
                "post_commit_reports_read": len(post_commit_reports),
                "audit_reports_read": len(audit_reports),
            }
            report_path, write_err = _write_reconcile_report(
                project_root, "commit_gateway_abuse_monitor", report,
            )
            if write_err:
                return ReconcileResult(
                    action="warn",
                    detail=f"abuse monitor done but report write failed: {write_err}",
                    gate_id=_GATE_ID,
                )

            # 6. 判定 action
            if not triggered:
                return ReconcileResult(
                    action="clean",
                    detail=(
                        f"abuse monitor clean: warn_only={metrics['warn_only_24h']}/24h, "
                        f"emergency={metrics['emergency_commit_24h']}/24h, "
                        f"allow_overlap={metrics['allow_overlap_7d']}/7d, "
                        f"forged={metrics['forged_gw_marker_24h']}/24h, "
                        f"non_gw={metrics['non_gw_commit_24h']}/24h, "
                        f"report={report_path.name}"
                    ),
                    gate_id=_GATE_ID,
                )

            # forged_gw_marker 触发 OR 3+ 维度 → critical_warn（横幅强制 AI 看到）
            forged_triggered = "forged_gw_marker_rate_24h" in triggered
            if forged_triggered or len(triggered) >= 3:
                return ReconcileResult(
                    action="critical_warn",
                    detail=(
                        f"ABUSE DETECTED ({len(triggered)} dimensions): "
                        + "; ".join(details)
                        + f" (report={report_path.name})"
                    ),
                    gate_id=_GATE_ID,
                )

            # 1-2 维度 → warn
            return ReconcileResult(
                action="warn",
                detail=(
                    f"abuse monitor warn ({len(triggered)} dimensions): "
                    + "; ".join(details)
                    + f" (report={report_path.name})"
                ),
                gate_id=_GATE_ID,
            )
        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常
            logger.warning("commit_gateway_abuse_monitor reconciler failed: %s", e)
            return ReconcileResult(
                action="warn",
                detail=f"monitor failed: {e}",
                gate_id=_GATE_ID,
            )

    return ReconcilerSpec(
        gate_id=_GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=_PRIORITY,
    )
