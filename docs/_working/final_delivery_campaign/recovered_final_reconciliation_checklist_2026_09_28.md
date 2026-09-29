---
ttl: task_bound
title: "ZephyrAlpha 全流通战役·终局对账与剩余施工清单（捞回件，原名《ZephyrAlpha全流通战役_终局对账与施工清单_2026-09-28.md》）"
session: st-finaldel-c266-20260930
---

# ZephyrAlpha 全流通战役·终局对账与剩余施工清单

> 生成：2026-09-28（基于 Qoder 会话导出日志 166,385 行全量消化 + 仓库盘面实测复核 + 业界/开源联网调研）
> 结论性质：已落地的全部经 `git log`/`git ls-files`/队列四态**实测复核**，未采信任何交接书口头声称。

> **[捞回注记 2026-09-30 | C266 车道 st-finaldel-c266-20260930]** 原件 2026-09-28 生成于桌面任务目录（st-finaldel 桌面审计战役产物）；2026-09-29 Owner 令删源文档时由会话 st-legacy-audit-20260929 备份至 `.runtime/tmp/st-legacy-audit-20260929/source_backup/桌面任务/`（原名《ZephyrAlpha全流通战役_终局对账与施工清单_2026-09-28.md》）。C266 八面全量搜索在该备份位命中并捞回：本副本=原件字节级拷贝+ttl frontmatter（TTL-METADATA gate 要求）+本注记，仓内路径循 TRAE-028 改 ASCII snake_case。原件 sha256=fb75474f2a913457c864b0ed2894d1f76039d0fb3a4b27488197e9901c8d3026。final_delivery_campaign/99_owner_gate.md 门位#5（"源文件三处皆无，需 Owner 重供或授权重建"）就此关闭——原件已寻获恢复，无需重建。

---

## 0. 一页结论

1. **战役九大交付面已闭合七个**：G/L/P/V 四线、Q 袋、12 份补挖案卷、战役文档树（145 件+四层接线清单）、chart 孤儿救援、autofix 三缺陷、治理工具袋（取号器+三面对账表）、落地链治本五连（roster heal/TEST-SOURCE/head_reader×2/语义分叉裁定）、F62 合规解锁——全部有 commit 哈希实证。
2. **四个业务代码袋死在黎明前**：T 袋（交易接线 15 件）、K 袋（风控熔断 6 件）、E8/E9 袋（组合装配+实盘归因 24 件）、F56 双袋+1A.5 袋——文件字节全部完好（主区暂存区+袋 blob 双备份），死因全是基建类（门禁误判/基底冲突/保护路径），且**堵它们的四个治本 commit 已全部落地**，现在只剩"修面+重投"的机械活。
3. **红蓝对抗未达标**（用户打断后停于 V1/V3，八向量完成 2 个），两轮连零未达成。
4. **M1 六向普查判定"未封矿"**：132 环节六向全绿仅 33/132（25%）；"全流通"名义下最大欠账是 F123-F132 十环的"装饰/半接线"治理。
5. **W-140 实证 12 合规闸真执法 0/12**（已有 5ddaf667aa 装两把）——这是实盘前的最后一块硬骨头。
6. 待裁定项经合并去重约 **60 项**，本文件全部给出裁定（§4）；最终施工清单见 §5（P0 今晚可干/避开 CH 停机与三个独占文件）。

---

## 1. 原始指令全景（Qoder 会话两条交接令的合并任务树）

**第一交接令（chief6→chief7）六任务**：
1. 三袋落地（T 候选池+反馈环+九态桥 / K 熔断接线 / Q 入队预检）——Q ✅ 已落 833284fe1e；T/K ❌ 死袋待重投
2. 战役树入袋（134 文件+wiring_gap）——✅ 已落（145 件 tracked+wiring_gap 在 HEAD）
3. 红蓝对抗两轮连续零——❌ 未达成（V1/V3 完成即被打断）
4. S4 工厂包（F21/F22/F16）——❌ 车道两次 150 轮截断，产物在 worktree 未落袋
5. 清临时件+91_progress §终局+终报——❌ 未做
6. 二期按 00_workorders §四推进（F56 断腿最高优先）——部分：F56 sim 腿已接（袋死），real 腿+沙箱窗未动

**第二交接令（chief4→chief5→chief7）优先序 11 项**：E8/E9 收口❌ / 1A.3+5.2 治理工具✅（bfdd84a440）/ 1A.5 死库处置🔶（袋死 PROTECTED-PATHS）/ 1B.1.2 双条🔶 / F30+F32-F35 知识 P1❌ / 波2.1 六图役 30 件🔶（六图已代投待追认=补-16）/ 波3/4/6 剩余包❌ / 波7 终验❌ / 波8 红蓝❌ / 波8 清洁❌ / 终报❌。

---

## 2. 已完成施工复查（全部实测核verify）

### 2.1 Qoder 会话期间落地（有哈希）
| 交付 | 哈希 | 复核 |
|---|---|---|
| chart_condition_package 孤儿救援（B 世系 40 绿，cross 红 7=判据牙）| 8158610ea6+3b4b1f86a1 | ✅ 在 HEAD |
| wire 四态定性入 Owner 台账 | d75e732e97 | ✅ |
| F123-F132 十卷+token 纯插入 | 06301500a5+351cafc51f | ✅ |
| Q 袋真增量（+484/−0，旁路封口红绿双证）| 833284fe1e | ✅ |
| autofix 三假绿治本（CI 入口/SSoT 路径/ConfigCheck 读腿）| 5d62909cb6 | ✅ |
| TEST-SOURCE 两侧同源（止"同袋新码+新测必死"）| 2754cc9e6f | ✅ |
| head_reader 半接线补齐 + 语义分叉裁定（F56 死因治本）| 94326c3bd9+a4211e4b16 | ✅ |
| roster heal（103→104 名册对账）| a0c2bc241b+9d319aba27 | ✅ |
| 红蓝 V1/V3 测试（5 passed）+两在案发现 | tests/governance/redblue_wave73/ | ✅（V2/V4-V8 未完）|

### 2.2 导出后其他班次落地（截至 09-28）
| 交付 | 哈希 |
|---|---|
| 治理工具袋（取号器+三面对账表+翻译册）| bfdd84a440 ✅ |
| F62 合规门锁装两把（补仓腿+策略级熔断）| 5ddaf667aa ✅ |
| 战役文档树 145 件+wiring_gap 入 HEAD | 多批 ✅（git ls-files 实测）|
| 盘位终裁定 INFRA-STORE-003 落册（补-10 销账）| 5ca4ae16b6 ✅ |
| S1 宿主空间急救（D 盘 11.92→26.57 GiB，补-20 降级）| 68356622d2 等 ✅ |
| 存储治本（备份分流/先数后删闸/取件单点裁决）| 103b97dc11/5d5398e848 ✅ |
| 破产底线第五类触发源接单一熔断仲裁点 | 4a2723c725e ✅ |

### 2.3 复查发现的账实不符（已勘正）
- 交接书说"V 线未落"→实际 1c65406934 已落；00_workorders 未回填。
- 91_progress 止于 09-27 04:0x，落后于实际进度（宪章要求的 §终局四清单未写）。
- 99_skipped_for_owner.md 本体只有 #1-#20，#21-#28 散在 00_workorders/HANDOFF 未回填；三条车道（工单总表/F56/1A.5）并行追加 #21 编号撞车。
- lane_q_notes 的"两枚 stash 禁 drop"前提已消失（`git stash list` 现为空），Q 线三文件已由 833284fe1e 落地——该登记项应销账。
- rescue 车道曾报"redblue governance 测试与 dev HEAD 字节一致"，现 `git ls-files` 实测**未跟踪**（曾被 186 枚暂存删除事件波及）——需从母本 blob（f8b182c4，tmp 与 .aidrafts 双处同 sha）重新收编。

---

## 3. 剩余未完成任务（按类别）

### A. 在飞即断的六个代码袋（字节全在，只差修面+重投）
| 袋 | 内容 | 死因（实测） | 现状 | 治本条件 |
|---|---|---|---|---|
| T 袋（chief7w-0001/0003/0007 三连死）| F40 候选池持久化+盘前通电 / F41 反馈环最后一米+九态桥，15 件 | ①TEST-SOURCE（已治本 2754cc9e6f）②GATE-PRECOMMIT ruff/any-abuse | 文件 staged（M/A）| ruff format+any 具体化后重投 0007 |
| K 袋（0004/0008 两死）| F60 减仓编排进料+F61 KillSwitch 失忆窗+PostSettlement 形态探测器，6 件 | 基底冲突：dev 推进触及 start_paper_session.py | 文件 staged（M）| 同步基底+`--adopt-prior-work` 重投；先 diff 对 4a2723c725e（他线已接单一仲裁点）防回退 |
| E8/E9 袋（0005 死）| F27 sleeve 装配+再平衡调度 / F28 decision_timestamp+影子组合，22-24 件 | ALGO_FLOW 标记+ruff-format+any-abuse | shadow_portfolio.py/rebalance_check_runner.py **确认不在 HEAD**，staged A | 锚已补（driver6 实测 present）；ruff format 两测试+any 具体化；decision_timestamp 增列先取裁定号（取号器已在 HEAD，正好首用）|
| F56 双袋 | bridge_instruction_kernel 440 行+sim-only 接线（红绿证 6 red→40 passed）| cascade_stale head_reader 缺失 | **已被 a4211e4b16 语义分叉裁定治本** | 直接 requeue 0001/0002 |
| 1A.5 袋 | 死指针改指活库+空壳 fail-closed 探针（红 2→16 passed）| PROTECTED-PATHS（trae_034 规则路径）| 袋 dead | 裁定登记+[ARCH-APPROVAL] 适配器通道，或拆袋先落代码件 |
| S4 工厂包 | F21 E2 deferred 幂等 / F22 llm_error 占坑 / F16 台账重建+对账校验器 | 车道两次 150 轮截断未落袋 | 产物在 worktree（intake_ledger_recon.py 等）| 验收 pytest→三件套→窄袋入队 |

### B. 红蓝与救援欠账
1. 红蓝八向量完成 2/8：V2 断链引用/V4 INV-1 克隆/V5 冒充 verified/V6 绕过禁止边/V7 PID 复用/V8 热册整覆未交付；在案发现两真缺陷未修（真域错挂无门拦、reaper 孵化收割无身份复核）。
2. 两轮连零未达成（宪章验收判据③）。
3. t1_t2_handover 未落地（COMPLEXITY-GUARD：run_acceptance 52>15 等三函数+13 参）——字节保袋 blob。
4. redblue 两测试未跟踪——从 f8b182c4 母本收编（robust 以 dev 现内容 9ad47e4d 为准，旧稿 e6fe1b30 弃）。
5. E 组 64 件挖矿文档不在 HEAD（41×st-ailayer-final worktree、22×chief3-baseline、2×csx-m5s1）——单副本零 git 备份，蒸发风险。

### C. 封矿缺口（M1 判定"未封矿"，六向全绿 33/132）
- F123-F132 十环判读：装饰（F123/F125/F127/F128/F130）+半接线（F129 4/43、F131 三跳链、F132 两路在产）+半开（F124 warn 真执法/block 装饰、F126 读侧四腿）。
- 17 环无册内处置、12 环无卷无工单、4 死实现定性（F83/F97 尺假阳性已销、F85 windows_service 退役候选、F89-b mutation 册已修）。
- 分母活边：knowledge(15py)/infra_runtime(9py) 在 Z 外待裁（裁-6）。

### D. 合规与安全
- W-140：12 合规闸真执法 0/12（OrderManager 6 处裸构造、ReportGate 未注入即放行、CancelRateGuard 恒惰、ProgrammaticTradingGuard/RegulatoryReportGenerator 零消费者）——5ddaf667aa 已装两把，剩十把。
- W-141 残病灶：run_post_settlement_daily.ps1 假 CONSUMERS 声明；SettlementReconciler 周时钟触发违宪（§9.3）。
- F56 TRD-A10 Owner 面：沙箱 v16→v17 换版重启+env=real 拒单启用+30 交易日窗（约 2026-11-06 起）。

### E. 台账/卫生/收尾
91_progress §终局四清单+终报未写；99 台账 #21-28 未回填+编号撞车；临时件（.runtime/tmp 各车道 inbox）未清；dead 917 袋未归档（dead 系 2397 件+#7）；w0 index.lock 陈旧锁仍在；主区两处回退弹（commit_queue.py +3/−50、commit_preflight.py +42/−71 陈旧副本）须丢弃；门禁自洽面（generate_gate_registry --diff）复跑确认。

### F. 二期战役序列（00_workorders §四，全部未开工）
F56 real 腿（sim 腿已接）/ F42 体检编排 / F43 做T统一调度 / F45 S1 扫描编排+X 流消融 / F46-F47 离场执行编排 / F53 Saga 编排+九态桥 / F02 onboarding_wizard / F04 清洗四引擎接线 / F115 R1-R3 最薄一刀 / F74 触达铃铛 / F73 首位参赛者+league_judge / F75 FSM 词表对齐 / F92 ROOR 册页回填 / F30 登记一行案 / F05-F06 空壳表前置。
另波9 红队回流 W-152..W-162 共 13 行（HMAC 立项/场景⑦补跑/四向对账表/负结果台账/孤儿件治理/st-metaq-gc 引用改道/13 条代裁追认/册标注/六册口径互斥）。

---

## 4. 待裁定清单与裁定结果

> 裁定方法（依 Owner 令）：第一性原理+长远期战略+100%AI 开发现实+业界实践（SR 11-7 模型风险管理/ESMA RTS 6 算法交易风控/A 股程序化交易新规 2024-10-08·2025-07-07 实施）+量化社区（LEAN paper=同构部署目标、vn.py 仿真必经层、Qlib RD-Agent"AI 研究全自动+实盘人守门"边界）+开源对照（nautilus_trader 回测实盘同码/启动对账、MLflow 晋升 alias/challenger、Great Expectations 数据契约、Dagster 事件驱动+幂等兜底）+AI 开发治理实证（METR RCT 自报不可信、Anthropic reward hacking 实证、防假绿=测试写权限隔离+断言 diff 复审+held-out 复跑）+事件驱动 vs cron 业界共识（事件主+幂等 cron 兜底混合）。
> 凡宪法 §5 门位项（资金/实盘/净删/flag），裁定形式="执行方案定版+启动键归 Owner"，这是宪法内的正确形态。

### 4.1 提交链与治理基建（99 #5-#17）
| # | 事项 | 裁定 | 依据 |
|---|---|---|---|
| 5 | heartbeat 计划任务兜底 | **批** | watchdog 兜底=可靠性基建业界标配；30 分钟空闲自退+计划任务重拉双层 |
| 6 | 门禁 diff 化+恒绿贵门处置窗 | **批** | 门禁瘦身已实证 71s→38s（−46%）；恒绿门=纯成本零信号 |
| 7 | dead 2397 件归档净删 | **批（归档式）**：git bundle+G 盘归档后净删，blob 引用保留 | 字节可回取=可逆；盘面卫生是 100%AI 开发的上下文预算刚需 |
| 8 | M2 候选 A 见证层出厂 flag | **批：模拟盘域出厂；实盘域等 F62 全链接线后二次批** | 见证层=防假绿基础设施，与业界 held-out 复跑同构；分级出厂控制爆炸半径 |
| 9 | requires-sync"宁停勿吃" | **维持** | 正确性>可用性，量化系统铁律（nautilus crash-only 同哲学）|
| 10 | --base-head 契约二选一 | **定 base_blobs 方案**（代码已按此准备，flag 不启用）| 证据链完整性优先；与 #ARCH-310 判官/证据同源原则一致 |
| 11 | [GW:] 归属去文本化 | **维持现状不改** | 伪造防护实战拦过假标记（POST-COMMIT-GUARD reset 实例）；改动收益<风险 |
| 12 | gate_registry 174≠180 归位 | **批** | 纯机生账目修正 |
| 13 | single-writer 提为 reconciler | **批** | 检测→修复闭环符合宪法 §9.3 事件触发 reconciler 定义 |
| 14 | commit_queue_interactive 出厂翻转 | **批翻转**：队列=正门、直连=显式例外；保留一键回退 flag+30 天审计窗 | 落地链治本三连（94326c3bd9/2754cc9e6f/a4211e4b16）已消除队列误杀主因；业界 merge queue 默认队列制 |
| 15 | 预检原则改册净零声明 | **批** | 净零形式合规 |
| 16 | 热册三向合并策略变更 | **批** | 整册覆盖式拉锯是注册表事故六层根因之一；三向合并=git 正统 |
| 17 | M5 三件 | 43 红样排期日班；四停用=转永退登记；三悬空=补指针 | 逐件定性优于批量挂起 |

### 4.2 数据面（99 #1-#4、#19、#20、#25）
| # | 事项 | 裁定 | 依据 |
|---|---|---|---|
| 1 | hfq 周月线补 lineage_version | **批**（93 册实测扩为族内 11 张一并补）| 元数据完善零风险；与菜单⑤合并执行 |
| 2 | 空壳表 9 张 | **l2_tick 保留建腿**（P2 已证 271 任务零 ERROR+护栏落地）；**其余 8 张退役** | w5_1 零触发零消费→退役；l2_tick 有真实消费者 |
| 3 | 真源收敛三处 | **收敛到唯一真源**（同真源可派生必并）| SSOT 铁律 |
| 4 | Ollama 11434 恢复 | **批恢复** | L1"统计快+LLM 慢"双路径的依赖；本地推理=100%AI 开发的成本底线 |
| 19 | etf_benchmark stub 重写 | **批**，实弹验证排明日白名单窗（今晚 CH 停机）| 数据面非资金面；假绿 stub=事故级（rows=[]→SUCCESS）|
| 20 | realtime_snapshot 换源 | **腾讯源先试**（东财封禁冷却中、qmt_bridge 依赖 Owner GUI 登录）；suspend 双源反爬归哨兵持续观察 | 多源冗余是反爬现实下的标准解；先试社区常用源 |
| 25/F51 | 币圈空壳去留 | **退役** | 业务边界=A 股；零触发零消费（w5_1）|

### 4.3 治理工具与边界（99 #21-#28）
| # | 事项 | 裁定 |
|---|---|---|
| 21 | F34 DDL --apply+首跑 | **批**：裁定登记后执行（架构数据走 apply_*_ddl 正门）；首跑=灌水验证属模拟面 |
| 22 | F88 usercustomize 运行时网 | **永久禁用**（仓内安全子集已做）| usercustomize=供应链投毒面，业界（pip/conda 生态）默认视为攻击面 |
| 23 | F76 schtasks 写操作+N/A 清理 | **批**（计划任务注册=自动化运维常态；探测器已防坏形态）|
| 24 | F68 T1 判卷三阻断 | **按裁定#413（GPU 方案①两轮制）解锁判据口径**，维持 prereg 冻结 | 上位裁定已存在 |
| 26 | F111 宪法入口三方冲突 | **AGENTS.md=唯一宪法入口**，另两处降级为指针 | SSOT；入口唯一性是宪法权威的根 |
| 27 | F119 双引擎真源 | **automation_master_plan.md 单点化**，10-08 继任点前完成合并 | 二真源互称唯一=必漂移 |
| 28 | F120/F121/F122 | F120 收编调度域；**F121 维持挂起**（四包不同质，强收编=假统一）；F122 改名消歧 |

### 4.4 全流通战役沿途门位
| 事项 | 裁定 |
|---|---|
| F56 TRD-A10 沙箱换版+env=real+30 交易日窗 | **换版重启批**（模拟面）；**env=real 拒单启用绑 F62 十闸接线完成后**；验收窗起点=换版日（对齐 RTS 6"受控部署"）|
| 1A.5 五/六个 0 字节死库删除 | **批删**：先 G 盘归档 7 天再删；指针已改指活库 governance.db（205MB/46 表）|
| ADR/KB DIM-3 空洞 | **ADR 补数据**（架构决策记录是 100%AI 开发的关键治理资产，SR 11-7 文档要求同构）；KB 空壳并入图书馆 |
| FMS-HYGIENE 棘轮 git 口径盲区 | 登记已知盲区，B10-P2 修（不紧急）|
| paper_outpost 阈值 0.6/0.001 | **先跑 2 周模拟收集实测分布再回填**（业界=预登记阈值，但无数据时阈值是猜的；MLflow 晋升门同哲学）|
| 前哨挂 SIM_DAILY 日链 | **批**（前哨=早期探测，挂日链=最小接线）|
| tick_data 空表口径 | **退役归档**（BdpanTickWatch 已删、缺口 14-15M 行/日已补齐，使命完成）|
| vendor/Kronos/examples 30 假孤儿 | **登记扫描 exclude**（vendored 代码不改动件是业界惯例）|
| ANY-ABUSE 7 处行级豁免季度审计 | **批季度审计**（同构 SOC2 季度 access review），挂季检清单 |
| ALGO_FLOW 四件 external 出仓 | **批**（capability 册锁已随 FMS 收尾释放，现可执行）|
| ai_secret_exposure/tombstone_ttl_proposer 零消费者 | **CLI 豁免登记保留**（运维工具 CLI 型零消费者正常；tombstone_ttl_proposer 是 B10-P1 退役自动化的组件）|
| W-156 假 CONSUMERS 声明 | **改锚**（1 行；假声明=事故级文档矛盾）|
| W-141 ⚑-1② 双入口分叉 | **撤销**（判伪证据充分：单任务单 Exec+注册器逐字段一致）|
| O-6 跨车道 164 枚暂存删除净删 | **批（归档式）**：字节全在 HEAD 可回取 |
| 主区回退弹（commit_queue.py +3/−50 等）| **丢弃**（已由 82308924d7/94326c3bd9/833284fe1e 取代，留着必炸）|
| test_commit_preflight_registry_cache.py 孤儿测试 | **收编**（impl 已在 HEAD 026fd1fbea；测试与 impl 同批是硬规则）|
| W-158 13 条代裁追认 | **建议批量追认**；例外=与本清单裁定冲突者以本清单为准 |
| chart_condition 两系分叉 | 已裁 B 系落地（8158610ea6）✅ 销账 |
| t1_t2_handover | **重构落地**（拆三函数+dataclass 化过 COMPLEXITY-GUARD；门是新立的，豁免=破窗）|
| redblue_robust 两版 | 以 dev 现内容 9ad47e4d 为准，旧稿 e6fe1b30 弃 |
| E 组 64 件挖矿文档 | **救援入库**（单副本零备份=蒸发风险）|
| F127 冷储双实现 | **收敛到 F08 archiver 单写者** |
| F129 版本真源二义 | **experiment_registry 唯一真源**，model_version_registry 作派生视图（MLflow registry 模式）|
| F130 ml_serve 独立包 | **退役**（serve 层实际由 F129 承担，四实体零消费）；model_drift_monitor 双份留 269 行版删 68 行版 |
| F131 collect_news 消费/退役 | 接线优先（三跳链已证活在产）；sentiment 重复簇交 CloneGuard 判 |
| F132 Timer 合宪性 | **合宪**：health-check 型 cron≠reconciler cron，宪法 §9.3 禁的是对账器 sleep-loop（业界共识=事件主+幂等 cron 兜底）|
| SettlementReconciler 周时钟触发 | **违宪成立→改事件触发**（收盘事件），保留幂等日终兜底 sweep |
| 死信"按漂移改判死因"预检升权威 | **批**（预检同源化是队列死信治本四件方案的方向）|

### 4.5 总包菜单①-⑤+补位批（93/96 册）
| 项 | 裁定 |
|---|---|
| ① 实盘合规门接线 | **批，三级推进**：一级=模拟盘 12 闸全接线（纯代码）；二级=实盘面注入（Owner 确认沙箱换版后）；三级=30 交易日观察窗 |
| ② GPU 首轮成绩单 | **B 主 C 并**（判据=盈亏平衡成本 c* 分布五道门全量不抽样，并 DSR≥0.95+PBO）；2 格先同窗对拍 |
| ③ 备份性价比 | **批**（P95 实测派生时限+免死名单 3 天影子账——可观测性先行）|
| ④ 三开关出厂 | **只批 immutable_tree**（24h 报实测）；词表门/AI 点火再等一轮自证 |
| ⑤ 净删/补列/归档 | **批血缘列定稿+台账去重**（hfq 族 11 张）；归档类维持不删 |
| 补-1 价格笼子限价单 | **乙案：先建相位判别器**（判不出相位就拒=保守正确，纪律优先）|
| 补-2 盘后退出码拆分 | **甲：批拆**，先出 38 条 freeze_manifest 受影响清单 |
| 补-3 EV-02/04/05/06 蒸发治本 | **放行**（三连发蒸发事故=结构性风险；EV-02 要红证）|
| 补-4 t0 甲位三版本 | **甲：先出三版本 diff 表**再定（三真源违反 SSOT）|
| 补-5 L09-C01 编排器 | **甲：两版同窗对拍拿差集再呈** |
| 补-6 emoreplay 交接 | **判未批**（两班口径互斥+裁定册零命中，按推荐处方原文捞回重呈）|
| 补-7 修宪入口 | **甲：复用既有通道**（不新增入口=净零）|
| 补-8 时帽 12h | **甲：追认"仅约束调度层"**，暂不装牙齿 |
| 补-9 AI 层 245 件批文 | **甲：补可复核批文**（货已在库补票，不追认不推翻）|
| 补-10 10-05 F 盘摘除 | **销账**（已被 09-28 盘位终裁定 5ca4ae16b6 取代）|
| 补-12 flags 轮转 | **取消**（只有标签无正文）|
| 补-13 266 件月批 | **当对账例行**，退役再单列 |
| 补-14 10-18~21 删链 | **只批"标记+隔离"两段**，真删另批（纪律 #234 三段式）|
| 补-15 提交正门防伪 | **甲：warn_only 审计腿**（先观测再执法）|
| 补-16 六图代投 | **追认代投**；图门接名册另批 |
| 补-17 AGENTS.md 两处漂移 | **乙：授权按金哈希规程改**（明日执行——今晚 AGENTS.md 被存储班独占）|
| 补-18 5 张图 token 通道 | **wide-prefix 豁免批**（49 条系既存在册件）|
| 补-19 RULING-REFERENCE 无执法 | **甲：补名册行+装载回归**（有声明无执法=假绿，必须补牙）|
| 补-20 D 盘 18G/98% | **降级为持续监控**（S1 急救已回 26.57G）|
| 补-21 两条悬空册条目 | **批净删** |
| F34 干流三步（建表/首跑/下游消费）| 批（同 #21）|

---

## 5. 最终施工清单

### P0（今晚即可开工——纯代码/治理/文档，不碰 CH 数据库；避开 AGENTS.md/INFRA-STORE-003/ruling_registry 三个独占文件）

**P0-1 六袋复活落地**（最高优先，全部只差修面+重投）
1. **F56 双袋**：直接 `commit_queue.py requeue q-20260927-st-c7-f56-20260927-0001 / -0002`（死因 head_reader 已被 a4211e4b16 治本）。验收：40 passed 复跑+`git log -1 --name-only` 核归属。
2. **T 袋**：staged 面跑 ruff format→定位 gate-any-abuse（order_enums.py Any 用法具体化）→重投 0007 内容。验收：signal_ashare 2850+plan_engine+ex_sor 616 三套件。
3. **K 袋**：先 `git diff` 对 HEAD 4a2723c725e（他线已接单一熔断仲裁点）核 K 袋增量仍是超集→同步基底→`--adopt-prior-work --allow-overlap` 重投。验收：相关 10 套件 254 passed。
4. **E8/E9 袋**：ruff format 两测试件+any 具体化→`next_ruling_id.py --claim` 为 decision_timestamp 增列取裁定号（裁定文写明"INVARIANTS 15 字段→16 字段"）→重投 24 件清单（e89_files_v3.txt 在 .runtime/tmp/st-chief7-20260927/）。验收：70 tests+影子组合只读模式确认。
5. **1A.5 袋**：拆袋——代码件（migrate_data 探针+validate_cross_references+shared_quickref）先落；trae_034 三处改指活库登记裁定后同批走 [ARCH-APPROVAL] 通道。验收：红样 2 failed→16 passed 复现。
6. **S4 工厂包**：从 worktree 收尾（F21 SQL WHERE verdict!=precheck_deferred / F22 幂等跳过 llm_error / F16 intake_ledger_recon.py）→pytest→三件套→窄袋。验收：E2 预审台账 63 行复算+CH 对账（CH 复活后）。

**P0-2 救援与收编**
7. redblue 两测试从 f8b182c4 母本收编（robust 用 dev 现内容）。
8. t1_t2_handover 重构落袋（run_acceptance/build_t2_subspace/run_handover 三拆+13 参 dataclass）。
9. E 组 64 件挖矿文档从三个 worktree 收编入库（防蒸发）。
10. 主区回退弹丢弃（commit_queue.py/commit_preflight.py 陈旧副本）。

**P0-3 红蓝收尾**
11. 补 V2/V4/V5/V6/V7/V8 六向量测试；修两在案发现（GATE-DOMAIN-FK 扩"真域错挂"判据；reaper 孵化收割加 create_time/cmdline 身份复核）。
12. 六目录（tests/governance、library、signal_ashare、ex_sor、trading、gov_enforcement）逐目录 pytest 两轮一致+红蓝两轮连零（表述纪律：只说"N 件通过且已证明能红"）。

**P0-4 台账与卫生**
13. 91_progress 写 §终局四清单（已打通/已修复/已排序/Owner 门位）；99 台账回填 #21-28 并消编号撞车；stash 前提销账。
14. W-156 改锚 1 行；⚑-1② 撤销落册；本清单 §4 裁定落 ruling_registry（等独占解除，明日）。
15. gate 自洽面复跑（generate_gate_registry --diff）+commit_queue health。

### P1（明日/CH VM 复活后）
16. **合规门十闸接线**（W-140 治本）：OrderManager 6 处裸构造注入→ReportGate/CancelRateGuard 真状态源→G7/G8 零消费者两闸定位消费面或明示退役——模拟盘执法先行（菜单①一级）。
17. F34 DDL --apply+首跑+#21；六个 0 字节死库归档后删除；F51 币圈退役；F130 ml_serve 退役；空壳表 8 张退役。
18. etf_benchmark 实弹重写+#19；realtime 换源腾讯源试验+#20。
19. M1 封矿治理第一批：F125/F127/F128/F130 装饰环逐环"接线或退役"执行（接线优先序=有消费需求方者）；裁-6 分母裁定（knowledge/infra_runtime 入 Z 与否）。
20. 二期战役启动：F56 real 腿（绑 F62）→F53 Saga 编排→F04 清洗四引擎→F74 触达→F75 词表→F92/F30/F05-F06。
21. 波9 回流 W-152..W-162 十三项。
22. SettlementReconciler 改事件触发+幂等日终 sweep（违宪整改）。
23. O-6 净删+dead 2397 件归档第一批（菜单⑤同批）。

### P2（本周内，结构性补强——业界对标出来的五件）
24. **防假绿三件套**（100%AI 开发生死线，METR/Anthropic 实证支撑）：①tests/ 目录写权限与业务代码分离（AI 车道禁改断言）；②断言/期望值 diff 触发强制独立复审门（新 gate）；③代理宣告成功后自动跑 held-out 第二测试集（波7.3 红蓝集扩充）。
25. **晋升门阈值预登记**：回测→模拟→小资金实盘三级晋升的量化判据（回测-模拟收益偏差、滑点、成交率/撤单率、波动衰减）预登记进 ruling_registry，对齐 MLflow 晋升阶段+RTS 6 年度自评；paper_outpost 阈值按 2 周实测回填后纳入。
26. **独立验证通道**（SR 11-7 二线等价物）：与策略开发链路代码隔离的验证器，point-in-time 数据重算关键指标，AI 生成因子/策略双检（概念稳健性+样本外结果分析）。
27. **三层对账日报**：回测↔模拟↔实盘偏差每日自动产物（LEAN Reconciliation 章节同构），作晋升门持续证据源。
28. **季度审计机制注册**：ANY-ABUSE 7 处+noqa 豁免+CloneGuard acknowledged 白名单+flag 全量，一表季检（SOC2 access review 同构）。

### 执行纪律（全程）
- 落地一律走 `git_commit.py --session <sid> --files <窄清单>`（--enqueue；失败读死因修后重投，禁裸 requeue 已取代袋）；新 sid 先 session_worktree_start+keeper 续命。
- 改前 claim、毕后 release；热册必 safe_write_text+写后验读回；token/翻译册先行或同袋（CREATE-GUARD 认 staged，落地仿真态读 HEAD 的门先落册）。
- 今晚三不碰：AGENTS.md、INFRA-STORE-003、ruling_registry（存储班独占）；CH 数据库相关（回测重跑/数据入库/仪表盘验证）一律等 VM 复活。
- 并发 ≤3-4 路防限流 1302；重投前必对 HEAD 现值 diff 防回退他线成果（q-0021 教训）。
