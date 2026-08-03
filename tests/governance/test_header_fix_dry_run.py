# [A_module] module_id=MOD-GOV-header-fix-dry-run | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""test_header_fix_dry_run.py — 文件头 module_id 批量修复脚本 dry-run 逻辑验证

用 10 个典型 mock 文件模拟修复脚本的判定逻辑，验证：
  - 已有 [A_module] 行但 module_id 不一致 → FIX
  - [BLUEPRINT] 行和 [A_module] 行 module_id 不同 → 分别判定
  - 缺 [A_module] 头 → ADD（标记需要补头）
  - 路径含 YAML anchor → SKIP
  - 文件不存在 → SKIP
  - 已一致 → NO_CHANGE（幂等性）

Usage::
    py -3.12 -m pytest tests/governance/test_header_fix_dry_run.py -v -n 0
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import pytest

# ──────────────────────────────────────────────────────────────────────────────
# 正则定义
# ──────────────────────────────────────────────────────────────────────────────

# 匹配: # [A_module] module_id=MOD-XXX | layer=...
RE_A_MODULE = re.compile(r"^(#\s*\[A_module\]\s*module_id=)(\S+?)(\s*\|.*)?$")

# 匹配: # [BLUEPRINT] MOD-XXX | docs/...
RE_BLUEPRINT = re.compile(r"^(#\s*\[BLUEPRINT\]\s*)(\S+?)(\s*\|.*)?$")


# ──────────────────────────────────────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class MockFile:
    """模拟一个待检查的文件。"""

    path: str
    depgraph_module_id: str
    build_status: str
    content: str | None = None  # None 表示文件不存在
    exists: bool = True


@dataclass
class DryRunResult:
    """dry-run 对单个文件的分析结果。"""

    path: str
    depgraph_module_id: str
    action: str  # FIX | ADD | SKIP | NO_CHANGE
    details: list[str] = field(default_factory=list)
    a_module_line: int | None = None  # [A_module] 行号（0-based），None=不存在
    blueprint_line: int | None = None  # [BLUEPRINT] 行号
    current_a_module_id: str | None = None
    current_blueprint_id: str | None = None


# ──────────────────────────────────────────────────────────────────────────────
# dry-run 核心逻辑
# ──────────────────────────────────────────────────────────────────────────────


def dry_run_analyze(mock: MockFile) -> DryRunResult:
    """对单个 mock 文件执行 dry-run 分析，返回判定结果。"""
    result = DryRunResult(path=mock.path, depgraph_module_id=mock.depgraph_module_id, action="NO_CHANGE")

    # 边界 1：路径含 YAML anchor → SKIP
    if "#" in mock.path:
        result.action = "SKIP"
        result.details.append("路径含 YAML anchor（#），跳过")
        return result

    # 边界 2：文件不存在 → SKIP
    if not mock.exists or mock.content is None:
        result.action = "SKIP"
        result.details.append("文件不存在，跳过")
        return result

    lines = mock.content.splitlines()

    # 扫描前 30 行寻找 [A_module] 和 [BLUEPRINT] 行
    for i, line in enumerate(lines[:30]):
        if i >= 30:
            break

        # 检查 [A_module] 行
        m = RE_A_MODULE.match(line)
        if m:
            result.a_module_line = i
            result.current_a_module_id = m.group(2).strip()
            continue

        # 检查 [BLUEPRINT] 行
        m = RE_BLUEPRINT.match(line)
        if m:
            result.blueprint_line = i
            result.current_blueprint_id = m.group(2).strip()
            continue

    # 判定逻辑
    needs_fix = False

    # 检查 [A_module] 行
    if result.current_a_module_id is not None:
        if result.current_a_module_id != mock.depgraph_module_id:
            result.details.append(f"[A_module] {result.current_a_module_id} → {mock.depgraph_module_id} (FIX)")
            needs_fix = True
        else:
            result.details.append(f"[A_module] {result.current_a_module_id} (OK)")
    else:
        result.details.append("[A_module] 行不存在 (ADD)")
        needs_fix = True

    # 检查 [BLUEPRINT] 行
    if result.current_blueprint_id is not None:
        if result.current_blueprint_id != mock.depgraph_module_id:
            result.details.append(f"[BLUEPRINT] {result.current_blueprint_id} → {mock.depgraph_module_id} (FIX)")
            needs_fix = True
        else:
            result.details.append(f"[BLUEPRINT] {result.current_blueprint_id} (OK)")
    else:
        result.details.append("[BLUEPRINT] 行不存在")

    if needs_fix:
        result.action = "FIX" if result.current_a_module_id is not None else "ADD"
    else:
        result.action = "NO_CHANGE"

    return result


def format_result(r: DryRunResult) -> str:
    """格式化输出结果。"""
    lines = [f"[{r.path}]"]
    lines.append(f"  depgraph_module_id: {r.depgraph_module_id}")
    lines.append(f"  action: {r.action}")
    for d in r.details:
        lines.append(f"  - {d}")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# 10 个典型 mock 文件
# ──────────────────────────────────────────────────────────────────────────────

MOCK_FILES: list[MockFile] = [
    # 1. [A_module] 不一致（MOD-GOV-xxx 模式）
    MockFile(
        path="src/mock/artifact_scanner.py",
        depgraph_module_id="MOD-L10-001",
        build_status="stable",
        content=(
            "# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_gov_drift/blueprint.md\n"
            "# [MODULE] zephyr.gov_drift.artifact_scanner\n"
            "# [DOMAIN] D_GOV_DRIFT\n"
            "# [STABILITY] stable\n"
            "# [SAFETY] M\n"
            "# [A_module] module_id=MOD-GOV-artifact_scanner | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable\n"
            "# [TTL] permanent\n"
            "\n"
            '"""Artifact scanner."""\n'
        ),
    ),
    # 2. [A_module] 不一致（MOD-UNK-xxx 模式）
    MockFile(
        path="src/mock/risk_manager.py",
        depgraph_module_id="MOD-L04-001",
        build_status="stable",
        content=(
            "# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_risk/blueprint.md\n"
            "# [MODULE] zephyr.risk.risk_manager\n"
            "# [DOMAIN] D_RISK\n"
            "# [A_module] module_id=MOD-UNK-risk_manager | layer=module | stability=stable | safety=H | ai_autonomy=ai_modifiable\n"
            "# [TTL] permanent\n"
        ),
    ),
    # 3. [A_module] 不一致（MOD-SEC-xxx 模式）
    MockFile(
        path="src/mock/scan_mutex.py",
        depgraph_module_id="MOD-INF-023",
        build_status="stable",
        content=(
            "# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_infrastructure/blueprint.md\n"
            "# [A_module] module_id=MOD-SEC-scan_mutex | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable\n"
        ),
    ),
    # 4. [BLUEPRINT] 正确但 [A_module] 错误
    MockFile(
        path="src/mock/oms_risk_engine.py",
        depgraph_module_id="MOD-GOVERNANCE",
        build_status="stable",
        content=(
            "# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §\n"
            "# [MODULE] zephyr.governance.financial_governance.oms_risk_engine\n"
            "# [DOMAIN] D_GOVERNANCE\n"
            "# [STABILITY] evolving\n"
            "# [SAFETY] L\n"
            "# [A_module] module_id=MOD-GOV-oms_risk_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable\n"
            "# [TTL] permanent\n"
        ),
    ),
    # 5. [BLUEPRINT] 和 [A_module] 都错
    MockFile(
        path="src/mock/default_tca_engine.py",
        depgraph_module_id="MOD-L07-001",
        build_status="generated",
        content=(
            "# [BLUEPRINT] MOD-UNK-default_tca_engine | docs/03_modules/_domain_reporting/blueprint.md\n"
            "# [MODULE] zephyr.reporting.default_tca_engine\n"
            "# [DOMAIN] D_REPORTING\n"
            "# [A_module] module_id=MOD-UNK-default_tca_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable\n"
            "# [TTL] permanent\n"
        ),
    ),
    # 6. 缺 [A_module] 头（有 [BLUEPRINT] 但无 [A_module]）
    MockFile(
        path="src/mock/validate_blueprint_overlap.py",
        depgraph_module_id="MOD-GOV_SCRIPTS",
        build_status="stable",
        content=(
            "# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/03_modules/_domain_gov_scripts/blueprint.md\n"
            "# [MODULE] scripts.governance.d11_compliance.validate_blueprint_overlap\n"
            "# [DOMAIN] D_GOV_SCRIPTS\n"
            "# [STABILITY] stable\n"
            "# [SAFETY] M\n"
            "# [TTL] permanent\n"
            "\n"
            '"""Validate blueprint overlap."""\n'
        ),
    ),
    # 7. __init__.py 模式（MOD-SELL_DECISION_api → MOD-SELL_DECISION）
    MockFile(
        path="src/mock/sell_decision/api/__init__.py",
        depgraph_module_id="MOD-SELL_DECISION",
        build_status="generated",
        content=(
            "# [BLUEPRINT] MOD-SELL_DECISION | docs/03_modules/_domain_sell_decision/blueprint.md\n"
            "# [A_module] module_id=MOD-SELL_DECISION_api | layer=module | stability=generated | safety=L | ai_autonomy=ai_modifiable\n"
        ),
    ),
    # 8. 已一致（幂等性验证）
    MockFile(
        path="src/mock/already_correct.py",
        depgraph_module_id="MOD-L04-001",
        build_status="stable",
        content=(
            "# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_risk/blueprint.md\n"
            "# [MODULE] zephyr.risk.risk_limits\n"
            "# [DOMAIN] D_RISK\n"
            "# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=H | ai_autonomy=ai_modifiable\n"
            "# [TTL] permanent\n"
        ),
    ),
    # 9. 路径含 YAML anchor → SKIP
    MockFile(
        path="docs/mock/infrastructure_registry.yaml#INFRA-DB-001",
        depgraph_module_id="INFRA-DB-001",
        build_status="stable",
        content="irrelevant",
    ),
    # 10. 文件不存在 → SKIP
    MockFile(
        path="src/mock/replacement_rebalance_sell.py",
        depgraph_module_id="MOD-SELL-006",
        build_status="stable",
        content=None,
        exists=False,
    ),
]


# ──────────────────────────────────────────────────────────────────────────────
# 测试类
# ──────────────────────────────────────────────────────────────────────────────


class TestDryRunAnalyze:
    """dry-run 逻辑正确性测试（10 个典型场景）。"""

    @pytest.fixture
    def results(self) -> list[DryRunResult]:
        return [dry_run_analyze(m) for m in MOCK_FILES]

    def test_case1_a_module_mismatch_gov_pattern(self, results):
        """场景1: [A_module] MOD-GOV-xxx → MOD-L10-001 (FIX)。"""
        r = results[0]
        assert r.action == "FIX"
        assert r.current_a_module_id == "MOD-GOV-artifact_scanner"
        assert r.depgraph_module_id == "MOD-L10-001"
        assert r.current_blueprint_id == "MOD-L10-001"  # BLUEPRINT 已正确
        assert any("FIX" in d and "A_module" in d for d in r.details)
        assert any("OK" in d and "BLUEPRINT" in d for d in r.details)

    def test_case2_a_module_mismatch_unk_pattern(self, results):
        """场景2: [A_module] MOD-UNK-xxx → MOD-L04-001 (FIX)。"""
        r = results[1]
        assert r.action == "FIX"
        assert r.current_a_module_id == "MOD-UNK-risk_manager"
        assert r.depgraph_module_id == "MOD-L04-001"

    def test_case3_a_module_mismatch_sec_pattern(self, results):
        """场景3: [A_module] MOD-SEC-xxx → MOD-INF-023 (FIX)。"""
        r = results[2]
        assert r.action == "FIX"
        assert r.current_a_module_id == "MOD-SEC-scan_mutex"
        assert r.depgraph_module_id == "MOD-INF-023"

    def test_case4_blueprint_correct_a_module_wrong(self, results):
        """场景4: [BLUEPRINT] 正确，[A_module] 错误 → 只 FIX [A_module]。"""
        r = results[3]
        assert r.action == "FIX"
        assert r.current_blueprint_id == "MOD-GOVERNANCE"  # BLUEPRINT 正确
        assert r.current_a_module_id == "MOD-GOV-oms_risk_engine"  # A_module 错误
        assert r.depgraph_module_id == "MOD-GOVERNANCE"
        # BLUEPRINT 不需要修改
        assert any("OK" in d and "BLUEPRINT" in d for d in r.details)

    def test_case5_both_blueprint_and_a_module_wrong(self, results):
        """场景5: [BLUEPRINT] 和 [A_module] 都错 → 两行都 FIX。"""
        r = results[4]
        assert r.action == "FIX"
        assert r.current_blueprint_id == "MOD-UNK-default_tca_engine"
        assert r.current_a_module_id == "MOD-UNK-default_tca_engine"
        assert r.depgraph_module_id == "MOD-L07-001"
        assert any("FIX" in d and "BLUEPRINT" in d for d in r.details)
        assert any("FIX" in d and "A_module" in d for d in r.details)

    def test_case6_missing_a_module_header(self, results):
        """场景6: 缺 [A_module] 头 → ADD。"""
        r = results[5]
        assert r.action == "ADD"
        assert r.current_a_module_id is None
        assert r.current_blueprint_id == "MOD-GOV_SCRIPTS"  # BLUEPRINT 存在但 module_id 不匹配
        assert r.depgraph_module_id == "MOD-GOV_SCRIPTS"

    def test_case7_init_py_pattern(self, results):
        """场景7: __init__.py MOD-SELL_DECISION_api → MOD-SELL_DECISION (FIX)。"""
        r = results[6]
        assert r.action == "FIX"
        assert r.current_a_module_id == "MOD-SELL_DECISION_api"
        assert r.depgraph_module_id == "MOD-SELL_DECISION"

    def test_case8_already_consistent(self, results):
        """场景8: 已一致 → NO_CHANGE（幂等性）。"""
        r = results[7]
        assert r.action == "NO_CHANGE"
        assert r.current_a_module_id == "MOD-L04-001"
        assert r.current_blueprint_id == "MOD-L04-001"
        assert r.depgraph_module_id == "MOD-L04-001"

    def test_case9_yaml_anchor_skip(self, results):
        """场景9: 路径含 YAML anchor → SKIP。"""
        r = results[8]
        assert r.action == "SKIP"
        assert any("anchor" in d for d in r.details)

    def test_case10_file_not_found_skip(self, results):
        """场景10: 文件不存在 → SKIP。"""
        r = results[9]
        assert r.action == "SKIP"
        assert any("不存在" in d for d in r.details)

    def test_summary_counts(self, results):
        """汇总: 6 FIX + 1 ADD + 1 NO_CHANGE + 2 SKIP = 10。"""
        from collections import Counter

        actions = Counter(r.action for r in results)
        print("\n=== Dry-Run 汇总 ===")
        for r in results:
            print(format_result(r))
        print(f"\n=== Action 分布: {dict(actions)} ===")

        # case1=FIX, case2=FIX, case3=FIX, case4=FIX, case5=FIX, case7=FIX
        assert actions["FIX"] == 6
        # case6=ADD
        assert actions["ADD"] == 1
        # case8=NO_CHANGE
        assert actions["NO_CHANGE"] == 1
        # case9=SKIP, case10=SKIP
        assert actions["SKIP"] == 2
