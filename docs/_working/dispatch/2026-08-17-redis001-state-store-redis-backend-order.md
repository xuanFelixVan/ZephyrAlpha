---
ttl: task_bound
---

施工会话 AI-REDIS-001。任务：state_store Redis 后端（Owner 2026-08-17 裁定派单，P0 风控接线批遗留项，与 AI-RFIX-001 零交集实证——你域=shared/state_store.py+tests/shared，禁碰 RFIX 施工面）。
worktree 已由统筹创建：D:\ZephyrAlpha\.worktrees\AI-REDIS-001（分支 ai/AI-REDIS-001/task-state-store-redis-backend，自 dev aaa570ea70 切出）。进入后 `. .\activate_env.ps1`。

背景：
- src/zephyr/shared/state_store.py（MOD-INF-016，production）——#ARCH-QUANT-002 Crash-only 状态外部化原语：JsonStateStore（命名空间 JSON 快照，pid-tmp+os.replace 原子写，读三分语义 None/dict/StateCorruptError）+ AppendOnlyDedupSet（append-only 持久化去重集，容忍 crash 末行残缺）
- 消费方（只读不碰）：zephyr.risk.implementations.default_risk_validator（KillSwitch 状态）/zephyr.risk.stop_loss/zephyr.ex_core.fill_handler（fill_id 去重）/zephyr.ex_core.position_tracker.tracker
- 文件 docstring L46-47 明示："文件后端为本批默认……Redis 后端按同一接口可后补（53 号 §7 '已有 Redis 基础设施'），消费方零改动"
- 53 号 memo §7：项目已有 Redis 基础设施（先 Grep 实证连接配置/客户端封装现状——config/.env*、src/zephyr/**/redis* 等）

范围：
1. Redis 基础设施现状实证（先查再设计）：Grep 全仓 redis 客户端/连接配置/既有封装；若无可用基础设施，评估引入 redis-py 依赖（requirements 变更须登记）
2. RedisStateStore + RedisDedupSet 实现（与 JsonStateStore/AppendOnlyDedupSet 同接口）：
   - 接口契约逐方法对齐（读三分语义/原子写语义/DedupSet.add 幂等/crash 容忍等价物——Redis SETNX/HSET/expire 语义映射）
   - 连接配置走 config（禁硬编码）；Redis 不可用时行为裁定（fail-fast 抛 StateStoreError——对齐"不可恢复错误 fail-fast"裁定，不做静默降级文件后端）
3. 消费方切换机制：后端选择走配置注入（构造参数或工厂），默认仍文件后端——Redis 后端为可选增强，消费方代码零改动实证
4. 测试：tests/shared/test_state_store.py 扩展——Redis 后端用 fakeredis 或真实 Redis（有 infra 则真实，无则 fakeredis 并登记依赖）；接口契约测试双后端同跑（参数化）；crash 恢复/幂等/损坏语义红队用例

避让：
- AI-RFIX-001 施工面 5 文件（risk/pf_alloc/ex_core/position 域）——零触碰
- AI-LVL3-001（risk/core 域）/AI-GOVA-001（governance 域）并发施工中——各自域不碰
- 消费方 4 文件只读（default_risk_validator/stop_loss/fill_handler/position_tracker）——切换走配置不改代码

验收：①新增测试 2 轮全绿+tests/shared 套件不回归 ②接口契约双后端参数化同跑实证 ③消费方零改动实证（grep 无 diff）④Step 1+Step 6（14 节版）双 PASS ⑤全走 GitCommitGateway（[GW:AI-REDIS-001]）
完工反馈六要素：commit hash/Step 1/Step 6/测试轮次/改动清单/遗留项。worktree 保留待统筹统一 merge。
