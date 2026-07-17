# [MODULE] tests.governance.generators.test_generate_gate_registry
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.generators.generate_gate_registry
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试 generate_gate_registry.py 核心函数（extract_commit_gates/generate）覆盖 CommitGate 同步治本（2026-07-17）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-GOV-test_generate_gate_registry | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_generate_gate_registry.py — generate_gate_registry.py 单元测试（CommitGate 同步治本 2026-07-17）

覆盖：
- extract_commit_gates: 扫描 commit_gates/*.py 提取 GateSpec 元数据（gate_id/priority/description）
- generate: 三源合并（pre-commit hooks + CommitGates + MANUAL_GATES）+ source 字段

治本背景：原生成器只读 .pre-commit-config.yaml（33 个 pre-commit hooks），漏掉全部 ~50 个
CommitGates（in-process gate 注册在 GitCommitGateway）。本次扩展后 gate_registry.yaml 覆盖
全部门禁，消除手工 blueprint §0.1 表的漂移风险。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# 添加项目根到 sys.path 以便 import 生成器模块
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.governance.generators.generate_gate_registry import (  # noqa: E402
    extract_commit_gates,
    generate,
)


def test_extract_commit_gates_returns_nonempty():
    """extract_commit_gates 应返回非空列表（实际 50 个 CommitGate）。"""
    gates = extract_commit_gates()
    assert len(gates) >= 40, f"CommitGate 数量异常少：{len(gates)}（预期 ~50）"


def test_extract_commit_gates_has_pure_assertion():
    """应含 PURE-ASSERTION（gate_id + priority=69）——治本触发用例。"""
    gates = extract_commit_gates()
    ids = [g["gate_id"] for g in gates]
    assert "PURE-ASSERTION" in ids, f"PURE-ASSERTION 缺失，实际 gate_ids: {ids[:10]}..."
    pa = next(g for g in gates if g["gate_id"] == "PURE-ASSERTION")
    assert "priority=69" in pa["name"], f"PURE-ASSERTION priority 异常：{pa['name']}"
    assert pa["source"] == "commit-gate"
    assert pa["category"] == "commit_gate"
    assert pa["entry"] == "in-process (GitCommitGateway)"


def test_extract_commit_gates_excludes_helpers():
    """应排除 __init__.py / _diff_helpers.py / gate_repo.py（无 GateSpec）。

    数量动态变化（其他会话可能新增 gate），用下限断言而非硬编码。
    """
    gates = extract_commit_gates()
    # 至少 50 个 GateSpec gate（治本时基准值，其他会话新增 gate 会更多）
    assert len(gates) >= 50, f"CommitGate 数量异常少：{len(gates)}（预期 >=50）"
    # 验证辅助文件确实被排除：_diff_helpers.py 无 GateSpec 会被自然跳过


def test_generate_merges_three_sources():
    """generate() 应合并三源：pre-commit + commit-gate + manual。"""
    output = generate()
    sources = {g.get("source") for g in output["gates"]}
    assert "pre-commit" in sources, "缺 pre-commit 源"
    assert "commit-gate" in sources, "缺 commit-gate 源"
    assert "manual" in sources, "缺 manual 源（MANUAL_GATES）"


def test_generate_no_duplicate_gate_id():
    """全量 gate_id 应无重复（pre-commit 与 CommitGate 命名空间不重叠）。"""
    output = generate()
    ids = [g["gate_id"] for g in output["gates"]]
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"重复 gate_id: {duplicates}"


def test_generate_total_gates_increased():
    """total_gates 应 >=80（33 pre-commit + 50 commit-gate + 1 manual = 84）。"""
    output = generate()
    assert output["total_gates"] >= 80, f"total_gates 异常：{output['total_gates']}（预期 84）"
    assert output["total_gates"] == len(output["gates"]), "total_gates 与 gates 列表长度不一致"


def test_generate_source_field_in_output_dict():
    """输出 dict 的 source 字段应声明三源。"""
    output = generate()
    assert "commit_gates" in output["source"], f"输出 source 字段未声明 commit_gates：{output['source']}"
    assert "MANUAL_GATES" in output["source"], f"输出 source 字段未声明 MANUAL_GATES：{output['source']}"


def test_extract_commit_gates_all_have_required_fields():
    """每条 CommitGate 应含全部必需字段。"""
    gates = extract_commit_gates()
    required = {"gate_id", "name", "entry", "description", "files_trigger",
                "always_run", "category", "status", "source"}
    for g in gates:
        missing = required - set(g.keys())
        assert not missing, f"gate {g.get('gate_id')} 缺字段: {missing}"
