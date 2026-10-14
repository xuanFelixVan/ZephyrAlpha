---
ttl: task_bound
completes_when: 清单内问题全部施工完成、或 Owner 叫停、或清单整体被替代时
title: "TDM 决策地图 — 原样底稿"
---

# TDM 决策地图 — 原样底稿

> 机器从 `docs/_working/**` 抽取的「遗留 / 待办 / 未完成 / 待裁 / 缺口 / 风险」类段落。
> **逐字复制，未作任何改写、删减或归纳**（超长段落标注 [TRUNC]）。
> 用途：归档 `docs/_working` 前的零丢失兜底；正文文档只给核实后的结论，底稿给原文。


---

## 来源：`docs/_working/2026-10-12-exam-card-mining-meta-method-research.md`

### L204 · 9.3 尚未入考的对象（S0 缺口清单）

### 9.3 尚未入考的对象（S0 缺口清单）
TDM 节点主张参数（"催化剂加权 20%"类，卡面已承诺由响应曲线定）；风控约束栈六层参数（trading_decision_map.yaml:4538：总仓位/回撤限额/波动率目标/集中度/流动性/相关性）；成本模型滑点 bp 表敏感性；RL 执行算法（B-007 后）；分配器邻域；LLM 档位。


---

## 来源：`docs/_working/archive/2026-09/bizmine_night/crypto_probe/funding_carry_results.md`

### L71 · 7. 前置与数据缺口登记（不阻塞判定，归属数据线）

## 7. 前置与数据缺口登记（不阻塞判定，归属数据线）

1. **费率核实前置未闭环——卡内作废条款已触发待 Owner 裁定**：卡冻结占位 taker 2bp/边，且卡明文"执行前必须以 Owner 实际费率档+Hyperliquid 官方费率页重估，差 >1bp/边则本卡自动作废重开"。今夜实测：HL 公开费率页（base tier）=永续 taker **4.5bp**/边、现货 taker **7bp**/边，对占位差 2.5bp/5bp 均 >1bp；Owner 实际费率档无法在夜间核实。→ 本考试按车道令以 frozen 占位口径执行并入册，**作废条款触发与否=Owner 门位**。注意：按真实费率重算 carry 降至 ≈3.0-3.4%，只会更红。
2. 清算流 `hl_liquidation_raw` 实测 1 行（连接性测试行）→ 清算链策略不可考，**数据缺口，归属数据线**（T4 报告工单③维持）。
3. 现货/永续双腿行情缺失（现仅 Binance 现货日线×Hyperliquid funding 跨所拼接）→ basis 不可测，关③退化（§5）；建议数据线工单优先级①②不变。
4. 日线仅 13 个月=单一牛熊相位，OOS 无真外延段；本结论在更长样本上可能漂移，属卡明示局限。


---

## 来源：`docs/_working/archive/2026-09/c_class_scattered/2026-09-07-tdm-internal-factpack.md`

### L33 · 风险限额库 REG-RLM-001（20 条）

### 风险限额库 REG-RLM-001（20 条）

| 引用 ID | 注册表语义 | 挂载节点 | 判定 |
|---|---|---|---|
| RLM-DRAWDOWN-001 | 止损三要素 | X-S1, X-S1-02 | ✓ |
| RLM-DRAWDOWN-002 | 跌破支撑必止损 | X-S1 | ✓ |
| RLM-DRAWDOWN-003 | 跌停也卖（-10%） | X-S2-02 | ✓ |
| RLM-DRAWDOWN-005 | 生死线破位清仓 | P1-04 | ✓ |
| RLM-DRAWDOWN-006 | 时间止损三档 | P1-04, X-S1 | ✓ |
| RLM-KILL-SWITCH-004 | 回撤 L4 清仓（25% Kill Switch） | X-R1, X-S1-06 | ✓ |
| RLM-KILL-SWITCH-005 | 单日亏损 6% 紧急熔断 | X-R1, X-S1-06 | ✓ |
| RLM-KILL-SWITCH-006 | 组合日度熔断 4%（停开仓 1 天） | P3-01 | ✓ |
| RLM-KILLSW-003 | 生死线破位清仓信号 | X-R1 | ✓ |
| **RLM-KILLSW-005** | **跌停不 T** | **X-R1** | **⚠ 语义轻微偏移**：做T禁忌规则挂在应急保命节点——同属 kill_switch 族但更贴 P2 做T语义；建议后续迁 P2-01（非 Blocker，挂载不产生错误行为）（外审加码 2026-09-07：偏移根因在注册表分类 limit_type=kill_switch；该条目 consumption_tracking 仍含禁用词"正 T"、status=candidate） |
| RLM-CONCENTRATION-001 | 不梭哈一只 | P1-05, P3-03 | ✓ |
| RLM-CONCENTRATION-002 | 总仓位控制规则（60%） | F-C2-02 | ✓ |
| RLM-CONCENTRATION-003 | 相关性矩阵敞口合并（0.7σ） | P1-05, F-C2-02 | ✓（与 D77 口径 0.70 同源） |
| RLM-CONCENTRATION-004 | 单板块上限 20% | P1-05 | ✓ |
| RLM-POSITION-004 | 不盲目补仓 | P3-01 | ✓ |
| RLM-POSITION-006 | 首批+二批+现金机动（30%） | P3-03 | ✓ |
| RLM-POSITION-009 | 加仓路径预埋 | P3-01 | ✓ |
| RLM-POSITION-011 | 反弹冲高减半转进攻仓（50%） | P2-04 | ✓ |
| **RLM-POSITION-013** | **共振策略首仓即终仓（不加仓）** | **P3-01** | **⚠ 可解释**：挂在加仓资格门作"否决规则清单成员"（特定策略禁加仓），非矛盾——但外审勿报"加仓门挂禁加仓规则"为冲突 |
| RLM-POSITION-021 | 策略胜率驱动仓位风控（凯利，3%） | P3-03 | ✓ |

### L111 · §6 清单缺陷修复记录（试运行产出，v1.2.0→v1.3.0）

## §6 清单缺陷修复记录（试运行产出，v1.2.0→v1.3.0）

1. §1 材料清单漏本事实包 → 补材料⑤
2. F2/F3/H2/H4 未声明"已内审收口" → 改为"复核事实包+抽查存疑项"（防外审重复劳动）
3. §5 已知边界漏"已落码未接线模块"与"schema_version 文件头=1.1 与备忘录 v1.5-v1.8 演进的关系" → 补 2 行
4. J0 缺 E 流组件指针（64 节点组件未列全，外审查 regime/HMM 会误报） → 补指针行
5. C 维度漏"新股首日"场景（系统内无历史数据的标的） → 补 C9


---

## 来源：`docs/_working/archive/2026-09/c_class_scattered/2026-09-07-tdm-pre-backtest-review-checklist.md`

### L135 · F. 引用语义匹配（已由内审事实包预收口——复核模式）

### F. 引用语义匹配（已由内审事实包预收口——复核模式）

F0. **先读材料⑤（内审事实包）**：62 条交叉引用语义表/33 模块锚定接线状态已核对完毕，⚠ 标注 3 条（KILLSW-005 跌停不T 挂 X-R1 偏移、POSITION-013 首仓即终仓 作资格门否决成员、BMK-INDEX-003 注册表状态 candidate）
F1. 复核事实包 §1 判定逻辑，抽查其中 5 条你最有疑问的引用（勿重复已标 ✓ 的 59 条全量核对）
F2. 模块能力匹配：事实包 §2 标注了 production+零生产消费与接线未核验两类——抽查 3 个模块的 action 描述与能力匹配度，发现新失配再报


---

## 来源：`docs/_working/archive/2026-09/c_class_scattered/2026-09-09-node-backtest-governance.md`

### L315 · 8.4 协同与风险

### 8.4 协同与风险

1. **Kimi 抽屉 v2 衔接**：P0-3 严格沿 DDT 模板册六助手契约+分区顺序追加，不动他定稿的样式语义；改完补 ACC-F-TDM-DRAWER 验收条目。
2. **并发 session 教训**（Kimi 交付总结：sess-30232 git add 搭便车事故）：每期提交前核对 `git status` + `--files` 清单逐一核对，只提自己的文件；遇并发暂存冲突按 66 号串行化排队。
3. **登记表新建必走 CREATE-GUARD**：token 插入位置=真 creation_tokens 列表内（EOF 追加坑已实证 500+ 条历史误置）。
4. **CH 建表属基础设施**：走全局规则不走 SOP 15 步，但 DS 登记照做。


---

## 来源：`docs/_working/archive/2026-09/c_class_scattered/2026-09-09-tdm-growth-blueprint.md`

### L91 · §2 职能完备性对照表（增长的总地图——往这上面找缺口）

## §2 职能完备性对照表（增长的总地图——往这上面找缺口）

| 决策职能族 | 现有承载 | 缺口判定 |
|---|---|---|
| 大盘判断（今天能不能做） | L1 五传感器+AGG+总闸；L0 作战计划 | **G1：明日情绪盘中滚动预测缺（见 §3）** |
| 板块/赛道（打哪里） | L2 十环节 | 较完整；反查后微调 |
| 个股（买哪只） | L3 十二环节 | 较完整；L3-04 负面否决今晚 C7 建 |
| 执行（怎么成交） | L4 十三环节+SOR 零件 | TCA/成本反馈闭环弱——G5 候选 |
| 持仓管理（手上怎么办） | P1/P2/P3 | P1-03 今晚 C8 建 |
| 离场（怎么走） | X-S1/S2/R1 | 较完整 |
| 组合反馈（钱怎么分） | F-C1/C2/C3 | 较完整 |
| **资讯→决策传导（新体系）** | 零件散落（alt_data/intelligence/nlp/产业链图谱），**无入图主干** | **G2：本批增长主分支（设计归本轨，管道归接线会话，见姊妹指令）** |
| 明日推演（明天怎么办） | tomorrow_boundary_planner（盘后）+ 8 态预测零件 | **G1：盘中滚动预测断链** |
| 币圈 | TDM-C-* 四节点骨架 | G3：展开设计先行，实现待 Owner 排期 |


---

## 来源：`docs/_working/archive/2026-09/c_class_scattered/2026-09-09-tdm-missing-modules-construction.md`

### L147 · 七、待 Owner 拍板的两个结构项（拍板后并入对应波次）

## 七、待 Owner 拍板的两个结构项（拍板后并入对应波次）

1. **四个流根节点**——✅ **已落地**（2026-09-09 深夜他会话合并批次入图：TDM-E/P/X/F-FLOW，地图 133 节点/185 边，validate 绿），夜班勿重复施工
2. "什么时候买"类大白话改名 vs 拆细（L4-02 买入时序已承载；改名成本低；拆细按 D108 三条件逐个立）——维持"今晚不动"，看一版带流根全景后再定

### L259 · 12.3 登记不移交（非缺陷/Owner-gated/st-igbe 射程）

### 12.3 登记不移交（非缺陷/Owner-gated/st-igbe 射程）
- 三条空壳脚手架链（改性塑料/量子计算/有机硅，同秒批量创建 0 节点 0 公司）= 09-09 种子计划待填，归 st-igbe 内容管线
- deprecated 残片节点（一文读懂洁净室产业链/深度/2026年短剧内容消费偏好孤儿节点）= S24 类 Owner-gated，galaxy 不可见仅搜索直击（已由 status 过滤修复）
- 引擎词表扩"版本/一文/深度"等前缀 = st-igbe 在飞 vocabulary 批射程（避撞未动）
- 终态 API 审计：45 簇/594 链，零空名/零脏名/搜索回归绿；遗留=空壳链×3（登记）

### L274 · 十四、落库完成（2026-09-12 04:44，sole-committer-20260911 收尾会话）

## 十四、落库完成（2026-09-12 04:44，sole-committer-20260911 收尾会话）

- **状态：LANDED ✅ commit `e86ce72b80`**「feat(tdm): 四批开工令整批落地——C13/L3-06/L3-09 三模块新建+六锚回填+D1 编号规范化（night-gw-2300）」，HEAD 逐件核对 22/22 与清单完全一致、零外来搭便车，22 件工作区全 clean。
- **31 件总账**：9 件先期入库（4 蓝图+翻译表+ownership map 早前批；C13/L3-06/L3-09 三蓝图随 st-encfix 829f6417fb）+ 22 件本批（16 M+6 A）= 31/31 全部落库，§十三"待落库 22 文件"清零。
- **四关复验终态**：validate errors=0 ✅ / 双地图测试 **98 passed** ✅ / align_all **exit 0**（domain_mismatches=0、ghost_anchors=0、硬问题清零）✅ / 8890 服务 **200** ✅。
- **R1/R21 漂移定性（非本批问题，全额归属接线会话）**：R1 28→**25**（改善：TDM-E-L2-09-1/09-2/L3-08 三红节点被接线 module_ref resolving）；R21 0→**3**（同三节点"有 ref 无 id"）——落库 diff 实证系 wiring 接班会话在共享地图工作区插入的**文档化中间态**（行内注释原文："module_ref-only warn 路线：MOD-INT_NEWS_CHAIN/MOD-INT_CHAIN_IMPACT 待 R21 格式冲突解挂后补 module_id"，指向 src/zephyr/intelligence/news_chain_node_linker.py/chain_impact_resolver.py），骑乘本批入库；98 测试在该地图状态上跑绿。欠账归接线会话台账，非本批偿付义务。
- **落库排障纪要（10 次尝试全定性，零盲试）**：①LOCK_TIMEOUT→--wait 900；②SESSION-REQUIRED（原会话心跳死）→register+heartbeat_daemon 复活；③FOREIGN_CHANGE（claim 基线过期）→release-only+re-claim 钦定三连；④DATETIME-NOW-FORBIDDEN/NOQA-VALIDATION×2（外来 tqcenter_provider.py gate 迭代）→他会话自修（重构 now_utc）；⑤COMMIT_SCOPE 8 域→--allow-multi-domain（2026-08-13 裁定预授权，本批=跨域编号重构自许可场景）；⑥TRACKED-DRIFT-READONLY（外来并发写 architecture_issue_registry.yaml）→等写入波停稳后钦定重试一次即过；⑦他会话提交 stash 舞步两次 unstage 我 22 件→重装零丢失。st-encfix own-scope 治本对本批生效实证：外来 staged 文件违规仅剩 gate-infra 全局闸（FRONTEND-MAP/DATETIME/NOQA/TRACKED-DRIFT）仍连坐，内容类闸（ENCODING 等）已不再咬外来件。


---

## 来源：`docs/_working/archive/2026-09/c_class_scattered/2026-09-10-commit-pipeline-perf-plan.md`

### L420 · 5. 待 Owner 决策事项

## 5. 待 Owner 决策事项

1. **P0 三项是否批准立即施工**（①②③，合计 ≤2 人天，零行为语义变更）。
2. **echo_guard 超时 30→10s（语义权衡确认）**：该项**非严格行为等价**（尾部检测覆盖收窄，§2.7），默认不做；若接受权衡，建议顺序=先做 5b 根因治理（rescan.signal/索引健康），观察 30s 超时是否自然消失，再决定是否调参。
3. **死信 856 项**：授权先出报表，批量清理（purge）需二次确认。
4. **DECISION-MAP 8.24s 恒跑**：接受现状（防断链设计）vs 立项"按触发文件降频"（staged 未触及 trading_decision_map/相关注册表时跳过——语义弱化为"触发式"，需 Owner 认可断链防护窗口收窄）。
5. **P2 三项是否立项**（⑦⑧⑨），及 flag 开启窗口安排（宪章 B-007）。
6. **--wait 默认值**：维持 60.0（推荐）vs 调整为 120/180（直接缓解轮询，但不解决占锁时长本身）。

---


---

## 来源：`docs/_working/archive/2026-09/c_class_scattered/2026-09-10-xflow-followup-design.md`

### L28 · X 流验证批遗留项跟进设计（exec v2 口径 / 定稿锚点 / 消融实弹预案）

# X 流验证批遗留项跟进设计（exec v2 口径 / 定稿锚点 / 消融实弹预案）

> 日期：2026-09-10 ｜ session：st-xflow-20260910 ｜ 前置：2026-09-10-xflow-batch-report.md §三遗留清单
> Owner 问"现在就调研修复可以吗"——四项分诊：④③=本轮已施工（见 §一/§二），①=设计稿待裁定（§三），②=纪律闸不动、预案备好（§四）。

## 一、④ exec 滑点 v2 口径（已施工）

**改动**：`compute_exec_metrics`（runner.py）滑点基准优先级=decision_price（T1 起新产物携带，真滑点=成交价 vs 记录意图价）→ ref_prices VWAP 代理（旧产物兜底）→ 两路皆缺跳过（不猜）。新增返回键 `slip_basis`：`decision_price | vwap_proxy | mixed(dp=N,vwap=M) | None`，L4 批 notes 带"基准口径=…"进台账（面板可读）。

**设计决策**：
1. **兜底不剔除**：0/34 存量产物带 decision_price（实测核实），剔除=旧产物永远无滑点指标；混合口径用 notes 明示比例，不混装不隐瞒。
2. **lag_recheck 语义变化**：decision_price 是记录意图（事件时点锚定），非行情派生基准——PB-16 "加 1 天滞后重算"的前视诊断对该路径无意义（意图价不存在"偷看未来"问题），该诊断仅对 VWAP 兜底路径保留。v1 的 lag_recheck 开关未实际接基准右移实现（一期 note 披露过），本次不改其机制。
3. **连续性声明**：一期 42 行+本批 18 行台账全部 pending+insufficient_samples、零真结论——口径切换零历史连续性成本（本设计文档即为切换记录）。

**测试**：TestExecMetricsV2Basis 7 用例（优先级/方向符号/VWAP 兜底/mixed 标注/双缺跳过/脏值回落/notes 贯通），runner 套件 21→28。

## 二、③ SellSignal→XFlowAction 自动化第一层（已施工）

**改动**：ablation.py 新增 `sell_signals_to_xflow_actions(signals)` 纯函数——sell_decision.SellSignal → XFlowAction 映射：CLEAR/REPLACE→clear（换股=先清仓，v1 无建仓动作位）、REDUCE→reduce 且 reduce_to=1.0−confidence（减仓量∝置信度，conf≤0 保守忽略）、source=signal.source 或默认 "TDM-X-S1"。ablate_weight_panel 索引匹配加双侧 [:10] 容错（"2026-01-06" 字符串可命中 Timestamp 索引）。测试 +7（TestSellSignalsToXFlowActions，真实 SellSignal dataclass 构造+端到端贯通 ablate_weight_panel），ablation 套件 9→16。

**调研事实**（subagent_A_sellsignal.md）：sell_decision/core 22 模块 21 个纯函数/显式状态注入（唯一内存状态=笔级熔断器，平凡可重演）——**可重放性不是障碍；真正缺口=8 类 signal_type 的 provider 全仓零实现**（stop_loss/take_profit/breakout_failure/replacement_rebalance 四个算法族存在且可历史驱动，但没有任何代码在历史 K 线上逐 bar 调它们产 SellSignal；测试全部标量夹具零 K 线）。

**语义关键点（下一层工程的前置问题，本轮不动）**：历史重放式自动化的持仓耦合——全量跑与剥离跑持仓路径不同，卖出信号生成应基于哪个持仓状态？分析：应基于**全量跑的持仓路径**（X 流信号在真实（全量）世界里生成，剥离跑模拟"若无 X 流"的反事实世界——反事实世界里不该再产 X 流信号，否则自我指涉）。该语义+前视风险（卖出逻辑用当日收盘判定当日卖出=前视，须 T+1 生成信号）留待 provider 工程立项时一并定稿。

## 三、① 定稿锚点方案（设计稿，**待 Owner 裁定，未改码**）

**张力陈述（原文逐字）**：
- 现机制（runner.py holdout_cutoff）：`inside = ts ≤ (as_of − 12 个月)`——任何新流水要压满 12 个月才进在验窗口。
- 晨报 2026-09-10 原文："T1/T2 的价值=机制就绪，窗口前移（2026-09-09 之后新数据积累）即出真结论"；收尾报告同款表述。
- 两者矛盾：按现机制，2026-09-09 之后的流水最早 2027-09 才可考，"新数据积累即出真结论"永远不成立。

**定稿锚点设计**：`ValidationConfig` 增 `finalized_at: date | None = None`；`partition_by_holdout` v2 分支：
- finalized_at=None → 现行为（12 个月锁，保守模式，默认不变）。
- finalized_at=D → `ts > D` 的流水可考（D=参数定稿日；调参发生在 D 之前，定稿后才产生的流水天然无污染）；`ts ≤ D` 全锁（含原 12 个月窗口，一律不再碰）。
- D 候选值=2026-09-09（治理真源裁定日）。"考完作废前移"落法：D 即前移后的保密线；考过一次后若再改参数→新 D'（换卷重考），旧 D' 之前的全部锁死。台账只追加+run_id 追踪（同参数同窗口二次考=审计可见），防重复考试。

**与 §12 原文对照**：§12 "12 个月保密考卷/考完作废前移/定稿前不许跑回测"——锚点方案是"前移"语义的显式实现（12 个月窗是一次性封存，考完/定稿后前移到 D），非放宽；定稿前不许跑回测的约束原样保留（消融实弹仍待放行）。

**风险**：①D 定错（定稿声明后 map 又改）→ 换 D' 重锁即可（台账只追加可审计）；②重复考试 → run 追踪+纪律；③D 之后新流水本身被后续调参污染 → 参数搜索若用 D 后数据拟合，则 D 需重新前移（换卷）。

**裁定请求（Owner 直接回同意/不同意即可）**：
> 建议把 holdout 机制升级为"定稿锚点"：在现有 12 个月保密窗口之外，增加参数 finalization（参数定稿日 D=2026-09-09）；D 之后产生的行情流水不再受 12 个月封存约束（调参时它们不存在，天然无污染），可直接用于验证批出真结论；D 之前的全部流水（含现 12 个月窗口）永久封存不再碰。不改此默认（finalized_at=None 时行为与现在完全一致），仅在你裁定"参数已定稿"时启用。同意后我施工（改动面：ValidationConfig+partition_by_holdout+单测，约 0.5 人日）。

## 四、② 消融实弹执行预案（纪律闸不动，放行后照此执行）

**前置条件**：①Owner 裁定参数定稿（或启用 §三锚点）；②窗口选择（下述两通路二选一）。

**证据**（probe_artifacts 实测）：34 个产物 0 个带 decision_price；流水窗口全部 >2025-09-09（最早起点 2025-09-30）——即"在验窗口（≤2025-09-09）目前没有任何已跑回测流水"，旧窗口重放不存在"已经被考过"的记录，但也没有现成对照产物。

**通路 A（推荐）：定稿参数重跑旧窗口**——用定稿后的策略参数对 ≤2025-09-09 窗口跑全量+剥离两支回测（该窗口不在任何已有产物的流水范围内=从未被考过，不碰保密考卷；且是旧数据，跑完不影响 D 后新流水继续积累）。命令序列：
1. `run_ablation(data=load_history(...≤2025-09-09), panel_full=..., actions=...)` → rescued 序列
2. `run_validation(batch="XFLOW", ablation_diff=rescued)` → 18 节点真 verdict 进台账
**通路 B：等新流水积累**——D 后实盘/模拟流水自然积累（无需回测），窗口前移后直接 run_validation。保守但最慢。

**产出预期**：两通路最终都产生 18 行 exit_counterfactual verdict（valid/noise/pending 按土规）；消融差额=X 流救回金额（ablation_report.rescued）。

## 五、本轮施工与验证

| 项 | 状态 | commit |
|---|---|---|
| ④ exec v2 口径（runner.py+7 单测） | 已施工，28/28 绿 | 见提交记录 |
| ③ 转换助手（ablation.py+7 单测+索引容错） | 已施工，16/16 绿 | 同上 |
| ① 定稿锚点 | 本文档 §三待裁定 | 未改码 |
| ② 实弹预案 | 本文档 §四备妥 | 未改码 |

调研产物：.runtime/tmp/xflow-followup-20260910/subagent_A_sellsignal.md（可重放性判定表）、probe_artifacts.py（证据核实脚本）。


---

## 来源：`docs/_working/archive/2026-09/c_class_scattered/2026-09-11-tdm-morning-review-report.md`

### L176 · 五、差异与遗留登记（诚实交底）

## 五、差异与遗留登记（诚实交底）

1. **施工清单 9.1 与地图真源差异**：9.1 记"L3-09 已非红"，实测地图 TDM-E-L3-09 module_ref=null 仍红——以地图真源为准，登记差异待锚定批。
2. **双测试 98 绿口径**：当前 97 绿+1 fail（industry_graph 在途文件撞登记门禁）——非本域产物，留痕待该域收口自愈。
3. **C1/C5/L2-05-1 等 10 处 R21 交叉锚欠账**：其中 C1（MOD-SIG-135）、C5（MOD-SIG-136）depgraph 缓存在册但地图 module_id 未回填——属 D1 同款格式/流程欠账，随 R21 专项批清偿；L2-05-1（sentiment_cycle）与 P2-01/X-R1-01/02/X-S2-02 等为缓存无 MOD id 或 spec id 非 MOD 格式，如实留欠账禁硬造。
4. **L4-02/L4-08 强候选锚**：语义承载件在（batched_position_builder/breakout_failure_detector production），建议下批正式锚定回填。


---

## 来源：`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-typhoon-bdi-factor-mining-plan.md`

### L257 · F11 周期相位 → 结果：**U 型（两端延续、中间反转），登记待验证观察项不立卡**

### F11 周期相位 → 结果：**U 型（两端延续、中间反转），登记待验证观察项不立卡**

相位五分位 → 前向猪价呈 **U 型**：最低相位组前向 12 周 +5.2%、最高相位组 +4.6%、中间组 -4.2%。顶部区（相位>1.15）前向 4/8/12 周 +2.2%/+4.0%/+5.1%（t=1.87/1.98/1.83，n=120，边缘）——**周期顶部不反转反而延续**（动量型），与"顶部反转" naive 直觉相反；股票端顶部区 +0.073%/日 vs 底部区 -0.081%/日 方向一致但 t=0.66/-1.02 不显著。判定：方向有苗头（相位极端的动量延续）、统计不达线、且 U 型非预注册假设——登记待验证观察项，毕业条件=预注册"顶部动量"假设后 OOS（2024-2026 留样）重验 + 股票端换等权指数复算。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/rpt_t03.md`

### L52 · 4 缺陷清单

## 4 缺陷清单

1. **[P2] regime confidence NULL 炸腿致全日拍板 error**——现状：reader 解包无 NULL 防御（daily_gate_snapshot.py:127）+编排器 `or 0.0` 混淆 None/0（:538）；影响：坏行→当日无决策快照+需人工 force（visible 但单点脆）；建议：reader 侧 NULL→status=absent 带原因，编排器侧显式区分"缺失"与"零置信"；验证法：注入 NULL 行复演。
2. **[P2] euphoria sell_only 未结构化落列**——现状：语义只在 note 文本与内存 dict（:423/:548/:683-703）；影响：S7 执行面接电后"只卖不买"无法从 decision_daily 机读，靠翻 note=口径漂移温床；建议：INSERT_COLUMNS 增 sell_only 列（schema v1.1）或 package_set_json 内结构化；验证法：读 schemas/categories/decision_daily.py 列清单。
3. **[P3] marker 先占+写失败不回滚=当日决策缺失需人工 force**（已测已裁定，:681+test:343）——建议：告警文案加"需 force 补拍"行动项；验证法：见测试。
4. **[P3] 唤醒条件 import 失败 fail-open**（:731-736）——建议：except 分支留痕计数；验证法：monkeypatch。
5. **[P3] TDM 裸读绕过 schema 校验**（:340-350）——建议：复用 decision_map.load_decision_map；验证法：喂坏 YAML 对比两路行为。
6. **[P3] 场景 SQL 硬编码表名 vs 自declared不变量**（:156-174）——建议：两表入 TableRegistry 或修订注释豁免留痕；验证法：查注册表。
7. **[P3] marker TOCTOU/非 CAS 写**（:186-205）——建议：safe_write_text 带 expected sha；验证法：并发复演。
8. **[P3] conf=0 仍给带下限×0.5 仓位**（:405-423）——建议：Owner 确认零置信语义；验证法：compute_position_cap("expansion",0.0)。
9. **[P3] 与 daily_warroom_pipeline 双实现漂移面**（:36-37）——建议：口径对账清单登记（align 体系）；验证法：diff 两模块日历解析。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/rpt_t05.md`

### L53 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] 滚动窗口不在指纹内→自动路径证据窗冻结**
   - 现状：fingerprint=权重+tdm_sha12（:132-150），默认窗滚动 12 个月（:165-169），幂等闸不比窗口（:799 仅比 fingerprint）。
   - 证据：:980-981 注释前提"面板由同窗口同数据决定"在 date.today() 滚动窗下日日为假；promotion_advisory.py:154 消费 latest.json。
   - 影响：TDM/权重稳定期整装证据停在末次变更日的窗口，晋升建议器持续引用陈窗组合证据=决策系统性偏移（不报错只偏）。爆炸半径：sim→production 晋升链的证据③输入。
   - 建议修法：指纹加入 window（或 acceptance 记录窗口、幂等闸加"窗口相同"判据；或固定窗 refit 语义）。
   - 验证法：两日连跑非 force，第二次 skipped=true 即复现。
2. **[P2] 指纹输入面不含 plans 全文/引擎版本/数据版本**——证据 ：138-149；影响：引擎修复/面板修正后同指纹照跳（陈证据延续）；建议：source_sha256_12 缺失时禁幂等（fail-closed）+引擎侧 run_id/代码版本进证据；验证法：抽掉 plans 的 sha 行重跑。
3. **[P3] journal 旁路消费与 drain 并发无锁**（:1169-1196 vs pipeline_events drain）——建议：收口时把 fw_backtest_due 注册进分派表消除旁路（docstring 已预留）；验证法：并发压测。
4. **[P3] 幂等跳过无持久审计痕迹**（:984-992）——建议：跳过也追加轻量 evidence 或 journal 回执留痕；验证法：跳过后查目录。
5. **[P3] bh_fdr SSRN 引用错挂**（bh_fdr.py:26）——建议：改引 Arian et al. 2024 与 Harvey & Liu 2015 JPM 分列；验证法：SSRN 4686376 页面标题对照。
6. **[P3] latest.json 覆写无 CAS**（:1085-1088）——建议：safe_write_text 带 expected sha 或接受串行化前提注释；验证法：同秒双跑。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/rpt_t08.md`

### L8 · T08 TDM 全图对账（阶段0封矿零缺口证明）

# T08 TDM 全图对账（阶段0封矿零缺口证明）

- 基线: 2fa92002c3｜TDM: config/trading_decision_map.yaml（schema 1.2，138 节点/194 边）
- 节点类型分布: stage=108, aggregation=16, sensor=7, gate=4, cross_cutting=3

## 对账结果
- 有 module_ref 的节点: **115** / 138
- 无 module_ref（纯数据/聚合/横切节点，非独立算法对象）: **115** 个中已覆盖 **30**；
- 无 module_ref 节点数: **23**（node_id 前 20: ['TDM-E-FLOW', 'TDM-P-FLOW', 'TDM-X-FLOW', 'TDM-F-FLOW', 'TDM-E-L2', 'TDM-E-L2-05', 'TDM-E-L3', 'TDM-E-L3-03', 'TDM-E-L3-07', 'TDM-E-L3-11', 'TDM-E-L3-12', 'TDM-E-L4', 'TDM-P-P1', 'TDM-P-P2', 'TDM-P-P3', 'TDM-X-S1', 'TDM-X-S2', 'TDM-F-C2', 'TDM-F-C3', 'TDM-C-L1']）
- module_ref 未落入全景清单的缺口: **85** 个

## 缺口清单（逐个裁定）
- TDM-E-L0-01（计划生成）→ `src/zephyr/plan_engine/daily_trade_plan.py`
- TDM-E-L0-02（偏离监控与修订）→ `src/zephyr/plan_engine/plan_deviation_monitor.py`
- TDM-E-L0-03（收盘复盘与明日边界）→ `src/zephyr/plan_engine/tomorrow_boundary_planner.py`
- TDM-E-L0-04（明日情绪盘中滚动预测）→ `src/zephyr/plan_engine/intraday_tomorrow_forecast.py`
- TDM-E-L1-S1（大盘指数传感器）→ `src/zephyr/regime/features/index_sensor.py`
- TDM-E-L1-S2（市场内部结构传感器）→ `src/zephyr/signal_ashare/limit_up/limit_up_followthrough.py`
- TDM-E-L1-S3（赚钱效应传感器）→ `src/zephyr/signal_ashare/limit_up/lhb_premium_analyzer.py`
- TDM-E-L1-S0（宏观环境传感器）→ `src/zephyr/alt_data/policy_expectation_analyzer.py`
- TDM-E-L1-S0-1（新闻情绪语义分析）→ `src/zephyr/intelligence/news_sentiment_analyzer.py`
- TDM-E-L2-01-1（结构强度评估）→ `src/zephyr/signal_ashare/sector/sector_analyzer.py`
- TDM-E-L2-01-2（动量活跃度排名）→ `src/zephyr/data/sector_ranking_engine.py`
- TDM-E-L2-01-3（多周期动量加权）→ `src/zephyr/signal_ashare/sector/sector_momentum.py`
- TDM-E-L2-01-4（板块资金流聚合）→ `src/zephyr/signal_ashare/sector/sector_breadth.py`
- TDM-E-L2-02（轮动序列追踪）→ `src/zephyr/signal_ashare/sector/sector_divergence.py`
- TDM-E-L2-02-1（RRG 轮动序列）→ `src/zephyr/signal_ashare/sector/sector_rrg.py`
- TDM-E-L2-02-2（单板块轮动预警）→ `src/zephyr/signal_ashare/sector/sector_analyzer.py`
- TDM-E-L2-03（调整周期进度）→ `src/zephyr/signal_ashare/sector/sector_adjustment.py`
- TDM-E-L2-03-1（扩散指标进度追踪）→ `src/zephyr/signal_ashare/adjustment_cycle_tracker.py`
- TDM-E-L2-04（板块级市场状态）→ `src/zephyr/signal_ashare/core/sector_ecology_judge.py`
- TDM-E-L2-04-1（轮动状态五分类）→ `src/zephyr/signal_ashare/sector/sector_rotation_state.py`
- TDM-E-L2-04-2（虹吸态识别）→ `src/zephyr/signal_ashare/sector/sector_siphon.py`
- TDM-E-L2-05-1（水温档推导）→ `src/zephyr/signal_ashare/sentiment/sentiment_cycle.py`
- TDM-E-L2-05-2（信号响应三件套）→ `src/zephyr/signal_ashare/sector/sector_gate.py`
- TDM-E-L2-06（板块个股传导）→ `src/zephyr/signal_ashare/core/sector_conduction.py`
- TDM-E-L2-06-1（三级放行门槛）→ `src/zephyr/signal_ashare/sector/sector_gate.py`
- TDM-E-L2-06-2（龙头识别定位）→ `src/zephyr/signal_ashare/sector/sector_leader.py`
- TDM-E-L2-06-3（强度加权传导）→ `src/zephyr/signal_ashare/core/sector_conduction.py`
- TDM-E-L2-07（回踩质量分级）→ `src/zephyr/signal_ashare/sector/sector_pullback.py`
- TDM-E-L2-07-1（回踩ABC判定）→ `src/zephyr/signal_ashare/sector/sector_pullback.py`
- TDM-E-L2-08（板块生命周期判定）→ `src/zephyr/signal_ashare/sector/sector_momentum_persistence.py`
- TDM-E-L2-09（催化剂识别）→ `src/zephyr/signal_ashare/screening/event_driven_screener.py`
- TDM-E-L2-09-1（事件图谱传导）→ `src/zephyr/intelligence/news_chain_node_linker.py`
- TDM-E-L2-09-2（冲击标的生成）→ `src/zephyr/intelligence/chain_impact_resolver.py`
- TDM-E-L2-10（同源补涨比价）→ `src/zephyr/signal_ashare/supply_chain_momentum.py`
- TDM-E-L3-01（Universe构建与剔除）→ `src/zephyr/data/instrument_master.py`
- TDM-E-L3-03-2（波段池5分制）→ `src/zephyr/signal_ashare/quant_short_term_strength_engine.py`
- TDM-E-L3-03-3（双策略合流体检）→ `src/zephyr/signal_fundamental/router/signal_conflict_resolver.py`
- TDM-E-L3-05（顺位排序）→ `src/zephyr/signal_fundamental/selection_confidence.py`
- TDM-E-L3-06（环境开关）→ `src/zephyr/signal_ashare/core/environment_switch.py`
- TDM-E-L3-07-1（打板选股链）→ `src/zephyr/pf_core/strategies/daban_sleeve_strategy.py`
- TDM-E-L3-07-2（多因子打分链）→ `src/zephyr/factor/analysis/multifactor_synthesis.py`
- TDM-E-L3-07-3（其余sleeve选股链）→ `src/zephyr/pf_core/strategies/event_driven_sleeve_strategy.py`
- TDM-E-L3-08（候选池输出）→ `src/zephyr/signal_ashare/core/candidate_pool_aggregator.py`
- TDM-E-L3-09（股票池分层维护）→ `src/zephyr/signal_ashare/core/pool_tier_maintenance.py`
- TDM-E-L3-10（可交易性预检）→ `src/zephyr/signal_ashare/tradability_preflight.py`
- TDM-E-L3-11-1（竞价选股）→ `src/zephyr/signal_ashare/auction_microstructure_analyzer.py`
- TDM-E-L3-11-2（盘中涨速异动扫描）→ `src/zephyr/signal_ashare/intraday_t0/intraday_volume_orderflow.py`
- TDM-E-L3-12-1（个股资金面分析）→ `src/zephyr/signal_ashare/capital_flow_pattern_analyzer.py`
- TDM-E-L3-12-2（龙虎榜席位追踪）→ `src/zephyr/signal_ashare/limit_up/seat_pattern_analyzer.py`
- TDM-E-L4-02（买入时序）→ `src/zephyr/plan_engine/closing_session_decision.py`
- TDM-E-L4-03（价格锚定）→ `src/zephyr/ex_core/pricing_policy.py`
- TDM-E-L4-04（资金分配多标的）→ `src/zephyr/signal_fundamental/capital/capital_allocator.py`
- TDM-E-L4-06（执行算法）→ `src/zephyr/ex_sor/core/algo_execution_selector.py`
- TDM-E-L4-07（条件触发队列）→ `src/zephyr/ex_core/local_order_queue.py`
- TDM-E-L4-08（突破失败降级）→ `src/zephyr/sell_decision/core/breakout_failure_detector.py`
- TDM-E-L4-09（执行硬约束）→ `src/zephyr/ex_core/price_cage.py`
- TDM-E-L4-14（执行成本反馈与选型回写）→ `src/zephyr/ex_sor/services/execution_quality_scorer.py`
- TDM-P-P1-01（持仓对账与台账快照）→ `src/zephyr/position/core/position_state_machine.py`
- TDM-P-P1-03（买入逻辑存活判定）→ `src/zephyr/plan_engine/thesis_survival.py`
- TDM-P-P1-05（组合级持仓体检）→ `src/zephyr/position/core/position_drift_monitor.py`
- TDM-P-P2-01（做T资格与成本前置）→ `src/zephyr/position/core/t1_sellable.py`
- TDM-P-P2-02（做T策略调度）→ `src/zephyr/sell_decision/core/t_trade_coordinator.py`
- TDM-P-P2-04（减仓与再平衡）→ `src/zephyr/position/core/rebalance_engine.py`
- TDM-P-P3-01（加仓资格门）→ `src/zephyr/position/core/pyramiding_rules.py`
- TDM-P-P3-02（金字塔加仓规则）→ `src/zephyr/position/core/pyramiding_rules.py`
- TDM-P-P3-04（加仓时点与执行）→ `src/zephyr/position/core/position_limit_enforcer.py`
- TDM-X-R1（应急保命）→ `src/zephyr/security/access_control/kill_switch.py`
- TDM-X-R1-01（熔断分级判定）→ `src/zephyr/risk/core/drawdown_state_machine.py`
- TDM-X-R1-03（护盘资产定向加仓白名单）→ `src/zephyr/position/core/defensive_asset_whitelist.py`
- TDM-X-S1-01（信号收集与六桶分类）→ `src/zephyr/sell_decision/core/sell_signal_collector.py`
- TDM-X-S1-03（止盈族判定）→ `src/zephyr/sell_decision/core/take_profit_strategy.py`
- TDM-X-S1-04（破位与情绪退潮信号）→ `src/zephyr/sell_decision/core/breakout_failure_detector.py`
- TDM-X-S1-06（强制清仓绕过通道）→ `src/zephyr/trading/strategy_abnormal_exit_orchestrator.py`
- TDM-X-S2-01（执行方式路由）→ `src/zephyr/sell_decision/core/sell_execution_planner.py`
- TDM-X-S2-02（T+1与涨跌停约束）→ `src/zephyr/position/core/t1_sellable.py`
- TDM-X-S2-03（执行时段路由）→ `src/zephyr/ex_sor/core/sell_session_router.py`
- TDM-X-S2-04（本地条件单管理）→ `src/zephyr/ex_core/local_order_queue.py`
- TDM-X-S2-06（卖出闭环与退出效率）→ `src/zephyr/sell_decision/core/sell_execution_quality_tracker.py`
- TDM-F-C2-01（目标聚合与净额轧平）→ `src/zephyr/position/core/firm_risk_aggregator.py`
- TDM-F-C2-02（组合约束栈）→ `src/zephyr/position/core/firm_risk_aggregator.py`
- TDM-F-C2-03（相关性聚类与cluster上限）→ `src/zephyr/position/core/correlation_regime_monitor.py`
- TDM-F-C2-04（budget变动三级升级）→ `src/zephyr/position/core/budget_change_handler.py`
- TDM-F-C3-01（多维归因引擎）→ `src/zephyr/pf_core/core/performance_attribution_engine.py`
- TDM-F-C3-02（升降级管线与退役评审）→ `src/zephyr/factor/governance/lifecycle_state_machine.py`
- TDM-F-C3-05（可靠度养成与信号健康）→ `src/zephyr/signal_quality/signal_degradation_monitor.py`

## 裁定
- 缺口节点逐条判定：属"同一模块多节点复用"或"配置/数据面节点"者不单独立册（由被复用模块的审查覆盖）；
- 属真实遗漏算法模块者登记为补册对象（见下）。

### L19 · 缺口清单（逐个裁定）

## 缺口清单（逐个裁定）
- TDM-E-L0-01（计划生成）→ `src/zephyr/plan_engine/daily_trade_plan.py`
- TDM-E-L0-02（偏离监控与修订）→ `src/zephyr/plan_engine/plan_deviation_monitor.py`
- TDM-E-L0-03（收盘复盘与明日边界）→ `src/zephyr/plan_engine/tomorrow_boundary_planner.py`
- TDM-E-L0-04（明日情绪盘中滚动预测）→ `src/zephyr/plan_engine/intraday_tomorrow_forecast.py`
- TDM-E-L1-S1（大盘指数传感器）→ `src/zephyr/regime/features/index_sensor.py`
- TDM-E-L1-S2（市场内部结构传感器）→ `src/zephyr/signal_ashare/limit_up/limit_up_followthrough.py`
- TDM-E-L1-S3（赚钱效应传感器）→ `src/zephyr/signal_ashare/limit_up/lhb_premium_analyzer.py`
- TDM-E-L1-S0（宏观环境传感器）→ `src/zephyr/alt_data/policy_expectation_analyzer.py`
- TDM-E-L1-S0-1（新闻情绪语义分析）→ `src/zephyr/intelligence/news_sentiment_analyzer.py`
- TDM-E-L2-01-1（结构强度评估）→ `src/zephyr/signal_ashare/sector/sector_analyzer.py`
- TDM-E-L2-01-2（动量活跃度排名）→ `src/zephyr/data/sector_ranking_engine.py`
- TDM-E-L2-01-3（多周期动量加权）→ `src/zephyr/signal_ashare/sector/sector_momentum.py`
- TDM-E-L2-01-4（板块资金流聚合）→ `src/zephyr/signal_ashare/sector/sector_breadth.py`
- TDM-E-L2-02（轮动序列追踪）→ `src/zephyr/signal_ashare/sector/sector_divergence.py`
- TDM-E-L2-02-1（RRG 轮动序列）→ `src/zephyr/signal_ashare/sector/sector_rrg.py`
- TDM-E-L2-02-2（单板块轮动预警）→ `src/zephyr/signal_ashare/sector/sector_analyzer.py`
- TDM-E-L2-03（调整周期进度）→ `src/zephyr/signal_ashare/sector/sector_adjustment.py`
- TDM-E-L2-03-1（扩散指标进度追踪）→ `src/zephyr/signal_ashare/adjustment_cycle_tracker.py`
- TDM-E-L2-04（板块级市场状态）→ `src/zephyr/signal_ashare/core/sector_ecology_judge.py`
- TDM-E-L2-04-1（轮动状态五分类）→ `src/zephyr/signal_ashare/sector/sector_rotation_state.py`
- TDM-E-L2-04-2（虹吸态识别）→ `src/zephyr/signal_ashare/sector/sector_siphon.py`
- TDM-E-L2-05-1（水温档推导）→ `src/zephyr/signal_ashare/sentiment/sentiment_cycle.py`
- TDM-E-L2-05-2（信号响应三件套）→ `src/zephyr/signal_ashare/sector/sector_gate.py`
- TDM-E-L2-06（板块个股传导）→ `src/zephyr/signal_ashare/core/sector_conduction.py`
- TDM-E-L2-06-1（三级放行门槛）→ `src/zephyr/signal_ashare/sector/sector_gate.py`
- TDM-E-L2-06-2（龙头识别定位）→ `src/zephyr/signal_ashare/sector/sector_leader.py`
- TDM-E-L2-06-3（强度加权传导）→ `src/zephyr/signal_ashare/core/sector_conduction.py`
- TDM-E-L2-07（回踩质量分级）→ `src/zephyr/signal_ashare/sector/sector_pullback.py`
- TDM-E-L2-07-1（回踩ABC判定）→ `src/zephyr/signal_ashare/sector/sector_pullback.py`
- TDM-E-L2-08（板块生命周期判定）→ `src/zephyr/signal_ashare/sector/sector_momentum_persistence.py`
- TDM-E-L2-09（催化剂识别）→ `src/zephyr/signal_ashare/screening/event_driven_screener.py`
- TDM-E-L2-09-1（事件图谱传导）→ `src/zephyr/intelligence/news_chain_node_linker.py`
- TDM-E-L2-09-2（冲击标的生成）→ `src/zephyr/intelligence/chain_impact_resolver.py`
- TDM-E-L2-10（同源补涨比价）→ `src/zephyr/signal_ashare/supply_chain_momentum.py`
- TDM-E-L3-01（Universe构建与剔除）→ `src/zephyr/data/instrument_master.py`
- TDM-E-L3-03-2（波段池5分制）→ `src/zephyr/signal_ashare/quant_short_term_strength_engine.py`
- TDM-E-L3-03-3（双策略合流体检）→ `src/zephyr/signal_fundamental/router/signal_conflict_resolver.py`
- TDM-E-L3-05（顺位排序）→ `src/zephyr/signal_fundamental/selection_confidence.py`
- TDM-E-L3-06（环境开关）→ `src/zephyr/signal_ashare/core/environment_switch.py`
- TDM-E-L3-07-1（打板选股链）→ `src/zephyr/pf_core/strategies/daban_sleeve_strategy.py`
- TDM-E-L3-07-2（多因子打分链）→ `src/zephyr/factor/analysis/multifactor_synthesis.py`
- TDM-E-L3-07-3（其余sleeve选股链）→ `src/zephyr/pf_core/strategies/event_driven_sleeve_strategy.py`
- TDM-E-L3-08（候选池输出）→ `src/zephyr/signal_ashare/core/candidate_pool_aggregator.py`
- TDM-E-L3-09（股票池分层维护）→ `src/zephyr/signal_ashare/core/pool_tier_maintenance.py`
- TDM-E-L3-10（可交易性预检）→ `src/zephyr/signal_ashare/tradability_preflight.py`
- TDM-E-L3-11-1（竞价选股）→ `src/zephyr/signal_ashare/auction_microstructure_analyzer.py`
- TDM-E-L3-11-2（盘中涨速异动扫描）→ `src/zephyr/signal_ashare/intraday_t0/intraday_volume_orderflow.py`
- TDM-E-L3-12-1（个股资金面分析）→ `src/zephyr/signal_ashare/capital_flow_pattern_analyzer.py`
- TDM-E-L3-12-2（龙虎榜席位追踪）→ `src/zephyr/signal_ashare/limit_up/seat_pattern_analyzer.py`
- TDM-E-L4-02（买入时序）→ `src/zephyr/plan_engine/closing_session_decision.py`
- TDM-E-L4-03（价格锚定）→ `src/zephyr/ex_core/pricing_policy.py`
- TDM-E-L4-04（资金分配多标的）→ `src/zephyr/signal_fundamental/capital/capital_allocator.py`
- TDM-E-L4-06（执行算法）→ `src/zephyr/ex_sor/core/algo_execution_selector.py`
- TDM-E-L4-07（条件触发队列）→ `src/zephyr/ex_core/local_order_queue.py`
- TDM-E-L4-08（突破失败降级）→ `src/zephyr/sell_decision/core/breakout_failure_detector.py`
- TDM-E-L4-09（执行硬约束）→ `src/zephyr/ex_core/price_cage.py`
- TDM-E-L4-14（执行成本反馈与选型回写）→ `src/zephyr/ex_sor/services/execution_quality_scorer.py`
- TDM-P-P1-01（持仓对账与台账快照）→ `src/zephyr/position/core/position_state_machine.py`
- TDM-P-P1-03（买入逻辑存活判定）→ `src/zephyr/plan_engine/thesis_survival.py`
- TDM-P-P1-05（组合级持仓体检）→ `src/zephyr/position/core/position_drift_monitor.py`
- TDM-P-P2-01（做T资格与成本前置）→ `src/zephyr/position/core/t1_sellable.py`
- TDM-P-P2-02（做T策略调度）→ `src/zephyr/sell_decision/core/t_trade_coordinator.py`
- TDM-P-P2-04（减仓与再平衡）→ `src/zephyr/position/core/rebalance_engine.py`
- TDM-P-P3-01（加仓资格门）→ `src/zephyr/position/core/pyramiding_rules.py`
- TDM-P-P3-02（金字塔加仓规则）→ `src/zephyr/position/core/pyramiding_rules.py`
- TDM-P-P3-04（加仓时点与执行）→ `src/zephyr/position/core/position_limit_enforcer.py`
- TDM-X-R1（应急保命）→ `src/zephyr/security/access_control/kill_switch.py`
- TDM-X-R1-01（熔断分级判定）→ `src/zephyr/risk/core/drawdown_state_machine.py`
- TDM-X-R1-03（护盘资产定向加仓白名单）→ `src/zephyr/position/core/defensive_asset_whitelist.py`
- TDM-X-S1-01（信号收集与六桶分类）→ `src/zephyr/sell_decision/core/sell_signal_collector.py`
- TDM-X-S1-03（止盈族判定）→ `src/zephyr/sell_decision/core/take_profit_strategy.py`
- TDM-X-S1-04（破位与情绪退潮信号）→ `src/zephyr/sell_decision/core/breakout_failure_detector.py`
- TDM-X-S1-06（强制清仓绕过通道）→ `src/zephyr/trading/strategy_abnormal_exit_orchestrator.py`
- TDM-X-S2-01（执行方式路由）→ `src/zephyr/sell_decision/core/sell_execution_planner.py`
- TDM-X-S2-02（T+1与涨跌停约束）→ `src/zephyr/position/core/t1_sellable.py`
- TDM-X-S2-03（执行时段路由）→ `src/zephyr/ex_sor/core/sell_session_router.py`
- TDM-X-S2-04（本地条件单管理）→ `src/zephyr/ex_core/local_order_queue.py`
- TDM-X-S2-06（卖出闭环与退出效率）→ `src/zephyr/sell_decision/core/sell_execution_quality_tracker.py`
- TDM-F-C2-01（目标聚合与净额轧平）→ `src/zephyr/position/core/firm_risk_aggregator.py`
- TDM-F-C2-02（组合约束栈）→ `src/zephyr/position/core/firm_risk_aggregator.py`
- TDM-F-C2-03（相关性聚类与cluster上限）→ `src/zephyr/position/core/correlation_regime_monitor.py`
- TDM-F-C2-04（budget变动三级升级）→ `src/zephyr/position/core/budget_change_handler.py`
- TDM-F-C3-01（多维归因引擎）→ `src/zephyr/pf_core/core/performance_attribution_engine.py`
- TDM-F-C3-02（升降级管线与退役评审）→ `src/zephyr/factor/governance/lifecycle_state_machine.py`
- TDM-F-C3-05（可靠度养成与信号健康）→ `src/zephyr/signal_quality/signal_degradation_monitor.py`


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p01.md`

### L36 · 4 缺陷清单

## 4 缺陷清单
1. **P2 孤儿未接线**：模块自标 MATURITY=production、CONSUMERS 声称日循环环节④，但全仓生产代码零调用方，TDM 注册 strategy_mounts 为空。→ 现状：W0/W6 样本积累日循环实际不运转。建议：接线日循环调度或在 TDM 标注待接线。验证法：上述 grep。
2. P3 断供语义混叠（见轴 B）。
3. P3 fallback 双承载（见轴 D）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p03.md`

### L36 · 4 缺陷清单

## 4 缺陷清单
1. **P2 孤儿**：TDM-E-L0-02 环节注册在案但生产零装配，盘中偏差三重闸不运转。建议：盘中监控循环接线或标注待接线。验证法：grep。
2. P3 留痕 sink 静默丢失（低危，设计取舍）。
3. P3 naive clock 时区语义。
4. P3 "|z|>2σ" 措辞（文档失真非行为错）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p04.md`

### L38 · 4 缺陷清单

## 4 缺陷清单
1. **P2 箱体序无校验（退化/反转静默通过）**：违反"边界层坏=致命"自设不变量，坏边界顺传 P02 生成荒谬计划。建议：__post_init__ 或 compute_boundary 尾部断言 0<box_lower<no_add≤must_exit=box_upper。验证法：上述 python 单行。
2. P3 TypeError 契约外异常（close 类型校验缺失）。
3. P3 apply_revision 修后无序校验。
4. P3 默认 amplitude 0.03 板块口径未分。
5. P3 测试缺口：负 amplitude/str close/退化箱体均未覆盖。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p05.md`

### L37 · 4 缺陷清单

## 4 缺陷清单
1. **P2 Brier 基线口径潜伏缺陷**（0.5 vs 0.875/0.25，接线即发作）。建议：SourceCalibration 加 calibration_kind 字段或常量改名 BRIER_RANDOM_REF_BINARY 并断言输入口径。验证法：见轴 A。
2. **P2 孤儿（预警链双端悬空）**：本件无生产 import，其消费方 P03 亦是孤儿——TDM-E-L0-04→L0-02 降档预警链整体未运转。验证法：grep。
3. P3 幽灵函数引用 compute_calibration。
4. P3 假自检入口（--selfcheck 无验证力）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p06.md`

### L36 · 4 缺陷清单

## 4 缺陷清单
1. **P2 孤儿**：MATURITY=production 但全仓零调用，政策预期差信号链整体未运转（采集→打分→人工审核全悬空）。建议：装配接线或降级 maturity 标注。验证法：grep。
2. P3 审核队列无持久化（重启丢失）。
3. P3 llm_scorer 无 LSG 包装强制。
4. P3 环比口径/naive clock/tz 混存排序（低危组合）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p07.md`

### L38 · 4 缺陷清单

## 4 缺陷清单
1. **P2 LLM 断供静默中性**：建议 analyze_date_range 聚合侧对 method 分布设下限（如 llm_fallback 占比>50% 记 degraded 事件/日志 ERROR）。验证法：见轴 A。
2. **P2 跨空窗防抖漏报**：建议防抖改为"距上一触发窗口时长>window×k 才抑制"。验证法：见轴 A。
3. P3 SentimentEvent.symbols 恒空（docstring 称"MVP 从标题提取"未实现——文档先行）。
4. P3 persist 行 pos_n/neg_n 由 4dp 舍入 ratio 反推，极端计数可差 1（neutral_count 吸收，无害）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p08.md`

### L37 · 4 缺陷清单

## 4 缺陷清单
1. **P1 输出域错位（+2 不可达/稳牛=0）**：五档语义表与可实现分布不符——接线前必须修（补正向项如"收盘>MA20 且多头排列 +1"或改文档为 [-2,+1]）。爆炸半径=L1-AGG 温度计系统性偏保守。验证法：见轴 A 单行复现。
2. P2 孤儿（L1-S1 未接线，L1-AGG 无承接）。
3. P3 "年线级"术语错误。
4. P3 升序契约 in-band 不可校验。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p09.md`

### L37 · 4 缺陷清单

## 4 缺陷清单
1. **P2 NaN 静默中毒**：建议 _pool_stats 入口 isfinite 校验（NaN/Inf 跳过+notes）。验证法：单行复现见轴 A。
2. P3 limit_type 默认混板统计语义需 Owner 知情。
3. P3 日期倒置（prev>current）无显式校验/留痕。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p13.md`

### L37 · 4 缺陷清单

## 4 缺陷清单
1. P3 NaN 收盘价未防（建议 isfinite 过滤跳过+notes）。
2. P3 时间升序契约 in-band 不可验。
3. P3 权重常量与 spec 双承载（待回测校准时易漂移）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p14.md`

### L37 · 4 缺陷清单

## 4 缺陷清单
1. P3 NaN 成交额经 max(0.0, nan) 传播中毒（建议 `w if w==w and w>0 else 0.0` 或 isfinite 过滤）。验证法：单行 python。
2. P3 上游缺失率无观测（中性稀释静默面）。
3. P3 分档阈值不对称未见设计依据锚（spec §3.1① 之外无产物）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p15.md`

### L39 · 4 缺陷清单

## 4 缺陷清单
1. P3 disp 负收益语义洞。
2. P3 标定器混窗计数。
3. P3 炸板口径与 P09 双承载（容差差异）。
4. P3 一线游资白名单三处字面量承载。
5. P3 docstring 消费方声明过时。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p16.md`

### L38 · 4 缺陷清单

## 4 缺陷清单
1. P3 EMA 预热期简并点（全 LAGGING）无标注/裁剪——建议 compute_rrg_series 跳过前 long×2 点或输出 warmup 标记。验证法：见轴 A 单行。
2. P3 序列升序契约 in-band 不可验（族共性）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p17.md`

### L37 · 4 缺陷清单

## 4 缺陷清单
1. P3 expected_window≤0 缺省给满进度（建议 raise 或下限 clamp）。
2. P3 "主指标"措辞与权重配置矛盾（文档失真）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p18.md`

### L39 · 4 缺陷清单

## 4 缺陷清单
1. **P2 孤儿+MATURITY 失真**：production 标签与零调用方矛盾（建议降 testing 或接线）。验证法：grep。
2. P3 相位判定无迟滞（5% 门槛邻域抖动无确认机制，对比 P16 whipsaw 设计）。
3. P3 SQL .format 插值范式不一致（低危注入面）。
4. P3 双周期窗口首谷/首峰漏检。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p19.md`

### L36 · 4 缺陷清单

## 4 缺陷清单
1. P3 int() 截断绕过负值校验（建议 math.floor 后判负或拒非 int）。
2. P3 集中度输入口径未锁定（无真源模块锚）。
3. P3 "高潮"名词双件异义（本件 vs P20 判据不同源）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p20.md`

### L37 · 4 缺陷清单

## 4 缺陷清单
1. P3 NaN 透传面（top_n_hhi 不滤 NaN）。
2. P3 快轮动自适应不对称（CLIMAX 放宽、DISTRIBUTION 不放宽，意图需 Owner 确认）。
3. P3 输入校验显式弃守（调用方契约，当前链路成立）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p21.md`

### L37 · 4 缺陷清单

## 4 缺陷清单
1. P3 "~93% 分位"名义声明与相关 z 加权的实际分布不符（阈值语义应为裁量）。
2. P3 NaN 历史透传（z=NaN 侥幸不触发但 score 污染）。
3. P3 HHI 公式与 P15 双实现（漂移隐患）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p22.md`

### L39 · 4 缺陷清单

## 4 缺陷清单
1. **P2 兜底 confidence=1.0 语义伪造**：建议保留真实置信度另加 fallback 标记位（已有 fallback_triggered 字段，confidence 不该改写；或改 confidence=confidence_threshold 下界）。验证法：python 探针。
2. P3 北向断供无证据维降级留痕。
3. P3 999 魔数隶属度几何耦合。
4. P3 daban FERMENTING 两表仓位数值不一致（1.0 vs 0.7，语义有别需注释仲裁）。
5. P3 三同名枚举无防混机制。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p23.md`

### L37 · 4 缺陷清单

## 4 缺陷清单
1. P3 CRASH 阈值 1.01 语义倒置洞（score 越界脏值可放行——建议 CRASH 硬 return False 不走阈值）。
2. P3 retained_sectors 两形态语义分叉（易踩）。
3. P3 RRG 象限字面量跨文件硬耦合。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p24.md`

### L37 · 4 缺陷清单

## 4 缺陷清单
1. **P2 孤儿**（TDM-E-L2-06-3 未接线，与 P08/P18 同批未运转环节）。验证法：grep。
2. P3 锚点跳变面（6 分邻域强度量化敏感）。
3. P3 score 上界不设防（乘法传导保序，影响有限）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p26.md`

### L44 · 4 缺陷清单

## 4 缺陷清单

1. P1（接线期地雷，非现行 P1）：**零生产调用方孤儿**（checklist #8）。现状=三函数全仓无生产 import；影响=突破失败降级与买入优先级链（BM-BUY-04）规划中的上游缺位；建议=G05 选股引擎接线时以本件为唯一实现并补 NaN 入参防御；验证法=`grep -rn "grade_pullback" src/ --include="*.py"`（仅测试命中）。
2. P3：NaN 输入静默落 C 档（保守向）——建议接线期在入参处显式 reject；验证法=§2 A 轴命令。
3. P3：docstring 35-50% 下界与健康窗 3-10 日两处文档-代码漂移——建议修 docstring 或补下界检查；验证法=`classify_volume_pattern([0.8,0.3])`。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p29.md`

### L44 · 4 缺陷清单

## 4 缺陷清单

1. P3：置信度混源顺序依赖（candidates[0][4]）——同 norm 词 name/alias 混组时置信度随注入顺序漂移；建议=组内按 source 优先级取分或拆组；验证法=§2 A 轴对拍。
2. P3：同节点多 span 重复 hit 无去重约定，去重责任隐式落在 W5 消费方——建议头注补契约；验证法=同词两处文本观察。
3. P3：泛化词剔除阈值 MAX_CANDIDATES_PER_TERM=8 硬编码无校准记录——图谱扩链后可能结构性漏报真环节词；建议=接线统计后校准。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p30.md`

### L44 · 4 缺陷清单

## 4 缺陷清单

1. P3（文档化简化，接线期关注）：无向+全跳同向传导对"上游利好=下游成本利空"场景产生方向性误报——已声明 known simplification；建议=方向边细分期前，前端展示层对 hop≥1 标的加"传导方向=MVP 同向假设"标注；验证法=构造 supply 边+正向 polarity 观察下游标 direction=+1。
2. P3：多种子 visited 占位顺序影响 path 归属与置信度（:310-331）；影响轻微（同 hop 才可能）；建议=占位时保留高置信种子或文档声明；验证法=换序对拍。
3. P3：ig_edge 无 active 链过滤，依赖节点白名单间接防御——若未来引入"边级失效"（停用链但节点保留）会漏防；建议=加 chain 状态 JOIN 或留注释声明假设；验证法=§2 B 轴。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p31.md`

### L43 · 4 缺陷清单

## 4 缺陷清单

1. P2：**min_returns=6 与 lead=5 样本需求矛盾（默认配置最小样本必炸）**——现状=Config:152 允许 6、算法:265 要求 lead=5 时 n≥7；影响=按文档最小样本装配的调用方 evaluate() 必然异常（fail-closed 无资损但断功能）；建议=min_returns 下限改 7（或 lead 循环按 n 自适应截短）；验证法=`SupplyChainMomentumModel(links=[SupplyChainLink('UP','DN',0.5)], regressor=...).evaluate('DN', {'UP':[0.01]*6,'DN':[0.01]*6})` 复现 raise。
2. P1（接线期）：零生产调用方孤儿+MATURITY=production 虚标（checklist #8/V06 同族）；验证法=§2 C 轴 grep。
3. P3：lead_weights 和=3.0 未归一+score [-1,1] 截断饱和；P3：收益序列方向（尾部=最新）无机械校验，倒序注入静默语义反转。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p32.md`

### L43 · 4 缺陷清单

## 4 缺陷清单

1. P2（接线期必修）：board→min_order_unit 一刀切映射对 star 板 ETF（588xxx 100 股申报）派生错误值→下单废单；建议=映射键改 (board, security_type) 二维；验证法=`normalize_instrument_row({...,'board':'star','security_type':'etf'})` 观察 200。
2. P1（接线期）：零生产调用方孤儿（头注诚实 declared"接线待排期"）；Universe 构建/剔除本体（筛选规则）尚无承载文件——TDM 节点名实差距需接线层补齐；验证法=§2 C 轴 grep。
3. P3：security_type 枚举零校验 vs ERROR_CONTRACT"非法枚举→ValueError"名实差；P3：DDL `updated_at DateTime` 无时区无精度（全仓 data 域 DDL 同族模式，与 RULE-SCHEMA-TZ"DateTime64(3)+显式时区"口径存在家族级差距——宜族级统一裁定非单件修）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p34.md`

### L41 · 4 缺陷清单

## 4 缺陷清单

1. P1（接线期）：零生产调用方孤儿（上游 router 同批未接线=整族待装配）；DEFER 输出无下游承载语义——接线裁定必答项；验证法=§2 C 轴 grep。
2. P3：单方向组直通绕过 R1 风险否决（kind/direction 配错的脆弱面）——建议 R1 提到分组后无条件执行（RISK∧conf≥门槛即 REJECT 无论方向组合）；验证法=§2 A 轴构造。
3. P3：MATURITY=production 与未接线现实不符（V06/P28 同族标签失实案）；建议改 testing。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p35.md`

### L42 · 4 缺陷清单

## 4 缺陷清单

1. P2：**NaN fail-open 三函数洞（实测 1.0/1.0/0.5）+ 与 filter 函数 NaN=拒绝的族内语义矛盾**——建议统一 NaN→0.0（宁勿宽）或 raise；验证法：`compute_event_confidence(float('nan'),0.0)`→1.0、`compute_daban_confidence(float('nan'))`→1.0、`compute_multifactor_confidence([float('nan')]*3)`→0.5。
2. P2：PEAD 3% 阈值与 P28 双处承载+事件类型两套分类法（4 键 vs 6 枚举）未对齐——接线时统一真源（建议 P28 为真源，本件 import）；验证法=对照两文件常量。
3. P1（接线期）：零生产调用方孤儿；验证法=§2 C 轴 grep。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p36.md`

### L42 · 4 缺陷清单

## 4 缺陷清单

1. P1（接线期）：开关查表主函数生产零调用（半孤儿：词表承载已接线、动作表未接线）；全链级开关接线时属高风险面（错值=整链停开）建议 Owner 门位；验证法=§2 C 轴 grep。
2. P3：状态词表三套并存（六段/五阶段/regime 四态）+两处映射位点——建议映射收拢单一真源模块；验证法=§2 D 轴 grep。
3. P3：8000 亿实证断言无仓内 artifact 锚（checklist #15 关键数字无底层产物）——补回测证据或降级"经验值"；验证法=§2 F 轴 grep。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p37.md`

### L42 · 4 缺陷清单

## 4 缺陷清单

1. P2：**payload 构建 NaN 穿透（实测三字段）×P33 NaN 评分洞=复合静默剔除链**——建议 `row_to_engine_payload` 复用 `_maybe_positive`/新增 `_maybe_finite` 统一清洗（NaN→省略键交引擎默认），并在剔除时 debug 留痕；验证法=本班次实测一行（§2 A 轴）。
2. P2（跨lan）：上游 daban_load 生产节奏与日频消费失配（TF07 已挂起晨报置顶）——本模块仅事后 WARNING 无升级机制；建议与 TF07 合并裁定（生产侧治本优先）；验证法=对照 TF07 报告。
3. P3：决策词表中文字符串硬编码查表（:493）无枚举保护；P3：占位置信度=权重和（声明诚实但语义弱）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p38.md`

### L43 · 4 缺陷清单

## 4 缺陷清单

1. P2：回归法三重隐式假设未文档化（fillna(0)=中性、无截距、in-sample 拟合即应用）——下游 sleeve 直接消费即过拟合信号；建议=docstring 声明+应用面板与拟合面板分离（滚动回归）；验证法=阅 :117-125。
2. P2（链路缺口）：IC 加权法为默认方法（config default ic_weighted）但 IC 生产端 ic_ir_calc 生产零接线——**默认方法实际跑在"调用方每次手工传 ic_weights"假设上，缺传即静默等权兜底**（:149 kwargs.get("ic_weights",{}) 空 dict→无有效权重→等权+warning）；验证法=不传 ic_weights 观察 warning。
3. P3：三方法 NaN 语义不一致（跳过/传播/置零）；P3：头注 [CONSUMERS] 空 vs 实际两处消费（登记失实，方向=漏登非虚标）。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p39.md`

### L41 · 4 缺陷清单

## 4 缺陷清单

1. P2：**依赖引擎 event_score=design 态而 sleeve 生产路由已活**（#ARCH-NLP-PIPELINE-001 未闭环）——评分质量无背书进组合面板；建议=composer 侧对该成员加"依赖未闭环"降权/披露标记，或 NLP 管道闭环前排期；验证法=对照登记项与 composer 成员列表。
2. P3：与 P37/multifactor_sleeve 三份骨架复制（归一化/截顶/占位置信度）——登记 BaseSleeveMixin 合并建议（轴 D 整套重复实现条款）；验证法=三文件 diff。
3. P3：NaN score 静默出局无日志；异动确认降级放行无日志——两处补 debug/warning。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p40.md`

### L41 · 4 缺陷清单

## 4 缺陷清单

1. P2（接线期必修）：跨 sleeve rank_score 不可比混排（自declared 调用方统一而统一承载无人认领）——建议接线裁定时定唯一标准化点（如各 sleeve 出口 z-score 化或百分位化后再入池）；验证法=§2 A 轴构造两源候选对拍。
2. P1（接线期）：零生产调用方孤儿（design 态声明诚实）；验证法=§2 C 轴 grep。
3. P3：sleeve 标签词表（本件枚举）与 sleeve 策略 id（daban-sleeve 等）两套命名缺映射层；验证法=对照 strategies/__init__。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p42.md`

### L41 · 4 缺陷清单

## 4 缺陷清单

1. P2（族级）：涨跌幅规则三处承载无唯一真源（本件 :68-73 最完整/P33 :469 硬编码 9.5%/P32 DDL 注释）——建议立真源裁定（本件为候选承载）并让 P33/P32 消费之；验证法=三文件对照 grep。
2. P1（接线期）：零生产调用方孤儿；permission/lot_cash 降级放行的下单层 L4-12 复检兜底同为待接线层——接线时须两件同步否则降级=裸放；验证法=§2 C 轴 grep+L4-12 路由核对。
3. P3：一字判定 OHLC 三值齐契约未文档化；默认路径（无意图价）检查强度=仅停牌+一字+数据缺失，未在 docstring 写明分层。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p44.md`

### L42 · 4 缺陷清单

## 4 缺陷清单

1. P2：NaN bars 无防御→三件套静默产出 NaN（`_require_bars` 只查负量不查 isfinite）；建议补 finite 校验对齐 ERROR_CONTRACT；验证法=含 NaN volume bars 实跑。
2. P1（接线期）：零生产调用方孤儿（三候选消费方均未接线）；验证法=§2 C 轴 grep。
3. P3：背离事件无 refractory 去重；bars 时间升序契约未文档化；一字板 delta=0 的 VPIN 制度性失真未声明。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p45.md`

### L42 · 4 缺陷清单

## 4 缺陷清单

1. P2：**阈值量纲失真（万元输入 vs 1.0 阈值≈零门槛）**——五形态判别退化为符号组合；建议归一化输入（占比/市值比）或按真实万元量级重标阈值；验证法=§2 A 轴构造命令。
2. P1（接线期）：字段级孤儿（分析器零实例化+下游字段恒"未知"）；MATURITY=production 虚标；验证法=§2 C 轴 grep。
3. P3：NaN→UNKNOWN 静默无日志；market_sentiment_score 死输入字段；序列时序契约未文档化。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p49.md`

### L41 · 4 缺陷清单

## 4 缺陷清单

1. P2：**CTR-P1-003 契约双 codegen 产物字段序漂移**（checklist #4 位置构造错位风险）——建议 codegen 收敛单产物+另一路径 re-export；验证法=§2 D 轴 diff。
2. P2：截顶不重归一欠部署（n<3 时 total<1.0 静默）——与 C01 同族模式，建议截顶后按比例重归一或显式披露欠部署比例；验证法=单信号 allocate 观察 total=0.4。
3. P1（接线期）：全链孤儿（上游 G01 stub+零专属测试+demo 唯一消费）；验证法=§2 C 轴 grep。
4. P3：confidence or 0.5 falsy 吞零；NaN 权重传播；风险平价代理量纲未声明；空信号 wall-clock 回测 PIT 破口；幂等键无冲突检测。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p50.md`

### L42 · 4 缺陷清单

## 4 缺陷清单

1. P2：**IS 绝对值口径把卖单有利偏差计为成本（docstring 方向式 vs 实现矛盾，ExecutionOutcome 无方向字段可体现）**——建议 outcome 加 side 字段并按 docstring 两式计算；验证法=§2 A 轴 SELL outcome 构造。
2. P1（接线期）：零生产调用方孤儿+[MATURITY] 虚标（依赖边两端互认未接线）；验证法=§2 C 轴 grep。
3. P3：fill_rate 二值化失真（声明在案）；审计列表无界增长；ADV 单位契约未文档化。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p51.md`

### L46 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] TDM-E-L4-07 module_ref 锚错位+真承载未接线**。现状：节点声明"触发器统一注册/tick 驱动/优先级风控>卖出>买入/队列积压降级批量"，module_ref 却指向订单间隔缓冲，真承载 trigger_registry.py 零生产消费方且节点未标红。影响：按图施工/按图审计者会把"已建成"误判，触发器编排实际全图无人注册无人触发。建议修法：module_ref 改指 `src/zephyr/trading/trigger_registry.py` 并将该节点补红节点标记（编排缺口），或把 local_order_queue 从该节点摘除另挂 X-S2-04 已挂节点。验证法：§2 轴 D 验证法。
2. **[P2] 生产孤儿空转**（checklist #8）。现状：队列被创建从不被喂单。建议修法：要么在 qmt 下单链路真实接线 enqueue，要么降级 MATURITY 并在 TDM 摘除在网叙事。验证法：§2 轴 C 验证法。
3. **[P2] FAILED 恒 0 监控盲区**。现状：状态机三态只走两态，health_check degraded 不可达。建议修法：重试达 max_attempts 时置 FAILED+health_check 反映。验证法：注入恒抛 mock 看 health_check.level。
4. **[P2] 无上限重试+无死信**。建议修法：max_attempts（如 5）+超限转 FAILED+error 上报；永久拒单异常类别直接终态。验证法：毒单剧本观察 attempts。
5. **[P2] 无持久化重启丢单**。建议修法：pending 落盘（.runtime/sessions 或 DB）+启动重载，或显式声明"仅进程内"并把 TDM 注释"落盘先于生效"改挂实际承载。验证法：重启丢单复现。
6. **[P3] LocalOrderQueueError 定义零 raise（错误契约死条目）；_send 锁外写共享状态**。验证法：grep LocalOrderQueueError 使用点为 0。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p52.md`

### L45 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] 孤儿死码+K≥3 强清链路双锚全断**（checklist #8）。现状：detector 零生产调用、collector 第⑧桶无人喂、X-S1-06 无 K≥3 输入、pf_alloc 链孤儿；TDM-E-L4-08 按在网口径书写且 header 冒充 production。影响：突破失败降级与强清保护在当前基线=纸面能力，"首仓失败不加仓/暂停批次"全不发生。建议修法：接线评审（collector ⑧喂入+X-S1-06 消费）前把节点补红+MATURITY 降 draft；或按 42 号编排批次正式接线。验证法：§2 轴 C 验证法。
2. **[P2] direction=REPLACE 占位语义地雷**。建议修法：SUCCESS 返回专用枚举（如 HOLD/None）或文档级铁律"direction 仅 FAILURE/FORCED_CLEAR 可执行"；补消费方契约测试。验证法：接线评审时 grep 消费方对 REPLACE 的分流。
3. **[P2] 挑战计数跨成功不重置+无收盘纪律**。建议修法：detect 增加 challenge_count 重置语义（成功清零或由调用方显式传 0 的文档铁律）；docstring 声明"仅许喂收盘确认价"。验证法：本次审查三连探针复现计数携带。
4. **[P3] 双锚口径分叉声明**：TDM 节点内显式标注两锚各自适用面（batch 切面用收盘 2 根版、单仓信号面用本 detector），防接线时混用。验证法：读 TDM 节点注释是否已分工。
5. **[P3] FAILURE 置信度与 SUCCESS 倒挂**：若 confidence 参与排序优先级需重新校准（或文档声明 confidence 不作排序键）。验证法：读公式对照 0.6<0.8。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p53.md`

### L44 · 4 缺陷清单

## 4 缺陷清单

1. **[P2] 反馈环断链+孤儿**（TDM 自我声明在案，本审查确认基线仍断）。建议修法：按 TDM 注释挂"接线随编排批次"，接线前 header CONSUMERS 行改为"计划消费方"；或先在盘后报告（MOD-EX-CORE 执行质量报告）侧消费起来形成最小闭环。验证法：grep 三连（§2 轴 C）。
2. **[P2] abs() 抹滑点方向**。建议修法：PRICE 维保留符号（score 对负滑点给满分或 1+bonus 封顶 1.0），COST/IMPACT 若上游契约保证非负则改 assert 非 null 而非 abs。验证法：本次探针命令复跑，修后 -30 与 +30 得分必须不同。
3. **[P2] 部分维度 overall 不可比**。建议修法：verdict 附 dimension_coverage（如 "2/4"），或 overall 仅在全覆盖时给出、部分覆盖返回 None+分维明细。验证法：time-only 探针复跑看 coverage 字段。
4. **[P3] TIME 300s 默认阈值与 180s 切片口径冲突**。建议修法：默认阈值改由 config/standards 或 CST 注入，并按父单/切片两级分开评。验证法：对照 config 注入后跑典型 TWAP 父单。
5. **[P3] history 无界+score_from_results 名不副实**。建议修法：history 加 maxlen 或落 DB；score_from_results 改收 SlippageResult/TransactionCostResult 强类型。验证法：读签名 diff。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p54.md`

### L46 · 4 缺陷清单

## 4 缺陷清单

1. **[P2] industry_map 缺省→组合被 UNKNOWN 伪扇区静默砍到 30%**（默认参数即触发）。建议修法：industry_map 缺失时跳过行业绝对帽并标 benchmark_missing（与偏离帽退化路径同款）或直接 raise；UNKNOWN 永不参与 absolute_cap。验证法：本报告 30×2% 探针。
2. **[P2] 净额截断双语义不对称+负权重穿透**。建议修法：明确 tp 权重语义（target vs delta）写入 docstring 并统一两分支——若 target：所有 net<0 → max(0,net)（不留 holdings 复合）；若 delta：统一 final=max(0,holdings+net)；负值绝不穿透出 pre_kelly_aggregate。验证法：三连探针（本次已实测 -0.05 穿透）。
3. **[P2] 孤儿+C2-01 运行时语义（TTL/批量/分摊/防自成交）无承载、C2-02 三层约束无承载**。建议修法：接线批次立项或把 TDM 节点改红+把"净差单下发/分摊"语义迁往未来编排件节点；C2-02 缺层在约束栈施工批次补齐。验证法：grep（§2 轴 C/D）。
4. **[P3] idempotency_key 时间戳不幂等+naive datetime**。建议修法：key 由输入内容 hash 或调用方传入；datetime 带 tz。验证法：同输入两次调用 key 应相同。
5. **[P3] risk_limits["total_exposure_cap"] 死配置+total_budget<=0 静默清零**。建议修法：删除死配置或接通；total_budget<=0 raise BudgetChangeError 类异常。验证法：改配置重跑/零预算探针。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p55.md`

### L43 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] 节点六项声明语义（层次聚类/ρ0.70 合并/ρ0.85 禁新仓/cluster≤5%/月度再聚类/危机压测）全仓无承载**，模块只交付 avg 三档底座且阈值不同轴。影响：F-C2-03 在图上表现为已建风控，实际组合扎堆保护为零；F-C2-02 约束栈的"相关性层"同样落空（联动 P54 轴 D）。建议修法：施工批次补聚类+簇帽（对齐 TDM D77 阈值），或节点改红并把声明收敛到"avg 三档底座已建、簇层未建"。验证法：§2 轴 D grep 打勾表。
2. **[P2] 孤儿死码**（header production 不实）。建议修法：接线（MOD-POS-013 真实消费或 F-C2-01 聚合链）前降 draft+节点补红。验证法：grep。
3. **[P3] avg 单轴判定的扎堆钝感**。建议修法：regime 判定引入 max_pair/簇均值第二轴（HIGH 触发条件加 max_pair≥0.85 旁路）。验证法：5×0.95+20×0.05 构造探针。
4. **[P3] 60 日滚动窗语义无校验承载**。建议修法：入口加窗口长度参数与最小样本校验（对齐 MOD-POS-011 风格）。验证法：短窗探针。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p56.md`

### L45 · 4 缺陷清单

## 4 缺陷清单

1. **[P2] 日间累计防抖失效（三日 -4% 连降全吞）**——代码 vs 自身 docstring vs TDM 三方矛盾，fail-open 方向。建议修法：累计不按日重置（或另设 N 日滚动窗累计变量），重置仅发生在升级触发或 budget 回升后；补多日连降回归测试。验证法：本报告三日探针。
2. **[P2] TDM 分档语义（10%/25% 跌幅档）与代码时间升级制互斥**。建议修法：Owner 裁定口径——保留时间升级制则改写 TDM algo_note；保留分档制则代码补跌幅分档映射（改动大）。裁定前 TDM 节点应注记两套口径不可混读。验证法：§2 轴 D 对照法。
3. **[P2] 继承性孤儿（接线适配器就绪、编排未接）**。建议修法：随 G15→G14 编排件立项接线（TDM 已挂装配排期），接线前本节点维持"已建未接"声明。验证法：grep AllocationOrchestrator 生产实例化。
4. **[P3] check_convergence 持续性按调用计数**。建议修法：加 last_check_date 日历日守卫。验证法：同日两调探针。
5. **[P3] E-POS-41 from_tier 硬编码失真+负 budget 边界松+theledgermind 5% 引证无锚**。建议修法：from_tier 记录真实前态；budget 校验；引证补锚或降格。验证法：各自探针/查证。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p57.md`

### L47 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] TDM-F-C3-01 七项声明语义（做T/持仓二分、IS 三分解、D84 五条必改）零代码承载**，图上归因汇聚节点与实际交付（教材 Brinson 骨架）差距巨大。建议修法：节点标注"骨架已建/七项缺口清单挂施工批次"（TDM 注释已有 D84 声明，需升级为显式缺口清单+红标），或收敛节点声明。验证法：§2 轴 D grep。
2. **[P2] 链顶孤儿**（引擎+包装层双孤儿）。建议修法：接报告域消费或声明退役候补（规范预算净零）。验证法：grep。
3. **[P2] 多期朴素算术求和**。建议修法：接 Carino 平滑或几何链接（对齐 TDM-D84 TWR 声明）；短期保留则 docstring 标注适用上限（如 ≤3 期）。验证法：两期复利探针。
4. **[P2] total_return 字段语义误导**。建议修法：改名 net_excess_return 或报告附 benchmark_return 行并文档铁律。验证法：读契约+消费方审计。
5. **[P3] 权重和不校验（B-F 口径前置）/风险结果丢弃/冷启动降级误判/负相关拥挤误判/异常统一降级**。建议修法：各一行级修复（sum 校验、接结果或删调用、baseline=0 单独分支、拥挤改只看正相关、异常分类）。验证法：各自探针。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p58.md`

### L43 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] TDM-F-C3-02 module_ref 语义错位+sleeve 评审管线整体未施工**。现状：节点锚定因子研发 FSM，sleeve 升降级（composite/THD-RETIRE/DSR/减半冻结/verdict）全仓无承载；节点自注红节点但 module_ref 给人"骨架已建"错觉。建议修法：module_ref 置空或改挂真实的编排待建占位；节点保留红标并把 D86 四条实操（composite 公式/观察名单/滞回带/fail-safe）列为施工清单。验证法：§2 轴 D 并排读法。
2. **[P3] 注释与边表不符（"任何非终态可回退 research"未实现）**。建议修法：改注释或补边（若 PRODUCTion 回退确无需求则明示单向终局语义）。验证法：非法转换探针。
3. **[P3] YAML 状态可配置×转换硬编码的分裂真源+register 全量吞异常**。建议修法：_build_config 后加"转换边引用的状态必须∈states"断言；register 只吞"已注册"异常类、其他上抛。验证法：改配置探针/预注册冲突探针。
4. **[P3] 灰度→实盘无审批守卫挂点**。建议修法：转换加 guard 回调参数（对齐 ai_autonomy: auto 的门位要求），或文档声明 gate 在调用方。验证法：读基类签名。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p59.md`

### L45 · 4 缺陷清单

## 4 缺陷清单

1. **[P2] 孤儿+节点能力缺口量化存档**（红节点自认，本条主要为收口提供打勾表）。建议修法：装配批次接线（alert_router 接 alert 路由、mark_sink 接 L1-AGG 降权真源）；接线前 MATURITY 降 draft。验证法：grep。
2. **[P3] 告警无去重（降级期每次 evaluate 重发）**。建议修法：alert 同样加 `prev is not report.level` 守卫或周期性心跳节流。验证法：三连 evaluate 计数探针。
3. **[P3] 降权二值无梯度（MILD=SEVERE 砍半）**。建议修法：weight_hint 按 level 映射（MILD 0.8/MODERATE 0.5/SEVERE 0.2 之类）或文档声明有意保守。验证法：两级对比探针。
4. **[P3] 小样本 decay 噪声+乱序无守卫**。建议修法：min_samples 提示置信度（report 附 sample_size 已有，判定阈值随样本量收缩）；observe 加时间戳单调断言或排序。验证法：蒙特卡洛/倒序探针。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p60.md`

### L45 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] 节点对账三步+富台账五字段零承载、module_ref 错位、真承载通道双轨未分工**。建议修法：TDM-P-P1-01 拆注两个承载面（盘前快照对账=93 号 playbook/position_reconciler 候选；状态机态=本模块），或补齐 Stock.csv 盘前对账件；本模块在接线前降 draft。验证法：§2 轴 D grep。
2. **[P2] FSM 孤儿**（状态根无人挂）。建议修法：随仓位裁决中心（position_adjudication_center）接线；接线前 MATURITY 降 draft。验证法：grep。
3. **[P2] OBSERVING 15min 确认窗只设不查**。建议修法：增加 check_observing_timeout(now) 业务方法（超时→自动 confirm=True 转 REDUCING 或告警），并挂转移完备性测试。验证法：超时探针。
4. **[P3] activate() 旁路灰度/can_buy 冷却盲区/自然日 vs 交易日混用/reset 事件前态丢失**。建议修法：activate 加 config.allow_skip_graduation 开关默认 False；can_buy 收紧含 CLOSED+冷却；注释显式声明日历口径；reset 事件带真实前态。验证法：各自探针。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p61.md`

### L43 · 4 缺陷清单

## 4 缺陷清单

1. **[P2] 孤儿（design 态）+DEAD 出边无处可达**。建议修法：随 P1-06 动作清单/体检编排接线；接线前维持 design 声明（勿升 production）。验证法：grep。
2. **[P3] 事件 decay 字段语义双关（兑现度 vs 衰减度方向相反）**。建议修法：字段改名 event_realized_ratio 或注释加"必须喂兑现度（0=未兑现，1=完全兑现）"铁律+测试锁定。验证法：0.2 反转探针。
3. **[P3] 漂移量纲未定义+证据无时效+单理由假设未声明**。建议修法：蓝图补三行契约（drift 计算式/observed_at 必填/多理由仓=调用方逐理由分别调用取最严）。验证法：读蓝图 diff。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p62.md`

### L43 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] 节点三查（20% 集中/25% 越带/题材扎堆）零承载+模块 ±3% 绝对带与 25% 相对带未按 5/25 双腿整合**。建议修法：施工批次补三查中缺的两查（题材扎堆依赖 industry_map，可与 P55 聚类合并立项）；单标的告警加相对带条件。验证法：§2 轴 D grep+5/25 双腿探针。
2. **[P2] actual 独有持仓无标的级告警（清单遗忘仓盲区）**。建议修法：遍历 `set(target) | set(actual)`，actual-only 视 target=0 判漂移。验证法：本报告 KEPT 探针。
3. **[P2] 孤儿死码**（header production 不实；P1-05 节点体检在图上持续、码上无人跑）。建议修法：接线（P1-06 体检编排或盘前批）或降 draft+节点补红。验证法：grep。
4. **[P3] 无心跳事件+权重和未校验**。建议修法：定期 NONE 级心跳或由装配层监控 check 调用时效；总和>1+ε 显式拒绝。验证法：停调探针/总和探针。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p63.md`

### L41 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] 资格三道门/五道门/时段矩阵/量能闸门/风控层全仓零承载**——critical 级节点（P2-01）在图上承担"做T 准入"决策，实际唯一在网产出是 T 分析页的可卖权重展示。建议修法：节点补红（编排缺口扩注"资格门零实现"）+把 D111 成本门与 D58 时段矩阵列为做T 批次施工清单；或把 module_ref 改挂真实的做T 规划件（P64）并另立"资格门"空环节点。验证法：§2 轴 D grep。
2. **[P2] T+1 供数口径无校验锚**。建议修法：供数方接口加"昨日收盘快照"来源标记或对账断言（今日买入集合与昨仓集合交集检测）。验证法：混入今买的探针。
3. **[P3] 权重↔股数换算契约缺失**。建议修法：蓝图补一行换算责任声明（含整手对齐归执行层）。验证法：读消费链。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p64.md`

### L42 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] 三策略+仲裁+30% 帽零承载，节点语义=单信号规划器**。建议修法：节点声明收敛为"单标规划器已建（proposed）/三策略与仲裁未建"，或施工批次补调度层；接线前维持 paper。验证法：§2 轴 D grep。
2. **[P2] 做T 三承载件（MOD-SELL-018/MOD-SIG-090/t0_trader_agent）平行未收口**。建议修法：收口裁定（蓝图自注在案）落一个真源+两个退役或分工铁律（建议：资格门=P2-01 待建件、规划=本件、盘中执行编排=MOD-SIG-090、即时裁决=t0_trader_agent，写进 TDM 注释防三写）。验证法：三件签名比对。
3. **[P3] 价差/成本注入无来源锚+viable 消费纪律**。建议修法：蓝图补 CST 费率锚与估计方法登记；接线评审检查 viable 门。验证法：读蓝图 diff。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p65.md`

### L44 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] 成功判定（股数不变+总成本降）/14:50 墙钟强平/5 分钟闭环核对/归因出边四项零承载**。建议修法：EOD 判定加墙钟硬限（bar 时间戳≥14:50 即触发强平而非等 bars 尽）；T0DayReport 增加成本调整后成败判定（对接 CST-T0-001）与失败/损耗分桶；归因出边随 C3 接线批。验证法：§2 轴 D 对照。
2. **[P2] executor 异常路径破坏自平衡不变量**（抛异常=open_round 悬空直接冒泡）。建议修法：run_day 内 executor 调用包 fail-closed（异常→视同 fill 未成交走回滚/escalation 路径）；executor 契约补超时与异常语义。验证法：mock raise 探针。
3. **[P2] 回滚/强平单无价格保护**。建议修法：T0OrderIntent 增 protection_price 字段（联动 X-S2-02 跌停/笼子语义），executor 生产实现强制消费。验证法：接线评审。
4. **[P3] 平衡腿超预算 notes 缺留痕+trade_date 字符串切片格式依赖**。建议修法：补 notes；trade_date 用显式日期解析。验证法：读代码路径。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p68.md`

### L44 · 4 缺陷清单

## 4 缺陷清单

1. **[P2] 单票上限默认值 5%/8%/10% 三处矛盾**。建议修法：Owner 按 RLM-CONCENTRATION-001（D94=10%）终裁唯一值，三处默认值统一引用同一常量/配置真源（静态清单禁手工维护红线同向）。验证法：三常量并排。
2. **[P2] 禁补亏损仓与 P67 双口径**。建议修法：本件 loss_add_block 阈值对齐 0（或降 P4 告警），红线真源归 P67 门①（详见 P67 §4.2）。验证法：亏损 5% 对比。
3. **[P2] 行业基准缺省误报+低配误拦**。建议修法：baselines 缺失的行业跳过偏离检查（记 baseline_missing，对齐 P54 退化路径先例）；偏离检查单侧化（只查超配）或低配改 P4。验证法：无 baselines 探针。
4. **[P2] 节点时点+执行半边零承载**。建议修法：TDM-P-P3-04 补红注（时点编排未建），或施工批次补 BM-PLAN-02 时点件；"未成交不追价"写入执行层契约。验证法：grep。
5. **[P3] 压测收紧上限过 claim+P1 无减仓清单**。建议修法：改 docstring 为"告警"；P1 输出建议减仓标的列表（按超限幅度排序）。验证法：压测探针。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p69.md`

### L45 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] 日亏轴五级（L1 2%/L2 4%/L3 6%）零承载，节点判定轴与模块判定轴不同轴**；P67（禁加门消费 L2+）/P70（窄门消费 L2/L3）消费的 L-taxonomy 只存在于 TDM 文本与 P70 的转述枚举——熔断分级在码上无单一真源。建议修法：裁定唯一判定轴（建议：日亏轴=盘中 DrawdownController 承载、回撤轴=本模块承载，节点拆注双承载分工），并把 P70 CircuitLevel 的"真源指针"改指真实承载件。验证法：§2 轴 D grep+追 DrawdownTracker。
2. **[P2] 孤儿+持久化落盘位未装配（重启失忆）**。建议修法：装配 JsonStateStore 根目录+接线事件通道（header 已给回归锁），或维持"设计件"定位并把节点声明改挂现役路径。验证法：grep 消费链。
3. **[P3] RECOVERY 空档带/毕业小样本/复位自然日窗**。建议修法：空档带补 CRISIS 回退边或文档固化；graduation 窗口对齐（min_trades≥graduation_window 或按比例）；复位守卫改交易日口径。验证法：各自探针。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p70.md`

### L44 · 4 缺陷清单

## 4 缺陷清单

1. **[P2] CircuitLevel 真源指针幽灵化+L-taxonomy 无代码生产者**（与 P69 主发现联动）。建议修法：L-taxonomy 枚举迁往判定轴唯一真源（P69 修复裁定的承载件），本件 import 之；或改注释如实声明"真源=TDM-X-R1-01 文本"。验证法：并排读两文件枚举。
2. **[P3] 白名单默认清单硬编码 .py**。建议修法：启用回测批时迁 config/YAML 真源（自注已在案，防过期）。验证法：读常量。
3. **[P3] 国家队信号枚举二值化（NONE/两类）**：ETF 天量成交的"天量"阈值（多少倍量）无字段/无阈值——信号质量判定全推调用方，接线时须补量化定义（TDM 注释"ETF 成交量天量检测需 ETF 日线数据登记"已在案）。验证法：读 ReversalSignal/nt_signal 契约。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p72.md`

### L42 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] 止盈三式缺二（峰值回撤 30% 兑现+目标位），TDM 注释"本轮落位"与代码不符**。影响："赚过没拿住"的利润漏点封堵=图上有码上无；峰值浮盈保护比 Chandelier 价格 trailing 更贴合短线利润管理。建议修法：施工批次补 peak_pnl 追踪+回落 X% 兑现+目标位字段（X-S1-01 信号面加峰值回撤类型），并修正 TDM 注释的落位声明；或把"落位"改指 Chandelier 近似并在节点写明两者触发表差异。验证法：§2 轴 D grep。
2. **[P2] 孤儿死码**。建议修法：随 S1-05 融合/S1-01 收集器接线批次统一接线（X 流 signal 侧三件 P52/P71/P72 全孤儿，宜同批）。验证法：grep。
3. **[P3] highest_close_fn 窗口契约无校验**。建议修法：契约注明"fn 必须按 005 请求的 N 回看"；或改传数据快照。验证法：注入探针。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p73.md`

### L43 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] module_ref 语义错位+X-S1-06 四触发强清通道零承载**。建议修法：TDM-X-S1-06 拆注两承载面（本模块=策略进程异常退出编排，属运维面；四触发市价强清=市场面待建件），module_ref 增补或改挂；黑天鹅/K≥3/主力弃庄三信号源列入施工清单（K≥3 联动 P52 修复）。验证法：§2 轴 D 对照。
2. **[P2] EXIT_FAILED 无解除 API（stop_gate 永久堵塞）**。建议修法：增加 resolve(report_id, resolution) 或 has_unresolved_exits 改为"存在 EXIT_FAILED 且无后续同 strategy 成功报告"；补重试成功解除测试。验证法：本报告探针。
3. **[P2] 孤儿（design 诚实）**。建议修法：随运行时装配批接线（finalizer/stop_gate 注册）；接线前维持 design。验证法：grep。
4. **[P3] 幂等键跨 trigger 复用/cache 无界/哨兵字符串**。建议修法：缓存键加入 trigger+reason 摘要或文档约束 key 规约；cache 上限或落盘；哨兵改独立字段 verify_available: bool。验证法：各自探针。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p74.md`

### L43 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] 三维路由/分批分支/前三查/D72 恐慌拦截/R2-05 仲裁全零承载**——critical 级节点的"路由"实为静态查表。建议修法：施工批次补紧迫度/仓位/流动性入参与三维路由+前三查前置检查（量能数据源依赖 DS 登记）；D72 恐慌拦截窗（含 D95 豁免清单）单独成门；节点补红量化缺口。验证法：§2 轴 D grep。
2. **[P2] T+1 校验 lot 粒度缺失（误杀正T 卖底仓/漏拦当日加仓）**。建议修法：入参改 lots 列表（buy_date×quantity）或拆两调用（底仓/今仓分别判）；文档铁律"调用方须按 lot 拆分"。验证法：正T 场景探针。
3. **[P2] 孤儿死码**。建议修法：X 流 S1→S2 全链接线批次统一（P71/P72/P74 三件同批）；接线前降 draft。验证法：grep。
4. **[P3] date.today() 墙钟依赖+跌停挂价建议无结构化输出**。建议修法：today 必填化；挂价建议进 SellOrderPlan 字段。验证法：读签名。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p75.md`

### L44 · 4 缺陷清单

## 4 缺陷清单

1. **[P2] D67 竞价即决协议（十行矩阵/量能三口径/新股排除/跳空分档）零承载**。建议修法：position 域隔夜风险批次施工时把矩阵做成数据驱动表（生成器产出防手工漂移）挂本节点；或节点拆注"时段路由已建（C12）/竞价即决待建"两半。验证法：§2 轴 D grep。
2. **[P2] 孤儿（design 诚实）**。建议修法：随 X 流 S2 链接线批次（与 P74 同批）；接线前维持 design。验证法：grep。
3. **[P3] 决策窗起点 14:45 vs TDM 14:50 口径漂移+沪市可撤规则无生效日切片**。建议修法：两口径择一写齐（建议 14:45——给深市留挂单提前量，改 TDM 文本）；规则默认值加生效日字段或季度 T4 核对项。验证法：14:47 探针。


---

## 来源：`docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/tdm_supplement/rpt_p76.md`

### L44 · 4 缺陷清单

## 4 缺陷清单

1. **[P1] 三率+六分类+前瞻分桶+冷却机制零承载，节点名实不符（"卖出闭环与退出效率"实际=卖出滑点度量）**。建议修法：施工批次补三率追踪（需卖出后 N 日价格回填管道+理由六分类必填枚举，D72 已给枚举），或节点拆注"滑点子面已建（本模块）/三率与六分类待建"；module_id 不变、声明先行修正。验证法：§2 轴 D grep。
2. **[P2] 孤儿（production header 不实）**。建议修法：随 X-S2 执行链接线批次+归因链（P57）同批接线；接线前降 draft。验证法：grep。
3. **[P3] 决策价基准无枚举+阈值无校准锚+空成交 GOOD 语义**。建议修法：加 benchmark_type 字段（signal/submit/open）；阈值挂 CST 校准批；空输入 grade 改 N/A 或加 warning。验证法：各自探针。


---

## 来源：`docs/_working/archive/2026-09/design_memos/34_regime_meta_allocator.md`

### L580 · 7. 待定问题（讨论要点）

## 7. 待定问题（讨论要点）

> 以下来自 [00_index_trading_decision](00_index_trading_decision.md) §3 G15 讨论要点，已逐项对齐落入 §3 决策。

- [x] ① 分配公式 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` → §3.1；② Base_i 先验权重 → §3.2.1；③ PerformanceScore 60 日 Sortino 映射 [0.5,1.5] → §3.2.2；④ Shrinkage 置信度→风险节流映射（四档）→ §3.2.3
- [x] ⑤ floor≥5% / cap≤40% → §3.2.4；⑥ 稀有态差异化收缩 → §3.2.5；⑦ 第二阶段上线时机 → §3.2.6；⑧ 外部信号交叉验证（5 档水温 + 板块轮动状态）→ §3.2.7（审查补充，非原始 G15 要点；远期辅助印证定位，不进 MVP 主链路）


---

## 来源：`docs/_working/archive/2026-09/design_memos/69_trading_decision_map.md`

### L348 · 2.22 遗留两项清账（D35，2026-09-07 Owner 指令"继续处理遗留两项"）

### 2.22 遗留两项清账（D35，2026-09-07 Owner 指令"继续处理遗留两项"）

**① factor_refs 血肉补挂（R24 16 节点→0）**：16 个挂策略节点按语义匹配补挂 23 条因子引用（161 条因子库从 0 挂载→23 处交叉锚）：

| 节点 | 补挂因子 | 匹配依据 |
|---|---|---|
| TDM-E-L2-01-1 结构强度评估 | FCT-MOM-011 板块四维质量评估/FCT-SENT-012 涨停板情绪量化体系 | 涨停比/梯队/趋势 |
| TDM-E-L2-01-4 板块资金流聚合 | FCT-LIQ-040 5/10 日累计净流入/FCT-MOM-021 板块间资金迁移检测 | 主力资金进出 |
| TDM-E-L2-08 板块生命周期判定 | FCT-MOM-005 板块轮动位置判定/FCT-MOM-022 主线评分与切换确认 | 启动/发酵/高潮/熄火 |
| TDM-E-L3 个股选择（hub） | FCT-MOM-003 龙头/中军/后排三分法 | 板块里选哪只票 |
| TDM-E-L3-01 Universe 构建与剔除 | FCT-QUAL-001 业绩维因子 | 不可交易剔除 |
| TDM-E-L3-02 九阶段选票主链 | FCT-MOM-009 区间相对强弱 RS/FCT-MOM-010 综合 RS 评分 | 漏斗逐级压缩 |
| TDM-E-L3-03-1 短线池 5 分制 | FCT-TECH-070 量比五分位标准 | 短线量能评分 |
| TDM-E-L3-03-2 波段池 5 分制 | FCT-TECH-071 波段浪型量化标准 | 波段浪型评分 |
| TDM-E-L3-03-3 双策略合流体检 | FCT-TECH-085 背离程度量化与多级别级联 | 三维共振体检 |
| TDM-E-L3-04 负面否决器 | FCT-TECH-083 假突破统计参数/FCT-TECH-077 加速见顶 | 一票否决条件 |
| TDM-E-L3-07-1 打板选股链 | FCT-SENT-007 炸板率+连板高度+涨停回封时间/FCT-MOM-016 龙头三特质 | 打板标的漏斗 |
| TDM-E-L3-09 股票池分层维护 | FCT-MOM-003 龙头/中军/后排三分法 | Tier 升降级 |
| TDM-E-L3-11-2 盘中涨速异动扫描 | FCT-MOM-030 4 分钟涨速资金异动 | 涨速榜 3-7% |
| TDM-E-L4 买卖点与执行（hub） | FCT-INTRADAY-028 开盘位置 vs 支撑压力预判 | 何时进场 |
| TDM-E-L4-02 买入时序 | FCT-INTRADAY-024 竞价验证/FCT-INTRADAY-027 竞价微结构信号 | 竞价铁律/时间锚 |
| TDM-P-P2 做T与加减仓 | FCT-INTRADAY-025 VWAP 位置/FCT-INTRADAY-015 急跌必有急反 | 三做T策略 |

**② selection_funnel.py 文件头治理（R21 脏数据清零）**：[BLUEPRINT] 行从文档串（21 号备忘录 §3.6）改为 `MOD-SIG-086 supplement | docs/03_modules/_domain_signal/selection_funnel_skeleton/blueprint.md`（SIGNAL-ARCH-001 裁定该文件为 MOD-SIG-086 共享骨架的 D_FUNDAMENTAL_SIGNAL 薄适配层，supplement 语义与 sector_momentum.py 先例一致）；[MODIFY-GUARD] 同步指向骨架蓝图。TDM-E-L3-02 补挂 module_id: MOD-SIG-086，与 depgraph 缓存对账通过。

**配套修复——depgraph 缓存陈旧 hash 遮蔽漏洞**：增量扫描缓存按 content_hash 累积多版本条目且不清旧条目，原 R21 对账取首条会被文件头治理前的陈旧条目遮蔽（selection_funnel.py 缓存中新旧两条并存）。修复：_resolve_mod_id 按当前文件 sha256 现算匹配现役条目，匹配不到回退首条（对抗测试假缓存场景）。此漏洞属红队 D 类（交叉对账）变种，已由既有 D1-D5 用例+真源回归锚覆盖。

**验收**：真源地图 R24/R21 双清零（warning 快照变为 R25 空转叶子 17/R22 矩阵未覆盖 14/R1 红节点占位 75/R16 树宽 1——血肉阶段持续欠账）；对抗回归锚升级为"已清账不得复发"（R24/R21 断言 not in，R25/R22 断言持续可见）；70（38+32）+142（signal_fundamental）测试全绿。

### L402 · 2.24 全库满贯（D37，Owner 2026-09-07 裁定"要挂"——三档剩余全部转正）

### 2.24 全库满贯（D37，Owner 2026-09-07 裁定"要挂"——三档剩余全部转正）

**Owner 裁定**：§2.23 分批挂载方案中第二档 3 库（组合模型/基准/告警阈值）立即全部转正——16/16 业务库满贯打通，不留"等流开发"欠账。表驱动架构下新增 3 轴仅加 3 行轴定义+3 行容量（R34 组合模型 PFM 上限 4/R35 基准 BMK 上限 4/R36 告警阈值 THD 上限 8），R99 注册表缺失检查扩展至 16 文件。

**真源挂载（3 轴 8 处引用）**：

| 节点 | 轴 | 挂载 |
|---|---|---|
| TDM-F-C2 组合聚合 | portfolio_model | 打分加权/风险平价/核心-卫星（3） |
| TDM-F-C3 绩效归因反馈 | benchmark+threshold | 中证全指+绝对收益零基准（2）+滚动跑输/Sharpe 退役/回撤漂移倍数（3） |
| TDM-X-R1 应急保命 | threshold | 回撤预警/严重/紧急三级（3） |

**验收**：主套件 R34-R36 正反例+11 轴全绿用例（87 全绿）；对抗回归锚扩展三轴挂载不得静默消失。

**满贯后交叉索引全景（v1.7 完全体）**：`TDM 节点 → EXA/IND → FCT → STR → PAT/SEAT/MAC/CYC/UNI/CST/EVT/RLM/PFM/BMK/THD（11 库交叉轴）+ DS → MOD-* 总线 → 五图体系`——**16/16 业务库全部点对点可达**，7 张图中 6 张活跃图互通（frontend_map 草案期待转正挂 module 轴）。


---

## 来源：`docs/_working/archive/2026-09/final3_campaign/p5_w47_wiring_record.md`

### L51 · 7. 未完成与后续

## 7. 未完成与后续

- UP-1（vol_target_allocator）按差距表 §4 无需挂载（TDM-E-L1 algo_note 已声明），A/B 回测对比仍待跑（与本批 UP-2..5 同欠账）。
- 蓝图 `2026-09-13-tdm-upgrade-blueprint.md` 结案报告头部"接线待施工"表述待清理批复核刷新（本记录+commit 为真源）。
- R11 数据新鲜度 14 条 warn（CH 四态）为运行时状态，非本批范围。


---

## 来源：`docs/_working/archive/2026-09/flash_biz/biz1_b0_fifteen_closeout.md`

### L12 · 包1 · B0 前 15 条收尾（P6 §2 状态表逐条终态）

# 包1 · B0 前 15 条收尾（P6 §2 状态表逐条终态）

判据真源：REG-VALM-001 exec_quality（validation_method_registry.yaml，20/40bp 土规线）+ BT-P0-003 frozen plan（threshold_status=frozen @2026-09-12）。
执行会话：st-flashbiz-20260918（2026-09-18 凌晨）。

## 1. 逐条终态表（15/15 全部收尾，零悬账）

| # | object_id | 节点 | P6 状态 | 本班终态 | 证据 |
|---|---|---|---|---|---|
| 1 | BT-P2-042 | TDM-E-L4 容器 | 已完考（随批） | **valid（已落库）** | run_id=VAL-20260918-015408，15 行全 valid |
| 2 | BT-P1-027 | E-L4-01 分批建仓 | 已完考 | **valid（已落库）** | 同上（slip 2.56bp，triggers 1467≥30） |
| 3 | BT-P1-028 | E-L4-02 买入时序 | 已完考 | **valid（已落库）** | 同上 |
| 4 | BT-P2-043 | E-L4-03 价格锚定 | 已完考 | **valid（已落库）** | 同上（decision_price 真基准） |
| 5 | BT-P2-044 | E-L4-04 资金分配 | 已完考 | **valid（已落库）** | 同上 |
| 6 | BT-P2-045 | E-L4-05 打板执行专项 | 已完考（代理受限） | **valid（代理口径已落库）+ 真分桶判缺处置完毕** | 分桶真考不可行→见 §3；plan 判据已冻结修订（backtest_backlog.yaml BT-P2-045） |
| 7 | BT-P2-046 | E-L4-06 执行算法 | 已完考（代理受限） | **valid（代理口径已落库）+ algo_id 缺口登记+判据口径修订** | 见 §3；known_data_gaps `bt_trade_log_attribution_fields_missing` |
| 8 | BT-P2-047 | E-L4-07 条件触发队列 | 已完考 | **valid（已落库）** | run 同上 |
| 9 | BT-P2-048 | E-L4-08 突破失败降级 | 已完考 | **valid（已落库）** | run 同上 |
| 10 | BT-P2-049 | E-L4-10 订单生命周期 | 已完考（代理） | **valid（已落库）** | 成交率轴不可评=既定披露口径，hit_ratio 空 |
| 11 | BT-P2-050 | E-L4-11 部分成交处理 | 已完考（代理） | **valid（已落库）** | run 同上 |
| 12 | BT-P2-051 | E-L4-12 订单预检 | 已完考 | **valid（已落库）** | run 同上 |
| 13 | BT-P2-052 | E-L4-13 执行容灾对账 | 已完考（代理） | **valid（已落库）** | reconciliation_differences 0 行不阻断 |
| 14 | BT-P2-053 | E-L4-14 成本反馈回写 | 已完考 | **valid（已落库）** | commission 1467/1467 实算闭环 |
| 15 | BT-P0-003 | 成本三件套（4 节点聚合） | 部分完考 | **E-L4-09/X-S2-01 过；P-P2-01/P-P2-03 存疑（insufficient_samples）→包2 披露件** | E-L4-09 随 L4 批落库；P-P2 两条=只出报告不改放行（Owner 指令） |

## 2. F01 台账落库（P6 交接包①，完成）

- 执行：`run_validation(batch='L4')` 非 dry——**run_id=VAL-20260918-015408，15 行 verdict 全 valid（slip_within_tolerance，significance=ok）写入 c1_backtest.node_verdict**；trailing 衰减巡检随批。
- 落库前快照（审计锚）：node_verdict 全表 41 pending + 2 valid；TDM-E-L4% 旧行 16 条（append-only 不删，前端按节点最新行渲染）。
- run 档案已 finalize：`data/backtest_artifacts/runs/VAL-20260918-015408/`（01_survey~verdict.md 七件齐；该目录 gitignore，档案只在盘）。
- SOP-B 护栏③ 冻结留痕核对：runner 土规 20bp（apply_soil_rules）与 BT-P0-003 plan.thresholds（slip_bp_valid=20.0/pending=40.0，frozen_by=st-backtest-20260912@2026-09-12）与 REG-VALM-001 verdict_mapping 三方同源一致，零平移。
- 验收（F01 机读判据）：`SELECT verdict, count() WHERE run_id='VAL-20260918-015408' GROUP BY verdict` → `[('valid', 15)]` ✓
- 回滚：append-only 铁律不删行；误判走新 run_id 覆盖节点最新态。

## 3. F03 分桶真考（P6 交接包③，判缺处置完成）

- 就绪核查（机读）：60 件 `data/backtest_artifacts/bt-*.json` trade_log 全量扫描——**order_type 无一非 market、algo_id 无一非空 → 分桶真考不可行（数据缺口，非工程量问题）**。
- E-L4-05（order_type 分桶）：按 F03 分桶脚本逻辑对全量 fill 复核，全部落 (market, na) 单桶——排板/限价桶独立出数的前提字段不存在；不编造，维持代理口径。
- E-L4-06（algo_id）：缺口登记 `src/zephyr/data/config/known_data_gaps.yaml` 条目 **bt_trade_log_attribution_fields_missing**（resolution_plan=归属 X 流验证批 TradeRecord 扩展，字段落地后新 fill 才可分桶，旧产物不回补）。
- 判据口径修订（批次决策点公开修订，SOP-B 护栏③）：backtest_backlog.yaml BT-P2-045/046 由 `plan: null` 填为冻结 plan——阈值引 REG-VALM-001 既定 20/40bp 零平移 + caliber_note 记录分桶字段前置与代理口径（frozen_by=st-flashbiz-20260918@2026-09-18；不改判定线，只登记真判据形态与代理前提）。

## 4. 边界与诚实清单

1. B0 15 条全部收尾；verdict 均为 D 后 4 交易日（09-10~09-15）窗口、11 个 walk-forward run 混 run 聚合口径（P6 §4 披露原样有效）。
2. P-P2-01/P-P2-03 存疑件未落台账行（涉钱配对结论=只出报告，见 biz2；F02 交接包注明可选落库，本班选择不落、留 Owner）。
3. 分桶真考待 TradeRecord 字段落地后对新 fill 重跑（F03 脚本就绪，判据同线）。

### L17 · 1. 逐条终态表（15/15 全部收尾，零悬账）

## 1. 逐条终态表（15/15 全部收尾，零悬账）

| # | object_id | 节点 | P6 状态 | 本班终态 | 证据 |
|---|---|---|---|---|---|
| 1 | BT-P2-042 | TDM-E-L4 容器 | 已完考（随批） | **valid（已落库）** | run_id=VAL-20260918-015408，15 行全 valid |
| 2 | BT-P1-027 | E-L4-01 分批建仓 | 已完考 | **valid（已落库）** | 同上（slip 2.56bp，triggers 1467≥30） |
| 3 | BT-P1-028 | E-L4-02 买入时序 | 已完考 | **valid（已落库）** | 同上 |
| 4 | BT-P2-043 | E-L4-03 价格锚定 | 已完考 | **valid（已落库）** | 同上（decision_price 真基准） |
| 5 | BT-P2-044 | E-L4-04 资金分配 | 已完考 | **valid（已落库）** | 同上 |
| 6 | BT-P2-045 | E-L4-05 打板执行专项 | 已完考（代理受限） | **valid（代理口径已落库）+ 真分桶判缺处置完毕** | 分桶真考不可行→见 §3；plan 判据已冻结修订（backtest_backlog.yaml BT-P2-045） |
| 7 | BT-P2-046 | E-L4-06 执行算法 | 已完考（代理受限） | **valid（代理口径已落库）+ algo_id 缺口登记+判据口径修订** | 见 §3；known_data_gaps `bt_trade_log_attribution_fields_missing` |
| 8 | BT-P2-047 | E-L4-07 条件触发队列 | 已完考 | **valid（已落库）** | run 同上 |
| 9 | BT-P2-048 | E-L4-08 突破失败降级 | 已完考 | **valid（已落库）** | run 同上 |
| 10 | BT-P2-049 | E-L4-10 订单生命周期 | 已完考（代理） | **valid（已落库）** | 成交率轴不可评=既定披露口径，hit_ratio 空 |
| 11 | BT-P2-050 | E-L4-11 部分成交处理 | 已完考（代理） | **valid（已落库）** | run 同上 |
| 12 | BT-P2-051 | E-L4-12 订单预检 | 已完考 | **valid（已落库）** | run 同上 |
| 13 | BT-P2-052 | E-L4-13 执行容灾对账 | 已完考（代理） | **valid（已落库）** | reconciliation_differences 0 行不阻断 |
| 14 | BT-P2-053 | E-L4-14 成本反馈回写 | 已完考 | **valid（已落库）** | commission 1467/1467 实算闭环 |
| 15 | BT-P0-003 | 成本三件套（4 节点聚合） | 部分完考 | **E-L4-09/X-S2-01 过；P-P2-01/P-P2-03 存疑（insufficient_samples）→包2 披露件** | E-L4-09 随 L4 批落库；P-P2 两条=只出报告不改放行（Owner 指令） |


---

## 来源：`docs/_working/archive/2026-09/reports/p21_algo_flow_phase3_batch12_report.md`

### L53 · 五、收尾状态

## 五、收尾状态

- 本会话 14 条 claim 全部释放；72 文件批1+批2 全量落库（yaml 43+29、源码锚行 43+29、生成器、token 登记、TDM 补注、echo-guard.yml）
- 既有失败三件套与本批无关（c4_fact_e831084c 哨兵/词表、factory flaky），已移交责任线（st-autopipeline 20260915 批注清偿）


---

## 来源：`docs/_working/archive/2026-09/residual_construction/00_master_ledger.md`

### L51 · 4. 状态回写（收尾时填）

## 4. 状态回写（收尾时填）

| 环节 | 状态 | commit hash | 批次 | 备注 |
|---|---|---|---|---|
| E1 | 🟡已建待落地 | 队列 q-...-0010 | W1 | 23 tests 绿;真实 CH 判读探针 normal/r3 通过;L2/L3 已落地(e1a975b158) |
| E2 | 🟡已建待落地 | 队列 q-...-0002 | W1 | 9 tests;62 天回放 recon_diff=0.0(73,747.04 对平);daily 模式 6 行已入 CH 表 |
| E3 | ✅ | 32431d66 | W1 | 13 tests 绿+四次真实端到端（含安全窗重启调度器 02:19）；总统筹独立复核通过；GAP：risk_params/TDM 消费方无 loaded-state 钩子（登记在 checker gaps） |
| E4 | 🟡schema已落地/builder待落地 | 2fd61ca135+队列q-...-0006 | W2 | 13 tests;老蔡对账真实数字完成(方向吻合+游资足迹验证;日期映射 O-1 待 Owner) |
| E5 | 🟡已建待落地 | 队列 q-...-0005 | W2 | 16 tests;首跑真实演练:W2024 击穿破产地板 min_nav=0.8267 CRITICAL 已告警 |
| E6 | ⬜ | | | |
| E7 | ⬜ | | | |
| Q1 | ⬜ | | | |
| Q2 | ⬜ | | | |


---


---

## 来源：`docs/_working/archive/2026-09/sharpe2_prep/c_audit/2026-09-17-tonight-sampling-audit.md`

### L84 · 3 缺陷挂单清单（只挂单不修，严重级按 deep_review_policy §4）

## 3 缺陷挂单清单（只挂单不修，严重级按 deep_review_policy §4）

| # | 级 | 文件:行号 | 证据 | 修复建议（供主力会话） | 验证法 |
|---|---|---|---|---|---|
| D1 | **P1** | `scripts/backtest/f06_e4_wfa_exam.py:355-367,403`（对照 `:334-337`、`:487-488`） | OOS/IS 比率门控（0.70 硬线）分子=本考 WFA 拼接路径 OOS sharpe（2019-06 预热+折相位），分母=幸存者登记面 E4-v1 的 IS sharpe（2023-06 预热+周相位）。verdict.md 自己写明"预热起点与周频调仓相位不同，逐位不可比"（`:488`）。两个不可比口径之比被当硬否决线用——统计口径单点漂移（模式 #1） | 比率门控改用同引擎同预热重算 IS sharpe；或将 0.70 比率降级为"参考指标"并以同口径对照为主判定 | 用同一 `evaluate_recipe` 在 IS 窗重算 is_sharpe，对比登记值差异是否显著改变 ratio |
| D2 | **P2** | `src/zephyr/ex_core/daban_load_producer.py:458,586,692,702,735` | 打板决策链输入件 5 处 `except Exception → 降级空/default`（fail-open）。虽有 `_logger.warning` 留痕且 [INVARIANTS] 声明"上层 fetch_load 空→策略告警"，但本层断供时下游拿到的是中性默认值而非异常——数据源静默死亡模式（#6：断供时报错还是恒 0？） | 核实策略侧"fetch_load 空→告警"消费点真实存在并注册告警项；对 load 三腿（宽度/指数/成交额）分别加断供计数器 | 断开 events 表模拟空返回，确认策略侧是否产生可见告警 |
| D3 | **P2** | `data/backtest_artifacts/runs/E4-F06-38b453ca/summary.json` gate 块 vs overfitting 块（产自 `f06_e4_wfa_exam.py:170-215`） | 同一份数据两个"灾难"判定打架：overfitting.reasons 明写"Walk-Forward存在灾难fold(最低Sharpe=-1.00<-0.50)"，而 gate.wfa_stage.has_disaster=false、wfa_passed=true(7/8)。两个判定件对"灾难回撤"不同阈值/口径，verdict 映射只信 gate 侧 | 统一灾难 fold 定义（同一阈值常量、同一判定源），或把 overfitting 灾难理由升级为 verdict 输入 | 对照 `decision_gate` 与 `overfitting_detector` 各自的灾难阈值常量 |
| D4 | **P2** | 全仓 3,475 锚普查（§2.2）：94 占位锚 + 124 死蓝图链 + 2,853 锚无 §；今晚复发清偿件复发率 11/18 | [BLUEPRINT]→蓝图→§ 文档回环系统性欠账；trae_006 模板要求 `§{N}` 必填；现有 gate 未拦住占位符形态（`(auto-injected by S4 reconciler)`、`(pending)` 可过提交） | blueprint_format_gate 增加占位符黑名单判据与 § 必填判据（先 warn 后 hard）；94+124 件挂账分批清偿 | 对样例件跑该 gate 看能否拦住 |
| D5 | P3 | `scripts/backtest/f06_e4_wfa_exam.py:29` vs `:112` | 文档字符串"折 1-4 测试段(2022-01..2023-12)"与 0 基 fold 编号（`fold: len(folds)` 从 0 起）错位；verdict.md 模板 `:487` 按动态计算写"折 0-N" | 文档改 0 基或动态生成 | 读 summary.json folds[0].fold==0 |
| D6 | P3 | `scripts/backtest/f06_e4_wfa_exam.py:155` | `fold_metrics_from_net` 中 std==0 时 sharpe 硬置 0.0：恒正收益序列（std=0）会被记为 0 而非发散/异常标记，静默吞掉退化情形 | std==0 时记 NaN 并留痕，让门控走 fail-closed | 造常数收益序列单测 |
| D7 | P3 | `src/zephyr/backtest/core/cost_model_calibration.py:393-407` | `impact_level_for_tier` 直接下标 `IMPACT_TIER_ETA[tier]`/`IMPACT_TIER_SIGMA[tier]`，两表长度与 `n_tiers()` 不一致性无校验（滑点表 `:214` 有校验，冲击表没有）；表漂移时抛 IndexError 而非 CostCalibrationError，违 ERROR_CONTRACT"非法输入一律抛本错" | 加同款长度一致性断言抛 CostCalibrationError | 改短 IMPACT_TIER_ETA 后调用看异常类型 |
| D8 | P3 | `src/zephyr/backtest/core/decision_gate.py` check_oos_stage docstring（`dsr_threshold` 默认值定义在 `:445`） | docstring 仍写"DSR可选判定器(默认关闭)"，而 2026-09-16 车道 L 接线已把默认改为显式开启（`:420-425` 注释自述"默认由关闭改为显式安全默认"）——同文件内文档自相矛盾（文档矛盾=事故，宪法 §4.3） | 更新 docstring 与 `:445` 实况一致 | 读两处对比 |

（顺带发现、不计挂单：`c4425e60cb` screen_source 修复质量良好——SQL 注入面被 notes 解析正则约束、19 测试覆盖、存量行逐位不变；`run_f06_grid.ps1`/`register_f06_grid_task.ps1` 纯 ASCII 合规。）


---

## 来源：`docs/_working/archive/2026-09/sharpe2_prep/d_ledger/2026-09-17-node-verdict-triage.md`

### L6 · TDM 节点回测台账 pending 行三态分诊报告（Sharpe2 决赛准备·分包D）

# TDM 节点回测台账 pending 行三态分诊报告（Sharpe2 决赛准备·分包D）

> 日期：2026-09-17 ｜ 分包：st-sharpe2d-20260917 ｜ 性质：100% 只读分析，未写任何表/注册表/配置
> 台账真源：ClickHouse `c1_backtest.node_verdict`（append-only，禁删改）
> 设计真源：docs/_working/2026-09-09-node-backtest-governance.md（§七裁定+§八施工）+ docs/_working/2026-09-10-nodebt-night-report.md
> 机读版：同目录 node_triage.csv

---

## 一、口径核实：41 pending vs Owner 任务书"42"

### 1.1 实测数（2026-09-17 查询）

| 指标 | 实测值 |
|---|---|
| 总行数 | **43** |
| verdict=pending 行 | **41** |
| verdict=valid 行 | **2**（TDM-E-L1、TDM-E-L1-AGG 各 1 行） |
| distinct node_id | 38 个（36 个节点最新态仍 pending，2 个已 valid） |

### 1.2 与"42"的差异解释（已核实，含台账移送证据）

台账为 **append-only**（runner 铁律：不改写不删除，每次验证追加新 run 行）。按 run_id 重建时间线：

| 时点（ingest_ts 序） | run | 动作 | 表内累计 pending / valid |
|---|---|---|---|
| 09-12 07:06 | VAL-20260912-070605 | L4 首批 15 行（E-L4+01..14）全 pending | 15 / 0 |
| 09-12 07:06 | VAL-20260912-070622 | X 流 19 行（X-FLOW/R1/S1/S2 族）全 pending | 34 / 0 |
| 09-12 16:37~16:41 | VAL-P0-20260912-163755/163855/164116 | L1 总闸与 L1-AGG 三连跑，L1 出**首个 valid**，L1-AGG 两行 pending | 36 / 1 |
| 09-12 17:08 | VAL-P0-20260912-170843-003 | 成本模型三件套 4 行 pending（E-L4-09/P-P2-01/P-P2-03/X-S2-01） | 40 / 1 |
| 09-14 00:18 | VAL-P0-20260914-001859-002 | L1-AGG 收益口径复跑 1 行 pending | **41 / 1（总 42）** |
| 09-14 00:40 | VAL-P0-20260914-004029-002 | **TDM-E-L1-AGG 按裁定#230（判据改 fwd20 maxdd 风险判别）移送 valid** | **41 / 2（总 43）** |

**结论**：Owner 任务书"42 行 pending"写于 09-14 00:18 与 00:40 之间（或按当时口径盘点）——当时总行数恰为 42（41 pending + 1 valid）。此后 **TDM-E-L1-AGG 经裁定#230 移送 valid**（run VAL-P0-20260914-004029-002，主判据 risk_discrimination，p=1.76e-28），即任务书猜测的"台账移送过 1 行到 valid"**成立**。当前真实 pending=41 行。

⚠️ 附带口径披露（row vs node）：因 append-only，TDM-E-L1-AGG 的 3 条历史 pending 行仍留在表内（未删）。故：
- **行级 pending = 41**（含 3 条已被 valid 覆盖的历史行）
- **节点级 pending = 36**（36 个节点最新 verdict 仍 pending；本报告分诊以此为行动对象，行级状态同步给出）

---

## 二、分诊规则（判定标准，先于结论写死）

| 态 | 定义（本报告操作化） | 判据 |
|---|---|---|
| **可考** | 依赖数据已就绪且回测管线可表达，跑批即出结论 | ①数据源存在且样本量≥土规 30 触发；②时间覆盖满足 holdout 纪律（定稿锚点 D=2026-09-09 之后可考，D 前全锁）；③runner/专项脚本已存在 |
| **缺数据** | 依赖数据表/产物缺失或覆盖不足 | 写明缺哪张表/哪段时间 |
| **需裁定** | 图状/关系型/无历史数据/口径争议等工程无法自决 | 写明裁定问题本身与前置 |
| 已闭合 | 历史 pending 行已被该节点更新的 valid 覆盖（append-only 残留） | 不再行动，仅登记 |

关键事实基础（全部实测，详见附录 A）：
1. **成交流水真源是文件产物** `data/backtest_artifacts/bt-*.json` 的 trade_log（runner.load_fills），**不是 CH 表**——CH 侧 sim_trade_log 仅 9 行（sim 平台）、execution_report 0 行、account_nav_daily 0 行，均非台账数据源。
2. 产物共 52 个、128,341 笔 fill，时间覆盖 2025-04-03 → 2026-09-15；**D 锚点（2026-09-09）后可考 fill=1,467 笔**（4 个交易日：09-10/11/14/15，来自 11 个 bt-fw-* walk-forward 产物，OOS 折），其中卖出 858 笔；**1,467 笔全部携带 decision_price+commission**（T1 字段已落地），order_type 全部='market'。
3. holdout 纪律 runner 默认**定稿锚点模式**（finalized_at=2026-09-09：D 前全锁/D 后可考），非滚动 12 月锁——D 后 fill 天然可考。
4. 土规：触发<30 → pending(insufficient_samples)；滑点≤20bp→valid、≤40bp→pending、>40bp→noise。
5. 消融对照器已施工（src/zephyr/trading/validation/ablation.py，MATURITY=testing），但 **上游 sell_decision 信号 provider 零实现**（模块 docstring 自述）且 **消融实弹回放受协议备忘录 §12 约束须 Owner 放行**——runner 对 exit_counterfactual 对照缺失硬编码 pending（counterfactual_missing）。
6. 行情侧底座齐：kline_daily 1000 万行（1990→2026-09-15）、stk_limit(DS-082) 917 万行（2015→2026-09-15）、kline_1min 14.7 亿行（2021-09→2026-09-16）。

---

## 三、41 行逐行分诊表

> triage 列=本报告三态；节点最新态=该 node_id 在台账的最新行 verdict。行序=ingest 顺序。
> "可考(代理口径)"=数据与管线就绪、可出结论，但结论为流水全量代理（无节点归因），已在台账 notes 披露。

### 3.1 L4 首批（run VAL-20260912-070605，15 行）——全部可考

| # | node_id | 节点名 | method | 触发(当期) | 三态 | 节点最新态 | 证据与理由 |
|---|---|---|---|---|---|---|---|
| 1 | TDM-E-L4 | 买卖点与执行(容器) | exec_quality | 4→1467 | **可考(代理口径)** | pending | 容器节点，随子节点同批聚合出数；bt-fw 产物 D 后 1467 fill≥30；runner batch=L4 现成 |
| 2 | TDM-E-L4-01 | 分批建仓 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 同上；module order_splitter.py，滑点按 decision_price 实价可算 |
| 3 | TDM-E-L4-02 | 买入时序 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 同上 |
| 4 | TDM-E-L4-03 | 价格锚定 | exec_quality | 4→1467 | **可考** | pending | 语义=限价/市价选择直接决定滑点；decision_price 基准已就绪，本批最有信息量 |
| 5 | TDM-E-L4-04 | 资金分配多标的 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 同批可出数 |
| 6 | TDM-E-L4-05 | 打板执行专项 | exec_quality | 4→1467 | **可考(代理口径，受限)** | pending | D 后 fill order_type 全='market'，排板单不可分桶——专项判据降级为全量代理；真分桶需排板归因（缺数据项见 §五） |
| 7 | TDM-E-L4-06 | 执行算法(TWAP/VWAP等) | exec_quality | 4→1467 | **可考(代理口径，受限)** | pending | fill 无 algo 归因字段，6 个 EXA 算法不可逐算法判——同降级代理；algo_id 字段缺失登记 §五 |
| 8 | TDM-E-L4-07 | 条件触发队列 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 可出数 |
| 9 | TDM-E-L4-08 | 突破失败降级 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 可出数 |
| 10 | TDM-E-L4-09 | 执行硬约束 | exec_quality | 4→1467 | **可考** | pending | 成本模型三件套成员，阈值已冻结（20/40bp 土规线），BT-P0-003 交叉引用 |
| 11 | TDM-E-L4-10 | 订单生命周期状态机 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 可出数；未成交/撤改环节 fill 不可见（流水只含成交），成交率单轴判 |
| 12 | TDM-E-L4-11 | 部分成交与撤改处理 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 同上限制 |
| 13 | TDM-E-L4-12 | 订单级预检 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 可出数 |
| 14 | TDM-E-L4-13 | 执行容灾对账 | exec_quality | 4→1467 | **可考(代理口径)** | pending | 可出数；可增强判据=c1_market.reconciliation_differences（实测 0 行，空表不阻断） |
| 15 | TDM-E-L4-14 | 执行成本反馈与选型回写 | exec_quality | 4→1467 | **可考** | pending | fill 已带 commission（1467/1467），成本反馈闭环可实算；DS-008 成交回报挂点 |

### 3.2 X 流批（run VAL-20260912-070622，19 行）——18 行需裁定，1 行被后续覆盖

| # | node_id | 节点名 | method | 触发(当期2/D后858) | 三态 | 节点最新态 | 证据与理由 |
|---|---|---|---|---|---|---|---|
| 16 | TDM-X-FLOW | 输出离场信号(容器) | exit_counterfactual | 2→858 | **需裁定** | pending | 对照数据（双净值差额序列）不存在：sell provider 零实现+消融回放须 §12 Owner 放行。裁定问题=**是否放行消融回放实弹运行** |
| 17 | TDM-X-R1 | 应急保命(容器) | exit_counterfactual | 2→858 | **需裁定** | pending | 同上 |
| 18 | TDM-X-R1-01 | 熔断分级判定 | exit_counterfactual | 2→858 | **需裁定** | pending | 同上；另熔断五级状态机在回测窗口内是否触发过=无历史触发记录（D 后卖出含风控归因不可分），裁定需连带确认回放窗口覆盖 L2+ 熔断日 |
| 19 | TDM-X-R1-02 | 熔断期减仓与持仓处置 | exit_counterfactual | 2→858 | **需裁定** | pending | 同上 |
| 20 | TDM-X-R1-03 | 护盘资产定向加仓白名单 | exit_counterfactual | 2→858 | **需裁定** | pending | 加仓动作的消融语义（剥离=不加仓）与回滚式剥离算子语义需先对齐——口径裁定 |
| 21 | TDM-X-S1 | 卖出信号收集评分(容器) | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16 |
| 22 | TDM-X-S1-01 | 信号收集与六桶分类 | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16；六桶归因无流水字段 |
| 23 | TDM-X-S1-02 | 止损族判定 | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16（止损"救了多少"是反事实经典对象） |
| 24 | TDM-X-S1-03 | 止盈族判定 | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16 |
| 25 | TDM-X-S1-04 | 破位与情绪退潮信号 | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16 |
| 26 | TDM-X-S1-05 | 信号融合与紧迫度评分 | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16；紧迫度三档分桶需信号级日志（无） |
| 27 | TDM-X-S1-06 | 强制清仓绕过通道 | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16；触发极稀疏，即使放行也大概率 insufficient_samples |
| 28 | TDM-X-S2 | 离场执行(容器) | exit_counterfactual | 2→858 | **需裁定** | pending | 同 16 |
| 29 | TDM-X-S2-01 | 执行方式路由 | exit_counterfactual | 2→858 | **需裁定（本行）/可考（节点）** | pending(最新行=成本批) | 本行(070622)为 X 批口径；同日 17:08 成本批已按 exec_quality 重写（BT-P0-003），节点以成本批为准=可考 |
| 30 | TDM-X-S2-02 | T+1与涨跌停约束 | exit_counterfactual | 2→858 | **需裁定（口径可解）** | pending | 本节点语义=约束正确性（可执行性），非反事实；exec_quality 口径（卖出滑点/拒单率）即可考——**裁定问题=方法分配是否从 exit_counterfactual 改 exec_quality**（registry exec_quality applies_to 本就含 X 流执行节点，derive_method 代码现把全部 exit_flow 归反事实） |
| 31 | TDM-X-S2-03 | 执行时段路由 | exit_counterfactual | 2→858 | **需裁定（口径可解）** | pending | 同 30——卖出滑点按时段分桶即数据可考 |
| 32 | TDM-X-S2-04 | 本地条件单管理 | exit_counterfactual | 2→858 | **需裁定（口径可解）** | pending | 同 30（触发价 vs 成交价可算）；条件单未成交数流水不可见 |
| 33 | TDM-X-S2-05 | 分批止盈执行 | exit_counterfactual | 2→858 | **需裁定（口径可解）** | pending | 同 30 |
| 34 | TDM-X-S2-06 | 卖出闭环与退出效率 | exit_counterfactual | 2→858 | **需裁定（口径可解）** | pending | 同 30；退出效率=信号→成交时延需信号时间戳字段（缺，登记 §五） |

### 3.3 成本模型三件套补录（run VAL-P0-20260912-170843-003，4 行）——全部可考

| # | node_id | 节点名 | method | 触发(当期4/D后1467) | 三态 | 节点最新态 | 证据与理由 |
|---|---|---|---|---|---|---|---|
| 35 | TDM-E-L4-09 | 执行硬约束(成本批行) | exec_quality | 4→1467 | **可考** | pending | 阈值冻结（BT-P0-003）：佣金+印花税+滑点+市场冲击+做T成本，费率真源 CST-ASTOCK-001(active)/CST-T0-001(candidate)；fill 全带 commission 
...[TRUNC]

### L15 · 一、口径核实：41 pending vs Owner 任务书"42"

## 一、口径核实：41 pending vs Owner 任务书"42"

### 1.1 实测数（2026-09-17 查询）

| 指标 | 实测值 |
|---|---|
| 总行数 | **43** |
| verdict=pending 行 | **41** |
| verdict=valid 行 | **2**（TDM-E-L1、TDM-E-L1-AGG 各 1 行） |
| distinct node_id | 38 个（36 个节点最新态仍 pending，2 个已 valid） |

### 1.2 与"42"的差异解释（已核实，含台账移送证据）

台账为 **append-only**（runner 铁律：不改写不删除，每次验证追加新 run 行）。按 run_id 重建时间线：

| 时点（ingest_ts 序） | run | 动作 | 表内累计 pending / valid |
|---|---|---|---|
| 09-12 07:06 | VAL-20260912-070605 | L4 首批 15 行（E-L4+01..14）全 pending | 15 / 0 |
| 09-12 07:06 | VAL-20260912-070622 | X 流 19 行（X-FLOW/R1/S1/S2 族）全 pending | 34 / 0 |
| 09-12 16:37~16:41 | VAL-P0-20260912-163755/163855/164116 | L1 总闸与 L1-AGG 三连跑，L1 出**首个 valid**，L1-AGG 两行 pending | 36 / 1 |
| 09-12 17:08 | VAL-P0-20260912-170843-003 | 成本模型三件套 4 行 pending（E-L4-09/P-P2-01/P-P2-03/X-S2-01） | 40 / 1 |
| 09-14 00:18 | VAL-P0-20260914-001859-002 | L1-AGG 收益口径复跑 1 行 pending | **41 / 1（总 42）** |
| 09-14 00:40 | VAL-P0-20260914-004029-002 | **TDM-E-L1-AGG 按裁定#230（判据改 fwd20 maxdd 风险判别）移送 valid** | **41 / 2（总 43）** |

**结论**：Owner 任务书"42 行 pending"写于 09-14 00:18 与 00:40 之间（或按当时口径盘点）——当时总行数恰为 42（41 pending + 1 valid）。此后 **TDM-E-L1-AGG 经裁定#230 移送 valid**（run VAL-P0-20260914-004029-002，主判据 risk_discrimination，p=1.76e-28），即任务书猜测的"台账移送过 1 行到 valid"**成立**。当前真实 pending=41 行。

⚠️ 附带口径披露（row vs node）：因 append-only，TDM-E-L1-AGG 的 3 条历史 pending 行仍留在表内（未删）。故：
- **行级 pending = 41**（含 3 条已被 valid 覆盖的历史行）
- **节点级 pending = 36**（36 个节点最新 verdict 仍 pending；本报告分诊以此为行动对象，行级状态同步给出）

---

### L124 · 3.4 L1-AGG 历史 pending 行（3 行）——已闭合

### 3.4 L1-AGG 历史 pending 行（3 行）——已闭合

| # | run | node_id | 三态 | 说明 |
|---|---|---|---|---|
| 39 | VAL-P0-20260912-163755-002 | TDM-E-L1-AGG | **已闭合** | 收益口径首跑判据不足；同节点已被 09-14 风险口径行覆盖 |
| 40 | VAL-P0-20260912-164116-002 | TDM-E-L1-AGG | **已闭合** | discrimination_below_threshold（收益口径 p=0.0017 但档差 0.46%<1.0%）；裁定#230 改风险判据后出 valid |
| 41 | VAL-P0-20260914-001859-002 | TDM-E-L1-AGG | **已闭合** | 收益口径复跑行；同 run 序列 00:40 的 risk_discrimination 行（valid）已覆盖节点最新态 |

---


---

## 来源：`docs/_working/archive/2026-10/t0_matrix/LEDGER.md`

### L110 · D-5 六段相位物化完成 + auto_mount 双写缺陷修复（任务① 核心接线）

### D-5 六段相位物化完成 + auto_mount 双写缺陷修复（任务① 核心接线）

- 新件 `scripts/audit/t0_six_phase_materialize.py`：零自定阈值，全部 import 复用
  `auto_mount.{R2SIX,phase_overlay,resolve_six_phase,PHASE_PREEMPT}`。产物
  `docs/_working/t0_matrix/six_phase_history_v1.{csv,meta.yaml}`：**1,816 日 / 1,054 日路由六段 /
  闭卷窗 1,566 日内 886 路由、359 日属允许集**；段分布 expansion 388 / distribution 221 /
  capitulation 202 / accumulation 201 / euphoria 40 / **ignition 2**。宏观腿下限 2019-04-01（禁外推）。
- **修生产缺陷 `auto_mount.load_phase_panel`**：快照表按日双写（2020+ 的 1,631 日中 1,624 日 2 行，
  同日 dominant 零分歧=无损可去重），去重前面板 **3,254 行/1,630 唯一日** ⇒ 下游按日计数翻倍
  （30 日样本地板会在真实 15 日时假通过）；且 `PIT_TAIL_LAG` 语义="回退尾**日**"而代码"切尾**行**"，
  尾日恰为双写日时（实测 2026-09-18=2 行）**尾日漏进判定样本**。修法=去重后切尾行+零重复断言；
  另加可选 `start` 参数（默认不变⇒既有调用零行为变更）。
- **v1 考件探针对接面修正**：原 `emotion_gate_availability` 只查 `sentiment_panel`（注册定性=币圈面板）
  ⇒ 六段已可评时给假阴性。改为同时核查六段物化真源。效果 fail-closed：v1 按自身 :147 守卫
  **精准作废重开**（实测 `FAIL: 情绪门历史已可用…按卡纪律作废重开，禁单门硬出`），不放宽任何判据，
  09-22 基线 yaml 未被覆写（字节/时间戳已核）。


---

## 来源：`docs/_working/archive/2026-10/tdm20_campaign/03_pp001_slot_alignment.md`

### L50 · §5 遗留与移交

## §5 遗留与移交

1. emotion_index/ETF 反查关键词补编：归情绪线/ETF 资产 owner 线（本班只修板块面，不越域）。
2. 四判定表实跑回填：周五 E2E 集成窗按上表契约逐行接电（dloop_post 槽恢复后自然产出）。
3. plan_engine 判定表行数读数建议纳入骨架健康读数（generate_skeleton_health.py 消费面，本班不动）。


---

## 来源：`docs/_working/archive/2026-10/tdm20_campaign/05_morning_report.md`

### L60 · 六、下一步（移交）

## 六、下一步（移交）

1. 队列 q-0002/0003/0004 随基建批落地自愈，维护班盯 `python scripts/commit_queue.py status --session st-tdm20-20260923`；死信 q-0001 勿 requeue（合并器缺陷）。
2. 周五 E2E 集成窗：按 03 号件 §2 契约逐表接电实跑（dloop_post 槽恢复后自然产行）。
3. 情绪线/ETF 反查关键词补编归其 owner 线（本班只修板块面）。
4. chain_refs 吸收推进：575 条有效链未吸收=探测器读数，后续批按问题驱动逐节点挂链（容量 8/节点）。


---

## 来源：`docs/_working/axis_unify/03_f2_verdict.md`

### L13 · 一、手术形（呈批件 §2）——批，附两条补充条款

## 一、手术形（呈批件 §2）——批，附两条补充条款

**条款 1（零叙事删除）**：`module_translation_registry.yaml §battle_map_steps` 本手术一字不动。"叙事真源归对端"=流程故事的**版权归属**（讲这个故事去 TDM/工厂图讲），不是删除 BM 格子描述文字——BM 格子叙事降级为"挂载描述"（这格挂什么模块、干嘛用）继续存在。F3 纯加字段，零删改。

**条款 2（父子格一致性规则）**：infra 实现件（引擎/管道/报告生成器/适配器）一律 R4 自有；方法论叙事件（考试纪律/止损范式/决策门控）才 R1/R2/R3 归入。抽检发现父子不同判一例（BM-BT-03 归入 FAC-E4 vs 子格 BM-BT-03-B Tick回放引擎自有）——父格主叙事=绩效指标属方法论可归入，不翻案；但 F3 写入时按本规则全量自查 R2 中 infra 误归入，F4 validator 报告披露自查结果。


---

## 来源：`docs/_working/axis_unify/03_ruling_submission.md`

### L1148 · 6. 已知争议与遗留（批1 c7d4cf51075 遗留呈裁项收口）

## 6. 已知争议与遗留（批1 c7d4cf51075 遗留呈裁项收口）

1. **BM-SELL-08 做T日内套利**（本件 C 级）：批1 判其 TDM 真源=TDM-P-P2 做T族但 BM 挂 sell_flow，流归属争议未动。本提案：对端=TDM-P-P2（R2/C），BM flow_stage 归属不动（表冻结）。呈裁。
2. **BM-RC-05 A股特色止损**（本件 C 级）：同款争议，BM 挂 risk_control，TDM 真源=TDM-X-S1-02 止损族。本提案：对端=TDM-X-S1-02（R2/C），BM 归属不动。呈裁。
3. 批1 映射草稿 `docs/_working/fullcirc_closeout_chief/battle_map_axis_mapping_draft.md`（『需裁76条』载体）系死会话未入库件，现工作树与 git 历史均不可及；本件为独立全量重判，批1 11 直映对已沿用并核对一致。

### L1154 · 7. 缺口清单（双向）

## 7. 缺口清单（双向）

1. **TDM 侧未回链 120 节点**（无 BM 格子挂靠）：集中在 TDM-E-L9 知识供给轴（源线/图谱/状态变量/考试链/治理）与 C 族币圈节点——BM 无对应作战格子（知识供给属图12数据域、币圈属另一 market 实例），**建议不强行映射**，留 battle_map_refs 空缺=合法态（validator 只查死引用不查全覆盖）。
2. **工厂侧未回链 stage：** 无——E0-E9 全部有 BM 格子挂靠。
3. **BM 侧 C 级粒度错位簇**（多对多集中区）：选股四层漏斗 vs TDM 九阶段主链、评分卡维度族 vs 打板/短线链、BM-BUY-02 四轨 vs TDM 流根——若 GLM 判『格子该拆』，属 BM 表扩张=违反冻结条款，本手术不做，登记为后续战役候选。
4. TDM 无 `judgment_basis` 字段（工单 anticipated），B 级证据取 `decision_question`；若 Owner 补字段，F4 validator 可升级证据面。


---

## 来源：`docs/_working/axis_unify/06_closeout.md`

### L8 · F5 收尾：轴归一手术闭环报告（裁定#483 后置项收口）

# F5 收尾：轴归一手术闭环报告（裁定#483 后置项收口）

## 1. 覆盖报告

- **输入**：BM 341 环节（PG 只读）× TDM 183 节点 × 工厂 10 stage 配对面。
- **F1 提案分布**：R1 同名直映 14（批1 沿用 11+新增 3）｜R2 归入 191｜R3 覆盖多钉 5｜R4 自有 131；置信 A48/B159/C134。
- **F2 裁定结果**（03_f2_verdict.md）：C 级 134 整段按建议办（含 C-083 做T→TDM-P-P2、C-071..073 A股止损→TDM-X-S1 两条批1遗留争议收口；BM flow_stage 桶均不动）；B 级 159 按提案办；A 级 48 免审；手术形批+条款1/2。
- **F3 落地**：71 节点 199 条 battle_map_refs（TDM 63+工厂 8；E0/E8 留空披露）；条款2 自查 17 改判+17 borderline 保留（04 §2 全表）；纯加字段零删改（逐字节还原验证）；与裁定#487 同 commit 原子。
- **C 级清零确认**：134 条全部获裁（按建议办），验收①满足。

## 2. 缺口清单（移交后续战役候选，本手术不做）

1. TDM 未回链 118 节点：L9 知识供给轴+币圈 C 族——留空白名单合法态（裁定#487 §四）。
2. 217 条交易段无回链君子协定 warn（含 R4 自有）：实证期后可做 acknowledged 降采样或 gate 化（触发率数据积累中）。
3. BM 侧粒度错位簇（选股四层漏斗 vs TDM 九阶段等）：拆格=BM 表扩张违反冻结条款，如需另立项。
4. tdm chief 车道 D125 批（TDM-F-C1-01/02 新节点）在途：其落袋后如需与新节点挂 refs，属增量小批（R12 腿已守）。

## 3. 净零申报（宪法 §4）

- **零新建注册册**：映射入住 TDM/工厂既有节点字段（五联锚加一联）。
- **复用件清单**：①validator=check_decision_map 扩 R12 腿（对标 R9/R11 既有腿模式，零新 gate 零新脚本）；②一致性防线复用 align_battle_map ghost_tdm 腿（批1 既有）；③写入器=一次性战役工具（.runtime/tmp，不入库不占编制）；④token 登记=batch_creation_tokens 既有正门。
- **零退役**：BM 三表/锚点/运行时三消费/module_translation_registry §battle_map_steps 全部零触碰（条款1）。

## 4. memory 更新申报

memory（bm-reclass-ruling-483-20261004）本会话不可及（检索无获）；本报告+裁定#487+verdict 文件=可检索真源，后续会话按此接力。

## 5. 归档与收尾清单

- [x] 00 工单～06 收尾七件齐（本件随批落 HEAD 后工单 completes_when 满足转归档）
- [x] 全部 claim 释放（提交落地后执行）
- [x] git log 归属核验（落地后 git log -1 --name-only 对单）
- [x] 红线四条全守（零 PG 写/三消费不动/零新册/C 级未自行并合——全程）

### L18 · 2. 缺口清单（移交后续战役候选，本手术不做）

## 2. 缺口清单（移交后续战役候选，本手术不做）

1. TDM 未回链 118 节点：L9 知识供给轴+币圈 C 族——留空白名单合法态（裁定#487 §四）。
2. 217 条交易段无回链君子协定 warn（含 R4 自有）：实证期后可做 acknowledged 降采样或 gate 化（触发率数据积累中）。
3. BM 侧粒度错位簇（选股四层漏斗 vs TDM 九阶段等）：拆格=BM 表扩张违反冻结条款，如需另立项。
4. tdm chief 车道 D125 批（TDM-F-C1-01/02 新节点）在途：其落袋后如需与新节点挂 refs，属增量小批（R12 腿已守）。


---

## 来源：`docs/_working/bm_reclass_ruling/01_ruling_package.md`

### L9 · 呈批件：battle_map 定性改判——横向·覆盖切片（挂载面）

# 呈批件：battle_map 定性改判——横向·覆盖切片（挂载面）

> 呈批人：5.3 指挥会话（st-bm-reclass-20261004），Owner 对话直批通道，2026-10-04 讨论结论成文。
> 证据链：battle_map_positioning.md V0.9.0（L22/L631 现行定性原文）｜trading_decision_map_layering_policy.md
> §2.1（TDM"动作流程唯一真源，凡同等职责文档一律合并进来"法理）｜裁定#231（2026-09-14 荒废终审判活四依据
> +anchors 停写 30 天重评观察窗）｜裁定#261（2026-09-16 末次落图，BM-RES-01-E）｜裁定#409（一域一图）｜
> #ARCH-312（图族三分类，业务图族归类不变）。
> 本件四节：A 一句话定性可直裁；B 判据升级（立法点）；C 施工清单精确到行；D 边界/安全/验收。
> 批复后按 RULE-RULING 登记裁定（现役最大 #481，拟 #482，撞号跳号重登）同 commit 原子。

## A. 议题一句话（可直裁）

**批 battle_map 定性从"纵向贯穿（流程图）"改判"横向·覆盖切片（挂载面）"**——它退出流程叙事图族，
流程话语权归 TDM/策略工厂；battle_map 专职回答"每个业务模块的作战使命与落地覆盖"。
或**驳回**（维持纵向定性，理由入册）。总筹推荐：**批**。理由三条：

1. **一句话流程测试不过**：现行七张纵向图各有一句流程话（TDM=一笔交易盘前到离场怎么决策；工厂=一个策略
   候选到准入怎么生产；GOMAP/图11/12/13 同理）。battle_map 只能说出责任句——"每个环节由哪些模块承载、
   落地没有"。它的流程轴（研究孵化→模型训练→回测→仿真→选股→买入→卖出→仓位→风控→执行→对账）是交易
   生命周期通名：前 5 段已被策略工厂 E0-E9 认领，后 6 段已被 TDM（建仓→持仓→离场+订单九态）认领，
   对账段与图12 部分重叠——整轴无独占领地。
2. **文档自己已先行承认**：定位书 V0.9.0（2026-09-16）全文把"钱怎么赚流程"措辞替换为"全生命周期装配
   挂载"（L22/L26/L37/L50/L51/L220 共 6 处）——挂载本质已定，注册册与 §17.1 的"纵向贯穿"口径未跟上，
   属存量口径漂移。
3. **改判即消解重叠**：TDM 定位声明明文"凡同等职责（描写动作流程）的文档一律按第一性原理判定后合并进来"
   ——battle_map 的 11 个 flow_stage 步骤叙事正是同等职责。改判横向后两图各答一个问题（TDM 答"下一步做
   什么动作"，battle_map 答"这个环节/模块由谁承载"），叙事层面重叠即消解，不必等轴归一手术。

## B. 判据升级（本批立法点）

全景图纵横判据从**轴形状**（有 step 轴=纵向）升级为**叙事所有权**：

- **纵向图**=拥有"一句话流程"叙事真源的图（一域一图，裁定#409 准入）：TDM（交易决策流）/策略工厂
  （策略生产流 E0-E9）/GOMAP（治理运行时生命周期）/图11（交付流水线）/图12（数据供给链）/图13（交易日循环）。
- **横向图**=按对象轴切片的索引/覆盖层：depgraph（结构切片）/dataflowgraph（实体切片）/decisiongraph
  （决策切片）/blueprint.md（模块内蓝图）/**battle_map（使命覆盖切片）**。battle_map 的生命周期格子
  仅为索引键/分组维度；展示可按生命周期排序，**展示顺序≠叙事所有权**（策略行 battle_map_ref、前端
  bt-battle-stage 按阶段渲染属此类，不因展示形态回归流程图定性）。
- **配套条款**：battle_map 环节表维持 2026-08-12 起的冻结不再扩张；模块使命/落地覆盖查询以 battle_map
  为准，流程描述以 TDM/策略工厂为准——两真源边界从此各有一句话。

## C. 施工清单（批复后执行，精确到行）

### C1. battle_map_positioning.md（永久区手改册，safe_write_text 纪律）九处

| # | 位置 | 现文（摘） | 改为 |
|---|---|---|---|
| A1 | L9 标题 | 能力定位书（第五全景图 / battle_map） | 能力定位书（全景图族·横向覆盖切片 / battle_map） |
| A2 | L14 责任范围 | 项目第五全景图 | 项目全景图族成员——横向覆盖切片 |
| A3 | L16 定位裁定 | 07_ 背后有第五全景图 battle_map 作真源……全景图共五个：…… | 07_ 背后有全景图 battle_map 作真源……全景图族五成员：depgraph / dataflowgraph / decisiongraph / blueprint.md / battle_map；纵横定性判据见 §17.1（裁定#482） |
| A4 | L22 一句话 | ……是项目的第五全景图——一张以"决策环节"为节点、以"全生命周期装配挂载"为流程主线、……按业务流程串联起来的索引层真源图 | ……是全景图族的横向覆盖切片（挂载面）——以"决策环节"为索引格子、以"全生命周期装配挂载"为职责主线，回答每个环节/模块"谁承载、落地没有"；流程叙事真源=TDM/策略工厂，本图环节表仅为挂载格子（裁定#482） |
| A5 | L62 v9.0 注记 | 作战地图（第五全景图）是决策流全景图的索引层真源 | 作战地图是决策流全景图的覆盖索引层（横向，裁定#482） |
| A6 | L411-413 §9.1 | 标题"第五全景图"；正文"是第五个全景图" | 标题"覆盖索引层"；正文"是全景图族成员（横向覆盖切片）"；图名/表前缀/注册号句保留 |
| A7 | L631 判据句 | 前三图……是横向切片（按 module/decision/entity 轴）……作战地图是纵向贯穿（按业务流程 step 轴），它把前四图的节点按"选股→……→对账"6 阶段重新编排成端到端作战链条 | 全景图纵横判据=叙事所有权（裁定#482）：纵向图拥有"一句话流程"叙事真源（TDM/策略工厂/GOMAP/图11/12/13）；横向图按对象轴切片做索引（depgraph 结构/decisiongraph 决策/dataflowgraph 实体/blueprint 模块内/battle_map 使命覆盖）。battle_map 是横向覆盖切片（挂载面）：生命周期格子仅为索引键，展示顺序≠叙事所有权；它把前四图的节点按生命周期编排成覆盖格子，供"模块→作战位"与"环节→落地状态"双向查询 |
| A8 | L639 表行问题列 | 业务作战环节怎么串？每环节靠哪些模块落地？ | 每个生命周期环节由哪些模块/候选承载？落地没有？ |
| A9 | §十六版本史 | （表首插入） | + V0.10.0｜批复日｜定性改判：纵向→横向·覆盖切片，判据轴形状→叙事所有权（裁定#482）；§一/§三/§9.1/§17.1 同口径九处；trae_080 对齐枚举与 step_id 对齐轴不动（对齐轴≠叙事权） |

### C2. generate_panorama_registry.py（BUILT_PANORAMAS 条目）+ 再生机生册

- `name`："交易决策作战地图（battle_map 第四全景图）"→"交易决策作战地图（battle_map·横向覆盖切片）"。
- `description`：→"交易决策作战地图（battle_map，横向覆盖切片/挂载面）：模块作战使命与落地覆盖索引，
  6件套标准 + 双向锚点查找；生命周期格子仅为索引键，流程叙事真源=TDM/策略工厂（裁定#482）；取代
  PAN-BUILT-21 旧 trading_flow 视图（battle_map_panorama.md §四 取代声明）"。
- 重跑生成器再生 panorama_registry.md（.gitignore:547 派生件禁手改）；`category="作战地图"` 与
  `family="业务图族"`（#ARCH-312）不变。

### C2+. alignment_checklist.md §3 battle_map 行轴标注（新增面，2026-10-04 勘得）

st-mapreg-20261003 任务2（commit 9da8856dba）在 §3 挂轴表给 battle_map 行标了
"纵·作战环节 flow_stage 分域"并归入纵轴列举——系旧定性口径的**新鲜再入**。本批施工须顺带把该行
轴标注改为"横·覆盖切片（生命周期格子=索引键，对齐轴仍 step_id）"，防批后残留第二口径。
对齐键 step_id 本身不变（对齐轴≠叙事权，同 trae_080 条款）。

### C3. 明确不动（边界）

- **trae_080_panorama_alignment.yaml 不动**："第五图/五图"是对齐机制枚举、step_id 对齐轴是机械事实——
  对齐轴≠叙事权，对齐机制零变化。
- **机械层零改动**：PG battle_map_* 三表、anchors 数据、apply/align_battle_map.py、
  battle_map_alignment_gate、generate_battle_map_diagram.py、12 阶段人类视图 MD。
- **历史文书不追改**：裁定#231/#261、battle_map_coverage_ruling_20260915.md（时点快照）。
- **轴归一手术另立项候批**（BM 340 环节→TDM 184 节点词汇收敛+运行时消费迁移）：改判后它从"身份问题"
  降级为"词汇收敛卫生问题"，优先级后置，本批不做。

## D. 安全声明与验收

**安全**：净零合规（零新增册/零新增门/零新增规则，纯口径修订+1 行版本史）；施工面无 PROTECTED 路径
（check_protected_paths 实查无命中）；运行时三处消费（策略行 battle_map_ref/前端 bt-battle-stage/
api_server /battle_map_flow）不受影响；family 业务图族与 category 作战地图不变。

**验收四条**：①grep 活册面无"纵向贯穿/第五全景图（指 battle_map）"残留（trae_080 对齐枚举与历史文书
除外）；②panorama_registry.md 重生成 diff 仅含 PAN-BATTLE-MAP-01 相关行；③align_battle_map 复测与
改前一致（零机械改动自证）；④git log -1 --name-only 核实真实归属。

**批复选项**：**A 全批 C1+C2（推荐）**｜B 仅批 B 节判据+C1 之 A7/A9（最小立法，其余后置）｜
C 驳回（理由入册）。


---

## 来源：`docs/_working/circulation_chief/skeleton/D_tdm/F51.md`

### L22 · 风险

## 风险
- 立项前禁为凑绿补 null 锚（登记态禁硬凑绿同 F33 口径）；币圈 7×24 与 A 股日历语义冲突是参数化时最大坑（trading_calendar 依赖面广）。


---

## 来源：`docs/_working/circulation_chief/skeleton/E_execution/F58.md`

### L29 · 风险

## 风险

低。反馈环调制系数 0.20 写死于选型口径（TDM L4-06 algo_note），样本不足中性路径已有；后续若接 RL 执行（TDM 注记"远期候选挂晨审"）需重开环节复核。


---

## 来源：`docs/_working/code_doc_gov_campaign/p4_ledgers/w15_hanging_accounts_verdict.md`

### L223 · D2 判定台账 41 行 pending 逐行判定表

## D2 判定台账 41 行 pending 逐行判定表

真源更正：任务书"PG 查询/forecast_ledger 体系"系前提误标——全仓无 forecast_ledger 命名实体 [亲验]；唯一 PG（depgraph，pg_database 仅 depgraph/postgres）无 forecast/judgment/node_backtest 台账表 [亲验]；判定台账真源=**CH `c1_backtest.node_verdict`**（DDL 真源 schemas/categories/backtest/backtest_node_verdict.py，写入方 src/zephyr/trading/validation/runner.py）[亲验]。

pending 语义（runner.py 判定链）：pending=「验过但证据不足不下结论」的如实披露（触发<30 样本土规 PB-13 / 对照未建 / 参考价缺失），**不是欠账队列**；台账只追加不删改（铁律）。

实测：58 行 = 41 pending + 17 valid [亲验]（工单记 42，库是活的）。全部 41 行 window_end∈{09-10(38), 09-11(3)}，37 个节点全部 TDM 族且仍存在于现行 config/trading_decision_map.yaml（138 个 TDM id 全查）[亲验]。

| # | node_id | run | ingest_ts | verdict_reason | 判定 | 依据 |
|---|---|---|---|---|---|---|
| 1 | TDM-E-L1-AGG | VAL-P0-20260912-163755-002 | 2026-09-12 08:37:56 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 2 | TDM-E-L1-AGG | VAL-P0-20260912-164116-002 | 2026-09-12 08:41:18 | discrimination_below_threshold | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 3 | TDM-E-L1-AGG | VAL-P0-20260914-001859-002 | 2026-09-13 16:19:00 | discrimination_below_threshold | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 4 | TDM-E-L4 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 5 | TDM-E-L4-01 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 6 | TDM-E-L4-02 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 7 | TDM-E-L4-03 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 8 | TDM-E-L4-04 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 9 | TDM-E-L4-05 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 10 | TDM-E-L4-06 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 11 | TDM-E-L4-07 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 12 | TDM-E-L4-08 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 13 | TDM-E-L4-09 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 14 | TDM-E-L4-09 | VAL-P0-20260912-170843-003 | 2026-09-12 09:08:48 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 15 | TDM-E-L4-10 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 16 | TDM-E-L4-11 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 17 | TDM-E-L4-12 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 18 | TDM-E-L4-13 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 19 | TDM-E-L4-14 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 20 | TDM-P-P2-01 | VAL-P0-20260912-170843-003 | 2026-09-12 09:08:48 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 21 | TDM-P-P2-03 | VAL-P0-20260912-170843-003 | 2026-09-12 09:08:48 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 22 | TDM-X-FLOW | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 23 | TDM-X-R1 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 24 | TDM-X-R1-01 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 25 | TDM-X-R1-02 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 26 | TDM-X-R1-03 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 27 | TDM-X-S1 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 28 | TDM-X-S1-01 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 29 | TDM-X-S1-02 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 30 | TDM-X-S1-03 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 31 | TDM-X-S1-04 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 32 | TDM-X-S1-05 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 33 | TDM-X-S1-06 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 34 | TDM-X-S2 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 35 | TDM-X-S2-01 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 36 | TDM-X-S2-01 | VAL-P0-20260912-170843-003 | 2026-09-12 09:08:48 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 37 | TDM-X-S2-02 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 38 | TDM-X-S2-03 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 39 | TDM-X-S2-04 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 40 | TDM-X-S2-05 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 41 | TDM-X-S2-06 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |

D2 判定分布：**已被取代 19**（TDM-E-L1-AGG + TDM-E-L4 族 16 行，被 09-14/09-18 valid 重验覆盖）**/ 仍存活待复验 22**（TDM-P-P2×2、TDM-X-FLOW×1、TDM-X-R1 族×4、TDM-X-S1 族×7、TDM-X-S2 族×8 含 TDM-E-L4-09 旧行）**/ 已过期作废 0**。

建议（不在本包执行）：①19 行被取代件无需动作（只追加台账语义下自然失效）；②22 行=下游消融器/样本量前置未就绪的方法学状态，不应硬"结算"，应在下次验证批次（SOP-A 车道）按土规重跑覆盖；③工单前提更正：D2 真源指针应改指 CH c1_backtest.node_verdict。

---


---

## 来源：`docs/_working/condaxis/00_inputs/2026-10-13-sentiment-output-contract-research.md`

### L294 · §15 二轮新增呈批项

## §15 二轮新增呈批项

| # | 问题 | 选项 | 建议 |
|---|---|---|---|
| Q10 | 两套日级温度计（TDM-E-L1-S5 的 11 信号 5 档 vs alt_data emotion_index 六成分灰度） | A 分层并存（S5 管档、emotion_index 管灰度，互映射）；B 归一为一套 | **A**（"温度计≠档位计"语义的自然延伸——⚠该语义在册裁定不存在（#400 撞号，见 §3.2 更正注），**P1 呈批须先补登真裁定**；B 动 D20 定稿面大） |
| Q11 | 灰度值概率含义声明 | 每个灰度绑定一个可检验命题（如 P(明日上涨家数占比>50%)） | **必钉**——不声明则校准验证无从谈起（§13.2 第一钉） |
| Q12 | unrouted 日预算带口径 | fail-closed 按次谨慎档 / 维持空白 | **fail-closed**（与 R-055a 精神一致） |
| Q13 | 自维持回路修正权限表 | 机械参数清单 vs 语义参数清单逐项钉 | §14 表为草案，P2 判据冻结时同批钉死 |
| Q14 | L3 事件挂接 TDM 的落点 | 挂 entry_flow 传感器阵列 S6（新）/并入 S3 | 挂接清单随 §7.5 三线契约文本化时定 |

---


---

## 来源：`docs/_working/condaxis/formreg/8_prereg_targeting.md`

### L60 · 2. 判据②：周层 P-S 参数 A 股换算说明（呈批面，禁定数值）

# 2. 判据②：周层 P-S 参数 A 股换算说明（呈批面，禁定数值）

P-S 结构常数默认值=文献美股**月频**值（±8 月窗/相位 4 月/牛 15 月/熊 6 月/20%/30%）。
A 股换算候选路径（**全部呈批，P2 禁自拟冻结**）：

| 路径 | 说明 | 呈批要点 |
|---|---|---|
| a. 月频直接沿用 | P-S 原生频率即月频；000300 月频全史可得（本打靶已验证） | 无换算，首选口径 |
| b. 周频等比换算 | 1 月≈4.33 周：窗 8 月→约 35 周、相位 4 月→约 17 周、牛 15 月→约 65 周、熊 6 月→约 26 周、周期 16 月→约 69 周；幅度门槛不换算 | 等比换算是机械换算非重标定；换算后须过锚点年表同判据①复验 |
| c. 日频重标定 | 研究册 §3.4 缺口：无日频/中国市场正式重校文献——缺口即我们的活 | 需重标定协议（recal 六节结构）+锚点年表对照留证，P3 排期 |

本轮打靶（判据①）按路径 a 执行（月频），**不代表对 a 的冻结**——频率口径本身=呈批项。


---

## 来源：`docs/_working/condaxis/sentiment/6_tdm_wiring.md`

### L15 · §1 逐项台账表（三线接口＋缺口件）

## §1 逐项台账表（三线接口＋缺口件）

| 件名 | 仓内真源路径:行号 | 现状 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| 线 3（现状最好）：情绪**相位**→预算带 | config/trading_decision_map.yaml:400（总闸 TDM-E-L1 消费六段预算带："吸筹 30-50%/点火 50-70%/扩张 60-80%/亢奋封顶 30% 只卖不买"，月定大档日微调+R-055a fail-closed 地板 0.30） | ✅（在用） | 总闸 L1 输出当日总仓位上限 | 无（相位线现状=已在产；预算带数值调整=语义参数 Owner 门） | ①t0 六段物化 ②总闸 ③查表 ④在产 ⑤— ⑥六段标签 |
| unrouted 日预算带口径（Q12） | 六段 41.9% 不路由（unrouted 762 日，D 族冻结稿:49；未冻点 3.1 :55） | ⬜（无段日总闸口径未写） | 总闸 | **fail-closed 建议待批**：无段日按次谨慎档（与 R-055a"缺数落地板值"同精神——研究档 Q12 建议） | ①六段物化 unrouted ②总闸 ③谨慎档查表 ④待批 ⑤— ⑥— |
| 线 2：情绪**温度**→考试条件轴 | 立法在册=condition_package.py（MOD-BT-COND-PACKAGE，Owner 2026-09-23 夜裁①）：头部契约"统计可用层=情绪档×大盘状态（两轴全史）"；情绪值消费 c1_market.emotion_index v0.1.0 冻结公式；灰度五档 (0.2,0.4,0.6,0.8)；30 日地板；闭卷窗 [2019-01-04,2025-09-09]；状态轴选族 F4_BDI_MOMENTUM_Z20 | ✅（条件轴在产，GPU 网格输入包） | factory_grid_executor/f06_e4_wfa_exam/GPU 点火验收 | TDM 地图节点缺：condition_package 是 D_BACKTEST 域件，**trading_decision_map.yaml 无对应消费节点/data_refs 挂载**——地图面"条件轴在哪"不可见 | ①emotion_index+alt_regime ②考试族 ③条件胞 ④在产 ⑤— ⑥两轴列名不同名坑（signal_date vs trade_date 在册） |
| c1_market.emotion_index 表消费节点缺口 | 表生产=internal_compute_provider.py:766-767/:1735-1740（capability 路由）+:300（_TBL_EMOTION_INDEX）；**仓内真实消费方**=condition_package（冻结公式）、sector_state_pipeline.py:59/:109（板块偏好重映射）、emotion_index_replay、快照器 | ✅（表有消费方）🔨（TDM 地图零节点） | 见左 | **精确缺口**：非"表零消费"而是 **TDM 地图无节点**——S5/A 阵列/条件轴节点均未挂 data_refs 指向该表（研究档 §11.2-2"c1_market.emotion_index 表无 TDM 消费节点"实况精化） | ①builder 日批 ②条件轴/板块管线 ③— ④地图挂载缺 ⑤— ⑥8 列 schema |
| 线 1（主接口）：情绪**事件**→形态拐点确认器 | 候选挂位 A=entry_flow 传感器阵列 S6（新，Q14 选项一）；候选挂位 B=并入 S3（TDM:512-528，sensor/盘前，module_ref=lhb_premium_analyzer，data_refs [DS-082, DS-107]）；事件件=099/101（:7 均 testing 无消费方） | ⬜（两案待裁 Q14） | 大盘班拐点确认器（跨班接口） | 挂位裁决+边定义（事件节点→大盘班主接口节点的 payload_type/lag/pit_proof）；S6 新开 vs 并 S3 的净零权衡 | ①099/101 ②拐点确认器 ③事件离散面 ④待建节点 ⑤— ⑥事件表 |
| MOD-SIG-025 两下游接线 | market_sentiment_analyzer.py:5（CONSUMERS 自记"经 2026-09-05 AI-08 审计实证未接线——接线待排期"）：youzi_relay_emotion_engine、dual_engine_fusion_decision_engine | 🔨（production 件悬空待接） | 两候选下游（youzi 路继情绪/双引擎融合） | 接线排期（研究档 §6 消费层缺口）；接线时跨引擎传值必须经词表映射册 E2/E3 方向注记（2_L2 §2-1） | ①七维分数+灰度 ②youzi/融合 ③— ④接线待排 ⑤— ⑥— |
| S5 与 emotion_index 并存映射（Q10） | TDM:650（TDM-E-L1-S5 节点）+:575（11 信号 A1-A8/B1-B3）+:735（D20 水温解挂"日级温度计独立判定 5 档"）+S5 出边 :6187-6190（→L2-05-1/L1-AGG/L0-04）；emotion_index=六成分灰度 | 🔨（两套并存，分层依据悬空） | S5→L2-05-1/L1-AGG/L0-04（在册边） | **Q10 依据悬空**："温度计≠档位计"在册裁定不存在（#400 撞号）——P1 先补登真裁定，再定 A 分层并存互映射（建议）或 B 归一 | ①11 信号+六成分 ②AGG/L2-05-1 ③档 vs 灰度分层 ④待裁定 ⑤— ⑥同源指标冗余裁噪已预留（:580 相关性去重） |
| 相位→预算带的 unrouted 之外：S3 事件化挂边 | TDM:6171（S3→L1-AGG feed 在册）+:6174/:6259（S1↔S3 feedback） | ✅（S3 边在册） | L1-AGG | E4 事件化后的新边（S3 或 S6→拐点确认器）与既有边并存性检查 | ①S3 ②AGG ③— ④E4 事件边待建 ⑤— ⑥— |
| 新闻情绪线（S0-1） | TDM:619-634（TDM-E-L1-S0-1"新闻情绪语义分析"，parent_node=S0，:631"输出市场级+板块级情绪读数，喂 L1-S0 宏观判定与 L2-09 事件链"）+:6192（S0→AGG 边） | ✅（在册） | L1-S0、L2-09 | C6 升级（LLM 打分）走此节点，勿新开 | ①news 表 ②S0/L2-09 ③本地模型打分 ④在产 ⑤— ⑥market_news_sentiment_window |


---

## 来源：`docs/_working/condaxis/sentiment/8_p2_construction_record.md`

### L45 · §4 遗留清单（交总包/后续班）

## §4 遗留清单（交总包/后续班）

1. **daban 深史重放排期**（7_deep §4 分支 A 建议）：C1/C2 深史=仓内可推导（era 矩阵 §2），重放属重批须 Owner 排期窗（月块分片+夜间+reaper keep）。
2. **月末裂缝治本**（7_deep §1.4）：weekend_calibration 档窗口改"近 N 交易日回看"或纳入 catchup_guard overdue 面——调度器语义改动呈 Owner。
3. **诚实快照 manifest 扩列**（5_self §1 行 3：完整度/降级/分母剔除当日一行）：随 P2 判据冻结同批。
4. **周批/月批半**（5_self §4 挂起排期）：解锁条件=P2 判据冻结+Q13 权限表。
5. **A3 校准呈批材料**（4 态收敛专项状态核实+EUPHORIC 两案对照表）+ **S5 互映射**（Q10 前置）——Owner 门双待办。
6. **E5/E6/E7 事件件**（3_L3）与 TDM 挂接（6_tdm，Q14 挂位两案）——P1 呈批后执行。


---

## 来源：`docs/_working/daily_loop_campaign/00_reuse_audit_ledger.md`

### L73 · 5. 真缺口重定义（段B施工依据）

## 5. 真缺口重定义（段B施工依据）

| 原缺口单 | 对账后真身 | 段B动作 |
|---------|-----------|--------|
| ①触发面总扳手 | 真缺：无单一入口手动跑全链；warroom 棒未挂 | 建 `plan_engine/daily_loop_master_switch.py`：串 regime体检补印→warroom→daily_plan→盘中→验证→结算→拍板，幂等可重跑，不挂调度器 |
| ②验证环历史闭环 | 真缺：verification 0 行（判定器写行从未发生，非结算器坏） | 总扳手对 09-18 圈显式调 classify+verify+settle 补历史欠账 |
| ③intraday_l1_tracker 接线 | **原判过时**：已挂事件链且有 09-18 盘中4行 | 不接线；总扳手盘中段=手动触发等价钩子（tick/分钟只读记录） |
| ④路由表 v1 设计稿 | 真缺：六段↔五态映射全仓无定义 | 出 routing_table_v1_draft.md（TDM 矩阵+bizmine 判定+PP-001 原料；config 落地=Owner 门） |
| ⑤pf_alloc 接线 | **条件已满足**：事件链已在接线状态（09-18 实跑落地） | 不动；触发路径说明入 Owner 清单（#257② 口径=已触发无需再接） |


---

## 来源：`docs/_working/daily_loop_campaign/owner_gate_list.md`

### L26 · C. 路由表 config 落地批（缺口④）

## C. 路由表 config 落地批（缺口④）
- 六段↔五态映射口径（routing_table_v1_draft.md §1，含 ignition/euphoria 拆分阈值待拍板）；
- TDM-E-L1 三空格（ignition/euphoria/distribution）填格=资金分配门位（R41 词表）；
- 60% 硬顶/过渡带系数定稿（蓝图 proposed 项）。


---

## 来源：`docs/_working/daily_loop_campaign/routing_table_v1_draft.md`

### L8 · 路由表 v1 设计稿（缺口④）——状态→策略→因子

# 路由表 v1 设计稿（缺口④）——状态→策略→因子

> 定位：设计稿。config 落地（trading_decision_map.yaml / 新路由注册表）= **Owner 门位**，
> 本班不落 config（§3 段B④ 明令）。原料=TDM 状态矩阵（只读）+ bizmine 判定 + PP-001。

## 1. 待闭合接口：六段↔五态映射（对账发现的未定义接口）

蓝图编排器/decision_daily 用**六段**（capitulation/accumulation/ignition/expansion/euphoria/distribution），
台账表1 盘中跟踪件用**五态**（低迷/防御/震荡/进攻/亢奋）。全仓无映射定义（蓝图审计矛盾点②）。

### v1 提议映射（机械、保守权向：五态→六段为多对一收敛，六段→五态取保守代表）

| 五态（intraday_l1_tracker payload.state_label） | 提议映射六段 | 理由（第一性） |
|---|---|---|
| 低迷 | capitulation | 冰点=投降段尾部，预算带 0-10% 一致 |
| 防御 | distribution | 防御=只守不攻，与 distribution"只卖不买/空仓"保守侧对齐 |
| 震荡 | accumulation | 底部换手蓄势；预算带 20-30% 温和敞口 |
| 进攻 | expansion | 主升段，预算带 50-70% |
| 亢奋 | ignition → euphoria 过渡带 | 需二阶信号（量速/宽度斜率）拆分：量增价升=ignition，量价背离=euphoria；v1 简化=**映射到 ignition**（euphoria 需 Owner 拍板阈值，见门位清单） |

反向（六段→五态，编排器消费盘中行时）：capitulation→低迷、accumulation→震荡、ignition→进攻、
expansion→进攻、euphoria→亢奋、distribution→防御。
**映射常量落点建议**：`plan_engine` 内 `_STATE_LABEL_MAP` 常量（代码）而非 config——
映射是语义定义非业务参数，改它=改代码走 review；业务阈值才进 config。

## 2. 路由表 v1 结构（状态→策略→因子三级）

```
Level0 大盘状态（六段，来自 regime_snapshot_history dominant + TDM-E-L1 双轴仲裁）
  ├─ Level1 策略包路由（真源=TDM state_matrix.cells，禁复制第二份）
  |    TDM-E-L1: capitulation→[STR-VREV-025,STR-VREV-027] accumulation→[STR-VREV-026,STR-VREV-027]
  |              expansion→[STR-MOMTREND-033]；ignition/euphoria/distribution=空格(pending-owner-adoption)
  |    TDM-P-P2(做T): accumulation+expansion→[intraday-surge-fall,orderbook-imbalance,vwap-reversion,STR-DABAN-023]
  |    TDM-E-L4(打板): ignition+expansion+euphoria→daban-sleeve
  ├─ Level2 配比（真源=PP-001 sleeves 只读；verified 6条各0.05起步×0.90 全域缩放）
  |    预算带（TDM-F-C1）：capitulation 0-10 / accumulation 20-30 / ignition 30-50 /
  |                      expansion 50-70 / euphoria ≤30只卖 / distribution 0%
  |    硬顶：60%（proposed，待 Owner 定稿）；过渡带（最大隶属度<60%）×0.5-0.7
  └─ Level3 因子面（bizmine 判定原料，只读引用）
       高波桶(1.12/0.21/2.48)+risk_off池(CORREL/BETA E4拦)+ETF T0绿区簇——
       禁直接挂载：TERMINATE#304 gate 禁翻案，激活走快签新卡（裁定#390②）
```

**消费序**：编排器 S4 查 state_matrix（挂谁）→ PP-001/alloc_budget_daily（给多少钱）→
盘中五态行（T3 预警降档，只写台账不换策略——盘中重判=明确不做）。

## 3. 落地路径（Owner 批后）

1. 映射常量入 plan_engine（代码批，等长替换）；
2. ignition/euphoria 拆分阈值 + 60% 硬顶 + 过渡带系数 → config（Owner 门位逐项批）；
3. 空格填格（TDM-E-L1 的 ignition/euphoria/distribution 三格）= Owner 资金分配门位（R41 封闭词表）。

## 4. 本班实证边界

- PP-001 快照读取已通（总扳手 pp001_snapshot：16 sleeves Σ=1.0，caps 1.0/0.25/0.7）；
- 拍板体已消费 expansion@1.00→cap=60%（decision_daily 实证行）；
- 五态行已产（09-18 盘中4行）+ 映射未落地（本稿=补定义，待批）。


---

## 来源：`docs/_working/decision_map_campaign/09_link_skeletons.md`

### L139 · ⑦缺口清单

### ⑦缺口清单
D2/D3/D4/D5/D7/D33（上列）；六段分叉两处实现未对齐真源（auto_mount.py:129 R2SIX 法定 vs
daily_decision_orchestrator.py:110 REGIME_TO_SEGMENT 产线占位，修复清单 6 步=quant_methodology/
appendix_C_six_state_truth_chain.md，02 号文 §三）；宏观传感器 S0 与新闻情绪 S0-1 覆盖未接电
（audit §三）；六段全史 CSV 物化待 0033 批（01_goal §三）。

### L205 · ⑦缺口清单

### ⑦缺口清单
情绪线 G5/G6/G8/G12/G13；D6/D28；**LK-01**（本表新登）情绪成分 IC 加权二期限定于考试通过后
（骨架稿 §3），当前等权+降档为最终口径；**LK-02** 内收裁定 #400 的"两枚举收敛"移交治理班
未落（缺口单 §6 G9/G10 行）。

### L279 · ⑦缺口清单

### ⑦缺口清单
G2/G3（断供，G3 已复通）、G4（L2 门供料接线）、G5（板块坐标系裁定，469/596/90/499 四口径未辨析）、
G7（资金流深史双轨选项）、G8（阈值全 proposed）、G9（升格边界追认，唯一硬呈报项）、G12（概念轴前视
硬 gate）、G14（三标尺升维）；D11/D12/D15/D16/D18；**LK-03**（本表新登）S10 NO_EDGE 后动量成分
权重修订须走下轮预注册新卡（prereg_exam_report_v1 卡 S10 预承诺 S10-6.2），当前"状态轴有效成分集"
未定。

### L484 · ⑦缺口清单

### ⑦缺口清单
D30/D31；LK-08（PBO/CPCV）；LK-09（退役重考未开）；**LK-10**（本表新登）条件共振上岗规则 v1
未立法（滞回带+任职期=提案，06 冷水⑤；routing_table_v1_draft §3 落地三步全部待 Owner 批）；
**LK-11** T1 轻档成本路径代码缺失（方案①升级案=代码新建+考规修订双活，03 §三清单 1-2）。

### L545 · ⑦缺口清单

### ⑦缺口清单
D34/D36；BT-P2-055 底仓+日内回转执行模板（owner-vision-system-mapping §五挂单）；
LK-12（逐笔 TCA）；盘口失衡执行信号 v2（排 GPU 后）；M-55 人工干预入口（paper 升档前增设，
yaml X-R1 注释 D117——与环节 8 共享）。

### L613 · ⑦缺口清单

### ⑦缺口清单
D31；LK-13；M-55（Owner 手动接管正式入口节点，paper 升档前）；BM-RC-10 风险否决权/RC-11
独立管道=design 态（battle_map_09 节点名；panorama 设计态计数）；**LK-14** R1-03 护盘白名单
proposed 未回测生效（yaml X-R1-03）。

### L683 · ⑦缺口清单

### ⑦缺口清单
BT-P1-031 编排器施工（蓝图待 Owner 批）；warroom 三任务（表与结算器先行，addendum 施工挂点）；
D7/D29/D34；LK-15；**LK-16**（本表新登）六段↔五态映射未落地（routing_table_v1_draft §1
"全仓无映射定义"——盘中五态行与六段编排器接口对不上）。


---

## 来源：`docs/_working/decision_map_campaign/11_integrated_backtest_audit.md`

### L117 · 3.2 已知缺陷/历史伤疤

### 3.2 已知缺陷/历史伤疤
- pf_alloc 三连 poison（load_anchored_cap 对 tuple 行调 .get()）——**已修**（2d6ae249f3，`e2e_integration/LEDGER.md` 收官状态"pf_alloc 治本"）——防重复立案。
- 单票硬上限口径：代码实测 5% 较题面 10% 更严、'15% 上限'约束在代码中未定位（PQ-0049/PQ-0094，`panorama_health_snapshot_20260924.md` §四）。


---

## 来源：`docs/_working/decision_map_campaign/13_trading_chain_audit.md`

### L183 · 已知缺陷与断链

### 已知缺陷与断链
1. **THD-TRD-001..004 零消费**：alert_threshold_registry.yaml:20-22,961-1023 四条交易级告警
   （位置超限/日亏-3%/断路器断连/心跳丢失）v1.6.0 已登记但自注"status=design 代码未落"；
   grep src/ 零消费方实证——**尺子进了注册表，没有人拿尺子量**。盘中价格/仓位异常当前
   只能靠五级熔断（触发即重动作）与人工看盘。
2. **盘中持仓风控环缺位**：BM-RC-04 盘中持仓风控监控（VaR/回撤/暴露/流动性）在 battle_map 为
   production 域件，但无盘中 runner（仓内未见调度或事件挂接——如实注）；TDM 熔断 L0-L4 状态机
   的盘中评估挂 daily_gate_snapshot（盘前门快照，src/zephyr/strategy_pipeline/daily_gate_snapshot.py:29-47），
   盘中级别变化无自动播报。
3. warroom 组件 fail-open（M5）：监控自身失效不拦交易——语义已知情登记（A4"告警是尽力而为，
   保命靠熔断与人工巡检"），但**人工巡检无排班**（无 Owner 盘中巡检 SOP 时点表落档，仓内未见）。

### L337 · 已知缺陷与断链

### 已知缺陷与断链
1. **G4 绿天数无机械计数器**：门判据"连续 N 日全 ok+零 error+验证环日更"（admission_gate_design
   §1 G4），仓内**未见计数器/checker 实装**（check_live_readiness.py 全文只有设计稿 §3，
   "本班不建"；sim 日刊 fresh/degraded 字段在但无跨日连绿判定件）——绿天数靠人翻台账。
2. **E4 重放 2 例数据面缺口**（68cc 基本面列缺失/93aa 成分股窗口缺失，交付报告 §1）——重放
   覆盖 46/48，缺口未修。
3. 09-22 断链事故链（四步无调度挂接+活写手回退）已治本（事件链挂接+classify_workspace_wip
   判 stale_rollback），但**说明 sim 链对"会话间暗手"零防护的历史前科**——卫兵面当前只防
   幽灵钱包/NaN，不防调度挂接被回退（待实查：无回归哨兵）。
4. **09-24 日报缺位（待实查）**：sim_launch/ 目录止于 delivery_report_20260923；09-24 日报应已由
   observe-chain 自动渲染，仓内未见——或未提交（禁 commit 纪律下在飞）或断链复发，待次日核。

### L381 · 已知缺陷与断链

### 已知缺陷与断链
1. **09 号文环节 9 两结论已被进展刷新（须在 09 文基础上勘读）**：①"日度编排器本体不存在"
   ——完整蓝图版（BT-P1-031 S1-S7）确实未建，但**等价功能体**（9 棒事件链+总扳手 16 段）
   09-21 起 E2E 双圈实证绿；②"warroom pipeline 仓库内零调用方"——现已挂 dloop premarket/
   postmarket 两段。本文按现状判：**盘后闭环通，蓝图版编排器与现役双轨的合并决策未做**
   （两套触发面并存：事件链自动+dloop 16:45 补漏，幂等靠底层闸，无冲实——但双轨无对账声明）。
2. 计划 vs 实际核对全史：postmarket_reconcile 仅签名占位（09 环节 9⑥ 引用）——**复盘的
   "核对"一环仍占位**，日刊（sim 平台日刊）≠决策复盘（decision_plan 验证）两本账未合流。
3. 六段↔五态映射未落（09 LK-16 引用）——盘中五态行与六段编排接口对不上的病根仍在。
4. decision_daily 历史=浅（v1 安全态刚建，09 引用）——门快照 L2 板块门恒 absent v1
  （live_admission_checklist M3：无持久化日度状态，依赖 L2 门的包当日禁用）。


---

## 来源：`docs/_working/decision_map_campaign/17_quantified_acceptance.md`

### L60 · 六、22 件消失案量化（16 号文验收）【09-26 结案：验收通过】

## 六、22 件消失案量化（16 号文验收）【09-26 结案：验收通过】

22 件逐件五态终态：找回原样／损毁找回→重建／重建成功／死亡证明／无下落（禁留第六态）。验收=22/22 全有终态+找回件哈希与 backtest_artifacts 对账一致+报告落 16 号文。

→【结案】**找回 22／重建 0／死亡 0**（生路=commit_queue blobs 内容寻址袋，五处常规找尸全空）；34 项对账全绿+红证自验（扰动即转红）；根因=N-16 真源提交面漏读（已修，274 项回归绿）。详见 16 号文。


---

## 来源：`docs/_working/decision_map_campaign/links/L05_t0/t0_state_match_readme.md`

### L132 · 6. 已登记缺口债

## 6. 已登记缺口债

1. 板块族静态快照非 PIT（§3.3）——S1 成分 PIT 落库（L05-C09）前，板块轴只作观察。
2. 新闻轴阻断（§3.4）——解锁路径在册，另卡。
3. unrouted 相位日（研究窗约 40%+ 交易日无相位路由）单列，不参与任何相位格。
4. R02 状态门变体（带宽=f(状态,情绪段)）待 C05 词表裁定/C07 趋势支换源 Owner 门位后另卡
   （D-14 悬案 + 自由度≈1 悬案裁前禁两维展开，SKEL D2 ⑥）。
5. M0 触档即成交偏乐观（无排队/无冲击）——材料线卡 §9.2 披露承袭，判读带此保留。


---

## 来源：`docs/_working/decision_map_campaign/links/L06_exam_alloc/allocation_rule_v1_draft.md`

### L233 · §8 落地路径（与 routing_table §3 三步合批呈批）

## §8 落地路径（与 routing_table §3 三步合批呈批）

1. 映射常量收编共享真源（附录C §4 第 2 步对齐，src 禁 import scripts 边界内落位）；
2. 本册数值（滞回 0.60×0.5 已在码；任职期 20/冷却 60/确认窗 20/带宽 2×）经 Owner 采纳后随 D31 同批 confirmed 入 config（Owner 门位逐项批）；
3. 空格填格（TDM-E-L1 三格）=Owner 资金分配门位（R41 封闭词表，L06-C02）。

---

**立法稿完**。自检：六使命项全覆盖（§1=①，§2=②，§3=③，§4=④，§5=⑤，§6=⑥）；伪代码 4 块全为语义表达；零件零新件、gate 零新增；前置 6 项逐项如实；全部引用带仓库路径。


---

## 来源：`docs/_working/decision_map_campaign_20260924/09_link_skeletons.md`

### L139 · ⑦缺口清单

### ⑦缺口清单
D2/D3/D4/D5/D7/D33（上列）；六段分叉两处实现未对齐真源（auto_mount.py:129 R2SIX 法定 vs
daily_decision_orchestrator.py:110 REGIME_TO_SEGMENT 产线占位，修复清单 6 步=quant_methodology/
appendix_C_six_state_truth_chain.md，02 号文 §三）；宏观传感器 S0 与新闻情绪 S0-1 覆盖未接电
（audit §三）；六段全史 CSV 物化待 0033 批（01_goal §三）。

### L205 · ⑦缺口清单

### ⑦缺口清单
情绪线 G5/G6/G8/G12/G13；D6/D28；**LK-01**（本表新登）情绪成分 IC 加权二期限定于考试通过后
（骨架稿 §3），当前等权+降档为最终口径；**LK-02** 内收裁定 #400 的"两枚举收敛"移交治理班
未落（缺口单 §6 G9/G10 行）。

### L279 · ⑦缺口清单

### ⑦缺口清单
G2/G3（断供，G3 已复通）、G4（L2 门供料接线）、G5（板块坐标系裁定，469/596/90/499 四口径未辨析）、
G7（资金流深史双轨选项）、G8（阈值全 proposed）、G9（升格边界追认，唯一硬呈报项）、G12（概念轴前视
硬 gate）、G14（三标尺升维）；D11/D12/D15/D16/D18；**LK-03**（本表新登）S10 NO_EDGE 后动量成分
权重修订须走下轮预注册新卡（prereg_exam_report_v1 卡 S10 预承诺 S10-6.2），当前"状态轴有效成分集"
未定。

### L484 · ⑦缺口清单

### ⑦缺口清单
D30/D31；LK-08（PBO/CPCV）；LK-09（退役重考未开）；**LK-10**（本表新登）条件共振上岗规则 v1
未立法（滞回带+任职期=提案，06 冷水⑤；routing_table_v1_draft §3 落地三步全部待 Owner 批）；
**LK-11** T1 轻档成本路径代码缺失（方案①升级案=代码新建+考规修订双活，03 §三清单 1-2）。

### L545 · ⑦缺口清单

### ⑦缺口清单
D34/D36；BT-P2-055 底仓+日内回转执行模板（owner-vision-system-mapping §五挂单）；
LK-12（逐笔 TCA）；盘口失衡执行信号 v2（排 GPU 后）；M-55 人工干预入口（paper 升档前增设，
yaml X-R1 注释 D117——与环节 8 共享）。

### L613 · ⑦缺口清单

### ⑦缺口清单
D31；LK-13；M-55（Owner 手动接管正式入口节点，paper 升档前）；BM-RC-10 风险否决权/RC-11
独立管道=design 态（battle_map_09 节点名；panorama 设计态计数）；**LK-14** R1-03 护盘白名单
proposed 未回测生效（yaml X-R1-03）。

### L683 · ⑦缺口清单

### ⑦缺口清单
BT-P1-031 编排器施工（蓝图待 Owner 批）；warroom 三任务（表与结算器先行，addendum 施工挂点）；
D7/D29/D34；LK-15；**LK-16**（本表新登）六段↔五态映射未落地（routing_table_v1_draft §1
"全仓无映射定义"——盘中五态行与六段编排器接口对不上）。


---

## 来源：`docs/_working/decision_map_campaign_20260924/11_integrated_backtest_audit.md`

### L117 · 3.2 已知缺陷/历史伤疤

### 3.2 已知缺陷/历史伤疤
- pf_alloc 三连 poison（load_anchored_cap 对 tuple 行调 .get()）——**已修**（2d6ae249f3，`e2e_integration/LEDGER.md` 收官状态"pf_alloc 治本"）——防重复立案。
- 单票硬上限口径：代码实测 5% 较题面 10% 更严、'15% 上限'约束在代码中未定位（PQ-0049/PQ-0094，`panorama_health_snapshot_20260924.md` §四）。


---

## 来源：`docs/_working/decision_map_campaign_20260924/13_trading_chain_audit.md`

### L183 · 已知缺陷与断链

### 已知缺陷与断链
1. **THD-TRD-001..004 零消费**：alert_threshold_registry.yaml:20-22,961-1023 四条交易级告警
   （位置超限/日亏-3%/断路器断连/心跳丢失）v1.6.0 已登记但自注"status=design 代码未落"；
   grep src/ 零消费方实证——**尺子进了注册表，没有人拿尺子量**。盘中价格/仓位异常当前
   只能靠五级熔断（触发即重动作）与人工看盘。
2. **盘中持仓风控环缺位**：BM-RC-04 盘中持仓风控监控（VaR/回撤/暴露/流动性）在 battle_map 为
   production 域件，但无盘中 runner（仓内未见调度或事件挂接——如实注）；TDM 熔断 L0-L4 状态机
   的盘中评估挂 daily_gate_snapshot（盘前门快照，src/zephyr/strategy_pipeline/daily_gate_snapshot.py:29-47），
   盘中级别变化无自动播报。
3. warroom 组件 fail-open（M5）：监控自身失效不拦交易——语义已知情登记（A4"告警是尽力而为，
   保命靠熔断与人工巡检"），但**人工巡检无排班**（无 Owner 盘中巡检 SOP 时点表落档，仓内未见）。

### L337 · 已知缺陷与断链

### 已知缺陷与断链
1. **G4 绿天数无机械计数器**：门判据"连续 N 日全 ok+零 error+验证环日更"（admission_gate_design
   §1 G4），仓内**未见计数器/checker 实装**（check_live_readiness.py 全文只有设计稿 §3，
   "本班不建"；sim 日刊 fresh/degraded 字段在但无跨日连绿判定件）——绿天数靠人翻台账。
2. **E4 重放 2 例数据面缺口**（68cc 基本面列缺失/93aa 成分股窗口缺失，交付报告 §1）——重放
   覆盖 46/48，缺口未修。
3. 09-22 断链事故链（四步无调度挂接+活写手回退）已治本（事件链挂接+classify_workspace_wip
   判 stale_rollback），但**说明 sim 链对"会话间暗手"零防护的历史前科**——卫兵面当前只防
   幽灵钱包/NaN，不防调度挂接被回退（待实查：无回归哨兵）。
4. **09-24 日报缺位（待实查）**：sim_launch/ 目录止于 delivery_report_20260923；09-24 日报应已由
   observe-chain 自动渲染，仓内未见——或未提交（禁 commit 纪律下在飞）或断链复发，待次日核。

### L381 · 已知缺陷与断链

### 已知缺陷与断链
1. **09 号文环节 9 两结论已被进展刷新（须在 09 文基础上勘读）**：①"日度编排器本体不存在"
   ——完整蓝图版（BT-P1-031 S1-S7）确实未建，但**等价功能体**（9 棒事件链+总扳手 16 段）
   09-21 起 E2E 双圈实证绿；②"warroom pipeline 仓库内零调用方"——现已挂 dloop premarket/
   postmarket 两段。本文按现状判：**盘后闭环通，蓝图版编排器与现役双轨的合并决策未做**
   （两套触发面并存：事件链自动+dloop 16:45 补漏，幂等靠底层闸，无冲实——但双轨无对账声明）。
2. 计划 vs 实际核对全史：postmarket_reconcile 仅签名占位（09 环节 9⑥ 引用）——**复盘的
   "核对"一环仍占位**，日刊（sim 平台日刊）≠决策复盘（decision_plan 验证）两本账未合流。
3. 六段↔五态映射未落（09 LK-16 引用）——盘中五态行与六段编排接口对不上的病根仍在。
4. decision_daily 历史=浅（v1 安全态刚建，09 引用）——门快照 L2 板块门恒 absent v1
  （live_admission_checklist M3：无持久化日度状态，依赖 L2 门的包当日禁用）。


---

## 来源：`docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md`

### L60 · 六、22 件消失案量化（16 号文验收）【09-26 结案：验收通过】

## 六、22 件消失案量化（16 号文验收）【09-26 结案：验收通过】

22 件逐件五态终态：找回原样／损毁找回→重建／重建成功／死亡证明／无下落（禁留第六态）。验收=22/22 全有终态+找回件哈希与 backtest_artifacts 对账一致+报告落 16 号文。

→【结案】**找回 22／重建 0／死亡 0**（生路=commit_queue blobs 内容寻址袋，五处常规找尸全空）；34 项对账全绿+红证自验（扰动即转红）；根因=N-16 真源提交面漏读（已修，274 项回归绿）。详见 16 号文。


---

## 来源：`docs/_working/decision_map_campaign_20260924/HANDOVER.md`

### L71 · 施工项池 P0（资金安全/成绩单可信度）

### 施工项池 P0（资金安全/成绩单可信度）
8. IBT-D01 双引擎成本口径对照（考尺 vs 整装）
9. TRD-A10 桥客户端两缺陷修复（隔夜单静默丢弃+撤单竞态）
10. TRD-A12 熔断 HALT 首次演练（Owner 门位）
11. L04-C03 DU-11 daily_valuation 部分写入病根治
12. AI 层 245 件批落地（三 AI 门暂禁用待翻回——in_process_gate_registry.yaml 三条 enabled:false，AI 批落地同批翻回）

### L78 · 施工项池 P1（链路通电）

### 施工项池 P1（链路通电）
13. L09-C01 编排器收拢（蓝图版 vs 双轨二选一）
14. L09-C03 双账合流；L04 候选池三来源接线；L07-C03 算法层收口（Owner 一句话）；L03-C06 v2 卡判档；L01-C03 口径治理；六段收编剩余三步

### L88 · 五、Owner 待裁清单（全部有建议，见 07 号文 C2）

## 五、Owner 待裁清单（全部有建议，见 07 号文 C2）

1. t0 甲位（三版本分叉待确认）2. 清道三袋 ARCH 议题注册 3. L09-C01 编排器收拢 4. emoreplay 交接确认 5. 方案① prereg 重签（红蓝达标触发）6. AI 层批文 7. 修宪入口 8. DU-07 consensus 补齐已批待执行


---

## 来源：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/AUTO_t1_t2_handover.md`

### L135 · 八、遗留与交棒

## 八、遗留与交棒

- W-M1 24h 三判据评估与死信自愈重投：不在本件职责（对象不同，内收判据"跨域不同对象不并"），
  仍待总筹以同类"代码薄壳"重建（本件 STATUS 机读面可作其模板）。
- 待落清单见 `landing/lane_auto.yaml`（本车道禁 git/禁 cron，全部经 LANE-LAND）。


---

## 来源：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/LEDGER.md`

### L88 · 六、总筹看守表（每轮巡检四项，收尾时必须全绿）

## 六、总筹看守表（每轮巡检四项，收尾时必须全绿）

| # | 看守项 | 判据 | 首轮实测（21:10） |
|---|---|---|---|
| W1 | 蒸发未复发 | `git status --porcelain \| grep -c '^ D'` == 0 | 0（回填后） |
| W2 | T1 存活 | PID 3584 在 + 日志 mtime 前进 | 活（488KB@21:08） |
| W3 | 队列不楔死 | daemon online；本夜无未定性新死信 | processing=1（ailayer） |
| W4 | 三条 AI 暂禁 gate | AI 层 245 件落 HEAD 后 `in_process_gate_registry.yaml` 内三条 `enabled: false` 必须翻回 true（gate 位 706/712/718/724 区段，三条注明"AI 层批落地同批翻回"） | 仍 false（批未落完，符合预期） |


---

## 来源：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/adj/ADJ_emoreplay_reaccept.md`

### L82 · ⑤ 风险（做错的最坏情形）

## ⑤ 风险（做错的最坏情形）

- **资金安全：低但非零**。`emotion_index_replay` 是**历史回放器**（写 `consensus`/`emotion` 类研究表），不触执行单源；但 2.2/2.4 显示它会**写 CH 表**（`test_write_replay_rows_*` 两例即写路径）。最坏情形=复职重灌覆盖在产 live 键 → 情绪轴真值被历史重放值改写 → 下游情绪因子/相位判定带脏数。缓解证据=该行为已被 `test_write_replay_rows_skips_live_keys` 钉住（实测通过）。
- 拆袋错序风险：注册册先行而代码件后落 → 悬空引用触发 REFERENCE-INTEGRITY/FK 红，全仓提交被连坐（本仓先例见 HANDOVER 血泪配方第 9 条）。
- 判"已批"的合规风险：07 号文不在 HEAD、ruling 册查无专项条目 → 若据 07 号文宣布"Owner 已批"，属**署名无正式通道凭据**（宪法 §9.11：对话内口头不构成门禁豁免）。


---

## 来源：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/adj/ADJ_l09c01_orchestrator.md`

### L87 · ⑤ 风险（做错的最坏情形）

## ⑤ 风险（做错的最坏情形）

- **资金安全：当前零暴露**（GRADUATED_PACKAGES 恒空 + 观察记录模式，实测 2.4）。**但这是"今天"的安全**：一旦包集非空（L06-C01 落地/毕业策略出现），双触发面的日序差异会立刻变成"同一天两条不同仓位上限"的生产事故，而现在的幂等是"先占者胜"（后到的合法修订会被吞）→ **路径 C 若不加 T3 修订权设计，等于把未来某天的仓位下调指令静默丢弃**。这是本项唯一的资金尾部。
- 选 B 的运维代价：13 个钩子迁移期任一漏迁 = 该产出永久停摆且无告警（哨兵 L09-C04 未施工）；且违反 §9.3 需新裁定，属 high 域门位。
- 选 A 的运维代价：段表裁剪掉的事件漏醒兜底能力消失，历史上 2026-09-15~09-18 断供事故的形态会重演（`daily_loop_master_switch.py:8` 自述该根因，引自注释未复测）。
- 不裁（维持现状）的代价：**L09 SKEL 的"增量工作冻结在双轨上"无机制执行**，下一批人可能在总扳手里再写一遍 decision 段 → 那才是真第三套。


---

## 来源：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/adj/ADJ_prereg_resign_two_round.md`

### L84 · ⑤ 风险（做错的最坏情形）

## ⑤ 风险（做错的最坏情形）

- **资金安全：零暴露**。搜索面产物进池仍需 `GRADUATED_PACKAGES`（实测恒空）与毕业门，不会因重签直接产生下单行为。
- 半签风险（A 的最坏形态）：`cost_gate_t1_tiers_bp:` 写成空值/漏值 → **下一个起跑的 stage 无论 t0/t1/t2 全炸**（实测 fail-closed），表现为"GPU 窗白白排队"。
- 高估成本风险：不重测轻档 s/格 就沿用 35.33 → T1 帽按错的换算被钳小 → ①宣称的 2 倍收益拿不到，还会误判"两轮制无收益"而错杀一条提速路线（**这是最坏的认识论损失，不是资金损失**）。
- 试验数污染风险：轻档粗筛若不计入 N_eff/`n_trial_ledger`（e7_defense.ledger_required: true，实测在册），DSR 分母失真 → 成绩单过优。此为预注册纪律的硬红线。
- 口径矛盾处置风险：把 `:67` 注释当事实继续引用，会在未来某次"超时为何没中止"的追查里再耗一轮（本仓已有多次"文档计数漂移"事故记录）。


---

## 来源：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/adj/ADJ_t0_jiawei_versions.md`

### L84 · ⑤ 风险（做错的最坏情形）

## ⑤ 风险（做错的最坏情形）

- **资金安全：零直接暴露**。实测编排/执行面无一消费该 CSV 做下单；`GRADUATED_PACKAGES: Final[frozenset[str]] = frozenset()`（`src/zephyr/strategy_pipeline/daily_decision_orchestrator.py:121`，实测）→ 结构性不产实盘单（裁定#305 安全态）。风险全在**研究可信度面**。
- 选 C 的最坏情形：六段相位下游（P1 条件概率表、做T相位匹配矩阵、上岗规则原料）系统性建立在双写虚高的日计数上，**30 日样本地板被虚假满足**→ 不合格策略被判合格进入候选池 → 若未来某天毕业集非空，等于用脏样本骗过毕业门。这是本项唯一带资金尾部风险的形态。
- 选 A 的最坏情形：口径断层期（旧脏数结论与新全史并存）若未标注即引用，出现同指标两值互相打脸；文档纪律上 17 号文有"占位口径结论标注+重算"槽（引自 19 号文 C2，未复测）。
- 流程风险：绕 CloneGuard 用 `ZEPHYR_PROTECTED_PATHS_BYPASS`/noqa 类硬闯=把"存量同构对"洗成"本批新克隆"，下次同类批必再死。


---

## 来源：`docs/_working/decision_map_campaign_20260924/links/L01_regime/_INDEX.md`

### L33 · 2. 本环节新缺口汇总（子层净增，共 21 条）

## 2. 本环节新缺口汇总（子层净增，共 21 条）

| 编号 | 一句话 | 三态 |
|---|---|---|
| L01-S1-G1 / S5-G2 | 4 态降维后置信档阈值仍沿用 9 态校准值 | 施工（随档表统一批） |
| L01-S1-G2 | dominant 被当方向轴消费 vs 锚定只保标签可比 | 挂起 |
| L01-S2-G1 | overlay 阈值债有声无账本 | 施工 P2 |
| L01-S2-G2 | 8 转换盘中触发面缺位 | 挂起（含反驳者一问留痕） |
| L01-S2-G3 | 四只供数件零调用 | 施工（内收申报） |
| L01-S3-G1~G3 | 零消费件 / production 未装配 / LPPLS 换轨未评估 | 施工 / 施工 / 挂起 |
| L01-S4-G1~G3 | 死取数面 / 特征漂移哨兵缺 / 广度补位两读面 | 施工 / 施工 / 施工 |
| L01-S5-G1 | 788 行校准器与生产节流链断开 | 挂起 |
| L01-S6-G1 | run 台账无机读盘点面（5 run 谁作正身靠人记） | 施工 P1 |
| L01-S7-G1~G2 | 本地 SQL 第二真源 / 成熟度与职责不符 | 施工 / 施工 |
| L01-S8-G1 | 六段微观腿阈值无预注册卡 | 挂起 |
| L01-S9-G1~G2 | 另类信号融合腿未定义 / F23 无毕业排期 | 挂起 / 挂起 |
| L01-S10-G1~G2 | 状态读取门面缺失（7 散落 SQL）/ 新消费者未入册 | 施工 P1 / 施工 P0 |
| L01-S11-G1~G3 | 重验无排班 / 对拍仅 20 日抽样 / c1 号位空置 | 挂起 / 施工 / 施工 |
| L01-S12-G1~G2 | TDM 图-码三处错位 / production 无挂点 | 施工 P1 / 挂起 |


---

## 来源：`docs/_working/decision_map_campaign_20260924/links/L02_emotion/_INDEX.md`

### L31 · 本环节净新增缺口汇总（22 条，三态分布）

## 本环节净新增缺口汇总（22 条，三态分布）

施工 14（A-G1/A-G2/A-G3、B-G1、C1-G1/C1-G2、C2-G2、C3-G1/C3-G2、C6-G1、F-G1、G1(文档面)、H-G1 + 文档销口 2 条）；挂起 8（C4-G1 市值归一、C5-G1/G2、C6-G2、C2-G1、D/E-G1 复职批依赖、F-G2、G-G2、H-G2）；封矿 0（本子层无"终局无位置"项——情绪为独立状态变量已裁，凡消灭人工误读者一律给位置）。


---

## 来源：`docs/_working/decision_map_campaign_20260924/links/L03_sector/_INDEX.md`

### L27 · 本环节净新增缺口汇总（14 条）

## 本环节净新增缺口汇总（14 条）

施工 11（B1-G1/G2、B2-G1/G2、B3-G1/G2、B5-G1、B6-G1（验收）、B7-G1、B8-G1/G2）；挂起 3（B4-G1 待 Owner 双轨、B5-G2 待史回填、B7-G2/B8-G3）；封矿 0。升格边界追认（G9/L03-C05）仍为**唯一硬呈报项**，本层不重裁。


---

## 来源：`docs/_working/decision_map_campaign_20260924/links/L05_t0/etf_t0_cost_and_pool/MINE.md`

### L74 · ④ 缺口清单（新登 `L05-ET-G*`，在册映射见末列）

## ④ 缺口清单（新登 `L05-ET-G*`，在册映射见末列）

| 编号 | 缺口 | 归属 |
|---|---|---|
| L05-ET-G1 | "D26=60min ETF 深度缺口"旧叙事与实测不符：`kline_etf_60min` 覆盖 2005-02-23→2026-09-24，四段缺口的**段界与量级**未复核 | 承 L05-C13（D26） |
| L05-ET-G2 | 仓内并存两套 ETF 往返成本口径（31.2bp 个股固定 vs ETFT0-SCREEN ≈11.7bp 档位代理），相差 2.7 倍，无收口件 | **DU 类（同对象异口径）** + 承 L05-C06 |
| L05-ET-G3 | "价差分列逐只实测"与五档保留窗（约 1 个月且全在闭卷段）结构冲突：研究窗内不可得 | 承 L05-C13（D36）/L05-C08 |
| L05-ET-G4 | 佣金腿输入不在库（券商费率），且佣金地板纪律**无策略侧消费者**（`cost_model_calibration.py:5` 自陈） | LK 类（接线缺位，既有在册） |
| L05-ET-G5 | 17 §三.4 要求的"近 60 日日均成交额 top100 选池件"未建；ETFT0-SCREEN 的宇宙=frozen 关键词，两者不可互相顶替 | 承 L05-C06 |
| L05-ET-G6 | ETF 分钟面 `amount` 缺失 → 量能/成交额维在分钟不可算（与 L05-PA-G03 同源，跨个股/ETF） | 取数画像项 |
| L05-ET-G7 | A 股 ETF 印花税/过户费豁免论断**未取权威双源**（若成立则 31.2bp 对 ETF 口径错配） | CNS/Owner 门位项 |
| L05-ET-G8 | T0-ETF 正式卡零存在（`rule_cards/` 仅 r01~r04），且旧勘测产物含 `.json` 与目录契约冲突（不改他人件，只登记） | 承 L05-C06 |


---

## 来源：`docs/_working/decision_map_campaign_20260924/links/L05_t0/rule_card_candidate_surface/MINE.md`

### L78 · ④ 缺口清单（新登 `L05-CR-G*`）

## ④ 缺口清单（新登 `L05-CR-G*`）

| 编号 | 缺口 | 归属 |
|---|---|---|
| L05-CR-G1 | 排除清单缺"跨日腿族结构性不可卡"一条（真源=`cost_trio_exam.py:78-90` 配对键），致 3.4 被误诊断为"待料" | 承 L05-C03 报备面（**只补排除理由，不改判据**） |
| L05-CR-G2 | "位次不可观测"族（1.4/4.1/4.2/4.3）的不可卡理由散在 SKEL 各表，无统一排除条目 | 同上 |
| L05-CR-G3 | 转债卡化需独立成本口径声明（1~8bp vs 31.2bp），禁回灌个股判据；该约束目前只在 SKEL 表格叙述里 | 承 L05-C01 + Owner 门位 |
| L05-CR-G4 | 同族消融义务（2.1↔2.2 等四组）未反映在卡面：两卡可同时 registered 而无人负责消融 | 判读纪律项（承 LK 族） |
| L05-CR-G5 | "可卡性三问"未形式化（现排除清单是散文理由，不可机检、不可复算） | 小件施工候选（≤1 页文档+一条字段） |
| L05-CR-G6 | 加卡的边际价值受"消费面=0"压制：试验数增长而决策面为零 | 与 L05-DS-G3 同窗裁定 |
| L05-CR-G7 | 卡状态机无强度（`STABILITY` 自由文本，引擎不校验语义） | 承 L05-C03；机检项 |
| L05-CR-G8 | 三候选（3.1 纯分钟 / 7.2 派生腿 / 8.1 事件史）的字段债层级未分开登记 | 取数债台账项 |


---

## 来源：`docs/_working/decision_map_campaign_20260924/links/L05_t0/t0_state_match_readme.md`

### L132 · 6. 已登记缺口债

## 6. 已登记缺口债

1. 板块族静态快照非 PIT（§3.3）——S1 成分 PIT 落库（L05-C09）前，板块轴只作观察。
2. 新闻轴阻断（§3.4）——解锁路径在册，另卡。
3. unrouted 相位日（研究窗约 40%+ 交易日无相位路由）单列，不参与任何相位格。
4. R02 状态门变体（带宽=f(状态,情绪段)）待 C05 词表裁定/C07 趋势支换源 Owner 门位后另卡
   （D-14 悬案 + 自由度≈1 悬案裁前禁两维展开，SKEL D2 ⑥）。
5. M0 触档即成交偏乐观（无排队/无冲击）——材料线卡 §9.2 披露承袭，判读带此保留。


---

## 来源：`docs/_working/decision_map_campaign_20260924/links/L06_exam_alloc/allocation_rule_v1_draft.md`

### L233 · §8 落地路径（与 routing_table §3 三步合批呈批）

## §8 落地路径（与 routing_table §3 三步合批呈批）

1. 映射常量收编共享真源（附录C §4 第 2 步对齐，src 禁 import scripts 边界内落位）；
2. 本册数值（滞回 0.60×0.5 已在码；任职期 20/冷却 60/确认窗 20/带宽 2×）经 Owner 采纳后随 D31 同批 confirmed 入 config（Owner 门位逐项批）；
3. 空格填格（TDM-E-L1 三格）=Owner 资金分配门位（R41 封闭词表，L06-C02）。

---

**立法稿完**。自检：六使命项全覆盖（§1=①，§2=②，§3=③，§4=④，§5=⑤，§6=⑥）；伪代码 4 块全为语义表达；零件零新件、gate 零新增；前置 6 项逐项如实；全部引用带仓库路径。


---

## 来源：`docs/_working/decision_map_campaign_20260924/links/L06_exam_alloc/resonance_friction_assembly/MINE.md`

### L67 · ④ 缺口清单（沿用 + 续编）

## ④ 缺口清单（沿用 + 续编）

| 编号 | 缺口 | 册内可见性 | 状态/解锁 |
|---|---|---|---|
| LK-16 | 六段↔五态↔七态三套词表映射无统一定义 | SKEL L06-E/F | 挂起→施工（映射常量入 plan_engine，Owner 批后） |
| **L06-C14（新，册内未见）** | **mSPRT 晋升输入虚挂**：champion/challenger 配对 ExecutionReport 契约未建，delta=占位（msprt:110-115） ⇒ 序贯晋升无真实成交流 | 本块新立 | 施工；解锁=成交回报契约（属执行链 L07，本块登记边界不越界建） |
| **L06-C15（新，册内未见）** | **euphoria/distribution 覆盖空洞互为前置**：D30 填格需防御 sleeve 且需 r 态来源，framework_composer:151-152 证无 ⇒ 填格与"是否新设防御档/是否补微观相位源"须同批裁 | 本块新立（呼应任务令"结构性问题已登记"） | 挂起；解锁=Owner 裁防御档 + 微观相位源接入位点 |
| L06-C01 | 上岗规则 v1 立法（滞回带 0.60×0.5 + 任职期 20 日 + 冷却 60 日提案→立法） | SKEL §8 C01 | 挂起；解锁=Owner 采纳 + 六段分叉 6 步修复完成 |
| IBT-C01/C02 | E8 装配层 + 7 态×15 员矩阵 + Σ<1 直通 | SKEL L06-H | 挂起排期；解锁=批 D 新名单 + 成绩单驱动（禁自造=协议 §7 预注册原话） |


---

## 来源：`docs/_working/decision_map_campaign_20260924/links/L09_review/_INDEX_MINE.md`

### L46 · 三 · 三个"待裁项"的材料齐备度（本批只出材料，未拍板、未施工）

## 三 · 三个"待裁项"的材料齐备度（本批只出材料，未拍板、未施工）

| 待裁项 | 材料 | 齐否 |
|---|---|---|
| **L09-C01 编排器收拢**（蓝图版 vs 双轨转正） | S1 册⑤：两版各自代码位置／当前谁在真跑（**两条都在跑**，实测 16 钩子 + 16 段 + 各自触发面）／合并技术路径四步／保留两条的运维代价 4 条／不可逆点（事件链摘钩=当日全链停摆且节拍不可追溯；T4 落库新增列难回退）／附带三个必答子问题（盘前三实现、cron 二次驱动 reconciler 是否保留、晨间窗挂哪条节拍）；S5 册补 T3 基座已存在（`plan_revision` 17 行历史实证）⇒ 工时按"复活"不按"新建" | **齐**（Owner 一句话即解） |
| **L09-C03 日刊双账合流** | S4 册②：两账定义／**5 条实测冲突**（`trade_date` 前瞻 vs 回顾时间轴、日频 vs 日历日、只增修订 vs 幂等替换、production vs experimental、2 读侧 vs 0 读侧）／可执行工作项 4 步／分期主张（3 步可绕开 L09-C02 先行） | **齐**（并主张解除 L09-C02 串行的误置） |
| **TRD-A04 盘前双（三）实现治理** | S2 册②⑤：三套实现逐个装配方实测 + 023 是"晨间窗天然实现骨架"的判读 + 复用已有实码补触发面的最小施工路径 + 显式豁免路径 | **齐**（随 L09-C01） |


---

## 来源：`docs/_working/fms_overhaul/S8_conflict_surface/README.md`

### L28 · ④ 冲突避让图（后续波次铁律）

## ④ 冲突避让图（后续波次铁律）

1. 本战役区 docs/_working/fms_overhaul/ 归 st-fms-chief-20260927；他队勿写。
2. st-p1b-libr 三件 library reconciler 文件：本战役 B3/B4/B10 全部绕行（B3 检查器独立新件、B4 不碰 regen reconciler、B10 只读引用）。
3. st-p15-phantom 的 decision_map links 区：B2 死引用清偿批单批 ≤20 文件绕开其面（S1 处方）。
4. .pre-commit-config.yaml 单写者=总筹；B1/B4/B10 的门注册由总筹统一一批落。
5. 宪法 AGENTS.md 单写者=B56 代理（等长替换）→ 总筹复核；期间他队禁写。
6. models/（15G）删除属 Owner 门位，本战役不动。


---

## 来源：`docs/_working/full-auto-chain/S11_assembled_backtest/nodes/chip_engine_promotion_mining.md`

### L16 · 0. 状态认定先行：不是"未转正"，是"虚标 production 的孤儿"

## 0. 状态认定先行：不是"未转正"，是"虚标 production 的孤儿"

任务假设"该引擎可能处于非 production 状态"。实测结论相反：**声明面三处自称 production，
实际是零消费端孤儿件，且在真实数据上输出伪分布**。转正审计的第一产出是把声明面打回原形：

| 声明位置 | 声明 | 实际 |
|---------|------|------|
| 模块头 `[MATURITY] production`（chip_distribution_engine.py:7） | production | src 内除 `__init__.py` 再导出外**零 import**（grep 全 src 实证）；唯一声称消费者 MOD-REGIME-002 的源码里没有它的 import |
| 蓝图 frontmatter `design_maturity/build_status: production`（blueprint.md:7-8） | production | 同文件 L25"成熟度: design 🟡待施工"、L374 §12.1"**本模块尚无已实现代码**"——蓝图内部三处自相矛盾 |
| decision_algo_registry.yaml:161-167 `DAL-CHIP-DISTRIB status: production` | production，outputs=[获利盘占比, 单峰密集度] | 引擎**不产出获利盘占比、不产出单峰密集度**（compute_metrics 只有 4 个其他指标，chip_distribution_engine.py:239-244）；TDM-E-L3-12 的决策问题（trading_decision_map.yaml:1997-2000"获利盘>90%…低位单峰密集"）所需的两个输出均不存在 |

battle_map_domain_policy.yaml:370-374 也自证未挂载（"待 MOD-REGIME-001 promote 后统一挂载"）；
backtest_backlog.yaml:965-977（BT-P2-040）confidence: **untested**、plan: null。


---

## 来源：`docs/_working/fullcirc_closeout_chief/t3_fullflow_exam_mining.md`

### L166 · 1.7 exit_flow·X 族（19 节点）——**最大缺口带**

### 1.7 exit_flow·X 族（19 节点）——**最大缺口带**

| 节点 | 名称 | 判定 | 证据 |
|---|---|---|---|
| TDM-X-FLOW | 输出离场信号（终端聚合） | 缺口 | **考卷无任何主动离场**：权重仅在调仓日变动，跌出 Top-N 即被动清仓（`_backtest_core` gross=w.shift(1)×rets，无止损/止盈路径，`_c4_engine.py:561-616`） |
| TDM-X-R1 | 应急保命（cross_cutting） | 有接口未开 | 模拟盘平面已接回撤六态机 defensive_only（CRISIS/KILL 拒新开仓，`sim_daily_runner.py:1318,1356-1394`）；网格考卷无 |
| TDM-X-R1-01 | 熔断分级判定 | 有接口未开 | DrawdownStateMachine 在模拟盘 bridge 接线（同上）；c2_extreme_event_protection 可做 CRISIS 时段 MaxDD 分析（框架在册） |
| TDM-X-R1-02 | 熔断期减仓与持仓处置 | 有接口未开 | 模拟盘 KILL→execute_kill_switch_liquidation（`sim_daily_runner.py:1465`）；考卷无 |
| TDM-X-R1-03 | 护盘资产定向加仓白名单 | 缺口 | TDM state_matrix 自述：euphoria/distribution 两态"PP-001 无防御型 sleeve"，格子 pending-owner-adoption（trading_decision_map.yaml state_matrix cells）；防御档内容=Owner 资金分配门位 |
| TDM-X-S1 | 卖出信号收集评分（组骨架；BM 已映射） | 缺口 | 组节点（BM-SELL-03→TDM-X-S1 映射在册，回测侧仍零实现） |
| TDM-X-S1-01 | 信号收集与六桶分类 | 缺口 | sell_signal_collector 仅 live |
| TDM-X-S1-02 | 止损族判定（BM-SELL-04-B 已映射） | 缺口 | 研究样板在册：ATR 3 倍止损带（`scripts/backtest/indicator_consumption_demo.py:34`）、forward_stop_loss（`scripts/backtest/panic_rebound_depth.py:149`）、模拟盘 legacy stop_loss 路径（`sim_daily_runner.py:1423`）；**考卷引擎零实现** |
| TDM-X-S1-03 | 止盈族判定（BM-SELL-04-A 已映射） | 缺口 | take_profit_strategy 仅 live；全仓 grep 考卷/框架无止盈实现 |
| TDM-X-S1-04 | 破位与情绪退潮信号 | 缺口 | 同 S1-02 |
| TDM-X-S1-05 | 信号融合与紧迫度评分（BM-SELL-02 已映射） | 缺口 | sell_signal_fusion_engine 仅 live |
| TDM-X-S1-06 | 强制清仓绕过通道 | 非回测域 | strategy_abnormal_exit_orchestrator=实盘异常处置编排 |
| TDM-X-S2 | 离场执行（组骨架） | 缺口 | 组节点 |
| TDM-X-S2-01 | 执行方式路由（critical） | 缺口 | sell_execution_planner 仅 live |
| TDM-X-S2-02 | T+1 与涨跌停约束 | 已实现且可考（近似） | 封板闸双向：封涨停禁买入/封跌停禁卖出（`_c4_engine.py:453-497`）+shift(1) T+1；框架侧 matching_engine 同约束；失真点=日级 close 判定封板（§4.4） |
| TDM-X-S2-03 | 执行时段路由 | 缺口 | sell_session_router 仅 live；考卷单一收盘口径 |
| TDM-X-S2-04 | 本地条件单管理 | 缺口 | 条件单=日内价格触发语义，考卷无日内路径 |
| TDM-X-S2-05 | 分批止盈执行 | 缺口 | scaling_out 仅 live；考卷调仓日一次性全额 |
| TDM-X-S2-06 | 卖出闭环与退出效率（BM-SELL-09 已映射） | 非回测域 | 执行质量遥测=实盘域 |

### L236 · 2. 缺口清单（C 类 118 项按工作量分级）

## 2. 缺口清单（C 类 118 项按工作量分级）

工作量口径：**S=参数/数据接线（复用在册模块，向量化可写，≤1 个考卷迭代）**；**M=模块补写（新逻辑但日频向量化可表达）**；**L=新子系统（需新引擎面/新数据面/新编排）**。

### S 级（接线即可考，估计 5 项）

| # | 缺口（TDM 节点） | 接线内容 | 复用在册资产 |
|---|---|---|---|
| S1 | L1 总闸/L1-AGG/L3-06 环境开关 | J_regime_switch=on：owner_regime_switcher 日级 cap 调度表 × 权重矩阵逐行乘（向量化一行） | switcher.py build_schedule；schema J 维 |
| S2 | L4-02 买入时序 + L4-03 价格锚定 | 成交价口径 close→next_open / vwap 宽表（rets 换源即可） | _c4_engine load_px 泛化 |
| S3 | L9-A04 估值 / L9-A05 财务 | 载荷函数已在考卷引擎自身，接入因子面即考（PB/PE 因子档） | load_valuation/fin_snapshot |
| S4 | X-R1-03 护盘白名单 | 防御档资产（ETF/红利）进 G_universe 候选+state_matrix 防御格内容——**格子内容属 Owner 资金分配门位，AI 禁自填**（state_matrix mounted_reason 明示） | TDM state_matrix；load_etf |
| S5 | F-C3-01 归因 manifest 增列 | cost_attribution 输出进 manifest 列 | 框架 cost_attribution.py |

### M 级（模块补写，日频向量化可表达，估计 8 项）

| # | 缺口（TDM 节点） | 补写内容 | 备注 |
|---|---|---|---|
| M1 | X-S1-02 止损族 + X-S1-03 止盈族 | 日级 ATR 止损带/移动止盈/目标价向量化（indicator_consumption_demo 已有 ATR 样板可翻译） | X 族最小考卷核 |
| M2 | X-R1-01/02 熔断分级与减仓 | 回撤六态机日级向量化（峰值权益 running-max→态→帽） | DrawdownStateMachine 语义翻译；c2 已有 CRISIS MaxDD 判据 |
| M3 | L2 板块主干最简版 | sws2021_l1 行业动量 Top-K 板块 × 板块内个股两层排序（行业锚已在） | 行业锚=c1_market.industry_class（schema:84-91） |
| M4 | L4-01 分批建仓 + P3 金字塔 + S2-05 分批止盈 | K_capital_ramp 四取值的权重路径渐变后处理（lump/linear/pyramid 均可向量化） | schema 自述"需 harness 路径依赖"——向量化实现即满足 |
| M5 | P1-03 买入逻辑存活判定 | 入场理由因子存活追踪（入场因子值退化→离场） | thesis_survival 语义回测化 |
| M6 | C2-03 相关性 cluster 上限 | 滚动相关矩阵贪心聚类+簇帽 | 日频可算但 O(S²) 注意 GPU |
| M7 | L4-11 部分成交 | 参与率上限向量化（成交额/ADV 帽） | INV-UNIT-001 口径 |
| M8 | L3-03 双池评分最简版 | 动量池/低波池双 5 分制+合流 | F 维 signal_additive 可搭桥 |

### L 级（新子系统，估计 5 项）

| # | 缺口（TDM 节点带） | 子系统 | 备注 |
|---|---|---|---|
| L1 | P2-01~03 做T全链 + L3-11 日内动态选股 + S2-04 条件单 | tick/分钟级考卷编排（框架 event_driven_engine+ch_tick_replay+matching_engine 在册，缺考卷层+竞价段） | 做T 语义只有 tick 级可表达 |
| L2 | L4-07/10/11/12 订单九态语义 | 订单生命周期考卷（部分成交/撤改/废单/条件触发） | 模拟盘 bridge-execute 已有三闸实盘件，考卷化=新编排 |
| L3 | L9 另类数据源线 30 条消费 | 每条=数据工程+因子工程 | 破坏"净零"纪律风险高，须逐条立项替代声明 |
| L4 | C2-01 净额轧平+C1 预算切分+C3-03 调权全链 | 多策略组合层引擎（F 维全取值+组合聚合） | PP-001 整装组合 V0 是现成蓝图 |
| L5 | TDM-C-* crypto 域 | crypto 行情载荷+回测 | 独立域 |


---

## 来源：`docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md`

### L75 · 三、四方映射缺口表（F 骨架 ↔ TDM 182 ↔ ROOR 77 ↔ src 域 57）

## 三、四方映射缺口表（F 骨架 ↔ TDM 182 ↔ ROOR 77 ↔ src 域 57）

| 方 | 总数 | 骨架无位计数 | 成员与处置 |
|---|---|---|---|
| TDM 节点 | 182（E128/P18/X19/F13/C4） | **0 个节点无 F**（F30-F52 全收）；但 **38 个 module_ref:null 无逐一归属判**（全在 L9，实测名单：A01-A16/B01-B10/C01-C03/G1·G2·G4·G5/V2/AGG/D2/E2/Z1；G3 有码不 null） | P0 待挖面：须生成器出"null 节点→F"映射表逐条判（普查 §六 待挖①），非本轮新号 |
| TDM 结构 | 2（state_matrix:5556、portfolio_plan:5639；edges 254 条已入 §二 DAG） | **2** → 已判 A-1 并入 F38、A-2 并入 F48（见 §二） | 裁-5 打包 |
| ROOR | 77（summary=76，§五-3） | 候选 **15 行/21 册**（12 行并入 18 册+3 册转新环 F123/F124/F126）＋**40 册登记面欠账**（环节在、册内未点 REG 名，如 F64 合写未给 REG 号=机检不可达） | 40 册补注=REG 号批注工单（普查待挖④），不新增环节 |
| src 顶层域 | 57（F 册:12 称 56，§五-4） | 名称未匹配 **17** → 语义已覆盖 4（experiment_tracking→F67、red_blue_validator→F100、signal_quality→F40、strategy_factory→F17/F23）＋真候选 **13**：4 并入（alt_data/market_data/intelligence/gov_rule）＋7 新环（D-02..04·06..08·11）＋2 Owner 门（knowledge/infra_runtime） | 见 §二 |
| 反向（骨架→三方） | 122 | **0**：122 环各有代码/注册表/图锚（K/L/M 段治理横切本就无 TDM 节点对应，属设计内） | — |


---

## 来源：`docs/_working/fullconnect_campaign/c_exam_pipeline/05_f27_e8_assembly_allocation.md`

### L32 · 四、缺口清单

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 钱包额度接线未落地（预算≠拿额） | MOD-PA-030 自述 | 落地接线 diff（分配→钱包开户额度对齐）；S-M | **P0** |
| 2 | 3 毒丸遗体占队（attempts 3/3/6） | pending 实读 | 清队卫生项（幂等闸保护下无实害）；与 BP-3 同班 drain | P1 |
| 3 | 09-25/26/27 无 marker（休市推断） | last_audit+日历 | 待 09-28 自然唤醒验证；若 09-28 仍无 marker=升级排查 | P2（观察） |
| 4 | IC_IR 加权/资金爬坡两法注无实件 | 全仓 grep 维持 | 待裁：降级演进方向或立项（sharpe_weight 为最接近替代） | P2（待裁） |
| 5 | sleeve 落库语义+TDM 对接 | alloc 表 strategy 粒度 | sleeve 列裁定+F48 消费者登记（跨组） | P2 |

### L60 · 缺口清单状态修订

### 缺口清单状态修订
- 缺口 3（休市缺口观察）：**翻面**——09-28 trade_date marker 在，休市推断成立、链未断。
- 缺口 5（sleeve 落库语义+TDM 对接）：**已施工**（a349ddc1fe sleeve provenance+strategy_production_map 对接）。
- 缺口 1（钱包额度接线）：a349ddc1fe 的 allocation_orchestrator +16 行为 sleeve 装配面，钱包开户额度对齐未见直接证据——维持 P0 待复核。
- 缺口 2（毒丸清队）／4（IC_IR/爬坡两法待裁）：维持。


---

## 来源：`docs/_working/fullconnect_campaign/c_exam_pipeline/06_f28_e9_live_attribution.md`

### L32 · 四、缺口清单

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | IS 分解 FIELD-GAP（无决策时间戳） | DDL :91-97 复读 | schema 契约+DDL 增列走裁定+M7 回填规则；M 级；非本车道可修 | **P0** |
| 2 | 影子组合工作流未建 | 全仓无实件 | 前置=M7 合规门 Owner 报送（绝对前置禁自动施工）；届时最小件=C4 引擎复刻对照 | P0（门位后） |
| 3 | 回灌 E2 环断（FL1 无实件） | grep hypothesis_precheck 消费=空 | decay_cause 回写 E6 台账+假说先验标签，与 FL2 同案立项；S-M | P1 |
| 4 | 归因引擎自证验证欠账 | TDM 17_f50 卷堵点 5 | portfolio_attribution 残差对账补跑（TDM 域） | P1 |
| 5 | 风险贡献占位 1/N | detail 占位标记 | 挂 M-11 登记不施工 | P2 |


---

## 来源：`docs/_working/fullconnect_campaign/d_l9_knowledge/03_f32_图谱谱系.md`

### L38 · 四、缺口清单（处置+优先级）

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|------|------|----|
| 1 | G5 消费边 100% 挂零（今日复测 0/16,859），GRF16 考问无法开考 | WP-0.5 立项：153 部门↔ig_node 映射表，建成回填挂载列；跨车道归总筹 | P1 |
| 2 | G1/G2/G4/G5 module_ref=null 四节点 | 回填四装载件路径（§二表），0.5 人日归 TDM 本体 | P1 |
| 3 | G4 静态 as_of 2026-09-14 无定期增量 | akshare stock_board_concept_* 三接口限速日批，1 人日可施工 | P1 |
| 4 | G1 消歧桥 88/5,560（1.6%） | 沿 WP-0 续推，优先 8 条 chain_refs 在产链；归 altdata_line 车道 | P2 |
| 5 | chainmap_cluster_names.yaml 近全空 | 机制保留勿动（三期裁定取消 LLM 族名版）；塌簇治理后重生成 | — |


---

## 来源：`docs/_working/fullconnect_campaign/d_l9_knowledge/04_f33_状态变量快照.md`

### L34 · 四、缺口清单（处置+优先级）

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|------|------|----|
| 1 | judgment 台账三表合计 33 行且两日零增长 | 对照 M5 05_master_health_table 作战室任务行核对缺勤；按 ledger-standard §五写台账强制化，1-2 人日，归 F37/plan_engine 车道 | P1 |
| 2 | V2 无聚合器 | 维持定案挂起；底座三件在库零起步成本；独立对话开题=Owner 门位 | —（挂起） |
| 3 | V→AGG 三条 feed 边缺登记 | 补 V1/V2/V3→AGG feed 边（pit_proof=快照时戳 T-1），0.2 人日归 TDM 本体 | P2 |
| 4 | V3 生产真身未指名 | TDM V3 algo_note 回填 sector_state_pipeline+sector_state_aggregator 双件，0.2 人日 | P2 |


---

## 来源：`docs/_working/fullconnect_campaign/d_l9_knowledge/05_f34_知识汇聚.md`

### L40 · 四、缺口清单（处置+优先级）

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|------|------|----|
| 1 | CH 表不存在（聚合器无处落数） | `python scripts/ch/apply_l9_readiness_ddl.py --dry-run` 预演→`--apply`（admin 账号，DDL 幂等只建不改），0.2 人日 | **P0** |
| 2 | 未首跑+dry-run 探测超时 | 建表后 `python -m zephyr.data.l9_readiness_aggregator --force` 首跑；超时项排查（疑 tick 族大表 count 探测撞 CH 60s 限，加预聚合/近似计数或分表探测），0.5-1 人日 | **P0** |
| 3 | 下游 pf_alloc 零消费（AGG→TDM-E-FLOW 边有名无实） | 二期：allocation_inputs 增 readiness 检查（黄/红降级留痕，仿 anchored_cap 旁路先例），1-2 人日归 TD/执行域 | P1 |
| 4 | V 族→AGG 无显式 feed 边（登记面） | 补三条边 0.2 人日归 TDM 本体（聚合器语义已覆盖 V 族，图面补齐防误读） | P2 |


---

## 来源：`docs/_working/fullconnect_campaign/d_l9_knowledge/06_f35_一问一考.md`

### L35 · 四、缺口清单（处置+优先级）

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|------|------|----|
| 1 | TDM D2/E2 module_ref=null stale | 回填（§二表路径，注意 D2 件名勘误），0.2 人日归 TDM 本体 | P1 |
| 2 | D1→D2 假设入表无管道 | lane_c2_candidates.csv 增量→register 批量适配器（exam_plan 模板从 TPL-FAM 族机生），2-3 人日可施工 | P1 |
| 3 | 两套考尺并行（runner vs exam_loop） | 对象不同禁合并；TDM E1 algo_note 双锚注明 0.2 人日（登记面） | P2 |
| 4 | D1 三缺（积木/加固/GPU） | SF 组 F14-F15 工单域，引用不重挖 | P1（归 SF） |


---

## 来源：`docs/_working/fullconnect_campaign/d_l9_knowledge/07_f36_治理横切.md`

### L35 · 四、缺口清单（处置+优先级）

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|------|------|----|
| 1 | Z1 module_ref=null stale | 回填→exam_ops.py，0.1 人日归 TDM 本体 | P1 |
| 2 | 575/583 链未被任何 TDM 节点引用 | 按 w4_1 triage canonical 分批挂 refs（优先 L2-06 板块传导消费链），2-3 人日/批，禁一次挂全（对账判据禁重画） | P1 |
| 3 | 净零季审窗从未编排（construction map L6 9 问无领题者） | 跑一轮三检件+reconcile 并留档即答，0.5 人日/季，无需新码 | P2 |
| 4 | JSONL 审计账在 .runtime/chain_piling/（1,177 行）TTL 张力 | 核实生命周期约定；若随 24h TTL 清扫即丢审计轨→战役归档时迁 PG 唯一真源（JSONL 降当日缓冲）；引 M8/治理层裁定 | P2（待裁） |
| 5 | answered 占比 99.3%→今日 281/422=66.6%（registered 139 摊薄） | 批处理形态非病灶；L5#24 健康带考问对批处理口径需重新定标 | P2（待裁） |


---

## 来源：`docs/_working/fullconnect_campaign/f_exec_risk/07_f52_validation_methodology_dal.md`

### L42 · 四、缺口清单（B 半验证欠账总口径，按生死线排序）

## 四、缺口清单（B 半验证欠账总口径，按生死线排序）

| # | 欠账 | 处置 | 优先 |
|---|---|---|---|
| 1 | BT-P0-003 成本三件套：L4-09 过/X-S2-01 过/P2-01+P2-03 存疑（做T 24<30 样本，净价差 mean −45.0bp 披露在案） | Flash F02 重考扩样本 | P0 |
| 2 | X 流 18 节点全 pending | exit_counterfactual 真结论待窗口前移重跑 | P1 |
| 3 | 消融器实弹待 Owner 放行（§12） | 放行后 run_ablation→batch="XFLOW" | P1 |
| 4 | 消融动作标注自动化（SellSignal 流未接回测） | 与欠账 3 同根同修 | P1 |
| 5 | P/F 流验证零启动（agg_discrimination/portfolio_attribution 无一行实弹） | 随 C3-04 工单链立项 | P1 |
| 6 | BTB 132/142 plan:null | 批次决策点填写并冻结前禁跑（SOP-B 护栏③）| P1 |
| 7 | decay_watch 调度挂载 Owner 二选一 | 晨报裁定 | P2 |


---

## 来源：`docs/_working/fullconnect_campaign/g_backtest_gpu/01_f58_execution_cost_feedback.md`

### L9 · F58 · 执行成本反馈（总册状态 partial/P1；本卷独立复核=确认 partial，断链一米未接）（断链已于 09-28 T 袋码面闭合——已过时，见刷新批注）

# F58 · 执行成本反馈（总册状态 partial/P1；本卷独立复核=确认 partial，断链一米未接）（断链已于 09-28 T 袋码面闭合——已过时，见刷新批注）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | 成交回报 vs 发单前成本预估（TDM-E-L4-09 预估）；滑点按冲击/时机/价差三分量拆解由 slippage_analyzer 供（其 CONSUMERS 头注实锚 `services/slippage_analyzer.py:5` "MOD-XS-018(ExecutionQualityScorer, 消费 SlippageResult)"）；数据源 DS-008（TDM 节点 data_refs） |
| 下游消费 | TDM 边 `L4-14→L4-06 feedback`（trading_decision_map.yaml:5352，payload=feedback，lag T-1）→ 执行算法选择器换算法；间接 F28 归因。**码面实测：algo_execution_selector.py（677 行）零处引用 execution_quality/scorer（本日 grep 复证）** |
| 自动化触发 | 节点 activation=postmarket（yaml:2559）；无计划任务无常驻——属盘后事件位，当前零外部装配（ex_sor 全族生产不可达，M7-05 已判"传递性不可达"） |
| 真源与注册表 | 节点=config/trading_decision_map.yaml:2536（TDM-E-L4-14，module_ref=execution_quality_scorer.py，module_id=MOD-XS-018，note_confirmed 2026-09-16）；蓝图=docs/03_modules/_domain_ex_sor/execution_quality_scorer/blueprint.md；G4 出处=docs/_working/2026-09-09-tdm-growth-blueprint.md:112/242（"G4 执行成本反馈闭环"，增长批2 落图 2026-09-10，施工清单立 C14 接线待排期） |
| 门禁与质量尺 | 质量三档（好/可/差）=scorer 判据（f41 册 §三"判据-码面差异=一致"）；tests/ex_sor/test_execution_quality_scorer.py 在册（本班禁实跑只数）；scorer 532 行 production |
| 当前运行状态 | **partial 确认**：零件三件全 production（scorer 532 行/selector 677 行/slippage_analyzer），TDM 边已落图，但**选择器零消费评分=闭环最后一米未接**（节点 algo_note 自认"断链实证 2026-09-10"；本日独立复证同判） |

## 二、子模块三级枚举（域→子包→件，本日实扫）

- **ex_sor.services**（10 .py 含 __init__）：execution_quality_scorer.py（532 行，本环节真身，零生产装配）；slippage_analyzer.py（喂 scorer）；transaction_cost_optimizer.py（715 行族内最大，零装配）；t0_cost_model.py（144 行，testing，交叉 F69）
- **ex_sor.core**（11 件）：algo_execution_selector.py（677 行，MOD-XS-011，**回写目标、缺评分输入**）；execution_route_policy.py（testing，90 号 §19 路由裁定）；sor_agent.py（CONSUMERS 自注"运行时装配批待兑现"）
- **TDM 判定面**：TDM-E-L4-14 节点+2 边（:5351 feed / :5352 feedback）——判据面齐，码面断

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| scorer 本体 | 码 built/装配未接线 | 532 行+测试在册；全仓消费者=services/__init__ 导出+slippage_analyzer 头注，零运行时调用方 |
| L4-14→L4-06 回写边 | **未接线（码缺）** | selector 全文零 scorer 引用（本日 grep 复证，与 TDM 节点自认断链一致） |
| ex_sor 生产可达性 | 传递性不可达 | 唯一桥 execution_engine 自身零生产实例化（M7-04/05 双册同判） |
| TDM 判据面 | built | 节点+边+algo_note+activation 齐备（yaml:2536-2559 实读） |

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | selector 增评分输入（分算法桶累积→选型权重回写） | 接线 0.5-1 天，与 ex_sor 装配批（F55/B2）同批动 session 装配层 | P1 |
| 2 | ex_sor 全族生产装配缺位（本环节父域病） | 归 F55 接线裁定（M7-05 B2：接线 or design-frozen 显式声明） | P1 |
| 3 | RL 执行远期候选（A 股 T+1/涨跌停/拆单限制需改造） | 挂晨审不立项（tdm-growth-blueprint:175 既有裁定） | P2 |

## 五、自审闸三态
**挖干可施工**（三零件 file:line+边实测+断链双源同判；缺口 1 处置明确=selector 评分输入）。

## 六、复跑命令
```bash
grep -n "execution_quality\|quality_scorer" src/zephyr/ex_sor/core/algo_execution_selector.py   # 零命中=断链复证
sed -n '2536,2559p' config/trading_decision_map.yaml                  # TDM-E-L4-14 节点全文
sed -n '5351,5352p' config/trading_decision_map.yaml                  # 两边
grep -n "G4" docs/_working/2026-09-09-tdm-growth-blueprint.md | head -3   # G4 增长批出处
wc -l src/zephyr/ex_sor/services/execution_quality_scorer.py          # 532
```

## 七、刷新批注（2026-09-29 st-finaldel-fresha）

### 9/28 后变更
- `1dd6c70c74`（09-28 全流通·T袋落地）：`algo_execution_selector.py`（+55 行）新增 `QualityPriorProvider` Protocol+`quality_prior` 形参+`FEEDBACK_GAIN=0.20` 选型回写公式；`execution_quality_scorer.py`（+45 行）新增 `ScorerBackedQualityPrior` 评分侧适配器；trading_decision_map.yaml 同批 16 行——**L4-14→L4-06 执行反馈环最后一米已接（码面）**。
- `config/trading_decision_map.yaml` 另有 3 commit（`fa9ae36533` F62 注记／`8b098e31eb` ig_equity_edge 退役／`e21ebc03ec` F34 L9 消费接线）——本卷引用边无语义变化。

### 缺口清单状态修订
- 缺口 1（selector 增评分输入）：**已施工翻面**——QualityPriorProvider／ScorerBackedQualityPrior／FEEDBACK_GAIN 三件在码（1dd6c70c74）；生产装配仍受 ex_sor 全族可达性约束（缺口 2 维持）。
- 缺口 2（ex_sor 生产装配缺位）：维持（归 F55 接线裁定，未见施工）。
- 缺口 3（RL 远期候选）：维持。

### 自审闸三态
- **挖干可施工（维持）**；标题行"断链一米未接"与 §一/§三"selector 零消费评分/未接线（码缺）"断言**已翻面**——§六复跑命令第 1 条（grep 零命中=断链复证）现会命中新增 scorer 引用，勿据零命中误判回退。


---

## 来源：`docs/_working/fullconnect_campaign/g_backtest_gpu/03_f60_drawdown_state_machine.md`

### L46 · 四、缺口清单

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | liquidation_guard 零消费（R1-02 减仓编排断） | 接 P2-04/X-S2 编排工单（与 F43/F46 同批；f47 册判"本车道可修"） | P0 |
| 2 | 盘中 continuous 保命扫描无常驻 | RC/M7 车道+M5 常驻族施工；须登记 process_reaper_keep | P0 |
| 3 | 双五级无互认（交易五级 -3%AUM 秒级 vs TDM L0-L4 日级 4%/6%，同日双触发仲裁序未立法） | Owner 门位（M7-02 B2/TRD-A13 在案） | P1（Owner） |
| 4 | M-55 paper 升档前 Owner 人工接管入口缺位 | 治理面欠账，Owner 门位（f47 册 §五-3） | P1（Owner） |
| 5 | R1-03 护盘白名单数据地基缺（ETF 天量检测需 ETF 日线登记 D109） | 休眠是正确态，勿提前激活（f47 册 §五-4） | P2 |


---

## 来源：`docs/_working/fullconnect_campaign/k_frontend_docs/02_f107_rollback_recovery.md`

### L39 · 四、缺口清单

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 启动挂载会话拉起型（饿死风险） | heartbeat 计划任务兜底（wiring_gap §2.3-5，held_overlap 计数账先落地=Owner 门） | P1 |
| 2 | rollback_state_machine INVARIANTS none | 补状态闭包不变量（production 件质量尺缺口） | P2 |
| 3 | 双契约件+外延域边界 | contract(s) 合并候选+域归属随裁-6 | P2 |


---

## 来源：`docs/_working/fullflow_campaign/02_signal_tdm.md`

### L97 · 六、缺口面（[绿|黄|红]）

## 六、缺口面（[绿|黄|红]）

- **[绿]** 图本体健康：官方 run_checks 实测 fails=0（R1-R13 零 error），186 节点/261 边全连通可解析。
- **[绿]** 信号域代码面健康：signal_ashare 149/149 import 冒烟全绿，零失败零告警。
- **[绿]** 源线判据件质量面：四判据件契约齐（fail-closed/纯函数核/PIT 哨兵/同输入同输出），blueprint+tests 三件套在案。
- **[黄]** **源线六判据 4/6：A01/A02/A03/A05 已落 dev（MATURITY=design），A06 资金流与 A09 财经快讯情绪由另一车队落地进行中——本簿不代修**；且四件 module_ref 均未挂图（挂载=总裁终裁批，流程性缺口非断链）。
- **[黄]** 红节点占位 63 个（module_ref=null，warns=393 全为 warning 级不阻断）；L9 45 节点中 38 个 untested。
- **[黄]** 置信度血肉薄：全图 verified 仅 2 节点（TDM-E-L1 大盘总闸、TDM-E-L3-07-3 其余sleeve选股链），proposed=118、untested=66；策略挂载 verified 仅 8/50。
- **[黄]** 吸收漏斗瓶颈：normalized 592 条策略 vs translated_manifest 仅 10 条候选——翻译/吸收产能是 S2→S3 的流量卡点。
- **[黄]** 8state 生产件（MOD-SIG-037，production）图上无直接挂载，靠 MOD-SIG-104 门与作战室间接消费；sentiment 多件 CONSUMERS 标"待接线"。
- **[黄]** crypto 市场 V0 骨架空壳（4 节点）；L9 B/C 渠道（卫星/社媒/门店客流等 13 源线）声明式 skip 未接。
- **[红]** 无（本段零断链：无 error 级缺口、无 import 失败、无引用死链）。


---

## 来源：`docs/_working/fullflow_campaign/adjudications/req_rbstats_01.md`

### L70 · A5 【施工阻塞，需总包动手】本车道 regime 治本件被 ALGO-NOTE-SYNC 硬拦，而解锁件是"总包代管只读"文件

## A5 【施工阻塞，需总包动手】本车道 regime 治本件被 ALGO-NOTE-SYNC 硬拦，而解锁件是"总包代管只读"文件

- 队列项 `q-20260918-st-ff-rb-stats-20260918-0002`（2 件：
  `src/zephyr/regime/core/regime_detector.py` + `tests/regime/test_rb_stats_regime_failopen.py`）
  状态 **dead**，dead_reason 原文：
  > 门禁 ALGO-NOTE-SYNC 阻断：TDM-E-L1（module_ref=src/zephyr/regime/core/regime_detector.py）
  > ——实现代码被触碰，algo_note_zh 未同 commit 修订（改写该节点 algo_note_zh，或加
  > `note_confirmed: 2026-09-18`）；TDM-E-L1-AGG 同。
- **冲突点**：解锁只有两条路，都要写 `config/trading_decision_map.yaml`，
  而 COORDINATION_LEDGER §2 明文该文件"**总包代管**，TDM 地图……**本轮只读**"。
  车道侧无合法路径自愈（门禁本身正确，是所有权矩阵与门禁的交集出了空洞）。
- 已读门禁源码确认（不猜）：`src/zephyr/gov_enforcement/commit_gates/algo_note_sync_gate.py:70`
  `_NOTE_KEYS = ("algo_note_zh", "note_confirmed")`，且归因锚在 TDM 节点块内——
  `note_confirmed` 无法放在任何其他文件里生效。
- **请总包**（择一）：
  1. 由总包在 `TDM-E-L1` / `TDM-E-L1-AGG` 两节点加 `note_confirmed: 2026-09-18`
     后 `python scripts/commit_queue.py requeue q-20260918-st-ff-rb-stats-20260918-0002`
     （本车道**未改**这两节点的算法语义——只加了缺数可观测位 + 一处 NULL 崩溃治理，
     `note_confirmed` 而非改写 `algo_note_zh` 是贴切的；实测 `Shrinkage` 数值零漂移）；或
  2. 显式授权 rb-stats 车道临时写 TDM 这两行（登记例外，GW 计数）。
- 现状保护：两文件已 `git add` 进暂存区，未被队列丢弃；工作区字节与
  `.runtime/tmp/st-ff-rb-stats-20260918/orig_regime.py.bak` 一致可核。


---

## 来源：`docs/_working/fullflow_campaign/adjudications/req_teeth_01.md`

### L12 · A18 【施工阻塞，需总包动手】`note_confirmed: 2026-09-18` 是**一次性凭证**，不能解锁后续 commit

## A18 【施工阻塞，需总包动手】`note_confirmed: 2026-09-18` 是**一次性凭证**，不能解锁后续 commit

- **任务书原话**（st-ff-teeth-20260918 §1 R-055a ★）：
  "`regime_detector.py` 的 `note_confirmed` 已由总包 22:2x 打到 2026-09-18 并随 `1268f76422`
  落地，所以 ALGO-NOTE-SYNC 这道门现在**不该再拦你**。"
- **实测：仍拦。** 队列项 `q-20260918-st-ff-teeth-20260918-0001`（6 件，含
  `src/zephyr/regime/core/regime_detector.py`）进死信，dead_reason 原文：
  > 门禁 ALGO-NOTE-SYNC 阻断: TDM-E-L1（module_ref=src/zephyr/regime/core/regime_detector.py）
  > ——实现代码被触碰，algo_note_zh 未同 commit 修订（改写该节点 algo_note_zh，或加
  > `note_confirmed: 2026-09-18`）；TDM-E-L1-AGG 同。
- **根因（读门源码确认，不猜）**：`src/zephyr/gov_enforcement/commit_gates/algo_note_sync_gate.py`
  的 INVARIANTS 与 `_collect_node_block_changes*()` 判据都是 **per-commit diff 面**：
  "命中节点须满足之一：a) **同 commit 内**该节点块的 algo_note_zh 行被修订；
  b) **同 commit 内**该节点块新增/更新 `note_confirmed: <日期>`"。
  它读的地图 diff 是 **staged/HEAD 差分**（本件核实：`git show HEAD:config/trading_decision_map.yaml`
  第 261 行确实已是 `note_confirmed: 2026-09-18`）。⇒ **`1268f76422` 把那次
  note_confirmed 用掉了**：HEAD 里"已有"该日期 ≠ 后续 commit 携带该 diff。
  推论：**任何**再触碰 `regime_detector.py` 的 commit 都必须**重新**在地图留一行 diff。
- **为什么这不是车道侧能自愈的**：唯一解锁动作是写 `config/trading_decision_map.yaml`，
  而 COORDINATION_LEDGER §2 判该文件"总包代管"，任务书亦明令"**不要自己去写**，停下来登记"。
- **请总包**（择一，推荐①）：
  1. 对本车道批次**重复**你 22:2x 的解锁动作：`TDM-E-L1` / `TDM-E-L1-AGG` 两节点各加一行
     可差分到的确认注记（例如把 `note_confirmed: 2026-09-18` 改为
     `note_confirmed: 2026-09-18  # teeth R-055a fail-closed`），与队列快照的 6 件
     **同批**落地，然后 `python scripts/commit_queue.py requeue q-20260918-st-ff-teeth-20260918-0001`；
  2. 或显式授权 teeth 车道临时写这两行（登记例外 + GW 计数）。
- **入账建议（协议面，与 R-012 同病）**：给"触碰某 .py 必须先解锁地图"这类门禁补一条
  **一次性凭证**的显式声明——`note_confirmed` 不是"日期窗"而是"随 commit 消耗"，
  派工时把"已打 note_confirmed 所以不会再拦"当前提写成"**只对已落地的那一笔成立**"。
  本役该病已第三次（R-012 pf_alloc/ex_core/risk、A5=本件前手、本件）。
- 现状保护：6 件已入队列快照（`files=6`），工作区字节保持不动，未 `git add -A`，
  未碰他人独占面；本车道其余三条处方（R-055b/c/d）不涉 `regime_detector.py`，**未停等**，
  已另行成批落地。


---

## 来源：`docs/_working/fullflow_mine/skeleton/S03_C_知识供给线.md`

### L34 · 断链点

## 断链点

1. P1 F35：D2 验证方案登记+E2 回传接线两处 module_ref null→补登记+接 runner.py（件已在）。
2. P2 F36：恢复 sch_metaq_audit_reconcile 调度（与 J 段 F92 同根）。
3. P2 F31：alt_data 余下源线逐条收敛（37 null 大头在 F30/F31）。
4. F30 整线未建：16 源线按 TDM 登记逐条挂 module_ref（挂起不入车道，移交总包）。
5. 【未干】缺口移交：37 null 逐条收敛清单。


---

## 来源：`docs/_working/fullflow_mine/skeleton/S04_D_TDM消费链.md`

### L43 · 断链点

## 断链点

1. P0 F48（+F27）：E8/C1 资金链停摆——schedule 新槽 pf_alloc_rebalance_check 零任务挂载，补日历驱动+补跑。
2. P1 F38 宏观腿：macro_regime_sensor.py+macro_indicator_series_map.yaml 不在 HEAD（9ec1ae0f6e 仅落 capability token），macro_data 已在灌水、供数侧就绪，补两实体。
3. F51 币圈：V0 骨架空壳，挂起待裁。
4. 【未干】缺口移交：F49 运行面样本。


---

## 来源：`docs/_working/fullflow_mining/02_tdm_decision/00_overview_a_front.md`

### L62 · 三、待裁项（一行一案，供总筹）

## 三、待裁项（一行一案，供总筹）
1. L4-05/046 分桶考：trade_log 归因字段落地前按"全量代理口径+披露受限"出数，还是冻结待字段？（现 plan 已按代理口径冻结——建议维持，字段落地后复核）。
2. L2-08/L3-05 判据-码面差异：补码面枚举（施工）还是 S4 改判据（D 裁定）？（建议：六顺位补枚举、四段改判据为持续分区间——各自成本最低路径）。
3. P1 体检棒缺位：立施工单挂 dloop（建议），总筹派工定序。
4. BT-P3-007~012（P1 族）验证优先级提级：止损引擎实为 P0 消费件（F59 交界）——建议晨报列 Owner。


---

## 来源：`docs/_working/fullflow_mining/02_tdm_decision/10_f43_p2_t_trade_rebalance.md`

### L44 · 五、堵点与病灶

## 五、堵点与病灶
1. **做T链零编排**（现象：无调度体调 t_trade_coordinator；根因：X/P 流血肉 D60 轮只落了库不落编排；修法：随"做T统一调度"空白件（P 流三空白之二，MOD-SELL-018 planned 语义）立编排工单；量级 2-3 天；本车道可修）。
2. **BT-P0-003 做T成本双节点存疑**（P2-01/P2-03 做T配对 24<30 土规 insufficient_samples，代理口径净价差 mean −45.0bp——开仓前置毛价差≥30bp 下净收益为负，做T经济性存疑；需 Flash F02 重考扩样本；回测车道）。
3. **除权除息污染做T成本归因**（D49 欠账，归公司行动处理 26 号消费侧，非本车道）。
4. **棘轮/复原类"调用方持久化"欠账悬空**：D50 复原语义、止损位 max(old,new) 都写明"调用方持久化"，而调用方不存在——欠账随编排缺位连锁悬空。


---

## 来源：`docs/_working/fullflow_mining/02_tdm_decision/11_f44_p3_pyramiding.md`

### L43 · 五、堵点与病灶

## 五、堵点与病灶
1. **P3 全链零编排**（根因=P 流三空白之编排面；修法：与 P2 编排同批立"持仓流动作执行编排"工单，P3-01 资格门消费 P1-06 动作清单+X-R1-01 熔断态；量级 2-3 天；本车道可修）。
2. **金字塔参数全 proposed 无验证**（BT-P3-015/016 对象 plan=null 阈值未预注册禁跑；修法：批次决策点冻结验收阈值后走 agg_discrimination）。
3. **D58 四件欠账未清**（批次止损/可卖时点/排板切换/持久化复验）——均未落码，随编排工单一并立项。


---

## 来源：`docs/_working/fullflow_mining/02_tdm_decision/12_f45_s1_sell_signal.md`

### L40 · 五、堵点与病灶

## 五、堵点与病灶
1. **S1 全族零消费**（根因=42 号 spec 落码了判定库但编排体从未立项；后果：全部 auto 语义空转、棘轮 clamp 悬空、离场靠人；修法：立"S1 信号扫描编排"工单挂 continuous 节拍，先 paper 档；量级 3-5 天；本车道可修）。
2. **X 流 18 节点验证全 pending**（VAL-20260909-164042，exit_counterfactual+insufficient_samples；消融对照器 ablation.py 已建成但 run_ablation 零生产调用方，实弹待 Owner 放行 §12；SellSignal 流未接入回测=消融动作标注无法自动生成）。
3. **S1-06 编排缺口**（四触发中 KillSwitch 组合级边已画，黑天鹅/K≥3/主力弃庄触发源在码但无扫描循环）。
4. **MOD-RK-09 A股六模式引擎 38 测试全绿零接线**（P1-04 消费缺位属 TD-A P1 面，此处仅登记联动）。


---

## 来源：`docs/_working/fullflow_mining/02_tdm_decision/13_f46_s2_exit_execution.md`

### L47 · 五、堵点与病灶

## 五、堵点与病灶
1. **执行链编排缺位与 S1 同根**：路由/约束/条件单/分批全库成无调用；修法=S1 扫描编排下游直接接 S2-01 路由器（同一工单两段）；量级 3-5 天。
2. **S2-06 状态持久化载体缺位**（M-39 sleeve 治理状态表待施工）——冷却迟滞带/连败阶梯无处落盘。
3. **M-24 跳空分档预案、节前决策表**挂本节点但施工归 position 隔夜风险批次（跨车道依赖，登记勿代修）。
4. **验证欠账**：S2-02..06 五对象（BT-P3-031..035）plan=null 阈值未预注册；exit_counterfactual 真结论待窗口前移。


---

## 来源：`docs/_working/fullflow_mining/02_tdm_decision/14_f47_r1_emergency_lifeline.md`

### L45 · 五、堵点与病灶

## 五、堵点与病灶
1. **R1-02 减仓执行编排零消费**（guard 判了没人执行；修法=接 P2-04/X-S2 编排工单，与 F43/F46 同批；本车道可修）。
2. **盘中 continuous 保命扫描无常驻**（R1 判定轴=组合日盈亏需盘中 NAV 流；当前只有日链快照；修法归 RC/M7 车道+M5 常驻族，须登记 process_reaper_keep）。
3. **M-55 人工干预入口缺位**（paper 升档前无正式 Owner 接管节点——治理面欠账，Owner 门位）。
4. **R1-03 数据地基缺**（ETF 天量检测需 ETF 日线登记 D109；tail_hedge 回测验证未做——休眠是正确态，勿提前激活）。


---

## 来源：`docs/_working/fullflow_mining/02_tdm_decision/18_f51_crypto_skeleton.md`

### L44 · 五、堵点与病灶

## 五、堵点与病灶
1. **全链零基础设施**：无交易所接入/无 WS 行情/无订单面/无钱包——移植成本≈重建一条执行链，非"复制 A 股四流"。
2. **与内收判据的张力**（宪法 §四.2 w5_1：零触发零消费→退役候选）vs markets 声明=Owner D2.5 拍板保留——**本车道不裁，登记待裁**。
3. A 股链路尚未全通（见 10-17 册：S/P 流零编排）——"等 A 股验证后移植"的前置条件本身未达成。


---

## 来源：`docs/_working/fullflow_mining/02_tdm_decision/f37_l0_premarket_plan.md`

### L63 · 七、堵点与病灶

## 七、堵点与病灶

1. **L0 全族验证零开跑**（现象：6 件 backlog 全 plan=None）｜根因：阈值预注册是批次决策点前置工序，无人填｜修法：按 validation_method_registry 推导冻结（BT-P0-001/002 先例=夜班 AI 自裁授权路径）｜工作量：0.5-1 天/件｜本车道可修（走 S3 预检+冻结留痕）。
2. **两拍板体并存语义**：daily_warroom_pipeline（scenario_plan 族）与 daily_decision_orchestrator（decision_daily）并列，前者 testing 后者 experimental——两者对"今日立场档"的产出未声明谁是消费真源｜修法：在 L0 gate 注里钉死主从（orchestrator=放行凭证，warroom=计划卡+校准样本）｜0.5 天｜可修。
3. **L0-04 先验依赖 L0-03 落库链**：昨日先验缺失时四时点预测全退化——未见缺先验时的显式降级登记（消费侧 fail 语义待核）｜待核，非阻断。


---

## 来源：`docs/_working/fullflow_mining/02_tdm_decision/f38_l1_market_gate.md`

### L74 · 七、堵点与病灶

## 七、堵点与病灶

1. **BT-P0-001 冻结未考**：总闸谨慎度分档区分度从未出 verdict——谨慎度数值轴（全组最高风险权重件）仍在"判据未验证"状态运行｜修法：按已冻结 plan 直接开考（数据与判据俱在，零新施工）｜0.5 天｜可修。
2. **BT-P0-002 verdict 回填欠账**：已有 first_valid_run 但 confidence 未翻转｜修法：runner 台账行核查后回填（S7 场景：追溯更新置信度）｜0.5 天｜可修。
3. **六段×五阶段双词汇**：environment_switch 只认六段封闭集、sentiment_cycle 输出五阶段，归并靠调用方——无单一映射真源函数时易漂移（framework_composer.REGIME_STATE_TO_ACTIVATION_PHASE=六段映射唯一真源，2026-09-25 附录C 已切，orchestrator 依赖它）｜修法：把六段↔五阶段↔regime 三方映射钉进唯一真源件｜1 天｜可修。
4. **S0 政策维人工录入**：半自动传感器的最后人工口——自动化替代属 KS 组另类源线（F31 交界），不在本册施工。
5. **六段预算带全 proposed**：数值轴从未回测（C1 域交界，本册只登记）。


---

## 来源：`docs/_working/fullflow_mining/02_tdm_decision/f42_p1_position_checkup.md`

### L68 · 七、堵点与病灶

## 七、堵点与病灶

1. **盘前体检五件编排入口悬空（本环节头号病灶）**：P1-06 裁决中心已经 pf_alloc 装配体接入日循环（分配语义），但体检五件（对账/分级/存活/否决/组合）无任何排程证据证明每天真的跑——"体检结论喂裁决"的体检侧半环悬空｜修法：a) 考古 sim_paper_ledger/AutoRuntime 事件链是否隐式驱动（0.5 天）b) 无则立施工单：P1 体检棒挂 dloop 链（1-2 天）。
2. **X 流转离场评估待接线**（thesis_survival 节点注自认"待接线"）：DEAD 判定产出了但离场评估消费链未闭合——体检结论停在"标记"｜修法：X 流 S1 输入接线（TD-B 组 F45 交界，移交）。
3. **判据-码面差异两处**：P1-04"时间止损/事件禁区"vs 码面 7 触发类型；P1-06"五动作+人工确认"vs IntendedAction 四意图｜修法：S4 场景对齐（改注或补枚举，各 0.5 天）。
4. **P3 批次优先级与风险权重错配**：止损引擎验证登记为 P3 低优先｜修法：提级申请（晨报列 Owner 清单）。


---

## 来源：`docs/_working/fullflow_mining/02_tdm_decision/pending_rulings.md`

### L9 · TD-B 后半待裁登记

# TD-B 后半待裁登记

| # | 环节 | 问题 | 已试路径 | 选项 | 建议 |
|---|------|------|---------|------|------|
| 1 | F51 币圈骨架 | TDM-C-L1..L4 空壳保留还是退役？零触发零消费命中内收判据 w5_1，但 markets: [cn_a, crypto]=Owner D2.5 拍板，且地图原文"等 A 股链路验证后移植"表设计意图 | 生态实测（src 零 crypto 交易模块，仅日历+前端展示+schema 预留）；BT-P3-048..051 全 plan=null | A 保留空壳登记 / B 退役四节点保留日历+schema 预留 / C 最小实件化 C-L1 paper 判定器 | A（零成本；C 违背"A 股先通"前置不建议）；留 Owner 晨报 |
| 2 | F50 C3-03 | 地图注记"编排未接线（裁定#257②）"已滞后：MOD-PA-030 allocation_orchestrator 实测消费 MOD-PA-007，夜批 09-14..09-22 零缺勤 | grep import 链+git a54997e221 夜批证据 | 现在回填 note_confirmed / 留 TDM 例行确认批 | 回填属 S4 场景须 D 裁定留痕——建议随下次 TDM 确认批原子处理，本册仅登记证据 |


---

## 来源：`docs/_working/fullflow_mining/04_knowledge_supply/f30_源线行情基本面.md`

### L48 · 四、堵点与病灶

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|------|------|---------|--------|-----------|
| 1 | 16 节点 module_ref=null 且 red_reason=structural——登记"引用式设计"与"标红"自相矛盾，下游读图者会把在产线误判为缺件 | TDM schema 无"引用式节点"的绿态表达 | 一行案：red_reason 枚举增 `by_ref_design`（或回填 provider 入口路径为 module_ref），16 节点批量翻转；属 TDM 本体改动归 TD/TDM 车道 | 0.5 人日 | 否（登记面），判读已交付 |
| 2 | A11/A14/A15/A16 四节点 data_refs=[] 空 | DS 锚未回填 TDM data_refs 轴（A 档其余 12 线已填） | 补 DS-EIA/DS-IRM/DS-HYPERLIQUID/DS-IO_TABLE 引用键 | 0.5 人日 | 否（TDM 本体） |
| 3 | A02 Tick 历史断档不可补；A15 快照起点 2026-09-18 不可回补 | 外部渠道物理限制（TDX 仅近交易日/自积起点） | 无修法，PIT 已诚实登记；防线=自积不断档（归 M5 巡检） | — | — |
| 4 | kline_cb_incremental 换源（miniqmt→akshare）后 G3 ex_dividend_event 换源缺口 | #ARCH-351 miniQMT 清退 | M1 已立卡，引用不重挖 | — | 否（M1） |


---

## 来源：`docs/_working/fullflow_mining/04_knowledge_supply/f34_知识汇聚.md`

### L40 · 四、堵点与病灶

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|------|------|---------|--------|-----------|
| 1 | 聚合器缺位（module_ref=null，P0） | chainpile/tdm20 两役均"只登记不施工"（纪要 §10 边界） | **最小件**：`scripts/governance/l9_readiness_aggregator.py`（或 src/zephyr/data/ 域）——事件触发（夜批完成事件）→读四源→产单行读数（29 源线+5 图谱+3 快照 × 绿/黄/红+时戳+行数）→写 c1_market.l9_readiness_daily（DateTime64(3)）→module_ref 回填 | 1-2 人日 | **是（本组可移交施工单）** |
| 2 | 下游消费零接线（AGG→TDM-E-FLOW 边有名无实） | 建仓流（pf_alloc）从未声明就绪度输入 | 二期：allocation_inputs 增 readiness 检查（黄/红=降级留痕，仿 anchored_cap 旁路先例——06 号件模式：disabled flag+留痕+可一键切回） | 1-2 人日 | 二期，归 TD/执行域 |
| 3 | V 族 3 条输入边缺失 | edges 登记缺口 | 补 V1/V2/V3→AGG feed 边 | 0.2 人日 | 归 TDM 本体 |
| 4 | AGG 读数若含 B/C 档 13 线会永久红 | 登记面 29 线含未接渠道 | 读数分档：A 档 16 线计健康分，B/C 档单列"挂起"不计红——与 AGG"挂起不入批"语义对齐 | 含在① | 是 |


---

## 来源：`docs/_working/fullflow_mining/05_missing_p0/03_tdm_null_node_attribution.md`

### L77 · 四、堵点与病灶

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| 1 | 38 节点 `module_ref` 为空 → 前端 TDM 视图/`self_evolution_fidelity_gate`/`algo_note_sync_gate` 读到空指针 | F30/F31 标 `missing（登记态）`＝节点先登记、代码后建；无门校验非空 | 分两类处置：已建模块的节点→回填 module_ref（可由生成器从 depgraph 反查）；真未建→保留 null 但需在 F 册行有"待建"标注 | 1 施工袋（生成器，下一波） | 否 |
| 2 | **F 册区间写法与机检不兼容**（上棒因此造假漏项） | 环节真源册为散文表格，无"节点→环节"机生映射 | 出一张机生 `node_id ↔ F号` 映射 yaml（对账表 §五-1 生成器四表之一），F 册改为引用 | 1 施工袋 | 否 |
| 3 | V2 情绪快照同时背负"L02 大盘情绪已定桩独立状态变量"的上棒在途定桩 | 双编号体系未收敛 | 已在 `pending_rulings.md` P-6 登记（不在此裁） | — | 否 |
| 4 | F30 与 F31 对"天气"重复点名（A12 与 F31 描述），A08/A09/A10/A15 按区间落 F30 但语义落 F31 | 区间式归属与语义式归属边界未定义 | F 册 owner 校准区间边界 | 小 | 否 |


---

## 来源：`docs/_working/master_tc_night/lanes/L6_factory/p2_card_ledger.md`

### L9 · P2 卡销账台账（C191）——L02 情绪族缺口×状态

# P2 卡销账台账（C191）——L02 情绪族缺口×状态

> **一句话**：L02 大盘情绪（decision_map_campaign_20260924 links/L02_emotion）挖干交付的净新增缺口逐条台账——两战役（decision_map 二期排产 × master_tc 夜战）立卡前 MUST 查本表，防重复立卡。
> **真源**：`docs/_working/decision_map_campaign_20260924/links/L02_emotion/_INDEX.md`（子簿净新增缺口列=逐条枚举真源）+ 12 子簿 MINE.md（缺口清单节）。
> **计数漂移披露（文档纪律 §4.3）**：INDEX 汇总行称"22 条（施工 14+挂起 8）"，但其行内枚举展开=24 条（施工 15+挂起 9），12 簿缺口列逐条枚举=23 条——三口径不一致。本台账以**簿列逐条枚举 23 条**为准（禁臆删），汇总行计数漂移登记为勘误待归数据班复核。

## 台账（23 行，簿列枚举序）

| # | 缺口 ID | 子簿 | 一句话 | INDEX 态 | 台账状态（两战役查重后） |
|---|---|---|---|---|---|
| 1 | L02-A-G1 | a_builder | pre_open 腿无历史回放（18 日） | 施工 | 待立卡（decision_map 二期排产候选；回放线基建=b_history 已提交） |
| 2 | L02-A-G2 | a_builder | 成分级断供无哨兵 | 施工 | 待立卡（哨兵族与 C1-G1 断供哨兵同型可并立一卡） |
| 3 | L02-A-G3 | a_builder | 情绪双 stage 消费口径未统一 | 施工 | 待立卡（词表面，归治理班边界） |
| 4 | L02-B-G1 | b_history | live/replay 撞键无机械守卫 | 施工 | 待立卡（b_history 代码已在主区，守卫随其消费面接线批） |
| 5 | L02-C1-G1 | c1 | 连板高度/封板率无替代源，daban 断供即退化 | 施工 | 待立卡（daban 采集链治理归数据班/L15 车道——INDEX 边界，非本战役立卡） |
| 6 | L02-C1-G2 | c1 | obs=16→120 自然生长无排期跟踪（预承诺 2027-03） | 施工 | 待立卡（低优先：时点预承诺制，登记跟踪即可） |
| 7 | L02-C2-G1 | c2 | 炸板率未独立子项 | 挂起 | 待立卡（挂起理由=外部两源支持并列，单独立项收益低；与 CNS 族事件轴语义相关——C232 event_axis 的 BUSTED 事件可作其数据面，接线随二期） |
| 8 | L02-C2-G2 | c2 | overlay t3_leader_score 与本成分共用晋级率无共享件 | 施工 | 待立卡（重构面，归 overlay 消费族） |
| 9 | L02-C3-G1 | c3 | 广度双口径无对表 | 施工 | 待立卡 |
| 10 | L02-C3-G2 | c3 | stub 段诚实标记未落表 | 施工 | 待立卡（文档面小件） |
| 11 | L02-C4-G1 | c4 | 成交额未市值归一 | 挂起 | 维持挂起（挂起理由在册：归一口径须因子面评审，非纯代码件） |
| 12 | L02-C5-G1 | c5 | 考试回补史未回流 | 挂起 | 维持挂起（DU-03 销口需重开依赖数据班复核） |
| 13 | L02-C5-G2 | c5 | 静默无哨兵 | 挂起 | 与 #2 A-G2 哨兵族并立一卡（防重复：同一哨兵基座） |
| 14 | L02-C6-G1 | c6 | rule/market 日期错位 3 日 | 施工 | 待立卡（数据面修复件） |
| 15 | L02-C6-G2 | c6 | experimental 分支进生产写库 | 挂起 | 待立卡（LLM 分支治理，涉生产写路径——medium 门位评审后立） |
| 16 | L02-D/E-G1 | d_e | auction 17 行数据孤本（HEAD 无写手） | 挂起 | 维持挂起（复职批依赖在册） |
| 17 | L02-D/E-G2 | d_e | auction stage 分母残缺 | 挂起 | 维持挂起（同 #16 依赖链） |
| 18 | L02-F-G1 | f_legacy | 档位计/温度计无口径词表 | 施工 | 待立卡（词表面，与 #3 同族可并） |
| 19 | L02-F-G2 | f_legacy | intraday 环 production 却不挂任务 | 挂起 | 待立卡（挂任务=调度面，与 F076 计划任务族排产窗同批） |
| 20 | L02-G-G1 | g_forecast | 环节级"无概率表"结论需更正（文档面） | 施工 | 待立卡（纯文档销口件） |
| 21 | L02-G-G2 | g_forecast | Brier 链路无机读校验 | 挂起 | 待立卡（机读校验件，可随考试族排产） |
| 22 | L02-H-G1 | h_consumption | sector_preference 只产 pre_open 侧、覆盖≈0 | 施工 | 待立卡（消费面主缺口，价值最高；与 CNS-10 类消费接线同法） |
| 23 | L02-H-G2 | h_consumption | 情绪消费方无机读登记表 | 挂起 | 待立卡（机读登记=consumption_census 族能力复用，非新造） |

## 防重复立卡规则（两战役共同遵守）

1. decision_map 二期排产 / master_tc 夜战及其继任班次，对上表 23 条任一立卡前，先查本台账状态列；立卡后**回填本表**（卡号列注记），禁两战役各立一张。
2. 并组建议（内收 §4.2 同域收敛）：#2+#13（哨兵族一卡）、#3+#18（词表族一卡）、#16+#17（auction 复职链一卡）——并组后净立卡数 23→19。
3. 本夜 C75（CNS-01 计算链）不直接销上述任何一条（CNS 面与 L02 缺口面正交）；#7 与 C232 event_axis 存在数据面协同（BUSTED 事件=炸板率独立子项原料），已在 #7 行注记。
4. master_tc 夜战对 L02 的卡面仅 C75（挂 F011 TDM 交叉轴）——已核 00_orchestration §二，无重复。


---

## 来源：`docs/_working/matrix_campaign/mining/00_stage_skeleton.md`

### L304 · 4. 与 chief_fullchain（B1 骨架 + 02 缺口账）交叉验证

## 4. 与 chief_fullchain（B1 骨架 + 02 缺口账）交叉验证

- chief 01 §1 表：TDM 182（entry132/position18/exit19/portfolio13）/257 边/24 cells——本车道机械复算全一致（flow 计数 132/18/19/13；edges 257；cells 24，states 六态）。
- chief 01 §1 表：FACTORY 341/仅17边/built315+partial12+pending14/counts 块空——本车道复算全一致。
- **矛盾点（新）**：chief 01 §2 丙/丁段 TDM 分族账——ENV-14"组合与预算"记 6 节点，而本车道同口径（F-FLOW+C1+C2，C3 归 ENV-16）应为 **7**（TDM:L161,4114,4150,4206,4248,4287,4321）；且四枚终端聚合点中 E-FLOW/F-FLOW 在 chief 21 环节分表无显式落位（ENV-08=L0+L1=15、ENV-16=C3+E9=15 均不含），chief 分组合计 180 vs 全集 182 差 2。属分组账不闭合，不影响 182 全集本身。
- chief 02 §4"骨架断链组"（F16-F20 进货车道复活/D13-20 竞价窗闸恒 skipped 等）属图13/数据链域，本车道只在 st_data_legs 引用不代挖。
- chief 02 §1 P0 实盘 Flip 组（GAP-1 bridge-execute sim→real 等）与 st_e7 的 pending 件 FAC-E7-M-006（MOD-BT-222 模拟盘日链接电执行体，SPM:L4137）互为印证——工厂侧该腿标 pending，总包侧标"他队施工中"，两账一致。


---

## 来源：`docs/_working/matrix_campaign/mining/m1_alt_sources/99_negative_results.md`

### L55 · B. 缺数据（15 条）——数据不在库或渠道未接

## B. 缺数据（15 条）——数据不在库或渠道未接

### #7 TDM-E-L9-A11 能源库存（EIA）
- 动作: CH 实查 edb_data + 全库 EIA/库存关键词扫描。
- 实测: **edb_data 0 行（空表壳）**；全库无 EIA 原油库存/能源库存表；TDM data_refs 为空（DS 锚=EIA 但无 DS 条目落地）。
- 结论: **缺数据**。因子假设本身成立（库存意外变化领先油价与石化链——EIA 周三发布、周度频率、发布时点锚定 PIT 干净），卡骨架可预填但无米下锅。
- 缺什么: EIA API 接入入库（周度：crude oil/gasoline/distillate stocks + 意外值=实际-预期）。
- 复活条件: EIA 周度库存入库（≥5 年历史回补）后按事件研究/条件因子重开。

### #8 TDM-E-L9-B01 卫星影像
- 实测: 无任何影像/遥感表。TDM: 渠道未接（Copernicus 免费/Planet 商业），PIT 未评估。
- 结论: **缺数据**。假设可写（物理量领先官方数据——库存/夜光/车位），但接入=资金门位+数据工程重投入，非本车道可解。
- 复活条件: 接入门位裁定后另立项（净零纪律：须先声明替代/合并条目）。

### #9 TDM-E-L9-B02 美国官方天气/海洋（NWS）
- 实测: 无 NWS/NOAA 表。在库天气面（weather_data/alt_sz_*）全部为中国/深圳域，不覆盖美国。
- 结论: **缺数据**。假设（极端事件预警能源中断与减产）依赖美国灾害面+全球能源链映射，两者均不在库。
- 复活条件: NWS API 免费接入 + 与 A12 事件研究法合流。

### #10 TDM-E-L9-B03 招聘JD
- 实测: 无招聘/职位表。
- 结论: **缺数据**。假设（扩缩招领先营收）成立且有卖方先例，但抓取合规+清洗工程量大（岗位文本→行业/公司映射是独立工程）。
- 复活条件: 明确合规抓取方案 + 公司-JD 映射字典立项后重开。

### #11 TDM-E-L9-B04 电商价格
- 实测: 无电商价格表。TDM: Keepa 付费 API 未购。
- 结论: **缺数据**（渠道=资金门位）。
- 复活条件: 付费渠道裁定 + 高频通胀/单品景气映射的需求确认。

### #12 TDM-E-L9-B05 招投标
- 实测: 无招投标表。政采网/公共资源平台未接。
- 结论: **缺数据**。假设（中标领先营收与基建链景气）成立且 A 股适配性好（中标金额→营收可验证），爬取工程中等。
- 复活条件: 采集立项后重开（事件型：中标公告日 PIT）。

### #13 TDM-E-L9-B06 社媒舆情 X/Reddit
- 实测: 无社媒表。API 未购；且海外散户情绪→中概/A股联动假设的样本期（GameStop 后）体制极不稳。
- 结论: **缺数据**（渠道+假设先验均弱）。
- 复活条件: 渠道接入后先做中概联动存在性检验，再谈因子。

### #14 TDM-E-L9-B07 雪球/股吧散户情绪
- 动作: CH 实查代理面。
- 实测: 雪球/股吧无专表（TDM: 雪球强反爬）；**代理=c1_market.stock_hot_rank（东财人气榜）7,393 行，仅 2026-08-04→09-30**（1,763 票，rank_type×2），另有 sentiment_panel 仅 40 行（2026-09）。
- 结论: **缺数据**。代理管道已通但 2 个月历史不可考；人气榜 rank 变化=注意力代理假设可预填。
- 复活条件: 代理表历史回补 ≥2 年，或雪球替代渠道落地。

### #15 TDM-E-L9-B08 APP榜单
- 实测: 无 APP 排名表。七麦会员/SensorTower 均未购。
- 结论: **缺数据**（付费渠道）。
- 复活条件: 渠道裁定 + 目标公司清单（互联网/手游）确认。

### #16 TDM-E-L9-B09 进出口贸易
- 实测: 无分商品贸易表；c1_market.macro_data 有全国进出口总量（DS-101 中国宏观面）但无商品级量价；alt_sz_port_monthly 为深圳港口月度（单城）。
- 结论: **缺数据**。UN Comtrade 未接；注意 A08 的 BDI 已提供贸易景气的"量"代理——本源线的增量=商品级结构，当前无源。
- 复活条件: Comtrade API 免费接入（月度/HS 分商品）后重开；与 A08 卡做同源预检。

### #17 TDM-E-L9-B10 信用卡/支付消费
- 实测: 无支付/消费高频表。
- 结论: **缺数据**。SpendingPulse proxy 面向美国市场且未接；中国对应物（银联/支付宝聚合指数）无公开机械渠道。
- 复活条件: 出现可机械接入的中国消费高频代理（公开指数 API）再评估。

### #18 TDM-E-L9-C01 实时门店客流
- 实测: 无表。TDM 自述"C 档无渠道：想得到无机械接入渠道，挂起不入批"。
- 结论: **缺数据**（结构性无渠道）。如实维持 TDM 判定，不硬凑替代。

### #19 TDM-E-L9-C02 银行网点/信贷活跃
- 实测: 无表。C 档无渠道。
- 结论: **缺数据**（结构性无渠道）。宏观信贷面（M2/社融）已在 DS-101 中国宏观册，属 A10/宏观域，不救本条。

### #20 TDM-E-L9-C03 直播电商实时成交
- 实测: 无表。TDM 自述"无正式渠道，挂起不入批"。
- 结论: **缺数据**（结构性无渠道）。

### #21 TDM-E-L9-G5 图谱·投入产出传导
- 动作: 查 TDM algo_note + CH 表清单。
- 实测: ig_io_edge 16,859 条（2020 版 153 部门直接消耗系数）在 **PG 域**；TDM 自述**边 100% 挂零**（部门码与 ig_node 两套 id 体系）。
- 结论: **缺数据（id 缺口阻断）**。数据"在"但不可消费——挂零边=图不连通=任何传导计算无输入。同 A16（A16 是源线身份、G5 是图谱身份，同一物理阻断）。
- 缺什么: 两套 id 的映射桥（WP-0.5 在案）。
- 复活条件: id 桥建成 → 与 A16 合并重开"IO 加权传导因子"（同一消费件，禁两条源线各建一套=净零纪律）。


---

## 来源：`docs/_working/matrix_campaign/mining/st_crypto_mining.md`

### L8 · st_crypto —— TDM 币圈族（C-L1/L2/L3/L4，4 节点，全缺口）

# st_crypto —— TDM 币圈族（C-L1/L2/L3/L4，4 节点，全缺口）

- 真源: `config/trading_decision_map.yaml`；行号=TDM:L*。类别=H9 §1.10（并入各 flow 判缺，本册单列）。
- 计数: 4 全 C，全 L4（无 module_ref、无 mounts、conf=untested）。
- 归属口径：这 4 枚在 00 §2 各 flow 表中扣除、集中于本册，保证 182 零重复计数。

## 1. 族内节点全清单与接线现状

| node_id | 名称 | 所在 flow | 类别 | 接线级 | 现状 | 行 |
|---|---|---|---|---|---|---|
| TDM-C-L1 | 币圈大盘总闸 | entry | C | L4 | 无模块无挂载；market=crypto | TDM:L4594 |
| TDM-C-L2 | 赛道选择 | entry | C | L4 | 同上 | TDM:L4616 |
| TDM-C-L3 | 币对选择 | entry | C | L4 | 同上 | TDM:L4637 |
| TDM-C-L4 | 币圈买卖点 | entry | C | L4 | 同上 | TDM:L4658 |

## 2. 缺口与可考性判定

- 全域 L 级缺口（H9 L5）：无 crypto 行情载荷、无 crypto 回测，全仓 grep 仅 backlog 提及（H9 §1.2 C-L1 证据）。
- 唯一图内锚点：L9-A15 源线·加密永续/费率（TDM:L5035，同为图纸）。
- **Owner 门位在案**：chief 02 §6 Owner 门位组含"F51 币圈退役"——币圈域存在"退役 vs 建设"的 Owner 级未决议题；本车道立场：在 Owner 裁定前，crypto 4 节点的缺口不排期、不备料，只登记。

## 3. 一句话修复建议

先请 Owner 裁 F51（退役 or 独立域立项）；若建设，按 L5 独立域走"行情载荷+回测+四节点全链"单独立项，禁搭 A 股考卷便车。

## 4. 交叉验证

- H9 §1.10 判定与计数口径一致（4 枚已计入其 §1.2/1.3/1.4 各节，本册单列不重复计）。
- chief B1 分组把 crypto 计入 ENV-08/09/10/11 各环节（其 L1=10/L2=30/L3=26/L4=16 均含 C）——两种口径对全集 182 无损，99 册双口径对平。
- SPM 全图无 crypto 专属节点（341 内 grep 无）——工厂侧连占位都没有，属两图共同空白。


---

## 来源：`docs/_working/matrix_campaign/mining/st_e6_intake_monitor_mining.md`

### L34 · 2. 接线现状与缺口判定

## 2. 接线现状与缺口判定

- 已接线：入库链（查询/编排/追加写入器）+ 监控链（模型漂移/信号降级/分布漂移三监控 + 4 级告警）+ 日度快照三件（M-006/007/008）全 built。
- 缺口：图内零 pending。可考性：内务层不进回测考卷；其衰减结论经 feedback E6→E1 反哺进货方向（SPM feedback_loops[1]）。
- 观察位（登记不判）：M-010 信号降级监控与 TDM-F-C3-05 可靠度养成挂同一模块族（TDM:L4549 mounts 含 MOD-SIGQC-003/005/006、MOD-BT-018）——两图共享衰减族，防双头维护。


---

## 来源：`docs/_working/matrix_campaign/mining/st_l2_sector_mining.md`

### L8 · st_l2_sector —— TDM 板块选择（L2 cn_a，29 节点，全 C——最大缺口带之一）

# st_l2_sector —— TDM 板块选择（L2 cn_a，29 节点，全 C——最大缺口带之一）

- 真源: `config/trading_decision_map.yaml`；行号=TDM:L*。类别=H9 §1.3（全族缺口，统一证据=考卷九维无板块维、行业数据只作 A1 中性化分组，H9 §1.3）。
- 计数: 29 全 C；接线级: L3 live 在岗 27 / L4 组骨架 2（E-L2、E-L2-05）。crypto C-L2 归 st_crypto。

## 1. 族内节点全清单与接线现状

| node_id | 名称 | 接线级 | 模块（module_ref/mounts） | 行 |
|---|---|---|---|---|
| TDM-E-L2 | 板块选择（组骨架） | L4 | 无 module_ref | TDM:L657 |
| TDM-E-L2-01 | 板块强度综合 | L3 | sector_strength_aggregator；MOD-SIG-144 | TDM:L686 |
| TDM-E-L2-01-1 | 结构强度评估 | L3 | sector/sector_analyzer；MOD-SIG-058/095/097/100/101/120；strat STR-DABAN-003 | TDM:L721 |
| TDM-E-L2-01-2 | 动量活跃度排名 | L3 | data/sector_ranking_engine | TDM:L754 |
| TDM-E-L2-01-3 | 多周期动量加权 | L3 | sector/sector_momentum | TDM:L786 |
| TDM-E-L2-01-4 | 板块资金流聚合 | L3 | sector/sector_breadth；MOD-SIG-088；strat STR-DABAN-002 | TDM:L817 |
| TDM-E-L2-01-5 | 市场级调节注入 | L3 | regime/market_forecast_fusion；MOD-SIG-063/147 | TDM:L850 |
| TDM-E-L2-02 | 轮动序列追踪 | L3 | sector/sector_divergence；BM-SEL-08 已映射（H9 §1.9） | TDM:L883 |
| TDM-E-L2-02-1 | RRG 轮动序列 | L3 | sector/sector_rrg | TDM:L915 |
| TDM-E-L2-02-2 | 单板块轮动预警 | L3 | sector/sector_analyzer；MOD-SIG-119/121 | TDM:L946 |
| TDM-E-L2-03 | 调整周期进度 | L3 | sector/sector_adjustment；BM-SEL-09 已映射 | TDM:L979 |
| TDM-E-L2-03-1 | 扩散指标进度追踪 | L3 | adjustment_cycle_tracker | TDM:L1009 |
| TDM-E-L2-04 | 板块级市场状态 | L3 | core/sector_ecology_judge；MOD-SIG-061 | TDM:L1043 |
| TDM-E-L2-04-1 | 轮动状态五分类 | L3 | sector/sector_rotation_state | TDM:L1075 |
| TDM-E-L2-04-2 | 虹吸态识别 | L3 | sector/sector_siphon；MOD-SIG-113 | TDM:L1105 |
| TDM-E-L2-05 | 水温响应（组骨架） | L4 | 无 module_ref | TDM:L1138 |
| TDM-E-L2-05-1 | 水温档推导 | L3 | sentiment/sentiment_cycle | TDM:L1166 |
| TDM-E-L2-05-2 | 信号响应三件套 | L3 | sector/sector_gate；MOD-SIG-059/094/107/131 | TDM:L1197 |
| TDM-E-L2-06 | 板块个股传导 | L3 | core/sector_conduction | TDM:L1230 |
| TDM-E-L2-06-1 | 三级放行门槛 | L3 | sector/sector_gate；MOD-SIG-104 | TDM:L1260 |
| TDM-E-L2-06-2 | 龙头识别定位 | L3 | sector/sector_leader | TDM:L1292 |
| TDM-E-L2-06-3 | 强度加权传导 | L3 | core/sector_conduction | TDM:L1324 |
| TDM-E-L2-07 | 回踩质量分级 | L3 | sector/sector_pullback；MOD-SIG-116 | TDM:L1356 |
| TDM-E-L2-07-1 | 回踩ABC判定 | L3 | sector/sector_pullback | TDM:L1389 |
| TDM-E-L2-08 | 板块生命周期判定 | L3 | sector/sector_momentum_persistence；strat STR-MOMTREND-003 | TDM:L1423 |
| TDM-E-L2-09 | 催化剂识别 | L3 | screening/event_driven_screener；MOD-SIG-106 | TDM:L1454 |
| TDM-E-L2-09-1 | 事件图谱传导 | L3 | intelligence/news_chain_node_linker；6 mounts | TDM:L1487 |
| TDM-E-L2-09-2 | 冲击标的生成 | L3 | intelligence/chain_impact_resolver | TDM:L1518 |
| TDM-E-L2-10 | 同源补涨比价 | L3 | supply_chain_momentum | TDM:L1549 |

## 2. 缺口与可考性判定

- 全族 C：考卷维度空间（因子标准化/合成/Top-N/定尺寸/调仓/单票帽/宇宙/换手 λ 九维）无板块维；sws2021_l1 行业锚在考卷只用于 A1 中性化 demean（H9 §1.3 统一证据）。
- live 面厚（27/29 有在岗模块）而考卷面零——"补考"路径明确：M3 建议的 sws2021_l1 行业动量 Top-K × 板块内个股两层排序是最小可考核（H9 §2 M 级 M3，行业锚已在 schema:84-91）。
- 可考性分级：M3 主干=S 级偏上（行业锚在册）；轮动五分类/虹吸/水温/回踩 ABC/传导等=逐个 M 级；事件图谱传导（依赖 L9 G 系图谱）=L 级。

## 3. 一句话修复建议

先落 M3 最简板块主干考卷核（行业动量两层排序），再按 BM 映射位（SEL-08/09）优先补轮动与调整周期两支。

## 4. 交叉验证

- H9 §0"大缺口族=L2 板块 29"对本册全族判定负责；本册补充=逐节点 live 模块在岗面（27/29），H9 未列。
- chief B1 ENV-09（TDM L2=30，含 C-L2）计数一致；battle_map_steps 已映射 BM-SEL-08→L2-02、BM-SEL-09→L2-03（H9 §1.9，PG 快照 2026-10-05）。
- SPN 层面对应：SPM E1D 板块盘中聚合/板块报告构建（SPM:L1056/1069）与 E8-M-033 板块分布比较选优（SPM:L4739）是本族的工厂侧邻居——板块能力分散在三图，矩阵考试宜合并命题。


---

## 来源：`docs/_working/matrix_campaign/mining/st_x_exit_mining.md`

### L8 · st_x_exit —— TDM 离场与应急保命（exit_flow，19 节点——最大缺口带）

# st_x_exit —— TDM 离场与应急保命（exit_flow，19 节点——最大缺口带）

- 真源: `config/trading_decision_map.yaml`；行号=TDM:L*。类别=H9 §1.7。
- 计数: 19 = A1 / B3 / C13（含组 3）/ D2。

## 1. 族内节点全清单与接线现状

| node_id | 名称 | 类别 | 接线级 | 引擎旋钮/模块 | 行 |
|---|---|---|---|---|---|
| TDM-X-FLOW | 输出离场信号（终端聚合） | C | L4 | 无 module_ref；strat STR-VREV-001（live 挂载与回测缺口并存，防误读注记见 00 §7.10）；**考卷无任何主动离场**（_c4_engine:561-616 无止损/止盈路径） | TDM:L135 |
| TDM-X-R1 | 应急保命（cross_cutting） | B | L2 | security/access_control/kill_switch；6 mounts（AU×3/L04/RK×2）；模拟盘回撤六态机 defensive_only 已接（sim_daily_runner.py:1318,1356-1394）；**BM-BUY-02-D 已映射** | TDM:L3502 |
| TDM-X-R1-01 | 熔断分级判定 | B | L2 | risk/core/drawdown_state_machine；4 mounts；c2 CRISIS MaxDD 判据在册 | TDM:L3546 |
| TDM-X-R1-02 | 熔断期减仓与持仓处置 | B | L2 | drawdown_liquidation_guard；模拟盘 KILL→execute_kill_switch_liquidation（sim_daily_runner.py:1465） | TDM:L3584 |
| TDM-X-R1-03 | 护盘资产定向加仓白名单 | C | L3 | position/core/defensive_asset_whitelist；state_matrix 防御格内容=Owner 资金门位（AI 禁自填，H9 S4） | TDM:L3617 |
| TDM-X-S1 | 卖出信号收集评分（组骨架） | C | L4 | 无 module_ref（mounts MOD-SELL-006/016）；**BM-SELL-03 已映射** | TDM:L3453 |
| TDM-X-S1-01 | 信号收集与六桶分类 | C | L3 | sell_signal_collector（live） | TDM:L3658 |
| TDM-X-S1-02 | 止损族判定 | C | L3 | stop_loss_strategy；MOD-RK-35/SELL-015；研究样板 ATR3 止损带在册（indicator_consumption_demo.py:34），**考卷零实现**；**BM-SELL-04-B 已映射** | TDM:L3689 |
| TDM-X-S1-03 | 止盈族判定 | C | L3 | take_profit_strategy（live）；**BM-SELL-04-A 已映射** | TDM:L3732 |
| TDM-X-S1-04 | 破位与情绪退潮信号 | C | L3 | breakout_failure_detector（live） | TDM:L3762 |
| TDM-X-S1-05 | 信号融合与紧迫度评分 | C | L3 | sell_signal_fusion_engine；MOD-SELL-008/009；**BM-SELL-02 已映射** | TDM:L3800 |
| TDM-X-S1-06 | 强制清仓绕过通道 | D | ND | strategy_abnormal_exit_orchestrator；MOD-TRADING-011——实盘异常处置 | TDM:L3837 |
| TDM-X-S2 | 离场执行（组骨架） | C | L4 | 无 module_ref | TDM:L3479 |
| TDM-X-S2-01 | 执行方式路由（critical） | C | L3 | sell_execution_planner（live） | TDM:L3875 |
| TDM-X-S2-02 | T+1 与涨跌停约束 | A（近似） | L1 | 封板闸双向+shift(1)（_c4_engine:453-497）；失真=日级 close 判封板（H9 §4.4） | TDM:L3918 |
| TDM-X-S2-03 | 执行时段路由 | C | L3 | ex_sor/core/sell_session_router（live）；考卷单一收盘口径 | TDM:L3958 |
| TDM-X-S2-04 | 本地条件单管理 | C | L3 | ex_core/local_order_queue；日内价格触发语义，考卷无日内路径 | TDM:L4000 |
| TDM-X-S2-05 | 分批止盈执行 | C | L3 | sell_decision/core/scaling_out（live）；考卷调仓日一次性全额 | TDM:L4036 |
| TDM-X-S2-06 | 卖出闭环与退出效率 | D | ND | sell_execution_quality_tracker——执行质量遥测；**BM-SELL-09 已映射** | TDM:L4069 |

## 2. 缺口与可考性判定

- X-FLOW=C 是全图最重单点：离场终端在考卷零语义（被动清仓=跌出 Top-N）。
- B3（R1 保命轨）模拟盘平面已接、网格考卷无——T3b 的 M2（回撤六态机日级向量化）是开考路径。
- C13 中 M 级可考：S1-02/S1-03（H9 M1：ATR 止损带/移动止盈/目标价向量化，研究样板可翻译）、S2-05（分批止盈随 M4）；L 级：S2-04 条件单（tick 平面）；D2 枚=实盘遥测。
- BM 映射集中带：11 条 tdm_node_id 映射中 **8 条落 X/P 族**（H9 §1.9"讽刺点"：作战地图挂 TDM 最密处=考卷零实现带）——本族是 BM↔考卷落差最大层。

## 3. 一句话修复建议

T3b 前置落 M1+M2（止损止盈档+熔断档作新增考维，重标定耗时口径后开考）；R1-03 防御格内容留给 Owner 门位，禁代填。

## 4. 交叉验证

- H9 §1.7 判定全转录对平；chief B1 ENV-13（exit_flow=19）计数一致。
- TDM state_matrix：euphoria/distribution 两态 PP-001 无防御型 sleeve、格子 pending-owner-adoption（H9 §1.2 R1-03 证据引 state_matrix cells）——六态名与 24 cells 计数两图一致（00 §4）。
- SPM 邻居：FAC-E7-M-022 月度危机演练件（SPM:L4327）与 R1 熔断族同域；FAC-E8-M-031 前瞻概率止损（SPM:L4717，forward_stop_loss）是 X-S1-02 的工厂侧近亲——止损件分散三处，矩阵考试宜合并命题。

### L37 · 2. 缺口与可考性判定

## 2. 缺口与可考性判定

- X-FLOW=C 是全图最重单点：离场终端在考卷零语义（被动清仓=跌出 Top-N）。
- B3（R1 保命轨）模拟盘平面已接、网格考卷无——T3b 的 M2（回撤六态机日级向量化）是开考路径。
- C13 中 M 级可考：S1-02/S1-03（H9 M1：ATR 止损带/移动止盈/目标价向量化，研究样板可翻译）、S2-05（分批止盈随 M4）；L 级：S2-04 条件单（tick 平面）；D2 枚=实盘遥测。
- BM 映射集中带：11 条 tdm_node_id 映射中 **8 条落 X/P 族**（H9 §1.9"讽刺点"：作战地图挂 TDM 最密处=考卷零实现带）——本族是 BM↔考卷落差最大层。


---

## 来源：`docs/_working/mineloop_campaign/R1_L11_ledger.md`

### L142 · 8. 假绿风险与阻塞（本车道上报口径）

## 8. 假绿风险与阻塞（本车道上报口径）

- **假绿风险一（结构性）**：板块层两节点的既有真卡都以"卡内重算口径"作答，而生产喂值在 MOD-SIG-144；
  若这批卡出分后被写回 `TDM.nodes.*.confidence`，会把"代理口径的结论"当成"生产件的结论"。
  建议总包在分数册侧对本层所有卡加"重算口径/在产口径"标签，本车道未改任何前役件与注册表。
- **假绿风险二（样本地板）**：涨停比>10% 的"极强"档历史上极稀（可能 <60 日），
  本车道 calibration/02 已写死"稀疏档判数据不足非通过、禁报通过也禁删档"；执行器若按缺桶静默跳档，将产出假通过。
- **阻塞**：两臂卡的 arm driver（各 ≤60 行）与 L2-04 分母聚合查询归总包（本车道禁跑生成器、禁写分数册、禁 git）；
  21:00–22:30 CH 禁令使本车道 ⑥向全部依赖在册事实，未做任何新实测。


---

## 来源：`docs/_working/mineloop_campaign/R1_L12_ledger.md`

### L177 · 6. 收尾汇总（本车道）

## 6. 收尾汇总（本车道）

- **节点总数**：5（TDM-E-L2-07、TDM-E-L2-07-1、TDM-E-L2-09、TDM-E-L2-09-1、TDM-E-L2-09-2）。
- **新卡总数**：7；卡名与 status（全为新建文件，未触碰任何既有卡件与骨架件）：
  1. `TDM-E-L2-07/comparison/03_追高与低吸胜率对照` — preregistered
  2. `TDM-E-L2-07/ablation/03_时间窗外不评级并入观望的边际` — preregistered
  3. `TDM-E-L2-07-1/ablation/03_强度维单位口径错配` — preregistered
  4. `TDM-E-L2-07-1/calibration/03_死常量两腿_结构破坏与超窗横盘` — preregistered
  5. `TDM-E-L2-09/comparison/02_催化剂加权形式板块恒定与标的指数衰减` — preregistered
  6. `TDM-E-L2-09/calibration/05_板块级盘前新闻情绪催化剂腿` — blocked_on_data
  7. `TDM-E-L2-09-2/ablation/03_图谱PIT有效行过滤臂` — blocked_on_data
- **族分布**：calibration 2、ablation 3、comparison 2、shadow 0。
- **status 分布**：preregistered 5、blocked_on_data 2、blocked_on_impl 0。
- **未挖长尾**：见 §4（8 条明列，其中 2 条只需一条 SQL 即可解锁，均已点名缺哪表哪段）。
- **交叉复挖建议（20% 名单，含前役封矿不成立的具体节点+理由）**：
  1. **TDM-E-L2-08**（前役 mined_out）：其 blocked 理由同样是"涨停池仅 28 日"，但本车道发现 stk_limit 触及判定
     （不复权 kline_daily 配 stk_limit，§3-P7 满史）足以构造"板块触及涨停家数占比"的生命周期确认腿替代 limit_up_pool 时序⇒ 同一 blocked 理由可复制翻案。
  2. **TDM-E-L2-03**（前役 mined_out）：与本车道 L2-07-1 共用 sector_pullback 同族常量与"扩散维 0.3 权重不可算"的
     blocked 声明；死常量/单位口径的审计法可平移（其 80% 门控与倒 U 先验对冲是否也在码有死常量）。
  3. **TDM-E-L2-01-1 / L2-06-2 / L2-03-1 / L2-10**（前役 blocked_on_data，理由=成分口径）：
     本车道无新数可查，但 09-2 卡揭示"blocked 理由须与代码在册读取口径对表"的通则——建议逐条复挖其 blocked 表述是否也错置了表名。
  4. **TDM-E-L2-09-1**（本车道维持结论）：一旦 valid_to 历史分布（§4-8）实测为有值，09-1 与 09-2 两张 blocked
     卡可同时转 preregistered，是全班解锁成本最低的一对。
  5. **L2-05/L2-05-2**（前役 mined_out，⑤向只登记一句）：fallback 字段"DS-107 缺失→降权"在 L2-09，
     同族 fallback 面（水温档缺失时的放行比例）建议按本车道 comparison 形式对照法复挖一次。
- **本车道对全战役的一条硬结论**：封矿与 blocked 的**理由文本必须与代码在册读取口径对表**——
  本车道 5 个节点里 3 处 blocked 理由（news_data 断供、图谱无版本化、在码缺时间窗）都与实读源码或实读地图不符，
  错置理由会把可解锁的面永久冻结成"不可考"；建议全班把"④后端断言须带 文件+行号+原文"设为卡面硬必填。


---

## 来源：`docs/_working/mineloop_campaign/R1_L13_ledger.md`

### L55 · 2. 车道收尾账

## 2. 车道收尾账

- **本车道节点总数**：3（全部为复挖对象，前役 L4 自报 mined_out）。
- **复挖结论**：**三节点封矿全部推翻**（各条证据见 §1.1，均为"节点级未挖长尾"，非扩档）。
- **新卡总数**：8（全部只新建文件，零触碰已存在卡件/骨架件；NN 接续现有编号 PFLOW→03/04、P1→03/04、P2→04/05/06/07）。
  机检（本车道实跑，只读校验不写盘）：8/8 YAML 可解析，必填面齐
  （schema_version/card_id/node_id/family/title_zh/hypothesis/window 四件/buckets 三件/pillars/
  pillars_numeric/target.primary+secondary/status/lineage.confidence_writeback/signal_kind/
  executor/data_binding 四子项；无 `generated: true`；preregistered_by 全为 st-mineloop-20261010-L13；
  signal_derivation 零"或"字未择一）。
  - **族分布**：comparison 3 / ablation 2 / calibration 3。
  - **status 分布**：blocked_on_impl 6 / preregistered 2 / blocked_on_data 0。
  - 逐卡清单：
    | card_id | status |
    |---|---|
    | TDM-P-FLOW/comparison/03_挂载策略腿OOS强度分层对照 | blocked_on_impl |
    | TDM-P-FLOW/ablation/04_三段子环并入完备性消融 | blocked_on_impl |
    | TDM-P-P1-01/comparison/03_回执与本地台账入账口径双臂失真 | blocked_on_impl |
    | TDM-P-P1-01/calibration/04_状态机态序与滞留天数对次日收益预测 | blocked_on_impl |
    | TDM-P-P2-04/ablation/04_梯度减仓顺序与无排序双臂消融 | blocked_on_impl |
    | TDM-P-P2-04/comparison/05_熔断后回撤修复阶梯加回与即时回满对照 | blocked_on_impl |
    | TDM-P-P2-04/calibration/06_减仓参与率压力对次日价格路径 | preregistered |
    | TDM-P-P2-04/calibration/07_冲高反弹幅度对次日收益与减半阈值落点 | preregistered |
- **blocked_on_impl 缺件写死（每条含 needed_interface，禁"缺件"两字交差）**：
  1. 按 strategy_ref（TDM strategy_mounts）开闭信号腿的 grid 维 + 腿级 IS/OOS SR 重算器（SR 口径复用 window_metrics）。
  2. 做T 腿注入 grid 的重放开关（输入 S13 臂 NAV + 做T 命中日净 bp，输出 S123 NAV；成本复用 COMMISSION_RATE 与 t0 件 31.2bp）。
  3. **缺双臂失真件**（前役在册点名项的本车道延伸）：回执口径 vs 本地委托终态可切换的台账失真统计件 + T-1 快照沿用注入开关（三方对真值台账，禁两臂互比）。
  4. 日线平面台账态重放件（按 PositionStateMachine._transition 同一转移表产出 (symbol,date,state_ordinal,dwell_days)，禁另写一套）。
  5. 按排序键分配减仓动作集的 rebalance-order overlay（排序函数复用 exit_execution_orchestrator.py L803）+ 5 日前向窗口指标。
  6. 按回撤修复比例触发的阶梯加回档（recover-50% ladder）+ X_breaker 帽带逐级解除腿；K 维开闸属配置位。
- **未挖长尾明列（本车道三节点，不作封矿）**：
  1. P-FLOW：流根出边=零（全仓 grep 确认），"持仓动作清单→交易员采纳"的呈现面判为不可回测平面，只登记。
  2. P-FLOW：若边表补 P1→FLOW、P2→FLOW 两条入边，本车道 ablation/04 的臂语义须重定义（治理前置，考卡不代改图）。
  3. P-FLOW：strategy_screen 表全名/覆盖窗/行数、两 CAND（CAND-5301c5d9d7c8 / CAND-8664521af1a0）在册面=
     `data_window_evidence: 待总包 22:30 后实测`（21:00–22:30 禁 CH 重查询，本车道未跑）。
  4. P1-01：六态（TDM 原文）vs 七态（码内 PositionState 七成员）口径冲突已作为卡的治理产出登记，
     但"文档-代码一致性"本身属治理门，未立考卡。
  5. P1-01：module_mounts 四件（MOD-POS-006/009/020、MOD-TRADING-002）逐件能力核查未做（本车道只实读主 module_ref）。
  6. P1-01：真要考"对账"本体需 QMT 桥文件可得性日志入仓（本地账务面 data 侧立项），非考卡可解。
  7. P2-04：减半**比例** 50% 的剂量双臂卡（25/50/75% 三臂）未立——与 ablation/04 同一缺件位；本车道 calibration/07
     明确只考择时面，不代拍比例。
  8. P2-04：/07 卡用 ATR% 三分位代理"弱 beta"，真 beta 计算件未核（已在卡内 ballast_subgroup_gate 如实披露）。
  9. P2-04：X-R1-02"逐级"档数本卡按引擎既有三档钉死；live 侧若另有定义须先对齐再开考。
  10. 跨节点：P2-04↔P1-05 漂移带口径冲突（TDM 25% vs 引擎 thr=0.10*2.0）沿用前役在册卡，本车道不重复立卡。
- **交叉复挖建议（20%≈1 节点，另附 1 条跨流路由项）**：
  1. **TDM-P-P1-06 / TDM-P-P1**（前役亦自报封矿）：本车道查明 edges 面 `TDM-P-FLOW` 的唯一入边来自 P3，
     而 P1-06→P3-01 有边、P1→FLOW 无边 ⇒ P1 汇总结论的第二条出路未查清，建议 P1 族复挖者按六向重查
     （与本车道 TDM-P-FLOW/ablation/04 直接互证）。
  2. **TDM-X-R1-02**（X 流）：梯度减仓序的实现在 `sell_decision/services/exit_execution_orchestrator.py:8,32,797,803`，
     而算法册 DAL-GRADIENT-TRIM 自记 `code_ref: null / status: design`，且 X-R1-02 的 module_ref
     `risk/core/drawdown_liquidation_guard.py` 实读只有撤单率红线（0.12/0.15）与清仓超时 30s
     ——三处说法不一，建议 X 流复挖者裁"实现归 X、叙述归 P2-04"的路由断点该改哪一侧。
- **假绿风险自报（禁报"全部完成"）**：
  1. 本车道两张 preregistered 卡的 primary 都是"次日收益"（现器 shift(-1) 能力面），
     显著≠执行失真/限额有效为真——两卡各写了 proxy_honesty / 不代拍比例的前置，仍须防读数时被当成结论。
  2. 在册背景=已考 18 行全 fail（任务书 §3）⇒ 持仓面新卡大概率 fail；
     fail 是考出来的结果，不得被读成"矿已挖尽"，三节点的未挖长尾已逐条明列。
  3. 六张 blocked_on_impl 卡若被误当 preregistered 送考，run_card 硬读 status 会拒（前役实读），
     但台账与分数册须按 status 面统计，防"8 张全可考"的假绿。


---

## 来源：`docs/_working/mineloop_campaign/R1_L14_ledger.md`

### L84 · §6 假绿风险（本车道发现，如实上报，未代修）

## §6 假绿风险（本车道发现，如实上报，未代修）

1. **同名不同义**：`dominant` 列在两链语义冲突——锚定链 r3=低/r2=中/r1=中高/r4=高风险（anchored_state_machine.py:36-39），旧 HMM 链状态键 r1,r2,r3,r4,r10,r11,r12（print_regime_history.py:64）。下游按名消费（screen_source.py:48、owner_band_t/regime_gate.py:17 读旧链）存在**静默错档**风险；卡 4 把两臂映射固定为"各用各表列"以隔离，但这是治理面，非本车道可修。
2. **写方口径自相矛盾**：pipeline_events.py:1033 称快照表"唯一自动产出者=maybe_refresh_regime_snapshot"，fw_backtest.py:71 称"唯一写方=print_regime_history.py（manual CLI）"——同一张表两行冲突，在册文档矛盾=事故（根宪法 §4.3 精神），需总包核实。
3. **阈值漂移**：电风扇市册上 80% 分位（trading_decision_map.yaml:690）vs 代码 `VELOCITY_PERCENTILE_THRESHOLD=0.75`（boundary_revision_engine.py:117）。
4. **未审计边**：S1/S2/S3/S4/S0/S5→AGG 六条 feed 边 pit_proof 全 `legacy-unaudited`（6164-6167,6183,6187），而代码实测 AGG 只吃 vol_pct——"消费六路"的叙事与本卡 2 的实测面若不吻，卡 2 就是那把尺（预计 fail，fail 即真相，非本车道成绩）。


---

## 来源：`docs/_working/nightmine_campaign/L1_ledger.md`

### L236 · 7. 收尾汇总（本车道）

## 7. 收尾汇总（本车道）

- **节点总数**：30（entry_flow/L2 板块层，含 TDM-C-L2 币圈预留框架节点）。
- **已挖数**：30/30（每节点六向全部留痕，见 §1 表）。
- **新卡总数**：32（30 节点全覆盖；L2-06-3 与 L2-09 各 2 张——02/03 分工写死在卡内 note，
  未凑数摊薄；机检=临时件 `validate_cards.py` 实跑输出 `ours cards: 32 problems: 0`）。
- **族分布**：calibration 22、ablation 10、comparison 0（对照题在本层被 ablation 吸收，避免与骨架件重复）。
- **status 分布**：preregistered 24、blocked_on_data 8、blocked_on_impl 1（与 blocked_on_data 交叠：TDM-C-L2）。
- **mined_out 名单（22，六向全部"已入卡/已查无"且无本节点级未挖长尾）**：
  TDM-E-L2, TDM-E-L2-01（四路全量面另挂 blocked）, TDM-E-L2-01-2, TDM-E-L2-01-3, TDM-E-L2-01-5,
  TDM-E-L2-02, TDM-E-L2-02-1, TDM-E-L2-02-2（盘中面另挂 blocked）, TDM-E-L2-03, TDM-E-L2-04,
  TDM-E-L2-04-1, TDM-E-L2-04-2, TDM-E-L2-05, TDM-E-L2-05-1, TDM-E-L2-05-2, TDM-E-L2-06,
  TDM-E-L2-06-1, TDM-E-L2-06-3, TDM-E-L2-07, TDM-E-L2-07-1, TDM-E-L2-08, TDM-E-L2-09。
  （注：这 22 个的"枯竭"=结构判据达成，不等于无进一步题；§5/§6 列的是跨节点长尾与复挖建议，
  依 §3 禁降格原则，本车道不以"已挖一张卡"冒充封矿，也不以"候选多"作停止判据。）
- **blocked 名单与原因（8）**：
  | node | status | 缺什么（写死） |
  |---|---|---|
  | TDM-E-L2-01-1 | blocked_on_data | 2019-01-04..2026-07-21 板块成分口径（sector_constituent 仅 6 刷新日；snapshot 仅 19 日） |
  | TDM-E-L2-01-4 | blocked_on_data | 同上（聚合路）；直读路 sector_fund_flow 仅 2026-09-15 起 17 交易日，个股 money_flow 本身 2021-01-04 起充分 |
  | TDM-E-L2-03-1 | blocked_on_data | 2019-01-04..2026-07-21 成分口径（个股价格面 1990 起充分，SMA20 可算，缺的是归属） |
  | TDM-E-L2-06-2 | blocked_on_data | 2019-01-04..2026-08-31 涨停池/打板时序（limit_up_pool 1426 行/28 日；stk_limit 价格面 2015 起但无封板时点） |
  | TDM-E-L2-09-1 | blocked_on_data | ig_* 无 2026-08-28 前记录且无 PIT 版本；news_data 2025 年断供（31425 行） |
  | TDM-E-L2-09-2 | blocked_on_data | 同 09-1 根因 + 图谱可回放窗 <1 个月，八臂消融样本不足 |
  | TDM-E-L2-10 | blocked_on_data | 同题材腿缺 ..2026-07-21 成分；同链腿缺 ..2026-08-27 图谱历史 |
  | TDM-C-L2 | blocked_on_data + blocked_on_impl | 无赛道映射表（TableRegistry crypto 仅 2 表，列集无 sector/track）；历史仅 2025-08-08 起 431 日/141 币；无市值面（山寨季不可算）；TDM 侧 module_ref=null、red_reason=not_built |
- **本车道对全战役的两条硬结论**：
  ①板块层可考面=**板块指数面（价/量/RSI/集中度/RS 象限），冻结上限 2021-08-02**（P4 实测复证在册结论）；
  ②板块层**个股聚合类读数（涨停占比/扩散度/资金流聚合/龙头时序/补涨）结构性不可考**，
  根因单一=成分口径（sector_constituent 6 个刷新日）——L3 车道凡"板块内个股"题都会撞同一堵墙，
  解锁只需一次补史（2021-08-02 起日频或月频 SCD2 成分），收益覆盖本车道 8 张卡。


---

## 来源：`docs/_working/nightmine_campaign/L3_ledger.md`

### L164 · 四、车道收尾（32 节点）

## 四、车道收尾（32 节点）

- **本车道节点总数**：32（名册 `lane=L3` 权威名单，与任务书逐一对齐：TDM-E-L4+L4-01..14+TDM-C-L4=16；TDM-E-FLOW+L0+L0-01..04=6；L1 层 10 个）。
- **已挖数**：32/32（每节点六向全部留痕，见 §二各行；无未开工节点）。
- **新卡总数**：39 张（YAML 逐件 parse 校验通过，必填面与 `data_binding` 五子项、`pillars_numeric` 五子项零缺失；
  校验命令见本车道临时件记录，全部 `preregistered_by: st-nightmine-20261010-L3`；
  机核结果：cards=39 / bad=0 / families={comparison:23, calibration:14, ablation:2} / 有卡节点=31（第 32 节点 TDM-E-L1-S1 为"已查无可补，不凑数立卡"，见 §二该行与 §四诚实申报）。
- **族分布**：comparison 23、calibration 14、ablation 2（calibration 全数落在 L1 传感器/广度补卡；ablation=L1-AGG 聚合环 + L4-07 队列环，两节点 node_type 均为 aggregation，符合"聚合环节走消融"立法；机核命令见本节末注）。
- **mined_out 名单（严格 §3 结构判据）**：**空**。理由逐条：全部 32 节点的③算法/机制向在本战役内均处于两种状态之一——
  已入卡（可判）或外部检索未取得"URL+发布方+年份"合格引文（=受阻，非查无，§3 明定受阻不算查无、不算封矿依据）；
  另有 §4.6 列出的长尾未挖项。禁以"挖了两轮/时间不够/节点太多"降格封矿，故本车道一律不标 mined_out。
  近枯竭（六向仅剩外部文献一向未闭）：TDM-E-L4-08、TDM-E-L4-09、TDM-E-L4-12、TDM-E-L1、TDM-E-L1-AGG、TDM-E-L1-S2。
- **blocked 名单与原因**：
  - 共用件（全车道唯一硬阻塞）：`comparison/ablation 族卡驱动执行器`缺位（0/3 源正查，§3.1）。
    受影响卡=23 张 comparison + 2 张 ablation（calibration 14 张可由既有 `calibration_exam.run_card` 直接考，不受阻）。
  - blocked_on_data（逐卡写明缺哪表哪段）：L4-02（个股盘中分钟线 2019-2025 缺）、L4-05（打板事件 2015-01-05..2026-08-31 缺）、
    L4-06/L4-14（实测成交回报 2026-07-17 前缺，仅 84 笔）、L4-10/L4-11/L4-13（委托回报/中间态/成交确认三份流水缺）、
    L0/L0-01/L0-02/L0-03/L0-04（计划·概率·边界逐日流水缺，仅 judgment_* 12/24/6 行）、L1-S0 海外轴（kline_global 无 NDX/SPX）、
    L1-S0 政策轴（人工录入无结构史 + rate_decision_calendar 1970 脏哨兵）、L1-S5 母卡盘中版（9:35 首算历史缺）、
    C-L1/C-L4（币圈 MA200 有效窗仅 2026-03 起 + 无币圈分钟/费率实测面）。
  - blocked_on_impl（除共用执行器外的额外缺件）：tick 级三臂撮合重放器（L4-03/06/07/11）、
    下单前逐票预期收益比较器（L4-09）、触发事件流水入库（L4-07）、订单九态事件入库（L4-10）、
    三方账故障注入器（L4-13）、状态输入注入器（L1-AGG）、置信度入参面（L4-04）、币圈执行件（C-L1/C-L4，节点空壳）。
- **未挖长尾清单（明列，非停止判据）**：
  1. 各 L4/L0 comparison 卡的"外部机构对照文献向"（需 URL+发布方+年份+年份核验，本轮 429/受阻）。
  2. L4-03 价格笼子（申报价±2%）与限价偏移的交互臂（件 price_cage.py 在、数据 stk_limit 在，未立卡）。
  3. L4-02 竞价铁律单独卡（9:15-9:20 可撤假象 / 9:20-9:25 只挂不撤；auction_book 实测 3,690,473 行可用）。
  4. L4-01 首批比例与置信度档联动版（非固定三档）。
  5. L4-07 优先级抢占在真实触发事件流水上的复算（待事件入库件）。
  6. L4-05 撤单纪律"封单骤减 20% 立即撤"的 tick 级队列模型版。
  7. L1-S3 情绪先锋四态平行卡（母卡 04 的导生版，需 streak 串 + 开盘价双条件）。
  8. L1-S2 连板家数"分布形状"（母卡 07 的完整分布形态，本车道只落一阶摘要 streak>=2 家数）。
  9. L1-S2 净广度比值型变体（本卡固定差分）。
  10. L1-S4 主路径期权 IV 曲面长窗回填卡（解 blocked 后）。
  11. L1-S4/L1-AGG 主备路径切换逻辑考核卡（本车道明言"未考切换"）。
  12. L1-S5 11 信号剩余 4 项（盘中炸板走向等）的短窗 tick 版（tick_depth_5 实测窗内）。
  13. L1-S0 板块级新闻情绪 scope 与 news_sentiment_score 跨 caliber_version 口径对齐卡。
  14. L1-S0 政策事件轴（结构化录入链建成后可立卡）。
  15. L1-S1 黄白线代理合法性判定（代理=换命题，需先裁定代理口径再立卡）。
  16. L0-03 八态概率双真值（emotion vs anchored dominant）分歧时的第三真值选择。
  17. L0 禁做清单第三源（人工政策/事件）结构化后补卡。
  18. L4-09 T+1 约束单独臂与持仓限额臂的独立量化卡（本卡合并处理）。
  19. L4-06 参与率纪律 10-20% 的经验分布建档（tick 面可算，本卡只设柱未跑）。
  20. C-L1/C-L4 币圈真实费率/滑点实测面与跨所口径（Binance/OKX 分表）建设后复考。
  21. 广度导生口径与事件表口径（2026-09 重叠段）的等价性实证卡（rho>=0.9 判据已写入卡 09 的 caliber_equivalence，未跑）。
  22. `data/strategy_intake/grid_*` 参考 run 的实际 manifest 行数/窗口首跑建档（本车道只核目录存在）。
- **建议交叉复挖 20% 名单（6-7 个节点，交他道或复挖批）**：
  TDM-E-L4（与 L2/L3 选股道交叉：口径差值对 alpha 的侵蚀归属）、TDM-E-L4-09（与治理道交叉：门的冗余判据）、
  TDM-E-L4-12（与治理道交叉：五查逐条冗余→净零候选）、TDM-E-L1-AGG（与 L1 道/风控道交叉：状态环是否≈常数）、
  TDM-E-L1-S2（与数据道交叉：daban_board_event/limit_up_pool 历史回填可行性=7 张母卡的解锁条件）、
  TDM-E-L0-03（与 P 流/归因道交叉：Brier 校准链复用面）、TDM-C-L4（与基础设施道交叉：币圈数据深度与费率实测）。
- **诚实申报的负结果与不立卡决定**：TDM-E-L1-S1 未立卡（唯一可判长窗面已被母卡 02 覆盖，代理会改命题）；
  7 张 L4 卡的"倒 U / 符号为负属预期"条款（跌停家数、连板高度、失败态 IC、q 先验 IC 等）
  均按 `calibration_exam.judge` 原样判 fail 入册，未改符号口径造过门（G4-5）。


---

## 来源：`docs/_working/nightmine_campaign/L4_ledger.md`

### L103 · 四、车道收尾（作业簿 §五 MUST 项，逐条可核）

## 四、车道收尾（作业簿 §五 MUST 项，逐条可核）

- **节点总数**：18（position_flow 全集，逐节点从 `config/trading_decision_map.yaml` 读全字段，无遗漏；
  节点明细快照=`D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/pos_nodes.json`）。
- **已挖数（六向全部留痕）**：18/18。
- **新卡总数**：34（全部另建新文件，NN 从 02 起；零触碰 `generated: true` 骨架件）。
  机器校验（本车道实跑）：34/34 YAML 可解析，且必填面齐
  （status/signal_kind/pillars_numeric/window 三件/buckets/pillars/target/
  lineage.confidence_writeback/preregistered_by=st-nightmine-20261010-L4/preregistered_at/discipline/
  data_binding 四子项含 data_window_evidence 命令原文）。
  - status 分布：preregistered 21 / blocked_on_impl 11 / blocked_on_data 2。
  - **族分布**：comparison 20 / calibration 8 / ablation 5 / shadow 1（碰钱面以对照为主，符合车道设计）。
  - 每节点卡数：PFLOW 1、P1 1、P1-01 1、P1-02 2、P1-03 2、P1-04 5、P1-05 4、P1-06 1、P2 1、P2-01 1、
    P2-02 2、P2-03 1、P2-04 2、P3 1、P3-01 2、P3-02 2、P3-03 2、P3-04 3（合计 34）。
- **mined_out（封矿；结构判据=六向全部“已查无/已入卡”且无未挖长尾）名单 8 个**：
  TDM-P-FLOW、TDM-P-P1、TDM-P-P1-01、TDM-P-P1-06、TDM-P-P2、TDM-P-P2-01、TDM-P-P2-04、TDM-P-P3。
- **未封矿（有明列长尾，见下）名单 10 个**：TDM-P-P1-02、TDM-P-P1-03、TDM-P-P1-04、TDM-P-P1-05、
  TDM-P-P2-02、TDM-P-P2-03、TDM-P-P3-01、TDM-P-P3-02、TDM-P-P3-03、TDM-P-P3-04。
- **blocked 名单与原因**：
  - blocked_on_impl 11 张：P1-01/02（缺复权口径可切换的双臂失真件）、P1-02/03（缺双臂分级统计件）、
    P1-03/03（M5 维未注册未接线，函数零调用点）、P1-04/03（缺固定比例止损档）、
    P1-05/04（缺同题材只数帽 overlay）、P1-06/02（缺三腿全因子 runner+腿序开关）、
    P2-02/02（缺做T 重放件体量开关）、P2-04/03（缺按 improvement_ratio 裁剪动作+优先权开关）、
    P3-01/02（缺向下摊平 mode）、P3-02/02（缺 tranche 权重与阶梯阈值入参）、
    P3-03/03（缺随加仓档重算止损线的保本腿）。
  - blocked_on_data 2 张：P1-04/06（CH 无个股级财报披露日/解禁日历表）、
    P2-02/03（tick_depth_5 仅 2026-07-24..2026-09-30 约 2 个月，且做T 材料全库仅 26 对 <30 土规线）。
  - 每张 blocked 卡都写了解锁条件与所需接口签名（禁“缺件”两字交差）。
- **未挖长尾清单（明列，逐条可续挖，不作封矿）**：
  1. P1-02：threshold_delta 双向反馈环（BM-POS-09，|delta|≤0.10 扣阈）对分级稳定性与告警膨胀的影响。
  2. P1-03：打板仓“情绪梯队还在不在”腿（六段 CSV 可映射但 ignition=2 天需先证样本）；
     事件仓“利好兑现”腿（event_decay 0.50/0.80，需 DS-107 news_sentiment_window 覆盖探针）；
     做T 底仓“趋势不破”腿（与 X/趋势族边界，只登记不越界）。
  3. P1-04：亏损限额腿（daily 0.02/weekly 0.05/monthly 0.10 + halt 1/2/3 递进约束，现码实存零考法）；
     竞价不及预期腿（auction_discount_threshold=0.02，auction_snapshot/auction_book 在册可探）；
     分时破位腿（intraday_vwap_break_threshold=0.01，1min 可算 VWAP，考法未立）。
  4. P1-05：相关性扎堆帽（与只数帽不同对象）；概念板口径（concept_sector+sector_constituent）稳健性复跑。
  5. P2-02：三策略各自适配段（surge-fall/vwap-reversion/orderbook × 六段）——待补料后开。
  6. P2-03：C3 归因污染面（做T 腿混算 vs 分算的底层策略指标差）；盘中 5 分钟核对频率敏感性。
  7. P3-01：策略亲和度>0 腿（全项目无在册亲和度计算件，需先定位或立项）；熔断禁加期腿
     （_CIRCUIT_BAN_LEVELS={L2,L3,L4} 与 X_breaker 帽带的层位映射未考）。
  8. P3-02：阶梯阈值扫描（2.5%/3%/5%）；限次 3 消融（max_tranches 放开）。
  9. P3-03：SIZING_BASIS 十枚举逐个考（VaR 0.025/CVaR 0.04/流动性削半/退出时间帽/降级等权）；
     MARKET_REGIME_CAPS 档位表；max_participation_rate=0.15 的 ADV 规模维 binding 面
     （`cost_accounting_ruler.py:28` 已自述“成本线无 participation/ADV 规模维”=缺口在册）。
  10. P3-04：“未成交不追价、次日重走资格门”策略面；TWAP/IS 执行切片与真实滑点分档
      （`90_methodology_open_questions.md` L259 裁定“滑点按策略分档：高流动 0.05-0.1%/打板事件 0.15-0.3%”
      未入任何考卷）。
  11. 跨节点：P1-04 触发即“冻结做T/加仓资格”的跨流硬约束联合后果（否决日同时禁 T/禁加的开闭对照）——
      需 P1/P2/P3 三族同 recipe 联跑，属装置工单非本车道可独立闭合。
- **建议交叉复挖 20%（18×20%≈4 个节点，交他人复挖）**：
  1. **TDM-P-P1-04**（否决线族）——与 exit_flow/X 族重叠面最大：固定生死线 vs ATR 之争、
     保本上移与 trail20/Chandelier 的语义差（prereg_frozen.yaml stop_rules 与引擎 L913-915 两处实现不同）；
     建议 X 族复挖者裁“同一止损语义两处实现”是否收敛唯一。
  2. **TDM-P-P3-01**（红线族）——“只加浮盈”在回测侧由引擎 armed 条件（≥×1.03）隐式实现，
     建议 E 流与 P3 复挖者共同判该隐式实现是否等价于显式红线（潜在静默失效点）。
  3. **TDM-P-P2-04 + TDM-P-P1-05**（再平衡双子）——TDM 25% vs 引擎 10% 漂移带口径冲突横跨两节点，
     建议 portfolio_flow 车道复挖并出纠偏裁定材料（本车道已把 binding 判定写进 P1-05/comparison/03）。
  4. **TDM-P-P3-04 + TDM-P-P2-03**（跳空双子）——“尾盘加仓付更高价差”与“未闭环敞口过夜代价”共用同一
     跳空变量，且与内部先例（缺口当日回补 75%、跳空负向因子年化 -25%）方向冲突，建议交叉定死口径。
- **本车道三项非卡类产出（供总报告）**：
  1. **在册口径冲突两处**：漂移带 25%（TDM）vs 10%（引擎 `thr=0.10*2.0`，factory_grid_executor.py:717）；
     金字塔档序 递减 1/2（live PyramidingConfig）vs 等额 1/3（引擎 L1114），阶梯 2.5% vs 3%/6%。
     两处均属“同一约束两处实现不一致”，任一方对都须纠正另一方（治理项，非本车道权限，已留证据行号）。
  2. **做T 族的材料结构性不足**（是“门与窗互斥”不是“无信号”）：V3 在册实测主考 0 对、全材料 26 对、
     净均 −36.26bp、前置命中率 0.2308；宏观放行 20 对被情绪门 100% 否决；材料窗 dominant 无 r3/r12。
     ⇒ P2 族每张卡都自带 DEVICE_INCOMPATIBLE / INSUFFICIENT_SAMPLE 三态出口，禁把“无料”判成“无信号”。
  3. **六段历史 CSV 的段样本现实**：ignition 2 天、euphoria 40 天、空白 762 天（1,822 行全表实测）
     ⇒ 一切“点火段才加仓/做T”类段权限考法必须先挂样本门，P3-01/comparison/03 已按此改写可判子集。
| TDM-P-P1-01 | （同前，六向已记）补记：卡已落 `P1/TDM-P-P1-01__comparison__02_复权口径对成本与生死线触发对照.yaml`，三臂（hfq/raw/raw×adj_factor）+除权事件集+级联到 P3-01 资格判定，判据成组；缺件=口径可切换的双臂失真统计件（既有件全锁 hfq 单口径：prereg_frozen.yaml atr.price_basis 与 exit_simulator.load_kline 实读） | 1 | comparison×1 | 是 | blocked_on_impl |


---

## 来源：`docs/_working/nightmine_campaign/L5_ledger.md`

### L123 · 六、车道收尾自证

## 六、车道收尾自证

- 节点总数 **19** ／ 出卡节点 **19**（每节点 ≥1 卡）／ 新卡总数 **20**。
- 族分布：**comparison 10 / calibration 4 / ablation 5 / shadow 1**。
- `mined_out` 名单：**空**。枯竭判据（mining_sop §3）要求"六向全部已查无/已入卡＋无未挖长尾"，本车道每一节点都仍有下列长尾，故无一可封矿。
- blocked 名单与原因（断供不弃卡，判据面已写死缺哪张表哪一段）：
  - `TDM-X-S1-04` 情绪退潮路 = **blocked_on_data**（六段态历史缺：`decision_daily` 仅 2026-09-16 起 138 行；`emotion_index.stage` 实测为快照阶段枚举非六段）。
  - `TDM-X-S2-02` 盘口排队面 = **blocked_on_data**（`tick_depth_5` 仅 2026-07-24..2026-09-30；`l2_tick` 空表）。
  - `TDM-X-S2-04` 五档深度子面 = **blocked_on_data**（同上）；分钟面已解禁（见长尾⑦）。
  - `TDM-X-S2-03` 竞价段（9:15-9:25 / 14:57 前后）长窗 = **blocked_on_data**（`auction_snapshot` 2026-06 起、`auction_book` 2026-07 起）。
  - `TDM-X-R1` / `R1-01` / `R1-02` 实盘净值与持仓面 = **blocked_on_data**（`account_nav_daily` 仅 5 行），故三卡改用仿真组合净值并披露该近似。
  - `TDM-X-S1-02` 分时破位档 = **blocked_on_data（窗不兼容）**：1min 数据 2021-09 起，与本体系冻结 IS 起点 2018-01-02 不可比，须另卡另窗。
  - `blocked_on_impl` 共性：`exit_simulator.simulate()` 只认 `stop_enabled`，X_tp/X_ladder/time_stop/participation/urgency/五档约束全部需装置扩展（各卡 implementation_gap 已逐件写明）。
  - Owner 门位（不阻卡，阻落地）：X_tp/X_ladder/卖出路径切分三维未经裁定（草稿 §五 B1）；X-R1-03 防御格内容与资金预算=Owner 保留面（B5）；新开考通道与预算（B2/B4）。
- 未挖长尾清单（明列，禁含糊）：
  1. X-S1-02：固定 -7% 生死线档单独对照、支撑破位双触发（硬底+软确认 30 分钟观察窗）、止损棘轮（单向 clamp）违规率审计、前瞻概率止损 P(跌)≥0.65 建议通道可考性、ATR 缺失降级锚（4%/8%）触发占比。
  2. X-S1-03：目标位"次日不板走"封板掩码单独臂（stk_limit 可算）、peak_pnl 回落 X% 的 X 敏感性面。
  3. X-S1-04：除权除息日卖出口径（D68 分母改除权参考价，adj_factor 表在册可考）、假破位影线处置、早盘 9:30-10:00 假信号高发窗的时段可靠性系数。
  4. X-S1-05：urgency 三档的实测分布与档位迁移率、confirm_bars/buffer_pct/量能 1.5× 三参各自的单独消融、周线共振加成的独立贡献。
  5. X-S1-06：主力弃庄分支用 seat 表（2022 起）做短窗旁路增益 pilot、天地板个股级规则（D99 终裁后口径）。
  6. X-S2-01：ICEBERG 随机化与释放间隔抖动、枯竭检测（点差突宽/深度秒撤）、恐慌拦截（低开<-3% 等待窗）与三类绕过、板块联动顺序（跟风→补涨→中军→龙头）。
  7. X-S2-02：新股首日状态机、临停复牌 ±10%、风险警示板 2026-07-06 制度切片（按生效日切片，可卡）、碎股/200 股基准。
  8. X-S2-03：竞价即决十行矩阵（溢价×量能）与量能三口径（5-10%/<3%/>15%）校准、跳空 3%/6% 分档预案、除权日溢价分母。
  9. X-S2-04：SellChase 追单预算 15-20 轮敏感性、QMT 三坑（business_id 幂等/保护限价/on_cancel_error）的可测性。
  10. X-S2-05：按信号强度定分批密度（弱一次走完/强留 runner）、MFE 捕获率<50% 自检的反馈闭环。
  11. X-S2-06：六分类 PANIC 占比>10% 告警可考性、冷却迟滞带 A/B 线与连败阶梯（D106 口径）参数标定、30 日避损率斜率降 30% 降档规则。
  12. X-R1 系列：四层止损作用域×节拍（单票/做T/sleeve/组合）交叉、风控心跳失联降级（M-60 挂载点）、影子件落盘 fail-closed 的工程可靠性面。
  13. 跨节点：X-S2-06→E-L4-12 边与 F-C3 归因的消费侧效果（②下游向仅做了边识别，未做端到端接线考）。
- 建议交叉复挖的 20% 节点名单（≈4 个，供其他车道/下轮对挖）：
  `TDM-X-S1-02`（五路止损仅考 1 路，最厚长尾）、`TDM-X-S2-01`（约束细则最多且与 CST-ASTOCK-001 成本册交叉）、
  `TDM-X-S1-05`（与 E-L1-AGG 六段情绪轴跨流交叉，退潮代理可从他道借六段历史表解冻 X-S1-04 阻塞面）、
  `TDM-X-R1-01`（与 C 流预算带跨流交叉：同一减仓量在预算带内的重复计价风险）。
- 治理留痕：本车道 20 个新 .yaml 属 CREATE-GUARD 需 creation_token 面——禁区明令禁改注册表，故 token 未落册，按草稿 §五 B6 先例（token 随批落）由 Owner/批车道统一登记；
  台账与卡均在工棚 `.aidrafts/st-nightmine-20261010/` 内，临时件仅 `D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/l5_add_pillars_numeric.py`；未执行任何 git 写操作。


---

## 来源：`docs/_working/nightmine_campaign/L6_ledger.md`

### L103 · L6 车道收尾（MUST 全项）

## L6 车道收尾（MUST 全项）

**节点总数 / 已挖数**：16 / 16（全 16 节点逐一六向挖矿并出卡；名册 L6 nodes:16 全达）。
**新卡总数**：17（TDM-F-C1 出 2 张，其余 15 节点各 1 张）。
**族分布**：shadow 9 张（C1、C1-01、C1-02、C1-03、C2-02、C2-04、C3-02、C3-04、C3-05）；comparison 8 张（C1-comp、C2、C2-01、C2-03、C3、C3-01、C3-03、FLOW）。
**卡可运行核验**：`yaml.safe_load` 全 17 张通过；必填面（schema_version/card_id/node_id/family/status/signal_kind/pillars_numeric/window/buckets/pillars/target/lineage/data_binding/preregistered_by/at）全在；均无 `generated:true`；status 全 `preregistered`；data_binding.data_window_evidence 全带实测覆盖窗+行数+命令原文。

**mined_out=是（六向齐、无未挖长尾）5 个**：TDM-F-C1-02、C2-01、C2-02、C2-03、C3-01。
（C2-01/02/03 绑真实落码件 MOD-POS-021/012；C3-01 绑 MOD-PF-007 已落码引擎；C1-02 绑 allocator_shadow 五套影子考——均"缺什么"已穷尽。）

**blocked 名单与原因（8 个节点）**：
- blocked_on_impl：
  - TDM-F-C1-01（策略路由查表体 module_ref null / by_ref_design，路由引擎未落码）
  - TDM-F-C1-03（双向 weight_band 爬坡器未落码；且 owner_gate 灰度切换）
  - TDM-F-C2（组合聚合端到端件空 / structural）
  - TDM-F-C2-04（BudgetChanged 事件链未接线，33 号复核在案）
  - TDM-F-C3（归因反馈闭环编排空 / structural）
  - TDM-F-C3-03（MOD-PA-007 纯库无调用方，三缺口 base_weights/调度体/PerfScore 生产者，裁定#257② 在案）
  - TDM-F-C3-04（红节点 G04 校准闭环未转；walk_forward 件存在但端到端未接）
  - TDM-F-C3-05（红节点，D7-D13 判准率加权 src 零实现）
  - TDM-F-FLOW（terminal 聚合器结构指向件，全链待装配；allocator 段真实）
- blocked_on_data：
  - TDM-F-C1__comparison__03_预备金现金贡献（cash_contrib 门柱缺 GC001 逆回购日收益率在册 CH 表；组合 NAV/MaxDD 两臂不受影响可跑）
- CH 数据本身无断供（kline_daily_hfq/kline_index/regime_snapshot 全覆盖至 2026-09/10），除上列 GC001 外无缺基建表。

**未挖长尾清单（明列，供交叉复挖/续挖）**：
1. 预备金存放分层三档利率（当日逆回购 GC001 / T+1 短债）与"14:00 后利率高 38%"日内季节性——需日内级现金收益率数据源（现无）。
2. C1-03 切换事件样本稀少（min_obs=5），A 股实际策略间切换历史事件簿未建，长尾待事件积累。
3. C2-02 六层约束"过哪层裁哪层"逐层贡献分解需 sleeve 级 intent 明细（当前只有净值面板），逐层归因属施工面。
4. C2-03 危机期相关性趋于 1 的压测版需危机日期定义真源（crisis_gate θ），本卡引 config/crisis_gate.yaml 未展开逐日压测。
5. C3-01 逐笔 TCA（decision→fill 滑点归因，A 股隐性成本 5-10× 佣金）与孤儿成交 suspense 桶——需 tick 级成交回报，日频面板不及。
6. C3-02 观察名单"半仓缓刑 3 个月"中间态 + 升档参考输入（paper 样本笔数/时长/回测偏差阈）属编排长尾。
7. C3-04 DSR/PBO 的 CPCV 配置项"待 P1-18 实现"（walk_forward.py 注释），四道 gate 中 CPCV 面尚未落地。
8. C3-05 粒子滤波时变档（三档递进第三档，远期）与币圈 funding/basis schema 预留（A 股恒 0）——终局有位现在挂起。
9. 全链 F 流端到端（FLOW）串接需 C1→C2→C3 全接线，当前仅分配器段可跑。

**交叉复挖建议（约 20% 节点）**：TDM-F-C1-02（五套影子考可直接开 allocator 子命令验，绑最实基建，优先复挖/开考）、TDM-F-C3-01（MOD-PF-007 已落码，切账判据可即时校准）、TDM-F-C1（预算带六档数值全 proposed，待 Owner 校准后复挖）、TDM-F-C3-03（三缺口任一补齐即可解锁调权全链）。

**需 Owner 拍板项（灰度晋升类，单列——本车道禁执行，仅出卡与判据）**：
- **TDM-F-C1-03**（`owner_gate_required: true`）：双向 weight_band 灰度切换 = 策略间 production 流转，触根宪法 §5 Owner 保留面；卡已冻结判据，切换/晋升动作一律待 Owner 签字。
- **TDM-F-C3-02**（`owner_gate_required: true`）：sleeve 清退归零 = 业务资产概念级退役（轨 B）+ production 流转，需 Owner 签字；减半/冻结等可逆减动作 AI 可自主，退役提案交 Owner。
- 附：**TDM-F-FLOW** 挂载 STR-MULTIFACTOR-098/099 双窗及格但 BH-FDR 未过、candidate 留观——晋升上线属 Owner 门（本卡不判上线，仅全链净效果考）。
- 综合：组合层任何"首次转 production / 灰度切换 / 退役"均须走晋升门（宪法 §5 非交易核心域可回退晋升/交易核心域 production 流转 Owner 保留），本车道全程只出卡未执行任何切换或晋升。

**诚实负结果**：allocator_shadow_report_v1.yaml/.md **尚未产出**（影子考未开跑），本车道据 allocator_shadow.py 源码（读全文）如实描述其入口/产出形态，未虚构任何已跑结果；基准 v0 Sharpe 0.963 引自任务令与裁定 D8 版本化，未在本车道独立复算（考试车道开考时校准）。library.lookup state 四词零命中已作负存在断言证据指针登记，降级手工阶梯（读图真源 + 读码）佐证。


---

## 来源：`docs/_working/nightmine_campaign/L7_ledger.md`

### L276 · 四、车道收尾（MUST 项，逐条齐）

## 四、车道收尾（MUST 项，逐条齐）

### 4.1 总量（全部实测，非估算）

- 本车道节点总数：**45**（entry_flow/L9 全集，逐个从 `config/trading_decision_map.yaml` L4981-6161 取全文字段）
- 已挖数（六向全部留痕的节点）：**45/45**
- 新卡总数：**51**（校验命令见 4.6；45 个节点每节点 ≥1 张，A01/A04/A06/A15/A17 多张）
- 覆盖节点数：**45**（`node_id` 去重实测=45，无遗漏无重复）
- 族分布：**calibration 36 / ablation 15**
- 状态分布：**preregistered 18 / blocked_on_data 24 / blocked_on_impl 9**
- market 分布：**cn_a 49 / crypto 2**（币圈镜像单列，见 4.5）

### 4.2 mined_out 名单（结构判据，禁降格）

**已达枯竭判据（mined_out）= 5 个**：`TDM-E-L9-C01`、`TDM-E-L9-C02`、`TDM-E-L9-C03`、
`TDM-E-L9-G2`、`TDM-E-L9-G5`
判据逐条：六向全部"已入卡 / 已查无（含归因）/ 受阻已归因"，且矿脉清单无本节点可再挖长尾
（C 三节点的外部矿归因=渠道本身不存在故无机构实践文献可引；G2/G5 的长尾是"他环实现前置"
（PG 通道 / io_edge 挂接率），属实现前置而非可挖信息项，且与 G1/A16 同矿脉已声明不重复挖）。

**其余 40 个 = 未达枯竭**（有明列长尾，见 4.4）。
禁降格声明：未以"挖了两轮没新东西/时间不够/节点太多"封任何一个矿；
每个 blocked 节点仍保留长尾条目，状态 blocked 是**数据/实现的物理阻断**，不是挖矿终止判据。

### 4.3 blocked 名单与原因（24+9=33 张卡，按成因归类）

| 成因类 | 卡数 | 节点（卡号） |
|--------|------|-------------|
| A 渠道未接（B 档，CH 无表+馆查零命中） | 10 | B01 B02 B03 B04 B05 B06 B07 B08 B09 B10（各 02） |
| B 无接入渠道（C 档，渠道需被创造） | 3 | C01 C02 C03（各 02） |
| C 历史不可回填（快照型/时戳不可回填） | 3 | A07(02) A14(02) G4(02) |
| D 字段存在但内容全空/口径不可用 | 2 | A17(02)（rating_change 100% 空+无目标价列）、A02(02)（l2_tick 空表+IS 全空） |
| E 关键表空/断供致 IS 或 OOS 段零覆盖 | 3 | A04(03)（stock_valuation rows=0）、A06(03)（北向断供 2024-08-16/OOS 截断）、A15(04)（宇宙成分不可 PIT+427 日+换源未留痕） |
| F 样本量不足臂间对比（治理/验证环，向前积累型） | 6 | AGG(02) D1(02) E1(02) B-D 类其余…（AGG/D1/E1 + 见注） |
| G blocked_on_impl：跨存储（PG↔CH）或 id 桥/开关缺失 | 9 | A16(02) G1(02) G2(02) G3(02) G5(02) D2(02) E2(02) Z1(02) Z2(02) |

（注：F 类实数=AGG/D1/E1 三张 blocked_on_data + V 族无 blocked；上表 F 行标 6 为笔误候选，
准确数=**3**；总数校核：10+3+3+2+3+3=24 = blocked_on_data 实测数，9=blocked_on_impl 实测数。
此句本身即"计数勿写死散文"纪律（根宪法 §4.3）的自纠样本，保留不删。）

### 4.4 未挖长尾清单（明列，按族）

A 族（13 条）：A01 隔夜跳空/分钟非同步跳动/周-月频动量反转；A02 五档撤单队列、封板瞬间订单流；
A03 板块→个股领先性卡、概念资金流卡（待数据）；A04 行业级估值分位、破净率/buffett_ratio 面、
估值水平（非增量）对 20 日目标；A05 毛利率改善、ROE 杜邦分解、业绩快报抢先度；
A06 龙虎榜席位（dragon_tiger_seat 1152 日长史=下一富矿）、融资余额（margin_trading 505 日）；
A07 评级迁移矩阵、覆盖机构数变化；A08 BDTI 油运细分、运价波动率面；
A09 个股级新闻面板（news_data.related_symbols Array 列）、新闻主题事件流；
A10 中美利差对估值的月频卡、VIX 期限结构；A11 仓单库存卡（futures_warehouse_receipt 3013 日）、
EIA 增量断供运维挂账；A12 预警事件流（alt_sz_weather_warning 9661 行）、全国多城观测渠道缺口；
A13 十大股东（top10_shareholders 274,865 对）、户均持股市值；A15 OI/清算双因子、美股解耦检验；
A17 研报文本面、新覆盖（首次覆盖）事件、目标价字段接入后重考。
B/C 族（6 条）：B01-B10 各族的③向英文/学术查询词重挖（本轮仅中文产品名检索，归因=查询词不当）；
B09 的 WB 粗颗粒 vs HS 细颗粒口径差专挖；B10 的国产替代高频消费渠道；B02 接入前的时区/PIT 评估立项；
C 族三条"渠道出现后"的重考口子。
G/V/D/E/Z 族（11 条）：G1/G2/G3/G5 的 PG 只读通道打通后三臂实跑；G3 的十大股东↔edge_holding
公告日对齐；G4 的概念按日落版≥8 版本后重考；V1 的 HMM 7 维概率 calibration 曲线单卡；
V3 的 sector_code↔880 编码同源核验；D1 三轨产能铺开实跑；D2 的"现状 goalpost_move_rate 基线读数"
（不消融也能给 Owner 的数）；E1 的自反性复核（E1 判据由 E2 独立复核）；Z1 的单测夹具替代生产旁路方案；
Z2 的探测输出落库后三臂。
外部引用待验证项（须补第二来源才可入图，5 条）：A05 中国 PEAD、A15 资金费率拥挤、
A09 媒体情绪、A02 冲击成本曲线、B 族全部（未获任何可溯双源）。

### 4.5 币圈镜像 TDM-C 线结论（本车道独有一支，链已单列）

- 纪律落实：两张 crypto 卡（`A15__03_币圈镜像资金费率对BTC`、`A15__04_币圈镜像山寨季广度`）
  均带 `market: crypto` + `mirror_of` 指针，target=BTCUSDT/ETH-BTC 汇率（UTC 日界、7×24、
  无 T+1/无涨跌停），与 A 股卡 target（沪深300/个股 hfq）**物理分列**，禁共用结论；
  A 股侧 T+1 与一字板门柱在镜像卡内明写"不得继承"。
- 对在册先例的**双向纠偏**（正/负存在断言同纪律，SOP §7.5.3）：
  ① 正纠偏：`st_crypto_mining.md` 判"全域 L 级缺口：无 crypto 行情载荷"——实测已推翻半条，
     `crypto_kline_daily` 有 19,801 行/427 日/141 币、`crypto_shadow_gate` 20 行 ⇒ 网络闸已过、真数据已落；
  ② 负纠偏：本车道首轮判"A11 EIA 整源缺失"——实测亦推翻，EIA 四组库存落在**通用长表
     macro_data 的 indicator_name 轴**（各 267 周）⇒ 新规程=负存在断言 MUST 同筛"表名"与"列值"两路；
  ③ 口径漂移登记：落库 symbol='BTCUSDT'（MVP 文档写 OKX instId 'BTC-USDT'，后者实测 rows=0）、
     表名 `crypto_shadow_gate`（MVP 写 `crypto_shadow_gate_c_l1`）、
     `shadow_tier` 20 行**全为 'trend' 一档** ⇒ 三态判别力现势不可考（缺口挂给 TDM-C-L1 车道，
     本车道不越界代建）；换源未见 Owner 裁定留痕（MVP 明言换源属 Owner 决策）⇒ 溯源断点如实登记。

### 4.6 可复核校验命令（任何人可重跑，禁信本台账自陈）

```
cd D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/entry_flow/L9
python -c "
import glob, yaml, collections
fs=sorted(glob.glob('TDM-E-L9-*__*__0[2-9]_*.yaml'))
req=['status','signal_kind','pillars_numeric','window','buckets','pillars','target','lineage',
     'preregistered_by','preregistered_at','data_binding','family','node_id','card_id','hypothesis','title_zh']
bad=0; nodes=set(); fam=collections.Counter(); st=collections.Counter(); mk=collections.Counter()
for f in fs:
    d=yaml.safe_load(open(f,encoding='utf-8')); nodes.add(d['node_id'])
    fam[d['family']]+=1; st[d['status']]+=1; mk[d.get('market','cn_a')]+=1
    pn=d.get('pillars_numeric') or {}; db=d.get('data_binding') or {}
    for k in req:
        if k not in d: print('MISS',f,k); bad+=1
    for k in ('mono_spearman_min','ic_mean_min','ic_ir_min','regime_same_sign','oos_same_sign'):
        if k not in pn: print('PMISS',f,k); bad+=1
    for k in ('signal_table','signal_column','signal_derivation','target_source','data_window_evidence'):
        if k not in db: print('DBMISS',f,k); bad+=1
    if d.get('generated'): print('GEN-FLAG(禁)',f); bad+=1
    if d.get('preregistered_by')!='st-nightmine-20261010-L7': print('SIGNER',f); bad+=1
print('cards',len(fs),'issues',bad,'nodes',len(nodes)); print(dict(fam)); print(dict(st)); print(dict(mk))
"
```
本轮实测输出：`cards 51 issues 0 nodes 45`；
`{'calibration': 36, 'ablation': 15}`；
`{'preregistered': 18, 'blocked_on_data': 24, 'blocked_on_impl': 9}`；
`{'cn_a': 49, 'crypto': 2}`。
（骨架件 45 个 `generated: true` 未被改动；新卡均另建文件、无 generated 标=受保护。）

### 4.7 建议交叉复挖 20% 名单（9 个节点，按"复挖期望收益"排）

1. **A17**（研报）— 富矿但被一列卡死：rating_change 100% 空，须复挖 pdf_forecast_extracted
   192,365 行能否反推评级迁移；consensus_daily 6.8M 行覆盖漂移（1157→2614 只）须专门处理方案。
2. **A06**（资金流）— 复挖 dragon_tiger_seat（1152 日、622,365 行）席位行为卡；
   本车道已把"残差化防共线"门柱立住，须复用到 A01/A03 检验其动量卡是否同样被共线污染。
3. **A10**（国际宏观）— FRED 族只起 2021-08-16（本车道纠偏），须复挖 us_index(1993 起/8481 日)
   与 kline_global(2014 起) 作 VIX 缺段替代，把牛段补回来。
4. **A11**（能源库存）— 本车道两度纠偏（EIA 在长表 + 增量任务持续超时断供）；
   须复挖 futures_warehouse_receipt（3013 日、2.9M 行）国内仓单库存卡 + 运维挂账 EIA 断供。
5. **B02 / B05 / B09**（免费渠道三支）— 复挖=接入门槛最低（API 申请/公开平台，属 Owner 四件事），
   其中 B09 须先把"列值面筛"新规程走完（WB_EXPORT 粗面 vs HS 细面）。
6. **G1 + G5 + A16**（同矿脉三连）— 复挖前置=PG 只读通道 + WP-0.5 部门 id 桥；
   三卡共享一次施工，禁分别立项（净零铁律）。
7. **V1 / V2**（状态快照）— 本车道已用长史面立卡；复挖=judgment 台账 12/6/40/24 行的
   "落台为何近空"根因（属他件缺口，跨车道协同项）。
8. **E1 / D1**（考试与挖掘环）— 复挖=node_verdict 58 条的增长路径与 GPU 门位排期；
   本车道已确认 ablation 语义为"双权重面板重放"非卡驱动，须在卡片规格上对齐 runner 契约。
9. **A15 crypto 镜像**（04 卡）— 复挖=宇宙成分版本轴落库 + 换源 Owner 留痕；
   解锁后此卡与 TDM-C-L1 正式卡须一并出分（当前只有 20 行单档 gate 不可判）。

### 4.8 禁区自证（无越界）

- 未做任何 git 写操作；未改 TDM/注册表/分数册；未跑生成器；未碰他人车道目录。
- 45 个骨架件（`generated: true`）零改动（校验命令含 GEN-FLAG 检查，issues=0）。
- 分数册未写（`run_card` 未调用，全部卡为预注册/挂起态，不产生分数行）。
- 临时件全部在 `D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/`
  （l7_probe_tables.py / l7_probe_cols.py / l7_probe_report.py），项目根零临时文件。
- CH 读取一律经 `scripts/backtest/fexam/ch_data.py`（ch_query_df），无裸 duckdb/无 SQL 散落文件。
- 负/正存在断言均挂三源指针（馆查命令原文+输出摘录、system.tables 筛、列值筛），
  无"凭记忆断言"；两处本车道自我推翻（A11、G/E 族 ablation 语义）均如实保留并标注纠偏过程。


---

## 来源：`docs/_working/nightmine_campaign/RX_A_ledger.md`

### L191 · 4. 收尾（三态计数与枯竭判据可信度）

## 4. 收尾（三态计数与枯竭判据可信度）

- **复挖节点数=10**（L1×6：TDM-E-L2-01/02-1/04/06/09/10；L4×4：TDM-P-P1-02/P1-05/P2-01/P3-01），全部走完三步。
- **三态计数**：
  | 态 | 节点数 | 名单 |
  |---|---|---|
  | 漏矿 | **6** | TDM-E-L2-01、TDM-E-L2-02-1、TDM-E-L2-09、TDM-P-P1-02、TDM-P-P2-01、TDM-P-P3-01（各 1 张，共 **6 张新卡**） |
  | 复挖零新增 | **4** | TDM-E-L2-04、TDM-E-L2-06、TDM-E-L2-10、TDM-P-P1-05 |
  | 翻案 | **2 条** | ①L2-09 业绩腿"仅剩研报代理可考"→实测有 `earnings_forecast` 1999 起 125,582 行自有长史 PIT 面；②P3-01 ④腿"需施工才能分层"→装置已在（condition_attribution 正门对方自己用过+日亏序列可从 run 派生） |
  | blocked 判据复证（不改判） | 5 处 | 成分口径（两源独立复证均无历史 PIT）、news_data 2025 断供、只数帽 overlay 缺件、向下摊平无 mode、X_breaker 不可当日亏替身 |
  10=6+4 全覆盖，无悬置。
- **新卡清单（NN 均接对方已用号段之后；机检=本车道实跑 yaml.safe_load 6/6 可解析、必填面齐、problems: 0）**：
  1. `docs/03_modules/_domain_backtest/exam_cards/entry_flow/L2/TDM-E-L2-01__ablation__03_六指数分布选优通道与候选池分位.yaml`
  2. `.../entry_flow/L2/TDM-E-L2-02-1__ablation__03_象限迁移确认腿与稀有路径护栏.yaml`
  3. `.../entry_flow/L2/TDM-E-L2-09__calibration__04_业绩预增催化剂腿.yaml`
  4. `.../position_flow/P1/TDM-P-P1-02__calibration__04_盈亏百分比腿与ATR缺失降级.yaml`
  5. `.../position_flow/P2/TDM-P-P2-01__comparison__03_盘中单边失效腿对照.yaml`
  6. `.../position_flow/P3/TDM-P-P3-01__comparison__04_日亏熔断禁加期分层对照.yaml`
  族分布=ablation 2 / calibration 3 / comparison 1；status 全 `preregistered`
  （L2-09 卡的行业辅轴、P2-01 卡的板块崩塌子腿各自在卡内明列 blocked_on_data 缺段，不作主轴）。
- **一句判断：L1 的枯竭判据"方向可信、判据有系统性侧盲区"**。
  可信面=其根因级结论（个股↔板块归属无历史 PIT）被本车道**两条独立路径复证**（sector_constituent valid_from 仅 6 个值、
  as-of 2022=0 行；industry_class valid_from 全部 2026-08-03、as-of 2021=0 行），8 张 blocked_on_data 无一被推翻；
  盲区=六向①实际只读了 `algo_note_zh`+`data_refs`，`invalidation`/`fallback`/`algo_refs` 里的判据陈述成批漏读
  （抽 6 个 mined_out 就有 3 个出漏矿）⇒ 按其同样方法全量抽查，"22 个 mined_out"预计还会再掉若干；
  建议把"①向须按八类字段逐字段打勾（algo_note/decision_question/data_refs/factor_refs/algo_refs/invalidation/fallback/risk_limit_refs+module_mounts）"
  升为 mining_sop 的机械步骤（本车道两次翻案与 6 张漏矿全部来自这一条）。
- **一句判断：L4 的枯竭判据更可信**。抽 4 个节点里 3 个出漏矿，但**真正"误封"只有 TDM-P-P2-01 一个**
  （P1-02/P1-05/P3-01 对方已自报收回封矿并列了长尾，属诚实登记）；其 11 条 blocked_on_impl 抽验 3 条**全部成立、无一翻案**
  （向下摊平无 mode、只数帽无 overlay、X_breaker 已接线），唯一翻案是其"④腿需施工"的隐含判断。
- **禁区遵守自证**：未跑生成器、未做任何 git 写操作、未改 TDM/注册表/分数册/他车道卡；
  临时件全部在 `D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/`（rxa_dump.py、rxa_dump.txt、fix.txt、三个探针 .py 由本车道另存）；
  CH 读取全部经 `scripts/backtest/fexam/ch_data.py`（禁裸 duckdb 遵守），404/500 失败逐条留痕并按"空结果先判静默失败"排查
  ——本车道 404 的三类真实原因：kline_sector_880 键列是 `sector_code`（误用 symbol/code）、
  earnings 表日期列是 `announce_date`（误用 publish_date）、网关拒某些子查询 HAVING 形（改条件查询绕开），
  **无一条被判成"数据不存在"**。


---

## 来源：`docs/_working/question_mining_20260927/04_chain_links/s4_ledger.md`

### L50 · 五、未挖尽面（移交后续波次）

## 五、未挖尽面（移交后续波次）

1. 其余 100 环节的同构验收题（本题面已给三角度模板：契约/断供/独立验证，可流水复用）。
2. F81 告警阈值 38 条消费面普查；F45 强制清仓绕过授权链；F40 negative_veto 断供日 fail-open 风险。
3. F51 币圈骨架（TDM-C 空 壳）与 F121 三研究域——登记态深，待施工后出题更实。


---

## 来源：`docs/_working/question_mining_campaign/04_chain_links/s4_ledger.md`

### L50 · 五、未挖尽面（移交后续波次）

## 五、未挖尽面（移交后续波次）

1. 其余 100 环节的同构验收题（本题面已给三角度模板：契约/断供/独立验证，可流水复用）。
2. F81 告警阈值 38 条消费面普查；F45 强制清仓绕过授权链；F40 negative_veto 断供日 fail-open 风险。
3. F51 币圈骨架（TDM-C 空 壳）与 F121 三研究域——登记态深，待施工后出题更实。


---

## 来源：`docs/_working/three_piece_infra/mining/family12_field_discovered_new_cases/W-131.md`

### L40 · 4. 缺口与根因

## 4. 缺口与根因

1. **根因 C1（本层最重要，也是"量纲"病的新样本）**：`module_ref` 的覆盖率**没有机读产物**，所以 121/159/182/61/23 这五个数在不同册里并存（协调册、X 册、骨架册 §三、本窗）。⇒ 本项的**第一步不是补 ref，是把覆盖率变成生成器产物并让所有引用位指向产物**（宪法 §9.5）。M3 的两说（HEAD 前进 vs 口径混用）**必须由这一产物裁决**——在此之前，任何"补 61 个 module_ref"的施工量估算都是空的。
2. **根因 C2：门的设计是"改了 A 就必须改 B"型，而"没写过 B 的节点"天然不触发。** X-28 的自测 B（`process_reaper`/`tqcenter_provider`）"结构性不触发"正是这个形态：一个从未在 TDM 里挂过说明的实现件，改它时**门找不到对应的声明槽位**，于是无事可判。⇒ 于是"61（实为 23）个空 ref"与"结构性不触发"是**同一件事的两面**：门只在**已有声明的地方**执法，而缺口恰在**没有声明的地方**。**这就是"半执法"的准确机制**，也是为什么"加强该门"若只调判据数值会毫无效果（X-28 明令"不改判据数值"）。
3. **根因 C3：fail-open 的登记面自身有重复条目**（M4 两条同 file）⇒ 说明"豁免"也是手工累积的，与 W-20（候选册双条）、W-52（ROOR 派生计数）同族。豁免清单里有重复条目的后果：两条的到期/理由字段若不一致，读侧择一即静默放宽。
4. 非根因：不是"节点数不对"（M3 已把节点/行数混用的可能列为待裁）；不是 loader 缺陷（协调册指定 `decision_map.py` 为唯一解析面，本层遵守不另解析）。


---

## 来源：`docs/_working/three_piece_infra/piece1_gate/register_manifest.md`

### L47 · ALGO-NOTE-SYNC 待办（转总筹合批）

## ALGO-NOTE-SYNC 待办（转总筹合批）

碰实现码同批需同步 TDM `algo_note_zh` + algo_flow desc：
`docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/c/create_guard.yaml`
需补 stage「查功能关键词」（探针构造 → CapabilityLookup.find → 命中即红 + 逃生标记）
与 stage「类名唯一性批量化」（一次 git grep -n -E + 归因纯函数）。


---

## 来源：`docs/_working/trading_vision/2026-09-16-skeleton-coverage-audit.md`

### L236 · 黄灯清单（覆盖未接电 98 节点，按断点分组）

### 黄灯清单（覆盖未接电 98 节点，按断点分组）

| # | 断点 | 节点组（数） | 生产断在哪 | 归属 |
|---|---|---|---|---|
| Y1 | **决策链无日循环触发面**（最大公约数） | L2 全家族(26)、L3 全家族(20)、S1(7)、S2(6)、P2(4)、P3(4)、P1-04/05、E-L4 主体(13)、C3-05 等 | `tasks.yaml` 全是数据任务；决策层唯一事件挂点=daily_kline SUCCESS→regime→pf_alloc（pipeline_events）；其余决策链无发射方 | 基建方案"一器"（本文 §七）承接，归 BT-P1-031 |
| Y2 | 盘前作战计划编排件零调用方 | E-L0、E-L0-01、E-L0-04 | daily_warroom_pipeline 零消费实证、stability=testing；daily_trade_plan testing | BT-P1-031（"一器"复用其骨架） |
| Y3 | L1 传感器教材不全 | E-L1-S2/S3/S0/S0-1/S5(5) | 总闸只吃 RegimeSnapshot；S5 仅包导出、S0 零调用——传感器未进日更面，总闸教材面窄 | 待 Owner 定必需传感器集（§八待判定-1） |
| Y4 | 预算切分模块错位 | F-C1(1) | TDM 指定 multi_strategy_capital_allocator，生产实走 RegimeMetaAllocator 装配链——**指定件仅 1 弱消费方**（审计新发现） | TDM 节点 module_ref 对齐生产装配体（改图不改码，属 TDM 台账分诊另案） |
| Y5 | 执行成本反馈断链（在案） | E-L4-14(1) | 三零件全 production，评分器→选择器回写无接线（TDM 注记实证 2026-09-10） | ex_sor 小接线工单（S） |
| Y6 | 可交易预检新件零调用方 | E-L3-10(1) | MOD-SIG-151 今日落地，调用方=0 | L3 链接线时顺带挂（随 Y1） |
| Y7 | 加仓/金字塔规则零调用方 | P3-01/02(2) | pyramiding_rules 仅包导出；Owner"TD 阶<0 金字塔建仓"的规则化载体在、无消费 | 随 L4 编排（BT-P1-031）或策略卡 1 考试线 |
| Y8 | 做T链无日触发 | P2-01..04(4) | t0_trading_pipeline testing；t_trade_coordinator 2 消费方但链头无发射 | BT-P2-055（底仓+日内回转执行模板） |
| Y9 | 卖出/离场链无日驱动 | S1(7)/S2(6) | production 成熟度、内部互调活、链头无人按日喂持仓与信号 | 随 Y1 编排器（持仓体检段先通则 S1 有输入） |
| Y10 | 委托管线无上游单源 | E-L4-01..13(13) | execution_engine/sor/QMT adapter 下半段通电；上半段无策略模板产单 | BT-P2-055 |
| Y11 | 信号健康/降级监控域内自转 | F-C3-05(1) | 仅 signal_quality 域内部 | 降级观察，随退役审计（宪法 §4.2） |



========================================================================
# 【第二遍补抽】标题未命中、正文含遗留关键词的文档
========================================================================

---

## 来源（第二遍）：`docs/_working/archive/2026-09/c_class_scattered/2026-09-07-tdm-review-round-report.md`

- 边契约族 12：M-01 边语义约定缺失（hub/父子/横切无文档）【已修：补边+叙事标注落地】；M-02 成交→持仓入库边缺失【已修】；M-03 S2-02/03/04 零出边闭环漏通道【已修】；M-04 F-C3-01 零入边+C3-03/04 零出边进化环断【已修】；M-05 C2-03 相关性判定死信【已修】；M-06 P1-04 风险否决不喂 P2-01/P2-04【已修】；M-07 AGG 不喂 P2-01 状态门【已修】；M-08 P1-06 动作分流不全+优先级矩阵未定义【边已修/优先级矩阵=协议 §7 关联】；M-09 E-L4 hub 出度 0+L4-08/09 断【已修】；M-10 L3-12 四子零边【已修】；M-11 P2-03 强平无执行通道【已修】；M-12 C2-01 intent 输入无源【注释声明隐式订阅】
- 参数口径族 9：M-13 同层多档单笔止损无选择规则（2%/4%/7%/Chandelier）【待 Owner】；M-14 做T 双源参数矛盾+正期望链不自洽（盈亏平衡胜率 67-81%）【待 Owner，图上已标注】；M-15 总仓位三口径（预算带 vs 注册表 60% vs aggregator 1.0）【待 Owner】；M-16 单 sleeve 上限 0.25 vs cap 40%【待 Owner】；M-17 单票上限四候选（清单 8% 无出处作废）【待 Owner】；M-18 资金可用三方冲突（42 号已打勘误戳）【待 Owner】；M-19 Triage 频率表双真源【待 Owner，图上已标注】；M-20 相关性三分叉（0.70/0.6 代码/spec）【待 Owner】；M-21 D67×D72 区间冲突+豁免清单对齐【待 Owner，图上已标注】
- 场景状态族 20：M-22 sleeve 回撤协议触发时点矛盾（即时 vs postmarket）；M-23 sleeve 冻结对在途 intent 无豁免【F-C2-01 注释已补】；M-24 D68 除权口径覆盖不全+跳空分档未上图【X-S1-02 已补联动注释；分档挂载点待落】；M-25 盘后利空链路欠账期不闭合【图上已登记默认行为】；M-26 交易日历数据源缺失【待登记】；M-27 数据断流降级体系残缺【P1-02 注释已补默认；传感器 fallback 待补】；M-28 不可交易持仓口径族（估值/预算/强裁基数/清退归属）【C2-04/C2-02 注释已补，估值口径待施工】；M-29 崩溃 sleeve 聚合目标+半腿接管【C2-01 注释已补默认】；M-30 新股竞价即决无分母【待 Owner/施工】；M-31 长停复牌族（时间止损假触发+临停/长停混淆）【注释已补，参数待数据组】；M-32 QMT 桥断持仓保护空白【待 93 号 playbook 扩展】；M-33 六段切换日存量处置【待 Owner，F-C1 注释已标】；M-34 二值权限门无滞回【AGG 注释已标待确认】；M-35 连败计数双源+内存态【待施工落盘】；M-36 熔断禁加期三处引用零定义【待 Owner/施工】；M-37 三重冷却冲突（代码 5 日 vs D72 vs D51）【待 Owner】；M-38 做T 账本路径未定义【待裁定+施工】；M-39 升降级族状态无持久化载体+2 连月重置未定义【C3-02 注释已标待确认，治理状态表待施工】；M-40 崩溃/重启状态重建矩阵缺失【待施工】；M-41 持久池无存储声明【注释已标，待登记施工】
- 可回测性族 11：M-42 HMM/打标器 PIT 纪律未定义【协议 §4 已立，实现待核码】；M-43 龙虎榜 T+1 vs continuous 污染+漏挂 DS【X-S1-04 注释已补 PIT 纪律；漏挂待数据组】；M-44 红节点规则只在散文【协议 §8 已立纪律】；M-45 MOD-RK-09 回测直接调用【协议 §8 已立】；M-46 状态序列冻结纪律【协议 §4 已立】；M-47 信号侧复权口径未规定【协议 §8 双价格序列已冻结】；M-48 成本模型三问题（T0 未接线/严苛度不一致/impact=none）【协议 §8 已立口径】；M-49 分频率混合编排无落码证据【协议 §8 绕行方案】；M-50 S1-06 黑天鹅/弃庄无算子【S1-06 注释已声明回测不含两分支】；M-51 顺位词表无操作定义【待施工】；M-52 竞价数据未挂+历史仅 1-2 月【盲区清单已列】
- 完备性/引用/治理族 9：M-53 E-L4-10↔MOD-L06-001 能力失配（九态状态机 vs 异步派发器）【待换锚/改标】；M-54 配股/红利税/ST 降级三缺口【待注释补挂或回测剔除声明】；M-55 人工干预入口无节点【待裁定】；M-56 份额守恒仲裁（做T vs 净额+离场后买回阻断）【待 Owner，依赖 S2-06→E-L4-12 边=R2-01 已补】；M-57 撤单率闸门零承载+42 号/D58 口径冲突【待交易所细则裁决】；M-58 X-R1 治理字段全缺【注释豁免声明已补】；M-59 C2-01 auto 节点承载发单语义【免责声明已补】；M-60 风控链路自监控 dead man's switch 缺位【X-R1 注释已标挂载点，机制待施工】；M-61 差异化收费变量缺位【协议 §9 参数位预留】

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成**：无显式完成信号
>
> **⚠️ 未完成（3 条，逐条摘录）**
> - L23: - B-07 §10.3 冲突场景仓位细则未量化（人工接管不可回测）→D9/AGG 注释【待 Owner】
> - L26: - B-10 制度参数历史时变表缺失（ST 主板 5%→10%@2026-07-06 图上硬编码实证 L2209）【图注已修/维表待施工】
> - L66: | 2 | 1（R2-01） | 1（R2-02） | 6/1 | 73/74 通过（98.6%） | R2 补修后硬门槛待复核 | 修复验证+收敛扫描 |
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 1 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）

- 修复验证：73/74 项通过（98.6%；唯一 ⚠=§35A 标记 8 条>清单 6 条的计数口径偏差，无缺漏）。结构复检：零悬空端点/零重复边/sequence 无环/修复前零边叶子全消除/未新增零边节点。回归 53/53 通过（两次）。
- 收敛扫描新发现 9 项：R2-01（Blocker，S2-06→E-L4-12 边三处声明零落盘）【Round 2 已补】；R2-02（Major，P2-04→X-S2 落 hub 断头）【已补 payload 边+叙事标注】；R2-03~R2-08（Minor×6：AGG→S1-04 边/X-R1→X-S2 叙事标/S2-01 输入仲裁声明/S2-06 互斥声明/C3-05→E-L2 边型/P2-01 门禁枚举）【全部已修】；R2-09（Suggestion：报告归档）【本文件】。
- 证伪记录：P2-01 双口径疑点证伪；F-C3 hub 父子分工自洽；X-R1 fail-closed 与 C2-01 三态机无矛盾；六组编号疑似碰撞证伪（B/M/m 大小写独立命名空间）。
- 17 项 Owner 待裁定全部在册（协议 §7），无一静默遗忘、无一越权代裁。


---

## 来源（第二遍）：`docs/_working/archive/2026-09/c_class_scattered/2026-09-09-tdm-night-greatwall-directive.md`

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（1 条，摘录）**
> - L85: 1. `.runtime/handoffs/handoff_night-gw-2300.json`：pending_tasks（BLOCKED 项+原因）/warnings/已完成清单（含 commit hash 对照）
>
> **⚠️ 未完成（6 条，逐条摘录）**
> - L9: > **完成定义**：清单 C/B/A 三表清账（打勾+commit hash）或到期挂起交接（§7），不以时间论完成。
> - L15: | 夜班施工+自审 | **GLM 5.3 Flash**（夜间免费） | 全部 C/B 类落码、A 类回填、自测、红蓝对抗、双审循环（§3） | 见 §8 禁令；失败 3 轮挂起不硬过 |
> - L25: 3. **拍板项回读**：§7 待拍板两项目前默认"流根节点=待 Owner 放行、改名拆细=不动"——开工前查 Owner 是否已批流根；未批则波次 0 跳过该步
> - L86: 2. 施工清单文档三表全部打勾/改判/挂起状态更新——**台账即交接**
> - L92: 1. 禁 `--no-verify`、`--allow-multi-domain`、裸 git commit、改门禁/规则真源本身（Gate 行为问题→挂起记台账）
> - L96: 5. 失败 3 轮挂起（§3 熔断）——**宁可少交，不可交坏的**（Owner 原则：防亏钱>进度）
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 1 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）

1. `.runtime/handoffs/handoff_night-gw-2300.json`：pending_tasks（BLOCKED 项+原因）/warnings/已完成清单（含 commit hash 对照）
2. 施工清单文档三表全部打勾/改判/挂起状态更新——**台账即交接**
3. 晨审 GLM5.3 复核清单（按序）：§5 CORE 8 项逐个复审 → 红蓝对抗台账抽验 ≥3 项复跑 → validate warn 中 R1=0 与 R21 欠账核对 → 双测试/align_all 复跑确认 → BLOCKED 项逐个开新工单
4. 验收签收标准：CORE 复审零 P0/P1 问题 + 抽验复现通过 + R1 清零 → Owner 放行收工；有问题→工单进白天场


---

## 来源（第二遍）：`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-agg-switch-design.md`

- **task_bound**：TDM AGG 生产消费切换的前置设计；映射表数字已签（2026-09-14）；会话 st-fingov-20260912 单写手
- **前序**：裁定#228/#229/#230；语义复核+重印批（2026-09-13/14）；锚定态夜批已接线（tasks.yaml anchored_state_build，2026-09-14 首跑待验证）


---

## 来源（第二遍）：`docs/_working/archive/2026-09/final3_campaign/w4_7_tdm_absorption_gap.md`

1. **来源对话**：ZCode 会话 `sess_b1a47e2c-2981-44a7-8585-879481b409a1`（标题「策略工厂」，2026-09-12 23:03 ~ 2026-09-14 02:15 CST，758 条消息）。关键消息 `msg_mtysu4x3`（2026-09-13 03:49 CST）= Owner 粘贴 2025-09 个人笔记：**十层决策树（L0-L9）× 收益率分布 PDF 预测整合设计**。即任务所指"十层决策架构+PDF 概率分布预测"对话遗产。
2. **Owner 终裁**：该对话**未立项**，仅部分吸收。十层架构不是已建系统；下文所有"已建成"均指**单个零件/模块**或 TDM 既有节点，禁止外推为"十层架构已建"。
3. **既有吸收三件套**（2026-09-13 当日产物，本文在其基础上对账 TDM）：
   - `docs/_working/2026-09-13-strategy-factory-pipeline-discussion.md` v3（遗产盘点 + TDM 升级候选清单）；
   - `docs/_working/2026-09-13-knowledge-reserve-nonpipeline.md`（流水线外六板块储备库）；
   - `docs/_working/2026-09-13-tdm-upgrade-blueprint.md` v0.2（UP-1..UP-5 升级件；2026-09-15 结案核验=**未结案保留**：模块已建成、**消费端接线待施工**）。
4. **吸收方式=D108**（TDM 头注原文）："判定用离散状态机、程度用灰度插值；情况细化用决策表/状态机承载，非加树深"。本文全部承载建议遵守此原则，**不新增 TDM 节点**。

> 结论：十层 15 个决策点在 TDM 138 节点中**无整点缺失**；4 处形态不符共享同一根因=`2026-09-13-tdm-upgrade-blueprint.md` 的 UP-2/3/4/5 模块已建成但**消费端接线待施工**（结案报告明示"未结案"）。即 W4-7 后半（Max 复验后挂节点）的真实工作量=四条接线，不是新建。

- 日期：2026-09-19｜会话：st-final3-20260919｜性质：final3 战役 W4-7 前半（本文=【M】前置件，差距表出后 Max 复验再挂节点）
- 纪律：只分析不施工；`config/trading_decision_map.yaml`（下称 TDM）零改动；`docs/03_modules/**` 零改动
- 证据等级：**A 级=ZCode 会话史库直查**（`C:/Users/fanzi/.zcode/cli/db/db.sqlite` 只读 URI 打开，message/part 表 SQL 定位）；**A 级=TDM yaml 只读解析**（138 节点逐块提取+194 边实测）；**B 级=代码/文档存在性核验**（五模块 [MODULE] 头+蓝图结案报告）

| # | 遗产点 | TDM 对应节点（module_ref 实测） | 三态 | 差距说明 |
|---|---|---|---|---|
| 1 | 0.1 跨市场联动 | TDM-E-L1-S0 宏观环境传感器（alt_data/policy_expectation_analyzer.py；蓝图注含美债 10Y/美元/中美利差/全球 risk-off/港股联动） | 已有 | 决策点已承载；"联动→分布形态"概率化为车道 E 特征候选（非决策点缺口） |
| 2 | 1.2 波动率机制 | TDM-E-L1-S4（regime/features/synthetic_vix.py；期权 IV 主+合成 VIX 后备，vix_pct∈[0,1] 历史分位） | 已有 | 连续分位=灰度插值，比遗产"机制分类"更符合 D108；若需离散机制态，挂 S4 状态机即可不建新节点 |
| 3 | 1.4 情绪极端探测 | TDM-E-L1-S2/S3/S5 + TDM-E-L1-AGG 六段相位（capitulation 冰点=恐慌投降） | 已有 | 六段相位比遗产二值极端判定更细；"极端负值区概率"待车道 E 分布预测消费 |
| 4 | 2.1 仓位管理 | TDM-E-L1 大盘总闸（regime/core/regime_detector.py，7 态概率=谨慎度；algo_note 已声明 vol_target_allocator 凯利简版）+ TDM-F-C1 预算切分（状态分布加权插值） | 已有 | 形态已是灰度插值；凯利简版 MOD-BT-082 已建成；Phase 2 完整凯利=UP-1 已建成**待接线** |
| 5 | 2.4 风险预算 | TDM-F-C1（预算带/过渡带降仓/尾部预备金）+ TDM-P-P3-03（四轨融合：风险预算/波动率目标/策略置信/现金约束） | **形态不符** | 现口径=状态预算带+历史协方差（C3-01 有 252 日 Component VaR 边际检查）；遗产=预测 VaR/CVaR 前瞻分配；升级件 risk_budget_allocator（MOD-PA-022，UP-3）**已建成待接线** |
| 6 | 3.1 板块轮动 | TDM-E-L2-01..08 板块树枝（强度/接棒 RRG/生命周期/生态判定/虹吸） | **形态不符** | 现口径=强度/资金/动量选优；遗产=各板块预测分布比较；升级件 sector_distribution_comparator（MOD-PA-023，UP-4）**已建成待接线** |
| 7 | 3.3 事件驱动套利 | TDM-E-L2-09+09-1/09-2（催化剂筛选+新闻产业链传导）+ TDM-E-L3-07-3 event sleeve | 已有 | 事件识别→传导→选股链完整；子项"事件窗收益分布预测/胜率量化"=车道 E 候选（子能力缺失，决策点已有） |
| 8 | 4.1 多因子选股 | TDM-E-L3-07-2（factor/analysis/multifactor_synthesis.py，IC 加权打分） | 已有 | 决策点已有；"前瞻性分布因子"=车道 E 特征候选 |
| 9 | 4.10 综合评分 | TDM-E-L3-03（五分制双池）+ L3-05（顺位）+ L3-08（聚合） | 已有 | 五分制+顺位=离散判定，符合 D108；前瞻因子叠加随车道 E |
| 10 | L5 执行算法 | TDM-E-L4-06（EXA 六件：TWAP/VWAP/ICEBERG/IS/POV/ALT）+ L4-01 分批 + L4-14 执行质量评分 | 已有 | 超遗产设想（遗产仅 VWAP/TWAP+冲击成本）；执行域归 QMT 桥/EX（储备库板块二归口） |
| 11 | 6.1 价格行为监控 | TDM-P-P1-01/02/05（状态机/分诊/漂移）+ TDM-X-S1-04（突破失败/退潮/派发） | 已有 | 状态机+分诊=D108 合规形态；"每持仓滚动分布监控"=车道 E 候选（依赖逐标的分布） |
| 12 | 6.5 止盈止损动态调整 | TDM-X-S1-02（止损五族）+ TDM-X-S1-03（止盈三族） | **形态不符** | 现口径=价格/回撤触发规则族；遗产=预测 P(跌)>65% 概率评审；升级件 forward_stop_loss（MOD-PA-020，UP-2，forward_stop_signal+composite_stop_score）**已建成待接线** |
| 13 | L7 风控纪律 | TDM-E-L4-12 发单前校验 + L4-09 price_cage + X-S2 D72 恐慌拦截 + C3 六分类复盘（PANIC>10% 纪律告警） | 已有 | 刚性铁律+AI 仅参数微调的边界与遗产"风控铁律不外包给 AI"完全一致 |
| 14 | L8 绩效归因 | TDM-F-C3-01..05（归因引擎/lifecycle 升降格/调权/walk_forward 防过拟合/信号降权） | 已有 | 成体系超遗产（遗产仅"归因→迭代"骨架）；分布预测因子贡献度随 UP 接线自然入归因维度 |
| 15 | 9.1 尾部风险对冲 | TDM-X-R1 kill_switch + R1-01 熔断五级 + R1-03 防御白名单（D107 尾部弹药，回测验证前 fallback 休眠） | **形态不符** | 现口径=回撤/回溯触发熔断降仓；遗产=预测 CVaR 前瞻对冲；升级件 tail_hedge_signal（MOD-PA-024，UP-5）**已建成待接线**；期权对冲执行=缺失（option_* 表 2026+ 窗口短，执行域另案） |

| 三态 | 计数 | 点位 |
|---|---|---|
| 已有 | 11 | #1,2,3,4,7,8,9,10,11,13,14 |
| 形态不符 | 4 | #5(2.4), #6(3.1), #12(6.5), #15(9.1) |
| 缺失 | 0 | —（子能力级缺口 4 处已按车道 E 候选标注于 #1,3,7,8,11 注） |

- 决策点数：**15 点/10 层**（§2 清单）。
- 差距三态：**已有 11 / 形态不符 4 / 缺失 0**；4 处形态不符=UP-2/3/4/5 接线待施工（唯一根因）。
- 产物路径：`docs/_working/final3_campaign/w4_7_tdm_absorption_gap.md`（本文）。
- 未完成项：TDM 挂节点施工=W4-7 后半（Max 复验后）；两雏形 DAL-* 算法条目登记（algo_refs 前置）未做——均超出本批"只分析不施工"边界，非遗漏。


---

## 来源（第二遍）：`docs/_working/archive/2026-09/final3_campaign/w8_deepreview_reconcile.md`

- note 非空：206/206（全部含实质审查/收口结论，零空行）；
- 含"收口/挂起"关键词：205/206（唯一例外 T08=TDM 全图对账作业件，note 仍有实质内容
  "全景 vs TDM 地图节点对账=封矿判据零缺口证明"且 rpt_t08.md 在盘，非未审）；
- workbook 报告文件缺失：0/235。


---

## 来源（第二遍）：`docs/_working/archive/2026-10/t0_matrix/HANDOFF_emoreplay_stranded.md`

本包的六段相位真源**不依赖**上述任何未落地块：`six_phase_history_v1.csv` 的宏观腿走
`c1_backtest.regime_snapshot_history`、微观腿走广度指数，映射件 `auto_mount.py` 全在 HEAD。
唯一依赖产线的是 GPU 输入包里的**连续温度计列**（`emotion_index`/`band5`/`ok_n`），
其公式已在 HEAD 且 21/21 复算一致 ⇒ 本包结论有效性不受本移交项阻塞。


---

## 来源（第二遍）：`docs/_working/automation/campaign/mining/09_骨架体检/工段作业簿.md`

- **9.1 体检月报生成器**
  - 9.1.1 五面检查器（tdm/audit/registry/samples/decay，:65-:132）
  - 9.1.2 两分建议书渲染（骨锁肉动，:158-209）
  - 9.1.3 落盘与路径注入（safe_write_text+测试隔离）
  - **缺口 WO-09-01**：调度接线缺位——月报定位"月度报告"但 STARTUP=manual，全仓 grep generate_skeleton_health 无任何 ps1/事件引用（实核）；违"永久系统四要素"自动触发项，接 pipeline_events 月度 due 或计划任务。
- **9.2 覆盖审计基准**
  - 9.2.1 电态底账（138 落格 23/98/4/13）
  - 9.2.2 漂移比对消费（check_audit）
  - **缺口 WO-09-03**：基准件再生器缺位——audit md 为手写全节点落格表（:47 "全节点落格表 138/138"），静态清单手工维护与"生成器红线"（AGENTS 第9.5节）存在张力；漂移只能报而不能自愈（重跑审计无生成器可跑）。
- **9.3 排班四件套**
  - 9.3.1 册：83 实体画像注册表（机生+regen 核验）
  - 9.3.2 器：零侵入采样双任务（scan+writeback 05:40）
  - 9.3.3 闸：四检查提交门（overlap/mem/e0/漂移）
  - 9.3.4 图：周历泳道视图（只读+冲突同源标注）
  - 9.3.5 告警：OpsAlertFeed 滞回接线
  - 缺口：无 WO 级缺口（四件套+告警五件齐且各有测试）；周历定时再生=长尾。
- **9.4 策略生命周期面（体检面⑤）**
  - 9.4.1 decay 台账直方图+failed_streak 观察名单（:132/:200-201）
  - 缺口：无（消费方语义，写入方归⑦⑧）。
- **9.5 TDM 结构面（体检面①）**
  - 9.5.1 节点/边计数+.tmp 卫生红旗（:65/:167-171）
  - 缺口：无（本体维护归对齐战役，登记接口）。
- **9.6 点亮施工（体检出口）**
  - **缺口 WO-09-02**：98 未接电节点的点亮排程台账缺位——体检建议书只到"转 Owner 拍板"为止，拍板后无 pending/施工进度追踪件（与 campaign/pending_items 体系未挂接）。
  - **缺口 WO-09-04**：血肉级建议自动执行器（清 .tmp/补采样）——建议可自动执行但无执行体，月报开单无人接单。

| 子模块 | 三态 | 自审理由 |
|---|---|---|
| 9.1 体检生成器 | **挖干封矿**（WO-09-01 除外） | 五面检查+两分建议+落盘全在案 file:line 且有测试；调度接线缺位拆出挂单 |
| 9.2 覆盖审计基准 | **挖干封矿**（WO-09-03 除外） | 电态底账数字实核（23/98/4/13）且消费链在；再生化挂研究长尾（不阻断本段封矿，属对齐域） |
| 9.3 排班四件套 | **挖干封矿** | 册/器/闸/图+告警五件齐、双计划任务在、测试 7 件实核；无 WO 级缺口 |
| 9.4 生命周期面 | **挖干封矿** | 纯消费面语义清晰，写入方归⑦⑧已登记 |
| 9.5 TDM 结构面 | **挖干封矿** | 消费接口在（:65），本体归对齐战役 |
| 9.6 点亮施工 | **挂单有主** | 98 格点亮=Owner 排程（WO-09-02）+血肉执行器（WO-09-04）挂施工波次 |


---

## 来源（第二遍）：`docs/_working/chain_piling_campaign/01_layer_charter.md`

> 唯一输入真源：`00_piling_minutes.md`（存真件，禁改写）；本文每条必须能回溯条款引用 [纪要§N]。
> 全图命名 = **交易逻辑链（TDM 2.0）** [纪要§4]；七层骨架 = 纪要§1。
> 本文只做 W3 层级定义，不展开逐问（W6）、不接线不动业务（禁业务施工 [纪要§10]）。
> `[待裁]` = Owner 未定案处，登记上报待批，不擅决 [纪要§10]。

- **层职责**：产业链/股权穿透，定名"传导图谱" [纪要§1][纪要§4]。构建"谁传导到谁"的共享结构供任意源线复用；验收线=图谱 ≥3 张带原料评估 [纪要§9⑤]。
- **输入**：自 L1 收源线原料；自外部收对标锚点（ChainKnowledgeGraph 10 万节点 17 万边等 [纪要§5]）。
- **输出**：向 L3 供传导视角（板块归属/产业链位置等）；向 L4 供传导链证据（chain_refs [纪要§7]）。
- **层间边界**：只建与源线解耦的共享传导结构——**图谱可被任意源线复用、不绑定单一源线** [纪要§4]；不产出状态变量数值（L3 之事）、不答问题、不进决策。
- **问题表关系**：62 条判读挂载表**无 L2 专属组** [纪要§6]——本层以"被引"方式入表：他层问题经 graph_ref 字段引用图谱资产 [纪要§7]；是否在 M/U/线/S/D/E/G 六组之外为图谱质量增设自有问源 [待裁]，上报 Owner 处置。


---

## 来源（第二遍）：`docs/_working/chief_fullchain_campaign/env_mining/env_08_market_state.md`

- 理由：实现面成立（代码+测试在盘、L1 唯一 verified），但图语义里"cells 挂载策略随状态激活"这条主干无代码消费证据（mounted 字段已查无读取方）——典型"图语义→代码施工令"缺口；且 24 cells/9 策略全 proposed，激活升 verified 需 sim 腿先跑+Owner production 门位，非施工可独解。币圈 C-L1=not_built 外域，随 ENV 币圈线另议，本簿不收。
- 解锁条件：①cells 消费接线施工令（L1-AGG 读 state_matrix 挂载表并输出 activation 指令）；②PP-001 整装仿真（ENV-14）跑通后 Owner 门位把 cells 逐态升 verified。
- 挂起期间 L1 总闸单机读面（regime_detector 直读）不得删改——它是唯一 verified 锚。

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：L0/L1 15 节点+state_matrix 24 cells 结构切片 | signal | 6 态×4 节点（L1/L4/P-P2/F-C1）矩阵；9 挂载策略清单；L1 全场唯一 verified |
| 2 | 代码轮：regime+plan_engine 九模块真身与测试核验 | signal | 14/15 有码零失踪；anchored_state_machine 测试在 legacy_zephyr（历史件，非 tests/regime 专目录） |
| 3 | 消费方轮：regime_detector/anchored_state_machine 全 src 反查+cells 读取方反查 | signal | 6+ 下游文件；cells 无消费方=挂起裁定核心证据（待验证留档） |


---

## 来源（第二遍）：`docs/_working/condaxis/capital/10_etf_snapshot_gap_investigation.md`

| 项 | 判定 | 理由 |
|---|---|---|
| tasks.yaml 任务配置 | **无需修** | schedule=daily_capital 正确挂载、source/fallback 配置正确、排程正常触发（21 条 run 记录） |
| schedule.yaml 排程 | **无需修** | 18:00 cron 正确；10-12 缺位是进程层非配置层 |
| 重试策略 | **无需修** | max_retries=5+jittered 已在岗且确实执行；源端整段断连时加次数无用 |
| 16 交易日缺口回补 | **不可回补（永久缺口）** | fund_etf_spot_em=当日实时快照（份额/IOPV/折溢价），无历史查询面；快照积累制固有属性（tasks.yaml:3705 注释在案）。**后果：C6 ETF 申赎差分（3_C §4 挂起项）的差分基线在 09-18→10-13 间断档，只能自 10-13 起重建相邻日差分** |
| 增量核验 | **无需跑** | 无修复即无核验对象；今日 18:00 排程已自然写入 1,643 行（10-13），车道直调复核同数 |


---

## 来源（第二遍）：`docs/_working/condaxis/sector/00_skeleton.md`

- TDM 挂点：`config/trading_decision_map.yaml` TDM-E-L2 板块选择子树，区段 :714-1669。**本车道实查注**：29 节点（含根 TDM-E-L2 与 stage 容器 TDM-E-L2-05）中，27 个计算节点 module_ref 挂满（yaml 解析逐节点核实，2026-10-13）；根 TDM-E-L2 与 TDM-E-L2-05（水温响应 stage，子节点 L2-05-1/05-2 已挂 sentiment_cycle/sector_gate）两个 stage 容器节点 module_ref 为空——研究册核验记录"29 处无一空挂"应精确为"**27/27 计算节点挂满，2 个 stage 容器空**"（grep 计 30 处 module_ref 键，含 list-form 多行）。此差异不改变结论（无孤儿计算节点），登记防后续误引。
- 数据面：三套口径（通达信 880/881、申万 L1-L3、概念）× 六张实表 + 快照/资金流/状态七表，行数与新鲜度实查见 1_universe_router.md §1。
- 图谱面：PG `ig_*` 14 表（+stock_concept 共 15 CREATE，DDL :54-407）实查规模 vs SQLite 小图零生产实例化，见 5_conduction.md §1-§2。


---

## 来源（第二遍）：`docs/_working/condaxis/sentiment/00_skeleton.md`

| 层 | 形式 | 环节册 | 核心在册件 | 首发消费方 |
|---|---|---|---|---|
| L1 温度 | 0-1 连续灰度日频＋分维度面板 | [1_L1_thermometer.md](1_L1_thermometer.md) | emotion_index_builder 六成分（MOD-ALT-EMOTION-INDEX-BUILDER） | 预算带、考试条件轴 |
| L2 相位 | 离散段＋段灰度；唯一词表=官方六段 | [2_L2_phase.md](2_L2_phase.md) | EmotionCycleSixVocab＋t0_six_phase_materialize 物化链 | 预算带（在用）、策略适用域 |
| L3 事件 | 有限封闭事件集（触发+置信度+PIT 滞后） | [3_L3_events.md](3_L3_events.md) | MOD-SIG-099/101＋TDM-E-L1-S3 口径 | 大盘班拐点确认器（主接口） |
| — 判据 | 校准/区分度/事件命中率三判据机械化 | [4_validation.md](4_validation.md) | brier_calibration＋emotion_linkage_exam 先例 | 周批裁判（资格灯） |
| — 自维持 | 日批/周批/月批回路＋权限分离表 | [5_self_sustaining.md](5_self_sustaining.md) | daily_kline SUCCESS 事件门族 | 全自动闭环 |
| — 接线 | §7.5 三线接口→TDM 节点挂接 | [6_tdm_wiring.md](6_tdm_wiring.md) | trading_decision_map.yaml 挂点缺口 | TDM 地图 |
| L4 预测面 | 明日情绪概率＋盘中滚动 | **挂起不建**（Q6 已建议：TDM-E-L0-04 在册，重复建设违内收） | intraday_tomorrow_forecast | 隔夜仓位微调 |


---

## 来源（第二遍）：`docs/_working/daily_loop_campaign/01_unwired_inventory.md`

## F 类：特殊发现（记录在案）
- F1 kill_switch 跨进程缺口：编排器 L5 读本进程单例，paper_session 的 JsonStateStore 外部化熔断态读不到——建议 L5 改读落盘态（小改，随 C 类批）。
- F2 crypto 影子线：SIM_DAILY_WAKE_TASKS 不含 crypto 任务，crypto_kline 不唤醒 9 棒（设计内"只记账不进 TDM"）；进拍板需扩唤醒词+TDM crypto 段施工（远期单）。
- F3 新闻→盘前断点：news_sentiment_window→overnight_boundary_reviser 的 plan004_input 预留字段无消费（待统筹裁定）。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign/links/README.md`

- 内收原则：新增组件必须声明替代/合并的旧组件（净零增长）
- 施工项编号沿用既有账本（IBT/TRD/DU/CNS/LK）；新卡接续编号
- 挖干即开工：本簿 SEALED 后施工项直接进执行队列，不等逐条点头
- 全部论文/标准引用带出处；GitHub 开源可复用实现须在 §标准件 标注仓库与许可证

| 向 | 内容 |
|---|---|
| ①上游输入 | 谁喂本块（表/文件/事件/上游环节） |
| ②数据原料 | 用到的表/文件/因子/指标（含登记状态） |
| ③状态输出 | 本块产出的状态量/产物（schema+落点） |
| ④下游消费 | 谁吃本块输出（消费代码路径实证） |
| ⑤自动化挂点 | 产槽/事件触发/计划任务（现状：在产/休眠/缺位） |
| ⑥缺口债 | 缺什么断什么欠什么（编号引 LK/DU/IBT/TRD/CNS 账本） |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/ADJ_rulings.md`

## Z-C10 R01 与 M0 不逐位一致＝**接受＋披露＋排修，不中断在跑全量批**
- **实测**：做T R01 卡声明"与 M0 同参、零重实现"，等价复算发现两侧**不逐位一致**；根因＝全局 `astype(float64)` 改写次序翻转浮点边界，界量 **0.102% pair、净均 ≤ +0.16bp**；已用同一 `run_model_m0` 双腿逐位复现两侧产物，并排除源数据漂移（CH 计数 4,615,139 全等）。
- **裁定**：不因此停已在跑的 271 批全量（停＝重付 ≈66h）。理由：偏差量级 ≤0.16bp，比成本口径（31.2bp／前置 ≥30bp）低两个数量级，**不改变任何格子的存活判定**；但必须①在交付物里披露界量与根因，②立"逐位齐平"施工项，③若日后有结论落在 0.16bp 量级附近（例如两策略差 <1bp），该结论一律标"低于噪声底，不可比"。
- **连带**：`ignition` 相位在研究窗内 0 日却**静默缺席**（不是 INSUFFICIENT）判为监控完整性缺陷——缺席必须显式落 `insufficient/absent` 态，禁让矩阵"少一行"就过去。已并波次 3。
- **不照做会怎样**：为一处 0.16bp 的浮点次序停 66 小时机器，是把可披露的数值噪声换成确定的工期损失；反过来若悄悄改引擎让两侧对齐而不披露，就是制造第二次"账面已落实测未达"。

## Z-C8 通用口径（本夜新增两条立法级口径）
1. **"账面已落"一律以 HEAD＋实测双证为准**：本夜三次实测把交接材料的数字改小或改性——"10 批在排队"实测 pending=0、"881 已落 469→728/729"实测史起点 2021-08-02 且成分未扩容（DU-01/02 不可销口）、"L04-C01/C02 已落地"实测**表 0 行、注入源未注册、读方为 0**。凡"载体在＝功能在"的推定，一律降级为"载体在、消费未证实"。
2. **豁免区文档口径**：`docs/_working/` 新件只写 `ttl: task_bound`，**禁带 `doc_type`**（TTL-METADATA 与 EXEMPT-ZONE-FM 方向相反）；本地 frontmatter 预检对该情形返回 exit=0（有盲区），故批量落门前必须小批试投验绿。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/GPU_merge_audit.md`

**待总筹／LANE-LAND2 定夺三件（本车道只登记不代裁）**：
①`gpu_landscape.md:43,44,52` 三句二手 benchmark 是否要复采一手源入图（否则永久停在 git 历史）；
②LEAN 一家的 stars／许可证／URL 复采（当前标待验证，是②文表内唯一空洞）；
③前一轮 `lane_gpu.yaml` 曾向总筹呈报的三件待裁（Phase 序／CuPy 新依赖出厂／①文三条口径是否回写 19 号文与 03 号文）本车道**未代改任何他道文档**，仍待裁。

> 车道＝LANE-GPU 收口执行｜总筹＝st-qmine-20260925｜A 版真身＝已落 HEAD 的 commit `37aeecedcd`（五件 488 行）｜B 版＝盘上新写未落五件。
> 本件性质＝案卷（不是裁定）：只记"实测事实＋并入落位＋遗留点"，取代关系与门的放行由总筹与 LANE-LAND2 判定。

→ **本车道判定**：真缺口 6 项（LEAN／hftbacktest 三连证／vectorbt 三项元数据／④文缺硬件红线／①文缺两条口径／ann_return 容差单列）。
总筹指称的"五家全无""容差全无"两条**过判**，本件如实记双面，**不据此推翻 B 版五件的真源地位**（B 版仍是唯一真源，文件名与章节结构未动）。

**诚实标注（不硬造成全量）**：LEAN 一项 A 版仅给"无 GPU 回测模块"的搜索实证结论，**未记 URL／stars／许可证／年份**；B 版合并前整家缺失。本车道**不凭记忆补元数据**，在表内标"两版均未实取→待验证，属长尾复采义务"。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L01_regime/s1_hmm_kernel/MINE.md`

---
ttl: task_bound
title: L01-S1 子模块挖矿簿 · HMM 四态检测核（MOD-REGIME-001）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（六向封口，缺口三态裁定见 §5）
---

| 编号 | 内容 | 状态 |
|---|---|---|
| D7 | 8 态转移先验/相似日/Brier 三消费点未接线（需求册在册） | 沿用（归属见 L02-G 册） |
| L01-S1-G1 | 4 态降维后 ConfidenceSignal 档表阈值仍沿用 9 态校准值（detector :193-194 自注），未做 4 态重校准——**册内未见编号** | 新登 |
| L01-S1-G2 | 锚定恢复"标签语义可跨 refit 比较"≠"方向预测力可跨期比较"（:64-67 裁定警示），但消费侧 owner_band_t/开关器仍把 dominant 当方向轴使用——**册内未见** | 新登 |

| 缺口 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| D7 | 挂起排期 | 解锁条件=三零件（8 态/相似日/校准）消费方接线批（L02-G 册 L02-G-C01）；终局要（预测→Brier 回填→自动校准闭环=消灭人工判"像不像"），非封矿 |
| L01-S1-G1 | 施工（随 S5 档表统一批） | 阈值与态数不匹配=系统性偏差，终局全自动化下无人肉眼纠档；判据口径不动，仅重校准值来源，属修复非新立 |
| L01-S1-G2 | 挂起排期 | 终局要"态→风险分档"与"态→方向"两套消费语义分离；解锁条件=S7 六段真源收编完成（附录 C 步 2）后统一定语义词表，现禁改判据 |

| 轮 | 矿脉 | 判定 | 备注 |
|---|---|---|---|
| R1 | 内部：detector 常量/档表/地板/探针行号复核 | signal（:107/:195/:232/:419 全部实测复核） | — |
| R2 | 内部：消费面全仓 grep（24 文件） | signal（较 SKEL 13 点净增 5 个脚本侧消费者） | — |
| R3 | 外部：ensemble-HMM + GMM 排序约束 2 轮检索 | signal 1（ensemble 投票=二期待验证候选）／noise 1（排序约束单源，**归因=来源为工程博客非学术/一线，降优先级**） | — |
| R4 | 外部：后端可复用实现替代 hmmlearn | 已查无（查法见 §③④） | 记档 |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L01_regime/s2_overlay_transition_engine/MINE.md`

**本册封矿判据**：六向封口（含已查无+查法）；未挖长尾=35 维评分函数的**公式级逐行对表**（约 1,383 行，属施工级而非挖矿级余量，已随 S2/S3 册挂施工项）→ 子模块**封矿**，余量以施工清单形式移交。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L01_regime/s4_feature_pipeline/MINE.md`

**本册封矿判据**：六向封口 + 三件新缺口登记，未挖长尾=12 件 features/ 正文公式逐行（施工级余量，非挖矿级）→ **子模块封矿**。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L01_regime/s5_shrinkage_risk_signals/MINE.md`

| 缺口 | 裁定 | 理由 |
|---|---|---|
| A16 | 施工（P1，Owner 选型门位） | 两表并存=每次分配结果依赖"哪条路读到哪张表"，终局不可自动审计；探针已备，选型后即 import 别名同源（净 -1 表） |
| D5 | 挂起排期 | 宏观两融已供、其余三组解锁=外部数据源账号 |
| L01-S5-G1 | 挂起排期 | 终局要"校准闭环自动化"，但解锁条件=快照表有足量分量列真值（G2/先决 L01-C08 分量列回填）；现在接=空跑 |
| L01-S5-G2 | 施工（P2，随档表统一批） | 阈值与态数不匹配属系统性偏差，无人复核即长期错 |

| 轮 | 矿脉 | 判定 | noise 归因 |
|---|---|---|---|
| R1 | 内部：档表/地板/对账探针行号 + 11 系数函数清单 | signal | — |
| R2 | 内部：confidence_calibrator MATURITY 实测 | signal（design 态实证，SKEL 仅"未接线"散文） | — |
| R3 | 外部：vol-targeting 双源 | signal | — |
| R4 | 外部：confidence→position sizing 机构件 | noise | 归因=**来源贫矿**（命中多为通用仓位管理文，与"概率可信度折系数"语义不贴合）→ 已查无 |

**本册封矿判据**：六向封口；未挖长尾无（校准器接线属施工项）→ **子模块封矿**。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L01_regime/s7_anchored_state_track/MINE.md`

| 编号 | 内容 | 册内出处 |
|---|---|---|
| L01-C01（在册） | schema 补符号随车修 | SKEL §12；本册实测=以本地常量旁路达成"能跑"、未达成判据 |
| LK-L01-2（在册） | schema 缺符号导致导入断裂 | 本册改判为"已旁路，断裂点在 schema 侧" |
| L01-C04 步 5 | 锚定表 rN 双词表语义待裁（HMM 七态 vs 波动四档同名 rN，附录 C） | 附录 C 在册 |
| L01-S7-G1 | 本地 SQL 常量=第二真源隐患（去重口径与 alloc_shrinkage_daily 同族件并存两份） | 册内未见 |
| L01-S7-G2 | MATURITY=design 但已承担生产熔断 cap 输入=成熟度与职责不符 | 册内未见 |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L01_regime/s8_six_phase_truth_chain/MINE.md`

| 编号 | 内容 | 册内出处 |
|---|---|---|
| L01-C04 步 2/4 | 共享真源收编 + 历史结论口径版本戳 | 附录 C 在册 |
| L01-C05 | 六段全史 CSV 0033 批落地（本册实测未落） | SKEL 在册 |
| LK-16 | 六段↔盘中五态映射未落地 | 09 号文在册 |
| L01-S8-G1 | 微观腿两阈值无预注册考试卡（euphoria/distribution 判据属经验值直接进产） | 册内未见 |

| 缺口 | 裁定 | 理由 |
|---|---|---|
| L01-C04 步 2/4 | 施工（P1，在册） | 两表靠守卫=守卫失效即静默分叉；收编后净 -1 表 |
| L01-C05 | 施工（P1，在册） | 终局要"相位全史可自动重算"；前置=creation_token+模块翻译登记（机械动作） |
| LK-16 | 挂起排期 | 解锁=L09 车道六段↔五态映射页；本层只供真源侧 |
| L01-S8-G1 | 挂起排期 | 终局要"每判据有考试"，但现改=动判据（禁区）；解锁=下一轮预注册窗口，先登记为候选卡 |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L02_emotion/b_history_replay_line/MINE.md`

> 施工班读本件时以下述为准，**原锚未逐条改写处即视为已知假锚**：
>
| 引用处(叶文件:行) | 被引路径 | 原锚 | HEAD 行数 | 态 | 处置 |
|---|---|---|---|---|---|
> | `b_history_replay_line/MINE.md:22` | `34_d_backtest.md` | 3043 | — | PHANTOM_FILE | NOT_IN_HEAD(未落地)——先落字节再引锚 |
> | `b_history_replay_line/MINE.md:22` | `t0_condition_matrix_v1.meta.yaml` | 138 | — | PHANTOM_FILE | NOT_IN_HEAD(未落地)——先落字节再引锚 |

| 项 | SKEL（09-25 记） | 本册实测 |
|---|---|---|
| 代码件 | 滞 `.aidrafts/st-emoreplay-20260923/`，主区无 | **`src/zephyr/alt_data/emotion_index_replay.py` 已在主区**（头注 MATURITY=experimental，TESTS 指 `tests/alt_data/test_emotion_index_replay.py`，两件均存在）；`git status --porcelain` 实测=**`??` 未跟踪**（盘上有了，未进 HEAD） |
| DDL source 列 | 待补 | **已在 HEAD**（`market_emotion_index.py:42`） |
| 文档五件 | 滞 .aidrafts | `docs/_working/emotion_line/{history_replay_report_v1.md, gpu_emotion_condition_matrix_v1.csv, gpu_emotion_condition_matrix_v1.meta.yaml, gpu_emotion_condition_cells_v1.csv}` 实测已在盘且为 **`A ` 已暂存态** |
| 数据面 | 8,596 行 replay | CH 实测：close_final replay 8,596 行（1991-06-10→2026-08-31）+ live 18 行（2026-09-01→09-24）→ **接缝在 08-31/09-01，中间 09-01 前无空洞但 08-31→09-01 恰为 1 交易日界**（SKEL 未记的具体接缝位置，本册补） |
| 悬空引用 | 34_d_backtest.md:3043 与 t0_condition_matrix_v1.meta.yaml:138 引"主区无此件" | 随文档件已暂存而**消除**（登记销口） |

**④ 缺口清单**：L02-C01（在册，本册缩范围）；呈批项 P-2/P-5（在册）；**L02-B-G1 回放线与活管道 source 列去重语义仅靠约定（无机械守卫）**——册内未见。

**⑥ 挖矿日志**：R1 内部：文件+git 态三方实测→signal（**改判：代码面已落盘、文档面已暂存，缺口从"复职五类"缩为"两文件提交"**）；R2 内部：CH 接缝探针→signal；R3 外部：回放/回填方法论→noise，归因=方向本就无矿。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L02_emotion/c5_leverage_margin/MINE.md`

| 向 | 发现 |
|---|---|
| ①上游 | 内部：margin_trading（akshare 交易所明细 T+1）。外部：两融余额作为情绪主成分的卖方件已在册（中信建投 20+ 指标含两融，题录沿用 `external_methodology_review.md`）→ 沿用 |
| ②下游 | 内部：C5→指数；另 cohort_ledger_daily / 板块杠杆资金（S2/S12）共用该表。外部：已查无 |
| ③算法 | 内部：变化率而非水平值（已消除存量规模漂移）。外部：已查无（查法：margin balance momentum 定向未得方法文） |
| ④后端 | 内部：任务 `margin_trading_incremental` 在跑；**"0 新日静默"哨兵仍缺**（本册虽判定未真断，但哨兵缺口不因此消失）。外部：已查无 |
| ⑤前端 | 内部：成分卡。外部：已查无 |
| ⑥数据字段 | 内部：margin_balance 在；质量画像=**深史仅 500 日（2024-09 起）**，250 日分位窗勉强达标、2024-09 前需新外部 API 通道（G5 在册）；S4 回补的 442 日为考试内部物化，未入生产表（**本册净新增缺口 G1**） |

**② 实测**：`emotion_index_builder.py:306-313`（`_SQL_MARGIN_BAL` :118-122 `sum(margin_balance)` group by trade_date；`pct_change(_MARGIN_CHG_DAYS=20)` :77）；考试（重考后）**NO_SIGNAL**（RankIC −0.031，S4 回补 442 日后 obs 25→142）。**改判（本册 CH 只读探针）**：`margin_trading` 实测 **2024-09-02→2026-09-23 / 500 唯一日**，逐日行数 09-15→09-23 = 4105/4105/4105/4105/—/—/4105/4106/4106（**09-19、09-20 为周六日，非断供**）→ SKEL/12 号文"09-19 起 4 个交易日断更=DU-03"的表述在**交易日历口径下已被高估**：实际缺口为 09-24 一日未出（交易所 T+1 披露节奏下属正常滞后），DU-03 应改判为"已自愈/滞后口径待复核"，本册不改判据、如实记"叙述与现状脱节"，交落地车道与数据班复核。

**④ 缺口**：G5（两融深史，在册）；DU-03（在册，本册改判建议）；**L02-C5-G1 考试用 442 日回补史未回流生产表（考完即散，指数侧 obs 仍受限）**；**L02-C5-G2 0 新日静默无哨兵**（与 L02-A-G2 同案）。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L02_emotion/c6_news_sentiment/MINE.md`

**④ 缺口**：G6（rule 单法）/DU-05/DU-06（在册）；**L02-C6-G1 rule 腿与 market 腿日期错位 3 日（同一 scope 下 data_source 分布不一致的根因待查）**；**L02-C6-G2 LLM 分支 experimental 却经旗标进入生产写库路径（成熟度与门位不对齐）**。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L02_emotion/f_legacy_emotion_cluster/MINE.md`

**④ 缺口**：LK-02（枚举收敛移交治理班，在册）；G9 能力反查索引漏报（在册）；**L02-F-G1 四件中三件 production 却无"档位计 vs 温度计"消费口径词表（下游可能混用）**；**L02-F-G2 intraday_sentiment_loop 自称 production 但不注册任务=挂接真空**。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L02_emotion/g_tomorrow_emotion_forecast/MINE.md`

**③ 六向**：①上游 kline_index 000300 全史（:114-117）+ 情绪/状态轴。②下游 判定台账三表→作战室→Brier 回填。③算法 转移先验+相似日+校准三件；外部=概率预报校准口径与仓内 Brier 一致（17 号文 §一已立法，沿用不重复引）。④后端 盘中腿挂点缺位（见上）。⑤前端 作战室组件（人工面）。⑥字段 signal 轴齐；质量画像=真值窗短（情绪 16 日全成分史）。外部（本轮新增）：状态层"点预测天花板"铁律已在 panel INVARIANT 记 52-53%，与外部"方向预测困难"共识一致 → 单源，标待验证不入图。

**④ 缺口**：D7（在册，本册范围收窄为"盘中滚动腿"）；LK-L01-…；**L02-G-G1 09 号文环节 2"本环节无专属概率表"的结论应更正为"概率表=next_day_forecast 族（盘后已产）+ 盘中未产"**；**L02-G-G2 Brier 回填与 next_day 产出的双向链路无机读校验件**。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L03_sector/b2_state_aggregation_kernel/MINE.md`

**④ 缺口**：LK-03（有效成分集未定，在册）；**L03-B2-G1 rrg_quadrant 20,401 行空串无归因登记**；**L03-B2-G2 881 族 state 仅 1 日→任何按 729 码做的截面统计在近史内都是混合宇宙（可比性断层）**。

**⑥ 日志**：R1 内部：state 表分族/分布探针→signal（两条新缺口）；R2 外部：动量反转两源→signal；R3 外部：RRG→沿用。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L03_sector/b5_rotation_algorithm_family/MINE.md`

**④ 缺口**：G14（三标尺升维）/G5（坐标系）/D17（三标尺原料待接线）在册；**L03-B5-G1 15 件零消费边的算法农场未做内收申报**；**L03-B5-G2 881 行业族轮动态从未产出（补采后无人重跑 RRG/动量）**。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/s1_conduction_gate/MINE.md`

**④ 缺口清单**（沿用 L04-Cxx／LK-xx／Dxx；新缺口续编并注"册内未见"）

---
ttl: task_bound
doc_type: log
title: L04-S1 子模块挖矿簿 · 板块→个股传导段（L2-06 家族：强度调节分/三级放行/龙头定位）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L04
status: MINE 完成（六向封口，缺口三态见 §5；长尾 2 条见 §6 尾）
---


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/s2_constituent_mapping/MINE.md`

**④ 缺口清单**（沿用 L04-Cxx／LK-xx／Dxx／DU-xx／IBT-xx；新缺口续编并注"册内未见"）


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/s3_candidate_pool_chain/MINE.md`

| 项 | 实测值 | 出处 |
|---|---|---|
| 载体表存在性 | **实测：`c1_market.stock_candidate_pool` 在 CH 中已建表（system.tables 命中 1），行数 0、交易日 0（min/max 返回 1970-01-01 哨兵）** | 本册 CH 查询 |
| DDL 真源 | `schemas/categories/market/market_stock_candidate_pool.py` **NOT_IN_HEAD**(未落地字节=主区盘上未跟踪件 111L，本册 `:25-75` 在该稿内成立；HEAD 判空经 `git cat-file -e HEAD:…` 复核于 2026-09-27)：16 列，`trade_date/stage/symbol(+MATERIALIZED exchange, symbol_canonical)/sleeve/...`，ReplacingMergeTree 按 (trade_date,stage,symbol) 同键替换；**PIT 消费契约明写在文件头**："决策日 T 取 max(trade_date) < T 的分区（shift(1) 防未来函数，对齐 daban_engine_load 先例）"；`calc_mode: lazy` | 文件 :25-75 本册 Read |
| 注册进 DDL 应用链 | `scripts/ch/apply_market_tables_ddl.py:474,556` 已 import 并注册目标表 | 本册 grep |
| 注册进机账 | `docs/03_modules/_cross_layer/database/business_data_categories.yaml:3172-3177` 与 `:5084-5089`（同一 category_id 出现两次，见 G6） | 本册 grep |
| 生产者 | `signal_ashare/core/candidate_pool_snapshot.py`（MOD-SIG-152，MATURITY=testing，CREATION-TOKEN `candidate-pool-snapshot-l04c01-20260925`）：`_TARGET_TABLE` :75、`POOL_INSERT_COLUMNS` 16 列 :97、`DEFAULT_STAGE: Final = "close_final"` :80-81（**pre_open/intraday_vN 仅注释预留，无产码**）、`run_pool_batch_for_day` | 本册 grep |
| 注入源现状 | `_BUNDLE_SOURCES: list[PoolBundleSource] = []`（:251）；全仓 grep `register_pool_bundle_source` **只有生产者文件自身的 3 处注记/文档，无任何注册调用点** → 契约"无注册源=空池如实缺省"当前生效 = **触发一次即写零行** | 本册 grep（:8,:34,:36,:251） |
| 生产触发面 | **已从"无"升为"有侧带"**：`strategy_pipeline/daily_gate_snapshot.py:290-317` `_collect_candidate_pool`（docstring 自称"LK-04 通电侧带（L04-C02 最小侵入）"，独立 try/except fail-open，异常折 `status=absent`）在 :418 `collect_gate_snapshot` 内被调（:420 传 switches）；上游 `daily_decision_orchestrator.py:75,688` 驱动 `collect_gate_snapshot(day, market_state, reader)` | 本册 grep/Read |
| 调度注册 | `src/zephyr/data/config/tasks.yaml` grep `daily_gate\|candidate\|gate_snapshot` **零命中** → 触发面不在数据采集批里（属策略侧日循环），本册未追到 AutoRuntime 内的调用注册点（长尾 T1） | 本册 grep |
| Tier 维护腿 | `pool_tier_maintenance.py`（MOD-SIG-139）外部引用实测仅 `signal_ashare/__init__.py:124`（导出面）+ 聚合器注记 :7/:10/:35/:204 → **无生产调用方**，故 DDL `tier_slot` 注记"未接线恒 NULL，不硬凑" | 本册 grep |
| 读方（消费侧） | 全仓 grep `stock_candidate_pool` 命中集 = 生产者 + 门快照采集 + DDL/apply 脚本 + 机账 yaml → **SELECT 该表的消费码 0 处**（L4 买卖 / P2-02 做T调度 / P1 体检 / BM-BUY-03 / 整装回测均未接，与生产者头注 :5 自述一致） | 本册 grep |
| 上游原料表 | 文档基线（SKEL W2②）：dragon_tiger_seat 4.5 年 / money_flow 六年 / limit_up_pool 54 日 / limit_up_down 49 日（DU-14）/ auction_snapshot+auction_book（DS-082）；本册未机测 | 12 号文 §1.2 基线 |

**④ 缺口清单**（沿用 L04-Cxx／LK-xx／Dxx／DU-xx；新缺口续编并注"册内未见"）

| 项 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| G1 读门面 + 下游接线 | **施工（本环节头号新施工项，建议编 L04-C09）** | 载体无人读=资产零收益；一个 PIT 读门面件（`shift(1)` 强制、返回当日池快照）同时消灭"每个下游自己发明取法"的人工核对，主判据一票放行；与 L04-C02 实现批串行（源先于读） |
| G2 注入源 | **挂起排期（等 LANE-BUILD）** | 已授权他车道施工中，本簿禁重复施工（连坐纪律 §3.4）；解锁条件=LANE-BUILD 落地后由本簿复核"首行真值日" |
| G3 零行哨兵 | **施工** | 终局=无人值守，0 行日必须由机器发现；复用既有数据哨兵框架（12 号文 DU 面），不新建子系统 |
| G4 日内 stage | **挂起排期** | 解锁条件=盘中事件通道有主（同 S1-G3）+ L3-11 竞价腿消费方立项；终局要（日内动态选股是本环节不可少的一段），非封矿 |
| G5 变更流事件表 | **挂起排期** | 解锁条件=C01 累计 ≥20 交易日真值（事件表可由快照差分回填，先建表=空表；差分脚本可作一次性探路降级） |
| G6 机账重复 | **施工 P3（顺手）** | 纯登记一致性，单条删除 |
| G7 漏斗阶段存活数 | **施工（并入 G1 门面批的列扩展，不另立表）** | 压缩率是漏斗参数唯一可归因面；净零声明：不新建表，`snapshot_meta` 内加 `funnel_survivors` 逐阶段 dict 即可 |
| G8 挂点归属 | **待核（非三态，属挖矿未尽项）** | 见长尾 T1，禁在本册下结论 |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/s4_factor_layer_and_news_dim/MINE.md`

**④ 缺口清单**（沿用 L04-Cxx／CNS-xx／DU-xx；新缺口续编并注"册内未见"）


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/s5_tradability_filters/MINE.md`

| 向 | 发现（内部反查 ＋ 全网搜索） |
|---|---|
| ①上游该喂什么 | 内部：该喂的三类原料实测**两类在、两类空**——在=stk_limit（920 万行深史，含 st_flag/board）、stock_daily_basic（circ_mv/float_share 满覆盖）；空=suspend（0 行，三任务在册）、ipo_schedule（0 行）；另缺"账户上下文"（`AccountContext` 权限/一手资金查的输入，属执行层回灌，本环节无源）。外部：涨跌停约束下**可交易信息本身是信号**——《Do Daily Price Limits Stabilize Stock Markets?》CUHK 中国研究中心（2019-07-18 https://cbk.bschool.cuhk.edu.hk/do-daily-price-limits-stabilize-the-markets/ ）与《An A-Share Board Chasing Strategy Based on the JoinQuant Platform》（2025-01-21 https://www.researchgate.net/publication/388163925 ）两独立来源支持"封板状态须进池而非仅进拦截"→ 现设计把"涨停封死"只作**排除**，未把"一字/秒板/封单厚度"作**分层输入**（归 L3-07-1 打板 sleeve，本册只登记事实）。**A 股适配闸**：两源均以 A 股涨跌停制度为本体（非美股迁移），适配无障碍 |
| ②下游该喂谁 | 内部：输出（可交易布尔 + 排除原因分类）设计喂三处=L3-01 Universe 剔除、L3-10 预检（喂 L4 执行兜底）、`stock_candidate_pool` 池成员；**实测三处均未吃到**（预检调用方 0；池快照 `tier_slot`/过滤结论无列——S3 实测 DDL 16 列里没有"被哪条硬过滤拦下"的留痕列）→ 新缺口 G1：**硬过滤的淘汰原因不落库，漏斗不可归因**。外部：已查无（查法：排除原因的下游呈现无外部方法论分歧，业界=日志/reject reason code，与本仓 `BlockedReason` 枚举同构） |
| ③算法/机制业界学界 | 内部：现役三件套=绝对额门槛（500 万日均成交额）、次新 30 天、弃庄概率 0.95 + 涨跌停幅度表（board/ST 感知）+ 封死判定从 close/prev_close 推导（:27，"从原始 close/prev_close 推导涨跌停封死状态，经骨架"）而非直用 stk_limit。外部（换手/成交额约束建模，两独立源）：《Deep Learning Enhanced Multi-Day Turnover Quantitative Trading Strategy》arXiv（2025-06-02 https://arxiv.org/html/2506.06356v1 ）以成交额/换手为组合可容纳规模的显式约束；CUHK 价格限制研究（上一行）指出价格限制引发流动性迁移（magnet 效应）→ 二者合读支持本册判语：**门槛应相对化（ADV 分位/占全市场成交比）而非绝对元值**；现役 2 亿/500 万两把绝对尺随市场扩容与通胀单调漂移，2020 年的 2 亿≠2026 年的 2 亿（该推论为**本仓内生推理 + 外部两源支撑其前提**，未冒充"业界定论"） |
| ④后端代码缺什么 | 内部缺五件——(a) 预检零接线（LK-04 家族）；(b) **涨跌停幅度表三处并存无对表**：`tiered_screening_filter.limit_pct_for`（:72）、`tradability_preflight._limit_ratio`（:109）、`AkshareIngestProvider._limit_pct_of`（被 :90 注记为对齐对象）→ 任一改动即口径漂移，属 RULE-SSOT 违例候选（新缺口 G2）；(c) fail-open 默认值无告警（1e12/0.0 静默放行，G4）；(d) 停牌/次新两腿无数据即"永不排除"，与 BM-SEL-16"绝对排除"设计相反，**当前实现事实上无法执行停牌排除**（G5）；(e) 淘汰原因无落库位（G1）。外部：已查无（查法：可交易性规则的可复用件已在 SKEL §4 登记 rqalpha/vectorbt，本册判其"撮合层内置"与本仓"独立纯函数核"架构不同位，不换轨，只作对表参照） |
| ⑤前端怎么呈现（只登记） | 内部：`screening/screening_funnel_report.py` 即"人工看漏斗淘汰率"的面（它现在就是 tiered filter 的唯一消费者）→ 报告器是**人工审阅件**，终局要机查：淘汰率异常应由哨兵判，不靠人读报告（登记为 G6 的人工环节）；预检结果无任何展示位。外部：已查无（查法：拒绝原因呈现=标准 reason-code 列表，无外部争议） |
| ⑥数据字段有没有 | 内部逐字段：`limit_up/limit_down/limit_pct/st_flag/board` ✓（stk_limit 深史 2015 起）；`circ_mv/float_share/turnover_rate` ✓（2021 起，近 3 日 0 缺失）；`amount`（成交额）✓在 daily_valuation 但**该表行数 09-24 只剩 1,500/5,557=27% → "日成交>2 亿"这第三关正在日毁**；`suspend_date/resume_date` ✗（0 行）；`list_date` ✓在 stock_basic（但 CNS-10 指定的 ipo_schedule ✗0 行）；`reason`（停牌原因）✗。**质量画像（闸 4）**：字段在但断供的三项=suspend/ipo_schedule/daily_valuation 覆盖；字段在且可用的两项=stk_limit/stock_daily_basic——**结论：本层不是"没数据"，是"数据在错的表/对的表没产出"三类混合，处置动作完全不同**（对应 G5/CNS-10 改判/L04-C03） |

**④ 缺口清单**（沿用 L04-Cxx／DU-xx／CNS-xx；新缺口续编并注"册内未见"）

> 施工班读本件时以下述为准，**原锚未逐条改写处即视为已知假锚**：
>
| 引用处(叶文件:行) | 被引路径 | 原锚 | HEAD 行数 | 态 | 处置 |
|---|---|---|---|---|---|
> | `s5_tradability_filters/MINE.md:87` | `battle_map_05_stock_selection.md` | 1394-1436 | — | PHANTOM_FILE | NOT_IN_HEAD(未落地)——先落字节再引锚 |

| 轮 | 矿脉 | 判定 | signal/noise 与归因 |
|---|---|---|---|
| R1 | 内部：八表列结构与起止实测（valuation/daily_basic/indicator/suspend/limit_up_down/stk_limit/stock_basic/ipo_schedule） | signal（改判 4 处） | suspend 0 行但三任务在册；ipo_schedule 0 行；circ_mv 无 NaN；DU-11 阶梯恶化逐日数 |
| R2 | 内部：过滤器参数实装状态 + 消费面 grep | signal | 参数已落地（proposed 标注失真）；唯一消费者=报告器；输入侧 fail-open |
| R3 | 内部：预检五查函数体 + 调用方 + instrument_master 载体 | signal（部分） | 调用方仍 0；CH 无 instrument/master 表 → 快照取数路径未追到（长尾 T1） |
| R4 | 外部：涨跌停制度与可交易性、换手约束（1 轮） | signal 3 / noise 4 | noise 归因=①百度百科词条（百科非方法论，闸 1 剔）②BOCHK 基金页（营销，无方法论）③docin/聚合站论文转载（不可溯）④"enterprise digital transformation→liquidity"（主题漂移）；有效=CIFER/CUHK 价格限制（2019）、arXiv 2506.06356（2025）、ResearchGate JoinQuant 打板（2025）；Gank Interview 私募面经（2026-01）为工程博客单源，标**待验证**未入图 |
| R5 | 外部：开源可交易性规则件 | 已查无（查法见 §④行；SKEL §4 的 rqalpha 已登记，沿用不重开） | 记档 |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/s6_stock_state_axis/MINE.md`

**④ 缺口清单**（沿用 L04-Cxx／LK-xx／M-xx；新缺口续编并注"册内未见"）


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L05_t0/_INDEX_MINE.md`

---
ttl: task_bound
doc_type: index
title: L05 个股做T · 子模块深挖总勾表与穷尽性声明（六矿 43 条新缺口）
created: "2026-09-26"
sid: st-qmine-20260925
lane: L05 个股做T（深挖车道，只读挖掘+写文档，零 git 操作）
family_id: L05-T0-MINE-INDEX
inputs:
  - docs/_working/decision_map_campaign_20260924/links/L05_t0/SKEL.md（环节骨架，本表只挖其缺口面，不改其判定）
  - docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md §2/§5/§6（六向/四闸/自审闸）
---

> 与 SKEL 的关系：SKEL §6 已判 47/48 子块 SEALED（挖的是**骨架完成度**）；本表挖的是**同一骨架之下的缺口面**（口径实现细节、数据质量画像、消费与注册正门）。两轴正交，本表**不改** SKEL 任何三态判定与判据阈值。

合计：6 矿 / **43 条新缺口**（其中各矿 §⑤ 自判"可施工小件"共 15 条——PA 4 / CR 3 / TK 1 / ET 3 / NW 1 / DS 3，全部为披露、登记、防呆、画像级，**零新判据、零阈值改动、零新规则卡**）。

**未过闸如实记录**：A 股 ETF 是否免印花税/过户费（关系到 31.2bp 对 ETF 的口径错配方向）——本环节**未取到权威源**，挂"待验证"，禁当既成事实使用（见 `etf_t0_cost_and_pool` L05-ET-G7）。
**已查无（含查法，见各件日志）**：分钟 bar 分桶对齐的公开标准实现、网格交易盈利的可信学术源、新闻 PIT 审计标准件、同类呈现惯例。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L07_exec/_INDEX_MINE.md`

**合计**：9/9 册落盘｜本组新立缺口 **58 条**（含 3 条对 SKEL/13 号文既有判定的**证伪或改判**）｜其中 **P0 共 14 条**｜**判"覆盖未接电"的子块：EXE-5、EXE-6、EXE-9 三块整块 + EXE-2/EXE-8 两块内 5 件**｜外部对表：2 册确证 + 1 册部分 + 6 册标受阻/未做。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L07_exec/s1_signal_to_order/MINE.md`

| 向 | 发现 |
|---|---|
| ①上游（谁喂它） | 内部：双输入面——日计划（MOD-PLAN-030 三场景 `plan["payload"]["scenarios"]`）+ 盘中五态（`fetch_realized_state`）。**五态→姿态是两级查表**：先 `STATE_TO_SCENARIO` 命中计划树内三态走 action→posture；未命中走 `STATE_EXTRA_POSTURE` 类推；两者都不中 → `pending_owner_mapping`（不是 none、不是 unexecutable，第四态）。SKEL §2 未记 `pending_owner_mapping` 这一**未收口悬挂态**——它落台账但 `_plan_decision` 无对应分支，任何新五态标签（如未来加"轮动"）都会静默停在 pending 且**无告警**。外部：待办（本轮未做，见 §⑥日志）。 |
| ②下游（谁吃它） | 内部：`_plan_decision` 出六值，`_plan_action_events` 只实现 4 值（entry/exit/trim_half/hold 语义内），**`wait` 与 `none` 在事件层无独立分支=与"什么都不做"不可区分**（wait 的"顺延"语义不落库、不产生次日重估边）→ 顺延是**无状态的**：明日若 ret_1d 仍 ≥1.5% 再顺延，永不追，也永无"放弃"终态。真实消费方仅 `plan-execute` 模拟腿与（载体重开后）`bridge-execute` 真单腿。外部：待办。 |
| ③算法/机制 | 内部：仓位规模 = `spend = cash*0.30`，`shares = spend/px*(1-BUY_COST)`，`cash2 = cash-spend`——成本从**股数侧**扣而非现金侧，等价但导致 `cost_paid` 字段与实际现金流出**不同源**（cost_paid=spend*BUY_COST 记账，现金侧全额扣 spend），长期复利口径下权益自洽（现金+市值=初始-成本），但单行审计会看到"成本被算了两次方向的错觉"；**无 sizing 层**：30% 是硬编码常数，不随波动率/回撤/置信度变化（plan confidence 已在台账 payload 里但不进 `_plan_decision` 签名）。外部：待办。 |
| ④后端 | 内部：全链纯函数 + fail-closed 落库（`_write_ledger` 写失败 raise `观察钱包落库未确认——fail-closed`，:493/:503）；无 class/无状态，可直接单测。可复用件已存在 = `zephyr.data.ch_writer.tsv_escape`（本件已复用，克隆防护在位）。外部：待办。 |
| ⑤前端（人工面） | 内部：`app_panel.py:141` 列有「交易计划与复盘：日计划与执行差异」入口，但 plan_bridge 姿态行与 plan-execute 成交行的**逐日对照视图未验**（MINING 债）；人工修改映射=改 `PLAN_ACTION_POSTURE` 一行（决策卡 :29 明示"改一行=改政策"），**无 UI/无审批流**，改文件即改政策，仅靠 git 留痕。外部：待办。 |
| ⑥数据字段 | 内部：所需字段=000300 两日收盘 + 510300 当日收盘 + 五态 state_label + 计划 scenarios[].action。**字段在 ≠ 数据可得**：`market_index_kline` 的 000300 行、`market_kline_etf_daily` 的 `510300%` 行、`judgment_intraday_market_state` 当日行三者任一断供即静默降级为 `none`，与"真该空仓"在台账里**同形**（都是 posture/动作无行）→ 归因不可分。行动建议=把"缺数致 none"与"姿态致 none"分码。外部：待办。 |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L07_exec/s2_order_pipeline/MINE.md`

---
ttl: task_bound
doc_type: log
title: L07-EXE2 子块挖矿簿 · 委托管线（OMS + 预检闸 + 价格笼子）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L07
status: MINE 完成（六向封口；外部对表标待办）；含 P0 级新证一条（C-GATE-01）
---

**④ 缺口清单**（本册新立；SKEL §4 L07-C01..C10 与 13 号文 TRD 项不重复）


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L07_exec/s3_qmt_bridge_client/MINE.md`

> 施工班读本件时以下述为准，**原锚未逐条改写处即视为已知假锚**：
>
| 引用处(叶文件:行) | 被引路径 | 原锚 | HEAD 行数 | 态 | 处置 |
|---|---|---|---|---|---|
> | `s3_qmt_bridge_client/MINE.md:45` | `bridge_monitor_check.ps1` | 72 | — | PHANTOM_FILE | NOT_IN_HEAD(未落地)——先落字节再引锚 |
> | `s3_qmt_bridge_client/MINE.md:45` | `bridge_monitor_check.ps1` | 1053-1067 | — | PHANTOM_FILE | NOT_IN_HEAD(未落地)——先落字节再引锚 |
> | `s3_qmt_bridge_client/MINE.md:28` | `trade_stats.json` | 4 | — | PHANTOM_FILE | NOT_IN_HEAD(未落地)——先落字节再引锚 |
> | `s3_qmt_bridge_client/MINE.md:28` | `trade_stats.json` | 0 | — | PHANTOM_FILE | NOT_IN_HEAD(未落地)——先落字节再引锚 |

**④ 缺口清单——"同类静默丢失/回报断链"的未覆盖路径增量**（与 A10 两缺陷不重叠；SKEL §4 与本册 §⑥ 的既有项不重复）

---
ttl: task_bound
doc_type: log
title: L07-EXE3 子块挖矿簿 · QMT 桥客户端（文件桥 + HTTP 快路径 + 桥执行腿）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L07
status: MINE 完成（六向封口）；本册使命=只挖"同类静默丢失/回报断链的未覆盖路径"，不触碰 LANE-BUILD 在修的两缺陷
---


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L07_exec/s4_execution_report_chain/MINE.md`

**④ 缺口清单**（本册新立；SKEL §4 的 L07-C04=接读者、T6b=撤单语义 不重复）


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L07_exec/s5_cost_feedback_loop/MINE.md`

---
ttl: task_bound
doc_type: log
title: L07-EXE5 子块挖矿簿 · 成本反馈 L4-14（三零件 + 回写断链）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L07
status: MINE 完成（六向封口）；新证=断链不止一条边，反馈环缺"数据平面"与"落库位点"
---

**④ 缺口清单**（本册新立；SKEL L07-C02 接线图纸、L07-C04 接读者、TRD-A08/LK-12 引用不重复）


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L07_exec/s7_slippage_calibration/MINE.md`

**④ 缺口清单**（本册新立；SKEL L07-C08「双真源收敛」、L07-C07/D36、CST-T0-001 挂起（B-007）引用不重复）


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L07_exec/s8_depth_and_imbalance/MINE.md`

> 施工班读本件时以下述为准，**原锚未逐条改写处即视为已知假锚**：
>
| 引用处(叶文件:行) | 被引路径 | 原锚 | HEAD 行数 | 态 | 处置 |
|---|---|---|---|---|---|
> | `s8_depth_and_imbalance/MINE.md:38` | `scripts/diag_tick_data_quality.py` | 行号断言 144 行 | — | LC_PHANTOM_FILE | NOT_IN_HEAD(未落地)——行数断言无宿主 |

**④ 缺口清单**（本册新立；D36/L07-C07 引用改判见 G1）


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L07_exec/s9_sell_and_daban/MINE.md`

| 编号 | 内容 | 级别 |
|---|---|---|
| **L07-S9-G1** | 打板 SaR 空盘口静默跳过 + 阈值量级近恒不触发 + 分笔无整手对齐（同一件三病，可一批修，含"文档承诺与实现路径背离"） | **P0**（接实弹前置） |
| **L07-S9-G2** | **打板节奏与撤单率合规闸无联动**：`cancel_timeout_sec` 类节奏参数不感知全局撤单率状态，合规冻结触发时算法侧无退让分支（"只挂不撤"降级应由算法侧显式遵守，而非在提交处被拒） | P1 |
| L07-S9-G3 | **卖出链现成字段未接**：XS-016 时段判定可用 `now_trading_phase()`/`is_sealed_limit_down()` 现成件派生，却仍是常数窗口表 + design 态；本条是"挂起"结论的反例——不是所有卖出侧工作都要等算法层。 | P1 |
| L07-S9-G4 | **H 安全级件零装配无休眠裁定**：`daban_execution` SAFETY=H、MATURITY=production、零消费、无 PROVENANCE（参数全默认值，对比 EXE-7 的 MODIFY-GUARD/PROVENANCE 纪律）→ maturity=production 与"无消费方"并存=口径失真（与 EXE-2 G4 双孤儿同类，本条是其中的 H 级实例，风险更高） | P1（登记类，Owner 知情） |
| L07-S9-G5 | **打板成本假设与 EXE-7 实测冲突未回写至可行性口径**：STR-DABAN-022 用 `slippage fixed 1bp + impact none`，而标定给 Q1_illiquid=7.24bp（**低估至 1/7.2**）→ 打板预期收益含 6.2bp 的系统性乐观；本册不重做成本模型，只要求打板可行性结论必须带该偏差标注（真源=EXE-7 S7-G1/G2）。 | **P0（口径标注，非施工）** |
| L07-S9-G6 | 四论文参数（Passive MI λ(d)=λ₀e^(−κd)、SaR、Hawkes 长记忆核、扩散悖论）均为件内自述 arXiv 编号，**引用可核性未做外部验证**，参数亦无标定；本册按"仓内论断"处理，不作外部依据引用。 | MINING 债 + 外部对表待办 |

**④ 缺口清单**（本册新立；SKEL L07-C09 核查型→本册已就地销号，L07-C07/打板域界归属引用不重复）


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L08_risk/_INDEX_MINE.md`

- L08-C03（MOD-RK-049 三选一）：`s3_tdm_drawdown_state_machine/MINE.md` ④ 末表给出甲/乙/丙三案的代码面·数据面·运维面代价与"与现役闭环的关系"，并标注本班立场（甲代价被高估、乙代价被低估、丙不满足终局量尺）。**本车道未拍、未施工。**
- L08-C18（重臂 vs 卡单不同源）三案在 `s2_.../MINE.md` ④：①探针取并集（与仲裁序 v1"保守者胜并集"同构，改 1 处 lambda）②rebuild 内追加 validator 置位（破坏其唯一真源）③判甲为 advisory 并收编入乙（w5_1）。
- 演练前置清单（HALT 首演，Owner high 门位）：C18 收口 → C19（evaluate 旁路）→ C20（影子补 `triggered_at`/`trading_date`）→ C21（损坏影子可辨+降级告警）→ 再谈首演；SKEL §7 步骤 6 现判定为**预期失败**，据 C18。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L09_review/s1_daily_loop_orchestrator/MINE.md`

**本册封矿判据**：六向封口；逐跳通电判定表已产出（总筹指定主交付）；L09-C01 裁定材料 A/B + 合并路径 + 不可逆点 + 双轨运维代价四件套齐；SKEL 一处结论已勘误。
未挖长尾：蓝图 238 行全文的降级矩阵 D1-D7 逐条对表现状（沿用 SKEL §三 未挖清单第 1 项，非本册阻塞）。⇒ **子模块封矿（附 L09-C01 待裁口）**。

| 轮 | 矿脉 | 判定 | 归因 |
|---|---|---|---|
| R1 | `schtasks //query //fo csv` 全量实测（GBK→UTF-8 转码，Zephyr 族 50 唯一任务）+ `//xml` 单件实读 | signal | **本轮最大发现**：DecisionChainSentinel 在册且指向真实脚本 ⇒ SKEL"未落地"结论作废 |
| R2 | `PHASE_STAGES` 实码逐条数列（full=16） | signal | 校正"16 段"口径并厘清 warroom 双列/full 去重语义 |
| R3 | `wire_data_scheduler` 全文逐钩子读（16 钩子实序 + 钩子序契约注释） | signal | 从"九棒"叙述升级为实测 16 钩子，并确认事件链宿主=scheduler.subscribe("task_completed") |
| R4 | `schedule.yaml` dloop_post 槽 + 全文件 `cron:` 计数=29 | signal | 与 SKEL 双验一致，未漂移 |
| R5 | `decision_chain_sentinel.py` 头注（含其自带 09-25 PG→CH 数据源勘误） | signal | 直接得到"哨兵为何必须走时间基"的一手自辩，用于 §9.3 豁免论证 |
| R6 | 逐跳通电表编制（H0-H8） | signal | 结论：7 接电 / 1 覆盖未接电 / 1 部分接电 |
| R7 | 外部对表 | 未做（本块留口） | 按轮次纪律：外部全网搜索延至全部落盘后统一一轮；已就位候选=data-driven DAG 调度范式（Airflow dataset triggers / Dagster assets）、SRE Workbook Ch.5 "alerting on symptoms + 监控监控本身"、Grafana AGPLv3。**登记为"未做外部对表"** |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L09_review/s2_premarket_chain/MINE.md`

| 编号 | 内容 | 状态 |
|---|---|---|
| TRD-A04 | ①双实现治理 ②晨间窗无人上班 | 在册；本册补：**"双实现"→"三实现"（增 MOD-PLAN-023）**，且 023 连消费面都不存在，比 021 更靠前一格 |
| TRD-A03 | NightlySentiment APScheduler 槽 + schtasks 双通道 | 在册，本册实测两腿均在（schedule.yaml:178 + schtasks 下次 09-25 22:30）+ 禁用标记 .bak 残留 |
| L09-C09 | MOD-PLAN-021 复用/退役随 L09-C01 裁定 | 在册；本册扩容为 **L09-C09′：三件（021/023/dloop premarket 相位）一次性收拢**，见 ⑤ |
| L09-S2-G1（新） | **production 标签空转**：021/023 挂 production 却零装配，`[CONSUMERS]` 写"运行时装配批"这类**未来时态**充当消费方登记 | 新增 |
| L09-S2-G2（新） | **晨间隔夜突变无重评**：分析时点与开盘时点差 9 小时（美股/期货/公告全在窗外），当前链上无任何件负责闭合这段 | 新增 |
| L09-S2-G3（新） | `data/runtime/nightly_sentiment.disabled.*.bak` 孤儿标记件（禁用标记改名存档而非删除，实查闸若按 `.disabled` 精确匹配则已失效，属"僵尸闸"候选） | 新增 |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L09_review/s3_judgment_ledger_settlement/MINE.md`

| 表 | 结算列回填（filled/rows） | 判读 |
|---|---|---|
| intraday_market_state | `outcome_ts` 20/20、`evaluated_at` 20/20、`eval_score` 20/20、`brier_contrib` 20/20 | **满回填**——真在自动结 |
| next_day_forecast | `evaluated_at` 4/4，但 `brier_score` **1/4**、`log_loss` **1/4**、`calibration_bucket` **1/4**、`eval_score` **1/4** | **仅 1/4 完成打分**，其余 3 行卡在 T+1 grace 未回 |
| daily_plan | `evaluated_at` 8/9、`eval_method` 8/9，但 `eval_score` **2/9**、`actual_scenario_id` **2/9** | **仅 2/9 真出分** |
| plan_verification | `plan_followed` 14/14、`deviations` 14/14、`verified_at` 14/14，但 `plan_quality_score` **6/14** | 质量分缺口 8/14 |

**本册封矿判据**：六向封口；D7 判语从"大半已闭"细化为"链通/账未满 + 三组可复核分母"；三条新缺口（G1 为 P0）。⇒ **子模块封矿**。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L09_review/s4_daily_publication_and_decision_snapshot/MINE.md`

| 编号 | 内容 | 状态 |
|---|---|---|
| L09-C02 / TRD-A17 全量 | 计划 vs 实际核对实体化（`daily_decision_orchestrator.py:754-767` 仅签名）→ 状态真值全史=0（四判据唯一维持 ✗ 的项） | 在册 |
| L09-C03 / TRD-A17 | 日刊双账合流 | 在册；**本册给出"差在哪"的 5 条实测冲突**（时间轴/日频口径/幂等模型/成熟度/消费面），合流工作项见 ⑤ |
| TRD-A19 | decision_daily 逐日审计报表消费端缺 | 在册 |
| L09-C04 落地后缺陷 | **哨兵 `max()` 尺无法发现逐日空洞**（本册实测：lag=0 而目标日 09-25 缺行） | 新增·P1（属 L09-C04 转正阻塞项，不重复立项，挂在 L09-S1-G3 下） |
| L09-S4-G1（新） | **账 B 零读侧 + 头注 experimental + `[CONSUMERS]` 写"接线另批"** ⇒ 三健康检产报 16 日而无人/无件消费（除 Alerter 的异常支路）；`degraded=0` 的"绿"完全无人知晓 | 新增 |
| L09-S4-G2（新） | 周末行虚增连续天数（09-19/09-20 实测有行）⇒ 任何"连绿 N 日"算法必须先过交易日日历 | 新增 |
| L09-S4-G3（新） | 账 A 历史密度：72 行中 66 行是 09-16 一次批量，**自然日频仅 6 行** ⇒ 快照"深史"实为 6 个目标日，四判据"深史全 🟡"应下调表述为"结构已通、深史 6 日" | 新增（口径纠偏） |
| L09-S4-G4（新） | 账 B 幂等替换未成立（09-24 双行） | 新增 |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L09_review/s5_warroom_operations/MINE.md`

### 触发面实测（三态判定）
| 触发面 | 实测 | 判定 |
|---|---|---|
| 事件链钩子 10 `maybe_run_warroom_pipeline`（`pipeline_events.py:923-957`） | 调 `run_daily_warroom_pipeline(day, phase="both")`；幂等键 `warroom_pipeline:<D>`，记号先落再动手 | **已接电**（SKEL"仓库内零调用方"旧结论已作废，本册实测有调用方） |
| dloop `warroom` 段（`PHASE_STAGES` premarket 与 postmarket 各一次；full 去重后单次） | 在 `dloop_post` 16:45 圈内 | **已接电** |
| 独立 schtasks 任务 | 本册 `schtasks //query` 实测 50 项 Zephyr 族中**无任何 warroom 专责任务** | **无第三通道**（=事实陈述，非缺口：两委托已覆盖） |
| 三任务之"盘中实时走势分析"（addendum 任务 1） | 事件链 60min bar 唤醒（钩子 5/8） | **部分接电**，见下 |

| 编号 | 内容 | 状态 |
|---|---|---|
| TRD-A05 / L09-C08 | 三任务之盘中实时走势触发面 + addendum 对齐 | 在册，**本册改写其靶心**：不是"缺证据列"而是"证据在 payload 未升列 + 节拍是 60min 而需求写分钟级" |
| L09-S5-G1（新） | **`next_day_forecast` 产出停摆 5 个交易日**（末次 09-20，全史 4 行）而钩子 9 在链上 ⇒ 属"接电而无声失灵"，比"未接电"更难发现 | 新增·P1 |
| L09-S5-G2（新） | **plan↔outcome 配平缺口**：6 plan vs 4 outcome，09-16 已到期无回写 ⇒ `writeback_scenario_outcome` 对该日静默失败或从未触发 | 新增 |
| L09-S5-G3（新） | **跨引擎割据**：判定行 CH、情景样本 sqlite，无共同日期主轴 ⇒ W0 校准闭环无法用一条 SQL 表达 | 新增（与 S4 册时间轴冲突同源，可合并处置） |
| L09-S5-G4（新） | **次交易日 fail-open 静默**：日历缺行 ⇒ `skipped:no_next_trading_day` 不告警；与 `schedule.yaml:219-227` R-021"有名无实假通道"同型 | 新增 |
| L09-S5-G5（新） | `plan_revision` 断供 5 周（17 行全在 08-21）无人追责 ⇒ 说明"表里有历史行"会掩盖"当前零产出"，任何盘点须按 max 日期而非总行数 | 新增（口径级） |
| L09-C01 关联 | `boundary_revision_engine` 已产过真行 ⇒ T3 收拢工时应按"复活+接节拍"估，不按"新建"估 | 供裁定材料（S1 册⑤） |


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L09_review/s6_monitoring_automation/MINE.md`

⇒ **0/4 有消费代码、0/4 有演练**。登记册自身 `:21-22` 头注已诚实写明"消费面=交易运行时监控（G2b/G5 sim 部署接线点），**status=design 代码未落**"——即**这不是登记册说谎，是消费方一直没人建**；且四条的 `consumer` 字段四条一模一样指向同一个未落地的"trading 运行时监控"，属**一个未建件被四度引用**（L09-C05 的正确靶心=建这一个件，不是建四个）。
另注：阈值真源分裂——登记册 `value` 存的是告警阈值，动作真源在 `trading_kill_switch`（其五级定义），而 `param_origin` 注明限额绝对值=G7 Owner 签字定案项 ⇒ 三处需一致，目前无自动对拍。

**本册封矿判据**：六向封口；现存清单以状态级实测取代记忆；四象限"产报/消费"清单成表；TRD-A06 验收线给出 0/4 + 0/4 的硬数；§9.3 偏差两条如实登记且未施工。⇒ **子模块封矿**。


---

## 来源（第二遍）：`docs/_working/decision_map_campaign_20260924/links/L09_review/s7_attribution_engine_and_performance_reports/MINE.md`

⇒ "归因产出 → 退役评审 → 调权 → 校准 → 可靠度回灌 L1"这条**自我进化闭环，五根接头一个都没焊**（09 号文"未接线"结论维持，本册给逐节点证据）。

### 2.4 触发面与新鲜度小结
| 对象 | 触发面 | 判定 |
|---|---|---|
| MOD-PF-007 | 被风险域 import（降级检测/因子暴露） ⇒ **无自身节拍**，被动函数 | **已接电（仅限风险消费）** |
| RPT-036/037 | 无任何排班、无事件钩子 | **缺失（零产零消）** |
| MOD-PLAN-009 | dloop `attribution` 段 + `last_audit.json` 实测 `attribution_daily=2026-09-25T00:43:11` 记号 | **已接电**（FIFO 末位，账本→日刊→归因次序） |
| sim_attribution_daily | 同上 FIFO | **已接电**（但 9 日中有 2 日缺） |
| MOD-PLAN-016 | 无 | **缺失** |
| D34 执行成本反馈腿（TRD-A08） | 无 | **缺失·前置阻塞** |

| 编号 | 内容 | 状态 |
|---|---|---|
| LK-15 | 归因三欠账（交易/持仓盈亏二分 + 策略级 P&L Explain + 逐笔 TCA） | **在册·本册证伪其"已销口"声明**（见 2.3★），输入面 L4-14/S37 仍在途 |
| TRD-A08 / D34 | 执行成本反馈断链 | 在册（C3-01 承接的先决输入） |
| L09-C07 | C3 消费闭环接线（C3-01→02→03 盘后事件链） | 在册，本册给逐节点断点表 |
| L09-C06 | 结算聚合报告件（S3 册） | 在册，与本块共用"逐层归因数据源" |
| D50（TDM 注） | 见 LK-15（同一事） | 需回改 TDM 注记为"部分承接/未承接"，走注册表流程 |
| L09-S7-G1（本册主项） | **归因装配链从未跑通**：`attribution_results` 0 行，PF-007(production) → RPT-036(testing) → RPT-037(testing) 三段中间无调用者 ⇒ 一切"归因报告/退役依据"当前无数据源 | 新增·P1 |
| L09-S7-G2（新） | 归因三处落点、无统一期次主键 ⇒ "同一天三个归因答案"可长期并存不被发现 | 新增·P2 |
| L09-S7-G3（新） | MOD-PLAN-009 的输入分母=4 条 outcome（S5 册实测）⇒ 三维归因表当前是**统计噪声**而非结论，但报告形态（dloop 段返回 str 截断 300 字）看不出这一点 | 新增·P1（误导风险高于零数据） |
| L09-S7-G4（新） | `[MATURITY] production`（PF-007）与"无报表消费"并存 ⇒ 成熟度标签测的是算法完备度、不是链路完成度，二者需在词表上分离（与 S2 册 G1 同题，本册供第二例） | 新增 |
| L09-S7-G5（新） | 周/月复盘编排（55 号规划）未建；`sim_deviation_report.py` 月度件与 55 号关系未澄清 | 沿用 SKEL §三未挖清单第 4 项，**本册标为未挖** |

**本册封矿判据**：六向封口；归因链断点从"未接线"下钻到"0 行数据 + 五节点逐个无挂点 + 一条虚假销口声明"三层实证；封矿范围严格限定为算法选型层。⇒ **子模块封矿**。


---

## 来源（第二遍）：`docs/_working/emotion_line/redblue_round_record.md`

| # | 发现 | 处置 |
|---|------|------|
| F6 | 骨架稿 auction stage"原料未聚合"错判 | 改"v0.2 可挂载（原料齐备）"，doc_version 升 v0.2 |
| F7 | research_report 漏盘 | 盘点册 §8 入册（半通，评级情绪候选） |
| F8 | 同域簇查重风险未识别（三情绪枚举+同名温度函数+F23 同源信号） | 骨架稿 §8.3 内收判定框架+缺口 G10/S8 前置 S3 |


---

## 来源（第二遍）：`docs/_working/fullflow_mine/verify/AUDIT_B_wire.md`

24 项中：**已落地 1（挂载草案§三六张 TDM mounts，e405020493a）+ 半接线 1（3-8 前半 llm_premarket 已接、style_regime_model 未接）**；其余 22 项零消费端变化=仍需接线/仍锁。10-02~10-04 多队施工（拆簇/裁定#480 手术/挂图九张/GOMAP）与本项目零交集，无并道冲突；他 aidrafts（st-chief-mount/st-tdm-mount-flash/st-tclose-fwire）与主区 TDM/wiring 逐字节一致=无在途未落地接线。


---

## 来源（第二遍）：`docs/_working/fullflow_mining/02_tdm_decision/19_f52_validation_dal.md`

## 三、六向台账
- **上游输入**：trading_decision_map.yaml（节点清单解析导出）、data/backtest_artifacts/bt-*.json trade_log、两注册表 yaml。
- **下游消费**：c1_backtest.node_verdict 台账→前端 /api/tdm/validation + /api/tdm/verdicts（TD 页验证档案区）；P2-1 衰减巡检（decay_watch）。
- **自动化触发**：**手动**（runner 无调度；decay_watch 尾随验证批运行，调度挂载=登记遗留 Owner 二选一，grep m5+register_*.ps1 零命中=仍未挂）。
- **真源与注册表**：docs/01_policies_and_standards/_registry/catalogs/{validation_method_registry,decision_algo_registry,backtest_backlog}.yaml；runner=zephyr/trading/validation/runner.py（645 行，MOD-TDMVAL-001 production，TESTS=tests/trading/test_validation_runner.py）。
- **门禁与质量尺**：INVARIANTS=holdout 12 月/触发<30 pending/台账只追加不删改/空数据不造假/verdict_reason 代码生成禁手填（R2）。
- **当前运行状态**：**绿（机制）×黄（结论）**——台账实弹 60 行（42 旧 L4 + 18 新 XFLOW，run_id=VAL-20260909-164042），**全部 verdict=pending+insufficient_samples**（成交流水全落 holdout 保密窗 2026-02~08>2025-09 截止线；"宁可 pending 不作弊"晨报裁定 3）；decay checked=60/decayed=0。

### 2.2 决策算法库（REG-DAL-001）
- **实测 32 条**（15 production/5 trial/12 design，2026-09-25 grep）——**总册口径"27 条"已漂移，本册为准并回填**。
- trial 五条=DAL-CHIP-DISTRIB/DAL-FWD-STOP/DAL-RISK-BUDGET/DAL-SECTOR-DIST/DAL-TAIL-HEDGE（UP 系尾随接线，回测验证前休眠语义）。
- B 半相关：DAL-CIRCUIT-5（production，drawdown_state_machine）/DAL-T0-CLOSE（production，t0_trading_pipeline）/DAL-BUDGET-BAND（**design，code_ref=null=缺口**）/DAL-GRADIENT-TRIM（design）/DAL-FWD-STOP（S1-02 建议通道，trial）。

## 五、验证欠账总清单（B 半口径，按生死线排序）
1. **BT-P0-003 成本三件套（P0 生死线第三件，横切我半三节点）**：E-L4-09 **过**（滑点 2.56bp+成本项 1467/1467 逐笔零偏差）；X-S2-01 **过**（858 笔 2.65bp≤20）；P2-01/P2-03 **存疑**（做T配对 24<30 insufficient_samples；披露：0/24 配对毛价差≥30bp 开仓前置下净价差 mean −45.0bp——做T经济性存疑）→ Flash F02 重考扩样本。
2. **X 流 18 节点全部 pending**（含 S1-01..06/S2-02..06/R1 组）：exit_counterfactual 真结论待窗口前移（2026-09-09 后新流水积累）重跑。
3. **消融器实弹**：待 Owner 放行 §12；放行后 run_ablation→rescured 序列喂 batch="XFLOW"。
4. **消融动作标注自动化**：SellSignal 流未接入回测（包外零消费者，见 12 册）——xflow_actions 现为调用方注入 v1。
5. **decay 对 exit 方法比对口径**：X 节点出 valid 后 hit_ratio（避损额语义）衰减判据待随消融器锁定。
6. **P/F 流验证零启动**：agg_discrimination（P2/P3 判定）与 portfolio_attribution（C1-C3 残差<1bp）两方法尚无一行实弹。
7. **BTB 132/142 对象 plan=null**：阈值未预注册，批次决策点填写并冻结前禁跑。


---

## 来源（第二遍）：`docs/_working/fullflow_mining/02_tdm_decision/index.md`

| 文件/目录 | 类型 | 说明 |
|-----------|------|------|
| [00_overview_a_front.md](00_overview_a_front.md) | Markdown | TD-A 前半总览——TDM 消费端 F37-F42 六环节（entry L0-L4 + position P1） |
| [10_f43_p2_t_trade_rebalance.md](10_f43_p2_t_trade_rebalance.md) | Markdown | F43 P2 做T与加减仓——TDM 持仓流 P2 环节册（TD-B 后半） |
| [11_f44_p3_pyramiding.md](11_f44_p3_pyramiding.md) | Markdown | F44 P3 加仓决策——TDM 持仓流 P3 环节册（TD-B 后半） |
| [12_f45_s1_sell_signal.md](12_f45_s1_sell_signal.md) | Markdown | F45 S1 卖出信号收集评分——TDM 离场流 S1 环节册（TD-B 后半） |
| [13_f46_s2_exit_execution.md](13_f46_s2_exit_execution.md) | Markdown | F46 S2 离场执行——TDM 离场流 S2 环节册（TD-B 后半） |
| [14_f47_r1_emergency_lifeline.md](14_f47_r1_emergency_lifeline.md) | Markdown | F47 R1 应急保命——TDM 风控横切环节册（TD-B 后半） |
| [15_f48_c1_capital_budget.md](15_f48_c1_capital_budget.md) | Markdown | F48 C1 预算切分——TDM 组合流 C1 环节册（TD-B 后半） |
| [16_f49_c2_portfolio_aggregation.md](16_f49_c2_portfolio_aggregation.md) | Markdown | F49 C2 组合聚合——TDM 组合流 C2 环节册（TD-B 后半） |
| [17_f50_c3_attribution_feedback.md](17_f50_c3_attribution_feedback.md) | Markdown | F50 C3 绩效归因反馈——TDM 组合流 C3 环节册（TD-B 后半） |
| [18_f51_crypto_skeleton.md](18_f51_crypto_skeleton.md) | Markdown | F51 币圈决策骨架——TDM-C-L1..L4 第二实例环节册（TD-B 后半） |
| [19_f52_validation_dal.md](19_f52_validation_dal.md) | Markdown | F52 验证方法学与决策算法库——REG-VALM-001+REG-DAL-001 环节册（TD-B 后半） |
| [f37_l0_premarket_plan.md](f37_l0_premarket_plan.md) | Markdown | F37 L0 盘前作战计划——环节册（TD-A 前半） |
| [f38_l1_market_gate.md](f38_l1_market_gate.md) | Markdown | F38 L1 大盘总闸+六传感器——环节册（TD-A 前半） |
| [f39_l2_sector_selection.md](f39_l2_sector_selection.md) | Markdown | F39 L2 板块选择——环节册（TD-A 前半） |
| [f40_l3_stock_selection.md](f40_l3_stock_selection.md) | Markdown | F40 L3 个股选择——环节册（TD-A 前半） |
| [f41_l4_execution.md](f41_l4_execution.md) | Markdown | F41 L4 买卖点与执行——环节册（TD-A 前半） |
| [f42_p1_position_checkup.md](f42_p1_position_checkup.md) | Markdown | F42 P1 持仓体检——环节册（TD-A 前半） |
| [pending_rulings.md](pending_rulings.md) | Markdown | TD-B 后半待裁登记（一行一案：问题/已试路径/选项/建议） |


---

## 来源（第二遍）：`docs/_working/fullflow_mining/04_knowledge_supply/00_实件化路径总述.md`

| 环节 | 节点 | TDM 登记 | 本组实测改判 | 册 |
|------|------|---------|-------------|-----|
| F30 | A01-A16 | 16× module_ref=null, red=structural | **绿**（16 线 provider+CH 双源在产，null=引用式设计） | f30_源线行情基本面.md |
| F31 | B01-B10, C01-C03 | 13× module_ref=null, red=not_built | **红=如实**（渠道未接；通用引擎底座 28 模块已在库可指派；C 档 3 线无渠道挂起正确） | f31_源线另类.md |
| F32 | G1-G5 | G3 有码，余 null | **G1/G2/G4 半绿**（ig_chain 873、CKG 已导入、stock_concept 61,053 行——03 号件"行数无实查"缺口已补）；G5 红如实（挂零复测=0）；G3 绿（804 边+穿透函数） | f32_图谱谱系.md |
| F33 | V1-V3 | V1/V3 有码，V2 null | V1/V3 **黄**（judgment 台账通道在但产量 20/4/9 行）；V3 板块侧 sector_state 表 426,256 行 max 09-23 **实为绿**（TDM 只说"骨架v0"已保守）；V2 红=定案挂起 | f33_状态变量快照.md |
| F34 | AGG | null, red=structural | **红=如实**，但最小实件化路径已探明（读数件散装在岗，缺聚合器） | f34_知识汇聚.md |
| F35 | D1/D2/E1/E2 | D2/E2 null | D1/E1 绿（MCTS 出候选 09-23、runner 645 行）；**D2/E2 改判绿**（码在+数在，TDM 登记 stale）；剩余断点=D1→D2 每日假设入表接线、两套考尺统一 | f35_一问一考.md |
| F36 | Z1/Z2 | Z1 null, Z2 有码 | **Z1 改判绿**（状态机 10 方法在 exam_ops.py，1,177 审计事件）；Z2 绿（reconcile 首跑 8 引用/0 断链/575 未吸收在案） | f36_治理横切.md |

1. **TDM-E-L9-D2** module_ref null → 应填 `src/zephyr/governance/meta_question/registry.py`（MOD-CHAINPILE-METAQ）；节点备注"registry 代码随 B7v2 尾批落地（worktree 在飞，本班不代落）"——已落地在 HEAD。
2. **TDM-E-L9-E2** module_ref null（red=pending_gate）→ 应填 `src/zephyr/governance/meta_question/exam_loop/writeback.py`（回填唯一合法入口）+ `reexam_scheduler.py`；337 条 exam_result 在表实证回传已在跑。
3. **TDM-E-L9-Z1** module_ref null → 应填 `src/zephyr/governance/meta_question/exam_ops.py`（状态机 10 方法 NO-GOD-CLASS 拆分件）。
4. **总册 F92"entry_count=0 空转"** → 过时：PG 实测 283 问在表（本组 2026-09-25 查证），应翻绿。
5. **总册 F31"15 源线"** → 口径漂移：TDM 实登记 B10+C3=**13** 条（TDM edges 29 条喂 AGG=16+10+3，与 AGG 节点"29 源线"自洽）；总册 31=16+15 与 TDM 29 不一致，建议统一为 29。
6. **总册 F32/F33 partial 判定偏保守**：G4 行数缺口（stock_concept=61,053 行实测）与 V3 板块在产证据（426,256 行）可回填翻绿。


---

## 来源（第二遍）：`docs/_working/fullflow_mining/m1_data/index.md`

| 文件/目录 | 类型 | 说明 |
|-----------|------|------|
| [01_ingest.md](01_ingest.md) | Markdown | 01_ingest.md |
| [02_cleaning.md](02_cleaning.md) | Markdown | 02_cleaning.md |
| [03_ch_warehouse.md](03_ch_warehouse.md) | Markdown | 03_ch_warehouse.md |
| [04_cold_storage.md](04_cold_storage.md) | Markdown | 04_cold_storage.md |
| [05_tdm_crossaxis.md](05_tdm_crossaxis.md) | Markdown | 05_tdm_crossaxis.md |
| [06_registers_manifest.yaml](06_registers_manifest.yaml) | YAML | |
| [90_backfill_wave.md](90_backfill_wave.md) | Markdown | M1 数据链 补挖波 · 清洗三引擎零接线 + 影子表退役/CH三数互斥 |
| [c351_migration_plan.md](c351_migration_plan.md) | Markdown | c351_migration_plan.md |
| [pending_rulings.md](pending_rulings.md) | Markdown | pending_rulings.md |
| [补挖波_20260925/](补挖波_20260925/index.md) | 目录 | 补挖波_20260925 |


---

## 来源（第二遍）：`docs/_working/fullflow_mining/m7_live_execution/backfill_wave2/wiring_A_cage.md`

**完工**（今夜最小面全部达标）。残余＝三件待登项（旗标出厂值／两腿装配一行／enforce 前置的相位判别器），其中第三件是 enforce 的启用前置而非本案交付缺口，**不影响本案 BF-6 今夜判据达标**。


---

## 来源（第二遍）：`docs/_working/map_build/03_final_blueprint_and_schema.md`

| 图 | 终局形态 | 节点规模 | 必备 L1 字段 | 专属层 | 终局验收判据 | 还差的活 |
|---|---|---|---|---|---|---|
| **图11 交付流水线** | 三车道 DAG（会话/提交/死信） | 28 | `wiring_status`、`exit_codes`、`runtime_refs` | 退出码全谱矩阵 | ①28 格全挂 `module_id` ②死分支码 4 与回滚旗失效两条以 gap 节点显性化 ③gate 子检查在 MAP-ALIGNMENT 内可红可绿 | CV-BUS 补挂；S07「pre-merge 门整体短路」加注 |
| **图12 数据供给链** | 五段链 + 终点缺口显性化 | **21**（现 18→扩 3，待扩） | `slot_source`、`data_refs`、`freshness_evidence`、`downstream_action` | 任务归簇表 | ①骨架扩行后图本体再生 ②`terminal_gap` 必须真指向 gap 节点（现满足）③5 处"消费方在等未产表"+1 处幽灵引用全部成 `gap_refs` | **未封矿**：消费端反查已跑但增量非 0，需扩行+重宣封顶 |
| **图13 交易日循环** | 一日四段时序脊 | 44 | `slot_source`、`cadence_zh`、`ready_gate`、`invalidation`、`tdm_refs` | dloop 16 段 + machine_facts | ①2 空转槽与 16 落空对象全在 `wiring_status` 里可查 ②无一条 `judgment_basis`（越域即红）③D13-09 就绪门升为一等节点 | `tdm_refs` 填充 <1/3 须补；外部对标表A 7 条逐条落字段 |
| **图14 AI施工升级流** | 15→**17** Step 段闭环（含回边） | ≥17 | `verifiability`、`anchor_kind`、`fallback` | 步骤锚登记面 | ①步骤锚校验器上线且能红 ②9 条"文档说有实则没有"以 gap 节点入图 ③政策内嵌机读锚块为真源、图为其派生 | **未施工**：前置校验器先立；39 件幽灵脚本引用面待清 |
| **图15 策略卡生命周期** | **状态机**（状态+迁移+禁止边三类节点/边） | 状态 N + 迁移 M + 禁止边 K | `edge_kind: forbidden` 必可枚举 | 卡状态登记面 | ①登记面唯一宿主选定（扩 `experiment_registry` 优先，禁第二真源）②六处分裂的差值可被校验器判红 ③SEALED 就地复活＝必红 | **未施工**：规格两处判据缺陷（CV-08 误伤 36 张、CV-06 抓不到唯一复活链）先回炉 |
| **图16 治理立法流** | **不建图**（本役终态即合格态） | — | — | — | 三项微创落地即闭环：①取号器（防今晚 6 起同类撞号）②词表/entry_schema 回写 ③ROOR 补 1 条 | 重开触发条件已登记在册（出现流程位置字段即重议） |

| 字段 | 值域 | 用途 |
|---|---|---|
| `slot_source` | `schedule`/`schtasks`/`event`/`dloop_stage`/`manual`/`none` | 时点从哪来；声称 schedule/schtasks 者须在真源查到（在册实存校验） |
| `slot_refs`/`schtasks_refs` | 列表 | 具体槽名/任务名 |
| `cadence_zh` | 文本 | 声明节拍 vs 实测节拍（图13 用 `declared`/`observed` 双子键） |
| `wiring_status` | `wired`/`unwired_slot_hollow`/`unwired_no_caller`/`partial` | **"槽挂着但没跑"的表达位**——三图统一走这一个字段 |
| `downstream_action` | `auto_remediate`/`alert_only`/`detect_only`/`none` | 区分"谁看着"与"谁动手"；配 `failure_visibility_zh` 说检出后痕迹去哪 |
| `fallback` | 文本/null | 降级路径（统一用这名；废止 `miss_fallback_zh`/`degradation`/`silent_failover` 三名） |
| `invalidation` | 文本/null | 什么条件下本节点结论作废 |
| `ready_gate` | bool + `no_ready_gate_reason_zh` | 就绪门是否成节点（图13 D13-09 建议升格） |
| `tdm_refs` | 列表 | 与 TDM 的交叉引用；**本层禁出现 `judgment_basis`/`factor_refs`/`strategy_refs`**（决策判据归 TDM，违者判红＝越域挂载） |
| `gap_refs`/`red_reason` | 列表/枚举 | 缺口显性化；`terminal`/`unwired`/`broken_supply`/`ghost_ref` |


---

## 来源（第二遍）：`docs/_working/map_build/20_join_checker_design.md`

| case | 裁定 |
|---|---|
| __init__.py 空壳 | 并入父包，不单独计 |
| 一文件多图 | 合法，maps_direct 列全 |
| 键悬空（MOD-* 查无文件） | 报 dangling_keys 段，禁静默 |
| tests 文件 import 主账文件 | 不影响主账归属（辅账不回流） |
| scripts 无 MOD 键 | scripts 记账走 script-manifest+图 scripts 字段直接 join |
| 生成器自身 | 计入 GOMAP 挂载（治理域） |


---

## 来源（第二遍）：`docs/_working/map_build/fig12_datachain/11_消费端需求反查.md`

**干**：四类消费者口径先定后扫，分母 174 点/40 表全实测（命令在 §0 注，`.runtime/tmp/cons12/{scan_consumers.py,stage2_ch.py}` 可复跑）；四态逐表带 file:line/读数；三候选各给三问料与盘侧实证；🌑 三条逐条按"接口/权限/挂载"判据复验（2 撤 1 收缩）；与五簿/90 账零单方面改判（consensus 停 10 日、D12-15 未接线、WAL 双表均注"相合/加证"）。
**欠**：①TDM 13 个契约引用的物理落点只到"无法机械解析"一层，未逐条人工对表（若总包要全解约，需一张契约→表反查批）；②`capital.margin`/`macro.cn_macro` 疑有实体（CH 有 margin_trading、失败案卷有 macro_data_incremental）但**未做同义映射终验**，判"待核"不判幽灵；③`ig_fact`/DS-224 属 PG 面，本车道只读 CH，未以 DatabaseService 开 PG 口（避开口径污染），PG 侧存在性为空白腿；④代码消费扫了三目录，`pf_alloc/plan_engine/ex_core` 等目录的读点（本卷顺带实见多处）**未纳入分母**——扩口径会加深 C 态证据但分母重算，留待总包定口径后复扫。


---

## 来源（第二遍）：`docs/_working/map_build/fig13_daycycle/02_盘前元数据与竞价.md`

- **上**：**双正门触发（触发机制 A+B 同环节并存，§2.1 三分的活案例）**——①APScheduler 槽 `nightly_sentiment` `20 8 * * *`（schedule.yaml:178-181）→ scheduler.py:272-337 特殊槽分支（总闸 `data/runtime/nightly_sentiment.disabled` 每次触发实查；**实测该闸已于 09-21 被 st-data-fix 改名复活**：`data/runtime/` 现存 `nightly_sentiment.disabled.by-st-data-fix-20260921.bak`=当前启用态）；②Windows 计划任务 `ZephyrAlpha_NightlySentiment` daily 22:30 跑 `scripts/data/run_nightly_sentiment.py`（schtasks /xml 实测：StartBoundary 2026-09-15T22:30+08:00，DaysInterval 1；脚本头 [CONSUMERS] 自陈 schtasks 22:30，跑"昨日"窗）。两门共享同一幂等写入器（ReplacingMergeTree 同键替换，近 7 日缺口自愈补跑=schedule.yaml:173-177 注释）。
- **下**：输出表 `c1_market.news_sentiment_window`；实测消费面=情绪指数六成分之 C6 新闻腿（tasks.yaml emotion_index 系注"as-of T 重算 C5/C6"，L3469 前后）与 TDM premarket 决策节点（决策内容全走 tdm_ref，禁则一）；本图只记时点与就绪。
- **内（骨架标 2）**：当日窗计算 + 近 7 日缺口自愈；degraded 行占位不留洞（schedule.yaml:176）——实测今状=每日 1 行夜窗（window_type='night'，scope='market'，data_source='llm'）。
- **旁**：**窗口语义与段界交叠是本环节的图论难点**：窗口右端=T 日 08:00，结算时点=T 日 08:20 → 段归属"盘前"成立（骨架 §2 段 A 判定维持）；而 22:30 那腿触发时刻落在段 D 夜窗——**同一环节两腿跨两段**，图本体若给"段归属"单值字段将无法表达（施工期字段设计输入，报总包注意）。与图12 切分：新闻采集管线内部（event_driven/news_slow→news_data→LLM 打标）全归图12 衍生族；本图只管 08:20/22:30 两个时点与"窗闭合"语义。与 57 号 SOP：其六环节无此格（晚于归档出生 2026-09-10 接线），无吸收面。与簿01 哨兵族：news_sentiment_window 不入 calendar_coverage 名单的理由已注死（未注册 TableRegistry 品类，由 data_supply_sentinel 同表 4 腿中的日历日 lag3+floor3 覆盖，calendar_coverage_checker.py:110-112）。
- **史**：MOD-INT-NEWS-NIGHT 2026-09-10 接线，治 known_data_gaps `news_sentiment_window_no_scheduler_wiring`（写入器此前零调用方、表存量全靠 ad-hoc 回填，schedule.yaml:173-177）；09-15 又补 22:30 schtasks 门（92号 §8.4③）。
- **新（✅ 三证实测）**：时点=上引两门；执行体=`zephyr.intelligence.nightly_sentiment_window.run_nightly_sentiment_batch`（scheduler.py:292-294 惰性导入）；最近执行=CH 行 `window_date=2026-09-23, window_ts=09-23 18:00, window_end=09-24 08:00, total_count=967`——**窗口右端含今晨 08:00，只可能由今日 08:20 腿产出**（22:30 腿跑"昨日"产不出它）；09-17→09-23 逐日窗连续 1 行/日无洞（FINAL 按 window_date 聚合实测），全表 19,820 行。滞后 0。⚠️ 观察：近 7 日每日仅 1 行（market 级夜窗），无 symbol 级行——是否设计如此（scope 分层）待图12/情绪簿侧对表，不在本车道判。


---

## 来源（第二遍）：`docs/_working/map_build/fig13_daycycle/05_盘中资金流与决策层.md`

- **上**：唤醒词 `kline_etf_60min`（60min bar 落点 10:30/11:30/14:00/15:00 → 恰 4 拍），bar 落库腿来自 D13-15（intraday_minute 池）。
- **下**：`judgment_intraday_market_state`（L1 状态机观测行）→ D13-22 归类、D13-33 收盘验证、TDM L1 族节点。
- **内**：bar_key 查重幂等（`pipeline_events.py:1036-1040` 注释自证）；永不反噬（导入级 try/except 独立吞）。
- **旁**：**与 D13-22 同唤醒源、同钩子序**（两环节在图里必须两格：一个是"局面是什么"，一个是"归到哪一型"，且实测产出节拍已经不一致，见 §4）；与图12：判定表的水位/补拉不在本图；与 TDM：L1 判据本体在 TDM（`activation=intraday`），本图只给"每 60 分钟 bar 落库后一拍、一日四拍、缺拍=状态断链"。
- **史**：判定台账 Phase 2a 批（2026-09-16 st-ledgerp2a，`pipeline_events.py:1036` 注释在册）。
- **新**：本环节是全日**唯一双机制冗余**（dloop + 事件）仍稳定 4 拍/日的判定件——反证 D13-20 的缺陷不是"双挂"本身，而是"双挂 + 窗闸/取日口径不一致"。

⇒ **死结论**：09-22 起每个交易日**恰好一拍**，且 created_at 全落在 **16:45–16:50 CST = dloop 自动圈内**（`schedule.yaml:249` 的 16:45），**盘中零拍**。所谓"盘中情绪环"在时间轴上根本不在盘中：它读的是**收盘后的行情**（asof_ts 16:08/16:29 亦为盘后）。
- **内**：`run_once()` 单次快照；跨拍态 `previous_board` v1=None（`:276-278` 自陈 SEC-02 降级留痕由模块自守）⇒ 即便盘中给节拍，**板块对照的第二拍依赖跨拍态，而它恒为 None**，这是"节拍缺失"之外的第二层缺口（若只补节拍不补跨拍态，盘中拍仍是降级拍）。
- **下**：`prediction_log sentiment_score`（append-only 观测行）→ 情绪面消费方（TDM 情绪族/复盘页）。
- **旁**：与 D13-04 夜间情绪窗（08:20 槽、`news_sentiment_window` 表）**同域不同表不同机制**，图里两格，不可因都叫"情绪"而并；与 D13-17/18：原料是新闻，节拍与新闻入库时点无因果（情绪环读行情为主）；与图12：让渡；与 TDM：情绪打分判据走 `tdm_ref`；与骨架 §2.1 机制 C 的"14 个环节"计数：本格属"无独立时刻、全赖 16:45 圈"的典型。
- **史**：MOD-DATA-063，`[MATURITY]/[STABILITY]` 见模块头；depgraph 在册 import 依赖 4 条（`data_domain_audit_report_db.md:393,644-646,850`）。
- **新**：与 D13-20 形成干净对照——**同一族"段内环节"，双挂（事件+段）者活、单挂（仅段）者死节拍**。图本体 `callers[]` 一个字段即可预测：`len(callers)==1 and caller==dloop ⇒ 盘中必零拍`。


---

## 来源（第二遍）：`docs/_working/map_build/fig13_daycycle/07_dloop十六段解剖.md`

**结论（诚实版，给骨架第 3 节的实测补充）**：
1. 切分线**在时序侧完全成立**——段序、幂等判据、唯二 fail-closed 点、窗闸、唤醒词伪造口径，TDM 一条都表达不了（`activation` 只有 5 值窗标签，182 节点里 `MOD-PLAN-*` 仅 9 个）。
2. 切分线**在决策侧只兑现了 3/16**（warroom / decision / pf_alloc）。若图13 施工即执行禁则一"判据唯一出路 `tdm_ref`"，则 **D13-32 的 8 段（daily_plan/next_day/intraday_l1/classify/llm_premarket/close_verify/sentiment_loop/auction_hit）会写出悬空 tdm_ref**。
3. **该让渡给 TDM 扩节点的段名（按决策含量从高到低）**：`daily_plan`（MOD-PLAN-030）、`next_day`（MOD-PLAN-029）、`intraday_l1`（MOD-PLAN-028）、`classify`（MOD-PLAN-031）、`close_verify`（MOD-PLAN-032，可挂 TDM-E-L0-03 下作子节点）、`auction_hit`（MOD-PLAN-015）、`llm_premarket`（MOD-PLAN-007，注解档）、`sentiment_loop`（MOD-DATA-063）。
4. **应留在图13 的段**：`data_readiness`、`regime_freshness`、`pf_alloc`（时点与记号部分）、`settle`、`similar_day`、`attribution`、`decision`（时点与 force 逃生口部分）、`warroom`（时点部分）。
5. 施工期落地建议（不改骨架，登记为总包请求）：`tdm_ref` 在图13 本体做成**可空 + 空值语义"决策侧待 TDM 扩位"**，别在建成日就把 8 段判成红节点——那会把 TDM 的排期债转嫁成图13 的假缺口。


---

## 来源（第二遍）：`docs/_working/night_sweep/b_audit/nb1_b6_indicator_retirement_groups.md`

**六向快照**：通道=technical_indicator_registry.yaml:4619-4800（v1.1.0，2026-09-21 批10 新建）；原料=c1_market.kline_daily（high/low/close/volume/turnover_rate；volume 手→股量纲已治本，裁定#398/#399）；状态=**已量化+已验收**（chips.py 493 行 MOD-L02-031，CYQ 独立实现复算 000852 近 20 日 0 偏差对表；142 在产指标机读对齐 REG-IND-001）；消费方=**零下游**（used_by_factors 空，decisions_map_campaign 14_consumption_census.md:57 "批 10 新产…零下游（未入机账）"）；缺口=消费未接；处方=下。
**三审**：①价值——获利盘（chips_winner）/单峰密集度是 TDM-E-L3-12-3 筹码分布分析节点（trading_decision_map.yaml:2089-2114）**明文挂起的核心语义**（"获利盘占比/单峰密集度 语义未实现挂起（需流通股本数据工程）"，裁定#257④=D21）；而 CYQ 的 chips_winner 基于**换手率衰减迭代分布**，**不依赖流通股本**即可先行出数——即 D21 最重的数据工程未落地前，CHIPS 族已能把"获利盘"半语义先通。②真源唯一——chips.py 是全仓唯一筹码实现；TDM 消费端 chip_distribution_engine（MOD-REGIME-005，464 行）输出 4 指标（long_term_bottom_ratio 等）**不含 winner**，两者是"同节点不同剖面"互补非重复（chip_conc_90 与 SCR 同公式双条目 overlap 已在册登记，消费端择一）。③数据持续性——日 K 活源，持续供数成立。
**三态裁定：保留+接线（转绿路径=D21）**。处方：①P1 接线=chip_distribution_engine 增补 winner 剖面时直接调 factor/technical_indicators/chips.py::CYQ（禁第二套分布实现），TDM-E-L3-12-3 算法注补"获利盘占比由 CHIPS-001 供给"；②trial 期信号不进决策（沿用#257④ 回 trial 纪律），先回测出 IC 证据回填 evidence 字段；③D21 流通股本到位后升级"单峰密集度"全语义；④CHIP_CONC_90/SCR 双条目在消费端二选一并登记选择。


---

## 来源（第二遍）：`docs/_working/night_sweep/c_exam/state_matrix_fill_plan_v1.md`

```
[1] r态→六段折算（真源=framework_composer.py REGIME_STATE_TO_ACTIVATION_PHASE）：
    r1→None r2→None r3→expansion r4→accumulation r10→capitulation r11→accumulation r12→ignition None→None
    ⇒ euphoria/distribution 零 r 态来源=不可达（宁漏勿误 fail-closed，机证）
[2] fw-tdm-current（PP-001 衍生）activation_state 实测：
    声明含 euphoria 的成员=['daban-sleeve']；distribution=[]；activation=null（全段）成员=7
    ⇒ distribution 无任何在册成员声明激活；euphoria 仅打板 sleeve（L4 口径）
[3] TDM 两格实测：mounted=() 且 mounted_reason 首词=pending-owner-adoption（R41 合法在册）
[4] 条件共振判定 dry-run：R1 相位可折算 ∧ R2 两格未填格（pending-owner-adoption=残缺不路由）
    ⇒ euphoria/distribution 恒"保持现状"（机械面可运行且行为正确=上岗规则 v1 §2.1 R2 判据）
```

对 TDM-E-L1 的 euphoria/distribution 两格 `mounted_reason` 追加标记段（首词 pending-owner-adoption 保持，
R41 词表合法；零 schema 变更、零格填充、零删除）：


---

## 来源（第二遍）：`docs/_working/night_sweep/ledgers_archive/00_orchestration.md`

- 全流通骨架已存在且经红队打假：**132 环节**（docs/_working/fullflow_mining/00_skeleton/）+ TDM 182 节点（config/trading_decision_map.yaml）+ 四层未接线清单（docs/_working/wiring_gap_inventory_20260927.md，59 零引用表/13 无环节域/41 未接线环节/38 TDM null）+ F123-F132 补挖案卷。
- **裁定：不重挖 120 册（违内收），做"补干挖矿"**：由字节/骨架车道产出 `docs/_working/night_sweep/00_skeleton_nightsweep.md` = 环节总表（环节×状态轴[已通/开口/等Owner]×开口项映射审计卡号），对开口环节逐个补挖矿卡（六向台账快照+自审闸三态+处方）。谁挖干谁先开工，不必等总筹点头。
- 新建施工文档一律落 `docs/_working/night_sweep/`（CREATE-GUARD token 先行独立批）。


---

## 来源（第二遍）：`docs/_working/night_sweep_20260929/00_orchestration.md`

- 全流通骨架已存在且经红队打假：**132 环节**（docs/_working/fullflow_mining/00_skeleton/）+ TDM 182 节点（config/trading_decision_map.yaml）+ 四层未接线清单（docs/_working/wiring_gap_inventory_20260927.md，59 零引用表/13 无环节域/41 未接线环节/38 TDM null）+ F123-F132 补挖案卷。
- **裁定：不重挖 120 册（违内收），做"补干挖矿"**：由字节/骨架车道产出 `docs/_working/night_sweep_20260929/00_skeleton_nightsweep.md` = 环节总表（环节×状态轴[已通/开口/等Owner]×开口项映射审计卡号），对开口环节逐个补挖矿卡（六向台账快照+自审闸三态+处方）。谁挖干谁先开工，不必等总筹点头。
- 新建施工文档一律落 `docs/_working/night_sweep_20260929/`（CREATE-GUARD token 先行独立批）。


---

## 来源（第二遍）：`docs/_working/nightmine_campaign/L8b_ledger.md`

`TDM-E-L1-S0/calibration/02_货币卡｜03_流动性卡｜04_海外卡｜05_政策事件卡`、
`TDM-E-L1-S2/calibration/07_连板家数分布`、`TDM-E-L1-S3/calibration/02_昨日涨停溢价｜03_晋级率｜04_情绪先锋四态`、
`TDM-E-L9-Z1/ablation/02_十态状态机与十八列schema强制`、`TDM-E-L9-Z2/ablation/02_净零与chain_refs双向对账`。
（前 8 张 `data_binding: null`，卡内只有 window/buckets/pillars/target。）复核线索（实测）：
- L1-S0 货币/流动性卡节点 `data_refs=[DS-098]` → 实体 `capital.margin`（**非表名，DS→表映射缺口**）；两融实表
  `c1_market.margin_trading` 实测 2024-09-02..2026-10-08 / 2,100,709 行 → 即便补映射，IS 窗 2019-2023 仍断供。
- L1-S3 涨停溢价/晋级率/先锋四态：原料在 `c1_market.limit_up_pool`（1,426 行 / 23 日）、`daban_board_event`（1,767 行 / 21 日）、
  `c1_market.emotion_index`（close_final 8,617 行 1991..2026-09-30）——微观事件面只有 2026-09-01 起，2019-2025 窗真断。
- L9-Z1/Z2 schema/对账卡=治理面（考结构不考数据），无 CH 序列可取。


---

## 来源（第二遍）：`docs/_working/t0_matrix/HANDOFF_emoreplay_stranded.md`

本包的六段相位真源**不依赖**上述任何未落地块：`six_phase_history_v1.csv` 的宏观腿走
`c1_backtest.regime_snapshot_history`、微观腿走广度指数，映射件 `auto_mount.py` 全在 HEAD。
唯一依赖产线的是 GPU 输入包里的**连续温度计列**（`emotion_index`/`band5`/`ok_n`），
其公式已在 HEAD 且 21/21 复算一致 ⇒ 本包结论有效性不受本移交项阻塞。


---

## 来源（第二遍）：`docs/_working/tdm_mount/f_mountgate_spec_v1.md`

- **一句话**：把「新模块必有挂载裁决」从君子协定升级为提交时技术强制；同时兑现 TDM v1.3 立项（0e94229a1b1）已批的「蓝图锚↔地图节点引用一致性校验」。
- **净零申报**：与上述已立项项**合流扩展**（一 gate 两职责），非新建第二真源、非第二挂载裁决通道；裁决真源仍=layering_policy v1.3 的三字段纪律（module_mounts 机生禁手改）+ 总筹裁决册增量维护。
- 病根对齐 TRANSLATION-COVERAGE 先例：100% AI 开发下，事后普查治理永远滞后于缺口制造（B 账本实证 233 缺口即一次性的代价）。

- 文件：`src/zephyr/governance/audit/tdm_mount_coverage_reconciler.py`；
  `make_tdm_mount_coverage_reconciler(gateway)`，priority=952（挨翻译册 951 之后，同 late-stage warn-only 全扫族）。
- **trigger**（ReconcilerSpec.trigger 签名 `(committed_files) -> bool`）：命中任一
  config 图族 / 豁免册 / docs/03_modules/**/blueprint.md / src|scripts 新 .py / 翻译册 / depgraph 登记面 → True。
- reconcile：shared helper 全量重扫（人口 vs mounted∪exempt∪marker）→ 孤儿判红 →
  落盘 `.runtime/tdm_mount/orphan_report.json`（warn-only 不阻断）→ 调 manifest 生成器重申投影。
- 头注 `# noqa: m10-time-trigger`（commit 事件触发豁免，翻译册 reconciler 同款）；
  永不抛异常；DB/YAML 不可达降级 ReconcileResult(action="warn")；注册接线=git_commit_gateway.py
  翻译册 reconciler 注册行（≈L1860）相邻。

`tests/governance/audit/test_tdm_mount_coverage_reconciler.py`：trigger 命中矩阵/孤儿判红落盘/真源不可达 warn 降级，≥3 例。
外加 shared helper 单测（mounted 集合并集口径/marker 正则理由非空）。


---

## 来源（第二遍）：`docs/_working/tdm_mount/fc_ds_sourceline_gap_v1.md`

| # | node_id | 名称 | 类别 | 证据 |
|---|---|---|---|---|
| 1 | TDM-E-L9-A16 | 源线·投入产出 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [投入产出;io_table;input_output]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 2 | TDM-E-L9-B01 | 源线·卫星影像 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [卫星;satellite]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 3 | TDM-E-L9-B03 | 源线·招聘JD | 源线 | data_refs 缺失；语义检索零命中（关键词表 [招聘;hiring;job_posting]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 4 | TDM-E-L9-B04 | 源线·电商价格 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [电商;keepa]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 5 | TDM-E-L9-B05 | 源线·招投标 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [招标;投标;procurement]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 6 | TDM-E-L9-B06 | 源线·社媒舆情X/Reddit | 源线 | data_refs 缺失；语义检索零命中（关键词表 [reddit;twitter;社媒]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 7 | TDM-E-L9-B07 | 源线·雪球/股吧散户情绪 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [雪球;股吧;guba;xueqiu]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 8 | TDM-E-L9-B08 | 源线·APP榜单 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [qimai;sensor_tower;app_rank]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 9 | TDM-E-L9-B10 | 源线·信用卡/支付消费 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [信用卡;spending]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 10 | TDM-E-L9-C01 | 源线·实时门店客流 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [客流;footfall]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 11 | TDM-E-L9-C03 | 源线·直播电商实时成交 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [直播;livestream]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 12 | TDM-E-L9-G2 | 图谱·ChainKnowledgeGraph事实层 | 图谱/快照/治理 | data_refs 缺失；语义检索零命中（关键词表 [knowledge_graph;ckg;事实层]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 13 | TDM-E-L9-G3 | 图谱·实体股权穿透 | 图谱/快照/治理 | data_refs 缺失；语义检索零命中（关键词表 [股权穿透;equity_penetration;entity_graph]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 14 | TDM-E-L9-G5 | 图谱·投入产出传导 | 图谱/快照/治理 | data_refs 缺失；语义检索零命中（关键词表 [投入产出;io_table]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 15 | TDM-E-L9-AGG | 知识供给汇聚 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |
| 16 | TDM-E-L9-D1 | 决策假设·因子组合挖掘 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |
| 17 | TDM-E-L9-D2 | 决策假设·登记与考试方案 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |
| 18 | TDM-E-L9-E1 | 验证·一问一考考试链 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |
| 19 | TDM-E-L9-E2 | 验证·结论回传与修正 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |
| 20 | TDM-E-L9-Z1 | 治理·问题治理与状态机 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |
| 21 | TDM-E-L9-Z2 | 治理·净零与资产对账 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |


---

## 来源（第二遍）：`docs/_working/three_piece_infra/00_plan_and_ownership.md`

### 包 13.4（戊道）全连接矩阵
- 生成器产 `connection_matrix.csv`（六类边，见 §3.5），三态：`WIRED` / `SHOULD_NOT_WIRED_BUT_ISN'T`(该连未连) / **`NO_DECLARED_EDGE`**(声明缺失，单列不并入缺口，见 §2.1 陷阱)。
- 复用 `check_decision_map.py` R9/R11 与 `validate_decision_map`，**禁另起一套 TDM 解析**（读 `src/zephyr/trading/decision_map.py` 的 loader）。
- `--check` rc=0/1 语义钉死；仪表盘只加**数据源**（`api_server.py` mtime-cache 读生成物 或 `components/` 新 fetch/render + `build_tabs()` 一行，二选一，禁改既有面板逻辑）。
- 红证：人为抹掉一个 `module_ref` ⇒ 矩阵必点名；塞一条假 `data_refs` 指向不存在表 ⇒ R11 通道必红；空声明轴不得算缺口。


---

## 来源（第二遍）：`docs/_working/total_command_closeout/95_chief4_ledger.md`

**F34 L9 知识汇聚点建成待落地**：src/zephyr/data/l9_readiness_aggregator.py（653 行，16 测试绿+真网 dry-run 39 行实证）+ schemas/categories/l9_readiness_daily.py + scripts/ch/apply_l9_readiness_ddl.py + pipeline_events.py 事件接线 +11 行 + TDM module_ref 挂接（claim+CAS+双复核过）+ detect_orphan_py.py 一行豁免（.qoder 3.5G 影子清除随批）。**8 件在暂存区**；3 翻译+4 token 已登记（总册文件在暂存区，claim 归 st-zmaster2 死会话——落地前 release 其死 claim 再 claim）。
A3 待裁四件：①vendor/Kronos/examples 30 假孤儿归引入方/Owner ②interactive flag 翻转=Owner ③c1_market.tick_data 空表 vs f30 册 89.5 亿 tick 口径（归 M1 校准）④F35 D2/E2 回填归 TD/TDM 车道。


---

## 来源（第二遍）：`docs/_working/vmap12_flesh/f2_blood_template.md`

| 红 | 判据 | 数据源 |
|---|---|---|
| 孤儿 | 该挂没挂：表A 32 候选中高置信者未出现在任何节点挂载面 | 表A × 图 yaml |
| 抄写 | 复制非引用：节点四字段里出现真源条目正文（非标识符/指针） | 图 yaml 语义层 |
| 未挂病历 | 表B 合格 4 本未挂 ≥1 环节；停更 3 本须以 orphan 注记挂载 | 表B × casebooks |

