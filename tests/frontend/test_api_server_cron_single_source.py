# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md | §下次调度
# [MODULE] tests.frontend.test_api_server_cron_single_source
# [DOMAIN] D_FRONTEND
# [INVARIANTS] 面板"下次调度"的 cron 表达式必须来自注册表 window_expr（标准口径）且由 croniter 求解——
#   代码内零自写字段匹配器；新旧实现输出对拍以"口径归一后逐字相同"为验收线
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即"cron 口径再次分叉 / 真源↔注册表漂移 / 降级语义破功"证据
# [TESTS] self
# [TTL] permanent
"""排班表 v2 §2.3 C-4 验收单测：api_server 下次调度 cron 单源化（真源+解析器两件）。

改造前有两套各自实现的"cron 件"：
1. 表达式：本端点直读 src/zephyr/data/config/schedule.yaml（APScheduler dow 口径
   0=周一），仓内真源链是 schedule.yaml →（生成器 _aps_dow_to_standard dow 归一）→
   config/resource_profile_registry.yaml window_expr（标准 cron 0=周日）→ croniter
   消费端（resource_schedule_gate / 周历视图）。端点绕过归一映射层，15 个带 dow 的
   时段整体错位一天（周历/闸说周一，面板说周日）。
2. 解析器：端点自写简化字段匹配器（注释"够 schedule.yaml 全部 14 时段"，真源已 21
   时段），与 croniter 是仓内第 3 份 cron 实现。

现方案=改动面最小、失败语义最清晰的一案：表达式改读注册表（复用既有 dow 归一成果，
不新造第 4 份口径换算），解析改 croniter（与闸/周历同基准 Asia/Shanghai、同 6 段剥秒
口径）。本文件三组对拍：
- 对拍①：21 个真实时段，同一（口径归一后）表达式喂新/旧两实现，固定基准逐字相同
- 对拍②：schedule.yaml ↔ 注册表 逐字段一致，差异只允许落在 dow 字段（漂移哨兵）
- 对拍③：改造前后对照，钉死"哪些时段变、哪些没变"，防口径再次分叉
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import pytest
import yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_PROJECT_ROOT / "src"), str(_PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import zephyr.frontend.dashboard.api_server as api_server  # noqa: E402

SCHEDULE_YAML = _PROJECT_ROOT / "src" / "zephyr" / "data" / "config" / "schedule.yaml"
REGISTRY_YAML = _PROJECT_ROOT / "config" / "resource_profile_registry.yaml"

_CN_WEEKDAY = "一二三四五六日"


# ---------------------------------------------------------------------------
# 改造前实现（冻结副本，仅本文件用于对拍；生产代码已无此实现）
# 两处唯一差异：① 表达式由入参给定（原实现读 schedule.yaml）② now() 由 base 入参
# 注入（原实现取本机墙钟）。字段匹配/扫描算法与 git HEAD 逐字相同。
# ---------------------------------------------------------------------------
def _legacy_field_match(val: int, lo: int, hi: int, expr_f: str) -> bool:
    """git HEAD::_next_cron_run.field_match（逐字照抄）。"""
    if expr_f == "*":
        return lo <= val <= hi
    if expr_f.startswith("*/"):
        try:
            step = int(expr_f[2:])
            return val % step == lo % step if step else False
        except ValueError:
            return False
    for part in expr_f.split(","):
        if "-" in part:
            a, b = part.split("-")
            if int(a) <= val <= int(b):
                return True
        elif part.isdigit() and int(part) == val:
            return True
    return False


def legacy_scan(expr: str, base: dt.datetime) -> dt.datetime | None:
    """git HEAD::_next_cron_run 的 8 天分钟扫描臂 → 首个命中时刻（无命中=None）。

    与 HEAD 唯一差异=返回 datetime（便于按日对拍），格式化交给 legacy_next_cron_run。
    """
    fields = expr.split()
    if len(fields) != 5:
        return None
    min_f, hour_f, dom_f, mon_f, dow_f = fields
    base = base.replace(second=0, microsecond=0)
    for offset in range(1, 8 * 24 * 60):  # 最多向后扫 8 天
        t = base + dt.timedelta(minutes=offset)
        # cron dow: 0=周日（原实现按标准 cron 解读，而真源是 APScheduler 0=周一）
        if not _legacy_field_match(t.minute, 0, 59, min_f):
            continue
        if not _legacy_field_match(t.hour, 0, 23, hour_f):
            continue
        if dom_f != "*" and not _legacy_field_match(t.day, 1, 31, dom_f):
            continue
        if mon_f != "*" and not _legacy_field_match(t.month, 1, 12, mon_f):
            continue
        if dow_f != "*" and not _legacy_field_match((t.weekday() + 1) % 7, 0, 6, dow_f):
            continue
        return t
    return None


def legacy_next_cron_run(expr: str, base: dt.datetime) -> str:
    """git HEAD::_next_cron_run 的格式化臂（三档中文串逐字照抄 HEAD）。"""
    fields = expr.split()
    if len(fields) != 5:
        return ""
    base = base.replace(second=0, microsecond=0)
    t = legacy_scan(expr, base)
    if t is None:
        return ""
    delta = t - base
    if delta.total_seconds() < 3600:
        return f"{(t - base).seconds // 60} 分钟后（{t.strftime('%H:%M')}）"
    if delta.days >= 1:
        return f"{delta.days} 天后（{t.strftime('%m-%d %H:%M')}）"
    return f"{delta.seconds // 3600} 小时后（{t.strftime('%H:%M')}）"


def legacy_load_schedule_crons() -> dict[str, str]:
    """git HEAD::_load_schedule_crons —— 直读 schedule.yaml + 6 段剥秒（不换算 dow）。"""
    data = yaml.safe_load(SCHEDULE_YAML.read_text(encoding="utf-8")) or {}
    out: dict[str, str] = {}
    for name, cfg in (data.get("schedules") or {}).items():
        expr = str((cfg or {}).get("cron", "")).strip()
        if not expr:
            continue
        fields = expr.split()
        out[name] = " ".join(fields[-5:]) if len(fields) == 6 else expr
    return out


# ---------------------------------------------------------------------------
# 夹具：真实真源（只读）+ 固定基准集
# ---------------------------------------------------------------------------
def _raw_schedules() -> dict[str, str]:
    data = yaml.safe_load(SCHEDULE_YAML.read_text(encoding="utf-8")) or {}
    return {str(k): str((v or {}).get("cron") or "").strip()
            for k, v in (data.get("schedules") or {}).items()}


def _registry_slot_exprs() -> dict[str, str]:
    """注册表 → {时段: window_expr}（走生产 loader，顺带验 _SLOT_TASK_ID_PREFIX 约定）。"""
    return api_server._load_schedule_crons()


RAW = _raw_schedules()
REG = _registry_slot_exprs()

# 对拍基准（周五/周六/周日/周一 × 盘前/盘中/盘后/深夜；含月末与月初=月频边界）
BASES = [
    dt.datetime(2026, 9, 11, 7, 30),    # 周五盘前
    dt.datetime(2026, 9, 11, 10, 3),    # 周五盘中
    dt.datetime(2026, 9, 11, 21, 45),   # 周五盘后（nightly 档边界后）
    dt.datetime(2026, 9, 12, 2, 30),    # 周六凌晨
    dt.datetime(2026, 9, 13, 3, 0),     # 周日 03:00（weekend_calibration APScheduler=周日?）
    dt.datetime(2026, 9, 14, 3, 0),     # 周一 03:00
    dt.datetime(2026, 9, 30, 23, 59),   # 月末深夜（月频档边界）
    dt.datetime(2026, 10, 1, 9, 0),     # 月初 09:00（monthly_static 触发瞬间）
    dt.datetime(2026, 2, 1, 10, 0),     # 2 月短月（月频档 + 长间隔）
]


def cron_first_hit(expr: str, base: dt.datetime) -> dt.datetime | None:
    """croniter 首个命中时刻（'|' 多段取最近、6 段剥秒位——与生产/闸同口径）。"""
    from croniter import croniter

    base = base.replace(second=0, microsecond=0)
    best = None
    for seg in str(expr or "").split("|"):
        seg = seg.strip()
        parts = seg.split()
        if len(parts) == 6:
            seg = " ".join(parts[1:])
            parts = seg.split()
        if len(parts) != 5:
            continue
        try:
            nxt = croniter(seg, base).get_next(dt.datetime)
        except (ValueError, KeyError, TypeError):
            continue
        if best is None or nxt < best:
            best = nxt
    return best


def beyond_legacy_scan_window(expr: str, base: dt.datetime) -> bool:
    """真·下次触发是否落在旧实现 8 天扫描上限之外。

    旧实现在此情形静默返回 ""（不是解析分歧，是扫描上限），对拍另案
    test_monthly_gap_beyond_legacy_scan_window_is_now_reported 单独锁定。
    """
    nxt = cron_first_hit(expr, base)
    gap = None if nxt is None else nxt - base.replace(second=0, microsecond=0)
    return gap is not None and gap > dt.timedelta(minutes=8 * 24 * 60 - 1)


def dow_field_values(field: str) -> set[int]:
    """cron dow 字段 → 数值集合（区间/列表/步进展开；'*'=周一~周日全集）。

    数值语义由调用方决定：schedule.yaml=APScheduler（0=周一，与 datetime.weekday()
    同序），注册表 window_expr=标准 cron（0=周日）。
    """
    field = str(field).strip()
    if field == "*":
        return set(range(7))
    out: set[int] = set()
    for part in field.split(","):
        part = part.strip()
        if not part:
            continue
        if part.startswith("*/"):
            step = int(part[2:])
            out.update(d for d in range(7) if step and d % step == 0)
        elif "-" in part:
            a, b = (int(x) for x in part.split("-", 1))
            out.update(range(a, b + 1))
        else:
            out.add(int(part) % 7)
    return out


def test_dow_bearing_slots_are_the_15_expected() -> None:
    """受 dow 口径影响面基线（15/21）——真源扩缩容时提醒对拍覆盖面复核。"""
    bearing = {k for k, v in RAW.items() if v.split()[-1] != "*"}
    assert len(RAW) == 21, f"schedule.yaml 时段数漂移：{len(RAW)}"
    assert len(bearing) == 15, sorted(bearing)


def test_croniter_available() -> None:
    """croniter 是仓内既有依赖（闸/周历共用）——缺席则对拍无意义，直接 fail。"""
    import croniter  # noqa: F401


# ---------------------------------------------------------------------------
# 对拍①：同一（口径归一后）表达式，新 vs 旧在 9 个固定基准下逐字相同
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", sorted(REG))
def test_new_impl_matches_legacy_on_normalized_expr(name: str) -> None:
    expr = REG[name]
    if expr.split()[-1] == "*":
        # 无 dow 字段 → 口径归一是恒等映射，注册表表达式=schedule.yaml 表达式
        assert expr == legacy_load_schedule_crons()[name], f"{name} 无 dow 却漂移"
    checked = 0
    for base in BASES:
        if beyond_legacy_scan_window(expr, base):
            continue  # 旧实现扫描上限外空显示（另案锁定），不属解析分歧
        checked += 1
        got = api_server._next_cron_run(expr, base=base)
        want = legacy_next_cron_run(expr, base)
        assert got == want, f"{name} @{base:%Y-%m-%d %H:%M}({expr}) 新={got!r} 旧={want!r}"
    assert checked, f"{name} 全部基准被跳过 = 对拍空跑（真源间隔超 8 天？）"


@pytest.mark.parametrize("base", BASES, ids=[f"{b:%m%d-%H%M}" for b in BASES])
def test_matcher_equivalence_holds_for_every_slot(base: dt.datetime) -> None:
    """基准维度反向对拍：同一时刻 21 个时段全体一致（任一小时/周字段形态都覆盖）。"""
    checked = 0
    for name, expr in REG.items():
        if beyond_legacy_scan_window(expr, base):
            continue
        checked += 1
        assert api_server._next_cron_run(expr, base=base) == legacy_next_cron_run(expr, base), name
    assert checked >= 20, f"基准 {base} 有效对拍仅 {checked} 条，覆盖不足"


# ---------------------------------------------------------------------------
# 对拍②：真源 ↔ 注册表逐字段一致，差异只允许落在 dow（漂移哨兵）
# ---------------------------------------------------------------------------
def test_registry_exprs_cover_schedule_yaml_without_gap() -> None:
    assert set(REG) == set(RAW), f"面板槽位↔真源漂移 新={set(REG) - set(RAW)} 缺={set(RAW) - set(REG)}"


def test_registry_differs_from_truth_only_in_dow_field() -> None:
    """注册表 window_expr = schedule.yaml（剥秒）+ dow 归一，别无其他改写。

    若生成器或真源漂移（除 dow 外的字段变化），本断言先炸——面板读注册表的前提。
    """
    for name, raw in RAW.items():
        legacy_side = legacy_load_schedule_crons()[name]  # 剥秒后的 5 段
        reg = REG[name]
        assert len(legacy_side.split()) == len(reg.split()) == 5, f"{name} 字段数漂移"
        a, b = legacy_side.split(), reg.split()
        assert a[:4] == b[:4], f"{name} 非 dow 字段漂移 {legacy_side!r} vs {reg!r}"
        if a[4] == "*":
            assert b[4] == "*", f"{name} 通配 dow 被改写：{legacy_side!r} vs {reg!r}"
        else:
            assert a[4] != b[4], f"{name} 带 dow 却未归一（口径再次分叉前兆）：{reg!r}"


def test_registry_dow_is_normalized_apscheduler_weekdays() -> None:
    """dow 归一算术对拍：注册表数值在标准口径下指同一批真实工作日。"""
    for name, raw in RAW.items():
        aps, std = raw.split()[-1], REG[name].split()[-1]
        if aps == "*":
            continue
        assert dow_field_values(std) == {(d + 1) % 7 for d in dow_field_values(aps)}, \
            f"{name} {aps} → {std}"


@pytest.mark.parametrize("name", sorted(REG))
def test_expr_is_parsable_by_croniter(name: str) -> None:
    """注册表表达式必须 croniter 可解（生成器↔消费器契约，闸同源表达式故同样受益）。"""
    from croniter import croniter

    expr = REG[name]
    croniter(expr.split("|")[0].strip(), dt.datetime(2026, 9, 11, 7, 30))


# ---------------------------------------------------------------------------
# 对拍③：改造前 vs 改造后在真实真源上的差异面（意图锁定）
# ---------------------------------------------------------------------------
def _fires_within_day(solve, expr: str, day_start: dt.datetime) -> bool:
    """day_start 之后首个触发是否落在当日（按日判定，分钟级档也能整周遍历）。"""
    first = solve(expr, day_start)
    return first is not None and first < day_start + dt.timedelta(days=1)


def test_weekday_bearing_slots_now_land_on_intended_weekdays() -> None:
    """带 dow 的 15 个时段：修复后触发日集合=APScheduler 原意（0-4=周一~周五 / 0=周一）。

    同测试顺手复算改造前（真源原表达式 + 旧匹配器）的触发日集，钉死"旧集≠原意集"——
    旧实现按"0=周日"解读 → 工作日档多跑周日、漏跑周五；weekend_* 两档整体偏到周日。
    """
    monday = dt.datetime(2026, 9, 7, 0, 0)  # 周一 00:00
    legacy_crons = legacy_load_schedule_crons()
    checked = 0
    for name, raw in RAW.items():
        if raw.split()[-1] == "*":
            continue
        checked += 1
        # APScheduler dow（0=周一）与 datetime.weekday() 同序 → 真源集合即原意集合
        want_days = dow_field_values(raw.split()[-1])
        new_days = {d for d in range(7) if _fires_within_day(
            cron_first_hit, REG[name], monday + dt.timedelta(days=d))}
        old_days = {d for d in range(7) if _fires_within_day(
            legacy_scan, legacy_crons[name], monday + dt.timedelta(days=d))}
        assert new_days == want_days, (
            f"{name} 真源 '{raw}' 应为周{'、'.join(_CN_WEEKDAY[d] for d in sorted(want_days))}，"
            f"新实现实得周{'、'.join(_CN_WEEKDAY[d] for d in sorted(new_days))}")
        assert old_days != want_days, (
            f"{name} 旧实现触发日集与真源原意相同 → 本测试失效（真源口径变了？请复核 C-4 裁定）")
    assert checked == 15, f"带 dow 时段数漂移：{checked}"


def test_legacy_weekend_slots_reported_sunday_new_reports_monday() -> None:
    """具体事故形态：weekend_calibration（真源 '00 3 * * 0'，APScheduler 0=周一）。"""
    base = dt.datetime(2026, 9, 9, 12, 0)  # 周三
    old = legacy_next_cron_run(RAW["weekend_calibration"], base)       # 直读真源，0 被当周日
    new = api_server._next_cron_run(REG["weekend_calibration"], base)  # 注册表 1=周一
    assert old == "3 天后（09-13 03:00）", old  # 09-13=周日（面板比周历早一天）
    assert new == "4 天后（09-14 03:00）", new  # 09-14=周一 ✓ 与周历/闸一致
    sunday = dt.datetime(2026, 9, 13, 2, 0)
    assert api_server._next_cron_run(REG["weekend_calibration"], base=sunday) == \
        "1 天后（09-14 03:00）"


def test_wildcard_dow_slots_output_unchanged_after_fix() -> None:
    """无 dow 的 6 个时段：改造前后输出逐字不变（修复零附带影响）。"""
    legacy_crons = legacy_load_schedule_crons()
    checked = 0
    for name, raw in RAW.items():
        if raw.split()[-1] != "*":
            continue
        for base in BASES:
            if beyond_legacy_scan_window(legacy_crons[name], base):
                continue
            checked += 1
            assert api_server._next_cron_run(REG[name], base=base) == \
                legacy_next_cron_run(legacy_crons[name], base), f"{name} @{base}"
    assert checked >= 24, f"有效比对仅 {checked} 条，覆盖不足"


def test_monthly_gap_beyond_legacy_scan_window_is_now_reported() -> None:
    """旧实现 8 天扫描上限外静默空显示；croniter 无上限，报真实日期（改进面）。"""
    base = dt.datetime(2026, 2, 1, 10, 0)  # 下次=3-1 09:00（27 天 23 小时后）
    assert legacy_next_cron_run(RAW["monthly_static"], base) == ""
    assert api_server._next_cron_run(REG["monthly_static"], base=base) == "27 天后（03-01 09:00）"


# ---------------------------------------------------------------------------
# 读取侧：注册表缺席/损坏 → 降级空表（端点不炸，与改造前读 schedule.yaml 同语义）
# ---------------------------------------------------------------------------
def test_loader_returns_registry_exprs_in_production() -> None:
    assert REGISTRY_YAML.exists(), f"注册表缺席：{REGISTRY_YAML}（面板下次调度将空显示）"
    assert REG and all(REG.values()), "注册表 window_expr 不得为空/缺槽"
    assert len(REG) == len(RAW), f"loader 收表 {len(REG)} 条 ≠ 真源 {len(RAW)} 条"
    assert api_server._SCHEDULE_CRON == REG


@pytest.mark.parametrize("break_how", ["missing", "corrupt", "no_entities", "foreign_source"])
def test_loader_degrades_to_empty_table(break_how: str, tmp_path, monkeypatch) -> None:
    entities = [{
        "task_id": "data_slot_pre_market",
        "schedule_truth_source": "src/zephyr/data/config/schedule.yaml",
        "window_expr": "30 8 * * 1-5",
    }]
    if break_how == "missing":
        path = tmp_path / "resource_profile_registry.yaml"
    elif break_how == "corrupt":
        path = tmp_path / "resource_profile_registry.yaml"
        path.write_text("entities: [ {未闭合\n", encoding="utf-8")
    elif break_how == "no_entities":
        path = tmp_path / "resource_profile_registry.yaml"
        path.write_text("generated_from: src/zephyr/data/config/schedule.yaml\n", encoding="utf-8")
    else:
        path = tmp_path / "resource_profile_registry.yaml"
        path.write_text(
            yaml.safe_dump({"entities": [
                {**entities[0], "schedule_truth_source": "src/other/thing.ps1"},
                {"task_id": "manual_entry", "window_expr": "0 1 * * *"},
                {"task_id": "data_slot_no_expr", "schedule_truth_source": "schedule.yaml"},
            ]}),
            encoding="utf-8",
        )
    monkeypatch.setattr(api_server, "_REPO", tmp_path)
    assert api_server._load_schedule_crons() == {}, f"{break_how} 未降级为空表"


def test_three_tier_readable_str_format_preserved_for_callers() -> None:
    """调用方（面板"下次调度"列）依赖三档中文串形态——改造后逐档保持。"""
    import re

    cases = {
        dt.datetime(2026, 9, 11, 8, 20): r"^\d+ 分钟后（\d{2}:\d{2}）$",          # <1h
        dt.datetime(2026, 9, 11, 6, 0): r"^\d+ 小时后（\d{2}:\d{2}）$",           # 1~24h
        dt.datetime(2026, 9, 12, 9, 0): r"^\d+ 天后（\d{2}-\d{2} \d{2}:\d{2}）$",  # ≥1d
    }
    for base, pattern in cases.items():
        s = api_server._next_cron_run("30 8 * * 1-5", base=base)
        assert re.match(pattern, s), f"基准 {base} 串形态走样：{s!r}"


def test_endpoint_degrades_to_empty_string_on_bad_expr() -> None:
    """失败语义与改造前一致：空/None/字段数非法 → ""（端点空显示，绝不抛）。"""
    for bad in ("", "   ", None, "5 段都缺", "* * * * * * *", "abc"):
        assert api_server._next_cron_run(bad) == "", bad


def test_six_field_expr_is_second_stripped_like_the_gate() -> None:
    """6 段（秒 分 时 日 月 周）剥秒位后求解——与 expand_windows 同口径。"""
    base = dt.datetime(2026, 9, 11, 8, 59)  # 周五 08:59
    assert api_server._next_cron_run("*/10 15-25 9 * * 1-5", base=base) == "16 分钟后（09:15）"


def test_multi_segment_expr_takes_nearest_segment() -> None:
    """'|' 多段（注册表窗档形态）取最近一段，与闸的按段展开同源语义。"""
    base = dt.datetime(2026, 9, 11, 8, 0)
    assert api_server._next_cron_run("0 21 * * 1-5|30 8 * * 1-5", base=base) == \
        "30 分钟后（08:30）"


def test_no_hardcoded_cron_or_weekday_table_left_in_endpoint() -> None:
    """C-4 清零断言：api_server 内不得再留自写 cron 字段匹配器/位表/工作日常量。"""
    src = (_PROJECT_ROOT / "src" / "zephyr" / "frontend" / "dashboard" / "api_server.py").read_text(
        encoding="utf-8")
    body = src[src.index("def _load_schedule_crons"):src.index("def _load_tasks_meta")]
    for token in ("def field_match", "8 * 24 * 60", "weekday() + 1", "for offset in range("):
        assert token not in body, f"旧 cron 件残留：{token}"
    assert "croniter" in body, "解析真源应为 croniter（与闸/周历同口径）"
    assert "resource_profile_registry.yaml" in body, "表达式真源须为注册表 window_expr"
    assert 'path = _REPO / "src" / "zephyr" / "data" / "config" / "schedule.yaml"' not in body, \
        "端点不得再直读 schedule.yaml（绕过 dow 归一层=第 3 份口径）"
