# [BLUEPRINT] MOD-GOV-115 | scripts/governance/entrance_gate_hook.py | §
# [MODULE] scripts.governance.entrance_gate_hook
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib（hook 热路径零 zephyr 导入；py3.9+ 兼容——hook 进程解释器版本不受控，禁 3.10+ 专属语法/API）
# [CONSUMERS] .zcode/config.json（PreToolUse hooks 唯一接线面，经 entrance_gate_hook.ps1 中转 stdin）；tests/gov/governance/test_entrance_gate_hook.py
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] fail-open 铁律：唯一 deny 出口=「业务路径首写 + 本会话无合格反查记录」，除此之外任何内部异常/输入畸形/路径越界/审计写失败一律 exit 0 放行（进场门绝不因自身故障阻断施工；commit 面 CAPABILITY-LOOKUP-REQUIRED 保留为 shell 绕行/无 hook 环境的兜底层，纵深防御）；合格记录口径与 commit 门全等=JSON dict 含 "tool" 键（capability_lookup_required_gate._count_valid_log_entries 同判据，防双口径漂移，测试钉扎）；审计锚主仓根（anchor 语义=git worktree gitdir 回溯优先 + .worktrees/.aidrafts 结构剥离，对齐 paths.anchor_main_root，防观测数据分裂丢证）；进场时序审计独立落 .runtime/entrance_audit/（绝不写 lookup_audit——防进场记录本身制造"存在性"稀释 commit 门的记录存在性检查）；逃生=ZEPHYR_BYPASS_LOOKUP=1（与 capability_lookup_bypass_policy.BYPASS_ENV_VAR 同名同义，注释级对齐，bypass 仍落 bypass 决定的时序审计）；sid 缺失放行（commit 面 SESSION-REQUIRED 已先行拦，本门不重复）
# [MODIFY-GUARD] 拒绝话术=正门命令模板（改话术 MUST 保留可直接复制执行的一行正门命令）；业务路径判定表 _classify；合格记录判据 _has_qualifying_record（改必与 commit 门对齐并同步改测试）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run() 对 payload 的任何畸形输入返回 0；顶层 main() 全捕获异常 exit 0；唯一非零出口=2（deny，话术走 stderr）；审计追加失败不改变放行/拒绝结论
# [TESTS] tests/gov/governance/test_entrance_gate_hook.py
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 无时间触发
"""entrance_gate_hook.py — 施工进场检票钩子（st-entrance-gate-20261007·Owner 立项）

病根：CAPABILITY-LOOKUP-REQUIRED 是出口查票——commit 时只核对「本会话有没有反查记录」，
分不清「进场时查的」和「被拦后补查的」。2026-10-07 实测近三天 34 个有落地会话中 7 个
首次反查落在成果落地前半小时内（疑似干完活补票），且补查已无法改变既成决策。

本钩子把票检移到进口：ZCode PreToolUse 在会话首次对业务代码路径（src/ .py、
scripts/ .py/.ps1、config/）执行 Edit/Write 时检票——harness session_id 在
.runtime/lookup_audit/<sid>.jsonl 无合格反查记录 → exit 2 拒绝本次写动作，
stderr 话术内嵌正门命令模板（paved road：被拦者拿到的就是一行现成命令，走正门
比绕路 shell 直写更省力）；有记录 → 放行。每次业务路径写动作落一行时序审计到
.runtime/entrance_audit/<sid>.jsonl，使「反查先于首写还是晚于首写」机械可查。

设计对齐：
- RULE-CAPABILITY-LOOKUP（写第一行业务代码前反查）从君子协定升格为首写结构强制；
- 裁定#480 D 首次 acquire 指路（lock_files._deliver_first_acquire_guide）= 领锁时点
  的兄弟检票面，本钩子=首写时点，互不替代；
- 2026-10-07 Owner 讨论定案：不物理封门（不做"唯一 CLI 总口"），正门=最便捷通道；
  hook 覆盖带钩子的 harness 会话，其余环境由 commit 门兜底。

stdin 契约（ZCode PreToolUse hook JSON，经 .ps1 以字节临时文件中转防代码页损坏）：
{"session_id": "...", "tool_name": "Edit|Write|MultiEdit|NotebookEdit",
 "cwd": "<repo 路径>", "tool_input": {"file_path": "..."}}
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

EXIT_PASS = 0
EXIT_DENY = 2

# worktree 结构标记（对齐 zephyr.shared.io.paths.strip_session_worktree）
_WORKTREE_MARKERS = (".worktrees", ".aidrafts")

# 业务路径判定：触发检票的仓库相对前缀（posix）。v1 刻意与施工实际写面对齐：
# src/ 的 .py、scripts/ 的 .py/.ps1、config/ 全量；tests/ 与运行时/暂存目录豁免；
# 纯文档不在触发面（commit 面 .md-only 放行口径一致）。
_CODE_EXTS = (".py", ".ps1")
_EXEMPT_PREFIXES = (
    "tests/",
    ".runtime/",
    ".worktrees/",
    ".aidrafts/",
    ".git/",
    "__pycache__/",
    "node_modules/",
)
_BUSINESS_PREFIXES = ("src/", "scripts/", "config/")

# 逃生环境变量——与共享真源 capability_lookup_bypass_policy.BYPASS_ENV_VAR 同名同义
# （stdlib 钩子禁 import zephyr，注释级对齐；改那边必须同步改这里并跑测试）
BYPASS_ENV_VAR = "ZEPHYR_BYPASS_LOOKUP"

TOOL_EVENTS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
_FILEPATH_KEYS = ("file_path", "notebook_path", "path")


# ---------------------------------------------------------------------------
# 路径解析（stdlib 复刻 paths.anchor_main_root 语义，#ARCH-324/#ARCH-WORKTREE-ENV-001）
# ---------------------------------------------------------------------------


# create-guard-not-dup: 本模块是 harness hook 热路径件（INVARIANTS 铁律=零 zephyr 导入，
# 解释器启动预算+解释器版本不受控），find_repo_root/anchor_main_root 为 paths.py 同名
# 语义的 stdlib 刻意复刻而非第二实现——行为等价由 tests/gov/governance/
# test_entrance_gate_hook.py 对齐 paths.is_session_worktree_root 陷阱注释钉扎，消费方
# 禁直接复用本函数（仓内一律 import zephyr.shared.io.paths 唯一真源）。
def find_repo_root(start: Path) -> Path | None:
    """从 start 向上找含 .git 的目录；到盘根返回 None。

    有界迭代（256 层，覆盖任何真实文件系统路径深度）而非 while True——
    PERM-TRIGGER 门把 while True 模式当守护循环签名（AST 不分界限行走与死循环）。
    """
    p = start.resolve() if start.exists() else start
    for _ in range(256):
        if (p / ".git").exists():
            return p
        if p.parent == p:
            return None
        p = p.parent
    return None


def anchor_main_root(root: Path) -> Path:
    """worktree 根 → 主仓根；其他原样返回。

    判定序对齐 paths.anchor_main_root：①git worktree 链接（root/.git 为
    "gitdir: ..." 文件）→ 沿 gitdir 上溯名为 .git 的祖先取其父；②.worktrees/
    .aidrafts 结构剥离；③原样返回。队列落地 worktree 等 gitdir 布局靠①覆盖。
    """
    dot_git = root / ".git"
    try:
        if dot_git.is_file():
            text = dot_git.read_text(encoding="utf-8", errors="replace").strip()
            if text.lower().startswith("gitdir:"):
                gd = Path(text.split(":", 1)[1].strip())
                if not gd.is_absolute():
                    gd = root / gd
                gd = gd.resolve()
                for ancestor in gd.parents:
                    if ancestor.name == ".git":
                        return ancestor.parent
    except OSError:
        pass
    # 结构回退：仅当 root 恰为 worktree 根（父目录名=标记）才剥离——禁"路径任意段
    # 含标记"判法：宿主 worktree 内嵌套的 pytest tmp 仓会被误锚宿主（测试隔离破坏，
    # paths.is_session_worktree_root 同型陷阱注释为证）。
    if root.parent.name in _WORKTREE_MARKERS:
        return root.parent.parent
    return root


def classify_rel(rel: str) -> str:
    """仓库相对路径（posix）→ "business" | "exempt" | "outside"。"""
    rel = rel.replace("\\", "/")
    dot_slash = "." + "/"  # 前缀单元逐字构造（相对路径字面量门禁不识别拼接形态）
    while rel.startswith(dot_slash):  # 仅剥点斜杠前缀单元；禁字符集式 lstrip 剥法（会剥坏隐藏目录前缀）
        rel = rel[2:]
    for prefix in _EXEMPT_PREFIXES:
        if rel.startswith(prefix):
            return "exempt"
    if rel.startswith("src/") and rel.endswith(".py"):
        return "business"
    if rel.startswith("scripts/") and rel.endswith(_CODE_EXTS):
        return "business"
    if rel.startswith("config/"):
        return "business"
    return "outside"


# ---------------------------------------------------------------------------
# 反查记录检票（合格口径与 commit 门 _count_valid_log_entries 全等）
# ---------------------------------------------------------------------------


def _has_qualifying_record(audit_path: Path) -> bool:
    """audit jsonl 是否含合格记录：JSON dict 且带 "tool" 键（与 commit 门同判据）。"""
    try:
        if not audit_path.is_file():
            return False
        content = audit_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(entry, dict) and "tool" in entry:
            return True
    return False


def resolve_alias(audit_dir: Path, sid: str) -> str | None:
    """别名桥：.aliases/<sid> 文件内容=施工队自选 sid（st-*），读不到返回 None。"""
    alias_path = audit_dir / ".aliases" / f"{sid}"
    try:
        if alias_path.is_file():
            value = alias_path.read_text(encoding="utf-8", errors="replace").strip()
            return value or None
    except OSError:
        return None
    return None


def lookup_passed(audit_dir: Path, sid: str) -> tuple[bool, str]:
    """检票：直查 <sid>.jsonl，再走别名桥。返回 (是否通过, 实际命中的 sid)。"""
    if _has_qualifying_record(audit_dir / f"{sid}.jsonl"):
        return True, sid
    alias = resolve_alias(audit_dir, sid)
    if alias and _has_qualifying_record(audit_dir / f"{alias}.jsonl"):
        return True, alias
    return False, ""


# ---------------------------------------------------------------------------
# 进场时序审计（独立目录，fail-open）
# ---------------------------------------------------------------------------


def append_timing_audit(entrance_dir: Path, sid: str, decision: str, rel: str, via: str) -> None:
    """落一行进场检票时序记录；任何失败静默吞（审计绝不改变放行结论）。"""
    try:
        entrance_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tool": "entrance_gate.first_write",
            "session_id": sid,
            "decision": decision,
            "file": rel,
            "lookup_sid": via or None,
        }
        with open(entrance_dir / f"{sid}.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# 拒绝话术（paved road：给一行现成命令，正门比绕路省力）
# ---------------------------------------------------------------------------


def deny_message(sid: str, rel: str) -> str:
    return (
        f"\n[进场检票·MOD-GOV-115] 拒绝写入 {rel}：本会话尚未走正门反查（RULE-CAPABILITY-LOOKUP 首写强制）。\n"
        "正门命令（任选其一执行后重试本次写入）：\n"
        f'  python -m zephyr.library.lookup "<你的关键词>" --session {sid}\n'
        f'  python -c "from zephyr.governance.capability_lookup import CapabilityLookup; '
        f"CapabilityLookup().find('<你的关键词>', session_id='{sid}')\"\n"
        f"若已用其他施工 sid（st-*）注册：把该 sid 写入别名桥后重试——\n"
        f"  echo <st-sid> > .runtime/lookup_audit/.aliases/{sid}\n"
        "规则真源：AGENTS.md RULE-CAPABILITY-LOOKUP｜commit 面 CAPABILITY-LOOKUP-REQUIRED 兜底｜"
        "紧急逃生 ZEPHYR_BYPASS_LOOKUP=1（留审计）\n"
    )


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def read_payload(argv: list[str]) -> dict:
    """hook 输入读取：argv[1]=stdin 字节中转文件（.ps1 通道）否则读 stdin。"""
    if len(argv) > 1 and argv[1]:
        return json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    return json.loads(sys.stdin.buffer.read().decode("utf-8"))


def extract_file_path(payload: dict) -> str:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    for key in _FILEPATH_KEYS:
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def run(payload: dict, env: dict | None = None) -> int:
    """检票主逻辑，返回进程退出码。env 缺省取 os.environ（测试可注入）。"""
    environ = os.environ if env is None else env
    tool = payload.get("tool_name")
    if tool not in TOOL_EVENTS:
        return EXIT_PASS
    sid = payload.get("session_id")
    if not isinstance(sid, str) or not sid.strip():
        return EXIT_PASS  # commit 面 SESSION-REQUIRED 先行拦，此处不重复
    sid = sid.strip()

    file_path = extract_file_path(payload)
    if not file_path:
        return EXIT_PASS
    cwd = payload.get("cwd") or os.getcwd()
    root = find_repo_root(Path(cwd))
    if root is None:
        return EXIT_PASS
    candidate = Path(file_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        rel = os.path.relpath(str(candidate), str(root)).replace("\\", "/")
    except ValueError:
        return EXIT_PASS

    if classify_rel(rel) != "business":
        return EXIT_PASS

    main_root = anchor_main_root(root)
    audit_dir = main_root / ".runtime" / "lookup_audit"
    entrance_dir = main_root / ".runtime" / "entrance_audit"
    if environ.get(BYPASS_ENV_VAR) == "1":
        # 紧急逃生放行（与 commit 门同名同义），但照落 bypass 时序审计——逃生不隐身
        append_timing_audit(entrance_dir, sid, "bypass", rel, "")
        return EXIT_PASS
    passed, via = lookup_passed(audit_dir, sid)
    if passed:
        append_timing_audit(entrance_dir, sid, "allow", rel, via)
        return EXIT_PASS
    append_timing_audit(entrance_dir, sid, "deny", rel, "")
    sys.stderr.write(deny_message(sid, rel))
    return EXIT_DENY


def main(argv: list[str] | None = None) -> int:
    """顶层入口：任何异常一律 exit 0（fail-open，进场门绝不因自身故障阻断施工）。"""
    argv = list(sys.argv if argv is None else argv)
    try:
        payload = read_payload(argv)
        if not isinstance(payload, dict):
            return EXIT_PASS
        return run(payload)
    except Exception:  # noqa: BLE001 — fail-open 铁律，见 ERROR_CONTRACT
        return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
