---
ttl: task_bound
title: F94 AI 层七段循环设计面——挖干案卷
session: zc-l10-20260927
---

# F94 · AI 层七段循环设计面（L1-L7 段卡+主文档 v2.0）

> 总册行（00_全环节总册.md:164）：design（全 design_done 未施工；L1 施工项 7 受 T3 双前置）｜上游 —｜下游 F86 施工｜P1
> 第一证据源：docs/_working/ai_layer_vision/（真源）＋ fullflow_mining/m4_ai_layer/01_ai_layer_six_families.md

## 一、六向台账（实证锚点）

| 向 | 实测证据（本日复核） |
|---|---|
| 上游输入 | 设计面无代码上游；定调真源=ai_layer_vision/README.md §1（七段一常数，Owner 2026-09-17 夜批 13 条，主文档 ai_layer_vision_and_roadmap_v1.md v2.0 active）＋§1.5 三轴一具（引擎×对象×运营）＋§1.6 与业务层四轴并轨（同一块治理底板） |
| 下游消费 | F86 施工面（src/zephyr/ai_layer/ 9 子包）；F95 四对象线走同一条七段循环（README §1.5 对象轴表）；施工排产消费 evolution_schedule_seeds |
| 自动化触发 | 设计面零运行件；循环本身要求事件驱动（L1 外扫+内监为点火器，README §1） |
| 真源与注册表 | 七段卡=L1_perceive..L7_heredity/ 各 README.md+DESIGN.md；段卡 status 全 design_done（L1 README.md frontmatter 实证 status: design_done） |
| 门禁与质量尺 | 设计内嵌纪律：L4 判据预注册/公平性三轴 fail-closed 拒考（L4 DESIGN §4 C5）；OBJ_R 四步流水线管尺子（不自我迭代，README §0.5 #8） |
| 当前运行状态 | **design 态**：V0/V1/V2 验证报告齐＋七段深挖毕；施工面状态见 m4 01 分册（黄：代码就绪但 187 件未落 HEAD、三 schema 未部署、常驻未点火） |

## 二、子模块三级枚举（设计面 7 段＋常数）

1. **L1 感知**（外扫+内监）：真源=L1_perceive/README.md（design_done 卡，§提及 9 施工项/三边契约/月检建议书 schema）；施工项 7=外扫节拍宿主，受 T3 双前置（Owner 追认+裁定登记）未解锁（m4 01 分册 §3.1 实证）。
2. **L2 收集**：L2_intake_library/DESIGN.md（原材料库生熟分离/MAP-Elites 保底）；施工面对应 intake 族（唯一已落 HEAD 族，ai_intake schema 13 表有真数据）。
3. **L3 清洗**：L3_cleaning/DESIGN.md（强模型洗/本地优先-API 分界/外部代码零执行）；施工面 cleaning 五件、washer 唯一 GATE-20 命中件合规挂 LSG。
4. **L4 对比**：L4_compare/DESIGN.md（协议层+登记层裁定 D-L4-01；C1-C8 八施工项+依赖序 C1→C2→C3→(C4/C5/C6)→C8）；施工面 comparator 五件+考场适配器×4 fail-closed。
5. **L5 排产**：L5_schedule_gate/DESIGN.md（门闸条件触发/配额/算力窗口）；施工面 scheduling 六件、order_daemon 设计常驻但无启动登记。
6. **L6 切换**：L6_ab_switch/DESIGN.md（champion/challenger 蓝绿/退役不删墓碑制/复活恒 shadow_recheck）；底层状态机真身 src/zephyr/intelligence/switch_engine/ 四件全在。
7. **L7 传承**：L7_heredity/DESIGN.md（回流闭环关键边）；施工面 heritage 五件，DDL 已部署 9 表但零数据。
8. **目标常数段**："更好"的真源不参与自迭代（防 objective hacking，README §1 图）；落地锚=预注册判据/Owner 口味（L4 C1 判据常量文件 comparison_policy.yaml 为其施工载体）。

## 三、接线四态独立复核

- 总册判 **design（未施工）**：独立复核成立。证据：ai_layer_vision 全目录 README.md:9-11 "L1-L7 段卡+OBJ 四条对象线均 design_done"；施工面 9 族仅 intake 落 HEAD（m4 01 分册 §3.2，git ls-tree HEAD=9 件）；进化主循环"件就绪、阀未开"手动/锁定态（m4 01 分册 §四结论原话）。
- **骨架勘误**：总册锚"docs/_working/ai_layer_vision/L1_perceive..L7_heredity/ 各 DESIGN.md"对 **L1 不成立**——L1_perceive/DESIGN.md 的 frontmatter title 实为"**L4 对比段——通用对比器真源设计稿 v1**"（本日 head 实证，与 L4_compare/DESIGN.md 同题不同文）；L1 段真源实为 L1_perceive/**README.md**（design_done 骨架卡）。引用 L1 设计须改指 README.md。

### 施工最小集建议（design done 未施工）
1. **落 HEAD**：187 件 v4 批按 landing_files_v4.txt 逐件对账 commit（非本车道可修，等队列畅通广播；LEDGER_final [06:3x] 恢复程序就绪）。
2. **DDL 部署三 schema**：ai_compare/ai_tools/ai_layer_scheduling（Owner high 门位点火 `--deploy`，m4 01 分册 §五.2）。
3. **常驻点火**：order_daemon 启动登记（事件驱动消费 SchedulingJournal，禁 cron）；登记 process_reaper_keep。
4. **L1 外扫节拍宿主解锁**：T3 双前置（Owner 追认+裁定登记）走裁定流程。
5. **heritage 通水**：首个真实工单闭环回填种子数据（m4 01 分册 §五.3）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| G1 | 七段循环全链未通水（阀未开） | 按施工最小集 1-5 排批 | P1 |
| G2 | L1_perceive/DESIGN.md 放错稿（L4 内容） | 待裁：改名迁移或 Owner 窗口归位（禁本车道动） | P2 |
| G3 | L1 设计卡与 DESIGN.md 双载体易断链 | 在 L1 README.md 头部加真源互指（施工批顺带） | P2 |
| G4 | 矿脉三挂点（depgraph 尾/align_all 尾 vein 再生钩）不在盘面 | m4 01 分册 §五.5 已登记；月检 vein_coverage 恒"产物缺失" | P2 |

## 五、自审闸三态

**设计面=挖干可施工**（七段真源全 design_done、六向有锚）；**施工面=待裁**（落 HEAD/DDL/点火三关均 Owner 门位或队列前置）；G2/G3 归档勘误待裁。

## 六、复跑命令

```bash
head -9 docs/_working/ai_layer_vision/L1_perceive/README.md        # L1 卡 status: design_done
head -9 docs/_working/ai_layer_vision/L1_perceive/DESIGN.md        # 勘误实证：title=L4 对比段
grep -m1 "^title:" docs/_working/ai_layer_vision/L*/DESIGN.md      # 七段 DESIGN 标题逐册
sed -n '150,160p' docs/_working/ai_layer_vision/README.md          # §3.5 待 Owner 处置总表入口
sed -n '88,92p' docs/_working/fullflow_mining/m4_ai_layer/01_ai_layer_six_families.md  # 阀未开结论
```
