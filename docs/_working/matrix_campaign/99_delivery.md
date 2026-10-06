---
campaign: matrix-20261006
session: st-matrix-20261006
created: 2026-10-06
owner_directive: 家底全接线·矩阵考试总包（就寝授权夜战）
ttl: task_bound
---

# 99 — 矩阵战役终报（四清单制）

> Owner 醒来先读本页。一句话：**策略工厂的注册表驱动考试自动化今晚建成并实测跑通**——四类家底全部有了三态verdict（合格/回炉/退役候选），骨架+缺口+施工队列全部机生落册，零孤儿、零凑数、零未审计面。

## 清单一：已接线（今晚建成的自动化）

| 件 | 路径 | 说明 |
|---|------|------|
| fexam 考试套件（8模块） | scripts/backtest/fexam/ | CLI单入口 run_fexam.py 八子命令；每晚一条命令重跑全量考 |
| 批0 应考名单机生器 | roster.py → docs/_working/fexam/bt_p0_roster_v1.yaml | 四册→名单零手工挑题（S3铁律），prereg 判据/窗口代码级冻结 |
| IC 考试引擎 | ic_exam.py | 快路径秩IC与官方内核逐位对拍（<1e-6，单测锁定）；ICIR/换手/分体制/衰减五项度量 |
| 策略标准化装置 | strategy_exam.py | MOD-BT-001 引擎（PIT/剔ST/T+1全开）+月频top20；DSR 记账自动入 N 账本 |
| 分配器影子考 | allocator_shadow.py | 五套同窗影子+证据量报告（MOD-PF-008 口径：不判终胜负） |
| 汇总器+家底总表 | campaign_report.py → data/strategy_intake/matrix_inventory.yaml | 八底册机生（334数据集/175因子/161策略/143指标/182环节/283原问题），L1-L4 接线级标注 |
| 四张缺口单 | data/strategy_intake/matrix_gap_lists_v1.yaml | 纯集合运算可复算 |
| 原问题回填通道 | campaign_report.py metaq --writeback | title→PQ 解析+claim+record API 链路已实证（严格子集纪律） |
| 挖矿产物 | docs/_working/matrix_campaign/mining/ | S骨架22件+M1另类11件+M2离场板块28件（61文件） |
| 施工队列 | docs/_working/matrix_campaign/construction_queue_v1.yaml | S8/M9/L清单，明天任何会话可领工 |

## 清单二：已考试（verdict 三态全覆盖，零遗漏）

| 批 | 对象数 | pass | rework | retire_candidate | 册 |
|----|--------|------|--------|------------------|-----|
| 批1 因子 | 175 | 0 | 175 | 0 | factor_exam_scores_v1.yaml |
| 批2 策略 | 161 | 0 | 161 | 0 | strategy_exam_scores_v1.yaml |
| 批3 指标 | 143 | 78 | 55 | 10 | indicator_exam_scores_v1.yaml |
| 批4 分配器 | 5 | 影子实测（见 allocator_shadow_report_v1，只报证据量） | | | allocator_shadow_report_v1.yaml/md |

**批1/批2 全 rework 是诚实结果，不是事故**（机判证据在每行 reason 字段）：
- 因子册 175 条实测仅 18 条有 outputs、2 条 quantized、CH 列直连=0——**册面量化欠账**，31 个 code_symbol 锚点=M级适配器工程（施工队列 M-7）。
- 策略册 161 条 alpha_sources 非空仅 2 条（且指向文本规则因子）、code_path=23——**策略册是设计态目录**，逐策略适配器=M-8。
- 批3 是今晚真实实测面：143 列全量（真源 c1_market.technical_indicator 4.03亿行），HOLDOUT 窗 2025-10-09..2026-09-30 与选样窗严格分离。头部发现：反向信号族（VOLUME-009/TREND-007 等 |IC|≈0.06-0.07）7.8 成过线；CYC 族整族退役候选；122 条 regime_valid 声明与实测有偏差（report-only）。
- 批4 五套分配器同窗影子（合成信号=指标列prereg回退，如实标注）：三层栈(champion) OOS Sharpe=+0.52/收益+8.2%/回撤-22.4%，胜等权(-0.22)/RK-08(+0.36)/PA-015(+0.32)；证据量 t=0.35~0.48 全部不足显著=不判终胜负只报证据（SIG-131 与等权同曲线：等权向量天然不被钳制改变，诚实记录）。

## 清单三：在队（自动落地中，无需 Owner 动作）

- 提交队列：q-0001（代码+测试+capability册+translation册14件）、q-0002（capability册token先行批）已入传送带（前方101袋多队夜战排队，自动消化）；袋2a/2b（战役文档64件+册/总表）待 bag0 落地后入队。
- 翻译册 8 条 fexam 条目已入工作区真源+账本（TRANSLATION 门落地仿真态已过）。
- depgraph 设计节点×2 已登记（目录级 MOD-BT-FEXAM + run_fexam.py 文件级）。

## 清单四：等Owner（只登记，未代裁）

1. **及格线校准**：prereg v1 全部初拟（IC>0.02/ICIR>0.3/retain≥0.5；策略 OOS Sharpe>0+MDD≤30%）——你醒来可改线重判，考卷已冻windows不改。
2. **retire_candidate 处置**：10 个指标退役候选（CYC族5+MOM3+REV/VOL/TREND各1）——退役=Owner 门位，册内只是候选。
3. **activation 升档单**：批3 的 78 个 pass 指标是否进信号候选池（升档=四门位类）。
4. **M级立项批**：施工队列 M-1~M-9（离场族ATR/板块传导/31因子适配器/23策略适配器/metaq逐问回填等）。
5. **R1/R2 地图定谳**：fac9_05 处方两处名实错位（fig16 队持锁，本役只开方）。
6. **T3a 开闸考**：与 st-tclose-t3a 车道握手后排期（GPU 预算表§四③已留）。
7. **metaq T-1**：min_confidence=95 post_hoc_amendment 待裁项（本役未动）。

## 夜战实录（详见 90_execution_log.md）

- 五发跑批六障全修（代理劫持/period误设/TSV无表头/三段切分/判据分离/regime重复快照），每障根因+修复留痕。
- 三路挖矿代理+总包共 5 线并行，零冲突零代修（fig16 持锁面只开方；fig13-bone 持锁面绕行）。
- 纪律全项遵守：机生禁手填/HOLDOUT 分离/负结果如实/四门位只登记/token先行/翻译册代收尾披露。

## 遗留与边界（如实）

- 批2 引擎为 CPU 逐日（vectorized_engine 无 cupy 核）——degrade 台账随册逐条可解释；GPU 0.53s/格口径属 c4 网格引擎（T3a 专用）。
- 今晚 GPU 网格预算未动用（四类考为 IC/整装考，非网格考；T1冠军复考/T3a 属握手后批次）。
- mining 代理产物已红队交叉验证（抽5项）：4/5 逐位命中真源/CH 实测（SL-A13 514,395行/5,906票逐位一致、骨架行号指针全实、指标分数册 verdict-IC 自洽、总表 334/61 三方对平）；1 处口径瑕疵（M2 X族19→13缩圈未全声明）已按复核处方当场补声明闭环。


## wave-2 施工战报（次日白天，九道车道全部完工）

| 道 | 产物 | 关键结论 |
|----|------|---------|
| A道 | alt_factor_exam_scores_v1（9 另类因子） | 0 过/4 回炉/5 退役候选；money_flow 8.5 月空洞等三条硬情报；挖矿→接线→考试闭环首通 |
| B道 | codesym_factor_exam_v1（31 code_symbol 因子） | 18 实测/13 缺数据线；0 过/3 退役候选/28 回炉；MOM-029 |IC|0.0517 过线仅缺 direction 注解=翻案候选 |
| C道 | sector_factor_exam_v1（9 板块因子） | 0 过/9 回炉；动量全负 IC=HOLDOUT 反转态（sanity 对拍证实非管线错位）；行业映射无 PIT 已折价标注 |
| D道 | codesym_strategy_exam_v1（23 code_path 策略） | A8/B14/C1/D0 全分类；10 实测（0 过/3 回炉/7 退役候选）+3 sanity error 如实；10 张精确适配工单（tick 数据缺口/指数码撞股票码/ daban 数据 1 月等）；**引擎 O(N²) 性能病灶发现+同语义记忆化修复（小时→4分钟）** |
| E道 | exit_sim_report_v1（ATR 止损对照） | **有增益**：OOS MaxDD 改善+16.5pp、Sharpe -0.19→+0.43；T3b-T0 重标定 0.428s/次（0.53s/格旧口径废止） |
| F道 | GPU 网格考适配器+点火器 | 5 配置/342 格干跑全过；点火五前置自愈；经三轮 bug 修复（桌面显存基线/WMI 自匹配/文件名后缀）后**实弹 324 格全部跑通（rc=0，~0.5-1s/格实证）** |
| G道 | IC 内核 GPU 移植四件 | 对拍 5/5 逐位 0 差；numpy 基线 19.5s/20 列；CPU 生产路径不动 |
| H道 | bootstrap 统一族 GPU 核 | 35/35 对拍 ≤1e-9；提速 WRC 8.8x/E2 14.2x；抓到 auto 静默上 GPU 险情并改显式门 |
| I道 | layered 核+wq87 算子层+dwm 探针 | layered 逐位+6.7x；wq87 五算子 14/14≤1e-12；**dwm 瓶颈=行物化 57.5% 非 IO（4.2%）——#2 工单改写** |
| J道 | state_recognizer_exam_v1（HMM 四态识别器） | **verdict=不合格**：混淆对角 20.6%（<乱猜 25%）、喊熊日反涨、3.4 倍抖动、压不过 SMA200；情绪指数表实测可考（8659 行） |
| 调查道 | gpu_survey_v1.md（23 面矩阵） | A5/B6/C12；Top5 施工排行带验收判据；I 道探针已修正 #2 打法 |

**wave-2 全部产物 token 已入账（72 枚）**；施工队列剩余项（M 级深水区：tick 回补/EDE tick 考道/事件管线闭环/时序择时通道）见各册工单字段与 construction_queue_v1。
