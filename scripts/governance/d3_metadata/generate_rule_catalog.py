# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/generate_rule_catalog.py | §
# [MODULE] scripts.governance.d3_metadata.generate_rule_catalog
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
# [CONSUMERS]
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 输出文件名必须为 rule_catalog_registry.yaml（snake_case 硬约束）；generate_catalog 幂等——内容零变更跳过写入（2026-09-13 Owner 指令，reconciler 周期触发防时间戳噪音）；保育语义——已存在但非本生成器输入源产出的 files 条目透传保留，生成器只更新它管的条目、不删它不管的（2026-09-16 #11.4-W2，防工具 YAML 侧合法登记被再生成剪除）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] scan_dir 不存在 → stderr 警告并返回空列表
# [TESTS] tests/governance/d3_metadata/test_generate_rule_catalog_idempotent.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
#!/usr/bin/env python3
"""Scan docs/01_policies_and_standards and emit _registry/catalogs/rule_catalog_registry.yaml.

Parses Markdown/YAML frontmatter (and YAML comment headers where applicable).

CLI::

    python generate_rule_catalog.py [--scan-dir DIR] [--output FILE]
"""

# Governance script manifest (YAML fragment for tooling/consumers; not evaluated as code).
__manifest__ = """
args: []
description: >
  Scan policy tree; aggregate frontmatter into rule_catalog_registry.yaml.
  Aligns with static-manifest SSOT for governance scripts (section 6.16-style workflow).
dimensions:
  - D3
priority: P2
timeout_seconds: 180
warn_only: false
"""

import argparse
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

# ── _shared 模块 import bootstrap（一次性极简 bootstrap 找 _shared；REPO_ROOT 真源
#    为 zephyr.shared.io.paths，经 _shared.constants re-export，符合 project_memory 铁律）──
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import (
    EXCLUDE_DIRS,
    EXIT_FINDINGS,
    EXIT_PASS,
    GOV_DOCS_DIR,
    REPO_ROOT,
    SCAN_EXTENSIONS_MD_YAML,
)
from _shared.encoding import ensure_utf8_stdout  # noqa: E402
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from _shared.frontmatter import parse_frontmatter  # noqa: E402
from _shared.walk import iter_files  # noqa: E402

ensure_utf8_stdout()


def extract_yaml_header(content: str) -> dict | None:
    """Extract header fields from a .yaml file.

    #ARCH-024 治本修复：原逻辑依赖 schema_version/doc_type 关键字判断是否
    调用 yaml.safe_load，导致 48 个无此字段的 trae_*.yaml 规则文件被跳过
    （只扫到 12/60）。修复：始终尝试 yaml.safe_load，注释头解析作为回退。
    """
    fields: dict = {}
    # 1. 始终尝试 yaml.safe_load（#ARCH-024 修复：不依赖关键字判断）
    try:
        full_yaml = yaml.safe_load(content)
        if isinstance(full_yaml, dict):
            fields.update(
                {
                    k: v
                    for k, v in full_yaml.items()
                    if k
                    in (
                        "module_id",
                        "doc_type",
                        "status",
                        "version",
                        "title",
                        "rule_form",
                        "scope",
                        "stability",
                        "layer",
                        "owner",
                        "ttl",
                        "superseded_by",
                        # 以下字段用于派生 _index.yaml 独有的规则元数据
                        # （#ARCH-024 治本：catalog 扩展为唯一规则索引）
                        "severity",
                        "tags",
                        "aliases",
                        "sections",
                    )
                }
            )
    except yaml.YAMLError:
        pass
    # 2. 回退：注释头解析（覆盖纯注释头文件，如脚本头部 BLUEPRINT 注释）
    if not fields:
        for line in content.split("\n"):
            if not line.startswith("#") and line.strip() != "":
                break
            if line.startswith("#"):
                m = re.match(r"#\s*(\w+)[\uff1a:]\s*(.+)", line)
                if m:
                    fields[m.group(1)] = m.group(2).strip()
    return fields if fields else None


def _extract_tier_from_tags(tags) -> str:
    """从 tags 列表中提取 tier（L0/L1/L2），无则返回空串。

    tier 真源为规则文件 frontmatter 的 tags 字段中的 Lx 元素（#ARCH-024 治本）。
    """
    if not isinstance(tags, list):
        return ""
    for tag in tags:
        if isinstance(tag, str) and re.match(r"^L[0-2]$", tag):
            return tag
    return ""


def _count_sections(sections) -> int:
    """计算 sections 字典的 section 数量。"""
    if isinstance(sections, dict):
        return len(sections)
    return EXIT_PASS


def _load_unmanaged_entries(output: Path, managed_paths: set[str]) -> list[dict]:
    """读取既有输出中非本生成器输入源产出的条目（保育语义透传，#11.4-W2）。

    背景（2026-09-16 02:58:54 write_audit 取证）：工具合法登记的条目
    （add_module_translation / batch_creation_tokens 等 YAML 侧通道写入）不在
    生成器扫描输入里，原实现整体替换 files 列表会将其剪除、再被 reconciler
    自动提交固化为 HEAD——与"静态清单禁手工维护"红线的合法通道冲突。
    保育语义：生成器只管理自身输入源（扫描 frontmatter）产出的条目；对既有
    输出中 path 不在本次输入里的条目原样保留（不修改字段、不重排序、除按
    path 去重外不做任何清洗）。同 path 冲突时以本次扫描条目为准（更新语义）。
    既有文件读不出/解析失败/结构异常 → 返回空列表（不阻塞再生成为主）。
    """
    if not output.exists():
        return []
    try:
        old = yaml.safe_load(output.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return []
    old_files = old.get("files") if isinstance(old, dict) else None
    if not isinstance(old_files, list):
        return []
    unmanaged: list[dict] = []
    seen: set[str] = set()
    for item in old_files:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        if not isinstance(path, str) or not path or path in managed_paths or path in seen:
            continue
        seen.add(path)
        unmanaged.append(item)
    return unmanaged


def scan_directory(scan_dir: str, repo_root: Path) -> list[dict]:
    """Scan directory for .md and .yaml files, extract frontmatter."""
    results: list[dict] = []
    scan_path = Path(scan_dir).resolve()
    repo_root = repo_root.resolve()

    if not scan_path.exists():
        print(f"ERROR: Scan directory does not exist: {scan_dir}", file=sys.stderr)
        return results

    for fpath in iter_files(
        scan_path, extensions=SCAN_EXTENSIONS_MD_YAML, exclude_dirs=EXCLUDE_DIRS | {".audit_cache"}
    ):
        fname = fpath.name
        try:
            rel_path = str(fpath.resolve().relative_to(repo_root)).replace("\\", "/")
        except ValueError:
            try:
                rel_path = str(fpath.resolve().relative_to(scan_path)).replace("\\", "/")
            except ValueError:
                rel_path = str(fpath.resolve())

        try:
            raw = fpath.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError) as e:
            print(f"WARNING: Cannot read {fpath}: {e}", file=sys.stderr)
            continue

        if fname.endswith(".md"):
            fm = parse_frontmatter(raw)  # Bug 7 fix: returns dict|None not tuple, [0] caused KeyError
        else:
            fm = extract_yaml_header(raw)

        if fm is None:
            continue

        entry = {
            "path": rel_path,
            "module_id": fm.get("module_id", ""),
            "title": fm.get("title", ""),
            "doc_type": fm.get("doc_type", ""),
            "status": str(fm.get("status", "")).lower(),
            "version": str(fm.get("version", "")),
            "rule_form": fm.get("rule_form", ""),
            "scope": fm.get("scope", ""),
            "stability": fm.get("stability", ""),
            "layer": fm.get("layer", ""),
            "superseded_by": fm.get("superseded_by", ""),
            # 以下4字段原由 rules/_index.yaml 手工维护（#ARCH-024 治本：改为自动派生）
            "severity": fm.get("severity", ""),
            "tier": _extract_tier_from_tags(fm.get("tags", [])),
            "aliases": fm.get("aliases", []),
            "section_count": _count_sections(fm.get("sections", {})),
        }
        results.append(entry)

    return results


def generate_catalog(entries: list[dict], output_path: str) -> None:
    """Write rule_catalog_registry.yaml（原子写入：tmp + os.replace；内容零变更跳过）.

    保育语义（#11.4-W2）：非本生成器输入源产出的既有条目透传保留
    （见 _load_unmanaged_entries）——生成器只更新它管的条目，不删它不管的。
    """
    gen_ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # 保育合并（#11.4-W2）：管辖条目（本次扫描输入）在前，被保育条目（既有
    # 输出中非本次输入产出）按原顺序追加在后。确定性合并 → 幂等跳过仍成立。
    managed_paths = {e["path"] for e in entries if isinstance(e.get("path"), str)}
    merged_entries = list(entries) + _load_unmanaged_entries(output, managed_paths)

    # 派生 tier_distribution 和 total_rules（仅统计有 tier 的规则文件；基于合并
    # 后列表——计数字段必须描述落盘 files 列表本身，防表内自相矛盾）
    # #ARCH-024 治本：原由 rules/_index.yaml 手工维护，现从条目自动派生
    tier_distribution: dict[str, int] = {}
    total_rules = 0
    for e in merged_entries:
        tier = e.get("tier", "")
        if tier:
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            total_rules += 1

    catalog = {
        "schema_version": "1.0.0",
        "module_id": "PS-REG-018",
        "ttl": "permanent",
        "doc_type": "register",
        # title 含「唯一真源(SSoT)」声明：让新AI第一眼识别这是规则索引真源
        # （向内收4原则之"新AI可发现性"——无歧义标记真源性质）
        "title": "规则路径目录（唯一真源 SSoT）",
        "status": "active",
        "generated_at": gen_ts,
        "generated_by": "scripts/governance/d3_metadata/generate_rule_catalog.py",
        # maintenance 字段治本（2026-06-29）：声明 auto 让 generate_registry_master_index.py
        # 正确标记本表为自动维护——原缺省填 manual 是标记滞后根因（registry_master_index L167 误标 manual）
        "maintenance": "auto",
        "total_files": len(merged_entries),
        "total_rules": total_rules,
        "tier_distribution": tier_distribution,
        "files": merged_entries,
    }

    # 幂等跳过（2026-09-13 Owner 指令"内容没变就不刷时间戳"）：本生成器被
    # reconciler 周期触发（实测约 12min/次），原实现每次必刷 generated_at=
    # 工作区永久漂移噪音（08:59→09:12 零内容变更实证，watchdog 反复收敛）。
    # 判定法：用旧时间戳重渲染（与历史写入同源 yaml.dump 参数）→ 与现文件
    # 逐字节一致=零变更，跳过写入（文件 mtime/git 状态全不动）；不一致=真内容
    # 变更，落盘并刷新时间戳。首次遇到渲染格式漂移（生成器代码曾改版）会重写
    # 一次后重新进入稳态——自愈，无需迁移逻辑。
    if output.exists():
        try:
            old_text = output.read_text(encoding="utf-8")
            old_ts = (yaml.safe_load(old_text) or {}).get("generated_at")
        except yaml.YAMLError:
            old_ts = None
        if old_ts:
            same_catalog = dict(catalog)
            same_catalog["generated_at"] = old_ts
            if (
                yaml.dump(
                    same_catalog,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )
                == old_text
            ):
                print(
                    f"Catalog unchanged ({len(merged_entries)} entries), skip rewrite (idempotent)",
                    file=sys.stderr,
                )
                return

    atomic_write_safe(
        output,
        yaml.dump(catalog, allow_unicode=True, default_flow_style=False, sort_keys=False),
    )
    print(f"Generated catalog with {len(merged_entries)} entries -> {output_path}", file=sys.stderr)


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="Generate rule catalog from frontmatter")
    parser.add_argument(
        "--scan-dir",
        default=str(GOV_DOCS_DIR),
        help="Directory to scan",
    )
    parser.add_argument(
        "--output",
        default=str(GOV_DOCS_DIR / "_registry" / "catalogs" / "rule_catalog_registry.yaml"),
        help="Output YAML file",
    )
    args = parser.parse_args()

    print(f"Scanning: {args.scan_dir}", file=sys.stderr)
    entries = scan_directory(args.scan_dir, REPO_ROOT)
    print(f"Found {len(entries)} files with frontmatter", file=sys.stderr)

    generate_catalog(entries, args.output)

    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
