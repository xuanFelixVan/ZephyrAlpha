---
ttl: task_bound
session: st-redblue-review-20261002
date: 2026-10-02
title: 三夜战役红蓝极限对抗审查终报（分支清零+接管显化+混沌演训复测）
completes_when: A-G 七向量全实测+红队缺口全治本+两轮独立验证判定呈Owner
---

# 三夜战役红蓝极限对抗审查终报（st-redblue-review-20261002）

> 审查令：对 st-ffchief-20261001/20261002 三夜战役（分支清零+接管显化基建+混沌演训）做全面审查+多车道并发压测复测。纪律：逐项实测禁凭文档下结论；发现真缺口直接治本并复测。

## 终判定：**根治成立（有保留项，全部当日闭环）**

三夜基建的四大主张——分支清零、接管显化（台账+门+钩子）、死信清算（第16类）、混沌演训六向量——经独立复测全部成立。红队挖出 **6 个真缺口（F1-F6）+2 个观察项**，全部当日治本落地并实弹复验。两轮独立验证（战役自测轮+本轮审查轮）结论一致。

## A-G 向量实测计分（10/10 过，2 项带修复后过）

| # | 向量 | 判定 | 证据锚 |
|---|------|------|--------|
| A | 分支清零 | 过（修复后） | 复测实测 18 条（10 条 chaos 演训残留）→蓝队回收→**8 条整**（dev+serializer×5+活会话2）；归档 tag 25 个；抽 5 tag 复活 sha 全等 |
| B | 接管显化基建 | 过 | 三件全在 HEAD；10/10 测绿；--list 16 条真实 open 带处方；resolve 迁移 resolved/ 实测 |
| C | 混沌演训复测 | 过（修复后） | 10 车道全链（注册→claim→写→enqueue）；随机处死 5（2 中途+3 落地后）→**5/5 捕获带处方**（03 经死亡钩子主路径，04/06/08/10 经孤儿路径）；伪造孤儿 orphansim 捕获；resolve 放行实测 |
| D | 死信清算 | 过（修复后） | sweep 两遍幂等（aged=764/fresh=464 恒等，1228 总账吻合）；F4 修复后 absorbed **0→10 实弹**；chaos2-st-01-0002 吸收入档、06-0001 正确保留 |
| E | 治本抽验 | 过 | 5 笔近期落地（9b3359eccf/a57de1be53/95dd7f426e/9e679d586f/394636ae78）关联测试面 63+32+14 全绿 |
| F | 红蓝对抗 | 过（修复后） | 见下节 |
| G | 并发压测 | 过 | 与 C 合并执行：10 车道并发 enqueue（错峰 0.5-2.5s）+2 车道中途死亡：**零死锁、零丢失**（9 袋落 dev+1 袋 ghost 闸死信带处方），belt 纪元自愈换血（pid 22300→36228）全程无感 |

## 红队战果（F1-F6 全部蓝队当日治本）

| # | 缺口 | 严重度 | 根因 | 治本 | 实弹复验 |
|---|------|--------|------|------|----------|
| F1 | 演训车道残留：10 条 chaos 分支+worktree 未回收，"≈8 条"口径失守 | P2 卫生 | 演训收尾未含自清 | 10 worktree remove+分支删除（全 merged ahead=0 零损失）+台账 10 条 resolve 收口 | git branch=8 整 |
| F2 | `--scan` CLI 孤儿在场即崩（KeyError: 'sid'）——**9b3359eccf 招牌功能经 CLI 不可达**；连带 --list 对字符串证据崩、孤儿 worktree 缺 dirty_files 门咬不住 | P1 | `_scan_orphan_resources` 产 `session_id` 键+扁平资源+字符串证据，`_cmd_scan` 读 `d["sid"]`；单测只测 scan_dead_sessions 本体未测 CLI 端到端 | 孤儿条目同构化（sid 键/dict 证据/resources 包裹/复用 `_worktree_dirty`）+_cmd_scan 防御性双键+_cmd_list 安全渲染 | 修复后 scan rc=0，5/5 孤儿捕获带处方；回归测试钉死同构四要件 |
| F3 | **TAKEOVER-PENDING 门全平面静默失效**：单测全绿、名册 enabled、门函数直跑正确，但 enqueue 预检与锁内落地链**从不咬合**（两次实弹提交命中面完美匹配仍放行）。两层根因：①落地网关 project_root=serializer worktree，台账住主仓 .runtime/（gitignored 不入检出）→按 worktree 根读恒空；②锁内链 commit() 传**绝对路径**而门直比 as_posix 永失配（HELD-OVERLAP 同类门均有 abs→rel 归一，唯此门没有） | **P0** | ①anchor 缺失 ②路径归一缺失——T1 落地（07:26）起所有 queue landing 与直连 commit 对死会话资源面零执法 | ①`anchor_main_root` 锚主仓根（approval_resolver #ARCH-324 同款处方）②命中面归一化：相对化锚=gateway 自身 root（worktree 暂存相对 worktree=repo 布局），台账读锚主仓——两锚分工 | 修复落 HEAD 后 belt 纪元自愈换血；直接 spec.check/check_all 双仿真全咬；最终实弹咬合见 C⑥ |
| F4 | sweep-absorbed 吸收判据与落地管线行尾规范化不对齐：git add CRLF→LF 而判据逐字节哈希→CRLF 系死信**永久不可吸收** | P2 | `_head_hash` 原始字节 vs 袋内原始字节，落地被 git 规范化 | 双侧 CRLF 规范化后比对（无 blob_ref 旧袋保守回退原口径） | 实弹 absorbed 0→10（chaos2-st-01-0002 入档验证） |
| F5 | （F2 治本次生）孤儿扫描对**普通目录**跑 git status 吸入主仓全量脏面（orphansim 实测 400+ 主仓脏文件进门命中面=误咬无辜 commit） | P2 | `.aidrafts/<名>` 非 worktree 时 `git -C` 落主仓语义 | 真 worktree（.git gitdir 文件）才走 _worktree_dirty；普通目录盘自身文件（.aidrafts/ 前缀=gitignored 不误咬）+non_worktree_dir 标记 | 回归测试钉死：主仓脏文件不入孤儿命中面 |
| F6 | **capability 注册表盘面=陈旧整文件快照，缺 HEAD 32 条**（09-24 时代死会话批次压盘）→batch_creation_tokens 写前自检 fail-safe 全员拒写，**token 管线对所有新文件堵死**（即 ffchief-0020 死信 STALE_BASE 同源病根） | P1 | 陈旧快照压盘+热册 CAS 拉锯；工具自诊给出正解（增量补回/禁整片覆盖/禁强行放行） | 按 R-063/Q-7 同型处方：机械盘账（HEAD 12548 vs 盘 12550，缺 31+1 重复条目）→区段尾 safe_write CAS 增量回补 32 条→yaml 可解析自检→重跑工具落册 | TOOL_RC=0，token redblue-review-audit-review-findings-20261002 落册验证；盘独 34 条核查=token 先行合法模式（32 条 .ps1 为 staged 新文件待其属主批落地），盘/HEAD/index 三面归一，拉锯周期终结 |

### 观察项（不构成缺口，移交维护班）

1. **gate_execution_stats 审计自 10-02 07:26（T1 落地笔）后零记录**——落地链门禁在跑（HotRegistry 等实弹有拦）但统计断流，可观测性盲区。
2. 死亡钩子 reason 模板瑕疵：idle 未超阈值也打印"> 7200s"字样（chaos2-st-03 实录 idle 175.3s/898.1s 配"> 7200s"文案）；钩子对 pid=0 会话判死口径偏宽（演训幸存者与审查会话自身均被写成 open 条目——显化无害，处置时按注册表活性复核即可）。
3. gate_auto_registrar 21 条 files_trigger 超宽告警（命中 1200-9200 文件，近 always-fire）——性能与语义噪声长期债。
4. 死信 ffchief-0020（HotRegistryContention，STALE_BASE_VIOLATION）为战役遗留，属他会话在途面，本审查未代处置。

## 蓝队修复 commit 清单（全部经 GitCommitGateway 正门落地）

| commit | 内容 |
|--------|------|
| 4cd33a61a | F2 孤儿条目同构化（scan/list CLI 三崩修复）+F3 一层（anchor_main_root 锚主仓根）+回归两测 |
| 7b671a244 | F4 sweep 吸收判据行尾规范化+回归测试（absorbed 0→10 实弹） |
| （本批 q-0005） | F3 二层（命中面 abs→rel 归一化，两锚分工）+F5 孤儿普通目录禁吸主仓脏面+回归三测 |
| 438cf3a4c / 68f01fdef / eedc0f51b9 | 门咬合测试载体（缺陷复现实弹，正文为审查进度锚） |

## C⑥/R4 终态（咬合→resolve→重投闭环）

最终实弹咬合（F3 双层修复+belt 换血后）：触碰死车道脏面文件→TAKEOVER-PENDING 硬阻断+五会话处方书；--resolve 后重投落地。chaos2-st-06 ghost 袋（裁定#459 存活闸拒自动重投的死信）经人工 requeue 改挂落地=零丢失闭环。

## 学费（审查方法）

1. **"单测全绿+名册 enabled+工厂直跑正确"≠门在执法**——门禁验收必须做**全平面实弹咬合**（enqueue 预检/锁内链/落地链三平面各自至少一发）。T1 的 10 测全绿给了假信心。
2. 门读跨平面资源（主仓 .runtime/）时必须过 anchor_main_root——worktree 进程内一切"按 project_root 读主仓资源"的写法都是潜伏失效（#ARCH-324 先例第二例）。
3. 链上路径形态是**实现细节真源**：commit() 归一绝对路径是既有行为，新门对 files 的归一化必须对齐先行门（HELD-OVERLAP），不能凭 CLI 直调经验写 as_posix。
4. 孤儿/残留扫描给"目录"做 git 语义判定前，先验 `.git` gitdir 文件——普通目录的 git status 是主仓语义。
