# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] tests.ai_layer.intake.test_dedup
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.intake.dedup; zephyr.governance.depgraph_schema (PG 可达性自探测)
# [CONSUMERS] pytest tests/ai_layer/intake/test_dedup.py
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 只读用例（不写生产 ai_intake）；五比对面逐面留痕，未比对面禁记成比过无命中；
#              PG 不可达=skip 而非假绿（判据同 conftest，但本件自带 needs_pg，不 import 在途 conftest——
#              该文件归 st-ff-alarm2-20260918 在办，跨道 import 其未落地符号会造成收集期 ImportError）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §2.3
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；known-gap 钉在判据收紧时主动变红；可达性探测异常=判不可达（skip，不吞真缺陷）
# [TESTS] tests/ai_layer/intake/test_dedup.py
# [TTL] permanent
"""test_dedup - SimHash64 判据两侧陡度 + 五比对面登记留痕（DESIGN 施工项 3 验收）。"""
from __future__ import annotations

import pytest

from zephyr.ai_layer.intake.card_store import hamming
from zephyr.ai_layer.intake.dedup import (
    ALL_FACES,
    HAMMING_K,
    IntakeDedup,
    content_fingerprint,
    normalize_text,
    simhash64,
    tokenize,
)


def _pg_reachable() -> bool:
    """真连一次 PG；任何异常=不可达（据此 skip，而非假绿）。

    连接经 ``release_depgraph_pg_connection`` 归池（池化连接禁直接 close）。
    """
    conn = None
    try:
        from zephyr.governance.depgraph_schema import (
            get_depgraph_pg_connection,
            release_depgraph_pg_connection,
        )

        conn = get_depgraph_pg_connection(read_only=True)
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001 - 可达性探测面，任何异常一律判不可达
        return False
    finally:
        if conn is not None:
            from zephyr.governance.depgraph_schema import release_depgraph_pg_connection

            release_depgraph_pg_connection(conn)


needs_pg = pytest.mark.skipif(not _pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")

T_BASE = ("MAP-Elites 质量多样性：以行为描述子网格取代单目标最优，逐格保留最高适应度个体，"
          "变异体入格竞争胜出者留下，规避局部最优陷阱")
T_EDIT1 = T_BASE + "（原文照抄后补一句）"
T_REWRITE = ("质量多样性网格照明：用行为描述子格子代替单一最优解，逐格保存精英解以躲开局部最优，"
             "把解映射到行为特征坐标形成网格，变异后代进格比拼留下赢家")
T_UNRELATED = "国债期货基差收敛的周内季节性，用隔夜跳空幅度做持仓配比微调"


def _dist(left: str, right: str) -> int:
    return hamming(simhash64(left), simhash64(right))


def test_simhash_is_64bit_and_deterministic() -> None:
    fp = simhash64(T_BASE)
    assert 0 <= fp < (1 << 64)
    assert simhash64(T_BASE) == fp


def test_normalize_collapses_width_and_case() -> None:
    assert normalize_text("  ABC   de  ") == "abc de"
    assert normalize_text("ＡＢＣ") == normalize_text("ABC")
    assert normalize_text(None) == ""


def test_tokenize_mixes_cjk_bigram_and_ascii() -> None:
    toks = tokenize("MA5 均线 cross")
    assert "ma5" in toks and "均线" in toks and "cross" in toks


def test_degenerate_empty_text_yields_zero_fingerprint() -> None:
    assert simhash64("") == 0
    assert tokenize("的 了 和 是") == [] or tokenize("   ") == []


def test_exact_same_text_distance_zero() -> None:
    assert _dist(T_BASE, T_BASE) == 0


def test_heavy_rewrite_stays_far_beyond_k() -> None:
    assert _dist(T_BASE, T_REWRITE) > HAMMING_K


def test_unrelated_text_is_far() -> None:
    assert _dist(T_BASE, T_UNRELATED) > HAMMING_K * 2


def test_content_fingerprint_stable_and_url_sensitive() -> None:
    a = content_fingerprint("https://arxiv.org/abs/1504.04909", "MAP-Elites")
    assert a == content_fingerprint("https://arxiv.org/abs/1504.04909", "MAP-Elites")
    assert len(a) == 64
    assert a != content_fingerprint("https://arxiv.org/abs/2506.13131", "MAP-Elites")


def test_known_gap_single_edit_escapes_k3() -> None:
    """钉住实测缺陷：轻改一个分句的中文近重复对距离=6 大于 k=3，近似层漏检（换皮防护弱于设计预期）。

    本用例不粉饰：断言的是漏检确实发生。一旦 k 或特征口径被收紧使距离落入 k 内，本钉即红，
    逼施工面显式处置（同步撤钉并更新 adjudications/req_aibase_02）。
    """
    dist = _dist(T_BASE, T_EDIT1)
    assert dist > HAMMING_K, "轻改距离=%d 已落入 k<=%d，判据已收紧请撤掉本 known-gap 钉" % (dist, HAMMING_K)


def test_all_faces_constant_matches_design() -> None:
    assert ALL_FACES == ("self", "chart", "indicator", "algo_flow", "L7")


@needs_pg
def test_five_faces_compare_and_l7_not_compared() -> None:
    dedup = IntakeDedup(schema="ai_intake")
    report = dedup.scan(T_BASE)
    assert set(report.compared) | set(report.not_compared) == set(ALL_FACES)
    assert "L7" in report.not_compared
    assert "self" in report.compared
    counts = dedup.snapshot_counts()
    assert counts["chart"] > 0 and counts["indicator"] > 0 and counts["algo_flow"] > 0
    for face, n in counts.items():
        if face != "L7" and n > 0:
            assert face in report.compared, "%s 面有快照却未参与比对" % face


@needs_pg
def test_dedup_query_readonly_shape() -> None:
    hits = IntakeDedup(schema="ai_intake").dedup_query(T_BASE)
    assert isinstance(hits, list)
    for h in hits:
        assert set(h) == {"card_id", "simhash", "hamming", "funnel_stage"}
