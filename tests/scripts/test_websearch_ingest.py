# [BLUEPRINT] MOD-REGIME-P2-E8 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
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


def test_validate_rejects_bad_chain_status() -> None:
    # status 非法值
    errs = wi._validate_records(
        [{"type": "chain", "name": "x", "status": "deleted", "market": "cn", "source_doc": SD}],
        stocks=set(),
    )
    assert any("status 非法" in e for e in errs)
    # deprecated 缺 merged_into（SOP §4.6）
    errs2 = wi._validate_records(
        [{"type": "chain", "name": "x", "status": "deprecated", "market": "cn", "source_doc": SD}],
        stocks=set(),
    )
    assert any("merged_into" in e for e in errs2)
    # merged_into 非 chain_id 格式
    errs3 = wi._validate_records(
        [{"type": "chain", "name": "x", "status": "deprecated", "merged_into": "某某链",
          "market": "cn", "source_doc": SD}],
        stocks=set(),
    )
    assert any("merged_into 非 chain_id" in e for e in errs3)


def test_validate_passes_deprecated_chain() -> None:
    errs = wi._validate_records(
        [{"type": "chain", "name": "x", "status": "deprecated", "merged_into": "CH-abcdef123456",
          "market": "cn", "source_doc": SD}],
        stocks=set(),
    )
    assert errs == [], errs


# ---- UNLISTED 编码表契约（SOP §4.10，2026-09-08 开放问题9裁定：现在就统一格式） ----

def test_validate_unlisted_ue_format_passes() -> None:
    # UNLISTED:UE-{12hex} 引用编码表主键——唯一合法格式（混端/端点各自校验均通过）
    errs = wi._validate_records(
        [{"type": "company_edge", "source": "websearch", "from_symbol": "688019.SH",
          "to_symbol": "UNLISTED:UE-c29a843e1aac", "from_name": "安集科技", "to_name": "长江存储",
          "year": 2026, "market": "cn", "source_doc": SD,
          "valid_from": "2026-01-01", "as_of": "2026-09-08", "edge_type": "supplies_to"}],
        stocks={"688019.SH"},
    )
    assert errs == [], errs


def test_validate_unlisted_legacy_name_rejected() -> None:
    # 旧格式 UNLISTED:公司名（直写公司名）——必须拒绝，防双格式并存致夜班幻觉
    errs = wi._validate_records(
        [{"type": "company_edge", "source": "websearch", "from_symbol": "688019.SH",
          "to_symbol": "UNLISTED:长江存储", "from_name": "安集科技", "to_name": "长江存储",
          "year": 2026, "market": "cn", "source_doc": SD,
          "valid_from": "2026-01-01", "as_of": "2026-09-08", "edge_type": "supplies_to"}],
        stocks={"688019.SH"},
    )
    assert any("UNLISTED 旧格式" in e for e in errs), errs


def test_validate_unlisted_entity_record_rules() -> None:
    # 登记合法
    errs = wi._validate_records(
        [{"type": "unlisted_entity", "name": "华为", "country": "CN", "status": "unlisted",
          "source_doc": SD, "source": "websearch"}],
        stocks=set(),
    )
    assert errs == [], errs
    # status 非法枚举
    errs2 = wi._validate_records(
        [{"type": "unlisted_entity", "name": "华为", "status": "半上市",
          "source_doc": SD, "source": "websearch"}],
        stocks=set(),
    )
    assert any("status 非法" in e for e in errs2), errs2
    # listed 必带真代码
    errs3 = wi._validate_records(
        [{"type": "unlisted_entity", "name": "华为", "status": "listed",
          "source_doc": SD, "source": "websearch"}],
        stocks=set(),
    )
    assert any("listed_symbol" in e for e in errs3), errs3
    # listed_symbol 格式非法
    errs4 = wi._validate_records(
        [{"type": "unlisted_entity", "name": "华为", "status": "listed", "listed_symbol": "华为控股",
          "source_doc": SD, "source": "websearch"}],
        stocks=set(),
    )
    assert any("listed_symbol 非真代码" in e for e in errs4), errs4
    # 缺 name
    errs5 = wi._validate_records(
        [{"type": "unlisted_entity", "status": "unlisted", "source_doc": SD, "source": "websearch"}],
        stocks=set(),
    )
    assert any("缺 name" in e for e in errs5), errs5


def test_ingest_unlisted_entity_idempotent(tmp_path: Path) -> None:
    # 编码表登记走 ingest 通道（幂等）+ 上市标定（listed+listed_symbol）
    name = "__未上市测试TMP__"
    recs = [{"type": "unlisted_entity", "name": name, "country": "CN", "status": "unlisted",
             "source_doc": SD, "source": "websearch"}]
    p = _tmp_batch(tmp_path, recs)
    assert wi.cmd_ingest(str(p)) == 0
    assert wi.cmd_ingest(str(p)) == 0  # 幂等复跑
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    try:
        cur.execute("SELECT count(*) FROM ig_unlisted_entity WHERE name=%s", (name,))
        assert cur.fetchone()[0] == 1  # 无重复行
        # 上市标定：status→listed + 回填 listed_symbol（真代码格式）
        recs2 = [{"type": "unlisted_entity", "name": name, "country": "CN", "status": "listed",
                  "listed_symbol": "9973.HK", "source_doc": SD, "source": "websearch"}]
        assert wi.cmd_ingest(str(_tmp_batch(tmp_path, recs2))) == 0
        cur.execute("SELECT status, listed_symbol FROM ig_unlisted_entity WHERE name=%s", (name,))
        row = cur.fetchone()
        assert row[0] == "listed" and row[1] == "9973.HK"
    finally:
        cur.execute("DELETE FROM ig_unlisted_entity WHERE name=%s", (name,))
        conn.commit()
        conn.close()


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


def test_ingest_deprecated_chain_no_resurrect(tmp_path: Path) -> None:
    # deprecated 落库后，幂等复跑同链（不带 status，如常规定期刷新场景）不得翻回 active
    chain = "__废弃链TMP__"
    recs = [{"type": "chain", "name": chain, "category": "钢铁", "market": "cn",
             "status": "deprecated", "merged_into": "CH-cbfda16e6c04",
             "source_doc": SD, "source": "websearch"}]
    p = _tmp_batch(tmp_path, recs)
    assert wi.cmd_ingest(str(p)) == 0
    assert wi.cmd_ingest(str(p)) == 0  # 幂等复跑（带 status）
    # 重发不带 status 的常规记录（模拟刷新 category）——status 不回落 active
    recs2 = [{"type": "chain", "name": chain, "category": "钢铁", "market": "cn",
              "source_doc": SD, "source": "websearch"}]
    p2 = _tmp_batch(tmp_path, recs2)
    assert wi.cmd_ingest(str(p2)) == 0
    # 验证 status 仍为 deprecated（不复活）+ 清理
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    try:
        cur.execute("SELECT status FROM ig_chain WHERE name=%s", (chain,))
        assert cur.fetchone()[0] == "deprecated"
    finally:
        cur.execute("DELETE FROM ig_chain WHERE name=%s", (chain,))
        conn.commit()
        conn.close()


def test_ingest_node_company_resolves_existing_node(tmp_path: Path) -> None:
    # node 先写 + node_company/node_edge 按(链+环节名)解析：不重算 ID、不造重复行、不 FK 违规
    chain = "__节点解析测试TMP__"
    cid = wi._chain_id(chain)
    recs = [
        {"type": "chain", "name": chain, "category": "半导体", "version_year": 2026,
         "market": "cn", "source_doc": SD, "source": "websearch"},
        {"type": "node", "chain_name": chain, "name": "解析环节", "tier": "中游",
         "market": "cn", "source_doc": SD, "source": "websearch"},
        {"type": "node_company", "chain_name": chain, "node_name": "解析环节",
         "symbol": "300750.SZ", "role": "参与", "confidence": 0.5,
         "evidence_text": "测试证据一句", "market": "cn", "source_doc": SD, "source": "websearch"},
        {"type": "node", "chain_name": chain, "name": "解析下游", "tier": "下游",
         "market": "cn", "source_doc": SD, "source": "websearch"},
        {"type": "node_edge", "chain_name": chain, "from_node": "解析环节", "to_node": "解析下游",
         "edge_type": "structure", "market": "cn", "source_doc": SD, "source": "websearch"},
        # node 重发同批同环节 -> UPDATE 已有行，不插重复
        {"type": "node", "chain_name": chain, "name": "解析环节", "tier": "中游",
         "market": "cn", "source_doc": SD, "source": "websearch"},
    ]
    p = _tmp_batch(tmp_path, recs)
    assert wi.cmd_ingest(str(p)) == 0
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    # 验证+清理同连接用 read_only=False（writer 角色）：depgraph_reader 无 DELETE 权限
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    try:
        cur.execute("SELECT count(*) FROM ig_node WHERE chain_id=%s", (cid,))
        assert cur.fetchone()[0] == 2  # 无重复节点行
        cur.execute(
            "SELECT count(*) FROM ig_node_company WHERE node_id IN "
            "(SELECT node_id FROM ig_node WHERE chain_id=%s) AND symbol='300750.SZ'",
            (cid,),
        )
        assert cur.fetchone()[0] == 1  # 落位挂到真实节点
        cur.execute(
            "SELECT count(*) FROM ig_edge WHERE from_node IN "
            "(SELECT node_id FROM ig_node WHERE chain_id=%s) "
            "AND to_node IN (SELECT node_id FROM ig_node WHERE chain_id=%s)",
            (cid, cid),
        )
        assert cur.fetchone()[0] == 1  # 边两端是真实节点
        # 引用不存在节点 -> 报错整批回滚
        (tmp_path / "bad").mkdir(exist_ok=True)
        bad = [{"type": "node_company", "chain_name": chain, "node_name": "不存在环节",
                "symbol": "300750.SZ", "confidence": 0.5, "market": "cn",
                "source_doc": SD, "source": "websearch"}]
        with pytest.raises(Exception):
            wi.cmd_ingest(str(_tmp_batch(tmp_path / "bad", bad)))
    finally:
        cur.execute(
            "DELETE FROM ig_node_company WHERE node_id IN (SELECT node_id FROM ig_node WHERE chain_id=%s)",
            (cid,),
        )
        cur.execute("DELETE FROM ig_edge WHERE from_node IN (SELECT node_id FROM ig_node WHERE chain_id=%s)", (cid,))
        cur.execute("DELETE FROM ig_node WHERE chain_id=%s", (cid,))
        cur.execute("DELETE FROM ig_chain WHERE chain_id=%s", (cid,))
        conn.commit()
        conn.close()
