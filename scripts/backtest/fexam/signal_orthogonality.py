# [BLUEPRINT] MOD-BT-SIGORTH | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.fexam.signal_orthogonality
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] 新信号准入门（裁定#535 同源：15 员池实测仅 4.4 个独立信号，成员互为拷贝）;
#   pool-report=独立信号清单产出工具; 人工 CLI（gate/pool-report）
# [STARTUP] manual
# [MATURITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] 准入门柱=|spearman|≤0.3（与在途裁定#535 同源，执行器零裁量，阈值 --gate 显式传参
#   缺省 0.3）；相关性只在共同日期交集上算（inner join，禁前向填充造相关）；reject→退出码 5
#   （准入门专用码），pass→0，入参错误→2；池面统计=相关矩阵特征值 participation ratio
#   =(Σλ)²/Σλ²，即有效独立信号数；只读输入 CSV，唯一写面=--out 指定路径；报告零时间戳
#   （输出为输入的纯函数，测试可复现）；测试零 CH 零 DB（tmp_path 合成 CSV）。
# [MODIFY-GUARD] tests/backtest/fexam/test_signal_orthogonality.py
# [STABILITY] experimental
# [ERROR_CONTRACT] ValueError: 缺 date/sig 列/文件不存在/池为空/共同日期<3/常数序列; SystemExit: argparse
# [TESTS] tests/backtest/fexam/test_signal_orthogonality.py
# [A_module] module_id=MOD-BT-SIGORTH | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 本件=人工/席位按需调用的 CLI 准入闸（gate/pool-report 子命令），非常驻服务，事件订阅不适用（裁定#538 抢救入库时按 m11 逐件声明通道补登）
# [not-trading: 回测研究面准入统计工具，不在实盘交易决策路径上]
# create-guard-not-dup: 本模块=回测研究面信号相关性统计工具（spearman 准入闸+池参与率，裁定#535 同源），非 LSG runtime_llm_call_interceptor 的第二实现——'run gate' 命中纯属 CLI 子命令措辞撞词，两者无代码/数据流交集
"""信号正交闸——新信号准入相关性门 + 信号池参与率统计。

背景（裁定#535 同源）：15 员池实测仅 4.4 个独立信号，成员互相是拷贝。故新信号准入
必过相关性门：候选 vs 池内每员算 |spearman|，max|corr|>0.3 → 判 reject（退出码 5）。

两子命令：
  gate         --candidate <csv> --pool <glob|目录> --gate 0.3 [--out report.json]
               逐员相关值 + max_corr/最像成员/verdict；JSON 报告含每员相关值。
  pool-report  --pool <glob|目录> [--out report.json]
               池内两两相关矩阵 + 特征值 participation ratio=(Σλ)²/Σλ²
               = 有效独立信号数——"独立信号清单"的产出工具。

信号形制：CSV 须含 date,sig 两列；相关性一律在共同日期交集（inner join）上算。
"""

from __future__ import annotations

import argparse
import glob as globlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_GATE = 0.3
GATE_EXIT_CODE = 5  # 准入门 reject 专用退出码
ERROR_EXIT_CODE = 2  # 入参/数据错误（与 argparse 惯例一致）
MIN_OVERLAP = 3  # 秩相关最少共同日期数

GATE_KIND = "signal_orthogonality_gate"
POOL_REPORT_KIND = "signal_orthogonality_pool_report"


def load_signal(csv: str | Path) -> pd.Series:
    """读入 date,sig 两列 CSV，返回按日期升序的 float Series（index=日期，name=文件 stem）。

    只认共同真值：缺列/缺文件抛 ValueError；非数值与空行丢弃；同日重复取末条。
    """
    path = Path(csv)
    if not path.is_file():
        raise ValueError(f"信号 CSV 不存在: {path}")  # noqa: MSG-EXPOSURE  路径系操作者自给 CLI 参数，回显为用户工程学非敏感泄露（裁定#538 抢救留档）
    frame = pd.read_csv(path)
    cols = {str(c).strip().lower(): c for c in frame.columns}
    if "date" not in cols or "sig" not in cols:
        raise ValueError(f"信号 CSV 须含 date,sig 两列: {path} 实有 {list(frame.columns)}")  # noqa: MSG-EXPOSURE  同上：操作者自给路径回显
    pair = frame[[cols["date"], cols["sig"]]].copy()
    pair.columns = ["date", "sig"]
    pair["date"] = pd.to_datetime(pair["date"], errors="coerce")
    pair["sig"] = pd.to_numeric(pair["sig"], errors="coerce")
    pair = pair.dropna().drop_duplicates(subset="date", keep="last").sort_values("date")
    return pd.Series(
        pair["sig"].to_numpy(dtype=float),
        index=pd.DatetimeIndex(pair["date"], name="date"),
        name=path.stem,
    )


def spearman_corr(a: pd.Series, b: pd.Series) -> tuple[float, int]:
    """共同日期交集上的 spearman 相关（pandas .corr(method='spearman')），返回 (corr, n_overlap)。

    两侧 Series 同名（候选被池目录 glob 吸入产生自比）时列名防撞：pandas DataFrame 同键
    会塌缩成单列，iloc[:,1] 越界 IndexError 裸崩 rc=1（st-ibtclose-20261015 回归修复），
    同名侧加 '#self' 后缀保双列，自比 |corr|=1 → 设计判 reject（退出码 5）。
    """
    common = a.index.intersection(b.index)
    if len(common) < MIN_OVERLAP:
        raise ValueError(f"共同日期不足: {len(common)} < {MIN_OVERLAP}（{a.name} vs {b.name}），拒绝算相关")
    name_a, name_b = str(a.name), str(b.name)
    if name_b == name_a:
        name_b = f"{name_b}#self"
    panel = pd.DataFrame({name_a: a.loc[common], name_b: b.loc[common]})
    corr = panel.iloc[:, 0].corr(panel.iloc[:, 1], method="spearman")
    if pd.isna(corr):
        raise ValueError(f"spearman 相关未定义（常数序列）: {a.name} vs {b.name}")
    return float(corr), int(len(common))


def expand_pool(spec: str) -> list[Path]:
    """池声明解析：目录→其下 *.csv；含通配符→glob；单文件→单元素。空命中抛 ValueError。"""
    p = Path(spec)
    if p.is_dir():
        members = sorted(p.glob("*.csv"))
    elif any(ch in spec for ch in "*?["):
        members = sorted(Path(x) for x in globlib.glob(spec))
    elif p.is_file():
        members = [p]
    else:
        members = []
    if not members:
        raise ValueError(f"--pool 未命中任何信号 CSV: {spec}")
    return members


def run_gate(candidate: str | Path, pool_spec: str, threshold: float = DEFAULT_GATE) -> dict:
    """候选 vs 池内每员 |spearman|；max|corr|>threshold → reject。报告含每员相关值。"""
    cand = load_signal(candidate)
    members = expand_pool(pool_spec)
    per_member = []
    for member in members:
        corr, n_overlap = spearman_corr(cand, load_signal(member))
        per_member.append({"member": str(member), "n_overlap": n_overlap, "corr": corr, "abs_corr": abs(corr)})
    worst = max(per_member, key=lambda row: row["abs_corr"])
    verdict = "reject" if worst["abs_corr"] > threshold else "pass"
    return {
        "kind": GATE_KIND,
        "candidate": str(candidate),
        "pool": [str(m) for m in members],
        "threshold": threshold,
        "per_member": per_member,
        "max_corr": worst["abs_corr"],
        "max_corr_signed": worst["corr"],
        "most_similar_member": worst["member"],
        "verdict": verdict,
    }


def run_pool_report(pool_spec: str) -> dict:
    """池内两两 spearman 相关矩阵 + 特征值 participation ratio=(Σλ)²/Σλ²=有效独立信号数。

    全员先对齐到共同日期交集（保证矩阵一致、特征值实数），单员池退化为 PR=1。
    """
    members = expand_pool(pool_spec)
    series = {str(m): load_signal(m) for m in members}
    common: pd.Index | None = None
    for sig in series.values():
        common = sig.index if common is None else common.intersection(sig.index)
    assert common is not None  # members 非空保证
    if len(common) < MIN_OVERLAP:
        raise ValueError(f"池内共同日期不足: {len(common)} < {MIN_OVERLAP}")
    panel = pd.DataFrame({name: sig.loc[common] for name, sig in series.items()})
    corr_matrix = panel.corr(method="spearman")
    eigenvalues = np.linalg.eigvalsh(corr_matrix.to_numpy(dtype=float))
    lam = np.clip(eigenvalues, 0.0, None)  # 数值噪声贴零负根钳零，稳 PR
    participation_ratio = float(lam.sum() ** 2 / (lam**2).sum())
    matrix = {row: {col: float(corr_matrix.loc[row, col]) for col in corr_matrix.columns} for row in corr_matrix.index}
    return {
        "kind": POOL_REPORT_KIND,
        "members": list(series),
        "n_members": len(series),
        "n_common_dates": int(len(common)),
        "correlation_matrix": matrix,
        "eigenvalues": [float(x) for x in eigenvalues],
        "participation_ratio": participation_ratio,
        "effective_n_signals": participation_ratio,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="signal_orthogonality", description="信号正交闸：新信号准入门 + 池参与率统计")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gate = sub.add_parser("gate", help="候选信号准入判定（|spearman|≤gate 才放行）")
    p_gate.add_argument("--candidate", required=True, help="候选信号 CSV（date,sig 两列）")
    p_gate.add_argument("--pool", required=True, help="信号池：glob 或目录（*.csv）")
    p_gate.add_argument("--gate", type=float, default=DEFAULT_GATE, help="门柱阈值（缺省 0.3）")
    p_gate.add_argument("--out", help="JSON 报告落盘路径（可省）")

    p_pool = sub.add_parser("pool-report", help="池内两两相关矩阵 + 有效独立信号数（PR）")
    p_pool.add_argument("--pool", required=True, help="信号池：glob 或目录（*.csv）")
    p_pool.add_argument("--out", help="JSON 报告落盘路径（可省）")

    args = parser.parse_args(argv)
    try:
        if args.command == "gate":
            report = run_gate(args.candidate, args.pool, threshold=args.gate)
        else:
            report = run_pool_report(args.pool)
    except ValueError as exc:
        print(f"[SIGNAL-ORTHOGONALITY] ERROR: {exc}", file=sys.stderr)
        return ERROR_EXIT_CODE

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if report["kind"] == GATE_KIND:
        print(
            f"verdict={report['verdict']} max|corr|={report['max_corr']:.4f} "
            f"(gate={report['threshold']}) most_similar={report['most_similar_member']}"
        )
        return GATE_EXIT_CODE if report["verdict"] == "reject" else 0
    print(
        f"n_members={report['n_members']} n_common_dates={report['n_common_dates']} "
        f"effective_n_signals(PR)={report['participation_ratio']:.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
