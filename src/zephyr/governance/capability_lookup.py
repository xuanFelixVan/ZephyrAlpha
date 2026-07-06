# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §registry
# [MODULE] zephyr.governance.capability_lookup
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] AI sessions (查询能力真源); GitCommitGateway (check_ssot_conflicts, check_capability_duplicates); scaffold (find_files_by_module_path); check_ssot_gate (check_ssot_conflicts, check_capability_duplicates)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] YAML 真源是人工裁定的能力索引（capability_id/aliases/description + 可选 override/manual 条目）；canonical_file/module_id/blueprint_id/domain/maturity/duplicates/removed_duplicates 均由磁盘扫描+git log 自动派生，不持久化为第二真源
# [MODIFY-GUARD] capability_canonical_file_registry.yaml (能力索引真源); governance/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises FileNotFoundError if YAML 真源缺失; returns empty list on scan errors; git 派生失败降级为空列表（不阻断查询）
# [TESTS] tests/test_capability_lookup.py
# [A_module] module_id=MOD-GOV_capability_lookup | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CapabilityLookup — 能力→真源文件反查注册表的查询 API + 扫描/派生逻辑（合一）
================================================================================

解决"AI 不知道某功能已存在、真源在哪"的信息不可达问题。

设计原则（第一性原理 / 向内收）：
  1. 真源唯一：YAML（capability_canonical_file_registry.yaml）是能力索引真源，
     人工只声明 capability_id / aliases / description（+ 可选 override / manual 条目）。
     canonical_file / module_id / blueprint_id / domain / maturity / duplicates /
     removed_duplicates 全部由磁盘扫描 + git log 自动派生——避免与代码头部同步漂移。
  2. 责任唯一：本模块一个文件管扫描+派生+查询+比对+CLI，不拆分扫描器脚本。
  3. 自动维护：CapabilityLookup() 初始化时自动扫磁盘头部 + 派生 git 历史，
     无需手工跑扫描器。canonical 文件迁移时自动跟随（basename 启发式 + 成熟度排序）。
  4. 无需同步：不持久化 @generated report，查询时实时算，避免第二数据源漂移。

对标：K8s Service（声明式 capability_id）+ Endpoints 控制器（实时发现 canonical）——
      Endpoints 不持久化为独立资源，是 Service 的实时投影。本模块同构。

派生规则（治本：消除 YAML↔代码头部同步成本）：
  - canonical 候选：磁盘文件 basename(无 .py) ∈ {capability_id} ∪ aliases（标准化后）
  - canonical 选择优先级：
      1. canonical_override（人工裁定，最高优先级）
      2. 单候选 → auto canonical
      3. 多候选 → 成熟度排序(production > prototype > design) → import 数 → 歧义(需 override)
  - duplicates (auto)：磁盘上同 basename 的其他候选
      relation 由 blueprint 比对派生：同蓝图=conflicting；异蓝图=sibling
  - duplicates_manual：语义 sibling（auto 按 basename 匹配会漏掉，人工声明 relation + note）
  - removed_duplicates (auto)：git log --diff-filter=D 派生（basename 匹配 + 头部验证）
  - removed_duplicates_manual：未被 git 跟踪的历史文件（人工声明 path + note）

用法：
    from zephyr.governance.capability_lookup import CapabilityLookup

    reg = CapabilityLookup()                  # 自动加载 YAML + 扫盘 + 派生
    reg.find("session handoff")               # 关键词搜索
    reg.get("rollback_executor")              # 按 capability_id 精确查
    reg.list_ssot_conflicts()                 # 列出同蓝图多实现冲突
    reg.check_file_canonical("src/zephyr/xxx.py")  # 反查某文件是哪个能力的 canonical

设计边界（ARCH-031 局限2 文档化，2026-07-01）：
  本模块是"能力→真源文件反查"（声明式能力索引），不是"符号发现"。
  - 能力发现（本模块）：查"某个能力是否存在 + canonical 在哪"，
    覆盖范围 = YAML 已声明的 capability 条目。
  - 符号发现（Grep）：查"某个符号（函数名/类名）定义在哪"，
    覆盖范围 = src/zephyr/**/*.py 全部文件（含未声明能力的子目录文件）。
  新 AI 知道符号名时，直接用 Grep 搜索符号名即可唯一命中 canonical 位置，
  不需要在本模块声明所有子目录文件（维护成本高且无必要，违反向内收原则①）。

CLI:
    python -m zephyr.governance.capability_lookup --find "handoff"
    python -m zephyr.governance.capability_lookup --list-conflicts
    python -m zephyr.governance.capability_lookup --check-file src/zephyr/xxx.py
"""

from __future__ import annotations

from typing import Final
import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------
REGISTRY_YAML: Final[Path] = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "capability_canonical_file_registry.yaml"
# 治本（P8 Phase 3 S4 可发现性）：多根化让 scripts/governance/ 下文件进入自动扫描，
# 消除 canonical_override 手填需求（原 scripts/ 不在扫描范围，需手动声明 canonical）
SCAN_ROOTS: Final[list[Path]] = [
    REPO_ROOT / "src" / "zephyr",
    REPO_ROOT / "scripts" / "governance",
]
# 向后兼容别名（单 root 时代的外部引用）：指向 SCAN_ROOTS[0]
SCAN_ROOT: Final[Path] = SCAN_ROOTS[0]
HEADER_SCAN_LIMIT: Final[int] = 30  # 头部字段都在前 30 行，只读这么多省时间

# 成熟度排序权重（production > prototype > design）；未知成熟度=0
_MATURITY_RANK: dict[str, int] = {"production": 3, "prototype": 2, "design": 1}

# CJK 公共子串匹配最小窗口长度（治本：阈值真源唯一，改此处全跟随）
# 取 3：2 字符窗口（如"路径"）过宽会假阳性命中所有含该子串的条目；
# 3 字符窗口（如"仓库根"）才能捕获语义 core 又避免巧合命中
_CJK_MIN_SUBSTRING: int = 3

# 能力重复修复指令（L2 gateway / L3 hook 共用，真源唯一，避免两处硬编码漂移）
CAPABILITY_DUPLICATE_FIX_HINT: Final[tuple] = (
    "修复指令：删除上述新增文件，扩展现有 canonical 文件后重新 commit"
    "\n  查已有 canonical：python -m zephyr.governance.capability_lookup --find <关键词>"
)


# ---------------------------------------------------------------------------
# 头部正则（代码文件十五字段头部）
# ---------------------------------------------------------------------------

_RE_MODULE = re.compile(r"^#\s*\[MODULE\]\s*(.+?)\s*$")
_RE_BLUEPRINT = re.compile(r"^#\s*\[BLUEPRINT\]\s*(\S+)")
_RE_DOMAIN = re.compile(r"^#\s*\[DOMAIN\]\s*(\S+)")
_RE_MATURITY = re.compile(r"^#\s*\[MATURITY\]\s*(\S+)")
_RE_MODULE_ID = re.compile(r"module_id=([^\s|]+)")
# 40 字符 hex 小写 = git commit hash（用于解析 git log --format=%H 输出）
_RE_GIT_HASH = re.compile(r"^[0-9a-f]{40}$")


# ---------------------------------------------------------------------------
# 数据模型（dataclass，无外部依赖，只读查询不需要 Pydantic 验证）
# ---------------------------------------------------------------------------

@dataclass
class HeaderInfo:
    """代码文件头部提取结果（[MODULE]/[A_module]/[BLUEPRINT]/[DOMAIN]/[MATURITY] + docstring 首行）。"""
    path: str
    module_path: str = ""        # [MODULE] zephyr.xxx.yyy
    module_id: str = ""          # [A_module] module_id=MOD-XXX_yyy
    blueprint_id: str = ""       # [BLUEPRINT] MOD-XXX
    domain: str = ""             # [DOMAIN] D-XXX
    maturity: str = ""           # [MATURITY] prototype/production/design
    docstring: str = ""          # 第一行 docstring（用于辅助识别）


@dataclass
class SSoTConflict:
    """SSoT 冲突条目（check_ssot_conflicts 返回）。

    L2（GitCommitGateway）和 L3（pre-commit hook）共享检测逻辑的唯一真源返回类型。
    """
    rel_path: str                # 新增文件相对路径（正斜杠）
    module_path: str             # 新增文件声明的 module_path
    conflicts: list[str]         # 冲突的已有文件列表（已排除新文件自己）


@dataclass
class CapabilityDuplicate:
    """能力重复阻断信号条目（check_capability_duplicates 返回）。

    L2（GitCommitGateway._check_ssot_canonical）和 L3（check_ssot_gate.py pre-commit hook）
    共享检测逻辑的唯一真源返回类型。返回此类型 = 阻断信号（门禁 BLOCK）。

    设计裁定（B 方案，向内收 2.3 治本）：去掉软层 advisory（find() 语义召回）——
    软层 TP≈0（Python 标识符下划线是 word char，handoff_v2 不可分割，find() 匹配不到），
    且 advisory 不阻断=无人行动=死数据。commit 门禁只负责高置信阻断（basename 精确碰撞），
    低置信检测不是门禁职责，由 AGENTS.md §9.0 手动查重 + reconciler 周期审计兜底。
    """
    rel_path: str                # 新增文件相对路径（正斜杠）
    capability_id: str           # 撞上的能力 ID
    canonical_file: str          # 该能力现有 canonical 文件
    relation: str                # conflicting/sibling/unknown/canonical_displaced_*
    detail: str                  # 人类可读说明


@dataclass
class ModuleIdConflict:
    """module_id 全局冲突条目（check_module_id_conflicts 返回，P0-2 防再生门禁）。

    同一个 module_id 出现在多个文件 = 跨域复刻信号（病根1：AI 跨域复制时
    连 module_id 一起抄过去，但忘记改）。与 check_ssot_conflicts（同 module_path）
    互补：module_path 是导入路径，module_id 是逻辑标识——两者不同维度。
    一个 module_id 只能对应一个真源文件（责任唯一，真源唯一）。
    """
    rel_path: str                # 新增文件相对路径（正斜杠）
    module_id: str               # 冲突的 module_id
    conflicts: list[str]         # 已声明同 module_id 的已有文件列表（已排除新文件自己）


@dataclass
class DomainMismatch:
    """MODULE 声明域与物理路径域不一致条目（check_module_domain_consistency 返回，P0-3 防再生门禁）。

    文件物理在 src/zephyr/governance/ 但 [MODULE] 声明 zephyr.infrastructure.xxx
    = 跨域复刻后忘记改 module_path（病根1 的典型症状：连导入路径一起抄）。
    Python 导入路径必须与物理目录一致（否则 import 不到），声明不符 = 谎报归属。
    """
    rel_path: str                # 新增文件相对路径（正斜杠）
    module_path: str             # 新增文件声明的 module_path
    declared_domain: str         # module_path 第2段（如 "infrastructure"）
    physical_domain: str         # 物理路径第3段（如 "governance"）


@dataclass
class CapabilityEntry:
    """能力条目。

    YAML 声明字段（人工维护，低频）：
      capability_id / aliases / description
      + 可选 canonical_override / duplicates_manual / removed_duplicates_manual

    派生字段（运行时算，不来自 YAML）：
      canonical_file / module_id / blueprint_id / domain / maturity / status /
      canonical_alive / duplicates / removed_duplicates / pending_candidates /
      derivation_note（派生过程说明，供 debug/审计）
    """
    capability_id: str
    aliases: list[str] = field(default_factory=list)
    description: str = ""
    # 可选人工裁定（覆盖或补充派生）
    canonical_override: str = ""
    duplicates_manual: list[dict] = field(default_factory=list)
    removed_duplicates_manual: list[dict] = field(default_factory=list)
    # 派生字段
    canonical_file: str = ""
    module_id: str = ""
    blueprint_id: str = ""
    domain: str = ""
    maturity: str = ""
    status: str = "alive"
    canonical_alive: bool = True
    duplicates: list[dict] = field(default_factory=list)
    removed_duplicates: list[dict] = field(default_factory=list)
    pending_candidates: list[dict] = field(default_factory=list)
    derivation_note: str = ""


# ---------------------------------------------------------------------------
# CapabilityLookup 主类
# ---------------------------------------------------------------------------

class CapabilityLookup:
    """能力→真源文件反查注册表查询 API + 派生逻辑。

    初始化时：
      1. 加载 YAML 真源（capability_id / aliases / description + 可选 manual 字段）
      2. 扫描 src/zephyr/**/*.py 头部（前 30 行）
      3. 派生 canonical + duplicates（basename 启发式 + 成熟度排序）
      4. 派生 removed_duplicates（git log --diff-filter=D，可选）
      5. 合并（reconcile）：标记 canonical_alive + 合并 manual + 发现 pending_candidates

    查询时走内存缓存，不再次扫盘。session 内有效（AI session 生命周期内文件变化少）。
    """

    def __init__(
        self,
        yaml_path: Path | str | None = None,
        scan_root: Path | str | list[Path | str] | None = None,
        *,
        scan: bool = True,
        derive_removed: bool = True,
    ) -> None:
        self._yaml_path: Path = Path(yaml_path) if yaml_path is not None else REGISTRY_YAML
        # 治本（P8 Phase 3）：scan_root 接受单根或多根（向后兼容）
        # None → SCAN_ROOTS（默认双根：src/zephyr + scripts/governance）
        # Path/str → [Path]（向后兼容单根测试场景）
        # list → [Path(x) for x in list]
        if scan_root is None:
            self._scan_roots: list[Path] = list(SCAN_ROOTS)
        elif isinstance(scan_root, list):
            self._scan_roots = [Path(r) for r in scan_root]
        else:
            self._scan_roots = [Path(scan_root)]
        # 向后兼容：单根时代的外部引用（如 summary() 输出）
        self._scan_root: Path = self._scan_roots[0]
        # canonical_file 在 YAML 中格式为 src/zephyr/xxx 或 scripts/governance/yyy，
        # 相对基准是项目根。单根时 scan_root.parent.parent = 项目根（向后兼容测试 tmp_path）；
        # 多根时直接用 REPO_ROOT（双根的公共祖先）。
        if len(self._scan_roots) == 1:
            self._base_root: Path = self._scan_roots[0].parent.parent
        else:
            self._base_root = REPO_ROOT
        self._capabilities: list[CapabilityEntry] = []
        self._disk_headers: dict[str, HeaderInfo] = {}
        self._loaded = False
        # git 派生缓存（惰性）：[(path, commit_hash), ...]，None=未加载
        self._git_deletions: list[tuple[str, str]] | None = None
        # git show 头部缓存："{commit}:{path}" → HeaderInfo | None，避免多能力匹配同一删除文件时重复 subprocess
        self._git_show_cache: dict[str, HeaderInfo | None] = {}
        # import 数缓存（tiebreaker）：module_path → importer count
        self._import_count_cache: dict[str, int] = {}
        # removed_duplicates 惰性派生标志：__init__ 不派生，首次查询（_entry_to_dict）时触发
        self._removed_derived: bool = False
        # git 派生仅在 scan=True 时有意义（scan=False 不派生任何派生字段）
        self._derive_removed = derive_removed and scan
        # YAML 真源必须加载（与 scan 解耦——scan=False 只跳过磁盘扫描+派生，不跳过 YAML）
        self._capabilities = self._load_yaml()
        if scan:
            self._disk_headers = self._scan_disk_headers()
            self._derive_all()
            self._reconcile()
        self._loaded = True

    # ---- 加载 + 扫描 ----

    def reload(self) -> None:
        """重新加载 YAML + 重扫磁盘 + 重派生（YAML 更新后调用）。"""
        self._capabilities = self._load_yaml()
        self._disk_headers = self._scan_disk_headers()
        self._git_deletions = None
        self._git_show_cache.clear()
        self._removed_derived = False
        self._import_count_cache.clear()
        self._derive_all()
        self._reconcile()
        self._loaded = True

    def _load_yaml(self) -> list[CapabilityEntry]:
        if not self._yaml_path.exists():
            raise FileNotFoundError(
                f"capability canonical registry YAML not found: {self._yaml_path}\n"
                f"真源文件应位于 docs/01_policies_and_standards/_registry/catalogs/"
            )
        data = yaml_safe_load(self._yaml_path) or {}
        caps: list[CapabilityEntry] = []
        for raw in data.get("capabilities", []):
            caps.append(CapabilityEntry(
                capability_id=raw["capability_id"],
                aliases=list(raw.get("aliases", []) or []),
                description=raw.get("description", ""),
                canonical_override=(raw.get("canonical_override", "") or "").strip(),
                duplicates_manual=list(raw.get("duplicates_manual", []) or []),
                removed_duplicates_manual=list(raw.get("removed_duplicates_manual", []) or []),
            ))
        return caps

    def _scan_disk_headers(self) -> dict[str, HeaderInfo]:
        """扫描所有 scan_roots/**/*.py 头部，返回 path → HeaderInfo 映射。

        path 用 _base_root 相对路径（与 YAML 中 canonical_file 格式 src/zephyr/xxx
        或 scripts/governance/yyy 对齐）。

        治本（P8 Phase 3）：多根化遍历 self._scan_roots 而非单根 self._scan_root。
        """
        result: dict[str, HeaderInfo] = {}
        for root in self._scan_roots:
            if not root.exists():
                continue
            for py in root.rglob("*.py"):
                try:
                    rel = py.relative_to(self._base_root).as_posix()
                except ValueError:
                    continue
                header = self._parse_header(py, rel)
                # 只收录有 module_id 或 module_path 的文件（有头部声明的）
                if header.module_id or header.module_path:
                    result[rel] = header
        return result

    @staticmethod
    def _parse_header(py: Path, rel: str) -> HeaderInfo:
        """解析单个 .py 文件的头部（薄包装：读文件 → _parse_header_from_text）。"""
        try:
            text = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return HeaderInfo(path=rel)
        return CapabilityLookup._parse_header_from_text(text, rel)

    @staticmethod
    def _parse_header_from_text(text: str, rel: str) -> HeaderInfo:
        """解析文本头部（核心逻辑，供 _parse_header 和 git show 输出共用）。

        与 _parse_header 的区别：输入是已加载的文本字符串，适用于
        - 磁盘文件（_parse_header 读文件后调用本方法）
        - git show {commit}^:{path} 输出（_git_show_header 调用本方法）
        """
        info = HeaderInfo(path=rel)
        lines = text.splitlines()[:HEADER_SCAN_LIMIT]
        in_docstring = False
        docstring_collected: list[str] = []
        docstring_quote: str = ""
        for line in lines:
            stripped = line.rstrip("\n")
            # 头部字段提取
            if m := _RE_MODULE.match(stripped):
                info.module_path = m.group(1).strip()
                continue
            if m := _RE_BLUEPRINT.match(stripped):
                info.blueprint_id = m.group(1).strip()
                continue
            if m := _RE_DOMAIN.match(stripped):
                info.domain = m.group(1).strip()
                continue
            if m := _RE_MATURITY.match(stripped):
                info.maturity = m.group(1).strip()
                continue
            if m := _RE_MODULE_ID.search(stripped):
                info.module_id = m.group(1).strip()
                continue
            # docstring 首行提取（三引号后第一行非空内容）
            if not in_docstring:
                for quote in ('"""', "'''"):
                    if quote in stripped:
                        after = stripped.split(quote, 1)[1]
                        # 单行 docstring（如 """xxx"""）
                        if quote in after:
                            inner = after.split(quote, 1)[0].strip()
                            if inner and not info.docstring:
                                info.docstring = inner
                            break
                        # 多行 docstring 开始
                        in_docstring = True
                        docstring_quote = quote
                        if after.strip():
                            docstring_collected.append(after.strip())
                        break
            else:
                if docstring_quote in stripped:
                    break
                stripped_s = stripped.strip()
                if stripped_s and len(docstring_collected) < 2:
                    docstring_collected.append(stripped_s)
        if docstring_collected and not info.docstring:
            info.docstring = docstring_collected[0]
        return info

    # ---- 派生逻辑：canonical + duplicates ----

    @staticmethod
    def _normalize_token(s: str) -> str:
        """标准化 token：lower + 连字符→下划线。用于 basename↔alias 匹配。"""
        return s.strip().lower().replace("-", "_")

    def _match_set(self, cap: CapabilityEntry) -> set[str]:
        """能力的匹配 token 集合：{capability_id} ∪ aliases（标准化，去空）。"""
        tokens: set[str] = set()
        cid = self._normalize_token(cap.capability_id)
        if cid:
            tokens.add(cid)
        for a in cap.aliases:
            t = self._normalize_token(a)
            if t:
                tokens.add(t)
        return tokens

    def _derive_all(self) -> None:
        """对每个能力派生 canonical / duplicates / removed_duplicates（manual）。

        git 派生 removed_duplicates 不在初始化时执行——改为惰性（_ensure_removed_derived），
        避免初始化时全量 git show 子进程调用导致超时（112 caps × 1305 deletions → 73 次
        git show ≈ 8s+）。
        """
        for cap in self._capabilities:
            self._derive_canonical_and_duplicates(cap)
            cap.removed_duplicates = list(cap.removed_duplicates_manual)

    def _ensure_removed_derived(self) -> None:
        """惰性派生 removed_duplicates：首次查询时触发，仅派生一次。"""
        if self._removed_derived or not self._derive_removed:
            return
        for cap in self._capabilities:
            self._derive_removed_duplicates(cap)
        self._removed_derived = True

    def _derive_canonical_and_duplicates(self, cap: CapabilityEntry) -> None:
        """派生 canonical_file + duplicates（basename 启发式 + 成熟度排序）。"""
        match_tokens = self._match_set(cap)
        # 候选：磁盘上 basename(无 .py) ∈ match_tokens 的文件
        candidates: list[tuple[str, HeaderInfo]] = []
        for path, header in self._disk_headers.items():
            basename = Path(path).stem
            if self._normalize_token(basename) in match_tokens:
                candidates.append((path, header))

        # 优先级 1：canonical_override（人工裁定）
        if cap.canonical_override:
            norm_override = _normalize_path(cap.canonical_override)
            cap.canonical_file = norm_override
            cap.derivation_note = "canonical_override (人工裁定)"
            override_header = self._disk_headers.get(norm_override)
            if override_header:
                self._fill_from_header(cap, override_header)
            cap.duplicates = []
            # ARCH-031 治本（2026-07-01）：canonical 是 __init__.py（包标记）时，
            # 同目录下的 .py 文件是包组件，不是 conflicting duplicates。
            # 病根：aliases 含包内模块 basename 时，auto-derive 把同目录模块
            # 误判为 conflicting（如 code_dedup_trackers 的 6 个 tracker 模块）。
            # 治本：canonical 是 __init__.py 时，排除同目录候选（包组件模式）。
            _pkg_dir = self._package_dir_if_marker(norm_override)
            for path, header in candidates:
                if path == norm_override:
                    continue
                if _pkg_dir and path.startswith(_pkg_dir + "/"):
                    continue  # 包组件，非 duplicate
                cap.duplicates.append(
                    self._make_duplicate_entry(path, header, override_header)
                )
            return

        # 优先级 2/3：无候选 / 单候选 / 多候选排序
        if not candidates:
            cap.canonical_file = ""
            cap.canonical_alive = False
            cap.derivation_note = "no disk candidate matches capability_id/aliases"
            cap.duplicates = []
            return

        sorted_cands = self._rank_candidates(candidates)
        canonical_path, canonical_header = sorted_cands[0]
        cap.canonical_file = canonical_path
        self._fill_from_header(cap, canonical_header)

        if len(candidates) == 1:
            cap.derivation_note = "single candidate (auto canonical)"
        else:
            # 判断 top-2 是否打平（成熟度 + import 数都相同 → 歧义）
            _, second_header = sorted_cands[1]
            tied = (
                self._maturity_rank(canonical_header) == self._maturity_rank(second_header)
                and self._count_importers(canonical_header.module_path)
                    == self._count_importers(second_header.module_path)
            )
            if tied:
                cap.derivation_note = (
                    f"AMBIGUOUS: {len(candidates)} candidates tie on maturity+imports; "
                    f"picked {canonical_path} (first by path). Set canonical_override to force."
                )
            else:
                cap.derivation_note = (
                    f"derived from {len(candidates)} candidates by maturity+imports"
                )

        cap.duplicates = []
        # ARCH-031 治本（2026-07-01）：auto-derived canonical 是 __init__.py 时，
        # 同目录 .py 文件是包组件，排除出 duplicates（同 override 分支逻辑）。
        _pkg_dir = self._package_dir_if_marker(canonical_path)
        for path, header in sorted_cands[1:]:
            if _pkg_dir and path.startswith(_pkg_dir + "/"):
                continue  # 包组件，非 duplicate
            cap.duplicates.append(
                self._make_duplicate_entry(path, header, canonical_header)
            )

    @staticmethod
    def _package_dir_if_marker(canonical_path: str) -> str | None:
        """canonical 是 __init__.py（包标记）时返回其目录，否则 None。

        ARCH-031 治本（2026-07-01）：包标记 canonical 的同目录 .py 文件是
        包组件，不是 conflicting duplicates。返回目录路径供调用方做前缀排除。
        """
        if canonical_path.endswith("/__init__.py"):
            return canonical_path.rsplit("/", 1)[0]
        return None

    def _rank_candidates(
        self, candidates: list[tuple[str, HeaderInfo]]
    ) -> list[tuple[str, HeaderInfo]]:
        """排序候选：成熟度降序 → import 数降序 → 路径字典序（稳定 tiebreak）。"""
        def sort_key(ch: tuple[str, HeaderInfo]):
            _path, header = ch
            return (
                -self._maturity_rank(header),
                -self._count_importers(header.module_path),
                ch[0],
            )
        return sorted(candidates, key=sort_key)

    @staticmethod
    def _maturity_rank(header: HeaderInfo) -> int:
        return _MATURITY_RANK.get(header.maturity, 0)

    @staticmethod
    def _fill_from_header(cap: CapabilityEntry, header: HeaderInfo) -> None:
        """从 canonical 文件的 HeaderInfo 填充 cap 的派生字段。"""
        cap.module_id = header.module_id
        cap.blueprint_id = header.blueprint_id
        cap.domain = header.domain
        cap.maturity = header.maturity

    def _make_duplicate_entry(
        self, path: str, header: HeaderInfo, canonical_header: HeaderInfo | None
    ) -> dict:
        """构造 duplicate 条目。relation 由 blueprint 比对派生。"""
        relation = "unknown"
        if canonical_header and header.blueprint_id and canonical_header.blueprint_id:
            relation = (
                "conflicting"
                if header.blueprint_id == canonical_header.blueprint_id
                else "sibling"
            )
        return {
            "path": path,
            "module_id": header.module_id,
            "module_path": header.module_path,
            "blueprint_id": header.blueprint_id,
            "domain": header.domain,
            "maturity": header.maturity,
            "relation": relation,
            "note": "auto-derived from disk scan (basename match)",
            "docstring": header.docstring,
        }

    def _count_importers(self, module_path: str) -> int:
        """统计 import 该 module_path 的文件数（tiebreaker，惰性缓存）。

        仅在 canonical 多候选成熟度打平时调用（rare），故扫全项目文件可接受。
        匹配规则：文件含 `from {module_path}` 或 `import {module_path}`。
        """
        if not module_path:
            return 0
        if module_path in self._import_count_cache:
            return self._import_count_cache[module_path]
        needle_from = f"from {module_path}"
        needle_import = f"import {module_path}"
        count = 0
        for path in self._disk_headers:
            abs_path = self._base_root / path
            try:
                                # 5.59.3 修复：原 errors="ignore" 静默丢弃非法字节，行数统计和 import 计数失真。
                # 改为 errors="replace" 用替换字符标记非法字节，至少保留行结构。
                text = abs_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if needle_from in text or needle_import in text:
                count += 1
        self._import_count_cache[module_path] = count
        return count

    # ---- 派生逻辑：removed_duplicates（git log） ----

    def _load_git_deletions(self) -> list[tuple[str, str]]:
        """扫描 git 历史，返回 [(path, commit_hash), ...] 删除记录（src/zephyr/ 下）。

        单次 subprocess，结果缓存到 self._git_deletions。
        git 不可用 / 非 git 仓库 → 返回空列表（降级，不阻断查询）。
        """
        if self._git_deletions is not None:
            return self._git_deletions
        deletions: list[tuple[str, str]] = []
        try:
            result = subprocess.run(
                [
                    "git", "log", "--diff-filter=D", "--name-only",
                    "--format=%H", "--", "src/zephyr/",
                ],
                cwd=str(self._base_root),
                capture_output=True,
                text=True,
                timeout=30,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode == 0:
                current_commit = ""
                for line in result.stdout.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    if _RE_GIT_HASH.match(line):
                        current_commit = line
                    elif (
                        line.startswith("src/zephyr/")
                        and line.endswith(".py")
                        and current_commit
                    ):
                        deletions.append((line, current_commit))
        except (subprocess.SubprocessError, OSError):
            # git 不可用或超时 → 降级为空（不阻断查询）
            pass
        self._git_deletions = deletions
        return deletions

    def _derive_removed_duplicates(self, cap: CapabilityEntry) -> None:
        """从 git 历史派生 removed_duplicates（basename 匹配 + 头部验证）。

        派生规则：
          1. 遍历 git log 中 src/zephyr/ 下被删的 .py 文件
          2. basename 匹配 capability_id 或 aliases
          3. git show {commit}^:{path} 读取已删文件，验证头部 module_id/module_path 匹配
             （避免 basename 巧合误报，如无关的 handoff.py 配置文件）
          4. 排除 canonical / duplicates / removed_duplicates_manual 已声明的路径
          5. 追加到 _derive_all 已合并的 manual 条目之后

        注：manual 条目合并由 _derive_all 无条件执行（不依赖 derive_removed），
        本方法只负责 git 派生部分。
        """
        match_tokens = self._match_set(cap)
        deletions = self._load_git_deletions()

        # git 派生（追加到 _derive_all 已合并的 manual 条目之后）
        declared = {cap.canonical_file}
        declared.update(d.get("path", "") for d in cap.duplicates)
        declared.update(d.get("path", "") for d in cap.removed_duplicates_manual)

        for path, commit in deletions:
            if path in declared:
                continue
            basename = Path(path).stem
            if self._normalize_token(basename) not in match_tokens:
                continue
            # 头部验证：从 commit 父节点读取已删文件内容
            header = self._git_show_header(commit, path)
            if header is None:
                # 无法读取（二进制/编码错/路径含特殊字符），保守跳过
                continue
            if not self._header_matches_capability(header, match_tokens):
                continue
            cap.removed_duplicates.append({
                "path": path,
                "removed_in_commit": commit,
                "module_id": header.module_id,
                "module_path": header.module_path,
                "note": "git-derived (auto from git log --diff-filter=D)",
            })

    def _git_show_header(self, commit: str, path: str) -> HeaderInfo | None:
        """git show {commit}^:{path} 读取已删文件，解析头部。失败返回 None。

        带缓存：同一 (commit,path) 仅 subprocess 一次，避免多能力匹配同一删除文件时重复调用。
        """
        cache_key = f"{commit}:{path}"
        if cache_key in self._git_show_cache:
            return self._git_show_cache[cache_key]
        try:
            result = subprocess.run(
                ["git", "show", f"{commit}^:{path}"],
                cwd=str(self._base_root),
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode != 0:
                self._git_show_cache[cache_key] = None
                return None
            header = self._parse_header_from_text(result.stdout, path)
            self._git_show_cache[cache_key] = header
            return header
        except (subprocess.SubprocessError, OSError):
            self._git_show_cache[cache_key] = None
            return None

    @staticmethod
    def _header_matches_capability(header: HeaderInfo, match_tokens: set[str]) -> bool:
        """验证文件头部是否与能力匹配（module_id / module_path 含匹配 token）。

        用于 removed_duplicates 派生时避免 basename 巧合误报。
        """
        if header.module_id:
            norm_id = CapabilityLookup._normalize_token(header.module_id)
            for tok in match_tokens:
                if tok and tok in norm_id:
                    return True
        if header.module_path:
            for seg in header.module_path.split("."):
                if CapabilityLookup._normalize_token(seg) in match_tokens:
                    return True
        return False

    # ---- reconcile ----

    def _reconcile(self) -> None:
        """合并派生结果与磁盘扫描：标记 canonical_alive + 合并 manual + 发现 pending。"""
        for cap in self._capabilities:
            # 1. canonical 文件是否存在于磁盘
            cap.canonical_alive = (
                cap.canonical_file in self._disk_headers
                or (bool(cap.canonical_file) and (self._base_root / cap.canonical_file).exists())
            )
            cap.status = "alive" if cap.canonical_alive else "dead"

            # 2. 合并 duplicates_manual（语义 sibling，auto 按 basename 匹配会漏掉）
            existing_dup_paths = {d.get("path", "") for d in cap.duplicates}
            for manual in cap.duplicates_manual:
                if manual.get("path", "") not in existing_dup_paths:
                    cap.duplicates.append(manual)

            # 3. pending candidates：磁盘上有文件声明了与 canonical 相同的
            #    module_id 或 module_path，但不在派生 canonical/duplicates/removed 里
            #    ——确凿的重复信号，需人工裁定。
            #    注意：不使用 aliases 子串匹配（太宽泛，会命中大量无关文件产生噪音）。
            #    aliases 仅用于 find() 查询和 basename 派生，不用于磁盘 candidate 发现。
            disk = self._disk_headers.get(cap.canonical_file)
            canonical_module_id = (disk.module_id if disk else "") or cap.module_id
            canonical_module_path = disk.module_path if disk else ""
            declared_paths = {cap.canonical_file}
            declared_paths.update(d.get("path", "") for d in cap.duplicates)
            declared_paths.update(d.get("path", "") for d in cap.removed_duplicates)
            for path, header in self._disk_headers.items():
                if path in declared_paths:
                    continue
                is_candidate = False
                match_reason = ""
                # 信号 1：module_id 与 canonical 相同（同 module_id 多文件 = 重复实现）
                if canonical_module_id and header.module_id == canonical_module_id:
                    is_candidate = True
                    match_reason = f"same module_id={header.module_id}"
                # 信号 2：module_path 与 canonical 相同
                #   （如两文件 [MODULE] 都声称 zephyr.xxx.rollback_executor——头部错声明或真重复）
                if canonical_module_path and header.module_path == canonical_module_path:
                    is_candidate = True
                    match_reason = (match_reason + "; " if match_reason else "") + \
                                   f"same module_path={header.module_path}"
                if is_candidate:
                    cap.pending_candidates.append({
                        "path": path,
                        "module_id": header.module_id,
                        "module_path": header.module_path,
                        "blueprint_id": header.blueprint_id,
                        "domain": header.domain,
                        "maturity": header.maturity,
                        "docstring": header.docstring,
                        "match_reason": match_reason,
                        "note": "磁盘有但派生结果未收录——确凿重复信号（同 module_id 或同 module_path），需人工裁定",
                    })

    # ---- 查询 API ----

    def find(self, query: str) -> list[dict]:
        """关键词搜索：匹配 capability_id / description / canonical_file / module_id / aliases（大小写不敏感）。

        匹配策略（治本：token 包含匹配，消除中文变体 alias 堆砌反模式）：
          0. 退化查询守卫：len(query.strip()) < 2 → 直接返回 []（空/空白/单字符
             是噪声输入，旧版 find('a')/find('的') 因 '' in haystack 恒真或单字符
             作为子串出现在所有 description 而命中全部——守卫拦截）
          1. 精确子串匹配（保留原行为，大小写不敏感）——处理 alias 原样命中
          2. token 包含匹配（精确子串未命中时启用）：
             - ASCII 词 token：全部必须在 haystack 中（AND，如 "repo root" → repo + root）
             - CJK 字符：query 的 CJK 字符序列与 haystack 须有 ≥_CJK_MIN_SUBSTRING 字符公共子串
               （捕获语义 core，如 "仓库根路径" 经 "仓库根" 命中 "仓库根目录"；
               避免"目录"单字 OR 误命中所有含"目"/"录"条目——公共子串要求连续）
             - 守卫：ASCII 词数 + CJK 字符数 ≥2，避免单 token 过宽匹配
           设计权衡（勿误判为 bug）：短词（如 ttl）会命中多个 ttl_* 能力——token 包含匹配的合理代价。精确查用 reg.get(capability_id)，宽搜用更长关键词（如 ttl_validation 而非 ttl）。
        """
        q = query.lower()
        if len(q.strip()) < 2:
            return []  # 退化查询守卫：空/空白/单字符不返回宽泛命中
        results: list[dict] = []
        ascii_tokens, cjk_str = self._tokenize(query)
        for cap in self._capabilities:
            haystacks = [
                cap.capability_id, cap.description,
                cap.canonical_file, cap.module_id,
            ] + list(cap.aliases)
            haystack = " ".join(haystacks).lower()
            if q in haystack:
                results.append(self._entry_to_dict(cap))
            elif self._token_match(ascii_tokens, cjk_str, haystack):
                results.append(self._entry_to_dict(cap))
        return results

    @staticmethod
    def _tokenize(text: str) -> tuple[list[str], str]:
        """分词：返回 (ascii_tokens, cjk_str)。

        - ASCII 词块：按非单词字符切分，整体小写（"REPO_ROOT" → ["repo_root"]，
          "repo root" → ["repo","root"]）
        - CJK 字符：合并为单一字符串（"仓库根路径" → "仓库根路径"），
          交由 _token_match 做 ≥_CJK_MIN_SUBSTRING 字符公共子串匹配
        """
        ascii_tokens: list[str] = []
        cjk_chars: list[str] = []
        for chunk in re.split(r"\W+", text, flags=re.UNICODE):
            if not chunk:
                continue
            cur_ascii: list[str] = []
            for ch in chunk:
                if ch.isascii():
                    cur_ascii.append(ch.lower())
                else:
                    if cur_ascii:
                        ascii_tokens.append("".join(cur_ascii))
                        cur_ascii = []
                    cjk_chars.append(ch)
            if cur_ascii:
                ascii_tokens.append("".join(cur_ascii))
        return ascii_tokens, "".join(cjk_chars)

    @staticmethod
    def _token_match(ascii_tokens: list[str], cjk_str: str, haystack: str) -> bool:
        """token 包含匹配：ASCII 词全在 + CJK ≥_CJK_MIN_SUBSTRING 字符公共子串。

        守卫：ASCII 词数 + CJK 字符数 < 2 → 直接返回 False（避免单 token 过宽）。
        CJK 阈值见 _CJK_MIN_SUBSTRING 常量（治本：阈值真源唯一，改常量全跟随）。
        短于阈值的 cjk_str：要求整体在 haystack 中（精确子串兜底，2 字符查询由 find()
        第一分支精确子串覆盖，此处仅"短 CJK + ASCII 词"混合查询时起作用）。
        """
        total = len(ascii_tokens) + len(cjk_str)
        if total < 2:
            return False
        # ASCII 词 token：AND
        for tok in ascii_tokens:
            if tok not in haystack:
                return False
        # CJK：≥_CJK_MIN_SUBSTRING 字符走滑动窗口；短于阈值要求整体在 haystack 中
        if cjk_str:
            if len(cjk_str) >= _CJK_MIN_SUBSTRING:
                if not any(cjk_str[i:i + _CJK_MIN_SUBSTRING] in haystack
                           for i in range(len(cjk_str) - _CJK_MIN_SUBSTRING + 1)):
                    return False
            elif cjk_str not in haystack:
                return False
        return True

    def get(self, capability_id: str) -> dict | None:
        """按 capability_id 精确查询。"""
        for cap in self._capabilities:
            if cap.capability_id == capability_id:
                return self._entry_to_dict(cap)
        return None

    def list_duplicates(self) -> list[dict]:
        """列出所有有 duplicates[] 的能力。"""
        return [
            self._entry_to_dict(cap)
            for cap in self._capabilities
            if cap.duplicates
        ]

    def list_ssot_conflicts(self) -> list[dict]:
        """列出 relation=conflicting 的 SSoT 冲突（同蓝图多实现）。"""
        results: list[dict] = []
        for cap in self._capabilities:
            conflicts = [
                d for d in cap.duplicates
                if d.get("relation") == "conflicting"
            ]
            if conflicts:
                results.append({
                    "capability_id": cap.capability_id,
                    "canonical_file": cap.canonical_file,
                    "blueprint_id": cap.blueprint_id,
                    "conflicts": conflicts,
                })
        return results

    def check_file_canonical(self, file_path: str) -> dict | None:
        """反查：某文件是哪个能力的 canonical 或已知 duplicate。

        供未来 create-time 门禁调用：新建/修改文件前查询本方法，若返回 is_canonical=False
        且 relation=conflicting，门禁应阻断并要求 Owner 裁定。
        """
        if not file_path or not isinstance(file_path, str):
            return None
        norm = _normalize_path(file_path)
        for cap in self._capabilities:
            if cap.canonical_file == norm:
                return {
                    "capability_id": cap.capability_id,
                    "canonical_file": cap.canonical_file,
                    "is_canonical": True,
                    "status": cap.status,
                }
            for d in cap.duplicates:
                if d.get("path") == norm:
                    return {
                        "capability_id": cap.capability_id,
                        "canonical_file": cap.canonical_file,
                        "is_canonical": False,
                        "relation": d.get("relation", "unknown"),
                        "note": d.get("note", ""),
                    }
        return None

    def find_files_by_module_path(self, module_path: str) -> list[str]:
        """反查：磁盘上哪些文件声明了指定的 module_path。

        SSoT 创建门禁的核心反查方法（方案 E：零新真源，复用 [MODULE] 头）。
        纯磁盘扫描——扫描 src/zephyr/**/*.py 的 [MODULE] 头部字段，
        返回所有声明了相同 module_path 的文件相对路径列表。

        真源是文件头部 [MODULE] 字段（已存在，零新真源，零同步）。
        不依赖 YAML registry——YAML 是人工裁定的能力索引，不是门禁的必需依赖。

        参数:
            module_path: 预期的 module path（如 "zephyr.shared.session_continuity"）

        返回:
            声明了该 module_path 的文件相对路径列表（如 ["src/zephyr/shared/session_continuity.py"]）
            空列表表示无冲突——门禁应 ALLOW。

        供 scaffold._check_duplicate_functionality 维度3 调用：
            新文件预期 module_path = zephyr.{package}.{name}
            命中已有文件 → BLOCK（ScaffoldError，重定向去 extend）
            未命中      → ALLOW
        """
        if not module_path:
            return []
        target = module_path.strip()
        if not target:
            return []
        matches: list[str] = []
        for path, header in self._disk_headers.items():
            if header.module_path == target:
                matches.append(path)
        return matches

    def check_ssot_conflicts(
        self, new_py_files: list[tuple[str, str]]
    ) -> list[SSoTConflict]:
        """检测新增 .py 文件的 module_path 冲突（L2/L3 共享检测逻辑唯一真源）。

        方案 E 治本重构：L2（GitCommitGateway._check_ssot_canonical）和
        L3（check_ssot_gate.py pre-commit hook）的检测逻辑收拢到本方法，
        避免两处重复实现导致的同步成本和漂移风险。

        调用方职责（各自差异部分，不在本方法内）：
          - L2: 从 commit files 筛选 src/zephyr/ + .py + 未跟踪（_is_git_tracked）
          - L3: 从 git diff --diff-filter=A 获取 staged 新增 src/zephyr/*.py
          - 两者都负责 import/初始化 CapabilityLookup 的 fail-open 降级

        本方法职责（唯一真源）：
          1. 解析每个新文件的 [MODULE] 头
          2. find_files_by_module_path 反查
          3. 排除新文件自己
          4. 返回冲突列表

        参数:
            new_py_files: [(abs_path, rel_path), ...] 新增 .py 文件列表
                          abs_path 用于读取文件头，rel_path 用于匹配 _disk_headers key
                          （调用方保证已筛选 src/zephyr/ + .py）

        返回:
            冲突列表——空列表表示无冲突（门禁应 ALLOW）。
            非空列表的每一项含 rel_path/module_path/conflicts（已排除自己）。

        已知限制（方案 E 固有边界，非缺陷）:
            1. 同批次互冲漏检：本方法只反查磁盘已有文件（find_files_by_module_path），
               不检查 new_py_files 列表内部互冲。若 AI 绕过 scaffold 批量 commit 两份
               声明相同新 module_path 的文件，两者都查不到已有冲突 → 漏检。
               缓解：L1 scaffold 单文件创建不会触发此问题（scaffold 逐个创建+检查）。
            2. module_path 大小写敏感：find_files_by_module_path 精确匹配，AI 声明
               Zephyr.Governance.X（大写）与已有 zephyr.governance.x（小写）不匹配 → 漏检。
               缓解：写错 module_path 等于文件 import 不到，功能上等于不存在。
            修改门禁前 MUST 读此段落，避免误判为 bug 或重新创造已有限制。
        """
        if not new_py_files:
            return []
        violations: list[SSoTConflict] = []
        for abs_path, rel_path in new_py_files:
            header = self._parse_header(Path(abs_path), rel_path)
            if not header.module_path:
                continue  # 无 [MODULE] 头，跳过（无法判断）
            matched = self.find_files_by_module_path(header.module_path)
            # 排除新文件自己（rel_path 用正斜杠，与 _disk_headers key 一致）
            matched = [c for c in matched if c != rel_path]
            if matched:
                violations.append(SSoTConflict(
                    rel_path=rel_path,
                    module_path=header.module_path,
                    conflicts=matched,
                ))
        return violations

    def check_capability_duplicates(
        self, new_py_files: list[tuple[str, str]]
    ) -> list[CapabilityDuplicate]:
        """检测新增 .py 文件是否参与"同能力多实现"（basename 碰撞 → 阻断）。

        与 check_ssot_conflicts 的分工（治本：检测逻辑唯一真源收拢到本方法，L2/L3 共用）：
          - check_ssot_conflicts：同 module_path 硬碰撞（[MODULE] 头字段精确匹配）。
          - 本方法：basename 撞上 capability_id/alias（registry 派生已标为 duplicate）。

        治本（2a/2c）：复用 registry 构造时已派生的 duplicates 状态——
          check_file_canonical 查 _derive_canonical_and_duplicates 的派生结果，
          不重新实现 basename 匹配逻辑（派生是唯一真源，重算=第二份实现=漂移源）。

        决策矩阵（B 方案：所有信号皆阻断，无 advisory）：
          info = check_file_canonical(rel_path) 反查已派生状态：
          - info is None（basename 不撞任何 cap）→ 追加未注册 basename 碰撞检测
            （ARCH-031 治本：_check_unregistered_basename_collision 收窄 governance/ 前缀）
          - info.is_canonical=True + cap.duplicates 非空 → 阻断（canonical_displaced_*）
          - info.is_canonical=True + cap.duplicates 空 → 无信号（合法首实现）
          - info.is_canonical=False → 阻断（duplicate，relation=conflicting/sibling/unknown）

        设计裁定（B 方案，去掉软层 advisory 的理由）：
          软层原用 find(module_path 末段) 做语义召回，但 Python 标识符下划线是
          word char（handoff_v2 不可分割），find() 的 token-AND 匹配捕获不到硬层
          漏掉的场景 → 软层 TP≈0。且 advisory 不阻断=无人行动=死数据。
          commit 门禁只负责高置信阻断，低置信检测由 §9.0 手动查重兜底。

        参数:
            new_py_files: [(abs_path, rel_path), ...] 新增 .py 文件列表
                          （调用方保证已筛选 src/zephyr/ + .py；rel_path 正斜杠，
                           与 _disk_headers key / canonical_file 格式一致）

        返回:
          CapabilityDuplicate 列表——空列表表示无信号（门禁应 ALLOW）；
          非空列表表示阻断信号（门禁应 BLOCK）。

        已知限制（方案固有边界，非缺陷，修改门禁前 MUST 读此段落）:
          1. 无 [MODULE]/[A_module] 头的新文件不被 _scan_disk_headers 收录
             → check_file_canonical 返回 None → 漏检（与 check_ssot_conflicts
             同边界，header 完整性由其他门禁负责）。
          2. "全新 basename + 全新 module_path 实现已有能力"不可约漏报，
             由 check_ssot_conflicts（同 module_path）+ AGENTS.md §9.0 查重习惯
             + reconciler 周期审计三层兜底。
        """
        if not new_py_files:
            return []
        results: list[CapabilityDuplicate] = []
        for _abs_path, rel_path in new_py_files:
            # 复用已派生状态：check_file_canonical 查 _derive 后的 duplicates
            info = self.check_file_canonical(rel_path)
            own_cap_id = info["capability_id"] if info else ""
            canonical_file = info.get("canonical_file", "") if info else ""
            relation = "none"
            detail = ""

            if info is None:
                # ARCH-031 门禁盲区治本（2026-07-01）：basename 不撞已注册 capability 时，
                # 追加磁盘 basename 碰撞检测（根vs子目录同名文件）。
                # 病根：原直接 continue → 新 AI 可在 governance/ 根目录重建子目录同名文件，
                # basename 不撞 capability 但构成磁盘碰撞，三层门禁无一层检测。
                collision = self._check_unregistered_basename_collision(rel_path)
                if collision:
                    results.append(collision)
                continue
            elif info.get("is_canonical"):
                # 新文件被派生为 canonical
                cap = self.get(own_cap_id)
                dups = cap.get("duplicates", []) if cap else []
                if not dups:
                    continue  # 合法首实现 → 无信号
                # 新 canonical 挤占已有同 basename 文件（多实现）
                relations = {d.get("relation", "unknown") for d in dups}
                if "conflicting" in relations:
                    relation = "canonical_displaced_conflicting"
                else:
                    relation = "canonical_displaced_sibling"
                detail = (
                    f"新文件成为 {own_cap_id} 的 canonical，但已有 "
                    f"{len(dups)} 个同 basename 文件降为 duplicate"
                    f"（relation={sorted(relations)}）——多实现违反 SSoT"
                )
            else:
                # 新文件被派生为 duplicate → 阻断
                relation = info.get("relation", "unknown")
                detail = (
                    f"新文件是 {own_cap_id} 的 {relation} duplicate"
                    f"（canonical={canonical_file}）——违反 SSoT"
                )

            results.append(CapabilityDuplicate(
                rel_path=rel_path,
                capability_id=own_cap_id,
                canonical_file=canonical_file,
                relation=relation,
                detail=detail,
            ))
        return results

    def _check_unregistered_basename_collision(
        self, rel_path: str
    ) -> CapabilityDuplicate | None:
        """检测未注册 capability 的新文件是否与已有文件构成 basename 碰撞。

        ARCH-031 门禁缺口治本（2026-07-01）：
          病根——check_capability_duplicates 原只检测 basename 撞已注册 capability，
          若新文件 basename 不撞任何 capability（info is None），直接跳过。
          但新 AI 可在 governance/ 根目录重建子目录同名文件（如 audit/foo.py 存在时
          新建 governance/foo.py），basename 不撞 capability 但构成磁盘碰撞，
          三层门禁无一层检测——门禁盲区。

          治本——在 info is None 分支追加磁盘 basename 碰撞检测：
            - 收窄到 src/zephyr/governance/ 前缀（ARCH-031 原始场景）
            - 排除 _archive/ 路径（归档副本非真源）
            - 只检测"根vs子目录"碰撞模式（同层平级不阻断，子目录化才阻断）

        已知限制：
          仅检测 _disk_headers 中收录的文件（有 [MODULE]/[A_module] 头的文件）。
          已有文件无头部时不在 _disk_headers 中 → 漏检（与 check_file_canonical
          同边界，header 完整性由其他门禁负责）。
        """
        _GOV_PREFIX = "src/zephyr/governance/"
        if not rel_path.startswith(_GOV_PREFIX):
            return None
        if "/_archive/" in rel_path:
            return None

        basename = rel_path.rsplit("/", 1)[-1]

        collisions: list[str] = []
        for existing_path in self._disk_headers:
            if existing_path == rel_path:
                continue  # 排除自己
            if not existing_path.startswith(_GOV_PREFIX):
                continue
            if "/_archive/" in existing_path:
                continue
            existing_basename = existing_path.rsplit("/", 1)[-1]
            if existing_basename != basename:
                continue
            if self._is_root_vs_subdir_collision(rel_path, existing_path):
                collisions.append(existing_path)

        if not collisions:
            return None

        return CapabilityDuplicate(
            rel_path=rel_path,
            capability_id="",  # 未注册 capability
            canonical_file=collisions[0],
            relation="unregistered_basename_collision",
            detail=(
                f"新文件与已有文件 basename 碰撞（ARCH-031 门禁盲区治本）: "
                f"{rel_path} 与 {', '.join(collisions)} 同名，"
                f"构成根vs子目录碰撞——违反 ARCH-031 命名约定"
                f"（属于子模块的文件必须放在子目录，根目录仅放跨模块桥接文件）。"
                f"修复：将新文件放入对应子目录，或扩展现有文件后删除新文件。"
            ),
        )

    @staticmethod
    def _is_root_vs_subdir_collision(rel_a: str, rel_b: str) -> bool:
        """判断同 basename 文件是否构成"同域包根 vs 子目录"碰撞。

        ARCH-031 场景：一方在域根（如 src/zephyr/governance/foo.py），
        另一方在子目录（如 src/zephyr/governance/audit/foo.py）。

        判定逻辑：
          - 共同前缀至少 3 级（src/zephyr/governance）
          - 一方 depth = common_depth + 1（直接在域根下，即根文件）
          - 另一方 depth > common_depth + 1（在子目录下，即子目录文件）
          - 一根一子目录 → 碰撞；同层（都根或都子目录）→ 不碰撞
        """
        parts_a = rel_a.split("/")
        parts_b = rel_b.split("/")
        common = 0
        for i in range(min(len(parts_a), len(parts_b))):
            if parts_a[i] == parts_b[i]:
                common += 1
            else:
                break
        # 共同前缀至少 3 级（src/zephyr/governance）
        if common < 3:
            return False
        depth_a = len(parts_a)
        depth_b = len(parts_b)
        root_a = (depth_a == common + 1)
        root_b = (depth_b == common + 1)
        return root_a != root_b

    def check_module_id_conflicts(
        self, new_py_files: list[tuple[str, str]]
    ) -> list[ModuleIdConflict]:
        """检测新增 .py 文件的 module_id 全局冲突（P0-2 防再生门禁）。

        同一个 module_id 出现在多个文件 = 跨域复刻后忘记改 ID。
        与 check_ssot_conflicts（同 module_path 硬碰撞）互补：
          - module_path 是 Python 导入路径（物理位置），同 module_path = 同一文件重复
          - module_id 是逻辑标识（[A_module] module_id=MOD-XXX），同 module_id = 逻辑重复
        两者维度不同，需分别检测。

        治本（向内收）：检测逻辑唯一真源收拢到本方法，L2/L3 共用。
        """
        if not new_py_files:
            return []
        violations: list[ModuleIdConflict] = []
        for abs_path, rel_path in new_py_files:
            header = self._parse_header(Path(abs_path), rel_path)
            if not header.module_id:
                continue
            matched = [
                p for p, h in self._disk_headers.items()
                if h.module_id == header.module_id and p != rel_path
            ]
            if matched:
                violations.append(ModuleIdConflict(
                    rel_path=rel_path,
                    module_id=header.module_id,
                    conflicts=sorted(matched),
                ))
        return violations

    def check_module_domain_consistency(
        self, new_py_files: list[tuple[str, str]]
    ) -> list[DomainMismatch]:
        """检测新增 .py 文件的 MODULE 声明域与物理路径域一致性（P0-3 防再生门禁）。

        文件物理在 src/zephyr/{domain_A}/ 但 [MODULE] 声明 zephyr.{domain_B}.xxx
        = 跨域复刻后忘记改 module_path（病根1 典型症状）。
        Python 导入路径必须与物理目录一致（否则 import 不到），声明不符 = 谎报归属。

        治本（向内收）：检测逻辑唯一真源收拢到本方法，L2/L3 共用。
        """
        if not new_py_files:
            return []
        violations: list[DomainMismatch] = []
        for abs_path, rel_path in new_py_files:
            header = self._parse_header(Path(abs_path), rel_path)
            if not header.module_path:
                continue
            mp_parts = header.module_path.split(".")
            if len(mp_parts) < 2:
                continue
            declared_domain = mp_parts[1]
            path_parts = rel_path.split("/")
            if len(path_parts) < 4:
                continue  # 直接在 src/zephyr/ 下的文件（如 __init__.py），无域段
            physical_domain = path_parts[2]
            if declared_domain != physical_domain:
                violations.append(DomainMismatch(
                    rel_path=rel_path,
                    module_path=header.module_path,
                    declared_domain=declared_domain,
                    physical_domain=physical_domain,
                ))
        return violations

    def list_all(self) -> list[dict]:
        return [self._entry_to_dict(cap) for cap in self._capabilities]

    def summary(self) -> dict:
        """返回注册表健康汇总。"""
        return {
            "total_declared": len(self._capabilities),
            "alive": sum(1 for c in self._capabilities if c.canonical_alive),
            "dead": sum(1 for c in self._capabilities if not c.canonical_alive),
            "with_duplicates": sum(1 for c in self._capabilities if c.duplicates),
            "ssot_conflicts": len(self.list_ssot_conflicts()),
            "pending_candidates": sum(len(c.pending_candidates) for c in self._capabilities),
            "yaml_path": str(self._yaml_path),
            "scan_roots": [str(r) for r in self._scan_roots],
        }

    def _entry_to_dict(self, cap: CapabilityEntry) -> dict:
        """转为 dict 前触发 removed_duplicates 惰性派生（首次查询时 git log + git show）。"""
        self._ensure_removed_derived()
        return {
            "capability_id": cap.capability_id,
            "name": cap.capability_id,  # name 已弃用，输出 capability_id 保持向后兼容
            "canonical_file": cap.canonical_file,
            "module_id": cap.module_id,
            "blueprint_id": cap.blueprint_id,
            "domain": cap.domain,
            "maturity": cap.maturity,
            "status": cap.status,
            "canonical_alive": cap.canonical_alive,
            "aliases": list(cap.aliases),
            "description": cap.description,
            "duplicates": list(cap.duplicates),
            "removed_duplicates": list(cap.removed_duplicates),
            "pending_candidates": list(cap.pending_candidates),
            "derivation_note": cap.derivation_note,
        }


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _normalize_path(p: str) -> str:
    """路径标准化：反斜杠→正斜杠，去掉前导 ./ （正确剥离前缀，非字符集）"""
    p = p.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def yaml_safe_load(path: Path) -> dict:
    """延迟 import yaml，避免 zephyr.governance.__init__ 加载顺序问题。"""
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.governance.capability_lookup",
        description="capability → canonical_file 反查注册表查询",
    )
    parser.add_argument("--find", metavar="QUERY", help="关键词搜索能力")
    parser.add_argument("--get", metavar="CAP_ID", help="按 capability_id 精确查询")
    parser.add_argument("--list-duplicates", action="store_true", help="列出有重复的能力")
    parser.add_argument("--list-conflicts", action="store_true", help="列出 SSoT 冲突（同蓝图多实现）")
    parser.add_argument("--check-file", metavar="PATH", help="反查某文件是哪个能力的 canonical")
    parser.add_argument("--summary", action="store_true", help="打印注册表汇总")
    parser.add_argument("--no-scan", action="store_true", help="跳过磁盘扫描（只读 YAML，快）")
    parser.add_argument(
        "--no-derive-removed",
        action="store_true",
        help="跳过 git log 派生 removed_duplicates（pre-commit 等高频场景加速）",
    )
    args = parser.parse_args(argv)

    try:
        reg = CapabilityLookup(
            scan=not args.no_scan,
            derive_removed=not args.no_derive_removed,
        )
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.find:
        _print_json(reg.find(args.find))
    elif args.get:
        r = reg.get(args.get)
        if r is None:
            print(f"NOT FOUND: {args.get}", file=sys.stderr)
            return 1
        _print_json(r)
    elif args.list_duplicates:
        _print_json(reg.list_duplicates())
    elif args.list_conflicts:
        _print_json(reg.list_ssot_conflicts())
    elif args.check_file:
        r = reg.check_file_canonical(args.check_file)
        if r is None:
            print(f"NOT IN REGISTRY: {args.check_file}", file=sys.stderr)
            return 1
        _print_json(r)
    elif args.summary:
        _print_json(reg.summary())
    else:
        parser.print_help()
        print("\n--- summary ---")
        _print_json(reg.summary())
    return 0


def _print_json(obj: object) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
