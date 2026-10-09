---
ttl: task_bound
title: 夜战总 Sweep 2026-09-29 终局报告（SW17 核销车道）
session: st-nightsweep-sw17-20260929
---

# 夜战总 Sweep 2026-09-29 · 终局报告（SW17 核销车道）

> sid=st-nightsweep-sw17-20260929｜总筹=st-nightsweep-chief-20260929｜生成=2026-09-29 10:2x
> 口径=袋终态实测（commit_queue 三态目录逐袋 JSON+git 判存），非台账转抄；与台账不符处已披露。
> 总账三数：**落地 25 袋（23 实内容哈希+2 noop）／在队 10+1（pending+processing）／死账 34 封记录→去重 11 项现存死账（各有处方）**。总交付袋 70。

## §终局四清单

### ①已打通/已落地（关键项+哈希，git 判存核实）

- **SW1 字节抢救**：107 件 fullconnect 挖矿文档 6 袋全落（a4acbb89/f9cb1cfd/b004c5da/d5acce8f/6402c0d0/0eabbbf8+尾批 0eabbbf8 含 14 lane index）；死信归档 743 封（零删除，禁投 26 封隔离）；blob 归档 7050 块孤儿（manifest 留痕）；C38 雷双副本甄别净变化零。
- **SW5/SW7 骨架与改名**：00_skeleton_nightsweep.md 132 环节一行不缺（已通 64/开口 57/等 Owner 11）随 R5 改名落新路径 docs/_working/night_sweep/（d094852ffa，原袋 sw1-0013+sw4-0001 合并重投核销）；night_sweep_20260929 旧路径全仓内容面清零。
- **SW2 宪法与 AI 层**：W-29 心跳 logical 会话修复 48aa677f；E09 washer 消费修复+ALGO_FLOW 出仓 233adc3c；E13 tombstone 接线 e040583b（均经 SW12 重投袋落地）。
- **SW3/SW8 提交链暗雷（代投直投系）**：S1 验收 4f088caae8（6000 verdict/100 台双口径零漂移，7.1x）；T14 五件 76fd3f1788（统一册 182→183 台，own_scope 114→168）；包5 工厂化 ErrorCodeRuntimeError 基类 130548cdb1。
- **SW4 考试链**：T1 三阻断修复 2/3+发车命令 bug 修复随 d094852ffa 落地（哨兵 5/6 判据绿；T2 按预注册 fail-closed 正确未发车）。
- **SW5 全流通业务链**：DDL#21 三步验证决策+EC3 复测六项+台账对账 2060958a；M1 封矿 F125/127/128/130 794f1656（SW12 重投）；F62 违宪整改事件腿 35ca1d69。
- **SW6 FMS 图书馆**：trae_032 六处死册指针 eb2df8bf；退役 A 路 c2ec2ff8；library_hygiene created 轴治本 14dc95cb（processing 孤儿被队列自愈回收=机制自愈实证）；FMS 判据连零棘轮 984c1787f8；FRONT-DOOR 9abbe6f1bc；B10-P2 9a2c6402d4；S5 簿附录 06dc31b719。
- **SW9 二期序列**：F92 序1 ROOR entry_count 0→422 3cb98bb6（PG 实查 422，挖矿基线 76 过期治正）。
- **SW10/SW14 CNS 与图形**：SW10 主袋 11 件（CNS-08/09 回填 7+32 条、IC 取证件、G-A.3 胞物化函数集+18 测、CHART-INVARIANT 红证钉）经 SW14 代维 requeue 在队（sw10-0002，位次 1）；SW14 CNS-14 机账 schema v3 实测 143 条（active 27/zero 115，CHIPS 5 条诚实重判 zero）+auction_book IC 实弹（IC=-0.0219 不显著如实，FCT-INTRADAY-031 维持 candidate）在队（sw14-0002..0005）。
- **SW11 治理杂项**：N-3 files_trigger 收窄 5 门净回收 13,783 触发面 1042b6d9；miniQMT 文案 2bd67c05+备份三小件 2ad4f15d（worktree 分支→SW12 merge train 在队）；W-56 悬空裁定号=零确凿悬空。
- **SW12 merge train 与残留收敛**：恒红测试防假绿判据相对化 2ee8ec84；死袋重投 5 袋全落（233adc3c/e040583b/98ce6370/794f1656/35ca1d69）；20 封现存死袋全处置留痕（销账 6/重投 11/后置 2/属主修 1，其中重投 5 袋已落地验证）；僵尸扫描 3923 文件零复现。
- **SW13 六图收口**：红蓝对抗 18/18 设计达成——但主袋终态见 §死账 I（台账记 DONE-LANED 与袋终态不符，本次纠正）。
- **SW15 门禁定性**：15→22 台"声明在册无人装载"治本（三源合并墓碑覆盖优先，统一册 15 台 active→deprecated+redirect_to，红证 15 违例复放）81d85b9a；W-134 CLI 腿 noop@e21ebc0；W-135 密钥门触发面改型在队（sw15-0003 processing）。
- **他队协同交叉验证**：W-173 prereg 声明通道 48829e4a8f6（#ARCH-366 载体）；zc9 系 trae_034 1cf01067f5 等——避让图零触碰达成。

### ②已修复（质量与基建）

恒红测试 worktree 绑定断言（2ee8ec84，防假绿判据跨环境可移植）｜washer C6 消费键读真源（233adc3c）｜tombstone_ttl_proposer 零消费接线（e040583b）｜commit_gates 六簇撞号（98ce6370，含 79 同病簇，134 测绿）｜SettlementReconciler 违宪事件腿（35ca1d69）｜SessionRegistry logical 会话+心跳豁免（48aa677f）｜t1_t2_handover --subspace-json 传参必崩（随 d094852ffa）｜aidrafts ch_probe _REPO_ROOT 深度病（SW4 卡内修）｜ops_guard sh_rm_recurse 别名分支失守（SW15 W-134）｜BARE-SUBPROCESS/NO-BARE-GETENV/NO-SECRET-HARDCODE 三门死触发面（SW15 W-135，在队）｜indicator_usage_audit 扫描根错位+文档计客双病根（SW14 schema v3，在队）｜SW12 移管 tmp 残留 3 件+无主孤儿 .py 2 件入 quarantine｜SW8 三件 stale index 快照归零+algo_flow 双态归零。

### ③在队待消化（袋号+预计，10:2x 快照）

| 袋 | 件数 | 位次(ahead) | 内容/预计 |
|---|---|---|---|
| sw15-0004 | 4 | 0 | 10_d_data 行数复测注记五面（下袋即落） |
| sw10-0002 | 11 | 1 | SW10 主袋代维重放（CNS 回填+G-A.3 函数集+IC 证件） |
| sw14-0002 | 1 | 2 | CNS-14 机账薄壳（落地后需 0005 增量批回正） |
| sw12-0016 | 6 | 14 | merge train T1 miniQMT 文案（GW 行剥离终版） |
| sw12-0017 | 6 | 15 | merge train T2 备份三小件 H04/H06/H08 |
| sw14-0003 | 5 | 16 | CNS-11 auction_strength 接线+IC 证据 |
| sw14-0004 | 2 | 17 | CNS 消化度终账 cns_closeout_ledger |
| sw12-0018 | 2 | 21 | reblue 红蓝报告 2 件（PROTECTED-PATHS 拆袋干净面） |
| sw12-0019 | 3 | 21→22 | du881 3 件零漂移面（CREATE-GUARD 拆袋） |
| sw14-0005 | 1 | 25 | CNS-14 parents[4] 增量修正 |
| sw15-0003 | 1 | processing | W-135 密钥门名册 CAS（在飞） |

预计：位次 0-2 三袋当日可落；余 7 袋在 k=4 池 1.3h/项卡点下约需 9-13h，卡点解除（Owner 菜单 E4）后收敛至 ~3h。**完工未投附注**：SW2 E10 l7_prior_opener（5 件+6 测绿）与 I6:N-1 read_side 三锚（6 件，35 测绿）磁盘健在未入队——前置=注册表 token 入 HEAD/claim 窗（SW7 卡5 BLOCKED 登记在案），处方=SW2 台账 next 清单原样补投。

### 死账处置总表（34 封记录→11 项现存死账，各有处方）

| # | 死账项（袋） | 死因 | 处方 |
|---|---|---|---|
| A | P3 链互锁 9 件（sw3-0001→sw8-0002） | cascade_stale（gateway 面 dev 推进） | 真三向重放后重投（转产已完成，blob 9/9 在） |
| B | E08 FSM 测试面（sw2-0002→sw12-0007） | test 基底漂移（dev 签名精化） | 属主修：19 行 hunk 处方在死袋 blob |
| C | F26 E7 前哨残面（sw5-0004→sw12-0005） | 基底漂移 | 属主修真三向；du881 面已拆袋 sw12-0019 |
| D | CAND-GOVTEST-005 撞号（sw3-0004→sw12-0014） | 三向合并拒绝 ours 自身重复键 | 前置=registry 去重对账器消存量（Owner 菜单 E8） |
| E | W-178/W-180 ch_reader 族 7 件（sw4-0002） | CREATE-GUARD class Finding 跨模块冲突 | 属主修：SW4 域内改名手术 7 文件（真缺陷非误拦） |
| F | FMS 99 报告 §十七-廿八（sw6-0004→sw8-0001） | git-dangerous 误拦复发（selfdoc 豁免未生效） | 复核豁免标记行后重投（引文内容零改） |
| G | **created 回填三批 1746 件（sw6-0005/0010/0011，最大死账）** | 批1/3=dev 同路径推进冲突；批2=回填面文件正文含实盘密钥键名字样触发 REAL-KEY-REFERENCE-SCAN | 拆小袋+基底重同步重投；批2 键名文件先行 selfdoc/白名单（manifest 全量在 SW6 tmp） |
| H | 六图战役收口 11 件（sw13-0001，台账误记 DONE-LANED 已纠正） | ROOR 基底冲突（dev 推进触同册） | 内容全在袋 blob（config 两图+词表+对抗测试+规格卡），重拍基底重投即落 |
| I→H 同项 | （SW9 F53 Saga+F04 清洗 15 件，sw9-0001，台账误记 DONE-LANED 已纠正） | cascade_stale 两册（stale_by sw11-0001 已落地=死因已消） | requeue 直接复活（saga 30 测+cleaning 25 测在 blob+worktree 分支双保险） |
| J | 旧路径总纲快照（sw1-0012） | R5 旧路径禁 | 后置-总筹：总纲快照过期，重拍后另袋 |
| K | N2 路由守卫（sw3-0003） | ruff-format 误拦 | 后置：等 c9-igdrop-0001（在队含同文件）先落后重放守卫 hunk |

已核销死账（重投后落地）：sw2-0003→233adc3c、sw2-0004→e040583b、sw4-0003→98ce6370、sw5-0001→794f1656、sw5-0002→35ca1d69。已销账：sw1-0003（出库令决策逆转+Owner 残留=菜单①外 E7 族）、sw1-0013（d094852ffa 落新路径）、sw3-0002/sw8-0004（T14 直投 76fd3f1788 含 token）、sw4-0004（chief7 系接管，避让不核）。禁投清单（st-ec2-p0 系/q-0021/GPU/chief7）全程零触碰。

### ④Owner 门位菜单

**总菜单=docs/_working/night_sweep/99_owner_gate_menu.md（本轮同批落盘）：六组 55+ 条目，canonical 75 条×14 台账×99_skipped #1-45 去重汇编。**
top5：①#410 续期 10-08 到期（E1，授权链断倒计时）②10-05 F 盘摘除窗（E2，716G 回收 6 天窗）③宪法两行 A37 落 HEAD（D1，PROTECTED-PATHS 机械拒=ARCH-362（死信清偿勘误：议题册查无此号，引用号存疑不改本文主张；登记缺口转门位工单） 需 Owner 正式批文）④D 盘 23.1G 恶化减压授权（E3）⑤T2 解锁三联=survival_floor/T1 定稿/⚑-2 口径（C1-C3）。

## §卫生终态

- **项目根零临时文件达成**：27 个非目录件全部为合法配置/文档（.env 系/pyproject/AGENTS.md 等），零 tmp/零 bak/零残留。
- **.runtime/tmp 我方车道目录 9 处**（24h TTL 自清，列出备查）：st-nightsweep-20260929（总筹+SW17 台账+msgs/sw15/sw14 补丁件）、-sw1（watchboard/dead_scan/c38_evidence）、-sw3、-sw6、-sw7、-sw8、-sw11、-sw12（含 quarantine/）、-sw16。
- **scratch worktree**：sw12 已清（.worktrees/.aidrafts 双查无痕）✓；存留 5 处均为内容载体非垃圾——.worktrees/{sw7,sw9,sw11}（sw9 分支=死袋 I 项复活保险）、.aidrafts/{sw13,sw15}；收尾归属=总筹裁（SW7 台账在案）。
- **quarantine 2 件**：st-nightsweep-sw12-20260929/quarantine/{backfill_registry_consumption.py, eval_tech_indicator_ic.py}（SW12-T2 移管留证禁删，owner 回归可取回）。
- **一行结论：项目根零临时件、我方 tmp 全在 TTL 自清区、scratch 余 5 处系载体待总筹裁、quarantine 2 件留证——卫生终态合格。**

## §queue 简报（10:2x 实测）

- 全队列：pending 28／processing 4／done 809／dead 422／total 1263。
- 我方（nightsweep）：25 done／10 pending／1 processing／34 dead 记录（见上表处置）。
- **k=4 落地池单工位卡点 ~1.3h/项（SW12 发现转述登记）**：实证 tailwork4-0001 1.24h、boardidx-mtr 57min、c8-watch 57min、c9-tzday 73min、sw12-0009 53min——池吞吐坍缩至 ~4 项/1.3h；drain 尝试 2 次 SKIPPED（lease 活体持有 pid 972 续约，合规不抢锁）；堵点解除靠持有者超时波次。**建议=维护班排查 GATE-PRECOMMIT-RUN 在落地面 pre-commit run 的子进程超时缺失**（已列 Owner 菜单 E4）。
- SW2 移交排雷项：并发写坏 actor（两起测试文件内容翻倍，HEAD 基底重建修复，SW12 T5 全树复扫零复现）+共享 index 陈旧 staged 面——均在 Owner 菜单 E7。

## §纪律遵守声明

本车道除两份落盘文档（token 先行+队列正门 enqueue）外零写入；禁碰队列袋达成（未 drain/requeue/withdraw 任何袋）；台账 verdict 与袋终态差异（SW13/SW9 两处）以袋终态为准如实纠正并披露。
