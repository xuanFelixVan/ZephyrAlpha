---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s9
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S9 挂起 suspended"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S9 行）
---

# D15-S9 挂起 suspended（卡生命周期十三态之九）

## 1. 定义

- 语义（词表 value=suspended）：裁定延后重考并带显式触发条件，禁被读成通过。
- 状态机属性：非终态；credential_required=true；machine_readable=no；`config/strategy_card_lifecycle_map.yaml#D15-S9`（build_status=partial）。
- 禁边挂钩：X10 S9→S6 把挂起读成通过（凭裁定#404 R2"禁直通模拟盘"；机验规格=挂起态卡若被 E7/E8 节点引用即红，跨图检查）。
- 全图唯一实例：P3-E1C-09（登记面 suspended 恰 1 条）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M14 S8→S9（actor=human，credential_required=ruling，gated=true，必填 trigger 表达式，✅ observed=P3-E1C-09） | `config/strategy_card_lifecycle_map.yaml#D15-M14`；`ruling_registry.yaml`（裁定#398 条目 :3052 起 / 裁定#404 条目 :3137 起，R2 原文"E1C-09 判挂起并入 IBT 批D 新鲜窗重考…触发=样本显著增厚或下个预注册考试窗"）；`docs/_working/integrated_backtest/max_remediation_plan.md` |
| 输出面 | M15 S9→S5（actor=machine，trigger 达成，**禁改卡**要改=新卡，⬜ 零活体——宪法 §9.3 事件触发铁律下的必建面）；M16 S9→S13 | `config/strategy_card_lifecycle_map.yaml#D15-M15/#D15-M16`；`AGENTS.md` §9.3（自动触发/自动运行/自动维护/自动关闭；禁 cron/Timer/sleep-loop） |
| SSOT 真源 | 双面冲突现行：登记面 suspended（宿主册 CARD-P3-E1C-09 card_state: suspended）对卡面 `docs/_working/archive/2026-09/kimi_audit/lane_reports/p3_prereg/P3-E1C-09.md:9` status 仍 frozen（F-03 原型） | `experiment_registry.yaml`（CARD-P3-E1C-09 条目，family_id=P3-E1C-STABLE13，n_eff=13）；卡面文件实存（本批核验） |
| 代码模块 | 零实现：M15 的 trigger 求值器、重考入队、卡面回写器均无；近似构件=`src/zephyr/governance/lifecycle_governance/`（治理生命周期域）与 `src/zephyr/factor/governance/lifecycle_state_machine.py`（因子生命周期状态机，跨域不并） | `ls src/zephyr/governance/lifecycle_governance/`、`src/zephyr/factor/governance/lifecycle_state_machine.py`（实存，本批核验；无 card-state 触发件） |
| 门禁约束 | X10（CV-07 规格，跨图检查挂作业簿 06 未落地）；触发条件入册强制（M14 credential 已含）；CV-10 活违规：校验器实跑 `CV-10——P3-E1C-09 卡面镜像 frozen ≠ 登记真源 suspended` | 校验器 2026-10-15 实跑 ERROR 输出；`config/strategy_card_lifecycle_map.yaml#D15-X10` |
| 自动化触发 | 无。触发条件（样本显著增厚/下个预注册考试窗）是散文表达式，无求值器；重考启动靠 IBT 批D 人工排程 | `ruling_registry.yaml` 裁定#404 R2 触发条款（散文）；max_remediation_plan.md 批D 排序（人工时间线） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | M14 唯一实例凭证链完整（裁定#398 R2+#404 R2 双裁定、trigger 表达式在册、n_eff=13 同根说明齐） |
| 输出面 | warn | 唯一前进口 M15 零活体（挂起卡无限期滞留）；void 口从未用 |
| SSOT 真源 | fail | F-03 原型+CV-10 活违规：裁定改了地位、卡头一字未动（"卡说它在 S3，裁定说它在 S9"），且方向条款（册→md）无回写执行器 |
| 代码模块 | fail | 本态的自动化面（trigger 求值+事件触发重考）完全缺位，而这是骨架标 P3 里唯一带"必建"注记的边（M15：宪法 §9.3 铁律下必建） |
| 门禁约束 | fail | CV-10 活违规在册未处置；X10 跨图检查未落地；"禁直通模拟盘"靠裁定文本自律 |
| 自动化触发 | fail | trigger 表达式无求值器、无事件源挂接（重考窗开启是人工排程） |

## 4. 缺口与建议

1. 缺口（本态最硬）：CV-10 ×1 活违规（P3-E1C-09 卡头 frozen）。修复=卡头一行补丁+宿主册已就位（方向册→md），随 S7 同款处置批量做。
2. 缺口：M15 必建面零实现。最小可行件=批D 名单生成时（人工动作既有）以事件回调查宿主册 suspended 行、命中年内考试窗即置 candidate 提示（不做自动跑数，符合 §9.3 与 Owner 门位）；不建议上 cron 轮询 trigger。
3. 建议：trigger 表达式结构化——把"样本显著增厚/下个预注册考试窗"落成宿主册 trigger 字段的结构化枚举（sample_thickening/next_exam_window），求值器才有输入；现 schema 该信息只在 credential note 散文里。
