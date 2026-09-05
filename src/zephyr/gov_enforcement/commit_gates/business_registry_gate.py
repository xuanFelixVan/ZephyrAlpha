# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §business_registry_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.business_registry_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] yaml（外部）；fnmatch/pathlib（stdlib）；depgraph（PG 只读查询，fail-open）
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（经 in_process_gate_registry.yaml 自动注册）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 硬阻断（确定性校验）——6 业务库（strategy/factor/technical_indicator/chart_pattern/portfolio_model/risk_limit）staged 变更时：①条目 id 重复→阻断 ②条目 module_id 缺失→阻断（对齐清单 §4.1"必须登记 depgraph"，2026-09-05 起"待建"转正式）③module_id 非 MOD-* 格式→阻断 ④module_id 在 depgraph 不存在→阻断（PG 查询，fail-open：DB 不可用跳过该子检查并 warn）；空库（0 条目）放行；文件级整库校验（基线 100% module_id 已实证：149+161+41）
# [MODIFY-GUARD] gate_id="BUSINESS-REGISTRY"；_REGISTRY_SPECS 段名/键名变更须同步对应注册表 schema
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] YAML 解析异常=fail-closed（库损坏须先修）；PG 异常=fail-open（跳过 depgraph 存在性子检查，logger.warning）
# [TESTS] tests/governance/test_alignment_gates_red_blue.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-BUSINESS-REG-GATE-001
# [CREATION-TOKEN] auto-business-registry-gate-20260905
"""business_registry_gate.py — 业务资产库入库门禁（BUSINESS-REGISTRY，priority=139）

病根（第一性原理）
-----------------
alignment_checklist.md §4.1 六个业务资产库的对齐工具一栏全部是"门禁（待建）"——
新策略/因子/指标注册时**没有任何门禁强制**挂 depgraph（module_id）。血肉填充阶段会
批量入库新条目，缺 module_id 的条目=地图上查不到实现的幽灵资产，且无机制发现。
本 gate 把"入库必须带 depgraph 锚点"从君子协定升为 commit 硬阻断（2026-09-05 起
"待建"转正式；基线 module_id 填充率 100% 已实证：strategy 149/149、factor 161/161、
indicator 41/41，三空库 0 条目——硬门禁基线安全）。

设计权衡
--------
1. **文件触发**：仅 staged 文件命中 6 库时才跑（读库+可选 PG 查询，非恒跑——6 库
   合计 25 万行 YAML，恒跑不可接受）。
2. **整库校验**（非 diff 抽取）：staged 库文件全量条目校验 id 唯一+module_id 存在——
   基线 100% 干净已实证，整库校验消灭"diff 解析漏项"这一失败模式。
3. **depgraph 存在性 fail-open**：PG 不可用时跳过该子检查（对标 NEW-FILE-DEPGRAPH-
   ENFORCEMENT/panorama gate 的 DB fail-open 惯例），格式校验仍硬。
4. **段名/键名显式声明**：6 库 section/id_key 各异（strategies/strategy_id、
   factors/factor_id、indicators/indicator_id、chart_patterns/pattern_id、
   portfolio_models/model_id、risk_limits/limit_id），_REGISTRY_SPECS 单点声明。

Usage::

    from zephyr.gov_enforcement.commit_gates.business_registry_gate import make_business_registry_gate
    registry.register(make_business_registry_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: staged 文件列表
#   fields: files（gateway 传入）
#   code: _check 按 _REGISTRY_SPECS 前缀匹配触发
# - id: I2
#   name: 命中的库 YAML + depgraph
#   fields: docs/01_policies_and_standards/_registry/catalogs/<registry>.yaml；depgraph nodes
#   code: _validate_registry_file + _module_exists_in_depgraph
# 层: 算法
# - id: A1
#   name_zh: ① 整库校验
#   name_en: validate_registry_file
#   intro: id 唯一 + module_id 非空且 MOD-* 格式（确定性，硬）
#   desc: 纯函数可单测；YAML 异常向上抛（gate fail-closed）
#   inputs: I2
#   outputs: list[str] fails
# - id: A2
#   name_zh: ② depgraph 存在性
#   name_en: _module_exists_in_depgraph
#   intro: PG 只读查询 module_id 是否存在（fail-open）
#   desc: DB 异常→跳过子检查并 warn（不阻断）
#   inputs: I2
#   outputs: set[str] 缺失 module_id
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec(gate_id="BUSINESS-REGISTRY", priority=139)
#   intro: 硬阻断型确定性门禁（业务库入库必须挂 depgraph 锚点）
#   downstream: git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I2 --> A2
# A1 --> O1
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import yaml

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_business_registry_gate", "validate_registry_file", "REGISTRY_SPECS"]

_REPO_ROOT = Path(__file__).resolve().parents[4]
_CATALOGS_DIR = _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"

# SQL 常量（NO-BARE-SQL 豁免命名约定 _SQL_*，先例=rename_depgraph_sync_gate._SQL_CHECK_FILE_PATH）
_SQL_CHECK_MODULE_ID = "SELECT 1 FROM nodes WHERE module_id = %s LIMIT 1"


@dataclass(frozen=True)
class RegistrySpec:
    """单库校验规格（段名/id 键/显示名）。"""

    filename: str
    section: str
    id_key: str
    display: str


REGISTRY_SPECS: tuple[RegistrySpec, ...] = (
    RegistrySpec("strategy_registry.yaml", "strategies", "strategy_id", "策略库"),
    RegistrySpec("factor_registry.yaml", "factors", "factor_id", "因子库"),
    RegistrySpec("technical_indicator_registry.yaml", "indicators", "indicator_id", "技术指标库"),
    RegistrySpec("chart_pattern_registry.yaml", "chart_patterns", "pattern_id", "图形形态库"),
    RegistrySpec("portfolio_model_registry.yaml", "portfolio_models", "model_id", "组合模型库"),
    RegistrySpec("risk_limit_registry.yaml", "risk_limits", "risk_limit_id", "风控限额库"),
)


def validate_registry_file(path: Path, spec: RegistrySpec) -> list[str]:
    """整库确定性校验：id 唯一 + module_id 非空且 MOD-* 前缀。

    Returns:
        fails 列表（空=通过）。YAML 解析异常向上抛（gate fail-closed）。
    """
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    entries = raw.get(spec.section) or []
    fails: list[str] = []
    seen: dict[str, int] = {}
    for idx, e in enumerate(entries):
        if not isinstance(e, dict):
            fails.append(f"{spec.filename}[{idx}] 条目非映射")
            continue
        eid = str(e.get(spec.id_key) or "")
        if not eid:
            fails.append(f"{spec.filename}[{idx}] 缺 {spec.id_key}")
            continue
        if eid in seen:
            fails.append(f"{spec.filename} {spec.id_key} 重复: {eid}（首见 [{seen[eid]}]）")
        seen[eid] = idx
        mid = e.get("module_id")
        if not mid:
            fails.append(
                f"{spec.filename} {eid} 缺 module_id（业务库入库必须挂 depgraph 锚点，"
                "alignment_checklist §4.1——2026-09-05 起强制）"
            )
        elif not str(mid).startswith("MOD-"):
            fails.append(f"{spec.filename} {eid} module_id 非 MOD-* 格式: {mid}")
    return fails


def _module_exists_in_depgraph(module_id: str) -> bool:
    """depgraph 只读存在性查询（fail-open：异常时返回 True=跳过子检查）。"""
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(_SQL_CHECK_MODULE_ID, (module_id,))
                return cur.fetchone() is not None
        finally:
            conn.close()
    except Exception as e:  # noqa: BLE001 — DB 不可用=fail-open（对标 NEW-FILE-DEPGRAPH gate）
        logger.warning("BUSINESS-REGISTRY gate: depgraph 查询失败，跳过存在性子检查（fail-open）: %s", e)
        return True


def make_business_registry_gate() -> GateSpec:
    """构造业务资产库入库硬阻断 GateSpec（G1：alignment_checklist §4.1"待建"转正式）。

    Returns:
        GateSpec(gate_id="BUSINESS-REGISTRY", priority=139)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        if not files:
            return True, ""
        triggered = [
            spec for spec in REGISTRY_SPECS if any(f.replace("\\", "/").endswith(spec.filename) for f in files)
        ]
        if not triggered:
            return True, ""

        all_fails: list[str] = []
        for spec in triggered:
            path = _CATALOGS_DIR / spec.filename
            try:
                fails = validate_registry_file(path, spec)
            except Exception as e:  # noqa: BLE001 — 库文件损坏=fail-closed
                logger.error("BUSINESS-REGISTRY gate: %s 解析异常（fail-closed）: %s", spec.filename, e)
                return False, f"BUSINESS-REGISTRY: {spec.filename} 解析异常（库损坏须先修）: {e}"
            all_fails.extend(f"【{spec.display}】{x}" for x in fails)

            # depgraph 存在性（fail-open 子检查）
            try:
                raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                mids = {
                    str(e.get("module_id"))
                    for e in (raw.get(spec.section) or [])
                    if isinstance(e, dict) and e.get("module_id")
                }
                missing = sorted(m for m in mids if not _module_exists_in_depgraph(m))
                all_fails.extend(f"【{spec.display}】module_id 在 depgraph 不存在: {m}" for m in missing)
            except Exception as e:  # noqa: BLE001 — 存在性子检查失败不阻断（格式校验已覆盖）
                logger.warning("BUSINESS-REGISTRY gate: depgraph 子检查跳过: %s", e)

        if not all_fails:
            return True, ""

        detail_lines = "\n".join(f"  - {x}" for x in all_fails)
        detail = (
            f"BUSINESS-REGISTRY：业务资产库入库校验 {len(all_fails)} 项违规\n"
            f"{detail_lines}\n"
            "-> 新增条目必须填 module_id（MOD-*，须已在 depgraph 登记）且 id 不重复"
            "（alignment_checklist §4.1：入库必须挂 depgraph 锚点）"
        )
        logger.error("BUSINESS-REGISTRY gate block:\n%s", detail)
        return False, detail

    return GateSpec(gate_id="BUSINESS-REGISTRY", check=_check, priority=139)
