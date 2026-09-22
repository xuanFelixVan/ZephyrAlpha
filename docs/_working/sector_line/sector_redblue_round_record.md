---
ttl: task_bound
title: 板块线红蓝对抗报告+循环两轮零记录
created: 2026-09-22
sid: st-secmine-20260922
lane: sector_line
status: draft（四轮实录：R1 三发全修、R2 三发全修、R3/R4 连续两轮零）
doc_version: v0.1
---

# 红蓝对抗报告+循环两轮零记录⑥

> 方法：蓝方=本班自查（事实断言逐条对 DB/代码实测）；红方=对抗视角（路径存在性/域断言/
> 过度断言/门禁合规）。全部发现如实留痕，修后复验；判档纪律遵循裁定#325。

## R1（蓝方·事实断言核查）——3 发现，全修

| # | 发现 | 定级 | 处置 |
|---|---|---|---|
| 1 | 考试卡 D2 写"regime 可回溯窗 2024-08 起"系未实测猜测——实测 regime_state_anchored **min=2017-07-11**，且 dominant 现值域仅 r1~r4 四档（anchored 表） | 事实错误 | 已改：2017-07 起+四档实测+r10~r12 换源注记（并触发对 L2 门值域的 R2 深挖） |
| 2 | 盘点册 §11 总账"板块行情 A=6/B=3/C=3"与 §1 明细表逐行不符（实际 5/2/2/1） | 计数漂移 | 已改：总账按明细行计 5/2/2/1 |
| 3 | 盘点册 §11 总账"行业 ETF A=5"与 §3 明细 4 行不符 | 计数漂移 | 已改：A=4 |

## R2（红方·对抗核查）——3 发现，全修

| # | 发现 | 定级 | 处置 |
|---|---|---|---|
| 1 | 盘点册 §3 引用的 bizmine 行业ETF 真源路径少一层目录（etf_t0_retest/），照抄会 404 | 引用失效 | 已改：`archive/2026-09/bizmine_night/etf_t0_retest/etft0_screen_results.csv`（ls 实证） |
| 2 | 盘点册 §4"dominant 真实值域=r1~r12"暗示 r5~r9 出现过——实测 regime_snapshot_history 观测值域恰为 **7 键 {r1,r2,r3,r4,r10,r11,r12}，r5~r9 从未出现** | 域断言不精确 | 已改：7 键全覆盖观测域、映射表零缺口（此修正反而强化了 L2 门桥接的完备性论证） |
| 3 | 盘点册 §0"16 模块 CONSUMERS **全**挂待 G05"过度断言（实为 majority，三处已接线实证在前） | 过度断言 | 已改："以待 G05 为主"+保留三处接线实证 |

## R3（机械全扫）——2 疑点均证伪，零实发现

- 六件内全部 `docs/_working/**` 路径引用批量存在性扫描：2 个 MISS 疑点（wiring_proposals_L2_sector_gate.md、redblue_round_record.md）经 ls 直查**均为扫描脚本误报**，实物在位——零实发现。
- 同窗核验提交链事件：token 先行批 qid 0001 landed=`noop@1877e328`——判定为**被吸收型 noop**（情绪班会话 1877e328f3 的注册表提交吸收了本班工作区增量）；按"被吸收型勿 requeue"配方核验：`git show HEAD:<registry> | grep -c secmine` = **12（=6 条 token × token 行+created_by 行）**，本班 6 条 token 确证已入 HEAD 在编。零动作正确。

## R4（终扫·门禁合规+跨册一致性）——零发现，两轮零达成

- frontmatter 六件 YAML 解析全通过；无 doc_type 字段（EXEMPT-ZONE-FM 合规）；文件名全字母开头 snake_case；落盘走子目录（FOLDER-CAPACITY 合规）。
- 跨册数字一致性：16 模块（盘点册§7=方法论§7.4=缺口G6）、39 源/19 核实（方法论§8 自洽）、7 键（盘点§4=骨架——）、tilt 0.8~1.2（骨架§4=卡D2-6）、五成分（骨架§3=卡S10）逐对相符。
- 六件与 token 注册表 6 条一一对应（file 路径逐字核对）。

**结论：R3/R4 连续两轮零，红蓝循环达标。** 残余风险如实登记：①emotion_index 成品未出，
D2 卡主判窗预期 INSUFFICIENT（预登记非事故）；②全部阈值保持 proposed 待考试校准；③
capability_lookup 注册盲区修复属 ulib 班写域，本班只移交未施工。

## R5（Owner 追问"挖干了吗"触发的挖干补查轮）——4 角落补挖，6 发现，全回灌

Owner 挑战成立：首轮六件交付面完成，但按挖干判据四个角落未翻到底。本轮反向全量扫描：

| # | 发现 | 处置 |
|---|---|---|
| 1 | 233 张表首轮正则筛表漏网 7 张板块聚合原料：dragon_tiger_seat（4.5 年龙虎榜深史）/margin_trading/northbound_hold_snapshot（停 3 个月 C）/daily_valuation/analyst_forecast/shareholder 族/stock_daily_basic——**三标尺的景气+拥挤度原料在库** | 盘点册新增 §12.1 四态表；缺口清单新增 G14（三标尺升维候选，v0 不动） |
| 2 | 调度真源实为 `src/zephyr/data/config/tasks.yaml`；产奶量实证：880 日K/快照/资金流全部在产满量，**intraday 任务在册在调但零产 7 天=通道/执行层故障非缺登记**，daban_derive 同款 | 盘点册新增 §12.2；G2/G3 根因面收窄 |
| 3 | **sector_fund_flow 改判 C→B**：在产+短史（09-15 开采）非断供 | 盘点册 §12.5 改判+G7 同步 |
| 4 | 策略层零直连、前端 dashboard 有板块展示面（表字典+个股板块标签） | 盘点册新增 §12.3 |
| 5 | 架构文档面（11_d_data_eng/62_d_plan/asset_catalog 等）已被 22 号 spec 枢纽全覆盖 | 盘点册新增 §12.4 判定"已挖干" |
| 6 | 北向持股停 3 个月与外部方法论 #16 北向披露规则调整风险同源互证 | §12.1 行注记 |

**R5 判定**：六发现全部为增量资产/证据升级，无推翻六件主结论者；"薄在集成不薄在原料"
结论被补遗**加强**（原料面比首轮盘点更厚）。挖干补查后四角落全部翻过：表全量反向过目✓、
调度产奶量✓、策略/前端消费面✓、架构文档面（经 spec 枢纽）✓。

## R6（提交链实战轮·N-16 重名改判）——1 事故，改名修复

- **事故**：qid0002 六件批死于 **N-16 基名重名门禁**——本班照搬情绪班文件命名（internal_inventory/
  external_methodology/prereg_exam_cards_v0/gap_list_and_construction_proposal/redblue_round_record
  五基名与其未提交文件撞车；N-16 扫工作区不看 HEAD，"未提交"不豁免）。**教训入册：跨班同构
  交付件命名必须自带 lane 前缀，照搬兄弟班命名=必撞 N-16。**
- **修复**：五件 git mv 加 `sector_` 前缀（sector_layer_skeleton_v0.md 基名本唯一不动）；
  注册表 5 条 token 路径先行批更新（gate 读 HEAD 配方）；改名批重入队。
- 改名后复核：六基名全仓零撞名（find 实证）；token 路径与新文件名一一对应（注册表先行批
  逐字更新）。

## 附：本班提交链留痕

- qid 0001（token 先行批）：done，被吸收型 noop@1877e328，HEAD grep=12 实证在编，勿 requeue。
- qid 0002（六件批）：**dead（N-16 基名重名）**——已被改名批取代，勿 requeue（requeue 会从
  死件袋复活旧路径旧内容）。
- qid 0003（补遗批，旧路径 3 件）：pending 排队中，预计排到时同因死或路径失活——**同被改名
  批取代，勿 requeue**；补遗内容已含在改名批中零丢失。
- 改名终批：token 路径先行批 + 六件改名批（五件 sector_ 前缀 + skeleton 原名），见最新 qid。
