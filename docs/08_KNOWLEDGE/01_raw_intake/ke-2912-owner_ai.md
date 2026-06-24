---
module_id: KE-2812------------ai-003
status: active
title: 场景：Owner 发现治理脚本漏检 — AI 修复全流程
category: module_blueprint
---

# 场景：Owner 发现治理脚本漏检 — AI 修复全流程

场景：Owner 发现治理脚本漏检 — AI 修复全流程

```
第 1 步：任务创建
  Owner → Orc: 创建 TaskCard
    task_type = OPS
    priority = P1
    description = "run_all.py 的 D12 维度漏检 .yaml 文件编码"
  Orc 内部:
    G0 Task Entry Gate 判定 → task_id 格式 OK, priority OK → PASS
    TaskCard.status: DRAFT → TODO

  → 涉及: CT-ORC-GATE-001 (G0 门禁)

第 2 步：上下文构建
  Orc → CE: CT-ORC-CE-001
    请求构建上下文——需要 run_all.py 源码 + D12 维度规则 + TaskCard 描述
  CE 内部:
    build 阶段: 收集 run_all.py + b_docs.yaml + TaskCard 28 字段
    → CE → VMS: CT-CE-VMS-001
      查询 "治理脚本 YAML 编码检测" → 返回 3 条历史 bug 修复记录
    compress 阶段: 压缩到 4000 tokens（保留 raw_text）
    validate 阶段: CE → LSG via CT-CE-LSG-001
      LSG: input_sanitizer → 无注入 → PASS
      LSG: process_sandbox → PASS
      LSG: behavior_audit → PASS
    inject 阶段: 将 context 注入 LLM 调用

  → 涉及: CT-ORC-CE-001, CT-CE-VMS-001, CT-CE-LSG-001

第 3 步：管线路由
  任务进入 Pipeline → CT-PIPE-ORC-001
    task_type = OPS → 路由到 M2 (OPS/修复) 节点
    模型选择: Claude Sonnet 4（能力矩阵中 OPS 类型的最佳模型）

  → 涉及: CT-PIPE-ORC-001

第 4 步：AI 生成修复
  AI Agent 在 M2 节点执行:
    读取 run_all.py → 发现 D12 维度的 glob 模式未包含 *.yaml
    修改: glob 模式追加 "**/*.yaml"
    沙箱检查: G4 Sandbox Gate → sandbox_profile 匹配 OPS → PASS
    工具调用检查: G6 Security Gate → 所有 tool_call 在白名单 → PASS

  → 涉及: CT-ORC-GATE-001 (G4, G6)

第 5 步：治理脚本判定
  Script System → 执行 run_all.py
    exit code = 0（所有维度 PASS）
    → CT-SCRIPT-GATE-001: exit 0 → GATE-n PASS

  → 涉及: CT-SCRIPT-GATE-001

第 6 步：知识入库（如果本次修复产生了新知识）
  Script System 产生 Finding(severity=MEDIUM, type=BUG_FIX)
    → CT-SCRIPT-KB-001: MEDIUM Finding → KE 入库
  KB 处理:
    KE 进入 KMS 管道 → G1 Ingest → G2 Triage → G3 Evaluate
    KE.status = ACTIVE
    → CT-KB-VMS-001: KB → VMS 生成 embedding

  → 涉及: CT-SCRIPT-KB-001, CT-KB-VMS-001

第 7 步：交付前门禁
  任务进入 REVIEW 状态 → Orc 触发 G7 Delivery Gate
    G7-C00: run_all.py exit 0 → PASS
    TaskCard.status: REVIEW → COMPLETED

  → 涉及: CT-ORC-GATE-001 (G7)

第 8 步：反馈闭环
  FLE 采集本轮数据:
    → CT-TELE-FLE-001: 读取 Telemetry 的 task_throughput, gate_pass_rate
    → FLE.detect_anomaly(): 无异常（所有指标正常）
    → CT-FLE-DB-001: 写入 fle_metrics 时序表（"无异常"本身也记录）
    → CT-FLE-ORC-001: 反馈给 Orc——本次 OPS 任务正常，无需调整调度

  → 涉及: CT-TELE-FLE-001, CT-FLE-DB-001, CT-FLE-ORC-001

全流程涉及的 CT-* 合同: 11/14
  未涉及: CT-ORC-VMS-001（本次无COMPLETED任务产出需要向量化）
          CT-ORC-SCRIPT-001（本次无CRITICAL/HIGH Finding触发自动创建OPS任务卡）
          CT-ORC-DB（任务状态持久化由Orc内部处理——无需显式展示）
```

---
---
