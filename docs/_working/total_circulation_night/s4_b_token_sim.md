---
ttl: task_bound
session: st-circ-a6-20260930
batch: 第4批/A6 挖矿簿 2/6
---

# S4-B 手术单 — CREATE-GUARD 判重二阶段 token 相似度（#456 两档化之上加结构证据）

> 立档：2026-09-30 ｜ 车道：A6（design-only，不附代码）
> 真源文件：`src/zephyr/gov_enforcement/commit_gates/create_guard.py`、`src/zephyr/governance/capability_lookup.py`、`src/zephyr/shared/utils/diff_utils.py`

## 1. 现象量级（遥测实证）

- 现行判重单腿=关键词探针（stem/docstring 首段/类函数名 → `CapabilityLookup.find()`），命中后按字段两档分流（裁定 #456，已落地 864c71e6）：标识符级硬拦 / 散文级 warn。
- 账本实证：`commit_block_events.jsonl` 全量 `precommit_channel_blocked ×140`；CREATE-GUARD 相关 warn 账本=`.runtime/gate_audit/create_guard_keyword_dup_warn.jsonl`（#456 落地后散文级命中全在此）。**散文级=只 warn 不拦**，即第二真源若描述措辞避开探针、但代码结构同构，现行只产 warn——这是本单要补的结构证据缺口。
- 基线锚：裁定 #456 判重两档（864c71e6）、骨架「已落地基座」明确勿重做。

## 2. 机理锚点

| 位置 | 内容 |
|------|------|
| `create_guard.py:1109-1133` | `_probe_hits_identifier_fields`（#456 两档化的字段复检点）：标识符三字段（capability_id/aliases/canonical_file）拼接面按 find() 同款语义复检；复用 `lookup._tokenize/_token_match` 静态件，**只调用不改 capability_lookup.py** |
| `create_guard.py:1136-1180` | `_scan_file_for_keyword_dupes`：探针→find()→命中归并+两档分流；自引用/同批豁免；逃生标记豁免 |
| `create_guard.py:1057-1106` | `_build_keyword_probes`：查询面=stem+docstring 首段+顶层类/函数名，上限 `_MAX_KEYWORD_PROBES` |
| `create_guard.py:1182-1279` | `_check_capability_keyword_overlap`：硬拦 fail-closed / warn fail-open 分档出口；`:1263-1278` warn 出口=本单二阶段的挂载点 |
| `capability_lookup.py:892-950` | `find()`：五字段（capability_id+description+canonical_file+module_id+aliases）拼 haystack 检索 |
| `capability_lookup.py:952-1000` | `_tokenize/_token_match`（静态件，ASCII 词全在 + CJK ≥`_CJK_MIN_SUBSTRING=3` :134 滑窗）——既有 token 设施 |
| `diff_utils.py:246-256` | `similarity_ratio`（difflib.SequenceMatcher.ratio，stdlib）——既有相似度设施 |

**既有设施盘点（勿引新重依赖）**：AST=标准库 `ast`（create_guard 已用 `ast.parse` :1151）；token 切分=`_tokenize`；序列相似度=`diff_utils.similarity_ratio`。jscpd 的 token 滑窗指纹思路可用「AST 标识符有序序列 + SequenceMatcher」零依赖近似，语义足够判同构。

## 3. 设计（意图，不附码）

1. **触发面收敛**：二阶段只对 **#456 散文级 warn 命中**的条目触发（不是全库扫）——量级受控于 warn 账本，标识符级硬拦路径零触碰。
2. **结构证据**：对 (新建 .py 的 AST 标识符有序序列) vs (命中条目 canonical_file 的 AST 标识符有序序列) 计算 token 相似度（复用 `_tokenize` 切词 + `diff_utils.similarity_ratio`）；canonical 读不到/语法错误 → 维持现状 warn（fail-open，不新增放水也不新增拦）。
3. **档位判据先影子后定档**：一期**影子模式**（audit-only）：二阶段结果只落 `.runtime/gate_audit/create_guard_token_sim_shadow.jsonl`（相似度分布可查），不改任何判定；跑满一周取分布，再由 Owner 门位定硬拦阈值（禁止拍脑袋阈值直接上硬拦——对标 gate_cache_preflight 白名单「实测准入」纪律）。
4. **canonical 侧 token 序列缓存**：按 (canonical 路径, mtime_ns, size) 键控的进程内缓存（同款键型见 create_guard.py:734），避免同一 canonical 重复 parse。
5. **不动面**：探针构造、find() 检索语义、#456 两档现行阈值、逃生标记字面量、`_MAX_KEYWORD_PROBES`。

## 4. 红测两针

- **R-B1 同构改名漏网红**：fixture=把某在册 canonical 文件复制、改名全部标识符同构保留、docstring 换写（避开探针词）→ 现行码只产 warn（散文级）甚至零命中 → 断言「该文件必须被二阶段标记高相似」——**现码无二阶段，必红**。
- **R-B2 历史账本零误拦锚（施工后红验）**：对 `create_guard_keyword_dup_warn.jsonl` 已放行样本逐条重放二阶段，断言硬拦判定数=阈值标定前必须=0（影子期）——**若一期就直接判死，本测必红**；此测同时锁死「影子先行」的施工纪律。

## 5. 差分矩阵

1. 标识符级命中（二阶段不触发，行为逐字节不变）；2. 散文级+低相似（维持 warn）；3. 散文级+高相似（影子期仍 warn，账本记 would_block）；4. 散文级+中相似（灰区记账）；5. canonical 文件缺失/语法错误（fail-open 维持 warn）；6. 新建文件自身语法错误（:1146 既有豁免不变）；7. 逃生标记命中（:1148 整体豁免不变）；8. 同批自引用/canonical 指向同批件（:1163 既有过滤不变）；9. 超 10k token 大文件（性能护栏：序列截断常量）；10. CJK 注释主导文件；11. canonical 缓存 mtime 失效正确性；12. lookup 桩（测试注入小型 lookup，:1014 既有缝）。

## 6. 风险与回滚

| # | 风险 | 缓解 | 残余 |
|---|------|------|------|
| 1 | 阈值未标定即硬拦→误杀合法新模块 | §3.3 影子先行+Owner 门位定档（本单一期不含硬拦开关） | 标定数据不足一周时顺延 |
| 2 | 性能：warn 面每条读 canonical | 进程内 mtime 键缓存；触发面=warn 账本量级（本窗 ≤230 次） | 大 canonical 冷读一次性成本 |
| 3 | SequenceMatcher 大序列慢 | 截断+只比 identifier 序列（非全文）；实测 >50ms/对则降采样 | 低 |
| 4 | 二阶段结果与 #456 档位混淆 | 影子账本独立文件，不回写既有 warn 账本 | 低 |

回滚：一期影子=纯增量审计文件，回滚=删调用点一行+删账本；零判据变化、零数据迁移。

## 7. 估时

| 步 | 内容 | 估时 |
|---|------|-----|
| 1 | 二阶段函数 + 触发面接入 warn 出口 | 1.0 h |
| 2 | canonical token 缓存 + R-B1 红证 | 1.0 h |
| 3 | 影子账本 + R-B2 重放锚 | 0.5 h |
| 4 | 差分矩阵 12 例全绿 | 1.0 h |
| 合计 | | **3.5 h**（阈值标定另需一周影子期，零工时） |

## 8. 执行留痕（G3 车道 st-circ-g3-20260930 施工，2026-10-01 夜）

**红证先行**：`tests/gov_enforcement/test_create_guard_token_sim_shadow.py` 共 7 测。R-B1 同构改名漏网红实现前**红证在案**（影子账本不存在必红——5 红 1 绿 1 skip，红点=R-B1+矩阵依赖新函数面）；实现后 6 绿+1 skip。

**实现面**（零判据变化，影子先行）：
- `_audit_token_sim_shadow` 挂载点=`_check_capability_keyword_overlap` warn 出口（`_audit_keyword_dup_warn` 之后）；触发面收敛=仅 #456 散文级 warn 命中条目（标识符级硬拦路径零触碰，矩阵 1 断言锁定）。
- 结构证据=AST 标识符有序序列（类/函数名+Name/Attribute/arg，`_TOKEN_SIM_TRUNC=10000` 截断护栏）经既有 `CapabilityLookup._tokenize` 切词后 `diff_utils.similarity_ratio`（stdlib difflib，**零新依赖**）。
- canonical 侧 (normcase 路径, mtime_ns, size) 键进程内缓存 `_CANON_TOKEN_SIM_CACHE`（失败不缓存——对标 :734 解析缓存语义，负结果不钉死）。
- 影子模式：独立账本 `.runtime/gate_audit/create_guard_token_sim_shadow.jsonl`（fail-open），记录恒带 `mode=shadow`、`would_block=false`、`threshold=null`；不回写 #456 warn 账本。硬拦开关不存在于本一期（回滚=删调用点一行+删账本）。

**影子模式验证证据（袋内红测断言）**：
- R-B1：同构改名复制体（engine→checker 词素保留改名+docstring 换写避探针）→ `passed=True` 行为零变化 + 影子账本记录 `similarity≥0.6`、`would_block=false`、`threshold=null`、`mode=shadow`；
- R-B2 历史账本零误拦锚：**skip 语义生效**——#456 落地后生产 warn 账本 `create_guard_keyword_dup_warn.jsonl` 尚无样本（散文级命中零发生，账本成形前 skip+提示），账本非空后重放断言自动生效（影子期硬拦判定数=0，若一期就判死本测必红）；
- 矩阵：标识符级不触发影子/canonical 缺失 fail-open 记 `token_sim_skipped`/缓存 mtime 失效重读/12k 标识符大文件截断=护栏常量/lookup 桩（真 _tokenize 静态件+桩 find）全绿。
- 回归：dup_tier（#456 两档化红证）6 测全绿；ruff check+format 双净。

**落地**：**01849a3d5d**（create_guard.py 全量+影子红测同袋；create_guard 的 S4-C 面同袋先行——队列 requeue"快照=当前工作区"语义，归因交叉已核，见 s4_c 簿 §8）。

**一周后动作（Owner 门位）**：取影子账本相似度分布定硬拦阈值（禁止拍脑桉阈值直接上硬拦）；标定数据不足一周时顺延。
