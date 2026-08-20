# [BLUEPRINT] MOD-GOV-029 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
# [TTL] permanent
"""
功能域中文名称映射表 / Functional Domain Chinese Name Mapping

真源优先级（治本 v2.4，2026-07-19，Step 2.5 遗留风险修复）：
1. depgraph (PostgreSQL) domains.domain_name（动态加载，真源——已由 sync_yaml_to_depgraph.py
   从 functional_domain_registry.yaml 的 domain_name_zh 字段同步为中文）
2. functional_domain_registry.yaml 的 domain_name_zh（DB 不可用时 fallback——
   确保返回中文 domain_name_zh 而非 domain_id）
3. DOMAIN_NAME_ZH 硬编码映射表（仅含测试域 D-T3-*/D-T4-*/D-T5-*/D-T9-*，
   生产域已全部移除——DB 为唯一真源，硬编码不再保留生产域备份）
4. fallback 参数或 domain_id 本身（DB/YAML/硬编码均无时的最终降级）

治本历史：
- v1.0：硬编码映射表作真源（绕过 db domain_name 英文/中文不一致问题）
- v2.0：apply_depgraph.py --update-domain-name 统一 db domain_name 为中文后，
  改为从 db 动态加载（真源归一），硬编码降为 fallback
- v2.1（2026-07-19 上午）：DB 仍是 63 个英文 subdomain 值（非先前以为的 38 英文+25 中文），
  domain_index 中英文化需要硬编码作权威中文真源，故反转优先级为硬编码优先
- v2.2（2026-07-19 下午）：sync_yaml_to_depgraph.py 改用 domain_name_zh 后跑 sync，
  DB 全 63 域 domain_name 已统一为中文（验证：ON CONFLICT 仅更 5 列，layer_id/lifecycle/
  max_modules/build_status/domain_group 5 个关键字段无漂移）。再次反转为 DB 优先（治本完成）。
- v2.3（2026-07-19 Step 2.5）：DOMAIN_NAME_ZH 瘦身为纯测试域 fallback（73 → 10 entry）。
  63 个生产域从硬编码移除——DB 已是生产域唯一真源，硬编码不再保留生产域备份。
  generate_domain_doc.py 同步重构：移除 DOMAIN_NAME_ZH 直接访问，改走 get_domain_name_zh
  / get_domain_name_zh_strict helper，确保所有路径都过 DB 优先级。
- v2.4（2026-07-19 Step 2.5 遗留风险修复）：新增 _load_domain_names_from_yaml() fallback。
  DB 故障时从 functional_domain_registry.yaml 加载中文（原 v2.3 DB 故障时返回 domain_id，
  如 D_FACTOR 而非"因子"——不优雅）。YAML 是 DB 源头真源，故 fallback 到 YAML 返回中文。
  4 层真源优先级链：DB → YAML → 硬编码（测试域）→ domain_id 降级。

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


# 域ID → 中文名称映射（v2.3 瘦身：仅测试域 fallback，生产域真源在 DB）
# 测试域不插入生产 depgraph (PostgreSQL)（隔离规则），故仅硬编码维护。
# 生产域中文名请通过 sync_yaml_to_depgraph.py 从 YAML 同步到 DB（已是中文）。
DOMAIN_NAME_ZH = {
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
    "D_FEEDBACK_LOOP": "Feedback Loop Engine",
    "D_ORCHESTRATOR": "Agent Orchestrator",
    "D_FBL_VERIFICATION": "Feedback Verification",
    "D_FBL_DIAGNOSERS": "Feedback Diagnosers",
    "D_FBL_DETECTORS": "Feedback Detectors",
    "D_GOV_RULE": "Rule Governance",
    "D_GOV_SCRIPTS": "Script Governance",
    "D_GOV_CODE_QUALITY": "Code Quality Governance",
    "D_GOV_OPS_RESILIENCE": "Ops Resilience Governance",
    # 未分类（DB layer_id 为 NULL 或未归类的手工插入域）
    "D_DATA": "Data Access Layer",
    "D_INFRASTRUCTURE": "Cross-Layer Contract Infrastructure",
}

# 域ID → 中文功能简介映射（用于域文档标题下方的功能简介行）
DOMAIN_DESC_ZH: dict[str, str] = {
    # L0 基础设施层
    "D_INFRA_A2A": "Agent 与 Agent 之间的通信协议层，负责 AI 代理间的消息传递、请求路由和协议适配",
    "D_INFRA_OPS": "资产清单与运维扫描，负责运行时资产盘点、基础设施配置管理和运维自动化",
    "D_INFRA_RECOVERY": "回滚恢复，负责系统故障时的状态回滚、事务补偿和恢复编排",
    "D_INFRA_RUNTIME": "运行时集成，负责组件生命周期编排、启动钩子和运行时上下文管理",
    "D_INFRA_TELEMETRY": "可观测性，负责系统遥测采集、指标监控、链路追踪、日志结构和健康检查",
    # L1 基础平台层
    "D_ALT_DATA": "另类数据，负责非传统金融数据的采集、清洗和标准化",
    "D_BEHAVIORAL_AUDIT": "行为审计，负责 AI 决策行为的可追溯审计和合规检查",
    "D_DATA_ENG": "数据工程，负责数据管道编排、ETL 流程和数据质量监控",
    "D_DATA_GOV": "数据治理，负责数据标准、元数据管理和数据生命周期治理",
    "D_DATA_SEC": "数据安全与契约，负责数据访问控制、加密和跨层契约校验",
    "D_FRONTEND": "前端，负责用户界面展示、交互可视化和前端状态管理",
    "D_GOVERNANCE": "生命周期管理，负责蓝图/模块/任务的声明周期管理和元数据治理",
    "D_INTEGRATION": "管线路由，负责跨域数据流路由、管道编排和集成适配",
    "D_INTEGRATION_GATEWAY": "集成网关，负责外部系统接入、协议转换和请求路由",
    "D_MKT_DATA": "行情数据，负责市场行情数据的采集、分发和订阅管理",
    "D_OPS": "反馈循环，负责系统运行反馈、性能监控和自动调优闭环",
    "D_REPORTING": "报告，负责投资报告、风险报告和合规报告的生成与分发",
    "D_SECURITY": "对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验证",
    "D_SECURITY_LLM": "LLM 防御，负责 LLM 安全防护、Prompt 注入防御和输出过滤",
    "D_SHARED": "共享服务，负责跨域共享的工具、协议和基础服务",
    # L1 智能层
    "D_INTELLIGENCE": "上下文管理，负责 AI 上下文窗口管理、记忆检索和上下文压缩",
    "D_KNOWLEDGE": "知识管理，负责知识库构建、向量索引和知识检索",
    "D_AUTONOMY_CORE": "自治核心，负责 AI 自治决策、目标分解和执行编排",
    # L2 业务域层 - 数据
    "D_DIGITAL_TWIN": "数字孪生，负责市场状态镜像、组合模拟和场景推演",
    # L2 业务域层 - 因子信号
    "D_FACTOR": "因子，负责因子计算、因子库管理和因子评价",
    "D_SIGLEGACY": "信号遗留设计态，负责旧版信号系统的设计态维护和迁移规划",
    "D_ASHARE_SIGNAL": "A 股特色信号，负责 A 股市场特色交易信号的生成和管理",
    "D_FUNDAMENTAL_SIGNAL": "基本面信号，负责基于财务数据的基本面信号生成",
    "D_SIGQC": "信号质量控制，负责信号质量评估、异常检测和质量门禁",
    # L2 业务域层 - 风险合规
    "D_RISK": "风控，负责风险指标计算、风险限额管理和风险预警",
    "D_COMPLIANCE": "合规，负责交易合规检查、规则引擎和合规报告",
    "D_AUTONOMY_PERM": "自治保护，负责 AI 自治行为的权限控制和安全边界",
    # L2 业务域层 - 组合决策
    "D_PF_CORE": "组合核心，负责投资组合构建、持仓管理和组合优化",
    "D_PF_ALLOC": "组合分配，负责资产配置、权重分配和再平衡",
    "D_SELL_DECISION": "卖出决策，负责卖出信号生成、卖出时机判断和退出策略",
    "D_CROSS_ASSET": "跨资产，负责多资产类别投资和跨资产套利策略",
    # L2 业务域层 - 执行交易
    "D_EX_CORE": "执行核心，负责订单执行引擎、执行策略和执行管理",
    "D_EX_SOR": "执行路由，负责订单路由、智能拆单和执行场所选择",
    "D_TRADING": "交易运营，负责交易生命周期管理、订单状态和成交处理",
    "D_POSITION": "仓位管理，负责持仓跟踪、仓位计算和盈亏分析",
    # L2 业务域层 - ML 平台
    "D_ML_TRAIN": "训练，负责模型训练、特征工程和模型评估",
    "D_ML_SERVE": "推理，负责模型部署、在线推理和模型服务管理",
    # L2 业务域层 - 回测仿真
    "D_BACKTEST": "回测，负责历史数据回测、回测引擎和回测报告",
    "D_SIMULATION": "仿真，负责市场仿真、模拟撮合和仿真环境管理",
    "D_EXEC_SIM": "执行仿真，负责执行过程仿真、滑点模拟和冲击成本建模",
    # L2 治理域层
    "D_AUDITTEST": "审计测试套件，负责审计测试用例管理和测试执行",
    "D_GOV_REPAIR": "治理修复，负责治理问题自动修复和修复策略管理",
    "D_GOV_AUDIT": "审计追踪，负责变更审计追踪和操作日志管理",
    "D_GOV_DOCS": "架构文档治理，负责架构文档生成、一致性和版本管理",
    "D_GOV_DRIFT": "漂移检测，负责架构漂移检测和漂移告警",
    "D_GOV_ENFORCEMENT": "规则执行，负责治理规则执行和门禁拦截",
    "D_FEEDBACK_LOOP": "反馈循环引擎，负责系统自我改进闭环：异常检测、根因诊断、自动修复和自我进化",
    "D_ORCHESTRATOR": "代理编排器，负责 Agent 任务全生命周期：任务入队、调度、沙箱执行、幻觉检测和收尾归档",
    "D_FBL_VERIFICATION": "反馈验证，负责反馈循环门禁拦截、结果验证器执行和反馈质量检查",
    "D_FBL_DIAGNOSERS": "反馈诊断器，负责异常根因诊断、模型健康监控、可靠性诊断和上下文窗口压力管理",
    "D_FBL_DETECTORS": "反馈检测器，负责异常检测、漂移检测、反馈信号检测和可靠性监控",
    "D_GOV_RULE": "规则治理，负责规则注册、规则版本和规则依赖管理",
    "D_GOV_SCRIPTS": "脚本治理，负责脚本生命周期管理和脚本质量门禁",
    "D_GOV_CODE_QUALITY": "代码质量治理，负责代码去重引擎、函数重复检测、AST语义分析和提交门禁引擎",
    "D_GOV_OPS_RESILIENCE": "运维弹性治理，负责运维治理、安全治理、弹性治理和升级协议",
    # 未分类（DB layer_id 为 NULL 或未归类的手工插入域，裁定#199/#200/#204）
    "D_DATA": "数据接入层，负责数据源接入、数据集成和数据标准化",
    "D_INFRASTRUCTURE": "跨层契约基础设施，负责跨层契约定义、共享契约管理和契约校验",
}


def get_domain_desc_zh(domain_id: str) -> str:
    """获取域的中文功能简介（硬编码真源，用于域文档标题下方）。

    Args:
        domain_id: 域ID，如 "D_INFRA_TELEMETRY"

    Returns:
        中文功能简介字符串；未知域返回空字符串
    """
    return DOMAIN_DESC_ZH.get(domain_id, "")


# 架构层ID → (中文名, 英文名) 映射
LAYER_NAME_BILINGUAL: dict[str, tuple[str, str]] = {
    "L0_infrastructure": ("L0 基础设施层", "L0 Infrastructure"),
    "L1_foundation": ("L1 基础平台层", "L1 Foundation"),
    "L1_platform": ("L1 平台层", "L1 Platform"),
    "L2_domain": ("L2 业务域层", "L2 Domain"),
}

# 模块级缓存：避免重复查询 db（None=未加载，dict=已加载，{}=加载失败回退硬编码）
_DOMAIN_NAME_CACHE: dict[str, str] | None = None
# YAML fallback 缓存（#ARCH-SSOT-GLOSSARY-MERGE-001：遗留域不在 DB，从 YAML 补查）
_YAML_NAMES_CACHE: dict[str, str] | None = None


def _load_domain_names_from_yaml() -> dict[str, str]:
    """从 functional_domain_registry.yaml 加载 domain_id → domain_name_zh 映射。

    作为 DB 不可用时的 fallback（治本 v2.4，2026-07-19 Step 2.5 遗留风险修复）。
    YAML 是 DB 的源头真源（sync_yaml_to_depgraph.py 从 YAML sync 到 DB），
    故 DB 不可用时从 YAML 加载是正确的降级路径——返回中文 domain_name_zh 而非 domain_id。

    Returns:
        dict[domain_id, domain_name_zh]；失败时返回空 dict。
    """
    global _YAML_NAMES_CACHE
    if _YAML_NAMES_CACHE is not None:
        return _YAML_NAMES_CACHE
    try:
        import yaml  # type: ignore[import-untyped]
        from _shared.constants import REPO_ROOT

        yaml_path = (
            REPO_ROOT
            / "docs"
            / "01_policies_and_standards"
            / "_registry"
            / "catalogs"
            / "functional_domain_registry.yaml"
        )
        if not yaml_path.exists():
            return {}
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        entries = data.get("entries", [])
        result: dict[str, str] = {}
        for entry in entries:
            domain_id = entry.get("domain", "")
            name_zh = entry.get("domain_name_zh", "")
            if domain_id and name_zh:
                if domain_id not in result:
                    result[domain_id] = name_zh
        _YAML_NAMES_CACHE = result
        return result
    except Exception:
        return {}


def _load_domain_names_from_db() -> dict[str, str]:
    """从 depgraph (PostgreSQL) domains 表动态加载 domain_id → domain_name 映射。

    真源优先级（治本 v2.4）：
    1. depgraph (PostgreSQL) domains.domain_name（真源——已由 sync_yaml_to_depgraph.py
       从 YAML 的 domain_name_zh 字段同步为中文）
    2. functional_domain_registry.yaml 的 domain_name_zh（DB 不可用时 fallback——
       确保返回中文 domain_name_zh 而非 domain_id）
    3. 空 dict → 调用方回退到硬编码 DOMAIN_NAME_ZH（仅测试域）

    延迟 import _shared.constants（避免模块加载时依赖 db 配置）。
    结果缓存到 _DOMAIN_NAME_CACHE，避免重复查询。

    Returns:
        dict[domain_id, domain_name]；DB 和 YAML 均不可用时返回空 dict。
    """
    global _DOMAIN_NAME_CACHE
    if _DOMAIN_NAME_CACHE is not None:
        return _DOMAIN_NAME_CACHE
    # 1. 优先从 DB 加载
    try:
        from _shared.constants import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection()
        cur = conn.execute("SELECT domain_id, domain_name FROM domains")
        result = {r["domain_id"]: r["domain_name"] for r in cur.fetchall() if r["domain_id"] and r["domain_name"]}
        conn.close()
        _DOMAIN_NAME_CACHE = result
        return result
    except Exception:
        # 2. DB 不可用：fallback 到 YAML（确保返回中文 domain_name_zh 而非 domain_id）
        yaml_result = _load_domain_names_from_yaml()
        if yaml_result:
            _DOMAIN_NAME_CACHE = yaml_result
            return yaml_result
        # 3. YAML 也不可用：返回空 dict（调用方回退到硬编码 DOMAIN_NAME_ZH）
        _DOMAIN_NAME_CACHE = {}
        return {}


def preload_domain_names() -> dict[str, str]:
    """预加载 db 域名映射到缓存（批量场景调用一次，避免首次调用延迟）。

    安全调用：db 不可用时静默回退到硬编码映射表。
    """
    return _load_domain_names_from_db()


def get_domain_name_zh(domain_id: str, fallback: str = "") -> str:
    """获取域的中文名称（DB 优先 + 硬编码 fallback 双层）。

    真源优先级（治本 v2.4，2026-07-19 Step 2.5 遗留风险修复）：
    1. depgraph (PostgreSQL) domains.domain_name（动态加载，真源——
       已由 sync_yaml_to_depgraph.py 从 YAML 的 domain_name_zh 字段同步为中文）
    2. functional_domain_registry.yaml 的 domain_name_zh（DB 不可用时 fallback——
       确保返回中文 domain_name_zh 而非 domain_id）
    3. DOMAIN_NAME_ZH 硬编码映射表（仅含测试域 D-T3-*/D-T4-*/D-T5-*/D-T9-*）
    4. fallback 参数或 domain_id 本身（DB/YAML/硬编码均无时的最终降级）

    Args:
        domain_id: 域ID，如 "D_TRADING"
        fallback: db 和硬编码都没有时的回退值

    Returns:
        中文名称字符串
    """
    # v2.2：优先从 db 动态加载（真源——sync 后全 63 域 domain_name 已统一为中文）
    db_names = _load_domain_names_from_db()
    if domain_id in db_names:
        return db_names[domain_id]
    # YAML fallback：DB 连接成功但域不在 DB（如遗留域 stability=deprecated 未 sync）
    yaml_names = _load_domain_names_from_yaml()
    if domain_id in yaml_names:
        return yaml_names[domain_id]
    # 回退到硬编码映射表（v2.3：仅测试域；生产域 DB 不可用时返回 fallback/domain_id）
    return DOMAIN_NAME_ZH.get(domain_id, fallback or domain_id)


def get_domain_name_zh_strict(domain_id: str) -> str:
    """获取域的中文名称，未找到返回空字符串（严格模式）。

    与 ``get_domain_name_zh`` 的区别：未找到时返回 ``""`` 而非 ``domain_id``，
    用于"未找到=不显示"场景（如 mermaid 标签、表格单元格）。
    v2.3（Step 2.5）新增：替代 generate_domain_doc.py 中直接的
    ``DOMAIN_NAME_ZH.get(ext, "")`` 调用，确保路径过 DB 优先级。
    v2.4：DB 不可用时通过 YAML fallback 返回中文（4 层真源优先级链）。

    Args:
        domain_id: 域ID，如 "D_TRADING"

    Returns:
        中文名称字符串；未找到返回空字符串
    """
    db_names = _load_domain_names_from_db()
    if domain_id in db_names:
        return db_names[domain_id]
    # YAML fallback：DB 连接成功但域不在 DB（如遗留域 stability=deprecated 未 sync）
    yaml_names = _load_domain_names_from_yaml()
    if domain_id in yaml_names:
        return yaml_names[domain_id]
    return DOMAIN_NAME_ZH.get(domain_id, "")


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
