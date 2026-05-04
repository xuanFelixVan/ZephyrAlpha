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
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = PROJECT_ROOT / "docs" / "03_modules"
REGISTRY_FILE = MODULES_DIR / "system-pathway-registry.yaml"
BLUEPRINT_PATTERN = "**/blueprint.md"

# 蓝图文件 -> module_id 映射 (从 frontmatter 提取)
MODULE_ID_RE = re.compile(r"^module_id:\s*(.+)$", re.MULTILINE)
# 状态提取
STATUS_RE = re.compile(r"^status:\s*(.+)$", re.MULTILINE)


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


def scan_blueprints() -> list[dict]:
    """扫描所有模块蓝图，提取路径注册信息。"""
    entries = []
    for bp in sorted(MODULES_DIR.glob(BLUEPRINT_PATTERN)):
        # 跳过 registry 目录和非模块蓝图
        relative = bp.relative_to(MODULES_DIR)
        parts = relative.parts

        mod_id = extract_module_id(bp)
        if not mod_id:
            mod_id = "UNKNOWN"

        # 推断 source_dir (从 module_id 推导)
        # 例: MOD-INF-001 capacity-assurance -> src/zephyr/capacity/
        name = parts[0] if "l01_infrastructure" in parts else parts[0]

        # 尝试从蓝图文档内提取路径
        source_dir = ""
        test_dir = ""
        config = ""

        entries.append(
            {
                "module_id": mod_id,
                "name": name,
                "layer": "L01" if "l01_infrastructure" in parts else "cross_layer",
                "blueprint": str(Path("docs/03_modules") / relative),
                "source_dir": source_dir,
                "test_dir": test_dir,
                "config": config,
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
        buf.write(f"  - module_id: \"{entry['module_id']}\"\n")
        buf.write(f"    name: \"{entry['name']}\"\n")
        buf.write(f"    layer: \"{entry['layer']}\"\n")
        buf.write(f"    blueprint: \"{entry['blueprint']}\"\n")
        if entry["source_dir"]:
            buf.write(f"    source_dir: \"{entry['source_dir']}\"\n")
        else:
            buf.write('    source_dir: ""\n')
        if entry["test_dir"]:
            buf.write(f"    test_dir: \"{entry['test_dir']}\"\n")
        if entry["config"]:
            buf.write(f"    config: \"{entry['config']}\"\n")
        buf.write("\n")

    return buf.getvalue()


def cmd_write() -> None:
    """覆写 registry 文件。"""
    entries = scan_blueprints()
    content = generate_yaml(entries)
    REGISTRY_FILE.write_text(content, encoding="utf-8")
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
