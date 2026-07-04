# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.config
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.code_dedup.policy_tree_validator; tests/code_dedup_engine/test_config_test_code_dedup_engine.py; tests/code_dedup_engine/test_self_scan_integrity.py; tests/config/test_config_root.py; tests/governance/shared/test_app_config_yaml.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_config | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""配置管理 — 策略树 YAML 加载 + 项目规模感知四 Tier 自适应阈值.

职责：
  - PROJECT_SCALE_TIERS 四Tier参数表（5000/15000/50000行边界）
  - 每个Tier含 AST阈值/签名匹配严格度/auto_fix批次/Sensitivity Sweep频率/Shadow Manifest大小
  - 策略树配置加载
  - 退出码约定
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# ── 项目规模感知四 Tier 自适应阈值 ──────────────────────────

PROJECT_SCALE_TIERS: dict[str, dict[str, Any]] = {
    "Tier1_small": {
        "name": "小型项目",
        "max_lines": 5000,
        "description": "<5000行——偏漏报策略（小项目不怕检查，怕遗漏）",
        "ast_similarity_threshold": 0.65,
        "signature_match_strictness": "loose",
        "auto_fix_batch_size": 10,
        "sensitivity_sweep_frequency": "weekly",
        "shadow_manifest_max_size": 200,
        "pre_commit_block_threshold": 0.7,
        "sbs_monitor_active": False,
    },
    "Tier2_medium": {
        "name": "中型项目",
        "min_lines": 5000,
        "max_lines": 15000,
        "description": "5000-15000行——默认策略·5000行魔咒临界点",
        "ast_similarity_threshold": 0.70,
        "signature_match_strictness": "normal",
        "auto_fix_batch_size": 5,
        "sensitivity_sweep_frequency": "weekly",
        "shadow_manifest_max_size": 150,
        "pre_commit_block_threshold": 0.65,
        "sbs_monitor_active": False,
    },
    "Tier3_large": {
        "name": "大型项目",
        "min_lines": 15000,
        "max_lines": 50000,
        "description": "15000-50000行——拦截增强",
        "ast_similarity_threshold": 0.75,
        "signature_match_strictness": "strict",
        "auto_fix_batch_size": 3,
        "sensitivity_sweep_frequency": "daily",
        "shadow_manifest_max_size": 100,
        "pre_commit_block_threshold": 0.60,
        "sbs_monitor_active": True,
    },
    "Tier4_xlarge": {
        "name": "超大型项目",
        "min_lines": 50000,
        "description": ">50000行——激进拦截·SBS监测激活·Shadow Manifest严格控制",
        "ast_similarity_threshold": 0.80,
        "signature_match_strictness": "very_strict",
        "auto_fix_batch_size": 2,
        "sensitivity_sweep_frequency": "continuous",
        "shadow_manifest_max_size": 100,
        "pre_commit_block_threshold": 0.55,
        "sbs_monitor_active": True,
    },
}

# ── 策略树配置 ───────────────────────────────────────────────

POLICY_TREE: dict[str, Any] = {
    "version": "0.10.0",
    "cloning_detection": {
        "type1_exact_match": True,
        "type2_rename_match": True,
        "type3_structure_variant": True,
        "type4_semantic_equivalent": True,
        "micro_clone_ngram_size": 3,
        "micro_clone_min_frequency": 2,
    },
    "thresholds": {
        "high_confidence": 0.95,
        "medium_confidence": 0.85,
        "low_confidence": 0.70,
        "min_block_size": 5,
    },
    "auto_fix": {
        "enabled": True,
        "max_batch_size": 5,
        "max_daily_fixes": 20,
        "doom_loop_max_attempts": 3,
        "observation_window_days": 14,
    },
    "monoculture_immunity": {
        "blast_radius_warning_threshold": 60,
        "blast_radius_critical_threshold": 80,
        "grandfather_age_days": 30,
    },
    "simplicity_audit": {
        "enabled": True,
        "frequency": "monthly",
        "net_negative_threshold": 50,
    },
}

# ── 退出码约定 ───────────────────────────────────────────────

EXIT_CODES: dict[int, str] = {
    0: "CLEAN — 无重复发现",
    1: "WARN — 发现低风险重复",
    2: "ERROR — 发现严重重复",
    3: "FAULT — 工具内部故障",
    4: "DEGRADED — 降级运行",
}

# ── 路径感知阈值 ─────────────────────────────────────────────

PATH_THRESHOLDS: dict[str, float] = {
    "shared": 0.3,
    "core": 0.6,
    "default": 0.7,
    "tests": 0.9,
    "scripts": 0.7,
}


def get_tier_for_project(total_lines: int) -> dict[str, Any]:
    """根据项目总行数返回对应的 Tier 配置."""
    if total_lines < PROJECT_SCALE_TIERS["Tier1_small"]["max_lines"]:
        return PROJECT_SCALE_TIERS["Tier1_small"]
    if total_lines < PROJECT_SCALE_TIERS["Tier2_medium"]["max_lines"]:
        return PROJECT_SCALE_TIERS["Tier2_medium"]
    if total_lines < PROJECT_SCALE_TIERS["Tier3_large"]["max_lines"]:
        return PROJECT_SCALE_TIERS["Tier3_large"]
    return PROJECT_SCALE_TIERS["Tier4_xlarge"]


def get_tier_name(total_lines: int) -> str:
    """返回 Tier 名称字符串."""
    tier = get_tier_for_project(total_lines)
    return tier["name"]


_POLICY_TREE_YAML_PATH: Path = Path(__file__).parent / "config" / "policy-tree.yaml"


def load_policy_tree() -> dict[str, Any]:
    """从 YAML 加载策略树配置，YAML 不存在或无效时 fallback 到硬编码 POLICY_TREE."""
    if _POLICY_TREE_YAML_PATH.exists():
        try:
            import yaml

            with open(_POLICY_TREE_YAML_PATH, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict) and "version" in data:
                return data
        except Exception:
            pass
    return POLICY_TREE


def load_policy_rules() -> list[dict[str, Any]]:
    """从 YAML 加载策略规则列表，YAML 不存在时从硬编码 POLICY_TREE 推导."""
    tree = load_policy_tree()
    if "rules" in tree and isinstance(tree["rules"], list):
        return tree["rules"]
    thresholds = tree.get("thresholds", {})
    monoculture = tree.get("monoculture_immunity", {})
    return [
        {
            "id": "R001",
            "name": "high_confidence_block",
            "condition": f"similarity >= {thresholds.get('high_confidence', 0.95)}",
            "action": "BLOCK_DEDUP",
            "exit_code": 2,
            "severity": "critical",
        },
        {
            "id": "R002",
            "name": "medium_confidence_warn",
            "condition": f"similarity >= {thresholds.get('medium_confidence', 0.85)}",
            "action": "WARN",
            "exit_code": 1,
            "severity": "warning",
        },
        {
            "id": "R003",
            "name": "low_confidence_skip",
            "condition": f"similarity >= {thresholds.get('low_confidence', 0.70)}",
            "action": "SKIP",
            "exit_code": 1,
            "severity": "info",
        },
        {
            "id": "R004",
            "name": "blast_radius_warning",
            "condition": f"brs >= {monoculture.get('blast_radius_warning_threshold', 60)}",
            "action": "WARN",
            "exit_code": 1,
            "severity": "warning",
        },
        {
            "id": "R005",
            "name": "blast_radius_critical",
            "condition": f"brs >= {monoculture.get('blast_radius_critical_threshold', 80)}",
            "action": "BLOCK_FIX",
            "exit_code": 2,
            "severity": "critical",
        },
    ]


class AppConfig:
    def __init__(self, config_path: str | Path | None = None, data: dict[str, Any] | None = None) -> None:
        self.config_path: str | Path | None = config_path
        self.data: dict[str, Any] = data or {}


def load_config(path: str | Path | None = None) -> AppConfig:
    # 5.12.2#6 修复：补充类型注解（原完全无注解）
    return AppConfig(config_path=path)


def reload_config(app_config: AppConfig) -> AppConfig:
    # 5.12.2#6 修复：补充类型注解
    return app_config


DEFAULT_CONFIG_FILENAMES = ["config.yaml", "config.yml", ".code_dedup.yaml"]


def _deep_merge_lists(base: list[Any] | None, override: list[Any] | None) -> list[Any] | None:
    return override if override is not None else base
