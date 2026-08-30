# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.shift_handover_checklist
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.utils.time_utils
# [CONSUMERS] CLI: python -m zephyr.trading.shift_handover_checklist
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 24/7 三班制窗口固定 UTC 0/8/16; 总体状态=所有检查项中最差级别(FAIL>WARN>PASS)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=总体非FAIL(可交接); exit 1=存在FAIL项(禁止交接)/快照文件错误; exit 2=参数错误
# [TESTS] tests/trading/test_shift_handover_checklist.py
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ShiftHandoverChecklist — 班次交接检查清单（24/7 连续市场班次运营）
====================================================================

每班开始前对接班环境做五项检查：

1. 持仓状态（positions）——持仓记录完整性 / 杠杆上限
2. 保证金水平（margin）——权益/已用保证金比率分级阈值
3. 资金费率（funding_rate）——极端费率成本风险
4. 信号有效性（signals）——信号新鲜度（TTL 过期判定）
5. 系统健康（system_health）——组件 up/degraded/down

每项输出 PASS/WARN/FAIL 三级结构化结果，总体状态取最差级别。
支持 JSON 输出供前端消费。

命令行::

    python -m zephyr.trading.shift_handover_checklist --shift 0/8/16 [--input snapshot.json]

exit codes: 0=总体非 FAIL（可交接）, 1=存在 FAIL 项或快照读取失败, 2=参数错误。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: shift 参数
#   fields: 参数 shift，类型注解 int
#   code: shift_handover_checklist.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: argv 参数
#   fields: 参数 argv，类型注解 list[str] | None
#   code: shift_handover_checklist.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① MarginState
#   name_en: MarginState
#   intro: 保证金快照。
#   desc: 保证金快照。；公共方法（定义序）: margin_ratio；源码 L183-L194
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② ShiftSnapshot
#   name_en: ShiftSnapshot
#   intro: 班次交接检查输入快照——由调用方从实时数据源装配。
#   desc: 班次交接检查输入快照——由调用方从实时数据源装配。；公共方法（定义序）: from_dict；源码 L225-L275
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ CheckFinding
#   name_en: CheckFinding
#   intro: 单项检查内的具体发现（带级别）。
#   desc: 单项检查内的具体发现（带级别）。；公共方法（定义序）: to_dict；源码 L279-L286
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ CheckItem
#   name_en: CheckItem
#   intro: 一个检查项的结构化结果。
#   desc: 一个检查项的结构化结果。；公共方法（定义序）: to_dict；源码 L290-L304
#   inputs: 无参数
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ ShiftHandoverReport
#   name_en: ShiftHandoverReport
#   intro: 班次交接检查报告——JSON 输出供前端消费。
#   desc: 班次交接检查报告——JSON 输出供前端消费。；公共方法（定义序）: to_dict, to_json；源码 L308-L332
#   inputs: 无参数
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ shift_window_utc
#   name_en: shift_window_utc
#   intro: 返回班次 UTC 窗口字符串，如 shift=0 → '00:00-08:00'。
#   desc: 返回班次 UTC 窗口字符串，如 shift=0 → '00:00-08:00'。；源码 L335-L340
#   inputs: shift
#   outputs: str
# - id: A7
#   name_zh: ⑦ ShiftHandoverChecklist
#   name_en: ShiftHandoverChecklist
#   intro: 班次交接检查清单——五项接班前检查，输出 PASS/WARN/FAIL 结构化结果。
#   desc: 班次交接检查清单——五项接班前检查，输出 PASS/WARN/FAIL 结构化结果。；公共方法（定义序）: run；源码 L349-L480
#   inputs: 无参数
#   outputs: 返回值
# - id: A8
#   name_zh: ⑧ main
#   name_en: main
#   intro: main(argv) 源码 L496-L509
#   desc: 源码 L496-L509
#   inputs: argv
#   outputs: int
#   （注：A8 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: CLI: python -m zephyr.trading.shift_handover_checklist
# - id: O2
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: CLI: python -m zephyr.trading.shift_handover_checklist
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> O1
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from zephyr.shared.utils.time_utils import now_utc

VALID_SHIFTS: tuple[int, ...] = (0, 8, 16)
SHIFT_HOURS = 8

# ── 分级阈值（魔数提取为命名常量）──
_MARGIN_FAIL_RATIO = 1.2  # 权益/已用保证金 低于此值 → FAIL（逼近强平线）
_MARGIN_WARN_RATIO = 1.5  # 低于此值 → WARN（缓冲不足）
_MAX_LEVERAGE = 10.0  # 单持仓杠杆上限
_MAX_POSITIONS = 100  # 持仓数量上限（超过 WARN）
_FUNDING_WARN_ABS = 0.001  # |资金费率| > 0.1% → WARN（成本偏高）
_FUNDING_FAIL_ABS = 0.003  # |资金费率| > 0.3% → FAIL（极端费率）
_SIGNAL_NEAR_EXPIRY_RATIO = 0.8  # 信号年龄超过 TTL 的 80% → WARN（临近过期）


class CheckStatus(Enum):
    """检查项三级状态。"""

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


_STATUS_RANK: dict[CheckStatus, int] = {
    CheckStatus.PASS: 0,
    CheckStatus.WARN: 1,
    CheckStatus.FAIL: 2,
}


@dataclass
class PositionState:
    """单个持仓快照。"""

    symbol: str
    quantity: float
    leverage: float = 1.0


@dataclass
class MarginState:
    """保证金快照。"""

    equity: float
    used_margin: float

    @property
    def margin_ratio(self) -> float:
        """权益/已用保证金比率；未用保证金时视为无穷大（无风险敞口）。"""
        if self.used_margin <= 0:
            return float("inf")
        return self.equity / self.used_margin


@dataclass
class FundingRateState:
    """单个品种资金费率快照。"""

    symbol: str
    rate: float


@dataclass
class SignalState:
    """单个交易信号快照。"""

    signal_id: str
    strategy: str = ""
    generated_at: str = ""  # ISO 格式时间戳
    ttl_seconds: float = 300.0


@dataclass
class ComponentHealth:
    """单个系统组件健康状态。status: up / degraded / down。"""

    name: str
    status: str = "up"
    detail: str = ""


@dataclass
class ShiftSnapshot:
    """班次交接检查输入快照——由调用方从实时数据源装配。"""

    positions: list[PositionState] = field(default_factory=list)
    margin: MarginState | None = None
    funding_rates: list[FundingRateState] = field(default_factory=list)
    signals: list[SignalState] = field(default_factory=list)
    components: list[ComponentHealth] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> ShiftSnapshot:
        """从 JSON dict 装配快照；未知键忽略，缺失段落按空处理。"""
        margin_raw = data.get("margin")
        margin = None
        if isinstance(margin_raw, dict):
            margin = MarginState(
                equity=float(margin_raw.get("equity", 0.0)),
                used_margin=float(margin_raw.get("used_margin", 0.0)),
            )
        return cls(
            positions=[
                PositionState(
                    symbol=str(p.get("symbol", "")),
                    quantity=float(p.get("quantity", 0.0)),
                    leverage=float(p.get("leverage", 1.0)),
                )
                for p in data.get("positions", [])
            ],
            margin=margin,
            funding_rates=[
                FundingRateState(symbol=str(f.get("symbol", "")), rate=float(f.get("rate", 0.0)))
                for f in data.get("funding_rates", [])
            ],
            signals=[
                SignalState(
                    signal_id=str(s.get("signal_id", "")),
                    strategy=str(s.get("strategy", "")),
                    generated_at=str(s.get("generated_at", "")),
                    ttl_seconds=float(s.get("ttl_seconds", 300.0)),
                )
                for s in data.get("signals", [])
            ],
            components=[
                ComponentHealth(
                    name=str(c.get("name", "")),
                    status=str(c.get("status", "up")),
                    detail=str(c.get("detail", "")),
                )
                for c in data.get("components", [])
            ],
        )


@dataclass
class CheckFinding:
    """单项检查内的具体发现（带级别）。"""

    level: CheckStatus
    message: str

    def to_dict(self) -> dict:
        return {"level": self.level.value, "message": self.message}


@dataclass
class CheckItem:
    """一个检查项的结构化结果。"""

    name: str
    status: CheckStatus
    summary: str
    findings: list[CheckFinding] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status.value,
            "summary": self.summary,
            "findings": [f.to_dict() for f in self.findings],
        }


@dataclass
class ShiftHandoverReport:
    """班次交接检查报告——JSON 输出供前端消费。"""

    shift: int
    window_utc: str
    overall: CheckStatus
    items: list[CheckItem]
    generated_at: str

    def to_dict(self) -> dict:
        counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
        for item in self.items:
            counts[item.status.value] += 1
        return {
            "shift": self.shift,
            "window_utc": self.window_utc,
            "overall": self.overall.value,
            "handover_allowed": self.overall is not CheckStatus.FAIL,
            "counts": counts,
            "items": [item.to_dict() for item in self.items],
            "generated_at": self.generated_at,
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


def shift_window_utc(shift: int) -> str:
    """返回班次 UTC 窗口字符串，如 shift=0 → '00:00-08:00'。"""
    if shift not in VALID_SHIFTS:
        raise ValueError(f"非法班次: {shift}（合法值: {VALID_SHIFTS}）")
    end = shift + SHIFT_HOURS
    return f"{shift:02d}:00-{end:02d}:00"


def _worst(findings: list[CheckFinding]) -> CheckStatus:
    if not findings:
        return CheckStatus.PASS
    return max((f.level for f in findings), key=lambda lv: _STATUS_RANK[lv])


class ShiftHandoverChecklist:
    """班次交接检查清单——五项接班前检查，输出 PASS/WARN/FAIL 结构化结果。"""

    def run(self, snapshot: ShiftSnapshot, shift: int, *, now: datetime | None = None) -> ShiftHandoverReport:
        """执行全部检查项并返回报告。``now`` 可注入便于测试，默认取当前 UTC。"""
        window = shift_window_utc(shift)  # 非法班次在此抛 ValueError
        now = now or now_utc()
        items = [
            self._check_positions(snapshot.positions),
            self._check_margin(snapshot.margin),
            self._check_funding(snapshot.funding_rates),
            self._check_signals(snapshot.signals, now),
            self._check_system_health(snapshot.components),
        ]
        overall = max((item.status for item in items), key=lambda lv: _STATUS_RANK[lv])
        return ShiftHandoverReport(
            shift=shift,
            window_utc=window,
            overall=overall,
            items=items,
            generated_at=now.isoformat(),
        )

    # ── 五项检查 ──

    def _check_positions(self, positions: list[PositionState]) -> CheckItem:
        findings: list[CheckFinding] = []
        if not positions:
            return CheckItem("positions", CheckStatus.PASS, "无持仓", findings)
        if len(positions) > _MAX_POSITIONS:
            findings.append(CheckFinding(CheckStatus.WARN, f"持仓数量 {len(positions)} 超过上限 {_MAX_POSITIONS}"))
        for pos in positions:
            if not pos.symbol:
                findings.append(CheckFinding(CheckStatus.FAIL, "存在缺失 symbol 的持仓记录（数据损坏）"))
            elif pos.quantity == 0:
                findings.append(CheckFinding(CheckStatus.WARN, f"{pos.symbol}: 零数量持仓记录"))
            if pos.leverage > _MAX_LEVERAGE:
                findings.append(
                    CheckFinding(CheckStatus.FAIL, f"{pos.symbol}: 杠杆 {pos.leverage}x 超过上限 {_MAX_LEVERAGE}x")
                )
        status = _worst(findings)
        summary = f"{len(positions)} 个持仓" + ("" if status is CheckStatus.PASS else f"，{len(findings)} 个异常")
        return CheckItem("positions", status, summary, findings)

    def _check_margin(self, margin: MarginState | None) -> CheckItem:
        if margin is None:
            return CheckItem(
                "margin",
                CheckStatus.WARN,
                "保证金数据缺失，无法确认保证金水平",
                [CheckFinding(CheckStatus.WARN, "未提供保证金快照")],
            )
        ratio = margin.margin_ratio
        if margin.equity < 0:
            return CheckItem(
                "margin",
                CheckStatus.FAIL,
                f"权益为负（{margin.equity:.2f}）",
                [CheckFinding(CheckStatus.FAIL, f"权益 {margin.equity:.2f} < 0")],
            )
        if ratio < _MARGIN_FAIL_RATIO:
            status, level = CheckStatus.FAIL, CheckStatus.FAIL
        elif ratio < _MARGIN_WARN_RATIO:
            status, level = CheckStatus.WARN, CheckStatus.WARN
        else:
            status, level = CheckStatus.PASS, CheckStatus.PASS
        summary = f"保证金比率 {ratio:.2f}" if ratio != float("inf") else "未使用保证金"
        findings = [] if status is CheckStatus.PASS else [CheckFinding(level, f"保证金比率 {ratio:.2f} 低于安全线")]
        return CheckItem("margin", status, summary, findings)

    def _check_funding(self, funding_rates: list[FundingRateState]) -> CheckItem:
        findings: list[CheckFinding] = []
        for fr in funding_rates:
            abs_rate = abs(fr.rate)
            if abs_rate > _FUNDING_FAIL_ABS:
                findings.append(CheckFinding(CheckStatus.FAIL, f"{fr.symbol}: 资金费率 {fr.rate:+.4%} 极端"))
            elif abs_rate > _FUNDING_WARN_ABS:
                findings.append(CheckFinding(CheckStatus.WARN, f"{fr.symbol}: 资金费率 {fr.rate:+.4%} 偏高"))
        status = _worst(findings)
        summary = "无资金费率敞口" if not funding_rates else f"{len(funding_rates)} 个品种资金费率正常范围内"
        if status is not CheckStatus.PASS:
            summary = f"{len(findings)} 个品种资金费率异常"
        return CheckItem("funding_rate", status, summary, findings)

    def _check_signals(self, signals: list[SignalState], now: datetime) -> CheckItem:
        findings: list[CheckFinding] = []
        for sig in signals:
            if not sig.generated_at:
                findings.append(CheckFinding(CheckStatus.WARN, f"{sig.signal_id}: 信号时间戳缺失"))
                continue
            try:
                generated = datetime.fromisoformat(sig.generated_at)
            except ValueError:
                findings.append(CheckFinding(CheckStatus.WARN, f"{sig.signal_id}: 信号时间戳无法解析"))
                continue
            if generated.tzinfo is None:
                generated = generated.replace(tzinfo=UTC)
            age_s = (now - generated).total_seconds()
            if age_s > sig.ttl_seconds:
                findings.append(
                    CheckFinding(
                        CheckStatus.FAIL,
                        f"{sig.signal_id}: 信号已过期（age={age_s:.0f}s > ttl={sig.ttl_seconds:.0f}s）",
                    )
                )
            elif age_s > sig.ttl_seconds * _SIGNAL_NEAR_EXPIRY_RATIO:
                findings.append(CheckFinding(CheckStatus.WARN, f"{sig.signal_id}: 信号临近过期（age={age_s:.0f}s）"))
        status = _worst(findings)
        summary = "无活跃信号" if not signals else f"{len(signals)} 个信号有效"
        if status is not CheckStatus.PASS:
            summary = f"{len(findings)} 个信号异常"
        return CheckItem("signals", status, summary, findings)

    def _check_system_health(self, components: list[ComponentHealth]) -> CheckItem:
        if not components:
            return CheckItem(
                "system_health",
                CheckStatus.WARN,
                "无系统健康数据上报",
                [CheckFinding(CheckStatus.WARN, "未提供组件健康快照")],
            )
        findings: list[CheckFinding] = []
        for comp in components:
            if comp.status == "down":
                findings.append(CheckFinding(CheckStatus.FAIL, f"{comp.name}: 组件宕机 {comp.detail}".strip()))
            elif comp.status == "degraded":
                findings.append(CheckFinding(CheckStatus.WARN, f"{comp.name}: 组件降级 {comp.detail}".strip()))
            elif comp.status != "up":
                findings.append(CheckFinding(CheckStatus.WARN, f"{comp.name}: 未知状态 {comp.status!r}"))
        status = _worst(findings)
        summary = f"{len(components)} 个组件全部正常" if status is CheckStatus.PASS else f"{len(findings)} 个组件异常"
        return CheckItem("system_health", status, summary, findings)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.trading.shift_handover_checklist",
        description="班次交接检查清单（24/7 连续市场班次运营）——JSON 输出供前端消费",
    )
    parser.add_argument(
        "--shift", type=int, required=True, choices=list(VALID_SHIFTS), help="班次起始 UTC 小时: 0/8/16"
    )
    parser.add_argument("--input", default=None, help="快照 JSON 文件路径；缺省使用空快照（视为健康基线）")
    parser.add_argument("--compact", action="store_true", default=False, help="紧凑 JSON 输出（无缩进）")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    snapshot = ShiftSnapshot()
    if args.input:
        try:
            snapshot = ShiftSnapshot.from_dict(json.loads(Path(args.input).read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, ValueError) as e:
            print(f"ERROR: 快照文件读取失败: {e}", file=sys.stderr)
            return 1

    report = ShiftHandoverChecklist().run(snapshot, args.shift)
    print(report.to_json(indent=None if args.compact else 2))
    return 0 if report.overall is not CheckStatus.FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
