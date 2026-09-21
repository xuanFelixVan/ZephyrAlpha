---
ttl: task_bound
session: st-collintake-20260920
topic: collection_intake_20260920
---

# 收藏情报包拆解与内外挖矿判定台账 2026-09-20

> 执行会话：st-collintake-20260920（Owner 授权令：先内部挖矿判"有没有/能不能用"，再对外挖矿补缺口，分类落档）。
> 输入：Owner 小红书/视频收藏包 = 8 段文案 + 4 帖 + 3 图（拆解为 25 条，见上会话聊天清单）。
> 方法：4 路并行挖矿（内部数据面 / 内部工程面 / 外部因子 / 外部工具），证据分级标注：`[亲验]`=本会话代理实查（附路径）、`[外部]`=全网核实（附 URL）、`[记忆]`=项目记忆、`[存疑]`=未证实。
> §0 一页结论（TL;DR）：**25 条中 0 条可直接照搬照抄；9 条内部已有等价物或数据已在库（A）；8 条部分有需补齐（B）；3 条是真缺口值得立项（C）；5 条证伪/存档（D/E）。** 最高价值三发现：①A 股期权 PCR 有交易所官方每日免费数据，akshare 直取，而本项目期权面只有 <2 个月浅数据——这是唯一值得新立项的数据批；②筹码峰 90%/70% 集中度配方与批 10 筹码族天然拼合，只差 cost_15/85 两列；③两个"网红项目"被证伪（Anthropic Fast Start File 查无实据、eclassic 因子库不存在），Jev 模型=营销性官宣按存档处理。**安全行动项 P0：ZCode 静默上传事件已被多方证实，本机三件自查见 security/sec_zcode_workspace_upload.md。**

## 判定分档口径

- **A 已有可直接用**：内部已有实现/数据，无需外采。
- **B 部分有需补齐**：有底子，列明具体缺口与补齐路径。
- **C 缺失需立项**：内外确认有价值且缺失，给立项建议（P0/P1/P2）。
- **D 存档不立项**：有价值但当前不排期。
- **E 证伪/存疑弃用**：查无实据或营销内容，禁止作为决策依据。

## 判定台账（25 条全量）

| # | 条目 | 内部挖矿结论 | 外部挖矿结论 | 判定 |
|---|------|-------------|-------------|------|
| 1 | 幻方十大因子 | 原料面大部分已在库（动量/反转/波动率/资金流/财务派生/板块齐）`[亲验]` | 十八问=公众号科普，无官方直链 `[外部]` | B：按假设卡入 E1C/E4，勿作方法论真源 |
| 2 | 筹码峰集中度配方 | 引擎 trial（裁定#257④打回）；批 10 范围未含 90%/70% 集中度与峰突破 `[亲验]` | 无需外采（配方自足） | B：并入批 10 扩 cost_15/85+集中度两列 |
| 3 | 期权 PCR 族 | 现算成交量 PCR（MOD-SIG-059），无 OI 表，期权历史 <2 月 `[亲验]` | **交易所官方每日发布 PCR 证实**；akshare `option_daily_stats_sse/szse` 免费直取 `[外部]` | C：P1 数据批立项（见 factor_spec_options_pcr.md） |
| 4 | Alpha101 论文 | 无表达式因子库；E1C 算子白名单可作对照 `[亲验]` | arXiv:1601.00991 全文免费+两个成熟复现仓 `[外部]` | B：入库路线就绪（分批翻译→E4 重考） |
| 5 | Alpha158/360（Qlib） | 无 | 证实，因子定义在 qlib handler.py `[外部]` | D：借"表达式→handler"范式多于因子本身 |
| 6 | eclassic 因子库 | 无 | **查无实据，判定不存在** `[外部]` | E：弃用，向来源索证前不采信 |
| 7 | 评论区因子池（16 条） | 散户持仓已补齐/龙虎榜已有/SUE 口径在案/恐贪在产——多数数据面就绪 `[亲验]` | — | A/B/D 分项见 factor_pool_comment_leads.md |
| 8 | 拥挤度轮动 | 无专门物 `[亲验]` | 社区共识方法论 | C P2：E4 出证维度加"拥挤度" |
| 9 | 降回撤双法/MOE/风险平价 | pf_alloc 有 risk_budget/vol_target 等算器件但 wiring=exempt 未接电 `[亲验]` | — | B：pf_alloc 接电时作为设计引用 |
| 10 | trade_when 条件调仓 | E1C DSL 白名单可纳 `[亲验]` | 语义证实（触发/更新/退出三元） `[外部]` | B：速赢——白名单加一条算子 |
| 11 | Factor Zoo 过滤文献 | E4=DSR/PBO/WFO 已是等价实践 `[亲验]` | 四篇文献逐字核实（Taming 在 JF 非 JFE） `[外部]` | A：作为 E4 准入门的引用基础 |
| 12 | 超级 Alpha 内部撮合 | 执行层成本思想 `[记忆]` | 101 论文引文 | D：存档于方法论文 |
| 13 | 长周期均线择时 | regime 线（S-OWNER-002 考试 FAIL 挂起中） `[亲验]` | — | D：regime 线复活时一并考 |
| 14 | PCR 跨市场映射 | 并入 #3 | — | —（并入期权文） |
| 15 | 外部因子必须本地重考 | E4 既有纪律 `[记忆]` | 社区实测"3 试 1 勉强"佐证 | A：铁律重申 |
| 16 | LLM_QUANT_FACTORY | 六件套对标：三强三缺（见 eng 文） `[亲验]` | 证实存在；**PolyForm Noncommercial 禁商用**；63★已停更（末次 push 2026-08-05） `[外部]` | B：只学思想不抄代码，QuantCombine 思想入 FAC-E7/E8 设计输入 |
| 17 | Agent Lightning | 全仓无 RL（gplearn+LLM-DSL 是唯二生成轨道） `[亲验]` | 证实；**仓址修正=microsoft/agent-lightning**（剪报地址 404）；MIT；41.8→56.4 绑定 Qwen3.5-9B+6K 样本 `[外部]` | C P2：AI 层候选（见 eng_agent_lightning.md） |
| 18 | Anthropic Fast Start File | 多代理编排已有自产件 `[亲验]` | **GitHub 全站 0 命中+黑客松名单无记录→不存在** `[外部]` | E：证伪；真实替代=Anthropic multi-agent research system 博客 |
| 19 | Gemini/Nano Banana Pro 图解 | LSG 网关在（LLM 调用必经） `[亲验]` | Nano Banana Pro=Gemini 3 Pro Image，API 可用 `[外部]` | D：工具笔记，接入须走 LSG |
| 20 | Ghidra .so 逆向 | 无在办闭源 SDK 分析需求 `[亲验]` | 12.1.3（2026-08-18），ELF/Android .so 内置支持 `[外部]` | D：存档工具笔记 |
| 21 | Hyperliquid 风险结构 | **HL 四表已在库+资金费 465 万行（2023-05-12 起）** `[亲验]` | 风险分析合理（清算已链上化，撮合道德风险仍在） `[外部]` | A：数据已接；风险条目入交易对手清单 |
| 22 | Hyperliquid 数据下载 | 快照两表 2026-09-18 起自积不可回补 `[亲验]` | 官方 S3 仅 L2 快照（requester-pays/每月/无保证）；K 线须 API 分页或 Tardis/CoinAPI `[外部]` | B：缺口渠道已明（见 tool_hyperliquid_data.md） |
| 23 | "Jev 模型" | — | **真实但=TypeSafe AI 2026-09-15 营销性官宣**（无同行评审/无权重）；疑与 JEPA 混淆讹传 `[外部]` | E：存档观察不采信（见 misc 文） |
| 24 | ZCode 静默上传事件 | 本会话即运行于 ZCode `[亲验]` | **事件证实**（ferstar 发现 ~/.zcode 700MB；RepoWiki 默认开；官方致歉三补救） `[外部]` | **P0 行动项（今天办，见 security 文）** |
| 25 | DLSS5/显卡发热 | 宿主机运维背景 `[记忆]` | — | D：并入周重启案背景资料 |

## 目录说明

```
collection_intake/
├── README.md                          本文件：总览+判定台账
├── factors/                           因子类（规格+内外判定）
│   ├── factor_spec_huanfang_ten.md        幻方十大因子规格卡
│   ├── factor_spec_chip_concentration.md  筹码峰集中度配方（→批10）
│   ├── factor_spec_options_pcr.md         期权 PCR 族（→P1 数据批立项）
│   ├── factor_spec_alpha101_191_158.md    Alpha101/191/158 外部因子集入库路线
│   └── factor_pool_comment_leads.md       评论区因子池 16 条分项判定
├── engineering/                       工程类
│   ├── eng_benchmark_llm_quant_factory.md LLM_QUANT_FACTORY 六件套对标
│   ├── eng_agent_lightning.md             Agent Lightning（AI 层候选）
│   └── eng_factor_methodology.md          因子工程方法论汇编
├── tools/                             工具类
│   ├── tool_hyperliquid_data.md           Hyperliquid 数据源+风险
│   ├── tool_gemini_chart_recipe.md        Gemini 图解配方
│   └── tool_ghidra_so_reversing.md        Ghidra .so 逆向
├── security/
│   └── sec_zcode_workspace_upload.md      ZCode 上传事件+P0 行动项
└── misc/
    └── misc_unverified_items.md           Jev 存疑+DLSS 杂项
```

## 立项建议汇总（按优先级）

1. **P0（今天，Owner 亲办）**：ZCode 本机三件自查（security/sec_zcode_workspace_upload.md）。
2. **P1（下一数据批候选）**：期权 PCR 数据批——akshare 官方统计接口（沪 CP_RATE/深持仓比），回补历史+入 CH 新表，喂 option_sentiment 从"成交量口径"升级为三口径（factor_spec_options_pcr.md）。
3. **P1（搭批 10 顺风车）**：筹码集中度扩项——批 10 增 cost_15/85 两列+90%/70% 集中度两指标+峰突破/发散信号规则（factor_spec_chip_concentration.md）。
4. **P2**：E1C 白名单加 trade_when 算子；E4 出证维度加拥挤度；AI 层路线图挂 Agent Lightning 观察项。


---

## 终局状态块（W8 第二圈 2026-09-21）

- 状态: A 已结案可归档（本目录已整体迁入 archive/2026-09/collection_intake/）
- 依据: 25 条判定台账固化 HEAD 9d609be2a3/924c4e7376/8f7d91fb22；六项后续承接指针见 closure_report.md §二；TC-10 卡=recovered_task_cards/
- 归档: docs/_working/archive/2026-09/collection_intake/（2026-09-21 W8 第二圈 st-workclean-20260921）
- 备注: README 即情报拆解方法论范本（A-E 判定分档+[亲验]/[外部]/[记忆]/[存疑] 证据分级），随档保留防误删
