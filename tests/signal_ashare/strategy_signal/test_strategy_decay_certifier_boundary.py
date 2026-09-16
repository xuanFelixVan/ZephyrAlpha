# [BLUEPRINT] MOD-SIG-150 | tests/signal_ashare/strategy_signal/test_strategy_decay_certifier_boundary.py
# [TTL] permanent
"""strategy_decay_certifier 边界域测试（挖矿节点 SDC-1 → 2026-09-17 施工后改写）。

审的是**输入定义域**。挖矿时的事实（仍成立，本文件第 1 节继续钉住）：
`deflated_sharpe` 唯一生产写方 `scripts/backtest/translated/_c4_engine.batch_deflated_sharpe`
写的是 `round(float(v.dsr), 4)`，dsr 由 `DeflatedSharpeCalculator.calculate` 产出，
`_normal_cdf` 值域 (0,1)（下溢可取 0.0），退化分支只返回 1.0/0.5
（src/zephyr/simulation/deflated_sharpe_calculator.py:305-312）⇒ **落库 ds 恒 ≥ 0**。
故旧判据 `ds < 0 → failed` 在生产中永不被取，连带 `failed_streak`→`retired` 建议链整体死亡，
而旧 `test_strategy_decay_certifier.py` 用 `ds=-0.2` 造 fixture 打到了 failed 分支——
那是生产者永不发出的值（测试假阳性，轴 A.3）。

SDC-1 治本（挖矿报告 §9 提案 A1）：判死判据改挂**同表在册**的 `oos_years_decay`
（DDL 注释「0~1, >=0.5 判存疑土规」，与 DECAY_SUSPECT_LINE 四条既有预注册线同数）。
本文件随之翻转（挖矿报告 §3 验收注："合法域永不产出 failed" 与 "存在合法输入可产出 failed"
二者不可同时绿——旧断言变红即施工到位的信号）：

* 第 2 节钉**可达性**：合法衰减值（≥0.5）确实产出 failed，并连周推到 retired；
* 第 3 节钉**轴分离**：DS 轴单独仍永不判死（判死权只在衰减轴上），越出 [0,1] 的 DS
  按上游口径事故封顶 probation 而非判死；
* 第 1 节只钉 DS 轴的**值域边界**（生产者永不发负 / 输入恒落 [0,1]）——退化态该判显著
  还是判"不可判"归 MOD-SIM-024 的 SDC-3/SDC-4 口径施工（2026-09-17 他会话 WIP），
  本件不钉他件语义。
"""

from __future__ import annotations

import json
import math
import random

import pytest

from zephyr.signal_ashare.strategy_signal.strategy_decay_certifier import (
    _CERTIFIED_DS,
    _DECAY_SUSPECT,
    FAILED_WINDOWS,
    run_strategy_decay_certify,
)
from zephyr.simulation.deflated_sharpe_calculator import (
    DeflatedSharpeCalculator,
    DSRConfig,
)

# 生产实测锚点（2026-09-16 只读 CH 查询，见挖矿报告 §2）：
# c1_backtest.strategy_screen 全部 1202 行中 deflated_sharpe 非空 269 行，
# min=0.0 max=0.1448，负值 0 行；>=0.5 仅 4 个 CAND-* 行（N=1 短序列）。
MEASURED_MAX_STRATEGY_DS = 0.1448


class _NoopClient:
    """certifier 无条件先建 client（_ensure_client 在 rows 分支之前）——注入哑件不触库。"""

    def execute(self, sql, params=None):  # pragma: no cover - rows 显式传入时不会被调用
        raise AssertionError("本测试显式传 rows，禁止回落到真实读数路径")


def _rows(triples: list[tuple[str, float | None, float | None]]) -> list[dict]:
    """load_latest_metrics 的产物形状（dict，5 键；第三元=oos_years_decay 证据）。"""
    return [
        {"strategy_id": sid, "deflated_sharpe": ds, "is_sharpe": 1.0,
         "max_drawdown": 0.1, "oos_years_decay": decay}
        for sid, ds, decay in triples
    ]


# ---------------------------------------------------------------------------
# 1 生产者值域：dsr 恒 ∈ (0,1]，永不为负——SDC-1 的数学前提
# ---------------------------------------------------------------------------


def test_canonical_dsr_is_never_negative_across_input_battery() -> None:
    """对 24 组收益序列（含零方差/全负/极端夏普/厚尾）跑官方计算器，dsr 恒 > 0。"""
    calc = DeflatedSharpeCalculator(DSRConfig(periods_per_year=252))
    rng = random.Random(20260916)
    series: list[list[float]] = [
        [0.001] * 60,                       # 零方差 → sr=0 退化分支
        [-0.001] * 60,                      # 全负收益
        [0.0] * 60,                         # 恒零
        [1e-9] * 30 + [-1e-9] * 30,         # 近零抖动
        [0.02] * 250,                       # 极端正夏普（无波动）
    ]
    for _ in range(19):                     # 随机正态/厚尾/负偏混合
        n = rng.choice([30, 60, 250, 500])
        heavy = rng.random() < 0.4
        series.append([
            rng.gauss(0.0005, 0.02) * (6.0 if (heavy and rng.random() < 0.08) else 1.0)
            for _ in range(n)
        ])
    for rets in series:
        for trials in (1, 35, 4497):
            res = calc.calculate(rets, num_trials=trials)
            assert res.dsr >= 0.0, f"dsr 为负：{res.dsr} (T={len(rets)}, N={trials})"
            assert res.dsr <= 1.0
            assert res.var_sr >= 0.0


def test_degenerate_series_input_stays_inside_dsr_domain() -> None:
    """历史退化构造（等差收益序列）：DS 恒 ∈ [0,1] ⇒ 判定器不会误读成"上游口径事故"。

    挖矿版此条钉的是 `var_sr<=0 ⇒ dsr=1.0`（"公式算不动被判成最显著"的 fail-open 现状）。
    该现状已不归本件钉：MOD-SIM-024 于 2026-09-17 做 SDC-3/SDC-4 口径施工（超额峰度→
    Pearson +3 转换、退化态映射为 DSR_UNDECIDABLE=0.0+degenerate=True+WARNING），
    同会话 WIP 中，其旧构造亦不再落进退化分支（实测 var_sr=+0.0064）。
    SDC-1 只依赖一条：**DS 轴的值域边界**（越界=事故封顶，不越界=可判），故本条只钉域。
    退化态该判显著还是判"不可判"=任务②（挖矿报告 §4 SDC-2/SDC-4）的裁定面，
    构造方法与实测数据已登记在「施工回填 SDC-1/PA-1」残余项。
    """
    calc = DeflatedSharpeCalculator(DSRConfig(periods_per_year=252))
    n = 250
    rets = [0.5 + i * (1.0 / (n - 1)) - 0.5 for i in range(n)]   # 0.0 ~ 1.0 等差
    res = calc.calculate(rets, num_trials=4497)
    assert 0.0 <= res.dsr <= 1.0, f"DS 越出定义域 ⇒ 判定器会按口径事故封顶：{res.dsr}"
    assert math.isfinite(res.var_sr) and res.var_sr >= 0.0


# ---------------------------------------------------------------------------
# 2 判据可达性（SDC-1 施工后的主断言）：合法衰减证据 → failed → 连周 retired
# ---------------------------------------------------------------------------

# 生产实测锚点（2026-09-17 只读 CH）：oos_years_decay 非空 148 行、max=1.0、p90=1.0
# ——对照同表 deflated_sharpe 非空 269 行 / 负值 0 行：衰减轴是**真有货**的证据列，
# 旧判据挂错的 DS 轴才是分支死亡的原因。
MEASURED_MAX_DECAY = 1.0

LEGAL_DECAY_DEADLY = [
    _DECAY_SUSPECT,            # 恰在存疑线上（>= 语义）
    0.55,
    0.9,
    MEASURED_MAX_DECAY,        # 生产实测最大值（完全衰减）
]


@pytest.mark.parametrize("decay", LEGAL_DECAY_DEADLY)
def test_legal_decay_reaches_failed_then_retired(tmp_path, decay) -> None:
    """合法衰减 ≥0.5 连周扫必推到 retired——退役建议链从结构性死亡里活过来。"""
    ledger = tmp_path / "led.json"
    seen: set[str] = set()
    for window in range(FAILED_WINDOWS):
        r = run_strategy_decay_certify(
            client=_NoopClient(), ledger_path=ledger, today=f"W{window}",
            rows=_rows([("STR-DECAY", 0.2, decay)]),
        )
        seen |= {s for s, n in r["counts"].items() if n}
        if window < FAILED_WINDOWS - 1:
            assert r["counts"]["retired"] == 0, f"decay={decay} 第{window}周提前退役"
    assert r["counts"]["retired"] == 1, f"decay={decay} 连周判死未推出 retired（链仍死？）"
    assert {"failed", "retired"} <= seen, seen


def test_death_line_is_the_pre_registered_suspect_value(tmp_path) -> None:
    """存疑线=0.5（DDL 注释 + 四条既有预注册线同数，非本件自立）：线下不判死、线上判死。"""
    below = run_strategy_decay_certify(
        client=_NoopClient(), ledger_path=tmp_path / "a.json", today="D1",
        rows=_rows([("S", 0.9, _DECAY_SUSPECT - 1e-9)]))
    assert below["counts"]["certified"] == 1 and below["counts"]["failed"] == 0
    on_line = run_strategy_decay_certify(
        client=_NoopClient(), ledger_path=tmp_path / "b.json", today="D1",
        rows=_rows([("S", 0.9, _DECAY_SUSPECT)]))
    assert on_line["counts"]["failed"] == 1


# ---------------------------------------------------------------------------
# 3 轴分离：判死权只在衰减轴上，DS 轴单独永不判死（挖矿事实仍成立）
# ---------------------------------------------------------------------------

LEGAL_DS_VALUES = [
    None,                      # 无 DS（生产 491/574 行）
    1e-12,                     # 下确界
    0.05,                      # 生产众数量级（实测 max=0.1448）
    MEASURED_MAX_STRATEGY_DS,  # 生产实测最大
    _CERTIFIED_DS - 1e-9,
    _CERTIFIED_DS,             # 认证线
    0.95,                      # 本仓 DSR 显著性 SSoT 线（MOD-SIM-024）
    1.0,                       # 上确界（含退化饱和）
]


@pytest.mark.parametrize("ds", LEGAL_DS_VALUES)
def test_ds_axis_alone_never_reaches_failed_or_retired(tmp_path, ds) -> None:
    """衰减证据 NULL 时，DS 全域（含 None）扫描仍永不判死：旧死分支不会被"换个入口"复活。"""
    ledger = tmp_path / "led.json"
    states: set[str] = set()
    for window in range(FAILED_WINDOWS + 2):     # 连跑超过退役所需周数
        r = run_strategy_decay_certify(
            client=_NoopClient(), ledger_path=ledger, today=f"W{window}",
            rows=_rows([("STR-LEGAL", ds, None)]),
        )
        assert r["counts"]["failed"] == 0, f"ds={ds} 第{window}周出现 failed（DS 轴被接回判死？）"
        assert r["counts"]["retired"] == 0, f"ds={ds} 第{window}周出现 retired"
        states |= {s for s, n in r["counts"].items() if n}
    assert states <= {"probation", "certified"}, states


@pytest.mark.parametrize("ds", LEGAL_DS_VALUES)
def test_certified_requires_both_pre_registered_lines(tmp_path, ds) -> None:
    """认证=DS≥0.5 ∧ 衰减未越线；DS 单轴升降不再改变判死结论（衰减在册且清）。"""
    ledger = tmp_path / "led.json"
    r = run_strategy_decay_certify(
        client=_NoopClient(), ledger_path=ledger, today="D1",
        rows=_rows([("STR-X", ds, 0.0)]),
    )
    expect = "certified" if (ds is not None and ds >= _CERTIFIED_DS) else "probation"
    doc = json.loads(ledger.read_text(encoding="utf-8"))
    assert doc["strategies"]["STR-X"]["state"] == expect, r["counts"]


def test_seeded_streak_advances_to_retired_on_decay_breach(tmp_path) -> None:
    """台账已存 failed_streak=7（人工种入）+ 当轮合法衰减越线 → 立即 retired。

    挖矿时该断言反向（"合法输入永不续命"），SDC-1 后正向：连周链真的在跑。
    """
    ledger = tmp_path / "led.json"
    ledger.write_text(json.dumps({
        "schema": "strategy_decay/2", "updated_at": "D0",
        "strategies": {"STR-Y": {"state": "probation", "failed_streak": FAILED_WINDOWS - 1}},
    }), encoding="utf-8")
    r = run_strategy_decay_certify(
        client=_NoopClient(), ledger_path=ledger, today="D1",
        rows=_rows([("STR-Y", 0.001, 0.6)]),
    )
    assert r["counts"]["retired"] == 1
    doc = json.loads(ledger.read_text(encoding="utf-8"))
    assert doc["strategies"]["STR-Y"]["failed_streak"] == FAILED_WINDOWS


def test_seeded_streak_resets_when_decay_clears(tmp_path) -> None:
    """衰减回落存疑线下=链断（不是"记仇到永远"），当轮按常规判定封顶 probation。"""
    ledger = tmp_path / "led.json"
    ledger.write_text(json.dumps({
        "schema": "strategy_decay/2", "updated_at": "D0",
        "strategies": {"STR-Y": {"state": "probation", "failed_streak": FAILED_WINDOWS - 1}},
    }), encoding="utf-8")
    r = run_strategy_decay_certify(
        client=_NoopClient(), ledger_path=ledger, today="D1",
        rows=_rows([("STR-Y", 0.001, 0.1)]),
    )
    assert r["counts"]["retired"] == 0 and r["counts"]["probation"] == 1
    doc = json.loads(ledger.read_text(encoding="utf-8"))
    assert doc["strategies"]["STR-Y"]["failed_streak"] == 0


def test_producer_side_column_cannot_emit_negative(tmp_path) -> None:
    """批产写方口径复核（轴 C 下游）：_c4_engine 落库值来自 runner.variants[*].dsr，
    runner 全委托官方件 → 落库列不可能为负。这里以官方件+退化输入联合复算代证。"""
    from zephyr.backtest.regime_validation.c4_deflated_sharpe_runner import (
        run_deflated_sharpe_batch,
    )

    variants = {
        "good": [0.01, 0.005, -0.002] * 84,
        "flat": [0.0] * 200,
        "loss": [-0.01, -0.004, 0.001] * 84,
    }
    rep = run_deflated_sharpe_batch(variants, num_trials=4497)
    assert all(0.0 <= v.dsr <= 1.0 for v in rep.variants)
    assert all(round(v.dsr, 4) >= 0.0 for v in rep.variants)
    assert math.isfinite(rep.best_dsr)
