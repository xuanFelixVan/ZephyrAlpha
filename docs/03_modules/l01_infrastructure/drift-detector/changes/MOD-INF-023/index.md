---
doc_type: index
status: active
title: "MOD-INF-023 — 目录索引"
version: "1.1.0"
created: "2026-05-06"
updated: "2026-05-06"
---

# MOD-INF-023 — Drift Detector 任务卡索引

> 蓝图真源：[`blueprint.md`](../../blueprint.md) | version 0.7.0 | 38 决策 | 38 文件 | 31 漂移维度 | 4 施工 Phase

## 目录内容（65 张任务卡）

| 任务卡 ID | 标题 | 优先级 | 关联决策 |
|-----------|------|:--:|---------|
| [TASK-INF-0001](TASK-INF-0001.md) | 模块骨架搭建与目录结构初始化 | P0 | — |
| [TASK-INF-0002](TASK-INF-0002.md) | 核心引擎 drift_engine.py + 数据模型 drift_models.py 实现 | P0 | — |
| [TASK-INF-0003](TASK-INF-0003.md) | 检测器注册表填充 + detector_dispatcher.py 并行调度器 | P0 | D-023-01, D-023-05 |
| [TASK-INF-0004](TASK-INF-0004.md) | 基线快照管理器 baseline_manager.py | P0 | D-023-03 |
| [TASK-INF-0005](TASK-INF-0005.md) | 漂移状态机 state_machine.py（10状态） | P0 | D-023-04 |
| [TASK-INF-0006](TASK-INF-0006.md) | 自动对账器 reconciler.py + incremental_scanner.py | P0 | D-023-02, D-023-05 |
| [TASK-INF-0007](TASK-INF-0007.md) | 检测触发策略与维护窗口 | P0 | D-023-06 |
| [TASK-INF-0008](TASK-INF-0008.md) | 自漂移检测 self_check.py | P0 | D-023-07 |
| [TASK-INF-0009](TASK-INF-0009.md) | 并发竞争控制——乐观并发 + AI施工优先 | P0 | D-023-11 |
| [TASK-INF-0010](TASK-INF-0010.md) | 漂移预算与施工门禁 | P0 | D-023-12 |
| [TASK-INF-0011](TASK-INF-0011.md) | 崩溃恢复与检查点机制 | P0 | D-023-17 |
| [TASK-INF-0012](TASK-INF-0012.md) | 漂移风暴与批量处理模式 | P1 | D-023-18 |
| [TASK-INF-0013](TASK-INF-0013.md) | 热修复/紧急变更旁路 | P1 | D-023-19 |
| [TASK-INF-0014](TASK-INF-0014.md) | 环境感知与渐进部署漂移 | P1 | D-023-20 |
| [TASK-INF-0015](TASK-INF-0015.md) | 自动学习假阳性模式识别与抑制 | P1 | D-023-21 |
| [TASK-INF-0016](TASK-INF-0016.md) | 多实例竞态控制——scan mutex | P1 | D-023-24 |
| [TASK-INF-0017](TASK-INF-0017.md) | 孤儿资源检测 orphan_scanner.py | P1 | D-023-25 |
| [TASK-INF-0018](TASK-INF-0018.md) | 符号链接与子模块完整性检查 symlink_checker.py | P1 | D-023-26 |
| [TASK-INF-0019](TASK-INF-0019.md) | 文件底层属性漂移检测 file_attr_checker.py | P1 | D-023-27 |
| [TASK-INF-0020](TASK-INF-0020.md) | 冷启动策略 cold_start.py | P0 | D-023-33 |
| [TASK-INF-0021](TASK-INF-0021.md) | Owner 缺席模式 absence_manager.py | P0 | D-023-34 |
| [TASK-INF-0022](TASK-INF-0022.md) | 告警可信度评分 credibility_engine.py | P1 | D-023-35 |
| [TASK-INF-0023](TASK-INF-0023.md) | 漂移维度完整清单——31维检测器覆盖矩阵 | P1 | §3 |
| [TASK-INF-0024](TASK-INF-0024.md) | AI 施工场景专用检测器——6类AI特有漂移模式 | P0 | §4.2 |
| [TASK-INF-0025](TASK-INF-0025.md) | 时序存储与趋势分析 trend_analyzer.py | P1 | D-023-08 |
| [TASK-INF-0026](TASK-INF-0026.md) | 关联引擎 correlation_engine.py | P1 | D-023-09 |
| [TASK-INF-0027](TASK-INF-0027.md) | 覆盖率仪表板 dashboard.py | P1 | §5.3 |
| [TASK-INF-0028](TASK-INF-0028.md) | 告警路由与疲劳管理 alert_router.py | P0 | D-023-13 |
| [TASK-INF-0029](TASK-INF-0029.md) | 修复ROI优先级引擎 roi_engine.py | P1 | D-023-14 |
| [TASK-INF-0030](TASK-INF-0030.md) | Git Bisect 溯源集成 git_bisector.py | P1 | D-023-15 |
| [TASK-INF-0031](TASK-INF-0031.md) | Evolution Engine 反馈闭环集成 | P1 | D-023-10 |
| [TASK-INF-0032](TASK-INF-0032.md) | 语义漂移检测——YAML间概念/枚举/归属一致性 | P1 | §6.2 |
| [TASK-INF-0033](TASK-INF-0033.md) | DB Schema 三方对账漂移检测 | P1 | §6.3 |
| [TASK-INF-0034](TASK-INF-0034.md) | 依赖版本漂移检测 | P1 | §6.4 |
| [TASK-INF-0035](TASK-INF-0035.md) | 安全策略漂移检测 | P1 | §6.5 |
| [TASK-INF-0036](TASK-INF-0036.md) | 文档-代码共演化漂移检测 | P1 | §6.6 |
| [TASK-INF-0037](TASK-INF-0037.md) | 测试覆盖漂移检测 | P1 | §6.7 |
| [TASK-INF-0038](TASK-INF-0038.md) | AI上下文注入——施工前预检 ai_context_injector.py | P0 | D-023-16 |
| [TASK-INF-0039](TASK-INF-0039.md) | 漂移演练手册自动生成 runbook_generator.py | P1 | §6.9 |
| [TASK-INF-0040](TASK-INF-0040.md) | 知识图谱实体化集成 | P1 | §6.10 |
| [TASK-INF-0041](TASK-INF-0041.md) | 检测器金丝雀部署 canary_controller.py | P1 | §6.11 |
| [TASK-INF-0042](TASK-INF-0042.md) | 漂移作为AI训练数据闭环 | P1 | §6.12 |
| [TASK-INF-0043](TASK-INF-0043.md) | 混沌工程——主动漂移注入 chaos_injector.py | P1 | §6.13 |
| [TASK-INF-0044](TASK-INF-0044.md) | 跨Session修复上下文交接 handoff_manager.py | P1 | §6.14 |
| [TASK-INF-0045](TASK-INF-0045.md) | 级联故障检测 cascade_detector.py | P0 | D-023-22 |
| [TASK-INF-0046](TASK-INF-0046.md) | 资源上限与优雅降级 resource_guard.py | P0 | D-023-23 |
| [TASK-INF-0047](TASK-INF-0047.md) | 漂移取证引擎 forensics_engine.py | P1 | §6.17 |
| [TASK-INF-0048](TASK-INF-0048.md) | 跨语言漂移检测框架 | P1 | §6.18 |
| [TASK-INF-0049](TASK-INF-0049.md) | 供应商锁定与基础设施迁移漂移 | P1 | §6.19 |
| [TASK-INF-0050](TASK-INF-0050.md) | 测试夹具漂移检测 test_fixture_checker.py | P1 | D-023-28 |
| [TASK-INF-0051](TASK-INF-0051.md) | 配置多源一致性 config_consistency.py | P1 | D-023-29 |
| [TASK-INF-0052](TASK-INF-0052.md) | Python版本兼容性漂移检测 python_compat.py | P1 | D-023-30 |
| [TASK-INF-0053](TASK-INF-0053.md) | 向后兼容策略漂移检测 backcompat_checker.py | P1 | D-023-31 |
| [TASK-INF-0054](TASK-INF-0054.md) | .gitignore完整性审计 gitignore_auditor.py | P1 | D-023-32 |
| [TASK-INF-0055](TASK-INF-0055.md) | 基线投毒防护 baseline_poisoning_guard.py | P1 | D-023-36 |
| [TASK-INF-0056](TASK-INF-0056.md) | 防篡改审计 tamper_proof_audit.py | P1 | D-023-37 |
| [TASK-INF-0057](TASK-INF-0057.md) | 命名约定与魔数字符串漂移 naming_magic_checker.py | P1 | D-023-38 |
| [TASK-INF-0058](TASK-INF-0058.md) | 全部38文件创建与初始化（§7文件组成清单） | P0 | §7 |
| [TASK-INF-0059](TASK-INF-0059.md) | Phase scaffold 施工执行（11项） | P0 | §8 |
| [TASK-INF-0060](TASK-INF-0060.md) | Phase experimental 施工执行（16项） | P0 | §8 |
| [TASK-INF-0061](TASK-INF-0061.md) | Phase beta 施工执行（20项） | P0 | §8 |
| [TASK-INF-0062](TASK-INF-0062.md) | Phase production 施工执行（15项） | P0 | §8 |
| [TASK-INF-0063](TASK-INF-0063.md) | G-CT-005 契约——漂移信号→Rollback 集成 | P0 | G-CT-005 |
| [TASK-INF-0064](TASK-INF-0064.md) | depends_on 依赖验证与集成对账 | P0 | depends_on |
| [TASK-INF-0065](TASK-INF-0065.md) | 变更管理——蓝图版本更新与construction_progress追踪 | P1 | §变更记录 |

## 统计摘要

| 维度 | 数量 |
|------|:--:|
| 任务卡总数 | 65 |
| P0 级任务卡 | 23 |
| P1 级任务卡 | 42 |
| 覆盖决策 | 38/38 |
| 覆盖蓝图章节 | 12/12 |
| 覆盖集成契约 | 5/5 |
| 覆盖施工 Phase | 4/4 |
| 覆盖漂移维度 | 31/31 |
| 覆盖 §7 文件 | 38/38 |

## 导航

- [蓝图真源](../../blueprint.md)
- [上级目录](../index.md)
- [项目根](../../index.md)
