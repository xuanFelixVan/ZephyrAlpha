# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §registry
# [MODULE] zephyr.governance.capability_lookup
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] AI sessions (查询能力真源); future create-time gate (check_file_canonical)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] YAML 真源是规则数据；磁盘扫描结果不持久化（查询时实时算，避免同步成本）
# [MODIFY-GUARD] capability_canonical_file_registry.yaml (canonical 声明真源); governance/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises FileNotFoundError if YAML 真源缺失; returns empty list on scan errors
# [TESTS] tests/test_capability_lookup.py
# [A_module] module_id=MOD-GOV_capability_lookup | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
CapabilityLookup — 能力→真源文件反查注册表的查询 API + 扫描逻辑（合一）
================================================================================

解决"AI 不知道某功能已存在、真源在哪"的信息不可达问题。

设计原则（第一性原理）：
  1. 真源唯一：YAML（capability_canonical_file_registry.yaml）是规则数据真源，
     人工声明 canonical + aliases + duplicates。
  2. 责任唯一：本模块一个文件管扫描+查询+比对+CLI，不拆分扫描器脚本。
  3. 自动维护：CapabilityLookup() 初始化时自动扫磁盘头部，无需手工跑脚本。
  4. 无需同步：不持久化 @generated report，查询时实时算，避免第二数据源漂移。

对标：K8s Service（声明式 canonical）+ Endpoints 控制器（实时发现 pod）——
      Endpoints 不持久化为独立资源，是 Service 的实时投影。本模块同构。

用法：
    from zephyr.governance.capability_lookup import CapabilityLookup

    reg = CapabilityLookup()                  # 自动加载 YAML + 扫描磁盘
    reg.find("session handoff")               # 关键词搜索
    reg.get("rollback_executor")              # 按 capability_id 精确查
    reg.list_ssot_conflicts()                 # 列出同蓝图多实现冲突
    reg.check_file_canonical("src/zephyr/xxx.py")  # 反查某文件是哪个能力的 canonical

CLI:
    python -m zephyr.governance.capability_lookup --find "handoff"
    python -m zephyr.governance.capability_lookup --list-conflicts
    python -m zephyr.governance.capability_lookup --check-file src/zephyr/xxx.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------

def _find_repo_root() -> Path:
    """从本文件位置推导项目根目录（src/zephyr/governance/capability_lookup.py → 上溯）。"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "src" / "zephyr" / "__init__.py").exists():
            return parent
    # 兜底：本文件上溯 4 级（src/zephyr/governance/ → repo root）
    return Path(__file__).resolve().parents[3]


REPO_ROOT: Path = _find_repo_root()
REGISTRY_YAML: Path = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "capability_canonical_file_registry.yaml"
SCAN_ROOT: Path = REPO_ROOT / "src" / "zephyr"
HEADER_SCAN_LIMIT = 30  # 头部字段都在前 30 行，只读这么多省时间


# ---------------------------------------------------------------------------
# 头部正则（代码文件十一字段头部）
# ---------------------------------------------------------------------------

_RE_MODULE = re.compile(r"^#\s*\[MODULE\]\s*(.+?)\s*$")
_RE_BLUEPRINT = re.compile(r"^#\s*\[BLUEPRINT\]\s*(\S+)")
_RE_DOMAIN = re.compile(r"^#\s*\[DOMAIN\]\s*(\S+)")
_RE_MATURITY = re.compile(r"^#\s*\[MATURITY\]\s*(\S+)")
_RE_MODULE_ID = re.compile(r"module_id=([^\s|]+)")


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
class CapabilityEntry:
    """能力条目（从 YAML 真源加载，运行时补充磁盘状态）。"""
    capability_id: str
    name: str
    canonical_file: str
    module_id: str = ""
    blueprint_id: str = ""
    domain: str = ""
    maturity: str = ""
    status: str = "alive"
    aliases: list[str] = field(default_factory=list)
    description: str = ""
    duplicates: list[dict] = field(default_factory=list)
    removed_duplicates: list[dict] = field(default_factory=list)
    # 运行时补充字段（不来自 YAML）
    canonical_alive: bool = True
    pending_candidates: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# CapabilityLookup 主类
# ---------------------------------------------------------------------------

class CapabilityLookup:
    """能力→真源文件反查注册表查询 API。

    初始化时：
      1. 加载 YAML 真源（capability_canonical_file_registry.yaml）
      2. 扫描 src/zephyr/**/*.py 头部（前 30 行）
      3. 合并两者（reconcile）：标记 canonical_alive + 发现 pending_candidates

    查询时走内存缓存，不再次扫盘。session 内有效（AI session 生命周期内文件变化少）。
    """

    def __init__(
        self,
        yaml_path: Path | str | None = None,
        scan_root: Path | str | None = None,
        *,
        scan: bool = True,
    ) -> None:
        self._yaml_path: Path = Path(yaml_path) if yaml_path is not None else REGISTRY_YAML
        self._scan_root: Path = Path(scan_root) if scan_root is not None else SCAN_ROOT
        # canonical_file 在 YAML 中格式为 src/zephyr/xxx，scan_root 是 src/zephyr，
        # 所以 canonical_file 相对的基准是 scan_root.parent.parent（项目根或 tmp_path）。
        self._base_root: Path = self._scan_root.parent.parent
        self._capabilities: list[CapabilityEntry] = []
        self._disk_headers: dict[str, HeaderInfo] = {}
        self._loaded = False
        # YAML 真源必须加载（与 scan 解耦——scan=False 只跳过磁盘扫描，不跳过 YAML）
        self._capabilities = self._load_yaml()
        if scan:
            self._disk_headers = self._scan_disk_headers()
            self._reconcile()
        self._loaded = True

    # ---- 加载 + 扫描 ----

    def _load_and_scan(self) -> None:
        """reload() 用：重读 YAML + 重扫磁盘。"""
        self._capabilities = self._load_yaml()
        self._disk_headers = self._scan_disk_headers()
        self._reconcile()
        self._loaded = True

    def reload(self) -> None:
        """重新加载 YAML + 重扫磁盘（YAML 更新后调用）。"""
        self._load_and_scan()

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
                name=raw.get("name", ""),
                canonical_file=raw["canonical_file"],
                module_id=raw.get("module_id", ""),
                blueprint_id=raw.get("blueprint_id", ""),
                domain=raw.get("domain", ""),
                maturity=raw.get("maturity", ""),
                status=raw.get("status", "alive"),
                aliases=list(raw.get("aliases", []) or []),
                description=raw.get("description", ""),
                duplicates=list(raw.get("duplicates", []) or []),
                removed_duplicates=list(raw.get("removed_duplicates", []) or []),
            ))
        return caps

    def _scan_disk_headers(self) -> dict[str, HeaderInfo]:
        """扫描 scan_root/**/*.py 头部，返回 path → HeaderInfo 映射。

        path 用 _base_root 相对路径（与 YAML 中 canonical_file 格式 src/zephyr/xxx 对齐）。
        """
        result: dict[str, HeaderInfo] = {}
        if not self._scan_root.exists():
            return result
        for py in self._scan_root.rglob("*.py"):
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
        """解析单个 .py 文件的头部（前 HEADER_SCAN_LIMIT 行）。"""
        info = HeaderInfo(path=rel)
        try:
            with py.open("r", encoding="utf-8") as f:
                lines = [f.readline() for _ in range(HEADER_SCAN_LIMIT)]
        except (OSError, UnicodeDecodeError):
            return info

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

    def _reconcile(self) -> None:
        """合并 YAML 真源与磁盘扫描结果：标记 canonical_alive + 发现 pending_candidates。"""
        for cap in self._capabilities:
            # 1. 检查 canonical 文件是否存在于磁盘
            cap.canonical_alive = (
                cap.canonical_file in self._disk_headers
                or (self._base_root / cap.canonical_file).exists()
            )
            # 2. 补充磁盘头部信息（YAML 没填的字段从磁盘拿）
            disk = self._disk_headers.get(cap.canonical_file)
            if disk:
                if not cap.module_id:
                    cap.module_id = disk.module_id
                if not cap.blueprint_id:
                    cap.blueprint_id = disk.blueprint_id
                if not cap.domain:
                    cap.domain = disk.domain
                if not cap.maturity:
                    cap.maturity = disk.maturity
            # 3. 发现 pending candidates：磁盘上有文件声明了与 canonical 相同的
            #    module_id 或 module_path，但不在 YAML 声明里——确凿的重复信号。
            #    注意：不使用 aliases 子串匹配（太宽泛，会命中大量无关文件产生噪音）。
            #    aliases 仅用于 find() 查询，不用于磁盘 candidate 发现。
            declared_paths = {cap.canonical_file}
            declared_paths.update(d.get("path", "") for d in cap.duplicates)
            canonical_module_id = (disk.module_id if disk else "") or cap.module_id
            canonical_module_path = disk.module_path if disk else ""
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
                        "note": "磁盘有但 YAML 未声明——确凿重复信号（同 module_id 或同 module_path），需人工裁定",
                    })

    # ---- 查询 API ----

    def find(self, query: str) -> list[dict]:
        """关键词搜索：匹配 capability_id / name / aliases / description / canonical_file（大小写不敏感）。"""
        q = query.lower()
        results: list[dict] = []
        for cap in self._capabilities:
            haystacks = [
                cap.capability_id, cap.name, cap.description,
                cap.canonical_file, cap.module_id,
            ] + list(cap.aliases)
            haystack = " ".join(haystacks).lower()
            if q in haystack:
                results.append(self._entry_to_dict(cap))
        return results

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
        不依赖 YAML registry——YAML 是人工裁定的补充信息，不是门禁的必需依赖。

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
            "scan_root": str(self._scan_root),
        }

    @staticmethod
    def _entry_to_dict(cap: CapabilityEntry) -> dict:
        return {
            "capability_id": cap.capability_id,
            "name": cap.name,
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
        }


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _normalize_path(p: str) -> str:
    """路径标准化：反斜杠→正斜杠，去掉前导 ./ """
    return p.replace("\\", "/").lstrip("./")


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
    args = parser.parse_args(argv)

    try:
        reg = CapabilityLookup(scan=not args.no_scan)
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
