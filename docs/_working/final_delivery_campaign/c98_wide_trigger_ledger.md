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

## C98 施工结果注记（st-finaldel-c98-20260930，2026-09-30，Owner 批"按建议执行"）

> 三批落地：一批 own-diff 通道 4 台、二批触发面收窄 5 台、三批条件化/登记 4 台、维持 2 台。
> 验收铁律全过：重放对拍三窗（一批 204 对/二批 192 对/三批 168 对，共享窗口径）阻断判定全程零漂移、新 fail 零；
> 阴性样例 5+9+4=18/18 仍拦；套件 98+26r5+57 绿；ruff/compile 净；每批独立一袋（一批 q-…-0001、二批 8a1ecdc6、三批 q-…-0002）。
> 触发面读数（台账复算口径，收窄前→收窄后，2026-09-30 HEAD=18,720 文件）：
> R5 14,529→14,529（登记维持）｜STATE-VOCAB 9,374→3｜GATE-DOMAIN-FK 9,102→9,102（音化防未来噪声）｜
> FILE-COPY/FUNCTION-DUP/COMPLEXITY-GUARD/UNSAFE-DICT-SPREAD 各 9,102→9,102（同上）｜MAP-ALIGNMENT 4,844→1,438｜
> SCRIPTS-IMPORT 1,384→1,150｜REF-INTEGRITY 8,641→8,536｜DEPGRAPH-FRESH 5,467→5,440｜
> RECONCILER-HEALTH 2,625→18,720（显式无条件=加严修复 86% 漏检）｜RECONCILER-FILE-OPS 1,375→1,378（维持）｜
> BLOOD-FLESH 4,934→4,935（维持）｜ASYNCIO 3,785→3,784（维持）。
> 耗时估计（触发面≈触发频次代理+单次成本）：静态消除噪音触发 ≈9,371+3,406+234+105+27=13,143 次/全树窗，
> 另 FILE-COPY 对照面单次 79ms→18ms（4.4x，rglob→git ls-files 既有索引）且剥离 71 个盘面暂态 .py 误报源；
> RECONCILER-HEALTH 反向 +16,095 次×1 读查询（fail-open，ms 级）=防护修复成本。

| # | gate_id | C98 施工注记 |
|---|---------|-------------|
| 1 | R5-DIGIT-SUFFIX | 登记执行（经复核维持宽触发）：A/R 改型否决——index 锚定盲化 worktree 落地路径（防护损失）且常态反增 1 次 subprocess=变慢；门现状 suspect 集空即返=常态零 git 调用；§3.3+perf §2.6 结构校验型登记已落名册行注 |
| 2 | STATE-VOCAB-REGISTRY | 按建议执行：9,374→3（vocab 真源前缀+册精确路径）；warn-only 门阻断面恒零，未登记词表类阴性样例仍检出 |
| 3 | GATE-DOMAIN-FK | 按建议执行：.py→*.py+门实现 own 化（_split_own_foreign，外来 staged warn+审计）；own_scope 名册字段 false→true 机生归真；假域阴性样例仍阻断 |
| 4 | FILE-COPY | 按建议执行：触发面 .py→*.py 音化；对照面 rglob 全树→git ls-files 既有索引（"新文件 vs 全库"语义保留，79ms→18ms=4.4x）；实现原已 own-scope（2026-09-23）复核确认；复制阴性样例仍阻断+干净对照过 |
| 5 | FUNCTION-DUP | 按建议执行：.py→*.py；实现原已 own-scope 复核确认；own_scope 名册字段归真；同体兄弟函数阴性样例仍阻断 |
| 6 | COMPLEXITY-GUARD | 按建议执行：.py→*.py（own_scope 原已 true）；cc>15 新增函数阴性样例仍阻断 |
| 7 | UNSAFE-DICT-SPREAD | 按建议执行：.py→*.py（own_scope 原已 true；warn-only 检出即防护）；**data 新增行阴性样例仍检出 |
| 8 | REFERENCE-INTEGRITY | 条件化执行：docs/ 前缀→门内 REFERENCE_TEXT_EXTS 六文本类型 fnmatch（8,641→8,536）；门本就 own-diff（只核 commit files 新增 §X.Y 引用）复核确认+登记；悬空引用阴性样例仍阻断 |
| 9 | DEPGRAPH-FRESHNESS | 条件化执行：删「depgraph」裸子串（5,467→5,440，纯 docs/册名散文噪音）；src/+scripts/ 语义域保留+§3.3/§2.6 结构校验型登记 |
| 10 | BLOOD-FLESH | 经复核维持（理由）：own_scope=true 已合宪，触发面=翻译覆盖义务域（TRANSLATION-COVERAGE）结构性全模块面，判可接受成立，零改动 |
| 11 | MAP-ALIGNMENT | 按建议执行：docs/03_modules/→*.md（4,844→1,438；实证 align_panoramas 只读 blueprint .md，非 .md 变更不影响对齐输出）；9 精确路径与门内 _TRIGGER_PATTERNS 镜像不变；own_scope false→true 归真 |
| 12 | ASYNCIO-RUN-IN-CONTEXT | 经复核维持（理由）：own_scope=true 已合宪，src/zephyr/*.py=AST 扫描意图边界，判可接受成立，零改动 |
| 13 | RECONCILER-HEALTH | 显式无条件化执行（W-135 NO-BARE-GETENV 先例）：「governance」裸子串系历史意外口径——门自身 [INVARIANTS] 即 always-on，裸子串反致 86% 提交漏检健康检查；本改=诚实口径属加严非放松；单次=1 次 governance.db 读查询（fail-open） |
| 14 | SCRIPTS-IMPORT-INTEGRITY | 按建议执行：scripts/→scripts/*.py（1,384→1,150，enabled=false 台卫生收窄，台内仍只查 scripts/governance/**/*.py own-scope） |
| 15 | RECONCILER-FILE-OPS | 经复核维持（登记执行）：四前缀=意图边界；门运行时本就 own-diff（只扫 commit files∩前缀逐文件全文），触发面=扫描域镜像非全仓扫描；§3.3/perf §2.6 登记已落名册行注 |

> 边界声明：本注记只记施工事实，注册表真源=in_process_gate_registry.yaml（CAS 机生通道），统一册=generate_gate_registry.py 机生；
> 重放证据=.runtime/tmp/st-finaldel-c98-20260930/{baseline,after_batch1,after_batch2,after_batch3}/verdicts.jsonl（各 480 行）。
