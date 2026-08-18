#!/usr/bin/env python
# [BLUEPRINT] MOD-GOV_DEFERRED_REG | docs/_working/2026-07-28-three_systems_upgrade_plan.md | §8
# [MODULE] scripts.governance.register_deferred_modules
# [DOMAIN] D_GOV_SCRIPTS
# [STARTUP] manual
# [MATURITY] production
# [SAFETY] H
# [A_module] module_id=MOD-GOV_DEFERRED_REG | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
将42项暂缓模块写入 depgraph 设计态，含3图对齐设计。

3图对齐机制：
  1. depgraph: 本脚本写入节点(path/blueprint_id/domain/build_status/can_build/gate_reason)
  2. dataflowgraph: add_design_node 自动调用 sync_module_panorama() 派生 placeholder
  3. decisiongraph: 同上，自动派生 placeholder
  4. 验证: 运行 align_panoramas.py 确认孤儿/状态漂移/域不一致/设计态孤立清零

分类:
  Category A (17项): 已注册为目录级设计态节点，仅更新 gate_reason/can_build/module_name_cn/description_cn
  Category B (25项): 未注册，需 add_design_node + 更新元数据
  Category C (3项): 已被生产代码覆盖，跳过 (D-DATA-ENG-04/05/08)
"""
from __future__ import annotations

__manifest__ = """
args: []
description: 将42项暂缓模块写入 depgraph 设计态，含3图对齐设计。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT), str(_REPO_ROOT / "src"), str(_REPO_ROOT / "scripts" / "governance")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection, release_depgraph_pg_connection

# ============================================================
# 模块数据定义（3图设计的核心）
# ============================================================
# 每个模块包含:
#   path: depgraph 节点路径
#   blueprint_id: MOD-* 格式
#   domain_id: D_BACKTEST / D_FACTOR / D_DATA / D_DATA_ENG
#   build_status: 'planned' (暂缓/未建)
#   can_build: 0(受限不可建) / 1(P2可建不急)
#   gate_reason: 暂缓原因
#   module_name_cn: 中文名称
#   description_cn: 功能简介
#   exists: True=已注册(Category A) / False=需新增(Category B)
#   granularity: 'directory' / 'module' (新增节点用)

# --- Category A: 已注册，仅更新元数据 (17项) ---
CATEGORY_A = [
    # FAC-* A股因子子模块 (9项, 受限, can_build=0)
    {"path": "src/zephyr/factor/ashare/microstructure/", "exists": True,
     "module_name_cn": "微观结构因子", "can_build": 0,
     "gate_reason": "受限：需Level-2逐笔成交数据(GATE-27-01)",
     "description_cn": "基于Level-2逐笔成交数据计算微观结构因子(买卖压力不平衡/成交单大小分布/大单净买入比例)"},
    {"path": "src/zephyr/factor/ashare/intraday/", "exists": True,
     "module_name_cn": "日内因子", "can_build": 0,
     "gate_reason": "受限：需3秒Tick管线稳定运行(GATE-29-01)",
     "description_cn": "基于3秒Tick数据计算日内因子(开盘冲击/尾盘异常/盘中动量)"},
    {"path": "src/zephyr/factor/ashare/smc/", "exists": True,
     "module_name_cn": "SMC因子", "can_build": 0,
     "gate_reason": "受限：GATE-55-01~02未解除",
     "description_cn": "Smart Money Concepts智能资金概念因子(订单块/公平价值缺口/流动性池)"},
    {"path": "src/zephyr/factor/ashare/irl/", "exists": True,
     "module_name_cn": "IRL因子", "can_build": 0,
     "gate_reason": "受限：GATE-56-01未解除",
     "description_cn": "逆强化学习因子(从市场行为反推机构隐含策略)"},
    {"path": "src/zephyr/factor/ashare/alpha87/", "exists": True,
     "module_name_cn": "87-Alpha因子", "can_build": 0,
     "gate_reason": "受限：GATE-92-01未解除",
     "description_cn": "WorldQuant 87因子全集实现(从经典Alpha#1~#177中筛选87个有效因子)"},
    {"path": "src/zephyr/factor/ashare/pattern_signal/", "exists": True,
     "module_name_cn": "形态转信号", "can_build": 0,
     "gate_reason": "受限：GATE-97-01未解除",
     "description_cn": "K线形态识别(头肩顶/双底/三角形等)转化为量化信号"},
    {"path": "src/zephyr/factor/ashare/institutional/", "exists": True,
     "module_name_cn": "机构行为因子", "can_build": 0,
     "gate_reason": "受限：需商业数据源龙虎榜+北向+大宗数据(GATE-100-01，原iFind已退役)",
     "description_cn": "基于龙虎榜+北向资金+大宗交易计算机构行为因子(筹码集中度/机构净流入/龙虎榜机构占比/北向持仓变化)"},
    {"path": "src/zephyr/factor/ashare/cross_market/", "exists": True,
     "module_name_cn": "跨市场因子", "can_build": 0,
     "gate_reason": "受限：需商业数据源全球市场数据(GATE-102-01，原iFind已退役)",
     "description_cn": "跨市场传导因子(VIX恐慌指数/美债利差/汇率波动/A50期货溢价对A股传导效应)"},
    {"path": "src/zephyr/factor/ashare/ps_liquidity/", "exists": True,
     "module_name_cn": "流动性因子", "can_build": 0,
     "gate_reason": "受限：需商业数据源全球市场数据+统计回归库(GATE-106-01，原iFind已退役)",
     "description_cn": "Pastor-Stambaugh系统性流动性风险因子(市场流动性溢价的度量)"},
    # D-FACTOR-05~24 因子域主模块 (7项, 受限, can_build=0)
    {"path": "src/zephyr/factor/mine/mining_agent/", "exists": True,
     "module_name_cn": "因子挖掘智能体", "can_build": 0,
     "gate_reason": "受限：需GPU硬件+多Agent框架(GATE-05-01~03)",
     "description_cn": "并发AI因子挖掘(多Agent并行生成因子假设→投票选最优)+相关性去重+自动验证闭环+自动入库"},
    {"path": "src/zephyr/factor/barra/risk_model/", "exists": True,
     "module_name_cn": "Barra风险模型", "can_build": 0,
     "gate_reason": "受限：需付费Barra数据(GATE-06-01~03)",
     "description_cn": "Barra风格因子(10大)+行业因子(28申万)+正交化+因子中性化(行业/市值/风格中性)"},
    {"path": "src/zephyr/factor/governance/engine/", "exists": True,
     "module_name_cn": "因子治理引擎(完整版)", "can_build": 0,
     "gate_reason": "受限：完整版需39类漂移检测器(GATE-07-01~03)，基础版engine.py已实现",
     "description_cn": "因子准入门禁+运行时监控+废弃审批+39类漂移检测器+因子-模型联合优化"},
    {"path": "src/zephyr/factor/analysis/correlation_analyzer/", "exists": True,
     "module_name_cn": "因子相关性分析器(完整版)", "can_build": 0,
     "gate_reason": "受限：完整版需LLM语义判断(GATE-09-01~02)，基础版correlation_analyzer.py已实现",
     "description_cn": "滚动相关矩阵+条件相关性+聚类分析+共线性检测(VIF)+LLM语义去重"},
    {"path": "src/zephyr/factor/barra/exposure_calculator/", "exists": True,
     "module_name_cn": "因子暴露计算器", "can_build": 0,
     "gate_reason": "受限：需D-FACTOR-06 Barra风险模型就绪(GATE-11-01)",
     "description_cn": "实时因子暴露(L1<1秒/Tick)+截面因子暴露+行业偏离+风格暴露约束"},
    {"path": "src/zephyr/factor/barra/risk_budget_allocator/", "exists": True,
     "module_name_cn": "因子风险预算分配器", "can_build": 0,
     "gate_reason": "受限：需06+11就绪+D-RISK域就绪(GATE-24-01~02)",
     "description_cn": "按因子IC/IR分配风险预算+因子暴露约束+风险限额检查"},
    # D_DATA 域 (2项, can_build=1)
    {"path": "src/zephyr/data/feature_store/", "exists": True,
     "module_name_cn": "特征存储", "can_build": 1,
     "gate_reason": "暂缓：独立大模块，当前因子值直接存ClickHouse可行",
     "description_cn": "PIT查询(DuckDB AS OF JOIN)+特征版本管理+特征服务API+在线/离线存储分离"},
    {"path": "src/zephyr/data/data_observability/", "exists": True,
     "module_name_cn": "数据可观测性平台", "can_build": 1,
     "gate_reason": "暂缓：P2优先级",
     "description_cn": "健康度监控+根因分析+SLA追踪，全链路数据质量监控"},
]

# --- Category B: 需新增设计态节点 (25项) ---
CATEGORY_B = [
    # BT-18~26 回测域辅助模块 (9项)
    {"path": "src/zephyr/backtest/services/decay_monitor.py", "exists": False,
     "blueprint_id": "MOD-BT-018", "domain_id": "D_BACKTEST", "granularity": "module",
     "module_name_cn": "策略衰减监控告警器", "can_build": 1,
     "gate_reason": "暂缓：因子侧decay_monitor已覆盖IC衰减监控",
     "description_cn": "监控策略实盘收益vs回测收益的偏离趋势，实盘收益持续低于回测预期时发出衰减告警"},
    {"path": "src/zephyr/backtest/services/report_generator.py", "exists": False,
     "blueprint_id": "MOD-BT-019", "domain_id": "D_BACKTEST", "granularity": "module",
     "module_name_cn": "回测报告自动生成器", "can_build": 1,
     "gate_reason": "暂缓：P2优先级，当前无报告展示需求",
     "description_cn": "自动生成回测报告(PDF/HTML)，含净值曲线/回撤分析/交易明细/绩效归因"},
    {"path": "src/zephyr/backtest/services/cache_manager.py", "exists": False,
     "blueprint_id": "MOD-BT-020", "domain_id": "D_BACKTEST", "granularity": "module",
     "module_name_cn": "回测缓存管理器", "can_build": 1,
     "gate_reason": "暂缓：P2优先级，当前回测量不大",
     "description_cn": "缓存回测中间结果与最终结果，相同参数组合直接复用避免重复计算"},
    {"path": "src/zephyr/backtest/services/param_analyzer.py", "exists": False,
     "blueprint_id": "MOD-BT-021", "domain_id": "D_BACKTEST", "granularity": "module",
     "module_name_cn": "参数优化结果分析器", "can_build": 1,
     "gate_reason": "暂缓：scheduler已含best/worst/mean摘要",
     "description_cn": "分析参数网格搜索结果的参数显著性(t统计量)与过拟合风险(参数敏感性)"},
    {"path": "src/zephyr/backtest/services/data_quality_checker.py", "exists": False,
     "blueprint_id": "MOD-BT-022", "domain_id": "D_BACKTEST", "granularity": "module",
     "module_name_cn": "回测数据质量检查器", "can_build": 1,
     "gate_reason": "暂缓：data域已有quality_gate+integrity_checker",
     "description_cn": "回测前检查输入数据质量：缺失日期检测/异常值检测/数据连续性验证"},
    {"path": "src/zephyr/backtest/services/anomaly_diagnoser.py", "exists": False,
     "blueprint_id": "MOD-BT-023", "domain_id": "D_BACKTEST", "granularity": "module",
     "module_name_cn": "回测异常诊断器", "can_build": 1,
     "gate_reason": "暂缓：P2优先级，当前回测失败率低",
     "description_cn": "回测失败时自动诊断错误原因并给出修复建议(数据缺失/参数越界/引擎异常)"},
    {"path": "src/zephyr/backtest/services/result_comparator.py", "exists": False,
     "blueprint_id": "MOD-BT-024", "domain_id": "D_BACKTEST", "granularity": "module",
     "module_name_cn": "回测结果对比器", "can_build": 1,
     "gate_reason": "暂缓：P2优先级，当前无多次对比需求",
     "description_cn": "对比多次回测结果的差异(参数变化/数据更新/策略迭代带来的收益变化)"},
    {"path": "src/zephyr/backtest/services/result_deployer.py", "exists": False,
     "blueprint_id": "MOD-BT-025", "domain_id": "D_BACKTEST", "granularity": "module",
     "module_name_cn": "回测结果一键部署器", "can_build": 0,
     "gate_reason": "受限：涉及实盘安全，需D-EX-CORE执行域就绪",
     "description_cn": "将通过验证的回测策略一键部署到实盘环境(参数迁移+风控配置+监控初始化)"},
    {"path": "src/zephyr/backtest/services/nan_processor.py", "exists": False,
     "blueprint_id": "MOD-BT-026", "domain_id": "D_BACKTEST", "granularity": "module",
     "module_name_cn": "指标计算NaN处理器", "can_build": 1,
     "gate_reason": "暂缓：P2优先级，当前数据缺失率低",
     "description_cn": "智能处理指标计算中的NaN值(前向填充/插值/剔除)，避免NaN传播导致绩效指标失真"},
    # D-FACTOR-10 换手率分析器 (1项)
    {"path": "src/zephyr/factor/analysis/turnover_analyzer/", "exists": False,
     "blueprint_id": "MOD-L02-001", "domain_id": "D_FACTOR", "granularity": "directory",
     "module_name_cn": "因子换手率分析器", "can_build": 0,
     "gate_reason": "受限：P2优先级(GATE-10-01~02)",
     "description_cn": "换手率计算+成本衰减模型+自相关系数+买卖价差估算"},
    # D-DATA-04, D-DATA-20 数据域 (2项)
    {"path": "src/zephyr/data/realtime_push_manager/", "exists": False,
     "blueprint_id": "MOD-L00-004", "domain_id": "D_DATA", "granularity": "directory",
     "module_name_cn": "实时行情推送管理器", "can_build": 0,
     "gate_reason": "受限：需Kafka/Flink流处理基础设施",
     "description_cn": "管理实时行情数据流(WebSocket/TCP推送)，支持多订阅者+断线重连+数据校验"},
    {"path": "src/zephyr/data/tick_data_manager/", "exists": False,
     "blueprint_id": "MOD-L00-004", "domain_id": "D_DATA", "granularity": "directory",
     "module_name_cn": "Tick数据管理器", "can_build": 0,
     "gate_reason": "受限：需Level-2数据源授权",
     "description_cn": "管理Level-2 Tick数据(采集/存储/清洗/重放)，支持秒级和逐笔数据"},
    # D-DATA-ENG-06~07,09~18,20 数据工程域 (13项)
    {"path": "src/zephyr/data_eng/services/stream_processing/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "流处理引擎", "can_build": 0,
     "gate_reason": "受限：需Kafka/Flink基础设施",
     "description_cn": "实时计算+窗口聚合+事件时间对齐+水位线+背压控制"},
    {"path": "src/zephyr/data_eng/services/drift_aware_scheduler/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "漂移感知调度器", "can_build": 1,
     "gate_reason": "暂缓：P1优先级，需D-AUTONOMY就绪",
     "description_cn": "ADWIN/DDM漂移检测+共形漂移检测+多尺度漂移检测+双层优化"},
    {"path": "src/zephyr/data_eng/services/training_data_manager/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "训练数据管理器", "can_build": 1,
     "gate_reason": "暂缓：P1优先级，需D-ML-TRAIN就绪",
     "description_cn": "训练数据版本管理+质量检查+数据增强+分层采样"},
    {"path": "src/zephyr/data_eng/services/knowledge_cleaning/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "知识清洗流水线", "can_build": 1,
     "gate_reason": "暂缓：P1优先级，需D-KNOWLEDGE就绪",
     "description_cn": "格式转换+去重+去噪+术语标准化+说话人分离+信息价值评分"},
    {"path": "src/zephyr/data_eng/services/gpu_resource_manager/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "GPU资源管理器", "can_build": 1,
     "gate_reason": "暂缓：P1优先级，需GPU硬件",
     "description_cn": "PyTorch CUDA内存分区+时段优先调度+显存预算管理+OOM防护"},
    {"path": "src/zephyr/data_eng/services/data_lake_manager/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "数据湖管理器", "can_build": 1,
     "gate_reason": "暂缓：P2优先级",
     "description_cn": "分层存储(热/温/冷)+生命周期管理+自动分层迁移"},
    {"path": "src/zephyr/data_eng/services/data_compression/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "数据压缩归档", "can_build": 1,
     "gate_reason": "暂缓：P2优先级",
     "description_cn": "冷热分离+自动归档(Parquet/ZSTD压缩)"},
    {"path": "src/zephyr/data_eng/services/schema_evolution/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "Schema演进管理器", "can_build": 1,
     "gate_reason": "暂缓：P2优先级",
     "description_cn": "Schema演进+兼容性检查(前向/后向)+自动迁移"},
    {"path": "src/zephyr/data_eng/services/data_replication/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "数据复制同步", "can_build": 1,
     "gate_reason": "暂缓：P2优先级",
     "description_cn": "跨源同步+一致性保证(CDC/Debezium)"},
    {"path": "src/zephyr/data_eng/services/data_profiling/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "数据画像", "can_build": 1,
     "gate_reason": "暂缓：P2优先级",
     "description_cn": "统计分布+异常检测+数据质量评分"},
    {"path": "src/zephyr/data_eng/services/data_catalog/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "数据目录同步", "can_build": 1,
     "gate_reason": "暂缓：P2优先级",
     "description_cn": "元数据自动采集+搜索(DataHub集成)"},
    {"path": "src/zephyr/data_eng/services/synthetic_data/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "合成数据生成器", "can_build": 1,
     "gate_reason": "暂缓：P2优先级",
     "description_cn": "SMOTE过采样+轻量GAN生成合成行情数据(仅训练增强)"},
    {"path": "src/zephyr/data_eng/services/data_product_manager/", "exists": False,
     "blueprint_id": "MOD-DATA_ENG", "domain_id": "D_DATA_ENG", "granularity": "directory",
     "module_name_cn": "数据产品管理器", "can_build": 1,
     "gate_reason": "暂缓：P2优先级",
     "description_cn": "产品定义+目录+版本+评估+退役"},
]


# ============================================================
# 辅助函数
# ============================================================

def _update_metadata_direct(path: str, gate_reason: str, can_build: int,
                            module_name_cn: str, description_cn: str) -> bool:
    """直接更新 nodes_metadata 表的 gate_reason/can_build/module_name_cn/description_cn。

    update_module_metadata CLI 仅支持 4 个字段(module_name_cn/en, description_cn/en)，
    不支持 gate_reason 和 can_build，因此用直接 SQL 更新 nodes_metadata。

    nodes_metadata 是受保护字段的 SSoT（裁定#209 Stage 2），
    write_depgraph_to_db 会从中恢复空字段到 nodes 表。
    """
    conn = get_depgraph_pg_connection(read_only=False)
    try:
        cur = conn.cursor()
        # UPSERT nodes_metadata
        cur.execute("""
            INSERT INTO nodes_metadata (path, gate_reason, module_name_cn, description_cn)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (path) DO UPDATE SET
                gate_reason = EXCLUDED.gate_reason,
                module_name_cn = EXCLUDED.module_name_cn,
                description_cn = EXCLUDED.description_cn
        """, (path, gate_reason, module_name_cn, description_cn))
        # 同步更新 nodes 表的 can_build 和 gate_reason（保持一致）
        cur.execute("""
            UPDATE nodes SET can_build = %s, gate_reason = %s
            WHERE path = %s
        """, (can_build, gate_reason, path))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"  [ERROR] 更新元数据失败 path={path}: {e}")
        return False
    finally:
        release_depgraph_pg_connection(conn)


def _add_design_node(path: str, blueprint_id: str, domain_id: str,
                     build_status: str, granularity: str) -> int:
    """调用 apply_depgraph.add_design_node 新增设计态节点。返回 node_id。"""
    try:
        # 导入 apply_depgraph 的函数
        import apply_depgraph
        node_id = apply_depgraph.add_design_node(
            path, blueprint_id, domain_id, build_status, granularity=granularity
        )
        return node_id
    except Exception as e:
        print(f"  [ERROR] add_design_node 失败 path={path}: {e}")
        return -1


def _query_node_id(path: str) -> int | None:
    """查询已有节点的 node_id。"""
    conn = get_depgraph_pg_connection(read_only=True)
    try:
        cur = conn.cursor()
        cur.execute("SELECT node_id FROM nodes WHERE path = %s LIMIT 1", (path,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        release_depgraph_pg_connection(conn)


# ============================================================
# 主流程
# ============================================================

def main():
    """Entry point: parse args, run logic, return exit code."""
    print("=" * 70)
    print("暂缓模块写入 depgraph 设计态 — 3图对齐")
    print("=" * 70)

    stats = {"A_updated": 0, "A_failed": 0, "B_added": 0, "B_failed": 0, "B_meta_failed": 0}

    # --- Category A: 更新已注册节点的元数据 ---
    print(f"\n--- Category A: 更新 {len(CATEGORY_A)} 个已注册节点的元数据 ---")
    for i, mod in enumerate(CATEGORY_A, 1):
        path = mod["path"]
        print(f"  [{i}/{len(CATEGORY_A)}] {mod['module_name_cn']} ({path})")
        ok = _update_metadata_direct(
            path, mod["gate_reason"], mod["can_build"],
            mod["module_name_cn"], mod["description_cn"]
        )
        if ok:
            stats["A_updated"] += 1
        else:
            stats["A_failed"] += 1

    # --- Category B: 新增设计态节点 + 更新元数据 ---
    print(f"\n--- Category B: 新增 {len(CATEGORY_B)} 个设计态节点 ---")
    new_node_ids: list[tuple[str, int]] = []
    for i, mod in enumerate(CATEGORY_B, 1):
        path = mod["path"]
        bp = mod["blueprint_id"]
        dom = mod["domain_id"]
        gran = mod["granularity"]
        print(f"  [{i}/{len(CATEGORY_B)}] {mod['module_name_cn']} ({bp} → {path})")

        # 检查是否已存在（避免重复添加）
        existing_id = _query_node_id(path)
        if existing_id is not None:
            print(f"    → 节点已存在(node_id={existing_id})，跳过添加，仅更新元数据")
            node_id = existing_id
        else:
            node_id = _add_design_node(path, bp, dom, "planned", gran)
            if node_id < 0:
                stats["B_failed"] += 1
                continue
            print(f"    → 新增成功 node_id={node_id}")
            stats["B_added"] += 1
            new_node_ids.append((path, node_id))

        # 更新元数据
        ok = _update_metadata_direct(
            path, mod["gate_reason"], mod["can_build"],
            mod["module_name_cn"], mod["description_cn"]
        )
        if not ok:
            stats["B_meta_failed"] += 1

    # --- 汇总 ---
    print("\n" + "=" * 70)
    print("执行汇总")
    print("=" * 70)
    print(f"  Category A (已注册更新):  成功={stats['A_updated']}  失败={stats['A_failed']}")
    print(f"  Category B (新增节点):    成功={stats['B_added']}  失败={stats['B_failed']}  元数据失败={stats['B_meta_failed']}")
    print("  Category C (已覆盖跳过):  3项 (D-DATA-ENG-04/05/08)")
    print("\n  下一步: 运行 sync_panorama_module.py --all 派生 dataflow/decision 图")
    print("  然后:   运行 align_panoramas.py 验证4类对齐问题清零")

    if stats["A_failed"] > 0 or stats["B_failed"] > 0:
        print("\n  ⚠️ 有失败项，请检查上方 [ERROR] 日志")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
