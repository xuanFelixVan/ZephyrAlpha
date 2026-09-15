# [BLUEPRINT] MOD-BT-201 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_forward_post
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas
# [CONSUMERS] MOD-BT-201 forward_post 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 CH；合成数据验证分类/统计
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-201 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""E7 前哨对账器纯函数单测——分类/统计/合成验证，零网络。"""
from __future__ import annotations

import numpy as np
import pytest

from scripts.backtest.forward_post import classify


class TestClassify:
    def test_hit(self):
        assert classify(1.5) == "命中"

    def test_deviation(self):
        assert classify(5.0) == "偏差"

    def test_missing(self):
        assert classify(None) == "缺失"
        assert classify(float("nan")) == "缺失"

    def test_custom_tolerance(self):
        assert classify(3.0, hit_tol=5.0) == "命中"
        assert classify(3.0, hit_tol=1.0) == "偏差"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
