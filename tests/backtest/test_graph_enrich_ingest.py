# [BLUEPRINT] MOD-BT-203 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_graph_enrich_ingest
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; pandas
# [CONSUMERS] MOD-BT-203 graph_enrich_ingest 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络；合成行验证三道校验门
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-203 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""图谱增补入图纯函数单测——三道校验门，零网络。"""
from __future__ import annotations

import pandas as pd
import pytest

from scripts.backtest.graph_enrich_ingest import read_staged, validate_row


class TestValidateRow:
    def _ok(self):
        return pd.Series({"supplier": "A公司", "customer": "B公司",
                          "product": "硅料", "confidence": 0.9, "evidence": "原文"})

    def test_valid(self):
        ok, why = validate_row(self._ok())
        assert ok, why

    def test_same_party(self):
        r = self._ok(); r["customer"] = r["supplier"]
        ok, why = validate_row(r)
        assert not ok

    def test_low_conf(self):
        r = self._ok(); r["confidence"] = 0.5
        ok, _ = validate_row(r)
        assert not ok

    def test_empty_evidence(self):
        r = self._ok(); r["evidence"] = ""
        ok, _ = validate_row(r)
        assert not ok


class TestReadStaged:
    def test_missing_file_returns_empty(self, tmp_path):
        df = read_staged(tmp_path / "no.csv")
        assert df.empty

    def test_filters_by_status(self, tmp_path):
        p = tmp_path / "s.csv"
        p.write_text("status\nstaged\ningested\n", encoding="utf-8")
        df = read_staged(p)
        assert len(df) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
