---
ttl: task_bound
lane: M1 数据链（补挖波，接续 st-commitspeed-tbl-20260924）
segment: F11 TDM 交叉轴挂接——13 轴 vs 16 表口径漂移司法取证（总册 P1，R-M1-05 证据包）
mined_at: 2026-09-25
session: st-ailayer-fullflow-d
---

# 10_f11_xref_counting_drift — TDM 交叉轴口径漂移取证册（F11）

> **与既有册关系**：05_tdm_crossaxis.md T1+R-M1-05 已登记漂移现象与修法方向；本册只补"取证"——用 git 考古钉死"16"的出生、变形与漂移链条，作为 R-M1-05 修宪的证据包。05 册其余结论引用不重挖。

## 一、环节定义与边界

一句话：回答一个数字问题——"业务资产库挂 TDM 交叉轴"到底是 16 还是 13（还是 19），三个数各自量的是什么，"16 表"错在哪一步。

## 二、六向台账（取证面）

| 向 | 内容与实证 |
|---|---|
| 上游输入 | git 历史（decision_map.py 六个关键 commit）+两代宪法文本（legacy v1/L0 AGENTS.md）+现行代码三张清单（_XREF_SPECS/_XREF_MAX/R99 必需文件循环） |
| 下游消费 | R-M1-05 修宪等长替换句（证据包交付）；总册 §五.1 口径漂移项收敛；#ARCH-351 旧口径另立注的素材 |
| 自动化触发 | 不适用（文档考古；防复发机制=T2 对账器+宪法计数不写死原则 §4.4，已在他册登记） |
| 真源与注册表 | 代码真源=src/zephyr/trading/decision_map.py:100-118（_XREF_SPECS 13 轴）+:955（R99 必需文件循环）；文本漂移源=AGENTS.md:115/agent_constitution_l0.md:119（同句"业务资产库 16 表"）+agent_constitution_legacy_v1.md:117（"业务资产库 16 个……门禁 R3-R36"） |
| 门禁与质量尺 | R99 缺文件=error（:957-959）；本册钉死的事实链见 §三 时间线 |
| 当前运行状态 | **绿（代码）+红（文本）**：代码 13 轴 19 文件自洽运转；宪法两处文本写"16 表"待修（R-M1-05 在案） |

## 三、取证核心：时间线（git 逐 commit 实证）

| 时点 | commit | 事件 | 数字状态 |
|---|---|---|---|
| 2026-09-07 | 2513720086（D36 全库交叉轴打通） | _XREF_SPECS 诞生：8 轴（pattern/seat/macro/cycle/universe/cost_model/event/risk_limit）；commit 文"R99 扩展 **13 注册表**" | 8 轴；R99 清单=5 核心+8 轴=**13 文件** |
| 2026-09-07 | ad9d5b18b9（D37 全库满贯） | +PFM/BMK/THD 3 轴=**11 轴**；commit 文"R99 扩展 **16 注册表**；**16/16 业务库全部点对点可达**" | **"16"出生=5 核心（strategy/factor/data_asset/execution_algo/technical_indicator）+11 轴=R99 必需文件数**；门禁跨 R3（策略引用）~R36（告警阈值） |
| 2026-09-09 | 23da636683（D38 补挂） | +ML 模型轴 R38（"75 库盘点唯一真缺口"） | 12 轴；R99 清单=17 文件 |
| 2026-09-11 | legacy v1 宪法（git bb44bbbebe 前身版） | :117 原文"业务资产库 **16 个**全部挂 TDM 交叉轴（_XREF_SPECS 表驱动，门禁 **R3-R36**）"——冻结 09-07 时点计数 | 文本=16 **个**（库/注册表），与当时 12 轴已差 1 |
| 2026-09-12 | c964c376c0（#ARCH-310 R3 宪法换版，git -S 唯一命中） | L0 抄入 AGENTS.md §8，措辞变"业务资产库 **16 表**挂 TDM 交叉轴" | **语义漂移点：个（注册表文件）→表**；轴数已 12，16 从未等于轴数 |
| 2026-09-23 | 9c9b1276a8（TDM2.0 扩容批2/3） | +CHN 传导链轴 R45（chain_registry 机生）；R99 核心扩 6（+_REG_DAL decision_algo） | **13 轴**；R99 清单=6 核心+13 轴=**19 文件**（现行） |

**结论（三句话）**：
1. "16"的出生=2026-09-07 D37 时点的 **R99 必需注册表文件数（5 核心+11 轴）**，commit 原文"16/16 业务库全部点对点可达"可证；它从头就**不是** _XREF_SPECS 轴数（当日轴数=11）。
2. 漂移分两步：v1 宪法把"16 个（注册表）"冻结；L0 换版（09-12）抄写时"个"变"**表**"——量纲换错。
3. 此后代码两次扩容（12→13 轴、核心 5→6），文本再未跟进；现行真值=**13 轴（挂接面）/19 文件（R99 全家福）**。

**第三混淆源裁定**：#ARCH-351 内"trade_calendar 不在**哨兵 16 表**"（architecture_issue_registry.yaml:22353）属另一家族的 16（quality_sentinel_tables 族，现役 9 表）——与交叉轴无关，纯同数巧合，R-M1-05 建议的"另立注防混淆"确认必要。

## 四、堵点与病灶（增量）

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| T1' | R-M1-05 修法句升级（证据包版） | 原建议只改"16→13"，未交代 16 的来历 | 宪法等长替换建议句：**"业务资产库 13 轴表驱动挂 TDM 交叉轴（`_XREF_SPECS`，R99 全家福 19 注册表；新库挂接义务见该表 §4）"**——一并交代 13/19 两量纲，防下次漂移 | 0.1 天 | 提请总筹走宪法替换通道 |
| T1'' | L0 与 docs/01.../sop/governance_sop/agent_constitution_l0.md:119 双副本同句 | 宪法正文与 SOP 副本两处维护 | 修宪时两处同批（sed 可枚举，grep "16 表" 全仓仅此两处+挖矿册自引） | 并入 T1' | 同批 |
| T4 | 教训入制：数量词随代码扩容漂移已是第二例（本例+01 册 B3 槽位数） | 散文写死计数违反宪法 §4.4 但无机检 | 提请：commit gate 对宪法/骨架册内"数字+表/轴/槽"模式做生成器计数比对（低优先 WARN） | 0.5 天 | 提请（M3 门禁侧） |

## 五、提速与合并机会

1. R99 必需文件循环（:955）与 _XREF_SPECS 天然一致——若宪法改注"以 decision_map.py R99 清单为计数真源"，未来扩容文本可零维护（计数自代码派生）。
2. 05 册提速项 1（_XREF_SPECS/_XREF_MAX 合表）与本册无冲突，同批施工更省。

## 六、自审闸三态

**取证挖干**（时间线每行双源：git commit 文本+文件内容实读，无推测环节）；R-M1-05 修法句升级版交总筹（T1'/T1''同批）；T4 提请 M3。**13 vs 16 争议终结：两个数都曾为真，量的不是同一物，错在 09-12 换版抄写的量纲。**

## 七、复核命令

```bash
git log -S "16 表" --format="%h %ad %s" --date=short -- AGENTS.md            # 唯一命中 c964c376c0 2026-09-12
git log -S "16/16" --format="%h %ad %s" --date=short -- src/zephyr/trading/decision_map.py | tail -1  # ad9d5b18b9 2026-09-07
git show ad9d5b18b9 --stat | head -5
git show 72a991ea99:src/zephyr/trading/decision_map.py | sed -n '/_XREF_SPECS: Final = (/,/^)/p' | grep -c '("'  # 11 轴（09-07 晚）
sed -n '100,118p' src/zephyr/trading/decision_map.py                          # 现行 13 轴
grep -n "for fname in (_REG" src/zephyr/trading/decision_map.py               # :955 R99=6 核心+13 轴
sed -n '117,117p' docs/01_policies_and_standards/sop/governance_sop/agent_constitution_legacy_v1.md  # v1 原文"16 个…R3-R36"
grep -n "16 表" AGENTS.md docs/01_policies_and_standards/sop/governance_sop/agent_constitution_l0.md  # 两处待修
sed -n '22353,22353p' docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml  # 哨兵 16 表=第三混淆源
```
