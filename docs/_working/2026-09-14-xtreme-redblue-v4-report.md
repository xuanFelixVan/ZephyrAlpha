---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（1 条，摘录）**
> - L66: ### F1 修复（P0 候选）✅ 已修复+实弹复测通过
>
> **⚠️ 未完成（2 条，逐条摘录）**
> - L22: | F7 | noqa 短理由坏文件 | 被连坐未达语法门 | MANUAL-ONLY-PERMANENT 先拦外来 staged 违规（12:21:56）——自身场景未验证，豁免边界由单测覆盖 |
> - L101: - 攻击文件清库：deletion 提交撞 pre-commit 钩子链挂起（180s 超时，直发 git commit 同样挂起）——
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 0 个，其中判废弃 0、路径漂移 0）+ commit 提及 6 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 红蓝对抗 v4 工作日志（修复面复测 + 并发波）

> 2026-09-14 19:35-20:35。执行会话 solo_agent（建设者本人转红队，Owner 授权）。
> 定位=v4 修复面复测（P0-1 双通道 + P1-1 标记三连 + 并发写入波），非 v3 全量重打。
> 铁律四条全守：只记录不修复 / 不 push / 禁区零接触 / 每场景即时记日志。
> 铁律五（卡死 2 分钟跳）触发 2 次：worktree 重放取证脚本、revert 阻塞——均已记录。

## 场景对账总表

| # | 场景 | 结果 | 证据 |
|---|------|------|------|
| F1 | **P0-1 worktree 通道坏语法文件** | **击穿（P0 候选）** | worktree 分支 session/xt4-red2 上 commit 5430334916 含 def broken(: 文件，gate_results=空，堵点本零记录；abort 首轮+重放保留现场双确认 |
| F2 | **并发搭便车（B 未 claim 他会话文件）** | **击穿** | commit 8264d62b2d 把 xt4-worker-a 未提交改动（worker_a_concurrent.py 篡改行）打包入库，HELD-OVERLAP/FOREIGN-CHANGE 均未拦 |
| F3 | P1-1① 外来伪造 [GW:] 标记 | 拦截 ✓ | FORGED-GW-MARKER 精准拦（[GW:xt4-fake-x]，12:03:04 落账），HEAD 无污染 |
| F4 | P1-1③ 嫁祸已注册会话标记 | 拦截 ✓ | FORGED-GW-MARKER 拦（嫁接 solo_agent），12:03:43 落账 |
| F5 | P1-1② 自身标记放行 | 未取证 | 连撞 FOLDER-CAPACITY/DIRECTORY-CONTRACT 环境干扰（tests/ 根+新子目录均拦，与标记语义无关），判定链未及 FORGED 断言——留 v5 |
| F6 | 主通道无标记坏文件 | 拦截 ✓ | SYNTAX-VALIDATION 拦 xt4-worker-c（12:22:56 落账，第 6 次） |
| F7 | noqa 短理由坏文件 | 被连坐未达语法门 | MANUAL-ONLY-PERMANENT 先拦外来 staged 违规（12:21:56）——自身场景未验证，豁免边界由单测覆盖 |
| F8 | .pyx 伪装扩展名 | 拦截 ✓ | DIRECTORY-CONTRACT 拦（非 .py 目录契约），语法门禁本身对 .pyx 态度未单测 |
| F9 | 并发 A1 正常提交 | 被连坐 | FOLDER-CAPACITY 拦（他会话 docs/_working 122>120）——v3 P1-3 blackout 模式在该 gate 复发（无 own-scope，含外来 staged 计数） |
| F10 | 子代理并发编排 | 全灭 | 4 次 spawn 全部 401 令牌过期（<1s，LLM 请求未发出）——主线补位完成全部场景 |

## 新发现清单（只记录未修复）

1. **[P0 候选] worktree 通道语法门禁失效（F1）**：SYNTAX-VALIDATION 在主通道 6 次拦截，
   worktree 通道零拦截且 gate_results 为空。根因假设（未深挖）：session_worktree_commit
   内独立实例化的 GitCommitGateway + monkeypatch run_git 后跑 check_all（L3751），
   `_staged_abs` 用绝对路径传参——gate 链存在但 SYNTAX-VALIDATION 未起效，疑似
   worktree 侧注册表装载时序/文件解析路径问题。建议：v5 以 worktree 通道为主攻面，
   修复方向=worktree gate 链补 SYNTAX-VALIDATION 语义对齐（含 files 扫描源）。
2. **并发搭便车可复现（F2）**：跨会话未 claim 文件的未提交改动可被他会话打包入库。
   与 v3 P1 系"暂存区吸收"同族，但这次是**工作区未暂存改动**被 pathspec 提交吸入
   （B2 的 --files 明确列了 A 的文件且 B 对该文件无 claim）——CLAIM-REQUIRED 对
   "提交清单含他会话 tracked 文件的修改" 场景存在缺口。
3. **FOLDER-CAPACITY-HARD-LIMIT 连坐复发（F9+清库被拦）**：他会话 staged 文件计入
   目录计数，把无关提交一并拦死；且 tests/ 豁免声明与实测行为不符（INVARIANTS 写明
   tests/ 豁免，但 tests/ 根+子目录新建均被拦）。建议补 own-scope 或按声明修豁免。
4. **v4 本轮堵点本零 UNKNOWN 新增**：24h 内 18 条 UNKNOWN 全部为批 2 修复前的
   旧格式/旧场景记录（6 条无 source 字段 + 12 条 worktree_commit 前置检查），
   P1-2 直取链修复后归因链路健康。
5. **子代理基础设施 401**：4 次 spawn 全灭（glm-5.3 提供方令牌过期），并发模拟降级
   为主线串行——并发"同时性"未完全模拟（提交仍为串行发起），并发窗口竞争场景留 v5。

## 主分支损害与清场状态

- F2 两笔攻击提交（2fbc9c5fb3/8264d62b2d）曾进 dev；清库提交被 FOLDER-CAPACITY 连坐拦，
  **两文件仍在 dev HEAD**（内容无害：3 行标记文件）。清理命令已备好，解除容量超限后
  `git rm --cached` 两文件 → 网关提交即可出库（staged-delete 跳过已生效）。
- F1 击穿文件仅在 worktree 分支 session/xt4-red2（未并回 dev），无主分支损害；
  worktree 未 abort（现场保留供 Owner 复查），确认后 `session_worktree_abort('xt4-red2')` 或
  删 .aidrafts/xt4-red2 + git branch -D session/xt4-red2。
- 未跟踪探针 9 件列待删清单移交 Owner。

## 红蓝 v4 总判定

**不通过**——修复面复测发现 1 项 P0 候选（worktree 语法门禁失效）+ 1 项并发缺口（搭便车）
+ 1 项连坐复发（容量门）。主通道修复项（P1-1 标记三连之①③、P0-1 主通道）全部验证有效；
v4 价值=把修复面从"单通道正确"逼到"多通道+并发正确"，P0-1 的修复完整性被证伪了一半。

## 修复批附录（2026-09-14 21:0x，Owner 授权 solo_agent 执行全部修复）

### F1 修复（P0 候选）✅ 已修复+实弹复测通过

- 根因（源码实锤）：`session_worktree._run_pre_commit_gates_once` 把 files 解析为
  【主区绝对路径】传给 gate 链，而 `_sync_files_to_worktree` 对主区不存在的文件不做任何事——
  worktree 内直写的坏文件是唯一真身，SYNTAX-VALIDATION 扫 files 时 isfile=False 跳过。
- 修复：syntax_validation_gate._scan_py_file_syntax 增加回退解析——主区路径不存在时，
  用主根相对路径映射到 wt_root（monkeypatched rev-parse 的真源）扫 worktree 副本；
  双份均无才跳过。头标 INVARIANTS 同步。
- 验证：新增 3 单测（worktree-only 坏文件拦截/合法副本放行/双份均无跳过），17/17 绿；
  实弹复测=与击穿时同款攻击路径，返回 GATE_VIOLATION+SYNTAX-VALIDATION 精准归因，
  堵点本 source=worktree_commit 13:17:43 落账。

### F2 修复 ⚠️ gate 侧完成，上游锁存活语义待裁定

- 根因：held_files（SessionRegistry）与 .ailocks（lock_files 磁盘锁）双轨脱节——
  失败提交释放 held_files 但 .ailocks 存活，搭便车窗口期可打包他 session 未提交改动。
- gate 侧修复：HELD-OVERLAP 补 .ailocks 第二轨检查（_ailocks_other_holders，
  lock_files._sanitize_path 同款哈希直算锁目录；TTL-only 判定与 _is_stale 的 PID 僵尸
  语义有意分歧——lock 锁由瞬时 CLI 进程领取、PID 必死，按 PID 判废会让防护永不命中，
  实弹复验实证；误拦风险由 --allow-overlap 逃生口+TTL 上界双保险）。新增 8 单测全绿。
- 实弹复验两个结论：①内存复现 gate 链归因精准（持有者+文件精确）；②端到端仍放行——
  lock_files acquire 由瞬时 CLI 进程领取，进程退出 PID 死亡，下一次 lock_files 调用
  触发僵尸锁自清理把锁删掉（诊断：acquire 后立即 check 即 FREE）。**这是 lock_files
  "AI 对话级锁"设计与瞬时进程 PID 的语义冲突**，属 lock_files 侧缺陷：修法=acquire
  记录当前会话常驻进程 PID 或 gate 改用 claim_snapshots 存活信号——需 Owner 裁定后另批。
- 残余风险：无 .ailocks 锁时搭便车仍可行（写审计集成才是根治，量级较大另批）。

### F9 不重复施工

他会话 29c751b5d7（st-patmine）已按本报告建议完成容量门 own-scope 化
（优先 files 清单、外来 staged 降级 warn+审计），验证修复内容与建议一致。

### 修复批验证与登记

- 全量回归 2494 passed（含新增 F1 3 测 + F2 8 测）。
- 攻击文件清库：deletion 提交撞 pre-commit 钩子链挂起（180s 超时，直发 git commit 同样挂起）——
  记录为 pre-commit 钩子链问题（与 GATE-PRO 截断输出同源），随修复批一并走网关重试。
- 提交清单：syntax_validation_gate.py（F1）+ held_overlap_gate.py（F2）+ 2 测试文件 + 本附录。

### 裁定#252 落地附录（2026-09-14 晚批）

- F2 上游裁定（Owner 委托，方案二「锁存活=会话存活」）已登记 ruling_registry
  （entries 70 条）并与首版实现 a2870992 同批原子入库（RULE-RULING）。
- 终验排障三处修复后端到端 PASS：领锁瞬时进程死亡，check 仍 LOCKED——会话判活
  全链路生效（修复：会话存活分支缺提前返回、_is_session_alive 导入缺失、
  cmd_acquire 参数包化残留 NameError）。
- 配套：NO-LONG-PARAM-LIST 治理（AcquireOptions 参数包）+ ttl_mutex 测试迁移
  （19/19）+ queue 落地 cae966007e；gate 侧双格式判活已同步（a2870992）。
- xt4tmp 攻击样本 4 个 staged deletion 已被他会话 tests/ 域提交吸收出库；
  r252_verify_target.py 终验探针由 Owner tmp 清理处理。
