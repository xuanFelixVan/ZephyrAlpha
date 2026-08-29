---
blueprint_id: MOD-VOTE_REVIEW_SHELL
module_name: vote_review_shell
domain: D_AUTONOMY_CORE
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-29
last_updated: 2026-08-29
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_AUTONOMY_CORE
path: src/zephyr/intelligence/reflexion/vote_review_shell.py
granularity: file
---

# MOD-VOTE_REVIEW_SHELL vote_review_shell 蓝图（投票评审壳）

> **module_id**: MOD-VOTE_REVIEW_SHELL | **域**: D_AUTONOMY_CORE | **优先级**: P1
> **设计真源**: 12号文 `docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/12_reflexion_multi_agent.md` §3.6（多Agent协作设计·可选模式设施）+ §4.3 P1-2（投票评审壳）/P1-4（多会话投票 SOP）
> **裁定**: #ARCH-OE-011（CC-14 投票优先降级为可选模式；主路径=单 Agent + red_blue_validator）
> 代码：`src/zephyr/intelligence/reflexion/vote_review_shell.py`

## 0. 定位

可选模式设施（**非主路径**）：高价值评审场景（如因子入库终审）需要多候选裁决时
由人手动启用。人多开 3-5 个 AI 会话（或多模型 API 并行）各自产出候选并互投，
本壳收齐候选文件 → 调既有 A2AVoting 引擎（MOD-INF-025，approve/reject/abstain +
quorum + 权重，**只消费不改结构**）逐候选计票 → 最优候选落盘 `selected/` → 裁决
报告 JSON。产出 100% human_gated：报告仅供人终审，壳不自动应用胜出候选。

主路径边界（#ARCH-OE-011）：solo 单 session 单 Agent 决策 + red_blue_validator
红蓝对抗为常驻主路径，本壳**默认不启用**，无任何自动触发路径（无调度器/定时器/
钩子/导入副作用，唯一入口=人手动 CLI）。

## 1. 处理阶梯

`run_review(candidates_dir, output_path, *, quorum=0.5, engine=None) -> dict`：

1. 收集候选：`<candidates_dir>/candidates/*` → candidate_id = 文件名 stem；
2. 收集选票：`<candidates_dir>/votes/*.json`（每会话一份：agent_id/weight/
   votes{candidate_id: approve|reject|abstain}）；
3. 逐候选计票：`engine.open_proposal(cid)` → 各会话 `cast_vote`（会话缺投记
   warning 续跑；指向缺失候选的票记 warning 忽略；非法动作 fail-closed 抛
   VoteReviewError）→ `engine.tally(cid, participant_count=选票数)`；
4. 裁决：仅 quorum_met 且 passed（approve>reject，引擎口径）候选可胜出；多名
   通过按 (净票, approve_weight) 取最优，同分取 candidate_id 字典序最小
   （确定性 tiebreak）；
5. 落盘：胜出候选复制 `<报告目录>/selected/`；裁决报告 JSON 写 output_path。

## 2. 接口

```python
DEFAULT_ROOT: Path                       # MAIN_REPO_ROOT/.runtime/vote_review
class VoteReviewError(RuntimeError)      # 目录缺失/选票非法/非法投票动作, fail-closed
@dataclass(frozen=True) SessionBallot: agent_id/weight/votes
run_review(candidates_dir, output_path, *, quorum=0.5, engine=None) -> dict  # 裁决报告
main(argv=None) -> int                   # 人手动 CLI 唯一入口:
    # python -m zephyr.intelligence.reflexion.vote_review_shell
    #   [--candidates-dir DIR] [--output FILE] [--quorum 0.5]
```

报告字段：verdict（selected/no_consensus/no_candidates/engine_error）/
generated_at/quorum/participant_count/candidates[]（逐候选计票明细含 votes）/
winner/selected_file/warnings/error/human_gate_required（恒 true）。

## 3. 不变量

- 壳体 <100 行纯编排（口径：tokenize 剥离纯注释行 + ast 剥离 docstring 后的
  非空物理行数，含 import/声明行；实测 97，见施工报告）。
- 引擎复用零改动：只消费 MOD-INF-025 公开接口（open_proposal/cast_vote/tally/
  VoteAction/VotingResult），不改其源文件（git diff 佐证）。
- 无自动触发路径：唯一入口为人手动 CLI；无调度器/定时器/钩子/导入副作用
  （静态扫描佐证）。
- 候选/选票目录缺失、选票文件非法、非法投票动作 → VoteReviewError
  （fail-closed，不产半成品报告）。
- 引擎异常 → 降级 verdict="engine_error"，已计票明细+错误落盘交人，不抛出。
- 无候选通过（quorum 不足/平票 approve≤reject）→ no_consensus 不选优。
- 产出 100% human_gated：壳不自动应用胜出候选，终审权在人。

## 4. 依赖

- MOD-INF-025 A2AVoting（`zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_voting`，**只消费既有公开接口**；测试注入 mock 覆盖异常降级）
- zephyr.shared.io.paths（MAIN_REPO_ROOT，默认 .runtime/vote_review 根）
- zephyr.shared.utils.time_utils（now_utc_str 报告时间戳）
- 标准库：argparse/json/logging/shutil/dataclasses/pathlib

## 5. SOP（P1-4 多会话投票操作规程，可选模式）

### 5.1 启用边界（先判再启用）

- ✅ 启用：高价值评审场景需多候选裁决（因子入库终审/关键策略稿评审等），
  人判定主路径（单 Agent + 红蓝对抗）产出分歧大或风险高时。
- ❌ 不启用：日常决策一律走主路径（solo + red_blue_validator）；本壳默认
  关闭、无自动触发；不为省人力常驻多会话（协调成本 > 质量收益，
  #ARCH-OE-011）。

### 5.2 操作步骤（全程文件交接，禁口头/截图传递）

1. **出题**：人把评审题目+评分维度写成 `brief.md`，放入
   `.runtime/vote_review/<评审组名>/`（评审组名=本次评审唯一标识）。
2. **分发**：人手动开 3-5 个 AI 会话（或多模型 API 并行），把 brief 内容
   分发给各会话；各会话独立产出候选。
3. **候选落盘**：每个会话交付两份文件——
   ① 候选产出 `…/<评审组名>/inbox/candidates/<candidate_id>.<ext>`
   （candidate_id 自定唯一，建议会话标识前缀）；
   ② 选票 `…/<评审组名>/inbox/votes/<session>.json`：
   `{"agent_id": "<会话标识>", "weight": 1.0,
     "votes": {"<candidate_id>": "approve"|"reject"|"abstain", …}}`
   规则：每会话必须对**全部**候选投票（含对自家候选，建议 abstain）；
   weight 缺省 1.0（人可在选票文件里调权重，如给更强模型 1.5）。
4. **收齐检查**：人确认 candidates/ 与 votes/ 文件齐全（3-5 份选票），
   无缺失再计票——不齐不收（quorum 语义依赖 participant_count=选票数）。
5. **计票**：人手动执行
   `python -m zephyr.intelligence.reflexion.vote_review_shell
    --candidates-dir .runtime/vote_review/<评审组名>/inbox
    --output .runtime/vote_review/<评审组名>/report.json`
6. **终审**：人读 report.json——verdict=selected → 胜出候选在 `selected/`，
   人终审后才可应用；verdict=no_consensus（quorum 不足/平票）→ 不采纳任何
   候选，回到 1 重跑或改走主路径；engine_error → 查 error 字段。
7. **归档**：`<评审组名>/` 整个目录（brief/candidates/votes/report/
   selected）保留备查，不删除——审计链=文件链。

### 5.3 异常处理

- 某会话未交付 → 等齐，或人裁定剔除该会话（删除其 votes 文件后计票，
  participant_count 随之变化）。
- 选票指向缺失候选 → 壳记 warning 忽略该票，人查 warning 追因。
- 平票/quorum 不足 → no_consensus 为正常产出而非故障，交人裁定。

## 6. MVP 边界（Phase 1）

- 验收：3 候选构造集跑通 approve/reject/abstain+quorum 全路径（测试覆盖）；
  MOD-INF-025 源文件零改动（git diff 佐证）；壳体行数实测 <100；无自动触发
  路径（静态扫描佐证）。
- 不做：自治多Agent辩论循环（30号文 §5 暂缓）；FactorMAD 式对抗互评
  （Phase 2 P2-2，人发起）；自动触发/定时评审；胜出候选自动应用；LLM 通道
  对接（会话产出由人搬运落盘，壳不呼叫任何模型）。
