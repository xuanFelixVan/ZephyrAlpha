---
task_id: "TASK-INF-0106"
module_id: "MOD-INF-024"
title: "Action History with Dedup — 结构化 Action 签名 + Semantic Hash + 效果去重 + 自修复螺旋检测（§2.5 + D-024-06）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: scaffold
blueprint_section: "§2.5"
estimated_tokens: 4000
estimated_time_minutes: 120
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\action_history.py"
acceptance_criteria:
  - "AC-01: ActionHistory 环形缓冲区——保留最近 50 个 action"
  - "AC-02: ActionSignature 五字段：tool_name, tool_params_hash, tool_params_semantic_hash, output_effect_hash, timestamp, cost_incurred"
  - "AC-03: tool_params_semantic_hash——文件名换但逻辑相同的参数生成同一哈希（md5 归一化后计算）"
  - "AC-04: output_effect_hash——读/写了哪些行、哪些文件的哈希（文件路径 + 行号范围 + 写入内容哈希）"
  - "AC-05: identical_action_3x → WARN + 写入 budget_enforcer_loop_events"
  - "AC-06: identical_action_5x → BLOCK——拒绝执行 + 返回 '检测到重复动作循环'"
  - "AC-07: no_effect_chain——连续 3 个 action 对输出无差异 → WARN '检测到无效果动作链'"
  - "AC-08: self_correction_spiral——同一文件同一区域被修改 > 5 次且 lint error_count 递增 → HALT '检测到自修复螺旋'"
  - "AC-09: semantic_duplicate_10x → TRIGGER_KILL_SWITCH——疑似 runaway agent"
  - "AC-10: action_ttl=300s——仅统计 5 分钟窗口内的 action"
  - "AC-11: 提供 check(action_signature) → DedupResult（含 suggested_action 和 confidence）"
  - "AC-12: 支持 action rollback——undo_last_action() 反转最近 action 的文件变更"
  - "AC-13: 所有阈值可配置（3x/5x/10x —— 来自 budget_policy.yaml 的 loop_detection 段）"
rollback_instructions: "删除 action_history.py，移除调用点对该类的 import。系统退化为无循环检测模式——依赖其他 guard（Burn Rate/Timeout Guard/Spiral EWS）作为安全网"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L370-L421 (§2.5 Action History with Dedup)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [action-history, dedup, loop-detection, self-correction-spiral, hash-based, scaffold]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0106: Action History with Dedup — 结构化动作历史 + 去重 + 自修复螺旋

## 1. 任务目标

实现基于结构化签名的 Agent Action 历史记录与去重系统。捕捉四种浪费模式：完全相同重复、语义等价重复、无效果动作链、自修复螺旋。对标 Stanford/MIT Token Economics 发现——50% 高成本运行的读写是重复的。

## 2. 背景

蓝图 §2.5（决策 D-024-06，v0.5.0 全面升级）：从 v0.3.0 简单 fingerprint matching 升级为结构化 Action History。对标 TokenFence、AgentGuard 的 action-level dedup。新增 semantic_hash、output_effect_hash、no_effect_chain、self_correction_spiral 四种检测。

## 3. 实施步骤

### Step 1: ActionSignature 类型
```python
@dataclass
class ActionSignature:
    tool_name: str
    tool_params_hash: str      # SHA256 of canonical JSON params
    tool_params_semantic_hash: str  # normalized path-independent hash
    output_effect_hash: str     # hash of (files_modified, line_ranges)
    timestamp: float
    cost_incurred: float

    @staticmethod
    def from_tool_call(tool_name: str, params: dict,
                       files_modified: dict[str, tuple[int, int]],
                       cost: float) -> "ActionSignature":
```

### Step 2: RingBuffer 实现
```python
class ActionRingBuffer:
    def __init__(self, capacity: int = 50, ttl: float = 300):
        self._buffer: deque[ActionSignature] = deque(maxlen=capacity)

    def append(self, action: ActionSignature):
        self._buffer.append(action)

    def get_recent(self, n: int, ttl: float) -> list[ActionSignature]:
        now = time.monotonic()
        recent = [a for a in self._buffer if now - a.timestamp < ttl]
        return list(recent)[-n:]
```

### Step 3: DedupChecker
```python
class DedupChecker:
    def check(self, new_action: ActionSignature,
              history: ActionRingBuffer) -> DedupResult:
        # 1. exact_match: 完全相同 action 计数
        # 2. semantic_match: semantic_hash 相同计数
        # 3. no_effect: output_effect_hash = NO_CHANGE_SENTINEL 计数
        # 4. self_correction: 同文件修改次数 + lint error 趋势
        # 返回 DedupResult(action, confidence)
```

### Step 4: SelfCorrectionSpiralDetector
- 追踪文件修改历史：{filepath: [modification_count, lint_error_trend]}
- 同一区域（行号重叠）修改 > 5 次 AND error_count 递增 → HALT

### Step 5: 集成点
- Pre-flight Gate 调用 DedupChecker 检查 new_action 是否应被 BLOCK
- Budget Enforcer 主循环每次 action 后 append 到 RingBuffer

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/action_history.py` | 新建 |
