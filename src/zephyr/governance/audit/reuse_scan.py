# [BLUEPRINT] MOD-GOV-REUSE-SCAN | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §裁定480-C2 reuse_scan
# [MODULE] zephyr.governance.audit.reuse_scan
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib（json/pathlib）；zephyr.shared.infra.process_pool（run_subprocess_hidden——trae_067 铁律2 CREATE_NO_WINDOW 统一子进程入口，BARE-SUBPROCESS 合规）
# [CONSUMERS] session_worktree.session_worktree_start（裁定#480 C-2：注册成功后打印同类半成品在途提示）；任何"先查再建"调用方
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯只读零写（git status / 文件存在性 / dead json 读取，绝不落任何盘面改动）；
#   三源 fail-open（git 不可用/目录缺失/单 json 损坏=跳过该源，不抛不阻断）；
#   路径归一化 posix 相对（Windows 反斜杠兼容）；
#   worktree 源只在"主区不存在该路径"时报（主分支 checkout 的既有文件存在于每个
#   worktree 是常态，不是在途半成品——防误报刷屏）；支持排除本会话 worktree（调用方
#   刚建的文件不是别人的半成品）；判据查盘面不查 HEAD（裁定#480 原理性红线：
#   预检判据查盘面——git status 本身就是盘面实况）
# [MODIFY-GUARD] zephyr.governance.audit.reuse_scan
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 三源各自吞异常（fail-open 降级为该源零结果）；函数级无 raise（调用方 session_worktree_start 只打印不阻断）；返回空 list=无同类在途
# [TESTS] tests/governance/test_reuse_scan.py
# [A_module] module_id=MOD-GOV-REUSE-SCAN | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 按需调用的只读扫描库（session 启动挂接+会话显式调用，非 cron/非 daemon）
"""reuse_scan —— 先查再建：新资产开工前扫描同类半成品在途（裁定#480 C-2）。

病根：AI 会话开工新文件前不看盘面实况，同类文件已在暂存区/其他活跃 worktree/
提交队列死信袋里半成品在途也照样重建——制造重复件、对撞 claim、死信积压三连。
处方（裁定#480 C-2）：三处只读扫描，开工前给一行提示（不阻断——渐进收紧第一档）：

  1. ``git status --porcelain``（暂存区/工作区同名或同基名文件在途）
  2. 活跃 worktree（``.aidrafts/*/`` 同路径文件——别的会话正在干同一件事）
  3. 死信袋（``.runtime/commit_queue/dead/*.json`` 的 files 字段命中——
     前人干过同一件事但落地失败，先读 dead_reason 再决定复用或重建）

原理性红线（裁定#480）：预检判据查盘面不查 HEAD——git status / 目录存在性 /
dead json 全是盘面实况，绝不用 git log/HEAD 快照做"是否有人做过"的判据（时序倒置）。

用法::

    from zephyr.governance.audit.reuse_scan import scan_similar_work
    hits = scan_similar_work(["src/zephyr/governance/audit/reuse_scan.py"], repo_root)
    # hits: [{"source": "dead_letter", "path": "...", "hint": "qid=... dead_reason=..."}, ...]

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: target_paths 目标路径清单
#   code: target_paths
# - id: I2
#   name: repo_root 仓库根
#   code: repo_root
# 层: 算法
# - id: A1
#   name_zh: git status 盘面扫描
#   name_en: scan_git_status
#   intro: porcelain -uall 同路径/同基名匹配
# - id: A2
#   name_zh: 活跃 worktree 同路径扫描
#   name_en: scan_worktrees
#   intro: .aidrafts/*/ 存在且主区不存在（防误报闸）
# - id: A3
#   name_zh: 死信袋 files 字段匹配
#   name_en: scan_dead_letters
#   intro: dead/*.json files[].path 精确命中（只读）
# I1 --> A1
# I1 --> A2
# I1 --> A3
# I2 --> A1
# I2 --> A2
# I2 --> A3
# A1 --> O1
# A2 --> O1
# A3 --> O1
# 层: 输出
# - id: O1
#   name: hits [{source, path, hint}]
#   code: return hits
    # [/ALGO_FLOW]
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

__all__: Final = ["scan_similar_work"]


def _norm_rel(p: str | Path, repo_root: Path) -> str:
    """路径归一化为 posix 相对（绝对路径尽量折算相对 repo_root；跨根绝对路径原样 posix 化）。"""
    s = str(p).strip().replace("\\", "/")
    if not s:
        return ""
    ap = Path(s)
    if ap.is_absolute():
        try:
            s = ap.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            s = ap.as_posix().lstrip("/")
    return s


def _scan_git_status(targets: set[str], basenames: set[str], repo_root: Path) -> list[dict]:
    """源①：git status 盘面——同名（同路径）或同基名文件在暂存区/工作区。

    fail-open：git 不可用/非 git 环境（如 tmp_path 假仓未 init）返回空。
    判据=porcelain 输出（盘面实况），status 码透传进 hint。
    子进程走 run_subprocess_hidden（trae_067 铁律2 CREATE_NO_WINDOW 统一入口）。
    """
    try:
        from zephyr.shared.infra.process_pool import (
            run_subprocess_hidden,  # noqa: PLC0415 — 惰性装载（BARE-SUBPROCESS 统一入口）
        )

        r = run_subprocess_hidden(
            # -uall：untracked 展开到文件级（默认目录级折叠会把同基名新文件藏进目录条目）
            ["git", "status", "--porcelain", "-uall"],
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(repo_root),
        )
    except Exception:  # noqa: BLE001 — git 不可用/池故障=该源零结果（fail-open）
        return []
    if r.returncode != 0:
        return []
    out: list[dict] = []
    for line in r.stdout.splitlines():
        if not line.strip() or len(line) < 4:
            continue
        status_code = line[:2].strip()
        # porcelain 重命名形态 "R  old -> new" 取 new；其余取去空格路径段
        raw_path = line[3:].strip()
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", 1)[1].strip()
        norm = raw_path.replace("\\", "/")
        if norm in targets:
            out.append({"source": "git_status", "path": norm, "hint": f"盘面在途（git status={status_code or '??'}）"})
        elif Path(norm).name in basenames:
            out.append(
                {"source": "git_status", "path": norm, "hint": f"同基名在途（git status={status_code or '??'}）"}
            )
    return out


def _scan_worktrees(targets: set[str], repo_root: Path, exclude_sids: set[str]) -> list[dict]:
    """源②：活跃 worktree（.aidrafts/*/）同路径文件——别的会话正在干同一件事。

    防误报闸：仅当主区 repo_root/<path> 不存在时报——主分支 checkout 的既有文件
    存在于每个 worktree 是常态（不是在途半成品）。排除本会话自己的 worktree
    （调用方刚建的/将建的文件不是"别人的半成品"）。
    """
    drafts = repo_root / ".aidrafts"
    if not drafts.is_dir():
        return []
    out: list[dict] = []
    for wt in sorted(drafts.iterdir()):
        if not wt.is_dir() or wt.name in exclude_sids or wt.name.startswith("_"):
            continue
        for norm in sorted(targets):
            if (wt / norm).exists() and not (repo_root / norm).exists():
                out.append(
                    {"source": "worktree", "path": norm, "hint": f"活跃 worktree .aidrafts/{wt.name}/ 存在同路径文件"}
                )
    return out


def _scan_dead_letters(targets: set[str], repo_root: Path) -> list[dict]:
    """源③：提交队列死信袋（.runtime/commit_queue/dead/*.json）files 字段命中（只读）。

    命中=前人干过同一件事但落地失败——hint 带 qid + dead_reason，调用方开工前
    应先读死信按处方修（复用）而不是盲目重建。单 json 损坏跳过（fail-open）。
    """
    dead_dir = repo_root / ".runtime" / "commit_queue" / "dead"
    if not dead_dir.is_dir():
        return []
    out: list[dict] = []
    for jf in sorted(dead_dir.glob("*.json")):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        qid = str(data.get("qid") or jf.stem)
        reason = str(data.get("dead_reason") or "unknown")
        files = data.get("files") or []
        if not isinstance(files, list):
            continue
        for f in files:
            norm = _norm_rel(f.get("path", "") if isinstance(f, dict) else str(f), repo_root)
            if norm and norm in targets:
                out.append(
                    {
                        "source": "dead_letter",
                        "path": norm,
                        "hint": f"死信袋 qid={qid} dead_reason={reason[:80]}（开工前先读死信按处方修）",
                    }
                )
    return out


def scan_similar_work(
    target_paths: list[str],
    repo_root: str | Path,
    *,
    exclude_worktree_sids: list[str] | None = None,
) -> list[dict]:
    """先查再建：对 target_paths 三源扫描同类半成品在途（纯只读，fail-open 不抛）。

    Args:
        target_paths: 本任务将建/将改的文件路径（相对或绝对；绝对路径折算相对 repo_root）。
        repo_root: 仓库根（测试注入 tmp_path 假仓的入口）。
        exclude_worktree_sids: 排除的 worktree 会话名（调用方传自己的 sid，防自报）。

    Returns:
        ``[{source, path, hint}]``——source ∈ git_status / worktree / dead_letter；
        空 list = 盘面无同类在途。三源各自 fail-open（git 不可用/目录缺失/
        单 json 损坏=该源零结果，绝不抛异常阻断调用方）。
    """
    root = Path(repo_root)
    targets = {_norm_rel(p, root) for p in target_paths if str(p).strip()}
    targets = {k for k in targets if k}
    if not targets:
        return []
    basenames = {Path(k).name for k in targets}
    exclude = set(exclude_worktree_sids or [])
    hits: list[dict] = []
    hits.extend(_scan_git_status(targets, basenames, root))
    hits.extend(_scan_worktrees(targets, root, exclude))
    hits.extend(_scan_dead_letters(targets, root))
    return hits
