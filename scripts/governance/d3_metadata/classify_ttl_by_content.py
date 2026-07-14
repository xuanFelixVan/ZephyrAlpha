# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/classify_ttl_by_content.py | §gate-15
# [MODULE] governance.d3_metadata.classify_ttl_by_content
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] _shared.frontmatter; _shared.constants
# [CONSUMERS] manual ttl audit; pre-rejudge content scan
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 基于内容关键词（标题+正文）判定 ttl，不依赖路径机械判定；输出三类清单供人工审查
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0; EXIT_ERROR=2
# [TTL] task_bound
"""基于内容关键词的 ttl 精细分类审查脚本。

与 backfill_ttl_metadata.py 的区别：
  - backfill：按 decision_tree（路径+doc_type）自动回填 ttl——执行工具
  - classify_by_content：按内容关键词（标题+正文信号）分类——审查工具，输出待定清单

判定逻辑（优先级从高到低）：
  1. 标题含 permanent 强信号词且不含 task_bound 强信号词 → permanent (high)
  2. 标题含 task_bound 强信号词且不含 permanent 强信号词 → task_bound (high)
  3. 标题信号冲突（同时含两类强信号词）→ pending
  4. 标题含灰色/待定词 → pending
  5. 标题无信号 → 看 doc_type 辅助判定
  6. 都无法判定 → pending

输出三类 CSV 到 docs/_working/ttl_content_audit/：
  - permanent_confirmed.csv
  - task_bound_confirmed.csv
  - pending_review.csv

Usage::

    # 全量扫描
    python scripts/governance/d3_metadata/classify_ttl_by_content.py

    # 限定子目录
    python scripts/governance/d3_metadata/classify_ttl_by_content.py docs/02_enterprise_architecture/
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 基于内容关键词的 ttl 精细分类审查脚本。
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""


import csv
import re
import sys
from pathlib import Path

import yaml as _yaml

# ── 路径设置 ──
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT  # noqa: E402
from _shared.frontmatter import parse_frontmatter  # noqa: E402

# ════════════════════════════════════════════════════════════════════════════
# 关键词分类体系（举一反三：从"蓝图/报告"两个例子扩展为系统性词表）
# ════════════════════════════════════════════════════════════════════════════

# ── permanent 强信号词：标题中出现 → 倾向永久 ──
# 依据：ttl_vocabulary.yaml values.permanent.applies_to + 文档类型语义
PERMANENT_SIGNALS: list[str] = [  # noqa: gate-vocab  # 关键词信号列表（非词表合法值副本；含 doc_type 值作信号词，语义关联非复制）
    # 治理核心
    "蓝图", "blueprint",
    "规则", "rule",
    "标准", "standard",
    "协议", "protocol",
    "政策", "policy",
    "宪章", "charter",
    "宪法", "constitution",
    # 架构核心
    "架构视图", "architecture view",
    "架构原则", "architecture principle",
    "不变量", "invariant",
    "约束", "constraint",
    "门禁", "gate",
    "裁定",  # 治理裁定（如 ARCH-REN-001）
    # 数据真源
    "词表", "vocabulary",
    "schema",
    "注册表", "registry", "register",
    "真源", "source of truth", "canonical",
    "元数据", "metadata",
    # 结构骨架
    "模板", "template",
    "索引", "index",
    "入口", "entry",
    "导航", "navigation",
    # 设计规格（非 service_spec 过程文档）
    "设计规格", "specification",
    "规格定义", "spec definition",
]

# ── task_bound 强信号词：标题中出现 → 倾向临时 ──
# 依据：ttl_vocabulary.yaml values.task_bound.applies_to + 过程性文档语义
TASK_BOUND_SIGNALS: list[str] = [
    # 过程记录
    "报告", "report",
    "记录", "record", "log", "日志",
    "变更记录", "changelog", "change log",
    "修复记录", "fix log",
    "迁移记录", "migration log",
    # 调研审计（过程性产出）
    "调研", "research", "investigation",
    "审计", "audit",  # 过程性审计产出（区别于 audit_report doc_type）
    "回顾", "retrospective",
    "复盘", "postmortem",
    # 施工过程
    "施工", "construction",
    "施工方案", "construction plan",
    "任务卡", "task card",
    "待办", "todo", "task list",
    # 临时产物
    "临时", "temporary", "temp",
    "笔记", "note",
    "草稿", "draft",
    "候选池", "candidate pool", "candidate",
    "提案", "proposal",
    "评估", "assessment",
    "清理", "cleanup",
    "交接", "handoff",
    "会话", "session",
]

# ── 灰色/待定词：标题中出现 → 需人工讨论 ──
# 依据：既可能是永久架构文档，也可能是临时过程文档
AMBIGUOUS_SIGNALS: list[str] = [
    "全景图", "panorama",  # 可能是蓝图（永久），也可能是快照报告（临时）
    "分析", "analysis",    # 架构分析=永久，调研分析=临时
    "总结", "summary",     # 年度总结=临时，架构总结=永久
    "概览", "overview",    # 架构概览=永久，项目概览=临时
    "能力定位书",           # 既像蓝图又像报告（用户指定案例）
    "能力定位",             # 同上
    "清单", "checklist",   # 注册表=永久，待办清单=临时
    "手册", "manual",      # 标准手册=永久，操作手册=临时
    "指南", "guide",       # 同上
    "导航图",              # 索引=永久，临时导航=临时
    "讨论", "discussion",  # 治理讨论=永久，草稿讨论=临时
    "方案",                # 设计方案=永久，施工方案=临时
    "对比", "comparison",  # 架构对比=永久，竞品对比=临时
    "规划", "roadmap",     # 战略规划=永久，任务规划=临时
    "矩阵", "matrix",      # 架构矩阵=永久，临时矩阵=临时
    "图谱", "graph",       # 知识图谱=永久，临时图谱=临时
]

# ── doc_type→ttl 映射（从 doc_type_vocabulary.yaml 动态加载）──
# 真源：doc_type_vocabulary.yaml values[].ttl_default
# 治本（2026-06-30）：消除原硬编码 PROCESS_DOC_TYPES / PERMANENT_DOC_TYPES 副本——词表变更只需改一处。
_DOC_TYPE_VOCAB_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards"
    / "_registry" / "vocabularies" / "doc_type_vocabulary.yaml"
)


def _load_doc_type_ttl_sets() -> tuple[set[str], set[str]]:
    """从 doc_type_vocabulary.yaml 动态构建 doc_type→ttl_default 映射。

    真源：doc_type_vocabulary.yaml values[].ttl_default
    消除原硬编码 PROCESS_DOC_TYPES / PERMANENT_DOC_TYPES 副本——词表变更只需改一处。
    """
    try:
        vocab = _yaml.safe_load(_DOC_TYPE_VOCAB_PATH.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        return set(), set()
    process_types: set[str] = set()
    permanent_types: set[str] = set()
    for entry in vocab.get("values", []):
        value = entry.get("value", "")
        ttl_default = entry.get("ttl_default", "")
        if ttl_default == "task_bound":
            process_types.add(value)
        elif ttl_default == "permanent":
            permanent_types.add(value)
    return process_types, permanent_types


PROCESS_DOC_TYPES, PERMANENT_DOC_TYPES = _load_doc_type_ttl_sets()

# ── 模糊 doc_type（不加入任何集合 → 标题无信号时进 pending）──
# log 等需结合标题内容判定，不单独靠 doc_type 判定

# ════════════════════════════════════════════════════════════════════════════
# 目录语义维度（目录路径本身即强信号）
# ════════════════════════════════════════════════════════════════════════════
# 按优先级排序：最具体的模式在前（如 */changes/ 优先于 docs/03_modules/）
# 匹配方式：contains（路径含子串即命中）
#
# 治本（2026-06-29）：路径列表从 directory_contract.yaml 动态加载，消除硬编码副本。
# 真源：directory_contract.yaml directory_zones.permanent.paths / temporary.paths / temporary.process_subdirs
# 仅保留 03_governance_reports/ 特殊规则硬编码（exempt_subdirs 中的过程性目录，契约未明确其 ttl）

_CONTRACT_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards"
    / "_registry" / "contracts" / "directory_contract.yaml"
)


def _load_dir_ttl_map() -> list[tuple[str, str, str]]:
    """从 directory_contract.yaml 动态构建目录→ttl 映射。

    真源：directory_contract.yaml directory_zones
    消除原硬编码 DIR_TTL_MAP 副本——路径变更只需改契约一处。

    特殊规则（硬编码，契约未明确）：
        03_governance_reports/ 是 permanent.exempt_subdirs 中的过程性目录，ttl=task_bound。
        其他 exempt_subdirs（00_overview_entry/ 等）是生成器专用，ttl=permanent（不列入此 map）。
    """
    try:
        contract = _yaml.safe_load(_CONTRACT_PATH.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        return []
    zones = contract.get("directory_zones", {})
    permanent_paths = zones.get("permanent", {}).get("paths", []) or []
    temporary_paths = zones.get("temporary", {}).get("paths", []) or []
    process_subdirs = zones.get("temporary", {}).get("process_subdirs", []) or []

    items: list[tuple[str, str, str]] = []
    # task_bound: temporary.paths（临时工作区）
    for p in temporary_paths:
        items.append((p, "task_bound", f"临时工作区（{p}）"))
    # task_bound: process_subdirs（过程性子目录，contains 模式带前导/）
    for sub in process_subdirs:
        sub_clean = sub.strip("/")
        items.append((f"/{sub_clean}/", "task_bound", f"过程性子目录（{sub_clean}/）"))
    # task_bound: 03_governance_reports/（特殊规则——permanent.exempt_subdirs 中的过程性目录）
    items.append((
        "docs/02_enterprise_architecture/03_governance_reports/",
        "task_bound",
        "治理报告目录（过程性：容量/调研/清理审查，permanent.exempt_subdirs 特殊规则）",
    ))
    # permanent: permanent.paths（永久区核心内容）
    for p in permanent_paths:
        items.append((p, "permanent", f"永久区路径（{p}）"))
    return items


DIR_TTL_MAP: list[tuple[str, str, str]] = _load_dir_ttl_map()


def classify_by_dir(rel_path: str) -> tuple[str, str] | None:
    """按目录语义判定 ttl。

    Returns:
        (ttl, reason) 或 None（目录无信号）。
    """
    for pattern, ttl, reason in DIR_TTL_MAP:
        if pattern in rel_path:
            return (ttl, f"目录语义: {reason}（匹配 {pattern}）")
    return None


# ════════════════════════════════════════════════════════════════════════════
# 内容提取
# ════════════════════════════════════════════════════════════════════════════

def extract_title(text: str, frontmatter: dict | None) -> str:
    """提取文档标题：优先 frontmatter.title，回退首个 # 标题，再回退文件名。"""
    if frontmatter and frontmatter.get("title"):
        title = str(frontmatter["title"]).strip().strip("\"'")
        if title:
            return title
    # 回退到首个 # 标题
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def extract_h1(text: str) -> str:
    """提取首个 H1 标题（用于关键词匹配，与 frontmatter title 分开）。"""
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def get_body_head(text: str, max_lines: int = 100) -> str:
    """提取正文前 N 行（frontmatter 之后）。"""
    # 跳过 frontmatter
    if text.startswith("---"):
        m = re.match(r"^---\s*\n.*?\n---\s*\n?", text, re.DOTALL)
        if m:
            body = text[m.end():]
        else:
            body = text
    else:
        body = text
    lines = body.split("\n")[:max_lines]
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════════
# 关键词匹配
# ════════════════════════════════════════════════════════════════════════════

def find_signals(text: str, signals: list[str]) -> list[str]:
    """在文本中查找信号词，返回命中的词列表（不区分大小写）。

    英文词用词边界匹配（防止 temp 匹配 template、log 匹配 catalog）；
    中文词用子串匹配（中文无词边界歧义）。
    """
    text_lower = text.lower()
    hits = []
    for s in signals:
        s_lower = s.lower()
        if re.search(r"[a-z]", s_lower):
            # 英文词：词边界匹配（支持复数 s）
            if re.search(r"\b" + re.escape(s_lower) + r"s?\b", text_lower):
                hits.append(s)
        else:
            # 中文词：子串匹配
            if s_lower in text_lower:
                hits.append(s)
    return hits


# ════════════════════════════════════════════════════════════════════════════
# 分类判定
# ════════════════════════════════════════════════════════════════════════════

def classify(
    title: str,
    h1: str,
    doc_type: str,
    body_head: str,
    current_ttl: str,
    rel_path: str,
) -> dict:
    """三维度综合判定 ttl 分类：目录语义 + 标题关键词 + doc_type。

    判定逻辑：
      A. 标题有强信号（permanent/task_bound）：
         - 目录一致或无信号 → 高置信
         - 目录冲突 → pending（真正歧义）
      B. 标题信号冲突或含灰色词：
         - 目录有信号 → 目录裁决（medium）
         - 目录无信号 → pending
      C. 标题无信号：
         - 目录有信号 → medium
         - doc_type 有信号 → medium
         - 都无 → pending

    Returns:
        dict with keys: suggested_ttl, confidence, key_signals, reason
    """
    # ── 维度1：目录语义 ──
    dir_result = classify_by_dir(rel_path)
    dir_ttl = dir_result[0] if dir_result else None
    dir_reason = dir_result[1] if dir_result else ""

    # ── 维度2：标题关键词 ──
    title_combined = f"{title} {h1}"
    perm_hits = find_signals(title_combined, PERMANENT_SIGNALS)
    task_hits = find_signals(title_combined, TASK_BOUND_SIGNALS)
    ambig_hits = find_signals(title_combined, AMBIGUOUS_SIGNALS)

    if perm_hits and task_hits:
        title_type, title_ttl = "conflict", None
    elif perm_hits:
        title_type, title_ttl = "strong", "permanent"
    elif task_hits:
        title_type, title_ttl = "strong", "task_bound"
    elif ambig_hits:
        title_type, title_ttl = "ambiguous", None
    else:
        title_type, title_ttl = "none", None

    # ── 维度3：正文辅助信号（仅记录）──
    body_perm = find_signals(body_head, PERMANENT_SIGNALS)
    body_task = find_signals(body_head, TASK_BOUND_SIGNALS)

    # 构建 key_signals
    signals_parts = []
    if dir_ttl:
        signals_parts.append(f"目录={dir_ttl}")
    if perm_hits:
        signals_parts.append(f"标题永久: {','.join(perm_hits)}")
    if task_hits:
        signals_parts.append(f"标题临时: {','.join(task_hits)}")
    if ambig_hits:
        signals_parts.append(f"标题灰色: {','.join(ambig_hits)}")
    if body_perm:
        signals_parts.append(f"正文永久: {','.join(body_perm[:3])}")
    if body_task:
        signals_parts.append(f"正文临时: {','.join(body_task[:3])}")
    key_signals = " | ".join(signals_parts) if signals_parts else "无信号"

    # ── 综合判定 ──

    # A. 标题有强信号
    if title_ttl is not None:
        if dir_ttl is None or dir_ttl == title_ttl:
            return {
                "suggested_ttl": title_ttl,
                "confidence": "high",
                "key_signals": key_signals,
                "reason": f"标题强信号({title_ttl})" +
                          (f"，目录一致" if dir_ttl == title_ttl else ""),
            }
        # 目录冲突——方向不对称处理
        if title_ttl == "task_bound" and dir_ttl == "permanent":
            # 永久区文件标题含过程性词——用 doc_type 进一步裁决（标题对 KE/架构文档不可靠）
            if doc_type and doc_type in PERMANENT_DOC_TYPES:
                # doc_type 是强永久类型（KE/blueprint/schema/architecture_view 等）
                # → doc_type 优先（KE 标题是章节名，架构文档标题含"报告"但本质永久）
                return {
                    "suggested_ttl": "permanent",
                    "confidence": "medium",
                    "key_signals": key_signals,
                    "reason": f"标题含过程性词但 doc_type={doc_type} 为永久类型，doc_type 优先于标题",
                }
            if doc_type and doc_type in PROCESS_DOC_TYPES:
                # doc_type 是过程性类型 → 确认为误放的过程性文件
                return {
                    "suggested_ttl": "task_bound",
                    "confidence": "medium",
                    "key_signals": key_signals,
                    "reason": f"标题+doc_type={doc_type} 均为过程性，位于永久区——过程性文件误放，建议移动到 docs/_working/",
                }
            # doc_type 模糊/缺失 → 需人工确认
            return {
                "suggested_ttl": "pending",
                "confidence": "low",
                "key_signals": key_signals,
                "reason": f"标题(task_bound)+目录(permanent)冲突，doc_type={doc_type or '缺失'}无法裁决——需人工确认是否误放",
            }
        # title_ttl == "permanent" and dir_ttl == "task_bound"
        # 过程性目录里的文件标题含永久词（如 changes/index.md 标题"索引"）
        # 跟随目录生命周期——目录是过程性的，其内文件也是过程性的
        return {
            "suggested_ttl": "task_bound",
            "confidence": "medium",
            "key_signals": key_signals,
            "reason": f"位于过程性目录，跟随目录语义（标题含永久词{perm_hits[:2] if perm_hits else []}但目录优先）",
        }

    # B. 标题冲突或灰色词
    if title_type in ("conflict", "ambiguous"):
        if dir_ttl is not None:
            return {
                "suggested_ttl": dir_ttl,
                "confidence": "medium",
                "key_signals": key_signals,
                "reason": f"标题{title_type}，目录裁决为{dir_ttl}: {dir_reason}",
            }
        else:
            ambig_detail = ""
            if title_type == "conflict":
                ambig_detail = f"冲突: 永久({','.join(perm_hits)}) vs 临时({','.join(task_hits)})"
            else:
                ambig_detail = f"灰色词: {','.join(ambig_hits)}"
            return {
                "suggested_ttl": "pending",
                "confidence": "low",
                "key_signals": key_signals,
                "reason": f"标题{ambig_detail}，无目录信号裁决",
            }

    # C. 标题无信号
    # C1. 过程性 doc_type 优先于目录（对齐 decision_tree Q2 > Q3）
    if doc_type and doc_type in PROCESS_DOC_TYPES:
        return {
            "suggested_ttl": "task_bound",
            "confidence": "medium",
            "key_signals": key_signals,
            "reason": f"标题无信号，doc_type={doc_type} 为过程性类型（优先于目录）",
        }

    # C2. 目录语义（含过程性目录 _working/changes 等 → task_bound；永久区 → permanent）
    if dir_ttl is not None:
        return {
            "suggested_ttl": dir_ttl,
            "confidence": "medium",
            "key_signals": key_signals,
            "reason": f"标题无信号，{dir_reason}",
        }

    # C3. 永久性 doc_type
    if doc_type and doc_type in PERMANENT_DOC_TYPES:
        return {
            "suggested_ttl": "permanent",
            "confidence": "medium",
            "key_signals": key_signals,
            "reason": f"标题无信号，doc_type={doc_type} 为永久性类型",
        }

    return {
        "suggested_ttl": "pending",
        "confidence": "low",
        "key_signals": key_signals,
        "reason": f"标题无信号，doc_type={doc_type or '缺失'}无法判定",
    }


# ════════════════════════════════════════════════════════════════════════════
# 主函数
# ════════════════════════════════════════════════════════════════════════════

CSV_FIELDS = [
    "relative_path", "current_ttl", "suggested_ttl", "confidence",
    "title", "doc_type", "key_signals", "reason",
]


def main() -> int:
    args = sys.argv[1:]
    path_args = [a for a in args if not a.startswith("-")]

    # 确定扫描范围
    if path_args:
        scan_dirs = [(REPO_ROOT / p).resolve() for p in path_args]
    else:
        scan_dirs = [REPO_ROOT / "docs"]

    # 收集 .md 文件
    md_files: list[Path] = []
    for scan_dir in scan_dirs:
        if scan_dir.is_file() and scan_dir.suffix == ".md":
            md_files.append(scan_dir)
        elif scan_dir.is_dir():
            md_files.extend(scan_dir.rglob("*.md"))

    if not md_files:
        print("OK: no .md files to classify")
        return EXIT_PASS

    # 分类
    permanent_rows: list[dict] = []
    task_bound_rows: list[dict] = []
    pending_rows: list[dict] = []

    for fpath in md_files:
        rel_path = str(fpath.relative_to(REPO_ROOT)).replace("\\", "/")
        try:
            text = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            pending_rows.append({
                "relative_path": rel_path,
                "current_ttl": "",
                "suggested_ttl": "pending",
                "confidence": "low",
                "title": "(读取失败)",
                "doc_type": "",
                "key_signals": "",
                "reason": "文件读取失败",
            })
            continue

        # 解析 frontmatter
        frontmatter, _ = parse_frontmatter(text) if text.startswith("---") else (None, text)
        doc_type = ""
        current_ttl = ""
        if frontmatter:
            doc_type = str(frontmatter.get("doc_type", "")).strip()
            current_ttl = str(frontmatter.get("ttl", "")).strip()

        title = extract_title(text, frontmatter)
        h1 = extract_h1(text)
        body_head = get_body_head(text)

        result = classify(title, h1, doc_type, body_head, current_ttl, rel_path)

        row = {
            "relative_path": rel_path,
            "current_ttl": current_ttl,
            "suggested_ttl": result["suggested_ttl"],
            "confidence": result["confidence"],
            "title": title[:100],
            "doc_type": doc_type,
            "key_signals": result["key_signals"],
            "reason": result["reason"],
        }

        if result["suggested_ttl"] == "permanent":
            permanent_rows.append(row)
        elif result["suggested_ttl"] == "task_bound":
            task_bound_rows.append(row)
        else:
            pending_rows.append(row)

    # 输出目录
    out_dir = REPO_ROOT / "docs" / "_working" / "ttl_content_audit"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 写 CSV
    def write_csv(filename: str, rows: list[dict]) -> Path:
        path = out_dir / filename
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            w.writeheader()
            w.writerows(rows)
        return path

    perm_path = write_csv("permanent_confirmed.csv", permanent_rows)
    task_path = write_csv("task_bound_confirmed.csv", task_bound_rows)
    pending_path = write_csv("pending_review.csv", pending_rows)

    # 统计报告
    total = len(md_files)
    print(f"\n{'=' * 70}")
    print(f"ttl 内容关键词分类报告")
    print(f"{'=' * 70}")
    print(f"  总扫描文件数          : {total}")
    print(f"  明确永久 (permanent)  : {len(permanent_rows)} ({len(permanent_rows)*100//total}%)")
    print(f"  明确临时 (task_bound) : {len(task_bound_rows)} ({len(task_bound_rows)*100//total}%)")
    print(f"  待定讨论 (pending)    : {len(pending_rows)} ({len(pending_rows)*100//total}%)")
    print(f"{'=' * 70}")
    print(f"\n输出文件：")
    print(f"  {perm_path}")
    print(f"  {task_path}")
    print(f"  {pending_path}")

    # 打印 pending 清单摘要（前 30 条）
    if pending_rows:
        print(f"\n{'─' * 70}")
        print(f"待定清单摘要（共 {len(pending_rows)} 条，显示前 30 条）：")
        print(f"{'─' * 70}")
        for r in pending_rows[:30]:
            print(f"  [{r['confidence']}] {r['relative_path']}")
            print(f"    标题: {r['title'][:60]}")
            print(f"    原因: {r['reason'][:80]}")
            print()

    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
