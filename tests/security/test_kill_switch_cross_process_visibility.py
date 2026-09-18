# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §跨进程可达性
# [MODULE] tests.security.test_kill_switch_cross_process_visibility
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.shared.infra.process_pool; zephyr.shared.state_store
# [CONSUMERS] —
# [STARTUP] —
# [MATURITY] experimental
# [INVARIANTS] 本件只观测不改行为：三套旗标的拉闸/复位全部发生在**子进程**内，
#   pytest 宿主进程零状态污染；判据=「拉闸方存活时，被保护方能否读到」
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 子进程非零退出/无 JSON → pytest.fail（不得静默跳过=假绿）
# [TESTS] 本件即测试
# [TTL] permanent
"""保命链路「跨进程可达性」机械探测器（红队 st-ff-rb-safe2-20260918 · 处方 req_rbsafe2_01）.

攻的是什么：`kill_switch_orchestrator.route_incident()` 是应急保命轨（BRK-078）
的**唯一出手点**，而它唯一的宿主是 OS 计划任务 process_reaper 的评估进程；
被保护的交易/策略执行体是**另外的进程**。若旗标只活在拉闸那一进程里，
则"拉闸"对真实风险进程零约束——且事后审计面 `check_consistency()` 仍报
consistent=True（它读的正是自己进程的内存态，结构上不可能看见别人的拉闸）。

三条不变式的机检形式（本件的三个测试）：
1. **仪器能红**（对照组，必须绿）：同一套读写工装，对一个**已外置**的旗标
   （JsonStateStore 落盘）必须读出 True。读不出→本测试红。 ⇒ 证明探测器不是
   橡皮图章：它能在"可达"时报可达，因此它在 P-1 三条上报"不可达"是有信息量的。
2. **三套旗标跨进程可达**（现状=红，故 xfail strict）：拉闸子进程**仍存活**时，
   孙进程读 `KillSwitch.is_global_tripped()` / 交易五级 `active` / 终极逃生舱
   `active` 必须为 True。今天全 False → xfail；落盘治本落地当天会 **XPASS 报错**，
   逼施工者回来销案（不会悄悄变成"永远红"也不会变成"永远绿"）。
3. **审计面不得自证清白**（现状=红，故 xfail strict）：别人正拉着闸时，
   `check_consistency()` 不得返回 consistent=True。

纪律：不发 LLM、不碰 CH、不写 data/（落盘全部走 tmp_path）、不碰真实账户。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

from zephyr.shared.infra.process_pool import run_subprocess_hidden

REPO_ROOT = Path(__file__).resolve().parents[2]

_NAMESPACE = "redteam_cross_process_flag"

# 孙进程读腿：只读，绝不拉闸（防测试互相污染）。占位符 __NS__ 由 _render 替换。
_READER = """
import json, sys
sys.path.insert(0, 'src')
from zephyr.shared.state_store import JsonStateStore
from zephyr.security.access_control.kill_switch import get_kill_switch
from zephyr.trading.trading_contracts.risk import trading_kill_switch as t
from zephyr.governance.resilience_governance.last_resort_watchdog import get_last_resort_watchdog
from zephyr.autonomy_core.kill_switch_orchestrator import get_orchestrator
store = JsonStateStore(sys.argv[1])
try:
    rec = store.load("__NS__")
except Exception as exc:
    rec = {"corrupt": repr(exc)}
o = get_orchestrator()
rep = o.check_consistency()
print(json.dumps({
    "externalized": bool(rec and rec.get("active")),
    "system_ks": bool(get_kill_switch().is_global_tripped()),
    "trading_daily_loss": bool(getattr(t.get_switch(t.KillSwitchLevel.DAILY_LOSS), "active", None)),
    "last_resort": bool(get_last_resort_watchdog().active),
    "orch_system": bool(o.is_tripped("SYSTEM")),
    "orch_trading": bool(o.is_tripped("DOMAIN", "trading")),
    "consistency": {"consistent": bool(rep.get("consistent")),
                    "system_tripped": bool(rep.get("system_tripped"))},
}))
"""

# 子进程写腿：真拉三套闸 → 记自见值 → 外置对照旗标 → 在**本进程仍存活时**起读腿。
_WRITER = """
import json, sys
sys.path.insert(0, 'src')
from zephyr.shared.infra.process_pool import run_subprocess_hidden
from zephyr.shared.state_store import JsonStateStore
from zephyr.security.access_control.kill_switch import get_kill_switch
from zephyr.trading.trading_contracts.risk import trading_kill_switch as t
from zephyr.governance.resilience_governance.last_resort_watchdog import get_last_resort_watchdog
from zephyr.autonomy_core.kill_switch_orchestrator import get_orchestrator
ks = get_kill_switch(); ks.manual_trip_global('rb-cross-process')
L = t.KillSwitchLevel.DAILY_LOSS
t.trigger(L)
get_last_resort_watchdog().activate()
r = get_orchestrator().route_incident('funds', reason='rb-cross-process')
JsonStateStore(sys.argv[1]).save("__NS__", {"active": True, "by": "redteam-control-leg"})
own = {"system_ks": ks.is_global_tripped(), "trading_daily_loss": t.get_switch(L).active,
       "last_resort": get_last_resort_watchdog().active, "route_success": r.success}
child = run_subprocess_hidden([sys.executable, "-c", READER_SRC, sys.argv[1]], timeout=600)
print(json.dumps({"own": own, "reader": json.loads((child.stdout or "{}").strip() or "{}"),
                  "reader_rc": child.returncode, "reader_err": (child.stderr or "")[-400:]}))
"""


def _render(script: str, reader_src: str = "") -> str:
    """填占位符（不用 str.format，避开与脚本内 JSON 花括号的冲突）。"""
    out = script.replace("__NS__", _NAMESPACE)
    return out.replace("READER_SRC", repr(reader_src))


def _observe(tmp_dir: Path) -> dict[str, Any]:
    """跑一次「写腿存活时起读腿」的双进程观测，返回 own/reader 两侧视图。"""
    cmd = [sys.executable, "-c", _render(_WRITER, _render(_READER)), str(tmp_dir)]
    proc = run_subprocess_hidden(cmd, cwd=REPO_ROOT, timeout=900)
    if proc.returncode != 0:
        pytest.fail(
            "读腿/写腿子进程非零退出（探测器失效不得当成『没测到』）："
            f"rc={proc.returncode} stderr_tail={(proc.stderr or '')[-500:]}"
        )
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError) as exc:
        pytest.fail(f"子进程未回 JSON（探测器失效）：{exc!r} stdout_tail={(proc.stdout or '')[-300:]}")



@pytest.fixture(scope="module")
def views(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """模块级一次性观测（三条测试共用，避免重复起解释器）。"""
    return _observe(tmp_path_factory.mktemp("xproc_state"))


def test_control_leg_externalized_flag_is_cross_process_visible(views: dict[str, Any]) -> None:
    """仪器能红：已外置的旗标必须被第二个进程读到——读不到说明**探测器**坏了。

    这条是另外两条的前提：只有当同一套工装能证明"外置=可达"，
    它报出的"三套旗标=不可达"才是结论而不是自证清白。
    """
    assert views["reader"]["externalized"] is True, (
        "对照组失败：JsonStateStore 落盘旗标跨进程读不到 ⇒ 本探测器本身失效，"
        f"另两条的判据不可信。raw={views}"
    )


def test_writer_actually_tripped_all_carriers_in_its_own_process(views: dict[str, Any]) -> None:
    """前置自检：写腿进程内三套闸确实拉上了（否则"跨进程读不到"是空判）。"""
    own = views["own"]
    assert own["route_success"] is True, f"route_incident 未成功，观测无意义：{views}"
    assert own["system_ks"] is True and own["trading_daily_loss"] is True and own["last_resort"] is True, (
        f"写腿自身未见熔断，观测无意义：{own}"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "缺陷在册（红队 st-ff-rb-safe2-20260918 / 申请书 req_rbsafe2_01）："
        "三套保命旗标纯进程内存态，拉闸方存活时别人也读不到。"
        "治本落地本条即 XPASS→硬报错，逼销案；禁改成 assert False 之类的自证清白。"
    ),
)
def test_three_carriers_must_be_visible_to_protected_process(views: dict[str, Any]) -> None:
    """判据：拉闸进程**还活着**时，被保护进程就该读到熔断（今天读不到=红）。"""
    reader = views["reader"]
    assert reader["system_ks"] is True, "系统级 KillSwitch 跨进程不可见"
    assert reader["trading_daily_loss"] is True, "交易五级 DAILY_LOSS 跨进程不可见"
    assert reader["last_resort"] is True, "终极逃生舱旗标跨进程不可见"
    assert reader["orch_trading"] is True, "编排器 is_tripped(DOMAIN,trading) 跨进程不可见"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "缺陷在册（req_rbsafe2_01 §审计面）：check_consistency() 只读自己进程的内存态，"
        "别人正拉着闸它也报 consistent=True=假绿形态；须补跨进程可见性自检。"
    ),
)
def test_consistency_audit_must_not_be_green_while_others_are_tripped(views: dict[str, Any]) -> None:
    """判据：事后审计面不得在"真实世界已拉闸"时报一致=绿。"""
    consistency = views["reader"]["consistency"]
    assert consistency["consistent"] is False, (
        f"拉闸方存活、被保护方却什么都读不到，而审计面仍报 consistent=True：{views['reader']}"
    )
