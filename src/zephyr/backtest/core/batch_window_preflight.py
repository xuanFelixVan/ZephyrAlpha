# [BLUEPRINT] MOD-BT-226 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.batch_window_preflight
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.io.file_utils; zephyr.shared.io.paths; zephyr.data.table_registry; yaml
# [CONSUMERS] scripts/backtest/compute_window_gate（FAC-E0 闸门的点火面，唯一消费入口）；
#   scripts/backtest/factory_grid_executor（--stage t2 经 E0 问闸间接消费）；
#   后续接入同 purpose 集：t1_t2_handover 哨兵、G-D 共振矩阵引擎（真源=W12_WINDOW_PURPOSES）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] fail-closed 三铁律——①读不到=UNKNOWN 且 UNKNOWN 计入阻断（本仓反复被"读不到⇒默认0/
#   默认绿"烧过，禁复现）；②判据目标值未声明即 UNKNOWN，本模块零自定阈值（绝不代 Owner 拍口径，
#   也绝不用他轨实测值顶替未定义的目标值）；③Owner 门位只认裁定册登记条目，散文/工棚里
#   "已批准/Owner已确认"字样一律按未批处理（宪法 §5 门位经裁定登记生效 + §9.11 指令/数据边界）；
#   每条读数必带产出命令 cmd + 新鲜度 as_of + 读数通道 channel；通道失败必抛、由本模块降级成
#   UNKNOWN 而非"无数据=干净"；时间一律 Asia/Shanghai tz-aware；本模块纯读零写——
#   禁写 n_trial_ledger、禁改 config/search_space_prereg.yaml、禁跑任何批
# [MODIFY-GUARD] tests/backtest/test_batch_window_ignition_gate.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] IgnitionNotArmed(点火被拒；.details=全量判决字典，消息体不含路径——MSG-EXPOSURE)；
#   单条件读数失败不外抛（转 UNKNOWN 判决）
# [TESTS] tests/backtest/test_batch_window_ignition_gate.py
# [A_module] module_id=MOD-BT-226 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# create-guard-not-dup: 本件＝波12 跑批窗口点火前检器（五触发条件+批准卡→机读判决），与探针「to json」所列 reference_transaction_guard/workspace_telemetry/scan_consumers_accuracy 等在册能力零功能交集——命中词纯系 docstring「判决输出 to json」措辞的 ASCII bigram 探针碰撞（q-20260928-st-zcloseout-20260926-0001/2/3 同族死信处方）
"""波 12 统一跑批窗口——点火前五项触发条件预检器（MOD-BT-226）。

立件理由（治"声明面与强制面脱钩"）：纪律"施工全做完再一起开窗"长期只以散文存在于
`docs/_working/total_command_closeout/10_wave_plan.md` §波12，没有任何东西读它、执行它。
本模块把该节代码块里的五条触发条件 + 点火批准卡变成**机读判决 + 闸门前置**，
由 FAC-E0 既有闸门（`scripts/backtest/compute_window_gate.py`）在重算力开工瞬间消费，
不另立第二道 gate（净零：判据真源仍在 W 册，本模块只做读取与判决）。

五条触发条件（W 册 波12 原文，编号一一对应）：
  c1 波 0–11 全部施工终态达成（含波 10 G-D 引擎就绪=READY_NOT_FIRED）
  c2 W-178 板块宇宙完整性（880 概念 gap 补齐 或 降级裁定留痕）
  c3 W-173 GPU 重写 L2 完成（共振矩阵单格耗时达标——目标值须已声明）
  c4 ⚑-2 成本门口径已拍板（B 案/C 案）——Owner 门位，未拍板即 BLOCKED_AWAITING_GATE
  c5 W-64 T2 晋级池基落主区（t2_subspace 产物 + 哨兵件在 HEAD）

四态判决语义（关键设计——不存在"默认绿"）：
  GREEN                    读数成立且判据满足
  RED                      读数成立且判据不满足
  UNKNOWN                  读不到／目标值未声明／通道失败（=阻断，且必给 knowable_when）
  BLOCKED_AWAITING_GATE    Owner 门位未拍板（=阻断，AI 不得代裁）

用法:
    from zephyr.backtest.core.batch_window_preflight import run_preflight, to_json
    print(to_json(run_preflight()))            # 机读判决（五条 + 批准卡 + 阻断清单）
    assert_ignition_armed("wave12_t2_final")   # 不放行即抛 IgnitionNotArmed（点名阻断条件）

# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/batch_window_preflight.yaml
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Final
from zoneinfo import ZoneInfo

from zephyr.shared.io.file_utils import safe_read
from zephyr.shared.io.paths import REPO_ROOT

_TZ = ZoneInfo("Asia/Shanghai")

STATUS_GREEN = "GREEN"
STATUS_RED = "RED"
STATUS_UNKNOWN = "UNKNOWN"
STATUS_BLOCKED = "BLOCKED_AWAITING_GATE"
#: 非绿皆阻断——UNKNOWN 与 BLOCKED 一律不得被当成"没数据所以干净"
BLOCKING_STATUSES = frozenset({STATUS_RED, STATUS_UNKNOWN, STATUS_BLOCKED})

C1_CONSTRUCTION = "c1_waves_0_11_construction_terminal"
C2_SECTOR_UNIVERSE = "c2_sector_universe_complete"
C3_GPU_L2 = "c3_gpu_rewrite_l2_complete"
C4_COST_CALIBER = "c4_cost_gate_caliber_decided"
C5_T2_PROMOTION_POOL = "c5_t2_promotion_pool_base_landed"
W12_CONDITION_IDS: tuple[str, ...] = (
    C1_CONSTRUCTION,
    C2_SECTOR_UNIVERSE,
    C3_GPU_L2,
    C4_COST_CALIBER,
    C5_T2_PROMOTION_POOL,
)

#: 波 0–11 施工终态须覆盖的波次主号（1A/1B 是 W 册外部审查后插入的半波，9.5 归 9）
REQUIRED_WAVES: tuple[str, ...] = (
    "0",
    "1A",
    "1B",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
)

#: 波12 两案的立案日（c4 成本门口径 / c2 板块宇宙降级备选 均在此日之后才可能存在）
#: 出处：10_wave_plan.md §波12 ②④ 与 93_owner_menu.md「⚑-2 追加」批（2026-09-26 呈裁面成形）；
#: 早于此日的裁定不可能是对本两项的拍板——缺这一道，同名关键词（如做T 成本门）会造假绿。
W12_CASE_MIN_DATE = "2026-09-26"

APPROVAL_CARD_REL = "docs/_working/total_command_closeout/ignition/W12_WINDOW.yaml"
RULING_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"
PREREG_REL = "config/search_space_prereg.yaml"
LEDGER_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml"
#: 波12 窗口内批次统一走点火闸；未来件（G-D 共振引擎／t1_t2_handover 哨兵）接同一集合即可
W12_WINDOW_PURPOSES: frozenset[str] = frozenset(
    {
        "wave12_t2_final",  # 窗口 A：T2 终审 900 格（T1 幸存者选优）
        "wave12_resonance_first",  # 窗口 B：图形共振矩阵首批（G-D prereg 点火）
        "wave12_retired_reexam",  # 窗口 C：退役策略重考（W-119 同卷同纪）
        "wave12_onboarding_v1",  # 窗口 D：上岗规则 v1 激活（W-116 填 state_matrix）
    }
)

_WAVE_RE = re.compile(r"^波\s*(\d+[A-Za-z]?)")
_VERIFIED = "verified"

ConditionReader = Callable[["PreflightContext"], "ConditionReading"]


class IgnitionNotArmed(RuntimeError):
    """波 12 点火未就绪（fail-closed）。消息体只含条件号，路径等细节走 .details。"""

    def __init__(self, purpose: str, blocking: tuple[str, ...], details: dict[str, Any]) -> None:
        super().__init__(f"波12 点火被拒 purpose={purpose} 阻断项={','.join(blocking) or '(未列明)'}")
        self.purpose = purpose
        self.blocking = blocking
        self.details = details


@dataclass(frozen=True)
class ConditionReading:
    """单条触发条件的判决（含产出命令与新鲜度——无 cmd 的读数不得当证据用）。"""

    condition_id: str
    title_zh: str
    status: str
    cmd: str
    channel: str
    as_of: str
    evidence: str = ""
    blocking_when: str = ""
    unknown_reason: str = ""
    knowable_when: str = ""

    @property
    def blocking(self) -> bool:
        return self.status in BLOCKING_STATUSES

    def to_dict(self) -> dict[str, Any]:
        return {
            "condition_id": self.condition_id,
            "title_zh": self.title_zh,
            "status": self.status,
            "cmd": self.cmd,
            "channel": self.channel,
            "as_of": self.as_of,
            "evidence": self.evidence,
            "unknown_reason": self.unknown_reason,
            "knowable_when": self.knowable_when,
        }


@dataclass(frozen=True)
class ApprovalReading:
    """点火批准卡判决（一窗一卡；Owner 批一次管全窗，本卡是唯一合法停点工件）。"""

    exists: bool
    status: str
    cmd: str
    channel: str
    as_of: str
    approval_ref: str = ""
    approval_ref_registered: bool = False
    prereg_sha_matches: bool = False
    universe_sha_present: bool = False
    reasons: tuple[str, ...] = ()

    @property
    def blocking(self) -> bool:
        return not self._is_armed()

    def _is_armed(self) -> bool:
        return bool(
            self.exists
            and self.status == "APPROVED"
            and self.approval_ref_registered
            and self.prereg_sha_matches
            and self.universe_sha_present
            and not self.reasons
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "exists": self.exists,
            "status": self.status,
            "cmd": self.cmd,
            "channel": self.channel,
            "as_of": self.as_of,
            "approval_ref": self.approval_ref,
            "approval_ref_registered": self.approval_ref_registered,
            "prereg_sha_matches": self.prereg_sha_matches,
            "universe_sha_present": self.universe_sha_present,
            "reasons": list(self.reasons),
            "blocking": self.blocking,
        }


@dataclass
class PreflightContext:
    """预检执行上下文——所有外部通道均可注入替身（测试零触网零写盘）。

    Attributes:
        now: 判决时刻（tz-aware Asia/Shanghai；naive 拒收）。
        repo_root: 判据文件所在根（默认当前仓；主区/车道显式传入）。
        ch_execute: ClickHouse 只读通道，须"返回行元组 + 失败抛错"（禁 TSV 字符串通道）。
        governance_rows: governance 库 tasks 表只读通道（同样失败抛错）。
        git_probe: `git` 树面探测通道（grep/cat-file，失败抛错）。
    """

    now: datetime
    repo_root: Path
    ch_execute: Callable[[str], list[tuple]] | None = None
    governance_rows: Callable[[str], list[tuple]] | None = None
    git_probe: Callable[..., list[str]] | None = None
    main_root: Path | None = None

    def __post_init__(self) -> None:
        if self.now.tzinfo is None:
            raise ValueError("naive datetime 拒收（RULE-SCHEMA-TZ）：须带 Asia/Shanghai tzinfo")
        self.repo_root = Path(self.repo_root)

    def path(self, rel: str) -> Path:
        return self.repo_root / rel

    @property
    def as_of(self) -> str:
        return self.now.astimezone(_TZ).isoformat(timespec="seconds")


@dataclass(frozen=True)
class PreflightVerdict:
    """全窗判决（机读）。allowed=True 当且仅当五条全绿且批准卡生效。"""

    as_of: str
    conditions: tuple[ConditionReading, ...]
    approval: ApprovalReading
    allowed: bool
    blocking: tuple[str, ...]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "w12_batch_window_preflight/1",
            "as_of": self.as_of,
            "allowed": self.allowed,
            "blocking": list(self.blocking),
            "conditions": [c.to_dict() for c in self.conditions],
            "approval_card": self.approval.to_dict(),
            "notes": list(self.notes),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, sort_keys=False)

    def condition(self, condition_id: str) -> ConditionReading | None:
        return next((c for c in self.conditions if c.condition_id == condition_id), None)


def to_json(verdict: PreflightVerdict, indent: int = 2) -> str:
    """机读判决输出（供 CLI/台账消费，禁人肉转述代替）。"""
    return verdict.to_json(indent=indent)


def _worst(statuses: list[str]) -> str:
    """聚合优先级：UNKNOWN > BLOCKED_AWAITING_GATE > RED > GREEN（取最保守者）。"""
    if STATUS_UNKNOWN in statuses:
        return STATUS_UNKNOWN
    if STATUS_BLOCKED in statuses:
        return STATUS_BLOCKED
    if STATUS_RED in statuses:
        return STATUS_RED
    return STATUS_GREEN


def _fail_to_unknown(
    ctx: PreflightContext, cid: str, title: str, cmd: str, channel: str, exc: Exception, knowable_when: str
) -> ConditionReading:
    """通道失败 → UNKNOWN（带异常类名与原因，绝不静默当"无数据=干净"）。"""
    return ConditionReading(
        condition_id=cid,
        title_zh=title,
        status=STATUS_UNKNOWN,
        cmd=cmd,
        channel=channel,
        as_of=ctx.as_of,
        unknown_reason=f"读数通道失败 {type(exc).__name__}: {str(exc)[:180]}",
        knowable_when=knowable_when,
    )


# ---------------------------------------------------------------------------
# 共享读数小工具（纯读；异常一律外抛，由调用点降级成 UNKNOWN）
# ---------------------------------------------------------------------------


def load_yaml(path: Path) -> dict[str, Any]:
    """读 YAML（缺失/非法即抛，禁返回空字典冒充"没有条目"）。"""
    import yaml

    if not path.exists():
        raise FileNotFoundError("yaml 缺失")
    data = yaml.safe_load(safe_read(path))
    if not isinstance(data, dict):
        raise ValueError("yaml 顶层非 mapping")
    return data


def sha256_file(path: Path) -> str:
    """文件字节 sha256（批准卡与 prereg 冻结一致性用）。"""
    if not path.exists():
        raise FileNotFoundError("待摘要文件缺失")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ruling_entries(ctx: PreflightContext) -> list[dict[str, Any]]:
    data = load_yaml(ctx.path(RULING_REGISTRY_REL))
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("裁定册 entries 段缺失或为空——拒判已裁")
    return [e for e in entries if isinstance(e, dict)]


def _find_owner_ruling(
    ctx: PreflightContext, keyword_groups: tuple[tuple[str, ...], ...], min_date: str
) -> dict[str, Any] | None:
    """在裁定册里找一条**成对关键词全命中**且日期不早于立案日的已生效裁定。

    成对关键词（而非单词）是防伪绿设计：单关键词（如"成本门"）会被同名无关裁定命中，
    那正是假绿的标准形态。命中不到=None——由调用点落 UNKNOWN/BLOCKED，绝不落 GREEN。
    """
    for entry in _ruling_entries(ctx):
        status = str(entry.get("status") or "").lower()
        if status not in {"active", "decided"}:
            continue
        if str(entry.get("date") or "") < min_date:
            continue
        blob = " ".join(str(entry.get(k) or "") for k in ("title", "summary", "category"))
        if any(all(k in blob for k in group) for group in keyword_groups):
            return entry
    return None


# ---------------------------------------------------------------------------
# c1 波 0–11 施工终态（含波 10 G-D 引擎 READY_NOT_FIRED）
# ---------------------------------------------------------------------------

_SQL_WAVE_CARDS = "SELECT title, verification_status FROM tasks WHERE title LIKE '波%' LIMIT 2000"


def _wave_card_status(ctx: PreflightContext) -> ConditionReading:
    """波次交付卡读数（governance 库 tasks 表，波1A.1/1A.2 的机读真源）。

    判据：波 0–11 每波至少一张卡，且全部 verification_status=verified（COMPLETED 不算交付）。
    """
    cmd = "python -m zephyr.backtest.core.batch_window_preflight --reading c1a"
    channel = "DatabaseService.get_governance_conn(read_only=True) → tasks（失败抛）"
    if ctx.governance_rows is None:
        return ConditionReading(
            condition_id="c1a_wave_cards",
            title_zh="波次交付卡全 VERIFIED",
            status=STATUS_UNKNOWN,
            cmd=cmd,
            channel="未注入（默认通道不可用）",
            as_of=ctx.as_of,
            unknown_reason="governance 库句柄未注入（默认通道取 paths.DB_PATH，缺文件即抛）",
            knowable_when="governance 库在册（真库=主区 data/databases/governance.db）即出读数",
        )
    try:
        rows = ctx.governance_rows(_SQL_WAVE_CARDS)
    except Exception as exc:  # noqa: BLE001 - 通道失败 → UNKNOWN（禁默认绿）
        return _fail_to_unknown(
            ctx,
            "c1a_wave_cards",
            "波次交付卡全 VERIFIED",
            cmd,
            channel,
            exc,
            "恢复 governance 只读通道后复跑本读数",
        )
    by_wave: dict[str, list[str]] = {}
    for title, vstat in ((str(r[0]), str(r[1] or "").strip().lower()) for r in rows):
        m = _WAVE_RE.match(title)
        by_wave.setdefault(m.group(1) if m else "?", []).append(vstat)
    missing = [w for w in REQUIRED_WAVES if w not in by_wave]
    not_verified = sorted(f"{w}:{st}" for w, sts in by_wave.items() for st in sts if st != _VERIFIED)
    evidence = (
        f"波次卡 {sum(len(v) for v in by_wave.values())} 张，覆盖波次主号 {sorted(by_wave)}；"
        f"零 VERIFIED 项 {not_verified[:6]}{'…' if len(not_verified) > 6 else ''}"
    )
    status = STATUS_GREEN if (not missing and not not_verified) else STATUS_RED
    if not by_wave:
        status = STATUS_UNKNOWN
    return ConditionReading(
        condition_id="c1a_wave_cards",
        title_zh="波次交付卡全 VERIFIED",
        status=status,
        cmd=cmd,
        channel=channel,
        as_of=ctx.as_of,
        evidence=evidence,
        unknown_reason="" if by_wave else "tasks 表零波次卡——追踪面未建，不可判终态",
        knowable_when="按 W 册把波 0–11 各包建卡（W1A.1 通道）并逐张升 VERIFIED（W1A.2 三判据）",
    )


def _wave10_engine_status(ctx: PreflightContext) -> ConditionReading:
    """波 10 G-D 共振矩阵引擎 READY_NOT_FIRED 读数。

    READY = 引擎件在 HEAD 树可检索；NOT_FIRED = 其正式批次未进 n_trial_ledger。
    两者任一读不到/不成立即非绿（未 READY 的件谈不上"就绪未点火"）。
    """
    cmd = (
        "git grep -l --fixed-strings -e 共振矩阵 -e resonance_matrix HEAD -- "
        "'*.py' '*.yaml' '*.sql'  # 只认代码/配置在册，散文命中不算"
    )
    channel = "git 树面探测（subprocess，失败抛）+ trial_ledger_registry.yaml"
    if ctx.git_probe is None:
        return ConditionReading(
            condition_id="c1b_wave10_engine",
            title_zh="波10 G-D 引擎 READY_NOT_FIRED",
            status=STATUS_UNKNOWN,
            cmd=cmd,
            channel="未注入",
            as_of=ctx.as_of,
            unknown_reason="git 树面探测通道未注入",
            knowable_when="在 git 工作树内跑本预检（注入 git_probe）",
        )
    try:
        hits = ctx.git_probe(["共振矩阵", "resonance_matrix"])
    except Exception as exc:  # noqa: BLE001
        return _fail_to_unknown(
            ctx,
            "c1b_wave10_engine",
            "波10 G-D 引擎 READY_NOT_FIRED",
            cmd,
            channel,
            exc,
            "恢复 git 树面探测后复跑",
        )
    engine_in_head = bool(hits)
    fired = False
    fired_note = "账本读数不可得"
    try:
        ledger = load_yaml(ctx.path(LEDGER_REGISTRY_REL))
        ids = {str(r.get("batch_id")) for r in (ledger.get("batch_records") or []) if isinstance(r, dict)}
        fired = any("resonance" in i or "共振" in i for i in ids)
        fired_note = f"账本批次号 {len(ids)} 条，共振类命中={fired}"
    except Exception as exc:  # noqa: BLE001 - 账本不可读时 NOT_FIRED 不可证
        return _fail_to_unknown(
            ctx,
            "c1b_wave10_engine",
            "波10 G-D 引擎 READY_NOT_FIRED",
            cmd,
            channel,
            exc,
            "trial_ledger_registry.yaml 可读即出读数",
        )
    status = STATUS_GREEN if (engine_in_head and not fired) else STATUS_RED
    return ConditionReading(
        condition_id="c1b_wave10_engine",
        title_zh="波10 G-D 引擎 READY_NOT_FIRED",
        status=status,
        cmd=cmd,
        channel=channel,
        as_of=ctx.as_of,
        evidence=(f"引擎件在 HEAD: {len(hits)} 命中 {hits[:3]}；{fired_note}"),
        unknown_reason="",
        knowable_when="G-D 引擎落 HEAD（READY）且正式批次未入账本（NOT_FIRED）时转绿",
    )


def read_construction_terminal(ctx: PreflightContext) -> ConditionReading:
    """c1 = 波次卡全 VERIFIED 且 G-D 引擎 READY_NOT_FIRED（子读数聚合取最保守）。"""
    subs = [_wave_card_status(ctx), _wave10_engine_status(ctx)]
    return ConditionReading(
        condition_id=C1_CONSTRUCTION,
        title_zh="波 0–11 施工终态达成（含波10 G-D=READY_NOT_FIRED）",
        status=_worst([s.status for s in subs]),
        cmd=" && ".join(s.cmd for s in subs),
        channel=" | ".join(s.channel for s in subs),
        as_of=ctx.as_of,
        evidence=" ; ".join(f"[{s.condition_id}={s.status}] {s.evidence}" for s in subs),
        unknown_reason=" ; ".join(f"[{s.condition_id}] {s.unknown_reason}" for s in subs if s.unknown_reason),
        knowable_when=" ; ".join(f"[{s.condition_id}] {s.knowable_when}" for s in subs if s.knowable_when),
    )


# ---------------------------------------------------------------------------
# c2 W-178 板块宇宙完整性
# ---------------------------------------------------------------------------

_SQL_GAP = (
    "SELECT uniqExact(sector_code) FROM {roster} WHERE sector_code LIKE '880%' AND "
    "sector_code NOT IN (SELECT DISTINCT sector_code FROM {const} WHERE sector_code LIKE '880%')"
)
_SQL_ROSTER = "SELECT uniqExact(sector_code) FROM {roster} WHERE sector_code LIKE '880%'"
_SQL_COVERED = "SELECT uniqExact(sector_code) FROM {const} WHERE sector_code LIKE '880%'"

_CATEGORY_ROSTER = "market_sector_kline_880"
_CATEGORY_CONSTITUENT = "market_sector_constituent_880"
_C2_KEYWORDS = (("降级", "板块"), ("observational_only", "板块"), ("板块宇宙", "真源"))


def read_sector_universe(ctx: PreflightContext) -> ConditionReading:
    """c2 = 880 概念宇宙 gap 归零，或降级为观察轴的裁定在正式通道留痕。

    两套并存口径（concept_board 专表 vs sector_constituent 880 段）任一有 gap 即不绿——
    真源未裁之前，"另一套补齐"不构成完整性（W-178 明文须先裁真源）。
    """
    cmd = (
        "python -m zephyr.backtest.core.batch_window_preflight --reading c2 "
        f"# TableRegistry({_CATEGORY_ROSTER}|{_CATEGORY_CONSTITUENT}) + 裁定册关键词扫描"
    )
    channel = "DatabaseService.get_clickhouse_conn(role='reader').execute（行元组，失败抛）"
    try:
        ruling = _find_owner_ruling(ctx, _C2_KEYWORDS, W12_CASE_MIN_DATE)
    except Exception as exc:  # noqa: BLE001 - 裁定册读不到 ⇒ 降级留痕不可证
        return _fail_to_unknown(
            ctx,
            C2_SECTOR_UNIVERSE,
            "W-178 板块宇宙完整性",
            cmd,
            channel + " + 裁定册 YAML",
            exc,
            "ruling_registry.yaml 可读即判降级留痕半件",
        )
    if ruling is not None:
        return ConditionReading(
            condition_id=C2_SECTOR_UNIVERSE,
            title_zh="W-178 板块宇宙完整性",
            status=STATUS_GREEN,
            cmd=cmd,
            channel=channel + " + 裁定册 YAML",
            as_of=ctx.as_of,
            evidence=f"降级/真源裁定已留痕：{ruling.get('ruling_id')}（{ruling.get('date')}）",
        )
    if ctx.ch_execute is None:
        return ConditionReading(
            condition_id=C2_SECTOR_UNIVERSE,
            title_zh="W-178 板块宇宙完整性",
            status=STATUS_UNKNOWN,
            cmd=cmd,
            channel="未注入",
            as_of=ctx.as_of,
            unknown_reason="CH 只读通道未注入（车道外无库面）",
            knowable_when="注入会抛错的 reader（禁 TSV 下标通道）后复跑",
        )
    try:
        from zephyr.data.table_registry import get_registry

        reg = get_registry()
        roster = reg.table(_CATEGORY_ROSTER)
        const = reg.table(_CATEGORY_CONSTITUENT)
        n_roster = int(ctx.ch_execute(_SQL_ROSTER.format(roster=roster))[0][0])
        n_covered = int(ctx.ch_execute(_SQL_COVERED.format(const=const))[0][0])
        n_gap = int(ctx.ch_execute(_SQL_GAP.format(roster=roster, const=const))[0][0])
    except Exception as exc:  # noqa: BLE001
        return _fail_to_unknown(
            ctx,
            C2_SECTOR_UNIVERSE,
            "W-178 板块宇宙完整性",
            cmd,
            channel,
            exc,
            "CH 服务在线 + 品类号在 TableRegistry 在册即出读数",
        )
    evidence = (
        f"880 名册={n_roster} 有成分={n_covered} gap={n_gap}"
        f"（名册口径={roster}，成分口径={const}；两套并存口径未裁真源）"
    )
    status = STATUS_GREEN if n_gap == 0 and n_roster > 0 else STATUS_RED
    return ConditionReading(
        condition_id=C2_SECTOR_UNIVERSE,
        title_zh="W-178 板块宇宙完整性",
        status=status,
        cmd=cmd,
        channel=channel,
        as_of=ctx.as_of,
        evidence=evidence,
        unknown_reason="",
        knowable_when="gap 归零（补齐采集）或降级观察轴裁定登记进 ruling_registry（二者其一即转绿）",
    )


# ---------------------------------------------------------------------------
# c3 W-173 GPU 重写 L2（共振矩阵单格耗时达标）
# ---------------------------------------------------------------------------

_TARGET_KEY = "resonance_per_cell_seconds_target"
_MEASURED_KEY = "resonance_per_cell_seconds_measured"


def read_gpu_l2(ctx: PreflightContext) -> ConditionReading:
    """c3 = 共振矩阵单格耗时 **对已声明目标值** 达标。

    目标值按 W 册归波12 prereg 声明；未声明即 UNKNOWN——本模块零自定阈值，
    且明确禁用他轨读数（grid T0 的 per_point_seconds_measured）顶替：口径不同，
    拿来凑绿就是把判据改成能过的样子。
    """
    cmd = f"python -m zephyr.backtest.core.batch_window_preflight --reading c3  # 读 {PREREG_REL}"
    channel = "config/search_space_prereg.yaml（只读，禁改）"
    try:
        cfg = load_yaml(ctx.path(PREREG_REL))
    except Exception as exc:  # noqa: BLE001
        return _fail_to_unknown(
            ctx,
            C3_GPU_L2,
            "W-173 GPU 重写 L2 达标",
            cmd,
            channel,
            exc,
            "prereg 可读即出读数",
        )
    caps = cfg.get("budget_caps") or {}
    if not isinstance(caps, dict):
        caps = {}
    target = caps.get(_TARGET_KEY)
    measured = caps.get(_MEASURED_KEY)
    other = caps.get("per_point_seconds_measured")
    note_other = (
        (f"（他轨 grid T0 实测 per_point_seconds_measured={other} 不可替代：口径=组合层网格单格，非共振矩阵单格）")
        if other is not None
        else ""
    )
    if target is None:
        return ConditionReading(
            condition_id=C3_GPU_L2,
            title_zh="W-173 GPU 重写 L2 达标",
            status=STATUS_UNKNOWN,
            cmd=cmd,
            channel=channel,
            as_of=ctx.as_of,
            evidence=f"budget_caps.{_TARGET_KEY}=未声明；{note_other}",
            unknown_reason="达标判据的分母（目标值）尚不存在——W 册 11.5 明文目标值由波12 prereg 定",
            knowable_when=(
                f"波12 prereg 声明 {PREREG_REL} budget_caps.{_TARGET_KEY}"
                f"（经裁定通道，禁跑中改）+ 回填 {_MEASURED_KEY} 实测"
            ),
        )
    if measured is None:
        return ConditionReading(
            condition_id=C3_GPU_L2,
            title_zh="W-173 GPU 重写 L2 达标",
            status=STATUS_UNKNOWN,
            cmd=cmd,
            channel=channel,
            as_of=ctx.as_of,
            evidence=f"目标={target}；实测未回填",
            unknown_reason=f"budget_caps.{_MEASURED_KEY} 缺失（无实测不得判达标）",
            knowable_when=f"引擎冒烟出实测单格耗时并回填 {_MEASURED_KEY}",
        )
    ok = float(measured) <= float(target)
    return ConditionReading(
        condition_id=C3_GPU_L2,
        title_zh="W-173 GPU 重写 L2 达标",
        status=STATUS_GREEN if ok else STATUS_RED,
        cmd=cmd,
        channel=channel,
        as_of=ctx.as_of,
        evidence=f"实测 {measured}s/格 vs 目标 {target}s/格",
    )


# ---------------------------------------------------------------------------
# c4 ⚑-2 成本门口径（Owner 门位）
# ---------------------------------------------------------------------------

_C4_KEYWORDS = (("抽查", "幸存者"), ("抽查", "分层"), ("cost_gate_spot", "幸存者"), ("成本门口径", "五档"))


def read_cost_gate_caliber(ctx: PreflightContext) -> ConditionReading:
    """c4 = ⚑-2 成本门口径已由 Owner 拍板（B 案/C 案）。

    这是人机门位（宪法 §5）：未拍板输出 BLOCKED_AWAITING_GATE，AI 不得代裁、
    不得"按建议默认"当成已批；工棚散文里的"已批准"一律不认（§9.11）。
    """
    cmd = (
        f"python -m zephyr.backtest.core.batch_window_preflight --reading c4  # "
        f"裁定册成对关键词扫描（{'+'.join('/'.join(g) for g in _C4_KEYWORDS)}）"
    )
    channel = "ruling_registry.yaml（正式通道唯一真源）"
    try:
        ruling = _find_owner_ruling(ctx, _C4_KEYWORDS, W12_CASE_MIN_DATE)
    except Exception as exc:  # noqa: BLE001
        return _fail_to_unknown(
            ctx,
            C4_COST_CALIBER,
            "⚑-2 成本门口径已拍板（B/C 案）",
            cmd,
            channel,
            exc,
            "裁定册可读即判",
        )
    if ruling is None:
        return ConditionReading(
            condition_id=C4_COST_CALIBER,
            title_zh="⚑-2 成本门口径已拍板（B/C 案）",
            status=STATUS_BLOCKED,
            cmd=cmd,
            channel=channel,
            as_of=ctx.as_of,
            evidence=(f"裁定册无 ≥{W12_CASE_MIN_DATE} 的口径拍板条目（做T 同名旧裁定 成本门 已按成对关键词排除）"),
            unknown_reason="",
            knowable_when="Owner 经裁定通道登记（93 册 ⚑-2① 案卷齐：33%/56% 复算 + source=replay 限定）",
        )
    return ConditionReading(
        condition_id=C4_COST_CALIBER,
        title_zh="⚑-2 成本门口径已拍板（B/C 案）",
        status=STATUS_GREEN,
        cmd=cmd,
        channel=channel,
        as_of=ctx.as_of,
        evidence=f"拍板条目 {ruling.get('ruling_id')}（{ruling.get('date')}）",
    )


# ---------------------------------------------------------------------------
# c5 W-64 T2 晋级池基落主区
# ---------------------------------------------------------------------------

_SUBSPACE_GLOB = "data/strategy_intake/grid_*/t2_subspace.json"
_SENTINEL_REL = "scripts/backtest/t1_t2_handover.py"


def read_t2_promotion_pool(ctx: PreflightContext) -> ConditionReading:
    """c5 = T2 晋级池基（t2_subspace 产物 + 构造它的哨兵件）落在**主区**且哨兵在 HEAD。

    判"落主区"用主区根（worktree 的 git common dir 上级），车道产物不算交付——
    本仓已多次发生"工棚做完=以为入库"。主区不可定位时落 UNKNOWN，不判绿也不判红。
    """
    cmd = f"ls <主区>/{_SUBSPACE_GLOB} && git -C <主区> cat-file -e HEAD:{_SENTINEL_REL}"
    channel = "文件系统只读 + git 对象库（失败抛）"
    if ctx.main_root is None:
        return ConditionReading(
            condition_id=C5_T2_PROMOTION_POOL,
            title_zh="W-64 T2 晋级池基落主区",
            status=STATUS_UNKNOWN,
            cmd=cmd,
            channel=channel,
            as_of=ctx.as_of,
            unknown_reason="主区根不可定位（无法区分车道产物与入库件）",
            knowable_when="在主区或可解析 git common dir 的工作树内跑本预检",
        )
    try:
        subspace = sorted(Path(ctx.main_root).glob(_SUBSPACE_GLOB))
        sentinel_hits = ctx.git_probe(["--cat-file-e", _SENTINEL_REL]) if ctx.git_probe else None
    except Exception as exc:  # noqa: BLE001
        return _fail_to_unknown(
            ctx,
            C5_T2_PROMOTION_POOL,
            "W-64 T2 晋级池基落主区",
            cmd,
            channel,
            exc,
            "git 对象库可读即判哨兵入库态",
        )
    if sentinel_hits is None:
        return ConditionReading(
            condition_id=C5_T2_PROMOTION_POOL,
            title_zh="W-64 T2 晋级池基落主区",
            status=STATUS_UNKNOWN,
            cmd=cmd,
            channel=channel,
            as_of=ctx.as_of,
            unknown_reason="git 树面通道未注入（哨兵入库态不可判）",
            knowable_when="注入 git_probe 后复跑",
        )
    evidence = (
        f"t2_subspace.json 命中 {len(subspace)} 件 {[p.parent.name for p in subspace][:3]}；"
        f"哨兵在 HEAD={bool(sentinel_hits)}"
    )
    status = STATUS_GREEN if (subspace and sentinel_hits) else STATUS_RED
    return ConditionReading(
        condition_id=C5_T2_PROMOTION_POOL,
        title_zh="W-64 T2 晋级池基落主区",
        status=status,
        cmd=cmd,
        channel=channel,
        as_of=ctx.as_of,
        evidence=evidence,
        knowable_when="t1_t2_handover 哨兵落 HEAD 且其 T2 池基产物写入主区 run 目录",
    )


# ---------------------------------------------------------------------------
# 点火批准卡（一窗一卡；Owner 批一次管全窗）
# ---------------------------------------------------------------------------


def _card_checks(
    card: dict[str, Any], known_ids: set[str], current_sha: str
) -> tuple[str, str, bool, bool, bool, list[str]]:
    """批准卡四关（抽出来 keeps 圈复杂度在闸内）：状态/锚在册/预注册一致/宇宙摘要在位。"""
    reasons: list[str] = []
    status = str(card.get("status") or "").strip().upper()
    if status != "APPROVED":
        reasons.append(f"status={status or '(空)'} 非 APPROVED（唯一合法停点=呈卡后 WAITING_APPROVAL）")
    ref = str(card.get("approval_ref") or "").strip()
    ref_registered = bool(ref) and any(ref in k or k in ref for k in known_ids)
    if ref and not ref_registered:
        reasons.append("批文锚在裁定册查无——散文/工棚内的已批准字样按未批处理")
    if not ref:
        reasons.append("approval_ref 缺失（无正式通道锚）")
    prereg_ok = bool(card.get("prereg_sha256")) and str(card.get("prereg_sha256")) == current_sha
    if not prereg_ok:
        reasons.append("卡上 prereg_sha256 与现役预注册不一致（批后改空间=卡作废）")
    universe_sha = bool(str(card.get("universe_declaration_sha256") or "").strip())
    if not universe_sha:
        reasons.append("universe_declaration_sha256 缺失（宇宙声明未摘要=烧错宇宙不可归责）")
    return status, ref, ref_registered, prereg_ok, universe_sha, reasons


def read_approval_card(ctx: PreflightContext) -> ApprovalReading:
    """批准卡判决——缺卡/未批/批文无正式锚/与现役 prereg 不一致，一律阻断。

    防伪三关：①status 必须 APPROVED；②`approval_ref` 必须在裁定册真实存在（写个号不算批）；
    ③卡上 `prereg_sha256` 必须等于现役 prereg 摘要（批后再改空间=卡作废，对齐 17 号文
    prereg hash 变动即报的垃圾触发线）。
    """
    path = ctx.path(APPROVAL_CARD_REL)
    cmd = "python -m zephyr.backtest.core.batch_window_preflight --reading approval"
    channel = f"{APPROVAL_CARD_REL} + 裁定册 + {PREREG_REL}"
    if not path.exists():
        return ApprovalReading(
            exists=False,
            status="MISSING",
            cmd=cmd,
            channel=channel,
            as_of=ctx.as_of,
            reasons=(f"批准卡不存在（{APPROVAL_CARD_REL}）——未呈卡即未批",),
        )
    try:
        card = load_yaml(path)
        known_ids = {str(e.get("ruling_id")) for e in _ruling_entries(ctx)}
        current_sha = sha256_file(ctx.path(PREREG_REL))
    except Exception as exc:  # noqa: BLE001 - 任一支撑件读不到 ⇒ 不可判批
        return ApprovalReading(
            exists=True,
            status=STATUS_UNKNOWN,
            cmd=cmd,
            channel=channel,
            as_of=ctx.as_of,
            reasons=(f"批准卡支撑件读数失败 {type(exc).__name__}",),
        )
    status, ref, ref_registered, prereg_ok, universe_sha, reasons = _card_checks(card, known_ids, current_sha)
    return ApprovalReading(
        exists=True,
        status=status or "MISSING",
        cmd=cmd,
        channel=channel,
        as_of=ctx.as_of,
        approval_ref=ref,
        approval_ref_registered=ref_registered,
        prereg_sha_matches=prereg_ok,
        universe_sha_present=universe_sha,
        reasons=tuple(reasons),
    )


DEFAULT_READERS: dict[str, ConditionReader] = {
    C1_CONSTRUCTION: read_construction_terminal,
    C2_SECTOR_UNIVERSE: read_sector_universe,
    C3_GPU_L2: read_gpu_l2,
    C4_COST_CALIBER: read_cost_gate_caliber,
    C5_T2_PROMOTION_POOL: read_t2_promotion_pool,
}


# ---------------------------------------------------------------------------
# 默认外部通道（真环境）
# ---------------------------------------------------------------------------


def default_ch_execute(sql: str) -> list[tuple]:
    """ClickHouse 只读通道——行元组 + 失败抛（禁 TSV 字符串通道，W-180.1 病根）。"""
    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_clickhouse_conn(role="reader")
    return list(conn.execute(sql))


def default_governance_rows(sql: str) -> list[tuple]:
    """governance 库只读通道（句柄缺失即抛，禁"查不到=零卡"）。"""
    from zephyr.shared.io.paths import DB_PATH

    if not Path(str(DB_PATH)).exists():
        raise FileNotFoundError("governance 库不在本树（车道常态，须主区跑）")
    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_governance_conn(read_only=True)
    cur = conn.cursor()
    cur.execute(sql)
    return [tuple(r) for r in cur.fetchall()]


def make_default_git_probe(repo_root: Path) -> Callable[[list[str]], list[str]]:
    """构造 git 树面探测函数：`git grep -l <term> HEAD`；`--cat-file-e <path>` 判入库。"""

    def _probe(argv: list[str], globs: tuple[str, ...] = ()) -> list[str]:
        if argv and argv[0] == "--cat-file-e":
            args = ["git", "-C", str(repo_root), "cat-file", "-e", f"HEAD:{argv[1]}"]
            rc = subprocess.run(args, capture_output=True, text=True, timeout=60).returncode
            return ["in-HEAD"] if rc == 0 else []
        terms = [t for t in argv if not t.startswith("--")]
        if not terms:
            raise ValueError("git 树面探测缺检索词")
        args = ["git", "-C", str(repo_root), "grep", "-l", "--fixed-strings"]
        for t in terms:
            args += ["-e", t]
        args += ["HEAD", "--"]
        args += list(globs) or ["*.py", "*.yaml", "*.sql"]  # 缺省剔散文：文档命中≠代码在册
        proc = subprocess.run(args, capture_output=True, text=True, timeout=120)
        if proc.returncode not in (0, 1):  # 1=零命中（合法空），其余=通道失败必抛
            raise RuntimeError(f"git grep 失败 rc={proc.returncode} {proc.stderr[:120]}")
        return [ln.split(":", 1)[-1] for ln in proc.stdout.splitlines() if ln.strip()]

    return _probe


def resolve_main_root(repo_root: Path) -> Path | None:
    """由 git common dir 反推主区根（车道内也能定位主区，判"落主区"用）。"""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            return None
        common = Path(proc.stdout.strip())
        return common.parent if common.name == ".git" else None
    except Exception:  # noqa: BLE001 - 定位失败即 None（上层落 UNKNOWN）
        return None


def build_context(now: datetime | None = None, repo_root: Path | None = None) -> PreflightContext:
    """默认真实上下文（全通道失败即抛，由读数器降级 UNKNOWN；本函数不写任何盘）。"""
    root = Path(repo_root) if repo_root else REPO_ROOT
    ctx = PreflightContext(
        now=now or datetime.now(_TZ),
        repo_root=root,
        ch_execute=default_ch_execute,
        governance_rows=default_governance_rows,
        git_probe=make_default_git_probe(root),
        main_root=resolve_main_root(root),
    )
    return ctx


# ---------------------------------------------------------------------------
# 判决组装
# ---------------------------------------------------------------------------


def run_preflight(
    ctx: PreflightContext | None = None,
    readers: dict[str, ConditionReader] | None = None,
    approval: ApprovalReading | None = None,
) -> PreflightVerdict:
    """跑五项触发条件 + 批准卡 → 机读判决（不抛：读数各自已降级为 UNKNOWN）。"""
    ctx = ctx or build_context()
    active = dict(DEFAULT_READERS)
    if readers:
        active.update(readers)
    readings = tuple(active[cid](ctx) for cid in W12_CONDITION_IDS if cid in active)
    missing_ids = [cid for cid in W12_CONDITION_IDS if cid not in active]
    approval = approval if approval is not None else read_approval_card(ctx)
    blocking: list[str] = [c.condition_id for c in readings if c.blocking]
    blocking += missing_ids
    if approval.blocking:
        blocking.append("approval_card")
    notes = [f"未注册读数器: {m}" for m in missing_ids]
    return PreflightVerdict(
        as_of=ctx.as_of,
        conditions=readings,
        approval=approval,
        allowed=not blocking,
        blocking=tuple(blocking),
        notes=tuple(notes),
    )


def blocking_detail(verdict: PreflightVerdict) -> str:
    """点名阻断条件（供闸门口令输出，"到底哪条挡着"必须一眼可见）。"""
    parts: list[str] = []
    for c in verdict.conditions:
        if c.blocking:
            parts.append(
                f"{c.condition_id}={c.status}（{c.title_zh}）" + (f" 因:{c.unknown_reason}" if c.unknown_reason else "")
            )
    if verdict.approval.blocking:
        parts.append("approval_card=" + "|".join(verdict.approval.reasons or ("未批或卡缺失",)))
    return " ;; ".join(parts) or "无阻断（全绿且批准卡生效）"


def assert_ignition_armed(
    purpose: str, ctx: PreflightContext | None = None, verdict: PreflightVerdict | None = None
) -> PreflightVerdict:
    """点火断言——不放行即抛 IgnitionNotArmed（携带全量判决供审计落盘）。"""
    v = verdict if verdict is not None else run_preflight(ctx)
    if not v.allowed:
        raise IgnitionNotArmed(purpose, v.blocking, v.to_dict())
    return v


__all__: Final = [
    "ApprovalReading",
    "ConditionReading",
    "IgnitionNotArmed",
    "PreflightContext",
    "PreflightVerdict",
    "W12_CONDITION_IDS",
    "W12_WINDOW_PURPOSES",
    "assert_ignition_armed",
    "blocking_detail",
    "build_context",
    "read_approval_card",
    "run_preflight",
    "to_json",
]
