---
task_id: TASK-OPS-0006
module_id: MOD-INF-005
title: "run_all.py 调度规范落地 — §5 接口契约 + 参数约定 + 顺序依赖链 + 超时策略"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - run-all
  - scheduling
  - dependency-chain
  - timeout
description: |
  将蓝图 §5 的调度规范全部落地为 run_all.py 的实现和验证。
  
  覆盖子节：
  - §5.1 接口契约：run_all_dimensions() + run_single_dimension() 函数签名
  - §5.2 参数约定：--dimensions / --list / --dry-run / --verbose / --warn-only / --output / --tags / --depth
  - §5.3 顺序依赖链：D1→D3→D5→D8 / D2→D4→D11→D9→D12 / D6→D7→D10（串行+并行）
  - §5.4 超时策略：文件扫描 30s/120s、内容分析 60s/240s、知识AI 120s/300s、全局硬超时 600s
  - §5.5 编码铁律：sys.stdout.reconfigure(encoding='utf-8')
  - §5.6 产出物命名规范：8 种文件名模式（C1-C5 各阶段）

acceptance_criteria:
  - "run_all.py --dry-run 输出包含依赖链拓扑排序——D1 在 D3 之前"
  - "任一脚本超时 → exit 3 阻断 + 标记该脚本为 TIMEOUT"
  - "全局硬超时 600s 后在 scan checkpoint 中记录已完成维度"
  - "产出物按 §5.6 命名规范生成——文件名包含维度/编号/日期"
  - "run_all.py 启动时验证所有脚本的编码铁律"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\run_all.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\_shared\\thresholds.yaml"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\run_all.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\validate_dependency_chain.py"

rollback_instructions: "git checkout -- scripts/governance/run_all.py"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§5.1", "§5.2", "§5.3", "§5.4", "§5.5", "§5.6"]

phase: phase_1_core
effort_estimate: L
risk_level: HIGH
depends_on_task: ["TASK-OPS-0003", "TASK-OPS-0005"]
blocks_task: ["TASK-OPS-0007"]
related_blind_spots: ["B65", "B70", "B71", "B72", "B77", "B93"]
related_risks: ["R2", "R3", "R5"]
related_contracts: []
card_type: implementation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed_review
---

# TASK-OPS-0006: run_all.py 调度规范落地 — §5 接口契约 + 参数约定 + 顺序依赖链 + 超时策略

## 1. 任务概述

蓝图 §5 定义了 run_all.py 作为脚本系统统一调度引擎的完整规范。当前 run_all.py 已实现基础调度，但需补全：依赖拓扑排序、超时机制、产出物命名规范、全局硬超时、编码铁律预检。

## 2. 施工步骤

### Step 1: 依赖拓扑排序
在 run_all.py 中实现 §5.3 的三条依赖链拓扑排序：
- 链 A: D1 → D3 → D5 → D8（串行）
- 链 B: D2 → D4 → D11 → D9 → D12（串行）
- 链 C: D6 → D7 → D10（串行）
- 三条链之间并行执行

### Step 2: 分层超时策略实现
- 每个子脚本通过 subprocess.run(timeout=N) 实现超时
- 超时脚本 exit code 3 → run_all.py 总退出 ≥ 2
- 全局硬超时 600s 后记录 checkpoint → 剩余维度标记为 SKIP+TIMEOUT

### Step 3: 编码铁律预检
run_all.py 在调度任何脚本前先检查其是否符合 §5.5 编码铁律：
```python
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
```

### Step 4: 产出物命名规范
run_all.py --output 生成的 JSONL 文件名严格遵循 §5.6 的命名模式：
- 全量扫描 → findings-full-{YYYYMMDD}.jsonl
- 单维度 → findings-{dimension}-{YYYYMMDD}.jsonl

## 3. 验收标准
- [ ] run_all.py --dry-run 显示三条并行链
- [ ] 脚本超时后 exit code = 3
- [ ] 全局超时后 checkpoint 文件存在
- [ ] --output 生成的文件名符合规范
- [ ] 三条依赖链在 --verbose 模式下可见拓扑顺序
