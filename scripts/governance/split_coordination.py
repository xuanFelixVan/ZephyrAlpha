# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §split_coordination
# [MODULE] scripts.governance.split_coordination
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib（argparse/pathlib）；yaml；SPLIT-COORDINATION gate（zephyr.gov_enforcement.commit_gates.split_coordination_gate，同 schema 消费方）
# [CONSUMERS] 拆分会话（begin/finish）、运维会话（status/sweep）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 声明单一写入方（本工具）；.runtime/coordination/active_splits.yaml 为运行时协调态（永不入 tracked 区）；begin 在动盘**之前**调用（协议时序）；幂等（同 dir 重复 begin=覆盖刷新）；原子写（临时文件+os.replace 带 EACCES 退避重试）
# [MODIFY-GUARD] 声明 schema（splits[].dir/mover_session/old_paths/new_root/declared_at）与 split_coordination_gate.py 同步变更
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 声明文件解析失败 → exit 2（fail-loud，status/begin 统一防御，红蓝 v3 P2-4 治本；文件不存在返回 [] 属正常）；begin 无 old_paths → exit 1（fail-closed，工具类零静默）
# [TESTS] tests/governance/commit_gates/test_split_coordination_gate.py（工具部分）
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-SPLIT-COORDINATION-001
# [CREATION-TOKEN] split-coordination-tool-20260913
# noqa: m11-perm-manual-legitimate  M11豁免: AI/运维会话按需调用的 permanent CLI runner（拆分协调声明登记台，非 cron/非 daemon/非常驻服务），由 SPLIT-COORDINATION gate 在 commit 事件链消费其声明
"""split_coordination — 拆分搬移协调声明工具（#ARCH-SPLIT-COORDINATION-001）

病根（2026-09-13 极限红蓝对抗 F5 100% 复现）：拆分者搬走 dir/*.md 后，并发编辑者
在旧平铺路径重建文件——单笔提交全合法，组合成 HEAD 双重存在（历史 651 处失效
路径引用事故根源）。commit 门禁缺"拆分进行中"跨会话信号，无法拦组合事故。

协议（机器强制，配合 SPLIT-COORDINATION gate）：
1. 拆分者动盘**前**：``begin`` 声明（old_paths 清单+新挂基点）——gate 开始拦
   他会话对 old_paths 的一切提交（mover 本人放行）。
2. 搬移+提交完成、消费方（编辑者等）全部 re-base 后：``finish`` 移除声明
   （拆除保护的正门——刻意不做"已落地自动失活"：落地=旧路径消失=重建风险
   开始，恰是保护最需存在的时点）。
3. 编辑者被 gate 拦截时按指引 re-base 到 new_root。
4. mover 弃单自愈：声明超 48h 陈旧 → gate 降级 warn 放行（防砖），
   ``sweep`` 可清扫陈旧声明。

用法::

    # 声明（自动扫描 dir 下平铺文件为 old_paths）
    python scripts/governance/split_coordination.py begin \\
        --session my-session --dir docs/_working/lab --new-root docs/_working/lab/a

    # 状态 / mover 收尾 / 清扫陈旧
    python scripts/governance/split_coordination.py status
    python scripts/governance/split_coordination.py finish --session my-session --dir docs/_working/lab
    python scripts/governance/split_coordination.py sweep
"""
from __future__ import annotations

import argparse
import os
import sys
import time as _time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[2]
try:  # #ARCH-324：worktree 内运行须锚主仓，使写入端与 gate 读端同源（主树/普通仓为恒等）
    from zephyr.shared.io.paths import anchor_main_root as _anchor

    _REPO = _anchor(_REPO)
except Exception:  # noqa: BLE001 — 锚定不可用退回本树（既有 fail-open 面）
    pass
DECL_PATH = _REPO / ".runtime" / "coordination" / "active_splits.yaml"


def _atomic_write_retry(path: Path, text: str) -> None:
    """原子写（临时文件+os.replace），EACCES 时 10/50/100ms 退避重试。

    session_registry WinError 5 教训（2026-09-13 治本 4d228f2d）：Windows 上
    json/yaml 被读方持有时 os.replace 报拒绝访问→写静默丢失。退避重试三次，
    仍失败则抛出（调用方 exit 1，工具类零静默）。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    last: OSError | None = None
    for delay_ms in (10, 50, 100):
        # 临时文件必须与目标同目录（os.replace 跨盘符 WinError 17；session_registry 同款教训域）
        tmp = path.parent / f".{path.name}.{os.getpid()}.tmp"
        try:
            tmp.write_text(text, encoding="utf-8")
            os.replace(tmp, path)
            return
        except OSError as e:
            last = e
            getattr(_time, "sleep")(delay_ms / 1000.0)  # 有界退避（3 次封顶，非常驻轮询）
        finally:
            tmp.unlink(missing_ok=True)
    raise last if last else OSError("atomic write failed")


def load_declarations() -> list[dict]:
    """load_declarations implementation."""
    if not DECL_PATH.exists():
        return []
    try:
        data = yaml.safe_load(DECL_PATH.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 红蓝 v3 P2-4：损坏态统一 fail-loud（原 status 裸 traceback 崩/begin 静默失效双副面孔）
        print(
            f"FAIL: 协调声明文件损坏（.runtime/coordination/active_splits.yaml），请修复或删除后重试（{type(e).__name__}）",
            file=sys.stderr,
        )
        sys.exit(2)
    return list((data or {}).get("splits") or []) if isinstance(data, dict) else []


def save_declarations(splits: list[dict]) -> None:
    """save_declarations implementation."""
    body = yaml.safe_dump(
        {"splits": splits}, allow_unicode=True, sort_keys=False, default_flow_style=False
    )
    _atomic_write_retry(DECL_PATH, f"# 拆分搬移协调声明（SPLIT-COORDINATION gate 消费；split_coordination.py 单一写入方）\n{body}")


def scan_flat_files(dir_rel: str) -> list[str]:
    """扫描 dir 下平铺文件（不含子目录）——FOLDER-CAPACITY 强制拆分场景的 old_paths。"""
    d = _REPO / dir_rel
    if not d.is_dir():
        return []
    return sorted(
        f"{dir_rel}/{p.name}".replace("\\", "/") for p in d.iterdir() if p.is_file()
    )


def _stale(entry: dict, max_age_h: float = 48.0) -> bool:
    """声明是否陈旧（declared_at 超过 max_age_h 小时）——mover 弃单判定（与 gate 同语义）。"""
    try:
        declared = datetime.fromisoformat(str(entry.get("declared_at") or ""))
    except ValueError:
        return False
    if declared.tzinfo is None:
        declared = declared.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - declared > timedelta(hours=max_age_h)


def cmd_begin(args: argparse.Namespace) -> int:
    """cmd_begin implementation."""
    if args.old_paths_file:
        old_paths = sorted(
            ln.strip().replace("\\", "/")
            for ln in Path(args.old_paths_file).read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        )
    else:
        old_paths = scan_flat_files(args.dir)
    if not old_paths:
        print(f"FAIL: {args.dir} 下无平铺文件可声明（或 --old-paths-file 为空）", file=sys.stderr)
        return 1

    splits = [s for s in load_declarations() if s.get("dir") != args.dir]  # 同 dir 幂等覆盖
    splits.append(
        {
            "dir": args.dir,
            "mover_session": args.session,
            "old_paths": old_paths,
            "new_root": args.new_root or "",
            "declared_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    save_declarations(splits)
    print(f"OK: 已声明拆分协调窗口 dir={args.dir} mover={args.session} old_paths={len(old_paths)} 条")
    print("    gate 将拦截他会话对上述旧路径的提交（mover 本人放行）；消费方 re-base 完成后 finish 收尾")
    return 0


def cmd_finish(args: argparse.Namespace) -> int:
    """cmd_finish implementation."""
    splits = load_declarations()
    entry = next((s for s in splits if s.get("dir") == args.dir), None)
    if entry is None:
        print(f"FAIL: {args.dir} 无活跃声明", file=sys.stderr)
        return 1
    if not args.force and entry.get("mover_session") != args.session:
        print(
            f"FAIL: {args.dir} 声明的 mover 是 {entry.get('mover_session')}，"
            f"{args.session} 无权 finish（mover 本人或 --force）",
            file=sys.stderr,
        )
        return 1
    save_declarations([s for s in splits if s.get("dir") != args.dir])
    print(f"OK: 已移除 {args.dir} 拆分声明（协调窗口关闭——确认消费方已全部 re-base）")
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    """cmd_status implementation."""
    splits = load_declarations()
    if not splits:
        print("无活跃拆分声明")
        return 0
    for s in splits:
        stale = _stale(s)
        print(
            f"dir={s.get('dir')} mover={s.get('mover_session')} "
            f"old_paths={len(s.get('old_paths') or [])} new_root={s.get('new_root') or '-'} "
            f"declared_at={s.get('declared_at', '?')} "
            f"[{'陈旧(弃单,gate 已降级 warn,可 sweep)' if stale else '进行中'}]"
        )
    return 0


def cmd_sweep(args: argparse.Namespace) -> int:
    """清扫陈旧声明（>max-age 小时弃单）——不按"已落地"清扫（落地=保护最需存在的时点）。"""
    splits = load_declarations()
    keep = [s for s in splits if not _stale(s, args.max_age)]
    removed = len(splits) - len(keep)
    if removed:
        save_declarations(keep)
    print(f"OK: sweep 清扫 {removed} 条陈旧声明（保留 {len(keep)} 条活跃）")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="拆分搬移协调声明工具（SPLIT-COORDINATION 协议）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_begin = sub.add_parser("begin", help="声明拆分协调窗口（动盘之前调用）")
    p_begin.add_argument("--session", required=True, help="拆分者会话名（mover_session）")
    p_begin.add_argument("--dir", required=True, help="被拆目录（仓库相对路径）")
    p_begin.add_argument("--new-root", default="", help="新挂基点（如 docs/_working/lab/a）")
    p_begin.add_argument("--old-paths-file", default="", help="旧路径清单文件（一行一条；缺省=自动扫描 dir 平铺文件）")
    p_begin.set_defaults(func=cmd_begin)

    p_fin = sub.add_parser("finish", help="移除声明（mover 收尾）")
    p_fin.add_argument("--session", required=True, help="会话名（须等于 mover_session）")
    p_fin.add_argument("--dir", required=True, help="被拆目录")
    p_fin.add_argument("--force", action="store_true", help="非 mover 强制收尾（运维清理）")
    p_fin.set_defaults(func=cmd_finish)

    p_st = sub.add_parser("status", help="列出活跃声明与陈旧状态")
    p_st.set_defaults(func=cmd_status)

    p_sw = sub.add_parser("sweep", help="清扫陈旧声明（mover 弃单 > max-age 小时）")
    p_sw.add_argument("--max-age", type=float, default=48.0, help="陈旧阈值（小时，默认 48）")
    p_sw.set_defaults(func=cmd_sweep)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
