# [BLUEPRINT] MOD-INF-005 | scripts/generate_pathway_registry.py | §
# [MODULE] scripts.generate_pathway_registry
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.__init__
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
# [TTL] permanent
#!/usr/bin/env python3
"""从所有 MOD 蓝图的 §路径索引 章节自动生成 system-pathway-registry.yaml。

对标: Google Monorepo 自动索引——不维护手工清单，由工具从各模块蓝图中提取。

用法:
    python scripts/generate_pathway_registry.py            # 生成 YAML (stdout)
    python scripts/generate_pathway_registry.py --write    # 覆写 registry 文件
    python scripts/generate_pathway_registry.py --check    # CI 模式: 比对差异，不一致时报红

CI 集成:
    .github/workflows/governance.yml:
      - name: Validate pathway registry
        run: python scripts/generate_pathway_registry.py --check
"""

import argparse
import os
import re
import sys
from pathlib import Path

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parent / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT  # noqa: E402
from zephyr.governance.rule_patterns import MODULE_ID_RE  # noqa: E402  # SSoT 治本 2026-07-02 (ARCH-033 Phase 7)

PROJECT_ROOT = REPO_ROOT
MODULES_DIR = PROJECT_ROOT / "docs" / "03_modules"
REGISTRY_FILE = MODULES_DIR / "system-pathway-registry.yaml"
BLUEPRINT_PATTERN = "**/blueprint.md"

# MODULE_ID_RE 已迁移到 zephyr.governance.rule_patterns（SSoT 治本 2026-07-02, ARCH-033 Phase 7）
# 状态提取
STATUS_RE = re.compile(r"^status:\s*(.+)$", re.MULTILINE)
PATH_INDEX_MARKER = "已实现代码完整路径索引"
PATH_ROW_RE = re.compile(r"\|\s*`([^`]+)`\s*\|")


def extract_module_id(blueprint_path: Path) -> str | None:
    """从 blueprint.md 的 YAML frontmatter 中提取 module_id。"""
    text = blueprint_path.read_text(encoding="utf-8")
    m = MODULE_ID_RE.search(text)
    if m:
        return m.group(1).strip()
    return None


def extract_status(blueprint_path: Path) -> str | None:
    """提取蓝图 doc status。"""
    text = blueprint_path.read_text(encoding="utf-8")
    m = STATUS_RE.search(text)
    if m:
        return m.group(1).strip()
    return None


def extract_path_index_tables(text: str) -> dict[str, list[str]]:
    """从蓝图「已实现代码完整路径索引」章节解析表格中的反引号路径。"""
    pos = text.find(PATH_INDEX_MARKER)
    if pos < 0:
        return {"source_paths": [], "test_paths": [], "config_paths": []}
    chunk = text[pos:]
    end = chunk.find("路径索引使用指南")
    if end >= 0:
        chunk = chunk[:end]
    src: list[str] = []
    tst: list[str] = []
    cfg: list[str] = []
    bucket: str | None = None
    for raw in chunk.splitlines():
        line = raw.strip()
        if line.startswith("###"):
            if "源码" in line:
                bucket = "source"
            elif "测试" in line:
                bucket = "test"
            elif "配置" in line:
                bucket = "config"
            else:
                bucket = None
            continue
        m = PATH_ROW_RE.search(raw)
        if not m or not bucket:
            continue
        p = m.group(1).strip()
        if bucket == "source":
            src.append(p)
        elif bucket == "test":
            tst.append(p)
        else:
            cfg.append(p)
    return {"source_paths": src, "test_paths": tst, "config_paths": cfg}


def common_path_prefix(paths: list[str]) -> str:
    """返回路径列表的最长公共目录前缀（posix，带尾斜杠）。"""
    norm = [
        p.strip().replace("\\", "/") for p in paths if p and p.startswith(("src/", "tests/", "config/", "scripts/"))
    ]
    if not norm:
        return ""
    comps = [p.split("/") for p in norm]
    common = comps[0]
    for c in comps[1:]:
        upper = min(len(common), len(c))
        i = 0
        while i < upper and common[i] == c[i]:
            i += 1
        common = common[:i]
    out = "/".join(common)
    return f"{out}/" if out else ""


def scan_blueprints() -> list[dict]:
    """扫描所有模块蓝图，提取路径注册信息。"""
    entries = []
    for bp in sorted(MODULES_DIR.glob(BLUEPRINT_PATTERN)):
        relative = bp.relative_to(MODULES_DIR)
        parts = relative.parts

        mod_id = extract_module_id(bp)
        if not mod_id:
            mod_id = "UNKNOWN"

        name = parts[0] if "infrastructure_runtime_integration" in parts else parts[0]

        text = bp.read_text(encoding="utf-8", errors="replace")
        tables = extract_path_index_tables(text)
        source_dir = common_path_prefix(tables["source_paths"]).rstrip("/")
        test_dir = common_path_prefix(tables["test_paths"]).rstrip("/")
        cp = tables["config_paths"]
        if len(cp) == 1:
            config = cp[0]
        else:
            config = common_path_prefix(cp).rstrip("/")

        entries.append(
            {
                "module_id": mod_id,
                "name": name,
                "layer": "L0_infrastructure" if "infrastructure_runtime_integration" in parts else "L1_foundation",
                "blueprint": str(Path("docs/03_modules") / relative),
                "source_dir": source_dir,
                "test_dir": test_dir,
                "config": config,
                "path_index_counts": {
                    "source": len(tables["source_paths"]),
                    "test": len(tables["test_paths"]),
                    "config": len(tables["config_paths"]),
                },
            }
        )

    return entries


def generate_yaml(entries: list[dict]) -> str:
    """生成 system-pathway-registry.yaml 内容。"""
    header = (
        "# ============================================================================\n"
        "# ZephyrAlpha 全系统路径地图 — 自动生成\n"
        "# 生成工具: scripts/generate_pathway_registry.py\n"
        "# 手工修改将被下一次自动生成覆盖。\n"
        "# ============================================================================\n\n"
    )

    doc = {
        "registry": {
            "version": "1.0.0",
            "generation": "auto",
            "auto_generated_by": "scripts/generate_pathway_registry.py",
            "total_modules": len(entries),
        },
        "pathways": entries,
    }

    import io

    buf = io.StringIO()
    buf.write(header)

    # 手写 YAML 以保持可读性，不用 yaml.dump
    buf.write("registry:\n")
    buf.write('  version: "1.0.0"\n')
    buf.write('  generation: "auto"\n')
    buf.write('  auto_generated_by: "scripts/generate_pathway_registry.py"\n')
    buf.write(f"  total_modules: {len(entries)}\n")
    buf.write("\npathways:\n")

    for entry in entries:
        buf.write(f'  - module_id: "{entry["module_id"]}"\n')
        buf.write(f'    name: "{entry["name"]}"\n')
        buf.write(f'    layer: "{entry["layer"]}"\n')
        buf.write(f'    blueprint: "{entry["blueprint"]}"\n')
        if entry["source_dir"]:
            buf.write(f'    source_dir: "{entry["source_dir"]}"\n')
        else:
            buf.write('    source_dir: ""\n')
        if entry["test_dir"]:
            buf.write(f'    test_dir: "{entry["test_dir"]}"\n')
        if entry["config"]:
            buf.write(f'    config: "{entry["config"]}"\n')
        counts = entry.get("path_index_counts") or {}
        if any(counts.values()):
            buf.write("    path_index_counts:\n")
            buf.write(f"      source: {counts.get('source', 0)}\n")
            buf.write(f"      test: {counts.get('test', 0)}\n")
            buf.write(f"      config: {counts.get('config', 0)}\n")
        buf.write("\n")

    return buf.getvalue()


def cmd_write() -> None:
    """覆写 registry 文件。"""
    entries = scan_blueprints()
    content = generate_yaml(entries)
    tmp_path = f"{REGISTRY_FILE}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(content, encoding="utf-8")
        os.replace(tmp_path, REGISTRY_FILE)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    print(f"[OK] Written {len(entries)} modules to {REGISTRY_FILE}")


def cmd_check() -> None:
    """CI 模式：比对当前 registry 和自动生成结果，不一致时报错。"""
    entries = scan_blueprints()
    generated = generate_yaml(entries)
    current = REGISTRY_FILE.read_text(encoding="utf-8")

    if current.strip() != generated.strip():
        print("[FAIL] system-pathway-registry.yaml is OUT OF SYNC.")
        print("       Run: python scripts/generate_pathway_registry.py --write")
        sys.exit(1)
    else:
        print("[OK] system-pathway-registry.yaml is in sync.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate system-pathway-registry.yaml")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true", help="Overwrite registry file")
    group.add_argument("--check", action="store_true", help="CI mode: exit 1 if mismatch")

    args = parser.parse_args()

    if args.check:
        cmd_check()
    elif args.write:
        cmd_write()
    else:
        entries = scan_blueprints()
        print(generate_yaml(entries))


if __name__ == "__main__":
    main()
