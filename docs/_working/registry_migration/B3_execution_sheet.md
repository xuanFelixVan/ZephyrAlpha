---
ttl: task_bound
title: "W-M1 B3 切换批施工单（只备不投——执行权在 5.3 总筹）"
session: st-wm1-cutover-20261003
completes_when: "5.3 总筹执行 B3 后归档"
---

# B3 切换批施工单（cutover：YAML 降级只读投影 + parse_gate 武装）

> 备单=st-wm1-cutover-20261003（2026-10-03）；执行=5.3 总筹。
> 备单纪律遵守声明：本单制备全程未改 ROOR 一字节、未执行任何 render、未生成 parse_gate 状态文件、未投任何 B3 commit（三不红线）。
> 前置已就绪（本班 B1/B2 实证）：reconcile_20261003_165937.json = **Phase 0 PASS 七册全绿（pg_only=0，yaml=pg 逐册相等）**——render(PG) 与盘面 YAML 语义零差已达，cutover diff 预期=纯格式归一噪音（jsonb 键序+键排序）+ 头部 verbatim 保持。

## 前置决策点（执行前必须裁定，本单给推荐）

| # | 决策 | 推荐 | 理由 |
|---|------|------|------|
| PD-1 | 投影状态文件**单槽**限制 | 方案①state v2 map 化 | 实勘：`state.py` 的 `registry_projection_state.json` 一次只挂一册（`registry_path` 单数），belt 探针也只 render `default_registry()=REG-CAPCAN-001`。逐册 render 七册会互相覆盖槽位，parse_gate 私改检测只罩最后一册。方案①=state.py 小改（map 按 registry_path 键控+向后兼容读旧单册形态），净零申报=替代单槽形态；方案②=首波只武装 CAPCAN、六册投影翻转但私改检测留 wave-2（诚实缺口，可接受但须呈明）；方案③=每册一份状态文件（改 STATE_REL 命名+gate 读法，改动面大于①，不推荐） |
| PD-2 | 三册不在 ROOR 的补登记 | 随 B3 批补登三条完整 entry（maintenance 直写 pg_ledger） | 实勘：REG-MODULE-TRANSLATION-001/REG-CAND-001/REG-RULING-001 三册 ROOR 无条目（82 册实测无 ID 无路径命中）。render 本身不需要 ROOR（`load_latest_snapshot` 直收 physical_path），但 maintenance 翻转无行可改=册面失真。核对总图 A-2"35 未册补登"已批范围与执行态，若已执行完则本三条走同一批文精神补登（RULE-RULING 同 commit 原子） |
| PD-3 | dual_track.enabled 旗处置 | B3 同批摘旗（随批记录） | 双轨使命（Phase 1 对账）在 cutover 后由 parse_gate+reconcile 接管；旗留存无执法副作用（reconcile 幂等 noop）但语义已失效。若 5.3 想保守，可保留观察一周再摘，二选一呈明即可 |
| PD-4 | reconcile CLI 旗自恢复小件 | B3 批内顺手施工（约 6 行） | **尚未内建**：2026-10-02 旗被 .runtime TTL 清扫吃掉的教训（LEDGER §修订行）留卡未施工——`wave0_phase0_gate.py reconcile` 与 belt `_dualtrack_reconcile_if_armed` 均只读旗不补挂。补法=reconcile 入口检测旗缺失→safe_write_text 补挂+告警行 |

## a) ROOR 七册 maintenance→pg_ledger 逐行精确 diff 预览

**写法纪律**：ROOR 热册，全部 `safe_write_text` CAS（`expected_base_sha256` **执行时现取盘面哈希**，禁用本单任何快照值）；编辑按 `registry_id:` 块锚定匹配，禁裸行号定位（上方插入会使行号移位）；每次编辑后断言 vs 编辑前零 minus（除目标行本身）。

四册在册（行号=2026-10-03 盘面参考值，仅助定位）：

```diff
  # REG-DOC-001（L287）
- maintenance: manual
+ maintenance: pg_ledger

  # REG-ARCH-ISSUE-001（L439）
- maintenance: manual
+ maintenance: pg_ledger

  # REG-CAPCAN-001（L452）
- maintenance: semi-auto（canonical 声明=manual；扫描=auto via CapabilityLookup.__init__）
+ maintenance: pg_ledger（canonical 声明=manual；扫描=auto via CapabilityLookup.__init__；2026-10-03 cutover 起文件=YAML 只读投影，条目写路径唯一入口=意图 API registry_ledger.api）

  # REG-ERRCODE-001（L483；physical_path=architecture_model/contracts/error_code_registry.yaml）
- maintenance: manual
+ maintenance: pg_ledger
```

三册不在册（PD-2）：REG-MODULE-TRANSLATION-001（docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml）、REG-CAND-001（同目录 candidate_module_registry.yaml）、REG-RULING-001（同目录 ruling_registry.yaml）→ 按 tiers[1] 既有 entry 形态补登（registry_id/name/physical_path/format: yaml/tier_1_governance/maintenance: pg_ledger/entry_count 用 reconcile_20261003_165937.json 实值 8748/623/294/counting_rule/status: active/ssot_for 对齐七册清单）。

## b) 投影全量重打七册命令序列

**路线二选一**：**推荐 A=逐册 `run()` 循环**（零新代码、逐册报告可隔离失败）；B=新建 `--render-all` CLI（否：一次性用途新增常驻 CLI 面违净零 §4，循环驱动即等价能力）。

**时序硬约束**（03 号文 §5 原文，执行前逐条核）：①提交队列排空（`python scripts/commit_queue.py status` 在途=0，drain 完）——在途袋携带旧基底快照，cutover 后整文件落地会覆盖投影；②PD-1/PD-2 已裁定；③执行窗内广播让道（各会话暂停注册表写）。

```bash
# 第 1 步：七册快照全量重发（render 的 source=None 走 load_latest_snapshot，
# 不重发会渲染陈旧快照——本班 B2 退役了 197 条，旧快照必然过期）
python scripts/governance/registry_migration/wave0_phase0_gate.py publish
# 核对 publish 报告 entry_count == reconcile_20261003_165937.json 实值：
# CAPCAN 13078 / TRANSLATION 8748 / DOC 298 / ARCH-ISSUE 815 / ERRCODE 800 / CAND 623 / RULING 294
```

```python
# 第 2 步：逐册 render（路线 A 驱动；<sid> 换 5.3 总筹会话名）
from pathlib import Path
from zephyr.governance.registry_ledger.baseline import p0_physical_paths, scan_registry_file
from zephyr.governance.registry_projection.projection_generator import run

root = Path('.')
for phys in p0_physical_paths(root):
    rid = scan_registry_file(root, str(phys))["registry_id"]
    rpt = run(root, mode="render", registry_id=rid, physical_path=str(phys),
              actor_session="<sid>")
    print(rid, rpt.ok, rpt.quadrant, rpt.wrote, rpt.detail)
    assert rpt.ok and rpt.quadrant in ("clean", "stale", "private_edit", "conflict"), rpt
# 语义注记：状态文件缺失时首跑走 _armed_initial_write（写 YAML+建状态），
# 已武装则走四象限处置（全自动：stale/private_edit→PG wins 重写+证据留档）。
```

```bash
# 第 3 步：批自检——reconcile 应零事件 noop-PASS（投影==账本的闭环证明）
python scripts/governance/registry_migration/wave0_phase0_gate.py reconcile
# 第 4 步（红蓝）：任取一册手改一行→commit 应被 REGISTRY-YAML-PARSE 拦（armed 实弹）→revert
```

## c) parse_gate 武装步骤 + 旗自恢复说明

- **武装机制**：`registry_yaml_parse_gate.py` 的投影私改检测读 `.runtime/projection/registry_projection_state.json`——文件缺失/损坏/registry_path 不符=**fail-open 零行为**（未武装）；文件在且匹配=armed（staged≠投影态→阻断+教学报错）。**状态文件没有独立生成命令**：由第 2 步首个 `mode="render"` 的 `_armed_initial_write`/`_commit_state` 自带生成（safe_write CAS）。核对命令：`cat .runtime/projection/registry_projection_state.json`，断言 `registry_path`/`content_sha256` 与目标册一致。
- **单槽限制=PD-1**：现状一次只挂一册（实勘 `state.py` STATE_REL 单文件单 registry_path），七册全武装必须先落 PD-1 方案①（或显式接受方案②的缺口）。
- **旗自恢复**：**未内建**（PD-4）——2026-10-02 教训留卡在案；B3 执行前若不施工小件，则每轮执行前手工核对 `test -f .runtime/registry_ledger/dual_track.enabled`（摘旗裁定后本项作废）。

## d) 原子落地批文件清单 + 提交命令

**文件清单**（执行 PD-1①+PD-2 口径）：

1. `docs/registry_of_registries.yaml`（a 节 4 行翻转+3 条补登）
2. 七册 YAML（b 节 render 重打；一次性排序/格式归一 diff；若单册净删超阈按家法带 `[allow-mass-deletion:投影归一…_semantics by CAS]` 标记）
3. `src/zephyr/governance/registry_projection/state.py`（+配套测试；PD-1①时）
4. `scripts/governance/registry_migration/wave0_phase0_gate.py`（PD-4 旗自恢复小件，若施工）
5. 本台账 LEDGER_wave0.md 收尾行

```bash
python scripts/git_commit.py --session <sid> --files \
  docs/registry_of_registries.yaml \
  docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml \
  docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml \
  docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml \
  docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml \
  architecture_model/contracts/error_code_registry.yaml \
  docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml \
  docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml \
  src/zephyr/governance/registry_projection/state.py \
  tests/governance/registry_projection/test_state_v2.py \
  scripts/governance/registry_migration/wave0_phase0_gate.py \
  docs/_working/registry_migration/LEDGER_wave0.md --enqueue
```

**回滚**（02 号文 §4 Phase 3 表引用）：回滚点=cutover 前一 commit（revert 即回手工态）；PG 侧账本保留不回滚只停用渲染；末次快照 `render_yaml` 可全量重生成翻回。**关联件备忘**（W4 设计原文，5.3 勿漏）：合并器白名单退出、generator_registry 登记（db: 输入投影语义）、REG-GEN-001 并条（P-5 已批）、消费方加载器切 PG 快照（逐册）。

## 附：本单事实来源（复算口）

- reconcile 终验=`.runtime/registry_ledger/reconcile_20261003_165937.json`（Phase 0 PASS）
- 单槽状态文件实勘=`src/zephyr/governance/registry_projection/state.py:44-100`；belt 单册探针=`commit_belt_daemon.py:416-436`
- parse_gate fail-open 面=`src/zephyr/gov_enforcement/commit_gates/registry_yaml_parse_gate.py:109-143`
- render 管道=`projection_generator.py:289-352`（unmanaged 短路/四象限/`_armed_initial_write`）
- ROOR 行号实勘=2026-10-03 盘面（REG-DOC-001 L287/REG-ARCH-ISSUE-001 L439/REG-CAPCAN-001 L452/REG-ERRCODE-001 L483；三册缺登 grep 实证）
