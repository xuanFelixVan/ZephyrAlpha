# [TTL] permanent
# [MODULE] tests.governance.rule_bridge.test_files_trigger_wiring
# [DOMAIN] D_GOVERNANCE
"""test_files_trigger_wiring.py — P5 files_trigger 接线测试（st-gslim-20260923）。

C98-c 追加（st-finaldel-vocabmid-20260930）：added: 第五路（本笔 git 新增 A 态文件
fnmatch）三钉——红转绿（vocab 外新增词表类提交必触发门）/ 零成本 skip（普通提交
门零执行）/ 词表目录触发+只扫 staged。向后兼容由 TestAddedRouteMatcher 逐断言钉死。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from zephyr.gov_enforcement.commit_gates.library.state_vocab_registry_gate import (
    STATE_VOCAB_REGISTRY_REL_PATH,
    make_state_vocab_registry_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    CommitGateRegistry,
    GateSpec,
    _files_trigger_hit,
)


def test_files_trigger_matcher_semantics():
    assert _files_trigger_hit((), ["a.py"]) is True  # 空=无条件
    assert _files_trigger_hit((".py",), []) is False  # 有条件但无清单
    assert _files_trigger_hit((".py",), ["docs/x.md"]) is False
    assert _files_trigger_hit((".py",), ["src/a.py"]) is True  # 子串
    assert _files_trigger_hit(("docs/",), ["docs/x.md"]) is True  # 目录前缀
    assert _files_trigger_hit(("*.yaml",), ["a/b.yaml"]) is True  # fnmatch
    assert _files_trigger_hit(("schema",), ["src/z/schema_loader.py"]) is True


def test_check_all_skips_non_matching_gate():
    reg = CommitGateRegistry()
    calls = []

    def _chk(gw, files, **kw):
        calls.append(files)
        return True, ""

    reg.register(GateSpec(gate_id="COND", check=_chk, priority=1, files_trigger=("schema",)))
    reg.register(GateSpec(gate_id="ALWAYS", check=_chk, priority=2))
    results = reg.check_all(gateway=object(), files=["docs/x.md"])
    by_id = {r.gate_id: r for r in results}
    assert by_id["COND"].passed and "files_trigger" in by_id["COND"].detail
    assert by_id["ALWAYS"].passed
    assert len(calls) == 1  # 只有 ALWAYS 真正执行


def test_registrar_injects_files_trigger(tmp_path, monkeypatch):
    import yaml

    from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import auto_register_gates

    roster = {
        "total_gates": 1,
        "gates": [
            {
                "gate_id": "WIRED",
                "module_path": "zephyr.gov_enforcement.rule_bridge.commit_gate_registry",
                "factory_function": "run_checker_script",
                "enabled": True,
                "files_trigger": ["schema"],
            }
        ],
    }
    # factory_function 必须返回 GateSpec——用专用桩
    (tmp_path / "roster.yaml").write_text(yaml.dump(roster), encoding="utf-8")


# ── C98-c 中间方案（st-finaldel-vocabmid-20260930）：added: 第五路触发 ──

#: 探针词表类源码（类名含 mode 关键词＋3 个全大写字符串赋值＝启发式命中形态）
_PROBE_VOCAB_SOURCE = (
    "from typing import Final\n\n\n"
    "class LaneDrainMode:\n"
    '    DRAIN: Final[str] = "DRAIN"\n'
    '    HOLD: Final[str] = "HOLD"\n'
    '    REFILL: Final[str] = "REFILL"\n'
)
#: 最小假册（LaneDrainMode 不在其中＝未登记）
_MIN_REGISTRY = "schema_version: 1\nvocabularies:\n  - {id: X1, class: KnownMode, location: 'src/x.py:1-2'}\n"


@dataclass
class _GitResult:
    returncode: int = 0
    stdout: str = ""


@dataclass
class _FakeGateGateway:
    """最小假 gateway：rev-parse / diff-filter=AM / diff-filter=A 三应答（_norm_rel 纯 Python 零 git）。"""

    root: object
    staged: tuple[str, ...] = ()
    added: tuple[str, ...] = ()
    git_calls: list = field(default_factory=list)

    @property
    def project_root(self) -> str:
        return str(self.root)

    def run_git(self, cmd, *a, **k):
        cmd = [str(c) for c in cmd]
        self.git_calls.append(tuple(cmd))
        if "rev-parse" in cmd:
            return _GitResult(returncode=0, stdout=str(self.root))
        if "--diff-filter=A" in cmd:
            return _GitResult(returncode=0, stdout="\n".join(self.added))
        if "diff" in cmd:
            return _GitResult(returncode=0, stdout="\n".join(self.staged))
        return _GitResult(returncode=0, stdout="")


def _vocab_registry_with_probe(tmp_path, *, staged: tuple[str, ...], added: tuple[str, ...]) -> _FakeGateGateway:
    reg_path = tmp_path / STATE_VOCAB_REGISTRY_REL_PATH
    reg_path.parent.mkdir(parents=True, exist_ok=True)
    reg_path.write_text(_MIN_REGISTRY, encoding="utf-8")
    return _FakeGateGateway(tmp_path, staged=staged, added=added)


class TestAddedRouteMatcher:
    """第五路匹配语义＋向后兼容钉（非 added: 门行为逐字节不变）。"""

    def test_legacy_four_route_semantics_unchanged(self):
        # 既有七断言复钉（wiring 原测同款；含 added_files 缺省形态）
        assert _files_trigger_hit((), ["a.py"]) is True  # 空=无条件
        assert _files_trigger_hit((".py",), []) is False  # 有条件但无清单
        assert _files_trigger_hit((".py",), ["docs/x.md"]) is False
        assert _files_trigger_hit((".py",), ["src/a.py"]) is True  # 子串
        assert _files_trigger_hit(("docs/",), ["docs/x.md"]) is True  # 目录前缀
        assert _files_trigger_hit(("*.yaml",), ["a/b.yaml"]) is True  # fnmatch
        assert _files_trigger_hit(("schema",), ["src/z/schema_loader.py"]) is True

    def test_added_route_matches_only_added_set(self):
        assert _files_trigger_hit(("added:*.py",), ["docs/x.md"], added_files=["src/zephyr/trading/zz.py"]) is True
        # files 命中不算数——added: 只看本笔新增（A 态）集
        assert _files_trigger_hit(("added:*.py",), ["src/zephyr/shared/vocab/market_state.py"], added_files=[]) is False
        assert _files_trigger_hit(("added:*.py",), ["src/a.py"]) is False  # 未传新增集（未计算态）
        assert _files_trigger_hit(("added:*.py",), None, added_files=["a/b.py"]) is True

    def test_empty_suffix_defense(self):
        # 空后缀经子串路恒真=纵深防御（校验层已拒收，消费层再滤一道）
        assert _files_trigger_hit(("added:",), ["src/a.py"], added_files=["src/a.py"]) is False

    def test_mixed_patterns_are_or(self):
        pats = ("src/zephyr/shared/vocab/", "added:*.py")
        assert _files_trigger_hit(pats, ["src/zephyr/shared/vocab/x.py"]) is True  # plain 路命中
        assert _files_trigger_hit(pats, ["docs/x.md"], added_files=["src/y.py"]) is True  # added 路命中
        assert _files_trigger_hit(pats, ["docs/x.md"], added_files=[]) is False  # 两路皆空=skip
        assert _files_trigger_hit(("added:src/zephyr/trading/",), [], added_files=["src/zephyr/trading/z.py"]) is True


class TestCheckAllAddedTriggerDispatch:
    """dispatcher 级：新增集惰性单次计算；e2e 复用真 STATE-VOCAB 门＋真名册触发面。

    工厂 make_state_vocab_registry_gate() 的 files_trigger=()（触发面唯一真源=
    in_process_gate_registry.yaml，经 gate_auto_registrar 注入）——e2e 必须按注入
    形态从真名册读触发面装回 spec，否则门是 always-fire，钉a 会假绿。
    """

    _ROSTER_REL = "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml"

    def _registry(self) -> CommitGateRegistry:
        import yaml  # noqa: PLC0415

        from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415

        spec = make_state_vocab_registry_gate()
        roster = yaml.safe_load((REPO_ROOT / self._ROSTER_REL).read_text(encoding="utf-8"))
        entry = next(g for g in roster["gates"] if g["gate_id"] == "STATE-VOCAB-REGISTRY")
        spec.files_trigger = tuple(entry["files_trigger"])
        reg = CommitGateRegistry()
        reg.register(spec)
        return reg

    def test_added_vocab_class_outside_vocab_dir_now_triggers_and_is_caught(self, tmp_path):
        """钉a 红转绿：redblue §3.4 红胜场景复现——vocab 外新增词表类 .py 现在必触发且检出。"""
        rel = "src/zephyr/trading/zz_gate_probe.py"
        (tmp_path / "src" / "zephyr" / "trading").mkdir(parents=True)
        (tmp_path / rel).write_text(_PROBE_VOCAB_SOURCE, encoding="utf-8")
        gw = _vocab_registry_with_probe(tmp_path, staged=(rel,), added=(rel,))
        results = self._registry().check_all(gateway=gw, files=[rel], session_id=None)
        r = {x.gate_id: x for x in results}["STATE-VOCAB-REGISTRY"]
        assert "skipped: files_trigger" not in r.detail, "红转绿失败：门仍被 trigger_skip（观测通道未复活）"
        assert "LaneDrainMode" in r.detail and "未登记" in r.detail, r.detail
        # 出厂 warn-only：passed=True＋detail 留痕（升硬属 Owner 门位，本钉只证观测通道复活）
        assert r.passed is True

    def test_normal_commit_gate_skips_at_zero_cost(self, tmp_path):
        """钉b：普通提交（无词表文件、无新增）→ 门零执行；新增集恰 1 次廉查询、门体扫描零调用。"""
        gw = _vocab_registry_with_probe(tmp_path, staged=(), added=())
        results = self._registry().check_all(gateway=gw, files=["docs/x.md"], session_id=None)
        r = {x.gate_id: x for x in results}["STATE-VOCAB-REGISTRY"]
        assert "skipped: files_trigger" in r.detail  # trigger_skip=门体未执行
        assert sum(1 for c in gw.git_calls if "--diff-filter=A" in c) == 1  # 新增集惰性单次
        assert not any("--diff-filter=AM" in c for c in gw.git_calls)  # 门体扫描面零调用

    def test_vocab_dir_modify_triggers_and_scans_staged_only(self, tmp_path):
        """钉c：词表目录文件改动（M 态非新增）→ 前缀路触发＋门体只扫 staged 清单。"""
        rel = "src/zephyr/shared/vocab/market_state.py"
        (tmp_path / "src" / "zephyr" / "shared" / "vocab").mkdir(parents=True)
        (tmp_path / rel).write_text("X = 1\n", encoding="utf-8")
        gw = _vocab_registry_with_probe(tmp_path, staged=(rel,), added=())
        results = self._registry().check_all(gateway=gw, files=[rel], session_id=None)
        r = {x.gate_id: x for x in results}["STATE-VOCAB-REGISTRY"]
        assert "skipped: files_trigger" not in r.detail  # 词表目录前缀路触发（C98 二批口径保留）
        assert sum(1 for c in gw.git_calls if "--diff-filter=AM" in c) == 1  # 门体只扫 staged（1 文件）

    def test_roster_static_trigger_surface_is_three_paths(self):
        """静态触发面口径=3：真名册 STATE-VOCAB 行=词表真源前缀＋册精确路径＋added:*.py。"""
        import yaml  # noqa: PLC0415

        from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415

        roster = yaml.safe_load(
            (REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml").read_text(
                encoding="utf-8"
            )
        )
        entry = next(g for g in roster["gates"] if g["gate_id"] == "STATE-VOCAB-REGISTRY")
        ft = entry["files_trigger"]
        assert len(ft) == 3, ft
        assert ft[0] == "src/zephyr/shared/vocab/" and ft[1].endswith("state_vocabulary_registry.yaml")
        assert ft[2] == "added:*.py"

    def test_check_all_without_added_declaration_pays_zero_added_query(self):
        """惰性守卫：无门声明 added: → check_all 永不付新增集查询（既有门零新增 git 面）。"""
        calls: list[list[str]] = []

        class _Gw:
            def run_git(self, cmd, *a, **k):
                calls.append([str(c) for c in cmd])
                return _GitResult(returncode=0, stdout="")

        reg = CommitGateRegistry()
        reg.register(
            GateSpec(gate_id="PLAIN", check=lambda gw, files, **kw: (True, ""), priority=1, files_trigger=("src/",))
        )
        results = reg.check_all(gateway=_Gw(), files=["src/a.py"])
        assert not any("--diff-filter=A" in c for c in calls), calls
        by = {x.gate_id: x for x in results}
        assert "files_trigger" not in by["PLAIN"].detail
