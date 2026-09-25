# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_session_env_guard
# [MODULE] zephyr.ai_layer.redline.session_env_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.redline.negative_list (DENY_ENV_PATTERNS/NL rule_id 常量，SSOT 引用不复制);
#                zephyr.security.access_control.kill_switch (record_event，SEV-3 信号原生级联);
#                zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] AI 会话启动器/spawn 面（S1 接线批：spawn 前调用 screen_session_env，
#             用返回的 allowed env 替换原 env 后再起进程）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] deny-list 机检（DESIGN §1 NL-2 检查点①）：命中 QMT 前缀实盘族/ZEPHYR_AUDIT_HMAC_SECRET/*_LIVE_*
#              的 env 键=拒绝启动该会话+审计；审计只记**键名与值长度**，值本体零落盘
#              （secrets.py sanitize 纪律：***REDACTED*** (len=N)）；非空值命中=泄密事故
#              候选（leak_suspected，SEV-3 最高级）；本模块只产"拒绝判定+审计+KillSwitch
#              信号"，不执行进程终止（kill/terminate=启动器职责，避免守门件越权动手）；
#              模块自身禁读 os.environ（守门件示范守规矩：env 一律由调用方显式传入）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md §1 NL-2
# [STABILITY] new
# [SAFETY] M（拒绝启动=会话级阻断，不放行任何密钥值）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] filter_env/screen_session_env 对畸形输入（非 str 键值）跳过该键计数不炸；
#                  审计写失败降级 logger.warning（留证失败不掩盖判定，verdict 仍=拒绝）；
#                  deny 模式空表=全放行（调用方失误面，NOT used in production default）
# [TESTS] tests/ai_layer/redline/test_session_env_guard.py（QMT 前缀实盘族环境被拒+留证/
#         ZEPHYR_AUDIT_HMAC_SECRET 与 *_LIVE_* 命中/非空值=leak_suspected/干净 env 全放行/
#         审计仅键名零值/审计写失败不炸仍拒绝/KillSwitch record_event 级联）
# [TTL] permanent
"""session_env_guard — AI 会话 env 白名单启动器（OBJ_S 施工项 S1）。

DESIGN §1 NL-2 检查点①：AI 会话 spawn 时对 env 做 deny-list 过滤，
deny=QMT 前缀实盘族/``ZEPHYR_AUDIT_HMAC_SECRET``/``*_LIVE_*``；命中即拒绝启动该会话+审计。
验收标准（红蓝 R1-F4）：含 QMT 前缀实盘族的环境在代理会话被拒且留证。

正确姿态：本模块是纯判定+留证件——调用方（会话启动器）拿到
``EnvScreenVerdict.allowed=False`` 后**不启动**该会话；allowed=True 时用
``filtered_env``（已剔除 deny 键）作为子进程 env。
"""

from __future__ import annotations

import fnmatch
import json
import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from zephyr.ai_layer.redline.negative_list import (
    DENY_ENV_PATTERNS,
    NL_REAL_KEYS,
)
from zephyr.security.access_control.kill_switch import (
    TriggerEvent,
    TriggerResult,
    get_kill_switch,
)
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

DEFAULT_AUDIT_PATH: Final = REPO_ROOT / ".runtime" / "gate_audit" / "obj_s_env_denial.jsonl"
REDACTED_TEMPLATE: Final = "***REDACTED*** (len={length})"
AUDIT_SOURCE: Final = "obj_s_session_env_guard"


@dataclass(frozen=True)
class EnvScreenVerdict:
    """S1 筛查裁定：allowed=False 时启动器必须拒绝启动该会话。"""

    session_id: str
    allowed: bool
    denied_keys: tuple[str, ...] = field(default_factory=tuple)
    leak_suspected: bool = False
    filtered_env: Mapping[str, str] = field(default_factory=dict)
    reason: str = ""


def filter_env(
    env: Mapping[object, object],
    *,
    deny_patterns: tuple[str, ...] = DENY_ENV_PATTERNS,
) -> tuple[dict[str, str], list[str]]:
    """按 deny 模式切分 env → (放行 dict, 拒绝键名 list)（纯函数）。

    非 str 键/值的条目跳过不进放行面（畸形输入不炸不放大）。
    """
    allowed: dict[str, str] = {}
    denied: list[str] = []
    for raw_key, raw_value in env.items():
        if not isinstance(raw_key, str) or not isinstance(raw_value, str):
            continue
        if any(fnmatch.fnmatchcase(raw_key, pattern) for pattern in deny_patterns):
            denied.append(raw_key)
        else:
            allowed[raw_key] = raw_value
    return allowed, denied


def _audit_record(verdict: EnvScreenVerdict, env: Mapping[object, object]) -> dict[str, object]:
    """审计记录（只键名+值长度，值本体零落盘——secrets.py sanitize 纪律）。"""
    shapes: dict[str, str] = {}
    for key in verdict.denied_keys:
        raw = env.get(key)
        length = len(raw) if isinstance(raw, str) else -1
        shapes[key] = REDACTED_TEMPLATE.format(length=length)
    return {
        "timestamp": now_utc().isoformat(),
        "source": AUDIT_SOURCE,
        "rule_id": NL_REAL_KEYS,
        "session_id": verdict.session_id,
        "action": "deny_spawn",
        "denied_keys": list(verdict.denied_keys),
        "denied_value_shapes": shapes,
        "leak_suspected": verdict.leak_suspected,
        "reason": verdict.reason,
    }


def _write_audit(verdict: EnvScreenVerdict, env: Mapping[object, object], audit_path: Path) -> None:
    """jsonl 追加留证（fail-open：写失败 warning，不掩盖拒绝判定）。"""
    try:
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(_audit_record(verdict, env), ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 留证失败不阻断判定（ERROR_CONTRACT）
        logger.warning("obj_s env denial 审计写失败（判定仍=拒绝）: %s", audit_path, exc_info=True)


def screen_session_env(
    env: Mapping[object, object],
    session_id: str,
    *,
    deny_patterns: tuple[str, ...] = DENY_ENV_PATTERNS,
    audit_path: Path | None = None,
    notify_kill_switch: bool = True,
) -> EnvScreenVerdict:
    """会话启动前 env 筛查（S1 正门）。

    命中 deny 名单 → allowed=False + 审计留证（仅键名）+ KillSwitch
    ``permission_boundary_probe`` record_event（SEV-3 信号，≥3 agent 原生级联全局）。
    非空值命中=leak_suspected（泄密事故候选，SEV-3 最高级，建议 Owner 立即轮换）。
    """
    allowed, denied = filter_env(env, deny_patterns=deny_patterns)
    leak_suspected = any(str(env.get(key, "")).strip() for key in denied)
    if not denied:
        return EnvScreenVerdict(
            session_id=session_id,
            allowed=True,
            filtered_env=allowed,
        )
    verdict = EnvScreenVerdict(
        session_id=session_id,
        allowed=False,
        denied_keys=tuple(sorted(denied)),
        leak_suspected=leak_suspected,
        filtered_env=allowed,
        reason=(
            f"env 命中 NL-2 禁发名单（{', '.join(sorted(denied))}）——拒绝启动该会话"
            + ("；非空值命中=泄密事故候选（SEV-3），建议 Owner 立即轮换" if leak_suspected else "")
        ),
    )
    _write_audit(verdict, env, audit_path or DEFAULT_AUDIT_PATH)
    if notify_kill_switch:
        result: TriggerResult = get_kill_switch().record_event(
            TriggerEvent(trigger="permission_boundary_probe", agent_id=session_id,
                         context={"rule_id": NL_REAL_KEYS, "denied_keys": sorted(denied)})
        )
        logger.warning(
            "obj_s env guard: session %s denied (%s) killswitch_action=%s",
            session_id, ", ".join(sorted(denied)), result.action,
        )
    return verdict
