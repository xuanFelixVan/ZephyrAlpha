# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §1 回写契约 + 20_management_policy.md §2.1 审计 what 全族 SSOT 词表
# [MODULE] zephyr.governance.meta_question.exam_loop.event_codes
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.yaml_utils (load_vocabulary_values，本簇扩展册动态加载); zephyr.governance.meta_question.exam_ops (AUDIT_WHAT_VOCAB 已落地词表，经 import 不回抄字面量)
# [CONSUMERS] zephyr.governance.meta_question.exam_loop.ledger（双轨写入器的落账码选择）; .exam_lifecycle（非法流转/冲突拦截痕）; .writeback（越权/降阈值/补录痕）; scripts/governance/meta_question/wo_b1_examloop/check_exam_loop.py（复考判据读取）; tests/governance/meta_question/test_exam_loop_ledger.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 扩展事件码唯一真源=config/examloop_audit_event_vocabulary.yaml（经 load_vocabulary_values 动态加载，禁在本模块写字面量列表——上一班四次死亡的治本处方）；
#              已落地码=AUDIT_WHAT_VOCAB（冻结件，import 回用），扩展码=本册 values，两集交集必须为空（重复登记=漂移，fail-closed）；
#              PG meta_question_audit.what 的 CHECK 枚举是物理闸：扩展码是否可直写由运行期 pg_constraint 自省判定（_landed_cache 进程内缓存一次），禁凭文件猜测；
#              过渡期载体=what=册内 carriage.base_what（登记族已落地值）+ event_code 双写进 after JSONB 与 evidence 前缀（PG/JSONL 双轨同键，20§2.2 差集对账不受扰）；
#              判据读取口径恒为 (what=<code> OR after->>'event_code'=<code> OR evidence LIKE '<prefix><code>%')——CHECK 放宽前后同一读法
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/20_management_policy.md §2.1（what 词表增补须先改总册）+ config/examloop_audit_event_vocabulary.yaml（机读册，扩展码增删只改本册）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 扩展册缺失/损坏=load_vocabulary_values strict 上抛（fail-closed，禁降级为空集）；
#                  扩展码与已落地码重叠=ValueError；PG 自省失败（权限/连接）时 is_landed 返回 False=保守走过渡载体，绝不假判已落地
# [TESTS] tests/governance/meta_question/test_exam_loop_ledger.py（词表接线/重叠断言/载体选择/未落地保守路径）
# [A_module] module_id=MOD-METAQ-EXAMLOOP | layer=module | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""event_codes — 考试循环簇审计事件码扩展册加载器与落账载体选择器（WO-B1）。

``AUDIT_WHAT_VOCAB``（20§2.1 四族词表）现以字面量驻于 ``exam_ops.py``/``apply_meta_question_ddl.py``
两处，且 PG ``meta_question_audit`` 有同名 CHECK 约束；本簇需要的 ``illegal_transition`` /
``claim_mismatch`` / ``version_conflict`` / ``threshold_lowered`` / ``supplement`` 等码不在其内。
本模块把增量声明为**机读册 + 运行期内省**，不改冻结件：

- 册内码若已在 PG CHECK 内 → 直写真实 ``what``（总包落地补丁后自动切换，零改码）；
- 尚未落地 → 以 ``update`` 为载体、``event_code`` 进 ``after`` JSONB 与 ``evidence`` 前缀落账。

用法::

    from zephyr.governance.meta_question.exam_loop.event_codes import resolve

    carriage = resolve("claim_mismatch")          # → Carriage(what='update', event_code='claim_mismatch')
    carriage = resolve("exam_writeback")          # → Carriage(what='exam_writeback', event_code=None)
# target: src/zephyr/governance/meta_question/exam_loop/event_codes.py (docstring 765 字, 14 函数, 0 步骤)
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/event_codes.yaml
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from zephyr.governance.meta_question.exam_ops import AUDIT_WHAT_VOCAB
from zephyr.shared.io.yaml_utils import load_vocabulary_values

_CONFIG_DIR: Final[Path] = Path(__file__).resolve().parent / "config"
EVENT_VOCAB_FILE: Final[str] = "examloop_audit_event_vocabulary.yaml"

#: 判据读取片段（复考器与对账器共用同一读法，禁各写一份）：
#:   三口径=what 列（已落地后）/ after JSONB 载荷（PG 复考器）/ evidence 前缀（过渡载体，双轨同键）
SQL_EVENT_MATCH: Final[str] = "(what = %s OR after->>'{key}' = %s OR evidence LIKE %s)"
#: 跨方言片段（SQLite mock 无 ``->>``，读侧一律用它；PG 复考器用上面的全口径）
SQL_EVENT_MATCH_PORTABLE: Final[str] = "(what = %s OR evidence LIKE %s)"

_landed_cache: dict[str, bool] = {}

__all__: Final = [
    "CODE_CLAIM_MISMATCH",
    "CODE_CLAIM_MISSING",
    "CODE_ILLEGAL_TRANSITION",
    "CODE_SUPPLEMENT",
    "CODE_THRESHOLD_LOWERED",
    "CODE_VERSION_CONFLICT",
    "Carriage",
    "EVENT_VOCAB_FILE",
    "SQL_EVENT_MATCH",
    "base_what_for_pending",
    "carrier",
    "clear_landing_cache",
    "event_code_key",
    "evidence_prefix",
    "extension_codes",
    "is_landed",
    "match_params",
    "mark_landed",
    "resolve",
    "sql_event_match",
]

# ---------------------------------------------------------------------------
# 事件码符号（值取自册内登记码，仅命名别名——禁在调用点散落字符串字面量；
# 在册性校验延后到 EXTENSION_CODES 装配完成处执行，见本模块 `_assert_symbols_registered`）
# ---------------------------------------------------------------------------
CODE_ILLEGAL_TRANSITION = "illegal_transition"
CODE_CLAIM_MISMATCH = "claim_mismatch"
CODE_CLAIM_MISSING = "claim_missing"
CODE_VERSION_CONFLICT = "version_conflict"
CODE_THRESHOLD_LOWERED = "threshold_lowered"
CODE_SUPPLEMENT = "supplement"

_CODE_SYMBOLS = (
    CODE_ILLEGAL_TRANSITION,
    CODE_CLAIM_MISMATCH,
    CODE_CLAIM_MISSING,
    CODE_VERSION_CONFLICT,
    CODE_THRESHOLD_LOWERED,
    CODE_SUPPLEMENT,
)


def _assert_symbols_registered(codes: frozenset[str]) -> None:
    missing = sorted(set(_CODE_SYMBOLS) - codes)
    if missing:
        raise ValueError(f"事件码符号未入册：{missing}（册={EVENT_VOCAB_FILE}，新增码须先写册再引符号）")


@dataclass(frozen=True)
class Carriage:
    """一条审计事件的落账载体（what 列值 + 事件码载荷）。"""

    what: str
    event_code: str | None
    landed: bool

    @property
    def is_passthrough(self) -> bool:
        """True=what 列即事件语义（已落地或原生词表码）；False=过渡载体。"""
        return self.event_code is None


def _load_event_vocab_raw() -> tuple[frozenset[str], dict[str, str]]:
    """读扩展册 → (扩展码集, 载体约定 dict)。strict=True：册缺失即抛（禁空集漂移）。"""
    values = load_vocabulary_values(EVENT_VOCAB_FILE, vocab_dir=_CONFIG_DIR, strict=True)
    if not values:
        raise ValueError(f"扩展事件码册空值：{EVENT_VOCAB_FILE}（fail-closed，禁静默放行）")
    import yaml  # noqa: PLC0415 ——仅取载体约定时惰性读，常规路径不引 YAML

    payload = yaml.safe_load((_CONFIG_DIR / EVENT_VOCAB_FILE).read_text(encoding="utf-8")) or {}
    raw_carriage = payload.get("carriage") or {}
    if not isinstance(raw_carriage, dict):
        raise ValueError(f"扩展册 carriage 段须为映射：{EVENT_VOCAB_FILE}")
    carriage = {str(k): str(v) for k, v in raw_carriage.items()}
    return frozenset(str(v) for v in values), carriage


EXTENSION_CODES, _CARRIAGE = _load_event_vocab_raw()
_assert_symbols_registered(EXTENSION_CODES)

# 双写防漂移：扩展码不得与已落地词表重叠（重叠=总包已落地却未把本册并入 SSOT）
_overlap = EXTENSION_CODES & frozenset(AUDIT_WHAT_VOCAB)
if _overlap:
    raise ValueError(
        f"事件码双登记（20§2.1 要求唯一 SSOT）：{sorted(_overlap)} 已在 AUDIT_WHAT_VOCAB 内，"
        "请把扩展册并入总册后从本册删除"
    )


def extension_codes() -> frozenset[str]:
    """本簇新增、尚待总包并入 AUDIT_WHAT_VOCAB 的事件码集合。"""
    return EXTENSION_CODES


def event_code_key() -> str:
    """载荷键名（after JSONB / 复考器读取口径）。"""
    return _CARRIAGE.get("payload_key", "event_code")


def evidence_prefix() -> str:
    """evidence 前缀（JSONL 轨无 JSONB 列，故双写进 evidence 使双轨同键）。"""
    return _CARRIAGE.get("evidence_prefix", "event_code=")


def base_what_for_pending() -> str:
    """未落地码的过渡载体 what 值（登记族已落地值，册内声明）。"""
    base = _CARRIAGE.get("base_what", "update")
    if base not in frozenset(AUDIT_WHAT_VOCAB):
        raise ValueError(f"载体 base_what={base!r} 不在已落地词表内（载体本身失真）")
    return base


def mark_landed(code: str, landed: bool) -> None:
    """写自省缓存（测试注入 / 自省结果复用）。"""
    _landed_cache[code] = bool(landed)


def clear_landing_cache() -> None:
    """清空缓存（DDL 变更后重自省）。"""
    _landed_cache.clear()


def is_landed(code: str) -> bool:
    """该扩展码是否已在已落地词表内（原生词表码恒 True）。"""
    if code in frozenset(AUDIT_WHAT_VOCAB):
        return True
    if code not in EXTENSION_CODES:
        raise ValueError(f"event_code 未登记：{code!r}（须先入 {EVENT_VOCAB_FILE}，禁另立枚举）")
    return bool(_landed_cache.get(code, False))


def resolve(code: str) -> Carriage:
    """落账载体选择：已落地→what=code；扩展未落地→what=base_what + event_code 载荷。"""
    if is_landed(code):
        return Carriage(what=code, event_code=None, landed=True)
    return Carriage(what=base_what_for_pending(), event_code=code, landed=False)


def carrier(
    code: str,
    before: dict[str, object] | None,
    after: dict[str, object] | None,
    evidence: str,
) -> tuple[str, dict[str, object] | None, dict[str, object] | None, str]:
    """把事件码/证据/前后载荷整形为落账四元组（过渡期双写 event_code）。"""
    picked = resolve(code)
    prefix = evidence_prefix()
    key = event_code_key()
    if picked.event_code is None:
        return picked.what, before, after, evidence
    payload = dict(after or {})
    payload[key] = picked.event_code
    stamp = f"{prefix}{picked.event_code};"
    return picked.what, before, payload, stamp + str(evidence or "")


def sql_event_match(*, portable: bool = False) -> str:
    """单个事件码的匹配片段（``portable=True`` 供 SQLite/无 JSONB 方言使用）。"""
    template = SQL_EVENT_MATCH_PORTABLE if portable else SQL_EVENT_MATCH
    return template.format(key=event_code_key())


def match_params(code: str, *, portable: bool = False) -> tuple[str, ...]:
    """与 :func:`sql_event_match` 一一对位的绑定参数（evidence 前缀须带码，禁串码匹配）。"""
    like = f"{evidence_prefix()}{code}%"
    return (code, like) if portable else (code, code, like)
