# [BLUEPRINT] MOD-LIB-006 | docs/03_modules/_domain_library/blueprint.md | §模块清单
# [MODIFY-GUARD] 改本文件必同步跑 tests/governance/test_scan_scope_convergence_equivalence.py 的同一性断言
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [MODULE] zephyr.governance.consumption.scan_scope_converged
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pathlib; re; dataclasses; typing（全部 stdlib，零第三方）
# [CONSUMERS] scripts.governance.d5_architecture.generators.generate_connection_matrix（波 13 包 13.4）;
#   zephyr.governance.consumption.consumption_census（包 13.3 丁道，本模块薄别名消费者）;
#   zephyr.governance.audit.library_new_module_reconciler（包 13.2 丙道，本模块薄别名消费者）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读（零写入）; 全仓"有没有消费者/有没有接线"判定的唯一扫描口径（波 13 §3.4 定档，
#   壬道收敛版），第二套口径=第二真源=禁止；丙/丁两侧同名公开量必须是本模块薄别名（import 绑定），
#   禁在车道文件里再派生（等价性红证 tests/governance/test_scan_scope_convergence_equivalence.py 看住）
# [ERROR_CONTRACT] 不吞异常——目录缺失返回空迭代（口径本身不判定存在性）
# [TESTS] tests/governance/test_connection_matrix_rulers.py;
#   tests/governance/test_scan_scope_convergence_equivalence.py
# [TTL] permanent
# create-guard-not-dup: 本件＝消费面/连接矩阵/图书馆共用的单一扫描口径常量定义（壬道收敛唯一真源，只定义 roots/exclusions 不实现任何 gate/scanner）——与死信所列 depgraph_scope_gate/blueprint_code_alignment_checker/yaml_anchor_consistency_scanner 零功能交集，命中词「scan scope」「scan hit」纯系本文件名与 docstring 措辞的探针碰撞（q-20260928-st-zcloseout-20260926-0003 死信处方）
# [ARCH-REF] 波 13 三件一体计划（无在册 #ARCH 编号，勿杜撰）: docs/_working/three_piece_infra/00_plan_and_ownership.md
# [CREATION-TOKEN] pending-registration: wave13-p3-matrix-20260926（登记由总筹在热册唯一写手制下合批；
#   壬道收敛=改写既有文件，不新增模块，无新 token）
"""scan_scope_converged — 波 13 §3.4 单一扫描口径的唯一定义处（壬道收敛版）。

大白话：判断"某个东西到底有没有人用/有没有接上"时，全波（消费面普查 + 连接矩阵 +
图书馆入编）必须用同一把尺子去仓库里翻文件。这把尺子在本文件里只定义一次：
翻 src/ + scripts/ + config/ 下的 .py 与 .yaml，.md 与 docs/ 一律不算消费者，
再排除 14 号文三层（producer / display / infra）**加观察者层**（尺自己提名不算客）。

收敛记录（三份近重复副本→本文件唯一真源，裁决详见
docs/_working/three_piece_infra/scope_convergence/CASE.md §二）：
  * 后缀取 `.py`/`.yaml`（§3.4 原文点名；丁道多出的 .yml 输——裁定文本非沉默，从严不适用）
  * display 取 14 号文原样 `frontend/`（路径子串；丁道锚定 src/zephyr/frontend/ 是其子集，
    戊道仅 dashboard/components/ 太窄被废——丁尺 R-G 对 app_panel.py=False 的断言也要求整删）
  * producer/infra 取丙/丁并集（§3.4 对"怎么算命中"沉默→并集=从严=少假"有客"）
  * observer 第四层保留（丁道独立发现：普查引擎/旧壳/生成器/本尺自身提到实体名＝自我认证
    假绿），并扩容到收敛后的三件尺自身文件
  * 面/层两分（C7）：`in_scan_surface`=扫描对象面（根+后缀+噪声目录+面级前缀），
    `counts_as_consumer`=面 ∧ ¬四层。矩阵取证走面（桶另有限定），消费者计数走判据。

为什么 .md 不算：文档提一句就把"有消费者"判绿，是族① 已实证的假绿（IND-REV-001）。
为什么 scripts/ 要算：40+ 个真跑批件都在 scripts/，不算就会把它们判成孤岛。
为什么 config/ 要算：TDM 与任务声明是真运行输入。
与 ORPHAN-MODULE 门的分歧不消除：那是**创建期**判据、扫 src/**，对象不同→不并
（内收判据"跨域不同对象→不并"），详见 CASE.md §六。

# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/scan_scope_converged.yaml
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable, Iterator

__all__: Final = [
    "SCOPE_RULING_REF",
    "SCAN_SCOPE_DIRS",
    "SCAN_SCOPE_SUFFIXES",
    "EXCLUDED_DIR_NAMES",
    "EXCLUDED_PATH_PREFIXES",
    "ScanScope",
    "CONSUMER_SCAN_SCOPE",
    "DOC_EVIDENCE_SCOPE",
    "DOC14_INFRA_TOKENS",
    "PRODUCER_EXCLUDE_RE",
    "DISPLAY_EXCLUDE_RE",
    "INFRA_EXCLUDE_RE",
    "OBSERVER_EXCLUDE_RE",
    "EXCLUSION_LAYERS",
    "exclusion_layer",
    "is_doc14_layer_excluded",
    "counts_as_consumer",
    "in_scan_surface",
    "CONSUMER_CAP",
    "ScanHit",
    "iter_scope_files",
    "grep_scope",
    "scope_fingerprint",
]

#: 口径真源指针（案卷引用用，勿在此复制条款全文）
SCOPE_RULING_REF: Final = "docs/_working/three_piece_infra/00_plan_and_ownership.md §3.4（单一 scope 定档）"

#: 版本控制/构建噪声与产物面（任何口径都不翻）——戊集 ∪ 丁集（C6：并集，语义中性）
EXCLUDED_DIR_NAMES: Final = frozenset({
    ".git", ".runtime", ".venv", "__pycache__", "node_modules", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "dist", "build", ".venvs", ".venv-local",
    "tmp", "_archive",
})

#: 14 号文 infra 层词表——取 14 号文 :11 原词（丙道原样；大小写不敏感子串匹配，
#: 覆盖丁道"DDL"大写形态——统一在 lower() 上匹配即丁的超集，从严）
DOC14_INFRA_TOKENS: Final = (
    "scripts/ch",
    "ddl",
    "backfill",
    "tasks.yaml",
    "known_data_gaps",
    "data_supply_sentinel",
    "speed_tester",
)

#: 14 号文三层 + 观察者层的机械判据（一律对 lower() 后的正斜杠相对路径匹配）。
#: producer：目录层（数据生产者自家）+ 丙道 stem 子串（provider/collector/fetcher，
#: 14 号文 `*provider*` 星号原形）∪ 丁道增量 writer/ingest（C3 并集，从严）。
PRODUCER_EXCLUDE_RE: Final = re.compile(
    r"(^src/zephyr/data/implementations/)"
    r"|(/[^/]*(?:provider|collector|fetcher)[^/]*\.py$)"
    r"|(/[^/]*(?:writer|ingest)[^/]*\.py$)"
)
#: display：14 号文原词 `frontend/`（路径子串，丙道原样——戊道 components-only 太窄被废，
#: 丁道锚定形态是其子集）；scripts/dashboard/ 为丁道增量保留（C2：展示面整删）。
DISPLAY_EXCLUDE_RE: Final = re.compile(r"(frontend/)|(^scripts/dashboard/)")
#: infra：14 号文词表子串 + 丁道增量 `^scripts/.*ch_`（运维/测速件同族语义；
#: 注意该形态亦把 scripts/governance/d5_architecture/… 纳入 infra 面——案卷 C4 已记）。
_INFRA_EXTRA_RE: Final = re.compile(r"(^scripts/.*ch_)")
INFRA_EXCLUDE_RE: Final = re.compile(
    "|".join(re.escape(t) for t in DOC14_INFRA_TOKENS) + r"|(^scripts/.*ch_)"
)
#: 观察者层（丁道实测新发现的第四层 + 壬道扩容：三件尺自身提名实体名＝自我认证假绿，
#: 与 .md 假绿同型；§3.4 沉默→从严保留并扩容，裁决 C5）
OBSERVER_EXCLUDE_RE: Final = re.compile(
    r"(consumption_census)|(indicator_usage_audit)|(generate_wiring_registry)"
    r"|(scan_scope_converged)|(generate_connection_matrix)|(library_new_module_reconciler)"
)

#: 四层（名字与丁道原名一致；判定顺序=producer→display→infra→observer）
EXCLUSION_LAYERS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    ("producer", PRODUCER_EXCLUDE_RE),
    ("display", DISPLAY_EXCLUDE_RE),
    ("infra", INFRA_EXCLUDE_RE),
    ("observer", OBSERVER_EXCLUDE_RE),
)


def exclusion_layer(rel_path: str) -> str | None:
    """命中文件属于哪一层（producer/display/infra/observer）；None=可算消费者候选。"""
    rp = rel_path.replace("\\", "/").lower()
    for name, rx in EXCLUSION_LAYERS:
        if rx.search(rp):
            return name
    return None


def is_doc14_layer_excluded(rel_path: str) -> bool:
    """14 号文**三层**（producer/display/infra）剔除判定——丙道原名原义（不含观察者层；
    消费判定请走 counts_as_consumer，四层齐全）。"""
    rp = rel_path.replace("\\", "/").lower()
    return any(
        rx.search(rp) for name, rx in EXCLUSION_LAYERS if name != "observer"
    )


@dataclass(frozen=True)
class ScanScope:
    """消费者口径的完整声明（可注入替代 roots 供测试沙盘）。"""

    roots: tuple[str, ...]
    suffixes: tuple[str, ...]
    excluded_dir_names: frozenset[str]
    excluded_rel_prefixes: tuple[str, ...]

    def iter_files(self, repo_root: Path, *, extra_suffixes: tuple[str, ...] = ()) -> Iterator[Path]:
        for rel in self.roots:
            base = repo_root / rel
            if not base.exists():
                continue
            for p in base.rglob("*"):
                if not p.is_file():
                    continue
                if p.suffix not in self.suffixes and p.suffix not in extra_suffixes:
                    continue
                rp = p.relative_to(repo_root).as_posix()
                if self.in_surface_parts(rp):
                    yield p

    def in_surface_parts(self, rel_posix: str) -> bool:
        """噪声目录与面级前缀剔除（不含后缀/根判定，供迭代与谓词共用）。"""
        if any(part in self.excluded_dir_names for part in rel_posix.split("/")[:-1]):
            return False
        return not any(rel_posix.startswith(x) for x in self.excluded_rel_prefixes)

    def in_scan_surface(self, rel_path: str) -> bool:
        """扫描面谓词（不含层级排除——层级命中仍在面上，只是不计客）。"""
        rp = rel_path.replace("\\", "/")
        if rp.endswith(".md") or rp.startswith("docs/"):
            return False
        if not self.in_surface_parts(rp):
            return False
        top = rp.split("/")[0] + "/"
        if top not in self.roots:
            return False
        return Path(rp).suffix in self.suffixes

    def counts_as_consumer(self, rel_path: str) -> bool:
        """§3.4 完整口径谓词＝在扫描面上 **且** 不落层级排除（producer/display/infra/observer）。"""
        return self.in_scan_surface(rel_path) and exclusion_layer(rel_path) is None


#: 消费者面单一实例：roots 带斜杠（丁道形制，in_scan_surface 依赖 top+"/" 成员判定）；
#: 后缀 .py/.yaml（§3.4 原文；.yml 输，裁决 C1）；面级前缀保留戊道原值 components/
#: （显示层整删由 DISPLAY_EXCLUDE_RE 负责——同一文件只此一处声明，C7）。
CONSUMER_SCAN_SCOPE: Final[ScanScope] = ScanScope(
    roots=("src/", "scripts/", "config/"),
    suffixes=(".py", ".yaml"),
    excluded_dir_names=EXCLUDED_DIR_NAMES,
    excluded_rel_prefixes=("src/zephyr/frontend/dashboard/components/",),
)

#: 文档侧（只作证据，不作消费者）——`.md` 提一句就算"有客"是 IND-REV-001 假绿的病根
DOC_EVIDENCE_SCOPE: Final[ScanScope] = ScanScope(
    roots=("src/", "scripts/", "config/", "docs/"),
    suffixes=(".md",),
    excluded_dir_names=EXCLUDED_DIR_NAMES,
    excluded_rel_prefixes=(),
)

#: 全波统一出口谓词（丙 derive / 丁 scope_verdict / 矩阵消费判定都走这一个名字）
def counts_as_consumer(rel_path: str) -> bool:
    """该文件能否算消费者＝§3.4 单一 scope 唯一判据（面 ∧ ¬四层）。"""
    return CONSUMER_SCAN_SCOPE.counts_as_consumer(rel_path)


def in_scan_surface(rel_path: str) -> bool:
    return CONSUMER_SCAN_SCOPE.in_scan_surface(rel_path)


#: 消费者清单上限（防单资产吃掉数组；超限在 detail 里留 truncated 痕——丙道原值并入真源）
CONSUMER_CAP: Final[int] = 200

# ── 戊道公开名的值别名（单一声明处派生，非第二真源）────────────────────────
SCAN_SCOPE_DIRS: Final = tuple(r.rstrip("/") for r in CONSUMER_SCAN_SCOPE.roots)
SCAN_SCOPE_SUFFIXES: Final = CONSUMER_SCAN_SCOPE.suffixes
EXCLUDED_PATH_PREFIXES: Final = CONSUMER_SCAN_SCOPE.excluded_rel_prefixes


@dataclass(frozen=True)
class ScanHit:
    """一条接线证据：相对路径 + 行号 + 命中行原文（截断）。"""

    rel_path: str
    line_no: int
    line: str

    def as_ref(self) -> str:
        return f"{self.rel_path}:{self.line_no}"


def iter_scope_files(repo_root: Path) -> Iterator[Path]:
    """按 §3.4 扫描对象面产出文件（排序稳定，供逐字节可复现的生成物）。

    返回**面**上的文件（含四层命中文件）：矩阵桶式取证需要 producer_only 类证据可见性，
    消费者计数请在谓词层走 counts_as_consumer（面/层两分=裁决 C7，非第二口径）。
    """
    root = Path(repo_root)
    yield from sorted(CONSUMER_SCAN_SCOPE.iter_files(root), key=lambda p: p.relative_to(root).as_posix())


def grep_scope(
    repo_root: Path,
    pattern: str,
    *,
    word_boundary: bool = False,
    max_hits: int = 5,
    skip_files: frozenset[str] = frozenset(),
    only_consumers: bool = False,
) -> list[ScanHit]:
    """§3.4 口径内的词边界正则命中（返回前 max_hits 条证据，全量计数不返回 0 伪装）。

    word_boundary=True 时对 pattern 加 ``(?<![\\w.-])...(?![\\w.-])`` 包裹——
    标识符含连字符（DS-001/FCT-X-001），默认 \\b 会把连字符当边界造成误命中。
    only_consumers=True 时进一步只收 counts_as_consumer 文件（消费者计数专用出口）。
    读不动的文件（编码/权限）跳过但不静默：调用方拿到 hits 为空时须自行判
    "口径内无命中"与"文件不可读"是两回事（见 CASE.md 读数通道披露）。
    """
    body = rf"(?<![\w.-]){pattern}(?![\w.-])" if word_boundary else pattern
    rx = re.compile(body)
    root = Path(repo_root)
    hits: list[ScanHit] = []
    for path in iter_scope_files(root):
        rel = path.relative_to(root).as_posix()
        if rel in skip_files:
            continue
        if only_consumers and not counts_as_consumer(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if rx.search(line):
                hits.append(ScanHit(rel, line_no, line.strip()[:200]))
                if len(hits) >= max_hits:
                    return hits
    return hits


def scope_fingerprint(repo_root: Path) -> dict[str, int]:
    """口径自检量（供案卷与 --check 的自相一致性判据，禁写死在散文里）。"""
    n = 0
    total = 0
    consumer_n = 0
    for path in iter_scope_files(Path(repo_root)):
        n += 1
        total += path.stat().st_size
        rel = path.relative_to(Path(repo_root)).as_posix()
        if counts_as_consumer(rel):
            consumer_n += 1
    return {"scope_files": n, "scope_bytes": total, "consumer_files": consumer_n}
