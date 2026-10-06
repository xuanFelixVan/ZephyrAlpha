# [A_test] module_id: MOD-TEST-FEAT-STORE-WRITER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-FS | docs/03_modules/_domain_factor/blueprint.md | 15 号 §3.4 要点④
# [MODULE] tests.factor.test_feature_store_writer
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.feature_store_writer; schemas.categories.factor_feature_value; pandas; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/factor/test_feature_store_writer.py
# [TTL] permanent
# [ARCH-REF] #15_data_feature_layer_spec §3.4 特征仓库存储层（写入管道，不执行）
# [ALGO_FLOW]
# 层: 输入
# - I1: 长表特征值 DataFrame(trade_date/symbol/factor_id/value) + 版本 + 可选 client
# 层: 算法
# - A1: build_feature_value_rows（对齐 INSERT_COLUMNS；NaN→None 预热期 NULL 语义）
# - A2: write_feature_values（分块 INSERT；client 注入式；空输入短路 0）
# 层: 输出
# - O1: 行 tuple 列表 / 写入行数 int
"""test_feature_store_writer.py — 特征仓库写入管道单元测试（15 号 §3.4 要点④）。

覆盖：
  1. build_feature_value_rows：列序对齐 INSERT_COLUMNS / NaN→None / 版本与数据源默认
  2. 缺必需列 → ValueError；空输入 → []
  3. write_feature_values：fake client 注入验证 INSERT 调用与分块；空输入不写库；
     client 不可得 → RuntimeError
  4. schema 文件契约：DDL 含表名/引擎/分区键；INSERT_COLUMNS 与写入列一致
"""

from __future__ import annotations

import datetime

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.feature_store_writer import (
    build_feature_value_rows,
    write_feature_values,
)


def _values(n: int = 3) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "trade_date": [datetime.date(2026, 8, 20)] * n,
            "symbol": [f"00000{i}.SZ" for i in range(1, n + 1)],
            "factor_id": ["rsi_momentum"] * n,
            "value": [0.5, np.nan, 1.2][:n],
        }
    )


class TestBuildRows:
    def test_column_order_and_defaults(self):
        rows = build_feature_value_rows(_values())
        assert len(rows) == 3
        td, sym, fid, ver, val, src = rows[0]
        assert td == datetime.date(2026, 8, 20)
        assert sym == "000001.SZ"
        assert fid == "rsi_momentum"
        assert ver == "0.0.0"
        assert val == pytest.approx(0.5)
        assert src == "factor_dag"

    def test_nan_value_becomes_none(self):
        """预热期 NaN → None（CH NULL，不前向填充——PIT 铁律特征层落实）。"""
        rows = build_feature_value_rows(_values())
        assert rows[1][4] is None

    def test_custom_version(self):
        rows = build_feature_value_rows(_values(1), factor_version="1.2.3")
        assert rows[0][3] == "1.2.3"

    def test_missing_column_raises(self):
        df = _values().drop(columns=["factor_id"])
        with pytest.raises(ValueError, match="factor_id"):
            build_feature_value_rows(df)

    def test_empty_returns_empty(self):
        assert build_feature_value_rows(_values(0)) == []


class _FakeClient:
    def __init__(self):
        self.calls: list[tuple[str, list]] = []

    def execute(self, sql, rows):
        self.calls.append((sql, list(rows)))


class TestWriteFeatureValues:
    def test_insert_with_injected_client(self):
        client = _FakeClient()
        n = write_feature_values(_values(), client=client)
        assert n == 3
        assert len(client.calls) == 1
        sql, rows = client.calls[0]
        assert "c1_market.factor_feature_value" in sql
        assert "factor_version" in sql
        assert len(rows) == 3

    def test_chunking(self):
        df = pd.concat([_values(3)] * 2, ignore_index=True)  # 6 行
        client = _FakeClient()
        n = write_feature_values(df, client=client, chunk_size=2)
        assert n == 6
        assert [len(c[1]) for c in client.calls] == [2, 2, 2]

    def test_empty_no_write(self):
        client = _FakeClient()
        assert write_feature_values(_values(0), client=client) == 0
        assert client.calls == []

    def test_client_unavailable_raises(self, monkeypatch):
        import zephyr.factor.feature_store_writer as mod

        monkeypatch.setattr(mod, "_get_ch_client", lambda: None)
        with pytest.raises(RuntimeError, match="不可用"):
            write_feature_values(_values(1))


class TestSchemaContract:
    def test_schema_ddl_core_elements(self):
        from schemas.categories.factor_feature_value import (
            DATABASE,
            FACTOR_FEATURE_VALUE_DDL,
            INSERT_COLUMNS,
            TABLE_NAME,
        )

        assert f"{DATABASE}.{TABLE_NAME}" in FACTOR_FEATURE_VALUE_DDL
        assert "ReplacingMergeTree" in FACTOR_FEATURE_VALUE_DDL
        assert "toYYYYMM(trade_date)" in FACTOR_FEATURE_VALUE_DDL
        assert "factor_id" in FACTOR_FEATURE_VALUE_DDL
        assert "factor_version" in FACTOR_FEATURE_VALUE_DDL
        for col in ("trade_date", "symbol", "factor_id", "factor_version", "value", "data_source"):
            assert col in INSERT_COLUMNS
