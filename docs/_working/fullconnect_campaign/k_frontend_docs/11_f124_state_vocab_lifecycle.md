---
ttl: task_bound
title: "F124 状态词表生命周期（REG-STATE-VOCAB-001 + STATE-VOCAB-REGISTRY 执法门）复飞案卷"
session: st-c7-mine-20260927
---

# F124 状态词表生命周期（K 段，P0，骨架态=unmined(new id)）

> 立卷依据：`00_skeleton_verified.md` §二 B-12 行——"REG-STATE-VOCAB-001 状态词表册（GATE-VOCAB 实拦无主）→ F124（P0，K 段，词表生命周期）"。
> 本卷首要结论：**"实拦无主"已不成立**——执法门在盘、已注册、已在提交链装载；真实缺陷是**它的硬阻断腿没有供给方**（模式常量为模块级硬编码，无 config 读取路径），因此当前只处于 warn 观察态。

## 一、六向台账（2026-09-27 实证，基准=HEAD 3b4b1f86a1）

| 向 | 实测证据 |
|---|---|
| 实现件 | 三件套全在盘且 `git cat-file -e HEAD:` 通过：①登记册 `docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml`（634 行，`vocabularies` 数组长度=**63**，§六 M2 实算）；②执法门 `src/zephyr/gov_enforcement/commit_gates/library/state_vocab_registry_gate.py`（16087 B，AST 启发式扫描）；③官方常量代码镜像 `src/zephyr/shared/vocab/market_state.py`（头注 :6/:9/:10 自述"新增状态值必须先登记 state_vocabulary_registry"）。 |
| 上游输入 | 语义真源=`docs/_working/vocab_legislation/01_official_state_vocabulary.md`（册头 :4 指认）＋存量普查 `docs/_working/vocab_legislation/02_state_vocabulary_mapping_register.md`（:5）；两册均 task_bound 工作区件。册头 :7 自宣"本册不新造任何状态值：所有 values/tokens/映射逐字取自上列两件已立法文件"⇒ 派生态，非第二真源（合规于 RULE-SSOT）。 |
| 下游消费 | 唯一运行时消费者=执法门自身：`state_vocab_registry_gate.py:97` `STATE_VOCAB_REGISTRY_REL_PATH = "docs/…/state_vocabulary_registry.yaml"`，:252 产 finding，:302 出 warn 文案。门的上游装载=`src/zephyr/gov_enforcement/commit_gates/__init__.py:70-71`（`from …library.state_vocab_registry_gate import make_state_vocab_registry_gate as _make_…`，带 `# noqa: F401` 装载注释）。M1 台账 dir4 仅采到 config-reader=门自身一腿。 |
| 测试 | `git ls-tree -r --name-only HEAD \| grep -iE "test.*state_vocab\|state_vocab.*test"` = **0 件**（§六 T1）。⇒ 执法件零测试锚点，本卷判为硬缺口（见 §四 缺 1）。 |
| 自动化触发 | 事件触发=每次提交（in-process 门，非 cron）：`gate_registry.yaml:1311` `- gate_id: STATE-VOCAB-REGISTRY`、:1312 记 `priority=135`；`in_process_gate_registry.yaml:646` 同 id 在册。豁免通道在册=`noqa_exempt_registry.yaml:438` `marker: "STATE-VOCAB-REGISTRY"`（:439 `metric_id: null`）。 |
| 真源与注册表 | ROOR `docs/registry_of_registries.yaml:252` `- registry_id: REG-STATE-VOCAB-001`，name=状态词表中央登记表，`format: yaml`，`maintenance: manual`。真源方向（册头 :3 原文）="立法件=语义真源，本册=机读登记真源，market_state.py=官方常量的代码镜像"——三态分层清晰，无环向倒挂。 |
| 门禁与质量尺 | 门自身即尺；但**观察期形态**：`state_vocab_registry_gate.py:94` `STATE_VOCAB_GATE_MODE = "warn"`（模块级 Final 常量），:308 `if STATE_VOCAB_GATE_MODE == "block":` 是唯一硬阻断分支。fail-open 面在 `fail_open_register.yaml:3320/3326/3332/3338/3344/5889` 共 6 处登记（AST 解析失败/文件读失败/注册表缺失均放行）。own-scope 依据=根宪法 §3.3（门头注 :8 原文引用）。 |
| 当前运行状态 | **warn 态在跑（真留痕、不阻断）**。审计留痕面在写（门 :302 文案路径），commit 结果不受影响。 |

## 二、子模块三级枚举

1. **登记层**（REG-STATE-VOCAB-001）
   - 二级=册结构：`schema_version`(=1) / `registry_id` / `name` / `status`(=active) / `maintenance` / `created_by_lane` / `ruling_basis` / `scope_statement` / `vocabularies[]`（§六 M1 实读键序）
   - 三级=`vocabularies` 63 条目：每条一套状态词表（类名或模块路径锚）+ values/tokens 逐字取自已立法两册；`entry_count` 为派生标量，册头 :8 明示由生成器/总筹按数组长度重算、禁手改散文（根宪法 §4.3 计数铁律）
2. **执法层**（state_vocab_registry_gate.py）
   - 二级=判定链：staged∩own-scope 取集 → AST 解析 → 启发式识别"新定义状态枚举类"（类名关键词 + 全大写成员计数）→ 查登记（类名或模块路径出现在册）→ 命中放行／未命中出 finding
   - 三级=四条逃生/失败面：①行级 noqa 豁免（`STATE-VOCAB-REGISTRY` 标记 + 原因，注册在 `noqa_exempt_registry.yaml:438`）；②`_audit_foreign_staged` 外来件只审计不阻断（根宪法 §3.1）；③AST/读文件失败 `logger.warning` 后 fail-open；④注册表缺失或损坏 fail-open（缺失仅 debug 级）
   - 二级=出口二态：warn（现值）→ 留痕+放行；block（:308 分支）→ 硬阻断，**当前不可达**（见 §三）
3. **代码镜像层**（`src/zephyr/shared/vocab/market_state.py`）
   - 二级=SH-VOCAB-001 官方常量；三级=`:9 [INVARIANTS] 纯常量零逻辑零IO`、`:10 [MODIFY-GUARD] 新增/改名状态值前置=state_vocabulary_registry.yaml 登记`、`:131` 注释回指登记册——镜像与登记册的先后序由纪律注释而非机检保证（§四 缺 3）。

## 三、接线四态独立复核

- **登记件 = 已接线**：被门以常量路径读取（:97），路径实核存在；M1 台账 config-reader 腿独立采到同一件，两侧一致。
- **执法门装载 = 已接线（但证据强度需说明）**：`commit_gates/__init__.py:70` 是**运行时真实 import**，不是 `if TYPE_CHECKING:` 块内导入——本卷按 AST 逐件区分（脚本口径见 §六 W1）；该行的 `# noqa: F401` 是"装了但不直接引用名字"的装载型 noqa，属**接线**不属装饰，区别于典型的 TYPE_CHECKING 装饰态。
- **硬阻断腿 = 装饰（本卷核心判读）**：`STATE_VOCAB_GATE_MODE`（:94）为模块级字面量 `"warn"`，全仓 `git grep -n "STATE_VOCAB_GATE_MODE" HEAD -- ':!tests/*'` 仅命中定义行、`__all__`(:91) 导出与比较行(:308)——**无任何 config/env/flag 读取方给它供值**。⇒ :308 的 `block` 分支是**永不进入的死码**，"未来 config 翻转"目前在盘上没有翻转通道。按本仓判据（守卫无供给方=装饰），本环节须记为"warn 面真执法 / block 面装饰"，不得整环节判已接线。
- **在册名实漂移（在册态瑕疵）**：`capability_canonical_file_registry.yaml:44084` 登记的是 `src/zephyr/gov_enforcement/commit_gates/state_vocab_registry_gate.py`（**已不存在**，门已移入 `library/` 子目录，见门头注 :8 的"0046-prime 移 library/ 子目录"自述与 :45504 的新路径条目）。⇒ 同一文件在权威文件册里同时挂着"死路径 + 活路径"两条，旧条目=死引用。
- **无判据失效证据**：本门属 `fail_open_register.yaml` 显式登记的 6 处 fail-open 面，登记本身合法；但 fail-open + warn-only 叠加 ⇒ 本环节当前对提交结果的影响恒为零，这是**设计意图（观察期）**而非缺陷，须与"判据失效"区分记账。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 执法门零测试（§六 T1 实测 0 件）：启发式识别、noqa 豁免、own-scope 剔除、fail-open 四腿全无红样 | 施工：补 `tests/gov_enforcement/commit_gates/test_state_vocab_registry_gate.py`，四腿各至少一红一绿；输出走 tmp_path | P0 |
| 2 | block 腿无供给方（装饰态）：`STATE_VOCAB_GATE_MODE` 硬编码 warn，:308 分支不可达 | 施工（供值通道）+ Owner 门位（翻转出厂值）：先补 config 读取腿，再由 Owner 决定 warn→block；根宪法 §5 明列"flag 出厂翻转 → Owner"，本道不得代翻 | P0 |
| 3 | 三态真源链无对账尺：立法件↔登记册↔`market_state.py` 镜像的一致性靠注释纪律，`align_all.py` 单入口未见本三元组 | 施工：把三态比对并入 align_all 的字段级对账族（与 F126 缺 1 同批，共用一把尺） | P1 |
| 4 | `capability_canonical_file_registry.yaml:44084` 死路径在册（旧位置未清） | 施工：随下次权威册再生清除；禁手工点删（热文件必经 safe_write_text，根宪法 §1.13） | P2 |
| 5 | `entry_count` 派生标量在 63 实测下是否已同步册面散文值，本卷未逐字段核 | 挂起：属权威册一致性面，交治理侧尺子统一判 | P2 |

## 五、自审闸三态

**未干。** 已穷尽的部分：三件套实现件全锚（含 ROOR/门注册/豁免注册三处在册态行号）、装载腿与装饰腿的 AST 级区分、供给方缺失的证伪、fail-open 全量登记点计数。未穷尽的部分：①`vocabularies` 63 条目**未逐条**与立法件 01 对字（需整册 diff，属词表重裁面，本道明确不重开——六段词表已裁，勿再动）；②门在真实提交链上的**运行留痕样本**未采集（需构造 staged 新枚举类跑一次 in-process 门，本夜为避连坐未做）；③缺 1 的红样设计需与治理门车道对齐落点，未在本卷定稿。这三件任一未闭即不足以盖"挖干"。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
# M1 三件套在 HEAD
for p in docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml \
         src/zephyr/gov_enforcement/commit_gates/library/state_vocab_registry_gate.py \
         src/zephyr/shared/vocab/market_state.py; do git cat-file -e HEAD:$p && echo "OK $p"; done
# M2 词条数（期望 63）与册顶层键序
python -c "import yaml,io;d=yaml.safe_load(io.open('docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml',encoding='utf-8'));print(list(d)[:8]);print('n_vocab',len(d['vocabularies']))"
# W1 装载腿是否装饰（期望：__init__.py:70 为 runtime import，非 TYPE_CHECKING 内）
python -c "
import ast,io
f='src/zephyr/gov_enforcement/commit_gates/__init__.py'
t=ast.parse(io.open(f,encoding='utf-8').read())
tc={m.lineno for n in ast.walk(t) if isinstance(n,ast.If) and 'TYPE_CHECKING' in ast.dump(n.test) for m in ast.walk(n) if isinstance(m,(ast.Import,ast.ImportFrom))}
for n in ast.walk(t):
    if isinstance(n,ast.ImportFrom) and 'state_vocab' in (n.module or ''): print(n.lineno,'TC' if n.lineno in tc else 'RUNTIME')"
# S1 模式常量供给方缺位自证（期望：只有定义/导出/比较三处，无 config/env 读取）
git grep -n "STATE_VOCAB_GATE_MODE" HEAD -- '*.py' '*.yaml' 'config/*'
# G1 在册态三处
grep -n -A2 "STATE-VOCAB-REGISTRY" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | head -6
grep -n "STATE-VOCAB-REGISTRY" docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml
grep -n "STATE-VOCAB-REGISTRY" docs/01_policies_and_standards/_registry/catalogs/noqa_exempt_registry.yaml
grep -n -A2 "REG-STATE-VOCAB-001" docs/registry_of_registries.yaml | head -5
# F1 fail-open 登记计数（期望 6）
grep -c "library/state_vocab_registry_gate.py" docs/01_policies_and_standards/_registry/catalogs/fail_open_register.yaml
# T1 测试面（期望 0）
git ls-tree -r --name-only HEAD | grep -iE "test.*state_vocab|state_vocab.*test" | wc -l
# D1 死路径在册自证（期望 44084 那条存在、文件不存在）
sed -n '44084p;45504p' docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml
test -f src/zephyr/gov_enforcement/commit_gates/state_vocab_registry_gate.py && echo UNEXPECTED || echo DEADPATH
```
