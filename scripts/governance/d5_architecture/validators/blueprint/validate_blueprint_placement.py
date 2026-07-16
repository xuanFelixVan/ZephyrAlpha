# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py | §
# [MODULE] scripts.governance.d5_architecture.validators.blueprint.validate_blueprint_placement
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.blueprint.__init__
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
# noqa: m02-manual  M02豁免: while True用于belongs_to链遍历(含break退出),非daemon常驻服务;一次性CLI验证工具
"""蓝图物理位置与归属链完整性校验器 (Blueprint Placement & BelongsTo Validator)

对标: P0-2 (cross_layer 物理错位) / P0-3 (belongs_to 全部缺失) / P0-4 (金字塔缺腰)
safety_level: M

检查项（按严重性）
-----------------
P0-1  蓝图文件缺少 belongs_to 字段（PS-STD-005 §6 MUST 要求）
P0-2  cross_layer 蓝图不在 _cross_layer/ 目录下（判据(c) 域归属豁免：functional_domain
      非空且路径在域目录树下则放行，裁定 R3/#206）
P0-3  按层蓝图的 layer 语义值与物理目录 dir_prefix 不匹配（判据(c) 域归属豁免同 P0-2）
P0-4  域覆盖度漏洞——≥5个模块归属同一父节点，但该父节点不是 Level 0/1 域蓝图（PS-STD-005 §3.3）
P0-5  layer 为废弃 L{NN} 格式（应为 layer_vocabulary.yaml 语义值，裁定 R6/#ARCH-011）
P1-1  belongs_to 链不完整——无法追溯到金字塔顶点 SYS-MASTER-001
P1-2  belongs_to 指向的目标 blueprint.md 文件不存在

用法
----
正常扫描（生成报告）:
    python scripts/governance/d5_architecture/validate_blueprint_placement.py

CI 模式（P0 违规时 exit(1)）:
    python scripts/governance/d5_architecture/validate_blueprint_placement.py --ci
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 蓝图物理位置与归属链完整性校验（belongs_to + 物理目录 vs layer 一致性 + 金字塔链可达性）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import BLUEPRINTS_DIR, EXIT_FINDINGS, EXIT_PASS, GOV_DOCS_DIR, REPO_ROOT
from _shared.walk import iter_files
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file

ensure_utf8_stdout()

import yaml

CROSS_LAYER_DIR = BLUEPRINTS_DIR / "_cross_layer"
INFRA_DIR = BLUEPRINTS_DIR / "infrastructure_runtime_integration"

_LAYER_VOCAB = GOV_DOCS_DIR / "_registry" / "vocabularies" / "layer_vocabulary.yaml"
_LAYER_DATA = yaml.safe_load(_LAYER_VOCAB.read_text(encoding="utf-8")) if _LAYER_VOCAB.exists() else {"values": []}
VALID_LAYERS: frozenset[str] = frozenset(
    str(v.get("value")) for v in _LAYER_DATA.get("values", []) if isinstance(v, dict)
)

VALID_BELONGS_TO: frozenset[str] = frozenset({"SYS-MASTER-001", "MOD-MASTER_BLUEPRINT", "DOM-GOV-001"})


def _is_blueprint(filepath: Path) -> bool:
    """_is_blueprint implementation."""
    return filepath.suffix == ".md" and filepath.name == "blueprint.md"


# 已废弃（2026-07-04 阶段4）：dir_prefix 体系随14层概念清除。
# layer_vocabulary.yaml v2.0.0 已移除 dir_prefix 字段，新4值体系按域平铺无层编号前缀。
# _LAYER_DIR_PREFIX_MAP 和 _layer_to_dir_prefix 已删除，P0-3 检查块改为跳过。


# 非域目录：_cross_layer 为横切合规位（判据(b) 合规位置），_restructuring 为临时迁移位
# （GOV-FSTR-001 待迁回 _cross_layer/）。二者均不作为判据(c) 的域目录。
NON_DOMAIN_DIRS: frozenset[str] = frozenset({"_cross_layer", "_restructuring"})

# 废弃的 L{NN} layer 格式（裁定 R6：layer 须为 layer_vocabulary.yaml 语义值，不得为 L00-L13）
_DEPRECATED_LAYER_RE = re.compile(r"^L\d{2}$")


def _is_domain_owned(fm: dict, path_parts: tuple) -> bool:
    """判据(c) 域归属豁免——functional_domain 非空且物理路径在某域目录树下。

    域目录 = 以 ``_`` 开头但非 ``_cross_layer``（横切合规位）/ ``_restructuring``
    （临时迁移位）的目录。依据裁定 R3（#206）：域归属组件豁免 cross_layer 物理位置
    约束（P0-2）与 dir_prefix 约束（P0-3），避免域组件被强制迁入 _cross_layer/ 破坏域内聚。
    与 project_memory「功能域平级→物理路径平级」一致。
    """
    fd = fm.get("functional_domain", "")
    if not isinstance(fd, str) or not fd.strip():
        return False
    return any(p.startswith("_") and p not in NON_DOMAIN_DIRS for p in path_parts)


def _collect_blueprints() -> dict[str, tuple[Path, dict]]:
    """_collect_blueprints implementation."""
    result: dict[str, tuple[Path, dict]] = {}
    if not BLUEPRINTS_DIR.exists():
        return result
    for md_file in iter_files(BLUEPRINTS_DIR, name_pattern="blueprint.md"):
        fm_tuple = parse_frontmatter_from_file(md_file)
        if fm_tuple is None:
            continue
        fm = fm_tuple[0] if isinstance(fm_tuple, tuple) else fm_tuple
        if not isinstance(fm, dict):
            continue
        module_id = fm.get("module_id", "")
        if not isinstance(module_id, str) or not module_id:
            continue
        result[module_id] = (md_file, fm)
    return result


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="蓝图物理位置与归属链完整性校验器")
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI模式——P0违规时 exit(1)（仅报告无 write 权限）",
    )
    args = parser.parse_args()

    blueprints = _collect_blueprints()
    violations_p0: list[str] = []
    violations_p1: list[str] = []

    # ── P0-1: belongs_to 字段缺失 ──
    for module_id, (filepath, fm) in sorted(blueprints.items()):
        bt = fm.get("belongs_to")
        if bt is None or (isinstance(bt, str) and not bt.strip()):
            violations_p0.append(f"[P0-1] 蓝图 {module_id} 缺少 belongs_to 字段 → {filepath.relative_to(REPO_ROOT)}")

    # ── P0-2: cross_layer 蓝图不在 _cross_layer/ 下 ──
    # 合规条件（满足任一即放行，裁定 R3/#206）：
    #   (a) module_id in KNOWN_LEVEL_01_IDS（Level 0/1 特例）
    #   (b) 在 _cross_layer/ 目录下（无域归属横切组件）
    #   (c) functional_domain 非空且物理路径在某域目录树下（域归属组件，_is_domain_owned）
    KNOWN_LEVEL_01_IDS = {"MOD-MASTER_BLUEPRINT", "SYS-MASTER-001", "DOM-GOV-001"}
    for module_id, (filepath, fm) in sorted(blueprints.items()):
        layer = fm.get("layer", "")
        if layer == "cross_layer" and module_id not in KNOWN_LEVEL_01_IDS:
            try:
                filepath.relative_to(CROSS_LAYER_DIR)
            except ValueError:
                rel = filepath.relative_to(REPO_ROOT)
                if _is_domain_owned(fm, rel.parts):
                    continue  # 判据(c) 域归属豁免
                violations_p0.append(
                    f"[P0-2] cross_layer 蓝图 {module_id} 不在 _cross_layer/ 下 → 当前: {rel}"
                )

    # ── P0-3: 已废弃（2026-07-04 阶段4）──
    # dir_prefix 体系随14层概念清除，layer_vocabulary.yaml v2.0.0 已移除 dir_prefix 字段。
    # 新4值体系（L0_infrastructure/L1_foundation/L2_domain/L3_application）按域平铺，无层编号前缀。
    # 原 dir_prefix 检查已无意义，跳过。

    # ── P0-5: layer 为废弃 L{NN} 格式（裁定 R6/#ARCH-011，填补 P0-3 漏洞） ──
    # 原P0-3 仅检查 layer in VALID_LAYERS，废弃 L 值不在 VALID_LAYERS 中被跳过，
    # 导致 #206-B 遗漏未被发现。P0-5 主动检测废弃格式防再发。
    for module_id, (filepath, fm) in sorted(blueprints.items()):
        layer = fm.get("layer", "")
        if isinstance(layer, str) and _DEPRECATED_LAYER_RE.match(layer):
            violations_p0.append(
                f"[P0-5] 蓝图 {module_id} layer={layer} 为废弃 L 格式（应为 layer_vocabulary.yaml 语义值）→ {filepath.relative_to(REPO_ROOT)}"
            )

    # ── P0-4: 域覆盖度——≥5模块的域是否缺少 Level 1 蓝图 ──
    # 先构建 module_bt（P1-1/P1-2 也复用此数据结构）
    module_bt: dict[str, str] = {}
    for module_id, (_fp, fm) in blueprints.items():
        bt = fm.get("belongs_to")
        if isinstance(bt, str) and bt.strip():
            module_bt[module_id] = bt.strip()

    KNOWN_LEVEL_0_AND_1_IDS = {"SYS-MASTER-001", "MOD-MASTER_BLUEPRINT", "DOM-GOV-001"}
    parent_children: dict[str, list[str]] = defaultdict(list)
    for module_id, bt_target in module_bt.items():
        parent_children[bt_target].append(module_id)

    for parent_id, children in sorted(parent_children.items()):
        if parent_id not in KNOWN_LEVEL_0_AND_1_IDS and len(children) >= 5:
            child_ids = ", ".join(children[:8])
            overflow = f" ... +{len(children) - 8} 个" if len(children) > 8 else ""
            violations_p0.append(
                f"[P0-4] 共 {len(children)} 个蓝图归属 '{parent_id}'，但 {parent_id} 不是 Level 0/1 域蓝图"
                f" → 缺少域集成蓝图 (PS-STD-005 §3.3)"
                f"\n       子模块: {child_ids}{overflow}"
            )

    # ── P1-1: belongs_to 链不可达金字塔顶点 ──
    for module_id, bt_target in module_bt.items():
        visited: set[str] = set()
        current = module_id
        chain = [current]
        while True:
            next_target = module_bt.get(current)
            if next_target is None:
                violations_p1.append(
                    f"[P1-1] belongs_to 链断裂——{module_id} 的链: {' → '.join(chain)} → 找不到 {current} 的 belongs_to 目标"
                )
                break
            if next_target == "SYS-MASTER-001":
                break
            if next_target == current:
                violations_p1.append(f"[P1-1] belongs_to 链自环——{module_id} 的 belongs_to 指向自身 ({current})")
                break
            if next_target in visited:
                violations_p1.append(
                    f"[P1-1] belongs_to 链循环——{module_id} 的链: {' → '.join(chain)} → 回到 {next_target}"
                )
                break
            visited.add(current)
            current = next_target
            chain.append(current)

    # ── P1-2: belongs_to 指向的目标文件不存在 ──
    for module_id, bt_target in module_bt.items():
        if bt_target not in blueprints:
            violations_p1.append(f"[P1-2] believes_to 目标 {bt_target} (来自 {module_id}) 不在已注册蓝图列表中")

    # ── 输出报告 ──
    total_p0 = len(violations_p0)
    total_p1 = len(violations_p1)
    total = total_p0 + total_p1

    print("🔍 蓝图物理位置与归属链校验器启动...")
    print(f"   扫描蓝图: {len(blueprints)} 个")
    print(f"   违规统计: P0={total_p0}  P1={total_p1}")

    if total == 0:
        print("   ✅ 全部通过——无违规")
        return EXIT_PASS
    print()
    if violations_p0:
        print("─" * 70)
        print("🔴 P0 违规（严重——阻塞 beta 完成门禁）:")
        print("─" * 70)
        for v in violations_p0:
            print(f"   {v}")

    if violations_p1:
        print()
        print("─" * 70)
        print("🟡 P1 违规（重要——影响可信度）:")
        print("─" * 70)
        for v in violations_p1:
            print(f"   {v}")

    if args.ci and total_p0 > 0:
        print(f"\n❌ CI 模式——{total_p0} 条 P0 违规 → 退出码 1")
        return EXIT_FINDINGS
    elif args.ci:
        print(f"\n⚠️  CI 模式——{total_p1} 条 P1 违规（不阻塞提交）")
        return EXIT_PASS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
