---
ttl: task_bound
completes_when: Owner 对"骨锁肉动"裁定与拍板项批复完毕，或挖矿 v2 替代
---

# 交易决策骨架（"股价"）全网挖矿报告 v1（st-autolnk-20260917）

> Owner 原问题：①股价（交易决策流程/权重决策流）这套挖过矿没有？②它的层级骨架会不会变、要不要为它建"自动升级"流程？③这套东西是不是很前沿？
> 对象定义（另一 AI 对话已冻结的版本）：5 决策层（L1 大盘/周期→L2 板块→L3 标的→L4 组合→L5 执行）× 4 时间节拍（T1 周期判定/T2 每日晨判/T3 盘中执行/T4 收盘复盘）× 每层双态输出（排序+出手/不出手）+ 日度编排器（"今天不交易"权）+ 周期切换器。

## §1 挖矿证据（分级标注）

**A 级（本轮全网实证，带来源）**
1. 自上而下四段漏斗是机构标准课：宏观→资产配置→板块轮动→选股。资产配置被机构估为**收益决定权的大头**（Fisher Investments 口径=70% 决策权重）；CFA III 体系将 top-down 列为组合管理标准流程；FPA Journal 实证 top-down 基金按商业周期相位主动轮动板块。
   来源：[Investopedia](https://www.investopedia.com/terms/t/topdowninvesting.asp) / [FE Training](https://www.fe.training/free-resources/portfolio-management/top-down-investing/) / [Fisher](https://www.fisherinvestments.com/en-us/personal-wealth-management/how-we-are-different/disciplined-investment-strategy/top-down-approach) / [FPA Journal](https://www.financialplanningassociation.org/article/journal/MAY21-understanding-intersection-between-style-exposure-sector-rotation-and-business-cycle)
2. **血肉有生命周期，业界靠"监控+退役+替换"续命**：alpha 会衰减、有始有终、甚至会反转（Essentia 实证）；HFT 策略全生命周期含盘后 P&曲线监控与退役判据（Quant Insider）；自营盘（Maven）把 alpha 衰减列为决策成本核心。
   来源：[Essentia](https://www.essentia-analytics.com/investment-alpha-lifecycle-analysis/) / [Quant Insider](https://quantinsider.io/blogs/anatomy-of-an-HFT-strategy-lifecycle) / [Maven](https://www.mavensecurities.com/alpha-decay-what-does-it-look-like-and-what-does-it-mean-for-systematic-traders/) / [Exegy](https://www.exegy.com/alpha-decay/)
3. **"AI 自动挖替换血肉"是 2025 活跃前沿**：AlphaAgent（arXiv 2502.16789）用 LLM 智能体挖因子并带正则化探索防衰减——正是⑤工段"因子自动合成"的学术同款。
   来源：[AlphaAgent arXiv](https://arxiv.org/html/2502.16789v2)
4. 机器维护窗业界实践见骨架 v1 §3（每周固定窗为主流+开机自检为共识）。

**B 级（经典共识，训练知识，标待复验）**
5. 骨架级框架几十年稳定：Brinson 归因（1986）至今是逐层归因行业标准；Hamilton regime switching（1989）是 L1 regime 门的祖源；风险预算倒推仓位（1990s 机构实践）是 L4 的根。→ 待下次搜索窗复验原始文献链接。
6. WorldQuant BRAIN=自动化 alpha 研究平台（表达式挖矿→秒级回测→及格线→提交替换）——"血肉自动流水线"的工业样板；本题搜索限流，描述出自模型知识，待复验。

## §2 裁定：骨锁肉动（回答 Owner 三问）

**问①挖过没有**：项目内已挖（另一 AI 的愿景映射+两张策略卡+TDM 覆盖审计在途）；项目外（业界情报）本报告=第一次，结论如下。

**问②骨架会不会变、要不要养**：**骨稳肉动，分开养**——
- **骨（L1-L5×T1-T4×双态门+两器）：几十年级稳定，不建自动改骨流程**。业界证据=上述 1/5：四段漏斗自上而下五十年未变结构，只加宽（加另类数据层、加 quant overlay）不加高。动骨牵一发动全身（TDM 138 节点重对齐+归因结构变+全部考试基准变），且 Owner 判断"赚钱核心灵魂"——**动骨=唯一拍板项**（与 Owner 口径一致）。
- **肉（每层的数据源/因子/模型/阈值/策略包）：有生命周期（证据 2），必须自动化养**。养法=**复用骨架 v1 的 8 工段流水线，不另建第二套**：每层立"模块卡"→①发现→③上架→④清洗→⑤⑥合成→⑦考试→⑧上线/退役建议。alpha 衰减监控=⑧模拟盘四件的月度偏离+组合门打分天然覆盖。
- **新增工段⑨骨架体检**：月度只读盘点（格子×模块健康度×新源可用性×alpha 衰减信号）→"增/删/换建议书"。建议书自动生成；**血肉级建议自动执行，骨架级建议转 Owner 拍板**。与另一 AI 分工：他做一次性 TDM 138 节点对格子（项目内审计，在途）；我做常态化月度体检（待其交付后开工，零撞车）。

**问③前沿吗**：是。"全自动养血肉"=业界正在做的（WorldQuant BRAIN 工业化样板+AlphaAgent 学术前沿）；"全自动改骨架"**无人公开做完整**——因为架构级变更=全链重考，风险收益不成比，业界都把架构锁死人工管、模块自动换。本项目的"骨锁肉动"正是把这个业界隐性共识显式化成制度——不冒进，也不缺位。

## §3 对 Owner 的拍板项（仅此三件）

1. **骨锁肉动裁定**认可否（动骨永远 Owner 拍板，血肉全自动）。
2. **每周日 04:00-09:00 休息窗**认可否（涉关机）。
3. **搜索设备 v0 开工**确认（Owner 已口头令"先把所有设备建起来"——默认开工，异议叫停）。
