---
created: 2026-10-08
chief: st-tail3-20261008
ttl: task_bound
completes_when: 三裁定全部落账（A 裁定号+B 去重计数+C 重启取证）且循环检查连续两轮零问题、红蓝每车道≥3 用例全过、清理释放完毕，经 Owner 查收后归档
---

# tail3 三项已裁遗留·总包 orchestration（st-tail3-20261008）

> **Owner 授权**：母单 st-tail3-20261008 对话令——三项已裁遗留总包执行，本班零再裁权（遇删除/退役类才呈报），全程不问不中断至全部完成。
> **输入**：三车道 Owner 已批裁定原文（见各车道簿）。
> **基线**：开工 HEAD `1c92315190`（2026-10-08 01:4x）。
> **作战环境**：今夜 st-acure-20261008-chief（审计闭合，持 ruling_registry claim）/st-govfix-g 系列/st-fflow-a/b/c1/c2/c3/st-datasop-20260930 等多会话在飞——锁纪律+队列提交+不碰他会话 staged 为硬纪律。

## 一、作战范围（三项小手术，不扩面）

| 车道 | session | 任务 | 裁定 |
|---|---|---|---|
| A 案册 | st-t3a-casebook | CASEBOOK 006/007/008 空号作废+注记机制+红蓝 | ④ |
| B 去重 | st-t3b-dedup | tasks.yaml cohort_ledger_daily 双条目+business_data_categories 100+ 重复收敛+防重测试+红蓝 | ⑥ |
| C 运维 | st-t3c-ops | 调度器 10-05 停跑诊断+低峰重启取证+16:05 复核判读+09-30 补跑/呈报 | ③① |

**不干什么**：宪法 §5 Owner 门位类（flag 出厂翻转/实盘资金/生产流转/注册表净删——B 车道去重为 Owner 已批立项不在其列）；C 车道 QMT 不自行拉起不自启（仍败=出呈报件）。

## 二、执行序（线内先挖后干、线间并行；挖干判据=六向台账+自审闸三态）

1. **W0 底座**：本簿+三车道簿骨架——总包直办。
2. **W1 挖矿**：三车道并发挖矿，作业簿落各自子目录（1 主簿+2-4 子簿封矿，禁过度展开）。
3. **W2 并行施工**：A/B/C 依挖矿结论施工；A 车道 ruling_registry 被 st-acure-20261008-chief 持锁→排队后置。
4. **W3 循环检查**：受影响域 pytest+own-diff 门自洽，连续两轮 0 问题=过。
5. **W4 红蓝对抗**：每车道攻击用例≥3，测出即修。
6. **W5 收尾**：清理（.runtime/tmp 本班件/reaper keep 退订/claims 全 release）、交付报告（本目录 99_delivery/）、端到端汇报。

## 三、硬纪律（继承总包夜战范式）

1. 冷启动 PATH=Python312；`lock_files.py cleanup && process_reaper --status`；改前 claim、毕后 release。
2. 提交唯一正门 `git_commit.py --session <sid> --files …`；主区直改带 `--allow-non-worktree`；失败 `--adopt-prior-work`；忙则 `--enqueue`；commit 后 `git log -1 --name-only` 核归属。
3. 新建 .md 必带 frontmatter（created+ttl: task_bound+completes_when）；新建 .py/.yaml 先 token（register_asset.py 一站式）；目录名禁 `_\d+$` 后缀；文档内禁写旧单元测试目录路径字面量（GATE-NO-TESTS-UNIT 拆写规范）。
4. 热册（ruling/casebook/capability 册）必 safe_write_text CAS+基底⊇HEAD 纯增插入禁整片+写后进程外复核。
5. 他会话 staged/modified 不碰；他队已完成面→交叉验证加固而非重做；同文件他队在编→登记排队后置再编辑。
6. 车道无法裁→本车道簿 OPEN_QUESTIONS 登记+跳过；删除/退役类=登记留呈 Owner；三处尝试仍堵→登记+跳过禁死磕。
7. 测试隔离：输出走 tmp_path，禁写 data/ 生产路径。
8. RULE-CAPABILITY-LOOKUP：各车道写第一行业务代码前 capability_lookup.find 留审计。

## 四、台账（总包维护，随工序更新）

| 时点 | 事件 | 证据 |
|---|---|---|
| 2026-10-08 01:38 | 冷启动完成：ENV 3.12.8/setup --check 过/reaper 在岗(32 白名单)/死锁清理 1 件(st-acure-r1 遗物) | 本簿 |
| 2026-10-08 01:4x | WIP 判读：ruling_registry=st-acure-20261008-chief 持 claim；business_data_categories=staged 无主(mtime<HEAD) | classify 输出 |
| 02:28→05:5x | W0 token 册五连死袋战役：q-0001 ghost_session（心跳缺）→keeper 保温；q-0002/q-0003 CREATE-GUARD（token 被盘面 stomper 蒸发）；q-0003 再死 TAKEOVER-PENDING（死会话 st-gomap-b-20261006 接管面→总包非破坏性接管：release claim+清 ghost 心跳+worktree merge/abort 留呈 Owner，台账迁 resolved）；q-0004/q-0005 快照被抢（belt 回放死袋积压旧注册表快照，盘面反复退回旧态=系统性疫情根因）；06:0x 单进程原子化（补缺+插 token+CAS 写+add+入队 <5s 窗口）→q-0006 入袋且 blob 实证携 4 token | commit_queue 死信/接管台账/blob sha |
| 03:35 | 车道A 子代理死于账户速率限制(1302)→总包亲接 | agent 通知 |
| 03:3x | 车道A 交叉验证：裁定④主面=chief 在途批（casebook 头注已引裁定#492，#490/#491 在其工作区，册尾 reserved_void 段未落）→本车道转后置协防：条件激活型防重门测试先行落地（void 段落地即自动 enforcement），红蓝 4 用例全过 | lane_a_casebook/00_workbook.md |
| 05:4x | 车道B 完工回报：tasks 276→275 正身钉死+防重测试 7 用例两轮绿+反向红证；categories 116 组完全重复经 G4 收敛交叉验证 116/116（本车道零编辑禁硬闯）；其作业簿 token 待册落地后补投 | 车道B 回报 |
| 05:5x | 车道C 报告：根因双定案（触发链断已由他队 a4b503a163/a67d6922588 修复+QMT 离线三连败日志锚）；免重启判定（任务 Enabled+Ready 健康）；取证四件+诊断报告落 ops/；袋 t3c-0001/0002 在飞 | ops/ 取证四件 |
| 16:20 | 车道C 16:05 复核分支处置=自动化 automation-c39f6c69 已布防（在线→09-30 补跑/仍败→升级呈报件） | CronList |
| （滚动） | — | — |

## 五、OPEN_QUESTIONS（总包面）

1. **[呈 Owner] CREATE-GUARD 读 HEAD 树 vs token 落地链窗口病**（车道B #5 同判）：入队预检读 HEAD 注册表，而 token 只能经落地进 HEAD——多会话并发登记场景结构性自堵，今晚 token 蒸发-重登循环 ×4 实证。建议：入队预检对「同批自带注册表」的袋读袋内版本。
2. **[呈 Owner] belt 回放死袋积压旧注册表快照=注册表时间倒流疫情**：02:58/05:0x/06:0x 多次实证盘面（乃至 HEAD 面）被 10-06/07 死袋旧快照打回。建议：注册表族袋落地前强制做 HEAD 超集校验（REGISTRY-MASS-DELETION 前移到落地闸）。
3. **[呈 Owner] st-gomap-b-20261006 worktree 处置**：dirty=7（registry 面=HEAD 超集 28 token 非陈旧投影，含潜在独有成果），merge/abort 与 worktree remove 属删除类裁量，总包零再裁权留呈（接管注记已留痕 .runtime/takeover/resolved）。
4. 车道A 裁定④主面（casebook reserved_void 注记段+裁定#492 落册）=st-acure-20261008-chief 在途批承载；若 chief 批最终不落，本班防重门测试（条件激活）已就位，主面留呈。
