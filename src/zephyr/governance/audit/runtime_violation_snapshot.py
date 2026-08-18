# [BLUEPRINT] MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT | docs/03_modules/_domain_governance/blueprint.md | §runtime-violation-snapshot
# [MODULE] zephyr.governance.audit.runtime_violation_snapshot
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec)
# [CONSUMERS] zephyr.governance.audit.runtime_violation_snapshot_reconciler ; scripts.governance.architecture_health_dashboard
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] snapshot 是 trae_060 §5 evidence 的 live 替代；baseline 是 frozen 历史快照；M20 drift = sum(|detected - claimed| > 0 的类别数)；reconciler 事件触发（post-commit），非 cron/manual；fail-open（检测器失败降级为 error 字段不中断其余）
# [MODIFY-GUARD] BASELINE_FILE 路径；_CATEGORY_TO_METRIC 映射表
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] generate_snapshot 永不抛异常——单检测器失败降级为 error 字段；返回 dict 始终含 violations 字段
# [TESTS] tests/governance/audit/test_runtime_violation_snapshot.py
# [A_module] module_id=MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable  # noqa: blueprint-amodule-cross-check [BLUEPRINT]==[A_module] same module
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)
"""

runtime_violation_snapshot.py — trae_060 §5 evidence 运行时快照（#ARCH-GOV-CONVERGENCE-META Phase 3.4b）。

病根1 治本（架构债务 §三 病根1）
------------------------------
trae_060 §5 "禁止清单（汇总与evidence）" 把"违规清单"（事实快照）当"规则本身"
写入 frozen YAML。规则应是判断标准（"禁止硬编码"），违规清单是事实快照
（"今天发现64处"）。把事实快照冻结=让规则随时间脱节。

证据（docs/_working/trae_060_s5_evidence_audit.md）：
  - §5 声称 23 处违规，实际为 0（4 处举例文件 3 个已删除 1 个已修复）
  - §5 声称 9 词表，实际为 27

治本方案（三要素）
------------------
1. **抽出**：把 §5 prohibitions 的历史计数移到 ``baseline_2026_06_26.yaml``
   （frozen 历史快照，不再更新）
2. **live 替代**：本模块生成 live 快照（``data/runtime_violation_snapshot/latest.json``），
   由 post-commit reconciler 事件触发自动更新
3. **可发现**：M20 指标（architecture_health_dashboard）报告 baseline vs live 漂移数

设计裁定
--------
- **复用优先**（trae_060 §2 原则①）：不重新实现检测器，subprocess 调用
  ``architecture_health_dashboard.py --json --metric M01 M02 M03 M10`` 复用现有 4 个指标
- **事件触发**（trae_060 §3 原则②）：reconciler 是 post-commit 事件触发，非 cron/manual
- **第一性原理**（trae_060 §4 原则③）：质疑"违规清单是否该 frozen"——答案是否，
  事实快照必须 live，规则才 frozen

snapshot 结构
-------------
::

    {
      "generated_at": "2026-07-19T14:00:00Z",
      "generated_by": "GATE-RUNTIME-VIOLATION-SNAPSHOT",
      "session_id": "sess-xxx",
      "commit_sha": "abc123",
      "baseline_file": "data/runtime_violation_snapshot/baseline_2026_06_26.yaml",
      "trae_rule_id": "TRAE-060",
      "trae_rule_version": "1.0.1",
      "violations": [
        {
          "category": "vocab_hardcode",
          "rule": "禁止硬编码词表合法值...",
          "claimed_count": 64,
          "detected_count": 0,
          "drift": -64,            # detected - claimed（负=已修复，正=新增）
          "detector_metric_id": "M01",
          "detector_error": "",
          "details": [...]
        },
        ...
      ],
      "summary": {
        "total_detected": 45,
        "total_claimed": 109,
        "drift_count": 4,          # |drift| > 0 的类别数（M20 报告值）
        "fresh": true              # generated_at 在 24h 内
      }
    }

Usage
-----
::

    from zephyr.governance.audit.runtime_violation_snapshot import (
        generate_snapshot, save_snapshot, load_snapshot, compute_drift_count,
    )

    # 生成 live 快照（reconciler 调用）
    snapshot = generate_snapshot(project_root, session_id="sess-xxx", commit_sha="abc")
    save_snapshot(snapshot, project_root)

    # M20 指标调用
    snapshot = load_snapshot(project_root)
    drift_count = compute_drift_count(snapshot)  # 0 = 无漂移

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: baseline 冻结历史快照 YAML
#   fields: data/runtime_violation_snapshot/baseline_2026_06_26.yaml 各类别 claimed_count + rule + claim_text
#   code: _BASELINE_REL L115 / _load_baseline L175
# - id: I2
#   name: dashboard 指标 live 计数 subprocess 数据
#   fields: architecture_health_dashboard.py --json --metric M01 M02 M03 M10 的 count/details/error
#   code: _run_dashboard L144
# 层: 算法
# - id: A1
#   name_zh: ① live 违规快照生成
#   name_en: generate_snapshot
#   intro: 对 4 个违规类别逐一对账：detected（dashboard live）- claimed（baseline 冻结）= drift
#   desc: 加载 baseline → subprocess 调 dashboard（120s 超时 fail-open）→ 按 _CATEGORY_TO_METRIC 映射（vocab_hardcode→M01 / manual_trigger→M02 / mergeable_clusters→M03 / time_trigger→M10）逐类算 drift=detected-claimed，drift≠0 累计 drift_count；检测器失败降级 error 字段
#   inputs: I1 I2
#   outputs: snapshot dict（violations + summary）
#   invariant: 永不抛异常，返回 dict 始终含 violations
# - id: A2
#   name_zh: ② 快照持久化双写
#   name_en: save_snapshot
#   intro: 快照写 latest.json 同时按 UTC 时间戳归档一份历史
#   desc: latest.json 覆盖写 + snapshot_<yyyyMMddTHHMMSSZ>.json 归档；归档失败仅 warn
#   inputs: A1
#   outputs: latest.json Path + 归档文件
# - id: A3
#   name_zh: ③ 漂移类别数计算
#   name_en: compute_drift_count
#   intro: 从快照取 drift_count（|drift|>0 的类别数），即 M20 指标报告值
#   desc: 优先读 summary.drift_count；缺失则从 violations 重算兜底；空快照返回 0
#   inputs: A1
#   outputs: drift_count int（0=无漂移）
# 层: 输出
# - id: O1
#   name_zh: live 违规快照文件
#   name_en: latest.json + 时间戳归档
#   intro: data/runtime_violation_snapshot/ 下的当前快照与历史归档，trae_060 §5 的 live 替代
#   downstream: runtime_violation_snapshot_reconciler（[CONSUMERS] 同包 reconciler 调用生成）
# - id: O2
#   name_zh: M20 漂移指标值
#   name_en: drift_count
#   intro: baseline vs live 漂移类别数，0=完全一致，>0=存在漂移
#   downstream: architecture_health_dashboard M20 指标（[CONSUMERS]）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A1 --> A3
# A2 --> O1
# A3 --> O2
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from zephyr.shared.infra.process_pool import run_subprocess_hidden

logger = logging.getLogger(__name__)


# ── 路径常量 ──────────────────────────────────────────────────────────────

# 相对 project_root 的路径
_BASELINE_REL = "data/runtime_violation_snapshot/baseline_2026_06_26.yaml"
_LATEST_REL = "data/runtime_violation_snapshot/latest.json"
_ARCHIVE_DIR_REL = "data/runtime_violation_snapshot"
_DASHBOARD_REL = "scripts/governance/architecture_health_dashboard.py"

# 类别 → 检测器 metric_id 映射（与 baseline YAML 一致）
# 顺序固定：vocab_hardcode → time_trigger → manual_trigger → mergeable_clusters
_CATEGORY_TO_METRIC: dict[str, str] = {
    "vocab_hardcode": "M01",
    "manual_trigger": "M02",
    "mergeable_clusters": "M03",
    "time_trigger": "M10",
}

# 快照新鲜度阈值（24h，对标 M15 depgraph_freshness）
_FRESH_SECONDS = 24 * 3600


# ── 工具函数 ──────────────────────────────────────────────────────────────


def _get_project_root(project_root: Path | str | None = None) -> Path:
    """获取 project_root，默认从 __file__ 推导。"""
    if project_root is not None:
        return Path(project_root) if not isinstance(project_root, Path) else project_root
    # 从 __file__ 推导：src/zephyr/governance/audit/runtime_violation_snapshot.py
    return Path(__file__).resolve().parents[4]


def _run_dashboard(
    project_root: Path, metric_ids: list[str], timeout: int = 120
) -> tuple[int, str, str]:
    """subprocess 调用 architecture_health_dashboard.py --json --metric <ids>。

    Returns:
        (returncode, stdout, stderr)
    """
    dashboard = project_root / _DASHBOARD_REL
    if not dashboard.is_file():
        return -1, "", f"dashboard not found: {dashboard}"
    cmd = [sys.executable, str(dashboard), "--json", "--metric", *metric_ids]
    child_env = {**os.environ, "PYTHONPATH": str(project_root / "src")}
    try:
        result = run_subprocess_hidden(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(project_root),
            env=child_env,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"dashboard timeout after {timeout}s"
    except Exception as e:  # noqa: BLE001 — fail-open
        return -2, "", f"dashboard run failed: {e}"


def _load_baseline(project_root: Path) -> dict:
    """加载 baseline YAML。fail-open：文件不存在返回空 dict。"""
    baseline_path = project_root / _BASELINE_REL
    if not baseline_path.is_file():
        logger.warning("baseline file not found: %s", baseline_path)
        return {}
    try:
        data = yaml.safe_load(baseline_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except yaml.YAMLError as e:
        logger.warning("baseline yaml parse failed: %s", e)
        return {}


def _parse_dashboard_metrics(stdout: str) -> dict[str, dict]:
    """解析 dashboard --json 输出，返回 {metric_id: metric_dict}。

    fail-open：解析失败返回空 dict。
    """
    if not stdout.strip():
        return {}
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        logger.warning("dashboard json parse failed: %s", e)
        return {}
    if not isinstance(data, dict):
        return {}
    metrics_list = data.get("metrics", [])
    if not isinstance(metrics_list, list):
        return {}
    result: dict[str, dict] = {}
    for m in metrics_list:
        if isinstance(m, dict) and "metric_id" in m:
            result[m["metric_id"]] = m
    return result


# ── 核心函数 ──────────────────────────────────────────────────────────────


def generate_snapshot(
    project_root: Path | str | None = None,
    session_id: str = "",
    commit_sha: str = "",
) -> dict:
    """生成 live 违规快照。

    流程：
      1. 加载 baseline（frozen 历史计数）
      2. subprocess 调 dashboard --json --metric M01 M02 M03 M10
      3. 对每个类别：detected_count = dashboard 计数，drift = detected - claimed
      4. 返回 snapshot dict

    Args:
        project_root: 项目根目录，None 则从 __file__ 推导。
        session_id: 触发本次快照的 session_id（可空）。
        commit_sha: 触发本次快照的 commit sha（可空）。

    Returns:
        snapshot dict（结构见模块 docstring）。永不抛异常。
    """
    root = _get_project_root(project_root)
    baseline = _load_baseline(root)
    baseline_violations = baseline.get("violations", {}) if isinstance(baseline.get("violations"), dict) else {}

    # 调 dashboard 获取 live 计数（fail-open：异常降级为空 metrics）
    metric_ids = list(_CATEGORY_TO_METRIC.values())
    try:
        code, out, err = _run_dashboard(root, metric_ids, timeout=120)
    except Exception as e:  # noqa: BLE001 — fail-open，generate_snapshot 永不抛异常
        logger.warning("dashboard run raised: %s", e)
        code, out, err = -2, "", f"dashboard run raised: {e}"
    if code != 0:
        logger.warning("dashboard run failed (code=%s): %s", code, err[:200])
    metrics_by_id = _parse_dashboard_metrics(out) if code == 0 else {}

    now_iso = datetime.now(timezone.utc).isoformat()
    trae_rule_id = baseline.get("trae_rule_id", "TRAE-060")
    trae_rule_version = baseline.get("trae_rule_version", "unknown")

    violations: list[dict] = []
    total_detected = 0
    total_claimed = 0
    drift_count = 0

    for category, metric_id in _CATEGORY_TO_METRIC.items():
        baseline_entry = baseline_violations.get(category, {})
        claimed_count = int(baseline_entry.get("claimed_count", 0))
        rule_text = baseline_entry.get("rule", "")
        claim_text = baseline_entry.get("claim_text", "")

        metric_data = metrics_by_id.get(metric_id, {})
        detected_count = int(metric_data.get("count", 0)) if metric_data else 0
        detector_error = metric_data.get("error", "") if metric_data else f"metric {metric_id} not in dashboard output"
        details = metric_data.get("details", []) if metric_data else []

        drift = detected_count - claimed_count
        if drift != 0:
            drift_count += 1

        total_detected += detected_count
        total_claimed += claimed_count

        violations.append({
            "category": category,
            "rule": rule_text,
            "claimed_count": claimed_count,
            "claim_text": claim_text,
            "detected_count": detected_count,
            "drift": drift,
            "detector_metric_id": metric_id,
            "detector_metric_name": baseline_entry.get("detector_metric_name", ""),
            "detector_error": detector_error,
            "details": details[:20] if isinstance(details, list) else [],
        })

    return {
        "generated_at": now_iso,
        "generated_by": "GATE-RUNTIME-VIOLATION-SNAPSHOT",
        "session_id": session_id,
        "commit_sha": commit_sha,
        "baseline_file": _BASELINE_REL,
        "trae_rule_id": trae_rule_id,
        "trae_rule_version": trae_rule_version,
        "violations": violations,
        "summary": {
            "total_detected": total_detected,
            "total_claimed": total_claimed,
            "drift_count": drift_count,
            "fresh": True,  # 刚生成，必 fresh
        },
    }


def save_snapshot(snapshot: dict, project_root: Path | str | None = None) -> Path:
    """保存快照到 ``data/runtime_violation_snapshot/latest.json`` + 时间戳归档。

    Args:
        snapshot: generate_snapshot 返回的 dict。
        project_root: 项目根目录。

    Returns:
        latest.json 的 Path。
    """
    root = _get_project_root(project_root)
    archive_dir = root / _ARCHIVE_DIR_REL
    archive_dir.mkdir(parents=True, exist_ok=True)

    latest_path = root / _LATEST_REL
    latest_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=False),
        encoding="utf-8",
    )

    # 时间戳归档（对标 architecture_health/dashboard_<ts>.json 模式）
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive_path = archive_dir / f"snapshot_{ts}.json"
    try:
        archive_path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=False),
            encoding="utf-8",
        )
    except OSError as e:
        logger.warning("archive snapshot save failed: %s", e)

    return latest_path


def load_snapshot(project_root: Path | str | None = None) -> dict:
    """加载 latest.json。fail-open：文件不存在/解析失败返回空 dict。"""
    root = _get_project_root(project_root)
    latest_path = root / _LATEST_REL
    if not latest_path.is_file():
        return {}
    try:
        data = json.loads(latest_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("snapshot load failed: %s", e)
        return {}


def compute_drift_count(snapshot: dict) -> int:
    """计算漂移类别数（|drift| > 0 的类别数）。

    M20 指标的核心计算：0 = 完全无漂移，>0 = 存在漂移。

    Args:
        snapshot: generate_snapshot 返回的 dict，或 load_snapshot 的结果。

    Returns:
        漂移类别数。snapshot 为空返回 0。
    """
    if not snapshot:
        return 0
    summary = snapshot.get("summary", {})
    if isinstance(summary, dict) and "drift_count" in summary:
        return int(summary.get("drift_count", 0))
    # 兜底：从 violations 重新计算
    violations = snapshot.get("violations", [])
    if not isinstance(violations, list):
        return 0
    return sum(1 for v in violations if isinstance(v, dict) and v.get("drift", 0) != 0)


def is_snapshot_fresh(snapshot: dict, max_age_seconds: int = _FRESH_SECONDS) -> bool:
    """检查快照是否新鲜（generated_at 在 max_age_seconds 内）。

    Args:
        snapshot: generate_snapshot 返回的 dict。
        max_age_seconds: 新鲜度阈值，默认 24h。

    Returns:
        True 如果 generated_at 在阈值内。snapshot 为空或无 generated_at 返回 False。
    """
    if not snapshot:
        return False
    generated_at = snapshot.get("generated_at")
    if not generated_at:
        return False
    try:
        gen_time = datetime.fromisoformat(generated_at)
        if gen_time.tzinfo is None:
            gen_time = gen_time.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - gen_time).total_seconds()
        return 0 <= age <= max_age_seconds
    except (ValueError, TypeError):
        return False


def compare_baseline_with_live(project_root: Path | str | None = None) -> dict:
    """对比 baseline 与 live 快照，返回详细对比结果（供 M20 调用）。

    Returns:
        dict with keys:
        - drift_count: 漂移类别数
        - fresh: bool
        - violations: list of {category, claimed, detected, drift, fresh_detail}
        - error: str (空字符串表示无错误)
    """
    root = _get_project_root(project_root)
    snapshot = load_snapshot(root)

    if not snapshot:
        return {
            "drift_count": 0,
            "fresh": False,
            "violations": [],
            "error": "snapshot not found or empty",
        }

    fresh = is_snapshot_fresh(snapshot)
    drift_count = compute_drift_count(snapshot)

    violations_detail = []
    for v in snapshot.get("violations", []):
        if not isinstance(v, dict):
            continue
        violations_detail.append({
            "category": v.get("category", ""),
            "claimed": v.get("claimed_count", 0),
            "detected": v.get("detected_count", 0),
            "drift": v.get("drift", 0),
            "detector_error": v.get("detector_error", ""),
        })

    return {
        "drift_count": drift_count,
        "fresh": fresh,
        "violations": violations_detail,
        "error": "" if fresh else "snapshot stale (generated_at > 24h)",
    }

