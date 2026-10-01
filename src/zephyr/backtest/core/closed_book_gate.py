# [BLUEPRINT] MOD-BT-201 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.closed_book_gate
# create-guard-not-dup: 本件是闭卷(HOLDOUT)读取闸(前视泄露fail-closed拦口),命中词to date系闭卷日语文巧合,非LLM探测/清单漂移/命名规范能力的第二实现
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.trading.validation.runner（延迟导入：holdout_cutoff + ValidationConfig.finalized_at）; zephyr.shared.io.file_utils; zephyr.shared.io.paths
# [CONSUMERS] zephyr.backtest.implementations.ch_tick_replay; zephyr.governance.data_governance.ch_tick_provider
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] 切点禁硬编码（唯一派生路=validation_method_registry.yaml discipline.holdout_months + ValidationConfig.finalized_at + runner.holdout_cutoff，缺位即 ClosedBookConfigError，禁放宽为全窗可读）; fail-closed（研究模式越切点=读库前抛错，SQL 执行次数恒 0）; 闭卷考试模式必经显式 exam_ticket（非空白串）且同批落审计行，缺票=拒; 比较口径=end 日期 > 切点即越界（切点当日放行，与 scripts/backtest/t0_material_line.enforce_closed_book 字符串比较同规）; 审计写=CAS+写后核读（热文件纪律）; 本件只读派生零库访问
# [MODIFY-GUARD] tests/backtest/test_closed_book_tick_gate.py
# [STABILITY] experimental
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ClosedBookViolation(越闭卷切点且无考卷工单)；ClosedBookConfigError(切点真源缺位/窗口参数不可解析)
# [TESTS] tests/backtest/test_closed_book_tick_gate.py
# [TTL] permanent
"""D_BACKTEST — 闭卷（HOLDOUT）读取闸：研究/回测数据面的前视泄露 fail-closed 拦口。

动机（LANE-PIT，2026-09-25 实测）：日线/分钟面研究件已有闭卷硬拦
（`scripts/backtest/t0_material_line.enforce_closed_book`，消费方 t0_rule_engine /
t0_state_match_matrix），但 tick 读口（`ch_tick_replay.fetch_historical`、
`ChTickProvider.fetch_historical`）无任何对应闸——切点后（闭卷保密区）的 tick
可以被无阻拦读入研究，且**不报错**。用于校正/定档/调参即前视泄露，直接污染成绩单。

判据真源：17 号文 §三.5（研究语料止于 HOLDOUT 切点，切点后=闭卷），
切点数值禁在本件落成常数——由 `closed_book_cutoff()` 从既有真源派生：
    cutoff = holdout_cutoff(as_of=ValidationConfig.finalized_at, months=discipline.holdout_months)
其中 finalized_at（定稿锚点 D=2026-09-09，Owner 裁定）在
`zephyr.trading.validation.runner`，holdout_months（=12，PB-08）在
`docs/01_policies_and_standards/_registry/catalogs/validation_method_registry.yaml`。
派生值与分钟面既有实现（t0_material_line.CLOSED_BOOK_CUTOFF）同一点，两处真源互证；
本件不落第二个切点常数（禁三头改）。

两态语义：
    研究态（默认，exam_ticket=None）：end > cutoff → ClosedBookViolation（读库前拦）。
    闭卷考试态（显式 exam_ticket 非空白）：放行 + 落一行审计（工单/读口/窗口/切点/时刻），
    审计面真源=data/backtest_artifacts/closed_book_exam_audit.jsonl。
    裸 flag（想考但不给工单）=同样拒——无审计痕迹的考试等于泄露口子。

# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/closed_book_gate.yaml
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Final

from zephyr.shared.io.file_utils import safe_read, safe_write_text
from zephyr.shared.io.paths import REPO_ROOT

_logger = logging.getLogger(__name__)

_METHOD_REGISTRY = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "validation_method_registry.yaml"
)
DEFAULT_EXAM_AUDIT_PATH = REPO_ROOT / "data" / "backtest_artifacts" / "closed_book_exam_audit.jsonl"


class ClosedBookConfigError(RuntimeError):
    """切点真源缺位/窗口参数不可解析（fail-closed：宁可拒读，禁放宽）。"""


class ClosedBookViolation(RuntimeError):
    """研究态读取越闭卷切点（PIT 前视泄露），或考试态缺工单。"""


@dataclass(frozen=True)
class ClosedBookDecision:
    """一次闸判定的可审计回执。"""

    surface: str
    cutoff: date
    start: date
    end: date
    mode: str  # "research" | "closed_book_exam"
    exam_ticket: str | None = None
    allowed: bool = True
    audit_path: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


def _holdout_months() -> int:
    """PB-08 保密窗月数（真源=YAML 纪律段，RULE-SSOT）。"""
    import yaml

    try:
        raw = yaml.safe_load(safe_read(_METHOD_REGISTRY))
    except Exception as exc:  # noqa: BLE001 — 真源不可读=不可判切点
        raise ClosedBookConfigError(f"holdout 纪律册不可读（{_METHOD_REGISTRY}）: {exc}") from exc
    months = (raw or {}).get("discipline", {}).get("holdout_months")
    if not isinstance(months, int) or months < 1:
        raise ClosedBookConfigError(f"discipline.holdout_months 非法: {months!r}")
    return months


def closed_book_cutoff() -> date:
    """闭卷切点（派生，禁硬编码）。

    Raises:
        ClosedBookConfigError: finalized_at 缺位/非法，或 holdout 纪律册读不到——
            此时宁拒不清（若静默返回一个极远日期=把闸自我拆除）。
    """
    from zephyr.trading.validation.runner import ValidationConfig, holdout_cutoff

    anchor = ValidationConfig().finalized_at
    if not anchor:
        raise ClosedBookConfigError(
            "ValidationConfig.finalized_at=None（12 个月滚动锁模式）——研究数据面闭卷切点不可派生，禁猜点放行"
        )
    try:
        anchor_dt = datetime.strptime(str(anchor)[:10], "%Y-%m-%d")
    except ValueError as exc:
        raise ClosedBookConfigError(f"finalized_at 非法（需 ISO date）: {anchor!r}") from exc
    return holdout_cutoff(anchor_dt, _holdout_months()).date()


def _to_date(value: date | datetime | str, *, name: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value[:10], "%Y-%m-%d").date()
        except ValueError as exc:
            raise ClosedBookConfigError(f"{name} 不可解析为日期: {value!r}") from exc
    raise ClosedBookConfigError(f"{name} 类型非法（需 date/datetime/ISO 串）: {type(value).__name__}")


def _now_iso() -> str:
    """显式时区时间戳（UTC，ISO8601）——RULE-SCHEMA-TZ：禁裸 now()/time.time()。"""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _append_audit(record: dict[str, Any], audit_path: Path) -> None:
    """CAS 追加一行审计（热文件纪律：读-改-写带 base sha + 写后核读）。"""
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, sort_keys=False)
    last_exc: Exception | None = None
    for attempt in range(10):
        text = safe_read(audit_path) if audit_path.exists() else ""
        import hashlib

        base_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        new_text = text + line + "\n"
        try:
            safe_write_text(audit_path, new_text, expected_base_sha256=base_sha, newline="\n")
            check = safe_read(audit_path)
            if not check.endswith(line + "\n"):  # pragma: no cover - 并发窗口兜底
                raise ClosedBookConfigError("闭卷考试审计写后核读不一致")
            return
        except Exception as exc:  # noqa: BLE001 — CAS 冲突重试（无 sleep：永久模块禁时间触发）
            last_exc = exc
            _logger.warning("闭卷审计 CAS 写第 %d 次冲突: %s", attempt + 1, exc)
    raise ClosedBookConfigError(f"闭卷考试审计写入失败（考试态不放行）: {last_exc}")


def enforce_closed_book_read(
    start: date | datetime | str,
    end: date | datetime | str,
    *,
    surface: str,
    exam_ticket: str | None = None,
    audit_path: Path | str | None = None,
    cutoff: date | None = None,
) -> ClosedBookDecision:
    """读取前闭卷判定（fail-closed）。

    Args:
        start/end: 请求窗端点（date/datetime/ISO 串）
        surface: 读口标识（审计用，如 "ch_tick_replay"）
        exam_ticket: 闭卷考试工单号；None/空白=研究态
        audit_path: 审计落点（默认 data/backtest_artifacts/closed_book_exam_audit.jsonl；测试注入 tmp_path）
        cutoff: 切点覆盖（仅供测试；生产禁传——派生真源唯一）

    Returns:
        ClosedBookDecision（考试态含 audit_path）。

    Raises:
        ClosedBookViolation: 研究态越切点，或考试态工单为空白。
        ClosedBookConfigError: 切点/窗参不可解析。
    """
    cut = cutoff or closed_book_cutoff()
    s = _to_date(start, name="start")
    e = _to_date(end, name="end")
    if s > e:
        raise ClosedBookConfigError(f"窗口非法 start={s} > end={e}")

    ticket = str(exam_ticket).strip() if exam_ticket is not None else ""
    if ticket and ticket != "0":
        mode = "closed_book_exam"
    elif exam_ticket is None:
        mode = "research"
    else:
        raise ClosedBookViolation(
            f"闭卷考试模式缺工单号（exam_ticket 空白）——无审计痕迹的考试=泄露口子，拒。"
            f"读口={surface} 窗=[{s}..{e}] 切点={cut}"
        )

    if mode == "research" and e > cut:
        raise ClosedBookViolation(
            f"FAIL: 读取窗终点 {e} 越闭卷切点 {cut}（读口={surface}）——禁闭卷数据入研究"
            "（17 号文 §三.5 HOLDOUT 纪律）。确属闭卷考试须显式传 exam_ticket=<工单号>，"
            "且本次读取会落审计痕迹。"
        )

    decision = ClosedBookDecision(surface=surface, cutoff=cut, start=s, end=e, mode=mode, exam_ticket=ticket or None)
    if mode == "closed_book_exam" and e > cut:
        path = Path(audit_path) if audit_path else DEFAULT_EXAM_AUDIT_PATH
        rec = {
            "recorded_at": _now_iso(),
            "surface": surface,
            "mode": mode,
            "exam_ticket": ticket,
            "cutoff": cut.isoformat(),
            "window": [s.isoformat(), e.isoformat()],
        }
        _append_audit(rec, path)
        decision = ClosedBookDecision(
            surface=surface,
            cutoff=cut,
            start=s,
            end=e,
            mode=mode,
            exam_ticket=ticket,
            audit_path=path.as_posix(),
        )
    return decision


__all__: Final = [
    "ClosedBookConfigError",
    "ClosedBookDecision",
    "ClosedBookViolation",
    "DEFAULT_EXAM_AUDIT_PATH",
    "closed_book_cutoff",
    "enforce_closed_book_read",
]
