---
ttl: task_bound
completes_when: 随战役归档
title: W8 红蓝验收报告——20 问反查
owner: ZephyrAlpha-Owner
session: st-chainpile-20260922
date: 2026-09-23
---

# W8 红蓝验收报告（20 问反查）

> 方法：从已实插 PG 的 283 问（`snapshots/registry_latest.yaml`，row_count=283，经 PG 只读实测 `meta_question.meta_question`=283 行对账一致）机械抽样 20 问，逐问反查五项：①五要素齐备 ②证据真实性 ③一问一考 ④查重 ⑤判读合规。
> 真源：五要素定义=[00_piling_minutes.md §2/§3]；源线=[02_source_line_registry.md]；图谱=[03_graph_registry.md]；层级判读=[01_layer_charter.md]+裁定#400；机检口径=`src/zephyr/governance/meta_question/registry.py`+`scripts/governance/check_meta_question_batch.py`+10 号件 §2.2/§3。
> 只读纪律：本验收零 git、零写命令；对 PG 仅执行 information_schema 查询与 count(*)；CH 表经仓内 DDL-as-Code（`schemas/categories/`+`scripts/ch/apply_market_tables_ddl.py`）核实。唯一写入=本件。

## §1 抽样清单（机械可复现）

分层配额：L0 抽 2（N=4）｜L1 抽 8（A 档 4（N=134）+B 档 2（N=60）+其余 2（N=6，line_ref 空的 U1-U6 母问））｜L2 抽 3（N=18）｜L3 抽 3（N=20）｜L4 抽 2（N=18）｜L5 抽 1（N=14）｜L6 抽 1（N=9）=20。
取样规则：层（档）内按 q_id 尾号升序排，取等距位 `idx=floor(i*N/n)`（i=0..n-1）——任何人可重放得到同一清单。

## §2 抽样 20 问反查结果表

| q_id | 层 | 线/图 | ①五要素 | ②证据 | ③一问一考 | ④查重 | ⑤判读合规 | 总判 | 一句话依据 |
|------|----|-------|--------|-------|----------|-------|----------|------|-----------|
| PQ-0001 | L0 | M1 | PASS | PASS | PASS | PASS | PASS | **PASS** | 两 PG 表实存（主表 283/审计 566 行实测）；拒绝率≤20%+单码≤50% 双数值阈值；M→L0 合判读表 |
| PQ-0003 | L0 | M3 | PASS | PASS | PASS | PASS | PASS | **PASS** | 可解析率=100% 具体可判；consumers 含未答看板（词表登记缺口归 F-3 系统项） |
| PQ-0005 | L1 | U1 母问 | PASS | PASS | PASS | PASS | PASS* | **PASS** | 19 个 DS 键与 W4§2 A 档 16 线锚并集逐一相等；threshold=16/16 硬判；*line_ref 空=母问口径，豁免未登记（F-2 注） |
| PQ-0008 | L1 | U4 母问 | PASS | PASS | PASS | PASS | PASS* | **PASS** | "高危线 A04/A05/A09"与 W4 各线 U4 风险标注（中高/高危/中高）吻合；同 F-2 注 |
| PQ-0011 | L1 | SL-A01-x1 | PASS | **WARN** | PASS | PASS | PASS | **WARN** | 考法需分钟线（30 分钟均线斜率+开盘后 30 分钟收益）而 data_sources 只挂 kline_daily+DS-MINIQMT；仓内 kline_1min/30min DDL 在库未挂（F-4） |
| PQ-0031 | L3 | S1 | PASS | PASS | PASS | PASS | **WARN** | **WARN** | pit 明写"今日输出→明日输入"[纪要§8.2] ✓；但 L3 全组 line_ref 缺（B 级规则未实现，F-2） |
| PQ-0037 | L3 | S7 | PASS | PASS | PASS | PASS | **WARN** | **WARN** | DS-CLS/money_flow 均实存；"多源"仅 2 源偏薄+聚合器属纪要§8.3 后续对话（W7 R7 已路由 建）；F-2 同上 |
| PQ-0043 | L4 | D1 | PASS | PASS | PASS | PASS | PASS | **PASS** | 三 CH 表实存；consumers pf_alloc 在 functional_domain_registry 命中（ssot=src/zephyr/pf_alloc）；T-1/T+1 时间分层显式 |
| PQ-0051 | L5 | E1 | PASS | PASS | PASS | PASS | PASS | **PASS** | E→L5 合判读表；覆盖率=100% 机械可判；meta_question 表实存 |
| PQ-0058 | L6 | G1 | PASS | PASS | PASS | PASS | PASS | **PASS** | G→L6 合判读表；net_zero 非空率+正则可解析=机械判据 |
| PQ-0063 | L2 | G1(GRF1) | PASS | PASS* | PASS | PASS | **WARN** | **WARN** | 所引 ig_io_edge/ig_node/kline_daily 均实存；但该问资产实为 G5 槽的 io 边（16,859 条 100% 挂零缺口 WP-0.5 在案），W7 却按 graph_ref=G1 路由 R4"接"（G5 孪生问走 R3"建/D4"）——路由不一致+F-1 |
| PQ-0069 | L2 | G2(GRF7) | PASS | PASS | PASS | PASS | **WARN** | **WARN** | 480 行业树与 511 申万均出自 ig_fact(ckg_2021) 证据成立；但"图谱质量问"正是裁定#400③ 留后续对话类目，挂载未收口（F-1） |
| PQ-0075 | L2 | G4(GRF13) | **WARN** | PASS | PASS | PASS | **WARN** | **WARN** | threshold"收敛…**或登记差异**"含兜底豁免分支，任意结果皆可过，证伪力弱化（F-5）；F-1 同上 |
| PQ-0082 | L3 | 扩展 | PASS | PASS | PASS | PASS | **WARN** | **WARN** | 涨跌家数可由 kline_daily 派生，阈值>55%+样本≥30 具体；F-2 同上 |
| PQ-0090 | L4 | 扩展 | PASS | PASS | PASS | PASS* | PASS | **PASS** | DS-TQCENTER/money_flow 实存；与 PQ-0045 同信号（板块动量/轮动+资金流 top3）异考法（扣费年化超额 vs IR 归因贡献），登记查重观察、不构成重考 |
| PQ-0123 | L1 | SL-A05 CMB | PASS | PASS | PASS | PASS* | PASS | **PASS** | ann_date PIT 正中 W4 A05"高危-按公告日对齐"条款；同族 PQ-0124/0125 仅前瞻窗长差（5/20/1 日）=预注册空间 lines6×wins3 [11号件§6]，为独立考单元非拆并不当 |
| PQ-0157 | L1 | SL-A05 U6 | PASS | PASS | PASS | PASS | PASS | **PASS** | 退役判据重放演练可机械执行（注："可执行率"口径半主观，归 Max 复审域）；ann_date ✓ |
| PQ-0190 | L1 | SL-A11 U3 | PASS | PASS | PASS | PASS | PASS | **PASS** | DS-EIA 锚实存；frequency=weekly 与该线 U3 周三发布节奏同源派生；threshold 不一致项=0 硬判 |
| PQ-0224 | L1 | SL-B01 U1 | PASS | PASS | PASS | PASS | PASS | **PASS** | Copernicus/Planet 均为 W4 已核实渠道，DS-EIA 为其 U6 交叉锚 ✓；frequency=daily 系按 U3 天级过境机械派生（注：宣称清单载体未指定，测量依赖 Max 复审核准） |
| PQ-0254 | L1 | SL-B06 U1 | PASS | **WARN** | PASS | PASS | PASS | **WARN** | data_sources 直引 Reddit API/X API——W4 明标"本环境未核实，复验前禁引用入库"（F-6）；pit_proof 已带"渠道未复验前不引生产"缓解且 W7 R1/台账 R-3 在册 |

计数：PASS 11 行，WARN 9 行（同问可带多项 WARN），FAIL 0 行。

## §3 全表机检复核（283 问背景核对，与验收硬数字 [纪要§9] 对表）

- 五要素结构机检：data_sources/exam_plan(criterion+threshold)/consumers/frequency/pit_proof 非空率=283/283=100% ✓；threshold 无"待定/TBD" ✓。
- frequency 枚举命中 7 值枚举 100% ✓（registry.py 同款枚举）；event_driven 事件源引用规则未触发违规。
- 查重：NFKC 归一化标题同层精确重复=0、跨层=0；TPL-U 156 实例 (line,slot) 零重复；62 条 v1 骨架（M4/U6/S12/D8/E7/G5）各恰 1 条 + SL-xx-x1/x2 十线 20 条齐 ✓；GRF 分布 G1:4/G2:3/G3:4/G4:4/G5:3 = 每图 3-5 ✓。
- 一致性：快照 row_count=283 = PG 实测 283 行 ✓（台账 R-4 所记"实插待广播"已过时，实际已落地）；exam_result 表 0 行与全表 status=registered 一致 ✓。

## §4 发现汇总（每条 WARN 给修法；0 条 FAIL）

**F-1（判读合规·系统性，影响 PQ-0063/0069/0075 及全 18 条 L2）**：18 条 GRF 问以 layer=L2 入表，与裁定#400③"W3 遗留：L2 暂无专属问源组，图谱质量问源留后续对话"（台账 R-2 仍在册待 Owner）未收口；其中 PQ-0069/0075 属典型图谱质量问，正中留置类目。另有低危注记：graph_ref 回填槽位号 G1-G5 而非 W5 §6 所写"本表图名"（机读可消歧，仅约定偏差）。
**修法**：呈 Owner 二选一收口——①补裁定追认"GRF 问源挂 L2 合法"（总包令 W6"每图谱 3-5 问"为授权基础，写明其与判读表"L2=0"的关系=判读表辖 62 条 v1、GRF 属新增扩展）；②或 18 条改挂消费层（layer=L3/L4）保留 graph_ref 引用。随口登记 G1-G5↔图名映射或改回图名。

**F-2（字段·B 级条件必填，影响 PQ-0031/0037/0082 及全 20 条 L3、6 条 U 母问）**：10 号件 §2.2 规定 line_ref 为 B 级必填（layer=L1/L3 或声明依赖源线时），但 `registry.py` 只实现 A 级校验、W6 checker 亦未查——数据侧 L3 20/20 全部 line_ref 为空，L1 的 6 条 U 母问为空（母问口径合理但豁免未见登记留痕）。
**修法**：三选一并留痕——①L3 回填正源线（如 S1/S7→SL-A01/SL-A09）+registry.py 增 B 级机检；②裁定 L3 豁免（状态变量由行情表直算，不逐问挂线）并把豁免写回 10 号件；③U 母问登记 line_ref=ALL 语义。

**F-3（消费方登记·系统性，全表 283 问波及）**：consumers 全词表 13 值中 11 个未命中 functional_domain_registry（7 个层名+入库闸/未答看板/模板生成器/E1C三轨）；20 号件 §4#4 称"consumers 真源以 W7 落定为准"但 W7 未落消费方清单。registry.py 如实走 degraded_check 降级（非伪装机检），全库放行依赖裁定#401 初始通道 Max 会签。
**修法**：机生消费方登记册（13 值入册，随 ROOR 衔接）或裁定确认"层名+战役组件"为合法消费方词表；同步消除 20 号件"W7 落定"的悬空指向。

**F-4（证据·源与考法错位，影响 PQ-0011）**：考法需分钟数据而 data_sources 只挂日线；checker 白名单（ALLOWED_SOURCES）同样不含任何分钟表（kline_1min/5min/15min/30min/60min 的 DDL-as-Code 在 `schemas/categories/kline/` 在库）。
**修法**：白名单补分钟表族；PQ-0011 data_sources 增补 kline_30min（或 kline_1min）；全表扫一遍"考法粒度 vs 源粒度"错位（机检可做：title 含 分钟/30 分钟/日内 而 data_sources 无分钟表）。

**F-5（要素 2·证伪力，影响 PQ-0075）**：threshold"重合率收敛（斜率>0 且显著）或登记差异"的"或登记差异"是兜底豁免分支——任意考试结果皆可落"登记差异"通过，违反"能被考试证伪"的本意。
**修法**：threshold 收敛为纯判据（斜率>0 且 p<0.05），"登记差异"移入考试后的处置/挂起分支，不与判定阈值并列。

**F-6（证据合规，影响 PQ-0254）**：data_sources 引用 W4 标"未核实"渠道（Reddit API/X API），与 W4 §6.4"未核实外链复验通过前禁止引用入库"存在张力；缓解项在位（pit_proof 显式"未复验不引生产"、W7 R1 全 B 档路由"建"、台账 R-3 复验在册）。
**修法**：该问 data_sources 改渠道中性引用（如"SL-B06 候选渠道（未复验）"）或增渠道状态标记；R-3 复验通过后回填实名渠道。

**观察注记（不计 WARN）**：PQ-0090 与 PQ-0045 同信号异考法，建议登记查重观察对；PQ-0157"可执行率"、PQ-0224"宣称覆盖"属半主观判据，归 Max 复审必审域（10 号件 §3 本就如此分工）；PQ-0123 同族三窗拆分为预注册设计 [11号件§6]，非一问一考违规。

## §5 结论

**红蓝第 2 轮：发现 6 条（0 FAIL / 6 WARN）。** 抽样 20 行中 11 行五项全 PASS、9 行带 WARN（其中 3 条为系统性：F-1 判读收口、F-2 B 级字段、F-3 消费方登记；3 条为点状：F-4/F-5/F-6）。无一例证据伪造、数据源虚构或五要素结构性缺失——283 问全表机检（五要素结构/frequency 枚举/归一化查重/62 骨架+GRF 分布）100% 通过，快照与 PG 实表 283=283 对账一致。3 条系统性 WARN 均属"已知在册未收口（R-2/R-3）"或"实现落后于自家设计文本"，修法已逐条给出且均可机械验收；建议随 W8 收口批一并呈 Owner 处置后归档。诚实声明：以上 WARN 均给实证出处，PASS 均给可复现核验路径，未放水亦未构陷。

> 验收动作留痕：本件为唯一产出件；未执行任何 git/写库/写表命令；PG 访问仅 information_schema 与 count(*) 只读。
