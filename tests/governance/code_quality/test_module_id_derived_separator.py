# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | (auto-injected by S4 reconciler) | §naming
# [TTL] permanent
"""派生轨分隔符等价测试（裁定#232，2026-09-14）。

裁定#232：派生轨段分隔符 - 与 _ 等价。背景=AI 会话天然写连字符
（MOD-INT-NEWS-CHAIN），原正则仅容下划线致共享注册表反复冻结。
本文件与 test_check_naming_convention_dual_track.py 互补——该文件被
N-06 内容自指封锁（其违规样例即触发物），故新用例独立成文件。
"""
from __future__ import annotations

import pytest

from scripts.governance.d3_metadata.validate_module_id_naming import (
    MODULE_ID_DOMAIN_DERIVED_RE,
    is_valid_module_id,
)

# ---- 裁定#232：连字符派生轨就地合法化（存量六 id 的回归锁定） ----

@pytest.mark.parametrize("value", [
    "MOD-INT-AISA",
    "MOD-INT-NEWS-CHAIN",
    "MOD-INT-IMPACT-STREAM",
    "MOD-REGIME-VAL-002",
    "MOD-NLP-INFERENCE-001",
    "MOD-DAT-fred_ingest",
])
def test_hyphen_derived_ids_legal(value):
    assert MODULE_ID_DOMAIN_DERIVED_RE.match(value)
    assert is_valid_module_id(value)


# ---- 原下划线/数字后缀形式保持合法（向后兼容） ----

@pytest.mark.parametrize("value", [
    "MOD-INT_AISA",
    "MOD-INT_NEWS_CHAIN",
    "MOD-SHARED-002",
    "MOD-INF-005",
])
def test_legacy_legal_forms_remain_legal(value):
    assert is_valid_module_id(value)


# ---- 非法形态仍被拒 ----

@pytest.mark.parametrize("value", [
    "D-FACTOR-01",      # D- 前缀已废弃为 submodule_id 专用
    "MOD_BAD",          # MOD 后必须用连字符
    "1MOD-ABC",         # 首字符须字母
])
def test_illegal_forms_remain_illegal(value):
    assert not MODULE_ID_DOMAIN_DERIVED_RE.match(value)
