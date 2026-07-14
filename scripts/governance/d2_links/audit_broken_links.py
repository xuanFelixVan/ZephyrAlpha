# [BLUEPRINT] MOD-INF-005 | scripts/governance/d2_links/audit_broken_links.py | §
# [MODULE] scripts.governance.d2_links.audit_broken_links
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d2_links.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""检测文档/数据文件中的断链与幽灵引用。

治本背景（2026-06-29）：
    调研发现 AI 在 .md/.csv/.yaml 中编造虚假文件引用（如 dom_gov_001 虚假审计闭环：
    index.md 列 22 张不存在的任务卡，move_plan.csv 引用 4 个不存在的文件）。
    现有 audit_broken_links.py 仅检测 .md 的 markdown 链接语法，漏检：
      - .csv/.yaml/.json 中的纯文本路径引用
      - frontmatter 中的 blueprint_id 引用
      - 跨目录的虚假文件引用闭环
    本扩展治本：从仅 .md markdown 链接扩展到多文件类型 + 多引用语法。

五防护缺口治本进展：
    GAP-1: 非.md文件路径引用（.csv/.yaml/.json）—— 已治本（v1）
    GAP-2: frontmatter.blueprint_id 存在性        —— 已治本（v2，本次扩展）
    GAP-3: index.md 文件清单完整性（严格本地解析）  —— 已治本（v2，本次扩展）
    GAP-4: audit_report 审计对象存在性            —— 已治本（v2，本次扩展）
    GAP-5: 跨目录引用闭环（_working/ 归档）      —— 已治本（reconciler）

支持模式：
    python audit_broken_links.py <文件>          # 检测单个文件
    python audit_broken_links.py <目录>          # 递归检测目录
    python audit_broken_links.py <文件> --ci      # 硬阻断模式（exit 1）
    python audit_broken_links.py <文件> --warn-only  # 只警告（exit 0）

检测的引用类型：
    1. Markdown 链接 [text](target)        —— .md 文件
    2. 纯文本文件路径（含 / + 扩展名）      —— .md/.csv/.yaml/.yml/.json
    3. CSV 列值中的文件路径               —— .csv 文件
    4. YAML 值中的文件路径               —— .yaml/.yml 文件
    5. frontmatter.blueprint_id 存在性     —— .md 文件（GAP-2）
    6. index.md 文件清单严格本地解析       —— index.md（GAP-3，禁 basename 兜底）
    7. audit_report 审计对象存在性         —— doc_type=audit_report（GAP-4）

跳过的引用：
    - http://, https://, ftp://, mailto: URL
    - 锚点引用 (#anchor)
    - 不支持的文件扩展名
    - 格式非法的 blueprint_id（交给 GATE-11 N-06 格式校验）
    - 空值 blueprint_id（合法，如 index.md 无归属蓝图）
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 检测文档/数据文件中的断链与幽灵引用。
dimensions:
- D2
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import argparse
import csv
import re

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

# Markdown 链接语法：[text](target)
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

# 纯文本文件路径：匹配 path/to/file.ext 格式（要求含 / 分隔符 + 有扩展名）
# 注意：不要求以 docs/ 开头，因为相对路径也可能是 ./file.md 或 subdir/file.yaml
# 中文前缀防误捕（与 reconciliation_registry.py 一致）：
#   lookbehind 用 [a-zA-Z0-9/] 而非 \w（中文是 \w，会阻挡中文后的路径起点，
#   导致"删除architecture_model/foo.yaml"中"删除"被吞入匹配）；
#   首字符限 [a-zA-Z]（路径必以 ASCII 字母起，杜绝中文前缀被捕获）。
TEXT_PATH_RE = re.compile(
    r"(?<![a-zA-Z0-9/])([a-zA-Z][\w\-./]*?/[\w\-]+\.(?:md|yaml|yml|json|py|ps1|sh|toml|txt|csv))\b"
)

# YAML 值中的文件路径：value: path/to/file.ext
# 同样用 [a-zA-Z] 首字符防中文前缀误捕
YAML_PATH_RE = re.compile(
    r":\s*[\"']?([a-zA-Z][\w\-./]*?/[\w\-]+\.(?:md|yaml|yml|json|py|ps1|sh|toml|txt|csv))[\"']?\s*$",
    re.MULTILINE,
)

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = frozenset({".md", ".csv", ".yaml", ".yml", ".json"})

# 跳过的 URL 前缀
URL_PREFIXES = ("http://", "https://", "ftp://", "mailto:", "#", "data:")

# basename 全局搜索缓存（lazy 初始化，策略3 兜底用）
# 作用：markdown 链接 [text](blueprint.md) 常用裸文件名，策略1/2 解析失败但文件实际
# 存在于项目其他目录。构建全项目 basename→路径集合，O(1) 查找消除大量误报。
_BASENAME_CACHE: set[str] | None = None


def _is_url(target: str) -> bool:
    """判断是否为 URL 或锚点（应跳过）。"""
    return any(target.startswith(p) for p in URL_PREFIXES)


def _get_basename_cache() -> set[str]:
    """获取（lazy 构建）全项目 basename 集合。

    扫描 REPO_ROOT 下所有文件（排除 .git/__pycache__/.runtime/.venv/node_modules），
    收集 basename 到 set 中。一次构建多次复用（模块级缓存）。
    """
    global _BASENAME_CACHE
    if _BASENAME_CACHE is not None:
        return _BASENAME_CACHE
    _BASENAME_CACHE = set()
    _skip_dirs = frozenset({".git", "__pycache__", ".runtime", ".venv", "node_modules", ".pytest_cache"})
    for p in REPO_ROOT.rglob("*"):
        if p.is_file() and not any(part in _skip_dirs for part in p.parts):
            _BASENAME_CACHE.add(p.name)
    return _BASENAME_CACHE


def _resolve_and_check(ref: str, source: Path) -> str | None:
    """解析引用路径并检查文件是否存在。

    路径解析策略（三重尝试，治本 GAP-1 + 裸文件名兜底）：
      1. 先相对于 source.parent 解析（markdown 链接习惯）
      2. 如果不存在，尝试相对于 REPO_ROOT 解析（CSV/YAML 项目根相对路径）
      3. 如果仍不存在，检查 basename 是否在全项目中存在（裸文件名兜底）

    :param ref: 引用路径（相对或绝对）
    :param source: 引用所在文件
    :return: 断链描述字符串（如果断链），None 如果通过
    """
    if _is_url(ref):
        return None

    # 去掉锚点
    ref = ref.split("#")[0].strip()
    if not ref:
        return None

    # 策略1：相对于文件所在目录解析（markdown 链接风格）
    try:
        target_path = (source.parent / ref).resolve()
        if target_path.exists():
            return None
    except (OSError, ValueError):
        pass

    # 策略2：相对于项目根解析（CSV/YAML 项目根相对路径风格）
    try:
        target_path = (REPO_ROOT / ref).resolve()
        if target_path.exists():
            return None
    except (OSError, ValueError):
        pass

    # 策略3：basename 全局搜索兜底（裸文件名如 blueprint.md 在项目其他目录存在）
    basename = ref.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    if basename in _get_basename_cache():
        return None

    return f"断链: {ref} ← {source.name}"


def _extract_md_links(content: str) -> list[str]:
    """提取 Markdown 链接中的目标路径。"""
    refs = []
    for match in MD_LINK_RE.finditer(content):
        target = match.group(2).split("#")[0].strip()
        if target:
            refs.append(target)
    return refs


def _extract_text_paths(content: str) -> list[str]:
    """提取纯文本中的文件路径引用。"""
    refs = []
    for match in TEXT_PATH_RE.finditer(content):
        path_str = match.group(1)
        if not _is_url(path_str):
            refs.append(path_str)
    return refs


def _extract_csv_paths(content: str) -> list[str]:
    """提取 CSV 文件中的文件路径列值。"""
    refs = []
    try:
        reader = csv.reader(content.splitlines())
        for row in reader:
            for cell in row:
                cell = cell.strip().strip('"').strip("'")
                # CSV 中的路径引用：含 / 且有文件扩展名
                if "/" in cell and "." in cell:
                    # 验证是否以已知扩展名结尾
                    if any(cell.endswith(ext) for ext in (".md", ".yaml", ".yml", ".json", ".py", ".ps1", ".sh", ".toml", ".txt", ".csv")):
                        if not _is_url(cell):
                            refs.append(cell)
    except Exception:
        pass  # CSV 解析失败则跳过
    return refs


def _extract_yaml_paths(content: str) -> list[str]:
    """提取 YAML 文件值中的文件路径。"""
    refs = []
    for match in YAML_PATH_RE.finditer(content):
        path_str = match.group(1)
        if not _is_url(path_str):
            refs.append(path_str)
    return refs


# ============================================================================
# GAP-2/3/4 治本扩展（2026-06-29）：语义引用完整性检测
# ============================================================================
# 背景：GAP-1（非.md文件路径引用）已治本。但 AI 幻觉的三类语义引用仍无检测：
#   GAP-2: .md frontmatter.blueprint_id 引用的蓝图是否在 blueprint_registry.yaml 存在
#   GAP-3: index.md 列出的文件清单是否真实存在（严格本地解析，禁 basename 兜底）
#   GAP-4: doc_type=audit_report 引用的审计对象（blueprint_id/module_id/正文ID）是否存在
# 治本路径：扩展现有 audit_broken_links.py（向内收原则 + AGENTS.md 显式声明唯一扩展点）

# --- frontmatter 解析（无 yaml 依赖，简单正则）---
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _frontmatter_field(content: str, field: str) -> str:
    """从 .md frontmatter 提取单字段值（简单正则，避免 yaml 依赖）。

    :param content: 文件全文
    :param field: 字段名（如 blueprint_id / module_id / doc_type）
    :return: 字段值（去除引号和注释），空字符串表示不存在或空值
    """
    m = _FRONTMATTER_RE.match(content)
    if not m:
        return ""
    fm = m.group(1)
    m2 = re.search(
        rf"^{field}:\s*[\"']?([^\"'\n#]+?)[\"']?\s*(?:#.*)?$",
        fm,
        re.MULTILINE,
    )
    if m2:
        return m2.group(1).strip()
    return ""


# --- module_id 格式正则（真源 validate_module_id_naming.py，裁定#208 + R2 治本修订）---
# R2 治本修订（2026-07-05）：D-XXX-NNN 已废弃为 module_id 派生轨，重定义为 submodule_id 专用
# 本文件保留 _MODULE_ID_DERIVED_D_RE 是为了断链检测——历史 blueprint_id 和 submodule_id
# 引用可能使用 D-XXX-NNN 格式，需要查 DB 存在性。R2 修订不影响此处的格式合法性判定，
# 真正的 module_id 格式校验由 GATE-11 N-06 负责（R2 后 N-06 阻断 D-XXX-NNN 作 module_id）。
_MODULE_ID_LAYER_MASTER_RE = re.compile(r"^MOD-[A-Z][A-Z0-9]{1,5}-[0-9]+\Z")
_MODULE_ID_DERIVED_MOD_RE = re.compile(r"^MOD-[A-Z]{1,20}(?:_[A-Z]{1,20})*(?:-[0-9]+)?\Z")
_MODULE_ID_DERIVED_D_RE = re.compile(r"^D-[A-Z]{1,20}(?:_[A-Z]{1,20})*-[0-9]+\Z")
_MODULE_ID_SHARED_RE = re.compile(r"^SH-[A-Z]{1,20}(?:_[A-Z]{1,20})*-[0-9]+\Z")

# 正文中的 MODULE_ID 模式（用于 GAP-4 audit_report 审计对象提取）
_BODY_MODULE_ID_RE = re.compile(
    r"\b("
    r"MOD-[A-Z][A-Z0-9]{1,5}-[0-9]+"
    r"|MOD-[A-Z]{1,20}(?:_[A-Z]{1,20})*(?:-[0-9]+)?"
    r"|D-[A-Z]{1,20}(?:_[A-Z]{1,20})*-[0-9]+"
    r"|SH-[A-Z]{1,20}(?:_[A-Z]{1,20})*-[0-9]+"
    r")\b"
)


def _is_valid_module_id_format(mid: str) -> bool:
    """检查 ID 字符串是否符合已知合法格式之一（用于断链检测的存在性查询门控）。

    真源：validate_module_id_naming.py（裁定#208 双轨制 + R2 治本修订）。

    注意：本函数判定"格式是否良好到值得查 DB 存在性"，不等同于"是否为合法 module_id"。
    R2 治本修订（2026-07-05）后：
    - D-XXX-NNN 已废弃为 module_id 派生轨，重定义为 submodule_id 专用（见 trae_028 gov_doc_009）
    - 但本函数仍接受 D-XXX-NNN 格式，因为：
      (a) 历史数据中可能存在 D-XXX-NNN 作为 blueprint_id（R2 修订前的遗留）
      (b) 蓝图正文中的 submodule_id 引用使用 D-XXX-NNN 格式
      (c) 断链检测需要查这些 ID 是否在 registry 中存在
    - 真正的 module_id 格式校验由 GATE-11 N-06 (_check_n06_dual_track_format) 负责，
      R2 修订后 N-06 会阻断 D-XXX-NNN 作为 module_id 的使用

    格式非法的 ID（如拼写错误）交给 GATE-11 N-06 校验，本函数仅判格式合法性以决定是否查存在性。
    """
    return any(
        p.match(mid)
        for p in (
            _MODULE_ID_LAYER_MASTER_RE,
            _MODULE_ID_DERIVED_MOD_RE,
            _MODULE_ID_DERIVED_D_RE,
            _MODULE_ID_SHARED_RE,
        )
    )


# --- blueprint_registry.yaml 缓存（GAP-2/GAP-4 共用）---
_VALID_BLUEPRINT_IDS: set[str] | None = None


def _get_valid_blueprint_ids() -> set[str]:
    """Lazy 加载 blueprint_registry.yaml 中所有合法 module_id 集合。

    真源链：blueprint.md frontmatter → sync_registry_from_blueprints.py
    → blueprint_registry.yaml → 本函数。
    本函数不调 load_blueprint_path()（src/zephyr/governance/...），保持
    audit_broken_links.py 纯 scripts/ 依赖（避免 import zephyr.* 链断裂风险）。
    """
    global _VALID_BLUEPRINT_IDS
    if _VALID_BLUEPRINT_IDS is not None:
        return _VALID_BLUEPRINT_IDS
    _VALID_BLUEPRINT_IDS = set()
    registry_path = REPO_ROOT / "docs" / "03_modules" / "blueprint_registry.yaml"
    if not registry_path.exists():
        return _VALID_BLUEPRINT_IDS
    try:
        import yaml
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for bp in (data or {}).get("blueprints", []):
            mid = bp.get("module_id")
            if mid:
                _VALID_BLUEPRINT_IDS.add(mid)
    except Exception:
        pass  # registry 解析失败不阻断（降级为空集，所有 ID 判通过）
    return _VALID_BLUEPRINT_IDS


def _check_blueprint_id_exists(bp_id: str, source: Path, gap_tag: str = "GAP-2") -> str | None:
    """GAP-2 核心：校验 blueprint_id 是否在 blueprint_registry.yaml 中存在。

    :param bp_id: 待校验的 module_id
    :param source: 引用所在文件（用于错误消息）
    :param gap_tag: GAP 标签（GAP-2=frontmatter / GAP-4=audit_report）
    :return: 断链描述字符串（如果不存在），None 如果通过

    规则：
    - 空值跳过（合法，如 index.md 无归属蓝图）
    - 格式非法跳过（由 GATE-11 N-06 覆盖格式校验，避免重复）
    - registry 不可用（空集）跳过（降级不阻断）
    """
    if not bp_id:
        return None
    if not _is_valid_module_id_format(bp_id):
        return None  # 格式问题交给 N-06，不在此重复校验
    valid_ids = _get_valid_blueprint_ids()
    if not valid_ids:
        return None  # registry 不可用，降级不阻断
    if bp_id not in valid_ids:
        return (
            f"{gap_tag} 幻觉blueprint_id: {bp_id} "
            f"不在blueprint_registry.yaml ← {source.name}"
        )
    return None


# --- GAP-3: index.md 文件清单严格本地解析 ---
def _check_index_md_inventory(content: str, source: Path) -> list[str]:
    """GAP-3: 严格校验 index.md 列出的文件清单存在性。

    仅相对 source.parent 解析，**禁止 basename 全局兜底**。
    理由：index.md 是"本目录契约"，basename 兜底会掩盖幻觉
    （如 index.md 列 phantom.md，别处有同名 phantom.md 误判通过）。

    处理两种引用格式：
    1. [text](relative_path) — markdown 链接（自动生成 index.md 风格）
    2. [text](file:///D:/ZephyrAlpha/...) — 绝对 URL（手工编写 index.md 风格）
    """
    if source.name != "index.md":
        return []

    broken: list[str] = []
    seen: set[str] = set()

    for m in MD_LINK_RE.finditer(content):
        target = m.group(2).split("#")[0].strip()
        if not target:
            continue
        # 跳过外部 URL（http/https/ftp/mailto/#/data:）
        if _is_url(target):
            continue

        # 处理 file:/// 绝对路径
        if target.startswith("file:///"):
            abs_path = target[len("file:///"):]
            # Windows: file:///D:/ZephyrAlpha/... -> 尝试直接解析
            try:
                if Path(abs_path).exists():
                    continue
            except (OSError, ValueError):
                pass
            # 剥离盘符+项目根，转项目相对路径
            norm = abs_path.replace("\\", "/")
            parts = norm.split("/", 2)
            if len(parts) >= 3 and ":" in parts[0]:
                rel = parts[2]
                try:
                    if (REPO_ROOT / rel).exists():
                        continue
                except (OSError, ValueError):
                    pass
            if target not in seen:
                seen.add(target)
                broken.append(
                    f"GAP-3 index清单断链: {target} ← {source.name}"
                )
            continue

        # 标准相对路径——仅 source.parent，无 basename 兜底
        try:
            if (source.parent / target).resolve().exists():
                continue
        except (OSError, ValueError):
            pass
        if target not in seen:
            seen.add(target)
            broken.append(f"GAP-3 index清单断链: {target} ← {source.name}")

    return broken


# --- GAP-4: audit_report 审计对象存在性 ---
def _check_audit_report_objects(content: str, source: Path) -> list[str]:
    """GAP-4: 校验 doc_type=audit_report 文档的审计对象存在性。

    三类引用：
    1. frontmatter.blueprint_id（非空）→ 校验存在性（复用 GAP-2 逻辑）
    2. frontmatter.module_id（非空）→ 校验存在性（语义混淆但事实存在）
    3. 正文 MODULE_ID 匹配 → 校验存在性

    自动生成 audit_report（无 blueprint_id 无 module_id）→ 跳过
    （由 generate_constraint_violations.py 等生成器保证数据真源）。
    """
    doc_type = _frontmatter_field(content, "doc_type")
    if doc_type != "audit_report":
        return []

    broken: list[str] = []
    seen: set[str] = set()

    # 1. frontmatter.blueprint_id
    bp_id = _frontmatter_field(content, "blueprint_id")
    if bp_id and bp_id not in seen:
        seen.add(bp_id)
        result = _check_blueprint_id_exists(bp_id, source, gap_tag="GAP-4")
        if result:
            broken.append(result)

    # 2. frontmatter.module_id
    mod_id = _frontmatter_field(content, "module_id")
    if mod_id and mod_id not in seen:
        seen.add(mod_id)
        result = _check_blueprint_id_exists(mod_id, source, gap_tag="GAP-4")
        if result:
            broken.append(result)

    # 3. 正文 MODULE_ID（双轨制+submodule_id 正则匹配）
    for m in _BODY_MODULE_ID_RE.finditer(content):
        mid = m.group(1)
        if mid in seen:
            continue
        seen.add(mid)
        result = _check_blueprint_id_exists(mid, source, gap_tag="GAP-4")
        if result:
            broken.append(result)

    return broken


def _audit_content(content: str, file_path: Path) -> list[str]:
    """审计文件内容，返回断链列表（不读磁盘）。

    被 audit_file 和 audit_file_check_new 共用，避免逻辑重复（向内收）。
    提取器选择 + GAP-2/3/4 检测 + 通用路径解析全在此函数。
    """
    broken: list[str] = []

    # 根据扩展名选择提取器
    refs: list[str] = []
    ext = file_path.suffix.lower()
    if ext == ".md":
        refs.extend(_extract_md_links(content))
        refs.extend(_extract_text_paths(content))
        # GAP-2: frontmatter.blueprint_id 存在性检测
        bp_id = _frontmatter_field(content, "blueprint_id")
        if bp_id:
            result = _check_blueprint_id_exists(bp_id, file_path, gap_tag="GAP-2")
            if result:
                broken.append(result)
        # GAP-3: index.md 文件清单严格本地解析（禁 basename 兜底）
        broken.extend(_check_index_md_inventory(content, file_path))
        # GAP-4: audit_report 审计对象存在性
        broken.extend(_check_audit_report_objects(content, file_path))
    elif ext == ".csv":
        refs.extend(_extract_csv_paths(content))
    elif ext in (".yaml", ".yml"):
        refs.extend(_extract_yaml_paths(content))
        refs.extend(_extract_text_paths(content))
    elif ext == ".json":
        refs.extend(_extract_text_paths(content))

    # 去重并检查（通用路径引用，含 basename 兜底）
    seen: set[str] = set()
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        result = _resolve_and_check(ref, file_path)
        if result:
            broken.append(result)

    return broken


def audit_file(file_path: str | Path) -> tuple[bool, list[str]]:
    """审计单个文件的断链与幽灵引用。

    :param file_path: 文件路径
    :return: (是否通过, 断链列表)
    """
    p = Path(file_path)
    if not p.exists():
        return False, [f"文件不存在: {file_path}"]
    if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return True, []  # 不支持的扩展名跳过

    try:
        content = p.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError) as exc:
        return False, [f"读取失败: {p} ({exc})"]

    broken = _audit_content(content, p)
    return len(broken) == 0, broken


# --- 历史豁免模式（--check-new，参考 N-16 模式）---
def _get_head_content(file_path: Path) -> str | None:
    """获取文件在 HEAD 版本的内容（用于历史豁免对比）。

    :return: HEAD 版本内容，或 None（文件不在 git 历史中，即新文件）
    """
    import subprocess
    try:
        abs_path = file_path.resolve()
        rel = abs_path.relative_to(REPO_ROOT)
    except (ValueError, OSError):
        return None
    rel_str = str(rel).replace("\\", "/")
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel_str}"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return None  # 新文件或 git 错误
    return result.stdout


def audit_file_check_new(file_path: str | Path) -> tuple[bool, list[str]]:
    """审计文件，仅报告本次修改新引入的断链（历史豁免）。

    对比 HEAD 版本和工作区版本：
    - 新文件（不在 HEAD）：报告所有断链（全部是新引入的）
    - 修改文件：仅报告 HEAD 中不存在的断链（新引入的）
    - 删除文件：跳过（无内容可检查）

    设计参考：check_naming_convention.py --check-new（N-16 历史豁免模式）。
    用于 pre-commit --ci 硬阻断：仅阻断新引入的断链，不阻断历史存量。

    :return: (是否通过, 新断链列表)
    """
    p = Path(file_path)
    if not p.exists():
        return True, []  # 删除文件不检查
    if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return True, []
    try:
        new_content = p.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return True, []  # 读取失败不阻断

    new_broken = set(_audit_content(new_content, p))

    head_content = _get_head_content(p)
    if head_content is None:
        # 新文件：所有断链都是新引入的
        return len(new_broken) == 0, sorted(new_broken)

    # 修改文件：仅报告 HEAD 中不存在的断链（新引入的）
    old_broken = set(_audit_content(head_content, p))
    new_violations = new_broken - old_broken
    return len(new_violations) == 0, sorted(new_violations)


def audit_directory(dir_path: str | Path) -> tuple[bool, list[str]]:
    """递归审计目录下所有支持文件的断链。"""
    p = Path(dir_path)
    if not p.exists():
        return False, [f"目录不存在: {dir_path}"]

    all_broken: list[str] = []
    for ext in SUPPORTED_EXTENSIONS:
        for file_path in p.rglob(f"*{ext}"):
            # 跳过 .git, node_modules, __pycache__ 等
            if any(part in (".git", "node_modules", "__pycache__", ".runtime", ".venv") for part in file_path.parts):
                continue
            ok, broken = audit_file(file_path)
            if not ok:
                all_broken.extend(broken)

    return len(all_broken) == 0, all_broken


def main() -> int:
    """Entry point: parse args, run audit, return exit code."""
    parser = argparse.ArgumentParser(
        description="检测文档/数据文件中的断链与幽灵引用"
    )
    parser.add_argument(
        "path",
        nargs="+",
        help="要检测的文件或目录路径（支持多个）",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI 硬阻断模式：发现断链时 exit 1（用于 pre-commit 钩子）",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="只警告模式：发现断链时仅打印，exit 0（用于过渡期巡检）",
    )
    parser.add_argument(
        "--check-new",
        action="store_true",
        help="历史豁免模式：仅报告本次修改新引入的断链（对比 HEAD 版本，参考 N-16 模式）",
    )
    args = parser.parse_args()

    all_broken: list[str] = []
    for path_str in args.path:
        p = Path(path_str)
        if p.is_dir():
            if args.check_new:
                # 目录模式 + 历史豁免：逐文件 check-new
                for ext in SUPPORTED_EXTENSIONS:
                    for fp in p.rglob(f"*{ext}"):
                        if any(
                            part in (".git", "node_modules", "__pycache__", ".runtime", ".venv")
                            for part in fp.parts
                        ):
                            continue
                        ok, broken = audit_file_check_new(fp)
                        all_broken.extend(broken)
            else:
                ok, broken = audit_directory(p)
                all_broken.extend(broken)
        else:
            if args.check_new:
                ok, broken = audit_file_check_new(p)
            else:
                ok, broken = audit_file(p)
            all_broken.extend(broken)

    if not all_broken:
        print("✅ 无断链")
        return EXIT_PASS

    print(f"❌ 发现 {len(all_broken)} 条断链:")
    for b in all_broken:
        print(f"  → {b}")

    if args.warn_only:
        return EXIT_PASS
    if args.ci:
        return EXIT_FINDINGS
    # 默认：打印断链但 exit 0（兼容旧行为）
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
