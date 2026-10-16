---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-D01
name_zh: 死信产生（不卡队）
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-D01
---

# D11-D01 死信产生（不卡队）

## 1. 定义
死信车道第一环节（Law 4 的执行面）：落地失败的分流。决策问题=「落地失败了，这一项去哪条道？队列会不会被卡住？」三分流协议（commit_queue.py 头 INVARIANTS 实读）：普通 Exception→dead/（带 dead_reason/dead_at，不卡队后续项继续）；BaseException（KeyboardInterrupt/SystemExit/测试崩溃注入）不捕获向上传播——留 processing 等孤儿回收；LandingEnvironmentError/热册三连（HotRegistryContentionError）→退回 pending 绝不死信。

## 2. 六向台账

### 2.1 输入面
- landing 落地流水线异常（C10 五步任一步失败）
- 瞬态判别输入：_TRANSIENT_GIT_MARKERS 特征串（git index.lock 争用/Windows 句柄/LOCK_TIMEOUT）+gate 装载失败新鲜子进程判别（M5.2）

### 2.2 输出面
- 死信项：`.runtime/commit_queue/dead/`（2026-10-15 实查 378 件，含 dead_reason/dead_at 字段；图记 09-25 为 403 件——清零战役轮换后净减）
- 退回件：pending（attempts 退避计数 B5 通道）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-D01`（wired/production，deadletter_class=[item,env,other]；laws：死信不卡队）
- 图 deadletter_class 顶层：special_branches 三条（LandingEnvironmentError 退回/cascade_stale 不消耗 landing/BaseException 留 processing）

### 2.4 代码模块
- `scripts/commit_queue.py:25-29`（分流协议注释实读：landing 抛普通 Exception=单项处理失败→死信；BaseException 不捕获向上传播）+`:376` `class LandingEnvironmentError(`+`:2206` `_transient_env_failure_of`+`:2227` 环境失败统一出口（st-circ-a1-20260930 自 LandingEnvironmentError 分支提取）
- env 标记兜底：`:282-292`（LandingEnvironmentError 转正后此标记只兜历史/直连路径死信——注记实读）

### 2.5 门禁约束
- 图面 gate_refs=[]；约束=「死信也要死得明白」（purpose label 10）：每件必带 dead_reason/dead_at；「宁可留错不可删错」：dead/ 永不自动清理

### 2.6 自动化触发
- drain 逐项 try/except 自动分流；不卡队=后续项继续排空

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 五步异常源+瞬态判别实存 |
| 输出面 | pass | dead 378 件带原因字段 |
| SSOT真源 | pass | 图/laws/三分支协议一致 |
| 代码模块 | pass | 分流协议+异常类+统一出口实存 |
| 门禁约束 | pass | 死得明白+不清理不变量在案 |
| 自动化触发 | pass | 全自动分流不卡队 |

## 4. 缺口与建议
- 【收敛建议】env 标记兜底分支（历史/直连路径）在 LandingEnvironmentError 转正后已是过渡件，建议排期迁移后退役（与 C10 建议同批）。
- 【水位】dead=378 见 C13 行动项；本环节无缺陷。
