---
ttl: task_bound
completes_when: >-
  长尾迁移清单（§5）全部迁入统一孵化入口或经裁定豁免；首批 5 消费方+模块+测试已落地
  （M1+M2+M3 批），后续消费方按渐进纪律随各自车道迁移。
---

# 统一进程孵化入口迁移指南（MOD-INF-PROC-INCUBATOR，治理战役 M1+M2+M3）

> 创建：2026-09-16 | 会话：st-govops-20260916 | 状态：首批 5 消费方已迁移
> 蓝图：docs/03_modules/_cross_layer/process_incubator/blueprint.md

## 1. 为什么

9-15 事故（9 孤儿 llama-server ≈12GB，commit 触顶全系统卡死）的结构性缺口：
detached 孵化无登记、无收割、无水位闸。统一孵化入口三件：

1. **孵化即登记（M1）**：每次 spawn 落盘 `.runtime/process_incubator/ledger.jsonl`
   （child_pid/parent_pid/ancestor_chain/cmd/spawned_at/expected_lifetime_s/owner）。
2. **水位门禁（M2）**：spawn 前查 commit 水位——≥85% 有界等待（30s），≥reject 线
   （引用 config/resource_optimization.yaml `pressure_thresholds.memory_emergency_percent`）
   抛 `WaterLevelRejected`。
3. **收割闭环（M3）**：process_reaper 每轮消费 ledger——超预期寿命且仍存活 → 树杀 +
   回写 reaped 戳（白名单/keep 命中永不杀，与孤儿矩阵同源 fail-safe）。

## 2. 怎么迁（一行改动）

```python
# 旧（process_pool 直孵）：
from zephyr.shared.infra.process_pool import spawn_python_hidden
proc = spawn_python_hidden(cmd, cwd=..., stdout_path=...)

# 新（统一孵化入口）：
from zephyr.shared.infra.process_incubator import get_incubator
proc = get_incubator().spawn(
    cmd, cwd=..., stdout_path=...,
    name="语义名",                 # 登记用
    expected_lifetime_s=1800.0,    # 预期寿命；超寿由 reaper 收割
    owner="你的模块名",             # 归属审计
    gate=True,                     # 重任务保持 True（默认）；轻量 watcher 可 False
)
```

## 3. 参数口径

| 场景 | expected_lifetime_s | gate | 说明 |
|------|--------------------:|------|------|
| 长驻 daemon（ollama serve/服务） | 86400 | True | 超寿=异常态，reaper 收割 |
| 常驻轻量 watcher | 86400 | False | 门禁关闭防误延时 |
| 有界 worker（reconcile 等） | ≤3600 | True | 算力任务，高压让路 |
| 一次性短命令 | ≤600 | 任意 | 默认 600 |

## 4. 首批已迁移（2026-09-16）

| 消费方 | 场景 | lifetime | gate |
|--------|------|---------:|------|
| `trading/auto_runtime_core.py`（ollama serve——9-15 事故源行） | 长驻 daemon | 86400 | True |
| `frontend/dashboard/services_registry.py`（服务孵化） | 长驻服务 | 86400 | True |
| `governance/audit/reconcile_runner.py`（reconcile worker） | 有界 worker | 1800 | True |
| `gov_enforcement/rule_bridge/write_audit_daemon.py`（守护自孵） | 常驻轻量 | 86400 | False |
| `gov_enforcement/rule_bridge/worktree_drift_watchdog.py`（守护自孵） | 常驻轻量 | 86400 | False |

## 5. 长尾迁移清单（渐进，禁一次大爆破）

- `scripts/mcp/launcher.py`（ProcessLifecycleGateway 消费方，池化语义保留可后移）
- `shared/infra/session_worktree.py`（3 处 spawn_python_hidden）
- `checker_supervisor.py`（裸 Popen 持久管道流式，需 spawn 支持管道后迁）
- 其余裸 Popen：`llm_impact_analyzer` / `semantic_similar_detector` / `isolation.py`
- 判定口径：TEST-ONLY 与门禁扫描器（bare_subprocess_gate 本体）不迁。

## 6. 测试

- `tests/shared/test_process_incubator.py`（M1+M2：登记/门禁三态/对账/fail-open）
- `tests/trading/runtime/test_process_reaper_incubation.py`（M3：超寿收割/白名单兜底/
  双端 ledger 路径契约）
