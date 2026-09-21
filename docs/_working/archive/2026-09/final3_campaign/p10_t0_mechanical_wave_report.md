---
ttl: task_bound
---

# P10 · RA-H2 T0 机械波计数报告（final3 战役 / 裁定#371）

- 执行会话：P10 分包（总包 st-maxexec-20260920）；测量时窗 2026-09-20 12:40–13:15（现场实测）
- 依据：`docs/01_policies_and_standards/sop/audit_prompts_20_ai.md`（v5）第 3 章 T0 机械检查卡 + 第 0 章 §0.15 T0 写权限白名单 + §0.6 分片规则 + 第 4 章指标口径；裁定#371（final3 战役授权）
- 分母：tracked 文件总数 **15904**（`git ls-files` 现场实测；波次期间并发会话落地使总数 15898→15904，计数为活体快照）
- 扫描产物与脚本：`.runtime/tmp/p10_t0/`（c01–c18 输出原文、domain_map.json、matrix.json、run_c05.py、attribute_domains.py）
- 证据等级：除单独标注外全部 **[亲验]**（命令均为本会话现场执行）

## 1. 域×卡计数矩阵

> 计数=该卡输出中归因到该域的违规条数（机械路径归因：输出行文件路径 × 第 2 章锚点映射，AI-11/12 先于 AI-13）。
> 「全域」=该卡检查器无分域能力或输出行不含路径，只跑一次计全域；「—」=该卡不适用本域（按第 2 章卡-域映射）。
> C-05 列=FAIL/WARNING（CRLF 属设计 warn 不阻断）；C-09=C-09a 临时文件；C-09c=孤儿 .py；C-16 括注分类：OM=孤模块/OS=孤脚本/OG=孤门禁/ZR=僵尸引用/MPM=模块路径错配。
> 域文件数=域锚点 tracked 展开数（AI-22=无主差集）。

| 域 | 文件数 | C-01 | C-02 | C-03 | C-04 | C-05 F/W | C-07 | C-08 | C-09 | C-09c | C-11硬 | C-14 | C-16 | C-17 | C-18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AI-01 | 25 | 0 | 0 | — | 全域 | 0/3 | — | — | 3 | — | — | — | 4 (OG2+OS2) | 0 | — |
| AI-02 | 348 | 0 | 0 | — | 全域 | 0/69 | — | — | 10 | — | — | — | 0 | 0 | — |
| AI-03 | 238 | 0 | 0 | — | 全域 | **375**/44325 | — | 7 | 0 | — | — | — | 6 (OM3+OS3) | 0 | — |
| AI-04 | 237 | 0 | 0 | 2 | 全域 | 0/199 | — | — | 10 | — | 0 | — | 0 | 0 | — |
| AI-05 | 138 | 0 | 0 | 0 | 全域 | 0/121 | — | — | 15 | — | 0 | — | 0 | 0 | — |
| AI-06 | 547 | 17 | 0 | 0 | 全域 | 0/422 | — | — | 41 | — | 1 | — | 0 | 0 | — |
| AI-07 | 221 | 0 | 0 | 0 | 全域 | 0/171 | — | — | 26 | — | 0 | — | 0 | 0 | — |
| AI-08 | 292 | 19 | 0 | 0 | 全域 | 0/256 | — | — | 38 | — | 0 | — | 0 | 0 | — |
| AI-09 | 350 | 3 | 0 | 0 | 全域 | 0/292 | — | — | 26 | — | 0 | — | 0 | 0 | — |
| AI-10 | 166 | 9 | 0 | 0 | 全域 | 0/145 | — | — | 12 | — | 1 | — | 2 (MPM) | 0 | — |
| AI-11 | 401 | 52 | 0 | 0 | 全域 | 0/332 | — | — | 14 | — | 0 | 4 | 0 | 0 | — |
| AI-12 | 213 | 1 | 0 | 0 | 全域 | 0/170 | — | — | 10 | — | 1 | 0 | 1 (MPM) | 0 | — |
| AI-13 | 213 | 0 | 0 | 0 | 全域 | 0/199 | — | — | 21 | — | 0 | 1 | 1 (MPM) | 0 | — |
| AI-14 | 341 | 1 | 0 | 0 | 全域 | 0/333 | — | — | 36 | — | **14** | 0 | 0 | 0 | — |
| AI-15 | 285 | 5 | 0 | 0 | 全域 | 0/259 | — | — | 43 | — | 0 | 0 | 0 | 0 | — |
| AI-16 | 419 | 4 | 0 | 0 | 全域 | 0/181 | — | — | 17 | — | 1 | 0 | 0 | 0 | — |
| AI-17 | 523 | 56 | 13 | 0 | 全域 | 0/101 | 240 | 1 | 0 | — | 0 | 0 | 0 | 0 | **115** |
| AI-18 | 6063 | **3298** | 5 | 0 | 全域 | 0/5030 | **1721** | 4 | 0 | — | 0 | 0 | 0 | 0 | 2 |
| AI-19 | 3657 | 527 | 0 | 0 | 全域 | 0/169 | — | — | 232 | — | 0 | 0 | 0 | 0 | — |
| AI-20 | 1157 | 179 | 0 | 2 | 全域 | 0/164 | — | — | 34 | — | 2 | 0 | 1 (ZR) | 0 | — |
| AI-22 | 70 | 0 | 0 | 1 | — | 未扫¹ | 20 | 0 | 12 | **30** | — | — | 47 (OM21+OS26) | **70** | 0 |
| 全域单跑 | — | — | — | — | **22阻断**/1791warn | — | — | — | — | — | — | — | — | — | — |

¹ C-05 本波覆盖第 2 章 20 个域锚目录+仓根文件；无主区子树（src/zephyr 根层 68 文件+tools/ 2）与 vendor/ 未扫——归属判定属 C-17 `报` 类，T1 派单定归属后补扫。

全域单跑卡实测（末行计数）：

| 卡 | 命令 | exit | 末行计数 |
|---|---|---|---|
| C-01 | `scripts/ops/verify_header_completeness.py` | 1 | `RESULT: 4171 FILES STILL MISSING REQUIRED FIELDS`（扫 11121 文件：A_full 3829/A_test 3450/B_yaml 3752/C_json 25/E_shell 72²） |
| C-02 | `check_frontmatter_metadata.py --all-files` | 1 | `FAIL: 18 file(s) with hard-block issues in 14761 files checked` |
| C-03 | `check_vocab_hardcode.py --ci` | 1 | `FOUND: 5 vocabulary hardcode issue(s) in 4340 files checked`（另 NOQA 豁免 94 处/67 文件，基线一致） |
| C-04 | `check_naming_convention.py --scan --warn-only` | 1 | `总计 22 个阻断性命名违规`（另 1791 warn）；SSoT 面 `--validate-ssot`：1 条 N-16 漂移（skip_dirs_docs YAML 含 algo_flow、fallback 缺） |
| C-05 | `check_encoding.py --dir <域锚>`×79 批 | 0/1 | 合计 FAIL=375 / WARNING=52941（单批最长 8.6s，无超时） |
| C-06 | `audit_directory_scalability.py` | 0 | `0 errors, 2 warnings`（docs/03_modules/_domain_data 7 md；src/zephyr/data 66 py） |
| C-07 | `check_index_integrity.py --warn-only` | 0 | 1981 条（LOW 1926/MEDIUM 55）；去 `--warn-only` 严格复跑 exit=1 |
| C-08 | `check_directory_contract.py` | 1 | `[GATE-DIRECTORY-CONTRACT] 12 个发现（12 errors, 0 warnings）`：DCR-005×8/DCR-008×2/DCR-001×1/DCR-006×1 |
| C-09 | `detect_temp_files.py` / `detect_residual_files.py --warn-only` / `detect_orphan_py.py` | 1/0/1 | 600 临时（全 MEDIUM，扫 16552 文件）/ `无残留物` / `FOUND 30 orphan .py`（vendor\Kronos 为主） |
| C-10 | `pytest tests/governance/test_error_code_consistency.py -q` | 1 | `1 failed, 7 passed`：未登记码 `ZA-INF-RT-ADM`（重号面 `known_duplicates=[]` =0，绿） |
| C-11 | `align_all.py --no-report` | 1 | `硬阻断: 20 个硬问题（…gomap error=20）`+`软问题: 693`；域不一致/幽灵锚点/frontend_map/decision_map/factory_map 均 0 |
| C-12 | `diagnose_depgraph.py --output …diag.yaml` | 0 | orphan_nodes=474、empty_blueprint_id=374、多节点环 12（data 域 `__init__` 环为主） |
| C-13 | （机械面由 C-16 ORPHAN MODULES=24 + C-12 orphan=474 承载） | — | 四步判岛（生产 import 双查+挂载对账）属 T1 判断面，本波不解读语义 |
| C-14 | `scripts/clone_guard_audit.py` | 0 | findings=5（extract=4/review=1）未 acknowledged，健康分 D（报告 `.runtime/clone_guard_audit/audit_20260920T125152.json`） |
| C-15 | 读册机读字段（未重跑生成器³） | — | total_fail_open=1595：hardcoded_default_permit=5/money_path_no_trace=176/designed_degradation_with_trace=735/undeclared_needs_review=679 |
| C-16 | `audit_registration.py --full` | 1 | `TOTAL: 62 issues`：OM24+OS31+OG2+ZR1+MPM4 |
| C-17 | `git ls-files`×第 2 章锚点差集 | — | 无主 tracked=70：strategy_factory 17/knowledge 15/strategy_pipeline 11/infra_runtime 9/ai_layer 7/infra_ops 6/gov_enforcement 根 3/tools/desktop 2 |
| C-18 | `check_pure_assertion.py --full-scan` | 1 | `检出 117 条违规` |

² C-01 首跑扫 11128、复跑 11121（并发会话在波次窗口内增删文件所致）；缺栏数两跑一致=4171。
³ C-15 册 generated_at=2026-09-18T11:21:15Z（距今 2 天）。重跑生成器写共享热文件 `_registry/catalogs/fail_open_register.yaml`，并发波次下按 0.10 记「共享收口」留总控串行执行——本波只读机读字段。

## 2. 机械面红数 Top10（按量）

| # | 卡/指标 | 现值 | 主集中域 |
|---|---|---|---|
| 1 | C-05 WARNING | 52941 | AI-03（44325，logs/tmp 运行时面；CRLF 属设计 warn） |
| 2 | C-01 表头缺栏 | 4171 | AI-18 3298 / AI-19 527 / AI-20 179 |
| 3 | C-04 warn 命名 | 1791（另阻断 22） | 输出无全路径，未分域（N-13 541/N-17 381/N-01 372/N-15 174/N-03 124…） |
| 4 | C-07 索引完整性 | 1981 | AI-18 1721 / AI-17 240 / AI-22 20 |
| 5 | C-11 软问题 | 693（硬 20 另计） | gomap 机生层漂移：AI-14 14 / AI-20 2 |
| 6 | C-12 依赖图孤儿 | 474（空 blueprint_id 374、环 12） | 图级指标 |
| 7 | C-15 fail-open | 1595（undeclared 679 / money_path_no_trace 176） | 册级指标（2 天前生成） |
| 8 | C-09a 临时文件 | 600 | AI-19 232 / AI-15 43 / AI-14 36 |
| 9 | C-18 纯陈述违规 | 117 | AI-17 115 |
| 10 | C-16 登记缺口 | 62 | AI-22 47（OM21+OS26） |

## 3. 与 v4 台账快照对照（第 4 章四主指标：基线→现值）

| 指标 | v4 基线（2026-09-18） | 本次实测（2026-09-20） | 趋势 |
|---|---|---|---|
| 表头缺栏文件数（C-01） | 4346 | **4171** | ↓175（改善） |
| frontmatter 硬阻断/检查总数（C-02） | 18 / 13513 | **18 / 14761** | 绝对数持平（分母 +1248：新增文件未引入新硬阻断） |
| 阻断性命名违规（C-04，另 warn） | 634（warn 1728） | **22**（warn 1791） | 阻断 ↓612（**#344 修复生效，如预期大幅下降**）；warn +63 待 gate-naming-audit 清 |
| 未登记错误码（C-10） | 3（ZA-DATA-ALERT-WEBHOOK/ZA-INF-RT-ADM/ZA-PA-CRISIS） | **1**（ZA-INF-RT-ADM） | ↓2（另两码已补登，余 1） |

## 4. 机械面清零判定

- **全绿卡：0 张完全清零**。计数为 0 的仅 C-06（error=0，2 容量 warn，按卡判绿——弱绿，见 §5）与 C-09b（残留物 0——未证绿，见 §5）。
- **有红卡=T1 线索清单**（19 卡中 17 卡有红或绿证不全）：
  1. C-01：4171 缺栏（补栏值须实读 import/registry，白名单 `改` 类但本波任务书限计数——入 T1 修复队列；AI-18/AI-19 大头）
  2. C-02：18 硬阻断（AI-17 13 全在 docs/02 永久区缺 frontmatter；AI-18 5 在 _working 缺 ttl）
  3. C-03：5 词表硬编码（alt_data×2、infra_runtime、generators、industry_graph）
  4. C-04：22 阻断 + SSoT 面 N-16 漂移 1 条（skip_dirs_docs 兜底常量缺 algo_flow——双份承载机械对齐义务，0.15 白名单④邻域但涉共享热文件配置）
  5. C-05：375 FAIL 全为 AI-03 logs/ 备份 JSON 的 UTF-8 BOM（gitignored 运行时产物，处置=AI-03 治理面：清旧备份或重生成）
  6. C-06：2 容量 warn（_domain_data 7 md / src/zephyr/data 66 py——建子目录属 `裁`）
  7. C-07：1981 索引断链（AI-18 大头：低学历勇闯量化/同花顺资料等 _working 区 index 指向不存在文件——含非 ASCII 文件名解析）
  8. C-08：12 DCR 违规（data/backup README.txt×、_working .json×4、session_logs .txt）
  9. C-09：600 __pycache__ 类 + 30 孤儿 py（vendor\Kronos 26+；`--fix` 已禁用，删除属门位）
  10. C-10：1 未登记码 ZA-INF-RT-ADM（机械补登属 `改` 类，但 error_code_registry.yaml 在受保护路径 architecture_model/contracts/ 下→共享收口交总控）
  11. C-11：硬 20 全为 gomap 机生层漂移（重跑 generate_governance_map.py 属白名单⑤派生重建——但写共享 yaml，并发波次留总控串行）；软 693
  12. C-12：孤儿 474 / 空 blueprint_id 374 / 环 12（删/退役一律上交走 §2.4A salvage）
  13. C-13：候选= C-16 OM 24 + C-12 474；四步判岛=T1
  14. C-14：5 克隆未 ack（session_worktree.py×4 [AI-11]、decisiongraph_schema.py×1 [AI-13]；acknowledged 走 echo-guard.yml 白名单须写理由）
  15. C-15：undeclared_needs_review=679 / money_path_no_trace=176（三轴分档 T1 处置或登记处方；册待总控重跑刷新）
  16. C-16：62 登记缺口（AI-22 无主区占 47）
  17. C-17：70 无主 tracked（归属建议→总控转 Owner；gov_enforcement 根 3 文件提示第 2 章 AI-11 锚点可能漏根文件——锚点漂移类发现）
  18. C-18：117 纯陈述违规（AI-17 115：02_enterprise 架构文档与归档 v1 宪法的"已废止/从X迁移到Y"过去态文本）

## 5. C-00 能红自证记录（0.14，双向）

| 卡 | 红向 | 绿向 | 判定 |
|---|---|---|---|
| C-05 | [亲验] BOM 注入样本→`INJ-007 FAIL` exit1 | [亲验] 干净样本→exit0 无输出 | **双向已证**（样本在 .runtime/tmp，已撤） |
| C-01/C-02/C-03/C-04/C-07(严格 exit1)/C-08/C-09a/C-09c/C-10/C-11/C-16/C-18 | [亲验] 实际输出红（计数>0=检查器对真实违规报红） | 本波未判绿，N/A | 红向实证 |
| C-06 | 部分：2 条 WARNING 对真实容量问题报警=警告级红向实证；**错误级红未注入**（需 >120 文件目录，T0 白名单禁仓内造样） | exit0（真实） | **未证绿（弱）** |
| C-09b | 未注入（需在扫描根造残留文件，超本波写权限） | exit0 `无残留物` | **未证绿** |
| C-14 | [亲验] 5 findings 报出=红向实证 | exit0 但 findings 非零，实质非清零 | 按卡 exit 判绿、实质红 |
| C-12 | count=474 报出（指标型卡） | — | 红向实证 |
| C-15 | 未重跑生成器（共享热文件） | — | 本波只读，未证 |
| C-17 | 差集非空（70）报出 | — | 红向实证 |

## 6. 基础设施故障清单

无。19 张卡全部在 5 分钟时限内完成（C-05 最慢单批 8.6s；C-02 全量 14761 文件、C-03 4340 文件、C-14 3505 文件均在时限内）。无重试、无跳过。

## 7. 备注

- 波次窗口内主仓 dev 有并发会话活动（tracked 15898→15904，+6 全落 docs/_working），本报告计数为活体快照，以本文件 commit 时点为准。
- 本波严格未做任何修复/删除/重命名（任务书限计数产出）；`改` 类白名单处置全部以 T1 线索形式登记于 §4。
- C-04 输出行不含全路径，分域归因不做臆测（矩阵记「全域」）；如需分域需增强检查器输出（T1 裁定项）。
