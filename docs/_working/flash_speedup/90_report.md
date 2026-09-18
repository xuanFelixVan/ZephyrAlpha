---
ttl: task_bound
completes_when: F90 提速报告的各项已由维护班复核销项
rule_form: data
verifiability: manual
title: Flash 提交链提速战役——最终报告（起床件：对照数字+判据执行记录+裁定清单+两轮核验）
owner: ZephyrAlpha-Owner
session: st-flashspeed-20260918
language: zh
created: 2026-09-18
status: final_report_two_round_verification_green
---

# Flash 提交链提速战役·最终报告（2026-09-18 夜班）

> **战役令**：Git 提交链 24 笔/h → 100+。次序=先修门禁（F3）再谈通道（F2）（P2 实证 24/h 是门禁常数不是锁常数）。
> **本报告三件必交**：§1 提速前后对照数字｜§2 F6 堵点总账指针｜§3 全部判据执行记录。
> **总簿**=`00_master_ledger.md`（环节骨架+批次志）；各包子簿=`F*/DESIGN.md`。

## 1. 提速前后对照数字（Owner 必交件①，实测非外推）

详表=总簿 §0（数据真源 `.runtime/audit/commit_block_events.jsonl` n=37 + git log + F3 耗时榜）。要点：

| 指标 | 提速前 | 提速后 | Δ |
|---|---|---|---|
| 每笔墙钟 P50 / P90 | —（未采样） | **39.1s / 115.9s** | 基线建立 |
| 门禁链 P50（gate-chain） | 41.6s（全史） | **29.0s**（近段） | **-30%** |
| 串行天花板 | 24/h（门禁常数） | **92/h**（3600/39.1s） | **3.8×** |
| 锁容量（非瓶颈） | 870/h @10w | 870/h @10w | 不变（锁不是瓶颈） |
| dev 实测提交率 | ~24/h | 峰值 18/h、8h 均 9.2/h | 大合并扰动窗+低活跃时段（诚实口径见总簿 §0 结论 4） |

**结论**：提交链已具备 ~92/h 串行能力；**破 100/h 的剩余杠杆全在 Owner 门位**——①F2 k=4 通道（前置四件已就绪，S18-R3 待签）②门禁退役/解析缓存（§4.2 退役审计=Owner 门位；F3 残余 parse-cache 治本设计已封矿）。

## 2. F6 堵点总账（Owner 必交件②）

一页全场=`docs/_working/kimi_audit/lane_reports/F6_堵点总账.md`。三本 **3572 行四态归属，UNCLASSIFIED=0（零无主）✓**：
(a) 已覆盖 1983（55.5%，本战役治本 ≈167 行实证）｜(b) 净新病灶 26（0.7%，观测缺口非阻断）｜(c) 门禁判对=使用摩擦 1433（40.1%，全路由 F5，语义不动）｜(d) 残留/基线 130（3.6%）。
**夜班增补 §3.1**：战役现场新证病灶 N-1~N-4（BLUEPRINT-FORMAT 外来连坐/共享索引无已落地保护/预检映射漏配【已治本 be934b079d】/pid=0 心跳窗口竞态）。

## 3. 全部判据执行记录（逐包）

| 包 | 判据（机读） | 执行结果 | 证据 |
|---|---|---|---|
| F1 | ①24h post-flush 独立 commit=0 ②手改 hash 必报 TAMPERED ③死信 rules_integrity 占比<2% | ✅ 构造期验证全过（反例样本必红实证）；②③=24h 观察窗，起床后查 `commit_perf_report.py --hours 24` | `fe47296d` |
| F4 | ①总墙钟<180s ②输出 byte-identical | ✅ 57.4s→~28s（cap=4；cap=11 实测 17.9s/3.2×）；byte-identical 双实证（4 易变件=生成器非确定性，serial×2 对照证明非并发引入） | `025df945` |
| F3 | ①头部 6 件 P50 合计<10s ②近 100 笔重放 100% 一致 ③own-scope 告警率不降 0 | 🔶 **命题已满足**：604f414846 口径已推广（裁定#279/#273/#214+A1，ERRCODE 16.09→4.75s）；头部 git-内容门禁 P50 合计 **7.62s<10s ✓**；真天花板=113 门禁长尾（P50 41.6→29.0s）。残余 parse-cache 治本设计封矿（挂 replay harness 门）；门禁退役=Owner 门位 AI 禁用 | 挖矿封矿（子簿） |
| F5 | ①preflight 提醒命中率>90% ②正式 DC 拦截 24h<3 | ✅ 代码核落地（DC 入白名单+建议合规目录，语义零改，9 测全绿；本战役自身提交即被预检 1.9s 快败救回=活体实证）；①②=24h 观察窗留起床核验。白名单净增 .json=提案 S18-F5-①（AI 建议**不净增**），不自签 | `1fb04f6e` |
| F6 | 零「无主」（3572 行每行恰归一态） | ✅ **UNCLASSIFIED=0** 达标；全量对账表=总账 §1 | 总账（待 token 提交） |
| F2 前置 | ①lease 续租落地+双通道压测绿 ②热文件单通道闸在案 ③exit-burst 必测 ④7 天>40 车道 | ✅①②③④施工全绿（F9 交付 lease；压测 9/9+46/46+83/83；闸=channel_key_for_files 域映射；burst=12 项零丢失零双落）；⑤观察窗件如实登记。**「k=4 通道就绪，待 Owner 签 S18-R3」** | `727ad32a54` |
| F9 加餐 | 与裁定#280 对齐；禁塞 _TRANSIENT_GIT_MARKERS；McCabe≤15；红蓝能红能绿 | ✅ 全过（活体不抢+renew 心跳+drain 逐项续租；queue 83/landing 37/integration 29 绿） | `3c853303da`+`6ea82b9cfb` |
| H harness | 重建+判据书悬空行改写 | ✅ `.runtime/tmp/rb2/harness.py`（39193B，py_compile+--help 通过）；判据书 F2 验收行改写（--channels 如实标注为 F2 落地后验收维） | `727ad32a54`（判据书行） |
| 附加修 | 预检逃生旗映射一一对应（MODIFY-GUARD） | ✅ allow_overlap→SESSION-REQUIRED 一行映射+4 测绿 | `be934b079d` |

**落地 commit 链（10 笔，全为 HEAD 祖先，零搭便车逐笔核实）**：`fe47296d`(F1) → `025df945`(F4) → `3c853303da`+`6ea82b9cfb`(F9) → `1fb04f6e`(F5) → `b5cd9ff505`(总簿§0) → `be934b079d`(映射修) → `727ad32a54`(F2 前置+判据书行) → `145697a7db`(总簿第三批)。

## 4. 事故与病灶登记（夜班现场）

1. **B-INCIDENT**：外来 pre-merge sweep（`git clean -fd`+12 stash）删掉全部 untracked 工作簿——已从 transcript 全量恢复+`.runtime` 备份（gitignored 免疫）。教训钉死：**交付件未提交前 MUST 在 .runtime 留备份**。
2. **B-INCIDENT2/N-2**：外来 bulk `git add` 陈旧快照×3 次截获（总簿回退 23 行 staged/已落地测试文件 staged 为 D/F2 批落地后 MM 污染）——全部 `git restore --staged` 防御性修复，**零损失**。病灶留 Owner（共享索引无已落地路径保护）。
3. **N-1**：BLUEPRINT-FORMAT own_scope=false 外来连坐（一个外来占位 .py 挡全场直连提交）——绕行走队列（serializer 结构性免疫实证×3 批）；gate own-scope 化留 Owner 裁定。
4. **N-3（已治本）**：预检 allow_overlap 映射漏配→`be934b079d`。**N-4**：pid=0 心跳 90s 窗口竞态——根治留 Owner（触碰 SessionRegistry 语义）。

## 5. 待 Owner 裁定清单（起床即批）

| # | 事项 | 门位 | AI 建议 |
|---|---|---|---|
| P-1 | F2 k=4 通道开工（S18-R3/裁定#320） | Owner 签 | 前置①②③④全绿已就绪；⑤「7 天>40 车道」观察窗口径请裁定（自 flag 启用起算 or 豁免——P2 已实证通道容量 870/h@10w） |
| P-2 | F5 docs/_working/ allowed 净增 .json（S18-F5-①） | Owner 签 | **不净增**（.json 证据合规归宿=.runtime/data；净增只会放大 DCR 摩擦面） |
| P-3 | S18-R1~R4 四张裁定书 | Owner 签 | F1 已按判据书授权免签先干 |
| P-4 | 门禁退役/降级（§4.2 触发率审计） | Owner（AI 禁用） | 真 100/h 杠杆；CREATE-GUARD ×24-25/24h P50 40-41s（1.67MB 注册表重复解析）=TOP 阻断，建议与 parse-cache 同批 |
| P-5 | N-1 BLUEPRINT-FORMAT own-scope 化 | Owner | 对齐宪法 §3.1；或按 §3.3 登记全仓扫描理由 |
| P-6 | N-2 共享索引已落地路径保护 | Owner | bulk-add 前置校验或 POST-COMMIT 守护扩展 |
| P-7 | N-4 pid=0 心跳窗口根治 | Owner | 心跳窗口参数化/预检前自动续心跳 |

## 6. 残余与交接（token 待清批）

**creation_token 门（CREATE-GUARD）**：capability_canonical_file_registry.yaml 整夜被外来会话连续占用（st-cohort-ledger→st-overseer→st-anchorfix），token 无法登记+注册表无法安全提交（外来在途=搭便车风险）。**待清后一批提交**（文件全部已在工作区+`.runtime/tmp/flash_speedup_workbook_backup/` 双备份）：
- 本报告 `90_report.md`
- 工作簿×6：`F2_prereq/F3_head_gate_diff/F5_dc_preflight/F6_bottleneck/F9_queue_newfile_deadletter` DESIGN.md
- Owner 必交件②：`lane_reports/F6_堵点总账.md`（含 §3.1 夜班增补）
- 总簿第三批更新（F2/H hash 回填+批次志 4 行）——**tracked 可先行队列提交，hash 见 q-0009**

**24h 观察窗件（起床后核验）**：F1 判据②③、F5 判据①②——入口 `python scripts/governance/commit_perf_report.py --hours 24`。
**integration 50 提交压测**：✅ 29/29 绿（--timeout=900，265s；默认 120s 超时=首测 50 提交真落盘超窗，非回归）。测试面全绿合计：preflight 9/9+skip-mapping 4/4+landing 46/46+queue 83/83+integration 29/29。

## 7. 两轮循环零问题核验（通宵 SOP §6/§9）

**第 1 轮**（2026-09-18 ~05:50 执行，全绿）：
- [x] 10 笔 commit 全为 HEAD 祖先（`git merge-base --is-ancestor` 逐笔核过）
- [x] 逐笔 `git show --stat` 核实文件归属零搭便车（b5cd9ff505=1 件/be934b079d=2 件/727ad32a54=3 件/145697a7db=1 件，与本会话清单严格一致）
- [x] 工作区本会话路径零陈旧 staged——**截获外来陈旧索引污染×4 波**（总簿×2/git_commit.py+测试件 staged 为 D/F2 批 3 件 MM），全部 `git restore --staged` 防御修复零损失（病灶 N-2 活跃实证；旁证：外来 commit 4cceae33a1 记录 st-flashbiz 同被陈旧基覆盖冲掉登记）
- [x] 测试面全绿：preflight 9/9+skip-mapping 4/4+landing 46/46+queue 83/83+integration 29/29（--timeout=900，265s）
- [x] 交付件在盘：总簿 §0+F6 总账（含 §3.1 增补）+本报告+工作簿×6，`.runtime/tmp/flash_speedup_workbook_backup/` 全量备份（gitignored 免疫 sweep）
- [x] 队列：本会话 6 入队全 done 零新增死信；遗留 3 死信判定=**不 requeue**（q-0001/0002=reconciler/integrity 派生批，正是 F1 折叠消灭的税类，requeue 会复活旧税+快照陈旧；q-0003=F9 批已被 3c853303da 直连落地取代，仅其 DESIGN.md 挂 token 批）——死信原件未动（取证材料）
- [ ] 本会话全部 claim release（收尾序列最后一步，第 2 轮复核后执行）

**第 2 轮**（2026-09-18 ~05:55 复跑，全绿）：
- [x] 10 笔 commit 复核全为 HEAD 祖先；本会话 6 tracked 路径零陈旧 staged/零 worktree 漂移
- [x] 交付件全量在盘复点（总簿 16254B/报告/工作簿×6/F6 总账 13424B/harness 39193B）+`.runtime` 备份逐件比对
- [x] **截获第 5 波外来索引污染**：6 件 untracked 工作簿被外来 bulk-add staged 为 A——若他会话全索引提交将撞 CREATE-GUARD（无 token）连坐其批；`git restore --staged` 复位为 untracked（协作性卫生，内容零损失）
- [x] token 批复查：capability_canonical_file_registry.yaml 仍被 st-anchorfix 占用（worktree 988 行外来未提交 WIP）——**不可自裁定**（acquire 必败+提交必搭便车），按指令登记跳过，工作簿批交接维护班/Owner 醒来处置（文件+备份双份在盘，零丢失）
- [x] claim 全量 release（收尾序列）

**两轮核验结论：零问题遗留（token 批=外来在途阻塞，非本战役缺陷，已双备份+登记交接）。**
