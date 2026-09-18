# [A_test] module_id: zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §registry_mass_deletion_gate
# [MODULE] tests.governance.commit_gates.test_registry_mass_deletion_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/commit_gates/test_registry_mass_deletion_gate.py
# [MATURITY] testing
# [INVARIANTS] 只测纯逻辑核心 _is_watch_file/_yaml_entry_count/_line_delta/_entry_identity_keys（不触 git）
# [MODIFY-GUARD] META-TESTS-COVERAGE 补课（gate [TESTS] 声明兑现，2026-09-12 st-perf-plan-20260910）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_registry_mass_deletion_gate.py — REGISTRY-MASS-DELETION 门禁纯逻辑单测（META-TESTS 声明兑现）。"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate import (
    _entry_identity_keys,
    make_registry_mass_deletion_gate,
    _is_watch_file,
    _line_delta,
    _yaml_entry_count,
)

NL = chr(10)  # 测试内构造 YAML 文本的行尾（避免源码里嵌 \t/\n 字面量歧义）


class TestIsWatchFile:
    def test_registry_yaml_hit(self):
        assert _is_watch_file("docs/01_policies_and_standards/_registry/catalogs/universe_registry.yaml")

    def test_non_registry_miss(self):
        assert not _is_watch_file("src/zephyr/data/loader.py")


class TestYamlEntryCount:
    def test_count_entries(self):
        text = "universe_registry:\n  - universe_id: U-001\n  - universe_id: U-002\n"
        assert _yaml_entry_count(text) == 2

    def test_unparsable_returns_none(self):
        assert _yaml_entry_count("\t: : :\n") is None


class TestLineDelta:
    def test_delta(self):
        head = "a\nb\nc\n"
        staged = "a\nb\nc\nd\n"
        deleted, added = _line_delta(head, staged)
        assert added == 1 and deleted == 0, "返回序=(deleted, added)（docstring 口径）"


class TestEntryIdentityKeys:
    """红队加固③（st-ff-rb-gov-20260918）：条目身份集——计数型判据的盲区补口。"""

    @staticmethod
    def _entry(cid: str) -> list[str]:
        return [f"- capability_id: {cid}", f"  path: {cid}.md"]

    def test_identity_set_uses_first_scalar_field(self):
        text = NL.join(self._entry("alpha") + self._entry("beta")) + NL
        assert _entry_identity_keys(text) == {"capability_id=alpha", "capability_id=beta"}

    def test_unparsable_or_non_list_returns_none(self):
        assert _entry_identity_keys("foo: bar" + NL) is None
        assert _entry_identity_keys(chr(9) + ": : :" + NL) is None

    def test_e1_counting_criteria_blind_spot_is_caught(self):
        """E1 实弹复现：删他人 2 条 + 插自己 3 条 → 计数判据放行，身份信号必须红。

        能红证据：前两条断言=旧判据"放行"的机械证明（净删 4 行 ≤ 净插 6 行、
        条目数 11 > 10 不减）；摘掉 gate 的信号3，第三条断言即失败。
        """
        head = NL.join(sum((self._entry(f"keep_{i}") for i in range(10)), [])) + NL
        kept = sum((self._entry(f"keep_{i}") for i in range(10) if i not in (3, 7)), [])
        mine = sum((self._entry(f"mine_{i}") for i in range(3)), [])
        staged = NL.join(kept + mine) + NL
        deleted, added = _line_delta(head, staged)
        assert deleted <= added, f"前置：净删行信号应放行（deleted={deleted} added={added}）"
        assert _yaml_entry_count(staged) >= _yaml_entry_count(head), "前置：条目数信号应放行"
        lost = _entry_identity_keys(head) - _entry_identity_keys(staged)
        assert lost == {"capability_id=keep_3", "capability_id=keep_7"}, "身份信号必须抓到被蒸发条目"


class _RbgovIdentityStubGateway:
    """真 git 仓 + run_git 透传（gate 闭包按 gateway.run_git 口径调用）。"""

    def __init__(self, root):
        self.project_root = root

    def run_git(self, cmd, timeout=30):  # noqa: ARG002 — gate 只传 cmd
        return subprocess.run(cmd, cwd=str(self.project_root), capture_output=True,
                              text=True, encoding="utf-8", errors="replace")


_REG_REL = "docs/01_policies_and_standards/_registry/catalogs/red_test_registry.yaml"


def _e2e_check(tmp_path: Path, head_entries: list[int], staged_entries: list[int], extra_mine: int = 0):
    """建一次性 git 仓：HEAD 版登记表 + staged 版登记表 → 跑 gate 闭包。"""
    repo = tmp_path / "repo"
    reg = repo / _REG_REL
    reg.parent.mkdir(parents=True, exist_ok=True)

    def render(ids, mine):
        lines = ["# red test registry", ""]
        lines += sum([[f"- capability_id: keep_{i}", f"  path: x{i}.md"] for i in ids], [])
        lines += sum([[f"- capability_id: mine_{i}", f"  path: m{i}.md"] for i in range(mine)], [])
        return NL.join(lines) + NL

    reg.write_text(render(head_entries, 0), encoding="utf-8")
    git = lambda *a: subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)  # noqa: E731
    git("init", "-q"); git("config", "user.email", "t@t"); git("config", "user.name", "t")
    git("add", "--", _REG_REL); git("commit", "-q", "-m", "head version")
    reg.write_text(render(staged_entries, extra_mine), encoding="utf-8")
    git("add", "--", _REG_REL)
    gate = make_registry_mass_deletion_gate()
    return gate.check(_RbgovIdentityStubGateway(repo), [_REG_REL], session_id=None, commit_message="")


class TestMassDeletionIdentitySignalE2E:
    """gate 闭包级 E2E：证明"计数放行/身份红"这条判据真的接在提交链路上。"""

    def test_e1_batch_now_blocked_end_to_end(self, tmp_path):
        """HEAD 10 条 → staged 删 2 条插 3 条：旧判据放行，本信号必须阻断（能红点）。"""
        passed, detail = _e2e_check(tmp_path, head_entries=list(range(10)),
                                    staged_entries=[i for i in range(10) if i not in (3, 7)],
                                    extra_mine=3)
        assert not passed, f"身份消失必须阻断，实得 passed={passed}"
        assert "身份消失 2 条" in detail, detail

    def test_pure_insert_still_passes(self, tmp_path):
        """正控：只插不删（真实登记常态）必须仍放行——加严不打死正门。"""
        passed, detail = _e2e_check(tmp_path, head_entries=list(range(10)),
                                    staged_entries=list(range(10)), extra_mine=3)
        assert passed, f"纯插入不应阻断，实得 detail={detail}"

    def test_marker_escape_still_works(self, tmp_path):
        """正控：[allow-mass-deletion:reason≥10字] 逃生通道未被本信号收紧掉。"""
        repo = tmp_path / "repo2"
        reg = repo / _REG_REL
        reg.parent.mkdir(parents=True, exist_ok=True)
        reg.write_text("- capability_id: keep_0" + NL + "  path: x0.md" + NL, encoding="utf-8")
        for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"],
                  ["add", "--", _REG_REL], ["commit", "-q", "-m", "h"]):
            subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)
        reg.write_text("- capability_id: mine_0" + NL + "  path: m0.md" + NL, encoding="utf-8")
        subprocess.run(["git", "add", "--", _REG_REL], cwd=str(repo), capture_output=True, text=True)
        gate = make_registry_mass_deletion_gate()
        passed, detail = gate.check(_RbgovIdentityStubGateway(repo), [_REG_REL], session_id=None,
                                    commit_message="[allow-mass-deletion:合法整表重排已备份可比对回滚]")
        assert passed, "白名单标记仍应放行（只加严判据，不动逃生语义）"
        assert "warn" in detail
