---
ttl: task_bound
completes_when: 全流通战役收官（验收仪尺子连续两轮 0 新断点）
---

# 断点归簇 + 普查四态重判（T3）— 验收仪自扫 vs `01_break_census.md` 85 条

产出者=`st-ff-verifier3-20260918`（尺子=第 1 笔落地的 `scripts/automation/flowthrough_verifier.py`）
自扫来源=`04_sixway_ledger.md`（17 环节实测，红=13 / 黄=5，生成时刻 2026-09-18 19:36）
本文件的每一条都标了**依据等级**：`亲验`=本会话亲自复跑了原始命令；`转报`=引前腿产物未复跑；`推断`=未取证。

> **本文件的论域声明（R-024C 教训的落地，非文档劝告）**
> 本结论论域 = 验收仪 6 真源推出的 17 个 `FF-*` 环节 × 六向中①③④⑤为**实测**、②为**真跑**、⑥为**静态推演**。
> 论域外（尺子没扫到，不代表无断点）：`src/zephyr/**` 的函数级静默失败细节面（z-silent 车道五模式在扫）、
> `docs/03_modules/**` 蓝图一致性面（z-arch 在出 #ARCH-338..356）、DB 数据正确性面（z-datagap 在治）。
> 本文**不说"全绿/全仓无断点"**；未复测项一律显式标 `未复测`，不猜判。

---

## 1. 验收仪自扫出的**新断点** → 与普查 85 条归簇

判据说明：`同对象`=路径/表/注册项同一；`同根因`=对象不同但成因机制同一；`完全不同`=普查 A–J 十族装不下。
**本腿不自行取 BRK 号**（取号权归总包），新立项用临时锚 `V3-NNN`，待总包转正。

| 新断点（尺子实测证据） | 环节 | 是否已被某 BRK 覆盖 | 建议 | 严重度 | Owner 门位 | 依据 |
|---|---|---|---|---|---|---|
| `src/zephyr/alt_data/cohort_daily_ledger.py` 真跑 `rc=1`，`ModuleNotFoundError: No module named 'schemas.categories'`（FF-01 2.06s / FF-06 2.23s 两次独立复现） | FF-01,FF-06 | **完全不同**——普查 A–J 无"入口真跑即崩"族；`cohort_daily_ledger`/`schemas.categories` 在 01 里 **0 命中**（亲验 grep） | **新立 V3-N01** | 高（该环节②向直接红，非推演） | 否 | 亲验 |
| `src/zephyr/data/ch_parts_monitor.py` 真跑 `rc=1`，`AttributeError: module 'calendar' has no attribute 'day_abbr'`（FF-02 1.23s / FF-03 1.33s 复现） | FF-02,FF-03 | **完全不同**，同上 | **新立 V3-N02** | 高 | 否 | 亲验 |
| 同上脚本在 FF-04 跑出**另一种**崩法：`AttributeError: partially initialized module 'pandas' has no attribute '_pandas_datetime_CAPI' (circular import)` | FF-04 | **同对象不同根因**于 V3-N02 → 归一条 BRK、两条子现象 | 并入 V3-N02（登记两症状） | 高（同一入口两种崩法=运行期不确定，比稳定崩更难查） | 否 | 亲验 |
| ⑤哨兵在岗判**红**的 4 环节：FF-08 / FF-10 / FF-16 / FF-17 | 4 环节 | **同根因**于 z-sentinel 车道在治的"哨兵按 `ingest_ts` 而非业务日期判滞后"（议息日历停更 323 天而 breach=0）——转报，本腿未复跑其取证 | **不新立**，交叉引用 z-sentinel | 高 | 否 | 转报 |
| ④下游能取判**红**：FF-13 横切机制层（唯一④红环节） | FF-13 | 待归簇——尺子未给到消费者级明细，本腿预算内未下钻 | **标未复测**，交下一轮 | 中 | 否 | 推断 |
| `FF-12→FF-02` 上游落点表本就缺失（尺子明判"基线红必须记在该跳自己头上"） | FF-12 | 属普查 **C 族（空表/无数据）**邻域，但对象未被逐条列出 | 待与 C 族 20 条逐条对 | 高（聚合下游，R-024 点名跳） | 否 | 转报 |

**净结论**：尺子确实扫出了普查**装不下的新族**——「②转化能跑：入口 import 期即崩」。
普查 A 族（孤儿/零入度）与 B 族（零调用生产者）都只判"有没有人调"，
**从不判"被调会不会当场炸"**；上面 3 条（V3-N01/N02，共 5 次实测复现）全是"有人建了、也确实被当入口跑、但一跑就死"，
落在 A/B 两族的**检出面盲区**里。这是本次归簇最实的增量，也是"尺子不是白造的"的证据。

## 2. 对普查的**四态重判**（R-026 八型失效 → 四态）

本腿**只给亲验过的条目下判**，其余如实标 `未复测`。四态判据：
`仍成立`=原始命令复跑，输出与普查申报一致；`已闭合`=复跑后违规对象消失；
`归属错`=对象存在但挂错环节/错族；`口径不符`=数字对不上或判据不同，不能直接可比。

| BRK | 普查申报 | 本腿复跑命令与实测输出 | 四态 |
|---|---|---|---|
| BRK-001 | GOMAP counts `{total 416, wired 244, wired_dynamic 6, wired_by_header 71, suspect_orphans 95}` | `yaml.safe_load(config/governance_operations_map.yaml)['counts']` → **逐字段完全一致 416/244/6/71/95** | **仍成立**（亲验） |
| BRK-048 | 硬编码 fail-open 开关 5 处 | `grep -rE "fail_open\s*=\s*True\|fail_open:\s*bool\s*=\s*True\|FAIL_OPEN" src/zephyr` → **count=5**，但 5 处全在 `src/zephyr/security/llm_defense/llm_security/gateway.py` 的 `FAIL_OPEN_LAYERS={"l6_observability","l7_validation"}`，是**显式命名的可观测层设计**、非散落的开关赋值 | **口径不符**（亲验）——计数对得上但语义不是普查说的那种"硬编码开关"；建议改判为"LSG 观测层 fail-open 设计是否合理"这一命题 |
| BRK-049 | 吞异常：裸 `except Exception:` 62 处 / `pass` 144 处 | `grep -rnE "except Exception:\s*$" src/zephyr --include=*.py \| wc -l` → **62** | **仍成立**（亲验，与验收仪⑥向静态"静默放行候选 324 处"是**不同口径**，勿混用：尺子那 324 含 AST except-pass + debug 放行 + 恒真门 + `.get(k,True)` + 投递前置闩五模式） |
| BRK-050 | `tasks.yaml` 262 任务、DAG 缺失 | `yaml.safe_load(...)['tasks']` → **n=264**（+2） | **口径不符**（亲验）——任务数已漂（战役在途新增），"DAG 缺失"这一判据本身本腿未复算 |
| BRK-051 | 死任务空挂 4 件（`schedule: disabled`） | 复算 `schedule=='disabled'` → **4** | **仍成立**（亲验） |
| BRK-052..055 | `config/flags.yaml` 四项 flag 面 | 未复跑（`flags.yaml` 属本车道禁写且战役有别的车道在动） | **未复测** |
| BRK-002..046, 056..085（余 79 条） | 孤儿分族 / 空表 / 死管线 / 无锚点 / 域注册表一致性 等 | **本腿轮数预算内未逐条复跑** | **未复测**（不猜判；R-019 要求"动前先复跑"，未复跑即不下判） |

四态计数（**仅本腿亲验的 5 条**）：仍成立 **3** / 已闭合 **0** / 归属错 **0** / 口径不符 **2** / 未复测 **80**。
→ 这个分布本身就是给 Max 的可信基线入口：**普查 85 条里，到本腿为止被独立复跑过的只有 5 条。**

## 3. 必须保住的骨架复核结论（防重构丢失）

`03_omission_crosscheck.md` §5 的结论，本腿已复验其原文存在（亲验，行 95–98）：

> 骨架『未归属=0』**不成立**——是**人工兜底后的 0**，非机械派生的 0。
> 异名机械归一**之后**仍有：`B_functional_domain_registry` 未归属 **2 项**
> （`D_ORDER`, `D_PORTFOLIO`）；`F_docs_03_modules_dirs` 未归属 **10 项**
> （`D_DATA_GOVERNANCE`, `D_DATA_SECURITY`, `D_EXECUTION_CORE`, `D_EXECUTION_SIM`,
> `D_INFRASTRUCTURE_OPERATIONS`, `D_INFRASTRUCTURE_RUNTIME`, `D_PLAN_ENGINE`,
> `D_PORTFOLIO_CORE`, `D_RED_BLUE_VALIDATOR`, `D_SIGNAL_QUALITY`）。

本腿把该结论**搬进本文件**，理由：尺子第 1 笔落地时 `flowthrough_verifier.py` 经历了
"回填被误删常量块"的重构（见 `lanes/verifier3_relay_start.md` §3），
03/04 两件产物仍是**未跟踪文件**，有被并发窗口扫掉的前科（本会话已亲历一次）。

## 4. 交叉引用（不重扫，避免与在途车道撞车）

- **z-silent**：⑥向五模式扫描与 z-silent 的"闩前置/恒真返回/只写不读"五模式**高度同族**。
  尺子的 324 处是**检出面**不是**裁定**；已落地的 `a9b3e039db`（z-silent 六处收口）会使其数字下降，
  故本文件**不将该 324 立为 BRK**，等 z-silent 收口后由尺子复扫出差值才有意义。
- **z-arch**：#ARCH-338..356 案卷（`lanes/arch_338_356_dossiers.md`，55KB）与本表无重叠对象。
- **z-sentinel**：`data_supply_sentinel.yaml` / `quality_sentinel*.py` 归其独占，本腿**只读未改**。
