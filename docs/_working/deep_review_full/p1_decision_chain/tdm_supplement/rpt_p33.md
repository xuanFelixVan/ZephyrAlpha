---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——波段池5分制
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：波段池5分制（P33）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/quant_short_term_strength_engine.py`
- TDM 节点: TDM-E-L3-03-2（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；节点名"波段池5分制"与文件实为"6 维百分制强度评分"——名实差距见 §5
- 生产调用方: **有：`pf_core/strategies/daban_sleeve_strategy.py:67-68,407`（打板 sleeve 构造注入即本引擎）+ dual_engine_fusion_decision_engine（:33 声明融合对面）——非孤儿**
- 测试文件: `tests/signal_ashare/test_quant_short_term_strength_engine.py`（49 用例，本班次实跑 49/49 绿）

## 1 对象快照

520 行评分引擎（MOD-SIG-034/D-SIGNAL-34）：6 维评分（动量 Z 20 分/行业 15/相对强度 20/资金 15/技术 20/风险 10 反向，合计恰 100）+A~E 单调评级+6 类输出分类（主升龙头/二进三/跟风/复苏/伪强/地天反包/中性），阈值全配置化（QuantStrengthConfig frozen）。降级路径有日志+is_degraded 标志（:510-520 符合 INVARIANTS:8）。测试覆盖：六维边界/评级单调/分类分支。排除项：游资引擎 D-SIGNAL-33 与融合引擎未审（非本件）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：六维分段查表+线性衰减（低于 fair 档 `max(8+(z-fair)×4,0)` 等）分段单调无跳变反转；权重和 20+15+20+15+20+10=100 与 min(sum,100) 截断自洽（:272）；评级单调映射（:434-445） | quant_short_term_strength_engine.py:272,294-428,434-445 | 通过 | 逐维边界值手算 |
| A 深度 | **边界②实锤：NaN 全链穿透——`_validate_input` 用范围比较（NaN 比较 False 全滑过 :498-508），实测 NaN 输入产出 total_score=nan/grade=E/category=中性/is_degraded=False**（E 评级+正常态=最误导组合，下游无法与"真实极弱"区分）；上游任意一维 NaN 即毒化总分 | :498-508 | P2 | 本班次实测：`analyze(QuantStrengthInput(momentum_z_score=float('nan'),...))` → total=nan |
| A 深度 | A 股口径③：**涨停/连板判定不分区板块——`stock_change_pct>=9.5` 恒定阈值（:469）对 20cm（科创/创业）与 30cm（北证）股票误判：非涨停日涨 9.5%+ 即可触发"地天反包"分类；"二进三"连板计数语义同患**（未传 board/tier 进引擎） | :469,477 | P2 | 构造 20cm 股 +12% 非涨停日观察 INVERSE_BOARD |
| A 深度 | 资金维④：ratio=净流入/流通市值（:369）量纲正确；float_market_cap<=0 → 0 分守门（:366-367）防除零——该维有防御，与 NaN 洞形成对照 | :366-369 | 通过 | — |
| B 上游 | checklist #6 断供：输入全为注入标量（上游算好后喂入），断供语义在调用方；youzi_emotion_score 默认 50/连板默认 0（:185-186）——**缺数据时默认值=中性偏上（50 分游资情绪）参与分类**，缺数据≠中性处理（S08 五维默认值同族案） | :165-188 | P3 | 不传 youzi 观察分类偏移 |
| C 下游 | 消费方=daban_sleeve_strategy:407（真实构造）+dual_engine_fusion；NaN 总分沿 sleeve 选股权重面板传导→选股清单污染（P37 审查面）；爆炸半径=打板 sleeve 单策略选股 | daban_sleeve_strategy.py:407 | P2(同 NaN 案) | 看 P37 报告交叉 |
| D 旁系 | checklist #4 双承载：6 维评分与 sector_strength_aggregator（S02）/P27 五维持续分同族不同物（个股强度 vs 板块持续性），无同式两算；"9.5% 涨停"判定在 limit_up 族另有实现——涨停判定口径多点位承载（本件 :469 内联硬编码 vs limit_up 家族专用引擎），接线对账时统一 | :469 | P3 | grep `9.5` src/zephyr/signal_ashare/ 对照涨停判定点 |
| E 对抗 | 五问：①静默失败=NaN 穿透即静默失败实锤（grade=E 伪装成正常输出）②假阳性=20cm 股地天反包误分类（A 股口径案）③断了没人知道=降级路径有日志合规④重触发幂等⑤时序=N/A（无时序状态） | :240,498-508 | P2(同上) | — |
| F 新鲜度 | 评分卡（scorecard）+规则分段映射为多因子合成常规做法，与本项目 multifactor_synthesis（P38）方法论同族；无学术前沿对照面（启发式评分卡非统计估计量）=**对等已有（方法论常规）** | 对等结论；对照检索见 rpt_p38 F 轴（multifactor family） | 通过 | — |

## 3 SOTA 对照

- 对等已有：分段评分卡+集成分类为业界量化短线选股常规工程做法，无偏差。
- 立卡候选：涨停判定接 board 感知（10/20/30cm）——与 P37/X04 LOT_SIZE 科创板同族 A 股口径债，建议接线期统一涨跌幅规则表（与 P32 立卡项同源）。
- 驳回：无。

## 4 缺陷清单

1. P2：**NaN 穿透产 total_score=nan 且伪装正常态（grade=E，is_degraded=False）**——建议 `_validate_input` 补 `math.isfinite` 五连检（momentum/sector/stock/market/capital）对齐 K05 治法；验证法=本报告 §2 A 轴实测一行。
2. P2：涨停判定 9.5% 恒定阈值不分区板块（地天反包/二进三两分类受染）——建议输入补 board 字段或阈值表化；验证法=20cm 股 +12% 输入观察分类。
3. P3：youzi_emotion_score 缺数据默认 50 参与分类（缺数据非中性）；P3：ERROR_CONTRACT 头注为空（:13）契约缺位；P3：9.5 阈值内联硬编码与 limit_up 族口径承载点多点漂移风险。

## 5 挂起疑问

- TDM 节点名"波段池5分制"vs 本件"6 维百分制（0-100）"名实差距——建议收口方核对 TDM-E-L3-03-2 的 module_ref 是否应指向本文件或另有 5 分制承载件（未在 signal_ashare 包内 grep 到"5 分制"实现）。

## 6 完备性自评

六轴全查。长尾：①dual_engine_fusion_decision_engine 的权重融合面未审（非本件范围）②阈值默认值出处文档（D:\临时工作区\...md:38 外部路径引用已不可达——出处锚点失效，P3 级文档债未列正式发现）③49 测试用例无 NaN/20cm 边界 case=测试缺口。

## 7 收口裁定（收口方填）
