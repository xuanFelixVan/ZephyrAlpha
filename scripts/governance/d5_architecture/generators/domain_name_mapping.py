# -*- coding: utf-8 -*-
# [TTL] permanent
"""
功能域中文名称映射表 / Functional Domain Chinese Name Mapping

真源优先级（治本 v2.0，2026-06-29）：
1. depgraph (PostgreSQL) domains.domain_name（动态加载，真源唯一）
2. DOMAIN_NAME_ZH 硬编码映射表（fallback，db 不可用时使用）

治本历史：
- v1.0：硬编码映射表作真源（绕过 db domain_name 英文/中文不一致问题）
- v2.0：apply_depgraph.py --update-domain-name 统一 db domain_name 为中文后，
  改为从 db 动态加载（真源归一），硬编码降为 fallback（向后兼容 + db 不可用兜底）

用法 / Usage:
    from domain_name_mapping import get_domain_name_zh
    display_name = get_domain_name_zh(domain_id, fallback_name)

    # 批量场景可预加载缓存（首次调用自动加载，无需手动触发）
    from domain_name_mapping import preload_domain_names
    preload_domain_names()
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 功能域中文名称映射表 / Functional Domain Chinese Name Mapping
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

# sys.path bootstrap（一次性，与同目录其他生成器一致）
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)


# 域ID → 中文名称映射（fallback：db 不可用时使用；新增域应通过 apply_depgraph.py 同步到 db）
DOMAIN_NAME_ZH = {
    # L0 基础设施层
    "D_INFRA_A2A": "A2A通信",
    "D_INFRA_OPS": "基础设施运维",
    "D_INFRA_RECOVERY": "回滚恢复",
    "D_INFRA_RUNTIME": "运行时集成",
    "D_INFRA_TELEMETRY": "可观测性",

    # L1 基础平台层
    "D_ALT_DATA": "另类数据",
    "D_BEHAVIORAL_AUDIT": "行为审计",
    "D_DATA_ENG": "数据工程",
    "D_DATA_GOV": "数据治理",
    "D_DATA_SEC": "数据安全与契约",
    "D_FRONTEND": "前端",
    "D_GOVERNANCE": "生命周期管理",
    "D_INTEGRATION": "管线路由",
    "D_INTEGRATION_GATEWAY": "集成网关",
    "D_MKT_DATA": "行情数据",
    "D_OPS": "反馈循环",
    "D_REPORTING": "报告",
    "D_SECURITY": "对抗验证",
    "D_SECURITY_LLM": "LLM防御",
    "D_SHARED": "共享服务",

    # L1 智能层
    "D_INTELLIGENCE": "上下文管理",
    "D_KNOWLEDGE": "知识管理",
    "D_AUTONOMY_CORE": "自治核心",

    # L2 业务域层 - 数据
    "D_DIGITAL_TWIN": "数字孪生",

    # L2 业务域层 - 因子信号
    "D_FACTOR": "因子",
    "D_SIGLEGACY": "信号遗留设计态",
    "D_ASHARE_SIGNAL": "A股特色信号",
    "D_FUNDAMENTAL_SIGNAL": "基本面信号",
    "D_SIGQC": "信号质量控制",

    # L2 业务域层 - 风险合规
    "D_RISK": "风控",
    "D_COMPLIANCE": "合规",
    "D_AUTONOMY_PERM": "自治保护",

    # L2 业务域层 - 组合决策
    "D_PF_CORE": "组合核心",
    "D_PF_ALLOC": "组合分配",
    "D_SELL_DECISION": "卖出决策",
    "D_CROSS_ASSET": "跨资产",

    # L2 业务域层 - 执行交易
    "D_EX_CORE": "执行核心",
    "D_EX_SOR": "执行路由",
    "D_TRADING": "交易运营",
    "D_POSITION": "仓位管理",

    # L2 业务域层 - ML平台
    "D_ML_TRAIN": "训练",
    "D_ML_SERVE": "推理",

    # L2 业务域层 - 回测仿真
    "D_BACKTEST": "回测",
    "D_SIMULATION": "仿真",
    "D_EXEC_SIM": "执行仿真",

    # L2 治理域层
    "D_AUDITTEST": "审计测试套件",
    "D_GOV_REPAIR": "治理修复",
    "D_GOV_AUDIT": "审计追踪",
    "D_GOV_DOCS": "架构文档治理",
    "D_GOV_DRIFT": "漂移检测",
    "D_GOV_ENFORCEMENT": "规则执行",
    "D_GOV_RULE": "规则治理",
    "D_GOV_SCRIPTS": "脚本治理",

    # 测试域（测试域不插入生产 depgraph (PostgreSQL)，仅硬编码 fallback 维护）
    "D-T3-W0": "测试域T3-0",
    "D-T3-W1": "测试域T3-1",
    "D-T3-W2": "测试域T3-2",
    "D-T3-W3": "测试域T3-3",
    "D-T4-SAME": "相同域T4",
    "D-T5-W0": "读写并发T5-0",
    "D-T5-W1": "读写并发T5-1",
    "D-T5-W2": "读写并发T5-2",
    "D-T5-W3": "读写并发T5-3",
    "D-T9-PREREQ": "T9前置域",
}

# 域ID → 英文名称映射（双语显示用，硬编码真源，与 DOMAIN_NAME_ZH 一一对应）
DOMAIN_NAME_EN: dict[str, str] = {
    # L0 基础设施层
    "D_INFRA_A2A": "A2A Communication",
    "D_INFRA_OPS": "Asset Inventory",
    "D_INFRA_RECOVERY": "Rollback Recovery",
    "D_INFRA_RUNTIME": "Runtime Integration",
    "D_INFRA_TELEMETRY": "Observability",

    # L1 基础平台层
    "D_ALT_DATA": "Alternative Data",
    "D_BEHAVIORAL_AUDIT": "Behavioral Audit",
    "D_DATA_ENG": "Data Engineering",
    "D_DATA_GOV": "Data Governance",
    "D_DATA_SEC": "Data Security & Contracts",
    "D_FRONTEND": "Frontend",
    "D_GOVERNANCE": "Lifecycle Management",
    "D_INTEGRATION": "Pipeline Routing",
    "D_INTEGRATION_GATEWAY": "Integration Gateway",
    "D_MKT_DATA": "Market Data",
    "D_OPS": "Feedback Loop",
    "D_REPORTING": "Reporting",
    "D_SECURITY": "Adversarial Validation",
    "D_SECURITY_LLM": "LLM Defense",
    "D_SHARED": "Shared Services",

    # L1 智能层
    "D_INTELLIGENCE": "Context Management",
    "D_KNOWLEDGE": "Knowledge Management",
    "D_AUTONOMY_CORE": "Autonomy Core",

    # L2 业务域层 - 因子信号
    "D_FACTOR": "Factor",
    "D_SIGLEGACY": "Signal Legacy (Design)",
    "D_ASHARE_SIGNAL": "A-Share Signal",
    "D_FUNDAMENTAL_SIGNAL": "Fundamental Signal",
    "D_SIGQC": "Signal Quality Control",

    # L2 业务域层 - 风险合规
    "D_RISK": "Risk Control",
    "D_COMPLIANCE": "Compliance",
    "D_AUTONOMY_PERM": "Autonomy Protection",

    # L2 业务域层 - 组合决策
    "D_PF_CORE": "Portfolio Core",
    "D_PF_ALLOC": "Portfolio Allocation",
    "D_SELL_DECISION": "Sell Decision",
    "D_CROSS_ASSET": "Cross Asset",
    "D_DIGITAL_TWIN": "Digital Twin",

    # L2 业务域层 - 执行交易
    "D_EX_CORE": "Execution Core",
    "D_EX_SOR": "Execution Routing",
    "D_TRADING": "Trading Operations",
    "D_POSITION": "Position Management",

    # L2 业务域层 - ML平台
    "D_ML_TRAIN": "Training",
    "D_ML_SERVE": "Inference",

    # L2 业务域层 - 回测仿真
    "D_BACKTEST": "Backtest",
    "D_SIMULATION": "Simulation",
    "D_EXEC_SIM": "Execution Simulation",

    # L2 治理域层
    "D_AUDITTEST": "Audit Test Suite",
    "D_GOV_REPAIR": "Governance Repair",
    "D_GOV_AUDIT": "Audit Trail",
    "D_GOV_DOCS": "Architecture Docs Governance",
    "D_GOV_DRIFT": "Drift Detection",
    "D_GOV_ENFORCEMENT": "Rule Enforcement",
    "D_GOV_RULE": "Rule Governance",
    "D_GOV_SCRIPTS": "Script Governance",
}

# 架构层ID → (中文名, 英文名) 映射
LAYER_NAME_BILINGUAL: dict[str, tuple[str, str]] = {
    "L0_infrastructure": ("L0 基础设施层", "L0 Infrastructure"),
    "L1_foundation": ("L1 基础平台层", "L1 Foundation"),
    "L1_platform": ("L1 平台层", "L1 Platform"),
    "L2_domain": ("L2 业务域层", "L2 Domain"),
}

# 模块级缓存：避免重复查询 db（None=未加载，dict=已加载，{}=加载失败回退硬编码）
_DOMAIN_NAME_CACHE: dict[str, str] | None = None


def _load_domain_names_from_db() -> dict[str, str]:
    """从 depgraph (PostgreSQL) domains 表动态加载 domain_id → domain_name 映射。

    延迟 import _shared.constants（避免模块加载时依赖 db 配置）。
    失败时返回空 dict（调用方回退到硬编码 DOMAIN_NAME_ZH）。
    结果缓存到 _DOMAIN_NAME_CACHE，避免重复查询。

    Returns:
        dict[domain_id, domain_name]；失败时返回空 dict。
    """
    global _DOMAIN_NAME_CACHE
    if _DOMAIN_NAME_CACHE is not None:
        return _DOMAIN_NAME_CACHE
    try:
        from _shared.constants import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection()
        cur = conn.execute("SELECT domain_id, domain_name FROM domains")
        result = {
            r["domain_id"]: r["domain_name"]
            for r in cur.fetchall()
            if r["domain_id"] and r["domain_name"]
        }
        conn.close()
        _DOMAIN_NAME_CACHE = result
        return result
    except Exception:
        # db 不可用：标记为空 dict，避免反复尝试失败的连接（进程生命周期内）
        _DOMAIN_NAME_CACHE = {}
        return {}


def preload_domain_names() -> dict[str, str]:
    """预加载 db 域名映射到缓存（批量场景调用一次，避免首次调用延迟）。

    安全调用：db 不可用时静默回退到硬编码映射表。
    """
    return _load_domain_names_from_db()


def get_domain_name_zh(domain_id: str, fallback: str = "") -> str:
    """获取域的中文名称（动态加载 + 硬编码 fallback 双层）。

    真源优先级：
    1. depgraph (PostgreSQL) domains.domain_name（动态加载，真源唯一）
    2. DOMAIN_NAME_ZH 硬编码映射表（fallback）
    3. fallback 参数或 domain_id 本身

    Args:
        domain_id: 域ID，如 "D_TRADING"
        fallback: db 和硬编码都没有时的回退值（通常已无意义，保留向后兼容）

    Returns:
        中文名称字符串
    """
    # 优先从 db 动态加载（真源）
    db_names = _load_domain_names_from_db()
    if domain_id in db_names:
        return db_names[domain_id]
    # 回退到硬编码映射表（db 不可用或测试域）
    return DOMAIN_NAME_ZH.get(domain_id, fallback or domain_id)


def get_domain_name_en(domain_id: str, fallback: str = "") -> str:
    """获取域的英文名称（硬编码真源，db 无对应字段）。

    Args:
        domain_id: 域ID，如 "D_TRADING"
        fallback: 硬编码没有时的回退值

    Returns:
        英文名称字符串
    """
    return DOMAIN_NAME_EN.get(domain_id, fallback or domain_id)


def get_layer_name_bilingual(layer_id: str) -> tuple[str, str]:
    """获取架构层的中英文名称（硬编码真源）。

    Args:
        layer_id: 层ID，如 "L0_infrastructure"

    Returns:
        (中文名, 英文名) 元组；未知层返回 (layer_id, layer_id)
    """
    return LAYER_NAME_BILINGUAL.get(layer_id, (layer_id, layer_id))


def get_domain_name_bilingual(domain_id: str, fallback_zh: str = "", fallback_en: str = "") -> tuple[str, str]:
    """获取域的中英文名称双显（get_domain_name_zh + get_domain_name_en 组合）。

    Args:
        domain_id: 域ID，如 "D_TRADING"
        fallback_zh: 中文名回退值
        fallback_en: 英文名回退值

    Returns:
        (中文名, 英文名) 元组
    """
    zh = get_domain_name_zh(domain_id, fallback_zh)
    en = get_domain_name_en(domain_id, fallback_en)
    return (zh, en)
