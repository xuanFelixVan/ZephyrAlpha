---
module_id: KE-4184
title: 目录内容（65 张任务卡）
category: module_blueprint
ttl: permanent
---

# 目录内容（65 张任务卡）

目录内容（65 张任务卡）

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
| [TASK-INF-0038](TASK-INF-0038.md) | AI上下文注入——施工
