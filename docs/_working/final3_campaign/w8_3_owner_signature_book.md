---
ttl: task_bound
title: W8-3 Owner 签字册——全仓"待 Owner 拍板"项一次性送签（128 项/10 主题，2026-09-19）
---

# W8-3 Owner 签字册（st-final3-20260919 汇编）

**签字项总数 128**（主题一 96 + 主题二~十 32）｜用法：只看末节【签字栏】，逐号批 a/b 即生效；细节回查各主题证据指针。证据等级：[亲验]=汇编会话直查（文件/PG/git 实测）；[转报]=引用在案裁定书草案/台账（未逐锚复验）；[推断]=汇编建议（Owner 可否）。

| 主题 | 项数 | 一句话 |
|---|---|---|
| 一 | 96 | kimi_audit S3 全仓待裁穷举（A/H 八族） |
| 二 | 1 | szopen 28 接口地址收集（深圳开放数据平台 Owner 操作） |
| 三 | 1 | W8-1 归档批 A14 目录+B3 件 git mv【O】 |
| 四 | 1 | W4-2 ig bak 92 表清理【O】（实测 92，非 90） |
| 五 | 1 | W4-6/W6-3 服务自启+看门狗两案选一【O】 |
| 六 | 1 | #342 B① 复裁：src/zephyr/data/ 扩面 vs MOD-L00-001 豁免 |
| 七 | 2 | W9-6③ 两裁定尾巴分支终裁（sowner002/tv2terrain） |
| 八 | 19 | deep_review 收官遗留 #ARCH-338..356 处置 |
| 九 | 4 | W4-1 传导链墓碑/判重 Owner 门位 |
| 十 | 2 | W1 收尾遗留（DCR-001 / GATE-21） |

---

## 主题一：kimi_audit S3 待裁 96 条

背景：09-17 主力会话五分区穷举全仓"待裁/需 Owner/挂单/HELD"标记，去重后净 96 条（含 12 批量合并项≈190 决策点），已比对裁定登记表（当期最大 #303）。[亲验·源表] `docs/_working/kimi_audit/s3_pending_rulings_inventory.md`（原文锚点在"锚点/来源"列，本册只摘录缩写）。
a/b 语义：a=按本册建议行通过；b=否决或行内另一选项。标【草案】者=已有 Owner 签字即生效的一页裁定书草案（`docs/_working/kimi_audit/adjudications/`，[转报]）；标【汇编】者=汇编建议（[推断]，Owner 裁前可要求补草案）。
回填现状：9 条已有草案（A-01/02/03/08、B-01~05/15、C-01/02/05、D-01、E/F 全族、G-01）；V-01/V-01b/V-02 违规发现已回填结案（清单 §9.1）；B 族红队复验=修正维持（附页三修正条款随草案）。

### A 族：资金动作·花钱闸（16）

| 编号 | 决策点（摘录） | 建议 |
|---|---|---|
| A-01 | 编排器 §八 八项打包裁（不交易判据/接入包/60% 硬顶预算带/日历降级/decision_daily/分发范围/T3 revoke/排班 stub） | 【草案】a=八项按草案过（首版接入包=空集；预算带 confirmed 标未校准；不双写；T3 自动仅限 kill_switch 联动）b=逐项另裁 |
| A-02 | 卖出族 17 处启用（四式止盈/密度止损/退出四式/阶段 6-8） | 【草案】a=整族挂起（依赖就绪自动回队）b=逐件启用 |
| A-03 | S-OWNER-002 默认翻转（全时全包→切换器管） | 【草案】a=不予放行（三重未就绪）b=放行 |
| A-04 | iFind 续费与否（不续=edb_data 永久 disabled） | 【汇编】a=续费 b=不续并接受 disabled |
| A-05 | L2 行情权限+大 QMT 沙箱开通 | 【汇编】a=开通 b=不开 |
| A-06 | 加密行情网络闸：反代/换源/代理 三选一 | 【汇编】a=三中择一放行 b=维持关 |
| A-07 | 链上付费 API（Glassnode/CryptoQuant）订阅 | 【汇编】a=不订（默认不买付费另类）b=订 |
| A-08 | 做T v2 战役：开跑/改设计/砍 | 【草案=S2】a=砍现形态（替代=单假设窄考试，前置=S5 尺子+指数分钟补全）b=全矩阵开跑 |
| A-09 | CST-T0-001 做T成本模型 candidate→production | 【汇编】a=暂缓（随 A-08 砍向联动）b=启用 |
| A-10 | GPU-04 RL 真训练+GPU-02 Kronos 消费门 B-007 审批 | 【汇编】a=暂缓（P-4 已裁不上，联动 E-03 挂起）b=批 |
| A-11 | 模拟盘计划任务 ZephyrAlpha_PaperSession 开闸 | 【汇编】a=开 b=不开 |
| A-12 | 影视票房付费层（艺恩/灯塔）是否评估 | 【汇编】a=不评估 b=评估 |
| A-13 | 另类 3/4 批：政采网/猫眼合规试点+VPN 常态在线 | 【汇编】a=批试点 b=不批 |
| A-14 | 商品现货采购+云盘存货接收 | 【汇编】a=批 b=不批 |
| A-15 | C1 lane_b/lane_c 无人值守授权（Owner 承担 token 成本） | 【汇编】a=授权 b=不授权 |
| A-16 | SLE-1 --rebalance→weight_adjust_assert 门开闸 | 【汇编】a=开 b=不开 |

### B 族：尺子·阈值·统计口径（19）

| 编号 | 决策点（摘录） | 建议 |
|---|---|---|
| B-01 | 严尺放行档=0 归因（两向都要结论） | 【草案】a=两向都成立主因尺子；采 STD-SIM-ACCESS-002，污染修复重考前归零维持 b=另判 |
| B-02 | STD-LIVE-REDLINE-001 draft→frozen | 【草案】a=暂不 frozen（先校准后冻结，义务挂 S12）b=立即 frozen |
| B-03 | N_eff 估计器冻结版追认+补登裁定号 | 【草案】a=追认+补登号（先于 002 frozen，红队修①②③随批）b=不追认 |
| B-04 | DSR 0.70 硬线出处 | 【草案】a=显式标"工程约定" b=补外部出处 |
| B-05 | 两大批（10,080/5,990）补登 N 账本 | 【草案】a=补登限研究筛选侧（不可审计不登）b=不登 |
| B-06 | EXP 复评 IS 窗三选一（缩窗/补 2022-2026 提取批/换前向窗） | 【汇编】a=授权补提取批（数据面修复后）b=缩窗或换窗 |
| B-07 | 共识聚合放宽 high-only（mid 入聚合） | 【汇编】a=暂不放宽（修复重考后再议）b=放宽 |
| B-08 | T1A-5 regime_overrides r1/r2/r11 回退基准 | 【汇编】a=认可现基准 b=另定 |
| B-09 | 考尺 P1 修后历史及格结论重判 | 【汇编】a=重判 b=不重判 |
| B-10 | R-A X-S2 执行族 5 节点方法分配 | 【汇编】a=按 triage 表通过 b=另分配 |
| B-11 | R-C TDM-X-R1-03 加仓消融剥离语义 | 【汇编】a=通过 b=另裁 |
| B-12 | R-E L0 计划族 5 节点方法学归属 | 【汇编】a=新增"计划质量"判据 b=挂 agg_discrimination |
| B-13 | B0 决赛前 15 条 backlog 开跑+L4 阈值补冻结 | 【汇编】a=批 b=不批 |
| B-14 | 流动性危机 13 项"经验阈值先行" | 【汇编】a=接受 b=逐项校准后启用 |
| B-15 | 组队方案 A 进 E7+观察档表述 | 【草案】a=采纳观察档+两前置（污染重考/S6 收口）b=直接上线 |
| B-16 | 竞价量归首 bar+open 代理口径+末态标定回补 ~600 万行立项 | 【汇编】a=三件全批 b=不批 |
| B-17 | 6 日永久 tick 缺口 1min 合成近似续回放 | 【汇编】a=接受近似 b=不留 |
| B-18 | daily_valuation 09-09~14 全 0 窗判定+10h 重刷 | 【汇编】a=弃窗不重刷 b=投重刷 |
| B-19 | crypto_top50_usdt 静态宇宙去留 | 【汇编】a=改动态 Top-50 b=留静态 |

### C 族：战役存亡·删资产·破坏性清理（18）

| 编号 | 决策点（摘录） | 建议 |
|---|---|---|
| C-01 | 清洁三件：10 空壳表 DROP/110 CAS tmp/重复 bak 二选一 | 【草案】a=批准走可逆通道（隔离 7 天再 DROP/冷存不删除）b=维持 |
| C-02 | 决赛后破坏性批（9 垃圾件/85MB forensic/integrator/20260526 bak ≈6860 万行） | 【草案】a=同 C-01 可逆通道 b=维持 |
| C-03 | auction_book_limit_bak_20260908（唯一副本）去留 | 【草案】a=不删，冷存保留（唯一副本豁免）b=删 |
| C-04 | BT-P2-055 底仓+日内回转模板立项（做T臂底座） | 【汇编】a=不立（随 A-08 砍向）b=立项 |
| C-05 | 方法论五选型 P-1~P-5 建/废 | 【草案】a=P-1/P-3/P-4 不上、P-2 三层、P-5 修订采纳 b=另裁 |
| C-06 | MOD-XS-008 RL 训练环境（按未裁 P-4 施工标 production）追认/撤件 | 【汇编】a=撤件（联动 C-05；frontmatter 与正文矛盾=V-07）b=追认 |
| C-07 | BM-INV-007 孤儿模块 439 件判法+口径收敛 | 【汇编】a=加 node_type 过滤收敛 17 件再判 b=按 439 全判 |
| C-08 | 31 件候选模块 deferred 建/废 | 【汇编】a=批量废（零触发零消费）b=逐件 |
| C-09 | 弃用流程第②步 9 件升格（PF-004/005→rejected 等） | 【汇编】a=按清单升格 b=维持 |
| C-10 | B13 nan_processor：退役 vs 保留删三策略 | 【汇编】a=保留但删 bfill/linear/mean b=整体退役 |
| C-11 | B7 semantic_audit/orchestrator 接线/退役 | 【汇编】a=退役 b=接线 |
| C-12 | B9 ashare_stop_loss_engine 保留/退役+里程碑 | 【汇编】a=定退役+接线里程碑（与 #ARCH-339 K06 同族联动）b=保留待接线 |
| C-13 | B14 gpu_consensus_scheduler 双实现（569/598 行零消费）合并 | 【汇编】a=择一保留并收编 b=双删 |
| C-14 | B10/B11 market_data 集群 salvage 升机制裁定 | 【汇编】a=升机制裁定 b=个案处理 |
| C-15 | CircuitBreaker 残余（capacity_assurance/context_pipeline_auto）收 SSoT | 【汇编】a=收编 b=维持 |
| C-16 | 一次性/遗留计划任务清理（4 测试遗留每日白烧工厂线等） | 【汇编】a=批清理 b=逐个 |
| C-17 | B5 silent-except 定点+新门禁（否决 122 处批量治理） | 【汇编】a=批准 b=否 |
| C-18 | 蓝图缺口"内容工程族 ~190 项"立 Owner 排期专项 | 【汇编】a=立项 b=不立 |

### D 族：注册表·flag·错误码门位（14）

| 编号 | 决策点（摘录） | 建议 |
|---|---|---|
| D-01 | 门位口径统一（一条规则批掉 D-02~D-06/H-03/低置信13） | 【草案】a=三档规则（净删=Owner 常设/tier0 新增改=提案登记/派生行全自动+号段自动预留）b=维持个案 |
| D-02 | 错误码 FAC/MLS/AUDITTEST 三前缀入 domain_prefixes | 【汇编】a=入 b=不入（D-01 过即连带） |
| D-03 | 预留码 ZA-PA/POS 关闭 vs 落码 | 【汇编】a=按 D-01 自动预留档 b=逐个 |
| D-04 | tool_contracts 34 契约码收编路线 | 【汇编】a=注册表新增 contract_declared 形态 b=逐个落 raise 点 |
| D-05 | 孤件 model_capability_exam__init__.yaml 删除 | 【汇编】a=删 b=留 |
| D-06 | C4 STR evidence 回填算注册表净变更？ | 【汇编】a=不算（派生行全自动档）b=算 |
| D-07 | ROOR schema 增 counting_rule 字段 | 【汇编】a=批 b=不批 |
| D-08 | unified-asset-index 唯一真源写者+扫描口径（宽 31847/B vs 窄 24415/C） | 【汇编】a=窄口径+唯一写者 b=宽口径 |
| D-09 | SYS-MASTER-001 §0.2 dispatch 两行 REMINDER 扩行 | 【汇编】a=扩 b=不扩 |
| D-10 | 三张 miniQMT 占位表/任务（从未产出）删登记 | 【汇编】a=删 b=留待替代源（与 F-06 退役向一致） |
| D-11 | D_AUTONOMY_PERM 两行 ssot_path 指向不存在目录 | 【汇编】a=退役域 b=补目录或改注册表 |
| D-12 | L6-#2 墓碑 TTL 清理判据+净删门确认 | 【汇编】a=批判据 b=另定 |
| D-13 | L4-#2 独立性 gate 立案 | 【汇编】a=准 b=不准 |
| D-14 | DS-275 生产读路径切换（consensus_daily_repaired） | 【汇编】a=切 b=不切 |

### E 族：晋升·冻结区解锁（9，全部【草案】EF-族）

| 编号 | 决策点（摘录） | 建议 |
|---|---|---|
| E-01 | 七份战役蓝图晋升 03_modules | a=批准（红队修①：combo_gate 蓝图头标注"尺子修订中"）b=缓 |
| E-02 | TableRegistry/business_data_categories 表名入册 | a=批准 b=缓 |
| E-03 | GPU-01/02 红线区+预测表 DDL+RL B-007 门 | a=挂起（等 C-05 签发）b=批 |
| E-04 | 禁写区蓝图×2 晋升 | a=批准 b=缓 |
| E-05 | .trae/documents/ 181 份承认为真源并迁册 | a=部分批准（承源迁移+蓝图架构图同步勘误）b=不认 |
| E-06 | 数据库 4 项"用户裁定"暂缓解锁 | a=不予解锁+补登裁定号 b=解锁 |
| E-07 | 三条 akshare 采集链开数据窗 | a=挂起（真源已归档=可得性未证）b=开 |
| E-08 | REG-EXP-001 整表 draft 晋升真源 | a=批准（顺带修计数）b=维持 draft |
| E-09 | 裁定#1（因子 DSL，>500 因子触发）执行/废止 | a=废止+触发达成自动复活草案 b=执行 |

### F 族：数据可得性与外推授权（12，全部【草案】EF-族）

| 编号 | 决策点（摘录） | 建议 |
|---|---|---|
| F-01 | 16 条 error 策略补考排期 | a=挂起到数据面修复后 b=即排 |
| F-02 | R-B 消融对照回放 §12 放行（13 节点只读） | a=批准 b=不放 |
| F-03 | R-D 3 条 pending 行加 superseded 机制 | a=批准 b=另议 |
| F-04 | L3 对账期初持仓快照源 A/B/C | a=选 B 案重拟 b=A/C 案 |
| F-05 | bdpan 云盘同步器 7/3 停更重启 | a=独立呈签（红队修②：查因与重启并行，断流即停）b=续挂 |
| F-06 | TradingWatchdog/RestartMiniQmt 启停 | a=退役（两处口径互斥取退役向）b=重启 |
| F-07 | TICK_SOURCE 切 xtdata 后桥降级纯后备 | a=批准 b=维持双活 |
| F-08 | QUOTE_V17 并入 TICKDUMP3 v20 | a=批准（一致性实证后退役 v17）b=维持双轨 |
| F-09 | L1 必需传感器集定义 | a=批准定义（必需=行情/指数/日历）b=另定 |
| F-10 | L4-#3 intake_exam_due 跨稿契约对齐 | a=批准 b=另议 |
| F-11 | L7 A/B 联赛 6 个月数据窗立项 | a=现在立项 b=续挂 |
| F-12 | 模拟盘 A 阶段 2026-12-14 首评维持"勿提前施工" | a=维持原令 b=提前 |

### G/H 族：方法论选型与机制澄清（8）

| 编号 | 决策点（摘录） | 建议 |
|---|---|---|
| G-01 | _system_master 〇-B 12 项"设计决策待定" | 【草案】a=11 项封挂+SQLite/锁按现实规模单独立项 b=全挂或全立 |
| G-02 | G07 判 COMBINATION_INVALID 后三件（红节点/情绪硬上限/定位器语义） | 【汇编】a=按案通过 b=另裁 |
| G-03 | belt daemon 治本路线 A（静默窗）vs B（短命子进程）#ARCH-324 | 【汇编】a=A b=B |
| G-04 | AI 资产盘点 7 开放问+Q10 依赖图快照（67% 路径失效）重生成/清理 | 【汇编】a=随草稿区清理 b=重生成 |
| G-05 | #ARCH-314 dataflowgraph 阶段分层排期 | 【汇编】a=暂不排期 b=立项 |
| H-01 | 审计链取证期间"冻结一切轮转"处置（26,909 HMAC 失配） | 【汇编】a=批临时冻结 b=不冻结 |
| H-02 | 裁定撞号 #264(WYF-3) vs #266 合法性认定（均 active） | 【汇编】a=认 #266 为准+回写引用面 b=认 #264 为准 |
| H-03 | 常设门位 vs 待裁边界：known_good_hashes PGP 签名是否真需人执行 | 【汇编】a=保持人工 PGP b=改自动+周期抽审 |

低置信 14 条（清单 §10）不入签字栏，Kimi/施工班裁前自判升格；指针同源表。

---

## 主题二：szopen 28 接口地址（1 项）

背景[亲验·原文]：`docs/_working/2026-09-15-szopen-pipeline-handoff.md`——"47 个接口已全部订阅（appKey 已入库），其中 19 个已接入管线并回补约 64 万行数据，剩余 **28 个已订阅但未接入**（卡在服务地址发现，见任务 3）"；终局侦察 §五·六："结论：剩余 **29 接口无法由 AI 单方面激活**，需要 Owner 在平台页面做两类各一次的操作"（28/29 口径差=环境气象预报计入与否，原文并存如实呈报）。
- **a**：Owner 执行两组动作——A 组 6 个接口页补订阅（toApiDetails 逐个点订阅：环境气象预报/气候资料历史/地面观测实况/空气质量日报/市场主体发展/水库水位表，链接在原文 §五·六）；B 组 23 个无 ctx 资源在接口测试控制台复制请求地址（或整页 HTML 存档）发回——之后施工班走任务 3 批量接入（统计月报 12 系列走 _SZ_STAT_SERIES）。约 10 分钟 Owner 操作。
- **b**：放弃剩余接口（保留已接入 19 通道+64 万行存量，本件归档留痕）。

## 主题三：W8-1 归档批【O】（1 项）

背景[亲验·台账]：`docs/_working/final3_campaign/w9_triage_ledger.md`（重扫 177 对象=A14/B3/C126/C-3:5/D19/E4/P6；总令基线"28 对象 A24+B4"与实测差=漂移说明②⑤：散文件 A10 无法机械恢复已并入 C，不虚标）。
**A14 目录**（→ docs/_working/archive/2026-09/，git mv 走正门+RENAME-DEPGRAPH 门禁）：alg01/、audit/、clean_exam_e2e/、dead_queue/、flash_biz/、greatwall_integration/、n5_closure/、pattern_line/、regime_recal/、reports/、resource_schedule/、sharpe2_prep/、sop_review_nodes/、wyf3/。
**B3 件**：handoff/、xt_lab3/（两件待办指针=直接 W8-1 归档批）；2026-09-18-HANDOFF-PROMPT.md（待办指针=“W8-2① 消费复核后归档”——建议随批但保留该前置）。
**C-3 例外**：总令写"3 份保留至季度末"，台账实测 **5 份**（2026-09-09-clearance-review-notes / 2026-09-12-ai-native-governance-review / 2026-09-13-xtreme-redblue-report / 2026-09-14-ch-redblue-adversarial-report / pattern_session_governance_report_2026_09_14，均标"2026-09-30 后 W8-1 归档"）——以实测 5 份为准[亲验]。
**clean_exam 前置**：总令要求"clean_exam 归档前确认编排器工单已移交"。移交证据[转报]=其结案报告 §遗留清单①："断点 E4：execution_report 生产者接线——编排器'出手'前置工单，下一班"（`docs/_working/clean_exam_e2e/2026-09-18-campaign-final-report.md`）；未找到更细承接回执，Owner 签字即视为此保留项知悉。
- **a**：批准 A14+B3（handoff/xt_lab3）批量 git mv 归档，C-3 五份留至 09-30，clean_exam 保留项知悉。**b**：整批缓办或指定剔除件。

## 主题四：W4-2 ig bak 表清理【O】（1 项）

背景：PG 图库每日备份表（`ig_*_bak_YYYYMMDD`），总令口径"约 90 张"。[亲验·只读实测] `get_depgraph_pg_connection(read_only=True)` 拉 pg_class：**92 张 / 12 族 / 合计 689,913,856 字节（≈658 MiB）**，活跃 ig_ 表 16 张不受影响。备份日期窗 2026-09-07~09-18。

| 族 | 张数 | 日期窗 | 字节 |
|---|---|---|---|
| ig_chain / ig_chunk / ig_edge / ig_node | 8+8+8+8 | 09-07..09-14 | 1.5MB+19.2MB+1.6MB+4.8MB |
| ig_company_edge / ig_company_metric | 8+8 | 09-07..09-14 | 67.4MB+218.9MB |
| ig_document / ig_fact | 8+8 | 09-07..09-14 | 15.7MB+252.0MB |
| ig_node_company | 8 | 09-07..09-14 | 28.8MB |
| ig_equity_edge / ig_unlisted_entity | 6+6 | 09-08/09..09-13/14 | 1.6MB+14.3MB |
| ig_product_revenue | 7 | 09-09..09-18 | 61.0MB |

- **a**：批准清理——保留每族最近 1 份+当日活表，其余 DROP（走 RULE-DATA-OPS 三步验证+可逆通道：先冷存再删，对齐 C-01/C-02 裁定姿势）。**b**：全部保留（盘内 <1GB，代价低但逐日续增）。

## 主题五：W4-6/W6-3 服务自启+看门狗【O】（1 项，两案选一）

背景[亲验]：W6-1/2 已落地（commit e77d0b13ba：api_server 挂 StaticFiles 一体化+壳入口切 8890）；壳=Electron（`tools/desktop/main.js`，台账实测修正"非 WebView2"）。壳内已有现成看门狗代码路径：`ensureApi()`（8890 探活复用→拉起→20s 健康等待→端口僵尸占口修复弹窗→瞬态失败重试一次）+`ensureDocs()`（8765 serve_docs --no-regen，Owner 2026-09-07 裁定"随面板自动拉起+总闸可管"）。`data/runtime/process_reaper_keep.txt` 已含 `zephyr.frontend.dashboard.api_server`（reaper 免杀白名单挂钩点在案）。
- **方案 A**：注册 2 个 Windows 计划任务（登录触发）直启 api_server+serve_docs，看门狗=reaper keep 白名单。代价：+2 常驻任务维护面（S3 C-16 正在清理同类遗留，反向教训）；与壳的 ensureApi 形成双拉起者（探活复用可吸收但竞态面+1）。
- **方案 B（建议）**：开机只自启 Electron 壳（Startup 快捷方式或 1 个计划任务），api/docs 生命周期全由壳内 ensureApi/ensureDocs 托管；reaper keep 白名单兜底防误杀（serve_docs 建议补一行 keep）。任务数净零增、复用已验证路径、故障面最小。
- **a**=方案 B；**b**=方案 A。

## 主题六：#342 B① 复裁（1 项）

背景[亲验·原文]：裁定#342（夜裁-02，`docs/_working/rule_audit_campaign/2026-09-19-max-dayshift-rulings.md:31`）上交包 B 修①="前缀真源扩 `src/zephyr/data/`（现只拦 `src/data/`，逃逸在宣称范围外）"。W1-D2 施工停手上交（台账 §5/§8）："src/zephyr/data/=合法模块 **MOD-L00-001**（数据集成器包，`python -m zephyr.data`，`docs/03_modules/_domain_data/blueprint.md:2`），字面扩前缀将冻结数据域→待 Owner 新裁定"。契约真源现值：`directory_contract.yaml` global_forbidden 仅 `forbidden_prefix: "src/data/"`[亲验]。
- **a**：精确扩面——契约不扩 `src/zephyr/data/` 整前缀，改为新增"运行态数据目录"条目（拦 `src/zephyr/data/` 下非代码产物，如 runtime/db/log 子目录名单），MOD-L00-001 代码面不受冻。
- **b**：豁免结案——前缀维持 `src/data/` 不变，契约显式登记 `src/zephyr/data/`=合法代码区并注明"#342① 不适用（MOD-L00-001）"，逃逸风险转由 F5/TEMP 类门禁兜底。
- 同批关联（不另占签字号）：B 修②"FORBIDDEN_PREFIXES=() 静默全放改 fail-closed"无争议，随任一案同批施工。

## 主题七：W9-6③ 两裁定尾巴终裁（2 项）

背景[亲验·git 实测]：总令 W9-6③ 要求两分支出终裁材料（并入 or 废弃二选一）。未发现 W9-6 代理已产出的独立材料文档（本节即终裁材料）。
**①`ai/st-sowner002-20260916/s-owner-002-regime-switcher`**（裁定"留分支"件）：分支 4 个有效 commit（探针 2 枚=预期死信勿落地）；dev 已有：裁定#304、e4_freeze/e4_handoff 两件、切换器模块 7 件+CLI+24 用例[亲验 `git cat-file`]；分支独有=出证报告 `e4_report_s_owner_002_regime_switcher.md`（fa5c8febaf，120 行，dev 无）。交接包合并指引[亲验]：`docs/_working/factory/strategy_cards/e4_handoff_s_owner_002_merge.md`（禁整支 merge，按序 cherry-pick；registry 冲突按 CAS 机械重放）。
- **a**：并入——按交接包 cherry-pick 残余（出证报告+registry 重放），完成后删分支。**b**：废弃——单文件抢救出证报告后直接删分支。
**②`ai/st-tv2terrain-20260917/BT-P1-032`**（做T#304 已封存）：分支独有=数据地形勘测报告 192 行（b7d8bafdde，dev 无）；BT-P1-032 勘测销账已由 0cd61d2b2f 写回 backlog（#304 四环关闭）[转报·bizmine owner_package]；S2 裁定=做T v2 现形态砍。
- **a**：并入——cherry-pick 勘测报告入档（数据地形事实留档）后删分支。**b**：废弃——整支删（报告随之弃）。

## 主题八：deep_review 收官遗留 #ARCH-338..356（19 项）

背景[亲验·注册表]：`architecture_issue_registry.yaml`（P0×2/P1×12/P2×5，均 status=open）；deep_review_full/ 目录留活指针至本族处置完后才归档（台账）。锚点=各 rpt_*.md（deep_review_full 内）。a=按注册表 adjudication 建议向；b=行内另一向。

| # | 一句话 | a / b |
|---|---|---|
| 338 | 执行域孤儿族（Saga/ExecutionEngine/ex_sor 全域零生产接线） | 接线（Saga 补偿+SOR 红线强制+科创板 lot）/ 退役删码 |
| 339 | 风控孤儿闸族（StopGate/止损引擎/清仓双守卫/黑天鹅分支零调用） | 整族接线（触发→清仓→复核闭环）/ 退役 |
| 340 | K02 资金事故假处置+kill switch 纯内存（P0） | 五级旗接入下单路径+开关持久化 / 显式弃用该机制 |
| 341 | K08 先报告后交易闸从未武装（P0，broker_ack 0/6） | 定 ack 数据源+武装时点 / 不武装 |
| 342 | 对账链双零接线+结算单缺失绿灯 | 随 #317 接线+Fill 契约加 side / 弃 |
| 343 | pf_alloc 整域（7 件仅 1 真接线，C04 veto 接线即 P0） | 整域接线（含 W05 真 ERC 立卡）/ 整域退役 |
| 344 | Regime 断供即满部署三腿 | fallback 三选一：a=hold-prev b=防御上限（告警显化建议必带） |
| 345 | Wyckoff 证伪旁路（弱 guard 静默接管） | 旁路拆除 / 等强证伪门 |
| 346 | embargo/purge 双承载缺省归零（PIT 实际零隔离） | 按 LdP 语义统一默认值 / 维持零默认 |
| 347 | 策略管线三洞（intake fail-open/陈窗直供/晋升 API 零认证） | T02 收紧灰度+T05 指纹修+T06 认证收半径 / 逐项另裁 |
| 348 | 卖出族族内对账（#309 挂起态下先记账） | 接电前族内对账统一 / 不对账接电（不建议） |
| 349 | 信号域接线期地雷（NaN 毒化/fail-open/标签漂移 5 例） | 接线前逐件矫治+MATURITY 治理 / 带病接线（不建议） |
| 350 | 数据基建三洞（熔断不落盘/缓存投毒/FINAL 三通道失效） | 缓存失效治理+熔断落盘 / 弃 |
| 351 | 9/18 miniQMT 退役 24 任务无退路+TF07 周频 DAG 边 | 退役映射表落地+时窗校验设计 / 逐任务个案 |
| 352 | 告警无推送通道（时延最坏 14h） | 重建推送通道 / 值班轮询机制 |
| 353 | F02 因子阶段闸失效+G01 stub（复算实锤） | F06 接线前必修+G01 填实或退役 / 拖 |
| 354 | 预测域接线期必修（NaN→(nan,nan)/symbol 直插 SQL） | 接线前补防御+参数化 / 拖 |
| 355 | X05 价格笼子恒 UNKNOWN 原价通过 | 券商层 quote 源接入设计 / 明示弃用该闸 |
| 356 | 轴 F 立卡清单（SOTA 对照 8 项） | 逐项按 mining_sop 立卡评估 / 整单搁置 |

## 主题九：W4-1 传导链 Owner 门位（4 项）

背景[亲验·备料]：`docs/_working/final3_campaign/w4_1_conduction_triage.md` §3.5（图库不变量"只增不删"，处置上限=状态/指针治理，禁物理删除）。
| # | 事项 | a / b |
|---|---|---|
| 9-1 | 3.2 节 12 条 status='active' 墓碑链（merged_into 已在，状态未翻） | a=统一翻转 deprecated（零数据变更）b=逐条判 |
| 9-2 | 4 条 S24 分流链缺 merged_into 指针（建筑材料/电池/电机/贵金属行业） | a=对照 S24 治理记录补指针 b=确认无目标 |
| 9-3 | 大型墓碑先核验后定终态（医疗器械 93/95 活跃节点等 4 条） | a=先节点迁移核验 b=直接定墓碑终态 |
| 9-4 | B 类 5 条判重并入（创新药/铝土矿/种业/无人机/工程机械→同名目标链；涉注册表净删=门位） | a=判重并入目标链 b=双链并存补 1 条传导边留痕 |

## 主题十：W1 收尾遗留（2 项）

背景[亲验·台账 §8]。
| # | 事项 | a / b |
|---|---|---|
| 10-1 | DCR-001：10_trading_map 目录契约不含 index（同批 advisory：check_index_integrity LOW 588→1500=生成器平铺 vs 校验器递归口径矛盾） | a=该目录补/生成 index b=契约登记豁免（口径矛盾随批给生成器/校验器统一口径） |
| 10-2 | GATE-21 manifest 秒级竞态窗口（校验与重生成并发窗） | a=登记为已知限制+例行重生成兜底 b=治本收窄（锁内重验，施工排期） |

---

## 签字栏（Owner 逐号批 a/b 即生效）

**主题一（96）**：
A-01__ A-02__ A-03__ A-04__ A-05__ A-06__ A-07__ A-08__ A-09__ A-10__ A-11__ A-12__ A-13__ A-14__ A-15__ A-16__
B-01__ B-02__ B-03__ B-04__ B-05__ B-06__ B-07__ B-08__ B-09__ B-10__ B-11__ B-12__ B-13__ B-14__ B-15__ B-16__ B-17__ B-18__ B-19__
C-01__ C-02__ C-03__ C-04__ C-05__ C-06__ C-07__ C-08__ C-09__ C-10__ C-11__ C-12__ C-13__ C-14__ C-15__ C-16__ C-17__ C-18__
D-01__（过则连带 D-02~D-06）D-02__ D-03__ D-04__ D-05__ D-06__ D-07__ D-08__ D-09__ D-10__ D-11__ D-12__ D-13__ D-14__
E-01__ E-02__ E-03__ E-04__ E-05__ E-06__ E-07__ E-08__ E-09__
F-01__ F-02__ F-03__ F-04__ F-05__ F-06__ F-07__ F-08__ F-09__ F-10__ F-11__ F-12__
G-01__ G-02__ G-03__ G-04__ G-05__ H-01__ H-02__ H-03__

**主题二~十（32）**：
- 二 szopen：__（a=Owner 做 A/B 两组操作，b=放弃）
- 三 W8-1 归档批：__（a=批准 A14+B2 即归档、C-3×5 留 09-30、clean_exam 保留项知悉）
- 四 W4-2 ig bak 92 表：__（a=留 1 份/族其余冷存后删）
- 五 自启+看门狗：__（a=方案 B 壳托管，b=方案 A 双计划任务）
- 六 #342 B①：__（a=精确扩面，b=豁免结案；B 修②随批）
- 七 sowner002 分支：__（a=cherry-pick 并入后删，b=抢救报告后删）
- 七 tv2terrain 分支：__（a=并入勘测报告后删，b=整支删）
- 八 #ARCH-338__ 339__ 340__ 341__ 342__ 343__ 344__ 345__ 346__ 347__ 348__ 349__ 350__ 351__ 352__ 353__ 354__ 355__ 356__
- 九 9-1__ 9-2__ 9-3__ 9-4__
- 十 10-1__ 10-2__

签字：____________ 日期：__________（批注可写在对应编号后，如"C-08 b(留 CAND-WFO-001)"）

---
汇编：st-final3-20260919 W8-3｜2026-09-19｜未找到项已如实标注（W9-6 代理材料未产出→主题七为本册自备；szopen 28/29 口径差原文并存；clean_exam 移交仅结案报告级证据）。
