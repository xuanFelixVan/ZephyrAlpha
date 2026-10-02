# [BLUEPRINT] MOD-SEC-SESSION-REGISTRY | tests/security/test_session_registry_chief_form.py | redblue
# [MODULE] tests.security.test_session_registry_chief_form
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] pytest; zephyr.security.access_control.session_concurrency.SessionRegistry
# [CONSUMERS] 无（测试件）
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 测试隔离——注册表落 tmp_path，零生产路径写入；chief-form 核验只读
# [MODIFY-GUARD] 归 MOD-SEC-SESSION-REGISTRY 修改守护
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试红
# [TESTS] 本文件
# [TTL] permanent
"""W-29 logical=True 形态核验（wave4-D 收口）单测。

覆盖：① chief 词形 sid 直接过；② 无形态词+无心跳=降级 logical=False；
③ 无形态词+新鲜心跳文件=过；④ mark_logical 原地翻转不受核验影响。
"""

import time
from pathlib import Path

from zephyr.security.access_control.session_concurrency import SessionRegistry


def _make_registry(tmp_path: Path) -> SessionRegistry:
    return SessionRegistry(project_root=tmp_path)


def test_chief_pattern_sid_passes(tmp_path):
    reg = _make_registry(tmp_path)
    info = reg.register("st-chief7-20260928", pid=0, held_files=[], logical=True)
    assert info.logical is True


def test_non_chief_without_heartbeat_downgraded(tmp_path):
    reg = _make_registry(tmp_path)
    info = reg.register("st-xyz-20261002", pid=0, held_files=[], logical=True)
    assert info.logical is False


def test_non_chief_with_fresh_heartbeat_passes(tmp_path):
    reg = _make_registry(tmp_path)
    hb_dir = tmp_path / ".runtime" / "sessions" / "st-xyz-20261002"
    hb_dir.mkdir(parents=True)
    (hb_dir / "heartbeat.jsonl").write_text("{}\n", encoding="utf-8")
    info = reg.register("st-xyz-20261002", pid=0, held_files=[], logical=True)
    assert info.logical is True


def test_existing_logical_inherits_without_reverify(tmp_path):
    reg = _make_registry(tmp_path)
    reg.register("st-chief7-20260928", pid=0, held_files=[], logical=True)
    # 二次注册不带 logical 实参——既有条目继承通道
    info2 = reg.register("st-chief7-20260928", pid=0, held_files=[], logical=False)
    assert info2.logical is True


def test_mark_logical_unaffected(tmp_path):
    reg = _make_registry(tmp_path)
    reg.register("st-plain-20261002", pid=123, held_files=[])
    assert reg.mark_logical("st-plain-20261002", logical=True) is True
    shard = tmp_path / ".runtime" / "session_registry" / "st-plain-20261002.json"
    if not shard.exists():
        shard = tmp_path / ".runtime" / "session_registry.json"
    import json

    stored = json.loads(shard.read_text(encoding="utf-8"))
    entry = stored.get("st-plain-20261002", stored) if isinstance(stored, dict) else {}
    assert entry.get("logical") is True
