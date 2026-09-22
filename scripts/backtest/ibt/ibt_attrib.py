# [BLUEPRINT] MOD-BT-IBT-ATTRIB | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.ibt.ibt_attrib
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; pyyaml
# [CONSUMERS] Max 施工方案 MAX-REMEDIATION-PLAN（复现/回归对照工具）；Owner 交付审计
# [STARTUP] manual CLI
# [MATURITY] experimental
# [INVARIANTS] 离线归因分析：读 artifacts nav/trades csv + run_summary/sensitivity yaml 计算成本/换手/回撤/Sharpe 底稿落 ibt_attribution.yaml；纯离线零 CH 访问零引擎重跑；协议冻结参数（IBT-PROTOCOL-V1）禁跑中改动；不接实盘不下单
# [MODIFY-GUARD] none（复现/回归对照工具件，改动须随数值回归对照 R-022）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError(产物缺失→跳窗 continue 同原稿) | ValueError(csv 列缺失) 透传
# [TESTS] none（工具件；红蓝对抗 ibt_redblue.py 即其自证）
# [TTL] task_bound
# [NOTE] 一次性战役工具件（manual CLI 非永久系统）；复现/回归对照专用
# [A_module] module_id=MOD-BT-IBT-ATTRIB | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""归因分析正式版（批A 工具正门化，源自 st-integrated-bt-20260922 原稿）——读 artifacts 离线计算，不重跑引擎.

产出: docs/_working/integrated_backtest/IBT-ATTRIBUTION.md 的数字底稿 yaml
  组合层指标汇总 / 成本归因 / 换手 / 成员贡献 / B-A regime 节流增量
用法: python scripts/backtest/ibt/ibt_attrib.py
产物: docs/_working/integrated_backtest/ibt_attribution.yaml（机读=.yaml 批H③口径）
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "docs" / "_working" / "integrated_backtest" / "artifacts"
WINDOWS = ["W_IS", "W_OOS", "W_HOLDOUT", "W_POSTD"]


def nav_stats(csv: Path) -> dict:
    import pandas as pd

    df = pd.read_csv(csv, parse_dates=[0])
    nav = df["nav"].astype(float)
    ret = nav.pct_change().dropna()
    ann = (nav.iloc[-1] / nav.iloc[0]) ** (252 / max(len(nav), 1)) - 1
    dd = (nav / nav.cummax() - 1).min()
    return {
        "days": int(len(nav)),
        "total_return": float(nav.iloc[-1] / nav.iloc[0] - 1),
        "ann_return": float(ann),
        "sharpe_daily": float(ret.mean() / ret.std() * (252 ** 0.5)) if ret.std() > 0 else 0.0,
        "max_dd": float(dd),
        "daily_vol": float(ret.std()),
    }


def cost_attr(csv: Path, initial: float = 1_000_000.0) -> dict:
    import pandas as pd

    df = pd.read_csv(csv, parse_dates=["date"])
    commission = float(df["commission"].sum())
    slippage = float(df["slippage_cost"].sum())
    buys = df[df["side"] == "BUY"]
    sells = df[df["side"] == "SELL"]
    buy_val = float((buys["quantity"] * buys["price"]).sum())
    sell_val = float((sells["quantity"] * sells["price"]).sum())
    days = df["date"].nunique()
    return {
        "fills": int(len(df)),
        "buys": int(len(buys)),
        "sells": int(len(sells)),
        "commission_total": commission,
        "slippage_total": slippage,
        "cost_total": commission + slippage,
        "cost_pct_of_initial": (commission + slippage) / initial,
        "buy_value": buy_val,
        "sell_value": sell_val,
        "annual_turnover_x": (buy_val / initial) / max(days / 252, 1e-9),
    }


def main() -> None:
    import yaml

    out = {}
    for w in WINDOWS:
        wdir = ART / w
        rs = wdir / "run_summary.yaml"
        if not rs.exists():
            continue
        art = yaml.safe_load(rs.read_text(encoding="utf-8"))
        block: dict = {"variants": art.get("variants", {}), "members": art.get("members", {}), "benchmark": art.get("benchmark", {}), "meta": {k: art["meta"].get(k) for k in ("window", "members", "skipped_members", "rescale_factor", "alpha_total", "compose_notes", "regime", "data")}}
        for vid in ("IBT-A", "IBT-B"):
            nav_csv = wdir / f"nav_{vid}.csv"
            tr_csv = wdir / f"trades_{vid}.csv"
            if nav_csv.exists():
                block[f"{vid}_nav_stats"] = nav_stats(nav_csv)
            if tr_csv.exists():
                block[f"{vid}_cost"] = cost_attr(tr_csv)
        sens = wdir / "sensitivity.yaml"
        if sens.exists():
            block["sensitivity"] = yaml.safe_load(sens.read_text(encoding="utf-8"))
        out[w] = block

    dest = ROOT / "docs" / "_working" / "integrated_backtest" / "ibt_attribution.yaml"
    dest.write_text(yaml.dump(out, allow_unicode=True, sort_keys=False, default_flow_style=False), encoding="utf-8")
    print(f"saved -> {dest}")
    for w, b in out.items():
        a = b.get("IBT-A_nav_stats", {})
        c = b.get("IBT-A_cost", {})
        print(f"{w}: A ret={a.get('total_return')} sharpe={a.get('sharpe_daily')} dd={a.get('max_dd')} "
              f"turnover={c.get('annual_turnover_x')}x cost={c.get('cost_total')}")


if __name__ == "__main__":
    main()
