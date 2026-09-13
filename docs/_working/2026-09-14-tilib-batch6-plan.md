---
ttl: task_bound
---

# 技术指标库 批 6 施工方案（挖矿增补内嵌）——RV 波动率族+BBI+立卡 1/2/3

> 任务：Owner 指令"施工：RV 波动率族 + BBI + 立卡 1/2/3 一批打掉，然后消费端接线批立项。施工方案用病菌寻路挖一遍再按施工 SOP 施工"。
> 依据：批 4/5 挖矿报告（本目录 indicator-mining-batch4.md §3-§6）；施工 SOP=construction_sop/construction_workflow_policy.md 15 步闭环。
> 规模：**14 指标 / 19 列**，REG-IND-001 78→92 条，DDL 116→135 列。全部落既有 4 文件（无新建模块，无 depgraph 设计节点新增）。

## 0. 方案挖矿增补（方案级，5 轮）

| 轮 | 矿脉 | 判定 | 产出 |
|---|------|------|------|
| P-R1 | STOCH/DX/Aroon TA-Lib 精确口径 | signal | [TA-Lib/ta-lib-python #709](https://github.com/TA-Lib/ta-lib-python/issues/709)：STOCH 参数 fastk=5/slowk=3/slowd=3 输出 slowk/slowd；STOCHF 输出 fastk/fastd；DX=100×\|+DI−−DI\|/(+DI+−DI)；AroonUp/Down=100×(N−距极值根数)/N |
| P-R2 | Yang-Zhang 公式细节 | signal | σ_yz²=σ_o²+k·σ_c²+(1−k)·σ_rs²（k=0.34/(1.34+(N+1)/(N−1))；σ_o=隔夜、σ_c=开收、σ_rs=Rogers-Satchell 项），批 4 R6 引文链（FlashAlpha/MetricGate/MIT OCW） |
| P-R3 | 库内惯例核对（内部） | signal | 通达信优先原则（16 号 §2）；列命名 snake_case 带周期后缀；warmup=最长依赖窗；OHLCV 契约全部满足（YZ 需 open——趋势文件 I1 fields 已含 open） |
| P-R4 | 三件套 checklist（内部） | signal | 代码+测试→DDL+逐列 migrations→registry（safe_write_text）→memo→639→~700 tests→battle_map 锚点核对（019/021/022/023 均已锚✓）→干净进程逐列 ALTER+探针→队列提交→回填五轮链 |
| P-R5 | A 股适配复核 | signal | YZ 隔夜跳空项恰好适配 A 股高开低开常态；BRAR/CR 通达信公式直接移植（批 4 R4 双源引文）；一字板 HH=LL 分母防护沿用 STOCH/KDJ 先例（where(hh==ll)） |

## 1. 指标算法规格表（14 指标 / 19 列）

### 波动类 volatility.py（+4，10→14）

| indicator_id | 输出列 | 参数 | 公式（口径来源） |
|---|---|---|---|
| parkinson | parkinson_20 | 20 | σ_p²=Σ[ln(H/L)]²/(4ln2)/N（Parkinson 1980） |
| garman_klass | garman_klass_20 | 20 | σ_gk²=mean{0.5[ln(H/L)]²−(2ln2−1)[ln(C/O)]²}（GK 1980） |
| rogers_satchell | rogers_satchell_20 | 20 | σ_rs²=mean{ln(H/O)ln(C/O)+ln(L/O)ln(C/O)}（RS 1991，漂移无关） |
| yang_zhang | yang_zhang_20 | 20 | σ_yz²=σ_o²+kσ_c²+(1−k)σ_rs²，k=0.34/(1.34+(N+1)/(N−1))（YZ 2000，处理隔夜跳空） |

口径：全部取滚动窗内均值后方差开方（年化不强制，输出日频波动；×100 百分比口径与 histvol 一致性另注）——**裁定：输出为日频标准差估计×100，与 histvol（年化%）区分，docstring 注明**。

### 趋势类 trend.py（+1，17→18）

| indicator_id | 输出列 | 参数 | 公式 |
|---|---|---|---|
| bbi | bbi | 3/6/12/24 | (MA3+MA6+MA12+MA24)/4（通达信/同花顺标配） |

### 动量类 momentum.py（+7，22→29）

| indicator_id | 输出列 | 参数 | 公式 |
|---|---|---|---|
| stoch | stoch_fastk/stoch_fastd/stoch_slowk/stoch_slowd | 5/3/3/3 | FastK=100(C−LL5)/(HH5−LL5)；fastd=SMA(fastk,3)；slowk=SMA(fastk,3)；slowd=SMA(slowk,3)（TA-Lib STOCH+STOCHF 合一） |
| aroon | aroon_up/aroon_down | 14 | 100×(N−距 HH/LV 根数)/N |
| aroonosc | aroonosc | 14 | aroon_up−aroon_down |
| bop | bop | 16 | SMA((C−O)/(H−L), 16)，H=L 时该项 0 |
| ppo | ppo | 12/26 | (EMA12−EMA26)/EMA26×100 |
| apo | apo | 12/26 | EMA12−EMA26 |
| dx | dx_14 | 14 | 100×\|+DI−−DI\|/(+DI+−DI)，复用 trend._di |

### 情绪能量（momentum 类内，+2，29→31 文件计数）

| indicator_id | 输出列 | 参数 | 公式 |
|---|---|---|---|
| brar | ar_26/br_26 | 26 | AR=Σ(H−O)/Σ(O−L)×100；BR=Σmax(0,H−Cp)/Σmax(0,Cp−L)×100（通达信） |
| cr | cr_26 | 26 | CR=Σmax(0,H−MIDp)/Σmax(0,MIDp−L)×100，MID=(H+L)/2（通达信） |

（指标类计数核对：波动 14/趋势 18/动量 31/量能 13/反转 5/统计 4/复合 1/循环 5=**91？**——不对：14+18+31+13+5+4+1+5=91≠92。修正：动量 22+9=31（stoch/aroon/aroonosc/bop/ppo/apo/dx/brar/cr=9），趋势 17+1=18，波动 10+4=14，共 14 新增 → 78+14=92 ✓（31+18+14+13+5+4+1+5=91——差 1：动量现值 22（含批 2b 后）+9=31 ✓；总数 78+14=92；分类合计 91+?——复合 1+循环 5=…91+1(composite)=？composite 已计入 1。重算：17+1(ichi)=trend 文件 18 但 trend 类=17+ichi 复合类另计 → 类维度：trend17+1=18？Ichimoku category=composite！所以 trend 类 18 不含 ichimoku → mcginley 后 trend=17（批 2a 后 11+批2b+1=…）——以代码实测为准，施工后跑 test 修正文档数字。）

## 2. 测试计划（每指标 2-3 用例，≈30 用例）

- RV 族：常数价→0；已知单 bar OHLC 手算（构造 H/L/O/C 使 ln 项可控）；warmup NaN；非负
- BBI：常数价=常数；=四 MA 均值手算对照；warmup=23
- STOCH：常数价防护（HH=LL）；上升序列 fastk=100；slowk/fastd 平滑关系
- Aroon：新High→up=100；单调上升 down=0；osc=up−down
- BOP/PPO/APO：常数零；升市正；warmup
- DX：复用 _di 手算对照；值域 [0,100]
- BRAR/CR：常数价 AR=BR=CR=100；手算单 bar；分母零防护

## 3. 已知坑 checklist（前三批沉淀，施工时逐条避）

1. CRLF：批量文本替换先 normalize LF（schemas/apply 脚本均 CRLF）
2. safe_write_text base hash=LF 归一口径
3. registry 条目 module_id 必须与文件头 BLUEPRINT 一致（本批全用 019/021/022——已锚✓）
4. CH ALTER：干净进程逐列+system.columns 探针（apply 脚本假成功待修）
5. heredoc 禁写代码——Edit/Write 工具
6. docs/_working frontmatter 只写 ttl: task_bound
7. 队列 enqueue+requeue 穿行；提交后 git log --name-only 核归属

## 4. 施工 SOP 15 步映射

Step 0 冷启动✓（本会话在途）→ Step 1 文档审查=本方案 → Step 1.5 创建前搜索=批 4/5 挖矿（无新建文件）→ Step 1.8 架构评审=轻量（既有模块扩展，无新蓝图）→ Step 2 全景图登记=免（无新节点）→ Step 3 五图对齐=提交时 gate 校验 → Step 4 施工编码=§1 → Step 5 测试=§2 → Step 6 长清单审查=无 → Step 7 施工文档=16 号 memo §6 追加 → Step 8 状态流转=registry 计数 → Step 9 完整性=探针 → Step 10 落地=队列 → Step 11 清理=.runtime/tmp 保留探针脚本（TTL 自清）→ Step 12 免（主工作区）。

## 5. 消费端接线批立项（批 7 卡）

- 背景批 5 R8 实证：指标列下游消费≈0。回填完成后，"指标→因子/策略输入"接线是数据价值变现瓶颈。
- 立项范围：internal_compute_provider 输出列 ↔ factor_registry 因子输入声明（如 boll_pctb 动量因子、RSI 背离策略、ATR 止损位）；C4 翻译车道读国外策略的 STOCH/Aroon/PPO 依赖；TDM 抽屉 algo_refs 锚点挂接。
- 启动条件：回填四轮完成（d/w/m 历史 ≥2 年）+ 批 6 落地。
- 工时估计：1-2 班（盘点消费清单→双向锚点→消费冒烟）。
