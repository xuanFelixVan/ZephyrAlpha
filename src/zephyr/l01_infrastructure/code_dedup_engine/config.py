"""配置管理 — 策略树 YAML 加载 + 项目规模感知四 Tier 自适应阈值.

职责：
  - PROJECT_SCALE_TIERS 四Tier参数表（5000/15000/50000行边界）
  - 每个Tier含 AST阈值/签名匹配严格度/auto_fix批次/Sensitivity Sweep频率/Shadow Manifest大小
  - 策略树配置加载
  - 退出码约定
"""

from __future__ import annotations

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
