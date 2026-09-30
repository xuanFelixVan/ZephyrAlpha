# [BLUEPRINT] MOD-TEST-001 | tests/governance/rule_bridge/test_files_trigger_validation.py | §
# [MODULE] tests.governance.rule_bridge.test_files_trigger_validation
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar, zephyr.gov_enforcement.rule_bridge.commit_gate_registry
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯单元测试（tmp_path + monkeypatch，测试不写生产路径）；验证 QMine M5 矿② files_trigger 注入校验 fail-closed 契约：结构违例（非 list[str]/空串/边缘空白/反斜杠/控制符/纯 glob 恒真）→ GateAutoRegistrationError（报 gate_id）；死触发/超宽只 warn 不拦
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试永不抛未捕获异常
# [TESTS] self
# [A_module] module_id=MOD-TEST-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_files_trigger_validation.py — files_trigger 注入校验单元测试（QMine M5 矿②）。

覆盖：
1. 好 trigger（合法 list[str]）→ 注册成功且 spec.files_trigger 注入
2. 缺省/null/空 list = always-fire 合法（与消费侧 _files_trigger_hit 语义同义）
3. 坏 trigger（非 list 标量 str/int/dict、非 str 条目、空串、边缘空白、反斜杠、
   控制符、纯 glob 恒真 `*`/`**/*`）→ GateAutoRegistrationError（fail-closed，裁定#351 通道）
4. 死触发（HEAD 树零命中）/超宽（命中 ≥ 阈值）→ logger.warning 不拦（warn 通道）
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_bridge import gate_auto_registrar as gar
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry
from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import (
    REGISTRY_REL_PATH,
    GateAutoRegistrationError,
    auto_register_gates,
)

_HELD = {
    "module_path": "zephyr.gov_enforcement.commit_gates.held_overlap_gate",
    "factory_function": "make_held_overlap_gate",
}
_ROSTER_HEAD = "total_gates: {n}\ngates:\n"


def _write_roster(tmp_path: Path, trigger_yaml: str, gate_id: str = "HELD-OVERLAP") -> None:
    """写测试名册：单 gate + 任意 files_trigger YAML 片段。"""
    body = (
        f"  - gate_id: {gate_id}\n"
        f"    module_path: {_HELD['module_path']}\n"
        f"    factory_function: {_HELD['factory_function']}\n"
        "    enabled: true\n" + trigger_yaml
    )
    path = tmp_path / REGISTRY_REL_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_ROSTER_HEAD.format(n=1) + body, encoding="utf-8")


def _no_git(*_a, **_k):
    """warn 通道 git 面断供（None=静默跳过），让结构校验测试不付 subprocess 成本。"""
    return None


class TestGoodTriggers:
    """好 trigger：过校验、注入 spec。"""

    @pytest.fixture(autouse=True)
    def _no_git_face(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gar, "_head_tracked_relpaths", _no_git)

    def test_valid_list_registers_and_injects(self, tmp_path: Path) -> None:
        """合法 list[str] → 注册成功，spec.files_trigger=同序 tuple。"""
        _write_roster(tmp_path, "    files_trigger:\n      - docs/\n      - '*.yaml'\n")
        registry = CommitGateRegistry()
        assert auto_register_gates(registry, tmp_path) == []
        spec = registry.get("HELD-OVERLAP")
        assert spec is not None
        assert spec.files_trigger == ("docs/", "*.yaml")

    def test_missing_trigger_is_always_fire(self, tmp_path: Path) -> None:
        """缺省=always-fire（合法），spec.files_trigger 保持 GateSpec 默认空 tuple。"""
        _write_roster(tmp_path, "")
        registry = CommitGateRegistry()
        assert auto_register_gates(registry, tmp_path) == []
        assert not registry.get("HELD-OVERLAP").files_trigger

    def test_null_and_empty_list_are_always_fire(self, tmp_path: Path) -> None:
        """null 与空 list 均合法（消费侧 `not patterns: return True` 同义）。"""
        for trigger_yaml in ("    files_trigger: null\n", "    files_trigger: []\n"):
            registry = CommitGateRegistry()
            _write_roster(tmp_path, trigger_yaml)
            assert auto_register_gates(registry, tmp_path) == []
            assert not registry.get("HELD-OVERLAP").files_trigger

    def test_added_prefix_pattern_registers_and_injects(self, tmp_path: Path) -> None:
        """C98-c：added: 前缀条目合法且原样注入（第五路=本笔新增态，st-finaldel-vocabmid-20260930）。"""
        _write_roster(tmp_path, "    files_trigger:\n      - 'added:*.py'\n")
        registry = CommitGateRegistry()
        assert auto_register_gates(registry, tmp_path) == []
        assert registry.get("HELD-OVERLAP").files_trigger == ("added:*.py",)


class TestBadTriggersFailClosed:
    """坏 trigger：全部经既有 except 收集 → GateAutoRegistrationError（零新增控制流）。"""

    CASES = [
        ("scalar_string", "    files_trigger: docs/\n", "must be list"),
        ("scalar_int", "    files_trigger: 42\n", "must be list"),
        ("scalar_dict", "    files_trigger: {a: b}\n", "must be list"),
        ("non_str_entries", "    files_trigger:\n      - docs/\n      - 42\n", "非 str 条目"),
        ("empty_string", '    files_trigger:\n      - ""\n', "空串或带边缘空白"),
        ("edge_whitespace", "    files_trigger:\n      - ' docs/'\n", "空串或带边缘空白"),
        ("backslash", "    files_trigger:\n      - 'docs\\sub'\n", "反斜杠"),
        ("control_char", '    files_trigger:\n      - "docs\\tsub"\n', "控制符"),
        ("pure_glob_star", "    files_trigger:\n      - '*'\n", "纯 glob"),
        ("pure_glob_doublestar", "    files_trigger:\n      - '**/*'\n", "纯 glob"),
        ("added_bare_prefix", "    files_trigger:\n      - 'added:'\n", "缺模式后缀"),
        ("added_pure_glob_suffix", "    files_trigger:\n      - 'added:**'\n", "纯 glob"),
    ]

    @pytest.fixture(autouse=True)
    def _no_git_face(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gar, "_head_tracked_relpaths", _no_git)

    @pytest.mark.parametrize(("name", "trigger_yaml", "match"), CASES, ids=[c[0] for c in CASES])
    def test_bad_trigger_rejected_with_gate_id(self, tmp_path: Path, name: str, trigger_yaml: str, match: str) -> None:
        """结构违例 → fail-closed 抛 GateAutoRegistrationError 且逐台报 gate_id。"""
        _write_roster(tmp_path, trigger_yaml)
        registry = CommitGateRegistry()
        with pytest.raises(GateAutoRegistrationError, match=match) as ei:
            auto_register_gates(registry, tmp_path)
        assert "HELD-OVERLAP" in str(ei.value)
        assert "register failed" in str(ei.value)  # 流入既有 failures 收集通道

    def test_scalar_dict_never_silently_coerced(self, tmp_path: Path) -> None:
        """旧病根回归锁：非 list 标量禁静默 (str(ft),) coercion（观测簿 §1③）。"""
        _write_roster(tmp_path, "    files_trigger: {module: x}\n")
        with pytest.raises(GateAutoRegistrationError, match="must be list\\[str\\]"):
            auto_register_gates(CommitGateRegistry(), tmp_path)


class TestWarnChannel:
    """死触发/超宽只 warn 不拦（观测簿方案②：先可见再治理）。"""

    def _register(self, tmp_path: Path, trigger_yaml: str) -> None:
        _write_roster(tmp_path, trigger_yaml)
        assert auto_register_gates(CommitGateRegistry(), tmp_path) == []  # warn 不阻断装载

    def test_dead_trigger_warns_but_loads(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog) -> None:
        """HEAD 树零命中 → warn「死触发」，注册不受影响。"""
        monkeypatch.setattr(gar, "_head_tracked_relpaths", lambda *_a, **_k: {"docs/a.md", "src/x.py"})
        with caplog.at_level(logging.WARNING, logger=gar.logger.name):
            self._register(tmp_path, "    files_trigger:\n      - zzz_never_matches\n")
        assert any("死触发" in r.message and "zzz_never_matches" in r.message for r in caplog.records)

    def test_overwide_trigger_warns_but_loads(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog) -> None:
        """命中数 ≥ 阈值 → warn「超宽」，注册不受影响（阈值 monkeypatch 降档便于测试）。"""
        monkeypatch.setattr(gar, "_OVERWIDE_WARN_THRESHOLD", 1)
        monkeypatch.setattr(gar, "_head_tracked_relpaths", lambda *_a, **_k: {"src/a.py", "src/b.py", "docs/d.md"})
        with caplog.at_level(logging.WARNING, logger=gar.logger.name):
            self._register(tmp_path, "    files_trigger:\n      - src/\n")
        assert any("超宽" in r.message and "src/" in r.message for r in caplog.records)

    def test_no_triggers_skips_git_face(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """名册零 trigger → 不付任何 git 面（lazy 短路）。"""
        called = []
        monkeypatch.setattr(gar, "_head_tracked_relpaths", lambda *a, **k: called.append(1) or None)
        self._register(tmp_path, "")
        assert not called

    def test_added_prefix_pattern_skips_head_tree_warn(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog
    ) -> None:
        """C98-c：added: 模式对 HEAD 树静态计数无口径 → 不进死触发/超宽 warn 面（防伪 warn）。"""
        monkeypatch.setattr(gar, "_head_tracked_relpaths", lambda *_a, **_k: {"src/a.py"})
        with caplog.at_level(logging.WARNING, logger=gar.logger.name):
            self._register(tmp_path, "    files_trigger:\n      - 'added:zzz_never_matches'\n")
        assert not caplog.records  # 旧逻辑会误报死触发（把 added: 后缀当 HEAD 模式数零命中）

    def test_git_face_failure_is_silent(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog) -> None:
        """git 面不可用 → warn 通道静默跳过，绝不影响装载（观测不是门禁）。"""

        def _boom(*_a, **_k):
            raise RuntimeError("no git")

        monkeypatch.setattr(gar, "_head_tracked_relpaths", _boom)
        with caplog.at_level(logging.WARNING, logger=gar.logger.name):
            self._register(tmp_path, "    files_trigger:\n      - docs/\n")
        assert not caplog.records
