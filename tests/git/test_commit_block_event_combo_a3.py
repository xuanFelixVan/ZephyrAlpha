# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.1
# [MODULE] tests.git.test_commit_block_event_combo_a3
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] stdlib; zephyr.gov_enforcement.rule_bridge.git_commit_gateway (GitCommitGateway/CommitResult/CommitStatus)
# [CONSUMERS] pytest（堵点本 detail 不截断+连击升级 A3 任务2 验收）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 自含不跨测试文件 import（test_git_commit_gateway.py 由 st-circ-a2-20260930 持 claim 在飞，冲突让位不共件）；测试输出全落 tmp_path；只测审计器纯逻辑（_audit_commit_block_event/_count_recent_block_signature），不测门禁判定本身
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败；不写生产路径
# [TESTS] tests/git/test_commit_block_event_combo_a3.py（本件）
# [A_module] module_id=MOD-CLONE_GUARD | layer=test | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""堵点本 detail 不截断 + 同签名连击升级验收（A3 任务2，st-circ-a3-20260930）。

深挖矿处方：BLUEPRINT-FORMAT 连击 47 事件/7 会话/最大 31 连击——违规清单 file:line
在阻断消息尾部，[:200] 截断恒把病灶切掉（溯源者看不到病灶=审计失去可行动性）；
同签名（session+gate+detail 全文 sha1）二次阻断起事件带 repeat_count+escalated 标记，
维护班按 sig 聚合即得重试环复发拓扑。
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult, CommitStatus, GitCommitGateway


def _init_git_repo(tmp_path: Path) -> None:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "T",
        "GIT_AUTHOR_EMAIL": "t@t.com",
        "GIT_COMMITTER_NAME": "T",
        "GIT_COMMITTER_EMAIL": "t@t.com",
    }
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(tmp_path), capture_output=True, env=env)
    (tmp_path / "f.txt").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "f.txt"], cwd=str(tmp_path), capture_output=True, env=env)
    subprocess.run(["git", "commit", "-m", "t", "--no-verify"], cwd=str(tmp_path), capture_output=True, env=env)


def _gw(tmp_path: Path) -> GitCommitGateway:
    _init_git_repo(tmp_path)
    return GitCommitGateway(project_root=tmp_path)


def _events(tmp_path: Path) -> list[dict]:
    p = tmp_path / ".runtime" / "audit" / "commit_block_events.jsonl"
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


_BLUEPRINT_MSG = (
    "BLUEPRINT-FORMAT: [BLUEPRINT] 头部 module_id 格式不合规（裁定#214 Phase 0 防蔓延）\n"
    "  合规格式: # [BLUEPRINT] MOD-XXX | docs/03_modules/.../blueprint.md\n"
    "  禁止格式: 空头部 / (migrated...) / SRC-XXX / DOM-XXX / 路径作 module_id\n"
    "  src/zephyr/gov_enforcement/commit_gates/bad_gate.py:1: [BLUEPRINT] header invalid module_id 'SRC-XXX': "
    "缺少 MOD-/SH- 前缀（裁定#208 双轨制）\n"
    "  src/zephyr/gov_enforcement/commit_gates/bad_gate2.py:157: [BLUEPRINT] header missing module_id\n"
    "-> 修复 [BLUEPRINT] 头部，使用合规的 MOD-/SH- 前缀 module_id"
)


class TestBlockEventDetailNotTruncated:
    def test_detail_full_with_file_line_preserved(self, tmp_path: Path) -> None:
        """detail 全量落盘：违规清单 file:line 在消息尾部不再被 [:200] 切掉。"""
        gw = _gw(tmp_path)
        blocked = CommitResult(status=CommitStatus.COMMIT_FAILED, message=_BLUEPRINT_MSG)
        assert len(_BLUEPRINT_MSG) > 200, "用例前提：消息超过旧 200 字截断线"
        gw._audit_commit_block_event("sess-bp", blocked, ["bad_gate.py"], 900.0)
        evs = _events(tmp_path)
        assert len(evs) == 1
        assert evs[0]["detail"] == _BLUEPRINT_MSG, "detail 必须全量（病灶 file:line 可溯源）"
        assert "bad_gate2.py:157" in evs[0]["detail"]


class TestBlockEventRepeatEscalation:
    def test_first_block_no_escalation(self, tmp_path: Path) -> None:
        gw = _gw(tmp_path)
        blocked = CommitResult(status=CommitStatus.COMMIT_FAILED, message=_BLUEPRINT_MSG)
        gw._audit_commit_block_event("sess-bp", blocked, [], 1.0)
        ev = _events(tmp_path)[0]
        assert ev["repeat_count"] == 1
        assert "escalated" not in ev, "首投不升级"
        assert ev["sig"], "签名必须落盘（跨进程聚合键）"

    def test_same_signature_second_block_escalates(self, tmp_path: Path) -> None:
        """同签名二次阻断：repeat_count=2 + escalated=true（31 连击可见化）。"""
        gw = _gw(tmp_path)
        blocked = CommitResult(status=CommitStatus.COMMIT_FAILED, message=_BLUEPRINT_MSG)
        for _ in range(3):
            gw._audit_commit_block_event("sess-bp", blocked, [], 1.0)
        evs = _events(tmp_path)
        assert [e["repeat_count"] for e in evs] == [1, 2, 3], "同签名连击计数单调"
        assert [bool(e.get("escalated")) for e in evs] == [False, True, True]
        assert len({e["sig"] for e in evs}) == 1, "同 session+gate+detail 签名稳定"

    def test_different_detail_gets_fresh_signature(self, tmp_path: Path) -> None:
        """不同 detail（病灶变化）=新签名：连击计数独立，不误并。"""
        gw = _gw(tmp_path)
        gw._audit_commit_block_event(
            "sess-bp", CommitResult(status=CommitStatus.COMMIT_FAILED, message=_BLUEPRINT_MSG), [], 1.0
        )
        gw._audit_commit_block_event(
            "sess-bp",
            CommitResult(status=CommitStatus.COMMIT_FAILED, message=_BLUEPRINT_MSG + "\n  附加新违规 one_more.py:9"),
            [],
            1.0,
        )
        evs = _events(tmp_path)
        assert evs[1]["repeat_count"] == 1, "detail 变化=新签名，复读计数独立"
        assert evs[1]["sig"] != evs[0]["sig"]

    def test_corrupt_tail_lines_tolerated(self, tmp_path: Path) -> None:
        """尾窗半行/损坏行容忍：计数不炸（drain 中断半写容忍同款）。"""
        gw = _gw(tmp_path)
        audit = tmp_path / ".runtime" / "audit"
        audit.mkdir(parents=True)
        (audit / "commit_block_events.jsonl").write_text('{"sig": "deadbeef"}\n{"sig": "cut', encoding="utf-8")
        assert gw._count_recent_block_signature("deadbeef") == 1
        assert gw._count_recent_block_signature("missing") == 0
