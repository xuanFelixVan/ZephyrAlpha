# [BLUEPRINT] MOD-GOV-CENSUSRECON
# [MODULE] zephyr.governance.consumption.consumption_census_reconciler
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.consumption.consumption_census(普查引擎);
#                zephyr.governance.audit.reconciliation_registry(ReconcilerSpec/ReconcileResult)
# [CONSUMERS] reconciliation_registry._EXTERNAL_SPEC_MODULES（清单行由总筹一次性插入，本道不自插）
# [STARTUP] imported(post-commit 事件触发；禁 cron/Timer/sleep-loop——宪法 §9.3)
# [MATURITY] design
# [INVARIANTS] 只写 gitignore 面台账（data/runtime/），零 git 动作、零裸 commit；
#              登记册与台账同新旧时 no-op（天然自终止，禁自环）；
#              孤岛新增/回填只报警不自动改册（入账由 generate_wiring_registry --check 出漂移）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 引擎异常→ReconcileResult(action="critical_warn") 不抛出（commit 已入历史，对账非阻断）
# [TESTS] tests/governance/test_consumption_census_redproof.py::test_reconciler_*
# [A_module] module_id=MOD-GOV-CENSUSRECON | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# create-guard-not-dup: 本件＝消费面普查的事件触发重跑+孤岛点名对账器，与死信所列 session_continuity/shrinkage_provider/git_safety_wrapper 等九项能力零功能交集——命中词「as of」「孤岛的事件触发报警与入账钩子」系本 docstring 措辞的探针碰撞（q-20260928-st-zcloseout-20260926-0002 死信处方）
"""consumption_census_reconciler — "上架无客"孤岛的事件触发报警与入账钩子（包 13.3 第 5 件）。

触发事件＝登记册变更（族名册=上架动作）或普查引擎自身落地，**非 cron**：
提交九族任一名册 → post-commit 重跑增量普查 → 新孤岛/回填岛点名 → warn。
写侧仅 `data/runtime/`（gitignore 面）；账本正式入册由
`scripts/governance/d3_metadata/generate_wiring_registry.py` 产机器视图、总筹落地 YAML。

复用的既有事件路径（不新建第二条）：`trading_lifecycle_weekly`
（`src/zephyr/data/config/tasks.yaml:3396` → `internal_compute_provider.py:650`
→ `_fetch_trading_lifecycle_weekly:880`，调用点 `:904`）——该 capability 分支的指标审计
现由本引擎族①承担（`indicator_usage_audit` 已降为薄壳）。

# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/consumption/consumption_census_reconciler.yaml
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Final
from zoneinfo import ZoneInfo

from zephyr.governance.audit.reconciliation_registry import ReconcileResult, ReconcilerSpec
from zephyr.governance.consumption.consumption_census import FAMILY_SPECS, run_consumption_census

__all__: Final = ["make_consumption_census_reconciler", "make_external_reconciler_spec"]

GATE_ID: Final = "GATE-CONSUMPTION-CENSUS"
_TZ = ZoneInfo("Asia/Shanghai")

#: 触发面＝九族登记册 + 引擎/生成器/本 reconciler 自身 + 孤岛入账册
_LEDGER_REL: Final = "data/runtime/consumption_census_ledger.json"


def _trigger_rels() -> set[str]:
    rels = {
        "docs/01_policies_and_standards/_registry/catalogs/wiring_registry.yaml",
        "src/zephyr/governance/consumption_census.py",
        "src/zephyr/governance/consumption_census_reconciler.py",
        "scripts/governance/d3_metadata/generate_wiring_registry.py",
    }
    for fam in FAMILY_SPECS:
        for f in (fam, *fam.union_of):
            for p in (f.registry_path, f.file_path):
                if p:
                    rels.add(p.replace("\\", "/"))
    return rels


def _rel(f: str, root: Path) -> str:
    try:
        return os.path.relpath(f, str(root)).replace("\\", "/")
    except ValueError:
        return f.replace("\\", "/")


def _as_of(root: Path) -> str:
    """时间戳取"名册最新 mtime"而非 datetime.now()（RULE-SCHEMA-TZ：生成器禁墙钟）。"""
    stamps = []
    for rel in _trigger_rels():
        p = root / rel
        if p.exists():
            stamps.append(p.stat().st_mtime)
    if not stamps:
        return "unknown"
    return datetime.fromtimestamp(max(stamps), tz=_TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


def _islands_of(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {f"{i['family']}::{i['entity_id']}": i for i in doc.get("islands", [])}


# trae_060-reviewed: 本 reconciler 由 _EXTERNAL_SPEC_MODULES 外部规格通道装载（非 gateway 静态注册段），
#   file_ops 显式声明 {"read","write"}、零 delete/move、零 git 动作，产物落 gitignore 面 data/runtime/，
#   触发面为登记册变更事件（非 cron/Timer），异常降级 critical_warn 不阻断——与 T1① 声明制与 §9.3 事件触发相符。
def make_consumption_census_reconciler(host: object | None = None) -> ReconcilerSpec:
    """构造"上架无客"孤岛对账 reconciler（只报警、只写 gitignore 面台账）。

    Args:
        host: ReconciliationRegistry / GitCommitGateway 实例或 None——仅取 project_root。
    """
    project_root = None
    if host is not None and getattr(host, "project_root", None):
        project_root = Path(str(host.project_root))
    if project_root is None:
        from zephyr.shared.io.paths import REPO_ROOT

        project_root = Path(str(REPO_ROOT))
    trigger_rels = _trigger_rels()
    ledger_path = project_root / _LEDGER_REL

    def _trigger(committed_files: list[str]) -> bool:
        return any(_rel(f, project_root) in trigger_rels for f in committed_files)

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        pre_islands = _islands_of(ledger_path)  # 上次账面（必须在跑之前取，闭包期取＝永远空）
        hit = [_rel(f, project_root) for f in committed_files if _rel(f, project_root) in trigger_rels]
        try:
            summary = run_consumption_census(
                repo_root=project_root,
                output_path=ledger_path,
                cache_path=project_root / "data/runtime/consumption_census_cache.json",
                today=_as_of(project_root),
                include_doc_mentions=False,  # post-commit 快档：文档证据面留在全量档
            )
        except Exception as exc:  # noqa: BLE001 — 对账非阻断，失败必须点名不可静默
            return ReconcileResult(
                action="critical_warn",
                detail=f"消费普查执行失败（不阻断，但必须修）: {type(exc).__name__}: {exc}",
                gate_id=GATE_ID,
            )
        post_islands = _islands_of(ledger_path)
        new = sorted(set(post_islands) - set(pre_islands))[:12]
        resolved = sorted(set(pre_islands) - set(post_islands))[:12]
        detail = {
            "trigger_files": hit[:8],
            "session_id": session_id,
            "counts": summary["counts"],
            "islands_total": summary["islands"],
            "new_islands": new,
            "resolved_islands": resolved,
            "ledger": str(ledger_path),
            "runtime": summary["runtime"],
        }
        if not hit:
            return ReconcileResult(action="skip", detail=json.dumps(detail, ensure_ascii=False), gate_id=GATE_ID)
        if new:
            return ReconcileResult(
                action="warn",
                detail=(
                    f"上架无客孤岛 +{len(new)}（总 {summary['islands']}）："
                    f"{', '.join(new[:6])}；入账=跑 generate_wiring_registry.py 交总筹落 YAML"
                ),
                gate_id=GATE_ID,
            )
        return ReconcileResult(action="clean", detail=json.dumps(detail, ensure_ascii=False), gate_id=GATE_ID)

    return ReconcilerSpec(
        gate_id=GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=246,  # 排在 library(≈220)/schedule 之后：普查是末端观测件，不参与修复竞争
        file_ops=frozenset({"read", "write"}),
    )


# trae_060-reviewed: 外部规格发现钩子（reconciliation_registry._EXTERNAL_SPEC_MODULES 契约签名），
#   与上方工厂同款，不新增第二台 reconciler，故无需独立评审结论。
def make_external_reconciler_spec(host: object | None = None) -> ReconcilerSpec:
    """ReconciliationRegistry 外部规格发现钩子入口（签名稳定：registry/gateway/None 均可）。"""
    return make_consumption_census_reconciler(host)
