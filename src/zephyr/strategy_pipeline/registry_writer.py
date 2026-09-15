# [BLUEPRINT] MOD-BT-192 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_pipeline.registry_writer
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.io.file_utils(safe_write_text CAS)
# [CONSUMERS] zephyr.strategy_pipeline.intake（C6 写入路径）; 验收⑥后开启的注册表追加
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 注册表=热文件：写入必经 safe_write_text CAS（base sha256+写后进程内复核 parse）；
#   语义 only-add：只做 EOF 追加条目块，禁改禁删既有行（写后断言条目数=旧+n 且既有 sid 全在）；
#   字段序=STR-DABAN-023 模板序（2026-09-14 转正批先例）；字符串值剥离引号/反斜杠防注入；
#   编号由 intake.next_strategy_number 决定，本模块不发明编号；CREATE-GUARD 不适用（非新文件，
#   条目级溯源走 evidence 内 run 指针+doc_ref）
# [MODIFY-GUARD] tests/strategy_pipeline/test_registry_writer.py
# [STABILITY] experimental
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(CAS 竞争/写后复核失败)——fail-closed，调用方留事件重试
# [TESTS] tests/strategy_pipeline/test_registry_writer.py
# [A_module] module_id=MOD-BT-192 | layer=module | stability=experimental | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] registry-writer-mod-bt-192-20260915
"""strategy_registry.yaml 条目追加写入器——C6 写入路径的机械手臂（交接清单③）。

文本级手术（与 auto_mount 同门）：读原文→EOF 追加渲染条目→safe_write_text CAS→写后复核
（yaml parse+条目数+新 sid 存在+既有条目零触碰）。渲染=确定性模板（字段序抄 STR-DABAN-023），
不引第三方 YAML dumper（保注释与既有排版零触碰）。
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from zephyr.shared.io.file_utils import safe_write_text

ROOT = Path(__file__).resolve().parents[3]
_ROOR = ROOT / "docs/registry_of_registries.yaml"  # 注册表的注册表（宪法 RULE-REGISTRY 唯一发现真源）


def resolve_registry_path(registry_id: str = "REG-STR-001") -> Path:
    """ROOR 反查注册表物理路径（勿背数；SSoT 路径禁硬编码——VOCAB-CHAIN/宪法 §0.6）。"""
    import yaml

    data = yaml.safe_load(_ROOR.read_text(encoding="utf-8"))
    for tier in data.get("tiers", []):
        for r in tier.get("registries", []):
            if r.get("registry_id") == registry_id:
                return ROOT / r["physical_path"]
    raise RuntimeError(f"ROOR 无 {registry_id} 条目——fail-closed")


REGISTRY = resolve_registry_path()

# 字段序模板（值类型驱动渲染：str→双引号标量 / list→inline / dict→块 / None→null / 数字→原样）
# 溯源：STR-DABAN-023（2026-09-14 转正批）全字段序
_FIELD_ORDER: list[tuple[str, Any]] = [
    ("strategy_id", "str"), ("name", "str"), ("name_zh", "str"), ("aliases", "list"),
    ("strategy_class", "str"), ("sleeve", "str"), ("alpha_sources", "list"), ("variant_of", "none"),
    ("entry_logic", "str"), ("exit_logic", "str"), ("position_sizing", "str"), ("risk_rules", "list"),
    ("holding_period", "str"), ("benchmark_id", "str"), ("universe_id", "str"), ("cost_model_id", "str"),
    ("module_id", "str"), ("doc_ref", "str"), ("code_path", "str"), ("lifecycle_status", "str"),
    ("status", "str"), ("version", "str"), ("created_at", "str"), ("updated_at", "str"),
    ("go_live_date", "none"), ("retired_date", "none"), ("owner", "str"),
    ("decay_detection_method", "none"), ("decay_threshold", "none"), ("last_decay_scan_at", "none"),
    ("mrp_baseline", "none"), ("adaptation_level", "none"), ("last_refit_at", "none"),
    ("baseline_sharpe", "num"), ("baseline_expectancy", "none"), ("baseline_win_rate", "none"),
    ("baseline_profit_factor", "none"), ("baseline_max_drawdown", "num"),
    ("combination_strategy", "dict"), ("meta_labeling_config", "dict"), ("origin", "str"),
    ("distilled_to_code", "bool"), ("capacity_aum_limit", "none"), ("participation_rate_limit", "num"),
    ("market_impact_model", "str"), ("baseline_trade_frequency", "none"), ("decay_cause", "str"),
    ("decay_scan_frequency", "str"), ("sharpe", "none"), ("max_drawdown", "none"),
    ("annual_return", "none"), ("capacity", "none"), ("turnover", "none"), ("last_evaluated_at", "str"),
    ("code_commit", "none"), ("data_quality_policy", "dq"), ("null_rate", "none"), ("drift_psi", "none"),
    ("drift_ks_pvalue", "none"), ("last_quality_scan_at", "none"), ("entry_series", "none"),
    ("range_bounds", "dict"), ("primary_timeframe", "str"), ("applicable_timeframes", "list"),
    ("regime_valid", "list"), ("regime_invalid", "list"), ("direction", "str"), ("entry_role", "str"),
    ("applies_to", "list"), ("tags", "list"), ("algorithm_status", "str"), ("evidence", "str"),
    ("family_redundancy", "raw_or_none"), ("code_symbol", "str"), ("code_fingerprint", "none"),
]

_DQ_POLICY = (
    "    data_quality_policy:\n"
    "      null_rate: {threshold: 0.02, window: \"1d\"}\n"
    "      drift_method: \"psi\"\n"
    "      drift_threshold: 0.2\n"
    "      freshness: {staleness_sla: \"2d\"}\n"
    "      semantic_contract:\n"
    "        null_semantics: \"null=未计算/未产生（非零值），禁止零填充\"\n"
    "        default_fill_policy: \"none\"\n"
)


def _clean(s: Any) -> str:
    """YAML 双引号标量安全：剥离引号/反斜杠/控制换行（auto_mount evidence 防注入同门）。"""
    return (str(s).replace("\"", "").replace("'", "").replace("\\", "")
            .replace("\n", " ").replace("\r", " "))


def _render_field(key: str, value: Any, kind: str) -> str:
    if kind == "dq":
        return _DQ_POLICY
    if kind == "raw_or_none":
        if value is None:
            return f"    {key}: null\n"
        lines = [f"    {key}:"]
        lines.append(f"      role: \"{_clean(value.get('role', 'cluster_head'))}\"")
        absorbed = value.get("absorbed") or []
        if absorbed:
            lines.append("      absorbed:")
            for a in absorbed:
                lines.append(f"      - candidate_id: \"{_clean(a.get('candidate_id', ''))}\"")
                lines.append(f"        name: \"{_clean(a.get('name', ''))}\"")
                corr = a.get("correlation")
                lines.append(f"        correlation: {corr}" if corr is not None else "        correlation: null")
        else:
            lines.append("      absorbed: []")
        lines.append(f"      ruling_ref: \"{_clean(value.get('ruling_ref', ''))}\"")
        return "\n".join(lines) + "\n"
    if value is None and kind in ("none",):
        return f"    {key}: null\n"
    if kind == "list":
        items = ", ".join(_clean(x) for x in (value or []))
        return f"    {key}: [{items}]\n"
    if kind == "dict":
        inner = ", ".join(f"{_clean(k)}: {_clean(v)}" for k, v in (value or {}).items())
        return f"    {key}: {{{inner}}}\n"
    if kind == "num":
        return f"    {key}: {value if value is not None else 'null'}\n"
    if kind == "bool":
        return f"    {key}: {'true' if value else 'false'}\n"
    return f"    {key}: \"{_clean(value)}\"\n"


def render_entry(entry: dict[str, Any]) -> str:
    """单条目块（首行带 `  - ` 列表项标记，后续行 4 空格缩进）；缺失字段用模板缺省值补齐。"""
    defaults: dict[str, Any] = {
        "aliases": [], "alpha_sources": [], "risk_rules": [], "variant_of": None,
        "position_sizing": "", "go_live_date": None, "retired_date": None,
        "decay_detection_method": None, "decay_threshold": None, "last_decay_scan_at": None,
        "mrp_baseline": None, "adaptation_level": None, "last_refit_at": None,
        "baseline_expectancy": None, "baseline_win_rate": None, "baseline_profit_factor": None,
        "combination_strategy": {}, "meta_labeling_config": {}, "distilled_to_code": True,
        "capacity_aum_limit": None, "baseline_trade_frequency": None,
        "sharpe": None, "max_drawdown": None, "annual_return": None, "capacity": None,
        "turnover": None, "code_commit": None, "null_rate": None, "drift_psi": None,
        "drift_ks_pvalue": None, "last_quality_scan_at": None, "entry_series": None,
        "range_bounds": {}, "regime_valid": [], "regime_invalid": [],
        "family_redundancy": None, "code_fingerprint": None,
        "status": "active", "version": "1.0.0", "owner": "MOD-GOVERNANCE",
        "decay_cause": "unknown", "decay_scan_frequency": "monthly",
        "origin": "c4_translated", "participation_rate_limit": 0.05,
        "market_impact_model": "square_root", "direction": "long", "entry_role": "trigger",
        "primary_timeframe": "daily", "applicable_timeframes": ["1d"],
        "benchmark_id": "BMK-ABSOLUTE-001", "universe_id": "UNI-RULE-001",
        "cost_model_id": "CST-ASTOCK-001", "module_id": "MOD-BT-189",
        "algorithm_status": "quantized", "sleeve": "alpha",
    }
    merged = {**defaults, **entry}
    out = []
    for i, (key, kind) in enumerate(_FIELD_ORDER):
        line = _render_field(key, merged.get(key), kind)
        if i == 0:
            line = "  - " + line.lstrip()
        out.append(line)
    return "".join(out)


def append_entries(entries: list[dict[str, Any]], registry_path: Path | None = None,
                   dry_run: bool = False) -> dict[str, Any]:
    """EOF 追加 n 条；CAS+写后复核（parse/计数/新 sid 在/旧 sid 全在）。返回回执。"""
    path = registry_path or REGISTRY
    before = path.read_text(encoding="utf-8")
    new_block = "".join(render_entry(e) for e in entries)
    after = before if before.endswith("\n") else before + "\n"
    after += new_block
    new_sids = [e["strategy_id"] for e in entries]
    import yaml

    b, a = yaml.safe_load(before), yaml.safe_load(after)
    b_ids = [e["strategy_id"] for e in b.get("strategies", [])]
    a_ids = [e["strategy_id"] for e in a.get("strategies", [])]
    assert a_ids[: len(b_ids)] == b_ids, "写后复核失败：既有条目被触碰（only-add 语义违约）"
    assert a_ids[len(b_ids):] == new_sids, "写后复核失败：追加序与计划不符"
    if dry_run:
        return {"dry_run": True, "new_sids": new_sids, "total_after": len(a_ids)}
    r = safe_write_text(path, after,
                        expected_base_sha256=hashlib.sha256(before.encode("utf-8")).hexdigest(),
                        newline="\n")
    if not getattr(r, "written", True):
        raise RuntimeError("safe_write_text 未确认写入（CAS 竞争?）——fail-closed")
    # 写后进程内复核（读回磁盘真身，非内存 after）：新条目在尾 + 既有条目零触碰
    back = yaml.safe_load(path.read_text(encoding="utf-8"))
    back_ids = [e["strategy_id"] for e in back.get("strategies", [])]
    if back_ids[: len(b_ids)] != b_ids or back_ids[-len(new_sids):] != new_sids:
        raise RuntimeError("写后磁盘复核失败：条目序不符（only-add 语义被破坏）——fail-closed")
    return {"dry_run": False, "new_sids": new_sids, "total_after": len(back_ids),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()[:12]}
