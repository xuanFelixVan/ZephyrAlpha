---
ttl: task_bound
title: 全项目六轴深度审查+施工战役晨报（终版 v1.0）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 晨报（终版）：全项目六轴深度审查+施工战役 2026-09-18 通宵班

> 进度真源=`01_master_ledger.csv`（235 行×六轴×状态）；全部审查报告在 `docs/_working/deep_review_full/`（p0_money_path 38 簿 / p1_decision_chain 91 簿 / p2_infra 45 簿 + 总控三件 + 本晨报）。

## 0. 一段话总结

**235 个审查对象全部完成六轴深度审查**（P0 钱路径 38 含双角色隔离对拍、P1 决策链 137、P2 基建+自动化任务族 45、TDM 全图对账 1），**确认缺陷 25 项全部治本**（每项：独立复现→修复→回归测试→套件复检绿→GitCommitGateway 队列落地），**挂起登记 19 条主题裁定项**（#ARCH-338..#ARCH-356，safe_write CAS 原子批），循环检查 R1 全域 6971 测试通过且 11 红全部分诊归位（R2 终跑见 §4）。战役级头号系统性发现：**TDM 决策地图与代码现实大面积脱节**（补册域孤儿 41/76、module_ref 语义错位成批——图上"已建"、码上"缺位/错位"）。

## 1. Owner 必读（按紧急度）

### 今日实盘相关
1. **X08 券商文件桥双键错配已治本**（全场唯一审查期 P0）：原状=指令写 idempotency_key、本地配对全用 order_id，实盘上线即状态推进/成交配对/撤单三链全断。已修复+三回归。**请用真柜台 CSV 复核 EXEC v16.4 解析口径（报告有遗留验证法）**。
2. **TF07 daban 名义 DAG 边**：daban_engine_load_daily（日频消费 T-1 事件）依赖 daban_board_event_derive（周一 03:00 周频生产），跨时段边被 task_queue 自动视为满足——**周二至周五引擎装载的是上周事件**。挂起 #ARCH-338 批（TF 退路与名义 DAG 条目），建议今天收盘后裁定 derive 频率。
3. **TF01/02/10 miniQMT 退役退路**：9/18 退役命中 24 任务无可用退路（tick_data_snapshot 的 bdpan fallback 未注册=死 fallback；ex_dividend_event 是 stk_limit 公式法唯一输入）。挂起登记，需数据线落地退役映射表。
4. **测试封闭化**：文件桥测试默认端口 18901 会打真 EXEC（今日实盘在监听）——已改 http_port=None 封闭。**风险提示：任何测试/工具构造 QmtFileBridgeBroker 不显式禁 HTTP 都可能误发实单**。

### 监管/资金安全裁定项（不裁不动）
5. **K08 先报告后交易闸从未武装**：闸码完整测试全绿，但 report_gate 全仓零注入+broker_ack 0/6——C-002 红线未生效。武装前置=券商 ack 数据流（0 ack 下武装=全拒单）。
6. **I26/T06 面板 API 无鉴权+CORS 全源**：`/api/promotion-decide`（Owner 门位）可被浏览器任意网页 drive-by 调用（本机绑定但网页可打 localhost）；持仓数据可被任意网页读取。修复=token 鉴权+收 CORS（需与前端联动）。
7. **K02 资金事故假处置**：kill switch 的 funds 事件翻旗无下单路径消费；系统级开关纯内存重启即丢。
8. **pf_alloc 整域**：7 件仅 W03 真接线；C04 veto 路径接线即 P0（账目脱节实测）；W05 模式开关无效。整域接线/退役裁决（#ARCH-338 批）。
9. **Regime 断供即满部署三腿**（D01/D05/D12）+**Wyckoff 证伪旁路**（D09/D11）——fallback 语义裁定。

### 数据/告警基建
10. **告警无推送通道**：飞书/SMTP 裁撤后告警=日志+json+前端页纯被动；health 失败路径无 notify（最坏 14h 才被 23:00 对账兜住）。挂起登记待重建裁定。

## 2. 治本清单（25 项，全部带回归）

| # | 对象 | 缺陷（严重级） | 修法 |
|---|---|---|---|
| 1 | X08 | 券商文件桥双键错配（**P0**） | 双键配对视图+撤单 remark 解析+Fill 回解 |
| 2 | V02 | 闸C 基线回退翻转认证态（P2 机验） | `__pooled__` 键恒同步真实池化基线 |
| 3 | V03 | FDR NaN 静默出"貌似合理错数" | NaN/Inf/越界 raise |
| 4 | V04 | 台账缺读数静默缩分母（DSR 放水向） | 缺 n_trials raise fail-closed |
| 5 | V05 | WFA 灾难否决缺字段旁路 | 缺 dd 窗口强制未通过（测试契约同步收紧） |
| 6 | V06 | `%.0%%` 非法格式串 | `%.0f%%` |
| 7 | V01 | Wilson 越界 rate 复数 TypeError/NaN 静默 0 | [0,1] 校验 |
| 8 | X01 | rebalance 不抵扣在途单（重复触发双下单） | 同侧在途抵扣+OM 异常降级留痕 |
| 9 | K05 | VaR portfolio_value NaN 穿透 | isfinite raise |
| 10 | B01 | **T+1 tick 级被绕过**（datetime 全等比较） | 日历日归一化比较 |
| 11 | B06 | tick 合并并列排序不稳定 | kind=stable |
| 12 | D03 | NaN 合成 VIX 静默判"平静" | 域检查+degraded 留痕 |
| 13 | D04 | NaN 分布穿透 Fail-Closed | 校验补 NaN/Inf 拒绝 |
| 14 | W07 | NaN 回撤判 NORMAL 满配 | dd/base_weight 双 NaN 拒收 |
| 15 | B11 | ADV 缺失→冲击腿 55× 虚高（生产 artifact 污染） | 分母退化层代表 ADV（对拍 199.7→3.63bp） |
| 16 | S05 | 市场九宫格 60 样本差一崩溃 | 门槛=max(min_history, long_window+1) |
| 17 | S06 | 全零量停牌股 NaN 弱标签 | 零成交中性降级+留痕 |
| 18 | S10 | 全平序列假卖出 75.2 置信 | RSI 平坦中性+四族等值三态化 |
| 19 | M03 | window=0 静默全量截断 | config 四防校验 |
| 20 | M04 | CP-VaR 双侧 target 对单侧破位（2× 欠覆盖显示为优） | target=(1−coverage)/2+测试契约收紧 |
| 21 | I15 | 一致预期探针 2027 时间炸弹 | max(forecast_year≤当年) 跨年自愈 |
| 22 | E03 | 止损降级锚 entry→盈利期悬崖 | 锚点同构 max(最高收盘,entry)（#309 挂起族内矫正） |
| 23 | E05 | 跌破止损线误判 MONITOR | 破位即 WATCH |
| 24 | P12 | 相对强度因子 abs() 方向反转（弱板块进推送池） | 去 abs 保符号 |
| 25 | TF15 | schedule:disabled 不识别→停用任务永久假红 | 应跑筛选补 disabled |

**反驳者对拍**（P0 双角色单轮）：8 个数学对象核心公式零"公式写错"级缺陷——DSR/Wilson/四闸/FDR/n_eff/Kelly/VolTarget 独立复算全部一致；成立的反例全在路径语义与边界（已修 5，挂 2 随 pf_alloc 域裁定）。

## 3. 挂起登记（#ARCH-338..#ARCH-356，19 条主题裁定项）

执行域孤儿族｜风控孤儿闸族｜K02 资金事故假处置｜K08 监管闸武装｜对账链双零接线｜pf_alloc 整域｜Regime 断供三腿｜Wyckoff 旁路｜embargo 双承载｜策略管线三洞（T02/T05/T06）｜卖出族族内对账｜信号域接线期地雷｜数据基建三洞（I03/I08/I09）｜TF 退路与名义 DAG｜告警无推送｜F02 回炉 FSM+G01 stub｜预测域 NaN｜X05 笼子 quote 源｜轴F 立卡 8 项（K02 持久化/K05 min_history/B08 purge-embargo/W05 真 ERC/频率感知年化/Hungarian 匹配/ATM 方差互换/TA-Lib 对拍）。

每条带报告锚点+裁定选项；**补册域（P01-P76）另呈"接线期地雷图"**：孤儿 41/76、机验实锤 15 处（P31 n=6 必炸、P33/P35/P37 NaN 链、P43 置信退化、P48 取整偏差、P49 双 codegen 错位、P54 伪扇区砍仓、P62 KEPT 隐身等）——接线时逐件矫治，未接线无现行损失。

## 4. 循环检查与红蓝

- **R1（全域）**：6971 passed；11 红全部分诊——8 红他会话 crisis_gate 在途前瞻规格（非本线）、1 红外来 crisis 级联（已移交车道作者）、1 红 alert_generator flaky（复跑过）、1 红我方文件桥测试不封闭（已修，18/18）。
- **R2（终跑）**：**7055 passed / 10 failed**——红全部外来归属（8=他会话 crisis_gate 在途前瞻规格、1=外来 crisis 级联已移交、1=alert_generator flaky）；**本线 25 项修复两轮稳定零回归**，R1 的文件桥 flake 已被封闭化修复消掉（11→10）。metamorphic 不变式 73/73。
- **红蓝检出率门**（裁定#324）：9/10——失败项=报告生成器空结果（0 vs ≥9），归属 rule 车道（本战役未触 rule 域），如实登记不移交修复。
- 门禁演进全程适应：R5-DIGIT-SUFFIX（目录改名）、EXEMPT-ZONE-FM（238 文件剥 doc_type）、CREATE-GUARD（token 随批）、ALGO-NOTE-SYNC（四节点大白话跟改+note_confirmed）、ARCH-REFERENCE（登记先落）、REGISTRY-MASS-DELETION（放弃整写改文本式追加——整写手法已自纠，±2.5 万行重排版未入历史）。

## 5. 提交账单与遗留

- 队列正门累计 **39+ 笔**；源码修复 15 文件、测试适配 6 文件、战役文档 240 件、挂起登记 19 条全部落地或消化中；死信 13 笔均为门禁演进中被合规批取代的旧快照（零内容丢失，清单在案）。
- 共享暂存吸收声明：注册表批按"registry 竞态三步"配方随批携带共享 token 载体（capability_canonical_file_registry.yaml 纯增 4 行+他会话 token 同批落袋）。
- 本会话 claim 将在收尾全部 release；.runtime/tmp 探针脚本按 TTL 自清。
- **无遗留待办未登记**：所有未施工发现均已入 #ARCH-338..356 或台账挂起列；无待裁定内容未列明（§1 十项即全部）。

## 6. 收尾后记（2026-09-18 晚追加）：189 件报告的落地面

- **事实**：189 件战役报告处于 staged 保护态，其中 **145 件含未落地内容**（各波审查者的完整报告正文+§7 收口节——落地批的队列快照早于报告重写，落的是脚手架版；44 件为纯 stale add 内容已落地）。
- **三重保护**：①工作区最终态；②git index blob（对象库已固化「已审」版，240 件在册，gc 不可达剪枝不触及 index 引用）；③队列死信快照袋 15 袋（q-0042/0043 等）。
- **落地面阻塞点（精确）**：直连与队列双通道被 N-5 共享暂存区脏件连坐——`scripts/backtest/crisis_drill_monthly.py`（N-5 清单 317 staged 之一）BLUEPRINT 头非法（module_id 未用 MOD-/SH- 前缀），卡锁内 BLUEPRINT 门禁，全仓所有会话的 commit 一并被拦；队列序列化器另现基线分叉（NOTHING_TO_COMMIT 快照未真应用，防线已自动死信回退）。**该件属 N-5 登记（待 Owner/Max 定夺恢复 or 废弃）范围，本战役未代修未动其 index 态。**
- **恢复指令（N-5 处置后执行）**：`git add docs/_working/deep_review_full/` 后按 p0/p2、p1、tdm_supplement 三批 `git_commit.py --files ... --allow-non-worktree --allow-overlap --enqueue` 即全量归位；或任何会话修复该外来件头注释后本批自动可落。
