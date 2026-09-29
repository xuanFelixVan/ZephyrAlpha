# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_ai_exposure
# [MODULE] zephyr.ai_layer.redline.ai_secret_exposure
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.redline.negative_list (DENY_ENV_PATTERNS 基线，SSOT 引用不复制);
#                zephyr.ai_layer.redline.session_env_guard (S1 筛查正门，deny_patterns 可注入);
#                zephyr.shared.io.paths (REPO_ROOT); PyYAML（只读 config/secret_registry.yaml）
# [CONSUMERS] tests/ai_layer/redline/test_ai_secret_exposure.py（本窗唯一实接线）;
#             待接线（总筹）：①S1 启动器 screen_session_env(deny_patterns=combined_deny_patterns())
#             ②secrets 读取面 assert_key_not_forbidden(key)——见回执"待接线一行"
# [STARTUP] manual（CLI: python -m zephyr.ai_layer.redline.ai_secret_exposure report）
# [MATURITY] new
# [INVARIANTS] 本件是 `ai_exposure: forbidden` 字段的**执法面**：字段没有读者=装饰，故真源 config/secret_registry.yaml 的 forbidden 条目在此被读成 deny 模式，与 S1 硬编码三族（QMT 前缀实盘族 / ZEPHYR_AUDIT_HMAC_SECRET / *_LIVE_*）取并集后交给 session_env_guard 判定——**只扩大拦截面、绝不缩小**；
#              "只扩不缩"自 W6-H 起**有实现**（rb2 §七.1 实测：修前撤掉 YAML 标注即静默缩回基线 4→3 条，零拒绝零留痕）：每次读册把当次 forbidden 键集与 append-only 台账 (.runtime/gate_audit/obj_s_ai_exposure_forbidden.jsonl，同族先例 session_env_guard DEFAULT_AUDIT_PATH) 的上一次读数比对，**变窄即抛 AiExposureError**，除非显式给撤章理由（理由与差集一并落台账＝显式留痕）；台账写不进=名单不可信=同样抛错，禁"记不下来就当没发生"；
#              缺 secrets 章节 / secrets 空表 / 条目全非映射 / 非法编码 = **抛错**（fail-closed，绝不当作"无人被禁"——rb2 §七.1/§七.2 两条绕过）；字段缺省=该条目不参与机检，但**整册零标注是"插座未接线"而非"已防护"**：此事实由 report.machine_check_state=outlet_only_field_unused + logger.warning 暴露（W6-H 前头注承诺"零标注即抛错"的分支根本不存在＝契约说谎，现网真册 106 条 0 条标注）；
#              ai_exposure 取值受控（forbidden/allowed/conditional），词表外值=该条计入 malformed 并被**当作 forbidden 处理**（拼错的红名单比漏判更危险）；筛查面与读取面共用同一个 fnmatch matcher（rb2 §七.3：曾一处拒一处放）；本件永不读 os.environ、永不输出密钥值（sanitize 纪律，只键名/计数）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md §1 NL-2 检查点①/§待 Owner 项②
# [STABILITY] new
# [SAFETY] M（拒绝判定+审计，不执行进程终止；密钥零落盘）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件缺失/非法编码/坏 YAML/顶层非映射/缺 secrets 章/secrets 空表/条目全非映射 → AiExposureError（真源不可用不得假装"无人被禁"；rb2 §七.2 说谎分支已补齐）；台账显示的 forbidden 集合变窄且无撤章理由 → AiExposureError；单条目缺 key 字段 → 跳过并计入 malformed；审计与 KillSwitch 级联沿用 session_env_guard，本件不另起留证面
# [TESTS] tests/ai_layer/redline/test_ai_secret_exposure.py（forbidden 抽取/基线并集严格扩大/未标注字段零变化/词表外取值按 forbidden 处置/坏 YAML 抛错/现网真册 report 计数/assert_key_not_forbidden 拒 with forbidden 放行 with 未标注）
# [TTL] permanent
"""ai_secret_exposure — 秘钥注册表 `ai_exposure: forbidden` 字段的机检面（OBJ_S 待 Owner 项 ②）。

大白话：秘钥册里给某些钥匙盖一个"AI 不许碰"的章。盖章本身不拦人——本件就是"看见章就拦"
的那道门：把盖了章的钥匙名并进 AI 会话启动时的禁发名单，并把判定交给既有的 S1 筛查件。

判据真源=`docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md` §1 NL-2（"registry 无字段
也能拦"＝S1 三族硬编码 deny-list 已功能等价）；本件的职责=证明**加了字段之后拦截面真的变宽**，
测试用"基线放行、加字段后拒绝"的同一 env 键做正反对照（拦截面扩大可证伪）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 秘钥册与台账（config/secret_registry.yaml、forbidden 台账 jsonl）
#   fields: secrets 条目 key/ai_exposure；台账上次 forbidden 键集
#   code: _load_entries/_ledger_prior
# 层: 算法
# - id: A1
#   name_zh: 扫描三态→只扩不缩闸→机检态→基线并集
#   name_en: load_ai_exposure_report
#   intro: _scan_exposure_entries 扫 forbidden/malformed/marked；_ratchet_check 变窄无理由即抛；_machine_check_state 诚实自述
#   inputs: I1
#   outputs: O1
# 层: 输出
# - id: O1
#   name: AiExposureReport/deny 并集/读取门禁
#   fields: forbidden_keys/machine_check_state/ratchet_state
#   code: combined_deny_patterns/key_matches_forbidden/assert_key_not_forbidden
#   downstream: zephyr.ai_layer.redline.session_env_guard（S1 筛查正门）；secrets 读取面（待接线）
# 边: I1 --> A1 ; A1 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.ai_layer.redline.negative_list import DENY_ENV_PATTERNS
from zephyr.ai_layer.redline.session_env_guard import EnvScreenVerdict, screen_session_env
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__: Final = [
    "AI_EXPOSURE_FIELD",
    "DEFAULT_FORBIDDEN_LEDGER",
    "DEFAULT_REGISTRY_PATH",
    "EXPOSURE_FORBIDDEN",
    "EXPOSURE_VALUES",
    "STATE_BASELINE_ONLY",
    "STATE_GUARD_ACTIVE",
    "STATE_MARKED_BUT_NONE_FORBIDDEN",
    "STATE_OUTLET_ONLY",
    "AiExposureError",
    "AiExposureReport",
    "assert_key_not_forbidden",
    "assert_key_not_forbidden_ai_side",
    "combined_deny_patterns",
    "current_session_is_ai_side",
    "forbidden_secret_keys",
    "key_matches_forbidden",
    "load_ai_exposure_report",
    "registry_deny_patterns",
    "screen_session_env_with_registry",
]

#: 秘钥册真源（热册本体由 Owner/总筹改，本件只读）
DEFAULT_REGISTRY_PATH: Final[Path] = REPO_ROOT / "config" / "secret_registry.yaml"
#: "只扩不缩"的记账面：append-only 台账（同族先例=session_env_guard.DEFAULT_AUDIT_PATH）
DEFAULT_FORBIDDEN_LEDGER: Final[Path] = REPO_ROOT / ".runtime" / "gate_audit" / "obj_s_ai_exposure_forbidden.jsonl"
AI_EXPOSURE_FIELD: Final[str] = "ai_exposure"
EXPOSURE_FORBIDDEN: Final[str] = "forbidden"
#: 字段受控取值（词表外值=按 forbidden 处置并计 malformed）
EXPOSURE_VALUES: Final[frozenset[str]] = frozenset({"forbidden", "allowed", "conditional"})
#: 机检态四值（诚实自述：现网 marked=0 是"插座"不是"护栏"，两件事分开表述——rb2 §七.5）
STATE_GUARD_ACTIVE: Final[str] = "guard_active"  # ≥1 条 forbidden＝真在拦
STATE_OUTLET_ONLY: Final[str] = "outlet_only_field_unused"  # 整册零标注＝插座未接线
STATE_MARKED_BUT_NONE_FORBIDDEN: Final[str] = "marked_but_none_forbidden"
STATE_BASELINE_ONLY: Final[str] = "baseline_only"  # 兜底（理论不达）
#: ledger_path 缺省哨兵（在调用时读模块常量，测试可 monkeypatch 到 tmp_path，禁写生产路径）
_USE_DEFAULT: Final[object] = object()


class AiExposureError(RuntimeError):
    """秘钥册不可用（缺文件/顶层形状非法）——fail-closed，绝不当作"无人被禁"。"""

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


@dataclass(frozen=True)
class AiExposureReport:
    """字段机检面自述（只计数与键名，零密钥值）。"""

    registry_path: str
    total_entries: int
    forbidden_keys: tuple[str, ...] = field(default_factory=tuple)
    marked_entries: int = 0
    unmarked_entries: int = 0
    malformed_values: tuple[str, ...] = field(default_factory=tuple)
    #: 机检态（STATE_*，四值）——把"现网 marked=0 故零行为变化"与"字段真能拦"分开表述
    machine_check_state: str = STATE_BASELINE_ONLY
    #: 并集是否真的比 S1 基线宽（False＝本件今天只提供插座，没加护栏）
    widened: bool = False
    #: 整册零标注（=今天的真实现网）
    field_unused: bool = False
    #: "只扩不缩"闸读数：baselined/unchanged/widened/removal_authorized/no_stamps_yet/not_checked
    ratchet_state: str = "not_checked"
    #: 台账上一次读数与本次的差集（非空=有人撤章，必须已留痕或已抛错）
    removals: tuple[str, ...] = field(default_factory=tuple)
    prior_forbidden_keys: tuple[str, ...] = field(default_factory=tuple)
    ledger_path: str = ""
    combined_patterns: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, object]:
        return {
            "registry_path": self.registry_path,
            "total_entries": self.total_entries,
            "forbidden_keys": list(self.forbidden_keys),
            "marked_entries": self.marked_entries,
            "unmarked_entries": self.unmarked_entries,
            "malformed_values": list(self.malformed_values),
            "machine_check_state": self.machine_check_state,
            "widened": self.widened,
            "field_unused": self.field_unused,
            "ratchet_state": self.ratchet_state,
            "removals": list(self.removals),
            "prior_forbidden_keys": list(self.prior_forbidden_keys),
            "ledger_path": self.ledger_path,
            "baseline_deny_patterns": list(DENY_ENV_PATTERNS),
            "combined_deny_patterns": list(self.combined_patterns),
            # 诚实自述：拦截面==基线时本件不是护栏，只是预置插座（rb2 §七.5"把插座记成护栏"）
            "outlet_not_guard": not self.widened,
        }


def _load_entries(path: Path) -> list[object]:
    """读秘钥册：缺文件/非法编码/坏 YAML/顶层非映射/**缺章**/**空表**/条目全非映射一律抛错。"""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise AiExposureError("secret_registry 文件缺失", details={"path": str(path)}) from exc
    except (UnicodeDecodeError, OSError) as exc:
        # rb2 §七.4：非法字节曾抛未声明的 UnicodeDecodeError，调用方按契约捕错会漏
        raise AiExposureError(
            "secret_registry 不可读（非法编码或 IO 故障）——fail-closed，禁当「无人被禁」",
            details={"path": str(path), "error": str(exc)[:200]},
        ) from exc
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise AiExposureError("secret_registry 坏 YAML", details={"path": str(path)}) from exc
    if not isinstance(raw, Mapping):
        raise AiExposureError("secret_registry 顶层须为映射", details={"path": str(path)})
    entries = raw.get("secrets")
    if not isinstance(entries, list):
        raise AiExposureError(
            "secret_registry 缺 secrets 章节（缺章=真源不可用，不得当作「无人被禁」）",
            details={"path": str(path)},
        )
    if not entries:
        raise AiExposureError(
            "secret_registry secrets 是空表（整册被清空=「无人被禁」的假象，禁放行）",
            details={"path": str(path)},
        )
    if not any(isinstance(entry, Mapping) for entry in entries):
        raise AiExposureError(
            "secret_registry 条目全为非映射（形状不合=读不出任何键名，禁当合规）",
            details={"path": str(path), "entries": str(len(entries))},
        )
    return entries


def _ledger_prior(path: Path) -> tuple[str, ...] | None:
    """台账最后一条记录的 forbidden 键集；None=尚无基线（本件第一次读数）。"""
    if not path.exists():
        return None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise AiExposureError(
            "禁读名单台账不可读（「只扩不缩」闸失效，禁静默放行）",
            details={"ledger": str(path), "error": str(exc)[:200]},
        ) from exc
    last: tuple[str, ...] | None = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            logger.warning("禁读名单台账坏行跳过（不据此判定）: %s", path)
            continue
        if isinstance(record, Mapping) and isinstance(record.get("forbidden_keys"), list):
            last = tuple(sorted(str(k) for k in record["forbidden_keys"]))
    return last


def _ledger_append(path: Path, keys: Iterable[str], *, registry: str, event: str, reason: str | None = None) -> None:
    """追加一条禁读名单读数（append-only）；**写不进=名单不可信=抛错**，禁"记不下当没发生"。"""
    record: dict[str, object] = {
        "at_utc": now_utc().isoformat(timespec="seconds"),
        "source": "obj_s_ai_exposure",
        "event": event,
        "registry": registry,
        "forbidden_keys": sorted(str(k) for k in keys),
    }
    if reason:
        record["reason"] = str(reason)[:500]
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        raise AiExposureError(
            "禁读名单台账写入失败（「只扩不缩」闸不得静默失效）",
            details={"ledger": str(path), "error": str(exc)[:200]},
        ) from exc


def _ratchet_check(
    current: tuple[str, ...], *, registry: str, ledger: Path | str | None, allow_shrinkage_reason: str | None
) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    """ "只扩不缩"闸：名单变窄=抛错，除非显式给撤章理由（理由与差集一并落台账＝显式留痕）。"""
    if ledger is None:
        logger.warning("AI 禁读名单「只扩不缩」闸未启用（ledger=None）——本件自述不得写成一道在跑的护栏")
        return "not_checked", (), ()
    path = Path(ledger)
    prior = _ledger_prior(path)
    if prior is None:
        if not current:
            return "no_stamps_yet", (), ()
        _ledger_append(path, current, registry=registry, event="baselined")
        return "baselined", (), ()
    removals = tuple(sorted(set(prior) - set(current)))
    if removals:
        if not allow_shrinkage_reason:
            raise AiExposureError(
                "禁读名单变窄（违反本件「只扩不缩」硬不变量）——撤章须显式给理由并留痕",
                details={"removed": "+".join(removals), "ledger": str(path), "registry": registry},
            )
        _ledger_append(path, current, registry=registry, event="removal_authorized", reason=allow_shrinkage_reason)
        logger.warning("AI 禁读名单变窄，已按显式理由留痕: %s", "+".join(removals))
        return "removal_authorized", removals, prior
    if set(prior) == set(current):
        return "unchanged", (), prior
    _ledger_append(path, current, registry=registry, event="widened")
    return "widened", (), prior


def _scan_exposure_entries(entries: list[object]) -> tuple[list[str], list[str], int]:
    """扫条目三态（load_ai_exposure_report 的条目循环段）：返回 (forbidden 键, malformed 账, marked 计数)。"""
    forbidden: list[str] = []
    malformed: list[str] = []
    marked = 0
    for entry in entries:
        if not isinstance(entry, Mapping):
            malformed.append("<non-mapping-entry>")
            continue
        key = str(entry.get("key") or "").strip()
        if not key:
            malformed.append("<missing-key>")
            continue
        if AI_EXPOSURE_FIELD not in entry:
            continue
        marked += 1
        value = str(entry.get(AI_EXPOSURE_FIELD) or "").strip()
        if value == EXPOSURE_FORBIDDEN or value not in EXPOSURE_VALUES:
            # 词表外取值按 forbidden 处置（宁严勿漏），同时留 malformed 账
            forbidden.append(key)
            if value not in EXPOSURE_VALUES:
                malformed.append(f"{key}:{value or '<empty>'}")
    return forbidden, malformed, marked


def _machine_check_state(current: tuple[str, ...], marked: int) -> str:
    """机检态三择一：有 forbidden=真在拦；整册零标注=插座未接线；有标注但零 forbidden=标而未禁。"""
    if current:
        return STATE_GUARD_ACTIVE
    if marked == 0:
        return STATE_OUTLET_ONLY
    return STATE_MARKED_BUT_NONE_FORBIDDEN


def load_ai_exposure_report(
    path: Path | str | None = None,
    *,
    ledger_path: Any = _USE_DEFAULT,  # noqa: any-abuse -- 三态哨兵参数(_USE_DEFAULT/None/Path|str)，类型面诚实要求
    allow_shrinkage_reason: str | None = None,
) -> AiExposureReport:
    """扫秘钥册 → 谁被标 forbidden、谁没标、谁拼错（三态全暴露，不粉饰）＋只扩不缩闸。

    Args:
        path: 秘钥册（None=config/secret_registry.yaml）。
        ledger_path: 名单台账；None=**关掉闸**（读数会自报 ratchet_state=not_checked，
            禁把关掉闸的读数写成"已执法"）；测试须指 tmp_path（禁写生产 .runtime）。
        allow_shrinkage_reason: 撤章显式理由；不给=名单变窄直接抛错。
    """
    target = Path(path) if path is not None else DEFAULT_REGISTRY_PATH
    entries = _load_entries(target)
    forbidden, malformed, marked = _scan_exposure_entries(entries)
    forbidden.sort()
    current = tuple(forbidden)
    ledger = DEFAULT_FORBIDDEN_LEDGER if ledger_path is _USE_DEFAULT else ledger_path
    ratchet_state, removals, prior = _ratchet_check(
        current, registry=str(target), ledger=ledger, allow_shrinkage_reason=allow_shrinkage_reason
    )
    widened = bool(set(current) - set(DENY_ENV_PATTERNS))
    state = _machine_check_state(current, marked)
    if state == STATE_OUTLET_ONLY:
        # 家法：零样本/零使用必打 WARNING——"没人被禁"不是"已防护"
        logger.warning(
            "AI 秘钥面机检未生效：册内 %d 条零条 %s 标注（state=%s）＝插座未接线，非护栏",
            len(entries),
            AI_EXPOSURE_FIELD,
            STATE_OUTLET_ONLY,
        )
    return AiExposureReport(
        registry_path=str(target),
        total_entries=len(entries),
        forbidden_keys=current,
        marked_entries=marked,
        unmarked_entries=len(entries) - marked,
        malformed_values=tuple(malformed),
        machine_check_state=state,
        widened=widened,
        field_unused=marked == 0,
        ratchet_state=ratchet_state,
        removals=removals,
        prior_forbidden_keys=prior,
        ledger_path=str(ledger) if ledger is not None else "",
        combined_patterns=combined_deny_patterns_from(current, base=DENY_ENV_PATTERNS),
    )


def combined_deny_patterns_from(
    forbidden: Iterable[str], *, base: tuple[str, ...] = tuple(DENY_ENV_PATTERNS)
) -> tuple[str, ...]:
    """基线 ∪ 册面（纯函数，供 report 与 combined_deny_patterns 共用，禁两处各拼一遍）。"""
    baseline = tuple(base)
    extra = tuple(p for p in tuple(forbidden) if p not in baseline)
    return baseline + extra


def forbidden_secret_keys(
    path: Path | str | None = None,
    *,
    ledger_path: Any = _USE_DEFAULT,  # noqa: any-abuse -- 三态哨兵参数(_USE_DEFAULT/None/Path|str)，类型面诚实要求
    allow_shrinkage_reason: str | None = None,
) -> tuple[str, ...]:
    """被标 forbidden 的秘钥名（升序确定性）；册形状不合=抛错，不回空表。"""
    return load_ai_exposure_report(
        path, ledger_path=ledger_path, allow_shrinkage_reason=allow_shrinkage_reason
    ).forbidden_keys


def registry_deny_patterns(path: Path | str | None = None, *, ledger_path: Any = _USE_DEFAULT) -> tuple[str, ...]:  # noqa: any-abuse -- 三态哨兵参数(_USE_DEFAULT/None/Path|str)，类型面诚实要求
    """字段 → deny 模式（与 S1 基线同形状，交给 fnmatch 判定）。"""
    return tuple(forbidden_secret_keys(path, ledger_path=ledger_path))


def combined_deny_patterns(path: Path | str | None = None, *, ledger_path: Any = _USE_DEFAULT) -> tuple[str, ...]:  # noqa: any-abuse -- 三态哨兵参数(_USE_DEFAULT/None/Path|str)，类型面诚实要求
    """S1 基线 ∪ registry forbidden（硬不变量：只扩不缩；变窄由台账闸拦下并抛错）。"""
    return combined_deny_patterns_from(forbidden_secret_keys(path, ledger_path=ledger_path))


def key_matches_forbidden(key: str, patterns: Iterable[str]) -> bool:
    """唯一 matcher：筛查面与读取面共用（rb2 §七.3 修前两读端一处拒一处放）。"""
    name = str(key or "").strip()
    if not name:
        return False
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in patterns)


def screen_session_env_with_registry(
    env: Mapping[object, object],
    session_id: str,
    *,
    registry_path: Path | str | None = None,
    audit_path: Path | None = None,
    ledger_path: Any = _USE_DEFAULT,  # noqa: any-abuse -- 三态哨兵参数(_USE_DEFAULT/None/Path|str)，类型面诚实要求
    notify_kill_switch: bool = True,
) -> EnvScreenVerdict:
    """S1 正门的"字段感知"版本：筛查用并集模式，留证/级联沿用 session_env_guard。"""
    target = Path(registry_path) if registry_path is not None else DEFAULT_REGISTRY_PATH
    return screen_session_env(
        env,
        session_id,
        deny_patterns=combined_deny_patterns(target, ledger_path=ledger_path),
        audit_path=audit_path,
        notify_kill_switch=notify_kill_switch,
    )


def assert_key_not_forbidden(
    key: str,
    *,
    registry_path: Path | str | None = None,
    ledger_path: Any = _USE_DEFAULT,  # noqa: any-abuse -- 三态哨兵参数(_USE_DEFAULT/None/Path|str)，类型面诚实要求
) -> str:
    """秘钥读取面的门禁原语：命中 forbidden 名单的键=抛错（供 secrets 调用面接线，非自读 env）。

    判定用与筛查面**同一个** fnmatch matcher（盖章成 QMT 前缀实盘族这类模式时两读端同判）。

    :return: 原样键名（放行时便于链式使用）
    """
    name = str(key or "").strip()
    patterns = registry_deny_patterns(registry_path, ledger_path=ledger_path)
    matched = [p for p in patterns if key_matches_forbidden(name, (p,))]
    if matched:
        raise AiExposureError(
            f"秘钥 {name} 命中 {AI_EXPOSURE_FIELD}={EXPOSURE_FORBIDDEN} 名单，AI 面拒读",
            details={
                "key": name,
                "matched_pattern": matched[0],
                "registry": str(registry_path or DEFAULT_REGISTRY_PATH),
            },
        )
    return name


#: 会话身份 env 惯例（真源=scripts/git_safety_wrapper.ps1 §Session ID injection）
SESSION_ID_ENV_VAR: Final[str] = "ZEPHYR_SESSION_ID"


def current_session_is_ai_side(
    session_id: str | None = None,
    *,
    project_root: str | Path | None = None,
) -> bool:
    """C108 前置：AI/生产会话判别器（owner 侧通道不拦，只拦 AI 侧）。

    仓内无现成判别器（grep session 判别/owner 通道 0 命中）→ 最小实现=env+会话注册表
    标志判别（2026-09-30）：

      1. session_id 显式参 > ``ZEPHYR_SESSION_ID``（git_safety_wrapper 注入惯例）；
         仍空 = 生产/owner 直连通道 → False（不拦）
      2. SessionRegistry.get_session 在册 = AI 施工会话 → True（拦）
      3. 不在册 / 查询失败 = owner 侧优先放行 → False（S1 启动面三族硬编码 deny
         仍在兜底，本判定只影响读取面断言的owner豁免，不缩 S1 拦截面）

    本函数永不抛异常（判别器故障不得反噬读取主路径）。
    """
    try:
        import os

        sid = (session_id or os.environ.get(SESSION_ID_ENV_VAR) or "").strip()
        if not sid:
            return False
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        if project_root is not None:
            registry = SessionRegistry(project_root)
        else:
            registry = SessionRegistry()
        info = registry.get_session(sid)
        if info is None:
            return False
        if isinstance(info, dict):  # 兼容 mock/旧式 dict 返回
            return bool(info.get("session_id") or sid)
        return True
    except Exception as e:  # noqa: BLE001 — 判别器故障保守非 AI（owner 侧优先，不反噬读取路径）
        logger.debug("ai-side session probe failed (assume non-AI): %s", e)
        return False


def assert_key_not_forbidden_ai_side(
    key: str,
    *,
    session_id: str | None = None,
    registry_path: Path | str | None = None,
    ledger_path: Any = _USE_DEFAULT,  # noqa: any-abuse -- 三态哨兵参数(_USE_DEFAULT/None/Path|str)，类型面诚实要求
) -> str | None:
    """秘钥读取面的"AI 侧感知"断言（C108 通电件②）：owner/生产通道放行，AI 会话拦。

    判别见 :func:`current_session_is_ai_side`；AI 侧 → 委托
    :func:`assert_key_not_forbidden`（同一 fnmatch matcher，同一名单）；非 AI →
    原样返回键名（owner 侧通道不拦）。

    :return: 放行时原样键名；AI 侧命中 forbidden 抛 :class:`AiExposureError`。
    """
    if not current_session_is_ai_side(session_id):
        return str(key or "").strip()
    return assert_key_not_forbidden(key, registry_path=registry_path, ledger_path=ledger_path)


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ai_secret_exposure", description=__doc__)
    parser.add_argument("command", choices=("report",), nargs="?", default="report")
    parser.add_argument("--registry", default=None)
    parser.add_argument("--ledger", default=None, help="名单台账覆盖（测试/演练指临时路径；缺省=生产 .runtime 台账）")
    parser.add_argument(
        "--no-ledger",
        action="store_true",
        help="关掉「只扩不缩」闸（读数会自报 ratchet_state=not_checked，禁当已执法）",
    )
    ns = parser.parse_args(argv)
    ledger: Path | str | None = ns.ledger if ns.ledger else None
    if not ns.no_ledger and not ns.ledger:
        ledger = _USE_DEFAULT
    report = load_ai_exposure_report(ns.registry, ledger_path=ledger)
    print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))
    if not report.widened:
        print("[OUTLET] 拦截面==S1 基线：字段未落地或全册零 forbidden＝预置插座，不是已防护（勿写成「已执法」）")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_cli())
