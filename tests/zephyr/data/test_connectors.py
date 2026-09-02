# [BLUEPRINT] MOD-L00-005 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [TTL] permanent
"""数据连接器（MOD-L00-005 data/connectors/）单元测试——抽象契约 + FileConnector 具体实现。"""

from __future__ import annotations

import pytest

from zephyr.data.connectors import (
    ConnectorError,
    ConnectorRequest,
    DataConnector,
    FileConnector,
)


@pytest.fixture()
def csv_dir(tmp_path):
    """夹具目录：两个数据集 CSV。"""
    (tmp_path / "kline_daily.csv").write_text(
        "trade_date,symbol,close\n2026-08-20,600519,1700.0\n2026-08-21,600519,1710.0\n2026-08-21,000001,11.5\n",
        encoding="utf-8",
    )
    (tmp_path / "sector.csv").write_text("name,score\nA,1\n", encoding="utf-8")
    return tmp_path


class TestFileConnector:
    def test_connect_and_health(self, csv_dir):
        c = FileConnector(csv_dir)
        assert c.health_check() is False  # 未 connect
        c.connect()
        assert c.health_check() is True
        c.connect()  # 幂等
        assert c.health_check() is True
        c.close()
        assert c.health_check() is False

    def test_connect_missing_dir_raises(self, tmp_path):
        with pytest.raises(ConnectorError):
            FileConnector(tmp_path / "nope").connect()

    def test_fetch_without_connect_raises(self, csv_dir):
        with pytest.raises(ConnectorError):
            FileConnector(csv_dir).fetch_batch(ConnectorRequest(dataset="kline_daily"))

    def test_fetch_all_rows(self, csv_dir):
        c = FileConnector(csv_dir)
        c.connect()
        batch = c.fetch_batch(ConnectorRequest(dataset="kline_daily"))
        assert batch.error is None
        assert batch.columns == ("trade_date", "symbol", "close")
        assert len(batch.rows) == 3
        assert batch.source.startswith("file:")

    def test_fetch_symbol_filter(self, csv_dir):
        c = FileConnector(csv_dir)
        c.connect()
        batch = c.fetch_batch(ConnectorRequest(dataset="kline_daily", symbols=("600519",)))
        assert len(batch.rows) == 2
        assert all(r[1] == "600519" for r in batch.rows)

    def test_fetch_date_range_filter(self, csv_dir):
        c = FileConnector(csv_dir)
        c.connect()
        batch = c.fetch_batch(ConnectorRequest(dataset="kline_daily", start="2026-08-21", end="2026-08-21"))
        assert len(batch.rows) == 2

    def test_fetch_missing_dataset_raises(self, csv_dir):
        c = FileConnector(csv_dir)
        c.connect()
        with pytest.raises(ConnectorError):
            c.fetch_batch(ConnectorRequest(dataset="ghost"))

    def test_no_date_column_dataset_unfiltered(self, csv_dir):
        """无 trade_date 列的数据集：日期过滤不适用，全量返回。"""
        c = FileConnector(csv_dir)
        c.connect()
        batch = c.fetch_batch(ConnectorRequest(dataset="sector", start="2026-01-01"))
        assert len(batch.rows) == 1


class TestAbstraction:
    def test_file_connector_is_data_connector(self, csv_dir):
        assert isinstance(FileConnector(csv_dir), DataConnector)

    def test_abc_not_instantiable(self):
        with pytest.raises(TypeError):
            DataConnector()  # type: ignore[abstract]
