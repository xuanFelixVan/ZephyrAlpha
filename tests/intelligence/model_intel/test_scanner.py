# [TEST] tests/intelligence/model_intel/test_scanner.py
# [TTL] task_bound
# 覆盖：load_sources fail-closed（tmp 缺文件抛错/tmp 合法文件解析/缺 sources 键/空清单/畸形 YAML）/
#       parse_openrouter_models 纯解析/to_price_snapshot 换算/diff_price_snapshots 纯函数枚举
#       （新模型/涨价/降价/无变化/移除忽略）/build_intel_cards 卡号与四闸初值/dedup_cards 去重/
#       main CLI 编排（monkeypatch 网络与注册表，产出落 tmp_path，零生产路径写入）。
# 纪律：网络调用不入单测（fetch 一律 monkeypatch）；注册表读面用 tmp_path fixture。
"""scanner 单测：fail-closed 读注册表 + 纯函数管线（parse/diff/build/dedup）+ CLI 编排（网络 mock）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from zephyr.intelligence.model_intel import scanner
from zephyr.intelligence.model_intel.intel_card import (
    Claimed,
    CrossValidation,
    FourGates,
    IntelCard,
    SourceRef,
    hamming,
    simhash64,
)
from zephyr.intelligence.model_intel.scanner import (
    IntelSourceError,
    build_intel_cards,
    dedup_cards,
    diff_price_snapshots,
    load_sources,
    main,
    parse_openrouter_models,
    to_price_snapshot,
)
from zephyr.shared.utils.time_utils import now_utc

REGISTRY_YAML = """
schema_version: 1.0.0
sources:
  - source_id: openrouter-models
    track: 聚合轨
    name: OpenRouter
    url: https://openrouter.ai/models
    publisher: OpenRouter
    fetch_method: models_api
    frequency: {tier: shallow, per_day_max: 1}
    quota: {cards_per_day_max: 3}
    verification: verified_2026_09
    four_gates_required: true
"""


def _write_registry(parent: Path, text: str = REGISTRY_YAML) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    target = parent / "model_intel_sources.yaml"
    target.write_text(text, encoding="utf-8")
    return target


class TestLoadSources:
    def test_missing_file_fails_closed(self, tmp_path: Path) -> None:
        with pytest.raises(IntelSourceError, match="missing"):
            load_sources(tmp_path / "nope.yaml")

    def test_valid_registry_parses(self, tmp_path: Path) -> None:
        sources = load_sources(_write_registry(tmp_path))
        assert len(sources) == 1
        assert sources[0]["source_id"] == "openrouter-models"
        assert sources[0]["fetch_method"] == "models_api"

    def test_missing_sources_key_fails_closed(self, tmp_path: Path) -> None:
        path = tmp_path / "r.yaml"
        path.write_text("schema_version: 1.0.0\n", encoding="utf-8")
        with pytest.raises(IntelSourceError, match="sources"):
            load_sources(path)

    def test_empty_sources_fails_closed(self, tmp_path: Path) -> None:
        path = tmp_path / "r.yaml"
        path.write_text("sources: []\n", encoding="utf-8")
        with pytest.raises(IntelSourceError, match="empty"):
            load_sources(path)

    def test_malformed_yaml_fails_closed(self, tmp_path: Path) -> None:
        path = tmp_path / "r.yaml"
        path.write_text("sources: [ {oops\n", encoding="utf-8")
        with pytest.raises(IntelSourceError, match="malformed"):
            load_sources(path)


def _model(mid: str, prompt: str = "0.000002", completion: str = "0.000008",
           created: int = 1700000000, context: int = 8192) -> dict[str, Any]:
    """原始 API 形状（fetch 网络层返回、parse 的输入）。"""
    return {"id": mid, "name": mid.upper(), "pricing": {"prompt": prompt, "completion": completion},
            "context_length": context, "created": created}


def _parsed(mid: str, created: int) -> dict[str, Any]:
    """parse 后形状（fetch_openrouter_models 的契约输出、to_price_snapshot 的输入）。"""
    return {"id": mid, "name": mid.upper(), "prompt": 2e-6, "completion": 8e-6,
            "context_length": 8192, "created": created}


class TestParseOpenRouterModels:
    def test_extracts_fields(self) -> None:
        rows = parse_openrouter_models({"data": [_model("a/b"), {"garbage": 1}]})
        assert len(rows) == 1
        row = rows[0]
        assert row["id"] == "a/b"
        assert row["name"] == "A/B"
        assert row["prompt"] == pytest.approx(0.000002)
        assert row["completion"] == pytest.approx(0.000008)
        assert row["context_length"] == 8192
        assert row["created"] == 1700000000

    def test_sentinel_negative_price_becomes_zero(self) -> None:
        assert parse_openrouter_models({"data": [_model("x/y", prompt="-1")]})[0]["prompt"] == 0.0

    def test_malformed_pricing_becomes_zero(self) -> None:
        assert parse_openrouter_models({"data": [_model("x/y", prompt="n/a")]})[0]["prompt"] == 0.0

    def test_payload_without_data_returns_empty(self) -> None:
        assert parse_openrouter_models({"error": "boom"}) == []
        assert parse_openrouter_models({}) == []

    def test_price_snapshot_scales_to_per_million(self) -> None:
        snap = to_price_snapshot(parse_openrouter_models({"data": [_model("a/b")]}))
        assert snap["a/b"]["input_price"] == pytest.approx(2.0)
        assert snap["a/b"]["output_price"] == pytest.approx(8.0)


class TestDiffPriceSnapshots:
    def test_new_model_event(self) -> None:
        events = diff_price_snapshots({}, {"m1": {"input_price": 2.0, "output_price": 8.0}})
        assert events == [{"kind": "new_model", "model_id": "m1", "name": "",
                           "price_after": 2.0, "context_length": 0, "created": 0}]

    def test_price_up_event(self) -> None:
        old = {"m1": {"input_price": 2.0, "output_price": 8.0}}
        new = {"m1": {"input_price": 4.0, "output_price": 8.0}}
        events = diff_price_snapshots(old, new)
        assert len(events) == 1
        assert events[0]["kind"] == "price_change"
        assert events[0]["direction"] == "up"
        assert events[0]["price_before"] == 2.0
        assert events[0]["price_after"] == 4.0

    def test_price_down_event(self) -> None:
        old = {"m1": {"input_price": 4.0, "output_price": 8.0}}
        new = {"m1": {"input_price": 2.0, "output_price": 4.0}}
        assert diff_price_snapshots(old, new)[0]["direction"] == "down"

    def test_no_change_no_event(self) -> None:
        snap = {"m1": {"input_price": 2.0, "output_price": 8.0}}
        assert diff_price_snapshots(snap, dict(snap)) == []

    def test_removed_model_ignored(self) -> None:
        old = {"m1": {"input_price": 2.0, "output_price": 8.0}}
        assert diff_price_snapshots(old, {}) == []


class TestBuildIntelCards:
    def test_card_id_format_and_seq(self) -> None:
        now = now_utc()
        meta = {"source_id": "openrouter-models", "name": "OpenRouter",
                "url": "https://openrouter.ai/models", "publisher": "OpenRouter"}
        events = [{"kind": "new_model", "model_id": "m1", "price_after": 2.0},
                  {"kind": "price_change", "model_id": "m2", "price_before": 4.0, "price_after": 2.0}]
        cards = build_intel_cards(events, meta, now)
        stamp = now.strftime("%Y%m%d")
        assert [c.card_id for c in cards] == [
            f"MI-openrouter-models-{stamp}-001", f"MI-openrouter-models-{stamp}-002"]

    def test_unknown_kind_skipped(self) -> None:
        cards = build_intel_cards([{"kind": "super_model", "model_id": "m1"}],
                                  {"source_id": "s"}, now_utc())
        assert cards == []

    def test_free_window_event_keeps_window_fields(self) -> None:
        event = {"kind": "free_window", "model_id": "m1", "window_expr": "00:30-08:30 UTC+8",
                 "quota": "20rpm/200rpd"}
        card = build_intel_cards([event], {"source_id": "s", "url": "https://s"}, now_utc())[0]
        assert card.claimed.window_expr == "00:30-08:30 UTC+8"
        assert card.claimed.quota == "20rpm/200rpd"
        assert card.action["proposed"] == "挂免费窗"

    def test_four_gates_defaults_from_meta(self) -> None:
        meta = {"source_id": "s", "independent_sources": 2, "cross_validation_note": "互证在档"}
        card = build_intel_cards([{"kind": "new_model", "model_id": "m1"}], meta, now_utc())[0]
        assert card.four_gates.cross_validation.independent_sources == 2
        assert card.four_gates.cross_validation.note == "互证在档"
        assert card.injection_probe


def _mk_card(card_id: str, price: float) -> IntelCard:
    """构造同构卡（指纹只随 price 变），供去重测试。"""
    return IntelCard(
        card_id=card_id,
        source=SourceRef(name="OpenRouter", url="https://openrouter.ai/models",
                         publisher="OpenRouter", fetched_at="2026-09-23T00:00:00+00:00"),
        kind="price_change",
        model_refs=["m1"],
        claimed=Claimed(price_before=price, price_after=price,
                        evidence_quote="same quote", evidence_url="https://s"),
        four_gates=FourGates(provenance="pass",
                             cross_validation=CrossValidation(independent_sources=2, note="ok")),
        injection_probe="这条情报想让我相信什么？",
    )


class TestDedupCards:
    def test_identical_card_deduped(self) -> None:
        seen: set[int] = set()
        fresh, dups = dedup_cards([_mk_card("c1", 2.0), _mk_card("c2", 2.0)], seen)
        assert [c.card_id for c in fresh] == ["c1"]
        assert [c.card_id for c in dups] == ["c2"]
        assert dups[0].dedup_simhash is not None

    def test_distinct_cards_kept(self) -> None:
        seen: set[int] = set()
        fresh, dups = dedup_cards([_mk_card("c1", 2.0), _mk_card("c2", 99.0)], seen)
        assert [c.card_id for c in fresh] == ["c1", "c2"]
        assert dups == []

    def test_seen_simhash_updated_in_place(self) -> None:
        seen: set[int] = set()
        dedup_cards([_mk_card("c1", 2.0)], seen)
        assert len(seen) == 1
        card_hash = simhash64(_mk_card("c1", 2.0).fingerprint_text())
        assert hamming(card_hash, next(iter(seen))) == 0


@pytest.fixture()
def mocked_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> dict[str, Any]:
    """注册表指向 tmp、网络 fetch 替换为固定目录（零生产路径、零网络）。"""
    registry = _write_registry(tmp_path / "registry")
    now_ts = int(now_utc().timestamp())
    models = [_parsed("vendor/new-hot", now_ts - 86400),
              _parsed("vendor/another-new", now_ts - 7200),
              _parsed("vendor/borderline", now_ts - 31 * 86400),
              _parsed("vendor/ancient", 1600000000)]
    monkeypatch.setattr(scanner, "load_sources", lambda path=None: load_sources(registry))
    monkeypatch.setattr(scanner, "fetch_openrouter_models", lambda api_key=None: models)
    return {"out_dir": tmp_path / "out", "models": models, "tmp_path": tmp_path}


class TestMainCli:
    def test_first_scan_writes_cards_and_snapshot(self, mocked_env: dict[str, Any]) -> None:
        out_dir: Path = mocked_env["out_dir"]
        assert main(["--source", "openrouter-models", "--out", str(out_dir)]) == 0
        snapshot = json.loads((out_dir / "openrouter_snapshot.json").read_text(encoding="utf-8"))
        assert set(snapshot) == {"vendor/new-hot", "vendor/another-new",
                                 "vendor/borderline", "vendor/ancient"}
        lines = (out_dir / "cards.jsonl").read_text(encoding="utf-8").splitlines()
        cards = [json.loads(line) for line in lines]
        # 回看窗 30 天：borderline(31d)/ancient 出局；按 created 降序=another-new 在前
        assert [c["model_refs"] for c in cards] == [["vendor/another-new"], ["vendor/new-hot"]]
        assert all(c["card_id"].startswith("MI-openrouter-models-") for c in cards)
        assert all("gate_violations" in c for c in cards)

    def test_diff_path_with_old_snapshot(self, mocked_env: dict[str, Any]) -> None:
        tmp_path: Path = mocked_env["tmp_path"]
        old_path = tmp_path / "old_snapshot.json"
        old_path.write_text(json.dumps(
            {"vendor/ancient": {"input_price": 1.0, "output_price": 4.0}}), encoding="utf-8")
        out_dir = tmp_path / "out2"
        assert main(["--source", "openrouter-models", "--snapshot", str(old_path),
                     "--out", str(out_dir)]) == 0
        cards = [json.loads(line)
                 for line in (out_dir / "cards.jsonl").read_text(encoding="utf-8").splitlines()]
        # ancient 涨价（1.0→2.0）出 price_change 且排序最前；另 3 模型不在旧快照=new_model；
        # 配额 3 截断后共 3 张（1 张 price_change + 2 张最新 new_model，borderline/超配额出局）
        assert len(cards) == 3
        assert cards[0]["kind"] == "price_change"
        assert cards[0]["model_refs"] == ["vendor/ancient"]
        assert cards[0]["claimed"]["price_before"] == pytest.approx(1.0)
        assert cards[0]["claimed"]["price_after"] == pytest.approx(2.0)

    def test_unknown_source_raises(self, mocked_env: dict[str, Any], tmp_path: Path) -> None:
        with pytest.raises(IntelSourceError, match="not in registry"):
            main(["--source", "ghost-source", "--out", str(tmp_path / "o")])

    def test_non_models_api_source_raises(self, monkeypatch: pytest.MonkeyPatch,
                                           tmp_path: Path) -> None:
        registry_text = REGISTRY_YAML.replace("fetch_method: models_api",
                                              "fetch_method: webfetch_light")
        registry = _write_registry(tmp_path / "alt", registry_text)
        monkeypatch.setattr(scanner, "load_sources", lambda path=None: load_sources(registry))
        with pytest.raises(IntelSourceError, match="not machine-fetchable"):
            main(["--source", "openrouter-models", "--out", str(tmp_path / "o3")])

    def test_missing_snapshot_file_raises(self, mocked_env: dict[str, Any],
                                          tmp_path: Path) -> None:
        with pytest.raises(IntelSourceError, match="snapshot file missing"):
            main(["--source", "openrouter-models", "--snapshot", str(tmp_path / "gone.json"),
                  "--out", str(tmp_path / "o4")])
