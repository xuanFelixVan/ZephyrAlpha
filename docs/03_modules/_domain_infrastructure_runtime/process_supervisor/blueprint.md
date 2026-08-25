---
module_id: MOD-INF-066
title: "NSSM+5 进程架构与自研 Supervisor 蓝图 — 启动升序/关闭降序编排+分级心跳+崩溃重启策略+服务定义就绪件"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L00_infrastructure
layer_name: infrastructure_runtime
functional_domain: infrastructure_runtime
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
design_maturity: design
build_status: testing
responsibility_domain: 
---

# MOD-INF-066 Process Supervisor — NSSM+5 进程架构与自研 Supervisor 蓝图

> **module_id**: MOD-INF-066 | **域**: D_INFRA_RUNTIME | **层**: L00 基础设施运行时
> **优先级**: P0 | **来源**: CAND-H1FS-002（B14-04521，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-INF-066

## 1. 定位

进程守护散件（MOD-INF-035 windows_service / health_monitor / lifecycle_manager、
MOD-INF-039 startup_sequencer）齐备，但 **NSSM 服务化注册与 P1~P5 优先级启停
编排未收口**；进程守护与断电自启属保命面。本模块收口 A9 §1.1：

- 五进程注册表（P1 market_data=10 / P3 trading_core=15 / P2 signal_engine=20 /
  P4 ai_autonomy=30 / P5 ml_pipeline=40，数值越小优先级越高）；
- 启动=优先级数值升序（P1→P3→P2→P4→P5），关闭=降序（P5→P4→P2→P3→P1）；
  硬约束：P3 先于 P1 关闭（挂单先撤回），P1 先于 Redis 关闭（末条行情先持久化）；
- 分级心跳 hb:{process}（P1 3s/15s、P3 2s/10s、P2 5s/30s、P4 10s/60s、
  P5 30s/120s；TTL=超时+30s 缓冲，规则复用 MOD-INF-063）；
- 崩溃重启策略：P3 任何时段不自动重启（HC-01 仅告警+人工）；P1/P2 交易时段
  告警+降级、非交易时段自动重启；P4/P5 自动重启（3 次上限终止重启循环）；
- 日志托管声明（NSSM AppStdout/AppStderr 落盘）。

## 2. 输入 / 输出

- 输入：进程 ID / 是否交易时段 / 连续失败次数（崩溃判定）。
- 输出：`FIVE_PROCESS_REGISTRY`；`compute_start_order()`/`compute_shutdown_order()`；
  `decide_crash_action()` → CrashAction 纯数据判定；`render_nssm_service_definitions()`
  服务定义声明 dict；`render_nssm_install_script()` 安装脚本**草稿文本**。

## 3. 核心规则

1. 编排真源=A9 §1.1 启动/关闭序列图；P3 先于 P1、P1 先于 Redis 为硬校验。
2. HC-01 不可降级：P3 崩溃判定恒 alert_only（任何时段），不得放宽。
3. Fail-Closed：未知进程 ID/注册表畸形（优先级重复/心跳倒挂/核号重叠）→
   抛 ProcessSupervisorError。
4. **硬边界（Owner 窗口）**：NSSM 注册、开机自启、计划任务、核亲和、禁 swap
   等系统级动作 AI 一律不执行——本模块只产出配置就绪件（服务定义 YAML +
   安装脚本草稿 + Supervisor 策略代码）。

## 4. 依赖前置

- MOD-INF-064 trading_core_process_spec（P3 条目规格派生，不重复声明）。
- MOD-INF-063 redis_state_layer_ssot（hb 命名空间 TTL 规则复用）。
- 契约对齐：MOD-INF-035/039（守护散件边界）、MOD-INF-016 ProcessLifecycleGateway
  （未来实际 spawn 通道；本 MVP 只产出编排策略与判定，不发起进程）。

## 5. 验收标准

- 单测全绿（五进程注册表真源值/启停序列/硬约束/心跳键与 TTL/崩溃判定全
  分支/注册表一致性/服务定义与脚本草稿含 Owner 标注）；相关域集成零回归。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-066`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-066` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-INF-066` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-066 | MOD-INF-066 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | testing | testing | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
