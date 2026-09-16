# [BLUEPRINT] MOD-PA-033 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] zephyr.pf_alloc.allocation_config
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.shared.io.paths(REPO_ROOT); PyYAML(可选，仅 config/pf_alloc.yaml 存在时)
# [CONSUMERS] zephyr.pf_alloc.allocation_orchestrator; scripts/backtest/sim_paper_ledger(钱包额度回退开关)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 分配链**唯一配置真源**（RULE-SSOT：代码零硬编码资金常量/零散落 getenv）；
#   三源优先级 env > config/pf_alloc.yaml > 本模块 DEFAULTS（缺省值即生产口径）；
#   enabled=False 是"回退到旧 flat 钱包口径"的显式真值开关（Owner 可一键回退，非删码回退）；
#   构造期校验失败一律 ValueError（fail-closed，禁静默吞配置错误）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(配置值越界/类型非法)；YAML 缺失=用缺省（可选文件，非错误）；
#   YAML 存在但解析失败=ValueError（配置在但读不懂不得静默降级）
# [TESTS] tests/pf_alloc/test_allocation_orchestrator.py
# [A_module] module_id=MOD-PA-033 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] allocation-config-mod-pa-033-20260916
"""allocation_config——组合分配链的配置真源（车道 D 实盘接线，2026-09-16）。

真源：pf_alloc_consumer_mining PFA-2（纸面账本每策略硬编码 1,000,000 与"组合分配"叙事
完全脱钩）+ PFA-5（STR-VREV-025 注册口径 vol-target 仓位 vs sim 全仓 all-in 的口径漂移）。

本模块治的是"回退路径必须是显式配置真值，而不是硬编码"：
  - enabled=True  → 钱包额度 = 分配链输出（allocation→shrinkage→cold_start→budget→裁决）
  - enabled=False → 钱包额度 = legacy_wallet_capital（旧 flat 口径，逐元不变）

[ALGO_FLOW]
输入: 三源配置（环境变量 ZEPHYR_PF_ALLOC_* / config/pf_alloc.yaml / DEFAULTS 常量）
前置检查: portfolio_total>0、legacy_wallet_capital>0、risk_signal_mode∈枚举、perf_lookback_days>0、
          max_single_sleeve∈(0,1]、persist_path 不落 data/ 生产目录
执行: 合并三源 -> 校验 -> 冻结 AllocationConfig -> resolve_portfolio_total(n) 派生总资金
输出: AllocationConfig（冻结，不可变）
降级: 无（配置错误必须炸，禁静默降级——否则分配口径不可信）
不变量: 同一 (env, yaml) 输入 -> 同一 config 对象字段值（确定性，可回测复现）
[/ALGO_FLOW]
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path

try:  # 复用仓内路径真源；独立测试环境缺失时按文件层级回退（不改变语义）
    from zephyr.shared.io.paths import REPO_ROOT as _REPO_ROOT
except Exception:  # noqa: BLE001 — 仅路径解析降级，配置校验不受影响
    _REPO_ROOT = Path(__file__).resolve().parents[2]

ENV_PREFIX = "ZEPHYR_PF_ALLOC_"

# 生产缺省口径（唯一真源，禁在业务代码里重复硬编码）
DEFAULT_LEGACY_WALLET_CAPITAL = 1_000_000.0  # Owner 批准的纸面盘单策略初始额度
DEFAULT_PERF_LOOKBACK_DAYS = 60  # MOD-PA-007 §3.2.2 60 日 Sortino 窗口
DEFAULT_MAX_SINGLE_SLEEVE = 0.25  # PP-001 aggregator.max_single_sleeve 常态上限
DEFAULT_MAX_TOTAL_POSITION = 1.0  # PP-001 aggregator.max_total_position（工程天花板）
DEFAULT_SCHEMA_VERSION = "alloc-1.0"

# risk_signal 来源口径（PFA-3：实盘 RiskSignal 13 参数无生产者，须显式登记近似口径）
RISK_SIGNAL_MODES = ("auto", "snapshot_direct", "snapshot_decomposed", "neutral_fail_closed")

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}


class AllocationConfigError(ValueError):
    """分配链配置非法（值越界/类型错/落点违规）。继承 ValueError 便于既有调用方捕获。"""

    error_code = "ZA-PA-0033"


@dataclass(frozen=True)
class AllocationConfig:
    """分配链运行配置（冻结）。字段即生产口径真源，改口径改本类缺省或配置文件。"""

    # ── 总开关（回退路径）──
    enabled: bool = True  # False=钱包额度回退 legacy flat（Owner 一键回退，不改码）
    write_to_db: bool = True  # False=只算不落库（影子/回放/单测口径）
    allow_legacy_fallback: bool = (
        False  # 分配链异常时是否允许回落 flat（默认禁——静默回落=重新制造 PFA-2 失真）
    )

    # ── 资金口径 ──
    legacy_wallet_capital: float = DEFAULT_LEGACY_WALLET_CAPITAL
    portfolio_total_capital: float | None = None  # None=钱包数 × legacy_wallet_capital（总资金与旧口径同量级）

    # ── 分配器参数 ──
    shrinkage_enabled: bool = True  # C1 验证开关（False=global_shrinkage 恒 1.0）
    risk_signal_mode: str = "auto"  # RISK_SIGNAL_MODES 之一（auto=能取直取否则反演再退中性）
    perf_lookback_days: int = DEFAULT_PERF_LOOKBACK_DAYS  # PerformanceScore 窗口（交易日）

    # ── 组合约束（裁决层注入，PP-001 真源可覆盖）──
    max_single_sleeve: float = DEFAULT_MAX_SINGLE_SLEEVE
    max_total_position: float = DEFAULT_MAX_TOTAL_POSITION

    # ── 落点 ──
    persist_path: str = ".runtime/pf_alloc/budget_tier_state.json"  # TierState 跨日快照（相对仓根）
    tdm_path: str = "config/trading_decision_map.yaml"  # PP-001 sleeve 先验真源（只读）

    schema_version: str = DEFAULT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.legacy_wallet_capital <= 0:
            raise AllocationConfigError(
                f"legacy_wallet_capital={self.legacy_wallet_capital} 须 >0"
            )
        if self.portfolio_total_capital is not None and self.portfolio_total_capital <= 0:
            raise AllocationConfigError(
                f"portfolio_total_capital={self.portfolio_total_capital} 须 >0（或 None=按钱包数派生）"
            )
        if self.risk_signal_mode not in RISK_SIGNAL_MODES:
            raise AllocationConfigError(
                f"risk_signal_mode={self.risk_signal_mode!r} 须∈{RISK_SIGNAL_MODES}"
            )
        if self.perf_lookback_days <= 0:
            raise AllocationConfigError(f"perf_lookback_days={self.perf_lookback_days} 须 >0")
        if not 0 < self.max_single_sleeve <= 1:
            raise AllocationConfigError(f"max_single_sleeve={self.max_single_sleeve} 须∈(0,1]")
        if not 0 < self.max_total_position <= 1:
            raise AllocationConfigError(f"max_total_position={self.max_total_position} 须∈(0,1]")
        for key in ("persist_path", "tdm_path"):
            v = str(getattr(self, key)).replace("\\", "/")
            if v.startswith("data/"):
                raise AllocationConfigError(
                    f"{key}={v} 落在 data/ 生产目录（宪法 §9.6 测试/运行时产物禁写生产路径）"
                )

    # ── 派生量 ────────────────────────────────────────────────

    def resolve_portfolio_total(self, n_wallets: int) -> float:
        """组合总资金：显式配置优先，否则按"钱包数 × 旧 flat 额度"派生。

        派生口径的意义：Owner 批准的纸面盘总资金量级不变（N 个策略 × 100 万），
        变的只是**切分方式**（flat 等分 → 分配链按 regime/绩效/风险节流切分），
        使"接线"这一改动可被归因（总盘子相同，权重变化才是分配链的贡献）。
        """
        if n_wallets <= 0:
            raise AllocationConfigError(f"n_wallets={n_wallets} 须 >0")
        if self.portfolio_total_capital is not None:
            return float(self.portfolio_total_capital)
        return float(n_wallets) * float(self.legacy_wallet_capital)

    @property
    def persist_full_path(self) -> Path:
        """TierState 快照绝对路径（相对仓根解析，目录不存在时由 handler 自建）。"""
        p = Path(self.persist_path)
        return p if p.is_absolute() else (_REPO_ROOT / p)

    @property
    def tdm_full_path(self) -> Path:
        p = Path(self.tdm_path)
        return p if p.is_absolute() else (_REPO_ROOT / p)

    def to_dict(self) -> dict[str, object]:
        """可序列化快照（入 alloc_* 表 note/prose 或日志，配置真值留痕）。"""
        return {
            "enabled": self.enabled,
            "write_to_db": self.write_to_db,
            "allow_legacy_fallback": self.allow_legacy_fallback,
            "legacy_wallet_capital": self.legacy_wallet_capital,
            "portfolio_total_capital": self.portfolio_total_capital,
            "shrinkage_enabled": self.shrinkage_enabled,
            "risk_signal_mode": self.risk_signal_mode,
            "perf_lookback_days": self.perf_lookback_days,
            "max_single_sleeve": self.max_single_sleeve,
            "max_total_position": self.max_total_position,
            "persist_path": self.persist_path,
            "schema_version": self.schema_version,
        }


def _read_yaml(path: Path) -> dict[str, object]:
    """读可选 YAML（不存在=空 dict；解析失败=抛错，禁静默降级）。"""
    if not path.exists():
        return {}
    import yaml  # 仓内既有依赖（RULE-DEP：不新增依赖）

    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:  # 配置在但读不懂 = 硬错
        raise AllocationConfigError(f"配置文件解析失败 {path}: {exc}") from exc
    if loaded is None:
        return {}
    if not isinstance(loaded, Mapping):
        raise AllocationConfigError(f"配置文件根节点须为映射，got {type(loaded).__name__}: {path}")
    return dict(loaded)


def _from_mapping(data: Mapping[str, object]) -> AllocationConfig:
    """YAML 段 -> config（只认已知键，未知键=报错防拼写漂移静默生效）。"""
    known = set(AllocationConfig.__dataclass_fields__)
    unknown = set(data) - known
    if unknown:
        raise AllocationConfigError(f"pf_alloc.yaml 含未知配置键 {sorted(unknown)}（拼写漂移防静默）")
    kwargs = dict(data)
    for key in ("persist_path", "tdm_path"):
        if key in kwargs and kwargs[key] is not None:
            kwargs[key] = str(kwargs[key])
    return AllocationConfig(**kwargs)  # type: ignore[arg-type]


def _parse_bool(key: str, raw: str) -> bool:
    v = raw.strip().lower()
    if v in _TRUE:
        return True
    if v in _FALSE:
        return False
    raise AllocationConfigError(f"{ENV_PREFIX}{key}={raw!r} 非布尔可解析值（须∈{sorted(_TRUE | _FALSE)}）")


def _parse_float(key: str, raw: str) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError) as exc:
        raise AllocationConfigError(f"{ENV_PREFIX}{key}={raw!r} 非数值") from exc


def load_allocation_config(
    yaml_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> AllocationConfig:
    """装配配置：缺省 ← config/pf_alloc.yaml ← 环境变量（后者覆盖前者）。

    Args:
        yaml_path: 显式配置文件路径（None=config/pf_alloc.yaml，**可选文件**）
        env: 环境变量映射（None=os.environ，测试注入用）

    Returns:
        AllocationConfig（冻结）
    """
    base = _REPO_ROOT / "config" / "pf_alloc.yaml" if yaml_path is None else Path(yaml_path)
    cfg = _from_mapping(_read_yaml(base))

    if env is None:
        env = os.environ

    def _get(key: str) -> str | None:
        raw = env.get(ENV_PREFIX + key)
        return None if raw is None or str(raw).strip() == "" else str(raw).strip()

    overrides: dict[str, object] = {}
    for env_key, field, parser in (
        ("ENABLED", "enabled", _parse_bool),
        ("WRITE_DB", "write_to_db", _parse_bool),
        ("ALLOW_LEGACY_FALLBACK", "allow_legacy_fallback", _parse_bool),
        ("SHRINKAGE_ENABLED", "shrinkage_enabled", _parse_bool),
        ("LEGACY_WALLET_CAPITAL", "legacy_wallet_capital", _parse_float),
        ("MAX_SINGLE_SLEEVE", "max_single_sleeve", _parse_float),
        ("MAX_TOTAL_POSITION", "max_total_position", _parse_float),
    ):
        if (v := _get(env_key)) is not None:
            overrides[field] = parser(env_key, v)

    if (v := _get("PERF_LOOKBACK_DAYS")) is not None:
        overrides["perf_lookback_days"] = int(v)
    if (v := _get("PORTFOLIO_TOTAL_CAPITAL")) is not None:
        overrides["portfolio_total_capital"] = (
            None if v.lower() in {"none", "auto"} else _parse_float("PORTFOLIO_TOTAL_CAPITAL", v)
        )
    for env_key, field in (("RISK_SIGNAL_MODE", "risk_signal_mode"), ("PERSIST_PATH", "persist_path"), ("TDM_PATH", "tdm_path")):
        if (v := _get(env_key)) is not None:
            overrides[field] = v

    return replace(cfg, **overrides) if overrides else cfg
