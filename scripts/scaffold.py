# [BLUEPRINT] MOD-INF-005 | scripts/scaffold.py | §
# [MODULE] scripts.scaffold
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d3_metadata.check_naming_convention; zephyr.infrastructure.__init__; zephyr.integration.mcp.__init__; zephyr.governance.__init__
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
"""scaffold.py — ZephyrAlpha 唯一创建入口（RULE-TWO 强制执行器）

所有新文件 MUST 通过本脚本创建，禁止直接用 IDE Write/SearchReplace 写入新文件。
找到重复 → 拒绝创建并告诉已有的是什么。
不注册 → 文件根本不存在（前门守卫）。

创建模式:
    module: src/zephyr/<package>/<name>.py → 更新 <package>/__init__.py
    script: scripts/<path>/<name>.py       → 更新 script_manifest.yaml
    gate:   src/zephyr/gov_enforcement/rule_enforcement/<name>.yaml   → 更新 _registry.yaml
    yaml:   <path>/<name>.yaml             → 通知资产盘点（kebab-case 强制）
    rule:   docs/.../rules/trae_XXX.yaml   → 自动分配 rule_id + 标准 frontmatter
    json:   <path>/<name>.json             → 通知资产盘点（kebab-case 强制）
    md:     <path>/<name>.md               → 通知资产盘点（kebab-case 强制）

用法:
    python scripts/scaffold.py module feedback-loop scheduler --desc "FLE 全链路调度器"
    python scripts/scaffold.py script governance/audit_registration --desc "孤儿注册检测"
    python scripts/scaffold.py gate g6_my_gate --title "My Gate" --category kms
    python scripts/scaffold.py yaml docs/01_policies/my-policy --desc "策略文档"
    python scripts/scaffold.py rule arch-new-rule --title "架构新规则" --scope arch_new_rule --layer compliance
    python scripts/scaffold.py json data/config/my-config --desc "配置文件"
    python scripts/scaffold.py md docs/guides/my-guide --desc "用户指南"

设计基线:
    RULE-TWO: 反孤儿功能——所有新产出必须可被系统发现和调用
    RULE-ONE: temp-file + atomic rename 写入
    对标的: K8s kubectl create / Rails scaffold generator / Angular CLI
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parent / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT as PROJECT_ROOT  # noqa: E402

# repo root 加入 sys.path 以便 from scripts.governance.d3_metadata... 生效
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.governance.d3_metadata.check_naming_convention import check_dir, check_file

# 5.154.11 修复: 声明 __all__, 明确公共API边界
# 注册表所述 line 90 __all__=[] 实为 MODULE_TEMPLATE 字符串内的模板内容, 非 scaffold.py 本身
# 此处为 scaffold.py 本体的 __all__
__all__ = [
    "MODULE_TEMPLATE",
    "SCRIPT_TEMPLATE",
    "ScaffoldEngine",
    "ScaffoldError",
    "main",
]

# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------
SRC_ZEPHYR = PROJECT_ROOT / "src" / "zephyr"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
GATES_DIR = SRC_ZEPHYR / "governance" / "rule_enforcement"
SCRIPT_MANIFEST = SCRIPTS_DIR / "script_manifest.yaml"
GATE_REGISTRY = GATES_DIR / "_registry.yaml"
RULES_DIR = PROJECT_ROOT / "docs" / "01_policies_and_standards" / "rules"
CAPABILITY_REGISTRY = PROJECT_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "capability_canonical_file_registry.yaml"
LAYER_VOCABULARY = PROJECT_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies" / "layer_vocabulary.yaml"


def _load_valid_layers() -> frozenset[str]:
    """从 layer_vocabulary.yaml 动态加载合法架构层名（SSoT）。

    layer_vocabulary.yaml 是 layer 字段的唯一真源（16 个架构层名），
    禁止在代码中硬编码 valid_layers 集合（ARCH-021）。
    """
    try:
        raw = yaml.safe_load(LAYER_VOCABULARY.read_text(encoding="utf-8")) or {}
        values = raw.get("values", []) or []
        return frozenset(str(v.get("value")) for v in values if v.get("value"))
    except (OSError, yaml.YAMLError):
        # 容错：词表不可读时返回空集，由调用方 layer 校验阻断非法值
        return frozenset()

# ---------------------------------------------------------------------------
# 规则主题前缀（ARCH-037，按文件名定位的命名约定）
# ---------------------------------------------------------------------------
# 多段主题前缀无法机械拆分，显式声明；新增多段主题时更新此处。
# 单段主题前缀由 _derive_rule_theme_prefixes() 从现有文件名自动派生。
_MULTI_SEGMENT_THEMES = frozenset({
    "anti_hallucination", "anti_orphan", "meta_rule", "domain_policy",
    "cross_blueprint", "file_operation",
})


def _derive_rule_theme_prefixes() -> frozenset[str]:
    """从现有规则文件名派生主题前缀集合（SSoT: rules/ 下现有文件名）。

    文件名格式 trae_NNN_<theme>_<desc>.yaml，提取 <theme> 段。
    多段主题（如 anti_hallucination）优先匹配 _MULTI_SEGMENT_THEMES，
    其余取第一段。新增规则后前缀集合自动更新，无需手动维护前缀列表。
    """
    prefixes: set[str] = set()
    for f in RULES_DIR.glob("trae_[0-9][0-9][0-9]_*.yaml"):
        parts = f.stem.split("_", 2)  # [trae, NNN, <rest>]
        if len(parts) < 3 or not parts[2]:
            continue
        rest = parts[2]
        matched = next(
            (ms for ms in _MULTI_SEGMENT_THEMES if rest == ms or rest.startswith(ms + "_")),
            None,
        )
        if matched:
            prefixes.add(matched)
        else:
            first = rest.split("_", 1)[0]
            if first:
                prefixes.add(first)
    return frozenset(prefixes)


# ---------------------------------------------------------------------------
# 模块空壳模板
# ---------------------------------------------------------------------------
MODULE_TEMPLATE = '''"""{description}"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

__all__: list[str] = []


def main() -> None:
    """入口——待实现。"""
    pass


if __name__ == "__main__":
    main()
'''

SCRIPT_TEMPLATE = '''"""{description}"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def main() -> None:
    """入口——待实现。"""
    pass


if __name__ == "__main__":
    main()
'''

GATE_TEMPLATE = """# {gate_id} — {title}
# category: {category}
# created: {created_at}
# scaffold generated — fill in rules below

schema_version: "1.0"
gate_id: "{gate_id}"
title: "{title}"
category: "{category}"
status: active
scope: global
execution_plane: warm

checks: []
"""

YAML_TEMPLATE = """# [BLUEPRINT] {blueprint_id} | {file_path} |
# [MODULE] {module_path}
# [INVARIANTS]
# [MODIFY-GUARD]
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]

# {description}
"""

RULE_TEMPLATE = """rule_id: {rule_id}
title: {title}
version: '1.0.0'
layer: {layer}
module_id: {rule_id}
depends_on: []
tags:
- TRAE
- {scope}
- {layer}
stability: {stability}
safety_level: {safety_level}
ai_autonomy: {ai_autonomy}
aliases: []
severity: {severity}
scope: {scope}
domain: TRAE
triggers: []
sections: {{}}
references:
  rule_ids: []
  scripts: []
  modules: []
  blueprints: []
enforcement:
  type: doc
  executors: []
  bypass_allowed: false
metadata:
  change_policy: {stability}
  impact_level: {safety_level}
  modification_permission: {ai_autonomy}
  superseded_by: null
provenance:
  extracted_at: '{timestamp}'
  extracted_by: {session_id}
"""

JSON_TEMPLATE = """{{
  "_meta": {{
    "blueprint": "",
    "module": "",
    "stability": "evolving",
    "safety": "L",
    "ai_autonomy": "ai_modifiable",
    "created_at": "{created_at}",
    "description": "{description}"
  }}
}}
"""

MD_TEMPLATE = """# [BLUEPRINT] | {file_path} |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

{description}
"""


# ===================================================================
# 核心引擎
# ===================================================================


class ScaffoldError(Exception):
    """脚手架阻断——创建失败（重复/冲突）。"""


class ScaffoldEngine:
    """创建→查重→注册 三步原子引擎。"""

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.actions: list[str] = []

    # ------------------------------------------------------------------
    # 入口
    # ------------------------------------------------------------------

    def create_module(
        self,
        package: str,
        name: str,
        description: str = "",
        domain: str = "",
        subdomain: str = "",
    ) -> Path:
        """在 src/zephyr/<package>/<name>.py 创建模块，注册到 __init__.py。"""
        package_dir = SRC_ZEPHYR / package
        file_path = package_dir / f"{name}.py"
        class_name = _to_class_name(name)
        init_py = package_dir / "__init__.py"

        # ── 检查 1: 目录存在 ──
        if not package_dir.is_dir():
            raise ScaffoldError(f"Package '{package}' 不存在: {package_dir}\n可用包: {_list_packages()}")

        # ── 检查 2: 文件冲突 ──
        if file_path.exists():
            raise ScaffoldError(f"文件已存在: {file_path}\n如果是功能重复，请复用已有文件而非新建。")

        # ── 检查 3: 功能重复 ──
        _check_duplicate_functionality(
            name, description, domain, subdomain,
            expected_module_path=f"zephyr.{package}.{name}",
        )

        # ── 检查 4: __init__.py 中无重复 ──
        if init_py.exists():
            existing_content = init_py.read_text(encoding="utf-8")
            if class_name in existing_content or name in existing_content:
                raise ScaffoldError(f"'{class_name}' / '{name}' 已在 {init_py} 中被引用。\n确认不是重复创建。")

        # ── 检查 5: 命名规范 ──
        _check_naming(str(file_path), str(package_dir))

        # ── 执行创建 ──
        content = MODULE_TEMPLATE.format(description=description or f"{class_name} 模块")
        _atomic_write(file_path, content, self.dry_run, self.actions)

        # ── 注册到 __init__.py ──
        _register_to_init(init_py, class_name, name, package, self.dry_run, self.actions)

        # ── 通知资产盘点系统（MOD-INF-026）──
        _notify_asset_inventory(str(file_path), "module", self.dry_run)

        # ── P0-5: 自动登记 creation_token（create_guard 闭环）──
        _register_creation_token(str(file_path), name, self.dry_run)

        # ── 同步蓝图 §0.1 文件清单（防漂移）──
        _sync_blueprint_file_list(package, name, self.dry_run)

        print(f"\n  CREATED  {file_path}")
        print(f"  REGISTERED  {init_py}  (export '{class_name}')")
        print(f"  ACTION:  from zephyr.{package} import {class_name}")
        _remind_sys_master_dispatch(package, name, description)
        _remind_path_tree_refresh()
        return file_path

    def create_script(
        self,
        rel_path: str,
        description: str = "",
        domain: str = "",
        subdomain: str = "",
        force_override: bool = False,
    ) -> Path:
        """在 scripts/<rel_path>.py 创建脚本并注册到 script_manifest.yaml。"""
        file_path = SCRIPTS_DIR / f"{rel_path}.py"

        # ── 检查 1: 父目录存在 ──
        parent = file_path.parent
        if not parent.is_dir():
            os.makedirs(parent, exist_ok=True)

        # ── 检查 2: 文件冲突 ──
        if file_path.exists():
            raise ScaffoldError(f"文件已存在: {file_path}\n如果是功能重复，请复用已有文件而非新建。")

        # ── 检查 3: 功能重复 ──
        _check_duplicate_functionality(
            rel_path, description, domain, subdomain,
            force_override=force_override,
            expected_module_path=f"scripts.{rel_path.replace('/', '.')}",
        )

        # ── 检查 4: manifest 中无重复 ──
        _check_manifest_duplicate(rel_path)

        # ── 检查 5: 命名规范 ──
        _check_naming(str(file_path), str(parent))

        # ── 执行创建 ──
        content = SCRIPT_TEMPLATE.format(description=description or f"{rel_path} 脚本")
        _atomic_write(file_path, content, self.dry_run, self.actions)

        # ── 注册到 manifest ──
        _register_to_manifest(rel_path, description, self.dry_run, self.actions)

        # ── 通知资产盘点系统（MOD-INF-026）──
        _notify_asset_inventory(str(file_path), "script", self.dry_run)

        # ── P0-5: 自动登记 creation_token（create_guard 闭环）──
        _register_creation_token(str(file_path), rel_path.replace("/", "_"), self.dry_run)

        print(f"\n  CREATED  {file_path}")
        print(f"  REGISTERED  {SCRIPT_MANIFEST}  (entry '{rel_path}')")
        print(f"  ACTION:  python scripts/{rel_path}.py")
        _remind_sys_master_dispatch("scripts", rel_path, description)
        _remind_path_tree_refresh()
        return file_path

    def create_gate(
        self,
        gate_id: str,
        title: str = "",
        category: str = "kms",
    ) -> Path:
        """创建门禁 YAML 并注册到 _registry.yaml。"""
        file_name = f"{gate_id.lower()}.yaml"
        file_path = GATES_DIR / file_name

        # ── 检查 1: 文件冲突 ──
        if file_path.exists():
            raise ScaffoldError(f"Gate 文件已存在: {file_path}")

        # ── 检查 2: registry 中无重复 ──
        _check_gate_registry_duplicate(gate_id)

        # ── 检查 3: 命名规范 ──
        _check_naming(str(file_path), str(GATES_DIR))

        # ── 执行创建 ──
        content = GATE_TEMPLATE.format(
            gate_id=gate_id,
            title=title or gate_id,
            category=category,
            created_at=datetime.now().strftime("%Y-%m-%d"),
        )
        _atomic_write(file_path, content, self.dry_run, self.actions)

        # ── 注册到 _registry.yaml ──
        _register_to_gate_registry(gate_id, title, category, file_name, self.dry_run, self.actions)

        # ── 通知资产盘点系统（MOD-INF-026）──
        _notify_asset_inventory(str(file_path), "gate", self.dry_run)

        print(f"\n  CREATED  {file_path}")
        print(f"  REGISTERED  {GATE_REGISTRY}  (gate_id '{gate_id}')")
        _remind_path_tree_refresh()
        return file_path

    def create_yaml(
        self,
        rel_path: str,
        description: str = "",
        domain: str = "",
        subdomain: str = "",
    ) -> Path:
        """在指定路径创建 YAML 文件（kebab-case 强制），通知资产盘点。"""
        # ── 检查 1: kebab-case 命名 ──
        name_part = Path(rel_path).name
        _enforce_kebab_case(name_part)

        file_path = PROJECT_ROOT / f"{rel_path}.yaml"

        # ── 检查 2: 父目录 ──
        parent = file_path.parent
        if not parent.is_dir():
            os.makedirs(parent, exist_ok=True)

        # ── 检查 3: 文件冲突 ──
        if file_path.exists():
            raise ScaffoldError(f"文件已存在: {file_path}\n如果是功能重复，请复用已有文件而非新建。")

        # ── 检查 4: 功能重复 ──
        _check_duplicate_functionality(name_part, description, domain, subdomain)

        # ── 检查 5: 命名规范 ──
        _check_naming(str(file_path), str(parent))

        # ── 执行创建 ──
        content = YAML_TEMPLATE.format(
            blueprint_id="",
            file_path=str(file_path).replace(str(PROJECT_ROOT) + "\\", "").replace("\\", "/"),
            module_path="",
            description=description or name_part,
        )
        _atomic_write(file_path, content, self.dry_run, self.actions)

        # ── 通知资产盘点系统（MOD-INF-026）──
        _notify_asset_inventory(str(file_path), "yaml", self.dry_run)

        print(f"\n  CREATED  {file_path}")
        _remind_path_tree_refresh()
        return file_path

    def create_rule(
        self,
        name: str,
        title: str,
        scope: str,
        layer: str = "compliance",
        severity: str = "error",
        stability: str = "evolving",
        safety_level: str = "L",
        ai_autonomy: str = "ai_modifiable",
    ) -> Path:
        """在 docs/01_policies_and_standards/rules/ 创建 trae_XXX.yaml 规则文件。

        自动分配 rule_id（TRAE-XXX），生成完整标准 frontmatter。
        """
        # ── 检查 1: snake_case 命名 ──
        if not re.match(r"^[a-z][a-z0-9_]*$", name):
            raise ScaffoldError(
                f"命名规范阻断: '{name}' 不符合 snake_case 规范。\n"
                f"  规则文件名必须使用 snake_case（小写+下划线），e.g. 'arch_new_rule'"
            )

        # ── 检查 1.5: 规则主题前缀（ARCH-037，按文件名定位的命名约定）──
        # 强制 name 至少含主题+描述两段；已知前缀静默通过，新前缀警告（允许扩展）。
        if "_" not in name:
            raise ScaffoldError(
                f"主题前缀阻断: '{name}' 缺少主题前缀。\n"
                f"  命名约定(trae_028 GOV-DOC-003, ARCH-037): 规则文件名 MUST 为 "
                f"trae_NNN_<主题>_<描述>.yaml，<主题>段便于按文件名定位。\n"
                f"  e.g. arch_new_rule / behavior_xxx / doc_xxx / methodology_xxx"
            )
        _known_prefixes = _derive_rule_theme_prefixes()
        if not any(name == p or name.startswith(p + "_") for p in _known_prefixes):
            _first_seg = name.split("_", 1)[0]
            print(
                f"  [WARN] 新主题前缀 '{_first_seg}'，现有主题前缀: "
                f"{sorted(_known_prefixes)}\n"
                f"  确认为新主题后继续（trae_028 GOV-DOC-003, ARCH-037）。",
                file=sys.stderr,
            )

        # ── 检查 2: layer 合法性（从 layer_vocabulary.yaml 动态加载，ARCH-021）──
        valid_layers = _load_valid_layers()
        if not valid_layers:
            raise ScaffoldError(
                f"无法从 layer_vocabulary.yaml 加载合法层名（文件不可读或为空），"
                f"请检查 {LAYER_VOCABULARY}"
            )
        if layer not in valid_layers:
            raise ScaffoldError(f"layer 必须是 {sorted(valid_layers)} 之一，得到: {layer}")

        # ── 检查 3: stability/safety_level/ai_autonomy 合法性 ──
        if stability not in {"frozen", "stable", "evolving", "volatile"}:
            raise ScaffoldError(f"stability 非法: {stability}")
        if safety_level not in {"H", "M", "L"}:
            raise ScaffoldError(f"safety_level 非法: {safety_level}")
        if ai_autonomy not in {"immutable_core", "human_gated", "ai_modifiable"}:
            raise ScaffoldError(f"ai_autonomy 非法: {ai_autonomy}")

        # ── 检查 4: 自动分配 rule_id ──
        rule_id, rule_num = _next_rule_id()

        # ── 检查 5: 文件冲突 ──
        file_name = f"trae_{rule_num:03d}_{name}.yaml"
        file_path = RULES_DIR / file_name
        if file_path.exists():
            raise ScaffoldError(f"规则文件已存在: {file_path}")

        # ── 检查 6: 功能重复 ──
        _check_duplicate_functionality(name, title, "trae", "rules")

        # ── 检查 7: 命名规范 ──
        _check_naming(str(file_path), str(RULES_DIR))

        # ── 执行创建 ──
        content = RULE_TEMPLATE.format(
            rule_id=rule_id,
            title=title,
            layer=layer,
            scope=scope,
            severity=severity,
            stability=stability,
            safety_level=safety_level,
            ai_autonomy=ai_autonomy,
            timestamp=datetime.now().strftime("%Y-%m-%dT00:00:00"),
            session_id="scaffold-generated",
        )
        _atomic_write(file_path, content, self.dry_run, self.actions)

        # ── 通知资产盘点系统（MOD-INF-026）──
        _notify_asset_inventory(str(file_path), "yaml", self.dry_run)

        print(f"\n  CREATED  {file_path}")
        print(f"  RULE_ID  {rule_id}")
        print(f"  NEXT STEP: 编辑 {file_path} 补充 sections/triggers/references 内容")
        _remind_path_tree_refresh()
        return file_path

    def create_json(
        self,
        rel_path: str,
        description: str = "",
        domain: str = "",
        subdomain: str = "",
    ) -> Path:
        """在指定路径创建 JSON 文件（kebab-case 强制），通知资产盘点。"""
        # ── 检查 1: kebab-case 命名 ──
        name_part = Path(rel_path).name
        _enforce_kebab_case(name_part)

        file_path = PROJECT_ROOT / f"{rel_path}.json"

        # ── 检查 2: 父目录 ──
        parent = file_path.parent
        if not parent.is_dir():
            os.makedirs(parent, exist_ok=True)

        # ── 检查 3: 文件冲突 ──
        if file_path.exists():
            raise ScaffoldError(f"文件已存在: {file_path}\n如果是功能重复，请复用已有文件而非新建。")

        # ── 检查 4: 功能重复 ──
        _check_duplicate_functionality(name_part, description, domain, subdomain)

        # ── 检查 5: 命名规范 ──
        _check_naming(str(file_path), str(parent))

        # ── 执行创建 ──
        content = JSON_TEMPLATE.format(
            created_at=datetime.now().strftime("%Y-%m-%d"),
            description=description or name_part,
        )
        _atomic_write(file_path, content, self.dry_run, self.actions)

        # ── 通知资产盘点系统（MOD-INF-026）──
        _notify_asset_inventory(str(file_path), "json", self.dry_run)

        print(f"\n  CREATED  {file_path}")
        _remind_path_tree_refresh()
        return file_path

    def create_md(
        self,
        rel_path: str,
        description: str = "",
        domain: str = "",
        subdomain: str = "",
    ) -> Path:
        """在指定路径创建 Markdown 文件（kebab-case 强制），通知资产盘点。"""
        # ── 检查 1: kebab-case 命名 ──
        name_part = Path(rel_path).name
        _enforce_kebab_case(name_part)

        file_path = PROJECT_ROOT / f"{rel_path}.md"

        # ── 检查 2: 父目录 ──
        parent = file_path.parent
        if not parent.is_dir():
            os.makedirs(parent, exist_ok=True)

        # ── 检查 3: 文件冲突 ──
        if file_path.exists():
            raise ScaffoldError(f"文件已存在: {file_path}\n如果是功能重复，请复用已有文件而非新建。")

        # ── 检查 4: 功能重复 ──
        _check_duplicate_functionality(name_part, description, domain, subdomain)

        # ── 检查 5: 命名规范 ──
        _check_naming(str(file_path), str(parent))

        # ── 执行创建 ──
        content = MD_TEMPLATE.format(
            file_path=str(file_path).replace(str(PROJECT_ROOT) + "\\", "").replace("\\", "/"),
            description=description or name_part,
        )
        _atomic_write(file_path, content, self.dry_run, self.actions)

        # ── 通知资产盘点系统（MOD-INF-026）──
        _notify_asset_inventory(str(file_path), "md", self.dry_run)

        print(f"\n  CREATED  {file_path}")
        _remind_path_tree_refresh()
        return file_path


# ===================================================================
# 注册辅助函数
# ===================================================================


def _register_to_init(
    init_py: Path,
    class_name: str,
    module_name: str,
    package: str,
    dry_run: bool,
    actions: list[str],
) -> None:
    """向 __init__.py 追加 import + __all__ 条目。"""
    if not init_py.exists():
        init_py.write_text(
            f'from zephyr.{package}.{module_name} import {class_name}\n\n__all__ = [\n    "{class_name}",\n]\n',
            encoding="utf-8",
        )
        return

    content = init_py.read_text(encoding="utf-8")

    import_line = f"from zephyr.{package}.{module_name} import {class_name}"
    if import_line not in content:
        lines = content.split("\n")
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                insert_pos = i + 1
        lines.insert(insert_pos, import_line)
        content = "\n".join(lines)

    if "__all__" in content:
        all_line = f'    "{class_name}",'
        if all_line not in content:
            content = _insert_into_all_list(content, class_name)
    else:
        content += f'\n__all__ = [\n    "{class_name}",\n]\n'

    if dry_run:
        actions.append(f"[DRY-RUN] Would update {init_py}")
        return

    _atomic_write(init_py, content, False, actions)


def _insert_into_all_list(text: str, name: str) -> str:
    """在 __all__ 列表中插入条目（字母序）。"""
    pattern = r"(\[ __all__\s*=\s*\[)(.*?)(\])"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        text += f'\n__all__.append("{name}")\n'
        return text

    prefix = match.group(1)
    middle = match.group(2)
    suffix = match.group(3)

    entries = [e.strip().strip('"').strip("'") for e in middle.split(",") if e.strip()]
    entries.append(name)
    entries = sorted(set(entries))

    new_middle = "\n    " + ",\n    ".join(f'"{e}"' for e in entries) + ",\n"
    return text[: match.start(2)] + new_middle + text[match.end(2) :]


def _next_rule_id() -> tuple[str, int]:
    """扫描 RULES_DIR 下所有 trae_XXX.yaml，返回下一个 (rule_id, number)。"""
    if not RULES_DIR.exists():
        return "TRAE-001", 1
    max_num = 0
    for f in RULES_DIR.glob("trae_*.yaml"):
        m = re.match(r"trae_(\d+)_", f.name)
        if m:
            num = int(m.group(1))
            if num > max_num:
                max_num = num
    next_num = max_num + 1
    return f"TRAE-{next_num:03d}", next_num


def _register_to_manifest(
    rel_path: str,
    description: str,
    dry_run: bool,
    actions: list[str],
) -> None:
    """向 script_manifest.yaml 追加条目。"""
    if not SCRIPT_MANIFEST.exists():
        raise ScaffoldError(f"script_manifest.yaml 不存在: {SCRIPT_MANIFEST}")

    manifest = yaml.safe_load(SCRIPT_MANIFEST.read_text(encoding="utf-8")) or {}
    scripts = manifest.get("scripts", [])

    entry = {
        "path": f"{rel_path}.py",
        "description": description or f"{rel_path} 脚本",
        "domain": rel_path.split("/")[0] if "/" in rel_path else "root",
        "execution_plane": "warm-path",
        "status": "registered",
    }
    scripts.append(entry)
    manifest["scripts"] = scripts
    manifest["total_scripts"] = len(scripts)
    manifest["generated_at"] = datetime.now().strftime("%Y-%m-%d")

    new_content = yaml.dump(manifest, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if dry_run:
        actions.append(f"[DRY-RUN] Would update {SCRIPT_MANIFEST}")
        return

    _atomic_write(SCRIPT_MANIFEST, new_content, False, actions)


def _register_to_gate_registry(
    gate_id: str,
    title: str,
    category: str,
    file_name: str,
    dry_run: bool,
    actions: list[str],
) -> None:
    """向 _registry.yaml 追加门禁条目。"""
    if not GATE_REGISTRY.exists():
        raise ScaffoldError(f"_registry.yaml 不存在: {GATE_REGISTRY}")

    registry = yaml.safe_load(GATE_REGISTRY.read_text(encoding="utf-8")) or {}
    gates = registry.get("gates", [])

    entry = {
        "gate_id": gate_id,
        "gate_name": gate_id.lower(),
        "title": title or gate_id,
        "category": category,
        "file": file_name,
        "status": "active",
        "scope": "global",
        "execution_plane": "warm",
    }
    gates.append(entry)
    registry["gates"] = gates
    registry["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    new_content = yaml.dump(registry, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if dry_run:
        actions.append(f"[DRY-RUN] Would update {GATE_REGISTRY}")
        return

    _atomic_write(GATE_REGISTRY, new_content, False, actions)


# ===================================================================
# 重复检查
# ===================================================================


def _check_duplicate_functionality(
    name: str,
    description: str,
    domain: str = "",
    subdomain: str = "",
    force_override: bool = False,
    expected_module_path: str = "",
) -> None:
    """SSoT门禁：检查功能域重叠 + module_path 冲突。硬阻断——重叠时禁止创建。

    三个检测维度：
      维度1: 功能域注册表重叠（force_override 不跳过——防止真重复）
      维度2: 蓝图关键词匹配（force_override 跳过）
      维度3: module_path 冲突 + basename 跨域查重（force_override 不跳过——确凿重复信号）
             维度3a: 同 module_path = 同文件身份（方案 E：复用 [MODULE] 头）
             维度3b: 同 basename 跨域 = 复刻信号（P0-4 防再生：阻断 AI 跨域复刻同名模块）
                     豁免: __init__.py / conftest.py / __main__.py（Python 包/约定标识）

    force_override=True 时跳过维度2（蓝图关键词匹配），维度1和维度3仍执行。
    用于确认 SSoT 误报后强制创建。
    """
    # ── 维度3a: SSoT module_path 冲突检测（方案 E：零新真源，复用 [MODULE] 头）──
    # force_override 不跳过——同 module_path = 同文件身份 = 确凿重复信号。
    # 真源是文件头部 [MODULE] 字段（已存在），反查通过 capability_lookup 实时扫描磁盘。
    # L1 fail-open（import 失败时降级放行），L2 兜底门禁（git_commit_gateway）补防线，
    # L3 pre-commit hook（check_ssot_gate.py）双保险——三层防线共用 check_ssot_conflicts。
    if expected_module_path:
        try:
            from zephyr.governance.capability_lookup import CapabilityLookup
            lookup = CapabilityLookup()
            conflicts = lookup.find_files_by_module_path(expected_module_path)
            if conflicts:
                conflict_list = "\n".join(f"    - {c}" for c in conflicts)
                raise ScaffoldError(
                    f"SSoT门禁阻断：module_path 冲突\n"
                    f"  新文件预期 module_path: {expected_module_path}\n"
                    f"  已有文件声明了相同 module_path:\n{conflict_list}\n"
                    f"  → 这是确凿的重复信号（同 module_path = 同文件身份）\n"
                    f"  复用决策（RULE-EIGHT）：\n"
                    f"    完全覆盖 → 直接用已有文件\n"
                    f"    80%覆盖 → 扩展已有文件（from zephyr.xxx import yyy 后加方法）\n"
                    f"    50%覆盖 → 重构已有+扩展\n"
                    f"    0%覆盖 → 确认 package/name 是否需要改名（module_path 必须唯一）"
                )
        except ScaffoldError:
            raise
        except ImportError:
            print("  WARNING: capability_lookup 不可用，跳过 module_path 冲突检测（L2 兜底门禁补防线）")
        except Exception as exc:
            print(f"  WARNING: module_path 冲突检测失败: {exc}（L2 兜底门禁补防线）")

        # ── 维度3b: basename 跨域查重（P0-4 防再生门禁）──
        # 同 basename 跨域 = AI 跨域复刻信号（病根1）。与 P0-1 N-16 src/ 门禁一致——
        # scaffold 是前门（创建时拦截），N-16 是后门（commit 时拦截），两者豁免清单一致。
        # 仅对 src/zephyr/ 模块创建生效（expected_module_path 以 zephyr. 开头）。
        if expected_module_path.startswith("zephyr."):
            basename = f"{Path(name).name}.py"
            # 豁免清单与 P0-1 _N16_SRC_EXEMPT_NAMES 一致（Python 包标识/pytest 约定/python -m 入口）
            _BASENAME_EXEMPT = frozenset({"__init__.py", "conftest.py", "__main__.py"})
            if basename not in _BASENAME_EXEMPT:
                existing = [
                    p for p in SRC_ZEPHYR.rglob(basename)
                    if "__pycache__" not in str(p) and "._archive" not in str(p)
                ]
                if existing:
                    exist_list = "\n".join(
                        f"    - {p.relative_to(PROJECT_ROOT)}" for p in sorted(existing)
                    )
                    raise ScaffoldError(
                        f"SSoT门禁阻断：basename 跨域重复\n"
                        f"  新文件 basename: {basename}\n"
                        f"  已有同 basename 文件:\n{exist_list}\n"
                        f"  → 同 basename 跨域 = 复刻信号（责任唯一，真源唯一）\n"
                        f"  复用决策（RULE-EIGHT）：\n"
                        f"    完全覆盖 → 直接用已有文件\n"
                        f"    80%覆盖 → 扩展已有文件\n"
                        f"    50%覆盖 → 重构已有+扩展\n"
                        f"    0%覆盖 → 改名（basename 必须项目内唯一，见 N-16 src/ 规则）"
                    )

    if force_override:
        # 仅跳过蓝图关键词匹配；功能域注册表检查仍执行（防止真重复）
        pass
    else:
        try:
            from zephyr.infrastructure.registry_governance import FunctionalDomainRegistry

            registry = FunctionalDomainRegistry()
            overlap = registry.check_overlap(
                domain=domain,
                subdomain=subdomain,
                name=name,
                description=description,
            )
            if overlap.has_overlap:
                details = "; ".join(overlap.overlap_details)
                raise ScaffoldError(
                    f"SSoT门禁阻断：功能域重叠检测到\n"
                    f"  {details}\n"
                    f"  复用决策（RULE-EIGHT）：\n"
                    f"    完全覆盖 → 直接用已有模块\n"
                    f"    80%覆盖 → 扩展已有模块\n"
                    f"    50%覆盖 → 重构已有+扩展\n"
                    f"    0%覆盖 → 确认domain/subdomain后重新创建\n"
                    f"  如确需新建，请指定 --domain 和 --subdomain 参数声明新功能域"
                )
        except ScaffoldError:
            raise
        except ImportError:
            pass
        except Exception as exc:
            print(f"  WARNING: 功能域注册表检查失败: {exc}")

        try:
            from zephyr.integration.mcp import BlueprintSearchServer
        except ImportError:
            return

        query = f"{name} {description}".strip()
        if not query or len(query) < 3:
            return

        try:
            server = BlueprintSearchServer()
            result = server._find_relevant_blueprint(query, num_results=5)
            matches = result.get("results", [])
            for m in matches[:3]:
                score = m.get("relevance_score", 0)
                if score >= 20:
                    raise ScaffoldError(
                        f"SSoT门禁阻断：蓝图关键词匹配检测到类似功能\n"
                        f"  已有蓝图: {m.get('blueprint_id', '?')} (score={score})\n"
                        f"  description: {m.get('hint', 'N/A')}\n"
                        f"  level={m.get('blueprint_level')} priority={m.get('priority')}\n"
                        f"  复用决策（RULE-EIGHT）：\n"
                        f"    完全覆盖 → 直接用已有蓝图\n"
                        f"    80%覆盖 → 扩展已有蓝图\n"
                        f"    50%覆盖 → 重构已有+扩展\n"
                        f"    0%覆盖 → 确认后使用 --force-override 强制创建"
                    )
        except ScaffoldError:
            raise
        except Exception:
            pass


def _check_manifest_duplicate(rel_path: str) -> None:
    """检查 script_manifest.yaml 中是否已有同路径条目。"""
    if not SCRIPT_MANIFEST.exists():
        return

    manifest = yaml.safe_load(SCRIPT_MANIFEST.read_text(encoding="utf-8")) or {}
    scripts = manifest.get("scripts", [])

    target = f"{rel_path}.py"
    for entry in scripts:
        if entry.get("path") == target:
            raise ScaffoldError(
                f"script_manifest.yaml 中已存在: {target}\ndescription: {entry.get('description', 'N/A')}"
            )


def _check_gate_registry_duplicate(gate_id: str) -> None:
    """检查 _registry.yaml 中是否已有同 ID 门禁。"""
    if not GATE_REGISTRY.exists():
        return

    registry = yaml.safe_load(GATE_REGISTRY.read_text(encoding="utf-8")) or {}
    gates = registry.get("gates", [])

    for entry in gates:
        if entry.get("gate_id", "").upper() == gate_id.upper():
            raise ScaffoldError(
                f"_registry.yaml 中已存在 gate_id='{gate_id}'\n"
                f"title: {entry.get('title', 'N/A')}\n"
                f"file: {entry.get('file', 'N/A')}"
            )


# ===================================================================
# 通用工具
# ===================================================================


def _check_naming(file_path: str, dir_path: str) -> None:
    """命名规范门禁：调用 check_naming_convention 检查文件名和目录名。
    检测到违规时打印违规信息并以非零退出码终止。
    强化: 传递 abspath 以启用 N-06/N-07/N-11/N-14/N-15 内容感知检查
    """
    rel_file = os.path.relpath(file_path, PROJECT_ROOT).replace("\\", "/")
    abspath = Path(file_path) if Path(file_path).exists() else None
    violations = check_file(rel_file, abspath, PROJECT_ROOT)
    violations.extend(check_dir(os.path.relpath(dir_path, PROJECT_ROOT).replace("\\", "/")))
    if violations:
        for v in violations:
            print(f"  NAMING VIOLATION [{v.rule}]: {v.message}")
        sys.exit(1)


def _notify_asset_inventory(file_path: str, asset_type: str, dry_run: bool) -> None:
    """post-creation hook: 通知资产盘点系统新文件已创建。

    MOD-INF-026 蓝图 §38 自资产注册 —— scaffold.py 是唯一创建入口，
    所有新文件通过此 hook 自动通知盘点系统。

    失败不阻塞 scaffold —— 盘点系统不可用也允许创建文件。
    """
    if dry_run:
        return

    try:
        from zephyr.governance.asset_inventory.telemetry import get_telemetry

        telemetry = get_telemetry()
        telemetry.inc(f"scaffold_{asset_type}_created")
    except Exception:
        pass


def _register_creation_token(file_path: str, capability: str, dry_run: bool) -> None:
    """P0-5 防再生门禁：scaffold 创建 .py 文件时自动登记 creation_token。

    create_guard（GitCommitGateway 注册 gate）硬阻断无 creation_token 的新 .py 文件。
    scaffold 是唯一创建入口（RULE-TWO），通过自动登记 token 实现"走 scaffold → 放行，
    绕 scaffold → 阻断"的闭环。AI 绕过 scaffold 直接 Write .py → 无 token → commit 阻断。

    失败不阻塞 scaffold —— token 登记失败时打印警告（commit 时 create_guard 会兜底阻断，
    AI 需手动补登记或用 --amend 重跑 scaffold）。
    """
    if dry_run:
        return
    if not CAPABILITY_REGISTRY.exists():
        print(f"  WARNING: capability registry 不存在，跳过 creation_token 登记: {CAPABILITY_REGISTRY}")
        return

    try:
        rel_path = str(Path(file_path).relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return

    import yaml as _yaml
    try:
        data = _yaml.safe_load(CAPABILITY_REGISTRY.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  WARNING: capability registry 解析失败，跳过 creation_token 登记: {exc}")
        return

    if not isinstance(data, dict):
        return

    tokens = data.get("creation_tokens", []) or []
    if not isinstance(tokens, list):
        tokens = []

    # 幂等：已有同 file 条目则跳过
    for entry in tokens:
        if isinstance(entry, dict) and entry.get("file", "").replace("\\", "/") == rel_path:
            return  # 已登记，跳过

    token_value = f"auto-scaffold-{capability}-{datetime.now().strftime('%Y%m%d')}"
    new_entry = {
        "file": rel_path,
        "token": token_value,
        "created_by": "scaffold.py",
        "capability": capability,
    }
    tokens.append(new_entry)
    data["creation_tokens"] = tokens

    try:
        _atomic_write(CAPABILITY_REGISTRY, _yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False), False, [])
        print(f"  REGISTERED  creation_token for {rel_path} (token={token_value})")
    except Exception as exc:
        print(f"  WARNING: creation_token 登记失败: {exc}")
        print(f"  → commit 时 create_guard 会阻断，需手动在 {CAPABILITY_REGISTRY} 补登记")


def _remind_path_tree_refresh() -> None:
    """post-creation hook: 提醒刷新项目路径树。

    创建/删除/移动文件后 MUST 同步刷新路径树，
    否则下一个 session 冷启动看到错误结构。
    """
    print("  ⚠️  REMINDER: 文件结构已变更，请刷新路径树:")
    print("  ⚠️    python D:/ZephyrAlpha/scripts/governance/generate_project_path_tree.py --write")


def _remind_sys_master_dispatch(package: str, name: str, description: str) -> None:
    """post-creation hook: 提醒更新 SYS-MASTER-001 §0.2 分派表。

    RULE-TWO 反孤儿功能——新模块/脚本创建后，下一个 AI session
    需要通过 §0 分派表发现它。如果分派表没有对应条目，新功能就是孤儿。
    """
    sys_master = PROJECT_ROOT / "docs" / "03_modules" / "_system_master" / "blueprint.md"
    if not sys_master.exists():
        return

    try:
        text = sys_master.read_text(encoding="utf-8")
        search_key = name.replace("-", "_").replace("/", "_")
        if search_key not in text and name not in text:
            print(f"  ⚠️  REMINDER: '{name}' not found in SYS-MASTER-001 §0.2 dispatch table.")
            print("  ⚠️  If this module serves a new task domain, add a row to §0.2:")
            print(f"  ⚠️    | {description or name} | 本蓝图 §N | <module blueprint> | ~400 |")
    except Exception:
        pass


def _sync_blueprint_file_list(package: str, name: str, dry_run: bool) -> None:
    """post-creation hook: 自动更新蓝图 §0.1 代码文件清单。

    RULE-TWO 反孤儿 + 防漂移——scaffold 创建新模块后，自动将新文件
    添加到对应蓝图的 §0.1 文件清单中，防止蓝图-代码漂移。

    查找逻辑：从 src/zephyr/<package>/ 定位到 docs/03_modules/ 下对应蓝图。
    """
    if dry_run:
        return

    code_dir = SRC_ZEPHYR / package
    if not code_dir.exists():
        return

    blueprint_dir = PROJECT_ROOT / "docs" / "03_modules"
    blueprint_candidates = list(blueprint_dir.rglob("blueprint.md"))
    target_blueprint = None
    for bp in blueprint_candidates:
        try:
            text = bp.read_text(encoding="utf-8")
            if (
                f'actual_disk_path: "src/zephyr/{package}/"' in text
                or f"actual_disk_path: 'src/zephyr/{package}/'" in text
            ):
                target_blueprint = bp
                break
        except Exception:
            continue

    if target_blueprint is None:
        return

    try:
        content = target_blueprint.read_text(encoding="utf-8")
        actual_files = sorted([f.name for f in code_dir.iterdir() if f.suffix == ".py"])
        actual_count = len(actual_files)

        import re

        section_match = re.search(r"###\s*§0\.1\s+代码文件清单", content)
        if not section_match:
            return

        listed_match = re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+)`", content[section_match.start() :], re.MULTILINE)
        listed_files = set(listed_match)
        actual_set = set(actual_files)
        missing_in_blueprint = actual_set - listed_files

        if not missing_in_blueprint:
            return

        last_row_match = None
        for m in re.finditer(
            r"^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|",
            content[section_match.start() :],
            re.MULTILINE,
        ):
            last_row_match = m
        if last_row_match is None:
            return

        last_num = int(last_row_match.group(1))
        insert_pos = section_match.start() + last_row_match.end()

        new_rows = ""
        for i, fname in enumerate(sorted(missing_in_blueprint), last_num + 1):
            new_rows += f"\n| {i} | `{fname}` | §3.1 | {fname.replace('.py', '').replace('_', ' ')} | 已实现 | — |"

        content = content[:insert_pos] + new_rows + content[insert_pos:]

        for old_count in range(1, 200):
            for pattern in [
                f"{old_count} .py files",
                f"{old_count} 个 .py 文件",
                f"{old_count} 个 .py",
                f"{old_count}代码文件",
            ]:
                if pattern in content and old_count != actual_count:
                    content = content.replace(pattern, pattern.replace(str(old_count), str(actual_count)))

        tmp_path = str(target_blueprint) + f".{os.getpid()}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(target_blueprint))

        print(
            f"  📋 SYNCED: Added {len(missing_in_blueprint)} file(s) to blueprint §0.1: {sorted(missing_in_blueprint)}"
        )
    except Exception as e:
        print(f"  ⚠️  SYNC-FAILED: Could not update blueprint §0.1: {e}")


def _atomic_write(path: Path, content: str, dry_run: bool, actions: list[str]) -> None:
    """RULE-ONE 合规: temp-file + atomic rename。"""
    if dry_run:
        actions.append(f"[DRY-RUN] Would write {path}")
        return

    tmp_path = Path(f"{path}.{os.getpid()}.tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8")
        os.replace(str(tmp_path), str(path))
    except PermissionError:
        try:
            os.remove(str(tmp_path))
        except OSError:
            pass
        raise


def _to_class_name(name: str) -> str:
    """snake_case → PascalCase。"""
    return "".join(part.capitalize() for part in name.split("_"))


def _to_kebab_case(name: str) -> str:
    """将任意命名转换为 kebab-case。支持 snake_case、PascalCase、camelCase。"""
    # 先处理 camelCase / PascalCase：在大写字母前插入连字符
    result = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    # 再将下划线和空格替换为连字符
    result = re.sub(r"[_\s]+", "-", result).lower().strip("-")
    result = re.sub(r"-+", "-", result)
    return result


def _enforce_kebab_case(name: str) -> str:
    """强制 kebab-case 命名。不符合时抛出 ScaffoldError 并建议正确形式。"""
    kebab = _to_kebab_case(name)
    if kebab != name:
        raise ScaffoldError(
            f"命名规范阻断: '{name}' 不符合 kebab-case 规范。\n"
            f"  建议使用: '{kebab}'\n"
            f"  YAML/JSON/MD 文件名必须使用 kebab-case（小写+连字符），禁止下划线和大写字母。"
        )
    return name


def _list_packages() -> str:
    """列出 src/zephyr/ 下所有子包。"""
    pkgs = [
        d.name
        for d in sorted(SRC_ZEPHYR.iterdir())
        if d.is_dir() and not d.name.startswith("_") and not d.name.startswith(".") and (d / "__init__.py").exists()
    ]
    return ", ".join(pkgs[:20])


# ===================================================================
# CLI
# ===================================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ZephyrAlpha Scaffold — 唯一创建入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    # module
    p_mod = sub.add_parser("module", help="创建 src/zephyr/<package>/<name>.py")
    p_mod.add_argument("package", help="目标包名 (e.g. feedback-loop)")
    p_mod.add_argument("name", help="模块名 (e.g. scheduler)")
    p_mod.add_argument("--desc", default="", help="功能描述")
    p_mod.add_argument("--domain", default="", help="功能域 (e.g. governance)")
    p_mod.add_argument("--subdomain", default="", help="子功能域 (e.g. gate_engine)")
    p_mod.add_argument("--dry-run", action="store_true", help="仅检查，不写入")

    # script
    p_scr = sub.add_parser("script", help="创建 scripts/<path>/<name>.py")
    p_scr.add_argument("path", help="scripts 下的相对路径 (e.g. governance/my_tool)")
    p_scr.add_argument("--desc", default="", help="功能描述")
    p_scr.add_argument("--domain", default="", help="功能域 (e.g. governance)")
    p_scr.add_argument("--subdomain", default="", help="子功能域 (e.g. gate_engine)")
    p_scr.add_argument("--dry-run", action="store_true", help="仅检查，不写入")
    p_scr.add_argument("--force-override", action="store_true", help="跳过蓝图关键词匹配检查（SSoT误报时使用）")

    # gate
    p_gate = sub.add_parser("gate", help="创建 src/zephyr/gov_enforcement/rule_enforcement/<id>.yaml")
    p_gate.add_argument("gate_id", help="Gate 标识 (e.g. G7)")
    p_gate.add_argument("--title", default="", help="门禁标题")
    p_gate.add_argument("--category", default="kms", help="门禁分类")
    p_gate.add_argument("--dry-run", action="store_true", help="仅检查，不写入")

    # yaml
    p_yaml = sub.add_parser("yaml", help="创建 YAML 文件（kebab-case 强制）")
    p_yaml.add_argument("path", help="项目根目录下的相对路径（不含扩展名，e.g. docs/01_policies/my-policy）")
    p_yaml.add_argument("--desc", default="", help="功能描述")
    p_yaml.add_argument("--domain", default="", help="功能域 (e.g. governance)")
    p_yaml.add_argument("--subdomain", default="", help="子功能域")
    p_yaml.add_argument("--dry-run", action="store_true", help="仅检查，不写入")

    # rule
    p_rule = sub.add_parser("rule", help="创建 trae_XXX.yaml 规则文件（自带标准 frontmatter）")
    p_rule.add_argument("name", help="规则文件名标识（snake_case，e.g. arch_new_rule）")
    p_rule.add_argument("--title", required=True, help="规则标题")
    p_rule.add_argument("--scope", required=True, help="规则作用域 (e.g. arch_new_rule)")
    p_rule.add_argument("--layer", default="compliance", help="架构层名(见layer_vocabulary.yaml,默认compliance)")
    p_rule.add_argument("--severity", default="error", help="严重度 critical/error/warning (默认 error)")
    p_rule.add_argument("--stability", default="evolving", help="frozen/stable/evolving/volatile (默认 evolving)")
    p_rule.add_argument("--safety-level", default="L", help="H/M/L (默认 L)")
    p_rule.add_argument(
        "--ai-autonomy", default="ai_modifiable", help="immutable_core/human_gated/ai_modifiable (默认 ai_modifiable)"
    )
    p_rule.add_argument("--dry-run", action="store_true", help="仅检查，不写入")

    # json
    p_json = sub.add_parser("json", help="创建 JSON 文件（kebab-case 强制）")
    p_json.add_argument("path", help="项目根目录下的相对路径（不含扩展名，e.g. data/config/my-config）")
    p_json.add_argument("--desc", default="", help="功能描述")
    p_json.add_argument("--domain", default="", help="功能域 (e.g. governance)")
    p_json.add_argument("--subdomain", default="", help="子功能域")
    p_json.add_argument("--dry-run", action="store_true", help="仅检查，不写入")

    # md
    p_md = sub.add_parser("md", help="创建 Markdown 文件（kebab-case 强制）")
    p_md.add_argument("path", help="项目根目录下的相对路径（不含扩展名，e.g. docs/guides/my-guide）")
    p_md.add_argument("--desc", default="", help="功能描述")
    p_md.add_argument("--domain", default="", help="功能域 (e.g. governance)")
    p_md.add_argument("--subdomain", default="", help="子功能域")
    p_md.add_argument("--dry-run", action="store_true", help="仅检查，不写入")

    args = parser.parse_args()
    engine = ScaffoldEngine(dry_run=args.dry_run)

    try:
        if args.mode == "module":
            engine.create_module(
                args.package,
                args.name,
                args.desc,
                domain=getattr(args, "domain", ""),
                subdomain=getattr(args, "subdomain", ""),
            )
        elif args.mode == "script":
            engine.create_script(
                args.path,
                args.desc,
                domain=getattr(args, "domain", ""),
                subdomain=getattr(args, "subdomain", ""),
                force_override=getattr(args, "force_override", False),
            )
        elif args.mode == "gate":
            engine.create_gate(args.gate_id, args.title, args.category)
        elif args.mode == "yaml":
            engine.create_yaml(
                args.path, args.desc, domain=getattr(args, "domain", ""), subdomain=getattr(args, "subdomain", "")
            )
        elif args.mode == "rule":
            engine.create_rule(
                args.name,
                args.title,
                args.scope,
                layer=args.layer,
                severity=args.severity,
                stability=args.stability,
                safety_level=args.safety_level,
                ai_autonomy=args.ai_autonomy,
            )
        elif args.mode == "json":
            engine.create_json(
                args.path, args.desc, domain=getattr(args, "domain", ""), subdomain=getattr(args, "subdomain", "")
            )
        elif args.mode == "md":
            engine.create_md(
                args.path, args.desc, domain=getattr(args, "domain", ""), subdomain=getattr(args, "subdomain", "")
            )
        else:
            parser.print_help()
            sys.exit(1)
    except ScaffoldError as e:
        print(f"\n  BLOCKED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
