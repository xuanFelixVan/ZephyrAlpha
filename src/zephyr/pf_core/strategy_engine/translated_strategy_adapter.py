# [BLUEPRINT] MOD-BT-196 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.pf_core.strategy_engine.translated_strategy_adapter
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.shared.io.paths; scripts/backtest/translated/c4_*.py（运行时动态加载，非静态依赖）
# [CONSUMERS] zephyr.pf_core.strategy_engine.framework_composer（_build_member_panels STR- 前缀路由）;
#   zephyr.strategy_pipeline.fw_backtest（预取面板+列发现）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 只路由 STR- 前缀成员（kebab 老成员走 StrategyRunner 原路，禁混）；面板=翻译件 build()
#   原样权重（禁再加工/禁 PIT 再平移——行 t 权重用 ≤t 收盘信息算得，引擎 exec_lag=1 于 t+1 执行，
#   已 PIT 安全）；代码真源=strategy_registry.yaml code_path（禁散落路径拼猜）；单成员失败上抛由
#   composer 捕获落 skipped 披露（本模块不静默吞）；build() 每进程每窗口只调一次（缓存重放）
# [MODIFY-GUARD] tests/pf_core/test_translated_strategy_adapter.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TranslatedAdapterError: strategy_id 非 STR- 前缀 / 注册表无条目或 code_path 非
#   translated/c4_ 件 / build() 契约不符（返回非二元组/weights 空）
# [TESTS] tests/pf_core/test_translated_strategy_adapter.py
# [A_module] module_id=MOD-BT-196 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""STR-* 翻译件面板适配器——把 c4_*.py 的 build(start,end) 契约包装成整装回测成员面板。

背景（S11/C3 断桥②）: TDM 挂图的 STR-* 策略是翻译件（scripts/backtest/translated/c4_*.py），
其口径 = build(start, end) → (weights, closes)：weights 为 date×symbol 目标持仓权重宽表
（值域 [0,1]，行合计 ≤1，余量=现金），与 StrategyRegistry 的 generate_target_weights
两套接口不兼容，framework_composer 造不出其面板——本适配器即桥。

权重语义（一行约束）: weights 行 t = 翻译件用 ≤t 收盘信息算出的目标持仓权重，引擎
exec_lag=1 在 t+1 执行——天然 PIT 安全，适配器**不做任何 shift/归一**（行级 Σ 归一由
compose_weight_panels 统一处理，成员权重不要求 Σ=1）。

已知边界（如实披露，v1 不解决）:
    - 引擎 v1 语义=零权重行"不调仓、沿用持仓"（非"清仓到现金"）——翻译件的空仓日语义
      在整装引擎中近似为持仓不动（与 kebab 成员的 ffill 契约同构）。
    - 权重列 symbol 若不在引擎 data（load_history=stock 日线表）中（如 000300 指数不在
      kline_daily_hfq），该腿 fill 无法成交→资金留存现金——证据包须披露不可成交腿。
    - closes（翻译件返回的第二元组）仅用于退化场景的 data 兜底（全成员皆空时引擎至少有
      收盘价可依）；正常路径 data 由首个 kebab 成员的 load_history 提供。

用法:
    from zephyr.pf_core.strategy_engine.translated_strategy_adapter import (
        is_translated_member, build_translated_weight_panel, prefetch_translated_panels,
    )
    if is_translated_member(w.strategy_id):
        data_i, panel_i = build_translated_weight_panel(w.strategy_id, symbols, start, end)

真源: docs/_working/full-auto-chain/S11_assembled_backtest/README.md §5 施工项 1。
"""

from __future__ import annotations

import importlib.util
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

STRATEGY_REGISTRY_PATH = (
    REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml"
)
_TRANSLATED_MARKER = "/translated/c4_"


class TranslatedAdapterError(Exception):
    """翻译件适配异常（前缀不符/注册表缺条目/code_path 非翻译件/build 契约不符）。"""

    error_code = "ZA-STRADAPT-0001"


@dataclass(frozen=True)
class _BuildResult:
    """单成员一次 build() 的产物（weights/closes 同源缓存，禁二次调用翻译件）。"""

    weights: pd.DataFrame
    closes: pd.DataFrame | None
    code_path: str


# 进程内缓存：键=(sid, start, end)——fw_backtest 预取列发现后，composer 二次构建零成本
_BUILD_CACHE: dict[tuple[str, str, str], _BuildResult] = {}
# 模块缓存：键=(绝对路径, mtime)——同一翻译件多窗口复用 exec 产物
_MODULE_CACHE: dict[tuple[str, int], Any] = {}


def is_translated_member(strategy_id: str) -> bool:
    """成员 ID 是否走翻译件适配路由（唯一判据=`STR-` 前缀；kebab 老成员=False）。"""
    return str(strategy_id).startswith("STR-")


def resolve_code_path(strategy_id: str, registry_path: str | Path | None = None) -> str:
    """strategy_registry.yaml 查 code_path（唯一真源；缺条目/非 c4 翻译件=拒绝）。"""
    path = Path(registry_path) if registry_path else STRATEGY_REGISTRY_PATH
    if not path.exists():
        raise TranslatedAdapterError(f"策略注册表缺失: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for entry in data.get("strategies", []):
        if str(entry.get("strategy_id", "")) == str(strategy_id):
            code_path = str(entry.get("code_path", "") or "").replace("\\", "/")
            if not code_path:
                raise TranslatedAdapterError(f"{strategy_id} 注册表条目无 code_path")
            if _TRANSLATED_MARKER not in code_path:
                raise TranslatedAdapterError(
                    f"{strategy_id} code_path 非 C4 翻译件（无 build 契约）: {code_path}"
                )
            return code_path
    raise TranslatedAdapterError(f"{strategy_id} 不在策略注册表: {path}")


def load_translated_module(code_path: str) -> Any:
    """按路径动态加载翻译件模块（引擎注入点：translated 目录入 sys.path 供 import _c4_engine）。

    与 auto_mount._load_translated_module 同一加载语义（scripts→src 单向依赖，禁 src 反向
    import scripts，故本模块独立实现加载原语）；模块按 (绝对路径, mtime) 缓存防重复 exec。
    """
    p = Path(code_path)
    if not p.is_absolute():
        p = REPO_ROOT / p
    if not p.exists():
        raise TranslatedAdapterError(f"翻译件不存在: {p}")
    key = (str(p.resolve()), int(p.stat().st_mtime))
    cached = _MODULE_CACHE.get(key)
    if cached is not None:
        return cached
    translated_dir = str(p.parent)
    if translated_dir not in sys.path:
        sys.path.insert(0, translated_dir)  # _c4_engine 注入点（引擎与翻译件同目录）
    spec = importlib.util.spec_from_file_location(f"translated_adapter_{p.stem}", p)
    if spec is None or spec.loader is None:
        raise TranslatedAdapterError(f"翻译件无法构建 import spec: {p}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    _MODULE_CACHE[key] = mod
    return mod


def _build_once(
    strategy_id: str,
    start: str,
    end: str,
    registry_path: str | Path | None,
) -> _BuildResult:
    """build() 每进程每窗口只调一次：结果缓存并同源返回（重放零漂移）。"""
    cache_key = (str(strategy_id), str(start), str(end))
    hit = _BUILD_CACHE.get(cache_key)
    if hit is not None:
        return hit
    code_path = resolve_code_path(strategy_id, registry_path)
    mod = load_translated_module(code_path)
    build = getattr(mod, "build", None)
    if not callable(build):
        raise TranslatedAdapterError(f"{strategy_id} 翻译件无 build(start, end) 契约: {code_path}")
    out = build(start, end)
    if not (isinstance(out, tuple) and len(out) == 2):
        raise TranslatedAdapterError(
            f"{strategy_id} build() 返回契约不符（须 (weights, closes) 二元组）: {code_path}"
        )
    weights, closes = out
    if not isinstance(weights, pd.DataFrame) or weights.empty:
        raise TranslatedAdapterError(f"{strategy_id} build() weights 为空/非 DataFrame: {code_path}")
    weights = weights.copy()
    weights.index = pd.to_datetime(weights.index)
    weights = weights.sort_index().astype(float).fillna(0.0)
    if isinstance(closes, pd.DataFrame) and not closes.empty:
        closes = closes.copy()
        closes.index = pd.to_datetime(closes.index)
        closes = closes.sort_index().astype(float)
    else:
        closes = None
    result = _BuildResult(weights=weights, closes=closes, code_path=code_path)
    _BUILD_CACHE[cache_key] = result
    return result


def build_translated_weights(
    strategy_id: str,
    start: str,
    end: str,
    registry_path: str | Path | None = None,
) -> pd.DataFrame:
    """翻译件 build(start,end) → weights 宽表（date×symbol 目标持仓权重，缓存重放）。"""
    return _build_once(strategy_id, start, end, registry_path).weights


def build_translated_weight_panel(
    strategy_id: str,
    symbols: list[str],
    start: str,
    end: str,
    registry_path: str | Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """composer 成员接口（StrategyRunner.build_weight_panel 等价形态）：(data, panel)。

    panel = 翻译件 weights 原样（禁再加工——见模块 docstring 权重语义）；
    data  = closes 兜底长表（MultiIndex(symbol, trade_date) × [close]，仅退化场景被
            引擎消费；正常路径 data 由首个 kebab 成员的 load_history 提供）。
    symbols 入参仅为接口对齐（翻译件自带标的宇宙，不消费该参数）。

    Raises:
        TranslatedAdapterError: 前缀不符/契约不符（composer 捕获后落 skipped 披露）。
    """
    if not is_translated_member(strategy_id):
        raise TranslatedAdapterError(
            f"{strategy_id} 非 STR- 前缀——翻译件路由仅限 STR-*（kebab 成员走 StrategyRunner 原路）"
        )
    result = _build_once(strategy_id, start, end, registry_path)
    data = pd.DataFrame()
    if result.closes is not None:
        rows: dict[str, list[Any]] = {"symbol": [], "trade_date": [], "close": []}
        for sym in result.closes.columns:
            col = result.closes[sym].dropna()
            rows["symbol"].extend([str(sym)] * len(col))
            rows["trade_date"].extend(list(col.index))
            rows["close"].extend([float(v) for v in col.values])
        if rows["symbol"]:
            data = pd.DataFrame(rows).set_index(["symbol", "trade_date"]).sort_index()
    return data, result.weights


def prefetch_translated_panels(
    strategy_ids: list[str],
    start: str,
    end: str,
    registry_path: str | Path | None = None,
) -> dict[str, pd.DataFrame]:
    """批量预取 STR 成员面板（fw_backtest 符号发现用）；返回 {sid: panel}（失败成员不在结果中）。"""
    out: dict[str, pd.DataFrame] = {}
    for sid in strategy_ids:
        if not is_translated_member(sid):
            continue
        try:
            out[sid] = build_translated_weights(sid, start, end, registry_path)
        except Exception as exc:  # noqa: BLE001——预取失败成员交给 composer 统一 skipped 披露
            logger.warning("STR 成员预取失败（%s）: %s: %s", sid, type(exc).__name__, exc)
    return out


def clear_caches() -> None:
    """清空进程内缓存（测试隔离用）。"""
    _BUILD_CACHE.clear()
    _MODULE_CACHE.clear()


__all__ = (
    "TranslatedAdapterError",
    "build_translated_weight_panel",
    "build_translated_weights",
    "clear_caches",
    "is_translated_member",
    "load_translated_module",
    "prefetch_translated_panels",
    "resolve_code_path",
)
