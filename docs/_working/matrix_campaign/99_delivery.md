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


## wave-2.5 十道战报（裁定执行夜）

| 道 | 产物 | 结论 |
|----|------|------|
| K道 | 16 件 tmp 抢救转正（bootstrap_gpu/gpu_ic/exit_sim/grid_adapter 四包） | 字节级一致+py_compile 15/15 绿；token 15+翻译 16+depgraph 待收 |
| M道 | 指标链向量化影子（438/438 列逐位） | 物化段 25-42x、全路径 1.9-2.3x；生产切挂=30 行改点（日光档+夜窗双跑） |
| N道 | MOM-029 假设补全+prereg v2+重考 | **回炉→合格转化首例**（假设事前/direction=short/四线全过/registry 3 行注解） |
| O道 | 情绪指数首考 | **不合格**（0/3 过；同步量无 5 日前瞻；PIT 干净但需 append-only 快照重考） |
| P道 | bootstrap×3+layered 核接线 | 进行中 |
| Q道 | 原问题机解回填 | **首批 3 件真实回填**（PQ-0126/0127 fail、PQ-0205 pass）；33 问留痕升级 |
| R道 | 324 格 OOS 分析 | 0 过（发现 F 道配置只跑了 OOS 窗=我的锅）；42 格 OOS 全正待 IS 补考；halflife60 族最亮；DSR 防双计 |
| S道 | direction 全册勘察 | 19 条空标签连片缺口；17 可客观推导/2 等 Owner；翻案候选唯 MOM-029 |
| T道 | HMM 重训回炉 | **仍不合格但大幅改善**（对角+72.9pp/抖动减半/标签置换消除）；生产不替换，SMA200 默认二次验证 |
| 数据申请 | data_requests_v1.yaml（DR-1~4） | 提交数据班：解锁 13 因子+5 策略+1 因子重考 |

**新增裁定执行记录**：paper 池 78 只落册；SMA200 默认帘子切换（HMM use_hmm=True 仅研究用）；MOM-029 注解 3 行。


## st-mx07 夜战端到端交付增补（2026-10-07/08，总包=st-mx07-chief）

第一波 12 车道 + 第二波 6 车道 + 总包回收 2 件 + 循环检查×2 + 红蓝对抗。测试面 257 用例 252 绿（5 红为 HEAD 预存豁免面 test_factory_grid_stage_cost_tiers，零本战役引入）；ruff 触达 182 件全清；全部成果经 GitCommitGateway 落 HEAD，零裸 commit。

### 第一波（裁定#489 与 backlog 可开工项）

| 道 | commit | 结论 |
|----|--------|------|
| L1 经典指标调查 | 469219b03f | 6 退役指标三选一：AC/MACD背离/CHOP=考法错；Squeeze/WAD=实现有错（修复处方在册）；HighPass3=等价维持退役。移交 3 施工单（blockers 在册） |
| L2 SMA200 默认帘子 | 576ba62650 | regime_series 默认 sma200_default、HMM 显式 opt-in；tests/backtest/fexam 26/26 绿+真 CH 冒烟 |
| L3 bootstrap 核接线 | a92886e31d/61543354d7/dd98757ab4 | 核迁 src/zephyr/backtest/accel/，WRC/E2/CORR 三处换核；同 idx 对拍 35/35 ≤1e-9；wiring 13 测+e2 16 测绿 |
| L4 layered spread 接线 | e5118cd455/e6cbed3c5d/7e6f66d055 | compute_layer_spread 委托核（use_kernel 默认 True，pandas 后备保留）；38 测绿；基准册留档 |
| L5 指标链向量化 | e3e32b7fed/62cfdff658/fd4578561d/a7f7c2b6f4 | 转正+生产切挂（provider→build_rows_vectorized）；对拍 438/438 \|Δ\|≤1e-9（红队复跑复现）；物化段 30.4x/31.6x；影子退役净零 |
| L6 HMM v3 设计卡 | 04eed40b22 | SOTA 全网调研+v3 三处外科设计+超参冻结一次窗口；判据冻结不可挪 |
| L7 MOM-029 direction | chief 代寄袋（原分支 32c063db6a） | direction=short+回炉 evidence+paper_pool_candidate 注记；+4/-2 与分支后像逐块相等校验 |
| L8 情绪快照+首考 | 783015e28b | append-only 快照器+首考修复前瞻缺陷；verdict=有条件合格（IC=-0.1905/ICIR=1.16/retain=5.94 三线过，负向）；投产前置=日批运维化（blockers） |
| L9 DR 申请包定稿 | 3f93955c7a | DR-1~4 窗口到日+验收判据+解锁对账（10 因子+6 策略+1 重考，13/5 原口径勘误留档在册）；待 Owner 转数据班 |
| L10 CYC 预注册卡 | dfcc8ec954 | 四指标分层判据+Bonferroni 族 N_fam 冻结+一次窗口；判死动作=registry retired |
| L11 进池判据门 | 9785cb6f23 | paper_pool_gate 三线 AND+聚合层 Bonferroni/DSR（SSOT 委托）；24 测合成真值绿；接线 campaign_report |
| L12 R1/R2 调档 | chief 重投袋 | 定谳：错位本体已治本（#484③+fac9_04）；#489⑥ 实为销账批，F1-F5 全 S 级呈批（blockers） |

### 第二波（前置解锁）

| 道 | commit | 结论 |
|----|--------|------|
| W1 t0_material_line 并行 | df854ec406+037ecabc3a | 建模 21.4h→≈53min（x54.3 实测）；对拍逐位 0 FAIL/20（+5 对 Decimal 语义缝如实披露）；单点切挂+回滚口径；GPU 二期与 CH 取数 IO 瓶颈遗留 |
| W2 HMM v3 施工+跑数 | c724894154 | 一次窗口 verdict=conditionally_qualified（①②③过；④滞后 med=10>5、⑤①分量 0.552<0.613 不过）→按裁定#489② **HMM 体制识别方向永久退役**；判死四动作已执行 |
| W3 CYC 考场跑数 | dfcc8ec954/229504a84c/f098af4148/4faf0517e8 | 一次窗口 family=fail，四指标全不过 Bonferroni→registry CYC-001/002/004/005 retired+evidence；解盲前 freeze 证据已抢救归档 |
| W4 离场族 12 节点 | 26a5f4a969（YELLOW） | 规格前置 B1-B5 缺失/证据冲突（E 道增益 vs T3b FAIL 两考卷）→prereg 草稿呈批、未跑数（宁缺毋假）；开考等 Owner 一次裁定 |
| W5 板块四路+传导接线 | 278f283636c | sector_surface 四路强度面板+conduction 三档 gate+schema 折叠维 X_sector；14/14 绿+真数 smoke |
| W6 wq_alpha_87 接线 | a7d9f91950 | FactorRegistry 入册+考试链 panel 截面协议；14+54 绿；capability 册经 ledger 意图 API+publish_snapshot v103 正道落地 |

### 质量门与红蓝

- 循环检查 R1：3 findings（r1r2 一页纸未落库=袋 B 承接；CAS 孤儿临时件=已清；预存红计数 7→5 勘误=已登记）。257 用例复验全绿零回退。
- 红队 11 findings（P0=0）：对拍四面攻不破（L5 复跑 438/438 复现、L3 同索引注入属实、L4 后备可达、W1 披露诚实）；PIT 五件无前视（L8 t+1 forward、W3 freeze 先于解盲、L2 同日特征、W2 滤波因果、L11 冻结常量）；门禁面无绕过。**P1=1**：W3 主批携带的他班在途退役批物理删 15 条 TREND/MOM（5 条 verdict=pass）无裁定授权→呈 Owner 核定（blockers 在册，不代修）。
- 已知热册风险：capability 册=PG 投影，手插条目会被 render 洗——本战役 matrix-l12 双 token 等经 ledger 重登记固化（blockers 在册）。

### 遗留移交（Owner/维护班/数据班）

1. RD P1-1 15 条删除授权链核定；2. W4 离场族 B1-B5 裁定后照草稿冻卡施工；3. W2 HMM 判死知会确认；4. L9 DR-1~4 转数据班；5. L8 快照器日批运维化；6. L1 三施工单；7. 队列工程债（ghost_session 家族/belt 活锁/心跳 Windows 存活率/T11 参数勘误）；8. W1 GPU 二期+CH 取数 IO；9. L12 F1-F5 销账批。全目见 dispatch_blockers.md。
