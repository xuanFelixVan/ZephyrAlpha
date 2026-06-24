# -*- coding: utf-8 -*-
"""
功能域中文名称映射表 / Functional Domain Chinese Name Mapping

所有生成器通过此模块获取域的中文名称，不直接使用数据库的 domain_name 字段。
数据库 domain_name 字段可能是英文或中文（不一致），此映射表确保显示一致。

用法 / Usage:
    from domain_name_mapping import get_domain_name_zh
    display_name = get_domain_name_zh(domain_id, fallback_name)
"""

# 域ID → 中文名称映射
DOMAIN_NAME_ZH = {
    # L0 基础设施层
    "D-INFRA_OPS": "基础设施运维",
    "D-INFRA_RUNTIME": "运行时集成",

    # L1 基础平台层
    "D-ALT_DATA": "另类数据",
    "D-BEHAVIORAL_AUDIT": "行为审计",
    "D-DATA_ENG": "数据工程",
    "D-DATA_GOV": "数据治理",
    "D-DATA_SEC": "数据安全与契约",
    "D-FRONTEND": "前端",
    "D-GOVERNANCE": "生命周期管理",
    "D-INTEGRATION": "管线路由",
    "D-MKT_DATA": "行情数据",
    "D-OPS": "反馈循环",
    "D-REPORTING": "报告",
    "D-SECURITY": "对抗验证",
    "D-SHARED": "共享服务",

    # L1 智能层
    "D-INTELLIGENCE": "上下文管理",
    "D-KNOWLEDGE": "知识管理",
    "D-AUTONOMY_CORE": "自治核心",

    # L2 业务域层 - 数据
    "D-DIGITAL_TWIN": "数字孪生",

    # L2 业务域层 - 因子信号
    "D-FACTOR": "因子",
    "D-SIGNAL": "信号",
    "D-SIGNAL_ASHARE": "A股特色信号",
    "D-SIGNAL_FUNDAMENTAL": "基本面信号",
    "D-SIGNAL_QUALITY": "信号质量",

    # L2 业务域层 - 风险合规
    "D-RISK": "风控",
    "D-COMPLIANCE": "合规",
    "D-AUTONOMY_PERM": "自治保护",

    # L2 业务域层 - 组合决策
    "D-PF_CORE": "组合核心",
    "D-PF_ALLOC": "组合分配",
    "D-SELL_DECISION": "卖出决策",
    "D-CROSS_ASSET": "跨资产",

    # L2 业务域层 - 执行交易
    "D-EX_CORE": "执行核心",
    "D-EX_SOR": "执行路由",
    "D-TRADING": "交易运营",
    "D-POSITION": "仓位管理",

    # L2 业务域层 - ML平台
    "D-ML_TRAIN": "训练",
    "D-ML_SERVE": "推理",

    # L2 业务域层 - 回测仿真
    "D-BACKTEST": "回测",
    "D-SIMULATION": "仿真",
    "D-EXEC_SIM": "执行仿真",

    # L2 治理域层
    "D-GOV_RULE": "规则治理",
    "D-GOV_AUDIT": "审计追踪",
    "D-GOV_DRIFT": "漂移检测",

    # 测试域
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


def get_domain_name_zh(domain_id: str, fallback: str = "") -> str:
    """
    获取域的中文名称。如果映射表中没有，返回 fallback 或 domain_id。

    Args:
        domain_id: 域ID，如 "D-TRADING"
        fallback: 映射表中没有时的回退值（通常是数据库的 domain_name）

    Returns:
        中文名称字符串
    """
    return DOMAIN_NAME_ZH.get(domain_id, fallback or domain_id)
