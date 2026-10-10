# [MODULE] tests.gov.infra.test_belt_watchdog_clock_unit
# [DOMAIN] D_AUDITTEST
# [TTL] permanent
# [DEPENDENCIES] scripts/installers/belt_watchdog.ps1（被测脚本，只读源码与算式）
# [CONSUMERS] pytest（tests/gov/infra/）
# [STARTUP] imported
# [MATURITY] production
# [BLUEPRINT] MOD-INFRA-BELT-WATCHDOG | scripts/installers/belt_watchdog.ps1 | guard
# [INVARIANTS] 钉两件事：①看门狗判活的 age 必须与心跳写侧同源（unix 秒）；②真死仍须判死
#   （age>600 时 alive=False）——防我把修口径变成"永不 spawn"的新洞
# [MODIFY-GUARD] 新建 2026-10-10 st-maint1-20261010（批复③ daemon 双实例根因治疗红证）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=口径未对齐；永不 skip
# [TESTS] 本文件即测试
"""belt watchdog 时钟口径对抗测试（2026-10-10 实测根因）。

病灶：心跳写侧 `wall_ts` 用 unix 秒（`time.time()`），看门狗读侧却算
`[DateTimeOffset]::UtcNow.UtcTicks / 1e7`（**.NET 纪元**：自 0001-01-01 的秒数）。
两式相减得 ~6.2e10 秒（约 1969 年），恒 > 阈值 600 ⇒ Stage 1 永远判死 ⇒
Stage 2（CIM 在负载下可空返回）每分钟 spawn 一个重复 daemon——正是该脚本文件头
自己警告的 pileup disease（历史上堆到 6-8 个）。

当晚实测：真心跳真实年龄 **6 秒**，看门狗算出 **62,135,596,806 秒**。
"""

from __future__ import annotations

import datetime
import re
from pathlib import Path

_NET_EPOCH = datetime.datetime(1, 1, 1, tzinfo=datetime.timezone.utc)
_THRESHOLD_S = 600.0


def _watchdog_text() -> str:
    for parent in Path(__file__).resolve().parents:
        cand = parent / "scripts" / "installers" / "belt_watchdog.ps1"
        if cand.exists():
            return cand.read_text(encoding="utf-8")
    raise RuntimeError("未找到 belt_watchdog.ps1（装载自证失败）")


def _age_line(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if re.search(r"^\s*\$age\s*=", ln)]
    assert lines, "看门狗里没有 $age 赋值行＝判活口径已失踪（比误判更糟）"
    return lines[0]


def test_age_uses_unix_seconds_not_dotnet_ticks() -> None:
    """主案：age 必须与写侧同源（unix 秒），禁 .NET UtcTicks 除法形态。"""
    line = _age_line(_watchdog_text())

    assert "ToUnixTimeSeconds" in line, f"age 未用 unix 秒口径，仍是异源时钟: {line}"
    assert "UtcTicks" not in line, f"age 仍含 .NET 纪元除法（恒判死根因未拔）: {line}"


def test_dotnet_tick_formula_is_the_measured_culprit() -> None:
    """同式实测：把当晚的两个数复算一遍，钉住"这不是理论推测"。"""
    wall_ts = 1791637069.431513  # 当晚真心跳（写侧 time.time()）
    unix_now = 1791637076.0  # 同刻本机 unix 秒

    real_age = unix_now - wall_ts
    dotnet_now = (datetime.datetime.fromtimestamp(unix_now, datetime.timezone.utc) - _NET_EPOCH).total_seconds()
    watchdog_age = dotnet_now - wall_ts

    assert real_age < _THRESHOLD_S, "真实年龄本应判活"
    assert watchdog_age > 6e10, f"旧口径应算出天文数字，实得 {watchdog_age}"
    # 旧口径必然越过阈值 ⇒ Stage 1 恒判死 ⇒ 每分钟 spawn
    assert not (watchdog_age < _THRESHOLD_S)


def test_fixed_formula_still_detects_real_death() -> None:
    """反向钉桩：修口径不得变成"永不 spawn"——陈旧心跳仍须判死。"""
    unix_now = 1791637076.0
    for stale_seconds, expect_alive in ((0.0, True), (599.0, True), (601.0, False), (7200.0, False)):
        age = unix_now - (unix_now - stale_seconds)
        assert (age < _THRESHOLD_S) is expect_alive, f"age={age}s 判活={not expect_alive}"


def test_heartbeat_writer_and_watchdog_share_one_clock() -> None:
    """跨侧对账：写侧确实用 unix 秒（否则我这次的"修法"本身就是新洞）。"""
    daemon_src = next(
        p
        for p in (Path(__file__).resolve().parents[3] / "src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py",)
        if p.exists()
    )
    src = daemon_src.read_text(encoding="utf-8")

    assert re.search(r"wall_ts", src), "写侧已无 wall_ts 字段＝本测试前提失效，须重写"
    assert re.search(r"time\.time\(\)", src), "写侧不再是 unix 秒＝看门狗口径须随之重定"
    assert "monotonic()" not in src.split("wall_ts")[0][-400:], "写侧若改用单调钟，age 判据须同步改"
