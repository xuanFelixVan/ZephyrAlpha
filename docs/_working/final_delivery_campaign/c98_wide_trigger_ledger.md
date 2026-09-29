---
ttl: task_bound
title: "C98 门禁触发面超宽台账（files_trigger ≥1000 全表，generator 口径实测）"
session: st-finaldel-lists-20260930
completes_when: "Owner 逐行勾选收窄口径后，另批施工收窄；本台账只读不改注册表"
---

# C98 · 门禁触发面超宽台账（ Owner 裁定用）

> **工卡**：`docs/_working/final_delivery_campaign/workorders_governance.md` L31（C98，OWNER_GATE，M+Owner）
> **依据（HEAD）**：`docs/_working/wave13_chief3/LEDGER_chief3.md` L119（§6.4 N-3）；`docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`（total_gates=178，本清单零改动）
> **口径（生成器/运行时同源）**：匹配语义=`src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py:280` `_files_trigger_hit` 四路 OR（目录前缀/精确/fnmatch/子串）；文件全集=`git ls-tree -r HEAD --name-only`（=18,706，与 `gate_auto_registrar._head_tracked_relpaths` 同口径）；超宽阈值=`gate_auto_registrar.py:135` `_OVERWIDE_WARN_THRESHOLD=1000`（"死触发/超宽=warn 不拦"观测簿通道）。
> **HEAD 复测 vs LEDGER N-3**：N-3 记"≥8 台、1,354–8,937 文件"→ 本表实测 **15 台、1,375–14,517**（+7 台、TOP1 1.6 倍），超宽面在扩大，佐证 N-3"存量连坐成本源"判断。
> **复算命令**：
> ```bash
> export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
> python - <<'PY'
> import fnmatch, subprocess, yaml
> files = subprocess.run(["git","ls-tree","-r","HEAD","--name-only"],capture_output=True,text=True).stdout.splitlines()
> hit = lambda rel,p: (p.endswith("/") and rel.startswith(p)) or rel==p.rstrip("/") or fnmatch.fnmatch(rel,p) or p in rel
> d = yaml.safe_load(open("docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml",encoding="utf-8"))
> for g in d["gates"]:
>     ft=g.get("files_trigger") or []
>     pats=[ft] if isinstance(ft,str) and ft else list(ft)
>     if pats and sum(1 for f in files if any(hit(f,p) for p in pats))>=1000:
>         print(g["gate_id"], sum(1 for f in files if any(hit(f,p) for p in pats)), pats)
> PY
> ```

## 台账（15 台，按触发面降序；own_scope=名册机生字段，True=源码含 `_build_own_scope` 即 own-diff 作用域）

| # | gate_id | 触发面定义（files_trigger 原文） | 实际文件数（占全仓） | own_scope | 建议收窄口径 | 风险评级 |
|---|---------|--------------------------------|---------------------|-----------|-------------|---------|
| 1 | R5-DIGIT-SUFFIX | `['docs/', 'scripts/', 'src/', 'data/']`（4 目录前缀） | 14,517（77.6%） | False | 条件化+登记：门内部已是增量检测（只查本次 commit 涉及目录的 `_\d+$`，单次成本极低），维持结构校验型宽触发但须按宪法 §3.3 登记"全仓扫描"理由+perf 分级；或收窄为目录结构变更事件语义 | 中 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 2 | STATE-VOCAB-REGISTRY | `['src/', '.py']` | 9,371（50.1%） | True | 收 glob：词表真源仅 `src/zephyr/shared/vocab/`（HEAD 实测 2 文件）+词表册文件；建议收窄到 `src/zephyr/shared/vocab/` 前缀+册精确路径，其余 src 变更与本门无关 | 中 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 3 | GATE-DOMAIN-FK | `['.py']` | 9,099（48.6%） | False | own-diff 化+收 glob：引 `_build_own_scope`（宪法 §3.1 内容扫描默认）；`.py` 裸子串改 `*.py` fnmatch（子串语义误伤非代码路径） | 高 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 4 | FILE-COPY | `['.py']` | 9,099（48.6%） | False | own-diff 化（必收）：内部 subprocess 调 `check_code_duplication` 真源查重，宽触发=凡含 .py 的提交即全量查重，15 台中单次成本最高 | 高 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 5 | FUNCTION-DUP | `['.py']` | 9,099（48.6%） | False | own-diff 化+收 glob：同 #3（`.py`→`*.py`+own_scope 化） | 高 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 6 | COMPLEXITY-GUARD | `['.py']` | 9,099（48.6%） | True | 收 glob：own_scope 已合宪（§3.1）；建议 `.py`→`*.py` 消子串误伤面 | 低 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 7 | UNSAFE-DICT-SPREAD | `['.py']` | 9,099（48.6%） | True | 收 glob：同 #6（own_scope 已合宪，`.py`→`*.py`） | 低 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 8 | REFERENCE-INTEGRITY | `['docs/']` | 8,630（46.1%） | False | own-diff 化：引用完整性检查应只扫本次变更文件的引用面（引 `_build_own_scope`）；`docs/` 前缀可保留（检查对象本就是 docs 引用网），但作用域必须 own-diff，否则任何 docs 提交全量扫 | 高 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 9 | DEPGRAPH-FRESHNESS | `['src/', 'scripts/', 'depgraph']` | 5,466（29.2%） | False | 条件化：depgraph 新鲜度天然随代码面=结构性超宽候选（按 §3.3 登记理由保留）；`depgraph` 裸子串项与 src//scripts/ 前缀高度重叠且命中 docs/册名散文，建议删除或收 `*depgraph*.py` | 中 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 10 | BLOOD-FLESH | `['src/zephyr/*.py', 'scripts/*.py', 'docs/.../module_translation_registry.yaml']` | 4,934（26.4%） | True | 判可接受（登记）：own_scope 已合宪；触发面=翻译覆盖天然全模块面（TRANSLATION-COVERAGE 义务域），结构性超宽登记即可 | 低 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 11 | MAP-ALIGNMENT | `[9 个 schema/apply/generate 精确路径 + 'docs/03_modules/']` | 4,839（25.9%；其中 docs/03_modules/=4,830，占 99.8%） | False | 收 glob/own-diff 化：`docs/03_modules/` 整目录前缀是超宽主因，改 own-diff（只核本次变更 blueprint 的对齐键 module_id/step_id）或收窄到被改模块对应子树 | 中 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 12 | ASYNCIO-RUN-IN-CONTEXT | `['src/zephyr/*.py']` | 3,785（20.2%） | True | 判可接受：own_scope 已合宪，模式即意图边界（src 生产代码 AST 扫描） | 低 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 13 | RECONCILER-HEALTH | `['governance']`（裸子串） | 2,621（14.0%） | False | 条件化：检查本体查 governance.db reconciler 状态、不读 staged 文件内容；`governance` 裸子串命中 docs 576+src 407+scripts 748 全是噪音——改 `always_run` 显式化（诚实口径）或收窄到 reconciler registry/配置文件 | 中 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 14 | SCRIPTS-IMPORT-INTEGRITY | `['scripts/']` | 1,382（7.4%） | True | 收 glob：own_scope 已合宪；`scripts/`→`scripts/*.py`（现含 yaml/md 噪音触发） | 低 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |
| 15 | RECONCILER-FILE-OPS | `['src/zephyr/governance/', 'src/zephyr/gov_enforcement/', 'scripts/governance/', 'scripts/backup/']` | 1,375（7.3%） | False | 判可接受（登记）：四前缀=意图边界，1,375 是目录体量的自然结果；如需降噪可 own-diff 化 | 中 —— **Owner 勾选：☐同意建议 ☐其他（注明）** |

## 汇总

- **超宽台数**：15 / 178 台（LEDGER N-3 时点 ≥8 台 → HEAD 15 台，面在扩大）。
- **TOP3 触发面**：①R5-DIGIT-SUFFIX 14,517 ②STATE-VOCAB-REGISTRY 9,371 ③`.py` 五连台 GATE-DOMAIN-FK/FILE-COPY/FUNCTION-DUP/COMPLEXITY-GUARD/UNSAFE-DICT-SPREAD 各 9,099。
- **建议分布**：own-diff 化 4 台（#3/#4/#5/#8，均 own_scope=False 内容扫描门）｜收 glob 5 台（#2/#6/#7/#11/#14）｜条件化/登记结构性超宽 4 台（#1/#9/#13/#15）｜判可接受 2 台（#10/#12）。风险 高 4 / 中 7 / 低 4。
- **边界声明**：本台账只读 `gate_registry.yaml`/`in_process_gate_registry.yaml`（两册 files_trigger 逐台一致已互证），零册面改动；收窄施工=Owner 按行勾选后另批（注册表净改/翻 flag 属 Owner 门位，见 workorders_governance L93）。
- **runtime 同证**：`gate_auto_registrar._warn_suspect_triggers` 每 commit 对同口径超宽台 emit warn（观测簿通道，"先可见再治理"）；registrar 内注记录的观测值 governance=2377/docs=7858/.py=8764 与本表 governance=2,621/docs/=8,630/.py=9,099 同量级漂移，均为真。
