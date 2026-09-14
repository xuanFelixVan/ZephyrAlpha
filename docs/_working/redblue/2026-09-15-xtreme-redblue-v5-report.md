---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（2 条，摘录）**
> - L74: | F9 own-scope 连坐 | ✅ 他会话已完成 own-scope 化（v4.5 验证过，本轮未复测重复项） |
> - L79: 现状：`.runtime/commit_queue/dead/` 956 条，按会话拆解主体为他会话产物；solo_agent 3 笔已归因（SESSION-REQUIRED/landing 异常/CAS 竞态，内容均已落地）。
>
> **⚠️ 未完成（1 条，逐条摘录）**
> - L93: > 实施状态：设计稿待 Owner 批准后施工（建议挂下批 reconciler 任务清单，非紧急）。
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 0 个，其中判废弃 0、路径漂移 0）+ commit 提及 4 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）

# 红蓝对抗 v5 复测报告——裁定#252 全链路 + gate 双格式判活 + 搭便车重放（2026-09-15）

> 执行：solo_agent（AI）。范围：v4 修复面全量复测（F1/F2/裁定#252 上游）。
> 结论：**17/17 场景全 PASS，零新增缺陷**。B 项（他会话悬空引用）定性为 depgraph PG 瞬态竞态（自愈，不修）。C 项 dead/ 退役审计机制设计见 §4。

## 0. 执行环境

- HEAD：裁定#252 链 `a287099285`（裁定+实现原子）→ `cae966007e`（终验补丁）→ `d5dbc7f61a`（v4 附录）之上（含他会话并行提交）。
- 方法：真实 `lock_files.py` CLI 子进程 + 真实 `SessionRegistry` + 真实 gate.check 全链路（非 mock 主导）；探针脚本 `.runtime/tmp/v5_*.py`（task_bound，Owner 清理）。

## 1. A 项：红蓝 v5 场景矩阵（17/17 PASS）

### A1/A2 裁定#252 全链路（7/7，`v5_a1_ruling252.py`）

| # | 场景 | 结果 |
|---|------|------|
| 1 | victim 注册会话（pid=0 心跳型） | PASS |
| 2 | 瞬时 CLI `acquire --session` 领锁 | PASS |
| 3 | 领锁进程死亡后 `check` → **LOCKED**（v4 F2 原样攻击被根治的判定点） | PASS |
| 4 | attacker `acquire` 同文件 → BLOCKED | PASS |
| 5 | 旧格式锁（无 --session）acquire | PASS |
| 6 | 旧格式锁持有进程死后 check → FREE（PID 僵尸语义保留=设计接受窗口） | PASS |
| 7 | attacker 抢到旧格式死锁（v4 F2 原路径仍存在于旧格式=裁定明确的兼容窗口） | PASS |

### A3 gate 侧双格式判活（6/6，`v5_a3_gate.py`）

| # | 场景 | 结果 |
|---|------|------|
| 1 | 会话活+绑定锁 → HELD_OVERLAP 阻断 | PASS |
| 2 | 阻断消息含持有者（归因精准） | PASS |
| 3 | 会话死（unregister）+绑定锁 → gate 放行（锁废） | PASS |
| 4 | 旧格式锁 TTL 内 → 阻断 | PASS |
| 5 | 同上（复验） | PASS |
| 6 | 旧格式锁+allow_overlap 逃生口 → 放行 | PASS |

### A4 搭便车端到端重放（4/4，`v5_a4_ride.py`）

| # | 场景 | 结果 |
|---|------|------|
| 1 | worker-a 会话绑定锁在位，worker-b 提交 → 阻断 | PASS |
| 2 | 阻断归因含 worker-a（可追责） | PASS |
| 3 | allow_overlap 逃生口 → 放行 | PASS |
| 4 | worker-a 会话死 → 锁废 → 放行（裁定#252 核心收益：瞬时进程退出/会话回收不再产生幽灵锁） | PASS |

### A5 F1 回归探针（2/2 + 主区 1 项，`v5_a5_f1.py/f1b.py`）

| # | 场景 | 结果 |
|---|------|------|
| 1 | 主区路径坏文件 → SYNTAX-VALIDATION 阻断 | PASS |
| 2 | 主区不存在+worktree 副本坏文件 → 回退解析检出（`'(' was never closed`） | PASS |
| 3 | worktree 副本好文件 → 放行 | PASS |

## 2. B 项：他会话 FRONTEND-MAP/SCHEMA 悬空引用——定性自愈，不修

昨晚全量回归 2 failed（`test_healthy_truth_source_passes` / `test_real_yaml_all_valid`，FRONTEND-MAP 报 MOD-SIG-145/147 不存在于 depgraph）。复测定性：

1. 单独重跑两测试 26/26 全绿；真实仓库 `run_checks()`=0 fails（354 功能点）。
2. depgraph PG `nodes` 表实查：MOD-SIG-145/147 存在、`has_frontend=yes`、`frontend_ref='F-PAT-WINRATE,F-PAT-EVENTS,F-PAT-EVIDENCE'` 与 frontend_map.yaml **双向闭合**。
3. 根因：他会话 `d34e5ef0dd`（策略工厂页）写 depgraph PG 的事务窗口内，全量回归的 FRONTEND-MAP 对账读到旧快照——**读侧瞬态竞态**（与 v4 已登记的 ARCH-REFERENCE 瞬态解析竞态同族，记录在案不修）。
4. 归属：非本批缺陷、非他会话代码缺陷，环境竞态自愈。无修复动作。

## 3. 与 v4 缺陷的收敛对照

| v4 缺陷 | v5 状态 |
|---------|---------|
| F1 worktree 语法门禁失效 | ✅ 修复保持（A5） |
| F2 搭便车（gate 侧） | ✅ 修复保持（A3/A4） |
| F2 上游锁僵尸自清理 | ✅ 裁定#252 全链路根治（A1/A2；旧格式锁兼容窗口=裁定接受的残余面） |
| F9 own-scope 连坐 | ✅ 他会话已完成 own-scope 化（v4.5 验证过，本轮未复测重复项） |
| 伪造标记/嫁祸 | ✅ FORGED-GW-MARKER 持续拦截（v4 实证，本轮无新攻击面） |

## 4. C 项：dead/ 队列季度退役审计机制（设计稿）

现状：`.runtime/commit_queue/dead/` 956 条，按会话拆解主体为他会话产物；solo_agent 3 笔已归因（SESSION-REQUIRED/landing 异常/CAS 竞态，内容均已落地）。

机制设计（对齐宪法 §4 规范预算与退役审计、§9.5 静态清单禁手工维护）：

1. **触发**：事件驱动（reconciler 宪法 §9.3）——季度边界事件或 dead/ 目录条目数跨越阈值（如 >1000）触发审计任务，禁 cron/Timer。
2. **输入**：dead/*.json 全量扫描（生成器产出，不手维护清单）。
3. **判定**（机械规则，逐条）：
   - `files` 清单中每个路径查 `git log -- <path>`：若存在**晚于** dead 时间戳的后续提交 → 判 `landed_elsewhere`（内容已由其他途径落地）；
   - 文件在 HEAD 不存在且无后续提交 → 判 `superseded_or_dropped`；
   - blob_sha256 在当前 HEAD 对应路径内容匹配 → 判 `content_landed`。
4. **输出**：审计报告（`docs/_working/`）+ 分类计数登记（字段化，非散文计数）；
5. **处置**：`landed_elsewhere`/`content_landed` → 死信归档（可安全物理清理，移交 Owner）；`superseded_or_dropped` → 保持 dead（历史证据）；有 requeue 价值项（≥3 条同因活跃 bug）→ 登记堵点源治理任务。
6. **预算**：净零——本机制替代手工归因流程，不新增常驻规则。

> 实施状态：设计稿待 Owner 批准后施工（建议挂下批 reconciler 任务清单，非紧急）。

## 5. 残余风险与移交

- 旧格式锁（无 --session）的 30min TTL 抢锁窗口**永久存在**（裁定#252 明确接受，逐步迁移消解）。
- `.runtime/tmp/` v5 探针（`v5_*.py`、`fix_verify_r252.py` 等）由 Owner 随 tmp 清理删除（AI 无删除权）。
- tests/xt4tmp 4 个 staged deletion 仍待他会话 tests/ 域提交顺路吸收。
