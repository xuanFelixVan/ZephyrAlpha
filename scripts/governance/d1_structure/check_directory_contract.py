#!/usr/bin/env python
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/check_directory_contract.py | §
# [MODULE] scripts.governance.d1_structure.check_directory_contract
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] _shared.constants; _shared.frontmatter; _shared.walk
# [CONSUMERS] .pre-commit-config.yaml GATE-DIRECTORY-CONTRACT (pre-commit hook，已启用)
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 真源为 directory_contract.yaml + doc_type_vocabulary.yaml；DCR-001~007 全部已启用；只读校验不修改文件
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
  DCR-001: doc_type.allowed_directories contains file.directory (error)
  DCR-002: doc_type.forbidden_directories not contains file.directory (error)
  DCR-003: permanent zone file ttl == permanent             (error)
  DCR-004: temporary zone file ttl == task_bound            (warning)
  DCR-005: file extension in directory_extensions.allowed   (error)
  DCR-006: file extension not in directory_extensions.forbidden (error)
  DCR-007: root directory file in root_directory_whitelist  (error)

DCR-001/002 豁免区：docs/_working/（临时区）、docs/_archive/（归档区）、.runtime/（运行时归档区）、.trae/（IDE 工具区）、docs/01_policies_and_standards/templates/（模板区 TMP-EX-001）
DCR-001/002 真源：doc_type_vocabulary.yaml values[].allowed_directories/forbidden_directories

Modes:
  --staged              check git-staged files only (pre-commit use)
  --all-files           force full scan (ignore file args)
  --warn-only           print findings, never block (exit 0)
  (default)             scan all in-scope files, block on errors (exit 1)
  file args             incremental check (pre-commit pass_filenames=true)

Exit codes: 0=pass, 1=findings (error-severity violations), 2=script error
"""

from __future__ import annotations

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

    DCR-001/002 真源：doc_type 的 allowed_directories/forbidden_directories
    由 doc_type_vocabulary.yaml 单一定义，本函数读取后建立查找表。
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
    """
    if not rule or "allowed_exceptions" not in rule:
        return set()
    rel_dir_norm = _normalize_dir(rel_dir)
    exceptions: set[str] = set()
    for exc in rule["allowed_exceptions"]:
        subdir = exc["subdir"].rstrip("/") + "/"
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

    仅校验 .md 文件（有 frontmatter ttl 字段）。.yaml 文件的治理锚定 ttl 由
    check_frontmatter_metadata.py 校验，本脚本不重复。
    """
    rel_dir = str(Path(rel_path).parent).replace("\\", "/")
    zone_name, zone = find_zone(contract, rel_dir)
    if not zone or zone.get("default_ttl") is None:
        return []  # neutral zone（default_ttl=null）不校验 ttl
    if not rel_path.endswith(".md"):
        return []  # 仅 .md 有 frontmatter ttl；代码文件无 ttl 字段
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


def _file_matches_pattern(rel_path: str, pattern: str) -> bool:
    """检查文件路径是否匹配 allowed/forbidden_directories 模式。

    匹配规则：
    - pattern 以 / 结尾 → 目录前缀匹配（文件所在目录 startswith pattern）
    - pattern 不以 / 结尾 → 文件路径精确匹配（如 docs/registry_of_registries.yaml）
    """
    rel_posix = rel_path.replace("\\", "/")
    if pattern.endswith("/"):
        rel_dir = str(Path(rel_posix).parent).replace("\\", "/")
        rel_dir_norm = rel_dir + "/" if rel_dir != "." else "./"
        return rel_dir_norm.startswith(pattern)
    else:
        return rel_posix == pattern


def check_doc_type_directory(rel_path: str, contract: dict, vocab: dict) -> list[dict]:
    """DCR-001 + DCR-002: doc_type 的目录约束校验。

    DCR-001: file.doc_type.allowed_directories contains file.directory
             OR file.directory in temporary_zone (docs/_working/)
             OR file.directory in archive_zone (docs/_archive/)
    DCR-002: file.doc_type.forbidden_directories not contains file.directory

    仅校验有 frontmatter 的文件。doc_type 真源为 doc_type_vocabulary.yaml。
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

    if doc_type not in vocab:
        return []  # 未知 doc_type 由其他门禁负责

    doc_type_config = vocab[doc_type]
    rel_posix = rel_path.replace("\\", "/")
    rel_dir = str(Path(rel_posix).parent).replace("\\", "/")

    findings: list[dict] = []

    # DCR-001: allowed_directories 校验（豁免 _working/ 和 _archive/）
    is_exempt = any(rel_posix.startswith(prefix) for prefix in _DCR_EXEMPT_PREFIXES)
    if not is_exempt:
        allowed_dirs = doc_type_config.get("allowed_directories", [])
        if allowed_dirs:
            matched = any(_file_matches_pattern(rel_posix, p) for p in allowed_dirs)
            if not matched:
                findings.append({
                    "rule": "DCR-001",
                    "severity": "error",
                    "file": rel_path,
                    "detail": f"doc_type={doc_type} 文件目录 {rel_dir}/ 不在 allowed_directories {allowed_dirs} 内",
                })

    # DCR-002: forbidden_directories 校验
    forbidden_dirs = doc_type_config.get("forbidden_directories", [])
    if forbidden_dirs:
        matched = any(_file_matches_pattern(rel_posix, p) for p in forbidden_dirs)
        if matched:
            findings.append({
                "rule": "DCR-002",
                "severity": "error",
                "file": rel_path,
                "detail": f"doc_type={doc_type} 文件目录 {rel_dir}/ 在 forbidden_directories {forbidden_dirs} 内",
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
    return findings


# ════════════════════════════════════════════════════════════════════════════
# 全量扫描
# ════════════════════════════════════════════════════════════════════════════

def scan_all(contract: dict) -> list[str]:
    """扫描契约覆盖的所有目录，返回相对路径文件列表。

    扫描范围：
      - 根目录（仅一级文件，DCR-007）
      - directory_extensions 中所有 path
      - directory_zones 中所有 zone 的 paths
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
            # 根目录：只扫描一级文件（不递归）
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
