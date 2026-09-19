---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 因子挖掘 SOP——矿脉→假设→IC筛→预注册→沙箱→E4正考→组队→入库 八段缝合册（regime 条件化强制）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-19
topic: mining_sop
---

# 因子挖掘 SOP——八段一段闸（真源）

> **一句话**：本册把"矿脉选择 → 假设登记 → IC 大海选（宽测筛）→ 预注册卡 → 沙箱三关 → E4 正考 → 组队备料 → 入库/归档"八段缝成一条因子生产线；每段给输入/输出产物与真源指针，不复制真源。**新增核心条款=regime 条件化**（§2）：每因子 MUST 报"什么状态下有效"，不看行情状态的考试结论一律降级为"无条件证据档"。
> **定位**：[mining_sop_policy.md](mining_sop_policy.md)（通用挖矿方法论）在**因子域**的专用实例，与 [skeleton_mining_policy.md](skeleton_mining_policy.md)（骨架域）、[trading_decision_map_pathfinding_policy.md](trading_decision_map_pathfinding_policy.md)（地图域）并列；语义冲突时按域归真源。
> **诞生**：2026-09-19 裁定#365 转正（v0.1 工作稿升 permanent；前身=`docs/_working/bizmine_night/factor_sop_screen/factor_mining_sop_v0_1.md`，固化 2026-09 两次实战先例：P3 一致预期族预注册、bizmine 通宵战 F 车道大海选）。
> **亲缘**：[sop_b_node_loop.md](../backtest_system_sop/sop_b_node_loop.md)（七步循环，真源不复制）｜[sop_c_strategy_library_intake.md](../backtest_system_sop/sop_c_strategy_library_intake.md)（入库漏斗，真源不复制）｜[exam_policy.md](../backtest_system_sop/exam_policy.md)（**考试段判据真源**：准入/口径/成本双口径/复权降级/负结果台账——本册 S5 只管位次，判据一律按 exam_policy 执行）｜诚实条款冲突时以战役令 §2 与本册 §3 就严者为准。

## 0. 流程总览（八段一段闸）

```
S0 矿脉选择 ─→ S1 假设登记 ─→ S2 IC 大海选（宽测筛）─→ S3 预注册卡 ─→ S4 沙箱三关
     (挖矿)        (立卡)          (筛≠考)              (封闭族)        (同源预检/去重/数据面)
                                                                    ↓
              S7 入库/归档 ←─ S6 组队备料（Owner 门 B-15）←─ S5 E4 正考（窄测/考试）
```

- **铁律一（筛≠考）**：S2 大海选只产"待考池"，不判 PASS/FAIL；任何因子不得凭海选结果直接入策略或改 factor_registry 的 ic/ir 字段。
- **铁律二（先钉后跑）**：S2 的筛选协议与 S3 的考窗/阈值/桶边界一律在跑数之前写死（预注册在先）；事后挪门柱=本批作废。
- **铁律三（全量入册）**：含负结果/零结果全部如实入册（另类挖矿 0/5 前科在案），缺留痕=结论作废（sop_b 留痕铁律延伸）。

## 1. 八段分述（输入/动作/输出）

### S0 矿脉选择（输入：数据资产台账+终局缺口）

- 动作：按 mining_sop_policy §2 六向寻路（内部反查优先+全网搜索补盲），过 §5 防噪音四闸（来源可溯/交叉验证/A股适配/可回测+数据可得——"可得≠可用"须补质量画像）。
- 输出：《矿脉日志》+ 候选假设清单（每条=机制一句话+数据面+出处）。
- 终止：矿脉枯竭结构判据（六向全查无+无未挖长尾），禁轮数触发。

### S1 假设登记（输入：候选假设清单）

- 动作：逐条立卡进 `factor_registry.yaml`（candidate 态）：factor_id / formula / inputs / mechanism（alpha_source）/ A 股适配改造点 / 数据面实查（表、字段、区间、覆盖）。映射不了数据列的（板块级/事件级/需专用数据）当场记 skip 及原因，禁硬凑。
- 输出：factor_registry candidate 条目（真源；本册不改其 schema）。

### S2 IC 大海选（宽测筛，输入：candidate 全集）

- 动作：预注册筛选协议（候选集/数据口径/IS 窗/前瞻档/除权与样本过滤/IC 算法/regime 状态轴与桶/排名规则/多重检验警示线）→ 按协议跑横截面 Spearman 秩 IC → 全部结果入册。
- 实战先例：`docs/_working/bizmine_night/factor_sop_screen/screen_report.md`（bizmine F 车道，IS 2019-2023，前瞻 5/10/20，F4_BDI 状态 T-1 分桶，top-20 待考池按预注册排名规则产出）。
- 输出：screen_results.csv（全候选×统计量+skip 清单）+ screen_report.md（协议回执+top-N 待考池+偏离登记）。
- 边界：不判 PASS；负结果照登；协议外任何临时改动进「偏离登记」逐条列明。

### S3 预注册卡（输入：待考池因子）

- 动作：每条升考因子写预注册卡（模板=§4；先例=p3_prereg/P3-B-NARROWING.md）：机制、数据面实查（P3 先例教训：prereview 声称的覆盖必须复核，consensus 值类"9.6 年完整"实查 2022 后断供）、考窗冻结（IS/OOS 写死）、**封闭族声明（N_eff）**、通过阈值预注册、多重检验账（族越大 DSR>0.5 所需 SR 越高）。
- 输出：prereg 卡（frozen，启动后不得改动）；落 `_working/` 对应 lane 目录，候 Owner 认可后归档。

### S4 沙箱三关（输入：prereg 卡）

1. **同源预检**：对既有基座（如 REG-IND-001）做增量 IC 预检，防同源重复计票（L1 车道前置先例）；
2. **族内去重**：相关性 >0.9 的变体先去重再定 N_eff（P3 §4 落选先例：OBV/AD/PVT 五条累积量族直考=N_eff 膨胀）；
3. **数据面复核**：以考试时点实查为准（P3 §5：数据断供/污染段圈出，考窗限净段，结论降级"净段证据档"）。
- 输出：沙箱过关单（三关各留痕）；任一不过→回 S2/S3 或落选登记。

### S5 E4 正考（窄测/考试，输入：沙箱过关单）

- **准入与判据真源=[exam_policy.md](../backtest_system_sop/exam_policy.md)**（何时允许点火一次考试/考窗成本通过线口径/复权暂定降级/负结果台账），本段只固定位次：按 sop_b ⑥执行——完整成本五项（费率读实际账户配置禁硬编码）+ WFA/OOS 门控 + 按对象类型映射验证层（factor→V1）+ OverfittingDetector 三阶段 + Deflated Sharpe（喂全部留痕试验次数）。执行器：`scripts/backtest/f06_e4_wfa_exam.py`（只可运行不可改）。
- **regime 条件化为必报项**（§2）：正考报告除总体指标外 MUST 附分状态桶指标；无状态分解的正考报告按"无条件证据档"降级收录。
- 输出：《节点回测报告》（六段分档+成本口径+迭代留痕附录），三出口=达标/不达标有假设回S0-S3/判死归档（出口语义与负结果台账落点按 exam_policy §5-§6）。

### S6 组队备料（Owner 门 B-15，输入：E4 达名单）

- 动作：三档候选名单（稳健/均衡/进攻，全标观察档）+ 按状态切换的组队示意 + 弹药需求清单（到目标还差多少条多强的 alpha）；**禁出部署结论**——部署与 sim→production 是 Owner 门位（宪法 §5）。
- 输出：组队备料件（备料≠部署）。

### S7 入库/归档（输入：E4 报告 / 判死单）

- 入库正路：策略走 sop_c C5-C6（差异化三轴+STR-* 注册+挂图+配比）；因子回写 factor_registry 的 ic/ir/decay 字段（只读真源回写走既定 gate）；判死的带"≥3 个已排除候选与排除理由"归档（sop_b ⑦），并落 exam_policy §5 负结果台账。
- 输出：注册表变更（走 GitCommitGateway）+ 台账行。

## 2. regime 条件化条款（本册新增核心，全段强制；=缺口 G4 销项载体，裁定#365）

> 背景教训：79 严选只活 1 条的疑似病根=考试不看行情状态；Owner 主纲=灰度大盘状态→选因子选策略（bizmine_general_order §0）。

1. **状态轴选定纪律**：一次考试/筛选只允许**一个预注册主轴**（成例：F 车道钉 alt_regime_signal F4_BDI，T-1 PIT）；换轴/加轴=新预注册，禁跑完换轴挑好看的（选择性报告）。
2. **PIT 口径**：状态取 T-1 日（严格早于因子日的最近一条状态）；禁用当日成立的状态给当日因子分桶。
3. **桶边界 IS 期钉死**：分桶规则（档数/边界/最小桶样本）在预注册里写死且只在 IS 期拟合；最小桶样本不足（F 先例：<60 交易日）标 low_power 照报不删。
4. **报告模板（每因子必报）**：总体 IC/Sharpe + 各状态桶 IC/Sharpe/占比 + "该因子在什么状态下有效、什么状态下失效"一句话结论。**若各桶表现接近，如实写"状态条件化暂无证据"，禁硬凑故事**（R 车道同款诚实条款）。
5. **分状态不稳剪**（对齐 sop_b ⑤）：仅 1-2 桶有效且无机制解释的→收窄适用状态并写进 factor_registry（regime_valid 字段已有，回填它）；全状态不稳→判死或回炉。
6. **灰度钩子**：状态轴从二值/三值向灰度（连续概率分位桶）升级时，桶边界同样 IS 钉死；灰度轴真源=c1_backtest.regime_state_anchored / regime_detector 七维概率（R 车道管辖，本册只引用不定义）。
7. **多重检验联动**：桶数计入 N_eff 账（§3）；桶×因子×前瞻的乘积是假阳性放大器，警示线按总组数校准。

## 3. 多重检验纪律（贯穿八段）

1. 桶边界/规则/阈值/考窗一律 IS 期钉死（预注册在先，事后禁挪）。
2. 全部结果入册：正/负/零结果同权留痕（另类挖矿 0/5 前科=没有正式台账的血泪；台账制度真源=exam_policy §5）；"没找到"必须写清排除了什么。
3. 筛≠考：海选 top-N 只是待考池；考试结论只出自 S5 且必须 Deflated Sharpe 校正（喂全部试验次数）。
4. 封闭族：每批考试 N_eff 封闭（P3 先例：20 条混考=N_eff=20 功效双杀，拆批各定）；中途加条目=重开预注册。
5. 警示线参考：海选阶段 |t|>3.29（0.1% 双侧）仅作"值得升考试"弱证据；这从不是"有效"的证据。

## 4. 预注册卡模板（v1.0，字段引 p3_prereg 先例）

```yaml
ttl: task_bound
title: <lane>-<family>-<NNN> 预注册卡——<因子/族名>
status: frozen          # 启动后不得改动
family_id: <族ID>
n_eff: <N>              # 封闭族声明（含失败者）
hypothesis: <机制一句话+学术/实务出处>
data_plane:             # 数据面实查（考试时点复核，禁抄 prereview 声称值）
  - {table: ..., fields: ..., range: ..., coverage: ..., pollution_notes: ...}
proxy_downgrade: <无 | proxy 描述+披露>
exam_windows:
  is:  <YYYY-MM..YYYY-MM>       # 冻结
  oos: <YYYY-MM..YYYY-MM..>     # 冻结
thresholds:                       # 通过线预注册
  - {metric: ..., rule: ...}
regime_axis: <主轴+PIT 口径+桶规则（边界 IS 钉死）+最小桶样本>
multiplicity:
  total_tests: <因子×前瞻×桶 总组数>
  dsr_note: <N_eff 与所需 SR 关系一句话>
cost_spec: <成本口径（引擎现行五项 / Owner-001 档），双口径并存声明（语义真源=exam_policy §4）>
exits: [达标→S6 备料 / 不达标回S0-S3 / 判死归档]
```

## 5. 产物与台账

- 每段产物落盘位置：正式候选件 `docs/_working/<campaign>/<lane>/`（.md 带 ttl frontmatter）；临时脚本/中间缓存一律 `.runtime/tmp/<campaign>/<lane>/`；禁生产路径写测试输出。
- 台账：每完成一段追加战役台账一行（台账锁忙则在车道报告登记代追加）；考试类批次的负结果/试验次数台账按 exam_policy §5 落。
- 提交：一律 GitCommitGateway / git_commit.py 正门，改前 claim，毕后 release。

## 6. 转正记录与净零申报（裁定#365，2026-09-19）

- **转正**：v0.1 工作稿（`docs/_working/bizmine_night/factor_sop_screen/factor_mining_sop_v0_1.md`，已标 superseded 存档）升 permanent 本册；§2 regime 条款随迁升 permanent（=strategy_sop_gap_report **G4 销项**；S4 第三关=**G10**、S6-S7 组装段=**G2** 的载体同批落地）。
- **净零申报**：同批新立 [exam_policy.md](../backtest_system_sop/exam_policy.md) 一本（净零原则下唯一新立候选），对价=**G3+G5+G6+G8 四条缺口登记销项**（strategy_sop_gap_report.md 相应条目已标 resolved）；其余缺口归宿按该报告 §3（G1 并 mining_sop 实例、G7 走 apply_* 架构批、G9 并 sop_c，另批施工）。
- 分工边界：本册=因子生产线编排（挖→筛→考→组队）；exam_policy=考试判据语义（准入/口径/降级/台账）。两册互挂不复制，语义冲突时考试判据以 exam_policy 为准、流程位次以本册为准。

## 7. 实战回填记录

| 日期 | 先例 | 回填段落 |
|------|------|---------|
| 2026-09-17 | P3-B-NARROWING（封闭族 N_eff=6+数据面复核推翻 prereview 声称+proxy 降级披露） | S3/S4/§3.4 |
| 2026-09-19 | bizmine F 车道 IC 大海选（预注册协议在先+全量入册+top-20 待考池+F4_BDI T-1 分桶） | S2/§2/§3 |
| 2026-09-19 | bizmine R 车道（灰度状态轴主权+条件化诚实条款） | §2.6 |
| 2026-09-19 | 裁定#365 转正（v0.1→permanent；exam_policy 拆分立册） | 全册定稿 |
