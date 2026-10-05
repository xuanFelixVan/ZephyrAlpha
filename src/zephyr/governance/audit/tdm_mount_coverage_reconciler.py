# [BLUEPRINT] MOD-GOV_TDM_MOUNT_COVERAGE_RECONCILER | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §mount-coverage-reconciler
# [MODULE] zephyr.governance.audit.tdm_mount_coverage_reconciler
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec); zephyr.shared.io.paths (REPO_ROOT); scripts.governance._shared.mount_obligation (build_mounted_set/collect_map_nodes/load_exemptions/has_not_trading_marker——挂载口径单计算双消费)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway（post-commit 注册，priority=952）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] post-commit 事件触发（trigger 命中面=config 图族/豁免册/blueprint.md/src|scripts 新 .py/翻译册）；reconciler 永不抛异常；warn-only（孤儿不阻断 commit，仅告警+落盘报告供追踪）；真源不可达 fail-open；只读扫描（不写任何真源，报告写 .runtime/tdm_mount/ 派生区）；孤儿判红口径=23 域人口 blueprint module_id − 挂载面并集 − 豁免册 − [not-trading] 标记，与 gate/manifest 同源（单计算双消费铁律）；禁 cron（宪法四要素——commit 事件触发）
# [MODIFY-GUARD] _GATE_ID / _PRIORITY / _REPORT_PATH
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile 永不抛异常——YAML/IO/助手异常降级为 ReconcileResult(action="warn")
# [TESTS] tests/governance/audit/test_tdm_mount_coverage_reconciler.py
# [A_module] module_id=MOD-GOV_TDM_MOUNT_COVERAGE_RECONCILER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)
"""tdm_mount_coverage_reconciler.py — TDM 挂载义务存量对账 reconciler（Layer 4）。

TDM-MOUNT-COVERAGE 四层防御的 Layer 4（post-commit 存量对账，对标
translation_coverage_reconciler 先例）：每次 commit 命中模块册变更面（config 图族/
豁免册/blueprint.md/新 .py/翻译册）时全量重扫——23 交易域人口 blueprint module_id
vs 挂载面并集（module_id∪module_mounts，经 _shared.mount_obligation 单计算）∪
豁免册 ∪ [not-trading] 标记，孤儿判红落盘 ``.runtime/tdm_mount/orphan_report.json``
（warn-only 不阻断）。

治本动机（第一性原理）
--------------------
gate（Layer 2，提交时）只管 staged 新增；存量可能因 reconciler 回退、手工编辑、
裁决册增量遗漏等重新产生孤儿（e 裁决册 233 行缺口的教训：缺口是长出来的，不是
一次性的）。本 reconciler 保证存量对账自动化——模块册一变更即重扫判红，禁 cron
（宪法四要素：事件触发）。

真源边界（SSoT 分类铁律 TRAE-062）
----------------------------------
- 人口/挂载/豁免=规则数据（blueprint.md frontmatter + config YAML，只读）
- 报告=派生数据（.runtime/tdm_mount/，可重建，非真源）
- 义务清单 manifest 重申=scripts/generate_mount_obligation_manifest.py（本 reconciler
  触发后由维护班/总筹按需重跑，不自动写 docs/_working/——报告面与投影面分离）

Usage
-----
::

    from zephyr.governance.audit.tdm_mount_coverage_reconciler import (
        make_tdm_mount_coverage_reconciler,
    )

    registry.register(make_tdm_mount_coverage_reconciler(gateway))

# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/audit/tdm_mount_coverage_reconciler.yaml
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Final

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
)
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

__all__: Final = ["make_tdm_mount_coverage_reconciler"]
# [not-trading: 治理域存量对账设施（非交易流程模块），挂载语义=守卫的图 YAML 输入面，见 [DEPENDENCIES]/[CONSUMERS] 声明]

# create-guard-not-dup: 与 translation_coverage_reconciler 同为存量对账族但判据面不同源（挂载义务孤儿判定 vs 翻译覆盖率 drift），capability 词面近义非同能力第二实现

# 关联的 pre-commit GATE 标识（与 tdm_mount_coverage_gate.py 同名——reconciler 补偿 gate）
_GATE_ID = "TDM-MOUNT-COVERAGE"

# 执行优先级——晚于 translation_coverage(951)，同 late-stage warn-only 全扫族
_PRIORITY = 952

# 详情条数上限（与 translation_coverage_reconciler 同款展示纪律）
_MAX_DETAIL_ITEMS = 5

# 漂移报告落盘路径（派生区，禁 .runtime 根直写——宪法 §9.4）
_REPORT_DIR = ".runtime/tdm_mount"
_REPORT_NAME = "orphan_report.json"

# trigger 命中面（模块册变更=重扫信号）
_TRIGGER_MAP_PREFIX = "config/"
_TRIGGER_BP_PREFIX = "docs/03_modules/"


def _load_helpers():
    """懒加载共享助手 + B 账本生成器人口扫描（跨 src/scripts 边界，单计算双消费）。

    人口侧复用 generate_map_coverage_ledger.scan_population（唯一人口口径，禁第二实现）；
    失败返回 None（fail-open）。
    """
    try:
        repo = str(REPO_ROOT)
        for p in (f"{repo}/scripts", f"{repo}/scripts/governance", f"{repo}/src"):
            if p not in sys.path:
                sys.path.insert(0, p)
        import generate_map_coverage_ledger as ledger_gen  # noqa: PLC0415
        from _shared.mount_obligation import (  # noqa: PLC0415
            build_mounted_set,
            collect_map_nodes,
            has_not_trading_marker,
            load_exemptions,
        )

        return build_mounted_set, collect_map_nodes, has_not_trading_marker, load_exemptions, ledger_gen
    except Exception as e:  # noqa: BLE001 — 助手不可达=环境异常
        logger.warning(
            "tdm_mount_coverage_reconciler: 共享助手装载失败(%s: %s)，fail-open。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _scan_orphans(helpers) -> dict:
    """全量重扫：人口 vs 挂载∪豁免∪marker，返回孤儿报告 dict（不落盘）。

    挂载面=module_id∪module_mounts∪module_ref 折算（三腿与 B 账本同源；ref 折算腿不可达时
    warn 降级为两腿——防 PG 抖动假红）。
    返回 {"orphan_total", "orphans", "mounted_count", "exempt_count", "marked_count"}。
    """
    build_mounted_set, collect_map_nodes, has_not_trading_marker, load_exemptions, ledger_gen = helpers
    with_id, _without = ledger_gen.scan_population()
    pop = {p["module_id"]: p for p in with_id}
    nodes = collect_map_nodes(REPO_ROOT)
    mounted = build_mounted_set(nodes)
    try:
        refs = {str(n["module_ref"]).replace("\\", "/") for n in nodes if n.get("module_ref")}
        if refs:
            path_map, pkg_map, _bid_domain, _anchor = ledger_gen.make_depgraph_resolver()
            mounted |= {
                folded for folded in (ledger_gen.fold_ref(r, path_map, pkg_map) for r in sorted(refs)) if folded
            }
    except Exception as e:  # noqa: BLE001 — ref 腿不可达降级两腿（warn 由调用方 result 体现）
        logger.warning("tdm_mount_coverage_reconciler: ref 折算腿不可达(%s: %s)，降级两腿判红。", type(e).__name__, e)
    exemptions = load_exemptions(REPO_ROOT)
    orphans: list[str] = []
    marked = 0
    for mid, entry in sorted(pop.items()):
        if mid in mounted or mid in exemptions:
            continue
        bp = REPO_ROOT / entry.get("blueprint", "")
        try:
            if bp.exists() and has_not_trading_marker(bp.read_text(encoding="utf-8")):
                marked += 1
                continue
        except OSError:  # noqa: PERF203 — 蓝图不可读按孤儿红处理（fail-closed 读面）
            pass
        orphans.append(mid)
    return {
        "orphan_total": len(orphans),
        "orphans": orphans,
        "mounted_count": len(mounted & set(pop)),
        "exempt_count": len(set(pop) & set(exemptions)),
        "marked_count": marked,
        "population_count": len(pop),
    }


def _write_report(report: dict, anchor: str) -> None:
    """报告落盘（fail-open；派生区非真源）。"""
    try:
        out = REPO_ROOT / _REPORT_DIR
        out.mkdir(parents=True, exist_ok=True)
        payload = {"gate_id": _GATE_ID, "anchor": anchor, **report}
        (out / _REPORT_NAME).write_text(
            json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8"
        )
    except Exception as e:  # noqa: BLE001 — 落盘失败不阻断
        logger.warning("tdm_mount_coverage_reconciler: 报告落盘失败(%s: %s)。", type(e).__name__, e)


def make_tdm_mount_coverage_reconciler(gateway) -> ReconcilerSpec:
    """构造 TDM 挂载义务存量对账 reconciler（priority=952，post-commit warn-only）。"""

    def _trigger(committed_files: list[str]) -> bool:
        """模块册变更面命中：config 图族/豁免册、blueprint.md、src|scripts .py。"""
        for f in committed_files:
            norm = f.replace("\\", "/")
            if norm.startswith(_TRIGGER_MAP_PREFIX) and norm.endswith(".yaml"):
                return True
            if norm.startswith(_TRIGGER_BP_PREFIX) and norm.endswith("blueprint.md"):
                return True
            if (norm.startswith("src/") or norm.startswith("scripts/")) and norm.endswith(".py"):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        """全量重扫孤儿判红，落盘报告（warn-only）。"""
        try:
            helpers = _load_helpers()
            if helpers is None:
                return ReconcileResult(action="warn", detail="挂载助手不可达，跳过存量对账", gate_id=_GATE_ID)
            report = _scan_orphans(helpers)
            anchor = ""
            try:
                import subprocess  # noqa: PLC0415

                r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10)  # noqa: bare-subprocess  只读锚标签展示面（HEAD 短哈希仅用于报告落款），无窗口闪现敏感路径
                anchor = (r.stdout or "").strip()
            except Exception:  # noqa: BLE001 — 锚标签仅展示面
                pass
            _write_report(report, anchor)
            if report["orphan_total"] == 0:
                return ReconcileResult(
                    action="clean",
                    detail=(
                        f"no mount obligation orphan (population={report['population_count']}, "
                        f"mounted={report['mounted_count']}, exempt={report['exempt_count']}, "
                        f"marked={report['marked_count']})"
                    ),
                    gate_id=_GATE_ID,
                )
            shown = report["orphans"][:_MAX_DETAIL_ITEMS]
            suffix = f"（还有 {report['orphan_total'] - len(shown)} 台）" if report["orphan_total"] > len(shown) else ""
            return ReconcileResult(
                action="warn",
                detail=(
                    f"{report['orphan_total']} 台人口模块无挂载裁决（孤儿红，报告="
                    f"{_REPORT_DIR}/{_REPORT_NAME}）: {', '.join(shown)}{suffix}"
                ),
                gate_id=_GATE_ID,
            )
        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常
            logger.warning(
                "tdm_mount_coverage_reconciler: reconcile 失败(%s: %s)。", type(e).__name__, e, exc_info=True
            )
            return ReconcileResult(action="warn", detail=f"tdm_mount_coverage reconcile error: {e}", gate_id=_GATE_ID)

    return ReconcilerSpec(
        gate_id=_GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=_PRIORITY,
        file_ops=frozenset({"read", "write"}),
    )
