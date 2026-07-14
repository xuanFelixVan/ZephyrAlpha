---
doc_type: audit_report
title: 架构约束违规报告
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 架构约束违规报告

> **文档作用 / Purpose**: 展示架构约束违规情况，包括跨层依赖、循环依赖、命名违规等，为架构治理提供修复清单。

> 本文档由 generate_constraint_violations.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) arch_constraints表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 约束总数 | 228 |
| Open（未解决） | 228 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 128 |
| warn | 100 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| cross_domain_violation | 92 |
| layer_violation | 35 |
| orphan_node | 100 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-ORPHAN-2421903 | 孤儿节点: 2421903 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 2421903 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-2421904 | 孤儿节点: 2421904 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 2421904 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-2421905 | 孤儿节点: 2421905 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 2421905 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-2421906 | 孤儿节点: 2421906 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 2421906 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-2521703 | 孤儿节点: 2521703 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2521703 路径 src/zephyr/alt_data/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2521704 | 孤儿节点: 2521704 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2521704 路径 src/zephyr/alt_data/__init__.py 未注册到目录树 |
| V-ORPHAN-2521706 | 孤儿节点: 2521706 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2521706 路径 src/zephyr/alt_data/infrastructure/__init__.py... |
| V-ORPHAN-2521707 | 孤儿节点: 2521707 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2521707 路径 src/zephyr/alt_data/services/__init__.py 未注册到目... |
| V-ORPHAN-2521708 | 孤儿节点: 2521708 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2521708 路径 src/zephyr/alt_data/models/__init__.py 未注册到目录树 |
| V-ORPHAN-2521709 | 孤儿节点: 2521709 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2521709 路径 src/zephyr/alt_data/_extensions/__init__.py 未注... |
| V-ORPHAN-2521710 | 孤儿节点: 2521710 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2521710 路径 src/zephyr/alt_data/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2521762 | 孤儿节点: 2521762 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2521762 路径 src/zephyr/autonomy_core/context/__init__.py 未... |
| V-ORPHAN-2521768 | 孤儿节点: 2521768 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2521768 路径 src/zephyr/autonomy_core/integration/__init__.... |
| V-ORPHAN-2521798 | 孤儿节点: 2521798 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2521798 路径 src/zephyr/autonomy_core/skills/skill_model.py... |
| V-ORPHAN-2521824 | 孤儿节点: 2521824 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521824 路径 src/zephyr/autonomy_perm/__init__.py 未注册到目录树 |
| V-ORPHAN-2521825 | 孤儿节点: 2521825 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2521825 路径 src/zephyr/autonomy_core/skills/__init__.py 未注... |
| V-ORPHAN-2521826 | 孤儿节点: 2521826 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521826 路径 src/zephyr/autonomy_perm/api/__init__.py 未注册到目... |
| V-ORPHAN-2521827 | 孤儿节点: 2521827 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521827 路径 src/zephyr/autonomy_perm/core/__init__.py 未注册到... |
| V-ORPHAN-2521828 | 孤儿节点: 2521828 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521828 路径 src/zephyr/autonomy_perm/infrastructure/__init... |
| V-ORPHAN-2521829 | 孤儿节点: 2521829 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521829 路径 src/zephyr/autonomy_perm/models/__init__.py 未注... |
| V-ORPHAN-2521830 | 孤儿节点: 2521830 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521830 路径 src/zephyr/autonomy_perm/red_blue_validator/at... |
| V-ORPHAN-2521831 | 孤儿节点: 2521831 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521831 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-2521832 | 孤儿节点: 2521832 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521832 路径 src/zephyr/autonomy_perm/red_blue_validator/by... |
| V-ORPHAN-2521833 | 孤儿节点: 2521833 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521833 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-2521834 | 孤儿节点: 2521834 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521834 路径 src/zephyr/autonomy_perm/red_blue_validator/de... |
| V-ORPHAN-2521835 | 孤儿节点: 2521835 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521835 路径 src/zephyr/autonomy_perm/red_blue_validator/ga... |
| V-ORPHAN-2521836 | 孤儿节点: 2521836 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521836 路径 src/zephyr/autonomy_perm/services/__init__.py ... |
| V-ORPHAN-2521837 | 孤儿节点: 2521837 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521837 路径 src/zephyr/autonomy_perm/red_blue_validator/__... |
| V-ORPHAN-2521838 | 孤儿节点: 2521838 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2521838 路径 src/zephyr/autonomy_perm/_extensions/__init__.... |
| V-ORPHAN-2521839 | 孤儿节点: 2521839 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521839 路径 src/zephyr/backtest/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2521840 | 孤儿节点: 2521840 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521840 路径 src/zephyr/backtest/core/decision_gate.py 未注册到... |
| V-ORPHAN-2521843 | 孤儿节点: 2521843 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521843 路径 src/zephyr/backtest/__init__.py 未注册到目录树 |
| V-ORPHAN-2521844 | 孤儿节点: 2521844 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521844 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-2521847 | 孤儿节点: 2521847 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521847 路径 src/zephyr/backtest/core/overfitting_detector.... |
| V-ORPHAN-2521848 | 孤儿节点: 2521848 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521848 路径 src/zephyr/backtest/core/pit_manager.py 未注册到目录... |
| V-ORPHAN-2521851 | 孤儿节点: 2521851 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521851 路径 src/zephyr/backtest/core/walk_forward.py 未注册到目... |
| V-ORPHAN-2521852 | 孤儿节点: 2521852 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521852 路径 src/zephyr/backtest/infrastructure/__init__.py... |
| V-ORPHAN-2521853 | 孤儿节点: 2521853 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521853 路径 src/zephyr/backtest/io/backtest_result_sink.py... |
| V-ORPHAN-2521858 | 孤儿节点: 2521858 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521858 路径 src/zephyr/backtest/io/result_repository.py 未注... |
| V-ORPHAN-2521859 | 孤儿节点: 2521859 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521859 路径 src/zephyr/backtest/models/__init__.py 未注册到目录树 |
| V-ORPHAN-2521860 | 孤儿节点: 2521860 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521860 路径 src/zephyr/backtest/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2521861 | 孤儿节点: 2521861 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521861 路径 src/zephyr/backtest/services/__init__.py 未注册到目... |
| V-ORPHAN-2521862 | 孤儿节点: 2521862 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521862 路径 src/zephyr/backtest/_extensions/__init__.py 未注... |
| V-ORPHAN-2521863 | 孤儿节点: 2521863 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521863 路径 src/zephyr/compliance/aisg_sandbox.py 未注册到目录树 |
| V-ORPHAN-2521864 | 孤儿节点: 2521864 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2521864 路径 src/zephyr/backtest/io/__init__.py 未注册到目录树 |
| V-ORPHAN-2521865 | 孤儿节点: 2521865 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521865 路径 src/zephyr/compliance/artifact_scanner.py 未注册到... |
| V-ORPHAN-2521866 | 孤儿节点: 2521866 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521866 路径 src/zephyr/compliance/compliance_manager.py 未注... |
| V-ORPHAN-2521867 | 孤儿节点: 2521867 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521867 路径 src/zephyr/compliance/evidence_pack.py 未注册到目录树 |
| V-ORPHAN-2521868 | 孤儿节点: 2521868 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521868 路径 src/zephyr/compliance/integrity.py 未注册到目录树 |
| V-ORPHAN-2521869 | 孤儿节点: 2521869 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521869 路径 src/zephyr/compliance/financial_compliance.py ... |
| V-ORPHAN-2521870 | 孤儿节点: 2521870 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521870 路径 src/zephyr/compliance/default_security_gateway... |
| V-ORPHAN-2521871 | 孤儿节点: 2521871 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521871 路径 src/zephyr/compliance/security_gateway_base.py... |
| V-ORPHAN-2521872 | 孤儿节点: 2521872 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521872 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-2521873 | 孤儿节点: 2521873 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521873 路径 src/zephyr/compliance/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2521874 | 孤儿节点: 2521874 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521874 路径 src/zephyr/compliance/audit_orchestrator/__ini... |
| V-ORPHAN-2521875 | 孤儿节点: 2521875 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521875 路径 src/zephyr/compliance/behavioral_admission/__i... |
| V-ORPHAN-2521876 | 孤儿节点: 2521876 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521876 路径 src/zephyr/compliance/audit_trail/__init__.py ... |
| V-ORPHAN-2521877 | 孤儿节点: 2521877 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521877 路径 src/zephyr/compliance/implementations/__init__... |
| V-ORPHAN-2521878 | 孤儿节点: 2521878 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521878 路径 src/zephyr/compliance/audit_trail/bridges/__in... |
| V-ORPHAN-2521879 | 孤儿节点: 2521879 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521879 路径 src/zephyr/compliance/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2521880 | 孤儿节点: 2521880 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521880 路径 src/zephyr/compliance/compliance_gate_a6/__ini... |
| V-ORPHAN-2521881 | 孤儿节点: 2521881 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521881 路径 src/zephyr/compliance/infrastructure/__init__.... |
| V-ORPHAN-2521882 | 孤儿节点: 2521882 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521882 路径 src/zephyr/compliance/models/__init__.py 未注册到目... |
| V-ORPHAN-2521883 | 孤儿节点: 2521883 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521883 路径 src/zephyr/compliance/services/__init__.py 未注册... |
| V-ORPHAN-2521884 | 孤儿节点: 2521884 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2521884 路径 src/zephyr/cross_asset/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2521885 | 孤儿节点: 2521885 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521885 路径 src/zephyr/compliance/zero_knowledge_audit_stu... |
| V-ORPHAN-2521886 | 孤儿节点: 2521886 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2521886 路径 src/zephyr/compliance/_extensions/__init__.py ... |
| V-ORPHAN-2521888 | 孤儿节点: 2521888 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2521888 路径 src/zephyr/cross_asset/core/__init__.py 未注册到目录... |
| V-ORPHAN-2521889 | 孤儿节点: 2521889 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2521889 路径 src/zephyr/cross_asset/infrastructure/__init__... |
| V-ORPHAN-2521890 | 孤儿节点: 2521890 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2521890 路径 src/zephyr/cross_asset/models/__init__.py 未注册到... |
| V-ORPHAN-2521891 | 孤儿节点: 2521891 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2521891 路径 src/zephyr/cross_asset/_extensions/__init__.py... |
| V-ORPHAN-2521892 | 孤儿节点: 2521892 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2521892 路径 src/zephyr/cross_asset/services/__init__.py 未注... |
| V-ORPHAN-2521893 | 孤儿节点: 2521893 | orphan_node | D_DATA |  | warn | advisory | 节点 2521893 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-2521894 | 孤儿节点: 2521894 | orphan_node | D_DATA |  | warn | advisory | 节点 2521894 路径 src/zephyr/data/backfill_checker.py 未注册到目录树 |
| V-ORPHAN-2521895 | 孤儿节点: 2521895 | orphan_node | D_DATA |  | warn | advisory | 节点 2521895 路径 src/zephyr/data/ch_reader.py 未注册到目录树 |
| V-ORPHAN-2521896 | 孤儿节点: 2521896 | orphan_node | D_DATA |  | warn | advisory | 节点 2521896 路径 src/zephyr/data/buffered_writer.py 未注册到目录树 |
| V-ORPHAN-2521897 | 孤儿节点: 2521897 | orphan_node | D_DATA |  | warn | advisory | 节点 2521897 路径 src/zephyr/data/ch_writer.py 未注册到目录树 |
| V-ORPHAN-2521900 | 孤儿节点: 2521900 | orphan_node | D_DATA |  | warn | advisory | 节点 2521900 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-2521903 | 孤儿节点: 2521903 | orphan_node | D_DATA |  | warn | advisory | 节点 2521903 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-2521904 | 孤儿节点: 2521904 | orphan_node | D_DATA |  | warn | advisory | 节点 2521904 路径 src/zephyr/data/news_dedup.py 未注册到目录树 |
| V-ORPHAN-2521905 | 孤儿节点: 2521905 | orphan_node | D_DATA |  | warn | advisory | 节点 2521905 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-2521906 | 孤儿节点: 2521906 | orphan_node | D_DATA |  | warn | advisory | 节点 2521906 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-2521908 | 孤儿节点: 2521908 | orphan_node | D_DATA |  | warn | advisory | 节点 2521908 路径 src/zephyr/data/__main__.py 未注册到目录树 |
| V-ORPHAN-2521910 | 孤儿节点: 2521910 | orphan_node | D_DATA |  | warn | advisory | 节点 2521910 路径 src/zephyr/data/speed_tester.py 未注册到目录树 |
| V-ORPHAN-2521911 | 孤儿节点: 2521911 | orphan_node | D_DATA |  | warn | advisory | 节点 2521911 路径 src/zephyr/data/implementations/eastmoney_news... |
| V-ORPHAN-2521912 | 孤儿节点: 2521912 | orphan_node | D_DATA |  | warn | advisory | 节点 2521912 路径 src/zephyr/data/implementations/akshare_provid... |
| V-ORPHAN-2521913 | 孤儿节点: 2521913 | orphan_node | D_DATA |  | warn | advisory | 节点 2521913 路径 src/zephyr/data/implementations/baostock_provi... |
| V-ORPHAN-2521914 | 孤儿节点: 2521914 | orphan_node | D_DATA |  | warn | advisory | 节点 2521914 路径 src/zephyr/data/implementations/cls_provider.p... |
| V-ORPHAN-2521915 | 孤儿节点: 2521915 | orphan_node | D_DATA |  | warn | advisory | 节点 2521915 路径 src/zephyr/data/implementations/ifind_provider... |
| V-ORPHAN-2521916 | 孤儿节点: 2521916 | orphan_node | D_DATA |  | warn | advisory | 节点 2521916 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-2521917 | 孤儿节点: 2521917 | orphan_node | D_DATA |  | warn | advisory | 节点 2521917 路径 src/zephyr/data/implementations/miniqmt_provid... |
| V-ORPHAN-2521918 | 孤儿节点: 2521918 | orphan_node | D_DATA |  | warn | advisory | 节点 2521918 路径 src/zephyr/data/implementations/tdx_provider.p... |
| V-ORPHAN-2521919 | 孤儿节点: 2521919 | orphan_node | D_DATA |  | warn | advisory | 节点 2521919 路径 src/zephyr/data/implementations/tickflow_provi... |
| V-ORPHAN-2521920 | 孤儿节点: 2521920 | orphan_node | D_DATA |  | warn | advisory | 节点 2521920 路径 src/zephyr/data/implementations/rss_provider.p... |
| V-ORPHAN-2521921 | 孤儿节点: 2521921 | orphan_node | D_DATA |  | warn | advisory | 节点 2521921 路径 src/zephyr/data/implementations/__init__.py 未注... |
| V-ORPHAN-2521922 | 孤儿节点: 2521922 | orphan_node | D_DATA |  | warn | advisory | 节点 2521922 路径 src/zephyr/data/implementations/tushare_provid... |
| V-ORPHAN-2521923 | 孤儿节点: 2521923 | orphan_node | D_DATA |  | warn | advisory | 节点 2521923 路径 src/zephyr/data/satellite_geospatial_engine/__... |
| V-ORPHAN-2521924 | 孤儿节点: 2521924 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2521924 路径 src/zephyr/data_eng/__init__.py 未注册到目录树 |
| V-ORPHAN-2521925 | 孤儿节点: 2521925 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2521925 路径 src/zephyr/data_eng/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2521926 | 孤儿节点: 2521926 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2521926 路径 src/zephyr/data_eng/api/__init__.py 未注册到目录树 |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | code |  |
| V-CROSS-D_AUTONOMY_CORE-D_FBL_VERIFICATION | 跨域违规: D_AUTONOMY_CORE -> D_FBL_VERIFICATION | cross_domain_violation | D_AUTONOMY_CORE | D_FBL_VERIFICATION | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_FBL_VERIFICATION |
| V-CROSS-D_AUTONOMY_CORE-D_FEEDBACK_LOOP | 跨域违规: D_AUTONOMY_CORE -> D_FEEDBACK_LOOP | cross_domain_violation | D_AUTONOMY_CORE | D_FEEDBACK_LOOP | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_FEEDBACK_LOOP |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTEGRATION |
| V-CROSS-D_AUTONOMY_CORE-D_INTELLIGENCE | 跨域违规: D_AUTONOMY_CORE -> D_INTELLIGENCE | cross_domain_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTELLIGENCE |
| V-CROSS-D_AUTONOMY_CORE-D_ORCHESTRATOR | 跨域违规: D_AUTONOMY_CORE -> D_ORCHESTRATOR | cross_domain_violation | D_AUTONOMY_CORE | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_ORCHESTRATOR |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SHARED |
| V-CROSS-D_AUTONOMY_CORE-D_TRADING | 跨域违规: D_AUTONOMY_CORE -> D_TRADING | cross_domain_violation | D_AUTONOMY_CORE | D_TRADING | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_TRADING |
| V-CROSS-D_AUTONOMY_PERM-D_SECURITY | 跨域违规: D_AUTONOMY_PERM -> D_SECURITY | cross_domain_violation | D_AUTONOMY_PERM | D_SECURITY | error | gate | 跨域依赖未声明: D_AUTONOMY_PERM -> D_SECURITY |
| V-CROSS-D_BACKTEST-D_DATA | 跨域违规: D_BACKTEST -> D_DATA | cross_domain_violation | D_BACKTEST | D_DATA | error | gate | 跨域依赖未声明: D_BACKTEST -> D_DATA |
| V-CROSS-D_COMPLIANCE-D_GOV_AUDIT | 跨域违规: D_COMPLIANCE -> D_GOV_AUDIT | cross_domain_violation | D_COMPLIANCE | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_AUDIT |
| V-CROSS-D_COMPLIANCE-D_GOV_DRIFT | 跨域违规: D_COMPLIANCE -> D_GOV_DRIFT | cross_domain_violation | D_COMPLIANCE | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_DRIFT |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | gate | 跨域依赖未声明: D_DATA -> D_SHARED |
| V-CROSS-D_FBL_VERIFICATION-D_GOV_AUDIT | 跨域违规: D_FBL_VERIFICATION -> D_GOV_AUDIT | cross_domain_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_FBL_VERIFICATION -> D_GOV_AUDIT |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DETECTORS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DETECTORS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DETECTORS | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_DETECTORS |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DIAGNOSERS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DIAGNOSERS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_DIAGNOSERS |
| V-CROSS-D_FRONTEND-D_FEEDBACK_LOOP | 跨域违规: D_FRONTEND -> D_FEEDBACK_LOOP | cross_domain_violation | D_FRONTEND | D_FEEDBACK_LOOP | error | gate | 跨域依赖未声明: D_FRONTEND -> D_FEEDBACK_LOOP |
| V-CROSS-D_GOVERNANCE-D_GOV_AUDIT | 跨域违规: D_GOVERNANCE -> D_GOV_AUDIT | cross_domain_violation | D_GOVERNANCE | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_AUDIT |
| V-CROSS-D_GOVERNANCE-D_GOV_CODE_QUALITY | 跨域违规: D_GOVERNANCE -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOVERNANCE | D_GOV_CODE_QUALITY | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_CODE_QUALITY |
| V-CROSS-D_GOVERNANCE-D_GOV_ENFORCEMENT | 跨域违规: D_GOVERNANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOVERNANCE | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOVERNANCE-D_GOV_KB | 跨域违规: D_GOVERNANCE -> D_GOV_KB | cross_domain_violation | D_GOVERNANCE | D_GOV_KB | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_KB |
| V-CROSS-D_GOVERNANCE-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOVERNANCE -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOVERNANCE | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_GOVERNANCE-D_GOV_REPAIR | 跨域违规: D_GOVERNANCE -> D_GOV_REPAIR | cross_domain_violation | D_GOVERNANCE | D_GOV_REPAIR | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_REPAIR |
| V-CROSS-D_GOVERNANCE-D_INFRA_RECOVERY | 跨域违规: D_GOVERNANCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOVERNANCE | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INFRA_RECOVERY |
| V-CROSS-D_GOVERNANCE-D_INTELLIGENCE | 跨域违规: D_GOVERNANCE -> D_INTELLIGENCE | cross_domain_violation | D_GOVERNANCE | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INTELLIGENCE |
| V-CROSS-D_GOVERNANCE-D_OPS | 跨域违规: D_GOVERNANCE -> D_OPS | cross_domain_violation | D_GOVERNANCE | D_OPS | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_OPS |
| V-CROSS-D_GOVERNANCE-D_TRADING | 跨域违规: D_GOVERNANCE -> D_TRADING | cross_domain_violation | D_GOVERNANCE | D_TRADING | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_TRADING |
| V-CROSS-D_GOV_AUDIT-D_FBL_DIAGNOSERS | 跨域违规: D_GOV_AUDIT -> D_FBL_DIAGNOSERS | cross_domain_violation | D_GOV_AUDIT | D_FBL_DIAGNOSERS | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_FBL_DIAGNOSERS |
| V-CROSS-D_GOV_AUDIT-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_AUDIT -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_AUDIT | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_GOV_AUDIT-D_GOV_RULE | 跨域违规: D_GOV_AUDIT -> D_GOV_RULE | cross_domain_violation | D_GOV_AUDIT | D_GOV_RULE | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOV_RULE |
| V-CROSS-D_GOV_AUDIT-D_INFRA_A2A | 跨域违规: D_GOV_AUDIT -> D_INFRA_A2A | cross_domain_violation | D_GOV_AUDIT | D_INFRA_A2A | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_INFRA_A2A |
| V-CROSS-D_GOV_AUDIT-D_INFRA_RUNTIME | 跨域违规: D_GOV_AUDIT -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_AUDIT | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_INFRA_RUNTIME |
| V-CROSS-D_GOV_AUDIT-D_INTELLIGENCE | 跨域违规: D_GOV_AUDIT -> D_INTELLIGENCE | cross_domain_violation | D_GOV_AUDIT | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_INTELLIGENCE |
| V-CROSS-D_GOV_AUDIT-D_SHARED | 跨域违规: D_GOV_AUDIT -> D_SHARED | cross_domain_violation | D_GOV_AUDIT | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_SHARED |
| V-CROSS-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_CODE_QUALITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOV_CODE_QUALITY-D_SHARED | 跨域违规: D_GOV_CODE_QUALITY -> D_SHARED | cross_domain_violation | D_GOV_CODE_QUALITY | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_SHARED |
| V-CROSS-D_GOV_DRIFT-D_GOVERNANCE | 跨域违规: D_GOV_DRIFT -> D_GOVERNANCE | cross_domain_violation | D_GOV_DRIFT | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_DRIFT -> D_GOVERNANCE |
| V-CROSS-D_GOV_DRIFT-D_GOV_AUDIT | 跨域违规: D_GOV_DRIFT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_DRIFT | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_DRIFT -> D_GOV_AUDIT |
| V-CROSS-D_GOV_DRIFT-D_SHARED | 跨域违规: D_GOV_DRIFT -> D_SHARED | cross_domain_violation | D_GOV_DRIFT | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_DRIFT -> D_SHARED |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_AUDIT | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_GOV_AUDIT |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_CODE_QUALITY | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_GOV_CODE_QUALITY |
| V-CROSS-D_GOV_KB-D_SHARED | 跨域违规: D_GOV_KB -> D_SHARED | cross_domain_violation | D_GOV_KB | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_KB -> D_SHARED |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOVERNANCE | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_GOVERNANCE |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOV_AUDIT | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOV_AUDIT | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_GOV_AUDIT |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOV_DRIFT | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOV_DRIFT | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_GOV_DRIFT |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INFRA_RECOVERY | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_INFRA_RECOVERY |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INTEGRATION | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INTEGRATION | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_INTEGRATION |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_OPS | 跨域违规: D_GOV_OPS_RESILIENCE -> D_OPS | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_OPS | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_OPS |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_ORCHESTRATOR | 跨域违规: D_GOV_OPS_RESILIENCE -> D_ORCHESTRATOR | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_ORCHESTRATOR |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_SHARED | 跨域违规: D_GOV_OPS_RESILIENCE -> D_SHARED | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_SHARED |
| V-CROSS-D_GOV_REPAIR-D_FACTOR | 跨域违规: D_GOV_REPAIR -> D_FACTOR | cross_domain_violation | D_GOV_REPAIR | D_FACTOR | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_FACTOR |
| V-CROSS-D_GOV_REPAIR-D_GOVERNANCE | 跨域违规: D_GOV_REPAIR -> D_GOVERNANCE | cross_domain_violation | D_GOV_REPAIR | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOVERNANCE |
| V-CROSS-D_GOV_REPAIR-D_GOV_AUDIT | 跨域违规: D_GOV_REPAIR -> D_GOV_AUDIT | cross_domain_violation | D_GOV_REPAIR | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_AUDIT |
| V-CROSS-D_GOV_REPAIR-D_GOV_DRIFT | 跨域违规: D_GOV_REPAIR -> D_GOV_DRIFT | cross_domain_violation | D_GOV_REPAIR | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_DRIFT |
| V-CROSS-D_GOV_REPAIR-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_REPAIR -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_REPAIR | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOV_REPAIR-D_GOV_KB | 跨域违规: D_GOV_REPAIR -> D_GOV_KB | cross_domain_violation | D_GOV_REPAIR | D_GOV_KB | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_KB |
| V-CROSS-D_GOV_REPAIR-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_REPAIR -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_REPAIR | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_GOV_REPAIR-D_GOV_RULE | 跨域违规: D_GOV_REPAIR -> D_GOV_RULE | cross_domain_violation | D_GOV_REPAIR | D_GOV_RULE | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_RULE |
| V-CROSS-D_GOV_REPAIR-D_INFRASTRUCTURE | 跨域违规: D_GOV_REPAIR -> D_INFRASTRUCTURE | cross_domain_violation | D_GOV_REPAIR | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_INFRASTRUCTURE |
| V-CROSS-D_GOV_REPAIR-D_INFRA_RUNTIME | 跨域违规: D_GOV_REPAIR -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_REPAIR | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_INFRA_RUNTIME |
| V-CROSS-D_GOV_REPAIR-D_TRADING | 跨域违规: D_GOV_REPAIR -> D_TRADING | cross_domain_violation | D_GOV_REPAIR | D_TRADING | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_TRADING |
| V-CROSS-D_GOV_RULE-D_GOVERNANCE | 跨域违规: D_GOV_RULE -> D_GOVERNANCE | cross_domain_violation | D_GOV_RULE | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_RULE -> D_GOVERNANCE |
| V-CROSS-D_GOV_RULE-D_INTEGRATION | 跨域违规: D_GOV_RULE -> D_INTEGRATION | cross_domain_violation | D_GOV_RULE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_GOV_RULE -> D_INTEGRATION |
| V-CROSS-D_GOV_SCRIPTS-D_DATA | 跨域违规: D_GOV_SCRIPTS -> D_DATA | cross_domain_violation | D_GOV_SCRIPTS | D_DATA | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_DATA |
| V-CROSS-D_GOV_SCRIPTS-D_GOVERNANCE | 跨域违规: D_GOV_SCRIPTS -> D_GOVERNANCE | cross_domain_violation | D_GOV_SCRIPTS | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_GOVERNANCE |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_RULE | 跨域违规: D_GOV_SCRIPTS -> D_GOV_RULE | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_RULE | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_GOV_RULE |
| V-CROSS-D_GOV_SCRIPTS-D_SHARED | 跨域违规: D_GOV_SCRIPTS -> D_SHARED | cross_domain_violation | D_GOV_SCRIPTS | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_SHARED |
| V-CROSS-D_INFRASTRUCTURE-D_SHARED | 跨域违规: D_INFRASTRUCTURE -> D_SHARED | cross_domain_violation | D_INFRASTRUCTURE | D_SHARED | error | gate | 跨域依赖未声明: D_INFRASTRUCTURE -> D_SHARED |
| V-CROSS-D_INFRA_A2A-D_GOVERNANCE | 跨域违规: D_INFRA_A2A -> D_GOVERNANCE | cross_domain_violation | D_INFRA_A2A | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_INFRA_A2A -> D_GOVERNANCE |
| V-CROSS-D_INFRA_RECOVERY-D_GOV_CODE_QUALITY | 跨域违规: D_INFRA_RECOVERY -> D_GOV_CODE_QUALITY | cross_domain_violation | D_INFRA_RECOVERY | D_GOV_CODE_QUALITY | error | gate | 跨域依赖未声明: D_INFRA_RECOVERY -> D_GOV_CODE_QUALITY |
| V-CROSS-D_INFRA_RECOVERY-D_GOV_DRIFT | 跨域违规: D_INFRA_RECOVERY -> D_GOV_DRIFT | cross_domain_violation | D_INFRA_RECOVERY | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_INFRA_RECOVERY -> D_GOV_DRIFT |
| V-CROSS-D_INFRA_RECOVERY-D_INFRA_RUNTIME | 跨域违规: D_INFRA_RECOVERY -> D_INFRA_RUNTIME | cross_domain_violation | D_INFRA_RECOVERY | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_INFRA_RECOVERY -> D_INFRA_RUNTIME |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_RULE | 跨域违规: D_INFRA_RUNTIME -> D_GOV_RULE | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_RULE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOV_RULE |
| V-CROSS-D_INFRA_RUNTIME-D_INFRA_A2A | 跨域违规: D_INFRA_RUNTIME -> D_INFRA_A2A | cross_domain_violation | D_INFRA_RUNTIME | D_INFRA_A2A | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INFRA_A2A |
| V-CROSS-D_INFRA_RUNTIME-D_INTEGRATION | 跨域违规: D_INFRA_RUNTIME -> D_INTEGRATION | cross_domain_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INTEGRATION |
| V-CROSS-D_INTELLIGENCE-D_GOV_DRIFT | 跨域违规: D_INTELLIGENCE -> D_GOV_DRIFT | cross_domain_violation | D_INTELLIGENCE | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_INTELLIGENCE -> D_GOV_DRIFT |
| V-CROSS-D_KNOWLEDGE-D_FEEDBACK_LOOP | 跨域违规: D_KNOWLEDGE -> D_FEEDBACK_LOOP | cross_domain_violation | D_KNOWLEDGE | D_FEEDBACK_LOOP | error | gate | 跨域依赖未声明: D_KNOWLEDGE -> D_FEEDBACK_LOOP |
| V-CROSS-D_REPORTING-D_INFRASTRUCTURE | 跨域违规: D_REPORTING -> D_INFRASTRUCTURE | cross_domain_violation | D_REPORTING | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_REPORTING -> D_INFRASTRUCTURE |
| V-CROSS-D_RISK-D_INFRASTRUCTURE | 跨域违规: D_RISK -> D_INFRASTRUCTURE | cross_domain_violation | D_RISK | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_RISK -> D_INFRASTRUCTURE |
| V-CROSS-D_SECURITY-D_GOV_DRIFT | 跨域违规: D_SECURITY -> D_GOV_DRIFT | cross_domain_violation | D_SECURITY | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOV_DRIFT |
| V-CROSS-D_SECURITY-D_SECURITY_LLM | 跨域违规: D_SECURITY -> D_SECURITY_LLM | cross_domain_violation | D_SECURITY | D_SECURITY_LLM | error | gate | 跨域依赖未声明: D_SECURITY -> D_SECURITY_LLM |
| V-CROSS-D_SECURITY_LLM-D_INFRA_RUNTIME | 跨域违规: D_SECURITY_LLM -> D_INFRA_RUNTIME | cross_domain_violation | D_SECURITY_LLM | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_SECURITY_LLM -> D_INFRA_RUNTIME |
| V-CROSS-D_SECURITY_LLM-D_ORCHESTRATOR | 跨域违规: D_SECURITY_LLM -> D_ORCHESTRATOR | cross_domain_violation | D_SECURITY_LLM | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_SECURITY_LLM -> D_ORCHESTRATOR |
| V-CROSS-D_SECURITY_LLM-D_SECURITY | 跨域违规: D_SECURITY_LLM -> D_SECURITY | cross_domain_violation | D_SECURITY_LLM | D_SECURITY | error | gate | 跨域依赖未声明: D_SECURITY_LLM -> D_SECURITY |
| V-CROSS-D_SECURITY_LLM-D_SHARED | 跨域违规: D_SECURITY_LLM -> D_SHARED | cross_domain_violation | D_SECURITY_LLM | D_SHARED | error | gate | 跨域依赖未声明: D_SECURITY_LLM -> D_SHARED |
| V-CROSS-D_SHARED-D_DATA | 跨域违规: D_SHARED -> D_DATA | cross_domain_violation | D_SHARED | D_DATA | error | gate | 跨域依赖未声明: D_SHARED -> D_DATA |
| V-CROSS-D_SHARED-D_GOV_OPS_RESILIENCE | 跨域违规: D_SHARED -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_SHARED | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_SHARED -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_SHARED-D_INFRA_RUNTIME | 跨域违规: D_SHARED -> D_INFRA_RUNTIME | cross_domain_violation | D_SHARED | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_SHARED -> D_INFRA_RUNTIME |
| V-CROSS-D_SHARED-D_INTEGRATION | 跨域违规: D_SHARED -> D_INTEGRATION | cross_domain_violation | D_SHARED | D_INTEGRATION | error | gate | 跨域依赖未声明: D_SHARED -> D_INTEGRATION |
| V-CROSS-D_SIGLEGACY-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_SIGLEGACY -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_SIGLEGACY | D_FUNDAMENTAL_SIGNAL | error | gate | 跨域依赖未声明: D_SIGLEGACY -> D_FUNDAMENTAL_SIGNAL |
| V-CROSS-D_TRADING-D_INFRASTRUCTURE | 跨域违规: D_TRADING -> D_INFRASTRUCTURE | cross_domain_violation | D_TRADING | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_TRADING -> D_INFRASTRUCTURE |
| V-CROSS-D_TRADING-D_INTEGRATION | 跨域违规: D_TRADING -> D_INTEGRATION | cross_domain_violation | D_TRADING | D_INTEGRATION | error | gate | 跨域依赖未声明: D_TRADING -> D_INTEGRATION |
| V-CROSS-D_TRADING-D_ORCHESTRATOR | 跨域违规: D_TRADING -> D_ORCHESTRATOR | cross_domain_violation | D_TRADING | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_TRADING -> D_ORCHESTRATOR |
| V-LAYER-D_AUTONOMY_CORE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | gate | 层级违规: 2525036 -> 2522460 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 层级违规: 2521739 -> 2523442 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_TRADING | error | gate | 层级违规: 2525012 -> 2524146 (L1_foundation -> L2_domain) |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | gate | 层级违规: 2522284 -> 2522651 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | gate | 层级违规: 2522021 -> 2522359 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 2522337 -> 2522543 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 2522900 -> 2522914 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_FACTOR | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_FACTOR | error | gate | 层级违规: 2522549 -> 2521980 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | gate | 层级违规: 2522527 -> 2522551 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | error | gate | 层级违规: 2522527 -> 2522687 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_DRIFT | error | gate | 层级违规: 2522527 -> 2522793 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_KB | error | gate | 层级违规: 2522439 -> 2522986 (L1_foundation -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_FEEDBACK_LOOP | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_FEEDBACK_LOOP | error | gate | 层级违规: 2525110 -> 2522009 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | gate | 层级违规: 2524810 -> 2522362 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | gate | 层级违规: 2523066 -> 2524043 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RECOVERY-D_FBL_DETECTORS | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_FBL_DETECTORS | error | gate | 层级违规: 2525155 -> 2522108 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RECOVERY-D_FBL_VERIFICATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_FBL_VERIFICATION | error | gate | 层级违规: 2525127 -> 2522312 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RECOVERY-D_GOV_CODE_QUALITY | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_GOV_CODE_QUALITY | error | gate | 层级违规: 2525125 -> 2522723 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RECOVERY-D_GOV_DRIFT | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RECOVERY | D_GOV_DRIFT | error | gate | 层级违规: 2526162 -> 2522825 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RECOVERY-D_ORCHESTRATOR | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_ORCHESTRATOR | error | gate | 层级违规: 2525154 -> 2523537 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_GOV_OPS_RESILIENCE | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_GOV_OPS_RESILIENCE | error | gate | 层级违规: 2521705 -> 2522525 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_GOV_RULE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOV_RULE | error | gate | 层级违规: 2523209 -> 2522953 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 层级违规: 2524171 -> 2523883 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_INTELLIGENCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_INTELLIGENCE | error | gate | 层级违规: 2524169 -> 2523463 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_SECURITY | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SECURITY | error | gate | 层级违规: 2524169 -> 2523667 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | gate | 层级违规: 2524159 -> 2523982 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INTEGRATION-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_TRADING | error | gate | 层级违规: 2523340 -> 2524145 (L1_foundation -> L2_domain) |
| V-LAYER-D_ORCHESTRATOR-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_ORCHESTRATOR | D_GOVERNANCE | error | gate | 层级违规: 2523519 -> 2522551 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | gate | 层级违规: 2522794 -> 2522543 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_AUDIT | error | gate | 层级违规: 2523776 -> 2522651 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_DRIFT | error | gate | 层级违规: 2522843 -> 2522837 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_KB | error | gate | 层级违规: 2526201 -> 2522997 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_RULE | error | gate | 层级违规: 2523726 -> 2522938 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOVERNANCE | error | gate | 层级违规: 2525216 -> 2522372 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOV_DRIFT | error | gate | 层级违规: 2525222 -> 2522800 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-2421903 | 孤儿节点: 2421903 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-2421904 | 孤儿节点: 2421904 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-2421905 | 孤儿节点: 2421905 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-2421906 | 孤儿节点: 2421906 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-2521703 | 孤儿节点: 2521703 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2521704 | 孤儿节点: 2521704 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2521706 | 孤儿节点: 2521706 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2521707 | 孤儿节点: 2521707 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2521708 | 孤儿节点: 2521708 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2521709 | 孤儿节点: 2521709 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2521710 | 孤儿节点: 2521710 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2521762 | 孤儿节点: 2521762 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2521768 | 孤儿节点: 2521768 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2521798 | 孤儿节点: 2521798 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2521824 | 孤儿节点: 2521824 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521825 | 孤儿节点: 2521825 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2521826 | 孤儿节点: 2521826 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521827 | 孤儿节点: 2521827 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521828 | 孤儿节点: 2521828 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521829 | 孤儿节点: 2521829 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521830 | 孤儿节点: 2521830 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521831 | 孤儿节点: 2521831 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521832 | 孤儿节点: 2521832 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521833 | 孤儿节点: 2521833 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521834 | 孤儿节点: 2521834 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521835 | 孤儿节点: 2521835 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521836 | 孤儿节点: 2521836 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521837 | 孤儿节点: 2521837 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521838 | 孤儿节点: 2521838 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2521839 | 孤儿节点: 2521839 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521840 | 孤儿节点: 2521840 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521843 | 孤儿节点: 2521843 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521844 | 孤儿节点: 2521844 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521847 | 孤儿节点: 2521847 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521848 | 孤儿节点: 2521848 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521851 | 孤儿节点: 2521851 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521852 | 孤儿节点: 2521852 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521853 | 孤儿节点: 2521853 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521858 | 孤儿节点: 2521858 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521859 | 孤儿节点: 2521859 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521860 | 孤儿节点: 2521860 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521861 | 孤儿节点: 2521861 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521862 | 孤儿节点: 2521862 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521863 | 孤儿节点: 2521863 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521864 | 孤儿节点: 2521864 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2521865 | 孤儿节点: 2521865 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521866 | 孤儿节点: 2521866 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521867 | 孤儿节点: 2521867 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521868 | 孤儿节点: 2521868 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521869 | 孤儿节点: 2521869 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521870 | 孤儿节点: 2521870 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521871 | 孤儿节点: 2521871 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521872 | 孤儿节点: 2521872 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521873 | 孤儿节点: 2521873 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521874 | 孤儿节点: 2521874 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521875 | 孤儿节点: 2521875 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521876 | 孤儿节点: 2521876 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521877 | 孤儿节点: 2521877 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521878 | 孤儿节点: 2521878 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521879 | 孤儿节点: 2521879 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521880 | 孤儿节点: 2521880 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521881 | 孤儿节点: 2521881 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521882 | 孤儿节点: 2521882 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521883 | 孤儿节点: 2521883 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521884 | 孤儿节点: 2521884 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2521885 | 孤儿节点: 2521885 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521886 | 孤儿节点: 2521886 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2521888 | 孤儿节点: 2521888 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2521889 | 孤儿节点: 2521889 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2521890 | 孤儿节点: 2521890 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2521891 | 孤儿节点: 2521891 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2521892 | 孤儿节点: 2521892 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2521893 | 孤儿节点: 2521893 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521894 | 孤儿节点: 2521894 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521895 | 孤儿节点: 2521895 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521896 | 孤儿节点: 2521896 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521897 | 孤儿节点: 2521897 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521900 | 孤儿节点: 2521900 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521903 | 孤儿节点: 2521903 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521904 | 孤儿节点: 2521904 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521905 | 孤儿节点: 2521905 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521906 | 孤儿节点: 2521906 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521908 | 孤儿节点: 2521908 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521910 | 孤儿节点: 2521910 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521911 | 孤儿节点: 2521911 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521912 | 孤儿节点: 2521912 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521913 | 孤儿节点: 2521913 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521914 | 孤儿节点: 2521914 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521915 | 孤儿节点: 2521915 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521916 | 孤儿节点: 2521916 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521917 | 孤儿节点: 2521917 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521918 | 孤儿节点: 2521918 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521919 | 孤儿节点: 2521919 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521920 | 孤儿节点: 2521920 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521921 | 孤儿节点: 2521921 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521922 | 孤儿节点: 2521922 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521923 | 孤儿节点: 2521923 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2521924 | 孤儿节点: 2521924 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2521925 | 孤儿节点: 2521925 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2521926 | 孤儿节点: 2521926 | orphan_node | D_DATA_ENG |  | warn | open |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_FBL_VERIFICATION | 跨域违规: D_AUTONOMY_CORE -> D_FBL_VERIFICATION | cross_domain_violation | D_AUTONOMY_CORE | D_FBL_VERIFICATION | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_FEEDBACK_LOOP | 跨域违规: D_AUTONOMY_CORE -> D_FEEDBACK_LOOP | cross_domain_violation | D_AUTONOMY_CORE | D_FEEDBACK_LOOP | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTELLIGENCE | 跨域违规: D_AUTONOMY_CORE -> D_INTELLIGENCE | cross_domain_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_ORCHESTRATOR | 跨域违规: D_AUTONOMY_CORE -> D_ORCHESTRATOR | cross_domain_violation | D_AUTONOMY_CORE | D_ORCHESTRATOR | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_TRADING | 跨域违规: D_AUTONOMY_CORE -> D_TRADING | cross_domain_violation | D_AUTONOMY_CORE | D_TRADING | error | open |
| V-CROSS-D_AUTONOMY_PERM-D_SECURITY | 跨域违规: D_AUTONOMY_PERM -> D_SECURITY | cross_domain_violation | D_AUTONOMY_PERM | D_SECURITY | error | open |
| V-CROSS-D_BACKTEST-D_DATA | 跨域违规: D_BACKTEST -> D_DATA | cross_domain_violation | D_BACKTEST | D_DATA | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_AUDIT | 跨域违规: D_COMPLIANCE -> D_GOV_AUDIT | cross_domain_violation | D_COMPLIANCE | D_GOV_AUDIT | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_DRIFT | 跨域违规: D_COMPLIANCE -> D_GOV_DRIFT | cross_domain_violation | D_COMPLIANCE | D_GOV_DRIFT | error | open |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | open |
| V-CROSS-D_FBL_VERIFICATION-D_GOV_AUDIT | 跨域违规: D_FBL_VERIFICATION -> D_GOV_AUDIT | cross_domain_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DETECTORS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DETECTORS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DETECTORS | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DIAGNOSERS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DIAGNOSERS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | error | open |
| V-CROSS-D_FRONTEND-D_FEEDBACK_LOOP | 跨域违规: D_FRONTEND -> D_FEEDBACK_LOOP | cross_domain_violation | D_FRONTEND | D_FEEDBACK_LOOP | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_AUDIT | 跨域违规: D_GOVERNANCE -> D_GOV_AUDIT | cross_domain_violation | D_GOVERNANCE | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_CODE_QUALITY | 跨域违规: D_GOVERNANCE -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOVERNANCE | D_GOV_CODE_QUALITY | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_ENFORCEMENT | 跨域违规: D_GOVERNANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOVERNANCE | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_KB | 跨域违规: D_GOVERNANCE -> D_GOV_KB | cross_domain_violation | D_GOVERNANCE | D_GOV_KB | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOVERNANCE -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOVERNANCE | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_REPAIR | 跨域违规: D_GOVERNANCE -> D_GOV_REPAIR | cross_domain_violation | D_GOVERNANCE | D_GOV_REPAIR | error | open |
| V-CROSS-D_GOVERNANCE-D_INFRA_RECOVERY | 跨域违规: D_GOVERNANCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOVERNANCE | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_GOVERNANCE-D_INTELLIGENCE | 跨域违规: D_GOVERNANCE -> D_INTELLIGENCE | cross_domain_violation | D_GOVERNANCE | D_INTELLIGENCE | error | open |
| V-CROSS-D_GOVERNANCE-D_OPS | 跨域违规: D_GOVERNANCE -> D_OPS | cross_domain_violation | D_GOVERNANCE | D_OPS | error | open |
| V-CROSS-D_GOVERNANCE-D_TRADING | 跨域违规: D_GOVERNANCE -> D_TRADING | cross_domain_violation | D_GOVERNANCE | D_TRADING | error | open |
| V-CROSS-D_GOV_AUDIT-D_FBL_DIAGNOSERS | 跨域违规: D_GOV_AUDIT -> D_FBL_DIAGNOSERS | cross_domain_violation | D_GOV_AUDIT | D_FBL_DIAGNOSERS | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_AUDIT -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_AUDIT | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOV_RULE | 跨域违规: D_GOV_AUDIT -> D_GOV_RULE | cross_domain_violation | D_GOV_AUDIT | D_GOV_RULE | error | open |
| V-CROSS-D_GOV_AUDIT-D_INFRA_A2A | 跨域违规: D_GOV_AUDIT -> D_INFRA_A2A | cross_domain_violation | D_GOV_AUDIT | D_INFRA_A2A | error | open |
| V-CROSS-D_GOV_AUDIT-D_INFRA_RUNTIME | 跨域违规: D_GOV_AUDIT -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_AUDIT | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_GOV_AUDIT-D_INTELLIGENCE | 跨域违规: D_GOV_AUDIT -> D_INTELLIGENCE | cross_domain_violation | D_GOV_AUDIT | D_INTELLIGENCE | error | open |
| V-CROSS-D_GOV_AUDIT-D_SHARED | 跨域违规: D_GOV_AUDIT -> D_SHARED | cross_domain_violation | D_GOV_AUDIT | D_SHARED | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_CODE_QUALITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_SHARED | 跨域违规: D_GOV_CODE_QUALITY -> D_SHARED | cross_domain_violation | D_GOV_CODE_QUALITY | D_SHARED | error | open |
| V-CROSS-D_GOV_DRIFT-D_GOVERNANCE | 跨域违规: D_GOV_DRIFT -> D_GOVERNANCE | cross_domain_violation | D_GOV_DRIFT | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_DRIFT-D_GOV_AUDIT | 跨域违规: D_GOV_DRIFT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_DRIFT | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_DRIFT-D_SHARED | 跨域违规: D_GOV_DRIFT -> D_SHARED | cross_domain_violation | D_GOV_DRIFT | D_SHARED | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_AUDIT | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_CODE_QUALITY | error | open |
| V-CROSS-D_GOV_KB-D_SHARED | 跨域违规: D_GOV_KB -> D_SHARED | cross_domain_violation | D_GOV_KB | D_SHARED | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOVERNANCE | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOV_AUDIT | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOV_AUDIT | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOV_DRIFT | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOV_DRIFT | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOV_DRIFT | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INFRA_RECOVERY | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INTEGRATION | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INTEGRATION | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INTEGRATION | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_OPS | 跨域违规: D_GOV_OPS_RESILIENCE -> D_OPS | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_OPS | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_ORCHESTRATOR | 跨域违规: D_GOV_OPS_RESILIENCE -> D_ORCHESTRATOR | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_ORCHESTRATOR | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_SHARED | 跨域违规: D_GOV_OPS_RESILIENCE -> D_SHARED | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_SHARED | error | open |
| V-CROSS-D_GOV_REPAIR-D_FACTOR | 跨域违规: D_GOV_REPAIR -> D_FACTOR | cross_domain_violation | D_GOV_REPAIR | D_FACTOR | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOVERNANCE | 跨域违规: D_GOV_REPAIR -> D_GOVERNANCE | cross_domain_violation | D_GOV_REPAIR | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_AUDIT | 跨域违规: D_GOV_REPAIR -> D_GOV_AUDIT | cross_domain_violation | D_GOV_REPAIR | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_DRIFT | 跨域违规: D_GOV_REPAIR -> D_GOV_DRIFT | cross_domain_violation | D_GOV_REPAIR | D_GOV_DRIFT | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_REPAIR -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_REPAIR | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_KB | 跨域违规: D_GOV_REPAIR -> D_GOV_KB | cross_domain_violation | D_GOV_REPAIR | D_GOV_KB | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_REPAIR -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_REPAIR | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_RULE | 跨域违规: D_GOV_REPAIR -> D_GOV_RULE | cross_domain_violation | D_GOV_REPAIR | D_GOV_RULE | error | open |
| V-CROSS-D_GOV_REPAIR-D_INFRASTRUCTURE | 跨域违规: D_GOV_REPAIR -> D_INFRASTRUCTURE | cross_domain_violation | D_GOV_REPAIR | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_GOV_REPAIR-D_INFRA_RUNTIME | 跨域违规: D_GOV_REPAIR -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_REPAIR | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_GOV_REPAIR-D_TRADING | 跨域违规: D_GOV_REPAIR -> D_TRADING | cross_domain_violation | D_GOV_REPAIR | D_TRADING | error | open |
| V-CROSS-D_GOV_RULE-D_GOVERNANCE | 跨域违规: D_GOV_RULE -> D_GOVERNANCE | cross_domain_violation | D_GOV_RULE | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_RULE-D_INTEGRATION | 跨域违规: D_GOV_RULE -> D_INTEGRATION | cross_domain_violation | D_GOV_RULE | D_INTEGRATION | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_DATA | 跨域违规: D_GOV_SCRIPTS -> D_DATA | cross_domain_violation | D_GOV_SCRIPTS | D_DATA | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_GOVERNANCE | 跨域违规: D_GOV_SCRIPTS -> D_GOVERNANCE | cross_domain_violation | D_GOV_SCRIPTS | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_RULE | 跨域违规: D_GOV_SCRIPTS -> D_GOV_RULE | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_RULE | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_SHARED | 跨域违规: D_GOV_SCRIPTS -> D_SHARED | cross_domain_violation | D_GOV_SCRIPTS | D_SHARED | error | open |
| V-CROSS-D_INFRASTRUCTURE-D_SHARED | 跨域违规: D_INFRASTRUCTURE -> D_SHARED | cross_domain_violation | D_INFRASTRUCTURE | D_SHARED | error | open |
| V-CROSS-D_INFRA_A2A-D_GOVERNANCE | 跨域违规: D_INFRA_A2A -> D_GOVERNANCE | cross_domain_violation | D_INFRA_A2A | D_GOVERNANCE | error | open |
| V-CROSS-D_INFRA_RECOVERY-D_GOV_CODE_QUALITY | 跨域违规: D_INFRA_RECOVERY -> D_GOV_CODE_QUALITY | cross_domain_violation | D_INFRA_RECOVERY | D_GOV_CODE_QUALITY | error | open |
| V-CROSS-D_INFRA_RECOVERY-D_GOV_DRIFT | 跨域违规: D_INFRA_RECOVERY -> D_GOV_DRIFT | cross_domain_violation | D_INFRA_RECOVERY | D_GOV_DRIFT | error | open |
| V-CROSS-D_INFRA_RECOVERY-D_INFRA_RUNTIME | 跨域违规: D_INFRA_RECOVERY -> D_INFRA_RUNTIME | cross_domain_violation | D_INFRA_RECOVERY | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_RULE | 跨域违规: D_INFRA_RUNTIME -> D_GOV_RULE | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_RULE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INFRA_A2A | 跨域违规: D_INFRA_RUNTIME -> D_INFRA_A2A | cross_domain_violation | D_INFRA_RUNTIME | D_INFRA_A2A | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INTEGRATION | 跨域违规: D_INFRA_RUNTIME -> D_INTEGRATION | cross_domain_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | open |
| V-CROSS-D_INTELLIGENCE-D_GOV_DRIFT | 跨域违规: D_INTELLIGENCE -> D_GOV_DRIFT | cross_domain_violation | D_INTELLIGENCE | D_GOV_DRIFT | error | open |
| V-CROSS-D_KNOWLEDGE-D_FEEDBACK_LOOP | 跨域违规: D_KNOWLEDGE -> D_FEEDBACK_LOOP | cross_domain_violation | D_KNOWLEDGE | D_FEEDBACK_LOOP | error | open |
| V-CROSS-D_REPORTING-D_INFRASTRUCTURE | 跨域违规: D_REPORTING -> D_INFRASTRUCTURE | cross_domain_violation | D_REPORTING | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_RISK-D_INFRASTRUCTURE | 跨域违规: D_RISK -> D_INFRASTRUCTURE | cross_domain_violation | D_RISK | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_SECURITY-D_GOV_DRIFT | 跨域违规: D_SECURITY -> D_GOV_DRIFT | cross_domain_violation | D_SECURITY | D_GOV_DRIFT | error | open |
| V-CROSS-D_SECURITY-D_SECURITY_LLM | 跨域违规: D_SECURITY -> D_SECURITY_LLM | cross_domain_violation | D_SECURITY | D_SECURITY_LLM | error | open |
| V-CROSS-D_SECURITY_LLM-D_INFRA_RUNTIME | 跨域违规: D_SECURITY_LLM -> D_INFRA_RUNTIME | cross_domain_violation | D_SECURITY_LLM | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_SECURITY_LLM-D_ORCHESTRATOR | 跨域违规: D_SECURITY_LLM -> D_ORCHESTRATOR | cross_domain_violation | D_SECURITY_LLM | D_ORCHESTRATOR | error | open |
| V-CROSS-D_SECURITY_LLM-D_SECURITY | 跨域违规: D_SECURITY_LLM -> D_SECURITY | cross_domain_violation | D_SECURITY_LLM | D_SECURITY | error | open |
| V-CROSS-D_SECURITY_LLM-D_SHARED | 跨域违规: D_SECURITY_LLM -> D_SHARED | cross_domain_violation | D_SECURITY_LLM | D_SHARED | error | open |
| V-CROSS-D_SHARED-D_DATA | 跨域违规: D_SHARED -> D_DATA | cross_domain_violation | D_SHARED | D_DATA | error | open |
| V-CROSS-D_SHARED-D_GOV_OPS_RESILIENCE | 跨域违规: D_SHARED -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_SHARED | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_SHARED-D_INFRA_RUNTIME | 跨域违规: D_SHARED -> D_INFRA_RUNTIME | cross_domain_violation | D_SHARED | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_SHARED-D_INTEGRATION | 跨域违规: D_SHARED -> D_INTEGRATION | cross_domain_violation | D_SHARED | D_INTEGRATION | error | open |
| V-CROSS-D_SIGLEGACY-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_SIGLEGACY -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_SIGLEGACY | D_FUNDAMENTAL_SIGNAL | error | open |
| V-CROSS-D_TRADING-D_INFRASTRUCTURE | 跨域违规: D_TRADING -> D_INFRASTRUCTURE | cross_domain_violation | D_TRADING | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_TRADING-D_INTEGRATION | 跨域违规: D_TRADING -> D_INTEGRATION | cross_domain_violation | D_TRADING | D_INTEGRATION | error | open |
| V-CROSS-D_TRADING-D_ORCHESTRATOR | 跨域违规: D_TRADING -> D_ORCHESTRATOR | cross_domain_violation | D_TRADING | D_ORCHESTRATOR | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_TRADING | error | open |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | open |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | open |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | open |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_FACTOR | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_FACTOR | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_DRIFT | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_KB | error | open |
| V-LAYER-D_INFRA_A2A-D_FEEDBACK_LOOP | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_FEEDBACK_LOOP | error | open |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_FBL_DETECTORS | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_FBL_DETECTORS | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_FBL_VERIFICATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_FBL_VERIFICATION | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_GOV_CODE_QUALITY | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_GOV_CODE_QUALITY | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_GOV_DRIFT | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RECOVERY | D_GOV_DRIFT | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_ORCHESTRATOR | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_ORCHESTRATOR | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_GOV_OPS_RESILIENCE | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_GOV_OPS_RESILIENCE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_GOV_RULE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOV_RULE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_INTELLIGENCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_INTELLIGENCE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_SECURITY | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SECURITY | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | open |
| V-LAYER-D_INTEGRATION-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_TRADING | error | open |
| V-LAYER-D_ORCHESTRATOR-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_ORCHESTRATOR | D_GOVERNANCE | error | open |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | open |
| V-LAYER-D_SECURITY-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_AUDIT | error | open |
| V-LAYER-D_SECURITY-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_DRIFT | error | open |
| V-LAYER-D_SECURITY-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_KB | error | open |
| V-LAYER-D_SECURITY-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_RULE | error | open |
| V-LAYER-D_SHARED-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOVERNANCE | error | open |
| V-LAYER-D_SHARED-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOV_DRIFT | error | open |
