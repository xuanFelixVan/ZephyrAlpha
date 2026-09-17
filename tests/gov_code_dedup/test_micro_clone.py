# [A_test] module_id: MOD-GOV_micro_clone | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-362 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.gov_code_dedup.test_micro_clone
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""微型克隆检测测试."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_scanner_blocks():
    from zephyr.infrastructure.asset_inventory.scanner import Scanner

    s = Scanner()
    source = "a = 1\nb = 2\nc = 3\nd = 4\ne = 5\nf = 6\n"
    blocks = s.scan_blocks(source)
    # B2 审计修复（2026-09-17）：原 `assert len(blocks) >= 2` 只数个数不看内容，
    # M16 变异实证（每块截短一行）照样绿。钉死确切切分：_BLOCK_MIN_LINES=3
    # 非重叠步进，6 行 → 2 块，内容与顺序逐字节相等。
    assert blocks == ["a = 1\nb = 2\nc = 3", "d = 4\ne = 5\nf = 6"]


def test_micro_clone_blind_spot():
    # B2 审计修复：原 `assert True  # stub` 纯占位零行为。替换为边界真断言：
    # 不足一个窗口（<_BLOCK_MIN_LINES 行）必须返回空——短文件不得产生伪块。
    from zephyr.infrastructure.asset_inventory.scanner import Scanner

    s = Scanner()
    assert s.scan_blocks("a = 1\nb = 2\n") == []
    # 尾部不足一个窗口的余行被丢弃（非重叠窗口口径钉扎）
    blocks = s.scan_blocks("a\nb\nc\nd\n")
    assert blocks == ["a\nb\nc"]
