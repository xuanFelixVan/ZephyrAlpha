# [BLUEPRINT] MOD-SIG-148 | docs/03_modules/_domain_signal/pattern_evidence_certifier/blueprint.md
# [MODULE] zephyr.signal_ashare.strategy_signal.pattern_evidence_certifier
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.pattern_win_rate_provider(_wilson_lower_bound 单源复用); zephyr.data.ch_writer(延迟 client); math(标准库)
# [CONSUMERS] internal_compute_provider(pattern_evidence_certify capability,W-CB); pattern_event_job.run_evidence_certify(W-CB); pattern_signal_runtime.PatternWeightSync(W-CC shrunk 口径); /api/pattern-winrate 认证列(W-CC)
# [STARTUP] imported(经调度器 daily_kline 档事件触发;禁 cron 自轮询)
# [MATURITY] design
# [INVARIANTS] 四闸判据纯函数化(二项精确检验/BH-FDR/n_eff 折扣/贝叶斯收缩)同输入必同输出; 阈值预注册(q=0.05/n_eff_min=30/k=100/conc_max=0.9)改动=裁定禁静默调; 认定只读统计表(运动员不兼任裁判); 台账/认证表只追加(ReplacingMergeTree 幂等重放); 失败 Fail-Closed(判不了的切片=failed 不猜)
# [MODIFY-GUARD] docs/03_modules/_domain_signal/pattern_evidence_certifier/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 统计输入越界(率∉[0,1]/n<0)->ValueError; CH 不可达->RuntimeError(经 FetchResult.error 透传); BH 空族->空表
# [TESTS] tests/signal_ashare/strategy_signal/test_pattern_evidence_certifier.py(教科书向量:二项 p/BH 例/收缩例/状态机迁移)
# [A_module] module_id=MOD-SIG-148 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""pattern_evidence_certifier — 反过拟合自动认证器（MOD-SIG-148，消费班续班）。

把"读表人"变成状态机（方案 v1.0：docs/_working/pattern_line/
2026-09-15-pattern-certification-plan.md）。四闸机器化，全部判据从
c1_market.market_pattern_win_rate 现有统计可算，零人工输入：

    闸A BH-FDR 多重检验修正（q<0.05）——堵 424 切片的运气赢家
    闸B n_eff = n_events/fwd_window 有效样本折扣（≥30）——堵重叠窗虚高 n
    闸C 分 regime 对照基线（加权 edge>0 且无单切片>90% 独活）——堵"何时响"混淆
    闸D 贝叶斯收缩 shrunk_rate（Efron-Morris 谱系）——替代裸 hit_rate 骗人读数

状态机：certified（四闸全过）/ probation（A+B 过 C 未过）/ failed（A 或 B 不过）。
阈值预注册，改动=裁定留痕；运动员不兼任裁判（只读统计表）。

# [ALGO_FLOW]
# 层: 统计核（纯函数）
# - id: S1
#   name: 单侧二项检验
#   code: binomial_ge_pvalue(hits_eff, n_eff, baseline) = Σ_{k≥hits} C(n,k)p0^k(1-p0)^(n-k)（lgamma 稳定实现）
# - id: S2
#   name: BH-FDR
#   code: 排序后 q_(i)=min(1, min_{j≥i} p_(j)·m/j)（step-up，跨同族切片）
# - id: S3
#   name: 有效样本
#   code: n_eff = n_events/fwd_window（重叠窗保守折扣）；Wilson LB/二项检验一律用 n_eff
# - id: S4
#   name: 贝叶斯收缩
#   code: shrunk = (hit_rate·n_eff + k·baseline)/(n_eff + k)
# 层: 认定（状态机）
# - id: C1
#   name: 闸序
#   code: failed = q≥q_thr 或 n_eff<min；probation = 加权 edge≤0 或 正edge单切片占比>conc_max；否则 certified
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Any

# 预注册阈值（改动=裁定留痕，禁静默调——方案 v1.0 §二）
Q_THRESHOLD = 0.05
N_EFF_MIN = 30.0
PRIOR_K = 100.0
CONCENTRATION_MAX = 0.9
_Z95 = 1.959963984540054

__all__ = [
    "binomial_ge_pvalue",
    "bh_adjust",
    "effective_n",
    "shrunk_rate",
    "within_regime_edge",
    "CertificationRecord",
    "certify_family",
    "run_certify",
]


# ── 统计核（纯函数） ─────────────────────────────────────────────────────────


def binomial_ge_pvalue(hits: float, n: float, p0: float) -> float:
    """单侧二项检验 P(X ≥ hits | n, p0)（lgamma 稳定实现，远尾下溢=0 视为精确零）。

    hits/n 允许浮点（n_eff 折扣后的有效计数，四舍五入到边界内）。
    """
    if not 0.0 <= p0 <= 1.0:
        raise ValueError(f"p0 越界: {p0!r}")
    if n < 0 or hits < 0:
        raise ValueError(f"负计数: hits={hits!r} n={n!r}")
    if n == 0:
        return 1.0
    if hits > n:
        return 0.0  # 不可能事件（钳位前先判，P(X≥n+1)=0）
    if hits <= 0:
        return 1.0  # 必然事件（浮点累积前短路）
    k = min(max(hits, 0.0), n)
    total = 0.0
    k_lo = int(math.ceil(k))
    for i in range(k_lo, int(n) + 1):
        logpmf = (
            math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
            + i * math.log(p0) + (n - i) * math.log1p(-p0)
        )
        total += math.exp(logpmf)
        if total >= 1.0:
            return 1.0
    return min(1.0, total)


def bh_adjust(pvalues: Sequence[float]) -> list[float]:
    """Benjamini-Hochberg step-up 调整（返回与输入同序的 q 值，截断 [0,1]）。"""
    m = len(pvalues)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: pvalues[i])
    q_sorted = [0.0] * m
    running = 1.0
    for rank in range(m, 0, -1):
        idx = order[rank - 1]
        running = min(running, pvalues[idx] * m / rank)
        q_sorted[idx] = min(1.0, running)
    return q_sorted


def effective_n(n_events: float, fwd_window: int) -> float:
    """重叠前视窗的有效样本折扣（闸B；fwd_window<1 视为 1）。"""
    if n_events < 0:
        raise ValueError(f"n_events 负数: {n_events!r}")
    w = max(1, int(fwd_window))
    return n_events / w


def shrunk_rate(hit_rate: float, n_eff: float, baseline: float, k: float = PRIOR_K) -> float:
    """闸D 贝叶斯收缩读数：(hit_rate·n_eff + k·baseline)/(n_eff + k)（Efron-Morris 谱系）。"""
    for name, v in (("hit_rate", hit_rate), ("baseline", baseline)):
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"{name} 越界: {v!r}")
    if n_eff < 0 or k <= 0:
        raise ValueError(f"n_eff/k 非法: n_eff={n_eff!r} k={k!r}")
    denom = n_eff + k
    if denom <= 0:
        return baseline
    return (hit_rate * n_eff + k * baseline) / denom


def within_regime_edge(
    regime_slices: Sequence[dict],
    baseline_by_regime: dict,
) -> tuple[float, float]:
    """闸C：分 regime 加权 edge 与正 edge 单切片集中度。

    返回 (weighted_edge, max_positive_share)；slices 元素含
    {regime_tag, hit_rate, n_events}；缺基线的 regime 按池化基线兜底由调用方预处理。
    空切片 → (0.0, 0.0)（无反证=闸C 放行，交由池化闸A/B 把关）。
    """
    total_n = sum(float(s.get("n_events") or 0) for s in regime_slices)
    if total_n <= 0 or not regime_slices:
        return (0.0, 0.0)  # 无 regime 切片=闸C 无反证放行（share 0.0<上限）
    weighted = 0.0
    pos_parts: list[float] = []
    for s in regime_slices:
        n = float(s.get("n_events") or 0)
        base = baseline_by_regime.get(s.get("regime_tag") or "")
        if base is None:
            base = baseline_by_regime.get("__pooled__", 0.5)
        edge = float(s.get("hit_rate") or 0.0) - float(base)
        part = n * edge
        weighted += part
        if edge > 0:
            pos_parts.append(n * edge)
    weighted_edge = weighted / total_n
    pos_total = sum(pos_parts)
    share = (max(pos_parts) / pos_total) if pos_parts else 1.0
    return (weighted_edge, share)


# ── 认定（状态机） ───────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CertificationRecord:
    """单形态切片认证记录（池化口径 regime_tag=''）。"""

    pattern_id: str
    timeframe: str
    direction: str
    fwd_window: int
    n_events: int
    n_eff: float
    p_value: float
    q_value: float
    shrunk: float
    wilson: float
    within_regime_edge: float
    edge_concentration: float
    state: str  # certified / probation / failed


def certify_family(
    pooled_rows: Sequence[dict],
    regime_rows_by_pattern: dict[str, Sequence[dict]],
    baseline_pooled: float,
    baseline_by_regime: dict,
    *,
    fwd_window: int,
    timeframe: str,
    direction: str,
    q_threshold: float = Q_THRESHOLD,
    n_eff_min: float = N_EFF_MIN,
    k: float = PRIOR_K,
    concentration_max: float = CONCENTRATION_MAX,
    wilson_fn: Callable[[float, float], float] | None = None,
) -> list[CertificationRecord]:
    """对一个家族（同 timeframe+direction+fwd_window 的全部池化切片）做四闸认定。

    闸序：failed（A 或 B 不过）→ probation（C 不过）→ certified（全过）；
    Fail-Closed：无基线/无数据的切片不进入认定（不出现在输出=未认证）。
    """
    if wilson_fn is None:
        from zephyr.signal_ashare.strategy_signal.pattern_win_rate_provider import (
            _wilson_lower_bound,
        )

        wilson_fn = _wilson_lower_bound
    candidates: list[dict] = []
    for row in pooled_rows:
        pid = row.get("pattern_id")
        if not pid or pid == "__baseline__":
            continue
        n = float(row.get("n_events") or 0)
        rate = row.get("hit_rate")
        if rate is None or n <= 0:
            continue
        n_eff = effective_n(n, fwd_window)
        hits_eff = float(rate) * n_eff
        p = binomial_ge_pvalue(hits_eff, n_eff, baseline_pooled)
        candidates.append({
            "pattern_id": pid, "n_events": int(n), "n_eff": n_eff,
            "hit_rate": float(rate), "p_value": p,
        })
    q_values = bh_adjust([c["p_value"] for c in candidates])
    out: list[CertificationRecord] = []
    for c, q in zip(candidates, q_values):
        shr = shrunk_rate(c["hit_rate"], c["n_eff"], baseline_pooled, k=k)
        wil = wilson_fn(c["hit_rate"], c["n_eff"])
        slices = regime_rows_by_pattern.get(c["pattern_id"]) or []
        w_edge, conc = within_regime_edge(slices, baseline_by_regime)
        if q >= q_threshold or c["n_eff"] < n_eff_min:
            state = "failed"
        elif w_edge <= 0 or conc > concentration_max:
            state = "probation"
        else:
            state = "certified"
        out.append(CertificationRecord(
            pattern_id=c["pattern_id"], timeframe=timeframe, direction=direction,
            fwd_window=fwd_window, n_events=c["n_events"], n_eff=c["n_eff"],
            p_value=c["p_value"], q_value=q, shrunk=shr, wilson=wil,
            within_regime_edge=w_edge, edge_concentration=conc, state=state,
        ))
    out.sort(key=lambda r: r.pattern_id)
    return out


# ── CH 读写（W-CB 任务块消费；延迟 client） ──────────────────────────────────


def _ensure_client(client=None):
    if client is not None:
        return client
    from zephyr.data import ch_writer

    c = ch_writer.get_client()
    if c is None:
        raise RuntimeError("clickhouse-driver 不可用（client 未注入且 get_client 返回 None）")
    return c


def load_family_rows(client, *, timeframe: str, direction: str, fwd_window: int) -> tuple[list[dict], dict[str, list[dict]], float, dict]:
    """读一个家族的池化行/regime 行/池化基线（含各 regime 基线）。"""
    rows = client.execute(
        "SELECT pattern_id, regime_tag, hit_rate, n_events, low_sample "
        "FROM c1_market.market_pattern_win_rate FINAL "
        "WHERE timeframe = %(tf)s AND direction = %(d)s AND fwd_window = %(w)d "
        "AND hit_rate IS NOT NULL",
        {"tf": timeframe, "d": direction, "w": int(fwd_window)},
    )
    pooled: list[dict] = []
    regime_by_pattern: dict[str, list[dict]] = {}
    baseline_by_regime: dict = {"__pooled__": 0.5}
    baseline_pooled = 0.5
    for pid, rt, rate, n, low in rows:
        if pid == "__baseline__":
            if rt:
                baseline_by_regime[rt] = float(rate)
            else:
                baseline_pooled = float(rate)
            continue
        if low:
            continue  # low_sample 不进认定（Fail-Closed）
        item = {"pattern_id": pid, "regime_tag": rt, "hit_rate": float(rate), "n_events": int(n)}
        if not rt:
            pooled.append(item)
        else:
            regime_by_pattern.setdefault(pid, []).append(item)
    if baseline_pooled == 0.5 and "__pooled__" not in baseline_by_regime:
        baseline_by_regime["__pooled__"] = 0.5
    return pooled, regime_by_pattern, baseline_pooled, baseline_by_regime  # noqa: RET504


def persist_certifications(client, records: Iterable[CertificationRecord], *, certified_at: Any) -> int:
    """认证结果全量重放写入（ReplacingMergeTree 同键取最新；只追加语义）。"""
    import datetime as _dt

    rows = [
        (r.pattern_id, r.timeframe, r.direction, int(r.fwd_window),
         float(r.p_value), float(r.q_value), float(r.n_eff), float(r.shrunk),
         float(r.wilson), float(r.within_regime_edge), float(r.edge_concentration),
         r.state, certified_at)
        for r in records
    ]
    if rows:
        client.execute(
            "INSERT INTO c1_market.market_pattern_certification "
            "(pattern_id, timeframe, direction, fwd_window, p_value, q_value, n_eff, "
            "shrunk_rate, wilson_lb, within_regime_edge, edge_concentration, state, certified_at) "
            "VALUES",
            rows,
        )
    return len(rows)


def load_certification(client, pattern_id: str, *, timeframe: str = "day",
                       direction: str = "向上", fwd_window: int = 10) -> dict | None:
    """读单形态认证行（W-CC 消费口：state/shrunk_rate；查无=None）。"""
    rows = client.execute(
        "SELECT state, shrunk_rate FROM c1_market.market_pattern_certification FINAL "
        "WHERE pattern_id = %(p)s AND timeframe = %(tf)s AND direction = %(d)s "
        "AND fwd_window = %(w)d LIMIT 1",
        {"p": pattern_id, "tf": timeframe, "d": direction, "w": int(fwd_window)},
    )
    if not rows:
        return None
    return {"state": rows[0][0], "shrunk_rate": float(rows[0][1])}


def run_certify(client=None, *, timeframe: str = "day", direction: str = "向上",
                fwd_window: int = 10) -> dict:
    """单家族认证入口（CLI/任务块共用）：读统计→四闸→写认证表→返回摘要。"""
    from datetime import datetime as _dt, timezone as _tz

    client = _ensure_client(client)
    pooled, regime_by_pattern, base_pooled, base_by_regime = load_family_rows(
        client, timeframe=timeframe, direction=direction, fwd_window=fwd_window
    )
    records = certify_family(
        pooled, regime_by_pattern, base_pooled, base_by_regime,
        fwd_window=fwd_window, timeframe=timeframe, direction=direction,
    )
    # 生命周期覆盖层（单写手：retired/resurrected/frozen 覆盖当日三态；方案 v1.0 W-R）
    try:
        from zephyr.signal_ashare.strategy_signal.pattern_lifecycle import (
            LifecycleStore,
            _key,
            update_lifecycle,
        )

        rate_by_id = {r["pattern_id"]: r["hit_rate"] for r in pooled}
        lc_records = [
            {"key": _key(r.pattern_id, r.timeframe, r.direction, r.fwd_window),
             "state": r.state,
             "hit_rate": rate_by_id.get(r.pattern_id, 0.0),
             "n_events": r.n_events}
            for r in records
        ]
        lc_store = LifecycleStore()
        update_lifecycle(
            lc_records, lc_store,
            baseline_by_key={
                _key(r.pattern_id, r.timeframe, r.direction, r.fwd_window): base_pooled
                for r in records
            },
            today=_dt.now(_tz.utc).date().isoformat(),
        )
        state_by_key = {r["key"]: r["state"] for r in lc_records}
        import dataclasses as _dc

        records = [
            _dc.replace(r, state=state_by_key.get(
                _key(r.pattern_id, r.timeframe, r.direction, r.fwd_window), r.state
            ))
            for r in records
        ]
    except ImportError:
        pass  # 生命周期层缺失不阻断认证主链（降级为三态）

    written = persist_certifications(client, records, certified_at=_dt.now(_tz.utc))
    counts: dict[str, int] = {}
    for r in records:
        counts[r.state] = counts.get(r.state, 0) + 1
    return {"family": f"{timeframe}/{direction}/{fwd_window}d", "total": len(records),
            "written": written, "counts": counts}


def main(argv: list[str] | None = None) -> int:
    """CLI 正身（任务块经 run_evidence_certify 子进程调用）。"""
    import argparse
    import json
    import sys as _sys

    parser = argparse.ArgumentParser(description="形态证据四闸认证器（MOD-SIG-148）")
    parser.add_argument("--certify", action="store_true")
    parser.add_argument("--timeframe", default="day")
    parser.add_argument("--direction", default="向上")
    parser.add_argument("--fwd-window", type=int, default=10)
    args = parser.parse_args(argv)
    if not args.certify:
        parser.print_help()
        return 2
    summary = run_certify(
        timeframe=args.timeframe, direction=args.direction, fwd_window=args.fwd_window
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
