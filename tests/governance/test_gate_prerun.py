# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/gate_prerun.py | §gate_prerun 预跑器能力守卫
# [MODULE] tests.governance.test_gate_prerun
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; scripts.governance.meta.gate_prerun
# [CONSUMERS] gate_prerun 预跑器质量守卫（能红/能绿/异常不吞/环境信号分箱/claim 成功清单语义）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部用例注入合成 GateSpec 与假 gateway，零真门执行、零生产写；
#   "能红"是本文件的主体判据——任何一条把 FAIL 断言改成 PASS 断言即失去意义；
#   违规文件真身建在 tmp_path（测试禁写生产路径）
# [MODIFY-GUARD] 与 gate_prerun.py 同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError（预跑器失去判别力时必红，不静默）
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""gate_prerun 预跑器守卫——**没被证明能红的检查器等于没有检查器**（0.3 程序法）。

本文件的存在理由：预跑器是"入队前标准一步"的载体，它一旦退化为恒绿，
整条防线会以"全 PASS"的面貌静默失效（本役 5 例热册蒸发的共同形状）。
因此这里不只测"干净清单通过"，更测：注入真存在磁盘上的违规文件 ⇒ **必红**、
门抛异常 ⇒ 计失败（不吞成 PASS）、预跑器自身被阉割时自检 ⇒ **必判 3**。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.governance.meta.gate_prerun as gp

_SESSION = "st-ffb19-20260919"
_BARE_SQL_MARK = "SELECT * FROM"


class _FakeSpec:
    """合成 GateSpec——形状与真 spec 一致（gate_id + check(gateway, files, **flags)）。"""

    def __init__(self, gate_id: str, verdict: tuple[bool, str] | None = None, raises: bool = False) -> None:
        self.gate_id = gate_id
        self.priority = 100
        self._verdict = verdict or (True, "")
        self._raises = raises

    def check(self, gateway: object, files: list[str], **flags: object) -> tuple[bool, str]:
        """按注入的判定表返回（raises=True 时抛异常，验证预跑器不吞异常）。"""
        if self._raises:
            raise RuntimeError(f"injected gate crash in {self.gate_id}")
        return self._verdict


class _ContentSqlSpec(_FakeSpec):
    """内容驱动型合成门：真读磁盘上入参 files 的字节，含裸 SQL 标记即判红。

    判据来自 files 实参 + 磁盘真身，不是硬编码返回值——这样"注入违规文件必红"
    测的是预跑器的**接线**（清单是否真透传给门），而不是合成门的自觉。
    """

    def __init__(self, root: Path, gate_id: str = "SYNTH-BARE-SQL") -> None:
        super().__init__(gate_id)
        self._root = root

    def check(self, gateway: object, files: list[str], **flags: object) -> tuple[bool, str]:
        """逐文件读盘判定，命中即 (False, detail)。"""
        for rel in files:
            path = self._root / rel
            if path.exists() and _BARE_SQL_MARK in path.read_text(encoding="utf-8"):
                return False, f"{rel} 含裸 SQL 字面量"
        return True, ""


class _FakeGateway:
    """假 gateway：只提供预跑真正依赖的两个面——注册表快照与 claim_files 语义。"""

    def __init__(self, specs: list[object], claim_ok: list[str] | None = None) -> None:
        self.specs = specs
        self._claim_ok = claim_ok
        self.claim_calls: list[tuple[str, tuple[str, ...]]] = []

    def claim_files(self, session_id: str, files: list[str], adopt_prior_work: bool = False) -> list[str]:
        """复刻真语义：**返回成功清单**，失败者被排除（坑③）。"""
        self.claim_calls.append((session_id, tuple(files)))
        return list(files if self._claim_ok is None else self._claim_ok)


@pytest.fixture()
def lab(tmp_path: Path) -> Path:
    """磁盘上真有一违规件 + 一干净件的临时根（不落生产路径）。"""
    (tmp_path / "bad_module.py").write_text("SQL_LEAK = 'SELECT * FROM secret_table'\n", encoding="utf-8")
    (tmp_path / "clean_module.py").write_text("VALUE = 1\n", encoding="utf-8")
    return tmp_path


def _cfg(files: list[str], root: Path, **kw: object) -> gp.GatePrerunConfig:
    """构造预跑配置（默认带身份与 claim，逐用例按需关掉以证伪红）。"""
    claim = bool(kw.pop("claim", True))
    flags = dict(kw.pop("flags", {}) or {})  # type: ignore[arg-type]
    return gp.GatePrerunConfig(
        session_id=_SESSION,
        files=files,
        flags=flags,
        claim=claim,
        **kw,  # type: ignore[arg-type]
    )


# ── (a) 预跑器必须能红 / (b) 干净清单必须能绿 ─────────────────────────
def test_injected_violating_file_turns_red(lab: Path) -> None:
    """注入一个已知违规文件 ⇒ 预跑必须失败（B19 验收判据第一半）。"""
    spec = _ContentSqlSpec(lab)
    outcome = gp.run_specs([spec], None, _cfg(["bad_module.py"], lab))
    assert outcome.exit_code == 1, f"违规文件未被判红：{outcome.hard_fail}"
    assert len(outcome.hard_fail) == 1
    assert "bad_module.py" in outcome.hard_fail[0]
    assert spec.gate_id in outcome.hard_fail[0]


def test_clean_file_list_passes(lab: Path) -> None:
    """干净清单 ⇒ 预跑通过（与上一腿构成双向对照，单跑任一条都不构成证据）。"""
    outcome = gp.run_specs([_ContentSqlSpec(lab)], None, _cfg(["clean_module.py"], lab))
    assert outcome.exit_code == 0
    assert outcome.hard_fail == [] and outcome.errors == []


def test_gate_exception_is_not_swallowed_as_pass() -> None:
    """门抛异常必须计失败——吞异常是预跑器最坏的退化形状。"""
    outcome = gp.run_specs([_FakeSpec("SYNTH-BOOM", raises=True)], None, _cfg(["a.py"], Path(".")))
    assert outcome.exit_code == 1
    assert len(outcome.errors) == 1 and "RuntimeError" in outcome.errors[0]
    assert outcome.hard_fail == []


def test_self_check_returns_zero_when_discriminating(capsys: pytest.CaptureFixture[str]) -> None:
    """工具自带自检：干净腿绿 + 违规腿红 ⇒ 0（车道才可信任它的 PASS）。"""
    assert gp.self_check() == 0
    assert "具备报红能力" in capsys.readouterr().out


def test_self_check_flags_a_neutered_prerunner(monkeypatch: pytest.MonkeyPatch) -> None:
    """反向对照：把 run_specs 阉成恒绿 ⇒ self_check 必判 3（否则自检本身是假绿）。"""

    def _always_green(specs: list[object], gateway: object, cfg: gp.GatePrerunConfig) -> gp.GatePrerunOutcome:
        return gp.GatePrerunOutcome(total_specs=len(specs))

    monkeypatch.setattr(gp, "run_specs", _always_green)
    assert gp.self_check() == 3


# ── 三条使用坑的机检面 ────────────────────────────────────────────────
def test_flags_carry_session_id() -> None:
    """坑①：不传 session_id 造四类伪红 ⇒ flags MUST 含 session_id。"""
    flags = gp.build_flags(_cfg(["a.py"], Path(".")))
    assert flags.get("session_id") == _SESSION


def test_env_signal_gates_are_bucketed_not_hard() -> None:
    """坑①续：WORKTREE/SESSION/COMMIT-SCOPE/TRACKED-DRIFT 归 ENV 箱，不判死整批。"""
    assert "WORKTREE-REQUIRED" in gp.ENV_SIGNAL_GATES and "SESSION-REQUIRED" in gp.ENV_SIGNAL_GATES
    specs = [_FakeSpec("WORKTREE-REQUIRED", (False, "非 worktree"))]
    outcome = gp.run_specs(specs, None, _cfg(["a.py"], Path(".")))
    assert outcome.exit_code == 0 and len(outcome.env_fail) == 1
    strict = gp.run_specs(specs, None, _cfg(["a.py"], Path("."), strict_env=True))
    assert strict.exit_code == 1 and len(strict.hard_fail) == 1


def test_only_and_skip_filters_are_honoured() -> None:
    """--only/--skip 过滤生效（车道单门复跑的唯一通道）。"""
    specs = [_FakeSpec("G-KEEP", (False, "x")), _FakeSpec("G-DROP", (False, "y"))]
    only = gp.run_specs(specs, None, _cfg(["a.py"], Path("."), only=("G-KEEP",)))
    assert only.exit_code == 1 and len(only.skipped) == 1
    dropped = gp.run_specs(specs, None, _cfg(["a.py"], Path("."), skip=("G-KEEP", "G-DROP")))
    assert dropped.exit_code == 0 and len(dropped.skipped) == 2


def test_claim_files_return_is_success_list_not_conflict_list() -> None:
    """坑③：claim_files 返回成功清单 ⇒ "未 claim 成功"要自己算差集。"""
    gw = _FakeGateway([], claim_ok=["a.py"])
    unclaimed = gp.claim_for_prerun(gw, _cfg(["a.py", "b.py"], Path(".")))
    assert unclaimed == ["b.py"], f"把成功清单读成冲突清单了：{unclaimed}"
    assert gw.claim_calls[0][0] == _SESSION


def test_no_claim_skips_claim_call() -> None:
    """坑②的反向：显式 --no-claim 就要真的不 claim（否则旗标是装饰品）。"""
    gw = _FakeGateway([], claim_ok=[])
    assert gp.claim_for_prerun(gw, _cfg(["a.py"], Path("."), claim=False)) == []
    assert gw.claim_calls == []


# ── CLI 层：用法错误与端到端退出码 ───────────────────────────────────
def test_main_rejects_missing_session() -> None:
    """缺 --session ⇒ exit 2：预跑器不给它报四类伪红的机会。"""
    assert gp.main(["--files", "a.py"]) == 2


def test_main_rejects_empty_file_list() -> None:
    """空清单 ⇒ exit 2（对空集预跑得到的"全绿"是最危险的假绿）。"""
    assert gp.main(["--session", _SESSION, "--files", ""]) == 2


def test_main_reports_missing_message_file() -> None:
    """--message-file 不存在 ⇒ exit 2（不静默用空 message 跑内容型 message 门）。"""
    assert gp.main(["--session", _SESSION, "--files", "a.py", "--message-file", "nope/__missing.md"]) == 2


def test_unreachable_registry_maps_to_usage_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """gateway 不可达 ⇒ exit 2：环境异常不得伪装成内容全绿。"""

    def _boom(_root: Path) -> object:
        raise RuntimeError("gateway down")

    monkeypatch.setattr(gp, "make_gateway", _boom)
    assert gp.main(["--session", _SESSION, "--files", "a.py"]) == 2


def test_main_end_to_end_red_and_green(lab: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """端到端：真 CLI 入口 + 假 gateway（注册表注入违规门）⇒ 违规批 1、干净批 0。"""
    gw = _FakeGateway([_ContentSqlSpec(lab)])
    monkeypatch.setattr(gp, "make_gateway", lambda _root: gw)
    monkeypatch.setattr(gp, "collect_specs", lambda _gw: list(gw.specs))
    assert gp.main(["--session", _SESSION, "--files", "bad_module.py", "--quiet"]) == 1
    assert gp.main(["--session", _SESSION, "--files", "clean_module.py", "--quiet"]) == 0
    assert len(gw.claim_calls) == 2, "claim 前移 MUST 发生在每次预跑里"


def test_json_output_is_machine_readable(tmp_path: Path) -> None:
    """--json 落盘可被回执直接引用（机读面不得只存人读文本）。"""
    out = tmp_path / "prerun.json"
    outcome = gp.GatePrerunOutcome(total_specs=2)
    outcome.hard_fail.append("SYNTH: detail")
    gp.dump_json(str(out), outcome)
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["exit_code"] == 1 and payload["hard_fail"] == ["SYNTH: detail"]
