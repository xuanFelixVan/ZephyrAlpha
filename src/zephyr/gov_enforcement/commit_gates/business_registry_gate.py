# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §business_registry_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.business_registry_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.registry_alignment（共享校验核心）；depgraph（PG 只读查询，fail-open）
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（经 in_process_gate_registry.yaml 自动注册）；tests/governance/test_alignment_gates_red_blue.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 硬阻断（确定性校验）——19 文件/21 段业务资产库全量（2026-09-11 满贯扩容，原 6 库→全量，REGISTRY_SPECS 真源移交 registry_alignment.py）staged 变更时：①条目 id 重复→阻断 ②条目 module_id 缺失→阻断 ③module_id 非 MOD-* 格式→阻断 ④module_id 在 depgraph 不存在→阻断（blueprint_id 口径，PG fail-open；2026-09-11 治本原 nodes.module_id 列不存在致子检查恒 fail-open 从未生效）；空库（0 条目）放行；文件级整库校验（基线 1463 条目填充率+格式 100% 已实证）
# [MODIFY-GUARD] gate_id="BUSINESS-REGISTRY"；REGISTRY_SPECS 段名/键名变更须同步对应注册表 schema（真源=registry_alignment.py）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] YAML 解析异常=fail-closed（库损坏须先修）；PG 异常=fail-open（跳过 depgraph 存在性子检查，logger.warning）
# [TESTS] tests/governance/test_alignment_gates_red_blue.py
# [TESTS-ALT] tests/governance/test_registry_alignment_layer2.py（同 gate 第二测试文件；[TESTS] 头仅支持单路径故以此行补记）
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-BUSINESS-REG-GATE-001
# [CREATION-TOKEN] auto-business-registry-gate-20260905
"""business_registry_gate.py — 业务资产库入库门禁（BUSINESS-REGISTRY，priority=139）

病根（第一性原理）
-----------------
alignment_checklist.md §4.1 业务资产库的对齐工具一栏原为"门禁（待建）"——
新策略/因子/指标注册时**没有任何门禁强制**挂 depgraph（module_id）。本 gate 把
"入库必须带 depgraph 锚点"从君子协定升为 commit 硬阻断（2026-09-05 六库转正式；
2026-09-11 满贯扩容至 19 文件/21 段全量，基线 1463 条目 100% 实证后纳入）。

2026-09-11 两项治本：
1. **SQL 列名 bug**：depgraph nodes 表无 module_id 列（真名 blueprint_id）——
   存在性子检查自上线起恒 fail-open 从未生效；修正后首轮即抓出 11 条幽灵锚点
   （MOD-FACTOR/MOD-STRATEGY 等域级占位），已批量正名到真实域蓝图 ID。
2. **共享化**：校验逻辑真源移交 zephyr.gov_enforcement.registry_alignment
   （gate/align_all/pytest 三方同源，防双真源漂移）；本文件保留 commit 专属
   逻辑（staged diff 提取新增条目 + BM 锚点强制）。

Usage::

    from zephyr.gov_enforcement.commit_gates.business_registry_gate import make_business_registry_gate
    registry.register(make_business_registry_gate())

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
import re
from pathlib import Path
from typing import Final

import yaml

from zephyr.gov_enforcement.registry_alignment import (
    CATALOGS_DIR as _CATALOGS_DIR,
    REGISTRY_SPECS,
    RegistrySpec,
    query_one as _query_one,
    validate_registry_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_business_registry_gate", "validate_registry_file", "REGISTRY_SPECS"]

# SQL 常量（NO-BARE-SQL 豁免命名约定 _SQL_*，先例=rename_depgraph_sync_gate._SQL_CHECK_FILE_PATH）
# 2026-09-11 治本：nodes 表真名为 blueprint_id（原 module_id 列不存在）
_SQL_GET_BUILD_STATUS = "SELECT build_status FROM nodes WHERE blueprint_id = %s LIMIT 1"
_SQL_CHECK_BM_ANCHOR = "SELECT 1 FROM battle_map_anchors WHERE target_graph = 'depgraph' AND target_id = %s LIMIT 1"


def _added_entry_ids(rel_path: str, id_key: str) -> list[str]:
    """从 staged diff 提取本次新增条目的 id（G1 二期 diff-scoped：只管新条目，存量不追溯）。

    git 不可用/无 diff → 返回空列表（fail-open）。
    """
    import subprocess

    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--", rel_path.replace("\\", "/")],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout
    except Exception:  # noqa: BLE001 — diff 不可得=fail-open
        return []
    pat = re.compile(r"^\+\s*-\s*" + re.escape(id_key) + r":\s*\"?([A-Za-z0-9][A-Za-z0-9_-]*)")
    return [m.group(1) for line in out.splitlines() for m in [pat.match(line)] if m]


def _module_exists_in_depgraph(module_id: str) -> bool:
    """depgraph 存在性（blueprint_id 口径；共享实现，fail-open=True 跳过）。"""
    from zephyr.gov_enforcement.registry_alignment import module_exists_in_depgraph

    return module_exists_in_depgraph(module_id)


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

            # depgraph 存在性（fail-open 子检查；在途豁免=他会话 staged 未提交实现
            # 文件的锚点，commit 后 reconciler 自动登记——防误伤并行 WIP）
            try:
                from zephyr.gov_enforcement.registry_alignment import (
                    _norm_mid,
                    in_flight_module_ids,
                    missing_depgraph_module_ids,
                )

                raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                mids = {
                    str(e.get("module_id"))
                    for e in (raw.get(spec.section) or [])
                    if isinstance(e, dict) and e.get("module_id")
                }
                in_flight = {_norm_mid(x) for x in in_flight_module_ids()}
                missing_set, _db_ok = missing_depgraph_module_ids(mids)
                missing = sorted(m for m in missing_set if _norm_mid(m) not in in_flight)
                all_fails.extend(f"【{spec.display}】module_id 在 depgraph 不存在: {m}" for m in missing)
            except Exception as e:  # noqa: BLE001 — 存在性子检查失败不阻断（格式校验已覆盖）
                logger.warning("BUSINESS-REGISTRY gate: depgraph 子检查跳过: %s", e)

            # G1 二期：新增条目 BM 锚点强制（diff-scoped，存量 457 孤儿不追溯——G4 清淤承载）
            # 规则：新增条目的 module 若 build_status=production → 必须已有 battle_map 锚点（硬）；
            #       design/planned → warn（待实现，锚点随后补）；PG 不可达 → 跳过（fail-open）
            rel = f"docs/01_policies_and_standards/_registry/catalogs/{spec.filename}"
            added_ids = _added_entry_ids(rel, spec.id_key)
            if added_ids:
                try:
                    entries_by_id = {
                        str(e.get(spec.id_key)): e
                        for e in (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get(spec.section) or []
                        if isinstance(e, dict) and e.get(spec.id_key)
                    }
                except Exception:  # noqa: BLE001 — 整库校验已覆盖解析错误
                    entries_by_id = {}
                for eid in added_ids:
                    mid = entries_by_id.get(eid, {}).get("module_id")
                    if not mid:
                        continue  # 缺 module_id 已被整库校验硬拦
                    skip_status, build_status = _query_one(_SQL_GET_BUILD_STATUS, str(mid))
                    if skip_status:
                        continue  # fail-open
                    skip_anchor, anchor_row = _query_one(_SQL_CHECK_BM_ANCHOR, str(mid))
                    if skip_anchor:
                        continue  # fail-open
                    if anchor_row is not None:
                        continue  # 已有锚点
                    if build_status == "production":
                        all_fails.append(
                            f"【{spec.display}】新增条目 {eid} 的模块 {mid} 为 production 态但无 battle_map 锚点"
                            "（G1 二期：已实现模块必须挂作战环节，apply_battle_map 补锚点）"
                        )
                    else:
                        logger.info(
                            "BUSINESS-REGISTRY gate: 新增条目 %s 模块 %s 为 %s 态无锚点（warn，待实现）",
                            eid,
                            mid,
                            build_status,
                        )

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
