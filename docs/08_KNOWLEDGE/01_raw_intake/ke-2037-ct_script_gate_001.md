---
module_id: KE-1946---------003
status: active
title: 2.8 CT-SCRIPT-GATE-001：脚本系统 ↔ Gates
category: module_blueprint
ttl: permanent
---

# 2.8 CT-SCRIPT-GATE-001：脚本系统 ↔ Gates

2.8 CT-SCRIPT-GATE-001：脚本系统 ↔ Gates

```yaml
contract: CT-SCRIPT-GATE-001
title: "脚本exit code → Gate判定"
systems:
  - role: producer
    name: script_system
    path: "scripts/governance/"
    blueprint: "MOD-INF-005"
  - role: consumer
    name: gate_engine
    path: "src/zephyr/gates/"
    blueprint: "MOD-GATE_ENGINE"

mapping:
  script_exit_0: "GATE-n → PASS → 任务状态不变"
  script_exit_1: "GATE-n → PASS_WITH_WARNINGS → 任务状态 ⚠️ WARNING"
  script_exit_2: "GATE-n → FAIL → 关联任务 BLOCKED → FLE记录"
  script_exit_3: "GATE-n → CRITICAL_FAIL → 全部活跃任务 BLOCKED + Owner通知"

gate_trigger:
  - GATE-18 (pre-commit): "每次 git commit → run_all.py quick scan → exit ≤ 1 才放行"
  - G0-G7 (任务门禁): "任务执行前后 → 对应维度脚本判定"

ai_prompt: >
  你是CT-SCRIPT-GATE-001的AI agent。当脚本系统输出exit code时：
  (1) exit 0 → PASS——不阻塞任何流程；
  (2) exit 1 → PASS_WITH_WARNINGS——任务继续但标记⚠️；
  (3) exit 2 → FAIL——关联任务BLOCKED，但不要阻断全局；
  (4) exit 3 → CRITICAL_FAIL——这是门禁自身崩溃的信号：全局阻断+Owner通知，无例外；
  (5) GATE-18 pre-commit是唯一不可绕过的硬门禁——`--no-verify`应急通道必须记录Session Log；
  (6) exit code映射是单向的：不要因为"修复中"而把exit 3降级为exit 2。

telemetry:
  metrics:
    - {name: "script_gate_exit_code", type: counter, labels: [exit_code, gate_id, dimension]}
    - {name: "script_gate_pass_rate", type: gauge, labels: [gate_id]}
    - {name: "pre_commit_block_count", type: counter}
  traces:
    required_spans: ["script_execute", "gate_evaluate", "gate_respond"]
```
