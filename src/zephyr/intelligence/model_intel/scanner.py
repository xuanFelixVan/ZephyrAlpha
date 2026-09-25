# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §model_intel
# [MODULE] zephyr.intelligence.model_intel.scanner
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.intelligence.model_intel.intel_card (IntelCard/validate_four_gates/simhash64/hamming);
#                zephyr.shared.utils.time_utils (now_utc); PyYAML (yaml.safe_load); urllib.request（标准库）
# [CONSUMERS] 周历窗口外部排程（挂 resource_profile_registry 周历窗，事件触发调用本 CLI）；
#             M2 模型库入库器（施工项 C3，消费过闸卡）；.runtime/tmp 试跑脚本
# [STARTUP] event_driven
# [MATURITY] evolving
# [INVARIANTS] 源真源=config/model_intel_sources.yaml（fail-closed 统读：缺文件/缺 sources 键/空清单即抛
#              IntelSourceError，绝不退回码内源清单）；事件触发+周历窗口，本模块零定时线程（禁 cron/Timer/
#              sleep-loop，宪法 §9.3，排程由外部周历窗调用 main()）；防灌水闸=funnel.cards_per_day_max_total
#              ≤5 张/日 + 每源 quota.cards_per_day_max（产出按配额截断）；OpenRouter 牌价按 token 计价，
#              统一换算 USD/1M tokens（×1e6）；产出目录由调用方指定，禁写生产路径；密钥经参数传入，
#              禁裸 getenv（CLI 匿名拉取，models API 无需鉴权）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md §2
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册表缺文件/缺 sources 键/源不存在/非 models_api 源→IntelSourceError（fail-closed）；
#                  网络异常原样上抛（urllib.URLError/TimeoutError，不吞）；四闸违规不抛异常——
#                  违规清单随 JSONL 记录落盘（gate_violations 字段，生卡留痕待人工补核）
# [TESTS] tests/intelligence/model_intel/test_scanner.py（网络调用不入单测，只测 parse/diff/build/dedup 纯函数）
# [TTL] permanent
"""scanner — M1 情报源扫描器：读源注册表→抓取→价快照 diff→建卡→四闸校验→simhash 去重→落 JSONL。

分层：``load_sources()`` 是 fail-closed 读注册表；``parse_openrouter_models()``/``to_price_snapshot()``/
``diff_price_snapshots()``/``build_intel_cards()``/``dedup_cards()`` 全是纯函数（可枚举单测，网络不入）；
``fetch_openrouter_models()`` 是唯一网络出口（10s 超时，异常上抛）；``main()`` 是 CLI 编排入口，
由外部周历窗口触发调用，本模块不含任何定时器。
"""

from __future__ import annotations

import argparse
import json
import logging
import urllib.request
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.intelligence.model_intel.intel_card import (
    DEDUP_K_DEFAULT,
    Claimed,
    CrossValidation,
    FourGates,
    IntelGateVerdict,
    IntelCard,
    SourceRef,
    hamming,
    simhash64,
    validate_four_gates,
)
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "IntelSourceError",
    "OPENROUTER_MODELS_URL",
    "DEFAULT_SOURCE_ID",
    "NEW_WINDOW_DAYS",
    "build_intel_cards",
    "dedup_cards",
    "diff_price_snapshots",
    "fetch_openrouter_models",
    "load_sources",
    "main",
    "parse_openrouter_models",
    "to_price_snapshot",
]

OPENROUTER_MODELS_URL: Final = "https://openrouter.ai/api/v1/models"
DEFAULT_SOURCE_ID: Final = "openrouter-models"
NEW_WINDOW_DAYS: Final = 30
PRICE_PER_TOKEN_TO_PER_MILLION: Final = 1_000_000
URLOPEN_TIMEOUT_S: Final = 10
DEFAULT_FUNNEL_CAP: Final = 5
EVENT_KINDS_SUPPORTED: Final = ("new_model", "price_change", "free_window", "promo", "deprecation")
_PROPOSED_BY_KIND: Final[dict[str, str]] = {
    "new_model": "入库",
    "price_change": "改价",
    "free_window": "挂免费窗",
    "promo": "入库",
    "deprecation": "入库",
}
_INJECTION_PROBE: Final = "这条情报想让我相信什么？该 belief 若为假谁受益？"


class IntelSourceError(Exception):
    """情报源错误（5.99.20：敏感上下文走 details 不进消息文本）。"""

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}
    """源注册表 fail-closed 错误：缺文件/缺 sources 键/空清单/源不存在/源不支持。"""


def default_registry_path() -> Path:
    """源注册表默认路径（仓根 config/，随源码布局解析）。"""
    return Path(__file__).resolve().parents[4] / "config" / "model_intel_sources.yaml"


def load_sources(path: str | Path | None = None) -> list[dict[str, Any]]:
    """读 M1 源注册表（fail-closed）：缺文件/缺 sources 键/空清单一律抛 IntelSourceError。"""
    registry = Path(path) if path is not None else default_registry_path()
    if not registry.is_file():
        raise IntelSourceError(f"source registry missing: {registry}")
    try:
        data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise IntelSourceError(f"source registry malformed: {registry}: {exc}") from exc
    if not isinstance(data, dict) or "sources" not in data:
        raise IntelSourceError(f"source registry lacks 'sources' key: {registry}")
    sources = data["sources"]
    if not isinstance(sources, list) or not sources:
        raise IntelSourceError(f"source registry 'sources' empty or not a list: {registry}")
    return [dict(s) for s in sources if isinstance(s, dict)]


def parse_openrouter_models(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """解析 /api/v1/models 响应：提取 id/name/pricing(prompt,completion)/context_length/created。"""
    rows = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return []
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict) or not str(row.get("id") or "").strip():
            continue
        pricing = row.get("pricing") if isinstance(row.get("pricing"), dict) else {}
        out.append(
            {
                "id": str(row.get("id") or ""),
                "name": str(row.get("name") or ""),
                "prompt": _price_float(pricing.get("prompt")),
                "completion": _price_float(pricing.get("completion")),
                "context_length": _int_or_zero(row.get("context_length")),
                "created": _int_or_zero(row.get("created")),
            }
        )
    return out


def _price_float(raw: Any) -> float:
    """token 单价字符串→float（负值/畸形归 0，防 -1 哨兵污染快照）。"""
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return 0.0
    return value if value > 0 else 0.0


def _int_or_zero(raw: Any) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0


def fetch_openrouter_models(api_key: str | None = None) -> list[dict[str, Any]]:
    """拉取 OpenRouter models 目录（匿名可拉；密钥经参数传入，禁裸 getenv；异常上抛）。"""
    headers: dict[str, str] = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(OPENROUTER_MODELS_URL, headers=headers)
    with urllib.request.urlopen(request, timeout=URLOPEN_TIMEOUT_S) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return parse_openrouter_models(payload)


def to_price_snapshot(models: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """模型目录→价快照 {model_id: {input_price, output_price, name, context_length, created}}。

    价格换算：OpenRouter 按 token 计价 → 统一 USD/1M tokens（×1e6）。
    """
    snapshot: dict[str, dict[str, Any]] = {}
    for m in models:
        mid = str(m.get("id") or "").strip()
        if not mid:
            continue
        snapshot[mid] = {
            "input_price": float(m.get("prompt") or 0) * PRICE_PER_TOKEN_TO_PER_MILLION,
            "output_price": float(m.get("completion") or 0) * PRICE_PER_TOKEN_TO_PER_MILLION,
            "name": str(m.get("name") or ""),
            "context_length": int(m.get("context_length") or 0),
            "created": int(m.get("created") or 0),
        }
    return snapshot


def diff_price_snapshots(old: dict[str, dict[str, Any]],
                         new: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """新旧价快照 diff→候选事件（纯函数）：新上架=new_model，价格变动=price_change，无变化不出事件。"""
    events: list[dict[str, Any]] = []
    for mid, meta in new.items():
        prior = old.get(mid)
        if prior is None:
            events.append({"kind": "new_model", "model_id": mid, "name": meta.get("name", ""),
                           "price_after": meta.get("input_price"), "context_length": meta.get("context_length", 0),
                           "created": meta.get("created", 0)})
            continue
        old_in = float(prior.get("input_price") or 0)
        old_out = float(prior.get("output_price") or 0)
        new_in = float(meta.get("input_price") or 0)
        new_out = float(meta.get("output_price") or 0)
        if (old_in, old_out) == (new_in, new_out):
            continue
        events.append({"kind": "price_change", "model_id": mid, "name": meta.get("name", ""),
                       "price_before": old_in, "price_after": new_in,
                       "output_price_before": old_out, "output_price_after": new_out,
                       "direction": "down" if new_in + new_out < old_in + old_out else "up"})
    return events


@dataclass(frozen=True)
class _CardContext:
    """卡片构造公共上下文（参数对象，防 8 参长参数表）。"""

    source_meta: dict[str, Any]
    src: SourceRef
    gates: FourGates
    source_id: str
    date_stamp: str


def _effective_event_meta(event: dict[str, Any], source_meta: dict[str, Any]) -> dict[str, Any]:
    """每卡四闸如实：事件可覆写独立源数与互证注记（人工卡/互证源如实落，自动化卡默认单源）。"""
    return source_meta | {
        "independent_sources": event.get("independent_sources",
                                         source_meta.get("independent_sources", 1)),
        "cross_validation_note": event.get("cross_validation_note",
                                           source_meta.get("cross_validation_note")),
    }


def _merge_model_refs(event: dict[str, Any]) -> list[str]:
    """model_refs 归一：model_id 无则补首（去重保序）。"""
    model_refs = [str(x) for x in event.get("model_refs") or []]
    model_id = str(event.get("model_id") or "")
    if model_id and model_id not in model_refs:
        model_refs.insert(0, model_id)
    return model_refs


def build_intel_cards(events: list[dict[str, Any]], source_meta: dict[str, Any],
                      now: datetime) -> list[IntelCard]:
    """事件→情报卡（card_id=MI-<source>-<yyyymmdd>-<seq>；四闸初值按 source_meta 如实落）。"""
    date_stamp = now.strftime("%Y%m%d")
    source_id = str(source_meta.get("source_id") or "unknown")
    fetched_at = str(source_meta.get("fetched_at") or now.isoformat())
    src = SourceRef(name=str(source_meta.get("name") or source_id),
                    url=str(source_meta.get("url") or ""),
                    publisher=str(source_meta.get("publisher") or ""),
                    fetched_at=fetched_at)
    ctx = _CardContext(source_meta=source_meta, src=src, gates=_four_gates(source_meta),
                       source_id=source_id, date_stamp=date_stamp)
    cards: list[IntelCard] = []
    seq = 0
    for event in events:
        kind = str(event.get("kind") or "")
        if kind not in EVENT_KINDS_SUPPORTED:
            log.warning("skip unsupported intel event kind=%s model=%s", kind, event.get("model_id"))
            continue
        seq += 1
        cards.append(_build_one_card(event, kind, ctx, seq))
    return cards


def _build_one_card(event: dict[str, Any], kind: str, ctx: _CardContext, seq: int) -> IntelCard:
    """单事件→单卡构造（四闸覆写与模型引用归一在此收口）。"""
    effective_meta = _effective_event_meta(event, ctx.source_meta)
    card_gates = ctx.gates if effective_meta == ctx.source_meta else _four_gates(effective_meta)
    return IntelCard(
        card_id=f"MI-{ctx.source_id}-{ctx.date_stamp}-{seq:03d}",
        source=ctx.src,
        kind=kind,
        model_refs=_merge_model_refs(event),
        claimed=Claimed(
            price_before=event.get("price_before"),
            price_after=event.get("price_after"),
            window_expr=str(event.get("window_expr") or ""),
            quota=str(event.get("quota") or ""),
            evidence_quote=str(event.get("evidence_quote") or ""),
            evidence_url=str(event.get("evidence_url") or ctx.source_meta.get("url") or ""),
        ),
        four_gates=card_gates,
        injection_probe=str(event.get("injection_probe") or _INJECTION_PROBE),
        action={"proposed": _PROPOSED_BY_KIND[kind], "review": "owner"},
        labor_killed=str(event.get("labor_killed") or "人肉刷价页/逛活动页"),
    )


def _four_gates(source_meta: dict[str, Any]) -> FourGates:
    """四闸初值：independent_sources/note 如实来自 source_meta（扫描时点通常=1，待人工补核升 2）。"""
    return FourGates(
        provenance="pass",
        cross_validation=CrossValidation(
            independent_sources=int(source_meta.get("independent_sources", 1)),
            note=str(source_meta.get("cross_validation_note") or "扫描时点单源，待补核交叉验证"),
        ),
        adaptation=IntelGateVerdict(verdict="pending", note="OpenAI 兼容/通道可达性待实测"),
        availability=IntelGateVerdict(verdict="pending", note="实测连通性待验证"),
    )


def dedup_cards(cards: list[IntelCard], seen_simhash: set[int],
                k: int = DEDUP_K_DEFAULT) -> tuple[list[IntelCard], list[IntelCard]]:
    """simhash 汉明距离 ≤k 判换皮：返回(新卡, 重复卡)；seen_simhash 就地更新供跨批续用。"""
    fresh: list[IntelCard] = []
    duplicates: list[IntelCard] = []
    for card in cards:
        fingerprint = simhash64(card.fingerprint_text())
        stamped = replace(card, dedup_simhash=fingerprint)
        if any(hamming(fingerprint, seen) <= k for seen in seen_simhash):
            duplicates.append(stamped)
            continue
        seen_simhash.add(fingerprint)
        fresh.append(stamped)
    return fresh, duplicates


def _events_first_scan(new_snap: dict[str, dict[str, Any]], now: datetime,
                       window_days: int) -> list[dict[str, Any]]:
    """首扫（无旧快照）：只登记最近 window_days 天新上架模型，防全量目录灌水成卡。"""
    cutoff = now - timedelta(days=window_days)
    cutoff_ts = cutoff.timestamp()
    recent = [meta | {"model_id": mid} for mid, meta in new_snap.items()
              if meta.get("created", 0) >= cutoff_ts]
    recent.sort(key=lambda m: -int(m.get("created") or 0))
    return [{"kind": "new_model", "model_id": m["model_id"], "name": m.get("name", ""),
             "price_after": m.get("input_price"), "context_length": m.get("context_length", 0),
             "created": m.get("created", 0)} for m in recent]


def _cap_events(events: list[dict[str, Any]], cap: int) -> list[dict[str, Any]]:
    """防灌水闸：产出按每源配额截断（price_change 优先级高于 new_model）。"""
    def rank(ev: dict[str, Any]) -> tuple[int, int]:
        return (0 if ev.get("kind") == "price_change" else 1, -int(ev.get("created") or 0))
    return sorted(events, key=rank)[:max(cap, 0)]


def _find_source(sources: list[dict[str, Any]], source_id: str) -> dict[str, Any]:
    for src in sources:
        if str(src.get("source_id")) == source_id:
            return src
    raise IntelSourceError(f"source_id not in registry: {source_id}")


def _load_old_snapshot(path: Path | None) -> dict[str, dict[str, Any]] | None:
    if path is None:
        return None
    if not path.is_file():
        raise IntelSourceError("snapshot file missing", details={"path": str(path)})
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise IntelSourceError("snapshot malformed (not a dict)", details={"path": str(path)})
    return data


def _write_jsonl(cards: list[IntelCard], out_dir: Path, source_meta: dict[str, Any]) -> Path:
    """过闸留痕落盘：每行一卡，gate_violations 字段随卡（空清单=过闸）。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "cards.jsonl"
    lines: list[str] = []
    for card in cards:
        violations = validate_four_gates(card)
        record = card.to_dict() | {"gate_violations": violations}
        lines.append(json.dumps(record, ensure_ascii=False, sort_keys=True))
    target.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    log.info("intel cards written: %d cards -> %s (source=%s)",
             len(cards), target, source_meta.get("source_id"))
    return target


def main(argv: list[str] | None = None) -> int:
    """CLI 编排：拉取→diff→建卡→四闸校验→simhash 去重→写 JSONL（exit 0=成功）。"""
    parser = argparse.ArgumentParser(prog="model_intel_scanner",
                                     description="M1 模型情报扫描（事件触发，由外部周历窗口调用）")
    parser.add_argument("--source", default=DEFAULT_SOURCE_ID, help="源注册表中的 source_id")
    parser.add_argument("--snapshot", default=None, help="旧价快照 JSON 路径（缺省=首扫，只登记近窗新模型）")
    parser.add_argument("--new-window-days", type=int, default=NEW_WINDOW_DAYS,
                        help="首扫新模型回看窗口天数")
    parser.add_argument("--out", required=True, help="产出目录（调用方指定，禁写生产路径）")
    args = parser.parse_args(argv)

    src = _find_source(load_sources(), args.source)
    if str(src.get("fetch_method")) != "models_api":
        raise IntelSourceError("source not machine-fetchable in v0", details={"source": str(args.source)})
    source_meta = {
        "source_id": src["source_id"], "name": src.get("name"), "url": src.get("url"),
        "publisher": src.get("publisher"), "independent_sources": 1,
    }
    cap = int((src.get("quota") or {}).get("cards_per_day_max", DEFAULT_FUNNEL_CAP))

    now = now_utc()
    models = fetch_openrouter_models(None)
    new_snap = to_price_snapshot(models)
    old_snap = _load_old_snapshot(Path(args.snapshot) if args.snapshot else None)
    events = (diff_price_snapshots(old_snap, new_snap) if old_snap is not None
              else _events_first_scan(new_snap, now, int(args.new_window_days)))
    cards = dedup_cards(build_intel_cards(_cap_events(events, cap), source_meta, now), set())[0]

    out_dir = Path(args.out)
    _write_jsonl(cards, out_dir, src)
    (out_dir / "openrouter_snapshot.json").write_text(
        json.dumps(new_snap, ensure_ascii=False, sort_keys=True, indent=1), encoding="utf-8")
    log.info("scan done: source=%s events=%d cards=%d", args.source, len(events), len(cards))
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维CLI入口由外部排班(排班登记register_*.ps1在册)/人工点火, 非自动常驻任务
    raise SystemExit(main())
