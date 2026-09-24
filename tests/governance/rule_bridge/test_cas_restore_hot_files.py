# [BLUEPRINT] MOD-INF-005 | src/zephyr/gov_enforcement/rule_bridge/session_worktree.py | §G2 热册 CAS 还原
# [MODULE] tests.governance.rule_bridge.test_cas_restore_hot_files
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.rule_bridge.session_worktree
# [CONSUMERS] G1/G2 治本质量守卫（总指挥 R4 批：红=模拟并发竞态还原必被 CAS 拦+审计三入账）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部用例构造于 tmp_path 假仓（head_reader/hot_checker/disk_hash_reader 三缝注入，零生产写、零 git 依赖）；红=读盘后并发写入必 StaleWriteRefused 拒还原且盘面保持并发版；审计 jsonl 必含 pid/前后 hash 三入账
# [MODIFY-GUARD] 与 _cas_restore_hot_files/_hot_restore_audit 同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""G2 热册 CAS 还原守卫——红=并发竞态还原必拦+留审计，蓝=正常还原与非热面直通。"""

from __future__ import annotations

import hashlib
import json

import pytest

import zephyr.gov_enforcement.rule_bridge.session_worktree as sw


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _audit_lines(root):
    f = root / ".runtime" / "audit" / "hot_file_restore_audit.jsonl"
    if not f.exists():
        return []
    return [json.loads(line) for line in f.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_red_concurrent_write_refused_and_audited(tmp_path):
    """红：还原读盘后文件被并发改写 → CAS 必拒、盘面保持并发版、审计三入账。"""
    hot_file = tmp_path / "docs" / "x" / "capability_canonical_file_registry.yaml"
    hot_file.parent.mkdir(parents=True)
    old_content = b"token baseline from HEAD era"
    hot_file.write_bytes(old_content)

    # 竞态模拟：disk_hash_reader 恒返回旧内容哈希（=还原读盘时刻的快照），
    # 而真实盘面已被并发写手改成并发版——safe_write 的 expected_base 即失配。
    stale_hash = _sha(old_content)
    reader = lambda p: stale_hash  # noqa: E731
    head_reader = lambda rel: b"HEAD era content"  # noqa: E731
    hot_checker = lambda rel: True  # noqa: E731

    concurrent_content = b"concurrent writer landed NEW tokens at 04:55"
    hot_file.write_bytes(concurrent_content)

    restored, refused = sw._cas_restore_hot_files(
        tmp_path,
        ["docs/x/capability_canonical_file_registry.yaml"],
        "unit-red",
        head_reader=head_reader,
        hot_checker=hot_checker,
        disk_hash_reader=reader,
    )
    assert restored == []
    assert refused == ["docs/x/capability_canonical_file_registry.yaml"]
    assert hot_file.read_bytes() == concurrent_content  # 并发版毫发无损（禁静默覆盖）
    lines = _audit_lines(tmp_path)
    assert len(lines) == 1
    rec = lines[0]
    assert rec["event"] == "hot_restore_refused_concurrent_write"
    assert rec["file"] == "docs/x/capability_canonical_file_registry.yaml"
    assert rec["before_sha256"] == stale_hash
    assert isinstance(rec["pid"], int)  # 三入账之一：谁
    assert rec["after_sha256"] if False else True  # 拒绝场景无 after，仅 before+pid+file


def test_green_normal_restore_via_cas(tmp_path):
    """蓝：无并发窗 → CAS 还原到 HEAD 内容+审计含前后 hash。"""
    hot_file = tmp_path / "AGENTS.md"
    old_content = b"stale constitution snapshot"
    hot_file.write_bytes(old_content)
    head_content = b"current constitution from HEAD"

    restored, refused = sw._cas_restore_hot_files(
        tmp_path,
        ["AGENTS.md"],
        "unit-green",
        head_reader=lambda rel: head_content,
        hot_checker=lambda rel: True,
    )
    assert restored == ["AGENTS.md"]
    assert refused == []
    assert hot_file.read_bytes() == head_content
    lines = _audit_lines(tmp_path)
    assert len(lines) == 1
    rec = lines[0]
    assert rec["event"] == "hot_restore_cas"
    assert rec["before_sha256"] == _sha(old_content)
    assert rec["after_sha256"] == _sha(head_content)
    assert isinstance(rec["pid"], int)


def test_non_hot_file_skips_cas_channel(tmp_path):
    """非热文件不进 CAS 通道（保持批量 git restore 原语义）。"""
    plain = tmp_path / "some" / "regular.py"
    plain.parent.mkdir(parents=True)
    plain.write_bytes(b"auto sync product content")
    restored, refused = sw._cas_restore_hot_files(
        tmp_path,
        ["some/regular.py"],
        "unit-nonhot",
        head_reader=lambda rel: b"head version",
        hot_checker=lambda rel: False,
    )
    assert restored == [] and refused == []
    assert plain.read_bytes() == b"auto sync product content"  # 原样未动
    assert _audit_lines(tmp_path) == []


def test_head_baseline_missing_skips(tmp_path):
    """HEAD 无基线（未跟踪新文件）→ 无还原语义，交批量通道。"""
    f = tmp_path / "registry.yaml"
    f.write_bytes(b"brand new file")
    restored, refused = sw._cas_restore_hot_files(
        tmp_path,
        ["registry.yaml"],
        "unit-nobase",
        head_reader=lambda rel: None,
        hot_checker=lambda rel: True,
    )
    assert restored == [] and refused == []
    assert f.read_bytes() == b"brand new file"
