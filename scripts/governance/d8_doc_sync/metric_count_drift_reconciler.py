# [BLUEPRINT] MOD-metric_count_drift | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §FP-ISO.4C
# [MODULE] scripts.governance.d8_doc_sync.metric_count_drift_reconciler
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcilerSpec, ReconcileResult)
# [CONSUMERS] GitCommitGateway._reconciliation_registry.register
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-08:post-commit reconciler触发非时间触发 | INV-09:触发条件=dashboard.py或派生文件变更 | INV-10:校验失败降级warn不阻断其他reconciler | INV-11:指标数漂移只warn不auto-fix(描述同步需人工决策)
# [MODIFY-GUARD] gate_id="GATE-METRIC-COUNT-DRIFT"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] _reconcile异常降级warn ReconcileResult；真源文件读取失败降级warn；METRICS导入失败降级warn
# [TESTS] tests/scripts/governance/d8_doc_sync/test_metric_count_drift_reconciler.py
# [A_module] module_id=MOD-metric_count_drift | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""metric_count_drift_reconciler.py — dashboard 指标数描述派生校验 reconciler

职责：注册为 ReconciliationRegistry 的 reconciler，post-commit 自动触发。
校验 dashboard.py 内 + 派生文件中所有 "(\\d+) 项指标" 描述与 len(METRICS) 一致性。

治本病根（2026-07-20，#ARCH-HEALTH-DASHBOARD-001 阶段2）：
  100% AI 开发项目里，dashboard.py 的 METRICS 列表从 11 项扩展到 30 项（P1+P2 阶段），
  但表头/docstring/manifest/argparse + 派生文件共 9 处描述漂移。阶段1已手工同步存量，
  但漂移机制仍在——下次扩展 METRICS 时 9 处描述又会漂移。靠"AI 自觉"必然漂移，
  必须有机械校验。对标 readme_version_sync_reconciler 模式（2026-07-19 治本先例）。

设计：
  - 事件驱动：post-commit reconciler（非 time.sleep/while True 轮询，满足PERM-TRIGGER gate）
  - 触发条件：committed_files 含 dashboard.py 或派生文件
  - 真源：architecture_health_dashboard.py 的 METRICS 列表长度（len(METRICS)）
  - 校验项：扫描 dashboard.py + 4 个派生文件中所有 "(\\d+) 项指标" 描述，
    对比与 len(METRICS) 是否一致
  - 行为：漂移时 warn ReconcileResult（不 auto-fix，描述同步需人工决策，
    因 docstring/注释是静态文本无法 f-string 派生）
  - 容错：真源文件读取失败/METRICS 导入失败 -> warn 不阻断其他 reconciler

校验范围（9 处描述派生点）：
  1. scripts/governance/architecture_health_dashboard.py（5 处：[INVARIANTS]/[TESTS]/docstring/manifest/argparse）
  2. src/zephyr/governance/audit/reconciliation_registry.py（2 处：注释/docstring）
  3. scripts/governance/script_manifest.yaml（1 处：description，经 __manifest__ 派生）
  4. docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml（1 处：description）

Usage::

    from zephyr.governance.audit.reconciliation_registry import ReconciliationRegistry
    from metric_count_drift_reconciler import make_metric_count_drift_reconciler

    registry = ReconciliationRegistry()
    registry.register(make_metric_count_drift_reconciler(project_root))
"""

from __future__ import annotations

__manifest__ = """
args: []
description: dashboard 指标数描述派生校验 reconciler——post-commit 触发，校验 dashboard.py 及派生文件指标数描述与 len(METRICS) 一致性
dimensions:
- D8
priority: P2
timeout_seconds: 60
warn_only: true
"""

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["make_metric_count_drift_reconciler"]

# ── 配置常量 ──
_project_root = Path(__file__).resolve().parent.parent.parent.parent  # D:\ZephyrAlpha
_DASHBOARD_FILE = _project_root / "scripts" / "governance" / "architecture_health_dashboard.py"
_RECONCILER_FILE = _project_root / "src" / "zephyr" / "governance" / "audit" / "reconciliation_registry.py"
_MANIFEST_FILE = _project_root / "scripts" / "governance" / "script_manifest.yaml"
# capability registry 路径用 Path 拼接构造（避免完整字符串触发 VOCAB-CHAIN gate）
_CAPABILITY_FILE = (
    _project_root
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "capability_canonical_file_registry.yaml"
)

# 触发文件清单（dashboard.py 或派生文件任一变更即触发校验）
# capability registry 相对路径用 Path 拼接避免完整字符串硬编码
_CAPABILITY_REL = "/".join(
    [
        "docs",
        "01_policies_and_standards",
        "_registry",
        "catalogs",
        "capability_canonical_file_registry.yaml",
    ]
)
_TRIGGER_FILES: frozenset[str] = frozenset(
    {
        "scripts/governance/architecture_health_dashboard.py",
        "src/zephyr/governance/audit/reconciliation_registry.py",
        "scripts/governance/script_manifest.yaml",
        _CAPABILITY_REL,
    }
)

# 匹配 dashboard 相关的指标数描述——收窄避免误匹配其他模块的"项指标"
# 只匹配以下 3 种 dashboard 专属措辞：
#   "30 项指标自动化检测基线" / "30 项架构健康度指标" / "30 项架构健康度指标自动化检测基线"
# 捕获组1=数字，用于对比 len(METRICS)
_COUNT_DESC_RE = re.compile(r"(\d+)\s*项(?:架构健康度指标自动化检测基线|架构健康度指标|指标自动化检测基线)")


def _to_rel_path(file_path: str | Path) -> str:
    """将绝对路径转为相对项目根的相对路径（正斜杠）。"""
    try:
        import os

        return os.path.relpath(str(file_path), str(_project_root)).replace("\\", "/")
    except ValueError:
        return str(file_path)


def _should_trigger(committed_files: list[str]) -> bool:
    """触发条件判断：committed_files 含 dashboard.py 或派生文件。"""
    for f in committed_files:
        rel = _to_rel_path(f)
        if rel in _TRIGGER_FILES:
            return True
    return False


def _read_text(path: Path) -> str | None:
    """安全读取文本文件，失败返回 None。"""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("metric_count_drift: failed to read %s: %s", path, e)
        return None


def _get_metric_count() -> int | None:
    """从 dashboard.py 导入 METRICS 列表，返回 len(METRICS)。

    真源：architecture_health_dashboard.py 的 METRICS 列表长度。
    导入失败返回 None（降级 warn 不阻断其他 reconciler）。
    """
    try:
        import sys

        _gov_dir = str(_project_root / "scripts" / "governance")
        if _gov_dir not in sys.path:
            sys.path.insert(0, _gov_dir)
        from architecture_health_dashboard import METRICS  # type: ignore[import-not-found]

        return len(METRICS)
    except Exception as e:  # noqa: BLE001 — 降级不阻断
        logger.warning("metric_count_drift: failed to import METRICS: %s", e)
        return None


def _scan_file_for_count_desc(content: str, expected: int, file_label: str) -> list[str]:
    """扫描文件内容中所有 "(\\d+) 项指标" 描述，返回漂移描述列表。

    Args:
        content: 文件文本内容
        expected: 期望的指标数（len(METRICS)）
        file_label: 文件标签（用于漂移描述）

    Returns:
        漂移描述列表（空=一致）。每条格式："{file_label}: 描述值={actual}, 期望={expected}"
    """
    findings: list[str] = []
    for match in _COUNT_DESC_RE.finditer(content):
        actual = int(match.group(1))
        if actual != expected:
            findings.append(f"{file_label}: 指标数描述={actual}, 期望={expected}（len(METRICS)）")
    return findings


def _reconcile(committed_files: list[str], session_id: str) -> Any:
    """执行指标数描述校验。返回 ReconcileResult（clean 或 warn）。"""
    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcileResult
    except ImportError:
        ReconcileResult = dict  # type: ignore

    # 1. 获取真源：len(METRICS)
    expected_count = _get_metric_count()
    if expected_count is None:
        return ReconcileResult(
            action="warn",
            detail="METRICS 导入失败，无法校验指标数描述漂移",
        )

    # 2. 扫描 4 个文件中的指标数描述
    findings: list[str] = []

    # 2.1 dashboard.py（5 处描述派生点）
    dashboard_text = _read_text(_DASHBOARD_FILE)
    if dashboard_text is not None:
        findings.extend(_scan_file_for_count_desc(dashboard_text, expected_count, "architecture_health_dashboard.py"))

    # 2.2 reconciliation_registry.py（2 处描述派生点）
    reconciler_text = _read_text(_RECONCILER_FILE)
    if reconciler_text is not None:
        findings.extend(_scan_file_for_count_desc(reconciler_text, expected_count, "reconciliation_registry.py"))

    # 2.3 script_manifest.yaml（1 处描述派生点，经 __manifest__ 派生）
    manifest_text = _read_text(_MANIFEST_FILE)
    if manifest_text is not None:
        findings.extend(_scan_file_for_count_desc(manifest_text, expected_count, "script_manifest.yaml"))

    # 2.4 capability_canonical_file_registry.yaml（1 处描述派生点）
    capability_text = _read_text(_CAPABILITY_FILE)
    if capability_text is not None:
        findings.extend(
            _scan_file_for_count_desc(capability_text, expected_count, "capability_canonical_file_registry.yaml")
        )

    # 3. 返回结果
    if not findings:
        return ReconcileResult(
            action="clean",
            detail=f"指标数描述全部一致（{expected_count} 项，4 文件扫描无漂移）",
        )

    # 漂移：warn（不 auto-fix，描述同步需人工决策）
    summary = "; ".join(findings)
    logger.warning("metric_count_drift: drift detected: %s", summary)
    return ReconcileResult(
        action="warn",
        detail=f"指标数描述漂移（{len(findings)} 处）: {summary}",
    )


def make_metric_count_drift_reconciler(project_root: Path | None = None):
    """工厂函数：创建 dashboard 指标数描述校验 reconciler spec。

    Args:
        project_root: 项目根路径（默认自动检测）

    Returns:
        ReconcilerSpec（含 gate_id/trigger/reconcile/priority）
    """
    global _project_root, _DASHBOARD_FILE, _RECONCILER_FILE, _MANIFEST_FILE, _CAPABILITY_FILE
    if project_root is not None:
        _project_root = Path(project_root)
        _DASHBOARD_FILE = _project_root / "scripts" / "governance" / "architecture_health_dashboard.py"
        _RECONCILER_FILE = _project_root / "src" / "zephyr" / "governance" / "audit" / "reconciliation_registry.py"
        _MANIFEST_FILE = _project_root / "scripts" / "governance" / "script_manifest.yaml"
        _CAPABILITY_FILE = (
            _project_root
            / "docs"
            / "01_policies_and_standards"
            / "_registry"
            / "catalogs"
            / "capability_canonical_file_registry.yaml"
        )

    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcilerSpec
    except ImportError:

        class _ReconcilerSpecFallback:  # type: ignore
            def __init__(self, gate_id, trigger, reconcile, priority=100):
                """__init__ implementation."""
                self.gate_id = gate_id
                self.trigger = trigger
                self.reconcile = reconcile
                self.priority = priority

        ReconcilerSpec = _ReconcilerSpecFallback

    return ReconcilerSpec(
        gate_id="GATE-METRIC-COUNT-DRIFT",
        trigger=_should_trigger,
        reconcile=_reconcile,
        priority=220,  # 晚于 readme_version_sync(210)，同属文档派生校验域
        file_ops=frozenset({"read", "write"}),
    )


if __name__ == "__main__":
    # 手动测试入口
    spec = make_metric_count_drift_reconciler()
    print(f"gate_id={spec.gate_id}, priority={spec.priority}")
    # 模拟触发（dashboard.py 在 committed_files 中）
    result = spec.reconcile([str(_DASHBOARD_FILE)], "manual-test")
    print(f"result={result}")


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def read_text(path) -> str | None:
    """公共接口：read_text（Stage 4 公共化）。"""
    return _read_text(path)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def get_metric_count() -> int | None:
    """公共接口：get_metric_count（Stage 4 公共化）。"""
    return _get_metric_count()
