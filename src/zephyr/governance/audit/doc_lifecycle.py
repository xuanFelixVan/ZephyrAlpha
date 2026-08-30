# [BLUEPRINT] MOD-GOV-043 | src/zephyr/governance/audit/doc_lifecycle.py | §
# [MODULE] zephyr.governance.audit.doc_lifecycle
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] scripts/ops_guard.py（guard_recycle/prune_recycle_bin 统一回收站）
# [CONSUMERS] zephyr.governance.audit.reconciliation_registry（GATE-WORKING-DOCS reconciler）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 永不物理删除（归档=guard_recycle 进回收站 30 天）；ttl: permanent 永不进观察；观察清单 SSoT=.runtime/archive_watchlist.json
# [MODIFY-GUARD] 状态机转移条件（WATCH_GRACE_SECONDS/INACTIVE_THRESHOLD_SECONDS）变更需同步本文件测试
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 评估异常→fail-open 返回 report 含 error 键（归档永不因异常执行）
# [TESTS] tests/governance/audit/test_doc_lifecycle.py
# [A_module] module_id=MOD-GOV-043 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name_zh: docs/_working 文档集
#   name_en: working_docs
#   fields: .md/.csv/.yaml/.yml/.json（排除 README.md）
# - id: I2
#   name_zh: 观察清单 SSoT
#   name_en: watchlist
#   fields: .runtime/archive_watchlist.json（state/first_seen/baseline_mtime/ghost_refs）
# 层: 处理
# - id: A1
#   name_zh: 引用提取+路径分级
#   name_en: extract_and_classify
#   desc: markdown 链接/反引号/纯文本路径三类提取；短命路径（.worktrees/.runtime/data 等）断裂不计分
# - id: A2
#   name_zh: 状态机评估
#   name_en: evaluate
#   desc: permanent 豁免；task_bound+（durable 幽灵>0 或 30 天零活跃）→watch；watch 满 7 天→归档；有生命迹象→复活
# 层: 输出
# - id: O1
#   name_zh: 归档动作
#   name_en: archive
#   desc: guard_recycle 进 .runtime/recycle_bin/<ts>/（30 天可恢复，零物理删除）
# - id: O2
#   name_zh: 评估报告
#   name_en: report
#   fields: watched/revived/archived/pruned 计数 + details
# 边: I1-->A1; I2-->A2; A1-->A2; A2-->O1; A2-->O2
# [/ALGO_FLOW]
"""
doc_lifecycle.py — 文档生命周期状态机（#ARCH-RECONCILER-AUTO-DELETE-GOV-001 治本核心）

替代旧 GATE-WORKING-DOCS 的"幽灵引用即归档"一枪毙命机制。

设计原理（第一性原理）：自动化代理的判定准确率恒 <100%，故删除决策必须
可逆且有宽限期——先标记不动手，7 天自证期，有生命迹象自动复活，到期
才归档，归档 = 30 天回收站可恢复。

四机制改动（对照旧机制"死板"病灶）：
1. 判定权还给文档声明：ttl: permanent 永不进观察名单（裁定书/SOP 类）；
   失效引用降级为辅助信号，不再单独定罪。
2. 路径分级：.worktrees//.runtime//data//.aidrafts/ 等短命路径断裂永远
   不作为死亡证据（历史记录型引用）；src//docs//scripts//tests/ 等长命
   路径断裂才计分。
3. 自动复活通道：观察期内文档被编辑（mtime 前移）/失效引用恢复 → 自动
   回健康态，零人工环节。
4. 归档≠删除：move 进 30 天回收站（ops_guard.guard_recycle），git 侧不再
   auto-commit 删除（I-GOV-2 合规）；回收站到期才物理删除。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ref 参数
#   fields: 参数 ref，类型注解 str
#   code: doc_lifecycle.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: content 参数
#   fields: 参数 content，类型注解 str
#   code: doc_lifecycle.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: source 参数
#   fields: 参数 source，类型注解 Path
#   code: doc_lifecycle.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 Path
#   code: doc_lifecycle.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① classify_path
#   name_en: classify_path
#   intro: 路径分级：短命（ephemeral）断裂不计分；长命（durable）断裂才计分。
#   desc: 路径分级：短命（ephemeral）断裂不计分；长命（durable）断裂才计分。；源码 L229-L237
#   inputs: ref
#   outputs: str
# - id: A2
#   name_zh: ② extract_refs
#   name_en: extract_refs
#   intro: 提取文档引用的项目内路径（去重保序）。
#   desc: 提取文档引用的项目内路径（去重保序）。；源码 L240-L254
#   inputs: content
#   outputs: list[str]
# - id: A3
#   name_zh: ③ is_ghost
#   name_en: is_ghost
#   intro: 双重路径解析判定失效引用（先相对文档目录，再相对项目根）。
#   desc: 双重路径解析判定失效引用（先相对文档目录，再相对项目根）。；源码 L257-L267
#   inputs: ref source project_root
#   outputs: bool
# - id: A4
#   name_zh: ④ read_ttl
#   name_en: read_ttl
#   intro: 读取 frontmatter ttl；无 frontmatter/无 ttl 字段 → 'undeclared'。
#   desc: 读取 frontmatter ttl；无 frontmatter/无 ttl 字段 → 'undeclared'。；源码 L277-L286
#   inputs: path
#   outputs: str
# - id: A5
#   name_zh: ⑤ load_watchlist
#   name_en: load_watchlist
#   intro: 读取观察清单；不存在/损坏 → 空表（fail-open 重建）。
#   desc: 读取观察清单；不存在/损坏 → 空表（fail-open 重建）。；源码 L306-L315
#   inputs: repo_root
#   outputs: dict[str, WatchEntry]
# - id: A6
#   name_zh: ⑥ save_watchlist
#   name_en: save_watchlist
#   intro: 原子写观察清单（tmp+replace）。
#   desc: 原子写观察清单（tmp+replace）。；源码 L318-L329
#   inputs: repo_root entries
#   outputs: 返回值
# - id: A7
#   name_zh: ⑦ evaluate_lifecycle
#   name_en: evaluate_lifecycle
#   intro: 状态机主入口（每个 post-commit 周期调用一次）。
#   desc: 状态机主入口（每个 post-commit 周期调用一次）。 转移规则： - 不在清单 + ttl≠permanent +（durable 幽灵引用>0 或 零活跃>30 天）→…；源码 L361-L450
#   inputs: repo_root now
#   outputs: LifecycleReport
#   （注：A7 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.governance.audit.reconciliation_registry（GATE-WORKING-DOCS reconciler）
# - id: O2
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.governance.audit.reconciliation_registry（GATE-WORKING-DOCS reconciler）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> O1
"""

from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# 常量（裁定参数：宽限期 7 天——2026-08-14 用户裁定）
# ---------------------------------------------------------------------------

#: 观察期宽限（秒）——7 天
WATCH_GRACE_SECONDS = 7 * 24 * 3600

#: 零活跃候选阈值（秒）——30 天无任何编辑才具备候选资格
INACTIVE_THRESHOLD_SECONDS = 30 * 24 * 3600

#: 观察清单 SSoT（机器可读，AI 会话/门禁均可消费）
WATCHLIST_REL = ".runtime/archive_watchlist.json"

#: 短命路径前缀——断裂永远不作为死亡证据（历史记录型引用）
EPHEMERAL_PREFIXES = (
    ".worktrees/",
    ".aidrafts/",
    ".runtime/",
    "data/",
)

#: 吞噬兼容形态（2026-08-14 第三轮统筹实证：引用提取正则首字符限 [a-zA-Z]，
#: `.runtime/` 被吞成 `runtime/`、`.worktrees/`→`worktrees/`——无前导点形态
#: 必须同判 ephemeral，否则短命路径豁免被正则吞噬击穿）
#: 安全性：项目根无 runtime//worktrees//aidrafts/ 实体目录（均带点），src/zephyr/runtime/
#: 等嵌套路径首段非 runtime/ 不误伤。
EPHEMERAL_COMPAT_PREFIXES = (
    "worktrees/",
    "aidrafts/",
    "runtime/",
)

#: 支持的文档类型（与旧机制一致）
SUPPORTED_EXTS = frozenset({".md", ".csv", ".yaml", ".yml", ".json"})

# ---------------------------------------------------------------------------
# 引用提取（模式与 audit_broken_links.py 同源：md 链接/反引号/纯文本路径）
# ---------------------------------------------------------------------------

_MD_LINK_RE = re.compile(r"\]\(([^)]+\.(?:py|yaml|yml|md))\)", re.IGNORECASE)
_BACKTICK_RE = re.compile(r"`([^`]+\.(?:py|yaml|yml|md))`", re.IGNORECASE)
_TEXT_PATH_RE = re.compile(
    r"(?<![a-zA-Z0-9/])([a-zA-Z][\w\-./]*?/[\w\-]+\.(?:md|yaml|yml|json|py|ps1|sh|toml|txt|csv))\b"
)


def _looks_like_path(ref: str) -> bool:
    """宁漏勿误的路径形态过滤（与旧机制一致）。"""
    if "/" not in ref and "\\" not in ref:
        return False
    if any(c in ref for c in (" ", "*", "?", "[", "(", "{")):
        return False
    if "..." in ref:
        return False
    return True


def classify_path(ref: str) -> str:
    """路径分级：短命（ephemeral）断裂不计分；长命（durable）断裂才计分。"""
    norm = ref.replace("\\", "/")
    if norm.startswith("./"):
        norm = norm[2:]
    for prefix in EPHEMERAL_PREFIXES + EPHEMERAL_COMPAT_PREFIXES:
        if norm.startswith(prefix):
            return "ephemeral"
    return "durable"


def extract_refs(content: str) -> list[str]:
    """提取文档引用的项目内路径（去重保序）。"""
    refs: list[str] = []
    for pattern in (_MD_LINK_RE, _BACKTICK_RE, _TEXT_PATH_RE):
        for m in pattern.finditer(content):
            r = m.group(1).replace("\\", "/")
            if _looks_like_path(r):
                refs.append(r)
    seen: set[str] = set()
    unique: list[str] = []
    for r in refs:
        if r not in seen:
            seen.add(r)
            unique.append(r)
    return unique


def is_ghost(ref: str, source: Path, project_root: Path) -> bool:
    """双重路径解析判定失效引用（先相对文档目录，再相对项目根）。"""
    if ref.startswith(("http://", "https://", "mailto:", "#")):
        return False
    if ref.startswith("file:///"):
        ref = ref[len("file:///") :]
    p1 = (source.parent / ref).resolve()
    if p1.exists():
        return False
    p2 = (project_root / ref).resolve()
    return not p2.exists()


# ---------------------------------------------------------------------------
# frontmatter ttl 读取
# ---------------------------------------------------------------------------

_TTL_RE = re.compile(r"^ttl:\s*([A-Za-z_\-]+)", re.MULTILINE)


def read_ttl(path: Path) -> str:
    """读取 frontmatter ttl；无 frontmatter/无 ttl 字段 → 'undeclared'。"""
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:2048]
    except OSError:
        return "undeclared"
    if not head.startswith("---"):
        return "undeclared"
    m = _TTL_RE.search(head)
    return m.group(1).strip() if m else "undeclared"


# ---------------------------------------------------------------------------
# 观察清单 SSoT
# ---------------------------------------------------------------------------


@dataclass
class WatchEntry:
    """单文档观察条目。"""

    state: str  # watch（观察中；archived 不出清单——已离工作区）
    first_seen: int
    baseline_mtime: float  # 进入观察时的 mtime 基线（复活判定用）
    last_checked: int
    ghost_refs: list[str] = field(default_factory=list)
    reason: str = ""


def load_watchlist(repo_root: Path) -> dict[str, WatchEntry]:
    """读取观察清单；不存在/损坏 → 空表（fail-open 重建）。"""
    p = repo_root / WATCHLIST_REL
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return {k: WatchEntry(**v) for k, v in data.get("entries", {}).items()}
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


def save_watchlist(repo_root: Path, entries: dict[str, WatchEntry]) -> None:
    """原子写观察清单（tmp+replace）。"""
    p = repo_root / WATCHLIST_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "updated_at": int(time.time()),
        "entries": {k: vars(v) for k, v in sorted(entries.items())},
    }
    tmp = p.with_suffix(f".{int(time.time())}.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


# ---------------------------------------------------------------------------
# 状态机评估
# ---------------------------------------------------------------------------


@dataclass
class LifecycleReport:
    """一次评估的结果。"""

    scanned: int = 0
    skipped_permanent: int = 0
    watched: list[str] = field(default_factory=list)
    revived: list[str] = field(default_factory=list)
    archived: list[str] = field(default_factory=list)
    pruned_recycle: int = 0
    error: str = ""


def _iter_working_docs(working_dir: Path) -> list[Path]:
    """枚举 docs/_working 下支持的文档（排除 README.md 定位说明）。"""
    if not working_dir.is_dir():
        return []
    out: list[Path] = []
    for p in working_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS and p.name != "README.md":
            out.append(p)
    return sorted(out)


def evaluate_lifecycle(repo_root: Path, *, now: int | None = None) -> LifecycleReport:
    """状态机主入口（每个 post-commit 周期调用一次）。

    转移规则：
    - 不在清单 + ttl≠permanent +（durable 幽灵引用>0 或 零活跃>30 天）→ watch
    - watch + 有生命迹象（mtime 前移 或 durable 幽灵清零）→ 复活出清单
    - watch + 满 7 天宽限 → guard_recycle 归档（零物理删除）
    - 顺带 prune_recycle_bin（30 天到期条目清理）
    """
    repo_root = Path(repo_root)
    now = now if now is not None else int(time.time())
    report = LifecycleReport()

    # 回收站到期清理（顺带，零新增调度）
    try:
        from scripts.ops_guard import guard_recycle, prune_recycle_bin

        report.pruned_recycle = prune_recycle_bin(repo_root=repo_root)
    except Exception as e:  # noqa: BLE001 — 回收站清理失败不阻断主流程
        report.error = f"prune_recycle_bin: {e}"
        return report

    entries = load_watchlist(repo_root)
    working_dir = repo_root / "docs" / "_working"
    docs = _iter_working_docs(working_dir)
    present_rels = {str(p.relative_to(repo_root)).replace("\\", "/") for p in docs}

    # 清单自愈：文件已不在工作区（被人工/其他途径处理）→ 出清单
    for rel in [k for k in entries if k not in present_rels]:
        del entries[rel]

    for doc in docs:
        rel = str(doc.relative_to(repo_root)).replace("\\", "/")
        ttl = read_ttl(doc)
        if ttl == "permanent":
            report.skipped_permanent += 1
            entries.pop(rel, None)  # permanent 永不观察（已在清单的赦免）
            continue

        report.scanned += 1
        try:
            content = doc.read_text(encoding="utf-8", errors="replace")
            mtime = doc.stat().st_mtime
        except OSError:
            continue

        durable_ghosts = [
            r for r in extract_refs(content) if classify_path(r) == "durable" and is_ghost(r, doc, repo_root)
        ]
        inactive = (now - mtime) > INACTIVE_THRESHOLD_SECONDS
        has_signal = bool(durable_ghosts) or inactive

        entry = entries.get(rel)
        if entry is None:
            # 健康 → 观察（task_bound/undeclared 且有信号才进）
            if has_signal:
                entries[rel] = WatchEntry(
                    state="watch",
                    first_seen=now,
                    baseline_mtime=mtime,
                    last_checked=now,
                    ghost_refs=durable_ghosts[:20],
                    reason=(f"durable_ghosts={len(durable_ghosts)}, inactive={inactive}"),
                )
                report.watched.append(rel)
            continue

        # 观察中 → 复活判定：mtime 前移（被编辑）或信号清零
        if mtime > entry.baseline_mtime or not has_signal:
            del entries[rel]
            report.revived.append(rel)
            continue

        # 观察中 → 归档判定：满 7 天宽限
        entry.last_checked = now
        entry.ghost_refs = durable_ghosts[:20]
        if now - entry.first_seen >= WATCH_GRACE_SECONDS:
            try:
                guard_recycle(
                    doc,
                    repo_root=repo_root,
                    reason=f"doc_lifecycle 满 7 天观察期归档（ghosts={len(durable_ghosts)}, inactive={inactive}）",
                )
                del entries[rel]
                report.archived.append(rel)
            except Exception as e:  # noqa: BLE001 — 单文件归档失败不拖垮整批
                report.error = f"archive {rel}: {e}"

    save_watchlist(repo_root, entries)
    return report


if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
