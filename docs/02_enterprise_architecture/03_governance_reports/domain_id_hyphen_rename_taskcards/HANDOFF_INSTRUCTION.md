---
doc_type: operational_rule
status: active
title: "6域ID改名执行交接指令（新AI会话一键复制）"
version: "1.0.0"
created: "2026-06-26"
updated: "2026-06-26"
ttl: task_bound
---

# 交接指令（以下内容一键复制到新AI会话）

```
你是ZephyrAlpha项目的执行AI。你的任务是端到端执行6个域ID连字符→下划线改名的14张任务卡（7主卡+7元审查卡），执行完成后做全量审查，循环审查至问题=0。

═══════════════════════════════════════════════════
一、背景与改名映射
═══════════════════════════════════════════════════

6个域ID违反NR-002命名规则（^D-[A-Z][A-Z0-9_]*$，禁止连字符），需改为下划线风格：

| 原域ID | 新域ID | domain_name | 预期DB行数 |
|---|---|---|---|
| D-GOV-DOCS | D-GOV_DOCS | architecture_docs | 756 |
| D-GOV-ENFORCEMENT | D-GOV_ENFORCEMENT | rule_enforcement | 436 |
| D-GOV-SCRIPTS | D-GOV_SCRIPTS | code_dedup | 2517 |
| D-GOV_AUDIT_TESTS | D-AUDITTEST | audit_test_suite | 156 |
| D-INTEGRATION-GATEWAY | D-INTEGRATION_GATEWAY | mcp_servers | 252 |
| D-SECURITY-LLM | D-SECURITY_LLM | llm_defense | 206 |
| 合计 | | | 4323行 |

注：D-GOV_AUDIT_TESTS改为D-AUDITTEST（非D-GOV_AUDIT_TESTS下划线版），因前者语义暗示是D-GOV_AUDIT的子域（NR-001盲区），改为独立ID彻底消除歧义。

═══════════════════════════════════════════════════
二、关键文件路径（全部绝对路径）
═══════════════════════════════════════════════════

【方案文档（详细施工细节，含所有动作的命令和预期输出）】
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_plan.md

【任务卡目录（14张卡+1索引）】
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\index.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062621.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062622.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062623.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062624.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062625.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062626.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062627.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062628.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062629.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062630.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062631.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062632.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062633.md
D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\OPS-2026062634.md

【DB（全景图，改前必须git备份）】
D:\ZephyrAlpha\data\databases\depgraph.db

【核心工具脚本】
D:\ZephyrAlpha\scripts\governance\apply_depgraph.py（--rename-domain 子命令，17步UPDATE+B1兜底）
D:\ZephyrAlpha\scripts\git_commit.py（GitCommitGateway，--files逗号分隔，禁止裸git commit）
D:\ZephyrAlpha\scripts\governance\diagnose_depgraph.py（post_sync_standard验收）
D:\ZephyrAlpha\scripts\governance\d3_metadata\check_frontmatter_metadata.py（GATE-15 ttl校验）
D:\ZephyrAlpha\scripts\governance\sync_yaml_to_depgraph.py（YAML→DB单向同步）

【YAML真源（域定义唯一真源）】
D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\functional_domain_registry.yaml

【17个手动修改文件（完整清单）】
1. D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\functional_domain_registry.yaml（YAML，7行改）
2. D:\ZephyrAlpha\scripts\governance\sync_yaml_to_depgraph.py（脚本，L706硬编码1处）
3. D:\ZephyrAlpha\scripts\governance\d5_architecture\dm200912_rewrite_views.py（脚本，L829/L832共2处）
4. D:\ZephyrAlpha\scripts\governance\d5_architecture\generators\generate_capability_heatmap.py（脚本，L116/L127共2处）
5. D:\ZephyrAlpha\docs\02_enterprise_architecture\target_architecture\architecture_model\index.yaml（活文档，6处）
6. D:\ZephyrAlpha\docs\02_enterprise_architecture\target_architecture\capability_heatmap.md（活文档，10处）
7. D:\ZephyrAlpha\docs\02_enterprise_architecture\target_architecture\index.md（活文档，9处）
8. D:\ZephyrAlpha\docs\02_enterprise_architecture\target_architecture\overview.md（活文档，2处）
9. D:\ZephyrAlpha\docs\02_enterprise_architecture\target_architecture\application_architecture.md（活文档，1处）
10. D:\ZephyrAlpha\scripts\_t17_domain_suggestions.csv（工作CSV，全局替换）
11. D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\preexisting_db_issues_investigation_report.md（历史文档，追加裁定说明，ttl=permanent已存在）
12. D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_architecture_panorama.md（历史文档，追加说明，ttl=permanent已存在）
13. D:\ZephyrAlpha\docs\02_enterprise_architecture\architecture_diagram_construction_plan.md（历史文档，**先补ttl:task_bound再追加说明**，GATE-15会阻断）
14. D:\ZephyrAlpha\docs\02_enterprise_architecture\_archive\phase4b_cleanup_construction_plan.md（历史文档，追加说明，ttl=permanent已存在）
15. D:\ZephyrAlpha\docs\_working\domain_split_plan_4_oversized_domains.md（历史文档，追加说明，ttl=task_bound已存在）
16. D:\ZephyrAlpha\docs\decomposition\tasks\DM-100254.md（历史文档，无frontmatter，GATE-15跳过）
17. D:\ZephyrAlpha\data\archive\taskcards\DM-100257.md（历史文档，无frontmatter，GATE-15跳过）

═══════════════════════════════════════════════════
三、执行流程（14张卡顺序执行，不可跳过、不可乱序）
═══════════════════════════════════════════════════

每张主卡含完整施工步骤（细到一个动作怎么做，含命令和预期输出）。
每张主卡后紧跟一张元审查卡，循环审查修复前一张主卡，连续2轮全PASS才放行下一张。

【第1对：备份+DB改名（最高风险🔴）】
步骤1：执行 OPS-2026062621（阶段0备份+阶段1 DB 6域改名4323行）
  - 动作0.1：git备份depgraph.db，记录commit hash为<BACKUP>
  - 动作1.1~1.6：逐域 dry-run预览→执行改名→验证0残留（6域）
  - 动作1.7：全表全列残留扫描=0
  - 动作1.8：git提交DB改名
步骤2：执行 OPS-2026062622（元审查：逐条验证6项验收标准，连续2轮全PASS）
  - V1 backup commit存在
  - V2 6个旧域ID在domains表零残留
  - V3 6个新域ID存在于domains表
  - V4 全表全列残留=0
  - V5 rename commit存在
  - V6 commit message含"4323 rows"

【第2对：YAML+脚本修改】
步骤3：执行 OPS-2026062623（阶段2 YAML 7行+阶段3 3个脚本5处硬编码）
步骤4：执行 OPS-2026062624（元审查5项：YAML零残留+3脚本行号验证+sync无diff）

【第3对：活文档+CSV修改】
步骤5：执行 OPS-2026062625（阶段4 5个活文档~28处+阶段5 1个CSV全局替换）
步骤6：执行 OPS-2026062626（元审查3项：5活文档零残留+CSV零残留+6新域名出现）

【第4对：历史文档ttl+追加说明】
步骤7：执行 OPS-2026062627（阶段6 7个历史文档，含动作6.3a补ttl:task_bound）
  - 注意：architecture_diagram_construction_plan.md必须先补ttl:task_bound到frontmatter（动作6.3a），再追加裁定说明（动作6.3b），否则GATE-15阻断commit
步骤8：执行 OPS-2026062628（元审查3项：7文件含ARCH-REN-001+ttl=task_bound+GATE-15 exit0）

【第5对：重新生成制品】
步骤9：执行 OPS-2026062629（阶段7 5批生成器：target_path_tree+project_depgraph+域文档+全局架构图+治理报告）
步骤10：执行 OPS-2026062630（元审查3项：6新域名在制品中出现+旧域名零残留+constraint_violations不报NR-002）

【第6对：循环验收】
步骤11：执行 OPS-2026062631（阶段8 2轮diagnose零错误+文件残留扫描=0+GATE-15校验exit0）
步骤12：执行 OPS-2026062632（元审查4项：独立复跑diagnose+残留+GATE-15+确认2轮连续）

【第7对：Git提交+最终验收】
步骤13：执行 OPS-2026062633（阶段9 提交17文件+提交生成制品，--files逗号分隔）
步骤14：执行 OPS-2026062634（元审查6项：2个commit存在+4个commit完整+git status干净+全局端到端DB+文件零残留+6新域名在DB存在）

═══════════════════════════════════════════════════
四、执行规则（严格遵守）
═══════════════════════════════════════════════════

1. 每张主卡必须严格按"施工步骤"中的动作顺序执行，只修改allowed_touch中的文件
2. 每张主卡执行完成后，立即执行对应的元审查卡，循环至连续2轮全PASS
3. 元审查卡未通过前，禁止执行下一张主卡
4. 每条命令执行后核对"预期输出"，不符则停下排查
5. DB修改必须通过apply_depgraph.py --rename-domain，禁止直接SQL改库
6. git提交必须通过scripts/git_commit.py（GitCommitGateway），禁止裸git commit
7. --files参数为逗号分隔的单字符串，不可用空格分隔
8. 改depgraph.db前必须先git备份（动作0.1），记录<BACKUP> hash用于回滚
9. 回滚区分两种场景：提交前用git checkout，提交后用git reset --hard <BACKUP>
10. 历史文档保留旧名+追加裁定说明（不逐一替换），仅architecture_diagram_construction_plan.md需先补ttl

═══════════════════════════════════════════════════
五、执行完成后的全量审查（问题=0循环）
═══════════════════════════════════════════════════

14张卡全部COMPLETED后，执行全量端到端审查，循环至连续2轮零问题：

【审查项1：DB零残留】
python -c "
import sqlite3
c = sqlite3.connect('data/databases/depgraph.db')
old_ids = ['D-GOV-DOCS','D-GOV-ENFORCEMENT','D-GOV-SCRIPTS','D-GOV_AUDIT_TESTS','D-INTEGRATION-GATEWAY','D-SECURITY-LLM']
tables = [r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name NOT IN ('domain_naming_rules','_schema_version','governance_audit_logs')\").fetchall()]
total = 0
for tbl in tables:
    cols = [col[1] for col in c.execute(f'PRAGMA table_info({tbl})').fetchall()]
    for col in cols:
        for oid in old_ids:
            cnt = c.execute(f'SELECT COUNT(*) FROM {tbl} WHERE CAST({col} AS TEXT) LIKE ?', (f'%{oid}%',)).fetchone()[0]
            if cnt > 0: print(f'RESIDUAL: {tbl}.{col} {oid}: {cnt}'); total += cnt
print(f'DB: {total}' + (' PASS' if total==0 else ' FAIL'))
"
预期：DB: 0 PASS

【审查项2：DB新域名存在】
python -c "
import sqlite3
c = sqlite3.connect('data/databases/depgraph.db')
new_ids = ['D-GOV_DOCS','D-GOV_ENFORCEMENT','D-GOV_SCRIPTS','D-AUDITTEST','D-INTEGRATION_GATEWAY','D-SECURITY_LLM']
for nid in new_ids:
    cnt = c.execute('SELECT COUNT(*) FROM domains WHERE domain_id=?', (nid,)).fetchone()[0]
    print(f'{\"PASS\" if cnt==1 else \"FAIL\"}: {nid}={cnt}')
"
预期：6行全PASS

【审查项3：文件零残留（活文档+脚本+CSV，排除历史文档和生成制品）】
python -c "
import os, re
old_ids = ['D-GOV-DOCS','D-GOV-ENFORCEMENT','D-GOV-SCRIPTS','D-GOV_AUDIT_TESTS','D-INTEGRATION-GATEWAY','D-SECURITY-LLM']
pat = re.compile('|'.join(r'(?<![A-Z])' + re.escape(d) for d in old_ids))
check_files = [
    'docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml',
    'docs/02_enterprise_architecture/target_architecture/architecture_model/index.yaml',
    'docs/02_enterprise_architecture/target_architecture/capability_heatmap.md',
    'docs/02_enterprise_architecture/target_architecture/index.md',
    'docs/02_enterprise_architecture/target_architecture/overview.md',
    'docs/02_enterprise_architecture/target_architecture/application_architecture.md',
    'scripts/governance/sync_yaml_to_depgraph.py',
    'scripts/governance/d5_architecture/dm200912_rewrite_views.py',
    'scripts/governance/d5_architecture/generators/generate_capability_heatmap.py',
    'scripts/_t17_domain_suggestions.csv',
]
total = 0
for f in check_files:
    if not os.path.exists(f): continue
    content = open(f, encoding='utf-8', errors='ignore').read()
    for m in pat.finditer(content):
        start = m.start()
        if start > 0 and content[start-1].isupper(): continue
        if '[BLUEPRINT]' in content[max(0,start-50):start+50]: continue
        print(f'RESIDUAL: {f}: {m.group()}'); total += 1
print(f'Files: {total}' + (' PASS' if total==0 else ' FAIL'))
"
预期：Files: 0 PASS

【审查项4：diagnose零错误】
python scripts/governance/diagnose_depgraph.py
预期：0 error，exit 0

【审查项5：GATE-15通过】
python scripts/governance/d3_metadata/check_frontmatter_metadata.py --all-files
预期：exit 0（唯一允许的预存FAIL是KE-R7-OVERSIZED-001.md，与本次改名无关）

【审查项6：git提交完整（4个commit）】
git log --oneline -6
预期包含4行：
  backup: pre-rename-hyphen depgraph.db snapshot [GW:rename-hyphen]
  rename: 6 domain IDs hyphen→underscore (4323 rows updated) [GW:rename-hyphen]
  rename: 6 domain IDs hyphen→underscore - file sync (17 files) [GW:rename-hyphen]
  rename: regenerate artifacts after 6 domain ID rename [GW:rename-hyphen]

【审查项7：git工作区干净】
git status --short
预期：无输出

【循环判定】
7项审查全PASS → 第1轮通过 → 再跑1轮确认 → 连续2轮全PASS = 整个改名流程COMPLETED
有FAIL → 修复后重跑全部7项 → 直到连续2轮全PASS

═══════════════════════════════════════════════════
六、回滚方案（出错时使用）
═══════════════════════════════════════════════════

提交前回滚（DB改名仅在工作区未commit）：
  git checkout data/databases/depgraph.db
  git checkout -- <修改的文件>

提交后回滚（DB改名已commit，整体回退到备份点）：
  git reset --hard <BACKUP>  （<BACKUP>是动作0.1的backup commit hash）

仅回退DB不回退文件：
  git checkout <BACKUP> -- data/databases/depgraph.db

═══════════════════════════════════════════════════
七、开始执行
═══════════════════════════════════════════════════

现在开始：
1. 先读取方案文档 D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_plan.md 了解全貌
2. 读取任务卡索引 D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\domain_id_hyphen_rename_taskcards\index.md 了解覆盖度
3. 从 OPS-2026062621.md 开始逐卡执行，每卡执行前先读取该卡完整内容
4. 每张主卡执行完立即执行对应元审查卡，循环至连续2轮全PASS
5. 14张卡全部COMPLETED后执行第五部分全量审查，循环至连续2轮零问题
6. 最后用大白话汇报所有工作成果、达成的目标、解决的问题
```
