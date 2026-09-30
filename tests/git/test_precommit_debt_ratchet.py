# [BLUEPRINT] MOD-GOV_CODE_QUALITY | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §precommit debt ratchet
# [MODULE] tests.git.test_precommit_debt_ratchet
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.rule_bridge.git_commit_gateway（_precommit_decide_failure/debt 棘轮族）
# [CONSUMERS] 全流通夜战 A2（st-circ-a2-20260930）：PRECOMMIT 存量债 warn 棘轮化行为钉
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 首扫全量入基线（grandfather）→基线内 warn 放行→净增键阻断→债消失基线缩小（只降不升）；env ZEPHYR_PRECOMMIT_DEBT_RATCHET=0 恢复 warn-only；基线损坏 fail-open 不自动重建；own 违规阻断路径不受棘轮影响
# [MODIFY-GUARD] 与 git_commit_gateway._precommit_debt_ratchet_decide 同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=tests.git.test_precommit_debt_ratchet | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""PRECOMMIT 存量债 warn 棘轮化测试（全流通夜战 A2 2026-09-30）。

病根：precommit_channel_global_debt_warned warn 通道 197/250 趟恒放行——
全局存量债只增不减，无人对净增负责。棘轮=首扫全量入基线（grandfather）、
基线只降不升（消失即出册）、净增键升级阻断（参照 fms_deadref_baseline 模式）。
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
    GitCommitGateway,
    _precommit_debt_keys,
)

# 两个 foreign（非 own）hook 失败段：证据行均不含 own staged 文件（docs/a.md）
OUT_VOCAB = (
    "Vocab....................................................................Failed\n"
    "\n"
    "- hook id: gate-vocab\n"
    "- exit code: 1\n"
    "scripts/governance/foo.py:88: term 'x' not in glossary\n"
    "scripts/governance/bar.py:12: term 'y' not in glossary\n"
    "Fix: python scripts/governance/fix_vocab.py  # 修复提示样板（非证据行）\n"
    "\n"
)
# OUT_VOCAB + 第三个 hook 失败段（净增场景：新 hook 新文件债）
OUT_VOCAB_PLUS_ZR = OUT_VOCAB + (
    "Zr....................................................................Failed\n"
    "\n"
    "- hook id: gate-zr\n"
    "- exit code: 1\n"
    "config/asset_inventory.yaml:139: GATE-ZR 全局 error 存量债\n"
)


def _git_init_repo(tmp_path: Path) -> GitCommitGateway:
    """tmp 真仓（Gateway 构造强校验 git repo；审计/基线全落 tmp，零生产面污染）。"""
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "T",
        "GIT_AUTHOR_EMAIL": "t@t.com",
        "GIT_COMMITTER_NAME": "T",
        "GIT_COMMITTER_EMAIL": "t@t.com",
    }

    def _g(*args: str) -> None:
        subprocess.run(["git", *args], cwd=str(tmp_path), capture_output=True, env=env, check=False)

    _g("init", "-q")
    (tmp_path / "f.txt").write_text("x", encoding="utf-8")
    _g("add", "f.txt")
    _g("commit", "-q", "-m", "t", "--no-verify")
    return GitCommitGateway(project_root=tmp_path)


@pytest.fixture()
def gw(tmp_path, monkeypatch):
    """网关 + 棘轮 env 归位（缺省 ON；防开发者环境变量串扰）。"""
    monkeypatch.delenv("ZEPHYR_PRECOMMIT_DEBT_RATCHET", raising=False)
    gateway = _git_init_repo(tmp_path)
    gateway._tmp_path = tmp_path  # 供断言 helper 定位（附在对象上，避免闭包泄漏）
    yield gateway


def _events(gw: GitCommitGateway) -> list[dict]:
    p = gw._tmp_path / ".runtime" / "audit" / "commit_block_events.jsonl"
    if not p.is_file():
        return []
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _baseline(gw: GitCommitGateway) -> dict | None:
    p = gw._tmp_path / ".runtime" / "gate_audit" / "precommit_global_debt_baseline.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _decide(gw: GitCommitGateway, output: str, session_id: str = "s1") -> str | None:
    return gw._precommit_decide_failure(session_id, ["docs/a.md"], output, False, ["docs/a.md"], [])


class TestDebtRatchetLifecycle:
    """棘轮生命周期：首扫建册→基内 warn→净增阻断→债消出册（只降不升）。"""

    def test_first_scan_creates_baseline_and_warns(self, gw) -> None:
        """首扫：全量债务键入基线（grandfather），warn 放行 + baseline_created 审计。"""
        assert _decide(gw, OUT_VOCAB) is None, "首扫全量入基线，warn 放行"
        base = _baseline(gw)
        assert base is not None and set(base["keys"]) == {
            "gate-vocab|scripts/governance/foo.py",
            "gate-vocab|scripts/governance/bar.py",
            "gate-vocab|<noanchor>",
        }, "修复提示样板行不入键（Fix: 行剥离）；无路径证据行折叠 <noanchor>"
        created = [e for e in _events(gw) if e["event"] == "precommit_channel_debt_baseline_created"]
        assert len(created) == 1 and created[0]["keys_count"] == 3

    def test_baseline_debt_warns_not_blocks(self, gw) -> None:
        """基线内债务再扫：仍 warn 放行（不阻断），事件带基线命中计数。"""
        _decide(gw, OUT_VOCAB)
        assert _decide(gw, OUT_VOCAB) is None
        warned = [e for e in _events(gw) if e["event"] == "precommit_channel_global_debt_warned"]
        assert len(warned) == 2
        assert warned[-1]["debt_ratchet"] == "on"
        assert warned[-1]["debt_keys"] == 3 and warned[-1]["debt_net_new"] == 0

    def test_net_new_key_blocks(self, gw) -> None:
        """净增键语义 v2（2026-10-01 提交链治本，宪法 §3.1 own-diff 作用域）：

        外来净增键（anchor 非 own 文件面）→ warn 放行 + foreign_net_new_warned 审计，
        不再阻断无辜提交人（2026-09-30 16 起连坐/7 会话实证：他会话 staged 债键把
        无辜方反复拦死）；own anchor 净增键仍阻断（见 TestDebtRatchetOwnForeignSplit
        纵深防御钉）。原「外来净增阻断」语义由本钉改写追认——棘轮记账/出册/审计
        语义零变化。
        """
        _decide(gw, OUT_VOCAB)
        block = _decide(gw, OUT_VOCAB_PLUS_ZR, session_id="s2")
        assert block is None, "外来净增 warn 放行（own-diff 作用域）"
        assert "ZEPHYR_PRECOMMIT_DEBT_RATCHET=0" not in (block or ""), "无阻断即无手柄处方"
        warned = [e for e in _events(gw) if e["event"] == "precommit_channel_debt_foreign_net_new_warned"]
        assert len(warned) == 1 and warned[0]["session_id"] == "s2"
        assert sorted(warned[0]["foreign_net_new_keys"]) == sorted(
            ["gate-zr|<noanchor>", "gate-zr|config/asset_inventory.yaml"]
        ), "审计留全量净增键供追责"
        blocked = [e for e in _events(gw) if e["event"] == "precommit_channel_debt_ratchet_blocked"]
        assert blocked == [], "零阻断（无 own anchor 键）"

    def test_baseline_never_grows_on_repeat(self, gw) -> None:
        """棘轮铁律：重复扫描永不把净增键写入基线（基线只降不升）。"""
        _decide(gw, OUT_VOCAB)
        _decide(gw, OUT_VOCAB_PLUS_ZR, session_id="s2")  # 净增阻断
        _decide(gw, OUT_VOCAB_PLUS_ZR, session_id="s3")  # 同净增再扫（仍阻断）
        base = _baseline(gw)
        assert set(base["keys"]) == {
            "gate-vocab|scripts/governance/foo.py",
            "gate-vocab|scripts/governance/bar.py",
            "gate-vocab|<noanchor>",
        }, "净增键绝不入册——基线永不含 gate-zr*"

    def test_debt_disappearance_shrinks_baseline(self, gw) -> None:
        """债消失（hook 转绿）→ 键出册 + shrunk 审计（棘轮下拧）。"""
        _decide(gw, OUT_VOCAB_PLUS_ZR)  # 首扫：5 键入册
        assert _decide(gw, OUT_VOCAB) is None  # gate-zr 转绿
        base = _baseline(gw)
        assert "gate-zr|config/asset_inventory.yaml" not in base["keys"]
        assert "gate-zr|<noanchor>" not in base["keys"]
        shrunk = [e for e in _events(gw) if e["event"] == "precommit_channel_debt_baseline_shrunk"]
        assert len(shrunk) == 1 and shrunk[0]["removed"] == 2

    def test_ratchet_env_off_restores_warn_only(self, gw, monkeypatch) -> None:
        """回退手柄：env ZEPHYR_PRECOMMIT_DEBT_RATCHET=0 → 恒 warn-only，不建基线。"""
        monkeypatch.setenv("ZEPHYR_PRECOMMIT_DEBT_RATCHET", "0")
        assert _decide(gw, OUT_VOCAB) is None
        assert _decide(gw, OUT_VOCAB_PLUS_ZR) is None, "净增也不拦（legacy warn-only）"
        assert _baseline(gw) is None, "手柄关闭零副作用（不建基线）"
        warned = [e for e in _events(gw) if e["event"] == "precommit_channel_global_debt_warned"]
        assert len(warned) == 2 and all("debt_ratchet" not in e for e in warned)

    def test_corrupt_baseline_fails_open_no_recreate(self, gw) -> None:
        """基线损坏：fail-open warn 放行 + corrupt 审计；不自动重建（防棘轮静默重置）。"""
        p = gw._tmp_path / ".runtime" / "gate_audit" / "precommit_global_debt_baseline.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{not-json!!", encoding="utf-8")
        assert _decide(gw, OUT_VOCAB_PLUS_ZR) is None, "损坏→fail-open 放行"
        corrupt = [e for e in _events(gw) if e["event"] == "precommit_channel_debt_baseline_corrupt"]
        assert len(corrupt) == 1
        assert p.read_text(encoding="utf-8") == "{not-json!!", "不静默重建（防基线被无声重置）"


class TestDebtKeyExtraction:
    """债务键稳定性：行漂移同键、样板剥离、散文折叠。"""

    def test_line_number_drift_same_key(self) -> None:
        k1 = _precommit_debt_keys({"hook_id": "h", "text": "a/b.py:10: bad thing"})
        k2 = _precommit_debt_keys({"hook_id": "h", "text": "a/b.py:999: bad thing"})
        assert k1 == k2 == {"h|a/b.py"}, "行号不进键——行漂移不得虚报净增"

    def test_hint_lines_stripped(self) -> None:
        keys = _precommit_debt_keys(
            {"hook_id": "h", "text": "x/y.py:1: bad\nFix: python scripts/governance/fix.py\n-> scripts/gen.py"}
        )
        assert keys == {"h|x/y.py"}, "Fix:/->/python 样板行剥离（与 own 归因同口径）"

    def test_prose_collapses_to_noanchor(self) -> None:
        keys = _precommit_debt_keys({"hook_id": "h", "text": "- exit code: 1\nsome prose finding"})
        assert keys == {"h|<noanchor>"}

    def test_empty_segment_fallback(self) -> None:
        assert _precommit_debt_keys({"hook_id": "h", "text": ""}) == {"h|<noanchor>"}


class TestOwnPathUnchanged:
    """回归钉：own 违规阻断路径不被棘轮吞掉（棘轮只管 foreign warn 通道）。"""

    def test_own_violation_still_blocks_no_baseline(self, gw) -> None:
        own_out = (
            "Vocab....................................................................Failed\n"
            "- hook id: gate-vocab\n"
            "- exit code: 1\n"
            "docs/a.md:3: term 'x' not in glossary\n"
        )
        block = gw._precommit_decide_failure("s1", ["docs/a.md"], own_out, False, ["docs/a.md"], [])
        assert block is not None and "GATE-PRECOMMIT-RUN" in block
        assert _baseline(gw) is None, "own 阻断路径零基线副作用"
        assert not [e for e in _events(gw) if e["event"].startswith("precommit_channel_debt")]

    def test_mutation_still_blocks(self, gw) -> None:
        block = gw._precommit_decide_failure("s1", ["docs/a.md"], OUT_VOCAB, True, ["docs/a.md"], [])
        assert block is not None and "hook 修改了文件" in block
        assert _baseline(gw) is None


class TestDebtRatchetOwnForeignSplit:
    """own/foreign 键级拆分（2026-10-01 提交链治本，宪法 §3.1 own-diff 作用域落地）。

    classify 段级归因下 own 键本就到不了棘轮（own 段提前走 own_failed 硬拦）；
    本拆分=①混合段兜底（foreign 段内 own anchor 键仍阻断，纵深防御）②外来净增键
    降级 warn+审计不阻断无辜提交人（2026-09-30 16 起连坐/7 会话实证）。
    """

    def test_foreign_net_new_warns_and_passes(self, gw) -> None:
        assert _decide(gw, OUT_VOCAB) is None, "首扫建册"
        assert _decide(gw, OUT_VOCAB_PLUS_ZR) is None, "外来净增键 warn 放行（anchor 非 own 文件面）"
        warned = [e for e in _events(gw) if e["event"] == "precommit_channel_debt_foreign_net_new_warned"]
        assert len(warned) == 1 and warned[0]["foreign_net_new_count"] == 2
        assert sorted(warned[0]["foreign_net_new_keys"]) == sorted(
            ["gate-zr|config/asset_inventory.yaml", "gate-zr|<noanchor>"]
        )
        base = _baseline(gw)
        assert base is not None
        assert "gate-zr|config/asset_inventory.yaml" not in base.get("keys", {}), "外来键永不入基线"

    def test_own_anchor_key_still_blocks_via_ratchet(self, gw) -> None:
        """直接调棘轮判定（绕 classify 构造混合段）：own anchor 净增键仍阻断。"""
        assert _decide(gw, OUT_VOCAB) is None, "首扫建册"
        seg = {"hook_id": "gate-mix", "text": "docs/a.md:5: own 面净增债\n"}
        msg, meta = gw._precommit_debt_ratchet_decide("s1", ["docs/a.md"], [seg])
        assert msg is not None and "净增" in msg, "own anchor 键阻断（纵深防御分支）"
        assert meta["debt_own_net_new"] == 1 and meta["debt_foreign_net_new"] == 0
