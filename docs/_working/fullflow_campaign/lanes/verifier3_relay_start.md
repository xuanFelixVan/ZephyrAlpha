---
ttl: task_bound
completes_when: 全流通战役收官（验收仪尺子连续两轮 0 新断点）
---

# verifier3 接力起点盘点（T0）— sid=`st-ff-verifier3-20260918`

> 本文件是**据实重列**的断点清单，来源=本会话亲验命令，不含总包任务书的转报前提。
> 总包任务书自陈其 R-024 段含幻觉，故本文对每条 T 项都标了「成立/伪命题/已被前腿做完」。

## 1. 亲验方法与关键命令（Max 可直接复跑）

```bash
# 磁盘件 vs 死件 blob 是否同一版本
python -c "import hashlib,pathlib;[print(p,hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()[:16]) \
  for p in ['scripts/automation/flowthrough_verifier.py']]"
# 用门禁自身的检测器直验（不猜判据）
python -c "import sys;sys.path.insert(0,'src');from zephyr.gov_enforcement.commit_gates.\
vocab_chain_gate import _detect_ssot_hardcoding;import pathlib;print(_detect_ssot_hardcoding(\
'scripts/automation/flowthrough_verifier.py',pathlib.Path('scripts/automation/flowthrough_verifier.py').read_text(encoding='utf-8',errors='replace')))"
# 未定义名（半截文件判定）
python -m pyflakes scripts/automation/flowthrough_verifier.py | grep "undefined name"
```

## 2. 前腿遗留的真实状态（与总包任务书的差异已标注）

| 事实 | 实测值 | 依据等级 |
|------|--------|---------|
| `lanes/verifier2_relay.md` | **不存在**（第二腿未写接力说明） | 亲验 |
| 两件 .py 是否在 HEAD | **否**（`git ls-tree HEAD` 无匹配）→ 尺子不受版本保护 | 亲验 |
| 磁盘 `flowthrough_verifier.py` | 122,655B @ **20:09** | 亲验 |
| 死件 blob `6a93d49e…` | 2,311 行 @ **20:04:36** | 亲验 |
| **磁盘 ≠ blob** | 磁盘比 blob **新 5 分钟**，差 5 行，且只差**一个 hunk**（83–152 区） | 亲验 |
| 第一腿报 11 passed | 已失效（第二腿改了测试） | 转报（不采信） |
| **第二腿真实通过数** | **21 passed / 0 failed**（本会话亲跑） | 亲验 |

## 3. ★ 核心发现：第二腿不是「没做完」，是「做完了但把文件改坏了」

`dead_reason` 现值（**非快照**，本会话重读 `.runtime/commit_queue/dead/q-20260918-st-ff-verifier2-20260918-0001.json`）
的完整违规点 = **2 条**，非截断：

```
"docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml"
"docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml"
```

但**磁盘件（20:09）里这两条已经不存在了**：第二腿在入队（20:04）之后继续编辑，
自己把 VOCAB-CHAIN 死因解掉了——改成经 ROOR（`docs/registry_of_registries.yaml`，
RULE-REGISTRY 唯一真源）反查 `registry_id → physical_path`，并新增 `_source_rel_path()`
逐源如实标发现方式（`ROOR:<id>` / `catalog_dir_fallback(ROOR 无此册)` / `literal(非治理册)`）。

**代价**：那笔编辑的 `old_string` 过长，连带误删了一整块模块级定义
（`DOC_MODULES_DIR`/`SKELETON_MD`/`SCAN_EXCLUDES`/`TABLE_LITERAL_RE`/`SINK_HINT_RE`/
`CONSUMER_HEADER_RE`/`SKIP_RUN_RE`/`DATE_COL_RE`/`SQL_DEPGRAPH_SIZE`/`SQL_DEPGRAPH_DOMAINS`/
`SQL_STAGE_CONSUMERS`/`SQL_MODULE_CONSUMERS` + `FlowthroughProbeContext` 数据类 + `_sha256()`），
造成 **13 个未定义名 / 8 件测试红**（首个崩点 `NameError: SKELETON_MD`）。

→ **「前腿半成品可安全续用」的判断=可续用，但须先回填被误删块**（依据等级：**亲验**——
blob pyflakes 干净 + 磁盘 pyflakes 报 13 未定义名 + 差集恰为那 12 常量+1 类+1 函数，
且只 1 个 hunk，无第三处改动）。
回填后：py_compile 双件通过、pyflakes undefined-name=0、**21 passed**、VOCAB-CHAIN 检测器返回 `[]`。

## 4. 据实重列的 T 项状态

| T 项 | 总包任务书说法 | 实测 | 本腿动作 |
|------|--------------|------|---------|
| 「修 --prove-red 两处漏检（4/6 精确指名）」 | 说是缺陷 | **伪命题**（总包自陈 R-024 幻觉）。但第二腿仍把它做成了 **A 族 12 跳逐跳 12/12 精确指名**，`--hop-count` 默认已=12 ≥ 要求的 10 | 不"修"，只复跑验证 |
| 「93 项新断点与普查 85 条归簇」 | 说是需求 | **"93" 这个数是编的**；但真实需求成立（自扫红项未被 01 覆盖） | 按真实条数做（见 T3） |
| T1 解 VOCAB-CHAIN | 待做 | **死因已被第二腿解掉**，只是文件被改坏 | 回填 + 落地 |
| T2 ⑤哨兵在岗 / ⑥失败会响 | 待做 | 第二腿均已实现（⑤独立 `sentinel_verdict`、allow_empty 不许判绿；⑥显式标 STATIC + `dynamic_injection=False`） | 验证，不重做 |
| T4 论域声明硬约束 | 待做 | 第二腿已实现 `universe_guard`（缺块写盘前抛 `UniverseDeclarationError`），有测试 `test_universe_guard_rejects_report_without_declaration` | 验证 |

**新发现的、任务书未列的真缺陷**（本会话亲验）：
1. `MOD-AUTO-L3-002(暂编号)` 双重不合规：BLUEPRINT 位带 `(暂编号)` 后缀被门判死；
   且 `MOD-AUTO-L3-002` **已被 HEAD 里的 `scripts/automation/source_card_drafter.py` 占用**（撞号）。
   → 改取 `MOD-AUTO-L3-003`，撞号事实留 `[PROVISIONAL]` 注记。
2. sanctioned 工具 `add_module_translation.py` 已坏：
   `ImportError: DEFAULT_REGISTRY_CATALOG_DIR from scripts/governance/_shared/yaml_utils`
   （符号在 SSoT `src/zephyr/shared/io/yaml_utils.py:48` 存在，shim 漏 re-export）。
   → 本腿绕行 CAS 通道登记；工具修复**出处方**（禁改他人共享件）。
3. `REG-BATTLE-MAP-DOMAIN-POLICY` 实测**不在 ROOR**，且 `battle_map_domain_policy.yaml`
   自身未声明 registry_id → 尺子走 `catalog_dir_fallback` 并**自标**，非伪装 ROOR 命中。
   补 ROOR 登记涉他车道独占热文件 → 出处方。
4. **施工期文件被扫**：本会话两件 .py 在 20:23 后一度从磁盘消失（同时 `git log -1` 显示
   z-silent 的 `a9b3e039db` 落地）。**未丢**——从本会话死件的 blob（sha256 自验通过）恢复。
   教训：未落地的未跟踪成品在并发窗口内是**可被扫掉的**，只有进 HEAD 才算交付。

## 5. 落地进度

- 尺子落地=第 1 笔（`flowthrough_verifier.py` + 测试 + `module_translation_registry.yaml` 同批）。
- 文档批次=第 2 笔（`lanes/verifier3_relay_start.md`、`lanes/verifier3_relay.md`、`skeleton/05_census_reconciliation.md`）。
