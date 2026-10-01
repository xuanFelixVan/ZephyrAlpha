# [BLUEPRINT] MOD-GOV_COMMON | docs/_working/architecture_diagram_construction_plan.md | §generator-common
# [MODULE] scripts.governance.d5_architecture.generators._common
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] (none — pure stdlib)
# [CONSUMERS] generate_domain_doc.py; scripts/governance/align_battle_map.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 模块级 import 纯 stdlib 解耦（+yaml）；不 import zephyr.*（便于 mutation testing）；# 函数体内懒加载 zephyr/_shared 例外（tbl_name/head_commit_time/anchor_label_bilingual，2026-10-02 CR-15 同批收内注记）
# [MODIFY-GUARD] cleanup_stale_files 的 name_pattern 参数语义
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] cleanup_stale_files 永不抛异常（目录不存在→返回空列表）
# [TESTS]
# [A_module] module_id=MOD-GOV_COMMON | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""生成器公共工具（向内收：消除重复）。

当前提供 cleanup_stale_files()——治本修复"生成器只增不删"问题。
根因：域重命名/删除后，旧编号文件不会被自动清理，导致目录残留过期文件
（如 D-SIGNAL 重命名后 26_d_digital_twin_architecture.md 残留为孤儿文件）。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 生成器公共工具（向内收：消除重复）。
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import re
import subprocess
from pathlib import Path

import yaml

__all__ = ["cleanup_stale_files", "DB_DISPLAY_NAME", "idempotent_timestamp", "idempotent_date"]


# 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：
# 仓库根真源——_common.py 位于 scripts/governance/d5_architecture/generators/，
# parents[0]=generators/ parents[1]=d5_architecture/ parents[2]=governance/
# parents[3]=scripts/ parents[4]=repo root。
_REPO_ROOT = Path(__file__).resolve().parents[4]

# 进程级缓存（治本：generate_domain_doc --all 时每域 md frontmatter + 每个 HTML 各调一次
# git log 子进程，73 域 ≈ 146 次 subprocess spawn）。同一进程内 git HEAD/工作树不变，
# 结果可安全复用；键 = 目标脚本路径字符串。
_TS_CACHE: dict[str, str] = {}


def idempotent_timestamp(script_path: Path | None = None) -> str:
    """幂等时间源：返回脚本最近一次 git commit 时间（ISO 8601 秒精度 YYYY-MM-DDTHH:MM:SS）。

    相同 commit → 相同时间戳，避免 ``datetime.now`` 等实时时钟导致生成器输出非确定性。

    治本：#ARCH-REGEN-NONIDEMPOTENT-001
    正典先例：generate_decision_diagram._git_commit_timestamp()
    真源铁律：RULE-SCHEMA-TZ（trae_065 时区批）"禁止在生成器中使用 datetime.now 或任何实时时间源"

    Args:
        script_path: 待查脚本路径；默认为调用方源文件。建议显式传 ``Path(__file__)``。

    Returns:
        ISO 8601 秒精度时间字符串（如 ``"2026-08-05T21:38:00"``）。
        git 不可用或文件未入库时返回 ``"unknown"``。
    """
    target = Path(script_path) if script_path is not None else Path(__file__)
    cache_key = str(target)
    if cache_key in _TS_CACHE:
        return _TS_CACHE[cache_key]
    ts = "unknown"
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(target)],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(_REPO_ROOT),
        )
        if r.returncode == 0 and r.stdout.strip():
            # %cI 输出形如 2026-08-05T21:38:00+08:00，截到秒（19 字符）
            ts = r.stdout.strip()[:19]
    except Exception:  # noqa: BLE001 — git 不可用时降级
        pass
    _TS_CACHE[cache_key] = ts
    return ts


def idempotent_date(script_path: Path | None = None) -> str:
    """幂等日期源（YYYY-MM-DD）。

    治本：#ARCH-REGEN-NONIDEMPOTENT-001
    基于 idempotent_timestamp 派生，相同 commit → 相同日期。
    """
    ts = idempotent_timestamp(script_path)
    if "T" in ts:
        return ts.split("T")[0]
    if " " in ts:
        return ts.split(" ")[0]
    return ts  # "unknown" 或其他格式原样返回


# 治本（2026-06-30）：数据库名真源——生成器产物引用此常量，禁止硬编码 `depgraph (PostgreSQL)`。
# 真源链：dependency_path_panorama.md L23 + 命名规范真源 trae_028_doc_structure_naming.yaml → 本常量（生成器可用真源）。
# 生成器纯 stdlib 解耦（不 import zephyr.*），无法读 .md，故在此收口。
DB_DISPLAY_NAME = "depgraph (PostgreSQL)"


def cleanup_stale_files(
    output_dir: Path,
    expected_basenames: set[str],
    name_pattern: str,
) -> list[str]:
    """清理生成器输出目录中的残留文件（治本：解决只增不删）。

    扫描 output_dir 中匹配 name_pattern 的文件，删除不在 expected_basenames
    集合中的文件。仅在 --all 模式下调用（单域模式不清理，避免误删）。

    安全保证：
    - 只删除匹配 name_pattern 的文件（不会碰其他生成器的文件）
    - 不删除 domain_index.md 等非编号文件（pattern 精确匹配 NN_d_xxx 格式）
    - 目录不存在时返回空列表（不抛异常）

    Args:
        output_dir: 生成器输出目录（如 02_domain_architecture_docs/）。
        expected_basenames: 本次生成器应该产出的文件 basename 集合。
            形如 {"22_d_audittest_architecture.md", ...}。
        name_pattern: 正则模式，匹配本生成器产出的文件名。
            architecture 生成器用 r'^\\d{2}_d_[a-z0-9_]+_architecture\\.md$'
            doc 生成器用 r'^\\d{2}_d_(?!.*_architecture\\.md$)[a-z0-9_]+\\.md$'
            （否定前瞻排除 _architecture.md，避免误删 arch 生成器的文件）

    Returns:
        被删除的文件 basename 列表（按字母序）。
    """
    if not output_dir.exists():
        return []
    regex = re.compile(name_pattern)
    deleted: list[str] = []
    for f in sorted(output_dir.iterdir()):
        if not f.is_file():
            continue
        name = f.name
        if regex.match(name) and name not in expected_basenames:
            f.unlink()
            deleted.append(name)
    return deleted


def head_commit_time(root: Path) -> str:
    """时间戳唯一合法派生通道=HEAD 提交时间（壁钟取时函数禁用——RULE-SCHEMA-TZ）。"""
    try:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        r = run_subprocess_hidden(["git", "show", "-s", "--format=%cI", "HEAD"], cwd=str(root), timeout=30)
        v = (r.stdout or "").strip()
        return v if v else "unobserved"
    except Exception:  # noqa: BLE001 — git 不可达=unobserved 占位，两次运行仍逐字节等
        return "unobserved"


def tbl_name(category_id: str) -> str:
    """按 category_id 从 TableRegistry 真源取全限定表名（#ARCH-CH-024 Phase 5）。

    禁硬编码表名字符串绕过 business_data_categories.yaml 真源；懒加载避免
    本模块被静态检视工具（无 src 运行环境）导入时强依赖 zephyr 包。
    """
    from zephyr.data.table_registry import get_registry

    return get_registry().table(category_id)


def anchor_label_bilingual(rel_path: str) -> str:
    """中英标签必经既有翻译 loader（模块级真源=module_translation_registry）；查无=退回路径本身。"""
    from _shared.module_translation_loader import get_module_translation

    trans = get_module_translation(rel_path) or {}
    zh = str(trans.get("name_zh") or "").strip()
    en = str(trans.get("name_en") or "").strip()
    if zh and en:
        return f"{zh} / {en}"
    return zh or en or rel_path


def serialize_map_document(doc: dict, header: str) -> str:
    """确定性序列化核心（键序=插入序，禁 sort_keys 打乱语义分组）——各图头注释由调用方给。"""
    return header + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=110)
