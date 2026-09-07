# [MODULE] tests.scripts.test_websearch_ingest
# [DOMAIN] D_GOV_ENFORCEMENT
# [MATURITY] production
# [TTL] permanent
"""websearch_ingest 三测（SOP §5 登记要求：幂等/校验拒绝/事务回滚）。

PG 不可达环境自动 skip（CI 无 depgraph 库时不阻断）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "industry_graph"))

import websearch_ingest as wi  # noqa: E402

SD = "测试查询|https://example.com/doc|2026-09-07"


def _pg_up() -> bool:
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection()
        conn.close()
        return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(not _pg_up(), reason="PG depgraph 库不可达")


# ---- 纯校验单测（无 PG 依赖，但共享 skip 标记简化处理；校验函数本身可独立测） ----

def test_validate_rejects_bad_sourcedoc() -> None:
    errs = wi._validate_records(
        [{"type": "company_edge", "source": "websearch", "from_symbol": "300750.SZ", "to_symbol": "002463.SZ",
          "year": 2026, "market": "cn", "source_doc": "无三段式", "valid_from": "2026-01-01", "as_of": "2026-01-01"}],
        stocks={"300750.SZ", "002463.SZ"},
    )
    assert any("source_doc" in e for e in errs)


def test_validate_rejects_high_confidence() -> None:
    errs = wi._validate_records(
        [{"type": "node_company", "source": "websearch", "symbol": "300750.SZ", "market": "cn",
          "source_doc": SD, "confidence": 0.9, "chain_name": "x", "node_name": "y"}],
        stocks={"300750.SZ"},
    )
    assert any("confidence" in e for e in errs)


def test_validate_rejects_bad_tier_and_suffix() -> None:
    errs = wi._validate_records(
        [{"type": "node", "source": "websearch", "chain_name": "x", "name": "某环节-材料", "tier": "材料",
          "market": "cn", "source_doc": SD}],
        stocks=set(),
    )
    assert any("-tier 后缀" in e for e in errs)
    errs2 = wi._validate_records(
        [{"type": "node", "source": "websearch", "chain_name": "x", "name": "环节", "tier": "unspecified",
          "market": "cn", "source_doc": SD}],
        stocks=set(),
    )
    assert any("禁 tier" in e for e in errs2)


def test_validate_rejects_bad_symbol_and_missing_pit() -> None:
    errs = wi._validate_records(
        [{"type": "node_company", "source": "websearch", "symbol": "300750", "market": "cn",
          "source_doc": SD, "chain_name": "x", "node_name": "y"}],
        stocks={"300750.SZ"},
    )
    assert any("symbol 非法" in e for e in errs)
    errs2 = wi._validate_records(
        [{"type": "company_edge", "source": "websearch", "from_symbol": "300750.SZ", "to_symbol": "002463.SZ",
          "year": 2026, "market": "cn", "source_doc": SD}],
        stocks={"300750.SZ", "002463.SZ"},
    )
    assert any("PIT" in e for e in errs2)


def test_validate_passes_good_record() -> None:
    errs = wi._validate_records(
        [{"type": "company_edge", "source": "websearch", "from_symbol": "300750.SZ", "to_symbol": "002463.SZ",
          "year": 2026, "market": "cn", "source_doc": SD, "valid_from": "2026-06-30", "as_of": "2026-08-30",
          "edge_type": "supplies_to"}],
        stocks={"300750.SZ", "002463.SZ"},
    )
    assert errs == [], errs


# ---- 集成三测（真 PG）----

def _tmp_batch(tmp_path: Path, records: list[dict]) -> Path:
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"batch_id": "test", "records": records}, ensure_ascii=False), encoding="utf-8")
    return p


def test_ingest_idempotent(tmp_path: Path) -> None:
    recs = [{"type": "chain", "name": "__测试链TMP__", "category": "半导体", "version_year": 2026,
             "market": "cn", "source_doc": SD, "source": "websearch"}]
    p = _tmp_batch(tmp_path, recs)
    assert wi.cmd_ingest(str(p)) == 0
    assert wi.cmd_ingest(str(p)) == 0  # 幂等复跑
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute("DELETE FROM ig_chain WHERE name='__测试链TMP__'")
    conn.commit()
    conn.close()


def test_ingest_rejects_invalid_batch(tmp_path: Path) -> None:
    recs = [{"type": "node", "source": "websearch", "chain_name": "x", "name": "坏-设备", "tier": "设备",
             "market": "cn", "source_doc": "bad"}]
    p = _tmp_batch(tmp_path, recs)
    assert wi.cmd_ingest(str(p)) == 3  # 校验拒绝退出码


def test_ingest_transaction_rollback(tmp_path: Path) -> None:
    # 两条 record，第二条 type 非法 -> 整批回滚，第一条不落库
    recs = [
        {"type": "chain", "name": "__回滚测试TMP__", "market": "cn", "source_doc": SD, "source": "websearch"},
        {"type": "不存在的类型", "market": "cn"},
    ]
    p = _tmp_batch(tmp_path, recs)
    with pytest.raises(Exception):
        wi.cmd_ingest(str(p))
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ig_chain WHERE name='__回滚测试TMP__'")
    assert cur.fetchone()[0] == 0  # 回滚生效
    conn.close()
