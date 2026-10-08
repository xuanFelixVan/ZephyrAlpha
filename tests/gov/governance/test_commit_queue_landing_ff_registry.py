# [TTL] permanent
"""注册表三方合并严格快进短路测试（st-chiefc-20261009，裁定#495 修宪批战役随批）。

被试：three_way_merge_registry_yaml 的 base==ours 字节相等快进分支。
能红证据：① ours==base 且 HEAD 侧带 YAML 锚点别名 → 修复前死信（undefined alias）、
修复后整文件取 theirs；② ours!=base 漂移 → 条目级合并路径行为不变；③ 快进目标
theirs YAML 非法 → 照样死信（护栏不能被用来落地坏文件）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))  # noqa: E402

from commit_queue_landing import three_way_merge_registry_yaml  # noqa: E402

_REL = "docs/01_policies_and_standards/_registry/catalogs/_ff_test_registry.yaml"

# 模拟 risk_tier_registry 实证形态：锚点在 mapping 段、别名在 list 条目块内
_ANCHORED = """module_id: REG-FF-TEST
version: 1.0.0
description: 旧头部（合并器对标量恒取 ours 的结构性缺口回归锚）
tiers:
  high:
    human_gate: &hhg
      - 旧一条
      - 旧二条
domain_tiers:
  - domain: D_A
    tier: high
    human_gate: *hhg
  - domain: D_B
    tier: low
    human_gate: []
"""

_DEANCHORED = """module_id: REG-FF-TEST
version: 1.1.0
description: 新头部（快进必须整文件带来，否则被 ours 吞掉）
tiers:
  high:
    human_gate:
      - 新一条
      - 新二条
      - 新三条
domain_tiers:
  - domain: D_A
    tier: high
    human_gate:
      - 新一条
      - 新二条
      - 新三条
  - domain: D_B
    tier: low
    human_gate: []
"""

# 无锚点常规册：验证漂移路径条目级行为不变
_PLAIN_BASE = """module_id: REG-FF-PLAIN
total_items: 1
items:
- key: a
  value: base
"""
_PLAIN_OURS = """module_id: REG-FF-PLAIN
total_items: 2
items:
- key: a
  value: base
- key: b
  value: ours_new
"""
_PLAIN_THEIRS = """module_id: REG-FF-PLAIN
total_items: 2
items:
- key: a
  value: base
- key: c
  value: theirs_new
"""


def test_ff_takes_theirs_whole_file_when_ours_equals_base() -> None:
    """base==ours（零漂移）→ 整文件取 theirs：头部+条目全量带来，锚点册可落地。"""
    merged, err = three_way_merge_registry_yaml(_ANCHORED, _ANCHORED, _DEANCHORED, rel_path=_REL)
    assert not err, f"快进分支不应死信: {err}"
    assert merged == _DEANCHORED, "快进必须逐字节取 theirs（头部改动不得被 ours 吞掉）"


def test_drift_path_still_entry_level_merge() -> None:
    """ours!=base（有漂移）→ 不走快进，条目级合并路径行为不变（ours 新条目保留）。"""
    merged, err = three_way_merge_registry_yaml(_PLAIN_BASE, _PLAIN_OURS, _PLAIN_THEIRS, rel_path=_REL)
    assert not err, f"漂移路径不应死信: {err}"
    assert "- key: b" in merged and "ours_new" in merged, "ours 侧独有新条目必须保留"
    assert "- key: c" in merged and "theirs_new" in merged, "theirs 独有新条目必须插入"
    assert "value: base" in merged, "未动条目保留 ours 原文"


def test_ff_with_invalid_theirs_yaml_still_dead_letters() -> None:
    """快进目标 theirs YAML 非法 → 死信回人工（快进不能成为落地坏文件的通道）。"""
    bad = _DEANCHORED + "  - broken: [unclosed\n"
    merged, err = three_way_merge_registry_yaml(_ANCHORED, _ANCHORED, bad, rel_path=_REL)
    assert merged is None and err, "非法 theirs 必须死信"
    assert "快进目标 theirs 解析失败" in err


def test_real_risk_tier_registry_ff_mergeable() -> None:
    """真册实测：HEAD 形态（若带别名）作为 ours==base、盘上 v1.1.0 作为 theirs → 可合并。"""
    import subprocess

    rel = "docs/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml"
    head = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True, text=True, encoding="utf-8").stdout
    disk = (REPO_ROOT / rel).read_text(encoding="utf-8")
    merged, err = three_way_merge_registry_yaml(head, head, disk, rel_path=rel)
    assert not err, f"真册快进失败: {err}"
    assert merged == disk, "真册快进必须等于盘上 v1.1.0 全文"
