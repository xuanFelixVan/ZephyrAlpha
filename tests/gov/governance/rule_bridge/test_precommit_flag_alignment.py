"""D11-G02 precommit 回滚旗对齐回归钉（st-sO2-probe-20261004 手术2-G02）。

考古结论（2026-10-04，车道O）：
- 原缺口：gateway 代码读 `gate_precommit_run_enabled`（未注册键）× is_enabled(default=True)
  ⇒ 恒 ON，Owner 回滚手柄（flags.yaml flag OFF）不可兑现（图11 gap 节点 D11-G02）。
- 修复事实：2026-09-30 b192fa39126（ND-E9 SW15 R-5）已一行对齐——gateway 常量
  _PRECOMMIT_RUN_FLAG='gate_precommit_run' 与 flags.yaml 在册键同名，回滚通道复活；
  machine_facts.precommit_flag_pair 已绿（code_key=registered=True）。

本套件钉死修复不被回退：
1. 键对齐钉——_PRECOMMIT_RUN_FLAG 值在 global_flag_registry 在册（未注册键×default=True
   的幽灵引用病理死绝）；
2. 回滚通道钉——flag 置 OFF ⇒ _precommit_run_enabled() 返回 False（Owner 紧急停用
   手柄真实可用；测后恢复原态）；
3. 图11 叙事层钉——config/dev_delivery_map.yaml D11-G02 节点不再断言「通道恒 ON」
   （语义层与代码面同步，文档矛盾=事故）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[4]


def test_green_flag_key_registered():
    """键对齐钉：代码常量=注册表在册键（幽灵引用病理死绝）。"""
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw
    from zephyr.shared.foundation.flags import ensure_global_flags_loaded, global_flag_registry

    key = gw._PRECOMMIT_RUN_FLAG
    assert key == "gate_precommit_run", f"代码键被改回旧幽灵名: {key!r}（D11-G02 复发）"
    ensure_global_flags_loaded()
    assert key in global_flag_registry._flags, (
        f"代码键 {key!r} 未在 flags 注册表在册——is_enabled 将恒走 default=True（D11-G02 病理复发）"
    )


def test_green_rollback_channel_off_works():
    """回滚通道钉：flag OFF ⇒ _precommit_run_enabled()=False（Owner 紧急停用手柄可用）。"""
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw
    from zephyr.shared.foundation.flags import ensure_global_flags_loaded, global_flag_registry

    ensure_global_flags_loaded()
    key = gw._PRECOMMIT_RUN_FLAG
    assert key in global_flag_registry._flags, "前置失败：键未注册（先看 test_green_flag_key_registered）"
    original = global_flag_registry._flags[key]
    try:
        global_flag_registry.set(key, enabled=False, description=original.description)
        assert gw._precommit_run_enabled() is False, "flag OFF 后通道仍 ON——回滚通道坏死（D11-G02 复发）"
        global_flag_registry.set(key, enabled=True, description=original.description)
        assert gw._precommit_run_enabled() is True, "flag ON 后通道应恢复运行"
    finally:
        global_flag_registry._flags[key] = original  # 恢复原注册态（测试不留副作用）


def test_green_map_narrative_synced_with_code():
    """叙事层钉：图11 D11-G02/C07 节点与代码面同步（语义层滞后=文档矛盾=事故）。

    G02 note 允许保留病理史实描述（含「恒 ON」字样述史），但必须带闭合标记；
    C07 note 不得再含旧断言「恒 ON/回滚面失效」形态。
    """
    doc = yaml.safe_load((_REPO / "config" / "dev_delivery_map.yaml").read_text(encoding="utf-8"))
    g02 = next(n for n in doc["nodes"] if n["node_id"] == "D11-G02")
    note = str(g02.get("note_zh", ""))
    assert "b192fa39126" in note, "D11-G02 note 缺修复锚（考古结论不许静默蒸发）"
    assert "已闭合" in note, "D11-G02 note 缺闭合标记（修复事实未同步进图）"
    assert "回滚通道复活" in note
    assert g02.get("wiring_status") == "wired", "D11-G02 修复后回滚通道已接线（wired）"
    pair = (g02.get("machine_facts") or {}).get("precommit_flag_pair") or {}
    assert pair.get("code_key") == "gate_precommit_run" and pair.get("registered") is True
    c07 = next(n for n in doc["nodes"] if n["node_id"] == "D11-C07")
    c07_note = str(c07.get("note_zh", ""))
    assert "恒 ON" not in c07_note and "回滚面失效" not in c07_note, (
        "D11-C07 note 仍断言通道恒 ON/回滚面失效——修复后叙事层未同步"
    )
