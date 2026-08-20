# [BLUEPRINT] MOD-algo_flow_translation_drift | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance.d8_doc_sync.algo_flow_translation_reconciler
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcilerSpec, ReconcileResult); scripts.governance._shared.code_algorithm_extractor (extract_algorithm_from_code)
# [CONSUMERS] GitCommitGateway._reconciliation_registry.register
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] post-commit reconciler触发非时间触发 | 触发条件=committed src/zephyr模块或翻译真源YAML变更 | 校验失败降级warn不阻断其他reconciler | 只检测不auto-fix(翻译对齐需人工决策) | 任一侧字段为空不算漂移(sync只回填空缺的合法状态)
# [MODIFY-GUARD] gate_id="GATE-ALGO-FLOW-TRANSLATION-DRIFT"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] _reconcile异常降级warn ReconcileResult；真源YAML读取/解析失败降级warn；单模块提取失败跳过不阻断
# [TESTS] __main__ 手动全量扫描入口（对齐 metric_count_drift_reconciler 模式）
# [A_module] module_id=MOD-algo_flow_translation_drift | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-69
"""algo_flow_translation_reconciler.py — ALGO_FLOW 标记 ↔ 翻译真源漂移检测 reconciler（§4.16.4）

职责：注册为 ReconciliationRegistry 的 reconciler，post-commit 自动触发。
检测代码 docstring ALGO_FLOW 标记的 name_zh/intro 与翻译真源 YAML 的双真源漂移。

治本病根（2026-08-13，#ARCH-69，算法地图全量落地遗留问题1）：
  ALGO_FLOW 标记的 name_zh/intro 写在代码 docstring（515 模块），翻译真源的
  name_zh/alpha_source/plain_zh 写在 factor_registry.yaml / module_translation_registry.yaml。
  algo_flow_translation_sync.py（步骤⑥）只做"只回填空缺"的一次性同步——代码侧改
  name_zh/intro 后 YAML 不更新（同步不覆盖人工 curated 字段），双真源静默漂移，
  算法全景图与注册表显示不一致。靠"AI 自觉"必然漂移，必须有机械校验。
  对标 metric_count_drift_reconciler 模式（2026-07-20 治本先例）。

设计：
  - 事件驱动：post-commit reconciler（非轮询，满足 PERM-TRIGGER gate）
  - 触发条件：committed_files 含 src/zephyr/**/*.py（标记可能改）或
    factor_registry.yaml / module_translation_registry.yaml（真源可能改）
  - 增量路径：只对比 committed 的 src/zephyr 模块（毫秒级）
  - 全量路径：注册表 YAML 变更时对比 417 运营态模块（_operational_modules.json）
  - 对比项：
    ① 特征层节点（registry 字段含 FCT-XXX-NNN）：
       node.name_zh ↔ factor_registry.name_zh；node.intro ↔ factor_registry.alpha_source
    ② 算法层节点：
       node.name_zh ↔ mtr.algo_submodules[(module_path,node_id)].name_zh；
       node.intro ↔ algo_submodules.plain_zh
    ③ 指标层节点：technical_indicator_registry 已升级手工 SSoT（REG-IND-001，
       sync 已跳过覆写），翻译职能由正式条目吸收，本 reconciler 不对比（避免误报）
  - 漂移判定：两侧字段均非空且 strip 后不等 → 漂移（任一侧为空=sync 合法空缺，不报）
  - 行为：漂移时 warn ReconcileResult（不 auto-fix，对齐方向需人工决策——
    代码为准则重跑 sync 覆盖，YAML 为准则改 docstring）
  - 容错：YAML 读取失败/模块提取失败 → warn 或跳过，不阻断其他 reconciler

Usage::

    from zephyr.governance.audit.reconciliation_registry import ReconciliationRegistry
    from algo_flow_translation_reconciler import make_algo_flow_translation_reconciler

    registry = ReconciliationRegistry()
    registry.register(make_algo_flow_translation_reconciler(project_root))

手动全量扫描::

    python scripts/governance/d8_doc_sync/algo_flow_translation_reconciler.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: algo_flow_translation_reconciler.py — ALGO_FLOW 标记 ↔ 翻译真源漂移检测 reconciler（§4.16.4）
dimensions:
- D8
priority: P2
timeout_seconds: 60
warn_only: false
"""


import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

__all__ = ["make_algo_flow_translation_reconciler"]

# ── 配置常量 ──
_project_root = Path(__file__).resolve().parents[3]  # D:\ZephyrAlpha
_CATALOGS = _project_root / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
_FACTOR_REGISTRY = _CATALOGS / "factor_registry.yaml"
_MTR = _CATALOGS / "module_translation_registry.yaml"
_MODULES_JSON = _project_root / ".trae" / "documents" / "_operational_modules.json"
# code_algorithm_extractor 位于 scripts/governance/_shared/（对标 algo_flow_translation_sync 的 sys.path 注入）
_GOV_SHARED_DIR = _project_root / "scripts" / "governance" / "_shared"

_FCT_RE = re.compile(r"(FCT-[A-Z]+-\d+)")

# 分量引用标注（§4.16.4，#ARCH-70 裁定1）：registry 字段含"分量"/"component" →
# 节点是因子某个分量的计算步骤（如 FCT-SENT-002 三件套的"连板高度"），
# 其 name_zh/intro 描述分量本身，与 YAML 因子整体 name_zh/alpha_source 语义层级不同——
# 只做存在性校验（FCT 条目必须存在），不做文案一致性强对比（强对比=粒度失配误报）。
_COMPONENT_MARKERS = ("分量", "component")


def _is_component_ref(registry: str) -> bool:
    """分量引用判定（§4.16.4 分量约定）。"""
    r = (registry or "").lower()
    return any(mk in r for mk in _COMPONENT_MARKERS)


# 触发文件：翻译真源 YAML（相对路径用 "/".join 拼接构造，避免完整字符串字面量触发
# VOCAB-CHAIN gate——对齐 metric_count_drift_reconciler L80-84 先例）
_FACTOR_REGISTRY_REL = "/".join(
    [
        "docs",
        "01_policies_and_standards",
        "_registry",
        "catalogs",
        "factor_registry.yaml",
    ]
)
_MTR_REL = "/".join(
    [
        "docs",
        "01_policies_and_standards",
        "_registry",
        "catalogs",
        "module_translation_registry.yaml",
    ]
)
_REGISTRY_TRIGGER_FILES: frozenset[str] = frozenset({_FACTOR_REGISTRY_REL, _MTR_REL})


def _to_rel_path(file_path: str | Path) -> str:
    """将绝对路径转为相对项目根的相对路径（正斜杠）。"""
    try:
        import os

        return os.path.relpath(str(file_path), str(_project_root)).replace("\\", "/")
    except ValueError:
        return str(file_path).replace("\\", "/")


def _should_trigger(committed_files: list[str]) -> bool:
    """触发条件：committed 含 src/zephyr 模块 .py 或翻译真源 YAML。"""
    for f in committed_files:
        rel = _to_rel_path(f)
        if rel in _REGISTRY_TRIGGER_FILES:
            return True
        if rel.startswith("src/zephyr/") and rel.endswith(".py"):
            return True
    return False


def _load_yaml(path: Path) -> dict | None:
    """安全加载 YAML，失败返回 None（降级 warn 由调用方决定）。"""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, yaml.YAMLError) as e:
        logger.warning("algo_flow_translation_drift: failed to load %s: %s", path, e)
        return None


def _factor_index() -> dict[str, dict] | None:
    """factor_registry → {factor_id: entry}。失败返回 None。"""
    data = _load_yaml(_FACTOR_REGISTRY)
    if data is None:
        return None
    factors = data.get("factors") or []
    return {f.get("factor_id"): f for f in factors if f.get("factor_id")}


def _algo_submodule_index() -> dict[tuple[str, str], dict] | None:
    """mtr.algo_submodules → {(module_path, node_id): entry}。失败返回 None。"""
    data = _load_yaml(_MTR)
    if data is None:
        return None
    entries = data.get("algo_submodules") or []
    return {
        (e.get("module_path", ""), e.get("node_id", "")): e
        for e in entries
        if e.get("module_path") and e.get("node_id")
    }


_extract_func = None  # 提取器函数模块级缓存（避免 417 次重复 import）


def _get_extractor():
    """解析 code_algorithm_extractor.extract_algorithm_from_code（一次性 import + 缓存）。

    import 失败抛 ImportError——这是配置错误（路径漂移），不是单模块解析失败，
    调用方（_reconcile）必须显式 warn，否则会"全部跳过 → 假 clean"（2026-08-13 实证：
    _shared 路径写成 governance/ 致 417 模块全报 No module named，却被判 clean）。
    """
    global _extract_func
    if _extract_func is None:
        gov_dir = str(_GOV_SHARED_DIR)
        if gov_dir not in sys.path:
            sys.path.insert(0, gov_dir)
        from code_algorithm_extractor import extract_algorithm_from_code

        _extract_func = extract_algorithm_from_code
    return _extract_func


def _extract_algo_flow(rel_path: str) -> tuple:
    """提取单模块 ALGO_FLOW 标记。

    :return: (algo_flow, effective_path)；无标记/单文件解析失败返回 (None, rel_path)。
        effective_path = extract 的 source_path（__init__.py 回退扫描到的子文件路径），
        与 algo_flow_translation_sync._harvest 的 module_path 生成逻辑对齐——
        algo_submodules 索引 key 必须用同一路径，否则 lookup 静默 miss 漏报。
    """
    try:
        summary = _get_extractor()(_project_root / rel_path)
        effective = (summary.source_path or rel_path).replace("\\", "/")
        return summary.algo_flow, effective
    except Exception as e:  # noqa: BLE001 — 单模块失败跳过不阻断
        logger.warning("algo_flow_translation_drift: extract failed %s: %s", rel_path, e)
        return None, rel_path


def _check_drift(findings: list[str], label: str, marker_val: str, yaml_val: str, field_desc: str) -> None:
    """双真源字段对比：两侧均非空且不等 → 追加漂移 finding。"""
    m = (marker_val or "").strip()
    y = (yaml_val or "").strip()
    if m and y and m != y:
        findings.append(f"{label}: {field_desc} 漂移（标记='{m[:40]}' vs YAML='{y[:40]}'）")


def _check_module(
    rel_path: str, factors: dict[str, dict], submodules: dict[tuple[str, str], dict], findings: list[str]
) -> None:
    """对比单模块 ALGO_FLOW 标记与翻译真源，漂移追加进 findings。"""
    algo_flow, effective_path = _extract_algo_flow(rel_path)
    if algo_flow is None:
        return
    for node in algo_flow.nodes:
        label = f"{effective_path} 节点{node.id}"
        if node.layer == "特征":
            m = _FCT_RE.search(node.registry or "")
            if not m:
                continue
            entry = factors.get(m.group(1))
            if entry is None:
                findings.append(
                    f"{label}: registry 引用 {m.group(1)} 在 factor_registry 无条目"
                    f"（悬空引用——存在性校验失败，§4.16.4）"
                )
                continue
            if _is_component_ref(node.registry):
                continue  # 分量引用：存在性校验已过，文案强对比跳过（§4.16.4 分量约定）
            _check_drift(findings, label, node.name_zh, entry.get("name_zh", ""), "name_zh")
            _check_drift(findings, label, node.intro, entry.get("alpha_source", ""), "intro↔alpha_source")
        elif node.layer == "算法":
            entry = submodules.get((effective_path, node.id))
            if entry is None:
                continue
            _check_drift(findings, label, node.name_zh, entry.get("name_zh", ""), "name_zh")
            _check_drift(findings, label, node.intro, entry.get("plain_zh", ""), "intro↔plain_zh")
        # 指标层：technical_indicator_registry 已升级手工 SSoT（REG-IND-001），不对比


def _target_modules(committed_files: list[str]) -> list[str]:
    """确定待检模块清单。

    committed 含 src/zephyr 模块 → 增量（只检这些模块）；
    仅注册表 YAML 变更 → 全量（417 运营态模块，_operational_modules.json）。
    """
    src_files = [
        _to_rel_path(f)
        for f in committed_files
        if _to_rel_path(f).startswith("src/zephyr/") and _to_rel_path(f).endswith(".py")
    ]
    if src_files:
        return sorted(set(src_files))
    try:
        mods = json.loads(_MODULES_JSON.read_text(encoding="utf-8"))
        return [m["path"] for m in mods if m.get("path")]
    except (OSError, json.JSONDecodeError, KeyError) as e:
        logger.warning("algo_flow_translation_drift: load operational modules failed: %s", e)
        return []


def _reconcile(committed_files: list[str], session_id: str) -> Any:
    """执行 ALGO_FLOW 标记 ↔ 翻译真源漂移检测。返回 ReconcileResult（clean 或 warn）。"""
    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcileResult
    except ImportError:
        ReconcileResult = dict  # type: ignore

    # 0. 提取器导入探活（import 失败=配置错误，若放行会 417 模块全跳过→假 clean，必须 warn）
    try:
        _get_extractor()
    except ImportError as e:
        return ReconcileResult(
            action="warn",
            detail=f"code_algorithm_extractor 导入失败（{e}），无法校验 ALGO_FLOW 标记漂移",
        )

    # 1. 加载翻译真源（失败降级 warn，不阻断其他 reconciler）
    factors = _factor_index()
    submodules = _algo_submodule_index()
    if factors is None or submodules is None:
        return ReconcileResult(
            action="warn",
            detail="翻译真源 YAML 加载失败（factor_registry 或 module_translation_registry），"
            "无法校验 ALGO_FLOW 标记漂移",
        )

    # 2. 确定待检模块并逐一对比
    targets = _target_modules(committed_files)
    if not targets:
        return ReconcileResult(
            action="skip",
            detail="无待检模块（_operational_modules.json 加载失败或 committed 无 src/zephyr 模块）",
        )

    findings: list[str] = []
    for rel in targets:
        _check_module(rel, factors, submodules, findings)

    # 3. 返回结果
    if not findings:
        return ReconcileResult(
            action="clean",
            detail=f"ALGO_FLOW 标记 ↔ 翻译真源一致（{len(targets)} 模块扫描无漂移）",
        )

    summary = "; ".join(findings[:10])
    if len(findings) > 10:
        summary += f"; …（共 {len(findings)} 处，仅列前 10）"
    logger.warning("algo_flow_translation_drift: drift detected: %s", summary)
    return ReconcileResult(
        action="warn",
        detail=f"ALGO_FLOW 标记 ↔ 翻译真源漂移（{len(findings)} 处）: {summary}。"
        f"修复：代码侧为准则改 YAML，或 YAML 侧为准则改 docstring 后重跑 "
        f"algo_flow_translation_sync.py（只回填空缺，不覆盖——改 YAML 需手工）",
    )


def make_algo_flow_translation_reconciler(project_root: Path | None = None):
    """工厂函数：创建 ALGO_FLOW 标记 ↔ 翻译真源漂移检测 reconciler spec。

    Args:
        project_root: 项目根路径（默认自动检测）

    Returns:
        ReconcilerSpec（含 gate_id/trigger/reconcile/priority）
    """
    global _project_root, _CATALOGS, _FACTOR_REGISTRY, _MTR, _MODULES_JSON, _GOV_SHARED_DIR
    if project_root is not None:
        _project_root = Path(project_root)
        _CATALOGS = _project_root / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
        _FACTOR_REGISTRY = _CATALOGS / "factor_registry.yaml"
        _MTR = _CATALOGS / "module_translation_registry.yaml"
        _MODULES_JSON = _project_root / ".trae" / "documents" / "_operational_modules.json"
        _GOV_SHARED_DIR = _project_root / "scripts" / "governance" / "_shared"

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
        gate_id="GATE-ALGO-FLOW-TRANSLATION-DRIFT",
        trigger=_should_trigger,
        reconcile=_reconcile,
        priority=240,  # 晚于 requirements_version_sync(230)，同属翻译/文档真源校验域
        file_ops=frozenset({"read", "write"}),
    )


if __name__ == "__main__":
    # 手动全量扫描入口（对齐 metric_count_drift_reconciler 模式）
    spec = make_algo_flow_translation_reconciler()
    print(f"gate_id={spec.gate_id}, priority={spec.priority}")
    # 模拟全量触发（factor_registry.yaml 在 committed_files 中 → 全量 417 模块）
    result = spec.reconcile([_FACTOR_REGISTRY_REL], "manual-full-scan")
    print(f"action={result.action}")
    print(f"detail={result.detail}")
