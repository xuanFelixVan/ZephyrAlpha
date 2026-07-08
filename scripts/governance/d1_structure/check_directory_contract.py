#!/usr/bin/env python
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/check_directory_contract.py | §
# [MODULE] scripts.governance.d1_structure.check_directory_contract
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] _shared.constants; _shared.frontmatter; _shared.walk
# [CONSUMERS] .pre-commit-config.yaml GATE-DIRECTORY-CONTRACT (pre-commit hook，已启用)
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 真源为 directory_contract.yaml（DCR-001/005/006/007 目录维度 + allowed_doc_types）；doc_type_vocabulary.yaml 仅用于 doc_type 合法性验证（GATE-15 主责）；DCR-001~007 已启用（DCR-002 废弃 P3）；只读校验不修改文件
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0; EXIT_FINDINGS=1（error 级违规）; EXIT_ERROR=2（脚本异常）
# [TESTS] none
# [TTL] task_bound
"""GATE-DIRECTORY-CONTRACT: Directory Contract validation gate.

Consumes directory_contract.yaml（目录维度约束的唯一真源，合并原先分散在
trae_047 directory_mapping / ttl_vocabulary Q3 / doc_type_vocabulary crosscheck
三维来源）并校验文件合规性。

Implemented checks (DCR-001~007):
  DCR-001: directory.allowed_doc_types contains file.doc_type (error, P3 改造)
  DCR-002: 废弃（P3 改造——forbidden_directories 全为空，allowed_doc_types 白名单已足够）
  DCR-003: permanent zone file ttl == permanent             (error)
  DCR-004: temporary zone file ttl == task_bound            (warning)
  DCR-005: file extension in directory_extensions.allowed   (error)
  DCR-006: file extension not in directory_extensions.forbidden (error)
  DCR-007: root directory file in root_directory_whitelist  (error)

DCR-001 豁免区：docs/_working/（临时区）、docs/_archive/（归档区）、.runtime/（运行时归档区）、.trae/（IDE 工具区）、docs/01_policies_and_standards/templates/（模板区 TMP-EX-001）
DCR-001 真源：directory_contract.yaml directory_extensions[].allowed_doc_types（P3 改造，原 doc_type_vocabulary.yaml allowed_directories 已废弃）

Modes:
  --staged              check git-staged files only (pre-commit use)
  --all-files           force full scan (ignore file args)
  --warn-only           print findings, never block (exit 0)
  (default)             scan all in-scope files, block on errors (exit 1)
  file args             incremental check (pre-commit pass_filenames=true)

Exit codes: 0=pass, 1=findings (error-severity violations), 2=script error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'GATE-DIRECTORY-CONTRACT: Directory Contract validation gate.'
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import subprocess
import sys
from pathlib import Path

# ── 路径设置 ──
# bootstrap：scripts/ 包外消费者一次性极简 sys.path，随后 from _shared.constants import REPO_ROOT
# 真源约束：AGENTS.md §7 REPO_ROOT 真源归一（project_memory REPO_ROOT 硬约束）
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402
from _shared.frontmatter import parse_frontmatter_from_file  # noqa: E402
from _shared.walk import iter_files  # noqa: E402

import yaml  # noqa: E402

# ── 真源路径 ──
_CONTRACT_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards"
    / "_registry" / "contracts" / "directory_contract.yaml"
)
_VOCABULARY_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards"
    / "_registry" / "vocabularies" / "doc_type_vocabulary.yaml"
)

# DCR-001/002 豁免目录前缀（临时区 + 归档区 + 运行时/IDE 工具区 + 模板区）
# docs/_working/：临时工作区（过程性文档）
# docs/_archive/：永久区归档（历史遗留，不受新规则约束）
# .runtime/：运行时归档区（working_archive 等，neutral zone，非正式文档区）
# .trae/：IDE 工具区（documents 等，过程性文档，非正式文档区）
# docs/01_policies_and_standards/templates/：模板区（TMP-EX-001 豁免——模板是 Class Definition，
#   cookbook template 的 doc_type 取目标类型，不受目标类型的 allowed_directories 约束）
_DCR_EXEMPT_PREFIXES = (
    "docs/_working/", "docs/_archive/", ".runtime/", ".trae/",
    "docs/01_policies_and_standards/templates/",
)

# 扫描的扩展名集合（覆盖所有 zone 可能出现的文件类型）
_SCAN_EXTENSIONS: frozenset[str] = frozenset({
    ".md", ".yaml", ".yml", ".py", ".sh", ".ps1", ".mmd",
    ".csv", ".json", ".jsonl", ".txt", ".bak", ".baseline",
})


# ════════════════════════════════════════════════════════════════════════════
# 契约加载
# ════════════════════════════════════════════════════════════════════════════

def load_contract() -> dict:
    """加载 directory_contract.yaml（目录维度约束唯一真源）。

    词表维度（ttl/doc_type 值定义）保留在各自 vocabulary.yaml，本契约只管目录维度。
    """
    with open(_CONTRACT_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_doc_type_vocabulary() -> dict:
    """加载 doc_type_vocabulary.yaml，返回 doc_type → config 映射。

    P3/P4 治本后用途收窄：DCR-001 真源已切到 directory_contract.yaml 的
    allowed_doc_types 字段，本函数仅用于验证 doc_type 是否为已知合法值
    （未知 doc_type 跳过 DCR-001 校验，交 GATE-15 负责）。
    doc_type_vocabulary.yaml 的 allowed_directories/forbidden_directories
    字段已于 P4 删除（目录约束迁移到 directory_contract.yaml）。
    """
    with open(_VOCABULARY_PATH, encoding="utf-8") as f:
        vocab = yaml.safe_load(f)
    return {v["value"]: v for v in vocab.get("values", [])}


def get_staged_files() -> list[str]:
    """获取 staged 文件列表（相对路径，仅新增/修改/重命名）。

    fail-open：git 不在 PATH 或调用失败时返回空列表（不阻断提交）。
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


# ════════════════════════════════════════════════════════════════════════════
# 契约查询（longest-prefix match）
# ════════════════════════════════════════════════════════════════════════════

def _normalize_dir(rel_dir: str) -> str:
    """目录路径归一化：反斜杠→正斜杠，确保以 / 结尾。"""
    normalized = rel_dir.replace("\\", "/").rstrip("/")
    return normalized + "/" if normalized else "./"


def find_zone(contract: dict, rel_dir: str) -> tuple[str | None, dict | None]:
    """查找目录所属 zone。

    Zone 优先级：temporary > permanent > neutral
    （temporary 是 docs/ 下的子集，需先于 permanent 检查——
    实际上两者路径不重叠，但先查 temporary 更安全）

    Returns:
        (zone_name, zone_config) 或 (None, None)
    """
    rel_dir_norm = _normalize_dir(rel_dir)
    for zone_name in ("temporary", "permanent", "neutral"):
        zone = contract["directory_zones"][zone_name]
        for path in zone["paths"]:
            if rel_dir_norm.startswith(path):
                return zone_name, zone
    return None, None


def find_extension_rule(contract: dict, rel_dir: str) -> dict | None:
    """查找最具体的 directory_extensions 规则（longest-prefix match）。

    多个规则可能同时匹配（如 docs/_working/ 和 docs/_working/audit/），
    取路径最长的（最具体的）。overrides_parent=true 的规则完全替换父规则。
    """
    rel_dir_norm = _normalize_dir(rel_dir)
    best_rule: dict | None = None
    best_len = 0
    for rule in contract["directory_extensions"]:
        path = rule["path"].rstrip("/") + "/"
        if rel_dir_norm.startswith(path) and len(path) > best_len:
            best_len = len(path)
            best_rule = rule
    return best_rule


def get_extension_exceptions(rule: dict, rel_dir: str) -> set[str]:
    """获取适用于当前子目录的扩展名例外（allowed_exceptions）。

    某些子目录允许父规则 forbidden 清单中的扩展名（如 _registry/schemas/ 允许 .json）。
    subdir 可写相对路径（相对于 rule path，如 _registry/schemas/）或完整路径
    （如 docs/01_policies_and_standards/_registry/schemas/），两种格式都支持。
    """
    if not rule or "allowed_exceptions" not in rule:
        return set()
    rel_dir_norm = _normalize_dir(rel_dir)
    rule_path = rule["path"].rstrip("/") + "/"
    exceptions: set[str] = set()
    for exc in rule["allowed_exceptions"]:
        subdir = exc["subdir"].rstrip("/") + "/"
        # subdir 若非完整路径，拼接 rule path（支持相对路径写法）
        if not subdir.startswith(rule_path):
            subdir = rule_path + subdir
        if rel_dir_norm.startswith(subdir):
            exceptions.update(exc.get("extensions", []))
    return exceptions


# ════════════════════════════════════════════════════════════════════════════
# DCR 校验逻辑
# ════════════════════════════════════════════════════════════════════════════

def check_extension(rel_path: str, contract: dict) -> list[dict]:
    """DCR-005 + DCR-006: 文件扩展名必须在目录的 allowed 清单内，不在 forbidden 清单内。

    DCR-005: file.extension in directory_extensions[path].allowed OR allowed_exceptions
    DCR-006: file.extension not in directory_extensions[path].forbidden
    """
    rel_dir = str(Path(rel_path).parent).replace("\\", "/")
    if rel_dir == ".":
        return []  # 根目录文件由 DCR-007 处理
    ext = Path(rel_path).suffix
    rule = find_extension_rule(contract, rel_dir)
    if not rule:
        return []  # 该目录无扩展名规则
    findings: list[dict] = []
    exceptions = get_extension_exceptions(rule, rel_dir)
    allowed = set(rule.get("allowed", [])) | exceptions
    forbidden = set(rule.get("forbidden", []))
    # DCR-005: 扩展名必须在 allowed 清单内（仅当 allowed 非空时校验）
    if allowed and ext not in allowed:
        findings.append({
            "rule": "DCR-005",
            "severity": "error",
            "file": rel_path,
            "detail": f"扩展名 {ext} 不在 {rule['path']} 的 allowed 清单 {sorted(allowed)} 内",
        })
    # DCR-006: 扩展名不得在 forbidden 清单内
    if ext in forbidden:
        findings.append({
            "rule": "DCR-006",
            "severity": "error",
            "file": rel_path,
            "detail": f"扩展名 {ext} 在 {rule['path']} 的 forbidden 清单内",
        })
    return findings


def check_root_whitelist(rel_path: str, contract: dict) -> list[dict]:
    """DCR-007: 根目录文件必须在白名单内。

    check: if file.directory == project_root then file.name in root_directory_whitelist.files
    """
    parent = Path(rel_path).parent
    if str(parent) != ".":
        return []
    filename = Path(rel_path).name
    whitelist = set(contract["root_directory_whitelist"]["files"])
    if filename not in whitelist:
        return [{
            "rule": "DCR-007",
            "severity": "error",
            "file": rel_path,
            "detail": f"根目录文件 {filename} 不在白名单内（白名单共 {len(whitelist)} 个文件）",
        }]
    return []


def check_ttl_zone(rel_path: str, contract: dict) -> list[dict]:
    """DCR-003 + DCR-004: 文件 ttl 必须匹配所在 zone 的 default_ttl。

    DCR-003: permanent zone file ttl == permanent (error)
    DCR-004: temporary zone file ttl == task_bound (warning)

    范围说明（2026-06-30 修正，trae_047 v1.2.0 全格式加 ttl 后原注释过时）：
      - DCR-003/004 校验"frontmatter.ttl 与 zone.default_ttl 的一致性"，仅对
        permanent/temporary zone 生效；neutral zone 的 default_ttl=null，无可比对值，跳过。
      - 仅校验 .md 是因为 permanent/temporary zone 主体是 .md 文档（.yaml 治理锚定
        ttl、.py 代码文件 ttl 的值合法性由 GATE-15 check_frontmatter_metadata.py 全格式校验，
        本脚本不重复）。
      - 代码文件（.py/.sh/.ps1）确实有 ttl 字段（A_full/A_test/E_shell 格式，trae_047 v1.2.0），
        但它们位于 neutral zone，DCR-003/004 不适用。
    """
    rel_dir = str(Path(rel_path).parent).replace("\\", "/")
    zone_name, zone = find_zone(contract, rel_dir)
    if not zone or zone.get("default_ttl") is None:
        return []  # neutral zone（default_ttl=null）无 default_ttl 可比对，跳过一致性校验
    if not rel_path.endswith(".md"):
        return []  # DCR-003/004 聚焦 .md（permanent/temporary zone 主体）；代码文件 ttl 值合法性由 GATE-15 负责
    abs_path = REPO_ROOT / rel_path
    try:
        fm, _ = parse_frontmatter_from_file(abs_path)
    except OSError:
        return []
    ttl = fm.get("ttl")
    if not ttl:
        return []  # ttl 缺失由 GATE-15 (check_frontmatter_metadata.py) 负责，不重复校验
    findings: list[dict] = []
    default_ttl = zone.get("default_ttl")
    if zone_name == "permanent" and ttl != "permanent":
        findings.append({
            "rule": "DCR-003",
            "severity": "error",
            "file": rel_path,
            "detail": f"永久区文件 ttl={ttl}，应为 permanent（目录 {rel_dir} 属 permanent zone）",
        })
    elif zone_name == "temporary" and ttl != "task_bound":
        findings.append({
            "rule": "DCR-004",
            "severity": "warning",
            "file": rel_path,
            "detail": f"临时区文件 ttl={ttl}，建议 task_bound（目录 {rel_dir} 属 temporary zone）",
        })
    return findings


def check_doc_type_directory(rel_path: str, contract: dict, vocab: dict | None = None) -> list[dict]:
    """DCR-001: 目录→doc_type 约束校验（P3 改造：数据源切到 directory_contract.yaml allowed_doc_types）。

    DCR-001: 文件所在目录的 allowed_doc_types 非空时，file.doc_type 必须在 allowed_doc_types 内
             豁免区：docs/_working/、docs/_archive/、.runtime/、.trae/、templates/（TMP-EX-001）
    DCR-002: 已废弃（P3 改造）——原 doc_type_vocabulary.yaml 的 forbidden_directories 全为空数组，
             allowed_doc_types 白名单已足够严格（不在白名单即违规，等价于 forbidden）

    数据源：directory_contract.yaml 的 directory_extensions[].allowed_doc_types
    方向：directory → doc_types（对应用户诉求"每个文件夹只能放什么类型的文件"）

    仅校验有 frontmatter 的文件。doc_type 合法性（是否在词表内）由 GATE-15 负责，
    本函数仅校验"合法 doc_type 是否出现在正确的目录"。

    vocab 参数保留向后兼容签名，仅用于验证 doc_type 是否为已知值（未知则跳过，交 GATE-15）。
    """
    if not rel_path.endswith((".md", ".yaml", ".yml")):
        return []

    abs_path = REPO_ROOT / rel_path
    try:
        fm, _ = parse_frontmatter_from_file(abs_path)
    except OSError:
        return []

    doc_type = fm.get("doc_type")
    if not doc_type:
        return []  # 无 doc_type 的文件不校验（由 GATE-15 负责）

    # 未知 doc_type 跳过（由 GATE-15 check_frontmatter_metadata.py 负责）
    if vocab is not None and doc_type not in vocab:
        return []

    rel_posix = rel_path.replace("\\", "/")
    rel_dir = str(Path(rel_posix).parent).replace("\\", "/")
    if rel_dir == ".":
        return []  # 根目录文件由 DCR-007 处理

    # 豁免区检查（临时区、归档区、运行时区、模板区）
    if any(rel_posix.startswith(prefix) for prefix in _DCR_EXEMPT_PREFIXES):
        return []

    # 查找文件所在目录的 extension rule（longest-prefix match）
    rule = find_extension_rule(contract, rel_dir)
    if not rule:
        return []  # 目录无声明，跳过

    allowed_doc_types = rule.get("allowed_doc_types")
    if not allowed_doc_types:
        return []  # allowed_doc_types 为空数组 []，该目录豁免 doc_type 约束（代码/数据/临时区）

    # DCR-001: file.doc_type 必须在 directory.allowed_doc_types 内
    if doc_type not in allowed_doc_types:
        return [{
            "rule": "DCR-001",
            "severity": "error",
            "file": rel_path,
            "detail": f"doc_type={doc_type} 不在目录 {rule['path']} 的 allowed_doc_types {allowed_doc_types} 内",
        }]

    return []


def check_deprecated_directory(rel_path: str, contract: dict) -> list[dict]:
    """检测文件是否位于废弃目录（directory_contract.yaml §7 deprecated_directories）。

    治本（2026-07-08，ARCH-DEBT-BACKUP-CLEANUP）：deprecated_directories 的设计意图是
    阻断**新建**文件进入废弃目录，而非阻断**删除**废弃目录中的已有文件。删除废弃目录中的
    文件正是期望的迁移行为，应予放行。通过检测文件是否存在于磁盘上区分 add/modify vs delete：
    文件不存在=删除操作→跳过 deprecated 检查。
    """
    # 文件不存在于磁盘 = 删除操作 → 放行（删除废弃目录中的文件是期望行为）
    if not (REPO_ROOT / rel_path).exists():
        return []
    findings: list[dict] = []
    for entry in (contract.get("deprecated_directories") or []):
        dep_path = entry.get("path", "").replace("\\", "/").rstrip("/")
        if not dep_path:
            continue
        rel_norm = rel_path.replace("\\", "/")
        if rel_norm == dep_path or rel_norm.startswith(dep_path + "/"):
            findings.append({
                "rule": "DCR-DEPRECATED",
                "severity": entry.get("severity", "error"),
                "file": rel_path,
                "detail": (
                    f"文件位于废弃目录 {dep_path}（{entry.get('reason', '已迁移')}），"
                    f"请迁移到 {entry.get('migrated_to', '合规目录')}"
                ),
            })
    return findings


def scan_files(files: list[str], contract: dict, vocab: dict | None = None) -> list[dict]:
    """对给定文件列表执行所有已实现的 DCR 校验。"""
    if vocab is None:
        vocab = load_doc_type_vocabulary()
    findings: list[dict] = []
    for rel_path in files:
        findings.extend(check_doc_type_directory(rel_path, contract, vocab))
        findings.extend(check_extension(rel_path, contract))
        findings.extend(check_root_whitelist(rel_path, contract))
        findings.extend(check_ttl_zone(rel_path, contract))
        findings.extend(check_deprecated_directory(rel_path, contract))
    return findings


# ════════════════════════════════════════════════════════════════════════════
# 全量扫描
# ════════════════════════════════════════════════════════════════════════════

def scan_all(contract: dict) -> list[str]:
    """扫描契约覆盖的所有目录，返回相对路径文件列表。

    治本（P6b 2026-06-30）：用 ``git ls-files --cached --others --exclude-standard``
    替代 ``os.walk``——只扫描 git 跟踪文件 + 未跟踪但未被 .gitignore 排除的文件。
    运行时产物（.json/.jsonl 缓存等，已被 .gitignore 排除）不再被误判为漂移。

    扫描范围：
      - 根目录（仅一级文件，DCR-007）
      - directory_extensions 中所有 path
      - directory_zones 中所有 zone 的 paths

    降级：git 不可用时回退到 os.walk（iter_files），此时运行时产物可能被误报。
    """
    # 构建扫描前缀集合（相对路径，末尾加 / 确保前缀匹配精确）
    scan_prefixes: set[str] = set()
    for rule in contract["directory_extensions"]:
        scan_prefixes.add(rule["path"].rstrip("/") + "/")
    for zone in contract["directory_zones"].values():
        for path in zone["paths"]:
            scan_prefixes.add(path.rstrip("/") + "/")

    # 尝试用 git ls-files 获取待扫描文件（治本：尊重 .gitignore）
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard",
             "--full-name"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            encoding="utf-8", errors="replace",
        )
        if result.returncode == 0:
            git_files = set(
                line.strip() for line in result.stdout.splitlines() if line.strip()
            )
            return _filter_scan_files(git_files, scan_prefixes)
    except (FileNotFoundError, subprocess.SubprocessError):
        pass  # 降级到 os.walk

    # 降级：os.walk（git 不可用时）
    return _scan_all_walk(contract, scan_prefixes)


def _filter_scan_files(git_files: set[str], scan_prefixes: set[str]) -> list[str]:
    """从 git ls-files 输出中筛选契约覆盖的文件。

    根目录文件（不含 /）全部保留（DCR-007 校验）。
    子目录文件必须落在某个 scan_prefix 内，且扩展名在 _SCAN_EXTENSIONS 中。
    """
    files: list[str] = []
    for rel_path in git_files:
        rel_posix = rel_path.replace("\\", "/")
        # 根目录文件（DCR-007）
        if "/" not in rel_posix:
            files.append(rel_posix)
            continue
        # 子目录文件：检查是否在扫描范围内
        for prefix in scan_prefixes:
            if rel_posix.startswith(prefix):
                ext = Path(rel_posix).suffix.lower()
                if ext in _SCAN_EXTENSIONS:
                    files.append(rel_posix)
                break
    return sorted(set(files))


def _scan_all_walk(contract: dict, scan_prefixes: set[str]) -> list[str]:
    """降级扫描：git 不可用时用 os.walk（iter_files）。

    注意：此路径不尊重 .gitignore，运行时产物可能被误报。
    """
    scan_dirs: set[Path] = set()
    scan_dirs.add(REPO_ROOT)  # 根目录文件（DCR-007）
    for rule in contract["directory_extensions"]:
        scan_dirs.add(REPO_ROOT / rule["path"])
    for zone in contract["directory_zones"].values():
        for path in zone["paths"]:
            scan_dirs.add(REPO_ROOT / path)

    files: list[str] = []
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        if scan_dir == REPO_ROOT:
            for p in REPO_ROOT.iterdir():
                if p.is_file() and not p.name.startswith(".git"):
                    files.append(str(p.relative_to(REPO_ROOT)).replace("\\", "/"))
        else:
            for p in iter_files(scan_dir, extensions=_SCAN_EXTENSIONS):
                files.append(str(p.relative_to(REPO_ROOT)).replace("\\", "/"))
    return sorted(set(files))


# ════════════════════════════════════════════════════════════════════════════
# 主入口
# ════════════════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        description="GATE-DIRECTORY-CONTRACT: 目录契约校验（DCR-001~007）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--ci", action="store_true",
                      help="硬阻断模式（违规 exit 1）——与默认行为一致，为 pre-commit 钩子兼容保留")
    mode.add_argument("--warn-only", action="store_true",
                      help="只警告不阻断（exit 0）")
    parser.add_argument("--staged", action="store_true",
                        help="只校验 git staged 文件（pre-commit use）")
    parser.add_argument("--all-files", action="store_true",
                        help="强制全量扫描（忽略传入的文件参数）")
    parser.add_argument("files", nargs="*", help="增量校验文件列表（相对路径）")
    args = parser.parse_args()

    # 加载契约
    try:
        contract = load_contract()
    except Exception as e:
        print(f"[GATE-DIRECTORY-CONTRACT] ERROR: 无法加载 directory_contract.yaml: {e}",
              file=sys.stderr)
        return EXIT_ERROR

    # 加载 doc_type 词表（DCR-001/002 真源）
    try:
        vocab = load_doc_type_vocabulary()
    except Exception as e:
        print(f"[GATE-DIRECTORY-CONTRACT] ERROR: 无法加载 doc_type_vocabulary.yaml: {e}",
              file=sys.stderr)
        return EXIT_ERROR

    # 确定扫描文件列表
    if args.staged:
        files = get_staged_files()
    elif args.all_files or (not args.files and not args.staged):
        files = scan_all(contract)
    else:
        files = [str(Path(f).as_posix()) for f in args.files]

    if not files:
        print("[GATE-DIRECTORY-CONTRACT] PASS: 无待校验文件", file=sys.stderr)
        return EXIT_PASS

    # 执行校验
    try:
        findings = scan_files(files, contract, vocab)
    except Exception as e:
        print(f"[GATE-DIRECTORY-CONTRACT] ERROR: 校验异常: {e}", file=sys.stderr)
        return EXIT_ERROR

    if not findings:
        print(f"[GATE-DIRECTORY-CONTRACT] PASS: {len(files)} 文件校验通过", file=sys.stderr)
        return EXIT_PASS

    # 分类输出
    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]

    print(f"[GATE-DIRECTORY-CONTRACT] {len(findings)} 个发现"
          f"（{len(errors)} errors, {len(warnings)} warnings）:", file=sys.stderr)
    for f in findings:
        print(f"  [{f['severity']}] {f['rule']} {f['file']}", file=sys.stderr)
        print(f"    {f['detail']}", file=sys.stderr)

    if args.warn_only:
        return EXIT_PASS
    if errors:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
