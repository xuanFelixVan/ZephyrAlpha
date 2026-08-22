---
blueprint_id: MOD-AU-001
module_name: autonomy_boundary_gate
domain: D_AUTONOMY_CORE
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: H
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-AU-001 autonomy_boundary_gate 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：15号文 §3.1 / §4.1-S0.2 + 16号文 §4.2 P0-1（统一事件 schema）+ 18号清单 §4.2 + #ARCH-160；注册表真源 GOV-AI-001。
> 代码：`src/zephyr/autonomy_core/autonomy_boundary_gate.py`

## 0. 定位

运行时写操作三分类判定门：写操作（文件写入/注册表变更/配置修改）发生前查 GOV-AI-001 注册表（`docs/01_policies_and_standards/_registry/catalogs/ai_autonomy_authority_registry.yaml`）——ai_modifiable 放行（留痕）/ human_gated 拦截并升级人审工单 / immutable_core 物理拦截并告警。与既有 commit_gates 互补：commit_gates 管提交时点，本 gate 管工作区内写操作时点。治理"AI 写操作无运行时权限边界=自治无刹车"缺口。

## 1. 接口

```python
class AutonomyBoundaryGate(registry_path=None, runtime_dir=None, repo_root=None)
    .check_write_permission(action_id, target_path_or_resource,
                            session_context=None, *, trace=True) -> GateVerdict
    .close() -> None
def check_write_permission(action_id, target, session_context=None) -> GateVerdict  # 默认单例便捷入口
def get_default_gate() -> AutonomyBoundaryGate
```

判定真源仅注册表（文件头 [AI_AUTONOMY] 锚定只是投影提示）。注册表索引 mtime+size 缓存自动刷新，失败不缓存（修复后自动恢复）；路径归一化后最长前缀匹配（子路径登记优先于父路径），占位 path（"同上 子模块"等）不参与匹配。

## 2. 输出契约

- `GateVerdict`（frozen dataclass）：verdict_id/action_id/target/decision（allow/escalate/block）/layer（三分类+unregistered/registry_unavailable/internal_error 三兜底）/reason/fail_closed/matched_path/matched_module/session_id/ticket_path/timestamp；`allowed` 仅 ai_modifiable 命中的 ALLOW 为 True。
- 留痕落点（runtime_dir 默认仓根 `.runtime/`）：
  - 全部判定 → `.runtime/audit/autonomy_boundary_gate.jsonl`（追加逐行 flush，16号文统一事件 schema：schema_version/event_id/timestamp/source_domain=access_control/threat_category/severity/evidence）
  - ESCALATE → `.runtime/autonomy_gate/queue/ticket-<verdict_id>.json`（status=pending_review 人审工单）
  - BLOCK → `.runtime/autonomy_gate/alerts.jsonl`（severity=critical）

## 3. 不变量

- fail-closed：注册表不可读/目标未登记/判定内部异常 ⇒ 永不放行，默认按 human_gated 升级人审（fail_closed=True 如实标注）
- 每次判定必留痕（trace=True 默认；仅延迟实测等探针场景关闭）
- `check_write_permission()` 永不抛异常（ERROR_CONTRACT）；任何内部失败降级为 fail-closed ESCALATE

## 4. 降级行为

- 审计/告警/工单落盘 IO 失败只 WARNING 不阻断——判定仍生效（审计缺口不掩盖拦截语义）
- 热路径（缓存命中）= 一次 os.stat + 线性前缀扫描 + 一行 jsonl 追加；实测 P95=313.5µs（15号文 §2.3 P95<1ms 达标，报告 docs/_working/reports/2026-08-22-autonomy-gate-latency.md）

## 5. 边界（不做）

- 不管提交时点门禁（commit_gates 职责）；不改注册表本体（GOV-AI-001 修订走治理流程）
- MODIFY-GUARD：Owner approval required；变更须同步 15号文 §4.1 S0.2 验收口径

## 6. 测试

tests/autonomy/test_autonomy_boundary_gate.py（#ARCH-160：tests/autonomy/ 2 文件 34 用例之一）。
