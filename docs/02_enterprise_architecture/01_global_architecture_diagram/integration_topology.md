# 集成拓扑图

> **文档作用 / Purpose**: 展示系统间集成关系和数据流向，包括API调用、事件订阅、数据同步等集成方式。

> 自动生成时间: 2026-07-06 18:02:32
> 数据源: depgraph (PostgreSQL) edges表（跨域依赖）
> 跨域依赖对数: 175

```mermaid

%% 所有功能域集成依赖关系图
%% 生成时间: 2026-07-06 18:02:32
%% 数据源: depgraph (PostgreSQL) edges表（跨域依赖）
%% 跨域依赖对数: 175

graph LR

    %% 功能域节点（按架构层分组）
    subgraph L0_infrastructure[L0_infrastructure]
        D_INFRA_A2A["D_INFRA_A2A<br/>a2a_communication<br/>(92模块)"]
        D_INFRA_OPS["D_INFRA_OPS<br/>asset-inventory<br/>(1模块)"]
        D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>rollback_recovery<br/>(54模块)"]
        D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>runtime_core<br/>(149模块)"]
        D_INFRA_TELEMETRY["D_INFRA_TELEMETRY<br/>observability_profiling<br/>(25模块)"]
    end
    subgraph L1_foundation[L1_foundation]
        D_ALT_DATA["D_ALT_DATA<br/>另类数据<br/>(7模块)"]
        D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>agent_lifecycle<br/>(114模块)"]
        D_DATA_ENG["D_DATA_ENG<br/>数据工程<br/>(7模块)"]
        D_DATA_GOV["D_DATA_GOV<br/>数据治理<br/>(7模块)"]
        D_DATA_SEC["D_DATA_SEC<br/>数据安全与契约<br/>(7模块)"]
        D_FRONTEND["D_FRONTEND<br/>前端<br/>(30模块)"]
        D_INTEGRATION["D_INTEGRATION<br/>pipeline_routing<br/>(72模块)"]
        D_INTEGRATION_GATEWAY["D_INTEGRATION_GATEWAY<br/>mcp_servers<br/>(20模块)"]
        D_MKT_DATA["D_MKT_DATA<br/>行情数据<br/>(7模块)"]
        D_OPS["D_OPS<br/>telemetry<br/>(3模块)"]
        D_REPORTING["D_REPORTING<br/>报告<br/>(10模块)"]
        D_SECURITY["D_SECURITY<br/>orphan_judge<br/>(147模块)"]
        D_SECURITY_LLM["D_SECURITY_LLM<br/>llm_defense<br/>(44模块)"]
        D_SHARED["D_SHARED<br/>shared_services<br/>(228模块)"]
    end
    subgraph L2_domain[L2_domain]
        D_ASHARE_SIGNAL["D_ASHARE_SIGNAL<br/>ashare_signal<br/>(7模块)"]
        D_AUDITTEST["D_AUDITTEST<br/>audit_test_suite<br/>(1720模块)"]
        D_AUTONOMY_PERM["D_AUTONOMY_PERM<br/>budget_enforcement<br/>(14模块)"]
        D_BACKTEST["D_BACKTEST<br/>回测<br/>(33模块)"]
        D_CROSS_ASSET["D_CROSS_ASSET<br/>跨资产<br/>(8模块)"]
        D_DIGITAL_TWIN["D_DIGITAL_TWIN<br/>数字孪生<br/>(8模块)"]
        D_EXEC_SIM["D_EXEC_SIM<br/>执行仿真<br/>(7模块)"]
        D_EX_CORE["D_EX_CORE<br/>执行核心<br/>(15模块)"]
        D_EX_SOR["D_EX_SOR<br/>执行路由<br/>(7模块)"]
        D_FACTOR["D_FACTOR<br/>因子<br/>(14模块)"]
        D_FUNDAMENTAL_SIGNAL["D_FUNDAMENTAL_SIGNAL<br/>fundamental_signal<br/>(25模块)"]
        D_GOVERNANCE["D_GOVERNANCE<br/>registry_management<br/>(850模块)"]
        D_GOV_AUDIT["D_GOV_AUDIT<br/>audit_orchestration<br/>(2模块)"]
        D_GOV_DOCS["D_GOV_DOCS<br/>architecture_docs<br/>(2模块)"]
        D_GOV_DRIFT["D_GOV_DRIFT<br/>drift_detection<br/>(1模块)"]
        D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>rule_enforcement<br/>(201模块)"]
        D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>script_governance<br/>(434模块)"]
        D_INTELLIGENCE["D_INTELLIGENCE<br/>context_management<br/>(43模块)"]
        D_KNOWLEDGE["D_KNOWLEDGE<br/>vector_storage<br/>(9模块)"]
        D_ML_SERVE["D_ML_SERVE<br/>推理<br/>(7模块)"]
        D_ML_TRAIN["D_ML_TRAIN<br/>model_evaluation<br/>(12模块)"]
        D_PF_ALLOC["D_PF_ALLOC<br/>组合分配<br/>(8模块)"]
        D_PF_CORE["D_PF_CORE<br/>组合核心<br/>(14模块)"]
        D_POSITION["D_POSITION<br/>仓位管理<br/>(8模块)"]
        D_RISK["D_RISK<br/>风控<br/>(20模块)"]
        D_SELL_DECISION["D_SELL_DECISION<br/>卖出决策<br/>(7模块)"]
        D_SIGQC["D_SIGQC<br/>signal_quality<br/>(8模块)"]
        D_SIMULATION["D_SIMULATION<br/>仿真<br/>(11模块)"]
        D_TRADING["D_TRADING<br/>交易运营<br/>(481模块)"]
    end
    subgraph unknown[unknown]
        D_GOV_REPAIR["D_GOV_REPAIR<br/>rollback<br/>(0模块)"]
        D_GOV_RULE["D_GOV_RULE<br/>rule_governance<br/>(0模块)"]
    end

    %% 跨域依赖（按依赖数排序，最多显示 100 条）
    D_AUDITTEST -->|638条 test_depends| D_TRADING
    D_AUDITTEST -->|519条 contract| D_GOVERNANCE
    D_AUDITTEST -->|221条 test_depends| D_GOV_ENFORCEMENT
    D_AUDITTEST -->|168条 test_depends| D_SECURITY
    D_AUDITTEST -->|161条 test_depends| D_SHARED
    D_GOVERNANCE -->|138条 import_depends| D_SHARED
    D_AUDITTEST -->|127条 test_depends| D_AUTONOMY_CORE
    D_AUDITTEST -->|126条 test_depends| D_INFRA_RUNTIME
    D_TRADING -->|86条 import_depends| D_SHARED
    D_INFRA_RUNTIME -->|75条 import_depends| D_SHARED
    D_AUDITTEST -->|63条 test_depends| D_INTEGRATION
    D_GOVERNANCE -->|59条 import_depends| D_TRADING
    D_AUDITTEST -->|52条 test_depends| D_INFRA_RECOVERY
    D_AUDITTEST -->|40条 test_depends| D_SECURITY_LLM
    D_GOV_SCRIPTS -->|40条 import_depends| D_SHARED
    D_INTEGRATION -->|37条 import_depends| D_SHARED
    D_AUDITTEST -->|36条 test_depends| D_INFRA_A2A
    D_GOV_ENFORCEMENT -->|35条 import_depends| D_GOVERNANCE
    D_GOV_SCRIPTS -->|31条 import_depends| D_GOVERNANCE
    D_AUDITTEST -->|31条 test_depends| D_INTELLIGENCE
    D_TRADING -->|26条 import_depends| D_GOVERNANCE
    D_TRADING -->|26条 import_depends| D_INTEGRATION
    D_GOVERNANCE -->|24条 contract| D_AUDITTEST
    D_GOVERNANCE -->|20条 import_depends| D_INTEGRATION
    D_GOV_ENFORCEMENT -->|19条 import_depends| D_SHARED
    D_INFRA_A2A -->|19条 import_depends| D_SHARED
    D_INTEGRATION_GATEWAY -->|19条 import_depends| D_SHARED
    D_INFRA_RUNTIME -->|18条 import_depends| D_GOVERNANCE
    D_SECURITY_LLM -->|17条 import_depends| D_SHARED
    D_GOVERNANCE -->|17条 import_depends| D_GOV_ENFORCEMENT
    D_GOVERNANCE -->|17条 import_depends| D_INTELLIGENCE
    D_TRADING -->|16条 import_depends| D_INFRA_RUNTIME
    D_GOVERNANCE -->|14条 config_depends| D_INFRA_RUNTIME
    D_INTELLIGENCE -->|14条 import_depends| D_SHARED
    D_FUNDAMENTAL_SIGNAL -->|14条 import_depends| D_TRADING
    D_INTEGRATION_GATEWAY -->|13条 import_depends| D_GOVERNANCE
    D_AUTONOMY_PERM -->|12条 import_depends| D_SECURITY
    D_GOVERNANCE -->|11条 import_depends| D_BACKTEST
    D_INFRA_RECOVERY -->|11条 import_depends| D_SHARED
    D_GOVERNANCE -->|11条 import_depends| D_SECURITY
    D_EX_CORE -->|11条 import_depends| D_GOVERNANCE
    D_INTEGRATION -->|11条 import_depends| D_INFRA_RUNTIME
    D_AUTONOMY_CORE -->|10条 import_depends| D_SHARED
    D_INTEGRATION -->|9条 import_depends| D_GOVERNANCE
    D_INFRA_TELEMETRY -->|8条 import_depends| D_SHARED
    D_INFRA_RECOVERY -->|8条 import_depends| D_GOVERNANCE
    D_GOV_SCRIPTS -->|8条 import_depends| D_GOV_ENFORCEMENT
    D_AUDITTEST -->|8条 test_depends| D_FRONTEND
    D_FRONTEND -->|7条 import_depends| D_GOVERNANCE
    D_AUTONOMY_CORE -->|7条 import_depends| D_INFRA_RUNTIME
    D_INFRA_RUNTIME -->|7条 import_depends| D_INTEGRATION
    D_SECURITY -->|7条 import_depends| D_SHARED
    D_GOV_ENFORCEMENT -->|6条 import_depends| D_INTEGRATION
    D_REPORTING -->|6条 import_depends| D_TRADING
    D_AUDITTEST -->|6条 test_depends| D_RISK
    D_AUTONOMY_CORE -->|6条 import_depends| D_INTEGRATION
    D_EX_CORE -->|6条 import_depends| D_TRADING
    D_SECURITY -->|6条 import_depends| D_GOVERNANCE
    D_SECURITY -->|6条 import_depends| D_GOV_ENFORCEMENT
    D_GOV_SCRIPTS -->|6条 import_depends| D_INFRA_RUNTIME
    D_TRADING -->|6条 import_depends| D_SECURITY
    D_GOVERNANCE -->|5条 import_depends| D_FRONTEND
    D_TRADING -->|5条 import_depends| D_INTELLIGENCE
    D_TRADING -->|5条 import_depends| D_GOV_ENFORCEMENT
    D_GOVERNANCE -->|5条 import_depends| D_SECURITY_LLM
    D_PF_CORE -->|5条 import_depends| D_GOVERNANCE
    D_GOVERNANCE -->|4条 contract| D_GOV_DRIFT
    D_AUDITTEST -->|4条 test_depends| D_EX_CORE
    D_GOVERNANCE -->|4条 contract| D_GOV_AUDIT
    D_GOV_AUDIT -->|4条 contract| D_GOVERNANCE
    D_TRADING -->|4条 import_depends| D_SECURITY_LLM
    D_INTEGRATION_GATEWAY -->|4条 import_depends| D_INTEGRATION
    D_AUTONOMY_CORE -->|4条 import_depends| D_GOVERNANCE
    D_INTELLIGENCE -->|4条 import_depends| D_GOVERNANCE
    D_INTELLIGENCE -->|4条 import_depends| D_ML_TRAIN
    D_AUDITTEST -->|4条 test_depends| D_OPS
    D_GOV_DRIFT -->|4条 runtime| D_GOVERNANCE
    D_TRADING -->|4条 import_depends| D_AUTONOMY_CORE
    D_GOV_ENFORCEMENT -->|3条 import_depends| D_SECURITY
    D_INTELLIGENCE -->|3条 import_depends| D_BACKTEST
    D_GOVERNANCE -->|3条 import_depends| D_INFRA_RECOVERY
    D_ML_TRAIN -->|3条 import_depends| D_SHARED
    D_SHARED -->|3条 import_depends| D_INFRA_RUNTIME
    D_SECURITY -->|3条 import_depends| D_TRADING
    D_TRADING -->|3条 import_depends| D_OPS
    D_GOVERNANCE -->|3条 import_depends| D_REPORTING
    D_GOVERNANCE -->|3条 import_depends| D_RISK
    D_GOV_SCRIPTS -->|3条 import_depends| D_INTEGRATION
    D_RISK -->|3条 import_depends| D_TRADING
    D_BACKTEST -->|3条 import_depends| D_GOVERNANCE
    D_RISK -->|3条 import_depends| D_SHARED
    D_GOV_ENFORCEMENT -->|3条 import_depends| D_INFRA_RECOVERY
    D_INTEGRATION -->|3条 import_depends| D_INTELLIGENCE
    D_AUTONOMY_CORE -->|2条 import_depends| D_INTELLIGENCE
    D_BACKTEST -->|2条 import_depends| D_SHARED
    D_EX_CORE -->|2条 import_depends| D_BACKTEST
    D_FRONTEND -->|2条 import| D_BACKTEST
    D_FRONTEND -->|2条 import_depends| D_EX_CORE
    D_FRONTEND -->|2条 import_depends| D_SHARED
    D_FRONTEND -->|2条 import_depends| D_TRADING
    %% ... 还有 75 条跨域依赖未显示

    %% 统计
    %% 域总数: 50
    %% 跨域依赖对数: 175
    %% 跨域依赖边总数: 3410

    %% Top 10 依赖对
    %% 1. D_AUDITTEST -> D_TRADING: 638 条
    %% 2. D_AUDITTEST -> D_GOVERNANCE: 519 条
    %% 3. D_AUDITTEST -> D_GOV_ENFORCEMENT: 221 条
    %% 4. D_AUDITTEST -> D_SECURITY: 168 条
    %% 5. D_AUDITTEST -> D_SHARED: 161 条
    %% 6. D_GOVERNANCE -> D_SHARED: 138 条
    %% 7. D_AUDITTEST -> D_AUTONOMY_CORE: 127 条
    %% 8. D_AUDITTEST -> D_INFRA_RUNTIME: 126 条
    %% 9. D_TRADING -> D_SHARED: 86 条
    %% 10. D_INFRA_RUNTIME -> D_SHARED: 75 条

```
