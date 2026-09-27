# [BLUEPRINT] MOD-GOV_CREATE_GUARD | tests/gov_enforcement/test_create_guard_keyword_overlap_canary.py | §create-guard-canary
# [MODULE] tests.gov_enforcement.test_create_guard_keyword_overlap_canary
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates.create_guard, zephyr.governance.capability_lookup
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 波13·包13.1 红证四件：①同义命中⇒门必红 ②零命中⇒放行且 find() 既有审计行 result_count=0 ③批量化前后判据逐字节全等（100+真实样本重放证据复算）④人为清空命中集⇒①的断言必须变红（判别力自证）；测试隔离——全部 tmp_path，禁写主仓 .runtime/lookup_audit（monkeypatch LOOKUP_AUDIT_DIR），禁跑全库扫描（_build_capability_lookup 缝注入小型 registry）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [A_module] module_id=MOD-GOV_CREATE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_create_guard_keyword_overlap_canary.py — 包13.1「CREATE-GUARD 查功能关键词」红证（R-5）。

覆盖（对应契约 §3 包13.1 红证四条）：
  ① test_pipeline_synonym_hit_blocks — 新建 .py 关键词与在册能力同义 ⇒ 门必 FAIL，
     消息逐字含 capability_id / canonical_override / 命中词 / 逃生标记字面量；
  ② test_zero_hit_passes_and_drift_audit — 零命中（小型在册集使 find() 自然返回 []，
     即「打桩 []」的等价且保留真实审计写入路径——纯 stub find 不会产审计行）⇒
     门放行且 .runtime/lookup_audit/<sid>.jsonl（测试重定向 tmp）逐查询含
     result_count==0 行 = 既有漂移日志；
  ③ test_batching_equivalence_replay — CLASS-UNIQUENESS 批量化：≥100 真实新增 .py
     样本重放证据（create_guard_batch_replay.py 产出）逐字节全等 + 归因纯函数复算；
  ④ test_clearing_hits_turns_canary_red — 人为清空命中集 ⇒ ①同款断言必红
     （证明红由命中集带来，尺有判别力）；
  另：逃生标记端到端豁免、非在册 fail-closed、真实注册表同义命中（重，单独一条）。

纪律：不改任何既有测试/阈值/skip；全部 tmp_path 隔离。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT), str(_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import zephyr.governance.capability_lookup as capability_lookup_mod  # noqa: E402
from zephyr.gov_enforcement.commit_gates import create_guard as cg  # noqa: E402
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway  # noqa: E402

_ESCAPE_MARKER = "# create-guard-not-dup: 探针专用——本文件只做红证展示，非在册能力的第二实现"

_HEADER_14 = "\n".join(
    [
        "# [BLUEPRINT] MOD-PIECE1_CANARY | self | §canary",
        "# [MODULE] tests.piece1_canary.tick_duplication_checker",
        "# [DOMAIN] D_GOV_ENFORCEMENT",
        "# [DEPENDENCIES] none",
        "# [CONSUMERS] none",
        "# [STARTUP] manual",
        "# [MATURITY] design",
        "# [INVARIANTS] 红证探针文件，永不投产",
        "# [MODIFY-GUARD] canary",
        "# [STABILITY] evolving",
        "# [SAFETY] L",
        "# [AI_AUTONOMY] ai_modifiable",
        "# [ERROR_CONTRACT] none",
        "# [TESTS] self",
        "# [TTL] permanent",
    ]
)

_CANARY_SRC = _HEADER_14 + '\n"""\nTick duplication checker.\n\n逐笔成交数据重复检测与去重计数闸。\n"""\n\n\nclass TickDuplicationChecker:\n    """红证探针类。"""\n\n    pass\n\n\ndef check_tick_duplication(rows):\n    return rows\n'

_CANARY_REL = "src/zephyr/data/__piece1_canary_tick_duplication_checker.py"
_CANONICAL_REL = "src/zephyr/data/__piece1_canary_tick_dup_check.py"

_MINI_REGISTRY_YAML = f"""
capabilities:
  - capability_id: __piece1_canary_tick_dup_check
    description: "逐笔成交重复检测与去重计数（红证在册能力）"
    aliases:
      - "tick duplication checker"
      - "check tick duplication"
    canonical_override: {_CANONICAL_REL}
creation_tokens:
  - file: {_CANARY_REL}
    token: "auto-piece1-canary-20260926"
    created_by: "session-st-p1-gate"
    capability: "__piece1_canary_tick_dup_check"
    merge_evaluation: "红证探针件：非第二真源，系包13.1 判重尺自带 canary（同真源可派生→必并对偶件）"
"""


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@test.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@test.com",
        }
    )
    return subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, check=False, timeout=60
    )


def _init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "user.email", "test@test.com")
    (repo / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    _git(repo, "add", ".gitignore")
    _git(repo, "commit", "-m", "init", "--no-verify")


def _write(repo: Path, rel: str, content: str) -> Path:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _stage(repo: Path, rel: str, content: str = "x = 1\n") -> Path:
    p = _write(repo, rel, content)
    _git(repo, "add", rel)
    return p


def _mini_lookup(repo: Path, *, empty_caps: bool = False):
    yaml_text = "capabilities: []\ncreation_tokens: []\n" if empty_caps else _MINI_REGISTRY_YAML
    reg = _write(repo, "mini_registry.yaml", yaml_text)
    scan = repo / "src" / "zephyr"
    scan.mkdir(parents=True, exist_ok=True)
    return capability_lookup_mod.CapabilityLookup(yaml_path=reg, scan_root=[scan], derive_removed=False)


@pytest.fixture()
def _isolate_env(monkeypatch, tmp_path):
    """审计重定向 + 会话环境变量清空（测试禁写主仓 .runtime；find 审计行为不变）。"""
    monkeypatch.setattr(capability_lookup_mod, "LOOKUP_AUDIT_DIR", tmp_path / "lookup_audit")
    monkeypatch.delenv(capability_lookup_mod.SESSION_ID_ENV_VAR, raising=False)


def _pipeline_repo(tmp_path: Path, canary_src: str) -> tuple[GitCommitGateway, Path]:
    """搭一个 tmp git 仓：tmp 真源册（token 已登记）+ 在册 canonical + staged 探针文件。"""
    repo = tmp_path / "repo"
    _init_repo(repo)
    _write(repo, _CANONICAL_REL, "# canonical 在册真源（红证 fixture）\nVALUE = 1\n")
    _git(repo, "add", _CANONICAL_REL)
    _git(repo, "commit", "-m", "canonical", "--no-verify")
    reg_rel = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
    _write(repo, reg_rel, _MINI_REGISTRY_YAML)
    f = _stage(repo, _CANARY_REL, canary_src)
    return GitCommitGateway(project_root=repo), f


class TestRedProofOneSynonymHitBlocks:
    """红证①：新建 .py 的查询面与在册能力同义命中 ⇒ 门必 FAIL（全管线，非旁路）。"""

    def test_pipeline_synonym_hit_blocks(self, tmp_path: Path, monkeypatch, _isolate_env) -> None:
        gw, f = _pipeline_repo(tmp_path, _CANARY_SRC)
        monkeypatch.setattr(cg, "_build_capability_lookup", lambda: _mini_lookup(tmp_path / "repo"))
        passed, detail = cg.make_create_guard().check(gw, [str(f)], session_id="piece1-canary-sid")
        assert passed is False, f"同义命中在册能力时门必须红: {detail!r}"
        assert "__piece1_canary_tick_dup_check" in detail, detail
        assert "canonical_override=" in detail and _CANONICAL_REL in detail, detail
        assert "命中词=" in detail, detail
        assert "# create-guard-not-dup: <一句话理由>" in detail, f"逃生标记必须逐字出现在文案: {detail}"

    def test_escape_marker_exempts_end_to_end(self, tmp_path: Path, monkeypatch, _isolate_env) -> None:
        src = _CANARY_SRC.replace('"""\nTick duplication checker.', _ESCAPE_MARKER + '\n"""')
        # 标记必须在注释列（模块 docstring 之前的注释行）
        src = _ESCAPE_MARKER + "\n" + src
        gw, f = _pipeline_repo(tmp_path, src)
        monkeypatch.setattr(cg, "_build_capability_lookup", lambda: _mini_lookup(tmp_path / "repo"))
        passed, detail = cg.make_create_guard().check(gw, [str(f)], session_id="piece1-canary-sid")
        assert passed is True, f"逃生标记应豁免本检测（其余登记面同测试①已通过）: {detail}"


class TestRedProofTwoZeroHitDriftAudit:
    """红证②：命中集为空（在册能力清零=find() 自然 []，保留真实审计通道）⇒ 放行+漂移行。"""

    def test_zero_hit_passes_and_drift_audit_has_result_count_zero(self, tmp_path: Path, monkeypatch, _isolate_env) -> None:
        gw, f = _pipeline_repo(tmp_path, _CANARY_SRC)
        mini = _mini_lookup(tmp_path / "repo", empty_caps=True)
        monkeypatch.setattr(cg, "_build_capability_lookup", lambda: mini)
        passed, detail = cg.make_create_guard().check(gw, [str(f)], session_id="piece1-drift-sid")
        assert passed is True, f"零命中应放行: {detail}"
        audit = tmp_path / "lookup_audit" / "piece1-drift-sid.jsonl"
        assert audit.exists(), "find() 既有审计通道必须落盘（漂移日志不另建文件）"
        lines = [json.loads(x) for x in audit.read_text(encoding="utf-8").splitlines() if x.strip()]
        queries = {l["query"]["query"] for l in lines}
        assert "tick duplication checker" in queries or "check tick duplication" in queries, queries
        for l in lines:
            assert l["result_count"] == 0, l
        assert all(l["tool"] == "capability_lookup.find" for l in lines)


class TestRedProofThreeBatchingEquivalence:
    """红证③：CLASS-UNIQUENESS 批量化——100+ 真实新增 .py 样本重放判据逐字节全等。"""

    _EVIDENCE = Path(__file__).resolve().parent / "create_guard_batch_replay_evidence.json"

    def test_batching_equivalence_replay(self) -> None:
        assert self._EVIDENCE.exists(), f"重放证据缺失: {self._EVIDENCE}（先跑 python tests/gov_enforcement/create_guard_batch_replay.py）"
        ev = json.loads(self._EVIDENCE.read_text(encoding="utf-8"))
        assert ev["n_samples"] >= 100, ev["n_samples"]
        # 逐字节全等（含真实同名违规——detail 串全等即含违规清单全等）
        assert ev["old"]["detail"].count("定义 class") >= 1, "样本集必须包含真实同名违规（判别力前提）"
        assert ev["verdict_byte_equal"] is True, "批量版与逐名版 (passed, detail) 未逐字节全等"
        assert ev["attribution_mismatch_names"] == []
        # 复算：由存储的批量 -n 原始输出重导 per-name 归因，与逐名 -l 结果全等
        old_map = ev["old"]["name_map"]
        checked = 0
        for call in ev["new"]["batch_calls"]:
            if call["returncode"] != 0:
                continue
            for k, v in cg._attribute_class_grep_lines(call["stdout"], call["chunk"]).items():
                assert v == old_map.get(k, []), f"归因不一致: {k}: new={v} old={old_map.get(k, [])}"
                checked += 1
        assert checked >= 100, f"证据中可复算的类名过少: {checked}"
        # 计时面：新实现 git grep 调用次数必须远小于旧（批量化的存在理由）
        assert ev["new"]["grep_calls"] < ev["old"]["grep_calls"], (ev["new"]["grep_calls"], ev["old"]["grep_calls"])

    def test_batching_positive_control_on_tmp_repo(self, tmp_path: Path) -> None:
        """正向对照：tmp 小仓里真实同名 class ⇒ 批量版必须报与逐名语义一致的冲突。"""
        repo = tmp_path / "tiny"
        _init_repo(repo)
        _write(repo, "src/zephyr/a/__piece1_dup.py", "class Piece1DupCanary:\n    pass\n")
        _git(repo, "add", ".")
        _git(repo, "commit", "-m", "dup", "--no-verify")
        f = _stage(repo, "src/zephyr/b/__piece1_dup2.py", "class Piece1DupCanary:\n    pass\n")
        _ = f
        gw = GitCommitGateway(project_root=repo)
        passed, detail = cg._check_class_uniqueness(gw, ["src/zephyr/b/__piece1_dup2.py"])
        assert passed is False and "Piece1DupCanary" in detail, detail
        assert "__piece1_dup.py" in detail, detail


class TestRedProofFourDiscriminatingPower:
    """红证④：把命中集人为清空 ⇒ ①的断言必须变红（尺不是自选自答）。"""

    def test_clearing_hits_turns_canary_red(self, tmp_path: Path, monkeypatch, _isolate_env) -> None:
        gw, f = _pipeline_repo(tmp_path, _CANARY_SRC)
        mini = _mini_lookup(tmp_path / "repo")
        mini.find = lambda q, session_id=None: []  # 人为清空命中集
        monkeypatch.setattr(cg, "_build_capability_lookup", lambda: mini)
        passed, detail = cg.make_create_guard().check(gw, [str(f)], session_id="piece1-clear-sid")
        assert passed is True, f"命中集清空后应放行（否则红与命中集无关）: {detail}"
        with pytest.raises(AssertionError):
            # ①同款断言在本场景必须红——它红了，才证明①的红由命中集带来
            assert passed is False, "test_pipeline_synonym_hit_blocks 同款断言"

    def test_missing_lookup_fail_closed(self, tmp_path: Path) -> None:
        gw = SimpleNamespace(project_root=tmp_path)
        passed, detail = cg._check_capability_keyword_overlap(
            gw, ["src/zephyr/x/y.py"], "sid", lookup=None, lookup_error="simulated registry outage"
        )
        assert passed is False and "fail-closed" in detail, detail


class TestRealRegistrySynonymHit:
    """真实注册表面（慢件 ~100s）：与在册能力同义的新建 .py ⇒ helper 必红。

    用真册 find() 走查证明「在册」不是小型 fixture 自证。
    """

    def test_real_registry_synonym_hit(self, tmp_path: Path) -> None:
        lookup = cg._build_capability_lookup()  # 真实注册表（非缝注入）——慢件 ~75s
        # 探针面：docstring 首段 ASCII bigram「capability lookup」在真实在册能力
        # capability_lookup（canonical=src/zephyr/governance/capability_lookup.py）命中。
        src = '"""\nCapability lookup surface for canary.\n"""\n'
        repo = tmp_path / "r"
        rel = "src/zephyr/foo/capability_lookup_canary_surface.py"
        _write(repo, rel, src)
        gw = SimpleNamespace(project_root=repo)
        passed, detail = cg._check_capability_keyword_overlap(gw, [rel], None, lookup=lookup)
        assert passed is False, f"真实在册能力应命中: detail={detail!r}"
        assert "capability_id=capability_lookup" in detail, detail
        assert "canonical_override=src/zephyr/governance/capability_lookup.py" in detail, detail
        assert "# create-guard-not-dup: <一句话理由>" in detail, detail
