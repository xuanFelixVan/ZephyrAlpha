---
ttl: task_bound
working_doc_type: fig11_step_ledger
map_node: D11-S03
name_zh: 会话心跳与活性判定
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-S03
---

# D11-S03 会话心跳与活性判定

## 1. 定义
会话车道第三环节：判定会话死活。决策问题=「会话还活着吗？新鲜窗与 idle 自退双轨怎么判死？」双轨=heartbeat_daemon 每 30s 刷新 jsonl 审计（pid>0=PID liveness+TTL 3600s 双判据；pid=0=心跳 90s 新鲜窗判据）+idle 超 1800s 自退；单一活性裁决表=liveness_verdict（裁定#480 C-2 八套活性机制只读折算，P1-P6 优先级，唯一结论=state+authoritative_signal）。

## 2. 六向台账

### 2.1 输入面
- 心跳事件流：`.runtime/sessions/<sid>/heartbeat.jsonl`（每 30s 追加 {ts,pid,status}）
- 保活授权流（2026-10-11 新增正门）：`.runtime/sessions/<sid>/keepalive.jsonl`（grant/revoke 事件字面量机读禁改名，TTL 缺省 1800s/上限 7200s 硬钳制）
- 会话注册表分片：`.runtime/session_registry/<sid>.json`

### 2.2 输出面
- 单一活性裁决：liveness_verdict 返回 state+authoritative_signal（P1 接管待决>P2 回魂违规>P3 幽灵无主>P4 判死>P5 降级>P6 存活，REGISTRY-FRESH）
- 会话目录实测：`.runtime/sessions/` 56 个（2026-10-15 实查）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-S03`（wired/production）
- 活性 schema 契约：`docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md`（图引用不复制）

### 2.4 代码模块
- `src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py:8`（INVARIANTS：30s 刷新/idle 自退/失锚自退/W-29 logical 豁免/C355 队列等待豁免/keepalive 三豁免皆 opt-in；:13 ERROR_CONTRACT fatal 落盘禁无痕死亡）
- `src/zephyr/security/access_control/session_concurrency.py:181` `_ACTIVITY_IDLE_TIMEOUT_SECONDS=1800`；`:2109` `def liveness_verdict(`（图记 :1608，行锚漂移 +501，符号在位）
- 阈值面：90s 新鲜窗/900s/1800s/1860s/3600s 全复用既有常量同向边界

### 2.5 门禁约束
- 图面 gate_refs=[]；约束=MODIFY-GUARD（:13）：三证旁证判据变更须与 tests/gov/session/test_takeover_pid_false_positive.py+session_takeover_ledger.py 同批；state/authoritative_signal 字面量禁改名禁新增替换

### 2.6 自动化触发
- heartbeat_daemon 独立 detached 进程常驻（每 30s）；idle 自退/失锚自退/无授权自退全自动
- 判死自动联动：stale session 90s 自动释放 held_files（消除 allow_overlap 超阈）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | heartbeat.jsonl+keepalive.jsonl 事件面在案 |
| 输出面 | pass | liveness_verdict 单一结论面+56 会话目录实存 |
| SSOT真源 | warn | 图 note 未含 2026-10-11 保活正门（register_heartbeat_keepalive）与 W-29/C355 豁免——语义层已超前图注 |
| 代码模块 | pass | 双文件锚点实存（liveness_verdict 行锚漂移 +501） |
| 门禁约束 | pass | MODIFY-GUARD 机读锁在码 |
| 自动化触发 | pass | daemon 30s 常驻+自退全自动+落痕 |

## 4. 缺口与建议
- 【语义层回写】保活正门/接管家=false_positive 治疗（2026-10-10）两项后置演进未回写图 note，建议随下次骨架回写批并入。
- 【观测建议】56 个会话目录中含大量历史壳，建议 health 面输出「活会话/僵尸壳」双计数（liveness_verdict 已有判据，只差聚合出口）。
