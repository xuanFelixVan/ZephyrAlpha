# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/backfill_module_domain.py | §
# [MODULE] scripts.governance.d3_metadata.backfill_module_domain
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib (argparse/csv/hashlib/json/os/re/subprocess/sys/collections/dataclasses/datetime/pathlib); _shared.constants; _shared.frontmatter; domain_header_maint(同级复用); zephyr.shared.io.yaml_utils(SSoT 词表); psycopg2(经 get_depgraph_pg_connection 惰性)
# [CONSUMERS] 战役 st-vocabconsol-20260918 W4c 补标工单；主会话分批 --apply 放量
# [STARTUP] manual
# noqa: m11-perm-manual-legitimate  M11豁免: 一次性存量治理批处理工具（对标 backfill_ttl_metadata/apply_depgraph CLI 写入工具豁免先例），无自动触发语义，由战役工单人工分批放量
# [MATURITY] staging
# [INVARIANTS] 推断链三级留证据（sibling_vote > path_prefix(YAML) > depgraph(PG)），任一级候选值必经 target_layer_vocabulary SSoT 合法性校验，非法/推不出=未决绝不瞎填；只增删改单行 `# [DOMAIN] X`，其余字节零改动（写后回读以"去掉 [DOMAIN] 行后的正文 sha256 不变"硬核验）；已有合法 [DOMAIN] 永不覆盖；dry-run 为默认零写入；--apply 跳过 git 脏文件与 .aidrafts；单批上限 batch；全程 JSONL 审计
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（推断/回填全部成功且无未决）；EXIT_FINDINGS=1（存在未决条目或写失败——批任务常态出口）；EXIT_ERROR=2（脚本异常/输入不可用）
# [TESTS] tests/governance/d3_metadata/test_backfill_module_domain.py
# [TTL] task_bound
"""backfill_module_domain.py — 模块 [DOMAIN] 头字段确定性补标生成器（W4c）

战役 st-vocabconsol-20260918 环节 W4c 工具面：为缺/空/非法 `[DOMAIN]` 头字段的
文件**确定性**推断 domain_id，并可执行回填。宪法铁律"静态清单禁手工维护"→
2115 条待补标清单（`no_domain_list.csv`）不手背，一律由本工具机生推断表。

推断优先级链（每级在推断表 `evidence_*` 列留证据，绝不臆测）::

    a. sibling_vote          同目录兄弟文件已有 [DOMAIN] 的多数票（≥2 兄弟一致才用）
    b. ownership_map         docs/03_modules/path_ownership_map.yaml：同 owner_blueprint
                             家族内已标注文件的多数票（≥2 一致）
       domain_registry_prefix
                             docs/01_policies_and_standards/_registry/catalogs/
                             functional_domain_registry.yaml 的 ssot_path 前缀 → domain
                             （最长前缀匹配）
    c. depgraph_*            PostgreSQL depgraph 只读连接（get_depgraph_pg_connection）：
                             file 节点 path 精确匹配 → directory 节点前缀 →
                             domain_mapping.path_prefix 最长前缀
    d. 全部推不出 / 值非法   inferred=None → 未决清单（`reject_reason` 记因），不写入

合法性校验唯一真源 = `target_layer_vocabulary.yaml`，经 SSoT 函数
``zephyr.shared.io.yaml_utils.load_vocabulary_values`` 加载（含 aliases 可见性）。
本脚本零硬编码域值。

安全护栏（--apply 才写盘）::

    * git status --porcelain 脏文件=他会话 WIP，直接跳过（可 --ignore-git-dirty 关闭，仅应急）
    * 跳过 .aidrafts/ 与 .runtime/ 等工作区外目录
    * 单批上限 --batch N（默认 200），按路径字典序取前 N 个可写项，分批放量
    * 写前 content_sha256 基线，写后回读核验：去掉 [DOMAIN] 行后的正文 sha256 必须与基线一致
    * 全程 JSONL 审计 .runtime/tmp/vocabconsol_backfill/audit.jsonl

用法::

    # 干跑（默认，只写 .runtime/tmp/ 下的推断表 + 报告）
    python scripts/governance/d3_metadata/backfill_module_domain.py --list <csv>

    # 重扫全仓缺失/非法 [DOMAIN] 的 .py（不依赖静态清单）
    python scripts/governance/d3_metadata/backfill_module_domain.py --all

    # 真回填（每批 200，重复执行直到未决为 0）
    python scripts/governance/d3_metadata/backfill_module_domain.py --apply --batch 200

    # 单文件试写（自测用）
    python scripts/governance/d3_metadata/backfill_module_domain.py --apply --files a.py,b.py

退出码：0=无未决无失败，1=有未决/有写失败（批任务常态），2=脚本异常。
"""

from __future__ import annotations

__manifest__ = """
args: ["--list", "--apply", "--batch", "--all"]
description: 模块 [DOMAIN] 头字段确定性补标生成器（三级证据推断 + 可执行回填，W4c）
dimensions:
- D3
priority: P2
timeout_seconds: 900
warn_only: false
"""

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

_SCRIPT_PATH = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_PATH.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import (  # noqa: E402
    EXIT_ERROR,
    EXIT_FINDINGS,
    EXIT_PASS,
    REPO_ROOT,
)

# SSoT 词表加载器（禁止本脚本自造 YAML 解析；src 目录惰性加入 sys.path）
_SRC_DIR = REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from zephyr.shared.io.yaml_utils import load_vocabulary_values  # noqa: E402

# ---------------------------------------------------------------------------
# 常量与路径（全部可被测试参数覆盖，无隐藏全局态）
# ---------------------------------------------------------------------------

DEFAULT_LIST = (
    REPO_ROOT
    / "docs/_working/2026-09-18_vocab_consolidation_campaign/w1_mining/no_domain_list.csv"
)
DEFAULT_TMP_DIR = REPO_ROOT / ".runtime/tmp/vocabconsol_backfill"
DEFAULT_VOCAB_FILE = "target_layer_vocabulary.yaml"
OWNERSHIP_MAP = REPO_ROOT / "docs/03_modules/path_ownership_map.yaml"
DOMAIN_REGISTRY = (
    REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml"
)

# 证据扫描范围：只认代码树（src/tests/scripts）的 [DOMAIN] 头。
# docs/ config/ schemas/ 等登记件与配置的头部锚定的是"本文件自身归属"，
# 拿去给别的目录投票会污染兄弟票/家族票，故不入证据基（仍可作补标对象）。
SCAN_DIRS = ("src", "tests", "scripts")
EXCLUDE_PARTS = {
    "__pycache__",
    ".git",
    ".runtime",
    ".aidrafts",
    ".worktrees",
    ".ailocks",
    "node_modules",
    ".venv",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

_HEADER_SCAN_LINES = 50
# 域头标记行（值可空）——用于定位与替换（勿写成行首字面量，避 GATE-DOMAIN-FK 锚定误报）
_DOMAIN_LINE_RE = re.compile(r"^#\s*\[DOMAIN\]\s*(\S*)")
_MODULE_LINE_RE = re.compile(r"^#\s*\[MODULE\]", re.M)
# .yaml 治理锚定块结束行（中文标记，逐行 in 判断，不用字节正则防编码歧义）
_ANCHOR_END_MARK = "治理锚定结束"

# 推断链级别（报告与 CSV 的 level 列）
LEVEL_A = "a_sibling_vote"
LEVEL_B = "b_path_prefix_yaml"
LEVEL_C = "c_depgraph_pg"
LEVEL_MIGRATION = "m_deprecated_migration"
SOURCE_ORDER = (
    "sibling_vote",
    "ownership_map",
    "domain_registry_prefix",
    "depgraph_node",
    "depgraph_dir_node",
    "depgraph_prefix_map",
)

# 跨源冲突标记：默认**不写盘**（须人工裁定后 --allow-conflict-write 放量）；
# sibling_vote_only_evidence / prefix_only_evidence 只是"证据弱"标注，可正常写入（报告里单列统计）。
CONFLICT_FLAGS = frozenset({"sibling_vote_conflicts_independent"})


# ---------------------------------------------------------------------------
# 参数对象（§5.150 Long Parameter List 治理：按用途分组的只读快照）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceLocations:
    """证据源装载位置（四类只读输入 + SSoT 词表文件名）。"""

    repo: Path = REPO_ROOT
    vocab_file: str = DEFAULT_VOCAB_FILE
    ownership_path: Path = OWNERSHIP_MAP
    registry_path: Path = DOMAIN_REGISTRY


@dataclass(frozen=True)
class TargetSelection:
    """目标集来源（优先级 --files > --all 重扫 > 静态清单）。"""

    list_path: Path | None = None
    all_mode: bool = False
    files: list[str] | None = None


@dataclass(frozen=True)
class BackfillWritePolicy:
    """写盘策略与阈值（默认 dry-run 零写盘）。"""

    apply: bool = False
    batch: int = 200
    min_sibling_support: int = 2
    skip_git_guard: bool = False
    allow_conflict_write: bool = False


@dataclass(frozen=True)
class OutputOptions:
    """产物输出选项（推断表 / JSONL 审计 / markdown 报告）。"""

    out_dir: Path = DEFAULT_TMP_DIR
    write_report: bool = True


@dataclass(frozen=True)
class InjectionHooks:
    """外部依赖注入点（None=走真实 git / depgraph PG；测试与沙箱替换）。"""

    git_runner: Callable | None = None
    conn_factory: Callable | None = None


@dataclass(frozen=True)
class Vocabulary:
    """SSoT 词表快照：合法域值集 + 废弃值唯一迁移映射。"""

    legal: set[str]
    deprecated_map: dict[str, str]


@dataclass(frozen=True)
class EvidenceSources:
    """六级证据快照（一次装载、逐文件复用；含词表合法性口径）。"""

    vocab: Vocabulary
    index: dict[str, str | None]
    ownership: dict[str, str]
    cohorts: dict[str, set[str]]
    prefixes: dict[str, str]
    db: tuple[dict[str, str], dict[str, str], list[tuple[str, str]]]


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    """字节串 sha256 十六进制（审计基线用）。"""
    return hashlib.sha256(data).hexdigest()


def rel_to_repo(path: Path) -> str:
    """绝对路径 → 仓库相对路径（正斜杠归一，与清单口径一致）。"""
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def is_excluded(rel_path: str) -> bool:
    """是否落在排除目录（.aidrafts/.runtime/... 永不处理）。"""
    parts = set(rel_path.split("/"))
    return bool(parts & EXCLUDE_PARTS)


def load_legal_domains(vocab_file: str = DEFAULT_VOCAB_FILE) -> set[str]:
    """从 SSoT 词表加载合法域值集合（含 aliases；strict=False 时返回空集）。

    空集=词表不可用，此时本工具视"一切候选非法"→全量未决（fail-safe，
    绝不因词表故障而写入未校验值）。
    """
    try:
        return load_vocabulary_values(vocab_file, strict=True)
    except Exception as exc:  # noqa: BLE001 — 词表不可用必须降级为"全未决"，不崩工具
        print(f"WARN: 词表加载失败（{exc}）→ 全部候选判非法，转未决清单", file=sys.stderr)
        return set()


def load_deprecated_replacements(vocab_file: str = DEFAULT_VOCAB_FILE) -> dict[str, str]:
    """词表 deprecated_values 中迁移目标唯一的 值→replacement 映射。

    2026-09-18 治本（st-vocabconsol W4c 放量实证）：既有废弃值（如 schemas
    的 D_DATA）若不优先走词表官方 replacement，兄弟票/前缀票会把它盖成语义
    错误值（实测 D_DATA→D_GOVERNANCE 7 件）。废弃≠随便换：换什么由词表说了算。
    """
    try:
        import yaml  # noqa: PLC0415 — 与家族一致：仅本函数需要，缺失时 fail-safe 返回空映射

        from zephyr.shared.io.yaml_utils import _resolve_vocab_path  # noqa: PLC0415

        vf = Path(vocab_file)
        text = (vf if vf.is_file() else _resolve_vocab_path(vocab_file, None)).read_text(encoding="utf-8")
        data = yaml.safe_load(text)
    except Exception:  # noqa: BLE001 — 与 load_legal_domains 同 fail-safe：映射不可用=不启用迁移优先
        return {}
    if not isinstance(data, dict):
        return {}
    result: dict[str, str] = {}
    for v in data.get("deprecated_values", []) or []:
        if not isinstance(v, dict):
            continue
        val = v.get("value")
        rep = v.get("replacement")
        if val and isinstance(rep, str) and rep.strip() and not rep.strip().startswith("N/A"):
            rep_clean = rep.strip()
            if "、" in rep_clean:  # 多靶=迁移目标不唯一，弃用（宁缺勿滥）
                continue
            result[str(val)] = rep_clean
    return result


def read_header_text(path: Path, max_bytes: int = 6000) -> str | None:
    """读文件头部文本（None=读失败）。仅用于 header 解析，不做写入。"""
    try:
        return path.read_bytes()[:max_bytes].decode("utf-8", errors="replace")
    except OSError:
        return None


def extract_domain_from_text(text: str | None) -> tuple[str | None, bool]:
    """从头部文本解析 `# [DOMAIN]` 值。返回 (值或 None, 是否在 50 行内找到该字段)。"""
    if not text:
        return (None, False)
    for line in text.splitlines()[:_HEADER_SCAN_LINES]:
        m = _DOMAIN_LINE_RE.match(line)
        if m:
            val = (m.group(1) or "").strip()
            if not val or val.startswith("#"):
                return (None, True)
            return (val, True)
    return (None, False)


# ---------------------------------------------------------------------------
# 证据源 1：仓库 header 索引（同目录兄弟票 + ownership 家族票共用）
# ---------------------------------------------------------------------------


def build_header_index(
    repo: Path = REPO_ROOT,
    scan_dirs: tuple[str, ...] = SCAN_DIRS,
    suffixes: tuple[str, ...] = (".py", ".yaml"),
) -> dict[str, str | None]:
    """扫描仓库头部 [DOMAIN] 现状 → {相对路径: domain|None}。

    只登记**有** [MODULE] 或 [DOMAIN] 的文件（兄弟票证据要求文件确已标注）。
    """
    index: dict[str, str | None] = {}
    for d in scan_dirs:
        base = repo / d
        if not base.is_dir():
            continue
        for fp in base.rglob("*"):
            if not fp.is_file() or fp.suffix.lower() not in suffixes:
                continue
            try:
                rel = fp.relative_to(repo).as_posix()
            except ValueError:
                try:
                    rel = fp.resolve().relative_to(repo.resolve()).as_posix()
                except ValueError:
                    continue
            if is_excluded(rel):
                continue
            head = read_header_text(fp)
            if not head or not _MODULE_LINE_RE.search(head):
                continue
            dom, _found = extract_domain_from_text(head)
            index[rel] = dom
    return index


def dir_votes(index: dict[str, str | None], rel_path: str, cohort: set[str] | None = None) -> Counter:
    """目录多数票：同目录（cohort=None）或指定家族内已标注文件的 domain 计数。

    自身排除；仅计有非空 [DOMAIN] 的文件。
    """
    parent = str(Path(rel_path).parent)
    c: Counter = Counter()
    for other, dom in index.items():
        if other == rel_path or not dom:
            continue
        if cohort is None:
            if str(Path(other).parent) == parent:
                c[dom] += 1
        elif other in cohort:
            c[dom] += 1
    return c


def majority_vote(counter: Counter, *, min_support: int = 2) -> tuple[str | None, int]:
    """多数票：≥min_support 支持才算成立，返回 (值, 支持数)。"""
    if not counter:
        return (None, 0)
    value, count = counter.most_common(1)[0]
    return (value, count) if count >= min_support else (None, count)


# ---------------------------------------------------------------------------
# 证据源 2：path_ownership_map.yaml（家族票）
# ---------------------------------------------------------------------------

_OWNERSHIP_ITEM_SPLIT = re.compile(r"^  - ", re.M)
_OWNERSHIP_PATH_RE = re.compile(r"^\s*path: '(?P<path>[^']*)'", re.M)
_OWNERSHIP_BP_RE = re.compile(r"^\s*owner_blueprint: '(?P<bp>[^']*)'", re.M)


def load_ownership_map(path: Path = OWNERSHIP_MAP) -> dict[str, str]:
    """解析 path_ownership_map.yaml → {路径: owner_blueprint}。

    该文件是生成器产出的登记件（56k 行），此处只做"路径→蓝本"读取；
    蓝本→域 由家族内已标注文件的多数票决定（不猜蓝本命名）。
    按列表项切块后再取键，字段序不敏感（生成器调序也不会静默丢整条 b 级证据源）。
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"WARN: ownership map 不可读（{exc}）→ b 级该源无证据", file=sys.stderr)
        return {}
    out: dict[str, str] = {}
    for block in _OWNERSHIP_ITEM_SPLIT.split(text)[1:]:
        pm = _OWNERSHIP_PATH_RE.search(block)
        bm = _OWNERSHIP_BP_RE.search(block)
        if not pm or not bm:
            continue  # ssot_claims 段等非路径条目
        p, bp = pm.group("path").strip(), bm.group("bp").strip()
        if p and bp:
            out[p] = bp
    return out


def build_blueprint_cohorts(ownership: dict[str, str]) -> dict[str, set[str]]:
    """owner_blueprint → 该蓝本名下路径集合（家族票的预索引，8k 条目线性一次）。"""
    cohorts: dict[str, set[str]] = defaultdict(set)
    for p, bp in ownership.items():
        cohorts[bp].add(p)
    return dict(cohorts)


def blueprint_cohort_votes(
    index: dict[str, str | None],
    cohorts: dict[str, set[str]],
    ownership: dict[str, str],
    rel_path: str,
) -> Counter:
    """同 owner_blueprint 家族内已标注文件的 domain 计数（排除自身）。"""
    bp = ownership.get(rel_path)
    if not bp:
        return Counter()
    return dir_votes(index, rel_path, cohort=cohorts.get(bp, set()))


# ---------------------------------------------------------------------------
# 证据源 3：functional_domain_registry.yaml ssot_path 前缀 → domain
# ---------------------------------------------------------------------------


def load_ssot_path_prefixes(path: Path = DOMAIN_REGISTRY) -> dict[str, str]:
    """读功能域注册表 ssot_path → domain（最长前缀表）。"""
    try:
        import yaml  # noqa: PLC0415 — 仅 b 级需要，惰性导入省启动税
    except ImportError:  # pragma: no cover
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — 注册表不可读只削弱 b 级证据
        print(f"WARN: 功能域注册表不可读（{exc}）→ b 级该源无证据", file=sys.stderr)
        return {}
    out: dict[str, str] = {}
    for entry in (data or {}).get("entries", []) or []:
        if not isinstance(entry, dict):
            continue
        prefix = str(entry.get("ssot_path") or "").strip()
        dom = str(entry.get("domain") or "").strip()
        if prefix and dom:
            out.setdefault(prefix, dom)
    return out


def longest_prefix_match(prefixes: dict[str, str], rel_path: str) -> tuple[str | None, str]:
    """最长前缀命中 → (domain, 命中的前缀)。

    等长多命中按前缀字典序取最小（确定性：同输入必同输出，防 DB 行序抖动）。
    """
    best_len = -1
    best_key: str | None = None
    for prefix, dom in prefixes.items():
        if not prefix or not rel_path.startswith(prefix):
            continue
        if len(prefix) > best_len or (len(prefix) == best_len and prefix < (best_key or prefix)):
            best_len, best_key = len(prefix), prefix
    if best_key is None:
        return (None, "")
    return (prefixes[best_key], best_key)


# ---------------------------------------------------------------------------
# 证据源 4：depgraph PostgreSQL（只读）
# ---------------------------------------------------------------------------

SQL_NODES_DOMAINS = (
    "select path, domain_id, granularity from nodes "
    "where domain_id is not null and domain_id <> ''"
)
SQL_PATH_PREFIX_MAPPING = (
    "select path_prefix, domain_id from domain_mapping "
    "where path_prefix is not null and domain_id is not null"
)


def load_depgraph_evidence(
    conn_factory: Callable[[], Any] | None = None,
) -> tuple[dict[str, str], dict[str, str], list[tuple[str, str]]]:
    """从 depgraph PG 取三份只读证据：

    Returns:
        ({file_path: domain}, {dir_path: domain}, [(path_prefix, domain)])

    PG 不可达/表缺失时返回空结构（c 级无证据，不崩工具）。
    """
    empty: tuple[dict[str, str], dict[str, str], list[tuple[str, str]]] = ({}, {}, [])
    try:
        if conn_factory is None:
            sys.path.insert(0, str(_GOV_DIR))
            from _shared.constants import get_depgraph_pg_connection  # noqa: PLC0415

            conn_factory = get_depgraph_pg_connection
        conn = conn_factory()
        nodes = conn.execute(SQL_NODES_DOMAINS).fetchall()
        mapping = conn.execute(SQL_PATH_PREFIX_MAPPING).fetchall()
        try:
            conn.close()
        except Exception:  # noqa: BLE001
            pass
    except Exception as exc:  # noqa: BLE001 — DB 故障降级为"无证据"，绝不编造
        print(f"WARN: depgraph PG 不可用（{type(exc).__name__}: {exc}）→ c 级无证据", file=sys.stderr)
        return empty

    file_dom: dict[str, str] = {}
    dir_dom: dict[str, str] = {}
    for row in nodes:
        path = str(row["path"] or "").strip()
        dom = str(row["domain_id"] or "").strip()
        if not path or not dom:
            continue
        if str(row.get("granularity") or "") == "directory":
            dir_dom[path if path.endswith("/") else f"{path}/"] = dom
        else:
            file_dom[path] = dom
    prefix_rows = [
        (str(r["path_prefix"]).strip(), str(r["domain_id"]).strip())
        for r in mapping
        if r.get("path_prefix") and r.get("domain_id")
    ]
    return file_dom, dir_dom, prefix_rows


# ---------------------------------------------------------------------------
# 推断主链
# ---------------------------------------------------------------------------


def _vote_candidate(
    source: str,
    level: str,
    counter: Counter,
    note_tpl: str,
    min_sibling_support: int,
) -> tuple[tuple[str, str, str | None, int, str], str | None]:
    """单级投票候选 → ((source, level, value, support, note), 门槛前原始票值)。"""
    raw_val, _raw_n = counter.most_common(1)[0] if counter else (None, 0)
    val, n = majority_vote(counter, min_support=min_sibling_support)
    return (source, level, val, n, note_tpl.format(n=n)), raw_val


def _depgraph_candidates(
    rel_path: str,
    file_dom: dict[str, str],
    dir_dom: dict[str, str],
    prefix_rows: list[tuple[str, str]],
) -> list[tuple[str, str, str | None, int, str]]:
    """c 级三源候选：PG nodes.file 精确 / PG nodes.directory 前缀 / domain_mapping 前缀。"""
    out: list[tuple[str, str, str | None, int, str]] = []
    if file_dom.get(rel_path):
        out.append(("depgraph_node", LEVEL_C, file_dom[rel_path], 1, "PG nodes.path 精确匹配"))
    else:
        out.append(("depgraph_node", LEVEL_C, None, 0, "PG 无该 file 节点"))

    ddom, dpfx = longest_prefix_match(dir_dom, rel_path)
    out.append(("depgraph_dir_node", LEVEL_C, ddom, len(dpfx), f"PG directory 节点前缀={dpfx or '<无>'}"))

    prefix_map: dict[str, str] = {}
    for pre, val in sorted(prefix_rows):
        prefix_map.setdefault(pre, val)
    pdb, ppfx = longest_prefix_match(prefix_map, rel_path)
    out.append(("depgraph_prefix_map", LEVEL_C, pdb, len(ppfx), f"domain_mapping 前缀={ppfx or '<无>'}"))
    return out


def _collect_evidence_candidates(
    rel_path: str,
    ev: EvidenceSources,
    min_sibling_support: int = 2,
) -> tuple[list[tuple[str, str, str | None, int, str]], set[str]]:
    """六级证据全算（源序=SOURCE_ORDER）→ (candidates, raw_seen)。

    candidates 元素=(source, level, value, support, note)；raw_seen=门槛前的原始票值
    （用于区分"票不足"与"完全无证据"）。
    """
    file_dom, dir_dom, prefix_rows = ev.db
    candidates: list[tuple[str, str, str | None, int, str]] = []
    raw_seen: set[str] = set()

    cand, raw = _vote_candidate(
        "sibling_vote",
        LEVEL_A,
        dir_votes(ev.index, rel_path),
        "同目录多数票 support={n}（门槛 " + str(min_sibling_support) + "）",
        min_sibling_support,
    )
    candidates.append(cand)
    if raw:
        raw_seen.add(raw)

    bp = ev.ownership.get(rel_path, "")
    cand, raw = _vote_candidate(
        "ownership_map",
        LEVEL_B,
        blueprint_cohort_votes(ev.index, ev.cohorts, ev.ownership, rel_path),
        f"owner_blueprint={bp or '<无>'} 家族票 support={{n}}",
        min_sibling_support,
    )
    candidates.append(cand)
    if raw:
        raw_seen.add(raw)

    pdom, pfx = longest_prefix_match(ev.prefixes, rel_path)
    candidates.append(("domain_registry_prefix", LEVEL_B, pdom, len(pfx), f"ssot_path 最长前缀={pfx or '<无>'}"))

    candidates.extend(_depgraph_candidates(rel_path, file_dom, dir_dom, prefix_rows))
    return candidates, raw_seen


def _candidate_summary(
    candidates: list[tuple[str, str, str | None, int, str]],
    legal: set[str],
) -> tuple[str, str, str]:
    """候选列 → (evidence 证据串, illegal 逗号串, conflict 跨源分歧串)。"""
    evidence = " | ".join(f"{src}={val or '<none>'}" for src, _lvl, val, _s, _n in candidates)
    illegal = sorted({val for _s, _l, val, _n, _x in candidates if val and val not in legal})
    distinct_legal = sorted({val for _s, _l, val, _n, _x in candidates if val and val in legal})
    conflict = ";".join(distinct_legal) if len(distinct_legal) > 1 else ""
    return evidence, ",".join(illegal), conflict


def _first_legal(
    candidates: list[tuple[str, str, str | None, int, str]],
    legal: set[str],
    *sources: str,
) -> tuple[str, str, str, int, str] | None:
    """按给定源序取首个**合法**候选。"""
    for want in sources:
        for cand in candidates:
            if cand[0] == want and cand[2] and cand[2] in legal:
                return cand
    return None


def _arbitrate(
    candidates: list[tuple[str, str, str | None, int, str]],
    legal: set[str],
) -> tuple[tuple[str, str, str, int, str] | None, str]:
    """证据强度分层仲裁 → (chosen, review_flag)。

    同模块独立证据 > 目录兄弟票 > 目录/前缀表（弱佐证）
    """
    independent = _first_legal(candidates, legal, "depgraph_node", "ownership_map")
    sibling = _first_legal(candidates, legal, "sibling_vote")
    weak = _first_legal(candidates, legal, "domain_registry_prefix", "depgraph_dir_node", "depgraph_prefix_map")

    if not sibling:
        chosen = independent or weak
        flag = "prefix_only_evidence" if chosen and not independent else ""
        return chosen, flag
    if not independent:
        # 目录惯例比粗粒度前缀表更特定；无独立证据时兄弟票仍胜出，仅打弱证标记
        flag = "" if weak and weak[2] == sibling[2] else "sibling_vote_only_evidence"
        return sibling, flag
    if independent[2] == sibling[2]:
        return sibling, ""  # 目录惯例 + 同模块独立证据一致 = 最高置信
    # 独立证据反对：目录混装多模块（实测 16 目录），兄弟票让位并转人工裁定
    return independent, "sibling_vote_conflicts_independent"


def _inferred_result(
    chosen: tuple[str, str, str, int, str],
    *,
    evidence: str,
    conflict: str,
    review_flag: str,
    illegal_str: str,
) -> dict[str, Any]:
    """仲裁成功 → 推断结果行（inferred 非空）。"""
    src, lvl, val, sup, note = chosen
    return {
        "inferred": val,
        "source": src,
        "level": lvl,
        "support": sup,
        "evidence": evidence,
        "chosen_note": note,
        "conflict": conflict,
        "review_flag": review_flag,
        "reject_reason": "",
        "illegal_candidates": illegal_str,
    }


def _unresolved_result(
    *,
    evidence: str,
    conflict: str,
    illegal_str: str,
    has_evidence: bool,
) -> dict[str, Any]:
    """仲裁失败 → 未决行（reject_reason 记因，绝不瞎填）。"""
    if illegal_str:
        reason = "illegal_value:" + illegal_str
    elif has_evidence:
        reason = "below_threshold"
    else:
        reason = "no_evidence"
    return {
        "inferred": None,
        "source": "",
        "level": "d_unresolved",
        "support": 0,
        "evidence": evidence,
        "chosen_note": "",
        "conflict": conflict,
        "review_flag": "",
        "reject_reason": reason,
        "illegal_candidates": illegal_str,
    }


def infer_one(rel_path: str, ev: EvidenceSources, min_sibling_support: int = 2) -> dict[str, Any]:
    """单文件推断：六级证据全算（全留证据列），按优先级取首个**合法**值。

    Args:
        rel_path: 仓库相对路径（正斜杠）。
        ev: 证据源快照（header 索引 / ownership 家族 / 注册表前缀 / depgraph + 词表合法集）。
        min_sibling_support: 兄弟票与家族票成立的最小支持数。

    优先级：a 同目录兄弟票 > b ownership 家族票 > b 功能域注册表前缀
    > c depgraph file 节点 > c directory 节点 > c domain_mapping 前缀。

    Returns dict: inferred / source / level / support / evidence / chosen_note /
    conflict / reject_reason / illegal_candidates。
    推不出（无证据 / 票不足 / 值非法）→ inferred=None（未决，绝不瞎填）。
    """
    legal = ev.vocab.legal
    candidates, raw_seen = _collect_evidence_candidates(rel_path, ev, min_sibling_support)
    evidence, illegal_str, conflict = _candidate_summary(candidates, legal)
    chosen, review_flag = _arbitrate(candidates, legal)
    if chosen:
        return _inferred_result(
            chosen, evidence=evidence, conflict=conflict, review_flag=review_flag, illegal_str=illegal_str
        )
    has_evidence = bool(raw_seen) or any(val for _s, _l, val, _n, _x in candidates)
    return _unresolved_result(
        evidence=evidence, conflict=conflict, illegal_str=illegal_str, has_evidence=has_evidence
    )


# ---------------------------------------------------------------------------
# 单文件文本改写（字节保真）
# ---------------------------------------------------------------------------


def plan_domain_line_edit(text: str, domain: str, legal: set[str] | None = None) -> tuple[str | None, str]:
    """生成把 `# [DOMAIN] domain` 补/改到文件头的新文本。

    Args:
        text: 原文件全文。
        domain: 推断出的合法域值（已过 SSoT 词表校验）。
        legal: 合法域值集合——既有值合法时**永不覆盖**（只补空值/改非法值）。

    Returns (new_text|None, action):
      - None + "skip_already_ok"      : 已有同值合法 [DOMAIN]
      - None + "skip_legal_exists"    : 已有**不同**合法值（永不覆盖既有合法标注）
      - new_text + "replaced"         : 原行值为空/非法 → 原地替换
      - new_text + "inserted_after_module" : 有 [MODULE] → 其后插入
      - new_text + "inserted_in_anchor"    : .yaml 治理锚定块 → 结束标记前插入
      - None + "no_anchor"            : 无可插入锚点（不瞎插，转未决）
    """
    legal = legal or set()
    lines = text.splitlines(keepends=True)
    scan = min(len(lines), _HEADER_SCAN_LINES)

    def _terminator(line: str) -> str:
        """_terminator implementation."""
        if line.endswith("\r\n"):
            return "\r\n"
        if line.endswith("\n"):
            return "\n"
        return ""

    for i in range(scan):
        m = _DOMAIN_LINE_RE.match(lines[i])
        if not m:
            continue
        current = (m.group(1) or "").strip()
        if current == domain:
            return (None, "skip_already_ok")
        if current and current in legal:
            return (None, "skip_legal_exists")
        term = _terminator(lines[i])
        lines[i] = f"# [DOMAIN] {domain}{term}"
        if not term:  # 末行无换行符——补换行会引入额外字节，改为原样拼接
            lines[i] = f"# [DOMAIN] {domain}"
        return ("".join(lines), "replaced")

    for i in range(scan):
        if _MODULE_LINE_RE.match(lines[i]):
            term = _terminator(lines[i]) or "\n"
            lines.insert(i + 1, f"# [DOMAIN] {domain}{term}")
            return ("".join(lines), "inserted_after_module")

    for i in range(scan):
        if _ANCHOR_END_MARK in lines[i]:
            term = _terminator(lines[i]) or "\n"
            lines.insert(i, f"# [DOMAIN] {domain}{term}")
            return ("".join(lines), "inserted_in_anchor")

    return (None, "no_anchor")


def strip_domain_lines(text: str) -> str:
    """删除所有 `# [DOMAIN]` 行——用于"其余字节零改动"核验。"""
    return "".join(ln for ln in text.splitlines(keepends=True) if not _DOMAIN_LINE_RE.match(ln))


def atomic_write_bytes(target: Path, data: bytes) -> None:
    """原子写（tmp + os.replace，RULE-ONE 并发安全；失败清 tmp 并抛出）。"""
    tmp = target.with_name(f"{target.name}.{os.getpid()}.backfilltmp")
    try:
        tmp.write_bytes(data)
        os.replace(str(tmp), str(target))
    except Exception:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
        raise


# ---------------------------------------------------------------------------
# 护栏：git 脏文件
# ---------------------------------------------------------------------------


def default_git_runner(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """真实 git 调用（测试注入假 runner）。"""
    from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

    return run_subprocess_hidden(args, capture_output=True, text=True, cwd=str(cwd))


def collect_dirty_paths(repo: Path = REPO_ROOT, runner: Callable | None = None) -> set[str]:
    """`git status --porcelain` 收集工作区脏路径（含 staged/未跟踪/改名两侧）。"""
    runner = runner or default_git_runner
    try:
        proc = runner(["git", "status", "--porcelain"], repo)
    except Exception as exc:  # noqa: BLE001 — git 不可用=保守跳过一切写入
        print(f"WARN: git status 失败（{exc}）→ 视为全部脏，--apply 拒绝写入", file=sys.stderr)
        return {"<git_unavailable>"}
    if getattr(proc, "returncode", 1) != 0:
        return {"<git_unavailable>"}
    dirty: set[str] = set()
    for raw in (proc.stdout or "").splitlines():
        entry = raw[3:] if len(raw) > 3 else ""
        if not entry:
            continue
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        entry = entry.strip().strip('"')
        if entry:
            dirty.add(entry.replace("\\", "/"))
    return dirty


# ---------------------------------------------------------------------------
# 输入清单
# ---------------------------------------------------------------------------


def read_list(list_path: Path) -> list[str]:
    """读补标清单：每行一个相对路径（无表头，正斜杠）。兼容首列表头与逗号分隔。"""
    try:
        text = list_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"ERROR: 清单不可读 {list_path}: {exc}") from exc
    out: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        cand = line.strip()
        if not cand or cand.startswith("#"):
            continue
        if "," in cand:  # 兼容多列 CSV：取第一列
            cand = cand.split(",", 1)[0].strip()
        if cand.lower() in {"path", "module_path", "file"}:
            continue
        cand = cand.replace("\\", "/")
        if cand not in seen:
            seen.add(cand)
            out.append(cand)
    return out


def collect_all_candidates(index: dict[str, str | None], legal: set[str]) -> list[str]:
    """--all 模式：重扫全仓，取"有 [MODULE] 但缺/空/非法 [DOMAIN]"的文件。"""
    return sorted(rel for rel, dom in index.items() if dom is None or dom not in legal)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


@dataclass
class _RunContext:
    """一次批处理的运行态：证据源快照 + 写盘策略 + 护栏脏清单 + 累积产物（仅模块内部流转）。"""

    repo: Path
    policy: BackfillWritePolicy
    evidence: EvidenceSources
    dirty: set[str]
    rows: list[dict[str, Any]] = field(default_factory=list)
    stats: Counter = field(default_factory=Counter)
    audits: list[dict[str, Any]] = field(default_factory=list)
    written: int = 0


def _build_context(
    locations: EvidenceLocations,
    policy: BackfillWritePolicy,
    hooks: InjectionHooks,
) -> _RunContext:
    """装载四类证据源（词表/header 索引/ownership/注册表/PG）+ 护栏脏文件清单。"""
    vocab = Vocabulary(
        legal=load_legal_domains(locations.vocab_file),
        deprecated_map=load_deprecated_replacements(locations.vocab_file),
    )
    index = build_header_index(locations.repo)
    ownership = load_ownership_map(locations.ownership_path)
    cohorts = build_blueprint_cohorts(ownership)
    prefixes = load_ssot_path_prefixes(locations.registry_path)
    db = load_depgraph_evidence(hooks.conn_factory)
    dirty = (
        set()
        if (not policy.apply or policy.skip_git_guard)
        else collect_dirty_paths(locations.repo, hooks.git_runner)
    )
    return _RunContext(
        repo=locations.repo,
        policy=policy,
        evidence=EvidenceSources(
            vocab=vocab,
            index=index,
            ownership=ownership,
            cohorts=cohorts,
            prefixes=prefixes,
            db=db,
        ),
        dirty=dirty,
    )


def _resolve_targets(ctx: _RunContext, selection: TargetSelection) -> list[str]:
    """目标集优先级：--files > --all 重扫 > 静态清单；去重后字典序。"""
    if selection.files is not None:
        targets = [f.replace("\\", "/") for f in selection.files]
    elif selection.all_mode:
        targets = collect_all_candidates(ctx.evidence.index, ctx.evidence.vocab.legal)
    else:
        targets = read_list(selection.list_path or DEFAULT_LIST)
    return sorted(set(targets))  # 确定性批序（同输入必同批次，防放量时窗口抖动）


def _new_row(rel: str, abspath: Path) -> dict[str, Any]:
    """推断表行骨架（全列预置空值，保证 CSV 列序与缺项可判）。"""
    return {
        "path": rel,
        "exists_on_disk": abspath.is_file(),
        "current_domain": extract_domain_from_text(read_header_text(abspath))[0] or "",
        "level": "d_unresolved",
        "source": "",
        "support": 0,
        "chosen_note": "",
        "inferred": "",
        "conflict": "",
        "review_flag": "",
        "illegal_candidates": "",
        "evidence": "",
        "action": "",
        "planned_action": "",
        "reject_reason": "",
        "sha_before": "",
        "sha_after": "",
    }


def _reject_row(ctx: _RunContext, row: dict[str, Any], action: str, reason: str, stat_key: str) -> None:
    """统一"本条不写盘"出口：标 action/reject_reason + 计数 + 入表。"""
    row["action"] = action
    row["reject_reason"] = reason
    ctx.stats[stat_key] += 1
    ctx.rows.append(row)


def _guard_target_row(ctx: _RunContext, rel: str, row: dict[str, Any]) -> bool:
    """三重护栏（磁盘幽灵 / 排除目录 / git 脏文件）；命中即记账并返回 True。"""
    if not row["exists_on_disk"]:
        _reject_row(ctx, row, "skip_ghost", "file_not_on_disk", "skip_ghost")
        return True
    if is_excluded(rel):
        _reject_row(ctx, row, "skip_excluded", "excluded_dir", "skip_excluded")
        return True
    if ctx.policy.apply and rel in ctx.dirty:
        _reject_row(ctx, row, "skip_git_dirty", "workspace_wip_other_session", "skip_git_dirty")
        return True
    return False


def _read_target_text(ctx: _RunContext, abspath: Path, row: dict[str, Any]) -> str | None:
    """读原文 + sha256 基线；解码失败=记账并返回 None（不写不崩）。"""
    raw = abspath.read_bytes()
    row["sha_before"] = sha256_bytes(raw)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        _reject_row(ctx, row, "error", f"decode_error:{exc.__class__.__name__}", "error")
        return None


def _migration_target(ctx: _RunContext, cur: str) -> str | None:
    """既有值=词表废弃且迁移目标唯一合法 → 目标值；否则 None（回落推断票）。"""
    vocab = ctx.evidence.vocab
    if not cur or cur in vocab.legal:
        return None
    target = vocab.deprecated_map.get(cur)
    return target if target and target in vocab.legal else None


def _migration_info(cur: str, target: str) -> dict[str, Any]:
    """废弃值官方迁移结果（与 infer_one 同形状）。"""
    return {
        "inferred": target,
        "source": "vocab_deprecated_migration",
        "level": LEVEL_MIGRATION,
        "support": 1,
        "evidence": f"既有值 {cur}=词表废弃，replacement 唯一={target}",
        "chosen_note": "词表官方迁移目标优先于推断票（2026-09-18 W4c 放量实证治本）",
        "conflict": "",
        "review_flag": "",
        "reject_reason": "",
        "illegal_candidates": "",
    }


def _infer_for_target(ctx: _RunContext, rel: str, row: dict[str, Any]) -> dict[str, Any]:
    """词表废弃迁移短路优先，否则走六级推断链；结果并入 row（不动 action）。"""
    cur = row["current_domain"]
    target = _migration_target(ctx, cur)
    if target:
        info = _migration_info(cur, target)
    else:
        info = infer_one(rel, ctx.evidence, ctx.policy.min_sibling_support)
    row["review_flag"] = info.get("review_flag", "")
    row.update(
        {
            "inferred": info["inferred"] or "",
            "source": info["source"],
            "level": info["level"],
            "support": info["support"],
            "chosen_note": info["chosen_note"],
            "conflict": info["conflict"],
            "illegal_candidates": info["illegal_candidates"],
            "evidence": info["evidence"],
        }
    )
    return info


# 计划动作但本条不写盘（既有合法标注 / 无锚点）：action → (统计键, 归因)
_PLANNED_REJECTS = {
    "skip_already_ok": ("already_ok", "header_already_legal"),
    "skip_legal_exists": ("conflict_existing_legal", "existing_legal_differs"),
    "no_anchor": ("no_anchor", "no_header_anchor"),
}


def _reject_planned_action(ctx: _RunContext, row: dict[str, Any], action: str) -> bool:
    """既有合法值不覆盖、无锚点不瞎插：命中即记账并返回 True。"""
    hit = _PLANNED_REJECTS.get(action)
    if not hit:
        return False
    _reject_row(ctx, row, action, hit[1], hit[0])
    return True


def _verify_written(text: str, after_text: str) -> tuple[bool, str | None, bool]:
    """写后核验三元组：正文 sha256 不变 / 回读到的值 / 行数增量∈{0,1}。"""
    ok_body = sha256_bytes(strip_domain_lines(text).encode("utf-8")) == sha256_bytes(
        strip_domain_lines(after_text).encode("utf-8")
    )
    ok_value, _ = extract_domain_from_text(after_text[:6000])
    ok_line_count = len(after_text.splitlines()) - len(text.splitlines()) in (0, 1)
    return ok_body, ok_value, ok_line_count


def _write_and_verify(
    ctx: _RunContext,
    rel: str,
    abspath: Path,
    row: dict[str, Any],
    text: str,
    info: dict[str, Any],
    new_text: str,
) -> None:
    """真写盘 + 正文不变核验 + JSONL 审计（写失败/核验失败均留证不崩批）。"""
    try:
        atomic_write_bytes(abspath, new_text.encode("utf-8"))
    except Exception as exc:  # noqa: BLE001 — 写失败必须留证不崩批
        _reject_row(ctx, row, "error", f"write_error:{type(exc).__name__}", "error")
        return
    ctx.written += 1
    after = abspath.read_bytes()
    row["sha_after"] = sha256_bytes(after)
    try:
        after_text = after.decode("utf-8")
    except UnicodeDecodeError:
        _reject_row(ctx, row, "error", "post_write_decode_error", "error")
        return
    ok_body, ok_value, ok_line_count = _verify_written(text, after_text)
    if not (ok_body and ok_value == info["inferred"] and ok_line_count):
        row["action"] = "error_rollback_needed"
        row["reject_reason"] = f"verify_failed(body={ok_body},value={ok_value},lines={ok_line_count})"
        ctx.stats["error"] += 1
    else:
        ctx.stats["applied"] += 1
    ctx.rows.append(row)
    ctx.audits.append(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "path": rel,
            "domain": info["inferred"],
            "source": info["source"],
            "level": info["level"],
            "action": row["action"],
            "sha_before": row["sha_before"],
            "sha_after": row["sha_after"],
            "verify_body_unchanged": ok_body,
        }
    )


def _resolve_row_action(
    ctx: _RunContext,
    rel: str,
    abspath: Path,
    row: dict[str, Any],
    text: str,
    info: dict[str, Any],
) -> None:
    """推断出值之后的落盘决策链：未决 → 计划动作 → 证据互斥 → 批次闸 → 写盘。"""
    if not info["inferred"]:
        _reject_row(ctx, row, "unresolved", info["reject_reason"], "unresolved")
        return

    new_text, action = plan_domain_line_edit(text, info["inferred"], ctx.evidence.vocab.legal)
    row["action"] = action
    if _reject_planned_action(ctx, row, action):
        return

    if not ctx.policy.allow_conflict_write and row["review_flag"] in CONFLICT_FLAGS:
        # 证据互斥（同目录票 vs 单文件独立证据）→ 不写盘，进未决清单人工裁定
        row["planned_action"] = action
        _reject_row(ctx, row, "needs_review", row["review_flag"], "needs_review")
        return

    if not ctx.policy.apply or ctx.written >= ctx.policy.batch:
        row["planned_action"] = action
        if not ctx.policy.apply:
            _reject_row(ctx, row, "would_change", "dry_run", "would_change")
        else:
            _reject_row(ctx, row, "batch_limited", "batch_limit_reached", "batch_limited")
        return

    _write_and_verify(ctx, rel, abspath, row, text, info, new_text)


def _process_targets(targets: list[str], ctx: _RunContext) -> None:
    """逐条走"护栏 → 读文 → 推断 → 决策"，产物累积到 ctx（rows/stats/audits/written）。"""
    for rel in targets:
        abspath = ctx.repo / rel
        row = _new_row(rel, abspath)
        if _guard_target_row(ctx, rel, row):
            continue
        text = _read_target_text(ctx, abspath, row)
        if text is None:
            continue
        info = _infer_for_target(ctx, rel, row)
        _resolve_row_action(ctx, rel, abspath, row, text, info)


_TABLE_FIELDNAMES = [
    "path",
    "exists_on_disk",
    "current_domain",
    "inferred",
    "inference_source",
    "level",
    "support",
    "chosen_note",
    "conflict",
    "review_flag",
    "illegal_candidates",
    "action",
    "planned_action",
    "reject_reason",
    "sha_before",
    "sha_after",
    "evidence",
]


def _write_inference_table(rows: list[dict[str, Any]], table_path: Path) -> None:
    """推断表 CSV 落盘（列序固定；source 另以 inference_source 列名暴露）。"""
    with table_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=_TABLE_FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            r["inference_source"] = r["source"]
            writer.writerow(r)


def _write_audits(audits: list[dict[str, Any]], audit_path: Path) -> None:
    """JSONL 审计追加（无写盘事件则不建文件）。"""
    if not audits:
        return
    with audit_path.open("a", encoding="utf-8") as fh:
        for rec in audits:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def process(
    *,
    selection: TargetSelection | None = None,
    locations: EvidenceLocations | None = None,
    policy: BackfillWritePolicy | None = None,
    output: OutputOptions | None = None,
    hooks: InjectionHooks | None = None,
) -> dict[str, Any]:
    """推断（可选回填）主流程。返回统计 dict（测试与报告共用）。

    入参按用途分为五个 frozen 参数对象（§5.150 Long Parameter List 治理）；
    任一组省略=取该组默认（默认整体=dry-run + 静态清单 + .runtime/tmp 输出）。
    """
    selection = selection or TargetSelection()
    locations = locations or EvidenceLocations()
    policy = policy or BackfillWritePolicy()
    output = output or OutputOptions()
    hooks = hooks or InjectionHooks()
    started = datetime.now(timezone.utc).isoformat()
    output.out_dir.mkdir(parents=True, exist_ok=True)
    ctx = _build_context(locations, policy, hooks)
    targets = _resolve_targets(ctx, selection)
    _process_targets(targets, ctx)
    rows = ctx.rows
    stats = ctx.stats
    audits = ctx.audits
    written = ctx.written

    out_dir = output.out_dir
    table_path = out_dir / ("inference_table.csv" if not policy.apply else "inference_table_apply.csv")
    _write_inference_table(rows, table_path)

    audit_path = out_dir / "audit.jsonl"
    _write_audits(audits, audit_path)

    report_path = out_dir / "dryrun_report.md"
    if output.write_report:
        report_path.write_text(
            render_report(
                stats=stats,
                rows=rows,
                total=len(targets),
                apply=policy.apply,
                started=started,
                table=table_path,
            ),
            encoding="utf-8",
        )

    return {
        "stats": stats,
        "rows": rows,
        "total": len(targets),
        "table": table_path,
        "audit": audit_path,
        "report": report_path,
        "written": written,
    }


def _report_head(*, total: int, apply: bool, started: str, table: Path) -> list[str]:
    """报告抬头：时间/模式/输入量/推断表位置。"""
    return [
        "# [DOMAIN] 补标工具干跑报告（backfill_module_domain.py）",
        "",
        f"- 生成时间（UTC）：{started}",
        f"- 模式：{'APPLY（已写盘）' if apply else 'DRY-RUN（零写盘）'}",
        f"- 输入条目：{total}",
        f"- 推断表：`{rel_to_repo(table)}`",
        "",
    ]


def _report_coverage(by_level: Counter, unresolved: list[dict[str, Any]]) -> list[str]:
    """a/b/c 级覆盖率 + 未决计数。"""
    lines = ["## 覆盖率", "", "| 级别 | 命中 |", "|------|------|"]
    for lvl in (LEVEL_A, LEVEL_B, LEVEL_C):
        lines.append(f"| {lvl} | {by_level.get(lvl, 0)} |")
    lines.append(f"| d_unresolved（未决） | {len(unresolved)} |")
    return lines


def _report_source_breakdown(by_source: Counter, stats: Counter, inferred_vals: Counter) -> list[str]:
    """证据源细分 + 动作分布 + 推断值 top 20。"""
    lines: list[str] = ["", "## 证据源细分", "", "| source | 命中 |", "|--------|------|"]
    for src, cnt in by_source.most_common():
        lines.append(f"| {src} | {cnt} |")
    lines += ["", "## 动作分布", "", "| action | 计数 |", "|--------|------|"]
    for act, cnt in stats.most_common():
        lines.append(f"| {act} | {cnt} |")
    lines += ["", "## 推断值分布（top 20）", "", "| domain | 计数 |", "|--------|------|"]
    for val, cnt in inferred_vals.most_common(20):
        lines.append(f"| {val} | {cnt} |")
    return lines


def _report_unresolved_attribution(by_reason: Counter, clusters: Counter) -> list[str]:
    """未决归因分布 + 未决目录簇 top 20。"""
    lines: list[str] = ["", "## 未决归因", "", "| reject_reason | 计数 |", "|---------------|------|"]
    for reason, cnt in by_reason.most_common():
        lines.append(f"| {reason} | {cnt} |")
    lines += ["", f"## 未决目录簇 top 20（共 {len(clusters)} 个目录）", "", "| 目录 | 未决数 |", "|------|--------|"]
    for d, cnt in clusters.most_common(20):
        lines.append(f"| {d} | {cnt} |")
    return lines


def _report_no_anchor_clusters(rows: list[dict[str, Any]]) -> list[str]:
    """无头锚点簇（目录 × 后缀分布）：本工具不瞎插，须先补头骨架。"""
    no_anchor = [r for r in rows if r["action"] == "no_anchor"]
    na_clusters: dict[str, Counter] = {}
    for r in no_anchor:
        na_clusters.setdefault(str(Path(r["path"]).parent), Counter())[Path(r["path"]).suffix or "<无后缀>"] += 1
    lines: list[str] = [
        "",
        f"## 无头锚点簇（no_anchor，共 {len(no_anchor)} 条 / {len(na_clusters)} 个目录）",
        "",
        "这些文件无 `# [MODULE]` 行（.py）或无 `治理锚定` 块（.yaml），`[DOMAIN]` 无处合规落地；",
        "**本工具不瞎插**，须先经头骨架通道（scaffold / add_module_translation）补齐再回填。",
        "",
        "| 目录 | 条数 | 后缀分布 |",
        "|------|------|----------|",
    ]
    for d in sorted(na_clusters, key=lambda k: (-sum(na_clusters[k].values()), k))[:15]:
        ext = na_clusters[d]
        lines.append(f"| {d} | {sum(ext.values())} | {', '.join(f'{e or '<无后缀>'}×{n}' for e, n in sorted(ext.items()))} |")
    return lines


def _report_unresolved_samples(unresolved: list[dict[str, Any]]) -> list[str]:
    """未决样本前 20 行（路径 + 归因 + 全证据串）。"""
    lines: list[str] = ["", f"## 未决样本前 20 行（共 {len(unresolved)} 条）", "", "```"]
    for r in unresolved[:20]:
        lines.append(f"{r['path']}\treject={r['reject_reason']}\tevidence={r['evidence']}")
    lines.append("```")
    return lines


def _report_arbitration(rows: list[dict[str, Any]]) -> list[str]:
    """证据强度仲裁面：review_flag 分布 + 待人工裁定清单 + 全量跨源分歧行。"""
    conflicts = [r for r in rows if r.get("conflict")]
    flagged = Counter(r["review_flag"] for r in rows if r.get("review_flag"))
    held = [r for r in rows if r["action"] == "needs_review"]
    lines: list[str] = [
        "",
        "## 证据强度仲裁",
        "",
        "取值序：同模块独立证据（depgraph file 节点 / ownership 家族票）> 同目录兄弟票 > 粗粒度前缀表。",
        "独立证据与兄弟票互斥时**不写盘**，转 `needs_review` 人工裁定（`--allow-conflict-write` 可放量）。",
        "",
        "| review_flag | 计数 |",
        "|-------------|------|",
    ]
    for flag, cnt in flagged.most_common():
        lines.append(f"| {flag} | {cnt} |")
    if not flagged:
        lines.append("| （无） | 0 |")
    lines += ["", f"### 待人工裁定（{len(held)} 条，本工具零写入）", "", "```"]
    for r in held[:40]:
        lines.append(
            f"{r['path']}\tplanned={r['planned_action']}\tinferred={r['inferred']}\tconflict={r['conflict']}"
        )
    if not held:
        lines.append("（无）")
    lines += ["```", "", f"### 全量跨源分歧行（{len(conflicts)} 条，含弱分歧）", "", "```"]
    for r in conflicts[:20]:
        lines.append(f"{r['path']}\tinferred={r['inferred']}\tconflict={r['conflict']}")
    if not conflicts:
        lines.append("（无）")
    lines.append("```")
    return lines


def render_report(
    *,
    stats: Counter,
    rows: list[dict[str, Any]],
    total: int,
    apply: bool,
    started: str,
    table: Path,
) -> str:
    """人读报告（覆盖率按 a/b/c 级别 + 未决簇）。"""
    by_level = Counter(r["level"] for r in rows if r["inferred"])
    by_source = Counter(r["source"] for r in rows if r["inferred"])
    unresolved = [r for r in rows if not r["inferred"]]
    by_reason = Counter(r["reject_reason"] for r in unresolved)
    clusters = Counter(str(Path(r["path"]).parent) for r in unresolved)
    inferred_vals = Counter(r["inferred"] for r in rows if r["inferred"])
    lines = _report_head(total=total, apply=apply, started=started, table=table)
    lines += _report_coverage(by_level, unresolved)
    lines += _report_source_breakdown(by_source, stats, inferred_vals)
    lines += _report_unresolved_attribution(by_reason, clusters)
    lines += _report_no_anchor_clusters(rows)
    lines += _report_unresolved_samples(unresolved)
    lines += _report_arbitration(rows)
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    """CLI 参数。"""
    p = argparse.ArgumentParser(
        description="模块 [DOMAIN] 头字段确定性补标生成器（三级证据推断 + 可执行回填）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--list", dest="list_path", help=f"待补标清单 CSV（默认 {rel_to_repo(DEFAULT_LIST)}）")
    p.add_argument("--all", action="store_true", help="忽略静态清单，重扫全仓缺/空/非法 [DOMAIN] 的文件")
    p.add_argument("--files", help="仅处理指定文件（逗号分隔，调试/自测用）")
    p.add_argument("--apply", action="store_true", help="真写盘（默认 dry-run 零写入）")
    p.add_argument("--batch", type=int, default=200, help="--apply 单批写入上限（默认 200）")
    p.add_argument("--out-dir", default=str(DEFAULT_TMP_DIR), help="报告/推断表/审计输出目录")
    p.add_argument("--vocab-file", default=DEFAULT_VOCAB_FILE, help="域合法性校验词表（SSoT）")
    p.add_argument("--min-sibling-support", type=int, default=2, help="兄弟/家族票成立的最小支持数")
    p.add_argument("--ignore-git-dirty", action="store_true", help="应急：关闭 git 脏文件护栏（默认开启）")
    p.add_argument(
        "--allow-conflict-write",
        action="store_true",
        help="人工裁定后放量：允许写证据互斥行（默认不写，标 needs_review）",
    )
    p.add_argument("--no-report", action="store_true", help="不写 markdown 报告")
    return p


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    args = build_parser().parse_args(argv)
    try:
        res = process(
            selection=TargetSelection(
                list_path=Path(args.list_path) if args.list_path else None,
                all_mode=args.all,
                files=args.files.split(",") if args.files else None,
            ),
            locations=EvidenceLocations(repo=REPO_ROOT, vocab_file=args.vocab_file),
            policy=BackfillWritePolicy(
                apply=args.apply,
                batch=args.batch,
                min_sibling_support=args.min_sibling_support,
                skip_git_guard=args.ignore_git_dirty,
                allow_conflict_write=args.allow_conflict_write,
            ),
            output=OutputOptions(out_dir=Path(args.out_dir), write_report=not args.no_report),
        )
    except SystemExit as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as exc:  # noqa: BLE001 — 顶层异常归一为 EXIT_ERROR
        print(f"ERROR: 脚本异常 {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR

    stats = res["stats"]
    print("=" * 64)
    print(f"[DOMAIN] 补标报告（{'APPLY' if args.apply else 'DRY-RUN'}）")
    print("=" * 64)
    print(f"  输入条目            : {res['total']}")
    for key in (LEVEL_A, LEVEL_B, LEVEL_C):
        print(f"  命中 {key:<20}: {sum(1 for r in res['rows'] if r['level'] == key)}")
    print(f"  未决                : {stats['unresolved']}")
    print(f"  待变更(would_change): {stats['would_change']}")
    print(f"  已写入(applied)     : {stats['applied']}")
    for k in ("already_ok", "skip_ghost", "skip_git_dirty", "skip_excluded", "conflict_existing_legal", "no_anchor", "needs_review", "batch_limited", "error"):
        if stats.get(k):
            print(f"  {k:<21}: {stats[k]}")
    print(f"  推断表              : {rel_to_repo(res['table'])}")
    print(f"  报告                : {rel_to_repo(res['report']) if not args.no_report else '<未写>'}")
    print(f"  审计                : {rel_to_repo(res['audit'])}")
    if stats.get("error") or stats.get("unresolved"):
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
