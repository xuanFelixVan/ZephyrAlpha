---
ttl: task_bound
title: F95 OBJ 四对象线设计面——挖干案卷
session: zc-l10-20260927
---

# F95 · OBJ 四对象线设计面（OBJ_M/T/S/R）

> 总册行（00_全环节总册.md:165）：design（31 项待 Owner 处置总表在案）｜上游 F94｜下游 施工批次｜P1
> 第一证据源：docs/_working/ai_layer_vision/OBJ_{M_models,T_tools,S_perimeter,R_rules_standards}/DESIGN.md ＋ README.md §3.5

## 一、六向台账（实证锚点）

| 向 | 实测证据（本日复核） |
|---|---|
| 上游输入 | F94 七段循环（对象轴走同一条循环，README §1.5）；OBJ_M 上游=L1 模型轨+Owner 手递（OBJ_M DESIGN §1①）；OBJ_T 上游=L1 源注册表+MCP 官方 Registry（OBJ_T DESIGN §1①） |
| 下游消费 | OBJ_M→config/model_routing_policy.yaml 12 轨+task_gate 护照；OBJ_T→L4 §2.1 工具行+L6 蓝绿；OBJ_S→负面清单机检+两 KillSwitch 分界；OBJ_R→宪法 §4 季度退役审计+ruling_registry |
| 自动化触发 | 设计态零运行件；OBJ_R 铁律"自动化的是提案和证据，不是裁决"（OBJ_R DESIGN 卷头原话） |
| 真源与注册表 | 四 DESIGN.md 全 design_v1（frontmatter 实证）；待 Owner 处置总表=README.md §3.5（152-249 行） |
| 门禁与质量尺 | OBJ_S 四总原则（尺与持尺分离/机检静态判据/fail-closed 与 fail-open 分界/两 KillSwitch 勿混用，OBJ_S DESIGN §0）；OBJ_R 重放判据=拦截集合 Jaccard（R5 裁定） |
| 当前运行状态 | **design 态**；施工碎片先行件：OBJ_R S1+S2（rule_replay）已由 gov 会话 3ac3af3faac 落地（LEDGER_final 接管账向一）；OBJ_R S3 提案骨架 76 常量（31 纳入/45 排除留痕）在 staging obj_r_s3_proposal.md（P1_final_report:98） |

## 二、子模块三级枚举（四对象线）

1. **OBJ_M 模型线**（M1-M5 五件）：源清单 12 源/权重（三 config 已进 v2 清单：model_intel_sources/model_scoring_policy/dual_run_criteria，LEDGER R2 件1）；三把尺=能力考试+同任务双跑+成本审计；§3.3 三口径互斥维持 B7 呈批；施工面 PG ai_layer_model 3 表实存但 registry/price_history=0 行（m4 01 §三.OBJ_M）。
2. **OBJ_T 工具线**（T1-T6 六件）：考尺=Tier B 有限样本档（效应量+区间+未决不硬判）+too-good 触发线 100% 含陷阱题；落点=config/mcp.json+tool-contracts.yaml 契约 SSoT v1.2.0+resource_profile_registry 排班画像；非 MCP 工具 manual_v0 诚实兜底（C2 补计量）。
3. **OBJ_S 红线与自由域**：主文档附录 C 六条"永不触碰"机检化+删除分级三档点名真源生成器+双指标看板（项目安全/不亏钱）；**不发明新刹车**——复用 immutable_core/KillSwitch/五级交易熔断/RULE-GIT-SAFE/REGISTRY-MASS-DELETION，新建件仅补缝；施工面=redline 九件（negative_list NL-1..6/三 gate 149/150/151 已挂 in_process 册 enabled:true，m4 01 §3.8 实证）。
4. **OBJ_R 标准与规则线**：四步流水线=AI 提案→治理立案→Owner 修标→重考历史；历史重放器第一优先（P1-P4+Jaccard 主判据）；S3 提案 76 常量施工归 gov 车道；同构母版=alert_threshold_registry+threshold_loader fail-closed 改造（R3 横查）。

## 三、接线四态独立复核

- 总册判 **design**：独立复核成立——四 DESIGN.md status 全 design_v1，无 OBJ 专属生产代码包（OBJ_S 的 redline 九件属 F87 落地件，是 OBJ_S 设计的部分先行实现）。
- **骨架勘误**：总册"31 项待 Owner 处置总表在案"口径易误读。README.md:154/205 实证：**31 项=处置总表全量对账（已销 17＋治理立案保留 9＋真待 Owner 5）**，非 31 项全待 Owner；P1 执行口径另记"待 Owner 批文 12 项/受阻 3 项"（P1_final_report:114）。三口径（5/12/31）引用时须注明镜头。

### 施工最小集建议（design done 未施工）
1. **OBJ_S 先行收尾**：redline 三 gate 已挂网（唯一在产 OBJ 件）；剩负面清单条目生成器化（禁手写计数）+annual_review 月检接线。
2. **OBJ_R 重放器 P3/P4 接数据**：gate_execution_stats.jsonl（.runtime/audit/）为触发率燃料；S3 提案随 gov 车道批次施工。
3. **OBJ_T 计量补齐**：manual_v0→gate_execution_stats/telemetry_server/failures 三源自动计量（C2 施工项）。
4. **OBJ_M B7 三口径互斥**呈批裁决后再排 C3/C6（路由增轨前置=OBJ_M-#1 Owner 终批，P1_construction_plan:101）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| G1 | OBJ_M/OBJ_T/OBJ_R 三线零生产件（仅 OBJ_S redline 先行） | 按施工最小集 1-4 排批；OBJ_R 归 gov 车道 | P1 |
| G2 | 真待 Owner 5 项+P1 批文 12 项催批 | Owner 门位，禁代裁（README §3.5 真待 Owner 表） | P1 |
| G3 | 待 Owner 口径三镜头（5/12/31）无单一字段化真源 | 生成器产出对账段（挂 README §3.5 重生成） | P2 |
| G4 | OBJ_T 基准可靠性三防（考卷版本化+判据冻结+陷阱题）未落机检 | OBJ_T DESIGN §1⑥ 已定调，随 T 线施工落地 | P2 |

## 五、自审闸三态

**设计面=挖干可施工**（四稿六向台账齐、施工项带验收标准）；**处置分晓=待裁**（真待 Owner 5 项+P1 12 项均 Owner 门位）；**本车道=零写动作**（只读挖矿，禁代裁禁施工）。

## 六、复跑命令

```bash
for d in OBJ_M_models OBJ_T_tools OBJ_S_perimeter OBJ_R_rules_standards; do grep -m1 "^title:" "docs/_working/ai_layer_vision/$d/DESIGN.md"; done
sed -n '152,156p;195,205p' docs/_working/ai_layer_vision/README.md   # 31 项对账=17+9+5
sed -n '114p;98p' docs/_working/ai_layer_vision/P1_final_report_20260924.md  # 批文 12 项/受阻 3 项；S3 76 常量
sed -n '707,725p' docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml  # OBJ_S 三 gate 149/150/151
```
