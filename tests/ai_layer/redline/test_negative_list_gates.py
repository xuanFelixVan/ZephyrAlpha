# [A_test] module_id: zephyr.ai_layer.redline.negative_list_gates | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_negative_list_gates
# [MODULE] tests.ai_layer.redline.test_negative_list_gates
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.ai_layer.redline.negative_list_gates
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/ai_layer/redline/test_negative_list_gates.py
# [MATURITY] testing
# [INVARIANTS] 验收标准（DESIGN 红蓝 R1-F4）：S2 负面清单 gate=违例样例被拦；六条各有一条
#              样例（NL-2 QMT" "_REAL 引用/NL-5 判据字段结构变更/NL-3 宪法超行）+白名单放行+
#              fail-open+外来 staged 不阻断；审计经 project_root=tmp_path 隔离
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_negative_list_gates.py — S2 负面清单 gate 组（三台）单测。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.ai_layer.redline.negative_list_gates import (
    CONSTITUTION_LINE_LIMIT,
    make_constitution_line_limit_gate,
    make_real_key_reference_scan_gate,
    make_task_order_docs_lock_gate,
    scan_constitution_lines,
    scan_real_key_hits,
    structural_field_changes,
    task_order_lock_violation,
)

TASK_HEAD = (
    "task_id: TO-0001\n"
    "definition_of_done:\n"
    "  - 交付 A\n"
    "red_lines:\n"
    "  - 不碰 B\n"
    "acceptance:\n"
    "  tests_pass: true\n"
)
TASK_CHANGED = TASK_HEAD.replace("交付 A", "交付 A+顺手改判据")


def test_real_key_reference_blocked(tmp_path: Path, fake_gateway_factory):
    """NL-2 样例：own-diff 源码出现 QMT" "_REAL 引用 → 硬阻断+审计。"""
    gateway = fake_gateway_factory(
        staged={"src/zephyr/demo/loader.py": "KEY = 'QMT" "_REAL_PATH'\n"}
    )
    passed, detail = make_real_key_reference_scan_gate().check(
        gateway, ["src/zephyr/demo/loader.py"], session_id="s1"
    )
    assert passed is False
    assert "QMT" "_REAL" in detail
    audit = tmp_path / ".runtime/gate_audit/real_key_reference_scan.jsonl"
    assert audit.exists()
    record = json.loads(audit.read_text(encoding="utf-8").splitlines()[0])
    assert record["action"] == "block" and record["rule_id"] == "NL-2"


def test_real_key_whitelist_secret_registry_and_secrets_md(fake_gateway_factory):
    """NL-2 白名单：secret_registry.yaml 本体与 SECRETS.md 文档行放行。"""
    gateway = fake_gateway_factory(
        staged={
            "config/secret_registry.yaml": "QMT" "_REAL_PATH: {category: config}\n",
            "docs/SECRETS.md": "# 实盘键现名 QMT" "_REAL_PATH（文档行）\n",
        }
    )
    passed, detail = make_real_key_reference_scan_gate().check(
        gateway,
        ["config/secret_registry.yaml", "docs/SECRETS.md"],
        session_id="s1",
    )
    assert passed is True and detail == ""


def test_real_key_foreign_staged_not_blocking(fake_gateway_factory):
    """§3.1 own-scope：外来 staged 违规 warn+审计，不阻断无辜提交人。"""
    gateway = fake_gateway_factory(
        staged={"other_session/leak.py": "x = 'QMT" "_REAL_ACCOUNT'\n"}
    )
    passed, detail = make_real_key_reference_scan_gate().check(
        gateway, ["mine.py"], session_id="s-mine"
    )
    assert passed is True and detail == ""


def test_scan_real_key_hits_pure():
    hits = scan_real_key_hits(
        {
            "a.py": "QMT" "_REAL here",
            "SECRETS.md": "QMT" "_REAL doc",
            "b.py": "clean",
        }
    )
    assert hits == ["a.py"]


def test_task_order_docs_lock_blocked_when_judging_own_criteria(tmp_path: Path, fake_gateway_factory):
    """NL-5 样例：own-diff 同含施工产物与任务书判据字段结构变更 → 阻断。"""
    gateway = fake_gateway_factory(
        staged={
            "tasks/TO-0001.yaml": TASK_CHANGED,
            "src/zephyr/demo/feature.py": "print('artifact')\n",
        },
        head={"tasks/TO-0001.yaml": TASK_HEAD},
    )
    passed, detail = make_task_order_docs_lock_gate().check(
        gateway, ["tasks/TO-0001.yaml", "src/zephyr/demo/feature.py"], session_id="s1"
    )
    assert passed is False
    assert "definition_of_done" in detail


def test_task_order_change_without_artifacts_allowed_with_audit(tmp_path: Path, fake_gateway_factory):
    """NL-5 近傍：只改任务书不带施工产物 → 放行+near_miss 审计（供 S7/S8 消费）。"""
    gateway = fake_gateway_factory(
        staged={"tasks/TO-0002.yaml": TASK_CHANGED},
        head={"tasks/TO-0002.yaml": TASK_HEAD},
    )
    passed, detail = make_task_order_docs_lock_gate().check(
        gateway, ["tasks/TO-0002.yaml"], session_id="s1"
    )
    assert passed is True and detail == ""
    audit = tmp_path / ".runtime/gate_audit/task_order_docs_lock.jsonl"
    record = json.loads(audit.read_text(encoding="utf-8").splitlines()[0])
    assert record["action"] == "near_miss_warn"


def test_task_order_new_card_is_preregistration_allowed(fake_gateway_factory):
    """新任务书（HEAD 无基线）=判据预注册动作 → 放行（结构性变更判据不适用）。"""
    gateway = fake_gateway_factory(
        staged={
            "tasks/TO-0003.yaml": TASK_HEAD,
            "src/zephyr/demo/feature.py": "x = 1\n",
        }
    )
    passed, _ = make_task_order_docs_lock_gate().check(
        gateway, ["tasks/TO-0003.yaml", "src/zephyr/demo/feature.py"], session_id="s1"
    )
    assert passed is True


def test_structural_field_changes_is_parse_level_not_string_level():
    """解析级 diff：键序重排等字符串级差异不判变更；字段值结构变化才判。"""
    reformatted = (
        "task_id: TO-0001\n"
        "red_lines:\n"
        "  - 不碰 B\n"
        "definition_of_done:\n"
        "  - 交付 A\n"
        "acceptance:\n"
        "  tests_pass: true\n"
    )
    assert structural_field_changes(TASK_HEAD, reformatted) == []
    assert structural_field_changes(TASK_HEAD, TASK_CHANGED) == ["definition_of_done"]
    assert structural_field_changes(None, TASK_HEAD) == [], "新任务书=预注册，返回空"
    assert structural_field_changes(TASK_HEAD, "\t: : :\n") == [], "YAML 坏 → fail-open 空"


def test_task_order_lock_violation_pure():
    assert task_order_lock_violation(["definition_of_done"], True) is True
    assert task_order_lock_violation(["definition_of_done"], False) is False
    assert task_order_lock_violation([], True) is False


def test_constitution_line_limit_blocked_over_300(tmp_path: Path, fake_gateway_factory):
    """NL-3 判据②样例：AGENTS.md 修改后 301 行 → 阻断。"""
    over = "\n".join(f"line {i}" for i in range(CONSTITUTION_LINE_LIMIT + 1))
    gateway = fake_gateway_factory(staged={"AGENTS.md": over})
    passed, detail = make_constitution_line_limit_gate().check(gateway, ["AGENTS.md"], session_id="s1")
    assert passed is False
    assert f">{CONSTITUTION_LINE_LIMIT}" in detail


def test_constitution_line_limit_allows_exactly_300(fake_gateway_factory):
    exact = "\n".join(f"line {i}" for i in range(CONSTITUTION_LINE_LIMIT))
    gateway = fake_gateway_factory(staged={"AGENTS.md": exact})
    passed, detail = make_constitution_line_limit_gate().check(gateway, ["AGENTS.md"], session_id="s1")
    assert passed is True and detail == ""


def test_constitution_lines_pure_counts():
    assert scan_constitution_lines("a\nb\nc") == 3
    assert scan_constitution_lines("") == 0


def test_git_failure_fail_open(fake_gateway_factory):
    """git diff 失败 → fail-open 放行（check 永不抛，交 gate 框架健康面）。"""

    class BrokenGateway:
        project_root = "."

        def run_git(self, args):  # noqa: ARG002
            raise RuntimeError("git unavailable")

    passed, detail = make_real_key_reference_scan_gate().check(BrokenGateway(), [], session_id="s1")
    assert passed is True and detail == ""


def test_gate_specs_shape():
    for factory, gate_id, priority in (
        (make_real_key_reference_scan_gate, "REAL-KEY-REFERENCE-SCAN", 149),
        (make_task_order_docs_lock_gate, "TASK-ORDER-DOCS-LOCK", 150),
        (make_constitution_line_limit_gate, "CONSTITUTION-LINE-LIMIT", 151),
    ):
        spec = factory()
        assert spec.gate_id == gate_id
        assert spec.priority == priority
        assert callable(spec.check)
