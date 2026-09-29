# [BLUEPRINT] MOD-AUTO-L11-REGISTRY | docs/_working/fullflow_mining/03_promotion_ab/02_ab_league.md | 第1节
# [MODULE] scripts.backtest.league_registry
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] yaml; zephyr.shared.io.file_utils; zephyr.shared.utils.time_utils
# [CONSUMERS] scripts/backtest/league_archive.py（读组席位）; scripts/backtest/league_restore.py;
#   scripts/backtest/league_monthly_snapshot.py（读成员清单）; Owner 终审门（6 个月挂单消费位）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 加载/校验纯读（load/validate 不落盘）;
#   挂单回写唯一入口=schedule_review（CAS safe_write_text，禁裸写注册表热文件）;
#   判定器复用 promotion_combo_gate 本体零修改——本模块只登记挂单不执行判定;
#   阈值不复制进本注册表（尺真源=config/standards.yaml，防第二真源漂移）
# [MODIFY-GUARD] config/league_registry.yaml（CAS 写，写后回读校验）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册表缺失→FileNotFoundError 上抛; schema 违规→validate 返回错误清单（不抛）;
#   组不存在→KeyError
# [TESTS] tests/backtest/test_league_registry.py
# [A_module] module_id=MOD-AUTO-L11-REGISTRY | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""league_registry — A/B 联赛注册表加载/校验/终审挂单 API（TC-11 件1，裁定#392 批）。

联赛生命周期轴（骨架 v1.1）：模拟竞争（A/B）站的组织台账。组席位 A~G 任意扩展；
状态机 champion | challenger | retired；判定窗=首组参赛日起 6 个月终审一次性
（月度快照留档、终审挂单经本模块 schedule_review 登记，判定执行仍归 Owner 门+组合门）。

用法（仓库根，Python 3.12）：
    python scripts/backtest/league_registry.py --check
    python scripts/backtest/league_registry.py --schedule-review --group A --note "满窗挂单"
"""

# create-guard-not-dup: 本件是回测联赛（F73 联赛 13 件批）的联赛注册表读写器，只服务 config/league_registry.yaml 回测域数据，与治理域各在册能力的注册表加载无实现或职责重叠，非第二真源
from __future__ import annotations

import argparse
import calendar
import json
import sys
from pathlib import Path

import yaml

# sys.path bootstrap（先例 scripts/governance/standards/standards_lib.py 的 _PROJECT_ROOT
# 范式——bootstrap 局部量不与真源 REPO_ROOT 同名）
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_PROJECT_ROOT), str(_PROJECT_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT
from zephyr.shared.utils.time_utils import now_utc_str  # noqa: E402

REGISTRY_PATH = REPO_ROOT / "config" / "league_registry.yaml"

ALLOWED_STATUS = ("champion", "challenger", "retired")

# noqa: m11-perm-manual-legitimate  M11豁免: 联赛台账按需调用的加载/挂单工具（--check/--schedule-review），非自动触发常驻


def load_registry(path: Path | str = REGISTRY_PATH) -> dict:
    """加载注册表原始 dict；文件缺失→FileNotFoundError；YAML 损坏→异常上抛。"""
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def validate_registry(data: dict) -> list[str]:
    """schema 校验，返回错误清单（空清单=通过）。纯函数，测试直喷。

    校验面：schema_version/title/review_policy 必备；groups 非空列表；每组 group_id 唯一、
    status 合法、joined_date/review_window 必备；成员引用为字符串清单。
    """
    errors: list[str] = []
    if not str(data.get("schema_version") or "").strip():
        errors.append("schema_version 缺失")
    if not str(data.get("title") or "").strip():
        errors.append("title 缺失")
    rp = data.get("review_policy")
    if not isinstance(rp, dict) or not rp:
        errors.append("review_policy 缺失或非 dict")
    else:
        if not isinstance(rp.get("window_months"), int) or rp.get("window_months", 0) <= 0:
            errors.append("review_policy.window_months 须为正整数")
        if not str(rp.get("judge") or "").strip():
            errors.append("review_policy.judge 缺失")
    groups = data.get("groups")
    if not isinstance(groups, list) or not groups:
        errors.append("groups 须为非空列表")
        return errors
    seen: set[str] = set()
    for g in groups:
        gid = str(g.get("group_id") or "").strip()
        if not gid:
            errors.append(f"组缺少 group_id: {g!r}")
            continue
        if gid in seen:
            errors.append(f"组 group_id 重复: {gid}")
        seen.add(gid)
        if g.get("status") not in ALLOWED_STATUS:
            errors.append(f"组 {gid} status 非法: {g.get('status')!r}（合法={ALLOWED_STATUS}）")
        if not str(g.get("joined_date") or "").strip():
            errors.append(f"组 {gid} joined_date 缺失")
        rw = g.get("review_window")
        if not isinstance(rw, dict) or not rw.get("start") or not rw.get("due"):
            errors.append(f"组 {gid} review_window.start/due 缺失")
        members = g.get("members")
        if members is not None and not isinstance(members, list):
            errors.append(f"组 {gid} members 须为列表")
    return errors


def get_group(data: dict, group_id: str) -> dict:
    """按 group_id 取组 dict；不存在→KeyError。"""
    for g in data.get("groups") or []:
        if str(g.get("group_id")) == group_id:
            return g
    raise KeyError(f"联赛组不存在: {group_id}")


def add_months(date_iso: str, months: int) -> str:
    """YYYY-MM-DD + N 个月 → YYYY-MM-DD（月末钳制：1/31+1 月=2/28/29）。纯函数。

    供判定窗 due 计算；日期解析失败→ValueError 上抛（fail-closed，不静默吞）。
    """
    date_part = date_iso.strip()[:10]
    y_str, m_str, d_str = date_part.split("-")
    y, m, d = int(y_str), int(m_str), int(d_str)
    total = (y * 12 + (m - 1)) + months
    ny, nm = divmod(total, 12)
    nm += 1
    last = calendar.monthrange(ny, nm)[1]
    return f"{ny:04d}-{nm:02d}-{min(d, last):02d}"


def register_member(
    group_id: str,
    strategy_id: str,
    note: str = "",
    path: Path | str = REGISTRY_PATH,
    *,
    registered_at: str | None = None,
) -> dict:
    """参赛入组唯一写入口：把 strategy_id 登记进组 members（幂等，已在组=原样返回）。

    CAS 写（safe_write_text + expected_base_sha256），写后回读核实；返回更新后的组 dict。
    入组语义（处方 02_ab_league.md 堵点 1）：首位参赛者=sim 现役幸存策略（禁编造），
    入 champion 初始席位组（A）；档案打包归 league_archive.py，本函数只登记席位。
    note/registered_at 留参仅作调用方审计口径，不落注册表（members=席位唯一真源）。
    """
    sid = str(strategy_id).strip()
    if not sid:
        raise ValueError("strategy_id 不能为空")
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    group = get_group(data, group_id)
    members = group.get("members")
    if members is None:
        members = group.setdefault("members", [])  # 引用挂载（禁 `or []` 重建列表——空清单 append 会落空）
    if sid in members:
        return group  # 幂等：已在组不重写
    members.append(sid)  # members=席位唯一真源（清单语义不裂生第二真源；登记时点留审计日志）
    new_text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    expected = content_sha256(raw)
    safe_write_text(p, new_text, expected_base_sha256=expected)
    # 写后进程外核实（宪法硬规则 13：写后核实）
    verify = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return get_group(verify, group_id)


def schedule_review(
    group_id: str,
    note: str = "",
    path: Path | str = REGISTRY_PATH,
    *,
    scheduled_at: str | None = None,
) -> dict:
    """挂 6 个月终审单：回写判定窗 review_scheduled/scheduled_at/note 字段。

    CAS 写（safe_write_text + expected_base_sha256），写后回读核实；返回更新后的组 dict。
    终审执行体不在此（判定器复用 promotion_combo_gate，Owner 门终裁）。
    """
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    group = get_group(data, group_id)
    rw = group.setdefault("review_window", {})
    rw["review_scheduled"] = True
    rw["scheduled_at"] = scheduled_at or now_utc_str()
    if note:
        rw["note"] = note
    new_text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    expected = content_sha256(raw)
    safe_write_text(p, new_text, expected_base_sha256=expected)
    # 写后进程外核实（宪法硬规则 13：写后核实）
    verify = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return get_group(verify, group_id)


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="A/B 联赛注册表工具（check/schedule-review）")
    ap.add_argument("--check", action="store_true", help="校验 league_registry.yaml schema")
    ap.add_argument("--registry", type=str, default=None, help="注册表路径（默认 config/league_registry.yaml）")
    ap.add_argument("--schedule-review", action="store_true", help="挂 6 个月终审单（写判定窗字段，CAS）")
    ap.add_argument("--group", type=str, default=None, help="挂单/入组目标组 ID")
    ap.add_argument("--note", type=str, default="", help="挂单备注")
    ap.add_argument(
        "--register-member",
        type=str,
        default=None,
        metavar="STRATEGY_ID",
        help="参赛入组：把指定 strategy_id 登记进 --group 组 members（CAS，幂等）",
    )
    args = ap.parse_args()

    reg = Path(args.registry) if args.registry else REGISTRY_PATH
    data = load_registry(reg)
    if args.check:
        errors = validate_registry(data)
        for g in data.get("groups") or []:
            rw = g.get("review_window") or {}
            print(
                f"{g.get('group_id')}: status={g.get('status')} joined={g.get('joined_date')} "
                f"due={rw.get('due')} scheduled={rw.get('review_scheduled')}"
            )
        print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False))
        return 1 if errors else 0
    if args.register_member:
        if not args.group:
            ap.error("--register-member 需要 --group")
        updated = register_member(args.group, args.register_member, note=args.note, path=reg)
        print(
            json.dumps(
                {"ok": True, "group": updated.get("group_id"), "members": updated.get("members")},
                ensure_ascii=False,
            )
        )
        return 0
    if args.schedule_review:
        if not args.group:
            ap.error("--schedule-review 需要 --group")
        updated = schedule_review(args.group, note=args.note, path=reg)
        print(
            json.dumps(
                {"ok": True, "group": updated.get("group_id"), "review_window": updated.get("review_window")},
                ensure_ascii=False,
            )
        )
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
