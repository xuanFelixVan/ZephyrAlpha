---


task_id: TASK-MOD-INF-001-0017
module_id: MOD-INF-001
title: "第五轮外部取证审计关闭：取证发现 #55 至 #67 + M-42~M-46 + 外部看门狗"
doc_type: task_card
status: done
priority: P1
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T03:04:00+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0006
  - TASK-MOD-INF-001-0010
  - TASK-MOD-INF-001-0016
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\heartbeat_server.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\blueprint_code_auditor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\model_capacity_probe.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\combinatorial_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\dual_channel_alert.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\task_heartbeat.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\owner_trust_gauge.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\capacity_calibrator.py"
  - "D:\\ZephyrAlpha\\config\\capacity\\external_watchdog.yaml"
  - "D:\\ZephyrAlpha\\config\\capacity\\ai_context_policy.yaml"
acceptance_criteria:
  - "#55 递归不可观测性→ExternalWatchdog: 外部心跳检测(5min),3次无响应→告警,6次→紧急通知"
  - "#56 蓝图-实现漂移→BlueprintCodeAuditor: 正则匹配关键数值(2×内存/30%启动退化/90%内存/Kill Switch drill)"
  - "#57 AI模型静默升级→ModelCapacityProbe: 每日07:00金丝雀任务,延迟/Token/代码行数漂移检测"
  - "#58 门禁沙漠交叉→CombinatorialGate: N≥3变更时全组合模拟,组合放大>1.3×→BLOCK+分拆方案"
  - "#59 Kill Switch悖论→EmergencyPool: 启动预分配5MB应急池,activate()先释放→再执行保护动作"
  - "#60 非线性涌现→ProgressiveCapacityCalibrator: 每100模块自动校准,误差>20%→修正因子"
  - "#61 告警管道单点→DualChannelAlertManager: 主通道(飞书)+备用(本地文件)+终端唤醒+闭环确认"
  - "#62 蓝图作为攻击手册→BlueprintAccessFilter: 分级访问(public/internal/forensic),敏感阈值移除"
  - "#63 僵尸任务→TaskHeartbeatMonitor: 10min心跳超时+僵尸标记+半写入文件回滚"
  - "#64 Owner信任漂移→OwnerTrustGauge: alert_dismissal_rate>30%→CRITICALLY_LOW,>30min→COMPLACENT"
  - "#65 Solo Coder经济约束→启动时打印月度成本报告(¥5~¥10/月+知情同意)"
  - "#66 Windows崩溃转储→部署脚本Disable-WERCrashDump"
  - "#67 atexit竞态→graceful_shutdown import在Kill Switch就绪前强制执行"
  - "4项快速取证记录: SLO后见之明/WER二次伤害/atexit竞态/影子测试蒸发"
rollback_instructions:
  - "外部取证模块独立，删除不影响核心保障"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§24 第五轮外部取证审计 #55-#67", "§24.12 快速取证补充", "§24.15 M-42~M-46", "§24.14 取证专家最终判词"]
    purpose: "提取外部取证13个取证发现+4项快速取证+M-42~M-46"
tags:
  - capacity-assurance
  - blind-spots
  - round-5
  - BS-055-to-BS-067
  - external-forensic
  - forensic-auditor
phase: phase_2_enhance
estimated_effort_minutes: 200
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §24 第五轮外部取证审计 #55-#67"
description: "第五轮外部取证审计关闭：取证发现 #55 至 #67 + M-42~M-46 + 外部看门狗"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\heartbeat_server.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\blueprint_code_auditor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\model_capacity_probe.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\combinatorial_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\dual_channel_alert.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\task_heartbeat.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\owner_trust_gauge.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\capacity_calibrator.py"
  - "D:\\ZephyrAlpha\\config\\capacity\\external_watchdog.yaml"
  - "D:\\ZephyrAlpha\\config\\capacity\\ai_context_policy.yaml"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\src\zephyr\shared\schemas.py"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-{DOMAIN}-{NNNN}"
  - module_id: "PS-STD-011"
  - module_id: "ADR-0040"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 60000
timeout_minutes: 200
depends_on:
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0006
  - TASK-MOD-INF-001-0010
  - TASK-MOD-INF-001-0016
blocked_by: []
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-001"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []


---



# 第五轮外部取证审计关闭：取证发现 #55 至 #67 + M-42~M-46

## 1. 任务来源

从蓝图 §24 "第五轮——外部取证审计（v2.6.0 新增）" 提取。

方法论切换：前四轮是"系统内部的设计者审视自己的盲点"。第五轮视角是：一名独立的外部取证专家（Forensic Auditor）被召来调查这个容量保障体系。使用五个穿透性问题：假设链分析 / 递归断裂点 / 组合爆炸 / 敌手思维 / "成功"的隐藏代价。

## 2. 取证发现清单与关闭映射

| # | 取证盲点 | 严重度 | 取证类型 | 关闭方式 |
|:---:|------|:---:|------|---------|
| #55 | 递归不可观测性——"冻结仪表盘悖论" | 致命 | 递归断裂 | External Watchdog + HeartbeatServer (M-42) |
| #56 | 蓝图-实现漂移——纸上的设计≠磁盘上的实现 | 致命 | 实现漂移 | BlueprintCodeAuditor (M-43) |
| #57 | AI模型静默升级——容量画像是昨天的 | 高 | 环境漂移 | ModelCapacityProbe (M-44) |
| #58 | 门禁的沙漠交叉——10个PASS=1个CRASH | 高 | 组合爆炸 | CombinatorialGate |
| #59 | Kill Switch的悖论——保护动作消耗被保护对象 | 致命 | 自指涉悖论 | Emergency Pool (Kill Switch增强) |
| #60 | 非线性涌现——1500模块的"相变" | 高 | 规模涌现 | ProgressiveCapacityCalibrator |
| #61 | 告警管道的单点故障——全部告警走一根管 | 高 | 通道单点 | DualChannelAlertManager |
| #62 | 蓝图作为攻击手册——AI读蓝本=拿到了越狱指南 | 致命 | 信息泄露 | BlueprintAccessFilter + Tiered Access |
| #63 | 僵尸任务——Session崩溃后任务永悬 | 高 | 状态逸失 | TaskHeartbeatMonitor (M-45) |
| #64 | Owner信任度漂移——信任没有自动校准 | 高 | 人为因素 | OwnerTrustGauge (M-46) |
| #65 | Solo Coder经济约束——保障本身烧钱 | 中 | 经济边界 | 月度成本透明度报告 |
| #66 | Windows崩溃转储→二次填满磁盘 | 中 | 环境陷阱 | Disable-WER + DumpType=0 |
| #67 | atexit竞态条件——关机钩子未注册 | 中 | 竞态条件 | 启动顺序强制执行 |

### 2.1 快速取证补充（4项）

| 取证 | 发现 | 方案 |
|------|------|------|
| 快速取证A | SLO的"后见之明偏差"——SLO目标系统性乐观 | §5 SLO Review中已部分覆盖，施工期需替代机制 |
| 快速取证B | Windows崩溃转储二次伤害——8GB .dmp填满磁盘 | 部署脚本 Disable-WERCrashDump |
| 快速取证C | Python atexit 与 Kill Switch 竞态 | graceful_shutdown import必须在Kill Switch就绪前完成 |
| 快速取证D | "影子测试"幽灵——AI可能优化掉测试 | Kill Switch/ErrorBudget Tracker测试也加入IMMUTABLE_CORE |

## 3. 施工内容

### 3.1 #55: External Watchdog + HeartbeatServer (M-42)

文件：`D:\ZephyrAlpha\src\zephyr\shared\heartbeat_server.py`

- 独立轻量 HTTP 心跳服务（端口 8899）
- `/health` endpoint: 返回 governance_loop_last_eval / error_budget_pct / memory_pct / timestamp
- 外部看门狗配置 `external_watchdog.yaml`：三个选项
  - Option A: 云函数（阿里云/AWS Lambda, 5min HTTP check）
  - Option B: 手机Termux（Python脚本, 5min check）
  - Option C: 死人开关（deadmansswitch.net, TTL=30min, 每5min续期）
- 强制项：Solo Coder场景下，无外部看门狗=系统死亡不会被发现

### 3.2 #56: BlueprintCodeAuditor (M-43)

文件：`D:\ZephyrAlpha\src\zephyr\shared\blueprint_code_auditor.py`

- 4 项蓝图断言（正则匹配代码中的关键数值）：
  - CapacityFingerprint memory阈值=2.0倍
  - CapacityDigitalTwin 启动退化=30%
  - CapacityDigitalTwin 内存退化=50%
  - Kill Switch 保守模式=90%内存
- `weekly_audit()`: 每周一09:00执行，发现CRITICAL漂移→P0告警

### 3.3 #57: ModelCapacityProbe (M-44)

文件：`D:\ZephyrAlpha\src\zephyr\shared\model_capacity_probe.py`

- 标准化金丝雀任务："实现一个函数 add(a: int, b: int) -> int"
- `probe_all_active_models()`: 每天07:00对所有活跃模型发送
- 对比昨天：延迟漂移 / Token产出漂移（>30%）/ 代码行数漂移（>50%）
- 自动更新 profile（指数平滑）

### 3.4 #58: CombinatorialGate

文件：`D:\ZephyrAlpha\src\zephyr\shared\combinatorial_gate.py`

- `check(task_card)`: N≥3变更时→全组合模拟 vs 各自独立之和
- 组合放大>1.3×→BLOCK + 生成分拆方案（分3个commit，间隔10min）
- 集成到 G5 门禁

### 3.5 #59: Kill Switch Emergency Pool

在 `kill_switch.py` 中增强：
- `emergency_pool = bytearray(5 * 1024 * 1024)` 启动时预分配5MB
- `activate()`: Step1释放应急池→Step2激活conservative模式→Step3最轻量日志→Step4暂停非关键→Step5安全持久化

### 3.6 #60: ProgressiveCapacityCalibrator

文件：`D:\ZephyrAlpha\src\zephyr\shared\capacity_calibrator.py`

- 校准点：[100, 200, 500, 800, 1000, 1200, 1500]
- `on_module_count_reached(count)`: 测量实际容量→对比预测→误差>20%→修正模型
- 用户看到："⚠️ 容量预测模型在500模块处校准——偏差35%——已自动修正"

### 3.7 #61: DualChannelAlertManager

文件：`D:\ZephyrAlpha\src\zephyr\shared\dual_channel_alert.py`

- 三通道：primary(飞书Webhook) / secondary(本地文件持久化) / tertiary(终端唤醒)
- `send_and_verify(alert)`: 发送→本地持久化→终端唤醒→等待Owner确认
- `startup_unacknowledged_scan()`: 重启后扫描未确认本地告警
- 关键原则：网络不可靠→本地磁盘可靠

### 3.8 #62: BlueprintAccessFilter

文件：`D:\ZephyrAlpha\src\zephyr\shared\context_assembler.py` + `D:\ZephyrAlpha\config\capacity\ai_context_policy.yaml`

- 三级访问：tier_public(AI可读) / tier_internal(仅Owner+Meta-SLO) / tier_forensic(仅取证审计)
- `filter_for_ai_context(blueprint_text)`: 正则移除敏感阈值
  - Kill Switch 90% → "[阈值信息已移除]"
  - 72h离线 → "[阈值信息已移除]"
- 设计中不应让AI知道所有阈值

### 3.9 #63: TaskHeartbeatMonitor (M-45)

文件：`D:\ZephyrAlpha\src\zephyr\shared\task_heartbeat.py`

- HEARTBEAT_TIMEOUT=600s, MAX_CONSECUTIVE_MISSES=3
- `_cleanup_crash_zombies()`: 系统启动时清理上次崩溃遗留
- `check_all()`: 30min无心跳→标记zombie+回滚半写入文件
- `heartbeat(task_id)`: AI Agent每次tool_call后调用

### 3.10 #64: OwnerTrustGauge (M-46)

文件：`D:\ZephyrAlpha\src\zephyr\shared\owner_trust_gauge.py`

- 三指标：alert_response_time / manual_override_rate / alert_dismissal_rate
- dismissal_rate>30%→CRITICALLY_LOW / response_time>30min→COMPLACENT
- `weekly_gauge()`: 输出信任水平+建议

### 3.11 #65: 月度成本透明度报告

系统启动时打印：
```
🛡️ ZephyrAlpha 容量保障系统 — 月度成本预估
├── 治理回路评估: ¥4.30
├── 模型探测: ¥0.03
├── 蓝图审计: ¥0.30
├── 数字孪生: ¥0.50~¥5.00
├── 总月度成本: ¥5~¥10
└── 预期ROI: 防止 ≥1 次需要 3h+ 恢复的系统事故
```

### 3.12 #66: Windows WER 禁用

部署脚本中：`Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting" -Name "Disabled" -Value 1`

### 3.13 #67: 启动顺序强制执行

`graceful_shutdown.py` 的 import 必须在 Kill Switch 就绪**之前**完成——启动顺序强制执行。

## 4. M-42~M-46

| 模块ID | 模块名称 | 职责 | 归属 |
|--------|---------|------|------|
| M-42 | heartbeat_server.py | 独立轻量 HTTP 心跳服务——供外部看门狗调用 | 独立进程 |
| M-43 | blueprint_code_auditor.py | 蓝图-代码一致性取证——检测实现漂移 | weekly cron |
| M-44 | model_capacity_probe.py | 每日金丝雀任务——检测 AI 模型静默升级 | daily cron 07:00 |
| M-45 | task_heartbeat.py | 任务心跳 + 僵尸清理——发现被遗弃的 AI 任务 | 每 10min cron |
| M-46 | owner_trust_gauge.py | Owner 信任水平——检测人为判断漂移 | weekly report |

## 5. 取证专家最终判词

```
★ 终局判词 ★
设计完备度: 98/100 (理论覆盖99/100, 方案质量97/100, 外部取证95/100, 实现验证0/100)
实现完备度: ~3/100
对标水平: World-Class
唯一缺失: 真实 1500 模块运行 30 天的压力数据
下一步: 不是"更多审计"，而是"开始施工"
```

## 6. 验收标准

1. 8 个新增模块文件创建完成
2. External Watchdog 15min无响应正确告警
3. BlueprintCodeAuditor 检测到蓝图-代码数值不一致
4. ModelCapacityProbe 金丝雀任务检测到每日漂移
5. CombinatorialGate N≥3变更全组合模拟
6. Kill Switch 应急池先释放再激活
7. DualChannelAlert 主通道失败→本地持久化
8. BlueprintAccessFilter 成功移除敏感阈值
9. TaskHeartbeat 30min无心跳→僵尸标记
10. OwnerTrustGauge 正确计算信任水平
11. 月度成本报告在启动时正确输出