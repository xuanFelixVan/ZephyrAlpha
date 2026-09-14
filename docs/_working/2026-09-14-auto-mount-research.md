---
ttl: task_bound
---

# 策略自动挂图调研报告——挂图全自动化可行性（Owner 问"能不能做成模块全自动"）

> 2026-09-14 st-c5promote 班｜按 TDM 寻路 SOP 三轮全网挖矿（机构实践/量化社区/学术论文）
> 起因：Owner 问挂图能不能自动化——策略转正后自动挂上决策地图，不再手动。

## 1. 结论（先说答案）

**可行，且三要素在我们项目里恰好全部具备自动化条件**。业界有工业级先例（WorldQuant BRAIN
生态全 API 化自动入库），学术有硬支撑（regime-conditional activation 系论文）。裁定：
**立项建设 auto_mount 自动挂图器，全自动 only-add 模式**——只做新增挂载，永不自动删/挪
（那才触碰 Owner 门位），门禁+月度审计兜底。

## 2. 挂图动作分解（我们上一班手动干了什么→每步能否自动化）

| 手动步骤 | 自动化方案 | 依据 |
|---|---|---|
| 判类别（择时/选股/做T）定节点 | 映射表纯函数：strategy_class→node_id（SOP-C §6.2 本来就是 5 行显式规则表） | 规则已在 SOP，strategy_class 是转正必填字段=人工只判这一次 |
| 判状态适配定格子（activation_state） | **分状态回测归因**：用 regime_snapshot_history 的 dominant 态把 IS 窗口切段，逐段算策略 Sharpe，段>0 且样本≥30 天→该态激活（宁漏勿误） | 学术硬支撑（HMM regime-conditional activation 系）；我们的 7 态概率表 1809 天现成，比论文还省推断一步 |
| 算配比（等权起步档） | 机械规则：新条目 0.05/条+老 sleeve 等比缩水（备忘 69 管线第一档） | 本班已实装一次，规则显式 |
| 挂证据（run 指针） | run_id 管线自带，verified+evidence 自动填 | 纯搬运 |
| 写地图+防格式漂移 | 文本级手术引擎（node_id 分块+唯一锚+count==1 断言——本班实测 diff 29+/15- 零漂移） | 本班已实装，直接模块化 |
| 门禁验收 | 挂后自动跑 validate_decision_map 38 规则+R17 容量+R12 权重和 | 全部机械化现成 |

## 3. 业界证据链（三轮挖矿）

### 3.1 工业先例：WorldQuant BRAIN 生态=全自动策略入库的活样本

- **wq-alpha-pipeline**（github.com/angel4angelov-glitch/wq-alpha-pipeline）：把 alpha 研究
  变成"brute-force overnight job"——定义→模拟→自相关检查→提交全 API 化无人值守；
- **worldquant-miner**（github.com/zhutoutoutousan/worldquant-miner）：LLM（Ollama+金融模型）
  自动生成→测试→提交 alpha 因子；
- BRAIN 官方提交检查=**自相关簇拒绝+簇内择优**（知乎 Alpha 预提交校验详解）——与本项目
  C5 聚类去重同构，他们全自动化了，证明"入库+去重+挂位"可以无人化。

### 3.2 学术支撑：activation_state 的自动化=regime-conditional activation

- **Wang et al. 2020（MDPI JRFM，67 引）**：HMM 识别市场体制→体制切换因子投资——"市场状态
  决定哪些因子/策略上线"的正名之作；
- **SSRN 5785443 / alphaXiv 2605.27848**：Markov switching+RL 的 regime-based portfolio
  allocation——条件化配置框架；
- **QuantStart（QSTrader）**：HMM regime filter"在不利状态禁止开仓"=二值激活矩阵的工程实现；
- **Macrosynergy/DXP Analytics**：regime 分类决定因子有效性与策略成败——"每个策略都是对
  某市场状态持续的下注"（这句话就是我们 activation_state 的定义）。

### 3.3 分类学现状：taxonomy 普遍存在但挂靠多靠人工——正是我们的机会

Quantt 策略九分类等 taxonomy 是现成的分类学，但业界地图/本体挂靠环节自动化程度低
（无 OWL/RDF 级金融交易本体成熟件）——**挂图自动化在业界是空白区，我们有确定性管线设计
（映射表+分状态回测），反而能做成比 BRAIN 更贴决策链的可审计版本**。

## 4. 立项登记：auto_mount 自动挂图器

- **模块**：scripts/backtest/auto_mount.py（MOD 号施工时领）；输入=strategy_registry 新
  candidate 条目；输出=地图 diff+挂图报告+校验回执。
- **管线五步**：①映射表 strategy_class→node_id ②分状态回测→activation_state（样本<30 天
  态不激活）③等权起步档权重计算 ④文本手术写入+38 规则校验+only-add 断言（diff 中禁删行）
  ⑤报告（挂哪/为什么/证据指针）。
- **治理边界（关键裁定）**：全自动 **only-add**——不删不挪不改既有挂载与权重；修正类操作
  仍走人工（Owner 门位不触碰）；月度挂图审计（对齐 decay_watch 节奏）扫错挂。
- **验收五条**：①6 条已挂策略可被管线重放复现（幂等）②分状态归因与人工裁定一致率≥5/6
  ③only-add 断言红蓝测试（伪造删除行必被拒）④38 规则校验全绿 ⑤owner 视觉复核一轮通过。
- **施工**：走 construction_workflow_sop 15 步（新模块义务）；排期=下一班开工（一个夜班班次
  量级，与 sim 方案C 同档）。
- **净零声明**：替代 SOP-C §6.2 手动挂图流程与散落"挂哪了"口头裁定，不新增规范对象。

## 5. 本班产出

调研报告（本文档）+立项登记。未施工（新模块须走 15 步，等排期）。
