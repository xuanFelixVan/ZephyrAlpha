"""N-16 应跳过 docs/_working/ 草稿区（trae_028 n16_config.skip_dirs_docs 含 _working）。

背景（#ARCH-PRECOMMIT-INCREMENTAL，2026-08-05）：
    eia_provider.py 提交被 2 个 N-16 阻断——docs/_working/ 下两份字节相同的
    battle_map_merge_mapping.md（其一为未跟踪 WIP 副本）触发文件名不唯一硬阻断。
    治本：把 _working 加入 trae_028 n16_config.skip_dirs_docs，使草稿区重名不阻断 commit。

本测试覆盖双轨：
    test_working_in_skip_dirs_yaml  —— YAML 真源（trae_028）含 _working
    test_working_in_skip_dirs_code —— 代码 fallback（_N16_DOCS_SKIP_DIRS_FALLBACK）含 _working
                                       （human_gated MOD-INF-005，diff 批准落盘后由红转绿）
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[3]
TRAEE_028_YAML = ROOT / "docs" / "01_policies_and_standards" / "rules" / "trae_028_doc_structure_naming.yaml"
GATE_SRC = ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"


def _find_key(obj, key):
    """递归查找 dict 中的 key（容忍结构微调）。"""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = _find_key(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for item in obj:
            r = _find_key(item, key)
            if r is not None:
                return r
    return None


def _load_skip_dirs_from_yaml() -> set[str]:
    import yaml

    cfg = yaml.safe_load(TRAEE_028_YAML.read_text(encoding="utf-8"))
    found = _find_key(cfg, "skip_dirs_docs")
    return set(found or [])


def test_working_in_skip_dirs_yaml():
    """trae_028 n16_config.skip_dirs_docs 必须含 _working（草稿区豁免）。"""
    skip_dirs = _load_skip_dirs_from_yaml()
    assert "_working" in skip_dirs, (
        f"trae_028 n16_config.skip_dirs_docs 必须含 _working（草稿区豁免），实际 skip_dirs_docs={sorted(skip_dirs)}"
    )


def test_working_in_skip_dirs_code():
    """check_naming_convention.py _N16_DOCS_SKIP_DIRS_FALLBACK 必须含 _working（与 YAML 双轨一致）。

    本测试在 MOD-INF-005（human_gated）代码 diff 落盘前为 RED，diff 批准落盘后转 GREEN。
    """
    src = GATE_SRC.read_text(encoding="utf-8")
    # 定位 _N16_DOCS_SKIP_DIRS_FALLBACK 集合字面量（容忍 `: set[str] =` 类型注解）
    m = re.search(
        r"_N16_DOCS_SKIP_DIRS_FALLBACK\b[^{]*\{([^}]*)\}",
        src,
        re.DOTALL,
    )
    assert m, "_N16_DOCS_SKIP_DIRS_FALLBACK 集合字面量未找到——check_naming_convention.py 结构已变？"
    fallback_block = m.group(1)
    assert '"_working"' in fallback_block or "'_working'" in fallback_block, (
        "_N16_DOCS_SKIP_DIRS_FALLBACK 必须含 '_working'（与 trae_028 YAML 双轨一致）。"
        "human_gated diff 批准落盘后本测试转绿。当前 fallback_block="
        f"{fallback_block.strip()}"
    )
