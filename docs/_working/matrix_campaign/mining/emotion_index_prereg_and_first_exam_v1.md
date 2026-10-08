---
ttl: task_bound
---

creation_token: matrix-campaign-emotion-index-prereg-and-first-exam-v1-20261007
lane: st-mx07-L8（矩阵战役 2026-10-07 夜战 L8｜P1-5 情绪指数快照+联动首考）| 及格线授权: 裁定#489③（IC>0.02/ICIR>0.3/retain≥0.5 冻结 v1）
日期: 2026-10-08 | 性质: 预注册设计卡+首考 verdict（prereg 冻结块先落盘、后开跑；开跑前①②③全部盲）
持久化说明: 本区（docs/_working，临时区）门禁强制 ttl=task_bound（FILE-PLACEMENT-TTL 禁 permanent）；车道卡"# [TTL] permanent"意图经交付 promote 流程落地——联动过线随投产前置件 promote 转永久区
证据基线:
  - 上考: docs/_working/fexam/emotion_index_exam_v1.yaml（2026-10-07，O 道，0/3 不合格）
  - 及格线真源: docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml 裁定#489【③及格线 v1】
  - 考试框架真源: scripts/backtest/fexam/ic_exam.py + roster.py（PREREG_V1 判据常量）+ ch_data.py（冻结窗）
  - 快照器: scripts/data/emotion_index_snapshot.py（本夜上线）

---

## 0. 一页结论

**verdict = 有条件合格**（prereg v2 冻结口径：三线全过 + PIT conditional_clean）。情绪指数水位 e(t)
对 000300 自 t+1 起 5 日收益（零重叠主标签 fwd5_off）呈**稳定负向预测力**：HOLDOUT
IC=-0.1905/ICIR=-1.1575、IS_REF IC=-0.0321、retain=5.94，三线全过（|IC| 0.1905>0.02、
|ICIR| 1.16>0.3、retain 5.94≥0.5）；两窗同号无变号。全窗 2005-2026（261 个月桶）
IC=-0.1710/ICIR=-0.7942 同向印证。方向=**反向**（情绪高点后短期收益走低），与上考"高情绪后不跌"
结论相反——上考考的是极值带胜率与 Δemo5 变化量，本考考的是水位-零重叠前瞻收益，对象不同不矛盾。
PIT=conditional_clean（a/b/c 零违例；e=无逐日留痕结构瑕疵，快照器本夜上线后增量留痕开始）。
投产前置（冻结规则原文）：逐日 append-only 快照持续+只追加读径；replay 重跑须留版本。

## 1. 上考败因与本卡修复（冻结节前已知事实）

上考（emotion_index_exam_v1，2026-10-07，考窗 2019-04-01..2026-08-31）0/3 不合格：

| # | 上考论文 | 结果 | 败因解剖 |
|---|---------|------|---------|
| ① | 高情绪（e≥0.90）反向择时 | FAIL | 高情绪后大盘不跌反略涨（p_neg 0.47/0.45 反低于基线），反向不成立、顺向亦不足 55% |
| ② | Δemo5 对 fwd5 相关 | FAIL | 前瞻相关 0.0212≈0，**同期相关 0.3209**——情绪是当期同步量（由涨跌家数/成交构成），对同窗起算的 fwd5 无增量前瞻 |
| ③ | 情绪档体制增益 | FAIL | d_bull=+0.017/d_bear=-0.016 跨体制变号，无稳定方向性 |

本卡修复（车道卡指令原文：**"情绪态用 t 日信息、forward 收益用 t+1 起 5 日，严禁重蹈同步量无前瞻"**）：
主标签改 **fwd5_off(t) = close(t+5)/close(t+1) − 1**（000300 收盘，收益窗=t+1..t+5 共 5 个交易日，
**与 t 日信号信息零重叠**）；上考旧口径 fwd5_old=close(t+5)/close(t)−1 降为 report-only 敏感性对照。
判定口径整体切换裁定#489③ v1 三线（IC/ICIR/retain AND），废除上考的 55% 胜率/带宽对比面。

## 2. prereg v2 冻结块（2026-10-08 开跑前落盘；判据事前定，禁看分改）

> 冻结纪律：本块落盘时，本考全部 IC/ICIR/retain 均未计算（①②③盲）。冻结节前已知=下文
> 如实标注的行数/覆盖事实、上考公开结果、快照器首件落盘台账，不含任何本次联动读数。

### 2.1 数据面（节前已知事实，开跑只读不改）

- 信号: `c1_market.emotion_index`（表名经 TableRegistry `market_emotion_index` 派生，禁硬编码），
  series = stage='close_final' AND version='v0.1.0'，e(t)=emotion_index（0-1 灰度分位，0=冰点 1=沸点）。
  读径=ch_reader 严格通道（FINAL 自动注入，每 (trade_date,stage) 键唯一，代码内断言 fail-visible）。
  节前已知: close_final 全表 8617 行（1991-06-10..2026-09-30）；全表三 stage 合计 8659 行、
  FINAL 去重后 8658 行（pre_open 2026-10-02 双行异值合并=表级可改写实证，v1 PIT-e 原判）。
- 代理: `c1_market.kline_index` symbol='000300' 收盘价（节前已知 5282 行，2005-01-04..2026-09-30）。
- 考窗: 代理可得窗 ∩ 信号可得窗 = **2005-01-04..2026-09-30**（上考 2019 起窗是 SMA200 预热需求，
  本卡废除体制门不再需要；考窗起点由数据可得性决定，事前冻结）。考窗内信号×代理日历对齐数开跑后如实报 n。
- append-only 快照基线: scripts/data/emotion_index_snapshot.py 首件已落盘
  data/emotion_index_snapshots/emotion_index_20261007T195219Z.jsonl.gz
  （sha256=cbc608c49bb4d1bfcca27e5887570af91d9797842b1dd9acce24942b42a2376e，8658 行）——
  此为 PIT-e 缺陷的修复起点；历史（≤2026-10-07）仍无逐日快照留痕，本考 e 项据此如实判。

### 2.2 标签（修复面，事前冻结）

- **主标签 fwd5_off(t) = close(t+5)/close(t+1) − 1**：t 日 close_final 于当日 15:10 落库可知，
  收益窗自 t+1 收盘起至 t+5 收盘止——信号日信息与收益窗零重叠（"同步量无前瞻"缺陷的治本定义）。
- 敏感性（report-only，不进判定）: fwd5_old=close(t+5)/close(t)−1（上考旧口径对照）；
  fwd5_leg5=close(t+6)/close(t+1)−1（t+1 起完整 5 条收益腿）；同期相关 corr(e(t), close(t)/close(t−1)−1)
  （同步性存档读数，预期高正值，只记录不判）。
- 尾部越窗: t 使 t+5（或 t+6）超出 2026-09-30 → 标签 NaN 剔除，如实报 n。

### 2.3 IC 构造（单序列时序考，事前冻结）

信号序列每日一个值，无截面，IC 采用**月度桶内 Spearman**：

- 桶 = 自然月；IC_m = spearman({e(t)}, {fwd5_off(t)}) 桶内全部有效对（有效对 <10 → 该月 NaN）；
- 窗归属按**信号日 t** 落窗（标签可伸入下一窗价格，属前向收益定义本身，非信息泄露；桶不跨窗）；
- 窗 IC = 窗内月度 IC 序列均值（NaN 跳过）；ICIR = 均值/std(ddof=0)；窗内有效月桶 <6 → 该窗判 n/a（如实报，判不达）。

### 2.4 窗与判定（冻结，与批1/批3 因子考试同门同窗）

- HOLDOUT 考试窗 = 2025-10-09..2026-09-30（canonical fexam 冻结窗，ch_data.WINDOW_HOLDOUT）
- IS_REF 衰减参照窗 = 2024-10-08..2025-09-30（ch_data.WINDOW_IS_REF，与 HOLDOUT 严格不交）
- **方向登记（两可，事前声明）**: 判定取 |IC|/|ICIR| 两向皆可。理由：上考实证情绪档区分度跨体制
  变号（d_bull/d_bear 反号），方向无法事前冻结唯一；两可登记于开跑前落盘即合规（禁考后改单边）。
- **及格线（裁定#489③ v1 原文口径，三线 AND）**:
  1. |IC_h| > 0.02
  2. |ICIR_h| > 0.3
  3. retain = |IC_h| / |IC_r| ≥ 0.5（|IC_r|=0 或窗 n/a → retain 不可判 → 判不达并如实记因）
- 判定窗 = HOLDOUT（headline），IS_REF 与全窗（2005-2026）读数 report-only。
- 符号稳定性: IS_REF 与 HOLDOUT 的 IC 符号异号 → retain 仍按 |·| 计（canon 口径），但必须显式标注
  "跨窗变号"警示（不自动改判，禁隐藏）。

### 2.5 PIT 复检（沿 v1 四检+e 项结构事实）

- a ts 时点: 考窗 close_final 行 ts 应=当日 15:10:00 且 ts 日期=trade_date
- b asof 越界: 考窗 close_final components 逐成分 asof ≤ trade_date
- c 同键异值: 同 (trade_date, stage='close_final') 键不得多行异值（FINAL 后唯一性断言）
- d 构造无前视: 冻结节前已核（v1 d 项：builder _pctl=vals.tail(250) trailing+拉窗止于当日+C6 rolling+C5 asof，
  代码事实援引不重推；builder 未经本考窗改动——git log 核验如实记）
- e 改写能力/快照留痕: 表级可重写实证在案（pre_open 2026-10-02 双行）；考窗 close_final 无逐日快照留痕
  （单批 replay 建成）；本夜快照器上线后增量留痕开始——e 仍判"仅结构瑕疵"
- pit_verdict_rule（沿 v1 逐字）: clean=a-d 全过且 e 未实证改写能力；conditional_clean=a-d 全过且
  e=仅结构瑕疵；dirty=a-c 任一违例>0 或 d 发现构造前视 → 总判不合格自动成立

### 2.6 verdict 规则（沿 v1 结构，判据换 #489③ v1）

- qualified: 三线全过 且 PIT=clean
- conditionally_qualified: 三线全过 且 PIT=conditional_clean（投产前置=继续逐日 append-only 快照 +
  只追加读径；replay 重跑须留版本）
- unqualified: 三线未全过，或 PIT=dirty（负结果如实入册，禁软判）

### 2.7 数据纪律

CH 只读 SELECT（ch_reader 严格通道，判据类读数禁 query() 返回串口径）；零 DB 写；禁改既有文件；
考试引擎=scripts/backtest/fexam/emotion_linkage_exam.py（本卡冻结常量落地，及格线 import roster.PREREG_V1
防抄写漂移）；单测=tests/backtest/fexam/test_emotion_linkage_exam.py（合成序列零 CH）。

## 3. 开跑后结果（上方冻结块逐字生效，本节只回填读数）

- 开跑: 2026-10-08 04:0x CST｜引擎 scripts/backtest/fexam/emotion_linkage_exam.py（7/7 单测绿）
  ｜verdict JSON=.runtime/sessions/st-mx07-L8/staging/emotion_linkage_exam_v1_results.json（CH 只读零写）
- 数据面实测: 信号 close_final 8617 行（1991-06-10..2026-09-30，version='v0.1.0' FINAL 唯一）；
  代理 000300 5282 行（2005-01-04..2026-09-30）；考窗=2005-01-04..2026-09-30，
  信号×代理日历对齐 **5282/5282 零错位**；主标签尾部越窗 NaN 剔除如实生效。

### 3.1 三线判定（headline=HOLDOUT 2025-10-09..2026-09-30，月度桶 Spearman，n=12 桶）

| 线 | 读数 | 线 | 判 |
|----|------|----|----|
| \|IC_h\| | **0.1905**（IC=-0.19054393302662956） | >0.02 | 过 |
| \|ICIR_h\| | **1.16**（ICIR=-1.15753428401348） | >0.3 | 过 |
| retain | **5.94**（=0.1905/0.0321） | ≥0.5 | 过 |

- IS_REF（2024-10-08..2025-09-30，n=12 桶）: IC=-0.0320647002299984 / ICIR=-0.2236（report-only）
- **符号稳定性: 两窗同号（均负），sign_flip=false**；retain 呈 5.94 高读数的机制=IS_REF 窗 |IC_r|
  偏小（0.032），衰减判据按 |·| 冻结口径通过——如实记录此读数结构，禁误读为"OOS 增强 6 倍"的点估计精度
- 全窗 2005-01..2026-09（n=261 桶）: IC=-0.17099169613025905 / ICIR=-0.7942505678899949
  （21 年 261 个月桶同向，t≈ICIR×√261≈-12.8，非近窗偶然）
- 月度 IC 全表: verdict JSON `monthly_ic` 节（holdout 12 月中 10 月为负、is_ref 12 月中 8 月为负）

### 3.2 敏感性（report-only，不进判定）

| 变体 | holdout IC/ICIR | is_ref IC/ICIR | 读法 |
|------|----------------|----------------|------|
| fwd5_old（上考旧口径 close(t+5)/close(t)-1） | -0.2159 / -0.8428 | -0.0555 / -0.3317 | 同向更强→负向预测力非标签改制artifact |
| fwd5_leg5（t+1 起完整 5 腿 close(t+6)/close(t+1)-1） | -0.2037 / -0.9436 | -0.0390 / -0.2006 | 同向稳健 |
| 同期 corr(e(t), ret_t) | +0.6937 / +5.8156 | — | 情绪确为同步量（上考同步性结论复证） |
| 滚动 20 日 Spearman（全窗逐日，n=5258） | mean -0.1728 / min -0.7369 / max +0.5847 | — | 均值稳定为负，逐日震荡大（时变强度） |

- 与上考结果的关系: 上考 paper2 测 Δemo5（**变化量**）≈0 无前瞻；本考测 e **水位** 对零重叠前瞻收益
  稳定负向——两者不矛盾（水位含反转信息，5 日差分把它洗掉了）；上考 paper1 极值带（e≥0.90 后不跌）
  与本考全水位负 IC 的张力=后段（2025-10..2026-09）高情绪月 IC 深负（2025-10 -0.35、2026-06 -0.52、
  2026-09 -0.37），极值带子样本≠全水位关系，如实并陈。

### 3.3 PIT 复检（考窗 2005-01-04..2026-09-30，5282 行）

| 检 | 读数 | 判 |
|----|------|----|
| a ts 时点 | n=5282，时点≠15:10:00 违例=0，ts 日期≠trade_date=0 | 过 |
| b asof 越界 | 5282 行逐成分扫，asof>trade_date=0 | 过 |
| c 同键异值 | FINAL 后 duplicate_keys=0，multi_value_keys=0 | 过 |
| d 构造无前视 | 冻结事实援引（prereg §2.5）：builder trailing250+当日拉窗；git log 核验 builder 末次变更=2026-10-04 70ee3704e8d，**仅供给面查表名派生（board_index_supply.resolve_table，同名同源零语义差）**，分位/拉窗构造未动 | 过 |
| e 改写能力/留痕 | 结构瑕疵（冻结事实）：表级可重写实证在案+考窗无逐日快照；快照器 2026-10-08 上线首件 emotion_index_20261007T195219Z.jsonl.gz（sha256=cbc608c4…3776e，8658 行）落地后增量留痕开始 | 仅结构瑕疵 |

**pit_verdict = conditional_clean**（a-d 全过 + e 仅结构瑕疵，按冻结规则）

### 3.4 总判

> **verdict = 有条件合格**（三线全过 + PIT conditional_clean；按 prereg §2.6 冻结规则，
> qualified 需 PIT=clean 不可达）。方向登记=两向皆可（冻结§2.4），实测方向为**负（反向）**：
> 情绪水位高 → 后 5 日（t+1 起）收益倾向走低。投产前置（冻结规则原文）：继续逐日 append-only
> 快照+只追加读径；replay 重跑须留版本。本判≠批准任何 flag 翻转/资金面启用（Owner 门位 §5 另议）。

## 4. 自裁记录

1. **[st-mx07-L8] docs/_working TTL 冲突自裁**：车道卡要求 prereg 卡"`# [TTL] permanent`"，
   但 FILE-PLACEMENT-TTL 门禁强制临时区 ttl=task_bound（L6 卡先例同款持久化说明）——按门禁落
   task_bound，permanent 意图经 promote 流程兑现。
2. **[st-mx07-L8] scripts/data/* gitignore 通配收编自裁**：新快照器被 `scripts/data/*` 通配忽略
   （token 登记器因此扫不到件），按 source_health_patrol.py 等 5 件先例加 `!scripts/data/emotion_index_snapshot.py`
   白名单豁免+快照输出目录 `data/emotion_index_snapshots/` 整目录忽略（快照可再生自 CH 全表，不入库）。
3. **[st-mx07-L8] PIT-a 测量仪器 bug 自裁**：首跑 PIT-a 全量误报（5282/5282）——ch_reader 返回
   tz-aware datetime，`astype(str)` 尾缀 `+08:00` 使后缀比对全假阳。冻结判据原文是"ts 时点=15:10:00"
   （语义判据），修的是表示层（strftime 剥时区）非判据本身；修后 0 违例，判据零变更。单测同步覆盖
   tz-aware 表示。
4. **[st-mx07-L8] creation_token 锚点并发冲突自裁**：capability_canonical_file_registry.yaml 当夜
   5+ 施工队并发写，段尾锚点 StaleWriteRefused 回放失败——改用段中低流量锚点
   `--anchor-capability trading_calendar_test` 重试成功（快照器 token 落册；runner/卡 token 同法）。
5. **[st-mx07-L8] retain=5.94 高读数定性自裁**：按冻结口径通过，但点估计上 IS_REF |IC_r|=0.032 偏小
   使比值爆炸——在 §3.1 明示"禁误读为 OOS 增强 6 倍"，判定仍按冻结三线机械执行不改判。
6. **[st-mx07-L8] 卡 token 前后端不一致自裁（第二次派发）**：registry 在册 token=
   `matrix-campaign-emotion-index-prereg-and-first-exam-v1-20261007`（capability=matrix_campaign，
   批量通道自动派生），本卡 frontmatter 原写 `matrix-l8-…-20261008`——以 registry 为真源（机械判定
   禁凭记忆），frontmatter 已对齐在册值（CREATE-GUARD 前后端一致性修复，非改判非重注册）。
7. **[st-mx07-L8] .gitignore 索引陈旧自裁（第二次派发）**：暂存区滞留旧版 .gitignore（缺本车道
   emotion 豁免两块+含他会话已落 HEAD 的 !.zcode/ 逆差），工作区版为当前正确态——重 add 工作区版
   使 staged diff 仅含本车道豁免增量，避免吸收他会话内容。

## 5. 第二次派发续传记录（2026-10-08 晨，断点续传面）

前次派发死于"10 分钟无活动强杀"（提交前），本节记录本次会话对遗留面的复核与增量：

- 遗留面复核全过：快照器/首考引擎/prereg 卡/verdict JSON 四件与 §3 读数逐字一致（headline
  ICIR=-1.15753428401348、retain=5.942482906743803、pit=conditional_clean 复算相符）；
  两套单测 11/11 绿（快照器 4+首考 7）；ruff check/format 零改动。
- 登记面核验：creation_token 3 枚在册（快照器 `data-ops-emotion-index-snapshot-20261007`、
  首考引擎 `fexam-emotion-linkage-exam-20261007`、本卡 `matrix-campaign-emotion-index-prereg-and-first-exam-v1-20261007`）
  +module_translation 2 条在册（module_translation_registry 68011/68027 行）+depgraph 设计节点
  DB 侧（node_id=16437401 起，前次登记）。
- **append-only 增量实证**：本会话跑第二件日快照
  `emotion_index_20261008T025521Z.jsonl.gz`（8659 行，pre_open 24→25，max_trade_date=2026-10-08，
  payload sha256=e617984ebbf73abf9809a87de9a6bc82111d6541cd3eb871d738fac040592a25）；
  manifest 2 记录，首件（20261007T195219Z）payload sha256 复验=cbc608c49bb4…与台账一致，
  **首件零改动**——只增不改铁律跨会话得证。
- 全表现状只读确认：8659 行（close_final 8617；1991-06-10..2026-10-08），与 §2.1 冻结节前已知
  8659 行口径一致（今日新增=pre_open 2026-10-08 行，close_final 未变，不影响首考读数）。
